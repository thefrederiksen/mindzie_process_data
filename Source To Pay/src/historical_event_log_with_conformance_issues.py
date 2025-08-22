#!/usr/bin/env python3
"""
Source to Pay Process Mining Dataset Generator with Conformance Issues
Generates historical event log with realistic process violations and conformance issues
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

# Conformance issue rates
CONFORMANCE_ISSUES = {
    "skip_approval": 0.03,           # 3% skip approval when required
    "duplicate_payment": 0.01,       # 1% duplicate payment attempts
    "wrong_sequence": 0.02,          # 2% activities in wrong order
    "missing_invoice_match": 0.04,   # 4% skip three-way matching
    "unauthorized_vendor": 0.02,     # 2% use unauthorized vendor
    "split_payment_bypass": 0.01,    # 1% split orders to bypass approval limits
    "emergency_bypass": 0.03,        # 3% emergency orders bypass normal process
    "retroactive_approval": 0.02,    # 2% approvals after ordering
    "manual_override": 0.01,         # 1% manual system overrides
    "incomplete_documentation": 0.03 # 3% missing required documentation
}

# Resources with performance factors
RESOURCES = {
    "requester": ["John Smith", "Maria Garcia", "David Chen", "Sarah Wilson", "Ahmed Al-Rashid", "Lisa Johnson", "Tom Anderson", "Priya Patel"],
    "buyer": ["Michael Brown", "Jennifer Lee", "Robert Taylor", "Emily Davis", "Carlos Rodriguez", "Anna Schmidt"],  # Robert is slow
    "ap_clerk": ["Susan Clark", "James White", "Michelle Kim", "Paul Martinez"],  # Paul is slow
    "approver": ["Director Johnson", "Manager Williams", "VP Chen", "CFO Anderson"],
    "finance": ["Finance Manager", "Treasury Specialist", "Controller"],
    "vendor": ["Vendor System", "Vendor Portal", "Manual Vendor Process"],
    "system": ["ERP System", "Payment Gateway", "Invoice System"],
    "unauthorized": ["Temp Worker", "Intern", "External Consultant"]  # For conformance violations
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
                    current = current.replace(hour=BUSINESS_START_HOUR, minute=0, second=0) + timedelta(days=days_to_monday)
                else:
                    # After hours, jump to next day
                    current = current.replace(hour=BUSINESS_START_HOUR, minute=0, second=0) + timedelta(days=1)
            else:
                # Before hours
                current = current.replace(hour=BUSINESS_START_HOUR, minute=0, second=0)
    
    return current

def select_resource(role: str, activity: str = None) -> str:
    """Select a resource based on role and optional activity bias"""
    resources = RESOURCES[role]
    
    # Bias selection for creating bottlenecks
    if role == "buyer" and activity == "Process Order" and random.random() < 0.4:
        return "Robert Taylor"  # 40% chance for slow buyer on complex activities
    elif role == "ap_clerk" and random.random() < 0.3:
        return "Paul Martinez"  # 30% chance for slow AP clerk
    elif role == "vendor" and random.random() < 0.2:
        return "Manual Vendor Process"  # 20% chance for manual vendor process
    
    return random.choice(resources)

def calculate_duration(base_hours: float, resource: str) -> float:
    """Calculate activity duration based on resource performance"""
    performance = PERFORMANCE_FACTORS.get(resource, 1.0)
    
    # Add some random variation (±20%)
    variation = random.uniform(0.8, 1.2)
    
    duration = base_hours / performance * variation
    
    return max(0.1, duration)  # Minimum 6 minutes

def weighted_choice(choices: List[Any], weights: List[float]) -> Any:
    """Make a weighted random choice"""
    return random.choices(choices, weights=weights)[0]

def generate_order_value() -> float:
    """Generate order value based on distribution"""
    range_choice = random.random()
    cumulative = 0
    
    for min_val, max_val, probability in ORDER_VALUE_RANGES:
        cumulative += probability
        if range_choice < cumulative:
            return round(random.uniform(min_val, max_val), 2)
    
    # Default to last range if something goes wrong
    return round(random.uniform(100000, 1000000), 2)

def generate_vendor_id() -> str:
    """Generate vendor ID with some repeat vendors"""
    if random.random() < 0.7:  # 70% chance of using existing vendor
        return f"V{random.randint(1000, 1050):04d}"  # 50 regular vendors
    else:
        return f"V{random.randint(1051, 2000):04d}"  # New/rare vendors

def generate_vendor_name(vendor_id: str) -> str:
    """Generate consistent vendor name for ID"""
    vendor_names = ["Acme Supplies", "Global Tech", "Office Direct", "Industrial Partners", 
                   "Software Solutions", "Equipment Pro", "Service Masters", "Supply Chain Co",
                   "Digital Services", "Maintenance Experts"]
    
    # Use vendor ID to consistently map to name
    index = int(vendor_id[1:]) % len(vendor_names)
    suffix = ["Inc", "LLC", "Corp", "Ltd", "Group"][int(vendor_id[1:]) % 5]
    return f"{vendor_names[index]} {suffix}"

def determine_conformance_issues() -> Dict[str, bool]:
    """Determine which conformance issues will occur in this case"""
    issues = {}
    for issue_type, probability in CONFORMANCE_ISSUES.items():
        issues[issue_type] = random.random() < probability
    return issues

def generate_standard_purchase_order(start_time: datetime, case_attributes: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate standard purchase order process activities with potential conformance issues"""
    activities = []
    current_time = start_time
    
    # Determine conformance issues for this case
    conformance_issues = determine_conformance_issues()
    case_attributes["ConformanceIssues"] = [k for k, v in conformance_issues.items() if v]
    
    # 1. Initiation Phase
    # Check for emergency bypass
    if conformance_issues["emergency_bypass"]:
        # Emergency order - skip straight to vendor selection
        resource = random.choice(RESOURCES["unauthorized"])
        activities.append({
            "ActivityName": "Emergency Order Bypass",
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "Role": "Unauthorized",
            "ConformanceViolation": "emergency_bypass"
        })
        current_time = add_business_hours(current_time, 0.1)
    
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
    
    # Check for split payment bypass
    if conformance_issues["split_payment_bypass"] and case_attributes["OrderValue"] > 50000:
        # Split into multiple smaller orders to bypass approval
        activities.append({
            "ActivityName": "Split Order",
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "Role": "Requester",
            "ConformanceViolation": "split_payment_bypass"
        })
        current_time = add_business_hours(current_time, 0.25)
    
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
    if random.random() < 0.15 or conformance_issues["incomplete_documentation"]:
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
        duration = calculate_duration(0.75, resource)
        activities.append({
            "ActivityName": "Review Order Info",
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "Role": "Buyer"
        })
        current_time = add_business_hours(current_time, duration)
        
        # Capture Customer Info
        duration = calculate_duration(0.5, resource)
        activities.append({
            "ActivityName": "Capture Customer Info",
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "Role": "Buyer"
        })
        current_time = add_business_hours(current_time, duration)
    
    # Check for unauthorized vendor usage
    if conformance_issues["unauthorized_vendor"]:
        activities.append({
            "ActivityName": "Use Unauthorized Vendor",
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "Role": "Buyer",
            "ConformanceViolation": "unauthorized_vendor"
        })
        current_time = add_business_hours(current_time, 0.1)
        case_attributes["PreferredVendor"] = False
    
    # 3. Vendor Interaction
    # Vendor processes order (simulated delay)
    vendor_resource = select_resource("vendor")
    duration = calculate_duration(random.uniform(8, 24), vendor_resource)  # 1-3 days
    current_time = add_business_hours(current_time, duration)
    
    # 4. Invoice Receipt
    # Receive Invoice
    resource = select_resource("ap_clerk")
    duration = calculate_duration(0.25, resource)
    invoice_type = "electronic" if random.random() < 0.7 else "hardcopy"
    
    if invoice_type == "electronic":
        activities.append({
            "ActivityName": "Receive Invoice",
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "Role": "AP Clerk"
        })
    else:
        activities.append({
            "ActivityName": "Receive Hard Copy",
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "Role": "AP Clerk"
        })
    current_time = add_business_hours(current_time, duration)
    
    # 5. Invoice Processing
    # Check for missing invoice match violation
    if not conformance_issues["missing_invoice_match"]:
        # Review Invoice (normal flow)
        duration = calculate_duration(0.5, resource)
        activities.append({
            "ActivityName": "Review Invoice",
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "Role": "AP Clerk"
        })
        current_time = add_business_hours(current_time, duration)
    else:
        # Skip invoice matching (violation)
        activities.append({
            "ActivityName": "Skip Invoice Matching",
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "Role": "AP Clerk",
            "ConformanceViolation": "missing_invoice_match"
        })
        current_time = add_business_hours(current_time, 0.1)
    
    # Invoice matching decision (10% need inquiry)
    if random.random() < 0.1:
        # Make Billing Inquiry
        duration = calculate_duration(2.0, resource)
        activities.append({
            "ActivityName": "Make Billing Inquiry",
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "Role": "AP Clerk"
        })
        current_time = add_business_hours(current_time, duration)
        
        # Manage Account
        duration = calculate_duration(0.5, resource)
        activities.append({
            "ActivityName": "Manage Account",
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "Role": "AP Clerk"
        })
        current_time = add_business_hours(current_time, duration)
        
        # Update Profile
        duration = calculate_duration(0.25, resource)
        activities.append({
            "ActivityName": "Update Profile",
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "Role": "AP Clerk"
        })
        current_time = add_business_hours(current_time, duration)
    
    # 6. Payment Authorization
    # Check for approval bypass
    need_approval = case_attributes["OrderValue"] > 10000
    
    if need_approval and not conformance_issues["skip_approval"]:
        # Normal approval flow
        resource = select_resource("approver")
        duration = calculate_duration(2.0, resource)  # 2 hours base
        
        # Check for retroactive approval
        if conformance_issues["retroactive_approval"]:
            # Add payment first, then approval (wrong order)
            activities.append({
                "ActivityName": "Create Payment",
                "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "Resource": select_resource("finance"),
                "Role": "Finance",
                "ConformanceViolation": "retroactive_approval"
            })
            current_time = add_business_hours(current_time, 0.5)
        
        activities.append({
            "ActivityName": "Authorize Payment",
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "Role": "Approver"
        })
        current_time = add_business_hours(current_time, duration)
        
    elif need_approval and conformance_issues["skip_approval"]:
        # Skip required approval (violation)
        activities.append({
            "ActivityName": "Skip Approval",
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": "System Override",
            "Role": "System",
            "ConformanceViolation": "skip_approval"
        })
        current_time = add_business_hours(current_time, 0.1)
    
    # Create Payment (if not done retroactively)
    if not conformance_issues["retroactive_approval"]:
        resource = select_resource("finance")
        duration = calculate_duration(0.5, resource)
        activities.append({
            "ActivityName": "Create Payment",
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "Role": "Finance"
        })
        current_time = add_business_hours(current_time, duration)
    
    # 7. Payment Method Selection and Processing
    payment_method = case_attributes["PaymentMethod"]
    
    if payment_method == "Credit Card":
        # Credit Card Path
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
        
        # Charge Credit
        duration = calculate_duration(0.1, resource)
        activities.append({
            "ActivityName": "Charge Credit",
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "Role": "System"
        })
        current_time = add_business_hours(current_time, duration)
        
    elif payment_method == "Bank Transfer":
        # Bank Transfer Path
        resource = select_resource("finance")
        duration = calculate_duration(0.5, resource)
        activities.append({
            "ActivityName": "Sign In (Payroll Account)",
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "Role": "Finance"
        })
        current_time = add_business_hours(current_time, duration)
        
        # Fill in Settlement Info
        duration = calculate_duration(0.75, resource)
        activities.append({
            "ActivityName": "Fill in Settlement Info",
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "Role": "Finance"
        })
        current_time = add_business_hours(current_time, duration)
        
    elif payment_method == "Check":
        # Check Path
        resource = select_resource("finance")
        duration = calculate_duration(1.0, resource)
        activities.append({
            "ActivityName": "Manage Payment",
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "Role": "Finance"
        })
        current_time = add_business_hours(current_time, duration)
        
        # Default Payment Method
        activities.append({
            "ActivityName": "Default Payment Method",
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "Role": "Finance"
        })
        current_time = add_business_hours(current_time, 0.25)
        
    else:  # Cash
        # Cash Path
        resource = select_resource("finance")
        duration = calculate_duration(0.5, resource)
        activities.append({
            "ActivityName": "Pay Cash",
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "Role": "Finance"
        })
        current_time = add_business_hours(current_time, duration)
    
    # Check for duplicate payment
    if conformance_issues["duplicate_payment"]:
        # Add duplicate payment attempt
        current_time = add_business_hours(current_time, 24)  # Next day
        activities.append({
            "ActivityName": "Duplicate Payment Attempt",
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "Role": "Finance",
            "ConformanceViolation": "duplicate_payment"
        })
        current_time = add_business_hours(current_time, 0.5)
    
    # 8. Payment Processing
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
    
    # Notify Client
    activities.append({
        "ActivityName": "Notify Client",
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "Role": "System"
    })
    current_time = add_business_hours(current_time, 0.1)
    
    # 9. Verification
    # Verify Successful Payment
    resource = select_resource("finance")
    duration = calculate_duration(0.25, resource)
    activities.append({
        "ActivityName": "Verify Successful Payment",
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "Role": "Finance"
    })
    current_time = add_business_hours(current_time, duration)
    
    # Payment success decision (2% fail)
    if random.random() < 0.02:
        # Cancel Invoice
        duration = calculate_duration(2.0, resource)
        activities.append({
            "ActivityName": "Cancel Invoice",
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource,
            "Role": "Finance"
        })
        case_attributes["PaymentStatus"] = "Failed"
    else:
        case_attributes["PaymentStatus"] = "Completed"
    
    # Check for manual override
    if conformance_issues["manual_override"]:
        activities.append({
            "ActivityName": "Manual System Override",
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": "System Administrator",
            "Role": "Admin",
            "ConformanceViolation": "manual_override"
        })
    
    return activities

def generate_credit_card_purchase(start_time: datetime, case_attributes: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate credit card direct purchase process activities"""
    activities = []
    current_time = start_time
    
    # Simpler process for small purchases
    # 1. Place Order (Credit Card)
    resource = select_resource("requester")
    duration = calculate_duration(0.25, resource)  # 15 minutes
    activities.append({
        "ActivityName": "Place Order",
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "Role": "Requester"
    })
    current_time = add_business_hours(current_time, duration)
    
    # 2. Receive Order
    resource = select_resource("buyer")
    duration = calculate_duration(0.1, resource)  # 6 minutes
    activities.append({
        "ActivityName": "Receive Order",
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "Role": "Buyer"
    })
    current_time = add_business_hours(current_time, duration)
    
    # 3. Request Payment by Credit Card
    duration = calculate_duration(0.25, resource)
    activities.append({
        "ActivityName": "Request Payment by Credit Card",
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "Role": "Buyer"
    })
    current_time = add_business_hours(current_time, duration)
    
    # 4. Receive E-Invoice
    resource = select_resource("system")
    duration = calculate_duration(0.05, resource)  # 3 minutes (automated)
    activities.append({
        "ActivityName": "Receive E-Invoice",
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "Role": "System"
    })
    current_time = add_business_hours(current_time, duration)
    
    # 5. Process Payment
    duration = calculate_duration(0.1, resource)
    activities.append({
        "ActivityName": "Charge Credit",
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "Role": "System"
    })
    current_time = add_business_hours(current_time, duration)
    
    # 6. Update Balance
    activities.append({
        "ActivityName": "Update Customer Balance",
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "Role": "System"
    })
    current_time = add_business_hours(current_time, 0.05)
    
    # 7. Verify Payment
    resource = select_resource("finance")
    duration = calculate_duration(0.1, resource)
    activities.append({
        "ActivityName": "Verify Successful Payment",
        "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Resource": resource,
        "Role": "Finance"
    })
    
    case_attributes["PaymentStatus"] = "Completed"
    
    return activities

def generate_case() -> Dict[str, Any]:
    """Generate a complete procurement case"""
    # Generate case ID
    case_id = f"PO{random.randint(100000, 999999):06d}"
    
    # Generate timestamps within date range
    days_range = (END_DATE - START_DATE).days
    start_day_offset = random.randint(0, days_range - 30)  # Leave room for process completion
    hour = random.randint(BUSINESS_START_HOUR, BUSINESS_END_HOUR - 1)
    minute = random.randint(0, 59)
    start_time = START_DATE + timedelta(days=start_day_offset, hours=hour-BUSINESS_START_HOUR, minutes=minute)
    
    # Skip weekends for start time
    while start_time.weekday() >= 5:
        start_time += timedelta(days=1)
    
    # Generate case attributes
    order_value = generate_order_value()
    vendor_id = generate_vendor_id()
    
    case_attributes = {
        "CaseId": case_id,
        "OrderType": weighted_choice(ORDER_TYPES, ORDER_TYPE_DISTRIBUTION),
        "OrderValue": order_value,
        "Currency": weighted_choice(CURRENCIES, CURRENCY_DISTRIBUTION),
        "Priority": weighted_choice(PRIORITIES, PRIORITY_DISTRIBUTION),
        "PaymentTerms": weighted_choice(PAYMENT_TERMS, PAYMENT_TERMS_DISTRIBUTION),
        "VendorID": vendor_id,
        "VendorName": generate_vendor_name(vendor_id),
        "VendorCategory": weighted_choice(VENDOR_CATEGORIES, VENDOR_CATEGORY_DISTRIBUTION),
        "VendorRating": round(random.uniform(2.0, 5.0), 1),
        "PreferredVendor": random.random() < 0.7,
        "RequesterID": f"EMP{random.randint(1000, 9999):04d}",
        "Department": weighted_choice(DEPARTMENTS, DEPARTMENT_DISTRIBUTION),
        "CostCenter": f"CC{random.randint(100, 999):03d}",
        "ApprovalLevel": 1 if order_value < 10000 else (2 if order_value < 100000 else 3),
        "InvoiceNumber": f"INV-{start_time.year}-{random.randint(1, 999999):06d}",
        "InvoiceAmount": round(order_value * random.uniform(0.98, 1.02), 2),  # ±2% variance
        "InvoiceStatus": "Pending",
        "PaymentMethod": weighted_choice(PAYMENT_METHODS, PAYMENT_METHOD_DISTRIBUTION),
        "PaymentStatus": "Pending",
        "DiscountApplied": round(order_value * 0.01, 2) if random.random() < 0.3 else 0  # 30% get 1% discount
    }
    
    # Determine process type (30% credit card for small orders)
    if order_value < 1000 and random.random() < 0.3:
        activities = generate_credit_card_purchase(start_time, case_attributes)
    else:
        activities = generate_standard_purchase_order(start_time, case_attributes)
    
    # Set payment date to last activity time
    if activities:
        last_activity_time = datetime.strptime(activities[-1]["ActivityTime"], "%Y-%m-%d %H:%M:%S")
        case_attributes["PaymentDate"] = last_activity_time.strftime("%Y-%m-%d")
        case_attributes["InvoiceDate"] = (last_activity_time - timedelta(days=random.randint(1, 7))).strftime("%Y-%m-%d")
    
    case_attributes["activities"] = activities
    return case_attributes

def main():
    """Generate historical dataset with conformance issues"""
    print("Generating Source to Pay historical event log with conformance issues...")
    print(f"Target cases: {TOTAL_CASES}")
    print(f"Date range: {START_DATE.date()} to {END_DATE.date()}")
    print("\nConformance issue rates:")
    for issue, rate in CONFORMANCE_ISSUES.items():
        print(f"  - {issue}: {rate*100:.1f}%")
    
    cases = []
    conformance_stats = {issue: 0 for issue in CONFORMANCE_ISSUES.keys()}
    
    for i in range(TOTAL_CASES):
        if (i + 1) % 500 == 0:
            print(f"Generated {i + 1} cases...")
        
        case = generate_case()
        cases.append(case)
        
        # Track conformance issues
        if "ConformanceIssues" in case:
            for issue in case["ConformanceIssues"]:
                conformance_stats[issue] += 1
    
    print(f"\nGenerated {len(cases)} cases total")
    print("\nConformance issues generated:")
    for issue, count in conformance_stats.items():
        percentage = (count / TOTAL_CASES) * 100
        print(f"  - {issue}: {count} cases ({percentage:.1f}%)")
    
    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Save as JSON
    json_output = {
        "metadata": {
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_cases": len(cases),
            "date_range": {
                "start": START_DATE.strftime("%Y-%m-%d"),
                "end": END_DATE.strftime("%Y-%m-%d")
            },
            "conformance_issues": conformance_stats
        },
        "cases": cases
    }
    
    json_path = os.path.join(output_dir, "source_to_pay_historical_with_conformance.json")
    with open(json_path, 'w') as f:
        json.dump(json_output, f, indent=2)
    print(f"\nJSON file saved to: {json_path}")
    
    # Save as CSV
    csv_path = os.path.join(output_dir, "source_to_pay_historical_with_conformance.csv")
    csv_rows = []
    
    # Collect all possible fieldnames
    all_fieldnames = set()
    for case in cases:
        case_data = {k: v for k, v in case.items() if k != "activities" and k != "ConformanceIssues"}
        case_data["ConformanceIssues"] = ";".join(case.get("ConformanceIssues", []))
        all_fieldnames.update(case_data.keys())
        
        for activity in case["activities"]:
            all_fieldnames.update(activity.keys())
    
    # Create rows
    for case in cases:
        case_data = {k: v for k, v in case.items() if k != "activities" and k != "ConformanceIssues"}
        case_data["ConformanceIssues"] = ";".join(case.get("ConformanceIssues", []))
        
        for activity in case["activities"]:
            row = {**case_data}
            # Add activity data
            for key in activity:
                row[key] = activity[key]
            # Ensure all fieldnames are present (with empty string for missing)
            for field in all_fieldnames:
                if field not in row:
                    row[field] = ""
            csv_rows.append(row)
    
    if csv_rows:
        fieldnames = sorted(list(all_fieldnames))
        with open(csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_rows)
        print(f"CSV file saved to: {csv_path}")
    
    # Calculate statistics
    total_activities = sum(len(case["activities"]) for case in cases)
    avg_activities = total_activities / len(cases) if cases else 0
    total_value = sum(case["OrderValue"] for case in cases)
    
    print(f"\nDataset Statistics:")
    print(f"  Total activities: {total_activities:,}")
    print(f"  Average activities per case: {avg_activities:.1f}")
    print(f"  Total order value: ${total_value:,.2f}")
    print(f"  Average order value: ${total_value/len(cases):,.2f}")
    
    # Payment method distribution
    payment_methods = {}
    for case in cases:
        method = case["PaymentMethod"]
        payment_methods[method] = payment_methods.get(method, 0) + 1
    
    print(f"\nPayment Method Distribution:")
    for method, count in sorted(payment_methods.items(), key=lambda x: x[1], reverse=True):
        print(f"  {method}: {count} ({count/len(cases)*100:.1f}%)")

if __name__ == "__main__":
    main()