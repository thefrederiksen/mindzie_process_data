# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

Process mining datasets and projects repository for research and education, demonstrating real-time process flow monitoring using process mining techniques.

## Key Architecture

### Two-Dataset Approach
- **Historical Dataset**: Traditional process mining analysis (1-2 years of completed cases)
- **Current State Dataset**: Real-time process flow monitoring (daily data with open cases)

### Project Structure Pattern
```
[domain_name]/
├── docs/                    # Process specifications and documentation
├── src/                     # Data generation and upload scripts
│   └── output/             # Generated datasets (CSV/JSON)
├── mindzie_studio/         # Mindzie Studio project files (.mpz, .mcl files)
└── README.md               # Project-specific documentation
```

## Common Development Commands

### Data Generation
```bash
# Navigate to project src directory first
cd "[Project Name]/src"

# Generate historical dataset (1-2 years of completed cases)
python historical_event_log.py

# Generate current state dataset (daily snapshot with open cases)
python daily_event_log.py

# View statistics for generated data
python historical_event_log_stats.py
python daily_event_log_stats.py
```

### Mindzie Studio Integration
Create `.env` file in project's `src` directory:
```
TENANT_ID=your-tenant-id-here
PROJECT_ID=your-project-id-here
API_KEY=your-api-key-here
```

Upload datasets:
```bash
python daily_dataset_upload.py
python historical_dataset_upload.py
```

### Data Validation (Hire to Retire project)
```bash
cd "Hire to Retire/src"
python data_validator.py
python enhanced_data_validator.py
python final_validator.py
```

## Key Technical Details

### Dependencies
- Python 3.7+ (standard library for core functionality)
- `requests` library for API uploads
- `python-dotenv` for environment configuration
- Fixed random seed (42) for reproducible data generation

### Data Format
Event logs contain:
- **CaseId**: Unique identifier for each process instance
- **ActivityName**: Process step completed
- **ActivityTime**: ISO 8601 timestamp
- **Additional attributes**: Domain-specific (PatientID, EmployeeID, etc.)

### FreezeTime Concept
Current state datasets use a "FreezeTime" - a snapshot timestamp for calculating waiting times and determining which cases are in-progress vs completed.

### Resource Performance Modeling
Data generators include realistic performance variations:
- Individual resource performance factors (e.g., PERFORMANCE_FACTORS dictionary)
- Time-based patterns (business hours, weekday variations)
- Bottleneck injection for specific resources/activities

## Current Projects

### Emergency Department
- Complete implementation with real-time monitoring
- 16 key activities tracking patient flow
- Waiting time alerts and bottleneck identification
- Resources: doctors, nurses, clerks, technicians
- Location: `Emergency Department/`

### SAP Accounts Payable
- Finance domain process mining dataset
- Invoice processing workflow (PO-based and non-PO)
- 15+ activities from invoice receipt to payment
- Location: `SAP Accounts Payable/`

### Hire to Retire
- HR process lifecycle from recruitment to termination
- Complex validation scripts for data quality
- Performance bottlenecks in equipment and reviews
- Location: `Hire to Retire/`

## Creating New Process Mining Datasets

1. Create directory structure following the pattern
2. Define activities in `activities.json`
3. Implement data generators based on existing examples
4. Include resource pools and performance factors
5. Create process specifications in `docs/`
6. Generate MCL files for Mindzie Studio stages
7. Implement validation scripts if needed