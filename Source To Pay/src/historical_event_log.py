#!/usr/bin/env python3
"""
Source to Pay Process Mining Dataset Generator - Historical Event Log
Generates 1-2 years of completed procurement cases with realistic bottlenecks and variations
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
TOTAL_CASES = 5000  # Target for ~500 cases per week over 10 weeks (2 months+)
START_DATE = datetime(2023, 1, 1, 8, 0, 0)
END_DATE = datetime(2024, 12, 31, 18, 0, 0)
BUSINESS_START_HOUR = 8
BUSINESS_END_HOUR = 18

# Resources with performance factors
RESOURCES = {
    "requester": ["John Smith", "Maria Garcia", "David Chen", "Sarah Wilson", "Ahmed Al-Rashid", "Lisa Johnson", "Tom Anderson", "Priya Patel"],
    "buyer": ["Michael Brown", "Jennifer Lee", "Robert Taylor", "Emily Davis", "Carlos Rodriguez", "Anna Schmidt"],  # Robert is slow
    "ap_clerk": ["Susan Clark", "James White", "Michelle Kim", "Paul Martinez"],  # Paul is slow
    "approver": ["Director Johnson", "Manager Williams", "VP Chen", "CFO Anderson"],
    "finance": ["Finance Manager", "Treasury Specialist", "Controller"],
    "vendor": ["Vendor System", "Vendor Portal", "Manual Vendor Process"],
    "system": ["ERP System", "Payment Gateway", "Invoice System"]
}

# Performance factors (1.0 = normal, <1.0 = slower, >1.0 = faster)
PERFORMANCE_FACTORS = {
    "Robert Taylor": 0.4,      # 60% slower buyer - creates procurement bottleneck
    "Paul Martinez": 0.3,      # 70% slower AP clerk - creates payment bottleneck
    "Manual Vendor Process": 0.2,  # 80% slower vendor processing
    "ERP System": 1.5,         # 50% faster (automated)
    "Payment Gateway": 2.0,    # 100% faster (automated)
    "Invoice System": 1.8      # 80% faster (automated)
}

# Order value distribution (in USD)
ORDER_VALUE_RANGES = [
    (10, 999, 0.30),      # Under $1,000: 30%
    (1000, 9999, 0.40),   # $1,000-$10,000: 40%
    (10000, 99999, 0.25), # $10,000-$100,000: 25%
    (100000, 1000000, 0.05)  # Over $100,000: 5%
]

# Master data distributions
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
                    # Weekend, jump to Monday
                    days_to_monday = 7 - current.weekday()
                    current += timedelta(days=days_to_monday)
                else:
                    # After hours, jump to next day
                    current += timedelta(days=1)
                current = current.replace(hour=BUSINESS_START_HOUR, minute=0, second=0)
            else:
                current = current.replace(hour=BUSINESS_START_HOUR, minute=0, second=0)
    
    return current

def select_resource(resource_type: str, activity_name: str = "") -> str:
    """Select resource based on activity type with realistic bottlenecks"""
    base_resources = RESOURCES.get(resource_type, ["Unknown"])
    
    # Create bottlenecks by assigning slow resources more frequently to certain activities
    if resource_type == "buyer":
        # Robert Taylor handles 40% of complex orders (creates bottleneck)
        if "Review" in activity_name or random.random() < 0.4:
            return "Robert Taylor"
        return random.choice(["Michael Brown", "Jennifer Lee", "Emily Davis", "Carlos Rodriguez", "Anna Schmidt"])
    
    elif resource_type == "ap_clerk":
        # Paul Martinez handles 30% of invoice processing (creates bottleneck)
        if random.random() < 0.3:
            return "Paul Martinez"
        return random.choice(["Susan Clark", "James White", "Michelle Kim"])
    
    elif resource_type == "vendor":
        # Manual vendor process for 20% of cases (creates delay)
        if random.random() < 0.2:
            return "Manual Vendor Process"
        return random.choice(["Vendor System", "Vendor Portal"])
    
    return random.choice(base_resources)

def calculate_duration(base_hours: float, resource: str) -> float:
    """Calculate actual duration based on resource performance"""
    performance = PERFORMANCE_FACTORS.get(resource, 1.0)
    if performance != 1.0:
        actual_hours = base_hours / performance
    else:
        # Add random variation for normal resources
        actual_hours = base_hours * random.uniform(0.8, 1.2)
    
    return actual_hours

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
    
    # Generate invoice details
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
        "InvoiceAmount": round(order_value * random.uniform(0.95, 1.05), 2),  # Small variance from order
        "InvoiceStatus": "Paid",  # All historical cases are complete
        "PaymentMethod": random.choices(PAYMENT_METHODS, weights=PAYMENT_METHOD_DISTRIBUTION)[0],
        "PaymentStatus": "Completed",  # All historical cases are complete
        "DiscountApplied": round(order_value * random.uniform(0.0, 0.05), 2) if random.random() < 0.3 else 0.0
    }

def generate_standard_purchase_order(start_time: datetime, case_attributes: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate standard purchase order process activities"""
    activities = []
    current_time = start_time
    
    # 1. Initiation Phase
    # Place Order
    resource = select_resource("requester")
    duration = calculate_duration(0.5, resource)  # 30 minutes base
    activities.append({
        "ActivityName": "Place Order",
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "Role": "Requester"
    })
    current_time = add_business_hours(current_time, duration)
    
    # Receive Order
    resource = select_resource("buyer")
    duration = calculate_duration(0.25, resource)  # 15 minutes base
    activities.append({
        "ActivityName": "Receive Order",
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "Role": "Buyer"
    })
    current_time = add_business_hours(current_time, duration)
    
    # 2. Order Processing
    # Process Order
    resource = select_resource("buyer", "Process Order")
    duration = calculate_duration(1.0, resource)  # 1 hour base
    activities.append({
        "ActivityName": "Process Order",
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "Role": "Buyer"
    })
    current_time = add_business_hours(current_time, duration)
    
    # Decision Point: Orders OK? (15% go to error handling)
    if random.random() < 0.15:
        # Call Centers
        resource = select_resource("buyer")
        duration = calculate_duration(0.5, resource)
        activities.append({
            "ActivityName": "Call Centers",
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "Role": "Buyer"
        })
        current_time = add_business_hours(current_time, duration)
        
        # Review Order Info
        resource = select_resource("buyer", "Review Order Info")
        duration = calculate_duration(1.5, resource)
        activities.append({
            "ActivityName": "Review Order Info",
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "Role": "Buyer"
        })
        current_time = add_business_hours(current_time, duration)
        
        # Capture Customer Info
        resource = select_resource("buyer")
        duration = calculate_duration(0.5, resource)
        activities.append({
            "ActivityName": "Capture Customer Info",
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "Role": "Buyer"
        })
        current_time = add_business_hours(current_time, duration)
    
    # 3. Invoice Receipt (vendor delay simulation)
    vendor_delay = random.uniform(24, 120)  # 1-5 business days
    current_time = add_business_hours(current_time, vendor_delay)
    
    # Receive Invoice (70% electronic, 30% hard copy)
    if random.random() < 0.7:
        resource = select_resource("system")
        duration = calculate_duration(0.1, resource)  # Automated
        activities.append({
            "ActivityName": "Receive Invoice",
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "Role": "System"
        })
    else:
        resource = select_resource("ap_clerk")
        duration = calculate_duration(0.5, resource)
        activities.append({
            "ActivityName": "Receive Hard Copy",
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "Role": "AP Clerk"
        })
    current_time = add_business_hours(current_time, duration)
    
    # 4. Invoice Processing
    # Review Invoice
    resource = select_resource("ap_clerk", "Review Invoice")
    duration = calculate_duration(1.0, resource)
    activities.append({
        "ActivityName": "Review Invoice",
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "Role": "AP Clerk"
    })
    current_time = add_business_hours(current_time, duration)
    
    # Invoice matching issues (10% of cases)
    if random.random() < 0.10:
        # Make Billing Inquiry
        resource = select_resource("ap_clerk")
        duration = calculate_duration(2.0, resource)
        activities.append({
            "ActivityName": "Make Billing Inquiry",
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "Role": "AP Clerk"
        })
        current_time = add_business_hours(current_time, duration)
        
        # Manage Account
        resource = select_resource("ap_clerk")
        duration = calculate_duration(1.0, resource)
        activities.append({
            "ActivityName": "Manage Account",
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "Role": "AP Clerk"
        })
        current_time = add_business_hours(current_time, duration)
        
        # Update Profile
        resource = select_resource("buyer")
        duration = calculate_duration(0.5, resource)
        activities.append({
            "ActivityName": "Update Profile",
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "Role": "Buyer"
        })
        current_time = add_business_hours(current_time, duration)
    
    # 5. Payment Authorization
    # Create Payment
    resource = select_resource("ap_clerk")
    duration = calculate_duration(0.5, resource)
    activities.append({
        "ActivityName": "Create Payment",
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "Role": "AP Clerk"
    })
    current_time = add_business_hours(current_time, duration)
    
    # Payment method specific activities
    payment_method = case_attributes["PaymentMethod"]
    
    if payment_method == "Credit Card":
        # Identify or Verify Credit Card Info
        resource = select_resource("ap_clerk")
        duration = calculate_duration(0.25, resource)
        activities.append({
            "ActivityName": "Identify or Verify Credit Card Info",
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "Role": "AP Clerk"
        })
        current_time = add_business_hours(current_time, duration)
        
        # Abstract Payment Method
        resource = select_resource("system")
        duration = calculate_duration(0.1, resource)
        activities.append({
            "ActivityName": "Abstract Payment Method",
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "Role": "System"
        })
        current_time = add_business_hours(current_time, duration)
        
    elif payment_method == "Bank Transfer":
        # Sign In (Payroll Account)
        resource = select_resource("ap_clerk")
        duration = calculate_duration(0.1, resource)
        activities.append({
            "ActivityName": "Sign In (Payroll Account)",
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "Role": "AP Clerk"
        })
        current_time = add_business_hours(current_time, duration)
        
        # Fill in Settlement Info
        resource = select_resource("ap_clerk")
        duration = calculate_duration(0.5, resource)
        activities.append({
            "ActivityName": "Fill in Settlement Info",
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "Role": "AP Clerk"
        })
        current_time = add_business_hours(current_time, duration)
        
    elif payment_method == "Check":
        # Manage Payment
        resource = select_resource("ap_clerk")
        duration = calculate_duration(1.0, resource)
        activities.append({
            "ActivityName": "Manage Payment",
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "Role": "AP Clerk"
        })
        current_time = add_business_hours(current_time, duration)
        
        # Default Payment Method
        resource = select_resource("system")
        duration = calculate_duration(0.2, resource)
        activities.append({
            "ActivityName": "Default Payment Method",
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "Role": "System"
        })
        current_time = add_business_hours(current_time, duration)
        
    elif payment_method == "Cash":
        # Pay Cash
        resource = select_resource("ap_clerk")
        duration = calculate_duration(0.5, resource)
        activities.append({
            "ActivityName": "Pay Cash",
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "Role": "AP Clerk"
        })
        current_time = add_business_hours(current_time, duration)
    
    # 6. Payment Processing
    # Authorize Payment
    resource = select_resource("approver")
    duration = calculate_duration(0.5, resource)
    activities.append({
        "ActivityName": "Authorize Payment",
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "Role": "Approver"
    })
    current_time = add_business_hours(current_time, duration)
    
    # Update Customer Balance
    resource = select_resource("system")
    duration = calculate_duration(0.1, resource)
    activities.append({
        "ActivityName": "Update Customer Balance",
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "Role": "System"
    })
    current_time = add_business_hours(current_time, duration)
    
    # Verify Successful Payment
    resource = select_resource("system")
    duration = calculate_duration(0.1, resource)
    activities.append({
        "ActivityName": "Verify Successful Payment",
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "Role": "System"
    })
    current_time = add_business_hours(current_time, duration)
    
    return activities

def generate_credit_card_direct_process(start_time: datetime, case_attributes: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate simplified credit card direct purchase process"""
    activities = []
    current_time = start_time
    
    # Place Order (Credit Card)
    resource = select_resource("requester")
    duration = calculate_duration(0.25, resource)
    activities.append({
        "ActivityName": "Place Order (Credit Card)",
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "Role": "Requester"
    })
    current_time = add_business_hours(current_time, duration)
    
    # Receive Order (Credit Card)
    resource = select_resource("buyer")
    duration = calculate_duration(0.1, resource)
    activities.append({
        "ActivityName": "Receive Order (Credit Card)",
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "Role": "Buyer"
    })
    current_time = add_business_hours(current_time, duration)
    
    # Request Payment by Credit Card (Direct)
    resource = select_resource("system")
    duration = calculate_duration(0.1, resource)
    activities.append({
        "ActivityName": "Request Payment by Credit Card (Direct)",
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "Role": "System"
    })
    current_time = add_business_hours(current_time, duration)
    
    # Receive E-Invoice
    resource = select_resource("system")
    duration = calculate_duration(0.1, resource)
    activities.append({
        "ActivityName": "Receive E-Invoice",
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "Role": "System"
    })
    current_time = add_business_hours(current_time, duration)
    
    # Authorize Payment
    resource = select_resource("system")
    duration = calculate_duration(0.1, resource)
    activities.append({
        "ActivityName": "Authorize Payment",
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "Role": "System"
    })
    current_time = add_business_hours(current_time, duration)
    
    # Verify Successful Payment
    resource = select_resource("system")
    duration = calculate_duration(0.1, resource)
    activities.append({
        "ActivityName": "Verify Successful Payment",
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "Role": "System"
    })
    current_time = add_business_hours(current_time, duration)
    
    return activities

def generate_case() -> Dict[str, Any]:
    """Generate a complete procurement case"""
    case_attributes = generate_case_attributes()
    
    # Generate random start time within the date range
    time_range = int((END_DATE - START_DATE).total_seconds())
    random_seconds = random.randint(0, time_range)
    start_time = START_DATE + timedelta(seconds=random_seconds)
    
    # Ensure start time is during business hours
    while not is_business_hours(start_time):
        start_time = add_business_hours(start_time, 0.1)
    
    # Determine process path (30% credit card direct, 70% standard)
    if case_attributes["OrderValue"] < 1000 and random.random() < 0.30:
        # Credit card direct process for small orders
        case_attributes["PaymentMethod"] = "Credit Card"
        activities = generate_credit_card_direct_process(start_time, case_attributes)
    else:
        # Standard purchase order process
        activities = generate_standard_purchase_order(start_time, case_attributes)
    
    # Set payment date to last activity time
    if activities:
        last_activity_time = datetime.strptime(activities[-1]["ActivityTime"], "%Y-%m-%d %H:%M:%S")
        case_attributes["PaymentDate"] = last_activity_time.strftime("%Y-%m-%d")
        case_attributes["InvoiceDate"] = (last_activity_time - timedelta(days=random.randint(1, 7))).strftime("%Y-%m-%d")
    
    case_attributes["activities"] = activities
    return case_attributes

def main():
    """Generate historical dataset"""
    print("Generating Source to Pay historical event log...")
    print(f"Target cases: {TOTAL_CASES}")
    print(f"Date range: {START_DATE.date()} to {END_DATE.date()}")
    
    cases = []
    for i in range(TOTAL_CASES):
        if (i + 1) % 500 == 0:
            print(f"Generated {i + 1} cases...")
        
        case = generate_case()
        cases.append(case)
    
    print(f"Generated {len(cases)} cases total")
    
    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate JSON output
    json_output = {
        "FreezeTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00"),
        "cases": cases
    }
    
    json_file = os.path.join(output_dir, "source_to_pay_historical.json")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_output, f, indent=2, ensure_ascii=False)
    
    print(f"JSON file saved: {json_file}")
    
    # Generate CSV output
    csv_file = os.path.join(output_dir, "source_to_pay_historical.csv")
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
    print("Historical dataset generation completed!")

if __name__ == "__main__":
    main()