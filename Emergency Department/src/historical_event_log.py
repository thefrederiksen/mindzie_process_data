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
    fieldnames = [
        "CaseId", "ActivityName", "ActivityTime", "PatientID", "Resource",
        "Age", "Sex", "ModeOfArrival", "VisitType", "HR", "BP", "Temp", "O2Sat", "Triage", "ArrivalShift"
    ]
    with open(out_path, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for case in all_cases:
            vitals = case.get("VitalSigns", {})
            for activity in case["activities"]:
                writer.writerow({
                    "CaseId": case["CaseId"],
                    "ActivityName": activity["ActivityName"],
                    "ActivityTime": activity["ActivityTime"],
                    "PatientID": case["PatientID"],
                    "Resource": activity.get("Resource", ""),
                    "Age": case.get("Age", ""),
                    "Sex": case.get("Sex", ""),
                    "ModeOfArrival": case.get("ModeOfArrival", ""),
                    "VisitType": case.get("VisitType", ""),
                    "HR": vitals.get("HR", ""),
                    "BP": vitals.get("BP", ""),
                    "Temp": vitals.get("Temp", ""),
                    "O2Sat": vitals.get("O2Sat", ""),
                    "Triage": case.get("Triage", ""),
                    "ArrivalShift": case.get("ArrivalShift", "")
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
    # Ensure there are enough unique values in the range
    if n > (max_val - min_val + 1):
        raise ValueError("Not enough unique IDs in the specified range.")
    ids = list(range(min_val, max_val + 1))
    random.shuffle(ids)
    return [f"{prefix}{id_}" for id_ in ids[:n]]

def random_age():
    r = random.random()
    if r < 0.15:
        return random.randint(0, 17)
    elif r < 0.85:
        return random.randint(18, 75)
    else:
        return random.randint(76, 100)

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

# --- STEP 2: MAIN GENERATION LOOP ---
def main(output_dir=None):
    print('Starting historical event log generation...')
    # Ensure output directory is src/Output relative to this script
    if output_dir is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, 'Output')
    os.makedirs(output_dir, exist_ok=True)
    current_date = START_DATE
    all_cases = []
    all_days = []
    # First, determine total number of cases needed
    print('Counting total number of cases...')
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
    print(f'Total number of cases to generate: {total_case_count}')
    SAFETY_MARGIN = 2
    print('Generating unique CaseIds...')
    unique_case_ids = generate_unique_ids("ED", total_case_count * SAFETY_MARGIN, 100000, 9999999)
    print('Generating unique PatientIDs...')
    unique_patient_ids = generate_unique_ids("P", total_case_count * SAFETY_MARGIN, 1000, 999999)
    print('Unique IDs generated. Beginning per-day case generation...')
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
        print(f"Generating {case_count} cases for {day_str} (admitted: {n_admitted}, discharged: {n_discharged})")
        simple_discharge_cases = []
        for _ in range(n_discharged):
            try:
                case = generate_simple_discharge(current_date, None, None)
                case["CaseId"] = next(case_id_iter)
                case["PatientID"] = next(patient_id_iter)
            except StopIteration:
                print("ERROR: Ran out of unique IDs. Increase the SAFETY_MARGIN or ID range.")
                raise
            case = add_case_attributes(case)
            simple_discharge_cases.append(case)
            if (len(simple_discharge_cases)) % 100 == 0:
                print(f'  Created {len(simple_discharge_cases)} simple discharge cases...')
        print('Generating discharge with tests cases...')
        discharge_with_tests_cases = []
        for _ in range(n_discharged):
            try:
                case = generate_discharge_with_tests(current_date, None, None)
                case["CaseId"] = next(case_id_iter)
                case["PatientID"] = next(patient_id_iter)
            except StopIteration:
                print("ERROR: Ran out of unique IDs. Increase the SAFETY_MARGIN or ID range.")
                raise
            case = add_case_attributes(case)
            discharge_with_tests_cases.append(case)
            if (len(discharge_with_tests_cases)) % 100 == 0:
                print(f'  Created {len(discharge_with_tests_cases)} discharge with tests cases...')
        print('Generating admission after observation cases...')
        admission_after_observation_cases = []
        for _ in range(n_admitted):
            try:
                case = generate_admission_after_observation(current_date, None, None)
                case["CaseId"] = next(case_id_iter)
                case["PatientID"] = next(patient_id_iter)
            except StopIteration:
                print("ERROR: Ran out of unique IDs. Increase the SAFETY_MARGIN or ID range.")
                raise
            case = add_case_attributes(case)
            admission_after_observation_cases.append(case)
            if (len(admission_after_observation_cases)) % 100 == 0:
                print(f'  Created {len(admission_after_observation_cases)} admission after observation cases...')
        print('Assembling all cases...')
        cases = simple_discharge_cases + discharge_with_tests_cases + admission_after_observation_cases
        print(f'Total cases generated for {day_str}: {len(cases)}')
        all_cases.extend(cases)
        current_date += timedelta(days=1)
    # Add LWBS cases at ~2% of total cases
    lwbs_cases = generate_lwbs_cases_for_historical(all_days, lwbs_n)
    for case in lwbs_cases:
        try:
            case["CaseId"] = next(case_id_iter)
            case["PatientID"] = next(patient_id_iter)
        except StopIteration:
            print("ERROR: Ran out of unique IDs. Increase the SAFETY_MARGIN or ID range.")
            raise
        case = add_case_attributes(case)
    all_cases.extend(lwbs_cases)
    print('Historical event log generation complete.')
    # Save all cases to a single JSON and CSV file
    save_all_cases_json(all_cases, output_dir)
    save_all_cases_csv(all_cases, output_dir)

if __name__ == "__main__":
    main() 