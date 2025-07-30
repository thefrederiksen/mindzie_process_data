# Hire to Retire Process Specifications

## Overview
This document defines the complete specifications for the Hire to Retire (H2R) process mining dataset. This dataset simulates the entire employee lifecycle in a large organization, from recruitment and hiring through retirement or termination.

## Process Scope
The Hire to Retire process encompasses all major HR touchpoints in an employee's journey:
- Recruitment and hiring
- Onboarding and orientation
- Performance management
- Learning and development
- Compensation and benefits changes
- Internal mobility (promotions, transfers)
- Leave management
- Offboarding (retirement, resignation, termination)

## Activities Tracked

### Core Activities (25 activities)
**Legend**: 
- 🏢 = Customer Organization performs this activity
- 🤝 = XYZ Company (outsourced HR) performs this activity
- 🔄 = Joint activity between Customer and XYZ

1. **Job Requisition Created** 🏢 - Manager creates request for new position
2. **Job Posted** 🤝 - Position advertised internally/externally by XYZ
3. **Application Received** 🤝 - Candidate submits application via XYZ portal
4. **Application Screened** 🤝 - Initial HR screening by XYZ recruiters
5. **Phone Interview Scheduled** 🤝 - Initial screening call arranged by XYZ
6. **Phone Interview Completed** 🤝 - Screening call conducted by XYZ
7. **Technical Assessment Sent** 🔄 - Skills test assigned (Customer defines, XYZ administers)
8. **Technical Assessment Completed** 🤝 - Skills test submitted and scored by XYZ
9. **Onsite Interview Scheduled** 🤝 - In-person/video interviews arranged by XYZ
10. **Onsite Interview Completed** 🏢 - Interviews conducted by Customer hiring team
11. **Reference Check Initiated** 🤝 - Background verification started by XYZ
12. **Reference Check Completed** 🤝 - Background verification finished by XYZ
13. **Offer Extended** 🔄 - Job offer made (Customer approves, XYZ communicates)
14. **Offer Accepted** 🤝 - Candidate accepts position via XYZ
15. **Onboarding Initiated** 🤝 - New hire process begins with XYZ coordination
16. **IT Equipment Assigned** 🏢 - Computer, accounts, access provided by Customer IT
17. **Orientation Completed** 🔄 - Company orientation (Customer content, XYZ delivery)
18. **Probation Period Started** 🤝 - Initial employment period tracked by XYZ
19. **Probation Review Completed** 🔄 - Assessment (Customer reviews, XYZ documents)
20. **Annual Performance Review** 🏢 - Yearly evaluation by Customer managers
21. **Promotion Processed** 🔄 - Role change (Customer approves, XYZ processes)
22. **Transfer Processed** 🔄 - Department change (Customer approves, XYZ processes)
23. **Leave Requested** 🤝 - Time off requested via XYZ system
24. **Leave Approved** 🏢 - Time off approved by Customer manager
25. **Exit Process Initiated** 🔄 - Resignation/retirement (Customer decides, XYZ processes)

### Optional Activities
- **Salary Adjustment Processed** 🔄 - Compensation change (Customer approves, XYZ processes)
- **Training Enrolled** 🤝 - Learning program registration via XYZ LMS
- **Training Completed** 🤝 - Learning program finished, tracked by XYZ
- **Disciplinary Action Taken** 🔄 - Performance issue (Customer decides, XYZ documents)
- **Benefits Change Processed** 🤝 - Insurance/benefits modification by XYZ
- **Exit Interview Conducted** 🤝 - Departure feedback session by XYZ
- **Final Settlement Processed** 🤝 - Last payment/benefits calculated by XYZ

## Division of Responsibilities

### XYZ Company (Outsourced HR Provider) Responsibilities
- **Recruitment Operations**: Job posting, candidate sourcing, initial screening
- **Administrative Processing**: Application tracking, interview scheduling, offer letters
- **HR Operations**: Benefits administration, leave tracking, payroll processing
- **Compliance**: Background checks, documentation, regulatory reporting
- **System Management**: HRIS maintenance, employee self-service portal
- **Exit Management**: Exit processing, final settlements, COBRA administration

### Customer Organization Responsibilities  
- **Strategic Decisions**: Hiring approvals, compensation decisions, promotions
- **Direct Management**: Performance reviews, disciplinary actions, leave approvals
- **Technical Evaluation**: Technical interviews, skill assessments (content)
- **IT Infrastructure**: Equipment provisioning, system access, security
- **Business Integration**: Team integration, role-specific training

### Joint Responsibilities
- **Onboarding**: Customer provides content, XYZ delivers process
- **Policy Enforcement**: Customer sets policies, XYZ implements
- **Performance Management**: Customer evaluates, XYZ documents and tracks
- **Compensation**: Customer decides amounts, XYZ processes changes

## Case Attributes

### Employee Attributes (constant within case)
- **EmployeeID**: Unique employee identifier (E100000-E999999)
- **HireDate**: Date employee joined organization
- **Department**: Current department (Sales, Engineering, HR, Finance, Operations, Marketing)
- **Location**: Office location (New York, London, Singapore, Sydney, Berlin)
- **JobLevel**: Position level (1-10, where 1=entry, 10=executive)
- **EmploymentType**: Full-time, Part-time, Contract
- **EducationLevel**: High School, Bachelor's, Master's, PhD
- **YearsExperience**: Prior experience at hire (0-40 years)

### Recruitment Attributes
- **RequisitionID**: Unique job requisition identifier
- **JobTitle**: Position being filled
- **HiringManager**: Manager requesting position
- **RecruitmentSource**: Internal, External, Referral, Agency
- **TargetStartDate**: Requested start date for position

### Dynamic Attributes (can change during case)
- **CurrentSalary**: Current compensation level
- **PerformanceRating**: Last performance score (1-5)
- **TenureYears**: Years with company
- **ManagerID**: Current manager identifier

### Activity Tracking Attributes
- **PerformedBy**: Organization performing activity ("Customer", "XYZ", "Joint")
- **SystemUsed**: System where activity was recorded ("XYZ_HRIS", "Customer_System", "Email", "Manual")

## Process Flow

### Standard Hiring Path (80% of cases)
1. Job Requisition Created
2. Job Posted (internal: 30%, external: 70%)
3. Application Received (average 50 per position)
4. Application Screened (40% pass screening)
5. Phone Interview Scheduled → Completed (75% pass)
6. Technical Assessment (60% of technical roles)
7. Onsite Interview Scheduled → Completed (50% receive offers)
8. Reference Check Initiated → Completed
9. Offer Extended (85% acceptance rate)
10. Offer Accepted
11. Onboarding Initiated
12. IT Equipment Assigned
13. Orientation Completed
14. Probation Period Started

### Ongoing Employment Activities
- **Annual Performance Review**: Once per year per employee
- **Promotion Processed**: 15% of employees annually
- **Transfer Processed**: 10% of employees annually
- **Leave Requested/Approved**: Average 3-4 times per year
- **Salary Adjustment**: With promotions or annual reviews
- **Training**: 2-3 programs per employee per year

### Exit Paths (20% annual turnover)
- **Voluntary Resignation**: 60% of exits
- **Retirement**: 20% of exits
- **Involuntary Termination**: 15% of exits
- **End of Contract**: 5% of exits

## Stage Definitions and Thresholds

### Recruitment Stages
1. **Waiting for Screening**: Application Received → Application Screened
   - Medium threshold: 3 days
   - High threshold: 7 days

2. **Waiting for Phone Interview**: Phone Interview Scheduled → Phone Interview Completed
   - Medium threshold: 5 days
   - High threshold: 10 days

3. **Waiting for Onsite Interview**: Onsite Interview Scheduled → Onsite Interview Completed
   - Medium threshold: 7 days
   - High threshold: 14 days

4. **Waiting for Offer Decision**: Onsite Interview Completed → Offer Extended
   - Medium threshold: 5 days
   - High threshold: 10 days

5. **Waiting for Offer Response**: Offer Extended → Offer Accepted/Rejected
   - Medium threshold: 5 days
   - High threshold: 10 days

### Onboarding Stages
6. **Waiting for Start Date**: Offer Accepted → Onboarding Initiated
   - Medium threshold: 14 days
   - High threshold: 30 days

7. **Waiting for IT Setup**: Onboarding Initiated → IT Equipment Assigned
   - Medium threshold: 1 day
   - High threshold: 3 days

8. **Waiting for Orientation**: IT Equipment Assigned → Orientation Completed
   - Medium threshold: 5 days
   - High threshold: 10 days

### Employment Stages
9. **Waiting for Performance Review**: Review cycle started → Annual Performance Review
   - Medium threshold: 7 days
   - High threshold: 14 days

10. **Waiting for Leave Approval**: Leave Requested → Leave Approved
    - Medium threshold: 1 day
    - High threshold: 3 days

11. **Waiting for Promotion Approval**: Promotion submitted → Promotion Processed
    - Medium threshold: 14 days
    - High threshold: 30 days

12. **Waiting for Exit Completion**: Exit Process Initiated → Employment Ended
    - Medium threshold: 14 days
    - High threshold: 30 days

## Time Scales
- **Recruitment Phase**: Days to weeks
- **Onboarding Phase**: Days to weeks  
- **Employment Phase**: Months to years
- **Exit Phase**: Days to weeks
- **Overall Case Duration**: 
  - Minimum: 1 month (failed probation)
  - Average: 5 years
  - Maximum: 40 years (career employee)

## Data Generation Rules

### Case Generation
- **Recruitment cases**: 200-300 active requisitions at any time
- **New hires**: 50-100 per month
- **Active employees**: 5000-8000
- **Exits**: 80-150 per month

### Timing Rules
- Business hours: Monday-Friday, 9 AM - 6 PM
- Interviews scheduled during business hours only
- Onboarding typically on Mondays
- Performance reviews clustered in Q1 and Q3
- No activities on weekends or holidays

### Probability Distributions
- **Screening pass rate**: 40%
- **Phone interview pass rate**: 75%
- **Onsite to offer rate**: 50%
- **Offer acceptance rate**: 85%
- **Probation success rate**: 90%
- **Annual promotion rate**: 15%
- **Annual transfer rate**: 10%
- **Annual turnover rate**: 20%

### Department-Specific Rules
- **Engineering**: Higher technical assessment usage (90%)
- **Sales**: Faster hiring process, higher turnover (25%)
- **Executive**: Longer recruitment cycle, lower turnover (10%)
- **Operations**: Higher internal mobility (15% transfers)

## Output Formats

### JSON Format
```json
{
  "CaseId": "HR2024_E123456",
  "ActivityName": "Onboarding Initiated",
  "ActivityTime": "2024-03-15T09:00:00Z",
  "EmployeeID": "E123456",
  "Department": "Engineering",
  "Location": "New York",
  "JobLevel": 3,
  "EmploymentType": "Full-time",
  "HiringManager": "M098765",
  "RecruitmentSource": "External",
  "CurrentSalary": 95000,
  "PerformanceRating": null,
  "TenureYears": 0,
  "PerformedBy": "XYZ",
  "SystemUsed": "XYZ_HRIS"
}
```

### CSV Format
```csv
CaseId,ActivityName,ActivityTime,EmployeeID,Department,Location,JobLevel,EmploymentType,HiringManager,RecruitmentSource,CurrentSalary,PerformanceRating,TenureYears,PerformedBy,SystemUsed
HR2024_E123456,Onboarding Initiated,2024-03-15T09:00:00Z,E123456,Engineering,New York,3,Full-time,M098765,External,95000,,0,XYZ,XYZ_HRIS
```

## Domain-Specific Considerations

### Compliance Requirements
- GDPR compliance for EU employees
- Equal Employment Opportunity (EEO) data tracking
- Audit trail for all compensation changes
- Documentation requirements for terminations

### Integration Points
- HRIS (Human Resources Information System)
- Payroll systems
- Learning Management System (LMS)
- Performance Management System
- Applicant Tracking System (ATS)

### Business Rules
- Minimum time between promotions: 12 months
- Maximum consecutive leave days: 30
- Probation period: 90 days for all new hires
- Notice period: 14-90 days based on level
- Retirement eligibility: Age 65 or 30 years service

### Key Performance Indicators
- Time to Fill (requisition to hire)
- Offer Acceptance Rate
- First Year Retention Rate
- Internal Mobility Rate
- Employee Satisfaction Score
- Cost per Hire
- Training Completion Rate
- Performance Review Completion Rate

## Data Quality Requirements
- All employees must have complete core attributes
- Activity timestamps must follow chronological order
- Salary changes must align with promotions/reviews
- Department transfers must update department attribute
- Exit activities cannot be followed by employment activities
- Performance ratings must be within 1-5 range
- Tenure calculations must match hire date

## Notes
- Employee IDs remain constant throughout employment lifecycle
- Case IDs include year prefix for easy filtering
- All monetary values in USD
- Timestamps in UTC
- Performance reviews may trigger multiple outcomes (promotion, salary adjustment, training)
- Some employees may have multiple cases (rehires)