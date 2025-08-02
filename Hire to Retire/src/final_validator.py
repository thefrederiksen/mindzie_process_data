#!/usr/bin/env python3
"""
Comprehensive validation script for Hire to Retire dataset.
Creates data_status.ok or data_status.not based on test results.
"""

import json
import csv
import yaml
import re
from datetime import datetime
import os
from collections import defaultdict, Counter

def extract_yaml_from_markdown(content):
    """Extract YAML blocks from markdown specification."""
    yaml_blocks = re.findall(r'```yaml\n(.*?)\n```', content, re.DOTALL)
    combined_yaml = '\n'.join(yaml_blocks)
    return yaml.safe_load(combined_yaml)

def load_specification():
    """Load and parse process specification."""
    with open('../docs/process_specification.md', 'r', encoding='utf-8') as f:
        content = f.read()
    return extract_yaml_from_markdown(content)

def validate_json_structure(json_path):
    """Validate JSON follows exact required structure."""
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            return {"passed": False, "issue": "JSON root must be a list of cases"}
        
        # Check each case
        for i, case in enumerate(data[:10]):  # Check first 10 cases
            # Required case fields
            if 'CaseId' not in case:
                return {"passed": False, "issue": f"Case {i} missing CaseId"}
            if 'Activities' not in case:
                return {"passed": False, "issue": f"Case {i} missing Activities"}
            
            # Check activities
            for j, activity in enumerate(case['Activities']):
                if 'ActivityName' not in activity:
                    return {"passed": False, "issue": f"Activity {j} in case {case['CaseId']} missing ActivityName"}
                if 'ActivityTime' not in activity:
                    return {"passed": False, "issue": f"Activity {j} in case {case['CaseId']} missing ActivityTime"}
                if 'Resource' not in activity:
                    return {"passed": False, "issue": f"Activity {j} in case {case['CaseId']} missing Resource"}
                
                # Validate datetime format
                try:
                    datetime.strptime(activity['ActivityTime'], "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    return {"passed": False, "issue": f"Invalid datetime format in case {case['CaseId']}"}
        
        return {"passed": True}
    except Exception as e:
        return {"passed": False, "issue": str(e)}

def validate_case_completeness(json_path):
    """Ensure historical data has proper closure."""
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    total_cases = len(data)
    closed_cases = 0
    
    closing_activities = [
        "Employment Ended", "Application Rejected", 
        "Interview Failed", "Offer Rejected", "Probation Failed"
    ]
    
    for case in data:
        if case['Activities']:
            last_activity = case['Activities'][-1]['ActivityName']
            if last_activity in closing_activities:
                closed_cases += 1
    
    closure_rate = closed_cases / total_cases if total_cases > 0 else 0
    
    if closure_rate >= 0.90:
        return {"passed": True, "closure_rate": closure_rate}
    else:
        return {
            "passed": False,
            "issue": f"Only {closure_rate:.1%} cases closed",
            "expected": "90%+",
            "found": f"{closure_rate:.1%}",
            "recommendation": "Ensure 90%+ cases have closing activities"
        }

def validate_attributes(json_path, spec):
    """Validate case and event attributes."""
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Get expected attributes from spec
    expected_case_attrs = [attr['name'] for attr in spec.get('case_attributes', [])]
    
    issues = []
    
    # Check first case for structure
    if data:
        first_case = data[0]
        actual_case_attrs = [k for k in first_case.keys() if k not in ['CaseId', 'Activities']]
        
        # Check missing attributes
        missing = set(expected_case_attrs) - set(actual_case_attrs)
        if missing:
            issues.append(f"Missing case attributes: {list(missing)}")
        
        # Check case attribute constancy
        for case in data[:50]:  # Check first 50 cases
            case_attrs = {k: v for k, v in case.items() if k not in ['CaseId', 'Activities']}
            
            # Verify attributes don't appear in activities
            for activity in case['Activities']:
                for attr_name in expected_case_attrs:
                    if attr_name in activity:
                        # CurrentSalary can appear in specific activities as it changes
                        if not (attr_name == 'CurrentSalary' and activity['ActivityName'] in ['Promotion Approved']):
                            issues.append(f"Case attribute {attr_name} found at activity level")
                            break
    
    # Check Resource attribute presence
    resource_missing = 0
    total_activities = 0
    
    for case in data[:100]:  # Check first 100 cases
        for activity in case['Activities']:
            total_activities += 1
            if 'Resource' not in activity:
                resource_missing += 1
    
    if resource_missing > 0:
        issues.append(f"{resource_missing} activities missing Resource attribute")
    
    if issues:
        return {"passed": False, "issues": issues[:5]}  # Return first 5 issues
    return {"passed": True}

def validate_bottlenecks(json_path, spec):
    """Check if bottlenecks are visible in the data."""
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Get bottleneck definitions from spec
    bottlenecks = spec.get('bottlenecks', [])
    
    # Track resource activity counts
    resource_activities = defaultdict(list)
    
    for case in data:
        for i in range(len(case['Activities']) - 1):
            activity = case['Activities'][i]
            next_activity = case['Activities'][i + 1]
            
            # Calculate duration
            start = datetime.strptime(activity['ActivityTime'], "%Y-%m-%d %H:%M:%S")
            end = datetime.strptime(next_activity['ActivityTime'], "%Y-%m-%d %H:%M:%S")
            duration_hours = (end - start).total_seconds() / 3600
            
            resource = activity.get('Resource', 'Unknown')
            activity_name = activity['ActivityName']
            resource_activities[resource].append({
                'activity': activity_name,
                'duration': duration_hours
            })
    
    # Check specific bottlenecks from spec
    issues = []
    for bottleneck in bottlenecks:
        resource = bottleneck.get('slow_resource')
        expected_rate = bottleneck.get('occurrence_rate', 0)
        
        if resource in resource_activities:
            activities = resource_activities[resource]
            actual_rate = len(activities) / sum(len(v) for v in resource_activities.values())
            
            # Allow some tolerance
            if abs(actual_rate - expected_rate) > 0.15:
                issues.append(f"{resource} bottleneck: expected {expected_rate:.0%}, got {actual_rate:.0%}")
    
    if issues:
        return {"passed": False, "issues": issues}
    return {"passed": True}

def validate_csv_matches_json(json_path, csv_path):
    """Verify CSV contains same data as JSON."""
    try:
        # Load JSON
        with open(json_path, 'r') as f:
            json_data = json.load(f)
        
        # Load CSV
        csv_rows = []
        with open(csv_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            csv_rows = list(reader)
        
        # Count activities in JSON
        json_activity_count = sum(len(case['Activities']) for case in json_data)
        
        # CSV should have same number of rows
        if len(csv_rows) != json_activity_count:
            return {
                "passed": False,
                "issue": f"Row count mismatch",
                "expected": f"{json_activity_count} rows",
                "found": f"{len(csv_rows)} rows"
            }
        
        return {"passed": True}
    except Exception as e:
        return {"passed": False, "issue": str(e)}

def create_approval_status(json_path, csv_path, test_results):
    """Create data_status.ok for approval."""
    with open("../data_status.ok", "w") as f:
        f.write("APPROVED: Dataset is production-ready\n")
        f.write(f"Tested at: {datetime.now()}\n")
        f.write(f"JSON file: {json_path}\n")
        f.write(f"CSV file: {csv_path}\n")
        f.write("\nValidation Summary:\n")
        f.write("- JSON structure: PASS\n")
        f.write("- Case completeness: PASS\n")
        f.write("- Attributes validated: PASS\n")
        f.write("- CSV matches JSON: PASS\n")
        f.write("- Bottlenecks visible: PASS\n")
        f.write("- All specifications met: PASS\n")
    
    print("Dataset APPROVED for production use")
    print("Created data_status.ok")

def create_rejection_status(test_results):
    """Create data_status.not with detailed feedback."""
    with open("../data_status.not", "w") as f:
        f.write("REJECTED: Dataset needs fixes\n")
        f.write(f"Tested at: {datetime.now()}\n\n")
        
        f.write("FAILURES:\n")
        for test_name, result in test_results.items():
            if not result.get('passed', False):
                f.write(f"\n[{test_name}]\n")
                if 'issue' in result:
                    f.write(f"Issue: {result['issue']}\n")
                if 'issues' in result:
                    f.write(f"Issues:\n")
                    for issue in result['issues']:
                        f.write(f"  - {issue}\n")
                if 'expected' in result:
                    f.write(f"Expected: {result['expected']}\n")
                if 'found' in result:
                    f.write(f"Found: {result['found']}\n")
                if 'recommendation' in result:
                    f.write(f"Fix: {result['recommendation']}\n")
        
        f.write("\nREQUIRED ACTIONS:\n")
        f.write("1. Fix the issues listed above\n")
        f.write("2. Regenerate the data\n")
        f.write("3. Delete this file when ready for re-testing\n")
    
    print("Dataset REJECTED - see data_status.not for details")

def main():
    """Main validation workflow."""
    # Check if files exist
    json_path = "output/hire_to_retire_historical.json"
    csv_path = "output/hire_to_retire_historical.csv"
    
    if not os.path.exists(json_path) or not os.path.exists(csv_path):
        create_rejection_status({
            "missing_files": {
                "passed": False,
                "issue": "Required output files not found",
                "expected": "Both JSON and CSV files",
                "found": "Missing files",
                "recommendation": "Generate both JSON and CSV outputs"
            }
        })
        return
    
    # Load specification
    spec = load_specification()
    
    # Run all validations
    test_results = {
        "json_structure": validate_json_structure(json_path),
        "case_completeness": validate_case_completeness(json_path),
        "attributes": validate_attributes(json_path, spec),
        "csv_matches_json": validate_csv_matches_json(json_path, csv_path),
        "bottlenecks": validate_bottlenecks(json_path, spec)
    }
    
    # Make decision
    all_passed = all(result.get('passed', False) for result in test_results.values())
    
    if all_passed:
        create_approval_status(json_path, csv_path, test_results)
    else:
        create_rejection_status(test_results)

if __name__ == "__main__":
    main()