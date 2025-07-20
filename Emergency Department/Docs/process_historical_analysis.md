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
