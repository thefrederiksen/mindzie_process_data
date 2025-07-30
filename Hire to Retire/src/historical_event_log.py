import random
random.seed(42)
import json
from datetime import datetime, timedelta
import os
import csv
from collections import Counter, defaultdict

# Constants
DEPARTMENTS = ["Sales", "Engineering", "HR", "Finance", "Operations", "Marketing"]
LOCATIONS = ["New York", "London", "Singapore", "Sydney", "Berlin"]
EMPLOYMENT_TYPES = ["Full-time", "Part-time", "Contract"]
EDUCATION_LEVELS = ["High School", "Bachelor's", "Master's", "PhD"]
RECRUITMENT_SOURCES = ["Internal", "External", "Referral", "Agency"]

# Time constants
BUSINESS_START = 9  # 9 AM
BUSINESS_END = 18   # 6 PM
WORKING_DAYS = [0, 1, 2, 3, 4]  # Monday to Friday

def load_activities(src_dir):
    with open(os.path.join(src_dir, 'activities.json'), 'r') as f:
        return json.load(f)

def is_business_hours(dt):
    """Check if datetime is during business hours"""
    return dt.weekday() in WORKING_DAYS and BUSINESS_START <= dt.hour < BUSINESS_END

def next_business_day(dt):
    """Get next business day"""
    dt = dt.replace(hour=BUSINESS_START, minute=0, second=0, microsecond=0)
    while dt.weekday() not in WORKING_DAYS:
        dt += timedelta(days=1)
    return dt

def add_business_time(start_dt, hours):
    """Add business hours to a datetime"""
    current_dt = start_dt
    remaining_hours = hours
    
    while remaining_hours > 0:
        if is_business_hours(current_dt):
            remaining_hours -= 1
        current_dt += timedelta(hours=1)
        
        # Skip to next business day if needed
        if current_dt.hour >= BUSINESS_END:
            current_dt = next_business_day(current_dt + timedelta(days=1))
    
    return current_dt

def random_employee_id(used_ids):
    """Generate unique employee ID"""
    while True:
        emp_id = f"E{random.randint(100000, 999999)}"
        if emp_id not in used_ids:
            used_ids.add(emp_id)
            return emp_id

def random_case_id(year, employee_id, case_type="HR"):
    """Generate case ID with year prefix"""
    return f"{case_type}{year}_{employee_id}"

def generate_employee_attributes():
    """Generate random employee attributes"""
    return {
        "Department": random.choice(DEPARTMENTS),
        "Location": random.choice(LOCATIONS),
        "JobLevel": random.randint(1, 10),
        "EmploymentType": random.choice(EMPLOYMENT_TYPES),
        "EducationLevel": random.choice(EDUCATION_LEVELS),
        "YearsExperience": random.randint(0, 40),
        "HiringManager": f"M{random.randint(100000, 999999)}",
        "RecruitmentSource": random.choice(RECRUITMENT_SOURCES),
        "CurrentSalary": random.randint(40000, 200000),
        "PerformanceRating": None,
        "TenureYears": 0
    }

def generate_recruitment_process(start_time, activities_def, employee_attrs):
    """Generate recruitment and onboarding activities"""
    events = []
    current_time = start_time
    requisition_id = f"REQ{random.randint(10000, 99999)}"
    
    # Job Requisition Created
    events.append({
        "ActivityName": "Job Requisition Created",
        "ActivityTime": current_time,
        "RequisitionID": requisition_id
    })
    current_time = add_business_time(current_time, random.randint(8, 24))  # 1-3 days
    
    # Job Posted
    events.append({
        "ActivityName": "Job Posted",
        "ActivityTime": current_time
    })
    current_time = add_business_time(current_time, random.randint(24, 72))  # 3-9 days
    
    # Applications (multiple)
    num_applications = random.randint(20, 80)
    applications = []
    
    for _ in range(num_applications):
        app_time = current_time + timedelta(days=random.randint(0, 14))
        applications.append({
            "ActivityName": "Application Received",
            "ActivityTime": app_time
        })
    
    # Process best candidate (simplified - in reality would track all)
    if applications:
        # Pick winning application
        winner = random.choice(applications)
        events.append(winner)
        current_time = winner["ActivityTime"]
        
        # Application Screened
        current_time = add_business_time(current_time, random.randint(8, 24))
        if random.random() < 0.4:  # 40% pass screening
            events.append({
                "ActivityName": "Application Screened",
                "ActivityTime": current_time
            })
            
            # Phone Interview
            current_time = add_business_time(current_time, random.randint(16, 40))
            events.append({
                "ActivityName": "Phone Interview Scheduled",
                "ActivityTime": current_time
            })
            
            current_time = add_business_time(current_time, random.randint(24, 80))
            if random.random() < 0.75:  # 75% pass phone interview
                events.append({
                    "ActivityName": "Phone Interview Completed",
                    "ActivityTime": current_time
                })
                
                # Technical Assessment (60% for technical roles)
                if employee_attrs["Department"] in ["Engineering", "Operations"] and random.random() < 0.6:
                    current_time = add_business_time(current_time, random.randint(8, 16))
                    events.append({
                        "ActivityName": "Technical Assessment Sent",
                        "ActivityTime": current_time
                    })
                    current_time = add_business_time(current_time, random.randint(24, 72))
                    events.append({
                        "ActivityName": "Technical Assessment Completed",
                        "ActivityTime": current_time
                    })
                
                # Onsite Interview
                current_time = add_business_time(current_time, random.randint(24, 80))
                events.append({
                    "ActivityName": "Onsite Interview Scheduled",
                    "ActivityTime": current_time
                })
                
                current_time = add_business_time(current_time, random.randint(40, 120))
                if random.random() < 0.5:  # 50% receive offers
                    events.append({
                        "ActivityName": "Onsite Interview Completed",
                        "ActivityTime": current_time
                    })
                    
                    # Reference Check
                    current_time = add_business_time(current_time, random.randint(8, 24))
                    events.append({
                        "ActivityName": "Reference Check Initiated",
                        "ActivityTime": current_time
                    })
                    
                    current_time = add_business_time(current_time, random.randint(24, 72))
                    events.append({
                        "ActivityName": "Reference Check Completed",
                        "ActivityTime": current_time
                    })
                    
                    # Offer
                    current_time = add_business_time(current_time, random.randint(8, 40))
                    events.append({
                        "ActivityName": "Offer Extended",
                        "ActivityTime": current_time
                    })
                    
                    current_time = add_business_time(current_time, random.randint(24, 120))
                    if random.random() < 0.85:  # 85% acceptance rate
                        events.append({
                            "ActivityName": "Offer Accepted",
                            "ActivityTime": current_time
                        })
                        return events, current_time, True
                    else:
                        events.append({
                            "ActivityName": "Offer Rejected",
                            "ActivityTime": current_time
                        })
    
    return events, current_time, False

def generate_onboarding_process(start_time, activities_def):
    """Generate onboarding activities"""
    events = []
    current_time = start_time
    
    # Wait for start date (2-4 weeks typically)
    current_time = add_business_time(current_time, random.randint(80, 160))
    
    # Onboarding Initiated
    events.append({
        "ActivityName": "Onboarding Initiated",
        "ActivityTime": current_time
    })
    
    # IT Equipment (1-3 days)
    current_time = add_business_time(current_time, random.randint(8, 24))
    events.append({
        "ActivityName": "IT Equipment Assigned",
        "ActivityTime": current_time
    })
    
    # Orientation (within first week)
    current_time = add_business_time(current_time, random.randint(8, 40))
    events.append({
        "ActivityName": "Orientation Completed",
        "ActivityTime": current_time
    })
    
    # Probation Period Started
    current_time = add_business_time(current_time, random.randint(1, 8))
    events.append({
        "ActivityName": "Probation Period Started",
        "ActivityTime": current_time
    })
    
    return events, current_time

def generate_employment_events(hire_date, exit_date, employee_attrs, activities_def):
    """Generate employment lifecycle events"""
    events = []
    
    # Calculate employment duration
    employment_months = (exit_date.year - hire_date.year) * 12 + (exit_date.month - hire_date.month)
    
    # Probation Review (after 90 days)
    probation_date = hire_date + timedelta(days=90)
    if probation_date < exit_date:
        events.append({
            "ActivityName": "Probation Review Completed",
            "ActivityTime": probation_date
        })
        
        # 90% pass probation
        if random.random() > 0.9:
            return events, probation_date, "probation_fail"
    
    # Annual Performance Reviews
    current_year = hire_date.year
    while True:
        review_date = datetime(current_year + 1, hire_date.month, 1)
        if review_date >= exit_date:
            break
            
        # Add some randomness to review date
        review_date = add_business_time(review_date, random.randint(-40, 40))
        
        events.append({
            "ActivityName": "Annual Performance Review",
            "ActivityTime": review_date
        })
        
        # Update performance rating
        employee_attrs["PerformanceRating"] = random.randint(2, 5)  # 2-5 rating
        
        # Possible outcomes from review
        if employee_attrs["PerformanceRating"] >= 4 and random.random() < 0.3:
            # Promotion
            promo_date = add_business_time(review_date, random.randint(40, 160))
            if promo_date < exit_date:
                events.append({
                    "ActivityName": "Promotion Processed",
                    "ActivityTime": promo_date
                })
                employee_attrs["JobLevel"] = min(10, employee_attrs["JobLevel"] + 1)
                employee_attrs["CurrentSalary"] = int(employee_attrs["CurrentSalary"] * 1.15)
        
        # Salary adjustment
        if random.random() < 0.7:
            salary_date = add_business_time(review_date, random.randint(8, 40))
            if salary_date < exit_date:
                events.append({
                    "ActivityName": "Salary Adjustment Processed",
                    "ActivityTime": salary_date
                })
                employee_attrs["CurrentSalary"] = int(employee_attrs["CurrentSalary"] * random.uniform(1.02, 1.08))
        
        current_year += 1
    
    # Transfers (10% annually)
    if employment_months > 12 and random.random() < (0.1 * employment_months / 12):
        transfer_date = hire_date + timedelta(days=random.randint(365, min(employment_months * 30, 3650)))
        if transfer_date < exit_date:
            events.append({
                "ActivityName": "Transfer Processed",
                "ActivityTime": transfer_date
            })
            employee_attrs["Department"] = random.choice([d for d in DEPARTMENTS if d != employee_attrs["Department"]])
    
    # Training events (2-3 per year)
    training_count = int(employment_months / 12 * random.uniform(2, 3))
    for _ in range(training_count):
        training_start = hire_date + timedelta(days=random.randint(90, min(employment_months * 30, 3650)))
        if training_start < exit_date:
            events.append({
                "ActivityName": "Training Enrolled",
                "ActivityTime": training_start
            })
            
            training_end = training_start + timedelta(days=random.randint(7, 30))
            if training_end < exit_date:
                events.append({
                    "ActivityName": "Training Completed",
                    "ActivityTime": training_end
                })
    
    # Leave requests (3-4 per year)
    leave_count = int(employment_months / 12 * random.uniform(3, 4))
    for _ in range(leave_count):
        leave_date = hire_date + timedelta(days=random.randint(30, min(employment_months * 30, 3650)))
        if leave_date < exit_date:
            events.append({
                "ActivityName": "Leave Requested",
                "ActivityTime": leave_date
            })
            
            approval_date = add_business_time(leave_date, random.randint(1, 8))
            if approval_date < exit_date:
                events.append({
                    "ActivityName": "Leave Approved",
                    "ActivityTime": approval_date
                })
    
    # Disciplinary actions (rare - 5% of employees)
    if random.random() < 0.05 and employment_months > 6:
        disciplinary_date = hire_date + timedelta(days=random.randint(180, min(employment_months * 30, 3650)))
        if disciplinary_date < exit_date:
            events.append({
                "ActivityName": "Disciplinary Action Taken",
                "ActivityTime": disciplinary_date
            })
    
    return events, exit_date, "normal"

def generate_exit_process(exit_date, exit_type, activities_def):
    """Generate exit process activities"""
    events = []
    current_time = exit_date - timedelta(days=random.randint(14, 60))  # Notice period
    
    # Exit Process Initiated
    events.append({
        "ActivityName": "Exit Process Initiated",
        "ActivityTime": current_time
    })
    
    # Exit Interview (80% of voluntary exits)
    if exit_type in ["resignation", "retirement"] and random.random() < 0.8:
        interview_date = exit_date - timedelta(days=random.randint(3, 10))
        events.append({
            "ActivityName": "Exit Interview Conducted",
            "ActivityTime": interview_date
        })
    
    # Final Settlement
    settlement_date = exit_date + timedelta(days=random.randint(5, 15))
    events.append({
        "ActivityName": "Final Settlement Processed",
        "ActivityTime": settlement_date
    })
    
    # Employment Ended
    events.append({
        "ActivityName": "Employment Ended",
        "ActivityTime": settlement_date
    })
    
    return events

def generate_employee_lifecycle(start_date, end_date, activities_def, used_employee_ids):
    """Generate complete employee lifecycle"""
    all_events = []
    employee_id = random_employee_id(used_employee_ids)
    employee_attrs = generate_employee_attributes()
    
    # Determine hire date (within the timeframe)
    hire_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days - 365))
    year = hire_date.year
    case_id = random_case_id(year, employee_id)
    
    # Generate recruitment process
    recruitment_events, offer_accepted_time, hired = generate_recruitment_process(
        hire_date - timedelta(days=random.randint(30, 90)), 
        activities_def, 
        employee_attrs
    )
    
    # Add recruitment events even if not hired
    for event in recruitment_events:
        event_data = {
            "CaseId": case_id,
            "EmployeeID": employee_id,
            **event,
            **employee_attrs,
            "HireDate": None,  # Not hired yet
            "TenureYears": 0
        }
        # Add activity-specific attributes
        activity_info = activities_def["activities"].get(event["ActivityName"], {})
        event_data["PerformedBy"] = activity_info.get("performed_by", "Unknown")
        event_data["SystemUsed"] = activity_info.get("system", "Unknown")
        all_events.append(event_data)
    
    if not hired:
        # Application rejected at some stage - still return the events
        return all_events
    
    # Generate onboarding
    onboarding_events, onboarding_complete = generate_onboarding_process(
        offer_accepted_time,
        activities_def
    )
    
    actual_hire_date = onboarding_events[0]["ActivityTime"]
    hire_date_str = actual_hire_date.strftime("%Y-%m-%d")
    employee_attrs["HireDate"] = hire_date_str
    
    # Update hire date for all previously added events
    for event in all_events:
        event["HireDate"] = hire_date_str
    
    for event in onboarding_events:
        event_data = {
            "CaseId": case_id,
            "EmployeeID": employee_id,
            **event,
            **employee_attrs
        }
        activity_info = activities_def["activities"].get(event["ActivityName"], {})
        event_data["PerformedBy"] = activity_info.get("performed_by", "Unknown")
        event_data["SystemUsed"] = activity_info.get("system", "Unknown")
        all_events.append(event_data)
    
    # Determine exit date and type
    tenure_days = random.randint(30, 3650)  # 1 month to 10 years
    exit_date = actual_hire_date + timedelta(days=tenure_days)
    
    if exit_date > end_date:
        # Employee still active at end of historical period
        exit_date = end_date
        exit_type = "active"
    else:
        # Determine exit type
        exit_rand = random.random()
        if exit_rand < 0.6:
            exit_type = "resignation"
        elif exit_rand < 0.8:
            exit_type = "retirement"
        elif exit_rand < 0.95:
            exit_type = "termination"
        else:
            exit_type = "contract_end"
    
    # Generate employment events
    employment_events, _, exit_reason = generate_employment_events(
        actual_hire_date,
        exit_date,
        employee_attrs,
        activities_def
    )
    
    # Update tenure
    for event in employment_events:
        event_time = event["ActivityTime"]
        tenure_years = (event_time - actual_hire_date).days / 365.25
        event_data = {
            "CaseId": case_id,
            "EmployeeID": employee_id,
            **event,
            **employee_attrs,
            "TenureYears": round(tenure_years, 2)
        }
        activity_info = activities_def["activities"].get(event["ActivityName"], {})
        event_data["PerformedBy"] = activity_info.get("performed_by", "Unknown")
        event_data["SystemUsed"] = activity_info.get("system", "Unknown")
        all_events.append(event_data)
    
    # Generate exit process if not still active
    if exit_type != "active":
        exit_events = generate_exit_process(exit_date, exit_type, activities_def)
        
        for event in exit_events:
            event_time = event["ActivityTime"]
            tenure_years = (event_time - actual_hire_date).days / 365.25
            event_data = {
                "CaseId": case_id,
                "EmployeeID": employee_id,
                **event,
                **employee_attrs,
                "TenureYears": round(tenure_years, 2)
            }
            activity_info = activities_def["activities"].get(event["ActivityName"], {})
            event_data["PerformedBy"] = activity_info.get("performed_by", "Unknown")
            event_data["SystemUsed"] = activity_info.get("system", "Unknown")
            all_events.append(event_data)
    
    # Sort events by time
    all_events.sort(key=lambda x: x["ActivityTime"])
    
    return all_events

def format_event_for_output(event):
    """Format event for JSON/CSV output"""
    formatted = {
        "CaseId": event["CaseId"],
        "ActivityName": event["ActivityName"],
        "ActivityTime": event["ActivityTime"].strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
        "EmployeeID": event["EmployeeID"],
        "Department": event["Department"],
        "Location": event["Location"],
        "JobLevel": event["JobLevel"],
        "EmploymentType": event["EmploymentType"],
        "HiringManager": event["HiringManager"],
        "RecruitmentSource": event["RecruitmentSource"],
        "CurrentSalary": event["CurrentSalary"],
        "PerformanceRating": event["PerformanceRating"],
        "TenureYears": event.get("TenureYears", 0),
        "PerformedBy": event["PerformedBy"],
        "SystemUsed": event["SystemUsed"],
        "HireDate": event.get("HireDate", "")
    }
    return formatted

def main():
    # Get the directory of the current script
    src_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Load activities
    activities_def = load_activities(src_dir)
    
    # Define time range for historical data (2 years)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)  # 2 years
    
    print("Generating Hire to Retire historical event log...")
    print(f"Time range: {start_date.date()} to {end_date.date()}")
    
    # Generate employee lifecycles
    all_events = []
    num_employees = 3000  # Generate 3000 employee lifecycles
    used_employee_ids = set()
    
    for i in range(num_employees):
        if i % 100 == 0:
            print(f"Generated {i}/{num_employees} employee lifecycles...")
        
        employee_events = generate_employee_lifecycle(start_date, end_date, activities_def, used_employee_ids)
        all_events.extend(employee_events)
    
    # Sort all events by time
    all_events.sort(key=lambda x: x["ActivityTime"])
    
    # Format events for output
    formatted_events = [format_event_for_output(event) for event in all_events]
    
    # Create output directory if it doesn't exist
    output_dir = os.path.join(src_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Write JSON output
    json_path = os.path.join(output_dir, "hire_to_retire_year_to_date.json")
    with open(json_path, 'w') as f:
        json.dump(formatted_events, f, indent=2)
    
    # Write CSV output
    csv_path = os.path.join(output_dir, "hire_to_retire_year_to_date.csv")
    if formatted_events:
        with open(csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=formatted_events[0].keys())
            writer.writeheader()
            writer.writerows(formatted_events)
    
    # Generate statistics
    print("\n=== Event Log Statistics ===")
    print(f"Total events generated: {len(formatted_events)}")
    print(f"Total employees: {len(set(e['EmployeeID'] for e in formatted_events))}")
    print(f"Total cases: {len(set(e['CaseId'] for e in formatted_events))}")
    
    # Activity frequency
    activity_counts = Counter(e['ActivityName'] for e in formatted_events)
    print("\nActivity Frequency:")
    for activity, count in sorted(activity_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {activity}: {count}")
    
    # Department distribution
    dept_counts = Counter(e['Department'] for e in formatted_events)
    print("\nDepartment Distribution:")
    for dept, count in sorted(dept_counts.items()):
        unique_employees = len(set(e['EmployeeID'] for e in formatted_events if e['Department'] == dept))
        print(f"  {dept}: {unique_employees} employees")
    
    # Performance by organization
    org_counts = Counter(e['PerformedBy'] for e in formatted_events)
    print("\nActivities by Organization:")
    for org, count in sorted(org_counts.items()):
        print(f"  {org}: {count} activities")
    
    print(f"\nFiles created:")
    print(f"  JSON: {json_path}")
    print(f"  CSV: {csv_path}")

if __name__ == "__main__":
    main()