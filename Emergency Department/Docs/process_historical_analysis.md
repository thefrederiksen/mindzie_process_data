# Historical Process Analysis: Emergency Department Event Log

This document outlines recommended analyses, dashboards, and process mining approaches for the historical event log of the Emergency Department (ED). The primary goal of historical analysis is to validate and contextualize the waiting times and stage durations observed in the daily process monitoring dashboard. By comparing current performance against historical benchmarks, the hospital can identify trends, anomalies, and improvement opportunities. These analyses support operational intelligence, enabling proactive decision-making in the command center, management oversight, and staff motivation.

All analyses are based on the activities, stages, thresholds, and calculations defined in the process specifications ([process_specifications.md](process_specifications.md) and [process_current_day.md](process_current_day.md)). Historical data covers January 1, 2025, to May 3, 2025, and includes injected anomalies (e.g., bed shortages, doctor shortages) for realistic simulation and root cause analysis.

The analyses are tailored for different user groups:
- **Command Center Dashboard**: Real-time comparison of today's data with historical trends for immediate operational adjustments.
- **Management Dashboard**: High-level overviews of long-term performance, compliance, and strategic insights.
- **ER Staff Dashboard**: Weekly/monthly views focused on team performance to motivate improvements in wait times and efficiency.

Analyses should be implemented using process mining tools (e.g., for variant analysis, conformance checking) and visualization platforms (e.g., dashboards with charts, tables, and filters). Ensure all metrics align with ED capacity (40 beds historically, 30 in current snapshots) and use FreezeTime for snapshot-based calculations in daily views.

---

## 1. Core Metrics and Visualizations
These foundational metrics form the basis for all dashboards. They validate daily stage waiting times (e.g., Waiting for Triage, Waiting for Bed) by providing historical context, such as averages, trends, and anomaly detection.

- **Patient Volume Metrics**:
  - Daily, weekly, and monthly patient counts (total, by outcome: Discharged, Admitted to Hospital, Left Without Being Seen (LWBS)).
  - Breakdown by day of week (e.g., higher volumes on weekends/Saturdays) and anomalies (e.g., spikes during simulated bed shortages).
  - Visualization: Line charts for trends, bar charts for comparisons (e.g., today vs. historical average).

- **Wait Times by Stage**:
  - Average, median, minimum, maximum, and percentile (e.g., 90th) durations for each stage (e.g., Waiting for Triage, Waiting for Doctor, Waiting for Test Results).
  - Distribution histograms to show variability and outliers.
  - Comparison: Today's wait times vs. historical averages (e.g., "Waiting for Bed today: 25 min vs. historical median: 18 min").
  - Edge Cases: Handle skipped stages (e.g., no diagnostic test) by excluding them from averages.

- **Threshold Compliance**:
  - % of cases within warning threshold, exceeding warning (yellow), and exceeding critical (red) for each stage (using thresholds from [process_current_day.md](process_current_day.md), e.g., Waiting for Triage: 15 min warning, 45 min critical).
  - For final outcomes (Discharged/Admitted): % exceeding 180 min (warning) and 300 min (critical) total case duration.
  - Visualization: Stacked bar charts or heatmaps showing compliance trends over time.

- **LWBS Metrics**:
  - Number and % of LWBS cases, correlated with wait times (e.g., higher LWBS during long triage waits).
  - Trend analysis: Spikes during anomalies (e.g., doctor shortages).
  - Visualization: Line chart with annotations for root causes.

- **Bed and Resource Utilization**:
  - Hourly/daily bed occupancy (peak, average; alert if >40 beds historically or >30 currently).
  - Utilization rates for doctors/nurses (if inferred from delays) and diagnostic resources (e.g., imaging bottlenecks).
  - Visualization: Area charts for occupancy over time, with overlays for anomalies.

- **Throughput and Outcome Metrics**:
  - Total case duration from Registration to final activity (Discharged/Admitted/LWBS).
  - Outcome distribution (% Discharged, % Admitted, % LWBS).
  - Busiest periods: By hour, day of week, or month (e.g., peak arrivals on Mondays post-weekend).
  - Visualization: Box plots for durations, pie charts for outcomes.

---

## 2. Process Mining Analyses
Use process mining to uncover patterns in historical data, validating daily observations (e.g., proving that long waits in "Waiting for Test Results" are due to recurring bottlenecks). Focus on conformance to expected flows and identification of inefficiencies.

- **Process Variant Analysis**:
  - Discover and rank the most common patient paths (e.g., Registration → Triage → Bed Assigned → ... → Discharged).
  - Quantify variants: % of cases following the "happy path" vs. deviations (e.g., skipped Nurse Assessment, loops in tests).
  - Comparison: Highlight how today's variants align with historical norms (e.g., increased skips during shortages).
  - Visualization: Process maps with frequency/thickness indicating variant popularity.

- **Conformance Checking**:
  - Compare actual traces to the ideal process model (based on activities in [process_specifications.md](process_specifications.md)).
  - Identify deviations: e.g., out-of-order activities (Doctor Examination before Nurse Assessment) or unexpected loops (repeated Diagnostic Test Ordered).
  - Metric: Conformance score (% of events fitting the model), trended over time.
  - Root Cause: Correlate low conformance with anomalies (e.g., bed shortages leading to skips).

- **Bottleneck and Delay Analysis**:
  - Identify stages with longest waits (e.g., Waiting for Specialist Consultation during doctor shortages).
  - Time-based bottlenecks: e.g., delays in Test Results Available correlated with high volume.
  - Visualization: Dotted charts for event timelines, bottleneck heatmaps.

- **Rework and Loop Detection**:
  - Detect repeated activities (e.g., multiple Blood Test Performed due to errors).
  - Metric: % of cases with loops, average loop count per stage.
  - Trend: Improvements over time (e.g., reduced rework after simulated interventions).

- **Root Cause Analysis**:
  - Correlate delays with factors: Time of day, day of week, volume, occupancy, or anomalies.
  - Example: Drill down into cases exceeding thresholds to identify common patterns (e.g., high LWBS when Waiting for Bed >60 min).
  - Visualization: Scatter plots (wait time vs. volume) or decision trees for causes.

---

## 3. Dashboard Designs by User Group
Tailor dashboards to user needs, integrating historical data for context. All dashboards should support filters (e.g., date range, stage, outcome) and export options. Use color-coding aligned with thresholds (green: on-target, yellow: warning, red: critical).

### 3.1 Command Center Dashboard (Operational Focus)
- **Purpose**: Monitor today's performance against historical benchmarks for real-time adjustments (e.g., allocate extra staff during detected bottlenecks).
- **Key Views**:
  - **Today vs. Historical Comparison**: Side-by-side panels showing current wait times, volumes, and compliance vs. historical averages/percentiles (e.g., "Waiting for Doctor today: 45 min (above historical median of 25 min)").
  - **Trend Alerts**: Real-time alerts for deviations (e.g., if today's LWBS rate > historical +20%, flag with anomaly context like "Similar to March 2025 bed shortage").
  - **Live Metrics**: Patient volume, bed occupancy, and stage waits updated with FreezeTime snapshots.
  - **Historical Context**: Rolling 7-day/30-day trends for quick benchmarking.
- **Visualizations**: Interactive line charts, gauges for compliance, and heatmaps for bottlenecks.
- **Frequency**: Daily use; auto-refresh with new snapshots.

### 3.2 Management Dashboard (Strategic Focus)
- **Purpose**: Provide high-level insights for resource planning, policy changes, and performance reviews. Validate daily improvements against long-term goals (e.g., reducing overall throughput from 240 min historical average to under 180 min).
- **Key Views**:
  - **Performance Trends**: Monthly/quarterly charts for key metrics (e.g., threshold compliance, LWBS rate, average stage durations).
  - **Anomaly and Improvement Tracking**: Before/after views for injected anomalies (e.g., "Post-doctor shortage simulation: Wait times improved by 15%").
  - **Benchmarking**: Compare ED performance to internal targets (e.g., desired wait times from specifications) or external standards.
  - **Outcome and Efficiency Reports**: Total throughput, % cases exceeding critical thresholds, and ROI-like metrics (e.g., reduced LWBS saving potential bed turns).
- **Visualizations**: KPI cards, trend lines with forecasts, and sankey diagrams for patient flows.
- **Frequency**: Weekly/monthly reviews; exportable reports for board meetings.

### 3.3 ER Staff Dashboard (Motivational Focus)
- **Purpose**: Empower staff with visibility into their performance to motivate reductions in wait times and improvements in efficiency (e.g., "This week's Waiting for Nurse Assessment: 8 min, down from last week's 12 min").
- **Key Views**:
  - **Weekly Performance Snapshot**: Focus on recent data (this week/last week) with comparisons to historical baselines (e.g., "Your team's triage compliance: 92% this week vs. 85% monthly average").
  - **Personalized Metrics**: If possible, break down by shift or team (e.g., night shift wait times vs. day shift).
  - **Improvement Gamification**: Progress bars toward targets (e.g., "Goal: <10 min for Bed Assigned – 80% achieved this week"), with badges for milestones.
  - **Stage-Specific Feedback**: Distributions of wait times per stage, highlighting wins (e.g., "Test Results waits improved due to faster processing").
- **Visualizations**: Simple bar charts, progress trackers, and motivational infographics (e.g., "Team Win: LWBS down 5%!").
- **Frequency**: Daily/weekly check-ins; accessible via mobile for on-floor staff.

---

## 4. Monitoring Typical ER Problems
Integrate these into all dashboards for proactive issue detection, using historical data to set alerts.

- **Long Waits in Key Stages**: Flag if > historical median (e.g., Waiting for Bed during high occupancy).
- **High LWBS Rate**: Alert on spikes, correlated with early-stage waits.
- **Bed/Doctor Shortages**: Occupancy >90% or delays in Doctor Examination.
- **Test and Treatment Delays**: Time from Test Results Available to Treatment Administered exceeding thresholds.
- **Discharge/Admission Bottlenecks**: Delays post-Disposition Decision.
- **Unusual Flows**: High % of variants with skips or loops.

---

## 5. Implementation Guidelines
- **Data Sources**: Use enriched historical event logs (with stage durations calculated as in [process_current_day.md](process_current_day.md)).
- **Tools**: Process mining software for variants/conformance; BI tools (e.g., Tableau, Power BI) for dashboards.
- **Validation**: Ensure analyses handle edge cases (e.g., skipped stages, ongoing cases at FreezeTime).
- **Expansion**: Add new metrics as needed (e.g., patient demographics if enriched). Track intervention impacts with A/B comparisons.
- **Security/Access**: Role-based views (e.g., staff dashboard hides sensitive management data).

---

### Historical Data Generation Methodology

The historical event log was synthetically generated to closely mimic real-world Emergency Department (ED) operations and to provide a robust baseline for process mining and dashboarding. Key aspects of the data generation process include:

- **Daily Patient Volume Variability**: Each day's patient count is based on a baseline (100 patients per day), but is modified by:
  - **Random daily noise**: ±8% random variation is applied to each day's volume to avoid artificial regularity.
  - **Seasonal effects**: January and February are modeled as busier months (+10% volume), while March and April are slightly quieter (-5%). May is modeled as typical, except for the partial day on May 4th (ending at 2:00 PM, i.e., 58% of a full day).
- **Admission Rate**: For all days, 17% of cases are admitted to the hospital, matching typical real-world ER statistics. The remainder are discharged, with a small percentage (~2%) modeled as "Left Without Being Seen" (LWBS).
- **Reproducibility**: A fixed random seed is used so that the same historical dataset can be regenerated for consistent benchmarking and analysis.
- **Process Paths**: Each case follows a realistic sequence of ED activities, with admitted and discharged cases following appropriate process variants.

This approach ensures that the historical data provides a realistic, variable, and reproducible context for validating daily performance and supporting advanced process mining analyses.

---

## 6. Dashboard Designs for Management and ER Staff

This section outlines the recommended dashboards for the two primary user groups beyond the command center: Management and Emergency Department (ER) Staff. Each dashboard is tailored to the needs and decision-making context of its audience.

### 6.1 Management Dashboard(s)
**Audience:** Hospital executives, department heads, quality improvement, resource planners

**Purpose:**
- Strategic oversight
- Resource planning
- Performance benchmarking
- Policy and process improvement

**Key Components/Views:**
- **Performance Trends:**
  - Monthly/quarterly trends for key metrics (wait times by stage, throughput, LWBS rate, admission rate)
  - Trend lines with historical context and targets
- **Threshold Compliance:**
  - % of cases within, exceeding warning, and exceeding critical thresholds for each stage
  - Stacked bar charts or heatmaps over time
- **Outcome and Efficiency Reports:**
  - Outcome distribution (% Discharged, % Admitted, % LWBS)
  - % of cases exceeding critical thresholds (e.g., >300 min total duration)
  - Box plots for case durations, pie charts for outcome breakdown
- **Anomaly and Improvement Tracking:**
  - Before/after views for known anomalies (e.g., “doctor shortage week”)
  - Annotations on trend charts for interventions or anomalies
  - Improvement deltas (e.g., “Wait times improved by 15% after intervention”)
- **Benchmarking:**
  - Compare ED performance to internal targets and external standards
  - KPI cards with color-coded status
- **Resource Utilization:**
  - Bed occupancy rates (peak, average)
  - Doctor/nurse utilization (if available)
  - Area charts for occupancy
- **Export/Reporting:**
  - Exportable reports (PDF, Excel) for board meetings
  - Scheduled email summaries

### 6.2 ER Staff Dashboard(s)
**Audience:** On-floor staff, shift leads, team managers

**Purpose:**
- Motivation and feedback
- Operational awareness
- Team/shift performance comparison

**Key Components/Views:**
- **Live Stage Calculator (Wall Display):**
  - Always-on, real-time display of current stage wait times
  - Color-coded by threshold (green/yellow/red)
  - Current patient count, bed occupancy, LWBS alerts
- **Weekly Performance Snapshot:**
  - This week vs. last week for key metrics (wait times by stage, compliance rates, LWBS rate)
  - Progress bars toward targets, badges for milestones
- **Shift/Team Breakdown:**
  - Wait times and compliance by shift (day/night) or team
  - Bar charts for comparison
- **Stage-Specific Feedback:**
  - Distributions of wait times per stage
  - Highlighted “wins” (e.g., “Test Results waits improved”)
  - Histograms or box plots for variability
- **Outcome Overview:**
  - % Discharged, % Admitted, % LWBS for the week
  - Pie chart or simple summary
- **Improvement Gamification:**
  - Progress toward goals (e.g., “Reduce triage wait <15 min”)
  - Motivational infographics and team rankings
- **Drilldown/Details:**
  - Ability to filter by date, shift, team, or stage
  - View individual case timelines (for learning)

**General Features for Both:**
- Filters: Date range, outcome, stage, shift/team
- Export: Data and charts for further analysis
- Annotations: For known events/interventions
- Mobile-friendly: Especially for staff dashboards

---

## 7. Emergency Department Human Resources (Staffing)

To create realistic historical data and process mining analyses, the following human resources are modeled for an Emergency Department with 30 beds and typical patient volumes:

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

---

## 7. Stage Duration Thresholds Table

The following table summarizes the duration calculations for each key stage in the Emergency Department process, including the activities used to calculate the duration and the thresholds for fast, warning, and critical performance. These thresholds are used for dashboard compliance and performance analysis.

| Stage                              | From Activity                | To Activity                        | Fast (min) | Warning (min) | Critical (min) |
|-------------------------------------|------------------------------|-------------------------------------|------------|---------------|----------------|
| Waiting for Triage                 | Registration                 | Triage                              | 5          | 15            | 45             |
| Waiting for Bed                    | Triage                       | Bed Assigned                        | 7          | 20            | 60             |
| Waiting for Nurse Assessment       | Bed Assigned                 | Nurse Assessment                    | 3          | 10            | 30             |
| Waiting for Doctor                 | Nurse Assessment             | Doctor Examination                  | 10         | 30            | 90             |
| Waiting for Test Results           | Diagnostic Test Ordered      | Test Results Available              | 20         | 60            | 180            |
| Waiting for Treatment              | Test Results Available*      | Treatment Administered              | 5          | 15            | 45             |
| Waiting for Observation Completion | Observation                  | Next Activity (e.g., Disposition Decision Recorded) | 10 (suggested) | Varies         | Varies         |
| Waiting for Specialist Consultation| Doctor Examination           | Specialist Consultation             | 20         | 60            | 180            |
| Waiting for Disposition Decision   | Last clinical activity†      | Disposition Decision Recorded       | 5          | 15            | 45             |
| Admitted to Hospital (case duration) | Registration               | Admitted to Hospital                | 60         | 180           | 300            |
| Discharged (case duration)         | Registration                 | Discharged                          | 60         | 180           | 300            |

*For Waiting for Treatment: If no diagnostic test is ordered, use Doctor Examination as the "From" activity.

†For Waiting for Disposition Decision: Use the last relevant clinical activity (e.g., Treatment Administered, Observation, or Specialist Consultation) as the "From" activity.

For “Observation Completion,” the fast threshold is suggested as 10 min, but this can be adjusted based on your clinical context.
