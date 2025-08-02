#!/usr/bin/env python3
"""
Attribute validation for Hire to Retire dataset
"""

import json
import os
import yaml
import re
from collections import defaultdict

def extract_yaml_from_markdown(content):
    """Extract YAML blocks from markdown specification."""
    yaml_blocks = re.findall(r'```yaml\n(.*?)\n```', content, re.DOTALL)
    combined_yaml = '\n'.join(yaml_blocks)
    return yaml.safe_load(combined_yaml)

def main():
    # Load the generated data
    with open('output/hire_to_retire_historical.json', 'r') as f:
        data_raw = json.load(f)
    
    # Handle both formats
    if isinstance(data_raw, list):
        cases = data_raw
    else:
        cases = data_raw.get('cases', [])

    # Load the process specification
    with open('../docs/process_specification.md', 'r', encoding='utf-8') as f:
        spec_content = f.read()
    spec = extract_yaml_from_markdown(spec_content)

    print('HIRE TO RETIRE ATTRIBUTE VALIDATION REPORT')
    print('=' * 50)
    print(f'Total cases analyzed: {len(cases)}')
    print()

    # Extract expected attributes from spec
    expected_case_attrs = [attr['name'] for attr in spec.get('case_attributes', [])]
    print(f'Expected case attributes from spec: {expected_case_attrs}')

    # Analyze first case structure
    if cases:
        first_case = cases[0]
        actual_case_attrs = [k for k in first_case.keys() if k not in ['CaseId', 'Activities', 'activities']]
        print(f'Actual case attributes found: {actual_case_attrs}')
        
        # Check for Activities vs activities
        if 'Activities' in first_case:
            activities_key = 'Activities'
        elif 'activities' in first_case:
            activities_key = 'activities'
        else:
            print('ERROR: No activities found in case structure')
            return
        
        print(f'Activities key used: {activities_key}')
        print()

        # Check missing attributes
        missing_attrs = set(expected_case_attrs) - set(actual_case_attrs)
        if missing_attrs:
            print(f'MISSING CASE ATTRIBUTES: {list(missing_attrs)}')
        else:
            print('SUCCESS: All expected case attributes present')

        # Check unexpected attributes
        unexpected_attrs = set(actual_case_attrs) - set(expected_case_attrs)
        if unexpected_attrs:
            print(f'Additional attributes found: {list(unexpected_attrs)}')
        print()

        # Check event attributes
        print('EVENT ATTRIBUTE ANALYSIS')
        print('-' * 30)
        
        # Sample first 10 activities
        activity_attrs = defaultdict(set)
        resource_count = 0
        total_activities = 0
        
        for case in cases[:100]:  # First 100 cases
            for activity in case.get(activities_key, []):
                total_activities += 1
                activity_name = activity.get('ActivityName', 'Unknown')
                
                # Track all attributes on this activity
                for attr in activity:
                    if attr not in ['ActivityName', 'ActivityTime']:
                        activity_attrs[activity_name].add(attr)
                
                if 'Resource' in activity:
                    resource_count += 1
        
        print(f'Total activities checked: {total_activities}')
        print(f'Activities with Resource attribute: {resource_count} ({resource_count/total_activities*100:.1f}%)')
        print()
        
        # Show attributes by activity type
        print('Attributes found per activity type (first 5):')
        for i, (activity_name, attrs) in enumerate(sorted(activity_attrs.items())):
            if i >= 5:
                break
            print(f'{activity_name}:')
            for attr in sorted(attrs):
                print(f'  - {attr}')
        
        # Check case attribute constancy
        print()
        print('CASE ATTRIBUTE CONSTANCY CHECK')
        print('-' * 30)
        
        constancy_issues = 0
        for case in cases[:50]:  # Check first 50 cases
            case_attrs = {k: v for k, v in case.items() if k not in ['CaseId', activities_key]}
            
            # Check each activity
            for activity in case.get(activities_key, []):
                for attr_name, case_value in case_attrs.items():
                    if attr_name in activity and activity[attr_name] != case_value:
                        constancy_issues += 1
                        if constancy_issues <= 3:
                            print(f'Issue in case {case.get("CaseId", "?")}:')
                            print(f'  {attr_name} changed from {case_value} to {activity[attr_name]}')
                            print(f'  At activity: {activity.get("ActivityName", "?")}')
        
        if constancy_issues == 0:
            print('SUCCESS: Case attributes remain constant')
        else:
            print(f'FAILURE: Found {constancy_issues} constancy violations')
        
        # Check specific attributes mentioned in the spec
        print()
        print('SPECIFIC ATTRIBUTE CHECKS')
        print('-' * 30)
        
        # Check for CurrentSalary in activities
        salary_in_activities = 0
        performedby_count = 0
        systemused_count = 0
        
        for case in cases[:100]:
            for activity in case.get(activities_key, []):
                if 'CurrentSalary' in activity:
                    salary_in_activities += 1
                if 'PerformedBy' in activity:
                    performedby_count += 1
                if 'SystemUsed' in activity:
                    systemused_count += 1
        
        print(f'CurrentSalary found in {salary_in_activities} activities')
        print(f'PerformedBy found in {performedby_count} activities')
        print(f'SystemUsed found in {systemused_count} activities')
        
        # Final determination
        print()
        print('VALIDATION SUMMARY')
        print('=' * 50)
        
        issues = []
        if missing_attrs:
            issues.append(f'Missing {len(missing_attrs)} required case attributes: {list(missing_attrs)}')
        if constancy_issues > 0:
            issues.append(f'Found {constancy_issues} case attribute constancy violations')
        if resource_count < total_activities * 0.9:
            issues.append(f'Only {resource_count/total_activities*100:.1f}% of activities have Resource attribute')
        
        if issues:
            print('VALIDATION FAILED:')
            for issue in issues:
                print(f'  - {issue}')
        else:
            print('VALIDATION PASSED: All attribute checks successful')

if __name__ == "__main__":
    main()