# Historical Process Specification: Emergency Department Event Log

This document defines the requirements and rules for generating the historical synthetic event log dataset for the Emergency Department (ED).

---

## 1. Date Range
- The historical dataset will cover the period from **January 1, 2025** to **May 3, 2025** (inclusive).
- Each day in this range will have a corresponding event log, representing a full day of ED operations.

## 2. Daily Data Requirements
- The ED is open every day; there are no closed days in the dataset.
- Each day should have a realistic number of cases (patients), reflecting typical hospital operations.
- Daily case counts should be consistent with the current day dataset and the ED's bed capacity (currently 40 beds).

## 3. Volume Patterns by Day of Week
- Patient volume should vary by day of week:
    - **Weekends (especially Saturdays):** Typically busier, higher patient counts.
    - **Mondays:** Often less busy than weekends.
    - **Other weekdays:** Moderate volume.
- Consider including public holidays or special events if relevant (to be specified).

## 4. Bed Capacity and Resource Constraints
- The ED has 40 beds; at most 40 patients can be assigned a bed at any one time.
- Daily case volume should be set so that bed occupancy is realistic, with some days approaching or exceeding capacity to simulate operational stress.

## 4a. Emergency Department Human Resources (Staffing)

To create realistic historical data and process mining analyses, the following human resources are modeled for an Emergency Department with 40 beds and typical patient volumes:

### Doctors
- **Total unique doctors:** 10
- **Example first names:** Peter, Maria, John, Priya, Ahmed, Emily, David, Chen, Anna, Luis
- **Coverage:** 2–3 doctors per shift (day, evening, night), with some overlap for handover

### Nurses
- **Total unique nurses:** 18
- **Example first names:** Sarah, Tom, Lisa, Kevin, Zoe, Mark, Julia, Sam, Chloe, Ben, Mia, Alex, Grace, Leo, Ella, Jack, Sophie, Max
- **Coverage:** 5–7 nurses per shift, with overlap for breaks and handover

### Nurse Practitioners / Physician Assistants (optional)
- **Total unique NPs/PAs:** 4
- **Example first names:** Olivia, Ryan, Hannah, Josh
- **Coverage:** 1 per shift, often supporting triage or fast-track

### Registration Clerks
- **Total unique clerks:** 3
- **Example first names:** Emma, Paul, Rita
- **Coverage:** 1 per shift

### Diagnostic Technicians (Lab/Imaging)
- **Total unique techs:** 4
- **Example first names:** Steve, Maya, Ivan, Tara
- **Coverage:** 1–2 per shift, depending on volume

### Other Roles (as needed)
- **Security, Porters, Housekeeping:** Not directly involved in clinical activities but may be referenced for completeness

**Note:** All staff are referenced by first name only in the data for privacy and simplicity. Staff are assigned to activities based on their role and shift, ensuring realistic resource allocation and handover patterns.

## 5. Anomaly and Problem Injection (for Process Mining/Analysis)
- The historical dataset will include periods or days with operational problems, such as:
    - **Bed shortages:** More patients than beds available, leading to long waits for bed assignment.
    - **Doctor shortages:** Fewer available doctors, causing delays in doctor examination and downstream stages.
    - **Other issues:** (to be defined, e.g., diagnostic test bottlenecks, staff shortages, etc.)
- These anomalies will be injected after the baseline data generation is validated.

## 6. Data Generation Rules (to be detailed)
- Rules for generating patient journeys, activity sequences, and timestamps will be based on the current day process, with adjustments for historical realism and volume.
- Stage durations, wait time thresholds, and activity patterns should be consistent with the process specifications, unless simulating an anomaly.

## 7. Validation and Quality Checks
- The generated historical data should be validated for:
    - Realistic daily and weekly volume patterns
    - No impossible overlaps (e.g., more patients in beds than capacity)
    - Consistency with process rules and thresholds
    - Correct injection of anomalies

## 8. Living Document
- This specification will be refined as requirements are clarified and as data generation and analysis proceed.
- Open questions and design decisions should be documented here for discussion.

---

## Step-by-Step Plan for Historical Data Creation and Analysis

1. **Generate Baseline Historical Event Log**
   - Create a complete, clean event log for the historical period (2025-01-01 to 2025-05-03) with realistic patient flows and volumes.
   - Ensure all core activities and stages are represented, and match daily/weekly/monthly volumes to realistic patterns (e.g., weekends busier).
   - Include all outcome types: Discharged, Admitted, Left Without Being Seen (LWBS).

2. **Calculate and Enrich Stage Durations**
   - For each case, calculate the duration spent in each stage (e.g., Waiting for Triage, Waiting for Bed) using activity timestamps.
   - Handle edge cases (e.g., skipped stages, incomplete cases).

3. **Assign Stage Threshold Compliance**
   - For each stage, determine if the duration is within warning, between warning and critical, or above critical, using thresholds from the process specification.
   - Add compliance labels to each case/stage.

4. **Inject Operational Anomalies**
   - Simulate real-world problems (e.g., bed shortages, doctor shortages, test bottlenecks) on selected days/weeks.
   - Increase wait times or case volumes on anomaly days and mark these cases/days for later analysis.

5. **Generate Resource Utilization Data**
   - Track bed occupancy, doctor/nurse workload, and diagnostic resource usage.
   - For each day/hour, calculate number of beds occupied; optionally, infer staff workload from activity timestamps.

6. **Add LWBS and Other Special Variants**
   - Ensure a realistic percentage of LWBS cases, with variants (leaving at different stages).
   - Distribute LWBS cases across the date range and stages, and correlate spikes with known anomalies.

7. **Create Process Mining Artifacts**
   - Prepare data for process mining (variant analysis, conformance checking, bottleneck detection).
   - Export event log in a format suitable for process mining tools and annotate cases with variant IDs, conformance scores, etc.

8. **Aggregate Data for Dashboards**
   - Summarize data for dashboard metrics (per day, week, month, stage, outcome).
   - Calculate patient volumes, wait times, compliance rates, LWBS rates, etc., and prepare summary tables for each dashboard user group.

9. **Validate Against Historical Benchmarks**
   - Ensure generated data matches expected historical patterns and thresholds.
   - Compare generated metrics to real-world or literature benchmarks and adjust generation logic as needed for realism.

10. **Document and Automate the Pipeline**
    - Make the data generation and analysis repeatable and transparent.
    - Document each step and its parameters, and create scripts/notebooks for each analysis and dashboard export.

---

*Use this plan to guide the incremental development of your historical data and analysis pipeline. Each step can be implemented and validated independently before moving to the next.* 