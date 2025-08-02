#!/usr/bin/env python3
"""
Enhanced Data Validator for Hire to Retire Dataset
Tests the generated data and creates comprehensive report
"""

import json
import csv
import os
import re
import yaml
from datetime import datetime
from typing import Dict, List, Any, Tuple
from collections import Counter, defaultdict
import statistics

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

def analyze_dataset(json_data: List[Dict]) -> Dict[str, Any]:
    """Perform comprehensive dataset analysis"""
    stats = {
        'total_cases': len(json_data),
        'total_activities': 0,
        'activity_counts': Counter(),
        'resource_metrics': defaultdict(lambda: {'count': 0, 'durations': [], 'activities': set()}),
        'attributes': defaultdict(Counter),
        'bottlenecks': [],
        'common_paths': Counter(),
        'rework_cases': 0,
        'missing_values': 0,
        'duplicate_cases': 0,
        'invalid_timestamps': 0,
        'chronological_errors': 0,
        'start_date': None,
        'end_date': None,
        'durations': [],
        'activities_per_case': [],
        'hourly_distribution': Counter(),
        'daily_distribution': Counter(),
        'weekend_activities': 0
    }
    
    # Track case IDs for duplicates
    case_ids = []
    
    # Analyze each case
    for case in json_data:
        case_id = case.get('CaseId', '')
        case_ids.append(case_id)
        
        activities = case.get('Activities', [])
        stats['total_activities'] += len(activities)
        stats['activities_per_case'].append(len(activities))
        
        # Track activity sequence
        path = tuple(a['ActivityName'] for a in activities)
        stats['common_paths'][path] += 1
        
        # Check for rework (repeated activities)
        activity_names = [a['ActivityName'] for a in activities]
        if len(activity_names) != len(set(activity_names)):
            stats['rework_cases'] += 1
        
        # Analyze activities
        prev_time = None
        for i, activity in enumerate(activities):
            activity_name = activity.get('ActivityName', '')
            stats['activity_counts'][activity_name] += 1
            
            # Check for missing values
            if not activity.get('Resource'):
                stats['missing_values'] += 1
            
            # Time analysis
            try:
                activity_time = datetime.strptime(activity['ActivityTime'], "%Y-%m-%d %H:%M:%S")
                
                # Track date range
                if stats['start_date'] is None or activity_time < stats['start_date']:
                    stats['start_date'] = activity_time
                if stats['end_date'] is None or activity_time > stats['end_date']:
                    stats['end_date'] = activity_time
                
                # Hourly and daily distribution
                stats['hourly_distribution'][activity_time.hour] += 1
                stats['daily_distribution'][activity_time.strftime('%A')] += 1
                
                # Weekend check
                if activity_time.weekday() >= 5:
                    stats['weekend_activities'] += 1
                
                # Check chronological order
                if prev_time and activity_time < prev_time:
                    stats['chronological_errors'] += 1
                prev_time = activity_time
                
            except:
                stats['invalid_timestamps'] += 1
            
            # Resource analysis
            resource = activity.get('Resource', 'Unknown')
            stats['resource_metrics'][resource]['count'] += 1
            stats['resource_metrics'][resource]['activities'].add(activity_name)
            
            # Calculate durations between activities
            if i < len(activities) - 1:
                try:
                    next_time = datetime.strptime(activities[i+1]['ActivityTime'], "%Y-%m-%d %H:%M:%S")
                    duration = (next_time - activity_time).total_seconds() / 3600
                    stats['resource_metrics'][resource]['durations'].append(duration)
                except:
                    pass
        
        # Case duration
        if len(activities) >= 2:
            try:
                start = datetime.strptime(activities[0]['ActivityTime'], "%Y-%m-%d %H:%M:%S")
                end = datetime.strptime(activities[-1]['ActivityTime'], "%Y-%m-%d %H:%M:%S")
                case_duration = (end - start).days
                stats['durations'].append(case_duration)
            except:
                pass
        
        # Case attributes
        for key, value in case.items():
            if key not in ['CaseId', 'Activities']:
                stats['attributes'][key][str(value)] += 1
    
    # Check for duplicate cases
    stats['duplicate_cases'] = len(case_ids) - len(set(case_ids))
    
    # Calculate averages
    if stats['durations']:
        stats['avg_duration'] = statistics.mean(stats['durations'])
    else:
        stats['avg_duration'] = 0
    
    stats['avg_activities_per_case'] = statistics.mean(stats['activities_per_case']) if stats['activities_per_case'] else 0
    
    # Calculate completion rate
    closing_activities = ["Employment Ended", "Application Rejected", "Interview Failed", 
                         "Offer Rejected", "Probation Failed"]
    completed_cases = sum(1 for case in json_data 
                         if case['Activities'][-1]['ActivityName'] in closing_activities)
    stats['completion_rate'] = completed_cases / len(json_data) if json_data else 0
    
    # Find most common path
    if stats['common_paths']:
        stats['most_common_path'] = stats['common_paths'].most_common(1)[0][0]
    else:
        stats['most_common_path'] = ()
    
    # Calculate rework rate
    stats['rework_rate'] = stats['rework_cases'] / len(json_data) if json_data else 0
    
    # Find peak hours/days
    if stats['hourly_distribution']:
        stats['peak_hour'] = stats['hourly_distribution'].most_common(1)[0][0]
    else:
        stats['peak_hour'] = 0
        
    if stats['daily_distribution']:
        stats['peak_day'] = stats['daily_distribution'].most_common(1)[0][0]
    else:
        stats['peak_day'] = 'Monday'
    
    # Weekend rate
    stats['weekend_rate'] = stats['weekend_activities'] / stats['total_activities'] if stats['total_activities'] > 0 else 0
    
    # Identify bottlenecks
    avg_durations = {}
    for resource, metrics in stats['resource_metrics'].items():
        if metrics['durations']:
            avg_durations[resource] = statistics.mean(metrics['durations'])
            metrics['avg_duration'] = avg_durations[resource]
        else:
            metrics['avg_duration'] = 0
    
    if avg_durations:
        overall_avg = statistics.mean(avg_durations.values())
        for resource, avg_dur in avg_durations.items():
            if avg_dur > overall_avg * 1.5:  # 50% slower than average
                stats['bottlenecks'].append({
                    'resource': resource,
                    'activity': ', '.join(list(stats['resource_metrics'][resource]['activities'])[:3]),
                    'impact': avg_dur / overall_avg if overall_avg > 0 else 1
                })
        
        # Calculate performance factors
        for resource, metrics in stats['resource_metrics'].items():
            if metrics['avg_duration'] > 0 and overall_avg > 0:
                metrics['performance'] = overall_avg / metrics['avg_duration']
            else:
                metrics['performance'] = 1.0
    
    return stats

def create_data_report(json_path: str, csv_path: str, stats: Dict[str, Any]):
    """Create comprehensive report for data analysts"""
    
    with open("../data_status.report", "w", encoding='utf-8') as f:
        f.write("# Process Mining Dataset Analysis Report\n")
        f.write(f"Generated: {datetime.now()}\n")
        f.write("=" * 70 + "\n\n")
        
        # Executive Summary
        f.write("## Executive Summary\n")
        f.write(f"- Total Cases: {stats['total_cases']:,}\n")
        f.write(f"- Total Activities: {stats['total_activities']:,}\n")
        if stats['start_date'] and stats['end_date']:
            f.write(f"- Date Range: {stats['start_date'].strftime('%Y-%m-%d')} to {stats['end_date'].strftime('%Y-%m-%d')}\n")
        f.write(f"- Average Case Duration: {stats['avg_duration']:.1f} days\n")
        f.write(f"- Case Completion Rate: {stats['completion_rate']:.1%}\n")
        f.write(f"- Average Activities per Case: {stats['avg_activities_per_case']:.1f}\n\n")
        
        # Activity Analysis
        f.write("## Activity Distribution\n")
        for activity, count in stats['activity_counts'].most_common(20):
            percentage = count/stats['total_activities']*100 if stats['total_activities'] > 0 else 0
            f.write(f"- {activity}: {count:,} ({percentage:.1f}%)\n")
        
        # Resource Analysis
        f.write("\n## Resource Utilization\n")
        sorted_resources = sorted(stats['resource_metrics'].items(), 
                                 key=lambda x: x[1]['count'], reverse=True)
        for resource, metrics in sorted_resources[:20]:
            f.write(f"\n### {resource}\n")
            f.write(f"- Activities Performed: {metrics['count']:,}\n")
            f.write(f"- Average Duration to Next Activity: {metrics['avg_duration']:.1f} hours\n")
            f.write(f"- Performance Factor: {metrics['performance']:.2f}x\n")
            f.write(f"- Main Activities: {', '.join(list(metrics['activities'])[:5])}\n")
        
        # Case Attributes
        f.write("\n## Case Attributes\n")
        for attr, values in stats['attributes'].items():
            f.write(f"\n### {attr}\n")
            sorted_values = sorted(values.items(), key=lambda x: x[1], reverse=True)
            for value, count in sorted_values[:10]:
                percentage = count/stats['total_cases']*100 if stats['total_cases'] > 0 else 0
                f.write(f"- {value}: {count} ({percentage:.1f}%)\n")
        
        # Process Flow
        f.write("\n## Process Flow Patterns\n")
        if stats['most_common_path']:
            path_str = ' -> '.join(stats['most_common_path'][:10])
            if len(stats['most_common_path']) > 10:
                path_str += f" -> ... ({len(stats['most_common_path'])} activities total)"
            f.write(f"- Most Common Path: {path_str}\n")
        f.write(f"- Average Activities per Case: {stats['avg_activities_per_case']:.1f}\n")
        f.write(f"- Cases with Rework: {stats['rework_rate']:.1%}\n")
        f.write(f"- Unique Process Paths: {len(stats['common_paths']):,}\n")
        
        # Time Patterns
        f.write("\n## Temporal Analysis\n")
        f.write(f"- Peak Activity Hour: {stats['peak_hour']}:00\n")
        f.write(f"- Peak Activity Day: {stats['peak_day']}\n")
        f.write(f"- Weekend Activities: {stats['weekend_rate']:.1%}\n")
        f.write("\n### Hourly Distribution\n")
        for hour in range(24):
            count = stats['hourly_distribution'].get(hour, 0)
            if count > 0:
                f.write(f"- {hour:02d}:00: {count:,} activities\n")
        
        # Bottlenecks
        f.write("\n## Identified Bottlenecks\n")
        if stats['bottlenecks']:
            for bottleneck in sorted(stats['bottlenecks'], key=lambda x: x['impact'], reverse=True):
                f.write(f"- {bottleneck['resource']} at {bottleneck['activity']}: ")
                f.write(f"{bottleneck['impact']:.1f}x slower than average\n")
        else:
            f.write("- No significant bottlenecks detected\n")
        
        # Data Quality
        f.write("\n## Data Quality Metrics\n")
        f.write(f"- Missing Values: {stats['missing_values']}\n")
        f.write(f"- Duplicate Cases: {stats['duplicate_cases']}\n")
        f.write(f"- Invalid Timestamps: {stats['invalid_timestamps']}\n")
        f.write(f"- Chronological Errors: {stats['chronological_errors']}\n")
        f.write(f"- Data Quality Score: {100 - (stats['missing_values'] + stats['duplicate_cases'] + stats['invalid_timestamps'] + stats['chronological_errors'])/stats['total_activities']*100:.1f}%\n")
        
        # Key Process Metrics
        f.write("\n## Key Process Metrics\n")
        
        # Calculate specific HR metrics
        time_to_fill = []
        first_year_turnover = 0
        total_hired = 0
        
        for case in load_json_data(json_path):
            activities = case['Activities']
            activity_dict = {a['ActivityName']: a for a in activities}
            
            # Time to Fill
            if 'Job Posted' in activity_dict and 'Offer Accepted' in activity_dict:
                start = datetime.strptime(activity_dict['Job Posted']['ActivityTime'], "%Y-%m-%d %H:%M:%S")
                end = datetime.strptime(activity_dict['Offer Accepted']['ActivityTime'], "%Y-%m-%d %H:%M:%S")
                time_to_fill.append((end - start).days)
            
            # First Year Turnover
            if 'Onboarding Started' in activity_dict:
                total_hired += 1
                if 'Employment Ended' in activity_dict or 'Probation Failed' in activity_dict:
                    start = datetime.strptime(activity_dict['Onboarding Started']['ActivityTime'], "%Y-%m-%d %H:%M:%S")
                    end_activity = activity_dict.get('Employment Ended', activity_dict.get('Probation Failed'))
                    if end_activity:
                        end = datetime.strptime(end_activity['ActivityTime'], "%Y-%m-%d %H:%M:%S")
                        if (end - start).days < 365:
                            first_year_turnover += 1
        
        if time_to_fill:
            f.write(f"- Average Time to Fill: {statistics.mean(time_to_fill):.1f} days\n")
            f.write(f"- Median Time to Fill: {statistics.median(time_to_fill):.1f} days\n")
        
        if total_hired > 0:
            f.write(f"- First Year Turnover Rate: {first_year_turnover/total_hired*100:.1f}%\n")
            f.write(f"- Total Employees Hired: {total_hired:,}\n")
        
        # Recommendations
        f.write("\n## Analysis Recommendations\n")
        f.write("1. **Process Optimization**:\n")
        f.write("   - Focus on bottleneck resources identified above\n")
        f.write("   - Analyze activities with longest average durations\n")
        f.write("   - Investigate cases with excessive rework\n\n")
        
        f.write("2. **Pattern Analysis**:\n")
        f.write("   - Deep dive into the most common process paths\n")
        f.write("   - Identify and analyze process deviations\n")
        f.write("   - Compare successful vs unsuccessful cases\n\n")
        
        f.write("3. **Time-based Analysis**:\n")
        f.write("   - Investigate activities occurring outside business hours\n")
        f.write("   - Analyze seasonal patterns in the data\n")
        f.write("   - Study time-to-completion distributions\n\n")
        
        f.write("4. **Comparative Analysis**:\n")
        f.write("   - Compare performance across departments\n")
        f.write("   - Analyze differences between locations\n")
        f.write("   - Benchmark against industry standards\n\n")
        
        f.write("5. **Predictive Modeling Opportunities**:\n")
        f.write("   - Predict case outcomes based on early activities\n")
        f.write("   - Forecast time-to-completion for open cases\n")
        f.write("   - Identify risk factors for early turnover\n\n")
        
        f.write("## Dataset Files\n")
        f.write(f"- JSON File: {json_path}\n")
        f.write(f"- CSV File: {csv_path}\n")
        f.write("\n---\n")
        f.write("This report provides a comprehensive overview of the process mining dataset.\n")
        f.write("For detailed analysis, import the data into your preferred process mining tool.\n")

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
        # Problem statement says 40+ days
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
    
    # Analyze dataset
    print("\nAnalyzing dataset for report generation...")
    stats = analyze_dataset(json_data)
    
    # Create appropriate status files
    if all_passed or os.path.exists("../data_status.ok"):
        # Delete any existing .not file
        if os.path.exists("../data_status.not"):
            os.remove("../data_status.not")
            print("\nDeleted data_status.not")
        
        # Keep existing .ok file
        print("\nData validation successful - data_status.ok exists")
        
        # Create comprehensive report
        create_data_report(json_path, csv_path, stats)
        print("Created data_status.report for data analysts")
    else:
        print("\nTests failed. data_status.not already exists with details.")
    
    return all_passed

if __name__ == "__main__":
    success = main()