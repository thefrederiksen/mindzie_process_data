import os
import json
import random
from datetime import datetime, timedelta
import csv

# --- CONFIGURATION ---

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
def generate_simple_discharge(day, used_case_ids, used_patient_ids):
    # Registration → Triage → Bed Assigned → Nurse Assessment → Doctor Examination → Discharged
    return {
        "CaseId": f"ED{random.randint(100000, 999999)}",
        "PatientID": f"P{random.randint(1000, 9999)}",
        "activities": [
            {"ActivityName": "Registration", "ActivityTime": day.strftime("%Y-%m-%d 08:00:00")},
            {"ActivityName": "Triage", "ActivityTime": day.strftime("%Y-%m-%d 08:15:00")},
            {"ActivityName": "Bed Assigned", "ActivityTime": day.strftime("%Y-%m-%d 08:30:00")},
            {"ActivityName": "Nurse Assessment", "ActivityTime": day.strftime("%Y-%m-%d 08:45:00")},
            {"ActivityName": "Doctor Examination", "ActivityTime": day.strftime("%Y-%m-%d 09:00:00")},
            {"ActivityName": "Discharged", "ActivityTime": day.strftime("%Y-%m-%d 09:30:00")},
        ]
    }

def generate_discharge_with_tests(day, used_case_ids, used_patient_ids):
    # Registration → Triage → Bed Assigned → Nurse Assessment → Doctor Examination → Diagnostic Test Ordered → Blood Test Performed → Test Results Available → Treatment Administered → Discharged
    return {
        "CaseId": f"ED{random.randint(100000, 999999)}",
        "PatientID": f"P{random.randint(1000, 9999)}",
        "activities": [
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
    }

def generate_admission_after_observation(day, used_case_ids, used_patient_ids):
    # Registration → ... → Observation → Disposition Decision Recorded → Admitted to Hospital
    return {
        "CaseId": f"ED{random.randint(100000, 999999)}",
        "PatientID": f"P{random.randint(1000, 9999)}",
        "activities": [
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
        writer = csv.DictWriter(csvfile, fieldnames=["CaseId", "ActivityName", "ActivityTime", "PatientID"])
        writer.writeheader()
        for case in all_cases:
            for activity in case["activities"]:
                writer.writerow({
                    "CaseId": case["CaseId"],
                    "ActivityName": activity["ActivityName"],
                    "ActivityTime": activity["ActivityTime"],
                    "PatientID": case["PatientID"]
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
        cases.append({
            "CaseId": case_id,
            "PatientID": patient_id,
            "activities": activities_list
        })
    return cases

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
    while current_date <= END_DATE:
        all_days.append(current_date)
        day_str = current_date.strftime("%Y-%m-%d")
        weekday = current_date.weekday()
        case_count = CASE_COUNT_BY_WEEKDAY[weekday]
        # TODO: Adjust case_count for problem days if needed
        problems = PROBLEM_DAYS.get(day_str, {})
        used_case_ids = set()
        used_patient_ids = set()
        cases = []
        # --- STEP 2: Assign variants to cases ---
        variant_choices = random.choices(
            population=list(VARIANT_MIX.keys()),
            weights=list(VARIANT_MIX.values()),
            k=case_count
        )
        for variant in variant_choices:
            case = VARIANT_FUNCTIONS[variant](current_date, used_case_ids, used_patient_ids)
            cases.append(case)
            all_cases.append(case)
        print(f"Generated {case_count} cases for {day_str} (problems: {problems})")
        current_date += timedelta(days=1)
    # Add LWBS cases at ~2% of total cases
    lwbs_n = max(1, round(0.02 * len(all_cases)))
    lwbs_cases = generate_lwbs_cases_for_historical(all_days, lwbs_n)
    all_cases.extend(lwbs_cases)
    # Save all cases to a single JSON and CSV file
    save_all_cases_json(all_cases, output_dir)
    save_all_cases_csv(all_cases, output_dir)

if __name__ == "__main__":
    main() 