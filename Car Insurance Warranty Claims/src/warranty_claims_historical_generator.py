#!/usr/bin/env python3
"""
Car Insurance Warranty Claims Process Mining Dataset Generator
Generates realistic automotive warranty claims data with embedded bottlenecks and fraud patterns
"""

import json
import csv
import random
import string
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional
import os

# Set random seed for reproducibility
random.seed(42)

# Configuration from specification
TOTAL_CASES = 1500
START_DATE = datetime(2024, 9, 1, 8, 0, 0)  # 3-month sample
END_DATE = datetime(2024, 11, 30, 18, 0, 0)
BUSINESS_START_HOUR = 8
BUSINESS_END_HOUR = 18
WORKING_DAYS = [0, 1, 2, 3, 4, 5]  # Mon-Sat (dealers open Saturdays)
COMPLETION_RATE = 0.92  # 92% of cases complete
STRAIGHT_THROUGH_RATE = 0.40  # 40% auto-approved
FRAUD_INJECTION_RATE = 0.035  # 3.5% fraud patterns

# Resource pools with bottleneck resources identified
RESOURCES = {
    "dealer_rep": ["DealerRep1", "DealerRep2", "DealerRep3", "OnlinePortal"],
    "coverage_analyst": ["CoverageAnalyst1", "CoverageAnalyst2", "CoverageAnalyst3", "AutoValidator"],
    "dealer_tech": ["DealerTech1", "DealerTech2", "DealerTech3", "DealerTech4"],
    "parts_specialist": ["PartsSpecialist1", "PartsSpecialist2", "PartsSpecialist3", "PartsCatalog"],
    "labor_analyst": ["LaborAnalyst1", "LaborAnalyst2", "LaborAnalyst3"],
    "tech_expert": ["TechExpert1", "TechExpert2", "SeniorReviewer"],
    "fraud_analyst": ["FraudAnalyst", "RiskTeam", "AutoFraudSystem"],
    "approval_manager": ["ApprovalManager", "AutoApproval", "SeniorApprover"],
    "denial_specialist": ["DenialSpecialist", "Manager", "AutoDenial"],
    "payment_processor": ["PaymentProcessor", "FinanceTeam", "AutoPayment"],
    "quality_auditor": ["QualityAuditor", "SeniorAuditor", "ComplianceTeam"]
}

# Performance factors for bottleneck resources (1.0 = normal, <1.0 = slower)
PERFORMANCE_FACTORS = {
    "DealerTech3": 0.6,      # Slow dealer diagnosis
    "LaborAnalyst1": 0.7,    # Labor review delays
    "TechExpert1": 0.5,      # Technical review backlog
    "FraudAnalyst": 0.6      # Fraud investigation queue
}

# Activity configuration with typical durations
ACTIVITIES = {
    "First Notice of Loss": {
        "resources": "dealer_rep",
        "duration_hours": 0.25,
        "mandatory": True
    },
    "Verify Coverage": {
        "resources": "coverage_analyst", 
        "duration_hours": 0.5,
        "mandatory": True
    },
    "Damage Assessment": {
        "resources": "dealer_tech",
        "duration_hours": (4, 24),
        "mandatory": False
    },
    "Request Documentation": {
        "resources": "parts_specialist",
        "duration_hours": (1, 2),
        "mandatory": False
    },
    "Liability Determination": {
        "resources": "labor_analyst",
        "duration_hours": (0.5, 1),
        "mandatory": False
    },
    "Claim Investigation": {
        "resources": "tech_expert",
        "duration_hours": (2, 6),
        "mandatory": False
    },
    "Assignment": {
        "resources": "fraud_analyst",
        "duration_hours": (1, 3),
        "mandatory": False
    },
    "Approve Settlement": {
        "resources": "approval_manager",
        "duration_hours": 0.25,
        "mandatory": False
    },
    "Resolution and Settlement": {
        "resources": "denial_specialist",
        "duration_hours": 0.5,
        "mandatory": False
    },
    "Payment Processing": {
        "resources": "payment_processor",
        "duration_hours": 0.25,
        "mandatory": False
    },
    "Generate Payment Confirmation": {
        "resources": "quality_auditor",
        "duration_hours": (2, 4),
        "mandatory": False
    },
    "Claim Closure": {
        "resources": "coverage_analyst",
        "duration_hours": (1, 3),
        "mandatory": False
    }
}

# Process flow probabilities from specification
FLOWS = {
    "First Notice of Loss": {
        "Verify Coverage": 1.0
    },
    "Verify Coverage": {
        "Damage Assessment": 0.55,
        "Approve Settlement": 0.40,  # Straight-through processing
        "Resolution and Settlement": 0.03,  # Immediate denial
        "Claim Closure": 0.02  # Incomplete submission
    },
    "Damage Assessment": {
        "Request Documentation": 0.85,
        "Liability Determination": 0.10,
        "Resolution and Settlement": 0.05
    },
    "Request Documentation": {
        "Liability Determination": 0.90,
        "Resolution and Settlement": 0.07,
        "Claim Closure": 0.03
    },
    "Liability Determination": {
        "Claim Investigation": 0.25,
        "Assignment": 0.15,
        "Approve Settlement": 0.55,
        "Resolution and Settlement": 0.05
    },
    "Claim Investigation": {
        "Assignment": 0.20,
        "Approve Settlement": 0.70,
        "Resolution and Settlement": 0.08,
        "Claim Closure": 0.02
    },
    "Assignment": {
        "Approve Settlement": 0.75,
        "Resolution and Settlement": 0.20,
        "Claim Closure": 0.05
    },
    "Approve Settlement": {
        "Payment Processing": 0.95,
        "Generate Payment Confirmation": 0.05
    },
    "Payment Processing": {
        "Generate Payment Confirmation": 0.10
    },
    "Claim Closure": {
        "Verify Coverage": 0.60,
        "Damage Assessment": 0.30,
        "Resolution and Settlement": 0.10
    }
}

# Closing activities that end the process
CLOSING_ACTIVITIES = ["Approve Settlement", "Resolution and Settlement", "Payment Processing", "Claim Closure"]

# Case attribute distributions from specification
VEHICLE_MAKES = ["Ford", "Chevrolet", "Toyota", "Honda", "Nissan", "BMW", "Mercedes", "Audi", "Volkswagen", "Hyundai", "Kia", "Mazda", "Subaru", "Jeep", "Ram"]
VEHICLE_MAKE_DIST = [0.15, 0.14, 0.12, 0.10, 0.08, 0.05, 0.04, 0.04, 0.04, 0.06, 0.05, 0.03, 0.03, 0.04, 0.03]

CONTRACT_TYPES = ["DOWC", "TransmissionPlus", "TechShield", "PremiumCare", "BasicWarranty"]
CONTRACT_TYPE_DIST = [0.25, 0.20, 0.20, 0.15, 0.20]

DEALER_REGIONS = ["Northeast", "Southeast", "Midwest", "Southwest", "West"]
DEALER_REGION_DIST = [0.20, 0.25, 0.20, 0.15, 0.20]

CUSTOMER_STATES = ["CA", "TX", "FL", "NY", "PA", "IL", "OH", "GA", "NC", "MI", "Other"]
CUSTOMER_STATE_DIST = [0.12, 0.10, 0.08, 0.07, 0.06, 0.05, 0.05, 0.04, 0.04, 0.04, 0.35]

CUSTOMER_TYPES = ["Individual", "Fleet", "Rental"]
CUSTOMER_TYPE_DIST = [0.75, 0.15, 0.10]

PRIOR_CLAIMS_DIST = [0.60, 0.25, 0.10, 0.03, 0.01, 0.01]

# Event-level attribute distributions
SYSTEM_USED = ["System1_Legacy", "System2_SAP", "System3_Cloud", "System4_Manual"]
SYSTEM_DIST = [0.25, 0.30, 0.20, 0.25]

DIAGNOSIS_CODES = ["ENG001", "TRANS002", "ELEC003", "SUSP004", "BRAKE005", "AC006", "OTHER"]
DIAGNOSIS_CODE_DIST = [0.25, 0.20, 0.15, 0.10, 0.10, 0.10, 0.10]

APPROVAL_LEVELS = ["Auto", "Level1", "Level2", "Manager"]
APPROVAL_LEVEL_DIST = [0.40, 0.35, 0.20, 0.05]

DENIAL_REASONS = ["NotCovered", "ExceedsLimit", "FraudSuspected", "IncompleteInfo", "PreExisting", "OutOfWarranty"]
DENIAL_REASON_DIST = [0.30, 0.20, 0.15, 0.15, 0.10, 0.10]

FRAUD_INDICATORS = ["DuplicateVIN", "ExcessiveLabor", "UnusualParts", "DealerAnomaly", "Multiple", "None"]
FRAUD_INDICATOR_DIST = [0.10, 0.15, 0.10, 0.10, 0.05, 0.50]

PAYMENT_METHODS = ["ACH", "Check", "Wire", "Credit"]
PAYMENT_METHOD_DIST = [0.60, 0.25, 0.10, 0.05]

AUDIT_RESULTS = ["Pass", "MinorIssue", "MajorIssue", "RequiresReview"]
AUDIT_RESULT_DIST = [0.70, 0.20, 0.07, 0.03]

REWORK_REASONS = ["MissingDocs", "IncorrectParts", "LaborDispute", "VerificationNeeded"]
REWORK_REASON_DIST = [0.40, 0.25, 0.20, 0.15]

PRIORITY_VALUES = ["Normal", "High", "Urgent"]
PRIORITY_DIST = [0.70, 0.25, 0.05]

# Fraud patterns for injection
DUPLICATE_VINS = set()
EXCESSIVE_LABOR_CASES = set()
DEALER_ANOMALY_CASES = set()

def generate_vin() -> str:
    """Generate a realistic 17-character VIN"""
    return ''.join([
        random.choice(string.ascii_uppercase),
        random.choice(string.ascii_uppercase + string.digits),
        random.choice(string.ascii_uppercase + string.digits),
        random.choice(string.ascii_uppercase + string.digits),
        random.choice(string.ascii_uppercase + string.digits),
        random.choice(string.digits),
        random.choice(string.ascii_uppercase + string.digits),
        random.choice(string.digits),
        random.choice(string.ascii_uppercase + string.digits),
        random.choice(string.ascii_uppercase + string.digits),
        random.choice(string.digits * 6),  # Last 6 are usually numeric
        random.choice(string.digits * 6),
        random.choice(string.digits * 6),
        random.choice(string.digits * 6),
        random.choice(string.digits * 6),
        random.choice(string.digits * 6),
        random.choice(string.digits * 6)
    ])

def is_business_time(dt: datetime) -> bool:
    """Check if datetime is within business hours"""
    if dt.weekday() not in WORKING_DAYS:
        return False
    if dt.hour < BUSINESS_START_HOUR or dt.hour >= BUSINESS_END_HOUR:
        return False
    return True

def add_business_hours(start_dt: datetime, hours: float, resource: str = "") -> datetime:
    """Add hours considering business hours and resource performance"""
    # Apply performance factor for bottleneck resources
    if resource in PERFORMANCE_FACTORS:
        hours = hours / PERFORMANCE_FACTORS[resource]
    
    current = start_dt
    remaining_hours = hours
    
    while remaining_hours > 0:
        if is_business_time(current):
            increment = min(remaining_hours, 1.0)
            current += timedelta(hours=increment)
            remaining_hours -= increment
        else:
            # Jump to next business hour
            if current.hour >= BUSINESS_END_HOUR or current.weekday() not in WORKING_DAYS:
                # Find next business day
                current += timedelta(days=1)
                while current.weekday() not in WORKING_DAYS:
                    current += timedelta(days=1)
                current = current.replace(hour=BUSINESS_START_HOUR, minute=0, second=0)
            else:
                current = current.replace(hour=BUSINESS_START_HOUR, minute=0, second=0)
    
    return current

def select_weighted_random(options: List, weights: List) -> Any:
    """Select random option based on weights"""
    return random.choices(options, weights=weights)[0]

def generate_case_attributes(case_id: int, fraud_pattern: Optional[str] = None) -> Dict[str, Any]:
    """Generate case-level attributes"""
    vin = generate_vin()
    
    # Handle duplicate VIN fraud pattern
    if fraud_pattern == "duplicate_vin":
        if len(DUPLICATE_VINS) > 0:
            vin = random.choice(list(DUPLICATE_VINS))
        else:
            DUPLICATE_VINS.add(vin)
    else:
        if random.random() < 0.02:  # 2% chance of duplicate VIN
            DUPLICATE_VINS.add(vin)
    
    make = select_weighted_random(VEHICLE_MAKES, VEHICLE_MAKE_DIST)
    year = random.randint(2019, 2024)
    
    # Generate model based on make
    models = {
        "Ford": ["F-150", "Mustang", "Explorer", "Escape", "Edge"],
        "Chevrolet": ["Silverado", "Camaro", "Equinox", "Malibu", "Cruze"],
        "Toyota": ["Camry", "Corolla", "RAV4", "Highlander", "Prius"],
        "Honda": ["Civic", "Accord", "CR-V", "Pilot", "Fit"],
        "Nissan": ["Altima", "Sentra", "Rogue", "Pathfinder", "370Z"]
    }
    model = random.choice(models.get(make, ["Model_X", "Model_Y", "Model_Z"]))
    
    # Generate other attributes
    mileage = int(random.lognormvariate(10.5, 0.5))  # Right-skewed distribution
    mileage = max(5000, min(150000, mileage))
    
    contract_type = select_weighted_random(CONTRACT_TYPES, CONTRACT_TYPE_DIST)
    dealer_region = select_weighted_random(DEALER_REGIONS, DEALER_REGION_DIST)
    customer_state = select_weighted_random(CUSTOMER_STATES, CUSTOMER_STATE_DIST)
    customer_type = select_weighted_random(CUSTOMER_TYPES, CUSTOMER_TYPE_DIST)
    
    # Claim value - higher for fleet/rental
    if customer_type == "Fleet":
        claim_value = int(random.lognormvariate(8.0, 0.8)) * 1.2
    elif customer_type == "Rental":
        claim_value = int(random.lognormvariate(8.0, 0.8)) * 1.1
    else:
        claim_value = int(random.lognormvariate(8.0, 0.8))
    claim_value = max(150, min(15000, claim_value))
    
    prior_claims = select_weighted_random(list(range(6)), PRIOR_CLAIMS_DIST)
    days_in_service = random.randint(180, 2190)
    
    # Fraud score - higher for fraud patterns
    if fraud_pattern:
        fraud_score = random.betavariate(5, 2)  # Higher fraud scores
    else:
        fraud_score = random.betavariate(2, 5)  # Lower fraud scores
    
    # Generate dealer name based on region
    dealer_prefixes = ["Auto", "Premier", "Elite", "Superior", "Quality", "Expert"]
    dealer_suffixes = ["Motors", "Automotive", "Service", "Repair", "Center"]
    dealer_name = f"{random.choice(dealer_prefixes)} {random.choice(dealer_suffixes)} ({dealer_region})"
    
    return {
        "ClaimNumber": f"CLM2024_{case_id:06d}",
        "VIN": vin,
        "VehicleMake": make,
        "VehicleModel": model,
        "VehicleYear": year,
        "Mileage": mileage,
        "ContractType": contract_type,
        "DealerName": dealer_name,
        "DealerRegion": dealer_region,
        "CustomerState": customer_state,
        "ClaimValue": claim_value,
        "CustomerType": customer_type,
        "PriorClaims": prior_claims,
        "DaysInService": days_in_service,
        "PredictedFraudScore": round(fraud_score, 3)
    }

def generate_event_attributes(activity_name: str, resource: str, case_attrs: Dict) -> Dict[str, Any]:
    """Generate event-level attributes for an activity"""
    attrs = {
        "SystemUsed": select_weighted_random(SYSTEM_USED, SYSTEM_DIST)
    }
    
    # Activity-specific attributes
    if activity_name in ["First Notice of Loss", "Damage Assessment"]:
        attrs["DealerRepairOrderNumber"] = f"RO-{random.randint(10000, 99999)}"
    
    if activity_name == "Damage Assessment":
        attrs["DiagnosisCode"] = select_weighted_random(DIAGNOSIS_CODES, DIAGNOSIS_CODE_DIST)
    
    if activity_name == "Request Documentation":
        parts_count = select_weighted_random(list(range(1, 9)), [0.40, 0.25, 0.15, 0.10, 0.05, 0.03, 0.01, 0.01])
        parts_value = int(random.lognormvariate(6.5, 0.8))
        parts_value = max(50, min(5000, parts_value))
        attrs["PartsCount"] = parts_count
        attrs["PartsValue"] = parts_value
    
    if activity_name == "Liability Determination":
        labor_claimed = max(0.5, random.normalvariate(3.5, 1.5))
        labor_claimed = min(12, labor_claimed)
        
        # Excessive labor for fraud pattern
        if case_attrs["ClaimNumber"] in EXCESSIVE_LABOR_CASES:
            labor_claimed *= 1.8  # 80% more labor
        
        labor_approved = labor_claimed * random.uniform(0.85, 1.0)
        labor_rate = random.randint(75, 150)
        
        attrs["LaborHoursClaimed"] = round(labor_claimed, 1)
        attrs["LaborHoursApproved"] = round(labor_approved, 1)
        attrs["LaborRate"] = labor_rate
    
    if activity_name == "Approve Settlement":
        attrs["ApprovalLevel"] = select_weighted_random(APPROVAL_LEVELS, APPROVAL_LEVEL_DIST)
    
    if activity_name == "Resolution and Settlement":
        attrs["DenialReason"] = select_weighted_random(DENIAL_REASONS, DENIAL_REASON_DIST)
    
    if activity_name == "Assignment":
        fraud_score = random.randint(0, 100)
        if case_attrs["PredictedFraudScore"] > 0.7:
            fraud_score = random.randint(60, 100)
        attrs["FraudScore"] = fraud_score
        attrs["FraudIndicators"] = select_weighted_random(FRAUD_INDICATORS, FRAUD_INDICATOR_DIST)
    
    if activity_name == "Payment Processing":
        # Calculate payment amount (usually less than claim value)
        payment_amount = int(case_attrs["ClaimValue"] * random.uniform(0.7, 0.95))
        attrs["PaymentAmount"] = payment_amount
        attrs["PaymentMethod"] = select_weighted_random(PAYMENT_METHODS, PAYMENT_METHOD_DIST)
    
    if activity_name == "Generate Payment Confirmation":
        attrs["AuditResult"] = select_weighted_random(AUDIT_RESULTS, AUDIT_RESULT_DIST)
        if random.random() < 0.5:
            sample_notes = [
                "All documentation complete", 
                "Minor discrepancy in parts pricing", 
                "Labor hours need verification", 
                "Potential duplicate claim"
            ]
            attrs["AuditNotes"] = random.choice(sample_notes)
    
    if activity_name == "Claim Closure":
        attrs["ReworkReason"] = select_weighted_random(REWORK_REASONS, REWORK_REASON_DIST)
    
    # Optional attributes
    if random.random() < 0.3:
        attrs["Priority"] = select_weighted_random(PRIORITY_VALUES, PRIORITY_DIST)
    
    if activity_name in ["Verify Coverage", "Claim Investigation", "Assignment"] and random.random() < 0.4:
        sample_notes = [
            "Standard claim", 
            "High value - requires review", 
            "Suspicious pattern detected", 
            "Previous claims on VIN", 
            "Dealer under investigation"
        ]
        attrs["ProcessingNotes"] = random.choice(sample_notes)
    
    return attrs

def get_next_activity(current_activity: str, rework_count: int = 0) -> Optional[str]:
    """Determine next activity based on flow probabilities"""
    if current_activity not in FLOWS:
        return None
    
    # Limit rework loops
    if current_activity == "Claim Closure" and rework_count >= 2:
        return "Resolution and Settlement"
    
    next_activities = list(FLOWS[current_activity].keys())
    probabilities = list(FLOWS[current_activity].values())
    
    return select_weighted_random(next_activities, probabilities)

def generate_activity_duration(activity_name: str) -> float:
    """Generate realistic duration for activity"""
    config = ACTIVITIES[activity_name]
    duration = config["duration_hours"]
    
    if isinstance(duration, tuple):
        return random.uniform(duration[0], duration[1])
    else:
        return duration * random.uniform(0.8, 1.4)  # Add some variation

def select_resource(activity_name: str) -> str:
    """Select resource for activity"""
    config = ACTIVITIES[activity_name]
    resource_pool = RESOURCES[config["resources"]]
    return random.choice(resource_pool)

def generate_case(case_id: int, start_date: datetime) -> Dict[str, Any]:
    """Generate a complete case with activities"""
    # Determine fraud pattern
    fraud_pattern = None
    if random.random() < FRAUD_INJECTION_RATE:
        patterns = ["duplicate_vin", "excessive_labor", "dealer_anomaly"]
        fraud_pattern = random.choice(patterns)
        
        if fraud_pattern == "excessive_labor":
            EXCESSIVE_LABOR_CASES.add(f"CLM2024_{case_id:06d}")
        elif fraud_pattern == "dealer_anomaly":
            DEALER_ANOMALY_CASES.add(f"CLM2024_{case_id:06d}")
    
    # Generate case attributes
    case_attrs = generate_case_attributes(case_id, fraud_pattern)
    
    # Generate activities
    activities = []
    current_activity = "First Notice of Loss"
    current_time = start_date
    rework_count = 0
    activity_count = 0
    
    while current_activity and activity_count < 20:  # Prevent infinite loops
        resource = select_resource(current_activity)
        duration = generate_activity_duration(current_activity)
        
        # Create activity
        activity = {
            "ActivityName": current_activity,
            "ActivityTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Resource": resource
        }
        
        # Add event-level attributes
        event_attrs = generate_event_attributes(current_activity, resource, case_attrs)
        activity.update(event_attrs)
        
        activities.append(activity)
        
        # Check if this is a closing activity
        if current_activity in CLOSING_ACTIVITIES:
            # 92% completion rate
            if random.random() < COMPLETION_RATE:
                break
        
        # Move to next activity
        next_activity = get_next_activity(current_activity, rework_count)
        if next_activity:
            # Calculate next activity time
            current_time = add_business_hours(current_time, duration, resource)
            
            # Track rework
            if next_activity == "Verify Coverage" and current_activity == "Claim Closure":
                rework_count += 1
            
            current_activity = next_activity
        else:
            break
        
        activity_count += 1
    
    return {
        "CaseId": case_attrs["ClaimNumber"],
        **case_attrs,
        "activities": activities
    }

def generate_dataset() -> List[Dict[str, Any]]:
    """Generate the complete dataset"""
    print(f"Generating {TOTAL_CASES} warranty claims cases...")
    
    cases = []
    current_date = START_DATE
    cases_per_day = TOTAL_CASES // ((END_DATE - START_DATE).days + 1)
    
    case_id = 1
    while current_date <= END_DATE and case_id <= TOTAL_CASES:
        # Generate cases for this day
        daily_cases = cases_per_day
        if current_date.weekday() == 0:  # Monday - higher volume
            daily_cases = int(daily_cases * 1.2)
        elif current_date.weekday() == 5:  # Saturday - lower volume
            daily_cases = int(daily_cases * 0.8)
        
        for _ in range(min(daily_cases, TOTAL_CASES - case_id + 1)):
            # Vary start time throughout the day
            start_time = current_date.replace(
                hour=random.randint(8, 16),
                minute=random.randint(0, 59),
                second=random.randint(0, 59)
            )
            
            case = generate_case(case_id, start_time)
            cases.append(case)
            case_id += 1
            
            if case_id > TOTAL_CASES:
                break
        
        current_date += timedelta(days=1)
    
    print(f"Generated {len(cases)} cases")
    print(f"Fraud patterns injected: {len(DUPLICATE_VINS)} duplicate VINs, {len(EXCESSIVE_LABOR_CASES)} excessive labor, {len(DEALER_ANOMALY_CASES)} dealer anomalies")
    
    return cases

def save_to_json(cases: List[Dict[str, Any]], output_dir: str):
    """Save cases to JSON format"""
    filepath = os.path.join(output_dir, "warranty_claims_historical.json")
    with open(filepath, 'w') as f:
        json.dump({"cases": cases}, f, indent=2)
    print(f"Saved JSON to {filepath}")

def save_to_csv(cases: List[Dict[str, Any]], output_dir: str):
    """Save cases to CSV format (flattened event log)"""
    filepath = os.path.join(output_dir, "warranty_claims_historical.csv")
    
    # Determine all possible fields by scanning ALL cases and activities
    fieldnames = ["CaseId", "ActivityName", "ActivityTime", "Resource"]
    
    # Add case attributes
    if cases:
        sample_case = cases[0]
        case_fields = [k for k in sample_case.keys() if k not in ["CaseId", "activities"]]
        fieldnames.extend(case_fields)
        
        # Add ALL possible event attributes by scanning all cases
        event_fields = set()
        for case in cases:  # Scan ALL cases, not just first 10
            for activity in case["activities"]:
                event_fields.update([k for k in activity.keys() 
                                   if k not in ["ActivityName", "ActivityTime", "Resource"]])
        fieldnames.extend(sorted(event_fields))
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for case in cases:
            case_data = {k: v for k, v in case.items() if k != "activities"}
            
            for activity in case["activities"]:
                row = case_data.copy()
                row.update(activity)
                writer.writerow(row)
    
    print(f"Saved CSV to {filepath}")

def main():
    """Main function to generate and save dataset"""
    # Ensure output directory exists
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate dataset
    cases = generate_dataset()
    
    # Save in both formats
    save_to_json(cases, output_dir)
    save_to_csv(cases, output_dir)
    
    # Print summary statistics
    total_activities = sum(len(case["activities"]) for case in cases)
    completed_cases = sum(1 for case in cases 
                         if any(act["ActivityName"] in CLOSING_ACTIVITIES 
                               for act in case["activities"]))
    # Count straight-through processing (Verify Coverage → Approve Settlement directly)
    straight_through = 0
    for case in cases:
        activities = [act["ActivityName"] for act in case["activities"]]
        if (len(activities) >= 3 and 
            activities[0] == "First Notice of Loss" and
            activities[1] == "Verify Coverage" and 
            activities[2] == "Approve Settlement"):
            straight_through += 1
    
    print(f"\nDataset Statistics:")
    print(f"Total cases: {len(cases)}")
    print(f"Total activities: {total_activities}")
    print(f"Average activities per case: {total_activities/len(cases):.1f}")
    print(f"Completion rate: {completed_cases/len(cases)*100:.1f}%")
    print(f"Straight-through processing: {straight_through/len(cases)*100:.1f}%")

if __name__ == "__main__":
    main()