# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## VS Code Title Bar Color Instructions

To change the VS Code title bar color for this workspace, update the workspace file (.code-workspace) with:

```json
"settings": {
    "workbench.colorCustomizations": {
        "titleBar.activeBackground": "#COLOR_HEX",
        "titleBar.activeForeground": "#ffffff",
        "titleBar.inactiveBackground": "#DARKER_COLOR_HEX",
        "titleBar.inactiveForeground": "#e3e3e3"
    }
}
```

Color suggestions:
- Blue: #1a73e8 (inactive: #135db5)
- Green: #2e7d32 (inactive: #1b5e20)
- Purple: #7b1fa2 (inactive: #4a148c)
- Orange: #ef6c00 (inactive: #bf360c)
- Red: #c62828 (inactive: #8e0000)
- Teal: #00796b (inactive: #004d40)
- Pink: #c2185b (inactive: #880e4f)

## Repository Overview

This repository contains process mining datasets and projects for research and education. The main focus is on demonstrating real-time process flow monitoring using process mining techniques. Currently features an Emergency Department project with plans for additional process mining datasets (SAP Accounts Payable and others).

## Key Architecture

### Two-Dataset Approach
- **Historical Dataset**: Traditional process mining analysis (1-2 years of completed cases)
- **Current State Dataset**: Real-time process flow monitoring (daily data with open cases)

### Project Structure Pattern
Each process mining project follows this structure:
```
[domain_name]/
├── docs/                    # Process specifications and documentation
├── src/                     # Data generation and upload scripts
│   └── output/             # Generated datasets (CSV/JSON)
├── mindzie_studio/         # Mindzie Studio project files
└── README.md               # Project-specific documentation
```

## Common Development Commands

### Data Generation
```bash
# Generate historical dataset (1-2 years of completed cases)
cd "Emergency Department/src"
python historical_event_log.py

# Generate current state dataset (daily snapshot with open cases)
python daily_event_log.py

# View statistics for generated data
python historical_event_log_stats.py
python daily_event_log_stats.py
```

### Mindzie Studio Integration
Before uploading datasets, create a `.env` file in the project's `src` directory:
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

### Testing
No specific test framework is configured. Verify data generation by:
1. Running the statistics scripts to check data quality
2. Reviewing generated CSV/JSON files in `src/output/`
3. Testing uploads to Mindzie Studio

## Key Technical Details

### Dependencies
- Python 3.7+ (standard library only for core functionality)
- `requests` library for API uploads
- `python-dotenv` for environment configuration
- Fixed random seed (42) for reproducible data generation

### Data Format
Event logs contain:
- **CaseId**: Unique identifier for each process instance
- **ActivityName**: Process step completed
- **ActivityTime**: ISO 8601 timestamp
- **Additional attributes**: Domain-specific (PatientID, age, etc.)

### FreezeTime Concept
Current state datasets use a "FreezeTime" - a snapshot timestamp for calculating waiting times and determining which cases are in-progress vs completed.

## Important Patterns

### Creating New Process Mining Datasets
Follow the structure defined in `agent_instructions.md`:
1. Create directory structure following the pattern
2. Define activities in `activities.json`
3. Implement data generators based on Emergency Department examples
4. Create process specifications in `docs/`
5. Generate MCL files for Mindzie Studio stages

### Code Style
- Use descriptive variable names
- Include docstrings for main functions
- Handle errors gracefully in upload scripts
- Maintain consistent timestamp formats (ISO 8601)
- Keep random seed fixed (42) for reproducibility

## Current Projects

### Emergency Department
- Complete implementation with real-time monitoring
- 16 key activities tracking patient flow
- Demonstrates waiting time alerts and bottleneck identification
- Location: `Emergency Department/`

### SAP Accounts Payable (In Progress)
- Finance domain process mining dataset
- Currently only specifications defined
- Location: `SAP Accounts Payable/`