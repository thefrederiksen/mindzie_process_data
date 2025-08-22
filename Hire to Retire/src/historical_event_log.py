#!/usr/bin/env python3
"""
Enhanced Hire to Retire Process Mining Dataset Generator
Generates realistic HR process data with comprehensive activities and realistic bottlenecks
"""

import json
import csv
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional
import os

# Set random seed for reproducibility
random.seed(42)

# Configuration
TOTAL_CASES = 3000
START_DATE = datetime(2023, 1, 1, 9, 0, 0)
END_DATE = datetime(2024, 12, 31, 18, 0, 0)
BUSINESS_START_HOUR = 9
BUSINESS_END_HOUR = 18

# Load activities from JSON
def load_activities():
    """Load activity definitions from activities.json"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    activities_path = os.path.join(script_dir, 'activities.json')
    with open(activities_path, 'r') as f:
        data = json.load(f)
    return {act['name']: act for act in data['activities']}

ACTIVITIES = load_activities()

# Resources with performance factors
RESOURCES = {
    "recruitment": ["Sarah", "Mike", "Emma", "Alex", "Jordan"],
    "interview": ["James", "Lisa", "Robert", "Peter", "Susan"],  # Peter is slow
    "equipment": ["David", "Jennifer", "Chris"],  # David is slow
    "management": ["James", "Lisa", "Robert", "Michelle"],  # Robert slow for reviews
    "training": ["Jennifer", "Michael", "Rachel"],
    "hr_admin": ["Emma", "Alex", "Jordan"],
    "it_support": ["Chris", "David", "Sam"],
    "system": ["System"]
}

# Performance factors (1.0 = normal, <1.0 = slower)
PERFORMANCE_FACTORS = {
    "Peter": 0.6,    # 40% slower
    "David": 0.5,    # 50% slower
    "Robert": 0.4,   # 60% slower for reviews
    "System": 0.3    # 70% slower for integrations
}

# Departments and locations
DEPARTMENTS = ["Sales", "Engineering", "HR", "Finance", "Operations", "Marketing", "Customer Success", "Legal"]
DEPT_DISTRIBUTION = [0.20, 0.25, 0.08, 0.12, 0.15, 0.10, 0.07, 0.03]

LOCATIONS = ["New York", "London", "Singapore", "Sydney", "Berlin", "Toronto", "Tokyo"]
LOC_DISTRIBUTION = [0.25, 0.20, 0.15, 0.10, 0.10, 0.10, 0.10]

EMPLOYMENT_TYPES = ["Full-time", "Part-time", "Contract", "Intern"]
EMP_TYPE_DISTRIBUTION = [0.75, 0.10, 0.10, 0.05]

RECRUITMENT_SOURCES = ["Internal", "External", "Referral", "Agency", "University", "LinkedIn"]
REC_SOURCE_DISTRIBUTION = [0.10, 0.35, 0.20, 0.15, 0.10, 0.10]

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

def select_resource(activity_name: str) -> str:
    """Select resource based on activity with realistic bottlenecks"""
    activity = ACTIVITIES.get(activity_name, {})
    responsible = activity.get('responsible', 'Unknown')
    
    # Map responsibility to resource type
    if 'Equipment' in activity_name or 'System Access' in activity_name:
        resource_type = 'equipment'
    elif 'Interview' in activity_name:
        resource_type = 'interview'
    elif 'Review' in activity_name or 'Promotion' in activity_name:
        resource_type = 'management'
    elif 'Training' in activity_name or 'Orientation' in activity_name:
        resource_type = 'training'
    elif any(x in activity_name for x in ['Posted', 'Application', 'Offer', 'Background', 'Reference']):
        resource_type = 'recruitment'
    elif 'System' in activity_name or 'Integration' in activity_name:
        resource_type = 'system'
    else:
        resource_type = 'hr_admin'
    
    base_resources = RESOURCES.get(resource_type, ["Unknown"])
    
    # Apply realistic bottleneck logic
    if resource_type == "equipment":
        if random.random() < 0.4:  # 40% chance David handles equipment (bottleneck)
            return "David"
        return random.choice([r for r in base_resources if r != "David"])
    
    elif resource_type == "interview":
        if random.random() < 0.3:  # 30% chance Peter does interviews (bottleneck)
            return "Peter"
        return random.choice([r for r in base_resources if r != "Peter"])
    
    elif resource_type == "management":
        if "Review" in activity_name and random.random() < 0.5:  # 50% of reviews go to Robert
            return "Robert"
        return random.choice([r for r in base_resources if r != "Robert"])
    
    elif resource_type == "system":
        return "System"  # Always slow
    
    # Default - balanced distribution
    return random.choice(base_resources)

def calculate_duration(activity_name: str, resource: str) -> float:
    """Calculate actual duration based on activity and resource performance"""
    activity = ACTIVITIES.get(activity_name, {})
    base_hours = activity.get('typical_duration_hours', 1.0)
    
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
        1: 45000, 2: 55000, 3: 70000, 4: 85000, 5: 105000,
        6: 130000, 7: 160000, 8: 190000, 9: 225000, 10: 275000
    }
    base = base_salaries.get(job_level, 85000)
    return int(base * random.uniform(0.85, 1.20))

def determine_responsible_party(activity_name: str) -> str:
    """Determine who performs the activity based on activities.json"""
    activity = ACTIVITIES.get(activity_name, {})
    responsible = activity.get('responsible', 'Unknown')
    
    if responsible == "XYZ Company":
        return "XYZ"
    elif responsible == "Customer Organization":
        return "Customer"
    elif responsible == "Joint":
        return "Joint"
    else:
        return "Unknown"

def determine_system_used(activity_name: str, performed_by: str) -> str:
    """Determine which system is used for the activity"""
    if performed_by == "XYZ":
        return "XYZ_HRIS"
    elif performed_by == "Customer":
        return "Customer_System"
    elif performed_by == "Joint":
        return random.choice(["XYZ_HRIS", "Customer_System", "Integrated_Platform"])
    else:
        return "Unknown_System"

def generate_recruitment_phase(case_id: str, start_date: datetime, employee_id: str) -> Tuple[List[Dict], Optional[Tuple[Dict, datetime]]]:
    """Generate comprehensive recruitment phase activities"""
    activities = []
    current_time = start_date
    
    # Initialize case attributes
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
    activity_name = "Job Posted"
    resource = select_resource(activity_name)
    duration = calculate_duration(activity_name, resource)
    current_time = add_business_hours(current_time, duration)
    performed_by = determine_responsible_party(activity_name)
    
    activities.append({
        **case_attrs,
        "ActivityName": activity_name,
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "PerformedBy": performed_by,
        "SystemUsed": determine_system_used(activity_name, performed_by)
    })
    
    # Application Received
    wait_days = random.randint(1, 7)
    current_time = add_business_hours(current_time, wait_days * 8)
    activity_name = "Application Received"
    resource = select_resource(activity_name)
    duration = calculate_duration(activity_name, resource)
    current_time = add_business_hours(current_time, duration)
    performed_by = determine_responsible_party(activity_name)
    
    activities.append({
        **case_attrs,
        "ActivityName": activity_name,
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "PerformedBy": performed_by,
        "SystemUsed": determine_system_used(activity_name, performed_by)
    })
    
    # Application Screened
    wait_days = random.randint(1, 3)
    current_time = add_business_hours(current_time, wait_days * 8)
    activity_name = "Application Screened"
    resource = select_resource(activity_name)
    duration = calculate_duration(activity_name, resource)
    current_time = add_business_hours(current_time, duration)
    performed_by = determine_responsible_party(activity_name)
    
    activities.append({
        **case_attrs,
        "ActivityName": activity_name,
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "PerformedBy": performed_by,
        "SystemUsed": determine_system_used(activity_name, performed_by)
    })
    
    # 50% rejected at screening
    if random.random() < 0.5:
        current_time = add_business_hours(current_time, random.randint(1, 2) * 8)
        activity_name = "Application Rejected"
        resource = select_resource(activity_name)
        performed_by = determine_responsible_party(activity_name)
        activities.append({
            **case_attrs,
            "ActivityName": activity_name,
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "PerformedBy": performed_by,
            "SystemUsed": determine_system_used(activity_name, performed_by),
            "RejectionReason": random.choice(["Experience mismatch", "Skills gap", "Overqualified", "Location mismatch"])
        })
        return activities, None
    
    # Phone Interview
    wait_days = random.randint(2, 5)
    current_time = add_business_hours(current_time, wait_days * 8)
    activity_name = "Phone Interview Scheduled"
    resource = select_resource(activity_name)
    duration = calculate_duration(activity_name, resource)
    current_time = add_business_hours(current_time, duration)
    performed_by = determine_responsible_party(activity_name)
    
    activities.append({
        **case_attrs,
        "ActivityName": activity_name,
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "PerformedBy": performed_by,
        "SystemUsed": determine_system_used(activity_name, performed_by)
    })
    
    wait_days = random.randint(1, 3)
    current_time = add_business_hours(current_time, wait_days * 8)
    activity_name = "Phone Interview Completed"
    resource = select_resource(activity_name)
    duration = calculate_duration(activity_name, resource)
    current_time = add_business_hours(current_time, duration)
    performed_by = determine_responsible_party(activity_name)
    
    activities.append({
        **case_attrs,
        "ActivityName": activity_name,
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "PerformedBy": performed_by,
        "SystemUsed": determine_system_used(activity_name, performed_by)
    })
    
    # 30% fail phone interview
    if random.random() < 0.3:
        current_time = add_business_hours(current_time, random.randint(1, 2) * 8)
        activity_name = "Interview Failed"
        resource = select_resource(activity_name)
        performed_by = determine_responsible_party(activity_name)
        activities.append({
            **case_attrs,
            "ActivityName": activity_name,
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "PerformedBy": performed_by,
            "SystemUsed": determine_system_used(activity_name, performed_by),
            "RejectionReason": random.choice(["Poor communication", "Technical skills", "Cultural fit"])
        })
        return activities, None
    
    # Onsite Interview
    wait_days = random.randint(3, 7)
    current_time = add_business_hours(current_time, wait_days * 8)
    activity_name = "Onsite Interview Scheduled"
    resource = select_resource(activity_name)
    duration = calculate_duration(activity_name, resource)
    current_time = add_business_hours(current_time, duration)
    performed_by = determine_responsible_party(activity_name)
    
    activities.append({
        **case_attrs,
        "ActivityName": activity_name,
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "PerformedBy": performed_by,
        "SystemUsed": determine_system_used(activity_name, performed_by)
    })
    
    wait_days = random.randint(2, 5)
    current_time = add_business_hours(current_time, wait_days * 8)
    activity_name = "Onsite Interview Completed"
    resource = select_resource(activity_name)
    duration = calculate_duration(activity_name, resource)
    current_time = add_business_hours(current_time, duration)
    performed_by = determine_responsible_party(activity_name)
    
    activities.append({
        **case_attrs,
        "ActivityName": activity_name,
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "PerformedBy": performed_by,
        "SystemUsed": determine_system_used(activity_name, performed_by)
    })
    
    # 40% fail onsite interview
    if random.random() < 0.4:
        current_time = add_business_hours(current_time, random.randint(1, 3) * 8)
        activity_name = "Interview Failed"
        resource = select_resource(activity_name)
        performed_by = determine_responsible_party(activity_name)
        activities.append({
            **case_attrs,
            "ActivityName": activity_name,
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "PerformedBy": performed_by,
            "SystemUsed": determine_system_used(activity_name, performed_by),
            "RejectionReason": random.choice(["Technical assessment", "Team fit", "Salary expectations"])
        })
        return activities, None
    
    # Reference Check
    wait_days = random.randint(1, 3)
    current_time = add_business_hours(current_time, wait_days * 8)
    activity_name = "Reference Check Completed"
    resource = select_resource(activity_name)
    duration = calculate_duration(activity_name, resource)
    current_time = add_business_hours(current_time, duration)
    performed_by = determine_responsible_party(activity_name)
    
    activities.append({
        **case_attrs,
        "ActivityName": activity_name,
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "PerformedBy": performed_by,
        "SystemUsed": determine_system_used(activity_name, performed_by)
    })
    
    # Background Check
    activity_name = "Background Check Initiated"
    resource = select_resource(activity_name)
    duration = calculate_duration(activity_name, resource)
    current_time = add_business_hours(current_time, duration)
    performed_by = determine_responsible_party(activity_name)
    
    activities.append({
        **case_attrs,
        "ActivityName": activity_name,
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "PerformedBy": performed_by,
        "SystemUsed": determine_system_used(activity_name, performed_by)
    })
    
    wait_days = random.randint(3, 7)
    current_time = add_business_hours(current_time, wait_days * 8)
    activity_name = "Background Check Completed"
    resource = select_resource(activity_name)
    duration = calculate_duration(activity_name, resource)
    current_time = add_business_hours(current_time, duration)
    performed_by = determine_responsible_party(activity_name)
    
    activities.append({
        **case_attrs,
        "ActivityName": activity_name,
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "PerformedBy": performed_by,
        "SystemUsed": determine_system_used(activity_name, performed_by)
    })
    
    # 2% fail background check
    if random.random() < 0.02:
        activity_name = "Background Check Failed"
        resource = select_resource(activity_name)
        performed_by = determine_responsible_party(activity_name)
        activities.append({
            **case_attrs,
            "ActivityName": activity_name,
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "PerformedBy": performed_by,
            "SystemUsed": determine_system_used(activity_name, performed_by)
        })
        return activities, None
    
    # Offer Extended
    wait_days = random.randint(1, 3)
    current_time = add_business_hours(current_time, wait_days * 8)
    case_attrs["CurrentSalary"] = generate_salary(job_level)
    
    activity_name = "Offer Extended"
    resource = select_resource(activity_name)
    duration = calculate_duration(activity_name, resource)
    current_time = add_business_hours(current_time, duration)
    performed_by = determine_responsible_party(activity_name)
    
    activities.append({
        **case_attrs,
        "ActivityName": activity_name,
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "PerformedBy": performed_by,
        "SystemUsed": determine_system_used(activity_name, performed_by)
    })
    
    # 10% reject offer
    if random.random() < 0.1:
        wait_days = random.randint(2, 7)
        current_time = add_business_hours(current_time, wait_days * 8)
        activity_name = "Offer Rejected"
        resource = select_resource(activity_name)
        performed_by = determine_responsible_party(activity_name)
        activities.append({
            **case_attrs,
            "ActivityName": activity_name,
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "PerformedBy": performed_by,
            "SystemUsed": determine_system_used(activity_name, performed_by),
            "RejectionReason": random.choice(["Better offer", "Location", "Role mismatch"])
        })
        return activities, None
    
    # Offer Accepted
    wait_days = random.randint(1, 5)
    current_time = add_business_hours(current_time, wait_days * 8)
    activity_name = "Offer Accepted"
    resource = select_resource(activity_name)
    duration = calculate_duration(activity_name, resource)
    current_time = add_business_hours(current_time, duration)
    performed_by = determine_responsible_party(activity_name)
    
    activities.append({
        **case_attrs,
        "ActivityName": activity_name,
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "PerformedBy": performed_by,
        "SystemUsed": determine_system_used(activity_name, performed_by)
    })
    
    return activities, (case_attrs, current_time)

def generate_onboarding_phase(case_attrs: Dict, start_time: datetime) -> Tuple[List[Dict], datetime]:
    """Generate comprehensive onboarding phase activities"""
    activities = []
    current_time = start_time
    
    # Wait for start date
    wait_days = random.randint(7, 21)
    current_time = add_business_hours(current_time, wait_days * 8)
    
    # Onboarding Started
    activity_name = "Onboarding Started"
    resource = select_resource(activity_name)
    duration = calculate_duration(activity_name, resource)
    current_time = add_business_hours(current_time, duration)
    performed_by = determine_responsible_party(activity_name)
    
    case_attrs["HireDate"] = current_time.strftime("%Y-%m-%d")
    
    activities.append({
        **case_attrs,
        "ActivityName": activity_name,
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "PerformedBy": performed_by,
        "SystemUsed": determine_system_used(activity_name, performed_by)
    })
    
    # Documents Submitted
    wait_hours = random.randint(1, 4)
    current_time = add_business_hours(current_time, wait_hours)
    activity_name = "Documents Submitted"
    resource = select_resource(activity_name)
    duration = calculate_duration(activity_name, resource)
    current_time = add_business_hours(current_time, duration)
    performed_by = determine_responsible_party(activity_name)
    
    activities.append({
        **case_attrs,
        "ActivityName": activity_name,
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "PerformedBy": performed_by,
        "SystemUsed": determine_system_used(activity_name, performed_by)
    })
    
    # Benefits Enrolled
    wait_days = random.randint(1, 3)
    current_time = add_business_hours(current_time, wait_days * 8)
    activity_name = "Benefits Enrolled"
    resource = select_resource(activity_name)
    duration = calculate_duration(activity_name, resource)
    current_time = add_business_hours(current_time, duration)
    performed_by = determine_responsible_party(activity_name)
    
    activities.append({
        **case_attrs,
        "ActivityName": activity_name,
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "PerformedBy": performed_by,
        "SystemUsed": determine_system_used(activity_name, performed_by)
    })
    
    # Equipment flow
    activity_name = "Equipment Requested"
    resource = select_resource(activity_name)
    duration = calculate_duration(activity_name, resource)
    current_time = add_business_hours(current_time, duration)
    performed_by = determine_responsible_party(activity_name)
    
    activities.append({
        **case_attrs,
        "ActivityName": activity_name,
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "PerformedBy": performed_by,
        "SystemUsed": determine_system_used(activity_name, performed_by)
    })
    
    wait_days = random.randint(1, 5)
    current_time = add_business_hours(current_time, wait_days * 8)
    activity_name = "Equipment Assigned"
    resource = select_resource(activity_name)
    duration = calculate_duration(activity_name, resource)
    current_time = add_business_hours(current_time, duration)
    performed_by = determine_responsible_party(activity_name)
    
    activities.append({
        **case_attrs,
        "ActivityName": activity_name,
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "PerformedBy": performed_by,
        "SystemUsed": determine_system_used(activity_name, performed_by)
    })
    
    # System Access
    activity_name = "System Access Granted"
    resource = select_resource(activity_name)
    duration = calculate_duration(activity_name, resource)
    current_time = add_business_hours(current_time, duration)
    performed_by = determine_responsible_party(activity_name)
    
    activities.append({
        **case_attrs,
        "ActivityName": activity_name,
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "PerformedBy": performed_by,
        "SystemUsed": determine_system_used(activity_name, performed_by)
    })
    
    # Orientation
    wait_days = random.randint(0, 2)
    current_time = add_business_hours(current_time, wait_days * 8)
    activity_name = "Orientation Completed"
    resource = select_resource(activity_name)
    duration = calculate_duration(activity_name, resource)
    current_time = add_business_hours(current_time, duration)
    performed_by = determine_responsible_party(activity_name)
    
    activities.append({
        **case_attrs,
        "ActivityName": activity_name,
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "PerformedBy": performed_by,
        "SystemUsed": determine_system_used(activity_name, performed_by)
    })
    
    # Manager Introduction
    activity_name = "Manager Introduction"
    resource = select_resource(activity_name)
    duration = calculate_duration(activity_name, resource)
    current_time = add_business_hours(current_time, duration)
    performed_by = determine_responsible_party(activity_name)
    
    activities.append({
        **case_attrs,
        "ActivityName": activity_name,
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "PerformedBy": performed_by,
        "SystemUsed": determine_system_used(activity_name, performed_by)
    })
    
    # 30-Day Check-in
    wait_days = 30
    current_time = add_business_hours(current_time, wait_days * 8)
    activity_name = "30-Day Check-in"
    resource = select_resource(activity_name)
    duration = calculate_duration(activity_name, resource)
    current_time = add_business_hours(current_time, duration)
    performed_by = determine_responsible_party(activity_name)
    
    activities.append({
        **case_attrs,
        "ActivityName": activity_name,
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "PerformedBy": performed_by,
        "SystemUsed": determine_system_used(activity_name, performed_by)
    })
    
    # 60-Day Check-in
    wait_days = 30
    current_time = add_business_hours(current_time, wait_days * 8)
    activity_name = "60-Day Check-in"
    resource = select_resource(activity_name)
    duration = calculate_duration(activity_name, resource)
    current_time = add_business_hours(current_time, duration)
    performed_by = determine_responsible_party(activity_name)
    
    activities.append({
        **case_attrs,
        "ActivityName": activity_name,
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "PerformedBy": performed_by,
        "SystemUsed": determine_system_used(activity_name, performed_by)
    })
    
    # Probation Completed
    wait_days = 30
    current_time = add_business_hours(current_time, wait_days * 8)
    activity_name = "Probation Completed"
    resource = select_resource(activity_name)
    duration = calculate_duration(activity_name, resource)
    current_time = add_business_hours(current_time, duration)
    performed_by = determine_responsible_party(activity_name)
    
    activities.append({
        **case_attrs,
        "ActivityName": activity_name,
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "PerformedBy": performed_by,
        "SystemUsed": determine_system_used(activity_name, performed_by)
    })
    
    # 5% fail probation
    if random.random() < 0.05:
        activity_name = "Probation Failed"
        resource = select_resource(activity_name)
        performed_by = determine_responsible_party(activity_name)
        activities.append({
            **case_attrs,
            "ActivityName": activity_name,
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "PerformedBy": performed_by,
            "SystemUsed": determine_system_used(activity_name, performed_by)
        })
        # Add exit activities
        exit_activities = generate_exit_phase(case_attrs, current_time, "Probation Failed")
        activities.extend(exit_activities)
        return activities, None
    
    return activities, current_time

def generate_employment_phase(case_attrs: Dict, start_time: datetime, end_date: datetime) -> Tuple[List[Dict], datetime]:
    """Generate employment phase activities"""
    activities = []
    current_time = start_time
    last_review_time = current_time
    
    # Employment activities loop
    while current_time < end_date:
        # Annual Performance Review
        if (current_time - last_review_time).days >= 365:
            activity_name = "Performance Review"
            resource = select_resource(activity_name)
            duration = calculate_duration(activity_name, resource)
            current_time = add_business_hours(current_time, duration)
            performed_by = determine_responsible_party(activity_name)
            
            # Update performance rating
            case_attrs["PerformanceRating"] = random.choice(["Exceeds", "Meets", "Below"])
            
            activities.append({
                **case_attrs,
                "ActivityName": activity_name,
                "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "Resource": resource,
                "PerformedBy": performed_by,
                "SystemUsed": determine_system_used(activity_name, performed_by)
            })
            
            last_review_time = current_time
            
            # Salary Review
            if case_attrs["PerformanceRating"] in ["Exceeds", "Meets"]:
                wait_days = random.randint(1, 5)
                current_time = add_business_hours(current_time, wait_days * 8)
                activity_name = "Salary Review"
                resource = select_resource(activity_name)
                duration = calculate_duration(activity_name, resource)
                current_time = add_business_hours(current_time, duration)
                performed_by = determine_responsible_party(activity_name)
                
                # Update salary
                if case_attrs["PerformanceRating"] == "Exceeds":
                    case_attrs["CurrentSalary"] = int(case_attrs["CurrentSalary"] * random.uniform(1.05, 1.15))
                else:
                    case_attrs["CurrentSalary"] = int(case_attrs["CurrentSalary"] * random.uniform(1.02, 1.05))
                
                activities.append({
                    **case_attrs,
                    "ActivityName": activity_name,
                    "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "Resource": resource,
                    "PerformedBy": performed_by,
                    "SystemUsed": determine_system_used(activity_name, performed_by)
                })
            
            # Possible Promotion
            if case_attrs["PerformanceRating"] == "Exceeds" and random.random() < 0.3:
                wait_days = random.randint(5, 15)
                current_time = add_business_hours(current_time, wait_days * 8)
                activity_name = "Promotion Approved"
                resource = select_resource(activity_name)
                duration = calculate_duration(activity_name, resource)
                current_time = add_business_hours(current_time, duration)
                performed_by = determine_responsible_party(activity_name)
                
                # Update job level
                case_attrs["JobLevel"] = min(10, case_attrs["JobLevel"] + 1)
                
                activities.append({
                    **case_attrs,
                    "ActivityName": activity_name,
                    "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "Resource": resource,
                    "PerformedBy": performed_by,
                    "SystemUsed": determine_system_used(activity_name, performed_by)
                })
        
        # Random Leave Requests (2-4 per year)
        if random.random() < 0.3:
            wait_days = random.randint(30, 90)
            current_time = add_business_hours(current_time, wait_days * 8)
            
            if current_time >= end_date:
                break
                
            activity_name = "Leave Requested"
            resource = select_resource(activity_name)
            duration = calculate_duration(activity_name, resource)
            current_time = add_business_hours(current_time, duration)
            performed_by = determine_responsible_party(activity_name)
            
            activities.append({
                **case_attrs,
                "ActivityName": activity_name,
                "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "Resource": resource,
                "PerformedBy": performed_by,
                "SystemUsed": determine_system_used(activity_name, performed_by),
                "LeaveType": random.choice(["Vacation", "Sick", "Personal", "Family"])
            })
            
            # Leave approval (95% approved)
            if random.random() < 0.95:
                wait_days = random.randint(1, 3)
                current_time = add_business_hours(current_time, wait_days * 8)
                activity_name = "Leave Approved"
                resource = select_resource(activity_name)
                duration = calculate_duration(activity_name, resource)
                current_time = add_business_hours(current_time, duration)
                performed_by = determine_responsible_party(activity_name)
                
                activities.append({
                    **case_attrs,
                    "ActivityName": activity_name,
                    "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "Resource": resource,
                    "PerformedBy": performed_by,
                    "SystemUsed": determine_system_used(activity_name, performed_by)
                })
        
        # Random Training (1-2 per year)
        if random.random() < 0.15:
            wait_days = random.randint(30, 60)
            current_time = add_business_hours(current_time, wait_days * 8)
            
            if current_time >= end_date:
                break
                
            activity_name = "Training Enrolled"
            resource = select_resource(activity_name)
            duration = calculate_duration(activity_name, resource)
            current_time = add_business_hours(current_time, duration)
            performed_by = determine_responsible_party(activity_name)
            
            activities.append({
                **case_attrs,
                "ActivityName": activity_name,
                "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "Resource": resource,
                "PerformedBy": performed_by,
                "SystemUsed": determine_system_used(activity_name, performed_by),
                "TrainingType": random.choice(["Technical", "Leadership", "Compliance", "Soft Skills"])
            })
            
            wait_days = random.randint(5, 30)
            current_time = add_business_hours(current_time, wait_days * 8)
            activity_name = "Training Completed"
            resource = select_resource(activity_name)
            duration = calculate_duration(activity_name, resource)
            current_time = add_business_hours(current_time, duration)
            performed_by = determine_responsible_party(activity_name)
            
            activities.append({
                **case_attrs,
                "ActivityName": activity_name,
                "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "Resource": resource,
                "PerformedBy": performed_by,
                "SystemUsed": determine_system_used(activity_name, performed_by)
            })
        
        # Move time forward
        current_time = add_business_hours(current_time, random.randint(30, 90) * 8)
        
        # Update tenure
        hire_date = datetime.strptime(case_attrs.get("HireDate", start_time.strftime("%Y-%m-%d")), "%Y-%m-%d")
        case_attrs["TenureYears"] = (current_time - hire_date).days / 365.25
        
        # Random exit chance (increases with tenure and poor performance)
        exit_probability = 0.05  # Base 5% per year
        if case_attrs.get("PerformanceRating") == "Below":
            exit_probability = 0.3
        elif case_attrs["TenureYears"] > 5:
            exit_probability = 0.1
        
        if random.random() < exit_probability:
            # Employee exits
            return activities, current_time
    
    return activities, current_time

def generate_exit_phase(case_attrs: Dict, start_time: datetime, exit_reason: str = "Resignation") -> List[Dict]:
    """Generate exit phase activities"""
    activities = []
    current_time = start_time
    
    # Determine exit type
    if exit_reason == "Resignation":
        # Resignation Submitted
        activity_name = "Resignation Submitted"
        resource = select_resource(activity_name)
        duration = calculate_duration(activity_name, resource)
        current_time = add_business_hours(current_time, duration)
        performed_by = determine_responsible_party(activity_name)
        
        activities.append({
            **case_attrs,
            "ActivityName": activity_name,
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "PerformedBy": performed_by,
            "SystemUsed": determine_system_used(activity_name, performed_by),
            "ExitReason": random.choice(["Better opportunity", "Relocation", "Career change", "Personal reasons"])
        })
    elif exit_reason in ["Probation Failed", "Termination"]:
        # Termination Initiated
        activity_name = "Termination Initiated"
        resource = select_resource(activity_name)
        duration = calculate_duration(activity_name, resource)
        current_time = add_business_hours(current_time, duration)
        performed_by = determine_responsible_party(activity_name)
        
        activities.append({
            **case_attrs,
            "ActivityName": activity_name,
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "PerformedBy": performed_by,
            "SystemUsed": determine_system_used(activity_name, performed_by),
            "ExitReason": exit_reason
        })
    
    # Exit Interview Scheduled
    wait_days = random.randint(1, 5)
    current_time = add_business_hours(current_time, wait_days * 8)
    activity_name = "Exit Interview Scheduled"
    resource = select_resource(activity_name)
    duration = calculate_duration(activity_name, resource)
    current_time = add_business_hours(current_time, duration)
    performed_by = determine_responsible_party(activity_name)
    
    activities.append({
        **case_attrs,
        "ActivityName": activity_name,
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "PerformedBy": performed_by,
        "SystemUsed": determine_system_used(activity_name, performed_by)
    })
    
    # Exit Interview Completed
    wait_days = random.randint(1, 3)
    current_time = add_business_hours(current_time, wait_days * 8)
    activity_name = "Exit Interview Completed"
    resource = select_resource(activity_name)
    duration = calculate_duration(activity_name, resource)
    current_time = add_business_hours(current_time, duration)
    performed_by = determine_responsible_party(activity_name)
    
    activities.append({
        **case_attrs,
        "ActivityName": activity_name,
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "PerformedBy": performed_by,
        "SystemUsed": determine_system_used(activity_name, performed_by)
    })
    
    # Equipment Returned
    activity_name = "Equipment Returned"
    resource = select_resource(activity_name)
    duration = calculate_duration(activity_name, resource)
    current_time = add_business_hours(current_time, duration)
    performed_by = determine_responsible_party(activity_name)
    
    activities.append({
        **case_attrs,
        "ActivityName": activity_name,
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "PerformedBy": performed_by,
        "SystemUsed": determine_system_used(activity_name, performed_by)
    })
    
    # System Access Revoked
    activity_name = "System Access Revoked"
    resource = select_resource(activity_name)
    duration = calculate_duration(activity_name, resource)
    current_time = add_business_hours(current_time, duration)
    performed_by = determine_responsible_party(activity_name)
    
    activities.append({
        **case_attrs,
        "ActivityName": activity_name,
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "PerformedBy": performed_by,
        "SystemUsed": determine_system_used(activity_name, performed_by)
    })
    
    # Final Paycheck Processed
    wait_days = random.randint(1, 5)
    current_time = add_business_hours(current_time, wait_days * 8)
    activity_name = "Final Paycheck Processed"
    resource = select_resource(activity_name)
    duration = calculate_duration(activity_name, resource)
    current_time = add_business_hours(current_time, duration)
    performed_by = determine_responsible_party(activity_name)
    
    activities.append({
        **case_attrs,
        "ActivityName": activity_name,
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "PerformedBy": performed_by,
        "SystemUsed": determine_system_used(activity_name, performed_by)
    })
    
    # Employment Ended
    activity_name = "Employment Ended"
    resource = select_resource(activity_name)
    duration = calculate_duration(activity_name, resource)
    current_time = add_business_hours(current_time, duration)
    performed_by = determine_responsible_party(activity_name)
    
    activities.append({
        **case_attrs,
        "ActivityName": activity_name,
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "PerformedBy": performed_by,
        "SystemUsed": determine_system_used(activity_name, performed_by)
    })
    
    return activities

def generate_complete_case(case_num: int) -> List[Dict]:
    """Generate a complete employee lifecycle case"""
    case_id = f"HR{START_DATE.year}_{case_num:05d}"
    employee_id = generate_employee_id()
    
    # Random start date within the period
    days_range = (END_DATE - START_DATE).days
    start_date = START_DATE + timedelta(days=random.randint(0, days_range))
    
    # Recruitment phase
    recruitment_activities, hire_result = generate_recruitment_phase(case_id, start_date, employee_id)
    
    if not hire_result:
        # Rejected during recruitment
        return recruitment_activities
    
    case_attrs, current_time = hire_result
    all_activities = recruitment_activities
    
    # Onboarding phase
    onboarding_activities, onboarding_end = generate_onboarding_phase(case_attrs, current_time)
    all_activities.extend(onboarding_activities)
    
    if not onboarding_end:
        # Failed probation
        return all_activities
    
    # Employment phase
    employment_activities, employment_end = generate_employment_phase(case_attrs, onboarding_end, END_DATE)
    all_activities.extend(employment_activities)
    
    # Exit phase (if employee leaves before end date)
    if employment_end and employment_end < END_DATE and random.random() < 0.2:  # 20% of hired employees exit
        exit_activities = generate_exit_phase(case_attrs, employment_end, "Resignation")
        all_activities.extend(exit_activities)
    
    return all_activities

def main():
    """Main function to generate the dataset"""
    print("Generating Hire to Retire dataset...")
    print(f"Total cases to generate: {TOTAL_CASES}")
    
    all_activities = []
    
    for i in range(TOTAL_CASES):
        if (i + 1) % 100 == 0:
            print(f"Generated {i + 1}/{TOTAL_CASES} cases...")
        
        case_activities = generate_complete_case(i + 1)
        all_activities.extend(case_activities)
    
    # Sort by timestamp
    all_activities.sort(key=lambda x: x['ActivityTime'])
    
    # Save as CSV
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, 'output')
    csv_filename = os.path.join(output_dir, 'hire_to_retire_historical.csv')
    os.makedirs(output_dir, exist_ok=True)
    
    if all_activities:
        # Collect all unique field names from all activities
        fieldnames = set()
        for activity in all_activities:
            fieldnames.update(activity.keys())
        fieldnames = sorted(list(fieldnames))  # Sort for consistent column order
        
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_activities)
        print(f"CSV saved to {csv_filename}")
    
    # Save as JSON (case-centric format)
    json_filename = os.path.join(output_dir, 'hire_to_retire_historical.json')
    cases = {}
    for activity in all_activities:
        case_id = activity['CaseId']
        if case_id not in cases:
            cases[case_id] = {
                'CaseId': case_id,
                'Activities': []
            }
        cases[case_id]['Activities'].append(activity)
    
    with open(json_filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(list(cases.values()), jsonfile, indent=2)
    print(f"JSON saved to {json_filename}")
    
    # Print statistics
    print(f"\nDataset Statistics:")
    print(f"Total activities: {len(all_activities)}")
    print(f"Total cases: {len(cases)}")
    
    # Count hired vs rejected
    hired_count = sum(1 for case in cases.values() 
                     if any(act['ActivityName'] == 'Offer Accepted' for act in case['Activities']))
    print(f"Hired employees: {hired_count}")
    print(f"Rejected applications: {len(cases) - hired_count}")
    
    # Count exits
    exit_count = sum(1 for case in cases.values() 
                    if any(act['ActivityName'] == 'Employment Ended' for act in case['Activities']))
    print(f"Exited employees: {exit_count}")

if __name__ == "__main__":
    main()