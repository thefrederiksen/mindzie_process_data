import os
import json
import random
from datetime import datetime, timedelta
import csv

# --- CONFIGURATION ---

RANDOM_SEED = 42  # For reproducibility
random.seed(RANDOM_SEED)

START_DATE = datetime(2025, 1, 1)
END_DATE = datetime(2025, 5, 3)
BED_CAPACITY = 40

# Typical case counts for each day of week (0=Monday, 6=Sunday)
CASE_COUNT_BY_WEEKDAY = {
    0: 60,  # Monday
    1: 65,
    2: 70,
    3: 75,
    4: 80,
    5: 90,  # Saturday (busiest)
    6: 85,  # Sunday
}

# Variant mix: proportion of each variant (must sum to 1.0)
VARIANT_MIX = {
    'simple_discharge': 0.6,
    'discharge_with_tests': 0.3,
    'admission_after_observation': 0.1,
}

# Problem injection plan (to be expanded)
PROBLEM_DAYS = {
    # '2025-02-14': {'bed_shortage': True, 'doctor_shortage': False},
}

# --- STEP 1: VARIANT TEMPLATES ---
# Resource pools for each role
DOCTORS = ["Peter", "Maria", "John", "Priya", "Ahmed", "Emily", "David", "Chen", "Anna", "Luis"]
NURSES = ["Sarah", "Tom", "Lisa", "Kevin", "Zoe", "Mark", "Julia", "Sam", "Chloe", "Ben", "Mia", "Alex", "Grace", "Leo", "Ella", "Jack", "Sophie", "Max"]
NP_PA = ["Olivia", "Ryan", "Hannah", "Josh"]
CLERKS = ["Emma", "Paul", "Rita"]
TECHS = ["Steve", "Maya", "Ivan", "Tara"]

# Map activity to resource type
ACTIVITY_RESOURCE_MAP = {
    "Registration": CLERKS,
    "Triage": NURSES,
    "Bed Assigned": NURSES,
    "Nurse Assessment": NURSES,
    "Doctor Examination": DOCTORS,
    "Diagnostic Test Ordered": DOCTORS,
    "Blood Test Performed": TECHS,
    "Imaging Performed": TECHS,
    "Test Results Available": TECHS,
    "Treatment Administered": NURSES,
    "Observation": NURSES,
    "Specialist Consultation": DOCTORS,
    "Disposition Decision Recorded": DOCTORS,
    "Discharged": NURSES,
    "Admitted to Hospital": NURSES,
    "Left Without Being Seen": CLERKS,
}

def assign_resource(activity_name):
    pool = ACTIVITY_RESOURCE_MAP.get(activity_name, NURSES)
    return random.choice(pool)

# Update activity generation to include resource

def add_resource_to_activities(activities):
    for act in activities:
        act["Resource"] = assign_resource(act["ActivityName"])
    return activities

def generate_simple_discharge(day, used_case_ids, used_patient_ids):
    # Registration → Triage → Bed Assigned → Nurse Assessment → Doctor Examination → Discharged
    activities = [
        {"ActivityName": "Registration", "ActivityTime": day.strftime("%Y-%m-%d 08:00:00")},
        {"ActivityName": "Triage", "ActivityTime": day.strftime("%Y-%m-%d 08:15:00")},
        {"ActivityName": "Bed Assigned", "ActivityTime": day.strftime("%Y-%m-%d 08:30:00")},
        {"ActivityName": "Nurse Assessment", "ActivityTime": day.strftime("%Y-%m-%d 08:45:00")},
        {"ActivityName": "Doctor Examination", "ActivityTime": day.strftime("%Y-%m-%d 09:00:00")},
        {"ActivityName": "Discharged", "ActivityTime": day.strftime("%Y-%m-%d 09:30:00")},
    ]
    return {
        "CaseId": f"ED{random.randint(100000, 999999)}",
        "PatientID": f"P{random.randint(1000, 9999)}",
        "activities": add_resource_to_activities(activities)
    }

def generate_discharge_with_tests(day, used_case_ids, used_patient_ids):
    # Registration → Triage → Bed Assigned → Nurse Assessment → Doctor Examination → Diagnostic Test Ordered → Blood Test Performed → Test Results Available → Treatment Administered → Discharged
    activities = [
        {"ActivityName": "Registration", "ActivityTime": day.strftime("%Y-%m-%d 08:00:00")},
        {"ActivityName": "Triage", "ActivityTime": day.strftime("%Y-%m-%d 08:10:00")},
        {"ActivityName": "Bed Assigned", "ActivityTime": day.strftime("%Y-%m-%d 08:25:00")},
        {"ActivityName": "Nurse Assessment", "ActivityTime": day.strftime("%Y-%m-%d 08:40:00")},
        {"ActivityName": "Doctor Examination", "ActivityTime": day.strftime("%Y-%m-%d 09:00:00")},
        {"ActivityName": "Diagnostic Test Ordered", "ActivityTime": day.strftime("%Y-%m-%d 09:10:00")},
        {"ActivityName": "Blood Test Performed", "ActivityTime": day.strftime("%Y-%m-%d 09:20:00")},
        {"ActivityName": "Test Results Available", "ActivityTime": day.strftime("%Y-%m-%d 09:50:00")},
        {"ActivityName": "Treatment Administered", "ActivityTime": day.strftime("%Y-%m-%d 10:00:00")},
        {"ActivityName": "Discharged", "ActivityTime": day.strftime("%Y-%m-%d 10:30:00")},
    ]
    return {
        "CaseId": f"ED{random.randint(100000, 999999)}",
        "PatientID": f"P{random.randint(1000, 9999)}",
        "activities": add_resource_to_activities(activities)
    }

def generate_admission_after_observation(day, used_case_ids, used_patient_ids):
    # Registration → ... → Observation → Disposition Decision Recorded → Admitted to Hospital
    activities = [
        {"ActivityName": "Registration", "ActivityTime": day.strftime("%Y-%m-%d 08:00:00")},
        {"ActivityName": "Triage", "ActivityTime": day.strftime("%Y-%m-%d 08:20:00")},
        {"ActivityName": "Bed Assigned", "ActivityTime": day.strftime("%Y-%m-%d 08:40:00")},
        {"ActivityName": "Nurse Assessment", "ActivityTime": day.strftime("%Y-%m-%d 09:00:00")},
        {"ActivityName": "Doctor Examination", "ActivityTime": day.strftime("%Y-%m-%d 09:30:00")},
        {"ActivityName": "Treatment Administered", "ActivityTime": day.strftime("%Y-%m-%d 10:00:00")},
        {"ActivityName": "Observation", "ActivityTime": day.strftime("%Y-%m-%d 10:30:00")},
        {"ActivityName": "Disposition Decision Recorded", "ActivityTime": day.strftime("%Y-%m-%d 12:00:00")},
        {"ActivityName": "Admitted to Hospital", "ActivityTime": day.strftime("%Y-%m-%d 12:30:00")},
    ]
    return {
        "CaseId": f"ED{random.randint(100000, 999999)}",
        "PatientID": f"P{random.randint(1000, 9999)}",
        "activities": add_resource_to_activities(activities)
    }

VARIANT_FUNCTIONS = {
    'simple_discharge': generate_simple_discharge,
    'discharge_with_tests': generate_discharge_with_tests,
    'admission_after_observation': generate_admission_after_observation,
}

def save_all_cases_json(all_cases, output_dir):
    out_path = os.path.join(output_dir, "alderaan_year_to_date.json")
    with open(out_path, "w") as f:
        json.dump({"cases": all_cases}, f, indent=2)
    print(f"Saved all cases to {out_path}")

def save_all_cases_csv(all_cases, output_dir):
    out_path = os.path.join(output_dir, "alderaan_year_to_date.csv")
    with open(out_path, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["CaseId", "ActivityName", "ActivityTime", "PatientID", "Resource"])
        writer.writeheader()
        for case in all_cases:
            for activity in case["activities"]:
                writer.writerow({
                    "CaseId": case["CaseId"],
                    "ActivityName": activity["ActivityName"],
                    "ActivityTime": activity["ActivityTime"],
                    "PatientID": case["PatientID"],
                    "Resource": activity["Resource"]
                })
    print(f"Saved all cases to {out_path}")

def generate_lwbs_cases_for_historical(all_days, n):
    """Generate n LWBS cases, distributed across the date range, with different variants."""
    cases = []
    lwbs_variants = [
        ["Registration"],
        ["Registration", "Triage"],
        ["Registration", "Triage", "Bed Assigned"],
        ["Registration", "Triage", "Bed Assigned", "Nurse Assessment"]
    ]
    used_case_ids = set()
    used_patient_ids = set()
    for i in range(n):
        # Distribute cases across the date range
        day = all_days[i % len(all_days)]
        case_id = f"ED{random.randint(100000, 999999)}"
        patient_id = f"P{random.randint(1000, 9999)}"
        path = lwbs_variants[i % len(lwbs_variants)].copy()
        path.append("Left Without Being Seen")
        time = day.replace(hour=8, minute=0, second=0)
        activities_list = []
        for activity in path:
            time += timedelta(minutes=random.randint(5, 30))
            activities_list.append({
                "ActivityName": activity,
                "ActivityTime": time.strftime("%Y-%m-%d %H:%M:%S")
            })
        activities_list = add_resource_to_activities(activities_list)
        cases.append({
            "CaseId": case_id,
            "PatientID": patient_id,
            "activities": activities_list
        })
    return cases

def generate_unique_ids(prefix, n, min_val, max_val):
    ids = set()
    while len(ids) < n:
        ids.add(f"{prefix}{random.randint(min_val, max_val)}")
    return list(ids)

# --- STEP 2: MAIN GENERATION LOOP ---
def main(output_dir=None):
    # Ensure output directory is src/Output relative to this script
    if output_dir is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, 'Output')
    os.makedirs(output_dir, exist_ok=True)
    current_date = START_DATE
    all_cases = []
    all_days = []
    # First, determine total number of cases needed
    total_case_count = 0
    temp_date = START_DATE
    while temp_date <= END_DATE:
        day_str = temp_date.strftime("%Y-%m-%d")
        month = temp_date.month
        seasonal_factor = 1.0
        if month in [1, 2]:
            seasonal_factor = 1.10
        elif month in [3, 4]:
            seasonal_factor = 0.95
        noise = random.uniform(-0.08, 0.08)
        base_count = 100 * seasonal_factor
        case_count = int(round(base_count * (1 + noise)))
        if day_str == "2025-05-04":
            case_count = int(round(case_count * 14 / 24))
        total_case_count += case_count
        temp_date += timedelta(days=1)
    # Add LWBS cases (~2% of total)
    lwbs_n = max(1, round(0.02 * total_case_count))
    total_case_count += lwbs_n
    # Pre-generate unique CaseIds and PatientIDs
    unique_case_ids = generate_unique_ids("ED", total_case_count, 100000, 999999)
    unique_patient_ids = generate_unique_ids("P", total_case_count, 1000, 9999)
    case_id_iter = iter(unique_case_ids)
    patient_id_iter = iter(unique_patient_ids)
    # Now generate cases as before, but assign unique IDs
    current_date = START_DATE
    while current_date <= END_DATE:
        all_days.append(current_date)
        day_str = current_date.strftime("%Y-%m-%d")
        month = current_date.month
        seasonal_factor = 1.0
        if month in [1, 2]:
            seasonal_factor = 1.10
        elif month in [3, 4]:
            seasonal_factor = 0.95
        noise = random.uniform(-0.08, 0.08)
        base_count = 100 * seasonal_factor
        case_count = int(round(base_count * (1 + noise)))
        if day_str == "2025-05-04":
            case_count = int(round(case_count * 14 / 24))
        n_admitted = int(round(case_count * 0.17))
        n_discharged = case_count - n_admitted
        cases = []
        for _ in range(n_discharged):
            case = generate_simple_discharge(current_date, None, None)
            case["CaseId"] = next(case_id_iter)
            case["PatientID"] = next(patient_id_iter)
            cases.append(case)
            all_cases.append(case)
        for _ in range(n_admitted):
            case = generate_admission_after_observation(current_date, None, None)
            case["CaseId"] = next(case_id_iter)
            case["PatientID"] = next(patient_id_iter)
            cases.append(case)
            all_cases.append(case)
        print(f"Generated {case_count} cases for {day_str} (admitted: {n_admitted}, discharged: {n_discharged})")
        current_date += timedelta(days=1)
    # Add LWBS cases at ~2% of total cases
    lwbs_cases = generate_lwbs_cases_for_historical(all_days, lwbs_n)
    for case in lwbs_cases:
        case["CaseId"] = next(case_id_iter)
        case["PatientID"] = next(patient_id_iter)
    all_cases.extend(lwbs_cases)
    # Save all cases to a single JSON and CSV file
    save_all_cases_json(all_cases, output_dir)
    save_all_cases_csv(all_cases, output_dir)

if __name__ == "__main__":
    main() 