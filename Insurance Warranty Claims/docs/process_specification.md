# Process Specification – Automotive Warranty Claims Processing
spec_version: "1.2"
last_updated: "2025-08-22"
author: Process Specwriter

## 1. Business Problem & Goals
```yaml
problem_statement: >
  Insurance companies processing automotive warranty claims face challenges with multiple disparate IT systems 
  from various acquisitions. Currently, 40% of claims achieve straight-through processing, while the 
  remaining 60% require manual intervention. Limited visibility into fraud patterns, dealer performance issues, 
  and claims trends leads to delayed fraud detection, inconsistent dealer performance, and 
  suboptimal claim processing efficiency.

goals:
  - Increase straight-through processing rate from 40% to 60% within 6 months
  - Reduce fraud losses by 2-3% through pattern detection and real-time flagging
  - Decrease average claim processing time by 30% through bottleneck identification
  - Improve dealer performance visibility and standardization across regions
  - Enable proactive trend analysis for recurring repair patterns
```

## 2. Process Context
```yaml
industry: "Insurance - Automotive Warranty Claims"
geography: "United States (multi-state operations)"
regulatory_drivers:
  - "State Insurance Regulations"
  - "Consumer Protection Laws"
  - "Automotive Warranty Standards"
  - "Anti-Fraud Compliance"
time_horizon_years: 2
expected_cases: 1500  # 3-month sample for demo
business_hours:
  start: 8
  end: 18
  working_days: [Mon, Tue, Wed, Thu, Fri, Sat]  # Dealers open Saturdays
```

## 3. Process Flow Definition
### 3.1 Activities
```yaml
activities:
  - name: "First Notice of Loss"
    mandatory: true
    typical_duration_hours: 0.25
    responsible_roles: ["DealerRep1", "DealerRep2", "DealerRep3", "OnlinePortal"]
    description: "Initial warranty claim submission from dealer or customer"
    
  - name: "Verify Coverage"
    mandatory: true
    typical_duration_hours: 0.5
    responsible_roles: ["CoverageAnalyst1", "CoverageAnalyst2", "CoverageAnalyst3", "AutoValidator"]
    description: "Verification of warranty contract coverage and claim validity"
    
  - name: "Damage Assessment"
    mandatory: false
    typical_duration_hours: 4-24
    responsible_roles: ["DealerTech1", "DealerTech2", "DealerTech3", "DealerTech4"]
    description: "Technical assessment of vehicle damage and required repairs"
    
  - name: "Request Documentation"
    mandatory: false
    typical_duration_hours: 1-2
    responsible_roles: ["PartsSpecialist1", "PartsSpecialist2", "PartsSpecialist3", "PartsCatalog"]
    description: "Request and validate parts documentation and pricing from dealer"
    
  - name: "Liability Determination"
    mandatory: false
    typical_duration_hours: 0.5-1
    responsible_roles: ["LaborAnalyst1", "LaborAnalyst2", "LaborAnalyst3"]
    description: "Determine warranty liability and coverage for labor costs"
    
  - name: "Claim Investigation"
    mandatory: false
    typical_duration_hours: 2-6
    responsible_roles: ["TechExpert1", "TechExpert2", "SeniorReviewer"]
    description: "Detailed investigation of complex or high-value warranty claims"
    
  - name: "Assignment"
    mandatory: false
    typical_duration_hours: 1-3
    responsible_roles: ["FraudAnalyst", "RiskTeam", "AutoFraudSystem"]
    description: "Assignment to fraud specialist for pattern analysis and risk scoring"
    
  - name: "Approve Settlement"
    mandatory: false
    typical_duration_hours: 0.25
    responsible_roles: ["ApprovalManager", "AutoApproval", "SeniorApprover"]
    description: "Settlement approved for payment to dealer"
    
  - name: "Resolution and Settlement"
    mandatory: false
    typical_duration_hours: 0.5
    responsible_roles: ["DenialSpecialist", "Manager", "AutoDenial"]
    description: "Final resolution - denial with reason code or settlement offer"
    
  - name: "Payment Processing"
    mandatory: false
    typical_duration_hours: 0.25
    responsible_roles: ["PaymentProcessor", "FinanceTeam", "AutoPayment"]
    description: "Process payment authorization to dealer"
    
  - name: "Generate Payment Confirmation"
    mandatory: false
    typical_duration_hours: 2-4
    responsible_roles: ["QualityAuditor", "SeniorAuditor", "ComplianceTeam"]
    description: "Generate payment confirmation and quality audit documentation"
    
  - name: "Claim Closure"
    mandatory: false
    typical_duration_hours: 1-3
    responsible_roles: ["CoverageAnalyst1", "CoverageAnalyst2", "CoverageAnalyst3"]
    description: "Final closure of claim with all documentation complete"

# Define closing activities explicitly
closing_activities: ["Approve Settlement", "Resolution and Settlement", "Payment Processing", "Claim Closure"]
```

### 3.2 Sequencing & Gateways
```yaml
flows:
  # Main flow
  - from: "First Notice of Loss"
    to: "Verify Coverage"
    probability: 1.0
    description: "All claims go through initial validation"
    
  # After initial validation
  - from: "Verify Coverage"
    to: "Damage Assessment"
    probability: 0.55
    description: "Claims requiring dealer diagnosis"
    
  - from: "Verify Coverage"
    to: "Approve Settlement"
    probability: 0.40
    description: "Straight-through processing - auto-approved"
    
  - from: "Verify Coverage"
    to: "Resolution and Settlement"
    probability: 0.03
    description: "Immediate denial - invalid contract"
    
  - from: "Verify Coverage"
    to: "Claim Closure"
    probability: 0.02
    description: "Incomplete submission - rework needed"
    
  # From dealer diagnosis
  - from: "Damage Assessment"
    to: "Request Documentation"
    probability: 0.85
    description: "Parts review needed"
    
  - from: "Damage Assessment"
    to: "Liability Determination"
    probability: 0.10
    description: "Labor only claim"
    
  - from: "Damage Assessment"
    to: "Resolution and Settlement"
    probability: 0.05
    description: "Denied based on diagnosis"
    
  # From parts review
  - from: "Request Documentation"
    to: "Liability Determination"
    probability: 0.90
    description: "Labor estimation after parts"
    
  - from: "Request Documentation"
    to: "Resolution and Settlement"
    probability: 0.07
    description: "Denied - parts not covered"
    
  - from: "Request Documentation"
    to: "Claim Closure"
    probability: 0.03
    description: "Parts clarification needed"
    
  # From labor estimation
  - from: "Liability Determination"
    to: "Claim Investigation"
    probability: 0.25
    description: "Complex claims need technical review"
    
  - from: "Liability Determination"
    to: "Assignment"
    probability: 0.15
    description: "Suspicious patterns trigger fraud check"
    
  - from: "Liability Determination"
    to: "Approve Settlement"
    probability: 0.55
    description: "Standard approval"
    
  - from: "Liability Determination"
    to: "Resolution and Settlement"
    probability: 0.05
    description: "Denied - excessive labor"
    
  # From technical review
  - from: "Claim Investigation"
    to: "Assignment"
    probability: 0.20
    description: "Technical issues raise fraud concerns"
    
  - from: "Claim Investigation"
    to: "Approve Settlement"
    probability: 0.70
    description: "Approved after technical review"
    
  - from: "Claim Investigation"
    to: "Resolution and Settlement"
    probability: 0.08
    description: "Denied - technical grounds"
    
  - from: "Claim Investigation"
    to: "Claim Closure"
    probability: 0.02
    description: "More information needed"
    
  # From fraud check
  - from: "Assignment"
    to: "Approve Settlement"
    probability: 0.75
    description: "Cleared of fraud"
    
  - from: "Assignment"
    to: "Resolution and Settlement"
    probability: 0.20
    description: "Fraud detected - denied"
    
  - from: "Assignment"
    to: "Claim Closure"
    probability: 0.05
    description: "Additional verification needed"
    
  # From approval
  - from: "Approve Settlement"
    to: "Payment Processing"
    probability: 0.95
    description: "Payment processing"
    
  - from: "Approve Settlement"
    to: "Generate Payment Confirmation"
    probability: 0.05
    description: "Selected for quality audit"
    
  # From payment
  - from: "Payment Processing"
    to: "Generate Payment Confirmation"
    probability: 0.10
    description: "Random quality audit after payment"
    
  # Rework loops
  - from: "Claim Closure"
    to: "Verify Coverage"
    probability: 0.60
    description: "Resubmitted for validation"
    
  - from: "Claim Closure"
    to: "Damage Assessment"
    probability: 0.30
    description: "Additional diagnosis needed"
    
  - from: "Claim Closure"
    to: "Resolution and Settlement"
    probability: 0.10
    description: "Abandoned - claim denied"
```

### 3.3 Timing Rules
```yaml
sla_hours:
  - activity: "Verify Coverage"
    max_time: 1
    description: "Must complete initial validation within 1 hour"
    
  - activity: "Approve Settlement"
    max_time: 48
    description: "Decision within 48 hours of submission"
    
  - activity: "Payment Processing"
    max_time: 72
    description: "Payment within 72 hours of approval"
    
  - activity: "Assignment"
    max_time: 24
    description: "Fraud review completed within 24 hours"
```

## 4. Bottlenecks & Error Patterns
```yaml
bottlenecks:
  - name: "Slow Dealer Diagnosis"
    affected_activities: ["Damage Assessment"]
    slow_resource: "DealerTech3"
    performance_factor: 0.6  # 40% slower than average
    occurrence_rate: 0.20
    description: "Certain dealers consistently slow in providing diagnosis"
    
  - name: "Labor Review Delays"
    affected_activities: ["Liability Determination"]
    slow_resource: "LaborAnalyst1"
    performance_factor: 0.7  # 30% slower
    occurrence_rate: 0.25
    description: "Labor analyst bottleneck in labor hour reviews"
    
  - name: "Technical Review Backlog"
    affected_activities: ["Claim Investigation"]
    slow_resource: "TechExpert1"
    performance_factor: 0.5  # 50% slower due to volume
    occurrence_rate: 0.15
    description: "Limited technical experts create bottleneck"
    
  - name: "Fraud Investigation Queue"
    affected_activities: ["Assignment"]
    slow_resource: "FraudAnalyst"
    performance_factor: 0.6
    occurrence_rate: 0.30
    description: "Manual fraud reviews take significant time"

error_patterns:
  - name: "Claim Rework Loop"
    trigger_activity: "Verify Coverage"
    rework_probability: 0.02
    max_loops: 2
    description: "Missing information requires rework"
    
  - name: "Parts Clarification"
    trigger_activity: "Request Documentation"
    rework_probability: 0.03
    max_loops: 1
    description: "Incorrect part numbers or pricing"
    
  - name: "Fraud Verification Loop"
    trigger_activity: "Assignment"
    rework_probability: 0.05
    max_loops: 2
    description: "Additional documentation needed for fraud clearance"

fraud_patterns:
  - name: "Duplicate VIN Claims"
    indicator: "Same VIN multiple claims within 30 days"
    occurrence_rate: 0.02
    severity: "High"
    
  - name: "Excessive Labor Hours"
    indicator: "Labor hours >150% of standard"
    occurrence_rate: 0.03
    severity: "Medium"
    
  - name: "Unusual Part Combinations"
    indicator: "Unrelated parts in single claim"
    occurrence_rate: 0.01
    severity: "High"
    
  - name: "Dealer Pattern Anomaly"
    indicator: "Dealer claims 3x regional average"
    occurrence_rate: 0.015
    severity: "High"
```

## 5. Case-Level Attributes
```yaml
case_attributes:
  - name: "ClaimNumber"
    type: "identifier"
    format: "CLM2024_XXXXXX"
    description: "Unique claim identifier"
    
  - name: "VIN"
    type: "identifier"
    format: "17-character alphanumeric"
    description: "Vehicle Identification Number"
    
  - name: "VehicleMake"
    values: ["Ford", "Chevrolet", "Toyota", "Honda", "Nissan", "BMW", "Mercedes", "Audi", "Volkswagen", "Hyundai", "Kia", "Mazda", "Subaru", "Jeep", "Ram"]
    distribution: [0.15, 0.14, 0.12, 0.10, 0.08, 0.05, 0.04, 0.04, 0.04, 0.06, 0.05, 0.03, 0.03, 0.04, 0.03]
    description: "Vehicle manufacturer"
    
  - name: "VehicleModel"
    type: "text"
    description: "Specific vehicle model"
    
  - name: "VehicleYear"
    type: "numeric"
    range: [2019, 2024]
    description: "Model year of vehicle"
    
  - name: "Mileage"
    type: "numeric"
    range: [5000, 150000]
    skew: "right"
    description: "Vehicle mileage at time of claim"
    
  - name: "ContractType"
    values: ["DOWC", "TransmissionPlus", "TechShield", "PremiumCare", "BasicWarranty"]
    distribution: [0.25, 0.20, 0.20, 0.15, 0.20]
    description: "Type of warranty contract"
    
  - name: "DealerName"
    type: "text"
    description: "Name of dealer submitting claim"
    
  - name: "DealerRegion"
    values: ["Northeast", "Southeast", "Midwest", "Southwest", "West"]
    distribution: [0.20, 0.25, 0.20, 0.15, 0.20]
    description: "Geographic region of dealer"
    
  - name: "CustomerState"
    values: ["CA", "TX", "FL", "NY", "PA", "IL", "OH", "GA", "NC", "MI", "Other"]
    distribution: [0.12, 0.10, 0.08, 0.07, 0.06, 0.05, 0.05, 0.04, 0.04, 0.04, 0.35]
    description: "State of vehicle owner"
    
  - name: "ClaimValue"
    type: "numeric"
    range: [150, 15000]
    skew: "right"
    unit: "USD"
    description: "Total claimed amount"
    
  - name: "CustomerType"
    values: ["Individual", "Fleet", "Rental"]
    distribution: [0.75, 0.15, 0.10]
    description: "Type of customer"
    
  - name: "PriorClaims"
    type: "numeric"
    range: [0, 5]
    distribution: [0.60, 0.25, 0.10, 0.03, 0.01, 0.01]
    description: "Number of prior claims on this VIN"
    
  - name: "DaysInService"
    type: "numeric"
    range: [180, 2190]  # 6 months to 6 years
    description: "Days since vehicle first in service"
    
  - name: "PredictedFraudScore"
    type: "numeric"
    range: [0.0, 1.0]
    distribution_type: "beta"
    alpha: 2  # Skews toward lower values
    beta: 5   # Most cases are legitimate (80% below 0.3)
    description: "ML model's fraud probability prediction (0=legitimate, 1=fraud)"
```

## 6. Event-Level Attributes
```yaml
event_attributes:
  # Standard resource attribute
  - name: "Resource"
    applies_to: ["all"]
    description: "Person, dealer, or system performing the activity"
    
  # System tracking
  - name: "SystemUsed"
    applies_to: ["all"]
    values: ["System1_Legacy", "System2_SAP", "System3_Cloud", "System4_Manual"]
    distribution: [0.25, 0.30, 0.20, 0.25]
    description: "Which of 4 IT systems processed this step"
    
  # Dealer-specific attributes
  - name: "DealerRepairOrderNumber"
    applies_to: ["First Notice of Loss", "Damage Assessment"]
    type: "text"
    format: "RO-XXXXX"
    probability: 1.0
    description: "Dealer's internal repair order number"
    
  - name: "DiagnosisCode"
    applies_to: ["Damage Assessment"]
    values: ["ENG001", "TRANS002", "ELEC003", "SUSP004", "BRAKE005", "AC006", "OTHER"]
    distribution: [0.25, 0.20, 0.15, 0.10, 0.10, 0.10, 0.10]
    probability: 1.0
    description: "Standardized diagnosis code"
    
  # Parts attributes
  - name: "PartsCount"
    applies_to: ["Request Documentation"]
    type: "numeric"
    range: [1, 8]
    distribution: [0.40, 0.25, 0.15, 0.10, 0.05, 0.03, 0.01, 0.01]
    probability: 1.0
    description: "Number of parts to be replaced"
    
  - name: "PartsValue"
    applies_to: ["Request Documentation"]
    type: "numeric"
    range: [50, 5000]
    skew: "right"
    unit: "USD"
    probability: 1.0
    description: "Total value of parts"
    
  # Labor attributes
  - name: "LaborHoursClaimed"
    applies_to: ["Liability Determination"]
    type: "numeric"
    range: [0.5, 12]
    distribution_type: "normal"
    mean: 3.5
    probability: 1.0
    description: "Labor hours claimed by dealer"
    
  - name: "LaborHoursApproved"
    applies_to: ["Liability Determination"]
    type: "numeric"
    range: [0.5, 10]
    probability: 1.0
    description: "Labor hours approved by reviewer"
    
  - name: "LaborRate"
    applies_to: ["Liability Determination"]
    type: "numeric"
    range: [75, 150]
    unit: "USD/hour"
    probability: 1.0
    description: "Hourly labor rate"
    
  # Decision attributes
  - name: "ApprovalLevel"
    applies_to: ["Approve Settlement"]
    values: ["Auto", "Level1", "Level2", "Manager"]
    distribution: [0.40, 0.35, 0.20, 0.05]
    probability: 1.0
    description: "Approval authority level"
    
  - name: "DenialReason"
    applies_to: ["Resolution and Settlement"]
    values: ["NotCovered", "ExceedsLimit", "FraudSuspected", "IncompleteInfo", "PreExisting", "OutOfWarranty"]
    distribution: [0.30, 0.20, 0.15, 0.15, 0.10, 0.10]
    probability: 1.0
    description: "Reason for claim denial"
    
  # Fraud attributes
  - name: "FraudScore"
    applies_to: ["Assignment"]
    type: "numeric"
    range: [0, 100]
    probability: 1.0
    description: "Fraud risk score (0-100)"
    
  - name: "FraudIndicators"
    applies_to: ["Assignment"]
    values: ["DuplicateVIN", "ExcessiveLabor", "UnusualParts", "DealerAnomaly", "Multiple", "None"]
    distribution: [0.10, 0.15, 0.10, 0.10, 0.05, 0.50]
    probability: 1.0
    description: "Type of fraud indicator detected"
    
  # Payment attributes
  - name: "PaymentAmount"
    applies_to: ["Payment Processing"]
    type: "numeric"
    inherits_from_case: false
    probability: 1.0
    description: "Final payment amount authorized"
    
  - name: "PaymentMethod"
    applies_to: ["Payment Processing"]
    values: ["ACH", "Check", "Wire", "Credit"]
    distribution: [0.60, 0.25, 0.10, 0.05]
    probability: 1.0
    description: "Payment method to dealer"
    
  # Audit attributes
  - name: "AuditResult"
    applies_to: ["Generate Payment Confirmation"]
    values: ["Pass", "MinorIssue", "MajorIssue", "RequiresReview"]
    distribution: [0.70, 0.20, 0.07, 0.03]
    probability: 1.0
    description: "Result of quality audit"
    
  - name: "AuditNotes"
    applies_to: ["Generate Payment Confirmation"]
    type: "text"
    probability: 0.5
    sample_values: ["All documentation complete", "Minor discrepancy in parts pricing", "Labor hours need verification", "Potential duplicate claim"]
    description: "Auditor notes and findings"
    
  # Rework attributes
  - name: "ReworkReason"
    applies_to: ["Claim Closure"]
    values: ["MissingDocs", "IncorrectParts", "LaborDispute", "VerificationNeeded"]
    distribution: [0.40, 0.25, 0.20, 0.15]
    probability: 1.0
    description: "Reason for sending claim to rework"
    
  # Processing attributes
  - name: "Priority"
    applies_to: ["all"]
    values: ["Normal", "High", "Urgent"]
    distribution: [0.70, 0.25, 0.05]
    probability: 0.3
    description: "Processing priority (optional)"
    
  - name: "ProcessingNotes"
    applies_to: ["Verify Coverage", "Claim Investigation", "Assignment"]
    type: "text"
    probability: 0.4
    sample_values: ["Standard claim", "High value - requires review", "Suspicious pattern detected", "Previous claims on VIN", "Dealer under investigation"]
    description: "Internal processing notes"
```

## 7. Output Format Requirements
```yaml
output_format:
  required_fields: ["CaseId", "ActivityName", "ActivityTime", "Resource"]
  datetime_format: "YYYY-MM-DD HH:MM:SS"  # No 'T', use space
  json_structure: "cases_with_embedded_activities"
  csv_structure: "flattened_event_log"
  file_naming:
    json: "warranty_claims_historical.json"
    csv: "warranty_claims_historical.csv"
```

## 8. KPIs to Showcase
```yaml
kpis:
  - name: "Average Claim Processing Time"
    formula: "Avg(Payment Authorized Time - Claim Submitted Time)"
    target_hours: 48
    current_average: 72
    description: "End-to-end processing time"
    
  - name: "Straight-Through Processing Rate"
    formula: "(Claims Auto-Approved / Total Claims) * 100"
    target_percentage: 60
    current_percentage: 40
    description: "Percentage of claims processed without manual intervention"
    
  - name: "First-Time Approval Rate"
    formula: "(Claims Approved without Rework / Total Claims) * 100"
    target_percentage: 85
    current_percentage: 75
    description: "Claims approved on first submission"
    
  - name: "Fraud Detection Rate"
    formula: "(Fraud Cases Detected / Total Fraud Cases) * 100"
    target_percentage: 95
    current_percentage: 70
    description: "Effectiveness of fraud detection"
    
  - name: "Dealer Performance Score"
    formula: "Composite of approval rate, accuracy, and turnaround time"
    target_score: 85
    description: "Overall dealer performance metric"
    
  - name: "Cost per Claim"
    formula: "Total Processing Cost / Number of Claims"
    target_usd: 25
    current_usd: 35
    description: "Administrative cost per claim"
```

## 9. Assumptions & Synthetic Details
| # | Topic | Assumption | Rationale |
|---|-------|------------|-----------|
|A1|Business hours|08:00-18:00 Mon-Sat|Dealers typically open Saturdays|
|A2|Claim volume distribution|Higher on Mondays, lower on weekends|Industry standard pattern|
|A3|Fraud rate|3-5% of claims|Industry benchmark for warranty fraud|
|A4|Parts markup|15-25% above cost|Standard dealer markup range|
|A5|Labor rate|$75-150/hour|Regional variation in labor costs|
|A6|System distribution|25% each across 4 systems|Assuming equal legacy system usage|
|A7|Audit selection|10% random + high-value claims|Standard quality control practice|
|A8|Rework success rate|90% resolved on first rework|Based on insurance industry data|
|A9|Seasonal patterns|Higher claims in winter months|Weather-related wear and tear|
|A10|Fleet vs individual|Fleet claims 20% higher value|Commercial vehicles higher repair costs|

## 10. Open Questions (if any)
1. Should we model different SLA requirements by contract type?
2. What percentage of claims require physical inspection?
3. Should supplier/parts availability delays be modeled?

## 11. Data Generation Instructions
```yaml
generation_parameters:
  total_cases: 1500
  time_period_months: 3
  completion_rate: 0.92  # 92% of cases should reach closing activity
  fraud_injection_rate: 0.035  # 3.5% fraud patterns
  straight_through_rate: 0.40  # 40% auto-approved
  
distribution_targets:
  approved: 0.85
  denied: 0.10
  pending: 0.05
  
special_patterns:
  duplicate_vins: 30  # ~2% of cases
  excessive_labor: 45  # ~3% of cases
  dealer_anomalies: 23  # ~1.5% of cases
  high_value_claims: 75  # ~5% over $5000
  
resource_pools:
  dealers: 30  # 30 unique dealers
  adjusters: 15  # 15 claim adjusters
  technical_experts: 5  # Limited technical reviewers
  fraud_analysts: 3  # Small fraud team
```

---

*This specification provides comprehensive requirements for generating realistic automotive warranty claims data that demonstrates key pain points, bottlenecks, and opportunities for process improvement through process mining analytics.*