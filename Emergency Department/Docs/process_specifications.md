# Process Specifications: Emergency Department Event Log

## Introduction
This document outlines the general and historical process specifications for the Emergency Department (ED) event log. For the current day (daily snapshot) process and synthetic data generation, see [process_current_day.md](process_current_day.md).

---

## Activities Tracked
The following activities are logged in the ED event log:

1. **Registration**
2. **Triage**
3. **Bed Assigned**
4. **Nurse Assessment**
5. **Doctor Examination**
6. **Diagnostic Test Ordered**
7. **Blood Test Performed**
8. **Imaging Performed**
9. **Test Results Available**
10. **Treatment Administered**
11. **Observation**
12. **Specialist Consultation**
13. **Disposition Decision Recorded**
14. **Discharged**
15. **Admitted to Hospital**
16. **Left Without Being Seen**

**Left Without Being Seen**:
This activity is logged when a patient leaves the Emergency Department before being seen by a provider (doctor or nurse), effectively cancelling the case. It is common in EDs and should be tracked for process analysis and quality improvement. The abbreviation LWBS (Left Without Being Seen) is commonly used in healthcare operations and quality reporting, but the activity name in the event log should be written in full. LWBS is a key operational and quality metric in emergency care, and its frequency can indicate issues with wait times, capacity, or patient satisfaction.

---

<!-- The following sections have been moved to current day.md:
- Main Patient Waiting Stages and Time Thresholds
- High-Level Process Groups for Dashboarding
- Key Timestamps for Stage Duration Calculation
- Rules for Calculating Time in Each Stage
- Desired Wait Times by Activity
- Emergency Department Capacity
- FreezeTime (Snapshot Time)
-->

For daily snapshot and synthetic data generation details, see [current day.md](current%20day.md).

---

## Notes
- Stages and activities are related but not always 1:1. For example, a patient may be waiting for a bed (stage) before the "Bed Assigned" activity is logged.
- Desired wait times are based on best practices and staff input, and may be adjusted for simulation or improvement projects.
- **Dashboard version 1:** The dashboard omits 'Diagnostic Test Ordered' and 'Waiting for Discharge' as waiting stages. For the final outcome stages (Discharged, Admitted to Hospital), the dashboard uses total case duration (Registration to final activity) with thresholds of 3 hours (medium) and 5 hours (high).
- **Synthetic event log and enrichment:** Synthetic event logs are generated for analysis, and all required stage duration columns (e.g., WaitingForDispositionDecision) must be present in the case table. These are created by running the corresponding enrichment blocks (see `stage_durations/`).
- **MCL file conventions:** All MCL files use simple, valid, unique hexadecimal GUIDs for clarity and consistency. Thresholds and time units are set according to this specification.
- This document will be expanded with further process details, diagrams, and requirements as the project evolves. 