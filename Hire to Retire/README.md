# Hire to Retire Process Mining Dataset

## Overview
This dataset simulates the complete employee lifecycle in a large organization, from recruitment through retirement or termination. The process is managed through an outsourced HR partnership model where XYZ Company provides HR services to a Customer Organization.

## Process Model
The Hire to Retire process includes 15 core activities across 4 major phases:

### 1. Recruitment (5 activities)
- **Job Posted** - Position advertised by XYZ
- **Application Received** - Candidate submits application
- **Interview Completed** - All interviews conducted (phone/onsite combined)
- **Offer Extended** - Job offer made
- **Offer Accepted** - Candidate accepts position

### 2. Onboarding (3 activities)
- **Onboarding Started** - New hire process begins
- **Equipment Assigned** - IT equipment and access provided
- **Probation Completed** - 90-day review passed

### 3. Employment (5 activities)
- **Performance Review** - Annual evaluation completed
- **Promotion Approved** - Role/level change processed
- **Leave Requested** - Time off requested
- **Leave Approved** - Time off approved
- **Training Completed** - Learning program finished

### 4. Exit (2 activities)
- **Resignation Submitted** - Employee initiates departure
- **Employment Ended** - Final exit processed

## Outsourcing Model
The dataset demonstrates a realistic HR outsourcing scenario:
- **XYZ Company** (Outsourced HR Provider) handles administrative tasks
- **Customer Organization** handles strategic decisions and approvals
- Activities are marked with who performs them (XYZ, Customer, or Joint)

## Dataset Statistics
- **Total Cases**: 3,000 employee lifecycles
- **Time Period**: 2 years of historical data
- **Hired Employees**: ~300 (10% success rate)
- **Rejected Applications**: ~2,700 (90% rejection rate)
- **Active Employees**: ~250
- **Exited Employees**: ~50

## Key Features
- Realistic recruitment funnel with proper rejection points
- Business hours constraints (Mon-Fri, 9 AM - 6 PM)
- Department-specific variations
- Location-based distribution across 5 global offices
- Performance-based promotions and salary adjustments
- Leave management workflow
- Training and development tracking

## Files Structure
```
Hire to Retire/
├── docs/
│   ├── process_specifications.md    # Complete process specification
│   ├── process_current_day.md       # Real-time monitoring setup
│   ├── process_historical.md        # Historical analysis approach
│   └── system_integration_guide.md  # HR systems integration guide
├── src/
│   ├── activities.json              # Activity definitions
│   ├── historical_event_log.py      # Dataset generator
│   ├── historical_dataset_upload.py # Upload to Mindzie Studio
│   └── output/
│       ├── hire_to_retire_year_to_date.json  # Case-centric JSON
│       └── hire_to_retire_year_to_date.csv   # Flat CSV format
└── README.md
```

## Usage

### Generate Historical Data
```bash
cd src
python historical_event_log.py
```

### Upload to Mindzie Studio
1. Create a `.env` file in the `src` directory:
```
TENANT_ID=your-tenant-id
PROJECT_ID=your-project-id
API_KEY=your-api-key
```

2. Run the upload script:
```bash
python historical_dataset_upload.py
```

## Process Mining Analysis Opportunities
- **Recruitment Efficiency**: Time to hire, rejection rates by stage
- **Onboarding Success**: Probation pass rates, time to productivity
- **Employee Retention**: Tenure analysis, exit patterns
- **Performance Management**: Review cycles, promotion rates
- **Resource Utilization**: Workload distribution between XYZ and Customer
- **Leave Patterns**: Seasonal trends, approval times
- **Training Effectiveness**: Completion rates, career development paths

## Data Quality Features
- No duplicate case IDs
- Consistent timestamps with business hours
- Realistic case durations and outcomes
- Proper activity sequences
- Dynamic attribute updates (salary, performance ratings)

## Technical Details
- **Random Seed**: 42 (for reproducibility)
- **Business Hours**: Monday-Friday, 9 AM - 6 PM
- **Date Format**: ISO 8601 (YYYY-MM-DDTHH:MM:SS.sssZ)
- **Case ID Format**: HR{year}_{employeeID}
- **Employee ID Format**: E{6-digit number}

## Future Enhancements
- Real-time monitoring dataset generation
- Additional rejection reasons and patterns
- More complex approval workflows
- Integration with benefits management
- Diversity and inclusion metrics
- Remote work patterns