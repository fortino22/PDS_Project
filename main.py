"""
Prescriptive Analytics: Training Allocation Optimization Using Linear Programming
================================================================================

Problem: Optimize training allocation to improve employee performance while
respecting budget, capacity, and fairness constraints.
"""

import pandas as pd
import numpy as np
from pulp import *
import warnings
warnings.filterwarnings('ignore')


# ============================================================================
# STEP 1: DATA LOADING AND PREPROCESSING
# ============================================================================

def load_and_prepare_data():
    """Load all datasets and prepare them for optimization"""
    
    print("="*80)
    print("LOADING HR DATASETS")
    print("="*80)
    
    # Load datasets
    employees = pd.read_csv('employee_data.csv')
    training = pd.read_csv('training_and_development_data.csv')
    engagement = pd.read_csv('employee_engagement_survey_data.csv')
    
    print(f"\nLoaded {len(employees)} employee records")
    print(f"Loaded {len(training)} training records")
    print(f"Loaded {len(engagement)} engagement survey records")
    
    # Filter only ACTIVE employees (eligibility constraint)
    active_employees = employees[employees['EmployeeStatus'] == 'Active'].copy()
    print(f"\nFiltered to {len(active_employees)} active employees (eligible for training)")
    
    # Merge engagement data
    active_employees = active_employees.merge(
        engagement, 
        left_on='EmpID', 
        right_on='Employee ID', 
        how='left'
    )
    
    active_employees['Engagement Score'].fillna(3, inplace=True)
    active_employees['Satisfaction Score'].fillna(3, inplace=True)
    active_employees['Work-Life Balance Score'].fillna(3, inplace=True)
    
    eligible_employees = active_employees[active_employees['Current Employee Rating'] < 5].copy()
    
    print(f"Pre-filtered to {len(eligible_employees)} employees with improvement potential (rating < 5)")
    
    # Take a random sample of 100 employees for faster optimization
    SAMPLE_SIZE = 100
    if len(eligible_employees) > SAMPLE_SIZE:
        eligible_employees = eligible_employees.sample(n=SAMPLE_SIZE, random_state=42)
        print(f"Sampled {SAMPLE_SIZE} employees for optimization (faster processing)")
    
    return eligible_employees, training


def extract_training_programs(training_df):
    """Extract unique training programs with their characteristics"""
    
    training_programs = training_df.groupby('Training Program Name').agg({
        'Training Duration(Days)': 'mean',
        'Training Cost': 'mean',
        'Training Type': lambda x: x.mode()[0] if len(x.mode()) > 0 else x.iloc[0]
    }).reset_index()
    
    training_programs.columns = ['Program', 'Duration', 'Cost', 'Type']
    
    # Calculate historical effectiveness based on outcomes
    outcome_effectiveness = training_df.groupby('Training Program Name')['Training Outcome'].apply(
        lambda x: sum(x.isin(['Passed', 'Completed'])) / len(x) if len(x) > 0 else 0.5
    ).reset_index()
    outcome_effectiveness.columns = ['Program', 'Effectiveness']
    
    training_programs = training_programs.merge(outcome_effectiveness, on='Program')
    
    print(f"\nIdentified {len(training_programs)} unique training programs")
    print("\nTraining Programs Available:")
    print(training_programs.to_string(index=False))
    
    return training_programs


# ============================================================================
# STEP 2: PARAMETER CALCULATION
# ============================================================================

def calculate_improvement_potential(employee, training_program):
    """
    Calculate expected improvement in employee rating if they receive training
    
    Factors considered:
    - Current rating (lower rating = higher improvement potential)
    - Engagement score (higher engagement = better training absorption)
    - Satisfaction score (affects learning effectiveness)
    - Training program effectiveness (historical success rate)
    """
    
    # Max rating is 5, improvement potential is inversely related to current rating
    rating_gap = 5 - employee['Current Employee Rating']
    
    # Normalize engagement and satisfaction scores (0-5 scale)
    engagement_factor = employee['Engagement Score'] / 5.0
    satisfaction_factor = employee['Satisfaction Score'] / 5.0
    
    # Training effectiveness from historical data
    training_effectiveness = training_program['Effectiveness']
    
    # Calculate expected improvement (weighted combination)
    expected_improvement = (
        rating_gap * 0.4 +                          # Room for improvement (40%)
        engagement_factor * 0.25 +                   # Engagement impact (25%)
        satisfaction_factor * 0.15 +                 # Satisfaction impact (15%)
        training_effectiveness * 0.20                # Training quality (20%)
    )
    
    return max(0, expected_improvement)


# ============================================================================
# STEP 3: LINEAR PROGRAMMING FORMULATION
# ============================================================================

def formulate_optimization_problem(employees_df, training_programs_df, 
                                   budget=50000, max_capacity_per_program=20):
    """
    Formulate the Integer Linear Programming problem
    
    DECISION VARIABLES:
    x[i,j] ∈ {0,1} - Binary variable indicating if employee i gets training program j
    
    OBJECTIVE FUNCTION:
    Maximize: Σ Σ (improvement_potential[i,j] * x[i,j])
              i j
    
    Where improvement_potential is calculated based on:
    - Current employee rating gap
    - Engagement and satisfaction scores
    - Training program effectiveness
    
    CONSTRAINTS:
    1. Budget constraint: Σ Σ (cost[j] * x[i,j]) ≤ Budget
                          i j
    
    2. One training per employee: Σ x[i,j] ≤ 1  ∀ i
                                   j
    
    3. Capacity constraint: Σ x[i,j] ≤ Capacity[j]  ∀ j
                            i
    
    4. Eligibility: Only active employees (handled in data preprocessing)
    
    5. Fairness (demographic balance): Ensure no demographic group is excluded
    """
    
    print("\n" + "="*80)
    print("FORMULATING LINEAR PROGRAMMING MODEL")
    print("="*80)
    
    # Create the LP problem
    prob = LpProblem("Training_Allocation_Optimization", LpMaximize)
    
    # Decision Variables: x[employee_id, training_program]
    employees = employees_df['EmpID'].tolist()
    programs = training_programs_df['Program'].tolist()
    
    # Binary decision variables
    x = LpVariable.dicts("assign", 
                         ((emp, prog) for emp in employees for prog in programs),
                         cat='Binary')
    
    print(f"\nCreated {len(employees) * len(programs)} decision variables")
    print(f"({len(employees)} employees x {len(programs)} training programs)")
    
    # ========================================================================
    # OBJECTIVE FUNCTION: Maximize total improvement in employee ratings
    # ========================================================================
    
    improvement_matrix = {}
    for _, emp_row in employees_df.iterrows():
        for _, prog_row in training_programs_df.iterrows():
            emp_id = emp_row['EmpID']
            prog_name = prog_row['Program']
            improvement = calculate_improvement_potential(emp_row, prog_row)
            improvement_matrix[(emp_id, prog_name)] = improvement
    
    prob += lpSum([improvement_matrix[(emp, prog)] * x[(emp, prog)] 
                   for emp in employees for prog in programs]), "Total_Performance_Improvement"
    
    print("\nObjective Function: Maximize total expected improvement in employee ratings")
    
    # ========================================================================
    # CONSTRAINT 1: Budget Constraint
    # ========================================================================
    
    cost_dict = dict(zip(training_programs_df['Program'], training_programs_df['Cost']))
    
    prob += lpSum([cost_dict[prog] * x[(emp, prog)] 
                   for emp in employees for prog in programs]) <= budget, "Budget_Constraint"
    
    print(f"\nConstraint 1: Total training cost <= ${budget:,.2f}")
    
    # ========================================================================
    # CONSTRAINT 2: Each employee can receive at most ONE training
    # ========================================================================
    
    for emp in employees:
        prob += lpSum([x[(emp, prog)] for prog in programs]) <= 1, f"One_Training_{emp}"
    
    print(f"Constraint 2: Each employee receives at most 1 training program")
    
    # ========================================================================
    # CONSTRAINT 3: Training capacity constraint
    # ========================================================================
    
    for prog in programs:
        prob += lpSum([x[(emp, prog)] for emp in employees]) <= max_capacity_per_program, \
                f"Capacity_{prog.replace(' ', '_').replace(',', '')}"
    
    print(f"Constraint 3: Maximum {max_capacity_per_program} employees per training program")
    
    # ========================================================================
    # CONSTRAINT 4: Fairness - Demographic balance
    # Ensure each gender group gets proportional representation
    # ========================================================================
    
    total_employees = len(employees)
    gender_counts = employees_df['GenderCode'].value_counts()
    
    for gender in gender_counts.index:
        gender_employees = employees_df[employees_df['GenderCode'] == gender]['EmpID'].tolist()
        gender_proportion = len(gender_employees) / total_employees
        min_selection = max(1, int(gender_proportion * max_capacity_per_program * 0.5))
        
        prob += lpSum([x[(emp, prog)] for emp in gender_employees for prog in programs]) >= min_selection, \
                f"Fairness_{gender}"
    
    print(f"Constraint 4: Demographic fairness ensured (proportional gender representation)")
    
    return prob, x, employees, programs, improvement_matrix


# ============================================================================
# STEP 4: SOLVE THE OPTIMIZATION PROBLEM
# ============================================================================

def solve_optimization(prob):
    """Solve the ILP problem using PuLP solver"""
    
    print("\n" + "="*80)
    print("SOLVING OPTIMIZATION PROBLEM")
    print("="*80)
    
    # Solve the problem with optimized parameters for faster solving
    # timeLimit: Maximum solving time in seconds
    # gapRel: Accept solution within 1% of optimal (much faster)
    # threads: Use multiple CPU cores
    solver = PULP_CBC_CMD(
        msg=1,           # Show solver progress
        timeLimit=300,   # Max 5 minutes
        gapRel=0.01,     # Accept 1% from optimal (speeds up significantly)
        threads=4        # Use 4 CPU threads
    )
    
    print("Solving with CBC optimizer (max 5 minutes, 1% optimality gap)...")
    prob.solve(solver)
    
    # Check solution status
    status = LpStatus[prob.status]
    print(f"\nSolution Status: {status}")
    
    if status == 'Optimal':
        print("Optimal solution found!")
        return True
    else:
        print("No optimal solution found")
        return False


# ============================================================================
# STEP 5: EXTRACT AND ANALYZE RESULTS
# ============================================================================

def extract_results(prob, x, employees, programs, employees_df, 
                   training_programs_df, improvement_matrix):
    """Extract and analyze the optimization results"""
    
    print("\n" + "="*80)
    print("OPTIMIZATION RESULTS")
    print("="*80)
    
    # Extract selected employees and their assigned training
    selected_assignments = []
    
    for emp in employees:
        for prog in programs:
            if x[(emp, prog)].varValue == 1:
                emp_data = employees_df[employees_df['EmpID'] == emp].iloc[0]
                prog_data = training_programs_df[training_programs_df['Program'] == prog].iloc[0]
                
                selected_assignments.append({
                    'Employee_ID': emp,
                    'Employee_Name': f"{emp_data['FirstName']} {emp_data['LastName']}",
                    'Current_Rating': emp_data['Current Employee Rating'],
                    'Engagement_Score': emp_data['Engagement Score'],
                    'Department': emp_data['DepartmentType'],
                    'Gender': emp_data['GenderCode'],
                    'Training_Program': prog,
                    'Training_Cost': prog_data['Cost'],
                    'Training_Duration': prog_data['Duration'],
                    'Expected_Improvement': improvement_matrix[(emp, prog)]
                })
    
    results_df = pd.DataFrame(selected_assignments)
    
    # Summary statistics
    print(f"\nSOLUTION SUMMARY:")
    print(f"   Total employees selected for training: {len(results_df)}")
    print(f"   Total training cost: ${results_df['Training_Cost'].sum():,.2f}")
    print(f"   Total expected improvement: {results_df['Expected_Improvement'].sum():.2f}")
    print(f"   Average expected improvement per employee: {results_df['Expected_Improvement'].mean():.2f}")
    print(f"   Optimal objective value: {value(prob.objective):.4f}")
    
    print(f"\nTRAINING PROGRAM DISTRIBUTION:")
    program_distribution = results_df['Training_Program'].value_counts()
    for prog, count in program_distribution.items():
        print(f"   {prog}: {count} employees")
    
    print(f"\nDEMOGRAPHIC DISTRIBUTION:")
    gender_distribution = results_df['Gender'].value_counts()
    for gender, count in gender_distribution.items():
        print(f"   {gender}: {count} employees")
    
    print(f"\nDEPARTMENT DISTRIBUTION:")
    dept_distribution = results_df['Department'].value_counts().head(5)
    for dept, count in dept_distribution.items():
        print(f"   {dept}: {count} employees")
    
    # Display selected employees
    print(f"\n" + "="*80)
    print("SELECTED EMPLOYEES FOR TRAINING")
    print("="*80)
    
    display_df = results_df[[
        'Employee_ID', 'Employee_Name', 'Current_Rating', 
        'Engagement_Score', 'Training_Program', 'Training_Cost', 
        'Expected_Improvement'
    ]].sort_values('Expected_Improvement', ascending=False)
    
    print("\n" + display_df.to_string(index=False))
    
    # Save results to CSV
    results_df.to_csv('training_allocation_results.csv', index=False)
    print(f"\nResults saved to 'training_allocation_results.csv'")
    
    return results_df


# ============================================================================
# STEP 6: IMPACT ANALYSIS
# ============================================================================

def analyze_impact(results_df, employees_df):
    """Analyze the expected impact of the training allocation"""
    
    print("\n" + "="*80)
    print("IMPACT ANALYSIS")
    print("="*80)
    
    # Calculate expected improvement in ratings
    total_improvement = results_df['Expected_Improvement'].sum()
    avg_improvement = results_df['Expected_Improvement'].mean()
    
    # Current average rating of selected employees
    selected_emp_ids = results_df['Employee_ID'].tolist()
    selected_current_ratings = employees_df[employees_df['EmpID'].isin(selected_emp_ids)]['Current Employee Rating']
    
    current_avg_rating = selected_current_ratings.mean()
    expected_new_avg_rating = current_avg_rating + avg_improvement
    
    print(f"\nPERFORMANCE IMPROVEMENT PROJECTION:")
    print(f"   Current avg rating of selected employees: {current_avg_rating:.2f}")
    print(f"   Expected avg rating after training: {expected_new_avg_rating:.2f}")
    print(f"   Overall improvement: +{avg_improvement:.2f} points ({(avg_improvement/current_avg_rating)*100:.1f}%)")
    
    # ROI Analysis
    total_cost = results_df['Training_Cost'].sum()
    cost_per_improvement_point = total_cost / total_improvement if total_improvement > 0 else 0
    
    print(f"\nRETURN ON INVESTMENT:")
    print(f"   Total investment: ${total_cost:,.2f}")
    print(f"   Total expected improvement points: {total_improvement:.2f}")
    print(f"   Cost per improvement point: ${cost_per_improvement_point:,.2f}")
    
    # Employees by improvement potential
    high_impact = len(results_df[results_df['Expected_Improvement'] >= 2.0])
    medium_impact = len(results_df[(results_df['Expected_Improvement'] >= 1.0) & 
                                   (results_df['Expected_Improvement'] < 2.0)])
    low_impact = len(results_df[results_df['Expected_Improvement'] < 1.0])
    
    print(f"\nIMPROVEMENT POTENTIAL BREAKDOWN:")
    print(f"   High impact (>= 2.0 improvement): {high_impact} employees")
    print(f"   Medium impact (1.0-2.0): {medium_impact} employees")
    print(f"   Low impact (<1.0): {low_impact} employees")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    
    print("\n" + "="*80)
    print(f"   Optimization: Fast mode (1% optimality gap, multi-threaded)")
    print("PRESCRIPTIVE ANALYTICS: TRAINING ALLOCATION OPTIMIZATION")
    print("Using Integer Linear Programming (ILP)")
    print("="*80)
    
    # Configuration parameters
    TRAINING_BUDGET = 50000  # Maximum budget for training
    MAX_CAPACITY_PER_PROGRAM = 20  # Maximum employees per training program
    
    print(f"\nCONFIGURATION:")
    print(f"   Training Budget: ${TRAINING_BUDGET:,}")
    print(f"   Max Capacity per Program: {MAX_CAPACITY_PER_PROGRAM} employees")
    
    # Step 1: Load and prepare data
    employees_df, training_df = load_and_prepare_data()
    training_programs_df = extract_training_programs(training_df)
    
    # Step 2 & 3: Formulate optimization problem
    prob, x, employees, programs, improvement_matrix = formulate_optimization_problem(
        employees_df, 
        training_programs_df,
        budget=TRAINING_BUDGET,
        max_capacity_per_program=MAX_CAPACITY_PER_PROGRAM
    )
    
    # Step 4: Solve the problem
    if solve_optimization(prob):
        # Step 5: Extract results
        results_df = extract_results(
            prob, x, employees, programs, 
            employees_df, training_programs_df, 
            improvement_matrix
        )
        
        # Step 6: Analyze impact
        analyze_impact(results_df, employees_df)
        
        print("\n" + "="*80)
        print("OPTIMIZATION COMPLETED SUCCESSFULLY")
        print("="*80)
    else:
        print("\nOptimization failed - please check constraints and data")


if __name__ == "__main__":
    main()
