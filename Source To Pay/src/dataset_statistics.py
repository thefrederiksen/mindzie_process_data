#!/usr/bin/env python3
"""
Dataset Statistics for Source to Pay Process Mining Data
Provides detailed statistics and insights about the generated datasets
"""

import json
import csv
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
from collections import Counter, defaultdict

def load_json_data(filepath: str) -> Dict[str, Any]:
    """Load JSON data file"""
    with open(filepath, 'r') as f:
        return json.load(f)

def analyze_case_statistics(cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze case-level statistics"""
    stats = {
        "total_cases": len(cases),
        "order_types": Counter(),
        "order_value_ranges": {"<$1K": 0, "$1K-$10K": 0, "$10K-$100K": 0, ">$100K": 0},
        "payment_methods": Counter(),
        "payment_status": Counter(),
        "invoice_status": Counter(),
        "departments": Counter(),
        "vendor_categories": Counter(),
        "priorities": Counter(),
        "currencies": Counter(),
        "total_order_value": 0,
        "avg_order_value": 0,
        "avg_activities_per_case": 0
    }
    
    total_activities = 0
    order_values = []
    
    for case in cases:
        # Order types
        stats["order_types"][case.get("OrderType", "Unknown")] += 1
        
        # Order value analysis
        try:
            order_value = float(case.get("OrderValue", 0))
            order_values.append(order_value)
            stats["total_order_value"] += order_value
            
            if order_value < 1000:
                stats["order_value_ranges"]["<$1K"] += 1
            elif order_value < 10000:
                stats["order_value_ranges"]["$1K-$10K"] += 1
            elif order_value < 100000:
                stats["order_value_ranges"]["$10K-$100K"] += 1
            else:
                stats["order_value_ranges"][">$100K"] += 1
        except (ValueError, TypeError):
            pass
        
        # Payment and invoice status
        stats["payment_methods"][case.get("PaymentMethod", "Unknown")] += 1
        stats["payment_status"][case.get("PaymentStatus", "Unknown")] += 1
        stats["invoice_status"][case.get("InvoiceStatus", "Unknown")] += 1
        
        # Organizational data
        stats["departments"][case.get("Department", "Unknown")] += 1
        stats["vendor_categories"][case.get("VendorCategory", "Unknown")] += 1
        stats["priorities"][case.get("Priority", "Unknown")] += 1
        stats["currencies"][case.get("Currency", "Unknown")] += 1
        
        # Activity count
        activities = case.get("activities", [])
        total_activities += len(activities)
    
    if len(cases) > 0:
        stats["avg_order_value"] = stats["total_order_value"] / len(cases)
        stats["avg_activities_per_case"] = total_activities / len(cases)
    
    if order_values:
        stats["min_order_value"] = min(order_values)
        stats["max_order_value"] = max(order_values)
        stats["median_order_value"] = sorted(order_values)[len(order_values) // 2]
    
    return stats

def analyze_activity_statistics(cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze activity-level statistics"""
    stats = {
        "total_activities": 0,
        "activity_types": Counter(),
        "resource_utilization": Counter(),
        "role_distribution": Counter(),
        "activity_sequences": Counter(),
        "avg_case_duration_hours": 0,
        "process_variants": Counter()
    }
    
    case_durations = []
    
    for case in cases:
        activities = case.get("activities", [])
        stats["total_activities"] += len(activities)
        
        if not activities:
            continue
        
        # Activity types and resources
        activity_sequence = []
        for activity in activities:
            activity_name = activity.get("ActivityName", "Unknown")
            resource = activity.get("Resource", "Unknown")
            role = activity.get("Role", "Unknown")
            
            stats["activity_types"][activity_name] += 1
            stats["resource_utilization"][resource] += 1
            stats["role_distribution"][role] += 1
            activity_sequence.append(activity_name)
        
        # Process variants (first 5 activities to identify main variants)
        variant_key = " -> ".join(activity_sequence[:5])
        stats["process_variants"][variant_key] += 1
        
        # Case duration calculation
        try:
            start_time = datetime.strptime(activities[0]["ActivityTime"], "%Y-%m-%d %H:%M:%S")
            end_time = datetime.strptime(activities[-1]["ActivityTime"], "%Y-%m-%d %H:%M:%S")
            duration_hours = (end_time - start_time).total_seconds() / 3600
            case_durations.append(duration_hours)
        except (ValueError, KeyError, IndexError):
            pass
    
    if case_durations:
        stats["avg_case_duration_hours"] = sum(case_durations) / len(case_durations)
        stats["min_case_duration_hours"] = min(case_durations)
        stats["max_case_duration_hours"] = max(case_durations)
    
    return stats

def analyze_bottlenecks(cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze potential bottlenecks and performance issues"""
    bottleneck_resources = ["Robert Taylor", "Paul Martinez", "Manual Vendor Process"]
    
    stats = {
        "bottleneck_activity_count": Counter(),
        "bottleneck_resource_utilization": {},
        "slow_activities": [],
        "resource_efficiency": {}
    }
    
    resource_activity_counts = Counter()
    total_activities = 0
    
    for case in cases:
        activities = case.get("activities", [])
        
        for activity in activities:
            resource = activity.get("Resource", "")
            activity_name = activity.get("ActivityName", "")
            
            resource_activity_counts[resource] += 1
            total_activities += 1
            
            # Track bottleneck resource activities
            if resource in bottleneck_resources:
                stats["bottleneck_activity_count"][resource] += 1
    
    # Calculate bottleneck utilization percentages
    for resource in bottleneck_resources:
        count = stats["bottleneck_activity_count"][resource]
        if total_activities > 0:
            stats["bottleneck_resource_utilization"][resource] = (count / total_activities) * 100
    
    # Identify top resource users
    stats["top_resources"] = resource_activity_counts.most_common(10)
    
    return stats

def analyze_waiting_stages(cases: List[Dict[str, Any]], freeze_time_str: str = None) -> Dict[str, Any]:
    """Analyze waiting stages for in-progress cases"""
    if not freeze_time_str:
        return {"message": "No freeze time provided, skipping waiting stage analysis"}
    
    try:
        freeze_time = datetime.strptime(freeze_time_str.split('T')[0] + ' ' + freeze_time_str.split('T')[1].split('+')[0], "%Y-%m-%d %H:%M:%S")
    except:
        return {"message": "Invalid freeze time format, skipping waiting stage analysis"}
    
    stage_analysis = {
        "in_progress_cases": 0,
        "completed_cases": 0,
        "waiting_times": [],
        "stages_summary": Counter()
    }
    
    for case in cases:
        payment_status = case.get("PaymentStatus", "")
        activities = case.get("activities", [])
        
        if payment_status == "Pending" and activities:
            stage_analysis["in_progress_cases"] += 1
            
            # Calculate waiting time from last activity
            try:
                last_activity_time = datetime.strptime(activities[-1]["ActivityTime"], "%Y-%m-%d %H:%M:%S")
                waiting_hours = (freeze_time - last_activity_time).total_seconds() / 3600
                stage_analysis["waiting_times"].append(waiting_hours)
                
                # Categorize by waiting time
                if waiting_hours < 4:
                    stage_analysis["stages_summary"]["< 4 hours"] += 1
                elif waiting_hours < 24:
                    stage_analysis["stages_summary"]["4-24 hours"] += 1
                elif waiting_hours < 72:
                    stage_analysis["stages_summary"]["1-3 days"] += 1
                else:
                    stage_analysis["stages_summary"]["> 3 days"] += 1
                    
            except (ValueError, KeyError):
                pass
        else:
            stage_analysis["completed_cases"] += 1
    
    if stage_analysis["waiting_times"]:
        stage_analysis["avg_waiting_hours"] = sum(stage_analysis["waiting_times"]) / len(stage_analysis["waiting_times"])
        stage_analysis["max_waiting_hours"] = max(stage_analysis["waiting_times"])
    
    return stage_analysis

def print_statistics_report(dataset_type: str, json_data: Dict[str, Any]) -> None:
    """Print comprehensive statistics report"""
    cases = json_data.get("cases", [])
    freeze_time = json_data.get("FreezeTime")
    
    print(f"\n{'='*60}")
    print(f"SOURCE TO PAY {dataset_type.upper()} DATASET STATISTICS")
    print(f"{'='*60}")
    
    if not cases:
        print("No cases found in dataset")
        return
    
    # Case-level statistics
    case_stats = analyze_case_statistics(cases)
    print(f"\nCASE STATISTICS:")
    print(f"  Total Cases: {case_stats['total_cases']:,}")
    print(f"  Total Order Value: ${case_stats['total_order_value']:,.2f}")
    print(f"  Average Order Value: ${case_stats['avg_order_value']:,.2f}")
    print(f"  Average Activities per Case: {case_stats['avg_activities_per_case']:.1f}")
    
    if 'min_order_value' in case_stats:
        print(f"  Order Value Range: ${case_stats['min_order_value']:,.2f} - ${case_stats['max_order_value']:,.2f}")
        print(f"  Median Order Value: ${case_stats['median_order_value']:,.2f}")
    
    print(f"\nORDER VALUE DISTRIBUTION:")
    for range_name, count in case_stats["order_value_ranges"].items():
        percentage = (count / case_stats['total_cases']) * 100
        print(f"  {range_name:>10}: {count:4d} cases ({percentage:5.1f}%)")
    
    print(f"\nTOP ORDER TYPES:")
    for order_type, count in case_stats["order_types"].most_common(5):
        percentage = (count / case_stats['total_cases']) * 100
        print(f"  {order_type:>15}: {count:4d} cases ({percentage:5.1f}%)")
    
    print(f"\nTOP PAYMENT METHODS:")
    for method, count in case_stats["payment_methods"].most_common(5):
        percentage = (count / case_stats['total_cases']) * 100
        print(f"  {method:>15}: {count:4d} cases ({percentage:5.1f}%)")
    
    print(f"\nTOP DEPARTMENTS:")
    for dept, count in case_stats["departments"].most_common(5):
        percentage = (count / case_stats['total_cases']) * 100
        print(f"  {dept:>15}: {count:4d} cases ({percentage:5.1f}%)")
    
    # Activity-level statistics
    activity_stats = analyze_activity_statistics(cases)
    print(f"\nACTIVITY STATISTICS:")
    print(f"  Total Activities: {activity_stats['total_activities']:,}")
    print(f"  Average Case Duration: {activity_stats['avg_case_duration_hours']:.1f} hours")
    
    if 'min_case_duration_hours' in activity_stats:
        print(f"  Duration Range: {activity_stats['min_case_duration_hours']:.1f} - {activity_stats['max_case_duration_hours']:.1f} hours")
    
    print(f"\nTOP ACTIVITIES:")
    for activity, count in activity_stats["activity_types"].most_common(10):
        percentage = (count / activity_stats['total_activities']) * 100
        print(f"  {activity[:30]:30}: {count:4d} ({percentage:5.1f}%)")
    
    print(f"\nTOP PROCESS VARIANTS:")
    for variant, count in activity_stats["process_variants"].most_common(5):
        percentage = (count / case_stats['total_cases']) * 100
        print(f"  {count:3d} cases ({percentage:4.1f}%): {variant[:80]}")
    
    # Resource utilization
    print(f"\nTOP RESOURCES:")
    for resource, count in activity_stats["resource_utilization"].most_common(10):
        percentage = (count / activity_stats['total_activities']) * 100
        print(f"  {resource[:25]:25}: {count:4d} activities ({percentage:5.1f}%)")
    
    # Bottleneck analysis
    bottleneck_stats = analyze_bottlenecks(cases)
    print(f"\nBOTTLENECK ANALYSIS:")
    for resource, percentage in bottleneck_stats["bottleneck_resource_utilization"].items():
        print(f"  {resource:>20}: {percentage:5.1f}% of all activities")
    
    # Waiting stage analysis (for daily datasets)
    if dataset_type == "daily" and freeze_time:
        waiting_stats = analyze_waiting_stages(cases, freeze_time)
        if "message" not in waiting_stats:
            print(f"\nWAITING STAGE ANALYSIS:")
            print(f"  In-Progress Cases: {waiting_stats['in_progress_cases']}")
            print(f"  Completed Cases: {waiting_stats['completed_cases']}")
            
            if 'avg_waiting_hours' in waiting_stats:
                print(f"  Average Waiting Time: {waiting_stats['avg_waiting_hours']:.1f} hours")
                print(f"  Maximum Waiting Time: {waiting_stats['max_waiting_hours']:.1f} hours")
            
            print(f"  Waiting Time Distribution:")
            for stage, count in waiting_stats["stages_summary"].items():
                percentage = (count / waiting_stats['in_progress_cases']) * 100 if waiting_stats['in_progress_cases'] > 0 else 0
                print(f"    {stage:>12}: {count:3d} cases ({percentage:5.1f}%)")

def main():
    """Generate statistics for both datasets"""
    print("Source to Pay Dataset Statistics Generator")
    
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    
    # Historical dataset statistics
    historical_file = os.path.join(output_dir, "source_to_pay_historical.json")
    if os.path.exists(historical_file):
        historical_data = load_json_data(historical_file)
        print_statistics_report("historical", historical_data)
    
    # Daily dataset statistics
    daily_file = os.path.join(output_dir, "source_to_pay_daily.json")
    if os.path.exists(daily_file):
        daily_data = load_json_data(daily_file)
        print_statistics_report("daily", daily_data)
    
    print(f"\n{'='*60}")
    print("Statistics generation completed!")

if __name__ == "__main__":
    main()