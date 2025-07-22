# Historical Process Specification: Emergency Department Event Log

This document defines the requirements and rules for generating the historical synthetic event log dataset for the Emergency Department (ED).

---

## 1. Date Range
- The historical dataset covers the period from **January 1, 2025** to **May 3, 2025** (inclusive).
- Each day in this range will have a corresponding event log, representing a full day of ED operations.

## 2. Daily Data Requirements
- The ED is open every day; there are no closed days in the dataset.
- Each day should have a realistic number of cases (patients), reflecting typical hospital operations.
- Daily case counts should be consistent with the current day dataset and the ED's bed capacity.

## 3. Volume Patterns by Day of Week
- Patient volume should vary by day of week:
    - **Weekends (especially Saturdays):** Typically busier, higher patient counts.
    - **Mondays:** Often less busy than weekends.
    - **Other weekdays:** Moderate volume.
- Consider including public holidays or special events if relevant.

## 4. Bed Capacity and Resource Constraints
- The ED has sufficient bed capacity for the generated patient volume.
- Daily case volume should be set so that bed occupancy is realistic, with some days approaching or exceeding capacity to simulate operational stress.

## 5. Staffing Model
To create realistic historical data, the following human resources are modeled:

### Doctors
- **Total unique doctors:** 10
- **Coverage:** 2–3 doctors per shift (day, evening, night), with some overlap for handover

### Nurses
- **Total unique nurses:** 18
- **Coverage:** 5–7 nurses per shift, with overlap for breaks and handover

### Other Staff
- **Nurse Practitioners / Physician Assistants:** 4
- **Registration Clerks:** 3
- **Diagnostic Technicians:** 4

**Note:** All staff are referenced by first name only in the data for privacy and simplicity.

## 6. Anomaly and Problem Injection
The historical dataset will include periods or days with operational problems, such as:
- **Bed shortages:** More patients than beds available, leading to long waits for bed assignment.
- **Doctor shortages:** Fewer available doctors, causing delays in doctor examination and downstream stages.
- **Test bottlenecks:** Delays in diagnostic testing or results processing.
- **Staff shortages:** Reduced capacity across various roles.

## 7. Data Generation Rules
- Rules for generating patient journeys, activity sequences, and timestamps are based on the current day process.
- Stage durations, wait time thresholds, and activity patterns should be consistent with the process specifications.
- The historical generator uses the same activity definitions and case attributes as the daily generator.

### Case Attributes
Each case includes the same attributes as the daily dataset:
- **CaseId** - Unique identifier for the patient visit (format: ED######)
- **PatientID** - Unique identifier for the patient (format: P####)
- **Age** - Patient age (skewed toward adults, includes children and elderly)
- **Sex** - Patient gender (M/F)
- **ModeOfArrival** - How the patient arrived (Ambulance, Walk-in, etc.)
- **VisitType** - Type of visit (Emergency, Urgent, etc.)
- **VitalSigns** - Object containing heart rate, blood pressure, temperature, O2 saturation
- **Triage** - Triage level (1-5, ESI/CTAS scale, weighted toward level 3)
- **ArrivalShift** - Time of arrival shift (Day: 7-15h, Evening: 15-23h, Night: 23-7h)

### Activities
The same 16 activities are used as defined in `src/activities.json`:
1. Registration, 2. Triage, 3. Bed Assigned, 4. Nurse Assessment, 5. Doctor Examination
6. Diagnostic Test Ordered, 7. Blood Test Performed, 8. Imaging Performed, 9. Test Results Available
10. Treatment Administered, 11. Observation, 12. Specialist Consultation, 13. Disposition Decision Recorded
14. Discharged, 15. Admitted to Hospital, 16. Transferred to Another Facility

## 8. Validation and Quality Checks
The generated historical data should be validated for:
- Realistic daily and weekly volume patterns
- No impossible overlaps (e.g., more patients in beds than capacity)
- Consistency with process rules and thresholds
- Correct injection of anomalies
- Proper case attribute generation and distribution

## 9. Output Format
The historical dataset is generated in the same formats as the daily dataset:
- **JSON format:** Complete case objects with all attributes and activities
- **CSV format:** Event-level data with one row per activity

## 10. Integration with Current Day Data
- The historical dataset should seamlessly connect with the current day snapshot (May 4th, 2025 at 14:00:00)
- Completed cases in the historical data should not overlap with in-progress cases in the current day data
- The historical data provides the baseline for process mining analysis (bottlenecks, rework, conformance)

---

## Implementation Notes

### Script Location
- **Historical Generator:** `src/historical_event_log.py`
- **Output Files:** 
  - `src/Output/alderaan_year_to_date.json`
  - `src/Output/alderaan_year_to_date.csv`

### Key Features
- **Reproducible:** Uses fixed random seed for consistent results
- **Realistic:** Includes day-of-week patterns and operational anomalies
- **Complete:** Covers all activities and case attributes
- **Validated:** Includes quality checks and statistics reporting

### Usage
```bash
python src/historical_event_log.py
```

This generates the complete historical dataset for process mining analysis and provides the foundation for understanding long-term patterns, bottlenecks, and process improvements in the Emergency Department. 