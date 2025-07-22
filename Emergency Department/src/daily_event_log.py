import random
random.seed(42)
import json
from datetime import datetime, timedelta
import os
import csv
from collections import Counter

def load_activities(src_dir):
    with open(os.path.join(src_dir, 'activities.json'), 'r') as f:
        return json.load(f)

def random_patient_id(used_patient_ids):
    while True:
        pid = f"P{random.randint(1000, 9999)}"
        if pid not in used_patient_ids:
            used_patient_ids.add(pid)
            return pid

def random_case_id(used_case_ids):
    while True:
        cid = f"ED{random.randint(100000, 999999)}"
        if cid not in used_case_ids:
            used_case_ids.add(cid)
            return cid

def generate_case_activities(start_time, complete=True, stage=None, stage_time=None, freeze_time=None):
    activities_list = []
    path = [
        "Registration", "Triage", "Bed Assigned", "Nurse Assessment", "Doctor Examination"
    ]
    if random.random() < 0.7:
        path.append("Diagnostic Test Ordered")
        if random.random() < 0.8:
            path.append("Blood Test Performed")
        if random.random() < 0.5:
            path.append("Imaging Performed")
        path.append("Test Results Available")
    if random.random() < 0.8:
        path.append("Treatment Administered")
    if random.random() < 0.3:
        path.append("Observation")
    if random.random() < 0.1:
        path.append("Specialist Consultation")
    path.append("Disposition Decision Recorded")
    if complete:
        path.append(random.choice(["Discharged", "Admitted to Hospital"]))
    stage_to_activity = {
        'Waiting for Registration': 'Registration',
        'Waiting for Triage': 'Triage',
        'Waiting for Bed': 'Bed Assigned',
        'Waiting for Nurse Assessment': 'Nurse Assessment',
        'Waiting for Doctor': 'Doctor Examination',
        'Waiting for Diagnostic Test': 'Diagnostic Test Ordered',
        'Waiting for Test Results': 'Test Results Available',
        'Waiting for Treatment': 'Treatment Administered',
        'Waiting for Observation Completion': 'Observation',
        'Waiting for Specialist Consultation': 'Specialist Consultation',
        'Waiting for Discharge': 'Disposition Decision Recorded',
        'Waiting for Admission to Hospital': 'Admitted to Hospital',
        'Waiting for Transfer to Another Facility': 'Transferred to Another Facility'
    }
    if stage and stage in stage_to_activity:
        stop_activity = stage_to_activity[stage]
        if stop_activity in path:
            stop_index = path.index(stop_activity)
            path = path[:stop_index]
    # If in-progress (not complete), generate backwards from freeze_time - stage_time
    if not complete and stage and freeze_time is not None and stage_time is not None:
        n = len(path)
        # Generate random intervals for each activity
        intervals = [random.randint(5, 30) for _ in range(n)]
        total = sum(intervals)
        # The last activity time is freeze_time - stage_time
        last_time = freeze_time - timedelta(minutes=stage_time)
        # Calculate all activity times backwards
        times = [last_time - timedelta(minutes=sum(intervals[i+1:])) for i in range(n)]
        for activity, t in zip(path, times):
            activities_list.append({
                "ActivityName": activity,
                "ActivityTime": t.strftime("%Y-%m-%d %H:%M:%S")
            })
    else:
        # Completed cases: generate forward as before
        time = start_time
        for activity in path:
            time += timedelta(minutes=random.randint(5, 30))
            activities_list.append({
                "ActivityName": activity,
                "ActivityTime": time.strftime("%Y-%m-%d %H:%M:%S")
            })
    return activities_list

def generate_completed_cases(num_completed_patients, snapshot_time, used_patient_ids, used_case_ids):
    completed_cases = []
    for _ in range(num_completed_patients):
        case_id = random_case_id(used_case_ids)
        patient_id = random_patient_id(used_patient_ids)
        # Build the path with optional activities
        path = ["Registration", "Triage", "Bed Assigned", "Nurse Assessment", "Doctor Examination"]
        if random.random() < 0.7:
            path.append("Diagnostic Test Ordered")
            if random.random() < 0.8:
                path.append("Blood Test Performed")
            if random.random() < 0.5:
                path.append("Imaging Performed")
            path.append("Test Results Available")
        if random.random() < 0.8:
            path.append("Treatment Administered")
        if random.random() < 0.3:
            path.append("Observation")
        # Always end with Disposition Decision Recorded and a final outcome
        if path[-1] != "Observation":
            # If last activity is not Observation, just append
            path.append("Disposition Decision Recorded")
        else:
            # If last activity is Observation, ensure Disposition Decision Recorded comes after
            path.append("Disposition Decision Recorded")
        path.append(random.choice(["Discharged", "Admitted to Hospital"]))
        # Assign timestamps forward
        n = len(path)
        intervals = [random.randint(5, 30) for _ in range(n-1)]
        total = sum(intervals)
        last_time = snapshot_time - timedelta(hours=random.randint(2, 10))
        times = [last_time - timedelta(minutes=total)]
        for interval in intervals:
            times.append(times[-1] + timedelta(minutes=interval))
        activities_list = [
            {"ActivityName": activity, "ActivityTime": t.strftime("%Y-%m-%d %H:%M:%S")} 
            for activity, t in zip(path, times)
        ]
        completed_cases.append({
            "CaseId": case_id,
            "PatientID": patient_id,
            "activities": activities_list
        })
    return completed_cases

def generate_discharged_cases(snapshot_time, used_patient_ids, used_case_ids, n=62):
    cases = []
    for _ in range(n):
        case_id = random_case_id(used_case_ids)
        patient_id = random_patient_id(used_patient_ids)
        # Optionally add observation, but always end with Discharged
        path = [
            "Registration", "Triage", "Bed Assigned", "Nurse Assessment", "Doctor Examination",
            "Diagnostic Test Ordered", "Blood Test Performed", "Test Results Available",
            "Treatment Administered"
        ]
        if random.random() < 0.3:
            path.append("Observation")
        path.append("Disposition Decision Recorded")
        path.append("Discharged")
        n_acts = len(path)
        intervals = [random.randint(5, 30) for _ in range(n_acts-1)]
        total = sum(intervals)
        last_time = snapshot_time - timedelta(hours=random.randint(2, 10))
        times = [last_time - timedelta(minutes=total)]
        for interval in intervals:
            times.append(times[-1] + timedelta(minutes=interval))
        activities_list = [
            {"ActivityName": activity, "ActivityTime": t.strftime("%Y-%m-%d %H:%M:%S")}
            for activity, t in zip(path, times)
        ]
        cases.append({
            "CaseId": case_id,
            "PatientID": patient_id,
            "activities": activities_list
        })
    return cases

def generate_admitted_cases(snapshot_time, used_patient_ids, used_case_ids, n=64):
    cases = []
    for _ in range(n):
        case_id = random_case_id(used_case_ids)
        patient_id = random_patient_id(used_patient_ids)
        path = [
            "Registration", "Triage", "Bed Assigned", "Nurse Assessment", "Doctor Examination",
            "Diagnostic Test Ordered", "Imaging Performed", "Test Results Available",
            "Treatment Administered"
        ]
        if random.random() < 0.3:
            path.append("Observation")
        path.append("Disposition Decision Recorded")
        path.append("Admitted to Hospital")
        n_acts = len(path)
        intervals = [random.randint(5, 30) for _ in range(n_acts-1)]
        total = sum(intervals)
        last_time = snapshot_time - timedelta(hours=random.randint(2, 10))
        times = [last_time - timedelta(minutes=total)]
        for interval in intervals:
            times.append(times[-1] + timedelta(minutes=interval))
        activities_list = [
            {"ActivityName": activity, "ActivityTime": t.strftime("%Y-%m-%d %H:%M:%S")}
            for activity, t in zip(path, times)
        ]
        cases.append({
            "CaseId": case_id,
            "PatientID": patient_id,
            "activities": activities_list
        })
    return cases

def generate_triage_cases(snapshot_time, stage_thresholds, used_patient_ids, used_case_ids, n_ok=6, n_warning=0, n_critical=0):
    cases = []
    triage_warning = stage_thresholds['Waiting for Triage'][0]
    triage_critical = stage_thresholds['Waiting for Triage'][1]
    
    # OK cases
    for _ in range(n_ok):
        case_id = random_case_id(used_case_ids)
        patient_id = random_patient_id(used_patient_ids)
        wait_time = random.randint(1, triage_warning)
        path = ["Registration"]
        last_time = snapshot_time - timedelta(minutes=wait_time)
        activities_list = assign_timestamps_forward(path, last_time)
        cases.append({
            "CaseId": case_id,
            "PatientID": patient_id,
            "activities": activities_list,
            "current_stage": 'Waiting for Triage',
            "waiting_time": wait_time
        })
    
    # Warning cases
    for _ in range(n_warning):
        case_id = random_case_id(used_case_ids)
        patient_id = random_patient_id(used_patient_ids)
        wait_time = random.randint(triage_warning+1, triage_critical-1)
        path = ["Registration"]
        last_time = snapshot_time - timedelta(minutes=wait_time)
        activities_list = assign_timestamps_forward(path, last_time)
        cases.append({
            "CaseId": case_id,
            "PatientID": patient_id,
            "activities": activities_list,
            "current_stage": 'Waiting for Triage',
            "waiting_time": wait_time
        })
    
    # Critical cases
    for _ in range(n_critical):
        case_id = random_case_id(used_case_ids)
        patient_id = random_patient_id(used_patient_ids)
        wait_time = random.randint(triage_critical+1, triage_critical+30)
        path = ["Registration"]
        last_time = snapshot_time - timedelta(minutes=wait_time)
        activities_list = assign_timestamps_forward(path, last_time)
        cases.append({
            "CaseId": case_id,
            "PatientID": patient_id,
            "activities": activities_list,
            "current_stage": 'Waiting for Triage',
            "waiting_time": wait_time
        })
    
    return cases

def generate_bed_assignment_cases(snapshot_time, stage_thresholds, used_patient_ids, used_case_ids, n_ok=4, n_warning=0, n_critical=0):
    cases = []
    bed_warning = stage_thresholds['Waiting for Bed'][0]
    for _ in range(n_ok):
        case_id = random_case_id(used_case_ids)
        patient_id = random_patient_id(used_patient_ids)
        wait_time = random.randint(1, bed_warning)
        path = ["Registration", "Triage"]
        last_time = snapshot_time - timedelta(minutes=wait_time)
        activities_list = assign_timestamps_forward(path, last_time)
        cases.append({
            "CaseId": case_id,
            "PatientID": patient_id,
            "activities": activities_list,
            "current_stage": 'Waiting for Bed',
            "waiting_time": wait_time
        })
    return cases

def generate_nurse_assessment_cases(snapshot_time, stage_thresholds, used_patient_ids, used_case_ids, n_ok=5, n_warning=1):
    cases = []
    nurse_warning = stage_thresholds['Waiting for Nurse Assessment'][0]
    for _ in range(n_ok):
        case_id = random_case_id(used_case_ids)
        patient_id = random_patient_id(used_patient_ids)
        wait_time = random.randint(1, nurse_warning)
        path = ["Registration", "Triage", "Bed Assigned"]
        last_time = snapshot_time - timedelta(minutes=wait_time)
        activities_list = assign_timestamps_forward(path, last_time)
        cases.append({
            "CaseId": case_id,
            "PatientID": patient_id,
            "activities": activities_list,
            "current_stage": 'Waiting for Nurse Assessment',
            "waiting_time": wait_time
        })
    for _ in range(n_warning):
        case_id = random_case_id(used_case_ids)
        patient_id = random_patient_id(used_patient_ids)
        wait_time = random.randint(nurse_warning+1, nurse_warning+20)
        path = ["Registration", "Triage", "Bed Assigned"]
        last_time = snapshot_time - timedelta(minutes=wait_time)
        activities_list = assign_timestamps_forward(path, last_time)
        cases.append({
            "CaseId": case_id,
            "PatientID": patient_id,
            "activities": activities_list,
            "current_stage": 'Waiting for Nurse Assessment',
            "waiting_time": wait_time
        })
    return cases

def generate_doctor_examination_cases(snapshot_time, stage_thresholds, used_patient_ids, used_case_ids, n_ok=5):
    cases = []
    doctor_warning = stage_thresholds['Waiting for Doctor'][0]
    for _ in range(n_ok):
        case_id = random_case_id(used_case_ids)
        patient_id = random_patient_id(used_patient_ids)
        wait_time = random.randint(1, doctor_warning)
        path = ["Registration", "Triage", "Bed Assigned", "Nurse Assessment"]
        last_time = snapshot_time - timedelta(minutes=wait_time)
        activities_list = assign_timestamps_forward(path, last_time)
        cases.append({
            "CaseId": case_id,
            "PatientID": patient_id,
            "activities": activities_list,
            "current_stage": 'Waiting for Doctor',
            "waiting_time": wait_time
        })
    return cases

def generate_test_results_cases(snapshot_time, stage_thresholds, used_patient_ids, used_case_ids, n_ok=3, n_warning=1, n_critical=0):
    cases = []
    test_results_warning = stage_thresholds['Waiting for Test Results'][0]
    for _ in range(n_ok):
        case_id = random_case_id(used_case_ids)
        patient_id = random_patient_id(used_patient_ids)
        wait_time = random.randint(1, test_results_warning)
        path = ["Registration", "Triage", "Bed Assigned", "Nurse Assessment", "Doctor Examination", "Diagnostic Test Ordered", "Blood Test Performed"]
        last_time = snapshot_time - timedelta(minutes=wait_time)
        activities_list = assign_timestamps_forward(path, last_time)
        cases.append({
            "CaseId": case_id,
            "PatientID": patient_id,
            "activities": activities_list,
            "current_stage": 'Waiting for Test Results',
            "waiting_time": wait_time
        })
    for _ in range(n_warning):
        case_id = random_case_id(used_case_ids)
        patient_id = random_patient_id(used_patient_ids)
        wait_time = random.randint(test_results_warning+1, test_results_warning+60)
        path = ["Registration", "Triage", "Bed Assigned", "Nurse Assessment", "Doctor Examination", "Diagnostic Test Ordered", "Imaging Performed"]
        last_time = snapshot_time - timedelta(minutes=wait_time)
        activities_list = assign_timestamps_forward(path, last_time)
        cases.append({
            "CaseId": case_id,
            "PatientID": patient_id,
            "activities": activities_list,
            "current_stage": 'Waiting for Test Results',
            "waiting_time": wait_time
        })
    return cases

# --- ENFORCE STRICT CONTROL OVER OBSERVATION COMPLETION CASES ---
# Only generate_observation_cases can end with 'Observation'.
# Remove 'Observation' as a possible last activity from all other per-stage generators.

def generate_treatment_cases(snapshot_time, stage_thresholds, used_patient_ids, used_case_ids, n_ok=3, n_warning=1):
    cases = []
    treatment_warning = stage_thresholds['Waiting for Treatment'][0]
    n_ok_doctor = n_ok // 2
    n_ok_test = n_ok - n_ok_doctor
    n_warning_doctor = n_warning // 2
    n_warning_test = n_warning - n_warning_doctor
    def assign_timestamps_forward(path, last_time):
        n = len(path)
        intervals = [random.randint(5, 30) for _ in range(n-1)]
        total = sum(intervals)
        times = [last_time - timedelta(minutes=total)]
        for interval in intervals:
            times.append(times[-1] + timedelta(minutes=interval))
        return [
            {"ActivityName": activity, "ActivityTime": t.strftime("%Y-%m-%d %H:%M:%S")} 
            for activity, t in zip(path, times)
        ]
    # OK cases: after Doctor Examination (no test ordered)
    for _ in range(n_ok_doctor):
        case_id = random_case_id(used_case_ids)
        patient_id = random_patient_id(used_patient_ids)
        wait_time = random.randint(1, treatment_warning)
        path = ["Registration", "Triage", "Bed Assigned", "Nurse Assessment", "Doctor Examination"]
        last_time = snapshot_time - timedelta(minutes=wait_time)
        activities_list = assign_timestamps_forward(path, last_time)
        cases.append({
            "CaseId": case_id,
            "PatientID": patient_id,
            "activities": activities_list,
            "current_stage": 'Waiting for Treatment',
            "waiting_time": wait_time
        })
    # OK cases: after Test Results Available (test path)
    for _ in range(n_ok_test):
        case_id = random_case_id(used_case_ids)
        patient_id = random_patient_id(used_patient_ids)
        wait_time = random.randint(1, treatment_warning)
        path = ["Registration", "Triage", "Bed Assigned", "Nurse Assessment", "Doctor Examination", "Diagnostic Test Ordered", "Blood Test Performed", "Test Results Available"]
        last_time = snapshot_time - timedelta(minutes=wait_time)
        activities_list = assign_timestamps_forward(path, last_time)
        cases.append({
            "CaseId": case_id,
            "PatientID": patient_id,
            "activities": activities_list,
            "current_stage": 'Waiting for Treatment',
            "waiting_time": wait_time
        })
    # Warning cases: after Doctor Examination (no test ordered)
    for _ in range(n_warning_doctor):
        case_id = random_case_id(used_case_ids)
        patient_id = random_patient_id(used_patient_ids)
        wait_time = random.randint(treatment_warning+1, treatment_warning+30)
        path = ["Registration", "Triage", "Bed Assigned", "Nurse Assessment", "Doctor Examination"]
        last_time = snapshot_time - timedelta(minutes=wait_time)
        activities_list = assign_timestamps_forward(path, last_time)
        cases.append({
            "CaseId": case_id,
            "PatientID": patient_id,
            "activities": activities_list,
            "current_stage": 'Waiting for Treatment',
            "waiting_time": wait_time
        })
    # Warning cases: after Test Results Available (test path)
    for _ in range(n_warning_test):
        case_id = random_case_id(used_case_ids)
        patient_id = random_patient_id(used_patient_ids)
        wait_time = random.randint(treatment_warning+1, treatment_warning+30)
        path = ["Registration", "Triage", "Bed Assigned", "Nurse Assessment", "Doctor Examination", "Diagnostic Test Ordered", "Blood Test Performed", "Test Results Available"]
        last_time = snapshot_time - timedelta(minutes=wait_time)
        activities_list = assign_timestamps_forward(path, last_time)
        cases.append({
            "CaseId": case_id,
            "PatientID": patient_id,
            "activities": activities_list,
            "current_stage": 'Waiting for Treatment',
            "waiting_time": wait_time
        })
    return cases

# In all other per-stage generators, ensure the path does not end with 'Observation'.
# (No changes needed for generate_observation_cases, which is the only function allowed to end with 'Observation'.)

def generate_observation_cases(snapshot_time, stage_thresholds, used_patient_ids, used_case_ids, n_ok=9, n_warning=4, n_critical=0):
    cases = []
    obs_warning = stage_thresholds['Waiting for Observation Completion'][0] or 60
    obs_critical = stage_thresholds['Waiting for Observation Completion'][1] or 180
    # OK cases
    for _ in range(n_ok):
        case_id = random_case_id(used_case_ids)
        patient_id = random_patient_id(used_patient_ids)
        wait_time = random.randint(1, obs_warning)
        path = ["Registration", "Triage", "Bed Assigned", "Nurse Assessment", "Doctor Examination", "Treatment Administered", "Observation"]
        last_time = snapshot_time - timedelta(minutes=wait_time)
        activities_list = assign_timestamps_forward(path, last_time)
        cases.append({
            "CaseId": case_id,
            "PatientID": patient_id,
            "activities": activities_list,
            "current_stage": 'Waiting for Observation Completion',
            "waiting_time": wait_time
        })
    # Warning cases
    for _ in range(n_warning):
        case_id = random_case_id(used_case_ids)
        patient_id = random_patient_id(used_patient_ids)
        wait_time = random.randint(obs_warning+1, obs_critical-1)
        path = ["Registration", "Triage", "Bed Assigned", "Nurse Assessment", "Doctor Examination", "Treatment Administered", "Observation"]
        last_time = snapshot_time - timedelta(minutes=wait_time)
        activities_list = assign_timestamps_forward(path, last_time)
        cases.append({
            "CaseId": case_id,
            "PatientID": patient_id,
            "activities": activities_list,
            "current_stage": 'Waiting for Observation Completion',
            "waiting_time": wait_time
        })
    # No critical cases
    return cases

def generate_disposition_decision_cases(snapshot_time, stage_thresholds, used_patient_ids, used_case_ids, n_ok=6, n_warning=2, n_critical=0):
    cases = []
    disp_warning = stage_thresholds['Waiting for Discharge'][0]
    disp_critical = stage_thresholds['Waiting for Discharge'][1]
    for _ in range(n_ok):
        case_id = random_case_id(used_case_ids)
        patient_id = random_patient_id(used_case_ids)
        wait_time = random.randint(1, disp_warning)
        path = [
            "Registration", "Triage", "Bed Assigned", "Nurse Assessment", "Doctor Examination",
            "Treatment Administered", "Observation", "Disposition Decision Recorded"
        ]
        # Truncate path so last activity is always 'Disposition Decision Recorded'
        last_time = snapshot_time - timedelta(minutes=wait_time)
        activities_list = assign_timestamps_forward(path, last_time)
        cases.append({
            "CaseId": case_id,
            "PatientID": patient_id,
            "activities": activities_list,
            "current_stage": 'Waiting for Discharge',
            "waiting_time": wait_time
        })
    for _ in range(n_warning):
        case_id = random_case_id(used_case_ids)
        patient_id = random_patient_id(used_case_ids)
        wait_time = random.randint(disp_warning+1, disp_critical-1)
        path = [
            "Registration", "Triage", "Bed Assigned", "Nurse Assessment", "Doctor Examination",
            "Treatment Administered", "Observation", "Disposition Decision Recorded"
        ]
        last_time = snapshot_time - timedelta(minutes=wait_time)
        activities_list = assign_timestamps_forward(path, last_time)
        cases.append({
            "CaseId": case_id,
            "PatientID": patient_id,
            "activities": activities_list,
            "current_stage": 'Waiting for Discharge',
            "waiting_time": wait_time
        })
    for _ in range(n_critical):
        case_id = random_case_id(used_case_ids)
        patient_id = random_patient_id(used_case_ids)
        wait_time = random.randint(disp_critical+1, disp_critical+30)
        path = [
            "Registration", "Triage", "Bed Assigned", "Nurse Assessment", "Doctor Examination",
            "Treatment Administered", "Observation", "Disposition Decision Recorded"
        ]
        last_time = snapshot_time - timedelta(minutes=wait_time)
        activities_list = assign_timestamps_forward(path, last_time)
        cases.append({
            "CaseId": case_id,
            "PatientID": patient_id,
            "activities": activities_list,
            "current_stage": 'Waiting for Discharge',
            "waiting_time": wait_time
        })
    return cases

# Helper for forward timestamp assignment (shared)
def assign_timestamps_forward(path, last_time):
    n = len(path)
    intervals = [random.randint(5, 30) for _ in range(n-1)]
    total = sum(intervals)
    times = [last_time - timedelta(minutes=total)]
    for interval in intervals:
        times.append(times[-1] + timedelta(minutes=interval))
    return [
        {"ActivityName": activity, "ActivityTime": t.strftime("%Y-%m-%d %H:%M:%S")} 
        for activity, t in zip(path, times)
    ]

def save_event_log_json(all_cases, output_dir, snapshot_time):
    event_log = {
        "FreezeTime": snapshot_time.strftime("%Y-%m-%dT%H:%M:%S+00:00"),
        "cases": all_cases
    }
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, 'alderaan_daily.json'), 'w') as f:
        json.dump(event_log, f, indent=2)

def save_event_log_csv(all_cases, output_dir):
    all_events = []
    for case in all_cases:
        vitals = case.get('VitalSigns', {})
        for activity in case['activities']:
            all_events.append({
                "CaseId": case['CaseId'],
                "ActivityName": activity['ActivityName'],
                "ActivityTime": activity['ActivityTime'],
                "PatientID": case['PatientID'],
                "Resource": activity.get('Resource', ''),
                "Age": case.get('Age', ''),
                "Sex": case.get('Sex', ''),
                "ModeOfArrival": case.get('ModeOfArrival', ''),
                "VisitType": case.get('VisitType', ''),
                "HR": vitals.get('HR', ''),
                "BP": vitals.get('BP', ''),
                "Temp": vitals.get('Temp', ''),
                "O2Sat": vitals.get('O2Sat', ''),
                "Triage": case.get('Triage', ''),
                "ArrivalShift": case.get('ArrivalShift', '')
            })
    all_events.sort(key=lambda x: (x['ActivityTime'], x['CaseId']))
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, 'alderaan_daily.csv')
    fieldnames = [
        "CaseId", "ActivityName", "ActivityTime", "PatientID", "Resource",
        "Age", "Sex", "ModeOfArrival", "VisitType", "HR", "BP", "Temp", "O2Sat", "Triage", "ArrivalShift"
    ]
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for event in all_events:
            writer.writerow(event)
    print(f"Generated {len(all_events)} event log entries (JSON and CSV).\n")

def print_statistics(completed_cases, current_cases):
    print("=== Event Log Statistics Report ===\n")
    print("[1] Live Snapshot (In-Progress Cases as of 2025-05-05 14:00)")
    print(f"  Number of in-progress cases: {len(current_cases)}")
    print(f"  Number of activities (events): {sum(len(c['activities']) for c in current_cases)}")
    print(f"  Number of unique patients: {len(set(c['PatientID'] for c in current_cases))}")
    print()
    activity_counter = Counter([a['ActivityName'] for c in current_cases for a in c['activities']])
    print("  Activity count (in-progress):")
    for activity, count in activity_counter.most_common():
        print(f"    {activity}: {count}")
    print()
    last_activity_by_case = {c['CaseId']: c['activities'][-1]['ActivityName'] for c in current_cases if c['activities']}
    completed_journey = [aid for aid in last_activity_by_case.values() if aid in ['Discharged', 'Admitted to Hospital']]
    print(f"  Number of in-progress cases that have completed their journey (admitted or discharged): {len(completed_journey)}")
    print()
    print("[2] Historical (Closed Cases)")
    print(f"  Number of closed cases: {len(completed_cases)}")
    print(f"  Number of activities (events): {sum(len(c['activities']) for c in completed_cases)}")
    print(f"  Number of unique patients: {len(set(c['PatientID'] for c in completed_cases))}")
    print()
    activity_counter = Counter([a['ActivityName'] for c in completed_cases for a in c['activities']])
    print("  Activity count (closed):")
    for activity, count in activity_counter.most_common():
        print(f"    {activity}: {count}")
    print()

def generate_lwbs_cases(snapshot_time, used_patient_ids, used_case_ids, n=2):
    """Generate cases where the patient leaves without being seen (LWBS) at various stages."""
    cases = []
    lwbs_variants = [
        ["Registration"],
        ["Registration", "Triage"],
        ["Registration", "Triage", "Bed Assigned"],
        ["Registration", "Triage", "Bed Assigned", "Nurse Assessment"]
    ]
    for i in range(n):
        case_id = random_case_id(used_case_ids)
        patient_id = random_patient_id(used_patient_ids)
        # Cycle through variants
        path = lwbs_variants[i % len(lwbs_variants)].copy()
        # Add LWBS as the last activity (no abbreviation)
        path.append("Left Without Being Seen")
        # Assign timestamps
        time = snapshot_time - timedelta(hours=random.randint(1, 10))
        activities_list = []
        for activity in path:
            time += timedelta(minutes=random.randint(5, 30))
            activities_list.append({
                "ActivityName": activity,
                "ActivityTime": time.strftime("%Y-%m-%d %H:%M:%S")
            })
        cases.append({
            "CaseId": case_id,
            "PatientID": patient_id,
            "activities": activities_list,
            "current_stage": "Left Without Being Seen",
            "waiting_time": (datetime.strptime(activities_list[-1]["ActivityTime"], "%Y-%m-%d %H:%M:%S") - datetime.strptime(activities_list[0]["ActivityTime"], "%Y-%m-%d %H:%M:%S")).total_seconds() // 60
        })
    return cases

def random_age():
    # Skew toward adults, but include children and elderly
    r = random.random()
    if r < 0.15:
        return random.randint(0, 17)  # Pediatric
    elif r < 0.85:
        return random.randint(18, 75)  # Adult
    else:
        return random.randint(76, 100)  # Elderly

def random_sex():
    return random.choices(['Male', 'Female', 'Other'], weights=[0.49, 0.49, 0.02])[0]

def random_mode_of_arrival():
    return random.choices(['Ambulance', 'Walk-in', 'Referral'], weights=[0.25, 0.7, 0.05])[0]

def random_visit_type():
    return random.choices(['New', 'Follow-up', 'Transfer'], weights=[0.85, 0.1, 0.05])[0]

def random_vitals():
    return {
        'HR': random.randint(50, 120),
        'BP': f"{random.randint(90, 160)}/{random.randint(50, 100)}",
        'Temp': round(random.uniform(35.5, 39.5), 1),
        'O2Sat': random.randint(90, 100)
    }

def random_triage():
    # ESI/CTAS 1 (most urgent) to 5 (least urgent)
    return random.choices([1, 2, 3, 4, 5], weights=[0.05, 0.15, 0.5, 0.2, 0.1])[0]

def get_arrival_shift(activities):
    reg_time_str = None
    for act in activities:
        if act['ActivityName'] == 'Registration':
            reg_time_str = act['ActivityTime']
            break
    if not reg_time_str:
        return None
    reg_time = datetime.strptime(reg_time_str, '%Y-%m-%d %H:%M:%S')
    hour = reg_time.hour
    if 7 <= hour < 15:
        return 'Day'
    elif 15 <= hour < 23:
        return 'Evening'
    else:
        return 'Night'

def add_case_attributes(case):
    case['Age'] = random_age()
    case['Sex'] = random_sex()
    case['ModeOfArrival'] = random_mode_of_arrival()
    case['VisitType'] = random_visit_type()
    case['VitalSigns'] = random_vitals()
    case['Triage'] = random_triage()
    case['ArrivalShift'] = get_arrival_shift(case['activities'])
    return case

def main():
    SRC_DIR = os.path.dirname(os.path.abspath(__file__))
    OUTPUT_DIR = os.path.join(SRC_DIR, 'Output')
    activities = load_activities(SRC_DIR)
    activity_names = [a['name'] for a in activities]
    stage_thresholds = {
        'Waiting for Registration': (10, 30),
        'Waiting for Triage': (15, 45),
        'Waiting for Bed': (20, 60),
        'Waiting for Nurse Assessment': (10, 30),
        'Waiting for Doctor': (30, 90),
        'Waiting for Diagnostic Test': (20, 60),
        'Waiting for Test Results': (60, 180),
        'Waiting for Treatment': (15, 45),
        'Waiting for Observation Completion': (None, None),
        'Waiting for Specialist Consultation': (60, 180),
        'Waiting for Discharge': (15, 45),
        'Waiting for Admission to Hospital': (30, 90),
        'Waiting for Transfer to Another Facility': (60, 180)
    }
    snapshot_time = datetime(2025, 5, 4, 14, 0)
    used_patient_ids = set()
    used_case_ids = set()
    # Modular per-stage in-progress case generation ONLY
    current_cases = []
    triage_cases = generate_triage_cases(snapshot_time, stage_thresholds, used_patient_ids, used_case_ids, n_ok=6, n_warning=3, n_critical=2)
    current_cases.extend(triage_cases)
    bed_assignment_cases = generate_bed_assignment_cases(snapshot_time, stage_thresholds, used_patient_ids, used_case_ids, n_ok=4, n_warning=0, n_critical=0)
    current_cases.extend(bed_assignment_cases)
    nurse_assessment_cases = generate_nurse_assessment_cases(snapshot_time, stage_thresholds, used_patient_ids, used_case_ids, n_ok=5, n_warning=1)
    current_cases.extend(nurse_assessment_cases)
    doctor_examination_cases = generate_doctor_examination_cases(snapshot_time, stage_thresholds, used_patient_ids, used_case_ids, n_ok=5)
    current_cases.extend(doctor_examination_cases)
    test_results_cases = generate_test_results_cases(snapshot_time, stage_thresholds, used_patient_ids, used_case_ids, n_ok=3, n_warning=1, n_critical=0)
    current_cases.extend(test_results_cases)
    treatment_cases = generate_treatment_cases(snapshot_time, stage_thresholds, used_patient_ids, used_case_ids, n_ok=3, n_warning=1)
    current_cases.extend(treatment_cases)
    observation_cases = generate_observation_cases(snapshot_time, stage_thresholds, used_patient_ids, used_case_ids, n_ok=9, n_warning=4, n_critical=0)
    current_cases.extend(observation_cases)
    disposition_cases = generate_disposition_decision_cases(snapshot_time, stage_thresholds, used_patient_ids, used_case_ids, n_ok=6, n_warning=2, n_critical=0)
    current_cases.extend(disposition_cases)
    # LWBS cases: 2% of total cases (rounded)
    total_cases_so_far = len(current_cases)
    lwbs_n = max(1, round(0.02 * total_cases_so_far))
    lwbs_cases = generate_lwbs_cases(snapshot_time, used_patient_ids, used_case_ids, n=lwbs_n)
    current_cases.extend(lwbs_cases)
    # Completed cases: only explicit discharged/admitted
    # Set total number of completed cases and admission rate
    total_completed = 100  # Adjust as needed for realism
    admit_rate = 0.17
    n_admitted = int(round(total_completed * admit_rate))
    n_discharged = total_completed - n_admitted
    completed_cases = []
    completed_cases.extend(generate_discharged_cases(snapshot_time, used_patient_ids, used_case_ids, n=n_discharged))
    completed_cases.extend(generate_admitted_cases(snapshot_time, used_patient_ids, used_case_ids, n=n_admitted))
    all_cases = completed_cases + current_cases
    # Check for cases ending with 'Observation'
    obs_end_count = sum(1 for case in all_cases if case['activities'][-1]['ActivityName'] == 'Observation')
    print(f"CASES ENDING WITH 'Observation': {obs_end_count}")
    assert obs_end_count == 13, f"Expected 13 cases ending with 'Observation', found {obs_end_count}"  # 9 OK + 4 warning
    save_event_log_json(all_cases, OUTPUT_DIR, snapshot_time)
    save_event_log_csv(all_cases, OUTPUT_DIR)
    print_statistics(completed_cases, current_cases)

if __name__ == "__main__":
    main() 