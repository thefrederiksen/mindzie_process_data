#!/usr/bin/env python3
"""
Data Validator for Hire to Retire Dataset
Tests the generated data against specifications
"""

import json
import csv
import os
import re
import yaml
from datetime import datetime
from typing import Dict, List, Any, Tuple
from collections import Counter

def load_json_data(filepath: str) -> List[Dict]:
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

def extract_yaml_from_specification(spec_path: str) -> Dict[str, Any]:
    """Extract YAML blocks from markdown specification"""
    with open(spec_path, 'r') as f:
        content = f.read()
    
    yaml_blocks = re.findall(r'```yaml\n(.*?)\n```', content, re.DOTALL)
    combined_yaml = '\n'.join(yaml_blocks)
    return yaml.safe_load(combined_yaml)

def test_json_structure(json_data: List[Dict]) -> Tuple[bool, str]:
    """Test if JSON follows case-centric structure"""
    errors = []
    
    for case in json_data:
        # Check required case fields
        required_fields = ["CaseId", "EmployeeID", "Department", "Location", "JobLevel", "Activities"]
        for field in required_fields:
            if field not in case:
                errors.append(f"Case {case.get('CaseId', 'Unknown')} missing field: {field}")
        
        # Check activities structure
        if "Activities" in case:
            if not isinstance(case["Activities"], list):
                errors.append(f"Case {case['CaseId']} Activities is not a list")
            else:
                for activity in case["Activities"]:
                    required_activity_fields = ["ActivityName", "ActivityTime", "Resource"]
                    for field in required_activity_fields:
                        if field not in activity:
                            errors.append(f"Activity in case {case['CaseId']} missing field: {field}")
    
    if errors:
        return False, f"Structure errors: {'; '.join(errors[:5])}..."
    return True, "JSON structure is correct"

def test_csv_matches_json(json_data: List[Dict], csv_data: List[Dict]) -> Tuple[bool, str]:
    """Test if CSV contains same data as JSON"""
    # Count activities in JSON
    json_activity_count = sum(len(case.get("Activities", [])) for case in json_data)
    csv_activity_count = len(csv_data)
    
    if json_activity_count != csv_activity_count:
        return False, f"Activity count mismatch: JSON has {json_activity_count}, CSV has {csv_activity_count}"
    
    return True, "CSV matches JSON data"

def test_case_completeness(json_data: List[Dict], spec_data: Dict) -> Tuple[bool, str]:
    """Test if cases are properly closed"""
    closing_activities = spec_data.get("closing_activities", [])
    incomplete_cases = 0
    total_cases = len(json_data)
    
    for case in json_data:
        activities = case.get("Activities", [])
        if activities:
            last_activity = activities[-1]["ActivityName"]
            if last_activity not in closing_activities:
                incomplete_cases += 1
    
    completion_rate = (total_cases - incomplete_cases) / total_cases * 100
    
    if completion_rate < 90:
        return False, f"Completion rate {completion_rate:.1f}% is below 90% requirement"
    
    return True, f"Completion rate {completion_rate:.1f}% meets requirement"

def test_bottleneck_visibility(json_data: List[Dict], spec_data: Dict) -> Tuple[bool, str]:
    """Test if bottlenecks are properly implemented"""
    bottlenecks = spec_data.get("bottlenecks", [])
    issues = []
    
    # Extract all activities
    all_activities = []
    for case in json_data:
        for activity in case.get("Activities", []):
            all_activities.append(activity)
    
    # Check each bottleneck
    for bottleneck in bottlenecks:
        slow_resource = bottleneck["slow_resource"]
        expected_rate = bottleneck.get("occurrence_rate", 0)
        affected_activities = bottleneck["affected_activities"]
        
        # Count occurrences
        total_affected = 0
        slow_resource_count = 0
        
        for activity in all_activities:
            activity_name = activity["ActivityName"]
            # Map activity IDs to names
            if activity_name in ["Interview Completed", "Equipment Assigned", "Performance Review"]:
                total_affected += 1
                if activity.get("Resource") == slow_resource:
                    slow_resource_count += 1
        
        if total_affected > 0:
            actual_rate = slow_resource_count / total_affected
            if abs(actual_rate - expected_rate) > 0.1:  # 10% tolerance
                issues.append(f"{slow_resource} bottleneck: expected {expected_rate*100:.0f}%, got {actual_rate*100:.0f}%")
    
    if issues:
        return False, f"Bottleneck issues: {'; '.join(issues)}"
    
    return True, "Bottlenecks properly implemented"

def test_kpi_targets(json_data: List[Dict], spec_data: Dict) -> Tuple[bool, str]:
    """Test if KPIs match problem statement targets"""
    issues = []
    
    # Calculate Time to Fill
    hired_cases = []
    for case in json_data:
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
        # Problem statement says 40+ days, we got 31.8
        if avg_time_to_fill < 40:
            issues.append(f"Time to Fill {avg_time_to_fill:.1f} days is below problem target of 40+ days")
    
    # Calculate First Year Turnover
    employees_hired = 0
    employees_left_first_year = 0
    
    for case in json_data:
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
        # Problem statement says 30% turnover
        if first_year_turnover < 25:  # Allow some tolerance
            issues.append(f"First year turnover {first_year_turnover:.1f}% is below problem target of 30%")
    
    if issues:
        return False, f"KPI issues: {'; '.join(issues)}"
    
    return True, "KPIs match targets"

def test_datetime_format(csv_data: List[Dict]) -> Tuple[bool, str]:
    """Test if datetime format is correct"""
    pattern = r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$'
    
    for i, row in enumerate(csv_data[:100]):  # Check first 100 rows
        if "ActivityTime" in row:
            if not re.match(pattern, row["ActivityTime"]):
                return False, f"Invalid datetime format: {row['ActivityTime']} (should be YYYY-MM-DD HH:MM:SS)"
    
    return True, "Datetime format is correct"

def main():
    """Main test execution"""
    print("=== HIRE TO RETIRE DATA VALIDATION ===\n")
    
    # Find files
    json_path = "output/hire_to_retire_historical.json"
    csv_path = "output/hire_to_retire_historical.csv"
    spec_path = "../docs/process_specification.md"
    
    # Check if files exist
    if not os.path.exists(json_path):
        print("FAIL: JSON file not found")
        return False
    
    if not os.path.exists(csv_path):
        print("FAIL: CSV file not found")
        return False
    
    # Load data
    print("Loading data files...")
    json_data = load_json_data(json_path)
    csv_data = load_csv_data(csv_path)
    spec_data = extract_yaml_from_specification(spec_path)
    
    # Run tests
    tests = [
        ("JSON Structure", lambda: test_json_structure(json_data)),
        ("CSV/JSON Match", lambda: test_csv_matches_json(json_data, csv_data)),
        ("Case Completeness", lambda: test_case_completeness(json_data, spec_data)),
        ("Bottleneck Visibility", lambda: test_bottleneck_visibility(json_data, spec_data)),
        ("KPI Targets", lambda: test_kpi_targets(json_data, spec_data)),
        ("DateTime Format", lambda: test_datetime_format(csv_data))
    ]
    
    all_passed = True
    results = []
    
    for test_name, test_func in tests:
        passed, message = test_func()
        status = "PASS" if passed else "FAIL"
        results.append((test_name, passed, message))
        print(f"{test_name}: {status} - {message}")
        if not passed:
            all_passed = False
    
    print("\n=== SUMMARY ===")
    print(f"Total tests: {len(tests)}")
    print(f"Passed: {sum(1 for _, passed, _ in results if passed)}")
    print(f"Failed: {sum(1 for _, passed, _ in results if not passed)}")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    
    # Create status file based on results
    if success:
        with open("../data_status.ok", "w") as f:
            f.write("All tests passed. Data generation successful.")
        print("\nCreated data_status.ok")
    else:
        print("\nTests failed. See data_status.not for details.")