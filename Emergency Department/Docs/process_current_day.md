# Current Day Process Specification: Emergency Department Event Log

This document contains all specifications and rules for generating and analyzing the current day's (daily snapshot) synthetic event log for the Emergency Department.

For general process and historical specifications, see [process_specifications.md](process_specifications.md).

---

## Main Patient Waiting Stages and Time Thresholds
*Stages represent what the patient is waiting for, not always a 1:1 mapping to activities.*

| Stage                              | Medium Threshold (min) | High Threshold (min) |
|-------------------------------------|------------------------|----------------------|
| Waiting for Registration           | 10                     | 30                   |
| Waiting for Triage                 | 15                     | 45                   |
| Waiting for Bed                    | 20                     | 60                   |
| Waiting for Nurse Assessment       | 10                     | 30                   |
| Waiting for Doctor                 | 30                     | 90                   |
| Waiting for Diagnostic Test        | 20                     | 60                   |
| Waiting for Test Results           | 60                     | 180                  |
| Waiting for Treatment              | 15                     | 45                   |
| Waiting for Observation Completion | None                   | None                 |
| Waiting for Specialist Consultation| 60                     | 180                  |
| Waiting for Disposition Decision   | 15                     | 45                   |
| Waiting for Admission to Hospital  | 30                     | 90                   |
| Waiting for Transfer to Another Facility | 60              | 180                  |

*Note: Observation completion has no thresholds as it's a clinical decision-based activity. The thresholds are used for real-time monitoring and alerting in the command centre.*

---

## Process Flow and Stage Mapping
The patient journey follows this typical path with corresponding waiting stages:

1. **Registration** → Waiting for Registration
2. **Triage** → Waiting for Triage  
3. **Bed Assigned** → Waiting for Bed
4. **Nurse Assessment** → Waiting for Nurse Assessment
5. **Doctor Examination** → Waiting for Doctor
6. **Diagnostic Test Ordered** → Waiting for Diagnostic Test (optional)
7. **Blood Test Performed / Imaging Performed** → Waiting for Test Results
8. **Test Results Available** → Waiting for Treatment
9. **Treatment Administered** → Waiting for Observation Completion (optional)
10. **Observation** → Waiting for Specialist Consultation (optional)
11. **Specialist Consultation** → Waiting for Disposition Decision
12. **Disposition Decision Recorded** → Waiting for Final Outcome
13. **Final Outcome** → Discharged / Admitted to Hospital / Transferred to Another Facility

---

## Key Timestamps for Stage Duration Calculation
The following table lists all the key timestamps (case attributes) needed to calculate the durations for each stage. Each timestamp corresponds to the ActivityTime of the specified activity, if it exists for the case.

| Attribute Name                  | Corresponding Activity                |
|----------------------------------|--------------------------------------|
| RegistrationTime                 | Registration                         |
| TriageTime                       | Triage                               |
| BedAssignedTime                  | Bed Assigned                         |
| NurseAssessmentTime              | Nurse Assessment                     |
| DoctorExaminationTime            | Doctor Examination                   |
| DiagnosticTestOrderedTime        | Diagnostic Test Ordered              |
| BloodTestPerformedTime           | Blood Test Performed (if present)    |
| ImagingPerformedTime             | Imaging Performed (if present)       |
| TestResultsAvailableTime         | Test Results Available               |
| TreatmentAdministeredTime        | Treatment Administered               |
| ObservationTime                  | Observation                          |
| SpecialistConsultationTime       | Specialist Consultation              |
| DispositionDecisionTime          | Disposition Decision Recorded        |
| DischargedTime                   | Discharged                           |
| AdmittedToHospitalTime           | Admitted to Hospital                 |
| TransferredToAnotherFacilityTime | Transferred to Another Facility     |

---

## Rules for Calculating Time in Each Stage

### Waiting for Registration
- **Rule:** The patient is waiting for registration from arrival until the 'Registration' activity is completed.
- **Calculation:** Time from case start to 'Registration'.
- **Edge Cases:** If registration is the first activity, wait time is 0.

### Waiting for Triage
- **Rule:** The patient has completed 'Registration' and is waiting for 'Triage'.
- **Calculation:** Time from 'Registration' to 'Triage'.
- **Edge Cases:** If the next activity after registration is not 'Triage', the patient is not considered to have waited for triage.

### Waiting for Bed
- **Rule:** The patient has completed 'Triage' and is waiting for 'Bed Assigned'.
- **Calculation:** Time from 'Triage' to 'Bed Assigned'.
- **Edge Cases:** If 'Bed Assigned' is skipped, the patient is not considered to have waited for a bed.

### Waiting for Nurse Assessment
- **Rule:** The patient has completed 'Bed Assigned' and is waiting for 'Nurse Assessment'.
- **Calculation:** Time from 'Bed Assigned' to 'Nurse Assessment'.
- **Edge Cases:** If 'Nurse Assessment' is skipped, the patient is not considered to have waited for nurse assessment.

### Waiting for Doctor
- **Rule:** The patient has completed 'Nurse Assessment' and is waiting for 'Doctor Examination'.
- **Calculation:** Time from 'Nurse Assessment' to 'Doctor Examination'.

### Waiting for Diagnostic Test
- **Rule:** The patient has completed 'Doctor Examination' and is waiting for 'Diagnostic Test Ordered'.
- **Calculation:** Time from 'Doctor Examination' to 'Diagnostic Test Ordered'.
- **Note:** If no diagnostic test is ordered, the patient does not enter this stage.

### Waiting for Test Results
- **Rule:** The patient has had a diagnostic test performed and is waiting for 'Test Results Available'.
- **Calculation:** Time from last diagnostic test performed to 'Test Results Available'.
- **Edge Cases:** If no test is performed, the patient does not enter this stage.

### Waiting for Treatment
- **Rule:** The patient is waiting for treatment after test results or doctor examination.
- **Calculation:** Time from 'Test Results Available' (or 'Doctor Examination' if no tests) to 'Treatment Administered'.
- **Edge Cases:** If no treatment is administered, the patient does not enter this stage.

### Waiting for Observation Completion
- **Rule:** The patient has started 'Observation' and is waiting for the next activity.
- **Calculation:** Time from 'Observation' to the next activity.
- **Edge Cases:** If the last activity is 'Observation', the patient is in this stage.

### Waiting for Specialist Consultation
- **Rule:** The patient is waiting for a specialist consultation.
- **Calculation:** Time from request to 'Specialist Consultation'.
- **Note:** This is an optional stage that may not occur for all patients.

### Waiting for Disposition Decision
- **Rule:** The patient has completed all required assessments and is waiting for a disposition decision.
- **Calculation:** Time from last relevant activity to 'Disposition Decision Recorded'.

### Waiting for Final Outcome
- **Rule:** The patient has a disposition decision and is waiting for the final outcome.
- **Calculation:** Time from 'Disposition Decision Recorded' to final outcome (Discharged/Admitted/Transferred).

---

## Desired Wait Times by Activity
*These are the target or ideal wait times for operational planning.*

- **Registration:** ≤ 10 minutes
- **Triage:** ≤ 15 minutes after registration
- **Bed Assigned:** ≤ 20 minutes after triage
- **Nurse Assessment:** ≤ 10 minutes after bed assignment
- **Doctor Examination:** ≤ 30 minutes after nurse assessment
- **Diagnostic Test Ordered:** Immediate if required
- **Blood Test Performed:** ≤ 15 minutes after order
- **Imaging Performed:** ≤ 30 minutes after order
- **Test Results Available:** ≤ 60 minutes after test performed
- **Treatment Administered:** ≤ 15 minutes after results/diagnosis
- **Observation:** As clinically required (varies)
- **Specialist Consultation:** ≤ 60 minutes after request
- **Disposition Decision Recorded:** ≤ 15 minutes after all results/consults
- **Discharged:** Immediate after disposition decision
- **Admitted to Hospital:** ≤ 30 minutes after disposition decision

---

## Emergency Department Capacity

- **Bed Capacity:** Sufficient for generated patient volume
- The synthetic event log and all calculations should reflect realistic bed occupancy patterns
- This constraint should be considered in the generation of synthetic data and in any dashboard or process analysis

---

## FreezeTime (Snapshot Time)

The event log is generated as a snapshot of the Emergency Department at a specific point in time, called the **FreezeTime**. This is the reference time for all calculations of waiting times and for determining which patients are currently in progress versus completed.

```
"FreezeTime": "2025-05-04T14:00:00+00:00"
```

- All waiting time calculations for in-progress cases are based on the difference between the FreezeTime and the timestamp of the last completed activity for each case.
- The FreezeTime is set in the generator script and should always reflect the current snapshot time for the log.
- The FreezeTime is documented in the README and should be kept consistent across all documentation and analysis.

---

## Case Distribution (Current Day)

### Completed Cases: 100 total
- **Discharged:** 83 cases (83%)
- **Admitted to Hospital:** 17 cases (17%)

### In-Progress Cases: Variable based on stage thresholds
- **Triage:** 11 cases (6 OK, 3 warning, 2 critical)
- **Bed Assignment:** 4 cases (4 OK)
- **Nurse Assessment:** 6 cases (5 OK, 1 warning)
- **Doctor Examination:** 5 cases (5 OK)
- **Test Results:** 4 cases (3 OK, 1 warning)
- **Treatment:** 4 cases (3 OK, 1 warning)
- **Observation:** 13 cases (9 OK, 4 warning)
- **Disposition Decision:** 8 cases (6 OK, 2 warning)

### LWBS Cases: ~2% of total cases

---

## Implementation Notes

### Script Location
- **Daily Generator:** `src/daily_event_log.py`
- **Output Files:** 
  - `src/Output/alderaan_daily.json`
  - `src/Output/alderaan_daily.csv`

### Key Features
- **Real-time Focus:** Designed for operational monitoring and command centre dashboards
- **Stage-based Monitoring:** Tracks waiting times for each stage with configurable thresholds
- **In-progress Cases:** Includes patients currently in the ED at the snapshot time
- **Case Attributes:** Complete patient information for operational decision-making

### Usage
```bash
python src/daily_event_log.py
```

This generates the current day snapshot dataset for real-time process flow monitoring and operational decision-making in the Emergency Department command centre. 