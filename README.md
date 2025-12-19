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

### 5. Results Export

CSV file containing complete training allocation results for implementation and tracking purposes.

---

## Technical Requirements

### Dependencies

```
- Python 3.8+
- pandas
- numpy
- PuLP (Linear Programming solver)
```

### Installation

```bash
pip install pandas numpy pulp
```

### Execution

```bash
python main.py
```

---

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

The model can handle large employee populations and multiple training programs efficiently through optimization algorithms.

---

## Limitations and Considerations

1. **Historical Data Dependency**: Training effectiveness estimates rely on historical outcome data quality
2. **Static Parameters**: Model assumes fixed training costs and capacities
3. **Improvement Estimation**: Actual performance improvements may vary from projected values
4. **Temporal Factors**: Does not account for timing constraints or employee availability
5. **Program Prerequisites**: Assumes all employees are qualified for all training programs

---

## Future Enhancements

1. Multi-period optimization for long-term training planning
2. Dynamic budget allocation across fiscal quarters
3. Integration of employee career progression paths
4. Consideration of team composition and organizational structure
5. Incorporation of skill gap analysis and competency frameworks
6. Real-time sensitivity analysis for parameter adjustments

---

## Conclusion

This prescriptive analytics solution demonstrates how Integer Linear Programming can be effectively applied to human resource management challenges. By mathematically optimizing training allocation decisions, organizations can maximize employee performance improvement while ensuring fair, cost-effective, and strategically aligned training investments.

The model provides a data-driven, transparent framework for resource allocation that balances multiple competing objectives and constraints, ultimately supporting organizational goals of workforce development and performance excellence.

---

## References

1. Linear Programming and Optimization Theory
2. Human Resource Analytics and Workforce Planning
3. Employee Training and Development Best Practices
4. Fairness and Equity in Algorithmic Decision-Making
5. Operations Research Applications in HR Management

---

## Project Information

**Course**: Prescriptive Data Science  
**Implementation**: Python with PuLP Optimization Library  
**Problem Type**: Integer Linear Programming (ILP)  
**Application Domain**: Human Resource Management

---

## Author Notes

This implementation serves as a demonstration of prescriptive analytics techniques applied to real-world business problems. The model can be adapted and extended based on specific organizational requirements and constraints.
