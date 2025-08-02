#!/usr/bin/env python3
"""
Attribute validation script for Hire to Retire dataset
Tests case and event attributes against specification
"""

import json
import os
import yaml
import re
from datetime import datetime
from collections import Counter, defaultdict

def extract_yaml_from_markdown(content):
    """Extract YAML blocks from markdown specification."""
    yaml_blocks = re.findall(r'```yaml\n(.*?)\n```', content, re.DOTALL)
    combined_yaml = '\n'.join(yaml_blocks)
    return yaml.safe_load(combined_yaml)

def main():
    # Load the generated data
    with open('output/hire_to_retire_historical.json', 'r') as f:
        data_raw = json.load(f)
    
    # Handle both formats - list of cases or dict with cases
    if isinstance(data_raw, list):
        data = {"cases": data_raw}
    else:
        data = data_raw

    # Load the process specification
    with open('../docs/process_specification.md', 'r', encoding='utf-8') as f:
        spec_content = f.read()
    spec = extract_yaml_from_markdown(spec_content)

    print('=== HIRE TO RETIRE ATTRIBUTE VALIDATION ===')
    print(f'Total cases analyzed: {len(data["cases"])}')
    print()

    # Extract expected attributes from spec
    expected_case_attrs = [attr['name'] for attr in spec.get('case_attributes', [])]
    print(f'Expected case attributes from spec: {expected_case_attrs}')

    # Analyze first case to see actual attributes
    first_case = data['cases'][0]
    actual_case_attrs = [k for k in first_case.keys() if k not in ['CaseId', 'activities']]
    print(f'Actual case attributes found: {actual_case_attrs}')
    print()

    # Check for missing attributes
    missing_attrs = set(expected_case_attrs) - set(actual_case_attrs)
    if missing_attrs:
        print(f'❌ MISSING CASE ATTRIBUTES: {missing_attrs}')
    else:
        print('✓ All expected case attributes present')

    # Check for unexpected attributes
    unexpected_attrs = set(actual_case_attrs) - set(expected_case_attrs)
    if unexpected_attrs:
        print(f'⚠️  Additional attributes found (not in spec): {unexpected_attrs}')
    print()

    # Validate case attribute constancy
    print('=== CASE ATTRIBUTE CONSTANCY CHECK ===')
    constancy_issues = []
    for i, case in enumerate(data['cases'][:100]):  # Check first 100 cases
        case_attrs = {k: v for k, v in case.items() if k not in ['CaseId', 'activities']}
        
        # Check if any activities have different values for case attributes
        for activity in case['activities']:
            for attr_name, case_value in case_attrs.items():
                if attr_name in activity and activity[attr_name] != case_value:
                    constancy_issues.append({
                        'case': case['CaseId'],
                        'attribute': attr_name,
                        'case_value': case_value,
                        'activity_value': activity[attr_name],
                        'activity': activity['ActivityName']
                    })

    if constancy_issues:
        print(f'❌ Found {len(constancy_issues)} case attribute constancy violations:')
        for issue in constancy_issues[:5]:
            print(f'  - {issue["attribute"]} changed in case {issue["case"]}: {issue["case_value"]} → {issue["activity_value"]}')
    else:
        print('✓ Case attributes remain constant throughout all cases')
    print()

    # Analyze event-level attributes
    print('=== EVENT ATTRIBUTE ANALYSIS ===')
    event_attrs_by_activity = defaultdict(lambda: defaultdict(int))
    total_activities_by_type = defaultdict(int)

    for case in data['cases']:
        for activity in case['activities']:
            activity_name = activity['ActivityName']
            total_activities_by_type[activity_name] += 1
            
            # Count attributes on this activity (excluding standard fields)
            for attr in activity:
                if attr not in ['ActivityName', 'ActivityTime', 'CaseId']:
                    event_attrs_by_activity[activity_name][attr] += 1

    # Display attribute distribution by activity
    print('Event attributes found per activity type:')
    for activity_name in sorted(total_activities_by_type.keys())[:10]:
        print(f'\n{activity_name} (n={total_activities_by_type[activity_name]}):')
        for attr, count in sorted(event_attrs_by_activity[activity_name].items()):
            percentage = (count / total_activities_by_type[activity_name]) * 100
            print(f'  - {attr}: {percentage:.1f}%')

    # Check Resource attribute specifically
    print('\n=== RESOURCE ATTRIBUTE CHECK ===')
    activities_without_resource = []
    resource_distribution = defaultdict(int)
    
    for case in data['cases']:
        for activity in case['activities']:
            if 'Resource' not in activity:
                activities_without_resource.append({
                    'case': case['CaseId'],
                    'activity': activity['ActivityName']
                })
            else:
                resource_distribution[activity['Resource']] += 1

    if activities_without_resource:
        print(f'❌ Found {len(activities_without_resource)} activities without Resource attribute')
        # Show first few examples
        for ex in activities_without_resource[:3]:
            print(f'  - Case {ex["case"]}, Activity: {ex["activity"]}')
    else:
        print('✓ All activities have Resource attribute')
    
    # Show resource distribution
    print('\nTop resources by activity count:')
    for resource, count in sorted(resource_distribution.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f'  - {resource}: {count} activities')

    # Check specific event attributes from spec
    print('\n=== SPECIFIC EVENT ATTRIBUTE VALIDATION ===')
    
    # Look for CurrentSalary updates after promotions
    salary_changes = []
    for case in data['cases']:
        last_salary = None
        for activity in case['activities']:
            if 'CurrentSalary' in activity:
                if last_salary and activity['CurrentSalary'] != last_salary:
                    salary_changes.append({
                        'case': case['CaseId'],
                        'activity': activity['ActivityName'],
                        'old_salary': last_salary,
                        'new_salary': activity['CurrentSalary']
                    })
                last_salary = activity['CurrentSalary']
    
    if salary_changes:
        print(f'Found {len(salary_changes)} salary changes in activities')
        for change in salary_changes[:3]:
            print(f'  - Case {change["case"]}: {change["old_salary"]} → {change["new_salary"]} at {change["activity"]}')
    
    # Check for PerformedBy attribute
    performedby_count = 0
    for case in data['cases']:
        for activity in case['activities']:
            if 'PerformedBy' in activity:
                performedby_count += 1
    
    print(f'\nPerformedBy attribute found in {performedby_count} activities')
    
    # Check for SystemUsed attribute
    systemused_count = 0
    system_values = set()
    for case in data['cases']:
        for activity in case['activities']:
            if 'SystemUsed' in activity:
                systemused_count += 1
                system_values.add(activity['SystemUsed'])
    
    print(f'SystemUsed attribute found in {systemused_count} activities')
    if system_values:
        print(f'  Unique systems: {", ".join(sorted(system_values))}')

if __name__ == "__main__":
    main()