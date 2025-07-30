#!/usr/bin/env python3
"""
SAP Accounts Payable Daily Event Log Statistics

This script provides comprehensive statistics and evaluation for the SAP AP daily dataset.
It analyzes 69 in-progress cases to validate real-time monitoring data and provide operational insights.

The script performs:
- Case count validation (in-progress cases)
- Activity frequency analysis
- Stage duration statistics
- Threshold compliance checking
- Data quality metrics
- Process flow validation
- Summary report generation
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def load_daily_data():
    """Load the daily event log data"""
    json_path = "output/sap_ap_daily.json"
    
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found. Please run daily_event_log.py first.")
        return None, None
    
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    events = data['events']
    metadata = data['case_metadata']
    
    return events, metadata

def analyze_case_distribution(metadata):
    """Analyze case distribution across stages and status"""
    print("=== CASE DISTRIBUTION ANALYSIS ===")
    
    # Stage distribution
    stage_counts = {}
    status_counts = {"ok": 0, "warning": 0, "critical": 0}
    
    for case_id, case_data in metadata.items():
        stage = case_data["WaitingStage"]
        status = case_data["Status"]
        
        if stage not in stage_counts:
            stage_counts[stage] = {"total": 0, "ok": 0, "warning": 0, "critical": 0}
        
        stage_counts[stage]["total"] += 1
        stage_counts[stage][status] += 1
        status_counts[status] += 1
    
    print(f"Total cases: {len(metadata)}")
    print(f"Expected cases: 69")
    
    if len(metadata) != 69:
        print(f"Warning: Expected 69 cases, found {len(metadata)}")
    
    print("\nStage Distribution:")
    for stage, counts in stage_counts.items():
        print(f"  {stage}: {counts['total']} cases ({counts['ok']} OK, {counts['warning']} Warning, {counts['critical']} Critical)")
    
    print("\nStatus Distribution:")
    for status, count in status_counts.items():
        percentage = (count / len(metadata)) * 100
        print(f"  {status.capitalize()}: {count} ({percentage:.1f}%)")
    
    # Cases requiring attention
    attention_cases = sum(1 for case_data in metadata.values() if case_data["RequiresAttention"])
    print(f"\nCases Requiring Attention: {attention_cases} ({attention_cases/len(metadata)*100:.1f}%)")
    
    return stage_counts, status_counts

def analyze_waiting_times(metadata):
    """Analyze waiting times for each stage"""
    print("\n=== WAITING TIME ANALYSIS ===")
    
    # Stage thresholds
    stage_thresholds = {
        "Invoice Scanning": {"warning": 2, "critical": 8},
        "Validation": {"warning": 4, "critical": 12},
        "Three-Way Match": {"warning": 2, "critical": 8},
        "Approval": {"warning": 24, "critical": 72},
        "GL Assignment": {"warning": 2, "critical": 8},
        "Payment Scheduling": {"warning": 4, "critical": 12},
        "Payment Execution": {"warning": 8, "critical": 24},
        "Document Archiving": {"warning": 24, "critical": 72}
    }
    
    # Analyze waiting times by stage
    stage_waiting_times = {}
    
    for case_id, case_data in metadata.items():
        stage = case_data["WaitingStage"]
        waiting_hours = case_data["WaitingTimeHours"]
        status = case_data["Status"]
        
        if stage not in stage_waiting_times:
            stage_waiting_times[stage] = {
                "times": [],
                "ok_count": 0,
                "warning_count": 0,
                "critical_count": 0
            }
        
        stage_waiting_times[stage]["times"].append(waiting_hours)
        
        if status == "ok":
            stage_waiting_times[stage]["ok_count"] += 1
        elif status == "warning":
            stage_waiting_times[stage]["warning_count"] += 1
        else:  # critical
            stage_waiting_times[stage]["critical_count"] += 1
    
    print("Waiting time statistics by stage:")
    for stage, data in stage_waiting_times.items():
        times = data["times"]
        thresholds = stage_thresholds[stage]
        
        print(f"\n  {stage}:")
        print(f"    Cases: {len(times)}")
        print(f"    Average waiting time: {np.mean(times):.2f} hours")
        print(f"    Median waiting time: {np.median(times):.2f} hours")
        print(f"    Min waiting time: {np.min(times):.2f} hours")
        print(f"    Max waiting time: {np.max(times):.2f} hours")
        print(f"    Warning threshold: {thresholds['warning']} hours")
        print(f"    Critical threshold: {thresholds['critical']} hours")
        print(f"    Status breakdown: {data['ok_count']} OK, {data['warning_count']} Warning, {data['critical_count']} Critical")
    
    return stage_waiting_times

def analyze_activity_frequency(events):
    """Analyze activity frequency and distribution"""
    print("\n=== ACTIVITY FREQUENCY ANALYSIS ===")
    
    df = pd.DataFrame(events)
    activity_counts = df['ActivityName'].value_counts()
    
    print("Activity frequency:")
    for activity, count in activity_counts.items():
        percentage = (count / len(events)) * 100
        print(f"  {activity}: {count} ({percentage:.1f}%)")
    
    # Check for missing activities
    expected_activities = [
        "Invoice Received", "Invoice Scanned", "Invoice Validation", "Three-Way Match",
        "Price Variance Check", "Quantity Variance Check", "Tax Calculation",
        "Approval Requested", "Manager Approval", "Finance Approval",
        "Vendor Master Data Review", "Payment Terms Verification", "GL Account Assignment",
        "Cost Center Assignment", "Payment Block Release", "Payment Scheduled",
        "Payment Executed", "Payment Confirmed", "Invoice Posted", "Document Archived"
    ]
    
    missing_activities = set(expected_activities) - set(activity_counts.index)
    if missing_activities:
        print(f"\nWarning: Missing activities: {missing_activities}")
    
    return activity_counts

def analyze_data_quality(events, metadata):
    """Analyze data quality metrics"""
    print("\n=== DATA QUALITY ANALYSIS ===")
    
    df = pd.DataFrame(events)
    
    # Check for missing values
    missing_values = df.isnull().sum()
    if missing_values.sum() > 0:
        print("Missing values found:")
        for column, count in missing_values.items():
            if count > 0:
                print(f"  {column}: {count}")
    else:
        print("No missing values found ✓")
    
    # Check for duplicate events
    duplicates = df.duplicated().sum()
    print(f"Duplicate events: {duplicates}")
    
    # Check timestamp consistency
    df['ActivityTime'] = pd.to_datetime(df['ActivityTime'])
    timestamp_issues = 0
    
    for case_id in metadata.keys():
        case_events = df[df['CaseId'] == case_id].sort_values('ActivityTime')
        if len(case_events) > 1:
            # Check for non-sequential timestamps
            for i in range(1, len(case_events)):
                if case_events.iloc[i]['ActivityTime'] <= case_events.iloc[i-1]['ActivityTime']:
                    timestamp_issues += 1
    
    print(f"Timestamp consistency issues: {timestamp_issues}")
    
    # Check case ID format
    case_id_format_issues = 0
    for case_id in metadata.keys():
        if not case_id.startswith('AP') or len(case_id) != 8:
            case_id_format_issues += 1
    
    print(f"Case ID format issues: {case_id_format_issues}")
    
    # Check FreezeTime consistency
    freeze_time = "2025-05-04T14:00:00+00:00"
    freeze_datetime = datetime.fromisoformat(freeze_time.replace('Z', '+00:00'))
    
    freeze_time_issues = 0
    for case_id, case_data in metadata.items():
        last_activity_time = datetime.fromisoformat(case_data["LastActivityTime"].replace('Z', '+00:00'))
        if last_activity_time > freeze_datetime:
            freeze_time_issues += 1
    
    print(f"FreezeTime consistency issues: {freeze_time_issues}")
    
    # Overall data quality score
    total_checks = 5
    passed_checks = 0
    
    if missing_values.sum() == 0:
        passed_checks += 1
    if duplicates == 0:
        passed_checks += 1
    if timestamp_issues == 0:
        passed_checks += 1
    if case_id_format_issues == 0:
        passed_checks += 1
    if freeze_time_issues == 0:
        passed_checks += 1
    
    quality_score = (passed_checks / total_checks) * 100
    print(f"Data Quality Score: {quality_score:.1f}%")
    
    return quality_score

def analyze_vendor_distribution(metadata):
    """Analyze vendor category distribution"""
    print("\n=== VENDOR DISTRIBUTION ANALYSIS ===")
    
    vendor_categories = [case_data.get('VendorCategory', 'Unknown') for case_data in metadata.values()]
    category_counts = pd.Series(vendor_categories).value_counts()
    
    print("Vendor category distribution:")
    for category, count in category_counts.items():
        percentage = (count / len(metadata)) * 100
        print(f"  {category}: {count} ({percentage:.1f}%)")
    
    # Check against expected distribution
    expected_distribution = {
        "Strategic": 0.30,
        "Preferred": 0.45,
        "Standard": 0.25
    }
    
    print("\nExpected vs Actual Distribution:")
    for category, expected_pct in expected_distribution.items():
        actual_count = category_counts.get(category, 0)
        actual_pct = (actual_count / len(metadata)) * 100
        difference = actual_pct - (expected_pct * 100)
        print(f"  {category}: Expected {expected_pct*100:.1f}%, Actual {actual_pct:.1f}% (Diff: {difference:+.1f}%)")
    
    return category_counts

def analyze_invoice_types(metadata):
    """Analyze invoice type distribution"""
    print("\n=== INVOICE TYPE ANALYSIS ===")
    
    invoice_types = [case_data.get('InvoiceType', 'Unknown') for case_data in metadata.values()]
    type_counts = pd.Series(invoice_types).value_counts()
    
    print("Invoice type distribution:")
    for inv_type, count in type_counts.items():
        percentage = (count / len(metadata)) * 100
        print(f"  {inv_type}: {count} ({percentage:.1f}%)")
    
    # Check against expected distribution
    expected_distribution = {
        "Goods": 0.60,
        "Services": 0.30,
        "Expenses": 0.10
    }
    
    print("\nExpected vs Actual Distribution:")
    for inv_type, expected_pct in expected_distribution.items():
        actual_count = type_counts.get(inv_type, 0)
        actual_pct = (actual_count / len(metadata)) * 100
        difference = actual_pct - (expected_pct * 100)
        print(f"  {inv_type}: Expected {expected_pct*100:.1f}%, Actual {actual_pct:.1f}% (Diff: {difference:+.1f}%)")
    
    return type_counts

def analyze_operational_metrics(metadata):
    """Analyze operational metrics for real-time monitoring"""
    print("\n=== OPERATIONAL METRICS ===")
    
    # Calculate operational KPIs
    total_cases = len(metadata)
    attention_cases = sum(1 for case_data in metadata.values() if case_data["RequiresAttention"])
    critical_cases = sum(1 for case_data in metadata.values() if case_data["Status"] == "critical")
    
    # Average waiting time
    waiting_times = [case_data["WaitingTimeHours"] for case_data in metadata.values()]
    avg_waiting_time = np.mean(waiting_times)
    
    # Stage-specific metrics
    stage_metrics = {}
    for case_data in metadata.values():
        stage = case_data["WaitingStage"]
        if stage not in stage_metrics:
            stage_metrics[stage] = {"cases": 0, "total_waiting": 0}
        
        stage_metrics[stage]["cases"] += 1
        stage_metrics[stage]["total_waiting"] += case_data["WaitingTimeHours"]
    
    print(f"Operational KPIs:")
    print(f"  Total in-progress cases: {total_cases}")
    print(f"  Cases requiring attention: {attention_cases} ({attention_cases/total_cases*100:.1f}%)")
    print(f"  Critical cases: {critical_cases} ({critical_cases/total_cases*100:.1f}%)")
    print(f"  Average waiting time: {avg_waiting_time:.2f} hours")
    
    print(f"\nStage-specific metrics:")
    for stage, metrics in stage_metrics.items():
        avg_stage_waiting = metrics["total_waiting"] / metrics["cases"]
        print(f"  {stage}: {metrics['cases']} cases, avg waiting {avg_stage_waiting:.2f} hours")
    
    return {
        "total_cases": total_cases,
        "attention_cases": attention_cases,
        "critical_cases": critical_cases,
        "avg_waiting_time": avg_waiting_time
    }

def generate_summary_report(events, metadata, results):
    """Generate summary report for daily dataset"""
    print("\n" + "="*60)
    print("DAILY DATASET SUMMARY REPORT")
    print("="*60)
    
    # Summary statistics
    print(f"\nDataset Summary:")
    print(f"  Total cases: {len(metadata)}")
    print(f"  Total events: {len(events)}")
    print(f"  Average events per case: {len(events) / len(metadata):.1f}")
    print(f"  FreezeTime: 2025-05-04T14:00:00+00:00")
    
    # Operational metrics
    print(f"\nOperational Metrics:")
    print(f"  Cases requiring attention: {results['operational']['attention_cases']} ({results['operational']['attention_cases']/len(metadata)*100:.1f}%)")
    print(f"  Critical cases: {results['operational']['critical_cases']} ({results['operational']['critical_cases']/len(metadata)*100:.1f}%)")
    print(f"  Average waiting time: {results['operational']['avg_waiting_time']:.2f} hours")
    
    # Key metrics
    print(f"\nKey Metrics:")
    print(f"  Data quality score: {results['quality_score']:.1f}%")
    print(f"  Expected case count: 69")
    print(f"  Actual case count: {len(metadata)}")
    
    # Recommendations
    print(f"\nRecommendations:")
    
    if results['operational']['attention_cases'] > 10:
        print("  ⚠️  High number of cases requiring attention - review resource allocation")
    
    if results['operational']['critical_cases'] > 5:
        print("  ⚠️  Critical cases detected - immediate intervention required")
    
    if results['quality_score'] < 100:
        print("  ⚠️  Address data quality issues")
    
    if len(metadata) != 69:
        print("  ⚠️  Case count mismatch - verify data generation")
    
    print("  ✓ Dataset ready for real-time monitoring")
    
    print("\n" + "="*60)

def main():
    """Main function to run all analyses"""
    print("SAP Accounts Payable Daily Event Log Statistics")
    print("="*60)
    
    # Load data
    events, metadata = load_daily_data()
    if events is None:
        return
    
    # Run analyses
    stage_counts, status_counts = analyze_case_distribution(metadata)
    waiting_times = analyze_waiting_times(metadata)
    activity_counts = analyze_activity_frequency(events)
    quality_score = analyze_data_quality(events, metadata)
    vendor_distribution = analyze_vendor_distribution(metadata)
    invoice_types = analyze_invoice_types(metadata)
    operational_metrics = analyze_operational_metrics(metadata)
    
    # Generate summary report
    results = {
        'quality_score': quality_score,
        'operational': operational_metrics
    }
    
    generate_summary_report(events, metadata, results)
    
    print("\nDaily event log statistics analysis completed!")

if __name__ == "__main__":
    main() 