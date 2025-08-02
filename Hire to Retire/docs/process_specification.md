# Process Specification – Hire to Retire
spec_version: "1.0"
last_updated: "2025-08-01"
author: Process Specwriter

## 1. Business Problem & Goals
```yaml
problem_statement: >
  Large organizations struggle with inefficient HR processes across the employee lifecycle,
  resulting in extended time-to-fill (40+ days), high first-year turnover (30%), poor
  candidate experience (40% abandonment), compliance gaps (10-15%), and excessive HR
  operational costs ($30,000 per employee annually). The fragmented nature of HR systems
  and lack of process visibility prevents organizations from optimizing their workforce
  management and achieving strategic HR objectives.

goals:
  - Reduce time-to-fill from 40+ days to <30 days for standard roles
  - Lower first-year turnover from 30% to <15%
  - Improve satisfaction scores to >80% with <25% candidate abandonment
  - Achieve >95% compliance rate across all HR processes
  - Reduce HR operational costs by 30% through automation
```

## 2. Process Context
```yaml
industry: "Cross-Industry HR Services"
geography: "Global (New York, London, Singapore, Sydney, Berlin)"
regulatory_drivers:
  - "GDPR"
  - "SOX"
  - "EEO"
  - "Local labor laws"
time_horizon_years: 2
expected_cases: 10000
case_distribution:
  recruitment_only: 9000    # 90% rejection rate
  full_lifecycle: 1000      # 10% hired
  active_employees: 250     # Currently employed
  exits: 50                 # Left organization
```

## 3. Process Flow Definition
### 3.1 Activities
```yaml
activities:
  # Recruitment Phase
  - id: A1
    name: "Job Posted"
    mandatory: true
    typical_duration_hours: 0.5
    responsible_roles: ["Sarah", "Mike", "Emma"]
    performed_by: "XYZ"
    
  - id: A2
    name: "Application Received"
    mandatory: true
    typical_duration_hours: 0.25
    responsible_roles: ["Sarah", "Mike"]
    performed_by: "XYZ"
    
  - id: A3
    name: "Interview Completed"
    mandatory: false
    typical_duration_hours: 2-4
    responsible_roles: ["James", "Lisa", "Robert"]
    performed_by: "Joint"
    
  - id: A4
    name: "Offer Extended"
    mandatory: false
    typical_duration_hours: 1
    responsible_roles: ["Sarah", "Emma"]
    performed_by: "Joint"
    
  - id: A5
    name: "Offer Accepted"
    mandatory: false
    typical_duration_hours: 0.25
    responsible_roles: ["Sarah", "Mike"]
    performed_by: "XYZ"
    
  # Onboarding Phase
  - id: A6
    name: "Onboarding Started"
    mandatory: false
    typical_duration_hours: 4
    responsible_roles: ["Emma", "Mike"]
    performed_by: "XYZ"
    
  - id: A7
    name: "Equipment Assigned"
    mandatory: false
    typical_duration_hours: 2
    responsible_roles: ["David", "Jennifer"]
    performed_by: "Customer"
    
  - id: A8
    name: "Probation Completed"
    mandatory: false
    typical_duration_hours: 1
    responsible_roles: ["James", "Lisa"]
    performed_by: "Joint"
    
  # Employment Phase
  - id: A9
    name: "Performance Review"
    mandatory: false
    typical_duration_hours: 2
    responsible_roles: ["James", "Lisa", "Robert"]
    performed_by: "Customer"
    
  - id: A10
    name: "Promotion Approved"
    mandatory: false
    typical_duration_hours: 1
    responsible_roles: ["Robert", "Lisa"]
    performed_by: "Joint"
    
  - id: A11
    name: "Leave Requested"
    mandatory: false
    typical_duration_hours: 0.25
    responsible_roles: ["Sarah", "Emma"]
    performed_by: "XYZ"
    
  - id: A12
    name: "Leave Approved"
    mandatory: false
    typical_duration_hours: 0.25
    responsible_roles: ["James", "Lisa"]
    performed_by: "Customer"
    
  - id: A13
    name: "Training Completed"
    mandatory: false
    typical_duration_hours: 8-40
    responsible_roles: ["Jennifer", "Michael"]
    performed_by: "XYZ"
    
  # Exit Phase
  - id: A14
    name: "Resignation Submitted"
    mandatory: false
    typical_duration_hours: 0.5
    responsible_roles: ["Sarah", "Emma"]
    performed_by: "Joint"
    
  - id: A15
    name: "Employment Ended"
    mandatory: false
    typical_duration_hours: 4
    responsible_roles: ["Sarah", "Mike", "David"]
    performed_by: "XYZ"
    
  # Rejection Activities
  - id: R1
    name: "Application Rejected"
    mandatory: false
    typical_duration_hours: 0.25
    responsible_roles: ["Sarah", "Mike"]
    performed_by: "XYZ"
    
  - id: R2
    name: "Interview Failed"
    mandatory: false
    typical_duration_hours: 0.5
    responsible_roles: ["James", "Lisa"]
    performed_by: "Joint"
    
  - id: R3
    name: "Offer Rejected"
    mandatory: false
    typical_duration_hours: 0.25
    responsible_roles: ["Sarah"]
    performed_by: "XYZ"
    
  - id: R4
    name: "Probation Failed"
    mandatory: false
    typical_duration_hours: 2
    responsible_roles: ["James", "Lisa", "Sarah"]
    performed_by: "Joint"

# Define closing activities
closing_activities: ["Employment Ended", "Application Rejected", "Interview Failed", "Offer Rejected", "Probation Failed"]
```

### 3.2 Sequencing & Gateways
```yaml
flows:
  # Recruitment flows
  - from: A1
    to: A2
    probability: 1.0
    
  - from: A2
    to: A3
    probability: 0.4    # 40% pass screening
    
  - from: A2
    to: R1
    probability: 0.6    # 60% rejected at screening
    
  - from: A3
    to: A4
    probability: 0.3    # 30% receive offer
    
  - from: A3
    to: R2
    probability: 0.7    # 70% fail interview
    
  - from: A4
    to: A5
    probability: 0.85   # 85% accept offer
    
  - from: A4
    to: R3
    probability: 0.15   # 15% reject offer
    
  # Onboarding flows
  - from: A5
    to: A6
    probability: 1.0
    
  - from: A6
    to: A7
    probability: 1.0
    
  - from: A7
    to: A8
    probability: 0.9    # 90% pass probation
    
  - from: A7
    to: R4
    probability: 0.1    # 10% fail probation
    
  # Employment flows (recurring activities)
  - from: A8
    to: A9
    probability: 1.0    # All employees get reviews
    
  - from: A9
    to: A10
    probability: 0.15   # 15% promoted
    
  - from: A9
    to: A11
    probability: 0.8    # Many request leave after reviews
    
  - from: A11
    to: A12
    probability: 0.95   # 95% approved
    
  - from: A8
    to: A13
    probability: 0.6    # 60% take training
    
  # Exit flows
  - from: A8
    to: A14
    probability: 0.2    # 20% annual turnover
    
  - from: A14
    to: A15
    probability: 1.0
    
  # Rework loops
  - from: A3
    to: A3
    probability: 0.25   # Interview rescheduling
    
  - from: A4
    to: A4
    probability: 0.15   # Offer negotiation loops
```

### 3.3 Timing Rules
```yaml
business_hours:
  start: 9
  end: 18
  working_days: [Mon, Tue, Wed, Thu, Fri]
  
sla_hours:
  - activity: "Interview Completed"
    max_time: 336      # 14 days
  - activity: "Offer Extended"
    max_time: 120      # 5 days after interview
  - activity: "Equipment Assigned"
    max_time: 24       # 1 day after start
  - activity: "Leave Approved"
    max_time: 24       # 1 day response
```

## 4. Bottlenecks & Error Patterns
```yaml
bottlenecks:
  - name: "Interview Scheduling Delays"
    affected_activities: ["A3"]
    slow_resource: "Peter"
    performance_factor: 0.7    # 30% slower
    occurrence_rate: 0.3       # 30% of interviews
    
  - name: "Equipment Provisioning Delays"
    affected_activities: ["A7"]
    slow_resource: "David"
    performance_factor: 0.6    # 40% slower
    occurrence_rate: 0.2       # 20% of new hires
    
  - name: "Review Processing Delays"
    affected_activities: ["A9"]
    slow_resource: "Robert"
    performance_factor: 0.5    # 50% slower
    occurrence_rate: 0.35      # 35% of reviews
    
  - name: "System Integration Delays"
    affected_activities: ["A2", "A6", "A7", "A15"]
    slow_resource: "System"
    performance_factor: 0.3    # 70% slower
    occurrence_rate: 0.25      # 25% of transactions

error_patterns:
  - name: "Background Check Failures"
    trigger_activity: "Offer Extended"
    rework_probability: 0.05
    max_loops: 1
    
  - name: "Documentation Missing"
    trigger_activity: "Onboarding Started"
    rework_probability: 0.2
    max_loops: 2
    
  - name: "System Access Failures"
    trigger_activity: "Equipment Assigned"
    rework_probability: 0.25
    max_loops: 3
    
  - name: "Review Calibration Required"
    trigger_activity: "Performance Review"
    rework_probability: 0.1
    max_loops: 2
```

## 5. Case-Level Attributes
```yaml
case_attributes:
  - name: "Department"
    values: ["Sales", "Engineering", "HR", "Finance", "Operations", "Marketing"]
    distribution: [0.25, 0.3, 0.1, 0.15, 0.15, 0.05]
    
  - name: "Location"
    values: ["New York", "London", "Singapore", "Sydney", "Berlin"]
    distribution: [0.3, 0.25, 0.2, 0.15, 0.1]
    
  - name: "JobLevel"
    type: "numeric"
    range: [1, 10]
    distribution: "normal"
    mean: 4
    
  - name: "EmploymentType"
    values: ["Full-time", "Part-time", "Contract"]
    distribution: [0.8, 0.1, 0.1]
    
  - name: "RecruitmentSource"
    values: ["Internal", "External", "Referral", "Agency"]
    distribution: [0.1, 0.5, 0.25, 0.15]
    
  - name: "CurrentSalary"
    type: "numeric"
    unit: "USD"
    range: [40000, 250000]
    skew: "right"
    
  - name: "PerformanceRating"
    type: "numeric"
    range: [1, 5]
    distribution: "normal"
    mean: 3.5
```

## 6. Output Format Requirements
```yaml
output_format:
  required_fields: ["CaseId", "ActivityName", "ActivityTime", "Resource", "Department", "Location"]
  datetime_format: "YYYY-MM-DD HH:MM:SS"
  json_structure: "cases_with_embedded_activities"
  case_id_format: "HR{year}_{employeeID}"
  employee_id_format: "E{6-digit}"
```

## 7. KPIs to Showcase
```yaml
kpis:
  - name: "Time to Fill"
    formula: "Days from Job Posted to Offer Accepted"
    target_days: 30
    current_average: 45
    
  - name: "First Year Retention Rate"
    formula: "(Employees staying 12+ months) / (Total hired)"
    target_percentage: 85
    current_percentage: 70
    
  - name: "Time to Productivity"
    formula: "Days from Onboarding Started to full productivity"
    target_days: 90
    current_average: 120
    
  - name: "Offer Acceptance Rate"
    formula: "(Offers Accepted) / (Offers Extended)"
    target_percentage: 85
    current_percentage: 85
    
  - name: "Process Compliance Rate"
    formula: "(Cases following standard flow) / (Total cases)"
    target_percentage: 95
    current_percentage: 80
```

## 8. Assumptions & Synthetic Details
| # | Topic | Assumption | Rationale |
|---|-------|------------|-----------|
|A1|Working hours|09:00-18:00 local|Common business hours globally|
|A2|Probation period|90 days standard|Industry standard for most roles|
|A3|Review frequency|Annual reviews|Most common review cycle|
|A4|Notice period|14-90 days by level|Standard practice varies by seniority|
|A5|Interview stages|Combined into single activity|Simplifies process tracking|
|A6|Retirement age|65 or 30 years service|Common retirement eligibility|
|A7|Leave quota|15-25 days annually|Standard PTO allowance|
|A8|Training frequency|2-3 programs per year|Typical L&D engagement|

## 9. Open Questions (if any)
None - specification is complete based on provided documentation.