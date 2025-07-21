# ED Event Log - May the 4th

**Hospital Name:** Alderaan General Hospital  
**Date:** 2025-05-04  
**Location:** Mos Eisley, Tatooine, Outer Rim Territories

## Description
This event log is created for two purposes:
1. To provide a live snapshot of all patients currently in the Emergency Department at 2:00 PM on May 4th, 2025, showing their current stage in the patient journey.
2. To provide historical event log data for all patients who have completed their ED journey (discharged or admitted) by that time.

The log captures the patient journey through the emergency department at Alderaan General Hospital, including registration, triage, assessment, diagnostics, treatment, and disposition.

**Activities Reference:** See `activities.json` for a list and description of all activities.

**Created By:** Synthetic Data Generator

**Notes:** All data is synthetic and for process mining research and education only.

---

## Event Log Structure

Each row in the event log represents a single activity for a single patient visit (case).

- **CaseId**: Uniquely identifies a patient visit (visit number).
- **ActivityName**: The step or event that occurred (e.g., Registration, Triage).
- **ActivityTime**: The timestamp when the activity was completed.
- **PatientID**: Unique identifier for the patient. All events for the same CaseId have the same PatientID.

### Example Row
| CaseId   | ActivityName   | ActivityTime        | PatientID |
|----------|---------------|---------------------|-----------|
| ED123456 | Registration  | 2025-05-04 08:15:00 | P001      |

---

## How to Generate Event Logs

There are now two separate scripts for generating event logs:

### 1. Daily Event Log (Live Snapshot)
- **Script:** `src/daily_event_log.py`
- **Output:**
  - `src/Output/alderaan_daily.json`
  - `src/Output/alderaan_daily.csv`
- **How to run:**
  ```bash
  python src/daily_event_log.py
  ```

### 2. Historical Event Log (All Closed Cases)
- **Script:** `src/historical_event_log.py`
- **Output:**
  - `src/Output/alderaan_year_to_date.json`
  - `src/Output/alderaan_year_to_date.csv`
- **How to run:**
  ```bash
  python src/historical_event_log.py
  ```

**Note:** Both scripts use a fixed random seed, so the generated event logs will be identical every time you run them. This ensures full reproducibility for your analysis and dashboarding.

---

## FreezeTime (Snapshot Time)

The event log is generated as a snapshot of the Emergency Department at a specific point in time, called the **FreezeTime** (or snapshot time). This is the reference time for all calculations of waiting times and for determining which patients are currently in progress versus completed. The FreezeTime is included in the event log output as a top-level field in the daily event log:

```
"FreezeTime": "2025-05-04T14:00:00+00:00"
```

- All waiting time calculations for in-progress cases are based on the difference between the FreezeTime and the timestamp of the last completed activity for each case.
- The FreezeTime is set in the generator script and should always reflect the current snapshot time for the log.
- The FreezeTime is also documented in the process specification and should be kept consistent across all documentation and analysis.

---

## Adding Case Attributes

Case attributes (like PatientID) are constant for all events in a case. You can extend the generator to include more attributes (e.g., Age, Gender, Triage Level) as needed.

---

## Development and Usage Notes

This section summarizes the evolving instructions and requirements for building this event log and generator:

1. **Event Log Structure**: The event log must have three main columns: `CaseId`, `ActivityName`, and `ActivityTime`. We added `PatientID` as a case attribute, so every event for a given case (visit) has the same patient ID.
2. **Case Attributes**: Each case (visit) is associated with a unique patient. All events for a case share the same `PatientID`. The generator can be extended to include more case attributes.
3. **Live and Historical Data**: The generators create both a live snapshot (patients currently in the ED at 2:00 PM on May 4th, 2025) and historical data (cases closed by that time).
4. **Statistics Reporting**: After generating the event log, the scripts print a statistics report with two main sections:
   - Live snapshot: Number of in-progress cases, number of activities, number of unique patients, activity count breakdown, and how many in-progress cases have completed their journey (admitted or discharged).
   - Historical (closed) cases: Number of closed cases, number of activities, number of unique patients, and activity count breakdown.
5. **Extensibility**: The generator and event log structure are designed to be extensible. You can add more case attributes or activity types as needed for your process mining or simulation needs.

---

For further customization or to add more features, update the generator scripts and this README accordingly. 

## Uploading Datasets to Mindzie Studio

There are two upload scripts, one for each dataset. Before uploading, ensure you have created a `.env` file in the `src` directory with the following parameters:

```
TENANT_ID=your-tenant-id-here
PROJECT_ID=your-project-id-here
API_KEY=your-api-key-here
```

- **TENANT_ID**: Your Mindzie tenant ID (can be found in the 'About' box in Mindzie Studio for the project you want to upload data into)
- **PROJECT_ID**: The project ID within your tenant (can be found in the 'About' box in Mindzie Studio for the project you want to upload data into)
- **API_KEY**: Your API key for authentication (can be retrieved in Mindzie Studio under Administration Settings, subsection API keys)

The `.env` file should be placed in the same directory as the upload scripts (e.g., `src/`).

### 1. Upload Daily Event Log
- **Script:** `src/daily_dataset_upload.py`
- **How to run:**
  ```bash
  python src/daily_dataset_upload.py
  ```
- This will generate the daily event log and upload it to Mindzie Studio.

### 2. Upload Historical Event Log
- **Script:** `src/historical_dataset_upload.py`
- **How to run:**
  ```bash
  python src/historical_dataset_upload.py
  ```
- This will generate the historical event log and upload it to Mindzie Studio. 