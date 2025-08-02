#!/usr/bin/env python3
"""
Hire to Retire Process Mining Dataset Generator
Generates realistic HR process data with embedded bottlenecks and problems
"""

import json
import csv
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
import os

# Set random seed for reproducibility
random.seed(42)

# Configuration
TOTAL_CASES = 10000
START_DATE = datetime(2023, 1, 1, 9, 0, 0)
END_DATE = datetime(2024, 12, 31, 18, 0, 0)
BUSINESS_START_HOUR = 9
BUSINESS_END_HOUR = 18

# Resources with performance factors
RESOURCES = {
    "recruitment": ["Sarah", "Mike", "Emma"],
    "interview": ["James", "Lisa", "Robert", "Peter"],  # Peter is slow
    "equipment": ["David", "Jennifer"],  # David is slow
    "management": ["James", "Lisa", "Robert"],  # Robert slow for reviews
    "training": ["Jennifer", "Michael"],
    "system": ["System"]
}

# Performance factors (1.0 = normal, <1.0 = slower)
PERFORMANCE_FACTORS = {
    "Peter": 0.5,    # 50% slower (double time)
    "David": 0.4,    # 60% slower
    "Robert": 0.3,   # 70% slower for reviews
    "System": 0.2    # 80% slower for integrations
}

# Departments and locations
DEPARTMENTS = ["Sales", "Engineering", "HR", "Finance", "Operations", "Marketing"]
DEPT_DISTRIBUTION = [0.25, 0.3, 0.1, 0.15, 0.15, 0.05]

LOCATIONS = ["New York", "London", "Singapore", "Sydney", "Berlin"]
LOC_DISTRIBUTION = [0.3, 0.25, 0.2, 0.15, 0.1]

EMPLOYMENT_TYPES = ["Full-time", "Part-time", "Contract"]
EMP_TYPE_DISTRIBUTION = [0.8, 0.1, 0.1]

RECRUITMENT_SOURCES = ["Internal", "External", "Referral", "Agency"]
REC_SOURCE_DISTRIBUTION = [0.1, 0.5, 0.25, 0.15]

def is_business_hours(dt: datetime) -> bool:
    """Check if datetime is within business hours"""
    if dt.weekday() >= 5:  # Weekend
        return False
    if dt.hour < BUSINESS_START_HOUR or dt.hour >= BUSINESS_END_HOUR:
        return False
    return True

def add_business_hours(start_dt: datetime, hours: float) -> datetime:
    """Add hours considering only business hours"""
    current = start_dt
    remaining_hours = hours
    
    while remaining_hours > 0:
        if is_business_hours(current):
            if remaining_hours >= 1:
                current += timedelta(hours=1)
                remaining_hours -= 1
            else:
                current += timedelta(hours=remaining_hours)
                remaining_hours = 0
        else:
            # Jump to next business hour
            if current.hour >= BUSINESS_END_HOUR:
                current = current.replace(hour=BUSINESS_START_HOUR, minute=0, second=0)
                current += timedelta(days=1)
            elif current.weekday() >= 5:
                days_to_monday = 7 - current.weekday()
                current += timedelta(days=days_to_monday)
                current = current.replace(hour=BUSINESS_START_HOUR, minute=0, second=0)
            else:
                current = current.replace(hour=BUSINESS_START_HOUR, minute=0, second=0)
    
    return current

def maybe_system_delay(resource: str, probability: float = 0.25) -> str:
    """Randomly replace resource with System for delays"""
    if random.random() < probability:
        return "System"
    return resource

def select_resource(activity_type: str, activity_name: str = "") -> str:
    """Select resource based on activity type and bottleneck rules"""
    base_resources = RESOURCES.get(activity_type, ["Unknown"])
    
    # Global bottleneck assignments - these resources should appear frequently across all activities
    # to achieve overall target percentages: Peter 30%, David 20%, Robert 35%
    
    # First, check for forced bottleneck assignments across all activities
    rand = random.random()
    if rand < 0.30:  # 30% of all activities go to Peter
        return "Peter"
    elif rand < 0.50:  # Next 20% go to David (30% + 20% = 50%)
        return "David" 
    elif rand < 0.85:  # Next 35% go to Robert (50% + 35% = 85%)
        return "Robert"
    
    # For remaining 15% of activities, use normal resource selection logic
    
    # Equipment assignments
    if activity_type == "equipment":
        return "Jennifer"  # Normal resource for remaining equipment activities
    
    # Interview assignments  
    elif activity_type == "interview":
        # Distribute among others
        others = ["James", "Lisa"]
        return random.choice(others)
    
    # Management activities
    elif activity_type == "management":
        return random.choice(["James", "Lisa"])
    
    # Recruitment activities
    elif activity_type == "recruitment":
        return random.choice(["Sarah", "Mike", "Emma"])
    
    # Training activities
    elif activity_type == "training":
        return random.choice(["Jennifer", "Michael"])
    
    # Default
    return random.choice(base_resources)

def calculate_duration(base_hours: float, resource: str) -> float:
    """Calculate actual duration based on resource performance"""
    performance = PERFORMANCE_FACTORS.get(resource, 1.0)
    if performance < 1.0:
        # Slower resources take longer
        actual_hours = base_hours / performance
    else:
        # Add some random variation for normal resources
        actual_hours = base_hours * random.uniform(0.8, 1.2)
    
    return actual_hours

def generate_employee_id() -> str:
    """Generate unique employee ID"""
    return f"E{random.randint(100000, 999999)}"

def generate_salary(job_level: int) -> int:
    """Generate salary based on job level"""
    base_salaries = {
        1: 40000, 2: 50000, 3: 65000, 4: 80000, 5: 100000,
        6: 125000, 7: 150000, 8: 180000, 9: 210000, 10: 250000
    }
    base = base_salaries.get(job_level, 80000)
    return int(base * random.uniform(0.9, 1.15))

def generate_recruitment_case(case_id: str, start_date: datetime, employee_id: str) -> Tuple[List[Dict], Dict]:
    """Generate a recruitment case (may end in rejection or hire)"""
    activities = []
    current_time = start_date
    
    # Case attributes
    department = random.choices(DEPARTMENTS, DEPT_DISTRIBUTION)[0]
    location = random.choices(LOCATIONS, LOC_DISTRIBUTION)[0]
    job_level = min(10, max(1, int(random.normalvariate(4, 2))))
    employment_type = random.choices(EMPLOYMENT_TYPES, EMP_TYPE_DISTRIBUTION)[0]
    recruitment_source = random.choices(RECRUITMENT_SOURCES, REC_SOURCE_DISTRIBUTION)[0]
    hiring_manager = f"M{random.randint(100000, 999999)}"
    
    case_attrs = {
        "CaseId": case_id,
        "EmployeeID": employee_id,
        "Department": department,
        "Location": location,
        "JobLevel": job_level,
        "EmploymentType": employment_type,
        "RecruitmentSource": recruitment_source,
        "HiringManager": hiring_manager,
        "CurrentSalary": None,
        "PerformanceRating": None,
        "TenureYears": 0
    }
    
    # Job Posted
    resource = select_resource("recruitment")
    resource = maybe_system_delay(resource, 0.25)  # 25% chance of system delay
    duration = calculate_duration(0.5, resource)
    current_time = add_business_hours(current_time, duration)
    
    activities.append({
        **case_attrs,
        "ActivityName": "Job Posted",
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "PerformedBy": "XYZ",
        "SystemUsed": "XYZ_HRIS"
    })
    
    # Application Received
    wait_days = random.randint(5, 14)  # Increased to add ~7 days average
    current_time = add_business_hours(current_time, wait_days * 8)
    resource = select_resource("recruitment")
    resource = maybe_system_delay(resource, 0.25)  # 25% chance of system delay
    duration = calculate_duration(0.25, resource)
    current_time = add_business_hours(current_time, duration)
    
    activities.append({
        **case_attrs,
        "ActivityName": "Application Received",
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "PerformedBy": "XYZ",
        "SystemUsed": "XYZ_HRIS"
    })
    
    # Note: System delays will be handled by randomly assigning System as resource
    
    # 60% rejected at screening
    if random.random() < 0.6:
        current_time = add_business_hours(current_time, random.randint(1, 3) * 8)
        resource = select_resource("recruitment")
        activities.append({
            **case_attrs,
            "ActivityName": "Application Rejected",
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "PerformedBy": "XYZ",
            "SystemUsed": "XYZ_HRIS"
        })
        return activities, None
    
    # Interview - may have rescheduling
    interview_loops = 1
    if random.random() < 0.25:  # 25% need rescheduling
        interview_loops = random.randint(2, 3)
    
    for loop in range(interview_loops):
        wait_days = random.randint(7, 21) if loop == 0 else random.randint(3, 7)  # Add ~7 more days
        current_time = add_business_hours(current_time, wait_days * 8)
        resource = select_resource("interview")
        # No system delay for measured bottleneck activity
        duration = calculate_duration(random.uniform(2, 4), resource)
        current_time = add_business_hours(current_time, duration)
        
        activities.append({
            **case_attrs,
            "ActivityName": "Interview Completed",
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "PerformedBy": "Joint",
            "SystemUsed": "Customer_System"
        })
    
    # 70% fail interview
    if random.random() < 0.7:
        current_time = add_business_hours(current_time, random.randint(1, 5) * 8)
        resource = select_resource("management")
        activities.append({
            **case_attrs,
            "ActivityName": "Interview Failed",
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "PerformedBy": "Joint",
            "SystemUsed": "Customer_System"
        })
        return activities, None
    
    # Offer Extended - may have negotiation loops
    offer_loops = 1
    if random.random() < 0.15:  # 15% negotiate
        offer_loops = random.randint(2, 3)
    
    case_attrs["CurrentSalary"] = generate_salary(job_level)
    
    for loop in range(offer_loops):
        wait_days = random.randint(5, 14) if loop == 0 else random.randint(2, 5)  # Add ~5 more days
        current_time = add_business_hours(current_time, wait_days * 8)
        resource = select_resource("recruitment")
        duration = calculate_duration(1, resource)
        current_time = add_business_hours(current_time, duration)
        
        activities.append({
            **case_attrs,
            "ActivityName": "Offer Extended",
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "PerformedBy": "Joint",
            "SystemUsed": "XYZ_HRIS"
        })
    
    # 15% reject offer
    if random.random() < 0.15:
        current_time = add_business_hours(current_time, random.randint(1, 10) * 8)
        resource = select_resource("recruitment")
        activities.append({
            **case_attrs,
            "ActivityName": "Offer Rejected",
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "PerformedBy": "XYZ",
            "SystemUsed": "XYZ_HRIS"
        })
        return activities, None
    
    # Offer Accepted
    wait_days = random.randint(1, 10)
    current_time = add_business_hours(current_time, wait_days * 8)
    resource = select_resource("recruitment")
    duration = calculate_duration(0.25, resource)
    current_time = add_business_hours(current_time, duration)
    
    activities.append({
        **case_attrs,
        "ActivityName": "Offer Accepted",
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "PerformedBy": "XYZ",
        "SystemUsed": "XYZ_HRIS"
    })
    
    return activities, (case_attrs, current_time)

def generate_onboarding_and_employment(case_attrs: Dict, start_time: datetime, end_date: datetime) -> List[Dict]:
    """Generate onboarding and employment activities"""
    activities = []
    current_time = start_time
    
    # Onboarding Started
    wait_days = random.randint(7, 30)
    current_time = add_business_hours(current_time, wait_days * 8)
    
    # Check for system delays
    if random.random() < 0.25:  # 25% system integration delay
        resource = "System"
        delay_hours = calculate_duration(random.uniform(24, 72), resource)
        current_time = add_business_hours(current_time, delay_hours)
    
    resource = select_resource("recruitment")
    duration = calculate_duration(4, resource)
    current_time = add_business_hours(current_time, duration)
    
    case_attrs["HireDate"] = current_time.strftime("%Y-%m-%d")
    
    activities.append({
        **case_attrs,
        "ActivityName": "Onboarding Started",
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "PerformedBy": "XYZ",
        "SystemUsed": "XYZ_HRIS"
    })
    
    # Equipment Assigned
    wait_days = 1 if random.random() > 0.2 else random.randint(1, 3)
    current_time = add_business_hours(current_time, wait_days * 8)
    resource = select_resource("equipment")
    # No system delay for measured bottleneck activity
    duration = calculate_duration(2, resource)
    current_time = add_business_hours(current_time, duration)
    
    activities.append({
        **case_attrs,
        "ActivityName": "Equipment Assigned",
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "PerformedBy": "Customer",
        "SystemUsed": "Customer_System"
    })
    
    # 10% fail probation
    probation_date = add_business_hours(current_time, 90 * 8)
    
    if random.random() < 0.1:
        resource = select_resource("management")
        activities.append({
            **case_attrs,
            "ActivityName": "Probation Failed",
            "ActivityTime": probation_date.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "PerformedBy": "Joint",
            "SystemUsed": "XYZ_HRIS"
        })
        return activities
    
    # Probation Completed
    resource = select_resource("management")
    duration = calculate_duration(1, resource)
    probation_date = add_business_hours(probation_date, duration)
    
    activities.append({
        **case_attrs,
        "ActivityName": "Probation Completed",
        "ActivityTime": probation_date.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "PerformedBy": "Joint",
        "SystemUsed": "XYZ_HRIS"
    })
    
    current_time = probation_date
    
    # Employment activities
    next_review = add_business_hours(current_time, 180 * 8)  # First review at 6 months
    has_resigned = False
    resignation_date = None
    
    # Determine if employee will resign (reduced from 95% to 70% to keep more employees longer)
    if random.random() < 0.70:  # 70% will resign eventually
        # More spread out resignation timing to ensure performance reviews happen
        if random.random() < 0.60:  # 60% resign in first year
            tenure_days = random.randint(200, 365)  # 7 months to 1 year (ensures 6-month review)
        elif random.random() < 0.80:  # 20% resign in second year  
            tenure_days = random.randint(366, 730)  # 1-2 years
        else:  # 20% resign later
            tenure_days = random.randint(731, 1460)  # 2-4 years
        resignation_date = add_business_hours(current_time, tenure_days * 8)
    
    while current_time < end_date and not has_resigned:
        # Check if time for resignation
        if resignation_date and current_time >= resignation_date:
            resource = select_resource("recruitment")
            duration = calculate_duration(0.5, resource)
            current_time = add_business_hours(current_time, duration)
            
            activities.append({
                **case_attrs,
                "ActivityName": "Resignation Submitted",
                "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "Resource": resource,
                "PerformedBy": "Joint",
                "SystemUsed": "XYZ_HRIS"
            })
            
            # Employment Ended
            exit_days = random.randint(14, 30)
            current_time = add_business_hours(current_time, exit_days * 8)
            
            # System delays for exit processing
            if random.random() < 0.25:
                resource = "System"
                delay_hours = calculate_duration(random.uniform(24, 48), resource)
                current_time = add_business_hours(current_time, delay_hours)
            
            resource = select_resource("recruitment")
            duration = calculate_duration(4, resource)
            current_time = add_business_hours(current_time, duration)
            
            activities.append({
                **case_attrs,
                "ActivityName": "Employment Ended",
                "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "Resource": resource,
                "PerformedBy": "XYZ",
                "SystemUsed": "XYZ_HRIS"
            })
            
            has_resigned = True
            break
        
        # Performance Review (annual)
        if current_time >= next_review:
            resource = select_resource("management", "Performance Review")
            # No system delay for measured bottleneck activity
            duration = calculate_duration(2, resource)
            review_time = add_business_hours(next_review, duration)
            
            # Update performance rating
            if case_attrs["PerformanceRating"] is None:
                case_attrs["PerformanceRating"] = round(random.normalvariate(3.5, 0.7), 1)
                case_attrs["PerformanceRating"] = max(1, min(5, case_attrs["PerformanceRating"]))
            else:
                # Slight variation from previous
                change = random.uniform(-0.5, 0.5)
                case_attrs["PerformanceRating"] = round(case_attrs["PerformanceRating"] + change, 1)
                case_attrs["PerformanceRating"] = max(1, min(5, case_attrs["PerformanceRating"]))
            
            activities.append({
                **case_attrs,
                "ActivityName": "Performance Review",
                "ActivityTime": review_time.strftime("%Y-%m-%d %H:%M:%S"),
                "Resource": resource,
                "PerformedBy": "Customer",
                "SystemUsed": "Customer_System"
            })
            
            # 15% get promoted
            if random.random() < 0.15 and case_attrs["JobLevel"] < 10:
                wait_days = random.randint(30, 60)
                promo_time = add_business_hours(review_time, wait_days * 8)
                resource = select_resource("management")
                duration = calculate_duration(1, resource)
                promo_time = add_business_hours(promo_time, duration)
                
                case_attrs["JobLevel"] += 1
                case_attrs["CurrentSalary"] = generate_salary(case_attrs["JobLevel"])
                
                activities.append({
                    **case_attrs,
                    "ActivityName": "Promotion Approved",
                    "ActivityTime": promo_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "Resource": resource,
                    "PerformedBy": "Joint",
                    "SystemUsed": "XYZ_HRIS"
                })
            
            # Schedule next review - annual after first 6-month review
            next_review = add_business_hours(next_review, 365 * 8)
        
        # Leave requests (3-4 times per year)
        leave_probability = 3.5 / 365  # Average 3.5 leaves per year
        if random.random() < leave_probability:
            resource = select_resource("recruitment")
            duration = calculate_duration(0.25, resource)
            leave_time = add_business_hours(current_time, duration)
            
            activities.append({
                **case_attrs,
                "ActivityName": "Leave Requested",
                "ActivityTime": leave_time.strftime("%Y-%m-%d %H:%M:%S"),
                "Resource": resource,
                "PerformedBy": "XYZ",
                "SystemUsed": "XYZ_HRIS"
            })
            
            # 95% approved
            if random.random() < 0.95:
                wait_hours = random.randint(4, 24)
                approval_time = add_business_hours(leave_time, wait_hours)
                resource = select_resource("management")
                duration = calculate_duration(0.25, resource)
                approval_time = add_business_hours(approval_time, duration)
                
                activities.append({
                    **case_attrs,
                    "ActivityName": "Leave Approved",
                    "ActivityTime": approval_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "Resource": resource,
                    "PerformedBy": "Customer",
                    "SystemUsed": "Customer_System"
                })
        
        # Training (2-3 times per year)
        training_probability = 2.5 / 365
        if random.random() < training_probability:
            training_hours = random.choice([8, 16, 24, 40])
            training_time = add_business_hours(current_time, training_hours)
            resource = select_resource("training")
            
            # 25% don't complete training
            if random.random() < 0.75:
                activities.append({
                    **case_attrs,
                    "ActivityName": "Training Completed",
                    "ActivityTime": training_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "Resource": resource,
                    "PerformedBy": "XYZ",
                    "SystemUsed": "XYZ_HRIS"
                })
        
        # Update tenure
        hire_date = datetime.strptime(case_attrs["HireDate"], "%Y-%m-%d")
        tenure_years = (current_time - hire_date).days / 365.25
        case_attrs["TenureYears"] = round(tenure_years, 1)
        
        # Move time forward
        current_time = add_business_hours(current_time, random.randint(1, 30) * 8)
    
    return activities

def generate_dataset():
    """Generate the complete dataset"""
    all_activities = []
    completed_cases = 0
    
    # Generate cases distributed over 2 years
    for i in range(TOTAL_CASES):
        # Distribute case starts over the 2-year period
        days_offset = random.randint(0, 730)
        case_start = add_business_hours(START_DATE, days_offset * 8)
        
        employee_id = generate_employee_id()
        case_id = f"HR{case_start.year}_{employee_id}"
        
        # Generate recruitment phase
        recruitment_activities, hire_info = generate_recruitment_case(case_id, case_start, employee_id)
        all_activities.extend(recruitment_activities)
        
        # Check if case ended (rejected/failed)
        last_activity = recruitment_activities[-1]["ActivityName"]
        if last_activity in ["Application Rejected", "Interview Failed", "Offer Rejected"]:
            completed_cases += 1
            continue
        
        # If hired, continue with onboarding and employment
        if hire_info:
            case_attrs, current_time = hire_info
            employment_activities = generate_onboarding_and_employment(case_attrs, current_time, END_DATE)
            all_activities.extend(employment_activities)
            
            # Check if case completed
            if employment_activities:
                last_activity = employment_activities[-1]["ActivityName"]
                if last_activity in ["Probation Failed", "Employment Ended"]:
                    completed_cases += 1
                elif employment_activities[-1]["ActivityTime"][:4] == "2024":
                    # Case reached end of time period
                    completed_cases += 1
    
    # Sort activities by time
    all_activities.sort(key=lambda x: x["ActivityTime"])
    
    # Create case-centric JSON structure
    cases_dict = {}
    for activity in all_activities:
        case_id = activity["CaseId"]
        if case_id not in cases_dict:
            # Get final case attributes from the last activity for this case
            final_salary = activity.get("CurrentSalary")
            final_rating = activity.get("PerformanceRating") 
            recruitment_source = activity.get("RecruitmentSource")
            
            # Find the most recent non-null values for case attributes
            for act in all_activities:
                if act["CaseId"] == case_id:
                    if act.get("CurrentSalary") is not None:
                        final_salary = act["CurrentSalary"]
                    if act.get("PerformanceRating") is not None:
                        final_rating = act["PerformanceRating"]
                    if act.get("RecruitmentSource") is not None:
                        recruitment_source = act["RecruitmentSource"]
            
            cases_dict[case_id] = {
                "CaseId": case_id,
                "Department": activity["Department"],
                "Location": activity["Location"],
                "JobLevel": activity["JobLevel"],
                "EmploymentType": activity["EmploymentType"],
                "RecruitmentSource": recruitment_source,
                "CurrentSalary": final_salary,
                "PerformanceRating": final_rating,
                "Activities": []
            }
        
        # Add activity without duplicating case attributes
        activity_only = {
            "ActivityName": activity["ActivityName"],
            "ActivityTime": activity["ActivityTime"],
            "Resource": activity["Resource"],
            "PerformedBy": activity["PerformedBy"],
            "SystemUsed": activity["SystemUsed"]
        }
        
        # Add TenureYears as event attribute since it changes over time
        if activity.get("TenureYears", 0) > 0:
            activity_only["TenureYears"] = activity["TenureYears"]
            
        cases_dict[case_id]["Activities"].append(activity_only)
    
    cases_list = list(cases_dict.values())
    
    # Calculate statistics
    print(f"Total cases generated: {len(cases_list)}")
    print(f"Completed cases: {completed_cases}")
    print(f"Completion rate: {completed_cases/len(cases_list)*100:.1f}%")
    print(f"Total activities: {len(all_activities)}")
    
    # Save JSON
    json_path = os.path.join("output", "hire_to_retire_historical.json")
    with open(json_path, 'w') as f:
        json.dump(cases_list, f, indent=2)
    print(f"JSON saved to: {json_path}")
    
    # Save CSV
    csv_path = os.path.join("output", "hire_to_retire_historical.csv")
    with open(csv_path, 'w', newline='') as f:
        if all_activities:
            # Collect all possible fieldnames from all activities
            fieldnames_set = set()
            for activity in all_activities:
                fieldnames_set.update(activity.keys())
            fieldnames = sorted(list(fieldnames_set))
            
            # Ensure important fields come first
            priority_fields = ["CaseId", "ActivityName", "ActivityTime", "Resource"]
            fieldnames = [f for f in priority_fields if f in fieldnames] + [f for f in fieldnames if f not in priority_fields]
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_activities)
    print(f"CSV saved to: {csv_path}")
    
    # Calculate and display KPIs
    calculate_kpis(cases_list, all_activities)

def calculate_kpis(cases: List[Dict], activities: List[Dict]):
    """Calculate and display key performance indicators"""
    print("\n=== KEY PERFORMANCE INDICATORS ===")
    
    # Time to Fill
    hired_cases = []
    for case in cases:
        acts = case["Activities"]
        job_posted = next((a for a in acts if a["ActivityName"] == "Job Posted"), None)
        offer_accepted = next((a for a in acts if a["ActivityName"] == "Offer Accepted"), None)
        
        if job_posted and offer_accepted:
            start = datetime.strptime(job_posted["ActivityTime"], "%Y-%m-%d %H:%M:%S")
            end = datetime.strptime(offer_accepted["ActivityTime"], "%Y-%m-%d %H:%M:%S")
            days = (end - start).days
            hired_cases.append(days)
    
    if hired_cases:
        avg_time_to_fill = sum(hired_cases) / len(hired_cases)
        print(f"Average Time to Fill: {avg_time_to_fill:.1f} days")
        print(f"  - Target: <30 days")
        print(f"  - Cases taking >45 days: {len([d for d in hired_cases if d > 45])}/{len(hired_cases)} ({len([d for d in hired_cases if d > 45])/len(hired_cases)*100:.1f}%)")
    
    # First Year Retention
    employees_hired = 0
    employees_left_first_year = 0
    
    for case in cases:
        acts = case["Activities"]
        onboarding = next((a for a in acts if a["ActivityName"] == "Onboarding Started"), None)
        exit_activity = next((a for a in acts if a["ActivityName"] in ["Employment Ended", "Probation Failed"]), None)
        
        if onboarding:
            employees_hired += 1
            if exit_activity:
                start = datetime.strptime(onboarding["ActivityTime"], "%Y-%m-%d %H:%M:%S")
                end = datetime.strptime(exit_activity["ActivityTime"], "%Y-%m-%d %H:%M:%S")
                if (end - start).days < 365:
                    employees_left_first_year += 1
    
    if employees_hired > 0:
        first_year_turnover = employees_left_first_year / employees_hired * 100
        print(f"\nFirst Year Turnover Rate: {first_year_turnover:.1f}%")
        print(f"  - Target: <15%")
        print(f"  - Employees who left in first year: {employees_left_first_year}/{employees_hired}")
    
    # Process Bottlenecks
    print("\n=== BOTTLENECK ANALYSIS ===")
    
    # Interview delays
    interview_delays = []
    for act in activities:
        if act["ActivityName"] == "Interview Completed" and act["Resource"] == "Peter":
            interview_delays.append(act)
    
    print(f"Interview Delays (Peter): {len(interview_delays)} cases affected")
    
    # Equipment delays
    equipment_delays = []
    for act in activities:
        if act["ActivityName"] == "Equipment Assigned" and act["Resource"] == "David":
            equipment_delays.append(act)
    
    print(f"Equipment Provisioning Delays (David): {len(equipment_delays)} cases affected")
    
    # Review delays
    review_delays = []
    for act in activities:
        if act["ActivityName"] == "Performance Review" and act["Resource"] == "Robert":
            review_delays.append(act)
    
    print(f"Performance Review Delays (Robert): {len(review_delays)} cases affected")

if __name__ == "__main__":
    print("Generating Hire to Retire Process Mining Dataset...")
    print("=" * 50)
    generate_dataset()
    print("\nDataset generation complete!")