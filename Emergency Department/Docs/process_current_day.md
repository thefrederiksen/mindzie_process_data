# Current Day Process Specification: Emergency Department Event Log

This document contains all specifications and rules for generating and analyzing the current day's (daily snapshot) synthetic event log for the Emergency Department.

For general process and historical specifications, see [Process specifications.md](Process%20specifications.md).

---

## Main Patient Waiting Stages and Time Thresholds
*Stages represent what the patient is waiting for, not always a 1:1 mapping to activities.*

| Stage                              | Warning Time (min) | Critical Time (min) |
|-------------------------------------|--------------------|---------------------|
| Waiting for Triage                 | 15                 | 45                  |
| Waiting for Bed                    | 20                 | 60                  |
| Waiting for Nurse Assessment       | 10                 | 30                  |
| Waiting for Doctor                 | 30                 | 90                  |
| Waiting for Test Results           | 60                 | 180                 |
| Waiting for Treatment              | 15                 | 45                  |
| Waiting for Observation Completion | Varies             | Varies              |
| Waiting for Specialist Consultation| 60                 | 180                 |
| Waiting for Disposition Decision   | 15                 | 45                  |
| Admitted to Hospital (case duration) | 180               | 300                 |
| Discharged (case duration)           | 180               | 300                 |

*Note: 'Waiting for Discharge' is no longer tracked as a stage. For the final outcome stages (Discharged, Admitted to Hospital), the dashboard/calculator uses the total case duration (from Registration to the final activity). The medium (warning) threshold is 3 hours (180 min), and the high (critical) threshold is 5 hours (300 min) for all three. These values reflect operational targets for timely ED throughput.*

---

## High-Level Process Groups for Dashboarding (Dashboard Version 1)
The dashboard groups and names stages as follows (see attached image for layout):

1. **Triage**
2. **Nurse Assessment**
3. **Bed Assignment**
4. **Doctor Examination**
5. **Specialist Consultation**
6. **Test Results** 
7. **Treatment Administered**
8. **Disposition Decision Recorded**
9. **Observation Completion**
10. **Discharged**
11. **Admitted to Hospital**

*'Diagnostic Test Ordered' is not shown as a separate stage. 'Test Results' is the new label for the stage previously called 'Test Results Available'.*

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

---

## Rules for Calculating Time in Each Stage
Below, each stage is described with the logic for determining when a patient is considered to be in that stage, based on the sequence of activities in the event log.

### Waiting for Triage
- **Rule:** The patient has a 'Registration' activity, and the next activity has not yet occurred. The patient is waiting for triage from the time of registration until the time of 'Triage'.
- **Calculation:** Time from 'Registration' to 'Triage'.
- **Edge Cases:** If the next activity after registration is not 'Triage' (e.g., 'Discharged'), the patient is not considered to have waited for triage.

### Waiting for Bed
- **Rule:** The patient is considered to be in the 'Waiting for Bed' stage if their most recent (last) activity is 'Triage' and 'Bed Assigned' has not yet occurred. This means the patient has completed triage and is waiting for a bed assignment. If the patient skips 'Bed Assigned' entirely (i.e., another activity occurs after 'Triage' without a 'Bed Assigned' event), they are **not** considered to be in this stage.
- **Calculation:** Time from 'Triage' to 'Bed Assigned'.
- **Edge Cases:** If the last activity is 'Triage' and 'Bed Assigned' has not occurred, the patient is in this stage. If 'Bed Assigned' is skipped, the patient is not considered to have waited for a bed.

### Waiting for Nurse Assessment
- **Rule:** The patient is considered to be in the 'Waiting for Nurse Assessment' stage if their most recent (last) activity is 'Bed Assigned' and 'Nurse Assessment' has not yet occurred. This means the patient has been assigned a bed and is waiting for a nurse assessment. If the patient skips 'Nurse Assessment' entirely (i.e., another activity occurs after 'Bed Assigned' without a 'Nurse Assessment' event), they are **not** considered to be in this stage.
- **Calculation:** Time from 'Bed Assigned' to 'Nurse Assessment'.
- **Edge Cases:** If the last activity is 'Bed Assigned' and 'Nurse Assessment' has not occurred, the patient is in this stage. If 'Nurse Assessment' is skipped, the patient is not considered to have waited for nurse assessment.

### Waiting for Doctor
- **Rule:** The patient has completed 'Nurse Assessment', and 'Doctor Examination' has not yet occurred. The patient is waiting for a doctor from 'Nurse Assessment' to 'Doctor Examination'.
- **Calculation:** Time from 'Nurse Assessment' to 'Doctor Examination'.

### Waiting for Diagnostic Test
- **Rule:** The patient has completed 'Doctor Examination', and 'Diagnostic Test Ordered' has not yet occurred. The patient is waiting for a diagnostic test from 'Doctor Examination' to 'Diagnostic Test Ordered'.
- **Calculation:** Time from 'Doctor Examination' to 'Diagnostic Test Ordered'.
- **Note:** If no diagnostic test is ordered, the patient does not enter this stage.

### Waiting for Test Results
- **Rule:** The patient has had a diagnostic test performed (e.g., 'Blood Test Performed' or 'Imaging Performed'), and 'Test Results Available' has not yet occurred. The patient is waiting for test results from the last test performed to 'Test Results Available'.
- **Calculation:** Time from last diagnostic test performed to 'Test Results Available'.
- **Edge Cases:** If the last activity is a test performed and 'Test Results Available' has not occurred, the patient is in this stage. If no test is performed, the patient does not enter this stage.

### Waiting for Treatment
- **Rule:** The patient is waiting for treatment if:
    - The last activity is 'Test Results Available' and 'Treatment Administered' has not yet occurred, **or**
    - The last activity is 'Doctor Examination', no diagnostic test is ordered, and 'Treatment Administered' has not yet occurred.
- **Calculation:**
    - If the last activity is 'Test Results Available', time from 'Test Results Available' to 'Treatment Administered'.
    - If the last activity is 'Doctor Examination' (and no test ordered), time from 'Doctor Examination' to 'Treatment Administered'.
- **Edge Cases:**
    - If a diagnostic test is ordered after 'Doctor Examination', the patient is not in this stage until after 'Test Results Available'.
    - A patient can only be in one waiting stage at a time.

### Waiting for Observation Completion
- **Rule:** The patient has received treatment or a procedure and is under observation ('Observation'), and the observation period is ongoing. The patient is waiting for observation completion from the start of 'Observation' until the next activity (e.g., 'Disposition Decision Recorded').
- **Calculation:** Time from 'Observation' to the next activity.
- **Edge Cases:** If the last activity is 'Observation' and no subsequent activity has occurred, the patient is in this stage.

### Waiting for Specialist Consultation
- **Rule:** The patient has had a specialist consultation requested, and 'Specialist Consultation' has not yet occurred. The patient is waiting for a specialist from the time of the request (e.g., after 'Doctor Examination' or 'Test Results Available') to 'Specialist Consultation'.
- **Calculation:** Time from the request to 'Specialist Consultation'.

### Waiting for Disposition Decision
- **Rule:** The patient has completed all required assessments, tests, and treatments, and is waiting for a disposition decision. This stage is from the last relevant activity (e.g., 'Treatment Administered', 'Observation', or 'Specialist Consultation') to 'Disposition Decision Recorded'.
- **Calculation:** Time from last relevant activity to 'Disposition Decision Recorded'.

### Waiting for Discharge
- **Rule:** The patient has a disposition decision to discharge, and 'Discharged' has not yet occurred. The patient is waiting for discharge from 'Disposition Decision Recorded' to 'Discharged'.
- **Calculation:** Time from 'Disposition Decision Recorded' to 'Discharged'.

### Waiting for Admission to Hospital
- **Rule:** The patient has a disposition decision to admit, and 'Admitted to Hospital' has not yet occurred. The patient is waiting for admission from 'Disposition Decision Recorded' to 'Admitted to Hospital'.
- **Calculation:** Time from 'Disposition Decision Recorded' to 'Admitted to Hospital'.

---

## Desired Wait Times by Activity
*These are the target or ideal wait times as expressed by hospital staff. Actual times may vary in practice.*

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

- **Number of beds:** 30
- The synthetic event log and all calculations should reflect this capacity: at most 30 patients can be assigned to a bed simultaneously, with additional patients waiting for bed assignment if all beds are occupied.
- This constraint should be considered in the generation of synthetic data and in any dashboard or process analysis.

---

## FreezeTime (Snapshot Time)

The event log is generated as a snapshot of the Emergency Department at a specific point in time, called the **FreezeTime** (or snapshot time). This is the reference time for all calculations of waiting times and for determining which patients are currently in progress versus completed. The FreezeTime is included in the event log output as a top-level field:

```
"FreezeTime": "2025-05-04T14:00:00+00:00"
```

- All waiting time calculations for in-progress cases are based on the difference between the FreezeTime and the timestamp of the last completed activity for each case.
- The FreezeTime is set in the generator script and should always reflect the current snapshot time for the log.
- The FreezeTime is also documented in the README and should be kept consistent across all documentation and analysis.

<!-- Add any other daily-specific rules or details here as needed. --> 