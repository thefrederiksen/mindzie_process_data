import json
from collections import defaultdict, Counter
from datetime import datetime
import os

# Define thresholds for each stage (should match your generator)
stage_thresholds = {
    'Waiting for Triage': (15, 45),
    'Waiting for Bed': (20, 60),
    'Waiting for Nurse Assessment': (10, 30),
    'Waiting for Doctor': (30, 90),
    'Waiting for Diagnostic Test': (20, 60),
    'Waiting for Test Results': (60, 180),
    'Waiting for Treatment': (15, 45),
    'Waiting for Observation Completion': (60, 180),  # Use defaults if None
    'Waiting for Specialist Consultation': (60, 180),
    'Waiting for Discharge': (15, 45),
}

# List of all possible stages to check
all_stages = [
    'Waiting for Triage',
    'Waiting for Bed',
    'Waiting for Nurse Assessment',
    'Waiting for Doctor',
    'Waiting for Diagnostic Test',
    'Waiting for Test Results',
    'Waiting for Treatment',
    'Waiting for Observation Completion',
    'Waiting for Specialist Consultation',
    'Waiting for Discharge',
    'Discharged',
    'Admitted to Hospital',
]

# Helper to determine the current stage for a case
def determine_stage(activities):
    names = [a['ActivityName'] for a in activities]
    if 'Discharged' in names and names[-1] == 'Discharged':
        return 'Discharged'
    if 'Admitted to Hospital' in names and names[-1] == 'Admitted to Hospital':
        return 'Admitted to Hospital'
    if names[-1] == 'Observation':
        return 'Waiting for Observation Completion'
    if names[-1] == 'Test Results Available' and 'Treatment Administered' not in names:
        return 'Waiting for Treatment'
    if names[-1] == 'Doctor Examination' and 'Treatment Administered' not in names and 'Test Results Available' not in names:
        return 'Waiting for Treatment'
    if names[-1] == 'Blood Test Performed' or names[-1] == 'Imaging Performed':
        if 'Test Results Available' not in names:
            return 'Waiting for Test Results'
    if names[-1] == 'Nurse Assessment' and 'Doctor Examination' not in names:
        return 'Waiting for Doctor'
    if names[-1] == 'Bed Assigned' and 'Nurse Assessment' not in names:
        return 'Waiting for Nurse Assessment'
    if names[-1] == 'Triage' and 'Bed Assigned' not in names:
        return 'Waiting for Bed'
    if names[-1] == 'Registration' and 'Triage' not in names:
        return 'Waiting for Triage'
    if names[-1] == 'Disposition Decision Recorded':
        return 'Waiting for Discharge'
    return 'Other'

# Helper to determine status (OK, warning, critical) for a case in a stage
def get_status(stage, waiting_time):
    if stage not in stage_thresholds or waiting_time is None:
        return 'Unknown'
    warning, critical = stage_thresholds[stage]
    if warning is None or critical is None:
        warning, critical = 60, 180
    if waiting_time <= warning:
        return 'OK'
    elif waiting_time <= critical:
        return 'Warning'
    else:
        return 'Critical'

# Load event_log.json
dir_path = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(dir_path, 'Output')
with open(os.path.join(output_dir, 'alderaan_daily.json'), 'r') as f:
    data = json.load(f)

cases = data['cases'] if 'cases' in data else data

# Track cases per stage and check for overlaps
stage_case_ids = defaultdict(set)
stage_status_counts = defaultdict(lambda: Counter({'OK':0, 'Warning':0, 'Critical':0}))
overlap_cases = set()

for case in cases:
    cid = case['CaseId']
    stage = case.get('current_stage')
    if not stage:
        # Try to infer stage from activities
        stage = determine_stage(case['activities'])
    if stage == 'Waiting for Discharge':
        stage = 'Waiting for Discharge'
    waiting_time = case.get('waiting_time')
    status = get_status(stage, waiting_time)
    stage_case_ids[stage].add(cid)
    stage_status_counts[stage][status] += 1

# Check for overlaps (cases in more than one stage)
all_case_to_stages = defaultdict(list)
for stage, cids in stage_case_ids.items():
    for cid in cids:
        all_case_to_stages[cid].append(stage)
overlap_cases = {cid: stages for cid, stages in all_case_to_stages.items() if len(stages) > 1}

# Print summary table
print(f"{'Stage':<30} {'OK':>4} {'Warn':>5} {'Crit':>5} {'Total':>6}")
print('-'*54)
for stage in all_stages:
    counts = stage_status_counts[stage]
    total = sum(counts.values())
    print(f"{stage:<30} {counts['OK']:>4} {counts['Warning']:>5} {counts['Critical']:>5} {total:>6}")

# Print breakdown of last activity for all cases
last_activity_counter = Counter()
obs_end_cases = []
lwbs_cases = []
for case in cases:
    if case['activities']:
        last_act = case['activities'][-1]['ActivityName']
        last_activity_counter[last_act] += 1
        if last_act == 'Observation':
            obs_end_cases.append(case)
        if last_act == 'Left Without Being Seen':
            lwbs_cases.append(case)
print("\nBreakdown by Last Activity (all cases):")
print(f"{'Last Activity':<30} {'Count':>6}")
print('-'*38)
for activity, count in last_activity_counter.most_common():
    print(f"{activity:<30} {count:>6}")

# Print number and percentage of LWBS cases
num_lwbs = len(lwbs_cases)
percent_lwbs = 100.0 * num_lwbs / len(cases) if cases else 0
print(f"\nNumber of cases Left Without Being Seen: {num_lwbs} ({percent_lwbs:.2f}% of all cases)")

# Print debug info for cases ending with 'Observation' but not in Waiting for Observation Completion
not_in_obs_stage = [case for case in obs_end_cases if case.get('current_stage') != 'Waiting for Observation Completion']
if not_in_obs_stage:
    print("\nCases ending with 'Observation' but not in 'Waiting for Observation Completion':")
    for case in not_in_obs_stage:
        print(f"  CaseId: {case['CaseId']}, current_stage: {case.get('current_stage')}, activities: {[a['ActivityName'] for a in case['activities']]}")

# Print any overlaps
if overlap_cases:
    print("\nCases in more than one stage at once:")
    for cid, stages in overlap_cases.items():
        print(f"  CaseId {cid}: {stages}")
else:
    print("\nNo cases are in more than one stage at a time.")

# Print the rules used for stage assignment
print("\n--- Stage Assignment Rules Used ---")
print("""
A case is assigned to a stage as follows (first match wins):

if 'Discharged' in activities and last_activity == 'Discharged':
    'Discharged'
elif 'Admitted to Hospital' in activities and last_activity == 'Admitted to Hospital':
    'Admitted to Hospital'
elif last_activity == 'Observation':
    'Waiting for Observation Completion'
elif last_activity == 'Test Results Available' and 'Treatment Administered' not in activities:
    'Waiting for Treatment'
elif last_activity == 'Doctor Examination' and 'Treatment Administered' not in activities and 'Test Results Available' not in activities:
    'Waiting for Treatment'
elif last_activity in ['Blood Test Performed', 'Imaging Performed'] and 'Test Results Available' not in activities:
    'Waiting for Test Results'
elif last_activity == 'Nurse Assessment' and 'Doctor Examination' not in activities:
    'Waiting for Doctor'
elif last_activity == 'Bed Assigned' and 'Nurse Assessment' not in activities:
    'Waiting for Nurse Assessment'
elif last_activity == 'Triage' and 'Bed Assigned' not in activities:
    'Waiting for Bed'
elif last_activity == 'Registration' and 'Triage' not in activities:
    'Waiting for Triage'
elif last_activity == 'Disposition Decision Recorded':
    'Waiting for Discharge'
else:
    'Other'
""") 