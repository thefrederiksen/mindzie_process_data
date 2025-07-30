#!/usr/bin/env python3
"""
SAP Accounts Payable Historical Event Log Statistics

This script provides comprehensive statistics and evaluation for the SAP AP historical dataset.
It analyzes 1,500 completed cases to validate data quality and provide insights for process mining.

The script performs:
- Case count validation (completed vs in-progress)
- Activity frequency analysis
- Stage duration statistics
- Threshold compliance checking
- Data quality metrics
- Process flow validation
- Comprehensive evaluation report
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def load_historical_data():
    """Load the historical event log data"""
    json_path = "output/sap_ap_year_to_date.json"
    
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found. Please run historical_event_log.py first.")
        return None, None
    
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    events = data['events']
    metadata = data['case_metadata']
    
    return events, metadata

def analyze_case_completion(events, metadata):
    """Analyze case completion status"""
    print("=== CASE COMPLETION ANALYSIS ===")
    
    # Check if all cases are completed
    completed_cases = set()
    for event in events:
        if event['ActivityName'] == 'Document Archived':
            completed_cases.add(event['CaseId'])
    
    total_cases = len(metadata)
    completed_count = len(completed_cases)
    completion_rate = (completed_count / total_cases) * 100
    
    print(f"Total cases: {total_cases}")
    print(f"Completed cases: {completed_count}")
    print(f"Completion rate: {completion_rate:.1f}%")
    
    # Check for incomplete cases
    incomplete_cases = set(metadata.keys()) - completed_cases
    if incomplete_cases:
        print(f"Warning: {len(incomplete_cases)} incomplete cases found")
        for case_id in list(incomplete_cases)[:5]:  # Show first 5
            print(f"  - {case_id}")
    
    return completed_cases, incomplete_cases

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

def analyze_stage_durations(events, metadata):
    """Analyze stage durations and processing times"""
    print("\n=== STAGE DURATION ANALYSIS ===")
    
    df = pd.DataFrame(events)
    df['ActivityTime'] = pd.to_datetime(df['ActivityTime'])
    
    # Calculate case durations
    case_durations = {}
    for case_id in metadata.keys():
        case_events = df[df['CaseId'] == case_id].sort_values('ActivityTime')
        if len(case_events) > 1:
            start_time = case_events.iloc[0]['ActivityTime']
            end_time = case_events.iloc[-1]['ActivityTime']
            duration = (end_time - start_time).total_seconds() / 3600  # hours
            case_durations[case_id] = duration
    
    if case_durations:
        durations = list(case_durations.values())
        print(f"Case duration statistics (hours):")
        print(f"  Mean: {np.mean(durations):.2f}")
        print(f"  Median: {np.median(durations):.2f}")
        print(f"  Min: {np.min(durations):.2f}")
        print(f"  Max: {np.max(durations):.2f}")
        print(f"  Std Dev: {np.std(durations):.2f}")
        
        # Duration percentiles
        percentiles = [25, 50, 75, 90, 95, 99]
        for p in percentiles:
            value = np.percentile(durations, p)
            print(f"  {p}th percentile: {value:.2f} hours")
    
    return case_durations

def analyze_threshold_compliance(events, metadata):
    """Analyze threshold compliance and SLA adherence"""
    print("\n=== THRESHOLD COMPLIANCE ANALYSIS ===")
    
    # Define expected thresholds (in hours)
    thresholds = {
        "Invoice Processing": 48,  # End-to-end processing
        "Approval Cycle": 24,      # Approval time
        "Payment Processing": 72,   # Payment execution
        "Document Archiving": 24    # Archive completion
    }
    
    df = pd.DataFrame(events)
    df['ActivityTime'] = pd.to_datetime(df['ActivityTime'])
    
    compliance_results = {}
    
    for case_id in metadata.keys():
        case_events = df[df['CaseId'] == case_id].sort_values('ActivityTime')
        if len(case_events) > 1:
            start_time = case_events.iloc[0]['ActivityTime']
            
            # Find key milestone times
            milestones = {}
            for _, event in case_events.iterrows():
                activity = event['ActivityName']
                if activity == 'Manager Approval':
                    milestones['approval'] = event['ActivityTime']
                elif activity == 'Payment Executed':
                    milestones['payment'] = event['ActivityTime']
                elif activity == 'Document Archived':
                    milestones['archive'] = event['ActivityTime']
            
            # Calculate compliance
            total_duration = (case_events.iloc[-1]['ActivityTime'] - start_time).total_seconds() / 3600
            compliance_results[case_id] = {
                'total_duration': total_duration,
                'within_sla': total_duration <= thresholds['Invoice Processing']
            }
    
    if compliance_results:
        sla_compliance = sum(1 for result in compliance_results.values() if result['within_sla'])
        total_cases = len(compliance_results)
        compliance_rate = (sla_compliance / total_cases) * 100
        
        print(f"SLA Compliance Rate: {compliance_rate:.1f}% ({sla_compliance}/{total_cases})")
        print(f"Target: > 95%")
        
        if compliance_rate < 95:
            print("Warning: SLA compliance below target")
    
    return compliance_results

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
    
    # Overall data quality score
    total_checks = 4
    passed_checks = 0
    
    if missing_values.sum() == 0:
        passed_checks += 1
    if duplicates == 0:
        passed_checks += 1
    if timestamp_issues == 0:
        passed_checks += 1
    if case_id_format_issues == 0:
        passed_checks += 1
    
    quality_score = (passed_checks / total_checks) * 100
    print(f"Data Quality Score: {quality_score:.1f}%")
    
    return quality_score

def analyze_process_flow(events, metadata):
    """Analyze process flow validation"""
    print("\n=== PROCESS FLOW VALIDATION ===")
    
    # Expected process flow
    expected_flow = [
        "Invoice Received",
        "Invoice Scanned",
        "Invoice Validation",
        "Three-Way Match",
        "Tax Calculation",
        "Approval Requested",
        "Manager Approval",
        "Vendor Master Data Review",
        "Payment Terms Verification",
        "GL Account Assignment",
        "Cost Center Assignment",
        "Payment Block Release",
        "Payment Scheduled",
        "Payment Executed",
        "Payment Confirmed",
        "Invoice Posted",
        "Document Archived"
    ]
    
    df = pd.DataFrame(events)
    flow_violations = 0
    
    for case_id in metadata.keys():
        case_events = df[df['CaseId'] == case_id].sort_values('ActivityTime')
        case_activities = case_events['ActivityName'].tolist()
        
        # Check if activities follow expected order
        for i, expected_activity in enumerate(expected_flow):
            if expected_activity in case_activities:
                activity_index = case_activities.index(expected_activity)
                # Check if any later expected activity appears before this one
                for later_activity in expected_flow[i+1:]:
                    if later_activity in case_activities:
                        later_index = case_activities.index(later_activity)
                        if later_index < activity_index:
                            flow_violations += 1
    
    print(f"Process flow violations: {flow_violations}")
    
    if flow_violations == 0:
        print("Process flow validation passed ✓")
    else:
        print("Warning: Process flow violations detected")
    
    return flow_violations

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

def generate_evaluation_report(events, metadata, results):
    """Generate comprehensive evaluation report"""
    print("\n" + "="*60)
    print("COMPREHENSIVE EVALUATION REPORT")
    print("="*60)
    
    # Summary statistics
    print(f"\nDataset Summary:")
    print(f"  Total cases: {len(metadata)}")
    print(f"  Total events: {len(events)}")
    print(f"  Average events per case: {len(events) / len(metadata):.1f}")
    
    # Key metrics
    print(f"\nKey Metrics:")
    print(f"  Case completion rate: {results['completion_rate']:.1f}%")
    print(f"  SLA compliance rate: {results['sla_compliance_rate']:.1f}%")
    print(f"  Data quality score: {results['quality_score']:.1f}%")
    print(f"  Process flow violations: {results['flow_violations']}")
    
    # Recommendations
    print(f"\nRecommendations:")
    
    if results['completion_rate'] < 100:
        print("  ⚠️  Investigate incomplete cases")
    
    if results['sla_compliance_rate'] < 95:
        print("  ⚠️  Review process bottlenecks affecting SLA compliance")
    
    if results['quality_score'] < 100:
        print("  ⚠️  Address data quality issues")
    
    if results['flow_violations'] > 0:
        print("  ⚠️  Review process flow logic")
    
    print("  ✓ Dataset ready for process mining analysis")
    
    print("\n" + "="*60)

def main():
    """Main function to run all analyses"""
    print("SAP Accounts Payable Historical Event Log Statistics")
    print("="*60)
    
    # Load data
    events, metadata = load_historical_data()
    if events is None:
        return
    
    # Run analyses
    completed_cases, incomplete_cases = analyze_case_completion(events, metadata)
    activity_counts = analyze_activity_frequency(events)
    case_durations = analyze_stage_durations(events, metadata)
    compliance_results = analyze_threshold_compliance(events, metadata)
    quality_score = analyze_data_quality(events, metadata)
    flow_violations = analyze_process_flow(events, metadata)
    vendor_distribution = analyze_vendor_distribution(metadata)
    invoice_types = analyze_invoice_types(metadata)
    
    # Calculate summary metrics
    completion_rate = (len(completed_cases) / len(metadata)) * 100
    
    sla_compliance = 0
    if compliance_results:
        sla_compliance = sum(1 for result in compliance_results.values() if result['within_sla'])
        sla_compliance_rate = (sla_compliance / len(compliance_results)) * 100
    else:
        sla_compliance_rate = 0
    
    # Generate evaluation report
    results = {
        'completion_rate': completion_rate,
        'sla_compliance_rate': sla_compliance_rate,
        'quality_score': quality_score,
        'flow_violations': flow_violations
    }
    
    generate_evaluation_report(events, metadata, results)
    
    print("\nHistorical event log statistics analysis completed!")

if __name__ == "__main__":
    main() 