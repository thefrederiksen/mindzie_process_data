# Continuous Case Flow Monitoring: Hospital Emergency Department

**Project:** Real-time process flow monitoring demonstration using hospital emergency department data  
**Hospital:** Alderaan General Hospital  
**Snapshot Date:** 2025-05-04 at 14:00:00  
**Location:** Mos Eisley, Tatooine, Outer Rim Territories  

## 🚀 Quick Start: Mindzie Studio Project

**Ready to explore?** Download the complete Mindzie Studio project with all data and process flow monitoring dashboards!

- **Project File:** `mindzie_studio/Alderaan Hospital.mpz`
- **Requirements:** Mindzie Desktop or Mindzie Enterprise access
- **What's Included:** 
  - Complete hospital emergency department data
  - Real-time process flow monitoring dashboards
  - Historical analysis and process mining models
  - Command centre configurations

Simply download the `.mpz` file and upload it to your Mindzie Studio environment to start exploring the continuous case flow monitoring system immediately.

---

## Project Overview

This project demonstrates how to implement real-time process flow monitoring using process mining techniques, with a hospital emergency department as the use case. The goal is to show how historical process mining analysis can be extended to provide real-time operational insights through a "command centre" approach.

### Key Objectives
- Demonstrate the Case Stage Calculator for real-time process monitoring
- Show how to set up a physical command centre with dashboards
- Illustrate the transition from historical analysis to real-time operational control
- Provide practical implementation guidance for similar projects

## Data Structure

The project uses synthetic hospital emergency department data that simulates patient flow through various stages of emergency care:

- **Patient registration and triage**
- **Waiting times for different services** (doctor, nurse, tests, etc.)
- **Treatment and discharge processes**
- **Real-time status tracking**

### Event Log Structure

Each row in the event log represents a single activity for a single patient visit (case):

- **CaseId**: Uniquely identifies a patient visit (visit number)
- **ActivityName**: The step or event that occurred (e.g., Registration, Triage)
- **ActivityTime**: The timestamp when the activity was completed
- **PatientID**: Unique identifier for the patient (all events for the same CaseId have the same PatientID)

### Example Row
| CaseId   | ActivityName   | ActivityTime        | PatientID |
|----------|---------------|---------------------|-----------|
| ED123456 | Registration  | 2025-05-04 08:15:00 | P001      |

## Data Generation

The project uses a two-dataset approach:

### 1. Historical Dataset
- **Purpose**: Traditional process mining analysis (bottlenecks, rework, conformance)
- **Content**: 1-2 years of completed patient cases
- **Script**: `src/historical_event_log.py`
- **Output**: 
  - `src/Output/alderaan_year_to_date.json`
  - `src/Output/alderaan_year_to_date.csv`

### 2. Current State Dataset (Real-time)
- **Purpose**: Real-time process flow monitoring
- **Content**: Daily data with all open patient cases
- **Script**: `src/daily_event_log.py`
- **Output**:
  - `src/Output/alderaan_daily.json`
  - `src/Output/alderaan_daily.csv`

### How to Generate Data

```bash
# Generate historical dataset
python src/historical_event_log.py

# Generate current state dataset
python src/daily_event_log.py
```

**Note**: Both scripts use a fixed random seed for reproducibility.

## FreezeTime (Snapshot Time)

The event log is generated as a snapshot of the Emergency Department at a specific point in time, called the **FreezeTime**. This is the reference time for all calculations of waiting times and for determining which patients are currently in progress versus completed.

```
"FreezeTime": "2025-05-04T14:00:00+00:00"
```

- All waiting time calculations for in-progress cases are based on the difference between the FreezeTime and the timestamp of the last completed activity for each case
- The FreezeTime is set in the generator script and should always reflect the current snapshot time for the log

## Mindzie Studio Integration

### Uploading Datasets to Mindzie Studio

Before uploading, ensure you have created a `.env` file in the `src` directory with the following parameters:

```
TENANT_ID=your-tenant-id-here
PROJECT_ID=your-project-id-here
API_KEY=your-api-key-here
```

**Parameter Sources:**
- **TENANT_ID**: Found in the 'About' box in Mindzie Studio for your project
- **PROJECT_ID**: Found in the 'About' box in Mindzie Studio for your project  
- **API_KEY**: Retrieved in Mindzie Studio under Administration Settings > API keys

### Upload Scripts

```bash
# Upload daily event log
python src/daily_dataset_upload.py

# Upload historical event log
python src/historical_dataset_upload.py
```

## Project Files

### Core Implementation
- `src/daily_event_log.py` - Generates daily event logs for real-time monitoring
- `src/historical_event_log.py` - Creates historical datasets for analysis
- `src/activities.json` - Defines hospital activities and process stages
- `src/daily_dataset_upload.py` - Uploads daily data to Mindzie Studio
- `src/historical_dataset_upload.py` - Uploads historical data to Mindzie Studio

### Mindzie Studio Files
- `mindzie_studio/` - Contains Mindzie Studio project files with process models
- `mindzie_studio/Current Day/` - Real-time monitoring dashboards and configurations
- `mindzie_studio/Current Day/Investigations/Stages/` - Process stage definitions

### Output Data
- `src/Output/` - Generated datasets and analysis results
- CSV and JSON formats for different use cases

### Documentation
- `Docs/` - Process specifications and documentation
- `presentation/` - Presentation materials and project overview

## Key Concepts

### Two-Dataset Approach
- **Historical Dataset**: For traditional process mining analysis
- **Current State Dataset**: For real-time operational monitoring
- **Focus**: Durations and bottlenecks rather than conformance for real-time monitoring

### Real-time Process Flow Monitoring
- **Purpose**: Immediate operational intervention capabilities
- **Value**: Reduced wait times and improved patient care
- **Implementation**: Physical command centre setup with multiple stakeholder views

## Development Notes

- All data is synthetic and for process mining research and education only
- The generator and event log structure are designed to be extensible
- You can add more case attributes or activity types as needed
- Both scripts include statistics reporting for verification

## License

MIT License - see LICENSE file for details.

---

**Created By:** Synthetic Data Generator using AI agents (Cursor, Claude CLI, etc.)  
**Purpose:** Process mining research, education, and real-time monitoring demonstration 