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

### Core Activities (15 activities)
**Legend**: 
- 🏢 = Customer Organization performs this activity
- 🤝 = XYZ Company (outsourced HR) performs this activity
- 🔄 = Joint activity between Customer and XYZ

#### Recruitment (5 activities)
1. **Job Posted** 🤝 - Position advertised by XYZ
2. **Application Received** 🤝 - Candidate submits application
3. **Interview Completed** 🔄 - All interviews conducted (phone/onsite combined)
4. **Offer Extended** 🔄 - Job offer made (Customer approves, XYZ communicates)
5. **Offer Accepted** 🤝 - Candidate accepts position

#### Onboarding (3 activities)
6. **Onboarding Started** 🤝 - New hire process begins
7. **Equipment Assigned** 🏢 - IT equipment and access provided
8. **Probation Completed** 🔄 - 90-day review passed

#### Employment (5 activities)
9. **Performance Review** 🏢 - Annual evaluation completed
10. **Promotion Approved** 🔄 - Role/level change processed
11. **Leave Requested** 🤝 - Time off requested
12. **Leave Approved** 🏢 - Time off approved
13. **Training Completed** 🤝 - Learning program finished

#### Exit (2 activities)
14. **Resignation Submitted** 🔄 - Employee initiates departure
15. **Employment Ended** 🤝 - Final exit processed

### Rejection Activities (for incomplete journeys)
- **Application Rejected** 🤝 - Candidate not selected after screening
- **Interview Failed** 🔄 - Candidate not progressing after interviews
- **Offer Rejected** 🤝 - Candidate declines offer
- **Probation Failed** 🔄 - Employee doesn't pass probation period

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

### Recruitment Path
1. **Job Posted** → Applications received (average 50 per position)
2. **Application Received** → 40% pass initial screening
3. **Interview Completed** → 30% of interviewed candidates receive offers
4. **Offer Extended** → 85% acceptance rate
5. **Offer Accepted** → Proceed to onboarding

### Onboarding Path (New Hires)
6. **Onboarding Started** → Within 2-4 weeks of offer acceptance
7. **Equipment Assigned** → Within first 3 days
8. **Probation Completed** → 90% pass probation at 90 days

### Employment Activities (Active Employees)
9. **Performance Review** → Annual for all employees
10. **Promotion Approved** → 15% of employees annually
11. **Leave Requested** → Average 3-4 times per year per employee
12. **Leave Approved** → 95% approval rate
13. **Training Completed** → 2-3 programs per employee per year

### Exit Path (20% annual turnover)
14. **Resignation Submitted** → 80% of exits are voluntary
15. **Employment Ended** → Final processing within 2-4 weeks

### Rejection Points
- **Application Rejected** → 60% of applications
- **Interview Failed** → 70% of interviewed candidates
- **Offer Rejected** → 15% of offers extended
- **Probation Failed** → 10% of new hires

## Stage Definitions and Thresholds

### Recruitment Stages
1. **Waiting for Interview**: Application Received → Interview Completed
   - Medium threshold: 7 days
   - High threshold: 14 days

2. **Waiting for Offer Decision**: Interview Completed → Offer Extended
   - Medium threshold: 5 days
   - High threshold: 10 days

3. **Waiting for Offer Response**: Offer Extended → Offer Accepted/Rejected
   - Medium threshold: 5 days
   - High threshold: 10 days

### Onboarding Stages
4. **Waiting to Start**: Offer Accepted → Onboarding Started
   - Medium threshold: 14 days
   - High threshold: 30 days

5. **Waiting for Equipment**: Onboarding Started → Equipment Assigned
   - Medium threshold: 1 day
   - High threshold: 3 days

6. **Waiting for Probation Review**: Equipment Assigned → Probation Completed
   - Medium threshold: 85 days
   - High threshold: 95 days

### Employment Stages
7. **Waiting for Performance Review**: Review due → Performance Review
   - Medium threshold: 7 days
   - High threshold: 14 days

8. **Waiting for Leave Approval**: Leave Requested → Leave Approved
   - Medium threshold: 1 day
   - High threshold: 3 days

### Exit Stages
9. **Waiting for Exit Processing**: Resignation Submitted → Employment Ended
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

## Industry Problems & Process Mining Opportunities

### Top HR Process Challenges (2024 Industry Data)
1. **92% of organizations** struggle with recruiting and retaining qualified personnel
2. **75% of employers** report difficulty filling roles (Manpower Global Talent Shortage)
3. **51% of employees** are actively looking for new jobs
4. **40% average increase** in time-to-fill from 36 to 40+ days
5. **$30,000 per employee** annual cost for routine HR transactions (Fortune 500)
6. **30% of new hires** leave within first 90 days
7. **51% of HR professionals** report poor technology integration

### Common Process Mining Findings in HR

#### 1. **Recruitment & Talent Acquisition Bottlenecks**
- **Ghost Jobs**: 8-10% of posted positions never filled (budget frozen, role changes)
- **Extended Time-to-Fill**: 15% of positions take 90+ days to fill
- **Application Black Hole**: 25% of applications never receive any response
- **Interview Scheduling Delays**: 30% experience 2+ week delays between stages
- **Candidate Dropout**: 40% of candidates withdraw due to slow process
- **Offer Delays**: 20% of offers extended 2+ weeks after final interview
- **Background Check Delays**: 10% take longer than 2 weeks
- **Multiple Approval Loops**: 35% go through redundant approval cycles

#### 2. **Onboarding & Early Experience Issues**
- **Pre-boarding Gaps**: 25% have no contact between offer acceptance and start date
- **Equipment Not Ready**: 20% don't have equipment/access on day 1
- **Incomplete Onboarding**: 15% miss critical orientation activities
- **Manager Unavailability**: 10% of managers absent for new hire's first week
- **System Access Delays**: 30% wait 3+ days for all system access
- **Early Turnover**: 12% leave within 90 days (probation fail or resignation)
- **Documentation Delays**: 25% of paperwork incomplete after 30 days

#### 3. **Performance Management Inefficiencies**
- **Delayed Reviews**: 35% of annual reviews happen 30+ days late
- **Missing Reviews**: 10% of employees never receive scheduled reviews
- **Calibration Delays**: 20% of reviews stuck in calibration for 2+ weeks
- **Goal Setting Gaps**: 40% don't have documented goals within first 60 days
- **Feedback Void**: 60% receive no formal feedback between annual reviews
- **Rating Inconsistency**: 25% variance in ratings across similar roles

#### 4. **Career Development & Retention Problems**
- **Training No-Shows**: 25% of enrolled employees don't complete training
- **Promotion Delays**: 40% of approved promotions take 60+ days to process
- **Transfer Blocks**: 30% of internal transfer requests denied or delayed
- **Career Path Opacity**: 70% unclear about advancement opportunities
- **Skill Gap Tracking**: 80% of organizations can't identify critical skill gaps
- **Succession Planning Void**: 65% of critical roles have no identified successor

#### 5. **Leave & Absence Management Issues**
- **Leave Approval Delays**: 20% of requests take 3+ days for approval
- **Leave Balance Errors**: 15% of employees report incorrect balances
- **Unplanned Absences**: 8% show patterns of no-notice absences
- **Return-to-Work Delays**: 25% of long-term leave returns poorly managed
- **Policy Confusion**: 40% unclear about leave policies and entitlements

#### 6. **Compensation & Benefits Administration**
- **Salary Adjustment Delays**: 35% of approved changes take 2+ pay cycles
- **Benefits Enrollment Issues**: 20% miss initial enrollment window
- **Compensation Errors**: 5% of paychecks contain errors requiring correction
- **Bonus Processing Delays**: 30% of bonuses paid late
- **Benefits Questions**: 45% of HR inquiries are benefits-related

#### 7. **Exit Process & Knowledge Transfer**
- **Sudden Resignations**: 20% give less than standard notice period
- **Exit Interview No-Shows**: 35% skip exit interviews entirely
- **Knowledge Transfer Gaps**: 50% leave without proper documentation
- **Access Revocation Delays**: 15% retain system access 7+ days post-exit
- **Final Pay Delays**: 10% experience issues with final settlement
- **Alumni Disconnect**: 90% lose touch with organization post-exit

#### 8. **Systemic & Technology Issues**
- **Data Quality Problems**: 10% of employee records have critical errors
- **System Integration Gaps**: Multiple data entry for same information
- **Approval Bottlenecks**: 40% of delays caused by senior approver availability
- **Communication Failures**: 25% of employees miss important HR updates
- **Document Management**: 30% of time spent on document creation/routing
- **Reporting Delays**: Monthly HR reports take 5+ days to compile

## Process Problems and Bottlenecks Injected in Dataset

Based on industry research and process mining findings, we inject the following realistic problems:

### Recruitment Problems (Affecting ~85% of cases)
- **Ghost Jobs**: 8% of posted positions never actually filled
- **Extended Time-to-Fill**: 15% of positions take 90+ days to fill
- **Interview Scheduling Delays**: 30% experience significant delays
- **Candidate Ghosting**: 10% of candidates stop responding mid-process
- **Offer Delays**: 20% of offers take 2+ weeks after final interview

### Onboarding Problems (Affecting hired employees)
- **Equipment Delays**: 20% don't have equipment ready on day 1
- **System Access Issues**: 30% wait 3+ days for full access
- **Manager Unavailability**: 10% have absent managers in first week
- **Documentation Delays**: 25% have incomplete paperwork after 30 days
- **Early Turnover**: 12% leave within 90 days

### Employment Lifecycle Problems
- **Performance Review Delays**: 35% happen 30+ days late
- **Missing Reviews**: 10% of scheduled reviews never happen
- **Leave Approval Delays**: 20% take 3+ days to approve
- **Training Incompletion**: 25% don't complete enrolled training
- **Promotion Processing**: 40% of promotions take 60+ days
- **Transfer Blocks**: 30% of transfer requests blocked

### Exit Process Problems
- **Short Notice**: 20% give insufficient notice
- **Exit Interview Skips**: 35% skip exit process
- **Knowledge Gaps**: 50% leave without proper handover
- **Access Issues**: 15% retain access too long

### Data Quality & System Issues
- **Missing Data**: 10% of records have missing critical fields
- **Duplicate Processing**: 15% of activities require rework
- **System Unavailability**: Affects 2% of transactions
- **Approval Delays**: 40% of multi-level approvals delayed

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