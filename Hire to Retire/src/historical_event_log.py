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
    """Generate random employee attributes with occasional data quality issues"""
    attrs = {
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
    
    # Data quality issues (10% have missing critical fields)
    if random.random() < 0.1:
        missing_field = random.choice(["Department", "Location", "HiringManager"])
        attrs[missing_field] = None
    
    return attrs

def generate_recruitment_process(start_time, activities_def, employee_attrs, end_date):
    """Generate recruitment activities with simplified 15-activity model"""
    events = []
    current_time = start_time
    requisition_id = f"REQ{random.randint(10000, 99999)}"
    
    # Check if this is a recent application (within last 2 months of dataset)
    days_from_end = (end_date - start_time).days
    is_recent = days_from_end < 60
    
    # Job Posted
    events.append({
        "ActivityName": "Job Posted",
        "ActivityTime": current_time,
        "RequisitionID": requisition_id
    })
    
    # Extended time-to-fill problem (15% take 90+ days)
    if random.random() < 0.15:
        current_time = add_business_time(current_time, random.randint(720, 1440))  # 90-180 days
    # Ghost jobs (8% never progress beyond posting)
    elif random.random() < 0.08:
        current_time = add_business_time(current_time, random.randint(960, 1920))  # 120-240 days
        # These will be filtered out as "too recent" eventually
    else:
        current_time = add_business_time(current_time, random.randint(24, 240))  # 3-30 days
    
    # Application Received
    events.append({
        "ActivityName": "Application Received",
        "ActivityTime": current_time
    })
    
    # Application Screening (internal process, not tracked as separate activity)
    current_time = add_business_time(current_time, random.randint(8, 24))  # 1-3 days
    
    # Check if recent and still pending screening
    if is_recent and random.random() < 0.15:  # 15% of recent applications still pending
        return events, current_time, False
    
    # 15% pass screening (more realistic)
    if random.random() >= 0.15:
        # Application rejected
        current_time = add_business_time(current_time, random.randint(1, 4))
        events.append({
            "ActivityName": "Application Rejected",
            "ActivityTime": current_time
        })
        return events, current_time, False
    
    # Interview Completed (combines phone and onsite interviews)
    # Interview scheduling delays (20% experience 2+ weeks delay)
    if random.random() < 0.2:
        current_time = add_business_time(current_time, random.randint(160, 320))  # 20-40 days
    else:
        current_time = add_business_time(current_time, random.randint(40, 160))  # 5-20 days
    
    # Check if recent and still pending interview
    if is_recent and random.random() < 0.1:
        return events, current_time, False
    
    events.append({
        "ActivityName": "Interview Completed",
        "ActivityTime": current_time
    })
    
    # 40% of interviewed candidates receive offers (balanced for demo)
    if random.random() >= 0.4:
        current_time = add_business_time(current_time, random.randint(8, 24))
        events.append({
            "ActivityName": "Interview Failed",
            "ActivityTime": current_time
        })
        return events, current_time, False
    
    # Offer Extended
    # Offer delays (20% take 2+ weeks after interview)
    if random.random() < 0.2:
        current_time = add_business_time(current_time, random.randint(160, 320))  # 20-40 days
    else:
        current_time = add_business_time(current_time, random.randint(24, 80))  # 3-10 days
    
    events.append({
        "ActivityName": "Offer Extended",
        "ActivityTime": current_time
    })
    
    # Offer Response
    current_time = add_business_time(current_time, random.randint(24, 120))  # 3-15 days
    
    # Check if recent and still pending offer response
    if is_recent and random.random() < 0.05:
        return events, current_time, False
    
    # 85% accept offer
    if random.random() < 0.85:
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
    
    # Onboarding Started
    events.append({
        "ActivityName": "Onboarding Started",
        "ActivityTime": current_time
    })
    
    # Equipment Assigned (within first 3 days)
    # Equipment not ready problem (15% don't have equipment on day 1)
    if random.random() < 0.15:
        current_time = add_business_time(current_time, random.randint(40, 120))  # 5-15 days delay
    else:
        current_time = add_business_time(current_time, random.randint(8, 24))
    events.append({
        "ActivityName": "Equipment Assigned",
        "ActivityTime": current_time
    })
    
    return events, current_time

def generate_employment_events(hire_date, exit_date, employee_attrs, activities_def):
    """Generate employment lifecycle events"""
    events = []
    
    # Calculate employment duration
    employment_months = (exit_date.year - hire_date.year) * 12 + (exit_date.month - hire_date.month)
    
    # Probation Completed (after 90 days)
    probation_date = hire_date + timedelta(days=90)
    if probation_date < exit_date:
        events.append({
            "ActivityName": "Probation Completed",
            "ActivityTime": probation_date
        })
        
        # 90% pass probation
        if random.random() > 0.9:
            # Probation failed
            fail_date = probation_date + timedelta(days=random.randint(1, 7))
            events.append({
                "ActivityName": "Probation Failed",
                "ActivityTime": fail_date
            })
            return events, fail_date, "probation_fail"
    
    # Performance Reviews (annual)
    current_year = hire_date.year
    while True:
        review_date = datetime(current_year + 1, hire_date.month, 1)
        if review_date >= exit_date:
            break
            
        # Add some randomness to review date
        review_date = add_business_time(review_date, random.randint(-40, 40))
        
        # Missing reviews (10% never happen)
        if random.random() < 0.1:
            current_year += 1
            continue
            
        # Delayed performance reviews (35% happen 30+ days late)
        if random.random() < 0.35:
            review_date = add_business_time(review_date, random.randint(240, 480))  # 30-60 days late
        
        events.append({
            "ActivityName": "Performance Review",
            "ActivityTime": review_date
        })
        
        # Update performance rating
        employee_attrs["PerformanceRating"] = random.randint(2, 5)  # 2-5 rating
        
        # Possible promotion after review (15% annually)
        if employee_attrs["PerformanceRating"] >= 4 and random.random() < 0.15:
            promo_date = add_business_time(review_date, random.randint(40, 160))
            
            # Promotion processing delays (30% take 2+ months)
            if random.random() < 0.3:
                promo_date = add_business_time(promo_date, random.randint(320, 640))  # 40-80 days extra
                
            if promo_date < exit_date:
                events.append({
                    "ActivityName": "Promotion Approved",
                    "ActivityTime": promo_date
                })
                employee_attrs["JobLevel"] = min(10, employee_attrs["JobLevel"] + 1)
                employee_attrs["CurrentSalary"] = int(employee_attrs["CurrentSalary"] * 1.15)
        
        current_year += 1
    
    # Training events (2-3 per year with 25% incompletion rate)
    training_count = int(employment_months / 12 * random.uniform(2, 3))
    for _ in range(training_count):
        training_date = hire_date + timedelta(days=random.randint(90, min(employment_months * 30, 3650)))
        if training_date < exit_date:
            # 25% of training is not completed (enrolled but not finished)
            if random.random() > 0.25:
                events.append({
                    "ActivityName": "Training Completed",
                    "ActivityTime": training_date
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
            
            # Leave approval delays (15% take 3+ days)
            if random.random() < 0.15:
                approval_date = add_business_time(leave_date, random.randint(24, 72))  # 3-9 days
            else:
                approval_date = add_business_time(leave_date, random.randint(1, 8))
                
            if approval_date < exit_date:
                events.append({
                    "ActivityName": "Leave Approved",
                    "ActivityTime": approval_date
                })
    
    return events, exit_date, "normal"

def generate_exit_process(exit_date, exit_type, activities_def):
    """Generate exit process activities"""
    events = []
    
    # For voluntary exits, add resignation
    if exit_type == "resignation":
        # Sudden resignations (15% give less than required notice)
        if random.random() < 0.15:
            resignation_date = exit_date - timedelta(days=random.randint(1, 7))  # 1-7 days notice only
        else:
            resignation_date = exit_date - timedelta(days=random.randint(14, 30))  # 2-4 weeks notice
        events.append({
            "ActivityName": "Resignation Submitted",
            "ActivityTime": resignation_date
        })
    
    # Employment Ended
    events.append({
        "ActivityName": "Employment Ended",
        "ActivityTime": exit_date
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
        employee_attrs,
        end_date
    )
    
    # Add recruitment events
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
        # Determine exit type (80% voluntary resignation)
        if random.random() < 0.8:
            exit_type = "resignation"
        else:
            exit_type = "termination"
    
    # Generate employment events
    employment_events, _, exit_reason = generate_employment_events(
        actual_hire_date,
        exit_date,
        employee_attrs,
        activities_def
    )
    
    # Handle probation failures
    if exit_reason == "probation_fail":
        exit_type = "probation_fail"
        # Find the probation failed event to get the correct exit date
        for event in employment_events:
            if event["ActivityName"] == "Probation Failed":
                exit_date = event["ActivityTime"]
                break
    
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
    
    # Generate exit process if not still active and not probation fail
    if exit_type != "active" and exit_type != "probation_fail":
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
    num_employees = 5000  # Generate 5000 employee lifecycles for better problem distribution
    used_employee_ids = set()
    
    for i in range(num_employees):
        if i % 100 == 0:
            print(f"Generated {i}/{num_employees} employee lifecycles...")
        
        employee_events = generate_employee_lifecycle(start_date, end_date, activities_def, used_employee_ids)
        all_events.extend(employee_events)
    
    # Sort all events by time
    all_events.sort(key=lambda x: x["ActivityTime"])
    
    # Group events by CaseId for nested JSON structure
    cases_dict = defaultdict(list)
    for event in all_events:
        cases_dict[event["CaseId"]].append(event)
    
    # Create case-centric JSON structure
    cases_json = {"cases": []}
    for case_id, events in sorted(cases_dict.items()):
        if not events:
            continue
            
        # Get case-level attributes from first event
        first_event = events[0]
        case_data = {
            "CaseId": case_id,
            "EmployeeID": first_event["EmployeeID"],
            "activities": []
        }
        
        # Add case-level attributes (constant across all activities)
        case_attributes = [
            "Department", "Location", "JobLevel", "EmploymentType",
            "HiringManager", "RecruitmentSource", "CurrentSalary",
            "PerformanceRating", "HireDate"
        ]
        
        for attr in case_attributes:
            if attr in first_event:
                case_data[attr] = first_event[attr]
        
        # Add activities with activity-specific attributes
        for event in events:
            activity = {
                "ActivityName": event["ActivityName"],
                "ActivityTime": event["ActivityTime"].strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
                "PerformedBy": event["PerformedBy"],
                "SystemUsed": event["SystemUsed"]
            }
            
            # Add tenure years which changes per activity
            if "TenureYears" in event:
                activity["TenureYears"] = event["TenureYears"]
                
            # Update case-level attributes that may have changed
            if event.get("CurrentSalary") != case_data.get("CurrentSalary"):
                case_data["CurrentSalary"] = event["CurrentSalary"]
            if event.get("PerformanceRating") != case_data.get("PerformanceRating"):
                case_data["PerformanceRating"] = event["PerformanceRating"]
            if event.get("Department") != case_data.get("Department"):
                case_data["Department"] = event["Department"]
            if event.get("JobLevel") != case_data.get("JobLevel"):
                case_data["JobLevel"] = event["JobLevel"]
                
            case_data["activities"].append(activity)
        
        cases_json["cases"].append(case_data)
    
    # Create output directory if it doesn't exist
    output_dir = os.path.join(src_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Write nested JSON output
    json_path = os.path.join(output_dir, "hire_to_retire_year_to_date.json")
    with open(json_path, 'w') as f:
        json.dump(cases_json, f, indent=2)
    
    # Generate CSV from the JSON structure
    csv_rows = []
    for case in cases_json["cases"]:
        case_attrs = {k: v for k, v in case.items() if k not in ["activities", "CaseId", "EmployeeID"]}
        for activity in case["activities"]:
            row = {
                "CaseId": case["CaseId"],
                "EmployeeID": case["EmployeeID"],
                "ActivityName": activity["ActivityName"],
                "ActivityTime": activity["ActivityTime"],
                "PerformedBy": activity["PerformedBy"],
                "SystemUsed": activity["SystemUsed"]
            }
            # Add case-level attributes
            row.update(case_attrs)
            # Add activity-specific attributes
            if "TenureYears" in activity:
                row["TenureYears"] = activity["TenureYears"]
            csv_rows.append(row)
    
    # Write CSV output
    csv_path = os.path.join(output_dir, "hire_to_retire_year_to_date.csv")
    if csv_rows:
        fieldnames = [
            "CaseId", "ActivityName", "ActivityTime", "EmployeeID",
            "Department", "Location", "JobLevel", "EmploymentType",
            "HiringManager", "RecruitmentSource", "CurrentSalary",
            "PerformanceRating", "TenureYears", "PerformedBy", 
            "SystemUsed", "HireDate"
        ]
        with open(csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_rows)
    
    # Generate statistics
    print("\n=== Event Log Statistics ===")
    print(f"Total events generated: {len(all_events)}")
    print(f"Total cases: {len(cases_json['cases'])}")
    print(f"Total employees: {len(set(case['EmployeeID'] for case in cases_json['cases']))}")
    
    # Count case outcomes
    hired_count = 0
    rejected_count = 0
    open_count = 0
    active_employees = 0
    exited_employees = 0
    
    for case in cases_json['cases']:
        activities = [a['ActivityName'] for a in case['activities']]
        
        if 'Onboarding Started' in activities:
            hired_count += 1
            if 'Employment Ended' in activities:
                exited_employees += 1
            else:
                active_employees += 1
        elif any(activity in activities for activity in [
            'Application Rejected', 'Interview Failed', 'Offer Rejected'
        ]):
            rejected_count += 1
        else:
            open_count += 1
    
    print(f"\nCase Outcomes:")
    print(f"  Hired: {hired_count}")
    print(f"    - Active employees: {active_employees}")
    print(f"    - Exited employees: {exited_employees}")
    print(f"  Rejected: {rejected_count}")
    print(f"  Open/In Progress: {open_count}")
    
    # Activity frequency
    activity_counts = Counter()
    for case in cases_json['cases']:
        for activity in case['activities']:
            activity_counts[activity['ActivityName']] += 1
    
    print("\nActivity Frequency:")
    for activity, count in sorted(activity_counts.items(), key=lambda x: x[1], reverse=True)[:20]:
        print(f"  {activity}: {count}")
    
    # Department distribution
    dept_counts = Counter(case.get('Department', 'Unknown') for case in cases_json['cases'])
    print("\nDepartment Distribution:")
    for dept, count in sorted(dept_counts.items(), key=lambda x: (x[0] is None, x[0])):
        if dept is None:
            print(f"  [Missing]: {count} employees")
        else:
            print(f"  {dept}: {count} employees")
    
    # Performance by organization
    org_counts = Counter()
    for case in cases_json['cases']:
        for activity in case['activities']:
            org_counts[activity['PerformedBy']] += 1
    
    print("\nActivities by Organization:")
    for org, count in sorted(org_counts.items()):
        print(f"  {org}: {count} activities")
    
    print(f"\nFiles created:")
    print(f"  JSON: {json_path}")
    print(f"  CSV: {csv_path}")

if __name__ == "__main__":
    main()