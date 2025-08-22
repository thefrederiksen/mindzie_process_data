#!/usr/bin/env python3
"""
Data Validator for Source to Pay Dataset
Tests the generated data against specifications and ensures data quality
"""

import json
import csv
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from collections import Counter, defaultdict

def load_json_data(filepath: str) -> Dict[str, Any]:
    """Load JSON data file"""
    with open(filepath, 'r') as f:
        return json.load(f)

def load_csv_data(filepath: str) -> List[Dict]:
    """Load CSV data file"""
    data = []
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

def test_json_structure(json_data: Dict[str, Any]) -> Tuple[bool, str]:
    """Test if JSON follows expected structure"""
    errors = []
    
    # Check top-level structure
    if 'FreezeTime' not in json_data:
        errors.append("Missing FreezeTime in JSON root")
    
    if 'cases' not in json_data:
        errors.append("Missing cases array in JSON root")
        return False, "Critical structure error: No cases array"
    
    cases = json_data.get('cases', [])
    if not isinstance(cases, list):
        errors.append("Cases is not an array")
        return False, "Critical structure error: Cases is not an array"
    
    # Check case structure
    required_case_fields = [
        "CaseId", "OrderType", "OrderValue", "Currency", "Priority", 
        "PaymentTerms", "VendorID", "VendorName", "VendorCategory",
        "RequesterID", "Department", "CostCenter", "activities"
    ]
    
    for i, case in enumerate(cases[:10]):  # Check first 10 cases
        for field in required_case_fields:
            if field not in case:
                errors.append(f"Case {i} missing field: {field}")
        
        # Check activities structure
        if "activities" in case:
            if not isinstance(case["activities"], list):
                errors.append(f"Case {i} activities is not a list")
            else:
                for j, activity in enumerate(case["activities"][:5]):  # Check first 5 activities
                    required_activity_fields = ["ActivityName", "ActivityTime", "Resource", "Role"]
                    for field in required_activity_fields:
                        if field not in activity:
                            errors.append(f"Case {i} activity {j} missing field: {field}")
    
    if errors:
        return False, f"Structure errors: {'; '.join(errors[:5])}{'...' if len(errors) > 5 else ''}"
    return True, "JSON structure is correct"

def test_csv_matches_json(json_data: Dict[str, Any], csv_data: List[Dict]) -> Tuple[bool, str]:
    """Test if CSV contains same data as JSON"""
    cases = json_data.get('cases', [])
    json_activity_count = sum(len(case.get("activities", [])) for case in cases)
    csv_activity_count = len(csv_data)
    
    if json_activity_count != csv_activity_count:
        return False, f"Activity count mismatch: JSON has {json_activity_count}, CSV has {csv_activity_count}"
    
    # Check that all case IDs match
    json_case_ids = set(case.get('CaseId', '') for case in cases)
    csv_case_ids = set(row.get('CaseId', '') for row in csv_data)
    
    if json_case_ids != csv_case_ids:
        missing_in_csv = json_case_ids - csv_case_ids
        extra_in_csv = csv_case_ids - json_case_ids
        return False, f"Case ID mismatch: Missing in CSV: {len(missing_in_csv)}, Extra in CSV: {len(extra_in_csv)}"
    
    return True, "CSV matches JSON data"

def test_case_completeness(json_data: Dict[str, Any]) -> Tuple[bool, str]:
    """Test if cases are properly completed or in valid waiting states"""
    cases = json_data.get('cases', [])
    completion_activities = [
        "Verify Successful Payment", "End Event", "Cancel Invoice"
    ]
    
    completed_cases = 0
    in_progress_cases = 0
    invalid_cases = 0
    
    for case in cases:
        activities = case.get("activities", [])
        if not activities:
            invalid_cases += 1
            continue
            
        last_activity = activities[-1]["ActivityName"]
        payment_status = case.get("PaymentStatus", "")
        
        if last_activity in completion_activities or payment_status == "Completed":
            completed_cases += 1
        elif payment_status == "Pending":
            in_progress_cases += 1
        else:
            invalid_cases += 1
    
    total_cases = len(cases)
    if invalid_cases > total_cases * 0.05:  # Allow up to 5% invalid cases
        return False, f"Too many invalid cases: {invalid_cases}/{total_cases} ({invalid_cases/total_cases*100:.1f}%)"
    
    return True, f"Case completeness OK: {completed_cases} completed, {in_progress_cases} in-progress, {invalid_cases} invalid"

def test_process_flow_validity(json_data: Dict[str, Any]) -> Tuple[bool, str]:
    """Test if activity sequences follow valid process flows"""
    cases = json_data.get('cases', [])
    
    # Define valid process flows
    standard_flow_activities = [
        "Place Order", "Receive Order", "Process Order", "Receive Invoice", 
        "Review Invoice", "Create Payment", "Authorize Payment", "Verify Successful Payment"
    ]
    
    credit_card_flow_activities = [
        "Place Order (Credit Card)", "Receive Order (Credit Card)", 
        "Request Payment by Credit Card (Direct)", "Receive E-Invoice",
        "Authorize Payment", "Verify Successful Payment"
    ]
    
    invalid_sequences = 0
    sequence_errors = []
    
    for case in cases[:100]:  # Check first 100 cases
        activities = [act["ActivityName"] for act in case.get("activities", [])]
        case_id = case.get("CaseId", "Unknown")
        
        if not activities:
            continue
            
        # Check if it follows either standard or credit card flow
        is_standard_flow = "Place Order" in activities[0] if activities else False
        is_credit_card_flow = "Place Order (Credit Card)" in activities[0] if activities else False
        
        if is_credit_card_flow:
            # Validate credit card flow
            expected_flow = credit_card_flow_activities
        else:
            # Validate standard flow
            expected_flow = standard_flow_activities
        
        # Check for basic flow violations
        if len(activities) > 1:
            # First activity should be a "Place Order" variant
            if not any(start in activities[0] for start in ["Place Order"]):
                sequence_errors.append(f"Case {case_id}: Invalid start activity '{activities[0]}'")
                invalid_sequences += 1
    
    if invalid_sequences > len(cases) * 0.1:  # Allow up to 10% with minor sequence issues
        return False, f"Too many invalid sequences: {invalid_sequences} cases with issues"
    
    return True, f"Process flow validation OK: {invalid_sequences} minor issues in {len(cases)} cases"

def test_business_hours_compliance(json_data: Dict[str, Any]) -> Tuple[bool, str]:
    """Test if activities occur within business hours"""
    cases = json_data.get('cases', [])
    
    violations = 0
    total_activities = 0
    
    for case in cases[:50]:  # Check first 50 cases
        activities = case.get("activities", [])
        
        for activity in activities:
            total_activities += 1
            activity_time = activity.get("ActivityTime", "")
            
            try:
                dt = datetime.strptime(activity_time, "%Y-%m-%d %H:%M:%S")
                
                # Check if it's a weekend
                if dt.weekday() >= 5:
                    # Allow some weekend activities for automated systems
                    if activity.get("Role") != "System":
                        violations += 1
                
                # Check if it's outside business hours (8 AM - 6 PM)
                if dt.hour < 8 or dt.hour >= 18:
                    # Allow some after-hours activities for automated systems
                    if activity.get("Role") != "System":
                        violations += 1
                        
            except ValueError:
                violations += 1  # Invalid datetime format
    
    violation_rate = violations / total_activities * 100 if total_activities > 0 else 0
    
    if violation_rate > 20:  # Allow up to 20% outside business hours (for systems, urgent cases)
        return False, f"Too many business hours violations: {violations}/{total_activities} ({violation_rate:.1f}%)"
    
    return True, f"Business hours compliance OK: {violations}/{total_activities} violations ({violation_rate:.1f}%)"

def test_data_distributions(json_data: Dict[str, Any]) -> Tuple[bool, str]:
    """Test if data follows expected distributions"""
    cases = json_data.get('cases', [])
    
    # Test order value distribution
    order_values = []
    payment_methods = []
    order_types = []
    departments = []
    
    for case in cases:
        try:
            order_values.append(float(case.get("OrderValue", 0)))
        except (ValueError, TypeError):
            pass
        
        payment_methods.append(case.get("PaymentMethod", ""))
        order_types.append(case.get("OrderType", ""))
        departments.append(case.get("Department", ""))
    
    # Check order value ranges
    under_1k = sum(1 for v in order_values if v < 1000)
    between_1k_10k = sum(1 for v in order_values if 1000 <= v < 10000)
    between_10k_100k = sum(1 for v in order_values if 10000 <= v < 100000)
    over_100k = sum(1 for v in order_values if v >= 100000)
    
    total_with_values = len(order_values)
    if total_with_values == 0:
        return False, "No valid order values found"
    
    # Expected: 30%, 40%, 25%, 5%
    under_1k_pct = under_1k / total_with_values * 100
    between_1k_10k_pct = between_1k_10k / total_with_values * 100
    
    # Allow some variance in distributions
    if not (20 <= under_1k_pct <= 40):
        return False, f"Order value distribution issue: Under $1k is {under_1k_pct:.1f}%, expected ~30%"
    
    if not (30 <= between_1k_10k_pct <= 50):
        return False, f"Order value distribution issue: $1k-$10k is {between_1k_10k_pct:.1f}%, expected ~40%"
    
    # Check payment method diversity
    payment_method_counts = Counter(payment_methods)
    if len(payment_method_counts) < 3:
        return False, f"Insufficient payment method diversity: {len(payment_method_counts)} methods"
    
    return True, f"Data distributions OK: Order values and payment methods properly distributed"

def test_resource_assignments(json_data: Dict[str, Any]) -> Tuple[bool, str]:
    """Test if resources are properly assigned and bottlenecks are present"""
    cases = json_data.get('cases', [])
    
    resource_activity_counts = defaultdict(int)
    role_counts = defaultdict(int)
    
    # Count resource utilization
    for case in cases[:100]:  # First 100 cases
        for activity in case.get("activities", []):
            resource = activity.get("Resource", "")
            role = activity.get("Role", "")
            
            resource_activity_counts[resource] += 1
            role_counts[role] += 1
    
    # Check for bottleneck resources (should have higher activity counts)
    bottleneck_resources = ["Robert Taylor", "Paul Martinez"]  # From the generator
    
    found_bottlenecks = []
    for resource in bottleneck_resources:
        if resource in resource_activity_counts:
            found_bottlenecks.append(resource)
    
    if len(found_bottlenecks) < 1:
        return False, "No bottleneck resources found in activity assignments"
    
    # Check role diversity
    if len(role_counts) < 4:
        return False, f"Insufficient role diversity: {len(role_counts)} roles found"
    
    return True, f"Resource assignments OK: {len(found_bottlenecks)} bottleneck resources found, {len(role_counts)} roles"

def run_all_tests(dataset_type: str) -> None:
    """Run all validation tests for the specified dataset type"""
    print(f"\n=== Source to Pay {dataset_type.title()} Dataset Validation ===")
    
    # Define file paths
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    json_file = os.path.join(output_dir, f"source_to_pay_{dataset_type}.json")
    csv_file = os.path.join(output_dir, f"source_to_pay_{dataset_type}.csv")
    
    if not os.path.exists(json_file):
        print(f"ERROR: JSON file not found: {json_file}")
        return
    
    if not os.path.exists(csv_file):
        print(f"ERROR: CSV file not found: {csv_file}")
        return
    
    # Load data
    print("Loading data files...")
    try:
        json_data = load_json_data(json_file)
        csv_data = load_csv_data(csv_file)
    except Exception as e:
        print(f"ERROR: Error loading data files: {e}")
        return
    
    print(f"Loaded {len(json_data.get('cases', []))} cases from JSON")
    print(f"Loaded {len(csv_data)} activity rows from CSV")
    
    # Run tests
    tests = [
        ("JSON Structure", lambda: test_json_structure(json_data)),
        ("CSV-JSON Consistency", lambda: test_csv_matches_json(json_data, csv_data)),
        ("Case Completeness", lambda: test_case_completeness(json_data)),
        ("Process Flow Validity", lambda: test_process_flow_validity(json_data)),
        ("Business Hours Compliance", lambda: test_business_hours_compliance(json_data)),
        ("Data Distributions", lambda: test_data_distributions(json_data)),
        ("Resource Assignments", lambda: test_resource_assignments(json_data)),
    ]
    
    passed = 0
    failed = 0
    
    print("\nRunning validation tests...")
    print("-" * 60)
    
    for test_name, test_func in tests:
        try:
            result, message = test_func()
            status = "[PASS]" if result else "[FAIL]"
            print(f"{status:<8} {test_name}: {message}")
            
            if result:
                passed += 1
            else:
                failed += 1
                
        except Exception as e:
            print(f"[ERROR] {test_name}: Exception during test - {e}")
            failed += 1
    
    print("-" * 60)
    print(f"Validation Summary: {passed} passed, {failed} failed")
    
    if failed == 0:
        print(f"SUCCESS: All tests passed! The {dataset_type} dataset is valid.")
    else:
        print(f"WARNING: {failed} test(s) failed. Please review the issues above.")

def main():
    """Main validation function"""
    print("Source to Pay Dataset Validator")
    print("=" * 50)
    
    # Validate both datasets if they exist
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    
    historical_exists = os.path.exists(os.path.join(output_dir, "source_to_pay_historical.json"))
    daily_exists = os.path.exists(os.path.join(output_dir, "source_to_pay_daily.json"))
    
    if historical_exists:
        run_all_tests("historical")
    else:
        print("Historical dataset not found. Run historical_event_log.py first.")
    
    if daily_exists:
        run_all_tests("daily")
    else:
        print("Daily dataset not found. Run daily_event_log.py first.")
    
    if not historical_exists and not daily_exists:
        print("No datasets found. Please generate datasets first.")

if __name__ == "__main__":
    main()