import os
import json
from collections import defaultdict
from datetime import datetime
import numpy as np

# --- Stage Definitions and Thresholds ---
stages = [
    {
        "name": "Waiting for Triage",
        "from": "Registration",
        "to": "Triage",
        "fast": 5,
        "warning": 15,
        "critical": 45
    },
    {
        "name": "Waiting for Bed",
        "from": "Triage",
        "to": "Bed Assigned",
        "fast": 7,
        "warning": 20,
        "critical": 60
    },
    {
        "name": "Waiting for Nurse Assessment",
        "from": "Bed Assigned",
        "to": "Nurse Assessment",
        "fast": 3,
        "warning": 10,
        "critical": 30
    },
    {
        "name": "Waiting for Doctor",
        "from": "Nurse Assessment",
        "to": "Doctor Examination",
        "fast": 10,
        "warning": 30,
        "critical": 90
    },
    {
        "name": "Waiting for Test Results",
        "from": "Diagnostic Test Ordered",
        "to": "Test Results Available",
        "fast": 20,
        "warning": 60,
        "critical": 180
    },
    {
        "name": "Waiting for Treatment",
        "from": "Test Results Available",
        "to": "Treatment Administered",
        "fast": 5,
        "warning": 15,
        "critical": 45
    },
    {
        "name": "Waiting for Specialist Consultation",
        "from": "Doctor Examination",
        "to": "Specialist Consultation",
        "fast": 20,
        "warning": 60,
        "critical": 180
    },
    {
        "name": "Waiting for Disposition Decision",
        "from": "Treatment Administered",
        "to": "Disposition Decision Recorded",
        "fast": 5,
        "warning": 15,
        "critical": 45
    },
    {
        "name": "Total Case Duration",
        "from": "Registration",
        "to": ["Discharged", "Admitted to Hospital"],
        "fast": 60,
        "warning": 180,
        "critical": 300
    }
]

# --- Load Data ---
script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, 'Output')
json_path = os.path.join(output_dir, 'alderaan_year_to_date.json')
with open(json_path, 'r') as f:
    data = json.load(f)
cases = data['cases']

def get_activity_time(case, activity_name):
    for act in case['activities']:
        if act['ActivityName'] == activity_name:
            return datetime.strptime(act['ActivityTime'], "%Y-%m-%d %H:%M:%S")
    return None

def get_first_activity_time(case, activity_name):
    # For cases with multiple activities of the same name
    for act in case['activities']:
        if act['ActivityName'] == activity_name:
            return datetime.strptime(act['ActivityTime'], "%Y-%m-%d %H:%M:%S")
    return None

def get_last_activity_time(case, activity_names):
    # For total case duration, find the last occurrence of any of the outcome activities
    for act in reversed(case['activities']):
        if act['ActivityName'] in activity_names:
            return datetime.strptime(act['ActivityTime'], "%Y-%m-%d %H:%M:%S")
    return None

def print_stage_stats(stage, durations):
    if not durations:
        print(f"\n{stage['name']}: No data.")
        return
    arr = np.array(durations)
    mean = np.mean(arr)
    median = np.median(arr)
    p90 = np.percentile(arr, 90)
    std = np.std(arr)
    fast = stage['fast']
    warning = stage['warning']
    critical = stage['critical']
    n = len(arr)
    n_fast = np.sum(arr <= fast)
    n_on_target = np.sum((arr > fast) & (arr <= warning))
    n_warning = np.sum((arr > warning) & (arr <= critical))
    n_critical = np.sum(arr > critical)
    print(f"\n=== {stage['name']} ===")
    print(f"SLA thresholds: Fast ≤ {fast} min, Warning ≤ {warning} min, Critical > {critical} min")
    print(f"Cases: {n}")
    print(f"  Mean: {mean:.1f} min | Median: {median:.1f} min | 90th percentile: {p90:.1f} min | Std: {std:.1f} min")
    print(f"  Fast: {n_fast} ({n_fast/n*100:.1f}%) | On Target: {n_on_target} ({n_on_target/n*100:.1f}%) | Warning: {n_warning} ({n_warning/n*100:.1f}%) | Critical: {n_critical} ({n_critical/n*100:.1f}%)")

def extract_stage_durations(stage, cases):
    durations = []
    for case in cases:
        if stage['name'] == "Total Case Duration":
            t_start = get_first_activity_time(case, stage['from'])
            t_end = get_last_activity_time(case, stage['to'])
        else:
            t_start = get_first_activity_time(case, stage['from'])
            t_end = get_first_activity_time(case, stage['to'])
        if t_start and t_end and t_end > t_start:
            duration = (t_end - t_start).total_seconds() / 60.0
            durations.append(duration)
    return durations

print("\n=================\nStage Duration SLA Statistics\n=================")
for stage in stages:
    durations = extract_stage_durations(stage, cases)
    print_stage_stats(stage, durations) 