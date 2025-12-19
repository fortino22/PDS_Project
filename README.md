# Training Allocation Optimization Using Linear Programming

## Executive Summary

This project implements a prescriptive analytics solution for optimal employee training allocation using Integer Linear Programming (ILP). The system determines which employees should receive training to maximize overall performance improvement while respecting organizational constraints including budget limitations, capacity restrictions, and demographic fairness.

---

## Problem Statement

### Business Context

Organizations face a critical challenge in allocating limited training resources to maximize employee performance. With constrained budgets and training capacity, management must make strategic decisions about which employees should receive training to achieve optimal organizational impact.

### Objective

Develop an optimization model that selects employees for training programs to maximize expected improvement in employee performance ratings while adhering to organizational constraints and ensuring fair allocation across demographic groups.

---

## Mathematical Formulation

### Decision Variables

Let **x[i,j]** be a binary decision variable:

```
x[i,j] = {
    1, if employee i is assigned to training program j
    0, otherwise
}
```

Where:

- i ∈ E (set of all eligible employees)
- j ∈ P (set of all training programs)

### Objective Function

**Maximize:**

```
Z = Σ Σ (improvement_potential[i,j] × x[i,j])
    i∈E j∈P
```

The improvement potential is calculated as a weighted function of:

- Employee rating gap (5 - current_rating) × 0.40
- Employee engagement score (normalized) × 0.25
- Employee satisfaction score (normalized) × 0.15
- Training program effectiveness (historical) × 0.20

### Constraints

#### 1. Budget Constraint

```
Σ Σ (cost[j] × x[i,j]) ≤ B
i∈E j∈P
```

Where B is the total allocated training budget.

#### 2. Training Assignment Constraint

Each employee can receive at most one training program:

```
Σ x[i,j] ≤ 1,  ∀ i ∈ E
j∈P
```

#### 3. Capacity Constraint

Each training program has a maximum capacity:

```
Σ x[i,j] ≤ C[j],  ∀ j ∈ P
i∈E
```

Where C[j] is the maximum capacity for training program j.

#### 4. Eligibility Constraint

Only employees with active employment status are eligible:

```
i ∈ E ⟹ status[i] = "Active"
```

#### 5. Demographic Fairness Constraint

Ensure proportional representation across demographic groups:

```
Σ   Σ x[i,j] ≥ ⌊proportion[g] × C_total × α⌋,  ∀ g ∈ G
i∈G_g j∈P
```

Where:

- G is the set of demographic groups
- G_g is the subset of employees in group g
- proportion[g] is the proportion of group g in total eligible employees
- α is the fairness threshold parameter (default: 0.5)

---

## Methodology

### Data Sources

The analysis utilizes three primary datasets:

1. **Employee Data**: Demographics, employment status, department, job title, performance scores, and current ratings
2. **Training Records**: Historical training participation, program types, costs, duration, and outcomes
3. **Engagement Survey Data**: Employee engagement scores, satisfaction scores, and work-life balance ratings

### Implementation Approach

#### Phase 1: Data Preprocessing

- Filter employees by active employment status
- Merge employee data with engagement survey results
- Handle missing values using appropriate imputation strategies
- Pre-filter employees with improvement potential (current rating < 5)
- Extract unique training programs with average costs and historical effectiveness

#### Phase 2: Parameter Calculation

Calculate improvement potential for each employee-training pair based on:

- Current performance gap
- Employee engagement and satisfaction levels
- Historical training program success rates

#### Phase 3: Model Formulation

- Define binary decision variables for all employee-training combinations
- Construct objective function to maximize total improvement
- Implement all constraints (budget, capacity, eligibility, fairness)

#### Phase 4: Optimization

- Solve the Integer Linear Programming problem using PuLP solver with CBC algorithm
- Utilize optimized solver parameters for faster computation:
- Verify solution optimality and feasibility

#### Phase 5: Results Analysis

- Extract optimal training assignments
- Analyze demographic and departmental distribution
- Calculate return on investment (ROI)
- Project performance improvement impact

---

## Key Parameters

| Parameter                                  | Default Value | Description                                          |
| ------------------------------------------ | ------------- | ---------------------------------------------------- |
| Training Budget                            | $50,000       | Maximum total expenditure for training programs      |
| Max Capacity per Program                   | 20 employees  | Maximum number of participants per training session  |
| Improvement Weight - Rating Gap            | 0.40          | Weight assigned to performance improvement potential |
| Improvement Weight - Engagement            | 0.25          | Weight assigned to employee engagement factor        |
| Improvement Weight - Satisfaction          | 0.15          | Weight assigned to employee satisfaction factor      |
| Improvement Weight - Program Effectiveness | 0.20          | Weight assigned to historical training success       |
| Fairness Threshold                         | 0.50          | Minimum proportional representation factor           |
| Solver Time Limit                          | 300 seconds   | Maximum solving time (5 minutes)                     |
| Optimality Gap Tolerance                   | 1%            | Acceptable deviation from theoretical optimal        |
| CPU Threads                                | 4             | Number of parallel processing threads                |

---

## Expected Outputs

### 1. Optimal Training Allocation

A detailed list of selected employees with:

- Employee identification and demographic information
- Assigned training program
- Current performance rating
- Expected improvement score
- Training cost and duration

### 2. Summary Statistics

- Total number of employees selected
- Total training cost utilized
- Total expected performance improvement
- Average improvement per employee
- Optimal objective function value

### 3. Distribution Analysis

- Training program enrollment distribution
- Demographic representation analysis
- Departmental coverage statistics

### 4. Impact Projection

- Current average rating of selected employees
- Expected average rating post-training
- Percentage improvement in performance
- Return on investment metrics
- Cost per improvement point

## Solution Benefits

### 1. Optimality

The Integer Linear Programming approach guarantees an optimal solution within the defined constraint space, ensuring maximum performance improvement for the allocated budget.

### 2. Fairness

Demographic balance constraints prevent discrimination and ensure equitable training opportunities across all employee groups.

### 3. Cost Efficiency

Budget constraints and ROI analysis ensure training investments deliver maximum value while remaining within financial limitations.

### 4. Transparency

The mathematical formulation provides clear, auditable decision criteria that can be explained to stakeholders and justified to management.

### 5. Scalability

The model efficiently handles large employee populations (2000+) through:

- Pre-filtering to focus on employees with improvement potential
- Multi-threaded parallel processing
- Optimality gap tolerance for faster convergence
- Typical solving time under 5 minutes for real-world datasets

---

## Limitations and Considerations

1. **Historical Data Dependency**: Training effectiveness estimates rely on historical outcome data quality
2. **Static Parameters**: Model assumes fixed training costs and capacities
3. **Improvement Estimation**: Actual performance improvements may vary from projected values
4. **Temporal Factors**: Does not account for timing constraints or employee availability
5. **Program Prerequisites**: Assumes all employees are qualified for all training programs
6. **Optimality Gap**: Solution is within 1% of theoretical optimal for computational efficiency
7. **Pre-filtering**: Focuses only on employees with current rating < 5 (excludes top performers)

---

## Future Enhancements

1. Multi-period optimization for long-term training planning
2. Dynamic budget allocation across fiscal quarters
3. Integration of employee career progression paths
4. Consideration of team composition and organizational structure
5. Incorporation of skill gap analysis and competency frameworks
6. Real-time sensitivity analysis for parameter adjustments

---

## Sample Execution Results

### Dataset Statistics

```
Total employee records: 3,002
Active employees eligible for training: 2,458
Employees with improvement potential (rating < 5): 2,236
Sample size for optimization: 100 employees
Training programs available: 5
```

### Training Programs Identified

| Program                | Duration (Days) | Cost ($) | Type     | Effectiveness |
| ---------------------- | --------------- | -------- | -------- | ------------- |
| Communication Skills   | 2.95            | 542.38   | Internal | 53.8%         |
| Customer Service       | 2.96            | 567.39   | Internal | 52.7%         |
| Leadership Development | 3.03            | 564.29   | Internal | 52.8%         |
| Project Management     | 3.03            | 563.73   | External | 47.9%         |
| Technical Skills       | 2.91            | 557.98   | External | 43.9%         |

### Optimization Results

**Problem Size**: 500 binary decision variables (100 employees × 5 programs)

**Solution Status**: Optimal (found in < 5 seconds)

**Selected Employees**: 89 out of 100

**Budget Utilization**: $49,777.73 out of $50,000.00 (99.6%)

**Total Expected Improvement**: 118.61 rating points

**Average Improvement per Employee**: 1.33 points

### Training Program Allocation

| Program                | Employees Selected | Capacity Utilization |
| ---------------------- | ------------------ | -------------------- |
| Customer Service       | 20                 | 100%                 |
| Project Management     | 20                 | 100%                 |
| Leadership Development | 20                 | 100%                 |
| Communication Skills   | 20                 | 100%                 |
| Technical Skills       | 9                  | 45%                  |

### Demographic Distribution

| Gender | Employees Selected | Percentage |
| ------ | ------------------ | ---------- |
| Female | 48                 | 53.9%      |
| Male   | 41                 | 46.1%      |

### Department Distribution (Top 5)

| Department           | Employees Selected |
| -------------------- | ------------------ |
| Production           | 49                 |
| IT/IS                | 16                 |
| Sales                | 13                 |
| Software Engineering | 8                  |
| Admin Offices        | 3                  |

### Impact Analysis

**Performance Improvement Projection**:

- Current average rating: 2.56
- Expected average rating after training: 3.89
- Overall improvement: +1.33 points (52.0% increase)

**Return on Investment**:

- Total investment: $49,777.73
- Total expected improvement: 118.61 points
- Cost per improvement point: $419.67

**Improvement Potential Breakdown**:

- High impact (≥ 2.0 improvement): 2 employees (2.2%)
- Medium impact (1.0-2.0): 77 employees (86.5%)
- Low impact (< 1.0): 10 employees (11.2%)

### Top 10 Selected Employees by Expected Improvement

| Employee ID | Name             | Current Rating | Engagement | Training Program       | Expected Improvement |
| ----------- | ---------------- | -------------- | ---------- | ---------------------- | -------------------- |
| 2450        | Vivian Bright    | 1              | 5          | Customer Service       | 2.05                 |
| 2891        | Addyson Pollard  | 1              | 5          | Leadership Development | 2.02                 |
| 3287        | Litzy Arias      | 1              | 5          | Customer Service       | 1.99                 |
| 2279        | Walter Immediato | 1              | 2          | Leadership Development | 1.96                 |
| 3558        | Mildred Gentry   | 1              | 2          | Customer Service       | 1.96                 |
| 2681        | Jaime Greer      | 1              | 3          | Customer Service       | 1.95                 |
| 2265        | Halle Pena       | 1              | 2          | Communication Skills   | 1.93                 |
| 3687        | Bria Mcpherson   | 1              | 2          | Leadership Development | 1.93                 |
| 2909        | Nancy Barrett    | 1              | 2          | Leadership Development | 1.93                 |
| 3700        | Brenden Nash     | 1              | 4          | Technical Skills       | 1.92                 |

### Key Insights

1. **Optimal Resource Utilization**: The model utilized 99.6% of the available budget while selecting 89 employees
2. **Balanced Allocation**: Four out of five training programs reached full capacity (20 employees each)
3. **Demographic Fairness**: Gender distribution (54% Female, 46% Male) reflects proportional representation
4. **High Impact Focus**: 88.7% of selected employees show medium to high improvement potential
5. **Performance Gain**: Expected 52% improvement in employee ratings post-training
6. **Cost Efficiency**: Each improvement point costs $419.67, demonstrating efficient resource allocation

---

## Conclusion

This prescriptive analytics solution demonstrates how Integer Linear Programming can be effectively applied to human resource management challenges. By mathematically optimizing training allocation decisions, organizations can maximize employee performance improvement while ensuring fair, cost-effective, and strategically aligned training investments.

The model provides a data-driven, transparent framework for resource allocation that balances multiple competing objectives and constraints, ultimately supporting organizational goals of workforce development and performance excellence.

The sample execution results validate the model's effectiveness, achieving 99.6% budget utilization, demographic fairness, and a projected 52% improvement in employee ratings for selected participants.

---
