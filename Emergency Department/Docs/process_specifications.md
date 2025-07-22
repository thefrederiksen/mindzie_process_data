# Process Specifications: Emergency Department Event Log

## Introduction
This document outlines the process specifications for the Emergency Department (ED) event log, including activities, case attributes, stage thresholds, and data generation rules. This specification applies to both historical analysis and real-time monitoring datasets.

---

## Activities Tracked
The following activities are logged in the ED event log (as defined in `src/activities.json`):

1. **Registration** - The patient has completed the registration process at the front desk
2. **Triage** - The triage nurse has finished assessing the patient's condition and assigned a triage level
3. **Bed Assigned** - The patient has been assigned a bed in the emergency department
4. **Nurse Assessment** - The nurse has completed the initial assessment of the patient in their assigned bed
5. **Doctor Examination** - The doctor has finished examining the patient and recorded their findings
6. **Diagnostic Test Ordered** - The doctor has ordered one or more diagnostic tests for the patient
7. **Blood Test Performed** - A blood test has been performed on the patient and the sample has been sent to the lab
8. **Imaging Performed** - An imaging test (such as X-ray or CT scan) has been performed on the patient
9. **Test Results Available** - The results of the ordered diagnostic tests are now available in the system
10. **Treatment Administered** - The patient has received treatment, medication, or a procedure as ordered by the doctor
11. **Observation** - The patient has completed a period of observation in the emergency department
12. **Specialist Consultation** - A specialist has completed their consultation with the patient
13. **Disposition Decision Recorded** - The doctor has recorded the decision regarding the patient's next steps
14. **Discharged** - The patient has been discharged from the emergency department and has left the facility
15. **Admitted to Hospital** - The patient has been admitted to an inpatient ward for further care
16. **Transferred to Another Facility** - The patient has been transferred to another healthcare facility for further treatment

**Note**: The "Left Without Being Seen" (LWBS) activity is generated in the code but not included in the activities.json file. LWBS cases represent approximately 2% of total cases and are important for operational analysis.

---

## Case Attributes
Each case includes the following attributes (generated in `src/daily_event_log.py`):

- **CaseId** - Unique identifier for the patient visit (format: ED######)
- **PatientID** - Unique identifier for the patient (format: P####)
- **Age** - Patient age (skewed toward adults, includes children and elderly)
- **Sex** - Patient gender (M/F)
- **ModeOfArrival** - How the patient arrived (Ambulance, Walk-in, etc.)
- **VisitType** - Type of visit (Emergency, Urgent, etc.)
- **VitalSigns** - Object containing:
  - HeartRate (60-120 bpm)
  - BloodPressure (systolic 90-180, diastolic 60-100)
  - Temperature (36.5-39.0°C)
  - O2Sat (90-100%)
- **Triage** - Triage level (1-5, ESI/CTAS scale, weighted toward level 3)
- **ArrivalShift** - Time of arrival shift (Day: 7-15h, Evening: 15-23h, Night: 23-7h)

---

## Stage Thresholds
The following waiting stages are monitored with medium and high thresholds (in minutes):

| Stage | Medium Threshold | High Threshold |
|-------|------------------|----------------|
| Waiting for Registration | 10 | 30 |
| Waiting for Triage | 15 | 45 |
| Waiting for Bed | 20 | 60 |
| Waiting for Nurse Assessment | 10 | 30 |
| Waiting for Doctor | 30 | 90 |
| Waiting for Diagnostic Test | 20 | 60 |
| Waiting for Test Results | 60 | 180 |
| Waiting for Treatment | 15 | 45 |
| Waiting for Observation Completion | None | None |
| Waiting for Specialist Consultation | 60 | 180 |
| Waiting for Discharge | 15 | 45 |
| Waiting for Admission to Hospital | 30 | 90 |
| Waiting for Transfer to Another Facility | 60 | 180 |

**Note**: Observation completion has no thresholds as it's a clinical decision-based activity.

---

## Process Flow
The typical patient journey follows this path (with optional activities):

1. **Registration** (always)
2. **Triage** (always)
3. **Bed Assigned** (always)
4. **Nurse Assessment** (always)
5. **Doctor Examination** (always)
6. **Diagnostic Test Ordered** (70% probability)
   - **Blood Test Performed** (80% of test orders)
   - **Imaging Performed** (50% of test orders)
   - **Test Results Available** (always after tests)
7. **Treatment Administered** (80% probability)
8. **Observation** (30% probability)
9. **Specialist Consultation** (10% probability)
10. **Disposition Decision Recorded** (always)
11. **Final Outcome** (always):
    - **Discharged** (83% of completed cases)
    - **Admitted to Hospital** (17% of completed cases)
    - **Transferred to Another Facility** (rare)

---

## Data Generation Rules

### FreezeTime (Snapshot Time)
- **Date**: May 4th, 2025 at 14:00:00 (2:00 PM)
- **Purpose**: Reference time for all waiting time calculations
- **Format**: "2025-05-04T14:00:00+00:00"

### Case Distribution
- **Completed Cases**: 100 total
  - Discharged: 83 cases (83%)
  - Admitted: 17 cases (17%)
- **In-Progress Cases**: Variable based on stage thresholds
  - Triage: 11 cases (6 OK, 3 warning, 2 critical)
  - Bed Assignment: 4 cases (4 OK)
  - Nurse Assessment: 6 cases (5 OK, 1 warning)
  - Doctor Examination: 5 cases (5 OK)
  - Test Results: 4 cases (3 OK, 1 warning)
  - Treatment: 4 cases (3 OK, 1 warning)
  - Observation: 13 cases (9 OK, 4 warning)
  - Disposition Decision: 8 cases (6 OK, 2 warning)
- **LWBS Cases**: ~2% of total cases

### Time Generation
- **Activity Intervals**: 5-30 minutes between activities
- **Random Seed**: Fixed at 42 for reproducibility
- **Backward Generation**: In-progress cases generate timestamps backward from FreezeTime
- **Forward Generation**: Completed cases generate timestamps forward from start time

---

## Output Formats

### JSON Format
```json
{
  "FreezeTime": "2025-05-04T14:00:00+00:00",
  "cases": [
    {
      "CaseId": "ED123456",
      "PatientID": "P001",
      "Age": 45,
      "Sex": "M",
      "ModeOfArrival": "Walk-in",
      "VisitType": "Emergency",
      "VitalSigns": {...},
      "Triage": 3,
      "ArrivalShift": "Day",
      "activities": [...]
    }
  ]
}
```

### CSV Format
Each row represents one activity:
- CaseId, ActivityName, ActivityTime, PatientID, Age, Sex, ModeOfArrival, VisitType, VitalSigns, Triage, ArrivalShift

---

## Notes
- All data is synthetic and for process mining research and education only
- The generator uses a fixed random seed for reproducible results
- Case attributes are constant for all events within a case
- LWBS cases are important for operational analysis and quality improvement
- The system supports both historical analysis and real-time monitoring datasets
- Stage durations are calculated based on the difference between FreezeTime and the last completed activity for in-progress cases 