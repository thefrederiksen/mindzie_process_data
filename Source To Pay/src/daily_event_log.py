#!/usr/bin/env python3
"""
Source to Pay Process Mining Dataset Generator - Daily Event Log
Generates current state data with mix of completed and in-progress cases for real-time monitoring
"""

import json
import csv
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
import os

# Set random seed for reproducibility
random.seed(42)

# Configuration for daily snapshot
FREEZE_TIME = datetime(2025, 5, 4, 14, 0, 0)  # 2:00 PM snapshot time
BUSINESS_START_HOUR = 8
BUSINESS_END_HOUR = 18

# Daily case distribution
COMPLETED_CASES_TODAY = 70  # Completed today
IN_PROGRESS_CASES = {
    "Waiting for Order Processing": (15, 20),
    "Waiting for Vendor Selection": (10, 15), 
    "Waiting for Invoice Processing": (20, 30),
    "Waiting for Payment Processing": (15, 25),
    "Waiting for Dispute Resolution": (5, 10)
}

# Import the same resources and performance factors from historical generator
RESOURCES = {
    "requester": ["John Smith", "Maria Garcia", "David Chen", "Sarah Wilson", "Ahmed Al-Rashid", "Lisa Johnson", "Tom Anderson", "Priya Patel"],
    "buyer": ["Michael Brown", "Jennifer Lee", "Robert Taylor", "Emily Davis", "Carlos Rodriguez", "Anna Schmidt"],
    "ap_clerk": ["Susan Clark", "James White", "Michelle Kim", "Paul Martinez"],
    "approver": ["Director Johnson", "Manager Williams", "VP Chen", "CFO Anderson"],
    "finance": ["Finance Manager", "Treasury Specialist", "Controller"],
    "vendor": ["Vendor System", "Vendor Portal", "Manual Vendor Process"],
    "system": ["ERP System", "Payment Gateway", "Invoice System"]
}

PERFORMANCE_FACTORS = {
    "Robert Taylor": 0.4,      # 60% slower buyer
    "Paul Martinez": 0.3,      # 70% slower AP clerk
    "Manual Vendor Process": 0.2,  # 80% slower vendor processing
    "ERP System": 1.5,         # 50% faster (automated)
    "Payment Gateway": 2.0,    # 100% faster (automated)
    "Invoice System": 1.8      # 80% faster (automated)
}

# Stage thresholds in business hours
STAGE_THRESHOLDS = {
    "Waiting for Order Processing": {"medium": 4, "high": 8},
    "Waiting for Vendor Selection": {"medium": 8, "high": 24},
    "Waiting for Order Approval": {"medium": 4, "high": 16},
    "Waiting for Invoice Receipt": {"medium": 48, "high": 120},
    "Waiting for Invoice Matching": {"medium": 8, "high": 24},
    "Waiting for Payment Approval": {"medium": 8, "high": 24},
    "Waiting for Payment Processing": {"medium": 4, "high": 16},
    "Waiting for Vendor Confirmation": {"medium": 24, "high": 72},
    "Waiting for Credit Check": {"medium": 2, "high": 8},
    "Waiting for Budget Verification": {"medium": 4, "high": 16},
    "Waiting for Three-Way Match": {"medium": 8, "high": 24},
    "Waiting for Dispute Resolution": {"medium": 48, "high": 120}
}

# Master data - same as historical generator
ORDER_TYPES = ["Standard", "Express", "Blanket", "Contract"]
ORDER_TYPE_DISTRIBUTION = [0.70, 0.15, 0.10, 0.05]

CURRENCIES = ["USD", "EUR", "GBP", "CAD", "JPY"]
CURRENCY_DISTRIBUTION = [0.60, 0.20, 0.10, 0.06, 0.04]

PRIORITIES = ["Low", "Medium", "High", "Critical"]
PRIORITY_DISTRIBUTION = [0.30, 0.50, 0.15, 0.05]

PAYMENT_TERMS = ["Net30", "Net60", "Net15", "Immediate", "Net90"]
PAYMENT_TERMS_DISTRIBUTION = [0.50, 0.20, 0.15, 0.10, 0.05]

VENDOR_CATEGORIES = ["Equipment", "Services", "Materials", "Software", "Maintenance"]
VENDOR_CATEGORY_DISTRIBUTION = [0.25, 0.30, 0.20, 0.15, 0.10]

DEPARTMENTS = ["Operations", "IT", "HR", "Finance", "Marketing", "Engineering", "Facilities", "Sales"]
DEPARTMENT_DISTRIBUTION = [0.20, 0.15, 0.10, 0.10, 0.08, 0.12, 0.15, 0.10]

PAYMENT_METHODS = ["Bank Transfer", "Credit Card", "Check", "Cash"]
PAYMENT_METHOD_DISTRIBUTION = [0.60, 0.25, 0.14, 0.01]

ORDER_VALUE_RANGES = [
    (10, 999, 0.30),      # Under $1,000: 30%
    (1000, 9999, 0.40),   # $1,000-$10,000: 40%
    (10000, 99999, 0.25), # $10,000-$100,000: 25%
    (100000, 1000000, 0.05)  # Over $100,000: 5%
]

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
            if current.hour >= BUSINESS_END_HOUR or current.weekday() >= 5:
                if current.weekday() >= 5:
                    days_to_monday = 7 - current.weekday()
                    current += timedelta(days=days_to_monday)
                else:
                    current += timedelta(days=1)
                current = current.replace(hour=BUSINESS_START_HOUR, minute=0, second=0)
            else:
                current = current.replace(hour=BUSINESS_START_HOUR, minute=0, second=0)
    
    return current

def select_resource(resource_type: str, activity_name: str = "") -> str:
    """Select resource based on activity type with realistic bottlenecks"""
    base_resources = RESOURCES.get(resource_type, ["Unknown"])
    
    if resource_type == "buyer":
        if "Review" in activity_name or random.random() < 0.4:
            return "Robert Taylor"
        return random.choice(["Michael Brown", "Jennifer Lee", "Emily Davis", "Carlos Rodriguez", "Anna Schmidt"])
    
    elif resource_type == "ap_clerk":
        if random.random() < 0.3:
            return "Paul Martinez"
        return random.choice(["Susan Clark", "James White", "Michelle Kim"])
    
    elif resource_type == "vendor":
        if random.random() < 0.2:
            return "Manual Vendor Process"
        return random.choice(["Vendor System", "Vendor Portal"])
    
    return random.choice(base_resources)

def generate_case_attributes() -> Dict[str, Any]:
    """Generate case-level attributes"""
    # Generate order value based on distribution
    order_value_range = random.choices(
        ORDER_VALUE_RANGES,
        weights=[r[2] for r in ORDER_VALUE_RANGES]
    )[0]
    order_value = round(random.uniform(order_value_range[0], order_value_range[1]), 2)
    
    # Generate vendor info
    vendor_id = f"V{random.randint(1000, 9999)}"
    vendor_names = [
        "Acme Supplies Inc", "Global Tech Solutions", "Premier Equipment Ltd",
        "Industrial Materials Co", "Office Depot Pro", "TechStart Solutions",
        "Maintenance Masters", "Software Innovators", "Equipment Express",
        "Service Specialists", "Material World Inc", "Digital Solutions Ltd"
    ]
    
    invoice_number = f"INV-{random.randint(100000, 999999)}"
    
    return {
        "CaseId": f"PO{random.randint(100000, 999999)}",
        "OrderType": random.choices(ORDER_TYPES, weights=ORDER_TYPE_DISTRIBUTION)[0],
        "OrderValue": order_value,
        "Currency": random.choices(CURRENCIES, weights=CURRENCY_DISTRIBUTION)[0],
        "Priority": random.choices(PRIORITIES, weights=PRIORITY_DISTRIBUTION)[0],
        "PaymentTerms": random.choices(PAYMENT_TERMS, weights=PAYMENT_TERMS_DISTRIBUTION)[0],
        "VendorID": vendor_id,
        "VendorName": random.choice(vendor_names),
        "VendorCategory": random.choices(VENDOR_CATEGORIES, weights=VENDOR_CATEGORY_DISTRIBUTION)[0],
        "VendorRating": round(random.uniform(3.0, 5.0), 1),
        "PreferredVendor": random.choice([True, False]),
        "RequesterID": f"EMP{random.randint(1000, 9999)}",
        "Department": random.choices(DEPARTMENTS, weights=DEPARTMENT_DISTRIBUTION)[0],
        "CostCenter": f"CC{random.randint(100, 999)}",
        "ApprovalLevel": 1 if order_value < 10000 else (2 if order_value < 100000 else 3),
        "InvoiceNumber": invoice_number,
        "InvoiceAmount": round(order_value * random.uniform(0.95, 1.05), 2),
        "PaymentMethod": random.choices(PAYMENT_METHODS, weights=PAYMENT_METHOD_DISTRIBUTION)[0]
    }

def generate_stage_activities(stage: str, wait_hours: float, freeze_time: datetime) -> List[Dict[str, Any]]:
    """Generate activities for cases waiting in a specific stage"""
    activities = []
    
    # Calculate the time when the case entered the current stage
    stage_start_time = add_business_hours(freeze_time, -wait_hours)
    
    # Define activity paths based on the waiting stage
    if stage == "Waiting for Order Processing":
        path = [
            ("Place Order", "requester", 0.5),
            ("Receive Order", "buyer", 0.25)
        ]
    elif stage == "Waiting for Vendor Selection":
        path = [
            ("Place Order", "requester", 0.5),
            ("Receive Order", "buyer", 0.25),
            ("Process Order", "buyer", 1.0)
        ]
    elif stage == "Waiting for Invoice Processing":
        path = [
            ("Place Order", "requester", 0.5),
            ("Receive Order", "buyer", 0.25),
            ("Process Order", "buyer", 1.0),
            ("Receive Invoice", "system", 0.1)
        ]
    elif stage == "Waiting for Payment Processing":
        path = [
            ("Place Order", "requester", 0.5),
            ("Receive Order", "buyer", 0.25),
            ("Process Order", "buyer", 1.0),
            ("Receive Invoice", "system", 0.1),
            ("Review Invoice", "ap_clerk", 1.0),
            ("Create Payment", "ap_clerk", 0.5)
        ]
    elif stage == "Waiting for Dispute Resolution":
        path = [
            ("Place Order", "requester", 0.5),
            ("Receive Order", "buyer", 0.25),
            ("Process Order", "buyer", 1.0),
            ("Receive Invoice", "system", 0.1),
            ("Review Invoice", "ap_clerk", 1.0),
            ("Make Billing Inquiry", "ap_clerk", 2.0)
        ]
    else:
        # Default path for unknown stages
        path = [("Place Order", "requester", 0.5)]
    
    # Generate activities backwards from the stage start time
    current_time = stage_start_time
    for activity_name, resource_type, base_duration in reversed(path):
        resource = select_resource(resource_type, activity_name)
        activities.insert(0, {
            "ActivityName": activity_name,
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "Role": resource_type.replace("_", " ").title()
        })
        
        # Move backwards for the next activity
        duration = base_duration * random.uniform(0.8, 1.2)
        current_time = add_business_hours(current_time, -duration)
    
    return activities

def generate_completed_case(completion_time: datetime) -> Dict[str, Any]:
    """Generate a completed case that finished today"""
    case_attributes = generate_case_attributes()
    
    # Generate activities for a completed standard process
    activities = []
    current_time = add_business_hours(completion_time, -random.uniform(4, 8))  # Started 4-8 hours ago
    
    # Standard completion path
    path = [
        ("Place Order", "requester", 0.5),
        ("Receive Order", "buyer", 0.25),
        ("Process Order", "buyer", 1.0),
        ("Receive Invoice", "system", 0.1),
        ("Review Invoice", "ap_clerk", 1.0),
        ("Create Payment", "ap_clerk", 0.5),
        ("Authorize Payment", "approver", 0.5),
        ("Update Customer Balance", "system", 0.1),
        ("Verify Successful Payment", "system", 0.1)
    ]
    
    for activity_name, resource_type, base_duration in path:
        resource = select_resource(resource_type, activity_name)
        activities.append({
            "ActivityName": activity_name,
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "Role": resource_type.replace("_", " ").title()
        })
        
        duration = base_duration * random.uniform(0.8, 1.2)
        current_time = add_business_hours(current_time, duration)
    
    # Mark as completed
    case_attributes["InvoiceStatus"] = "Paid"
    case_attributes["PaymentStatus"] = "Completed"
    case_attributes["PaymentDate"] = completion_time.strftime("%Y-%m-%d")
    case_attributes["InvoiceDate"] = (completion_time - timedelta(days=random.randint(1, 7))).strftime("%Y-%m-%d")
    case_attributes["DiscountApplied"] = round(case_attributes["OrderValue"] * random.uniform(0.0, 0.05), 2) if random.random() < 0.3 else 0.0
    
    case_attributes["activities"] = activities
    return case_attributes

def generate_in_progress_case(stage: str, freeze_time: datetime) -> Dict[str, Any]:
    """Generate an in-progress case waiting in a specific stage"""
    case_attributes = generate_case_attributes()
    
    # Generate random waiting time based on stage thresholds
    thresholds = STAGE_THRESHOLDS.get(stage, {"medium": 4, "high": 8})
    
    # Weight distribution: 60% under medium, 30% between medium-high, 10% over high
    wait_distribution = random.random()
    if wait_distribution < 0.6:
        # Under medium threshold
        wait_hours = random.uniform(0.5, thresholds["medium"])
    elif wait_distribution < 0.9:
        # Between medium and high threshold  
        wait_hours = random.uniform(thresholds["medium"], thresholds["high"])
    else:
        # Over high threshold (problematic cases)
        wait_hours = random.uniform(thresholds["high"], thresholds["high"] * 2)
    
    # Generate activities for this stage
    activities = generate_stage_activities(stage, wait_hours, freeze_time)
    
    # Mark as in-progress
    case_attributes["InvoiceStatus"] = "Pending"
    case_attributes["PaymentStatus"] = "Pending"
    case_attributes["PaymentDate"] = None
    case_attributes["InvoiceDate"] = (freeze_time - timedelta(days=random.randint(0, 3))).strftime("%Y-%m-%d")
    case_attributes["DiscountApplied"] = 0.0
    
    case_attributes["activities"] = activities
    return case_attributes

def generate_daily_dataset():
    """Generate daily snapshot dataset with completed and in-progress cases"""
    print(f"Generating Source to Pay daily snapshot for {FREEZE_TIME}")
    
    cases = []
    
    # Generate completed cases for today
    print(f"Generating {COMPLETED_CASES_TODAY} completed cases...")
    for i in range(COMPLETED_CASES_TODAY):
        completion_time = FREEZE_TIME
        case = generate_completed_case(completion_time)
        cases.append(case)
    
    # Generate in-progress cases by stage
    total_in_progress = 0
    for stage, (min_cases, max_cases) in IN_PROGRESS_CASES.items():
        num_cases = random.randint(min_cases, max_cases)
        print(f"Generating {num_cases} cases in stage: {stage}")
        
        for i in range(num_cases):
            case = generate_in_progress_case(stage, FREEZE_TIME)
            cases.append(case)
        
        total_in_progress += num_cases
    
    print(f"Generated {len(cases)} total cases ({COMPLETED_CASES_TODAY} completed, {total_in_progress} in-progress)")
    
    return cases

def main():
    """Generate daily dataset"""
    cases = generate_daily_dataset()
    
    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate JSON output
    json_output = {
        "FreezeTime": FREEZE_TIME.strftime("%Y-%m-%dT%H:%M:%S+00:00"),
        "cases": cases
    }
    
    json_file = os.path.join(output_dir, "source_to_pay_daily.json")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_output, f, indent=2, ensure_ascii=False)
    
    print(f"JSON file saved: {json_file}")
    
    # Generate CSV output
    csv_file = os.path.join(output_dir, "source_to_pay_daily.csv")
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'CaseId', 'ActivityName', 'ActivityTime', 'Resource', 'Role',
            'OrderType', 'OrderValue', 'Currency', 'Priority', 'PaymentTerms',
            'VendorID', 'VendorName', 'VendorCategory', 'VendorRating', 'PreferredVendor',
            'RequesterID', 'Department', 'CostCenter', 'ApprovalLevel',
            'InvoiceNumber', 'InvoiceDate', 'InvoiceAmount', 'InvoiceStatus',
            'PaymentMethod', 'PaymentStatus', 'PaymentDate', 'DiscountApplied'
        ]
        
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for case in cases:
            case_data = {k: v for k, v in case.items() if k != 'activities'}
            for activity in case['activities']:
                row = {**case_data, **activity}
                writer.writerow(row)
    
    print(f"CSV file saved: {csv_file}")
    print("Daily dataset generation completed!")

if __name__ == "__main__":
    main()