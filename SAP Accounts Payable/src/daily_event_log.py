#!/usr/bin/env python3
"""
SAP Accounts Payable Daily Event Log Generator

This script generates a current day event log for SAP Accounts Payable processes
with 69 in-progress invoice processing cases for real-time monitoring.

The generated data includes:
- 69 in-progress invoice processing cases
- Cases distributed across 8 different waiting stages
- Realistic waiting times based on FreezeTime
- Cases requiring attention (warning and critical thresholds)
- Real-time monitoring data for command center dashboards

Output files:
- src/output/sap_ap_daily.json
- src/output/sap_ap_daily.csv
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# Set random seed for reproducibility
random.seed(42)
np.random.seed(42)

# Configuration
FREEZE_TIME = "2025-05-04T14:00:00+00:00"
FREEZE_DATETIME = datetime.fromisoformat(FREEZE_TIME.replace('Z', '+00:00'))

# Stage thresholds (in hours) for monitoring
STAGE_THRESHOLDS = {
    "Invoice Scanning": {"warning": 2, "critical": 8},
    "Validation": {"warning": 4, "critical": 12},
    "Three-Way Match": {"warning": 2, "critical": 8},
    "Approval": {"warning": 24, "critical": 72},
    "GL Assignment": {"warning": 2, "critical": 8},
    "Payment Scheduling": {"warning": 4, "critical": 12},
    "Payment Execution": {"warning": 8, "critical": 24},
    "Document Archiving": {"warning": 24, "critical": 72}
}

# Current day case distribution (69 total cases)
CASE_DISTRIBUTION = {
    "Invoice Scanning": {"total": 8, "ok": 6, "warning": 2, "critical": 0},
    "Validation": {"total": 12, "ok": 9, "warning": 3, "critical": 0},
    "Three-Way Match": {"total": 6, "ok": 5, "warning": 1, "critical": 0},
    "Approval": {"total": 15, "ok": 10, "warning": 3, "critical": 2},
    "GL Assignment": {"total": 4, "ok": 4, "warning": 0, "critical": 0},
    "Payment Scheduling": {"total": 8, "ok": 6, "warning": 2, "critical": 0},
    "Payment Execution": {"total": 6, "ok": 5, "warning": 1, "critical": 0},
    "Document Archiving": {"total": 10, "ok": 8, "warning": 2, "critical": 0}
}

# SAP AP Activities (20 activities total)
ACTIVITIES = [
    "Invoice Received",
    "Invoice Scanned", 
    "Invoice Validation",
    "Three-Way Match",
    "Price Variance Check",
    "Quantity Variance Check",
    "Tax Calculation",
    "Approval Requested",
    "Manager Approval",
    "Finance Approval",
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

# Process flow for determining last completed activity
PROCESS_FLOW = {
    "Invoice Received": "Invoice Scanned",
    "Invoice Scanned": "Invoice Validation",
    "Invoice Validation": "Three-Way Match",
    "Three-Way Match": "Price Variance Check",
    "Price Variance Check": "Tax Calculation",
    "Quantity Variance Check": "Tax Calculation",
    "Tax Calculation": "Approval Requested",
    "Approval Requested": "Manager Approval",
    "Manager Approval": "Vendor Master Data Review",
    "Finance Approval": "Vendor Master Data Review",
    "Vendor Master Data Review": "Payment Terms Verification",
    "Payment Terms Verification": "GL Account Assignment",
    "GL Account Assignment": "Cost Center Assignment",
    "Cost Center Assignment": "Payment Block Release",
    "Payment Block Release": "Payment Scheduled",
    "Payment Scheduled": "Payment Executed",
    "Payment Executed": "Payment Confirmed",
    "Payment Confirmed": "Invoice Posted",
    "Invoice Posted": "Document Archived"
}

# Vendor categories
VENDOR_CATEGORIES = ["Strategic", "Preferred", "Standard"]
INVOICE_TYPES = ["Goods", "Services", "Expenses"]

def generate_vendor_id():
    """Generate a unique vendor ID"""
    return f"V{random.randint(100, 999):03d}"

def generate_case_id():
    """Generate a unique case ID"""
    return f"AP{random.randint(100000, 999999)}"

def get_last_completed_activity(waiting_stage):
    """Get the last completed activity based on waiting stage"""
    # Reverse lookup to find the activity that leads to the waiting stage
    for activity, next_activity in PROCESS_FLOW.items():
        if next_activity == waiting_stage:
            return activity
    
    # If not found, return a reasonable default
    stage_to_activity_map = {
        "Invoice Scanning": "Invoice Received",
        "Validation": "Invoice Scanned",
        "Three-Way Match": "Invoice Validation",
        "Approval": "Tax Calculation",
        "GL Assignment": "Payment Terms Verification",
        "Payment Scheduling": "Payment Block Release",
        "Payment Execution": "Payment Scheduled",
        "Document Archiving": "Invoice Posted"
    }
    return stage_to_activity_map.get(waiting_stage, "Invoice Received")

def calculate_waiting_time(status, stage):
    """Calculate waiting time based on status and stage"""
    thresholds = STAGE_THRESHOLDS[stage]
    
    if status == "ok":
        # Within acceptable limits
        return random.uniform(0.1, thresholds["warning"] * 0.8)
    elif status == "warning":
        # Exceeding warning threshold
        return random.uniform(thresholds["warning"] * 0.8, thresholds["critical"] * 0.8)
    else:  # critical
        # Exceeding critical threshold
        return random.uniform(thresholds["critical"] * 0.8, thresholds["critical"] * 1.5)

def generate_case_events(case_id, vendor_id, waiting_stage, status, start_date):
    """Generate events for an in-progress case"""
    events = []
    current_time = start_date
    
    # Generate events up to the last completed activity
    last_completed = get_last_completed_activity(waiting_stage)
    
    # Start with Invoice Received
    current_activity = "Invoice Received"
    
    while current_activity and current_activity != last_completed:
        # Add some processing time
        processing_hours = random.uniform(0.5, 4.0)
        current_time += timedelta(hours=processing_hours)
        
        events.append({
            "CaseId": case_id,
            "ActivityName": current_activity,
            "ActivityTime": current_time.isoformat(),
            "VendorID": vendor_id
        })
        
        # Move to next activity
        current_activity = PROCESS_FLOW.get(current_activity)
    
    # Add the last completed activity
    if last_completed:
        processing_hours = random.uniform(0.5, 4.0)
        current_time += timedelta(hours=processing_hours)
        
        events.append({
            "CaseId": case_id,
            "ActivityName": last_completed,
            "ActivityTime": current_time.isoformat(),
            "VendorID": vendor_id
        })
    
    return events

def generate_daily_data():
    """Generate the current day dataset with in-progress cases"""
    all_events = []
    case_metadata = {}
    
    # Generate cases for each stage
    for stage, distribution in CASE_DISTRIBUTION.items():
        for status in ["ok", "warning", "critical"]:
            count = distribution[status]
            
            for i in range(count):
                # Generate case data
                case_id = generate_case_id()
                vendor_id = generate_vendor_id()
                vendor_category = random.choice(VENDOR_CATEGORIES)
                invoice_type = random.choice(INVOICE_TYPES)
                
                # Calculate start date (random time before FreezeTime)
                days_before = random.uniform(1, 30)  # 1-30 days before FreezeTime
                start_date = FREEZE_DATETIME - timedelta(days=days_before)
                
                # Generate case events
                case_events = generate_case_events(case_id, vendor_id, stage, status, start_date)
                all_events.extend(case_events)
                
                # Calculate waiting time
                waiting_hours = calculate_waiting_time(status, stage)
                last_event_time = datetime.fromisoformat(case_events[-1]["ActivityTime"].replace('Z', '+00:00'))
                
                # Store case metadata
                case_metadata[case_id] = {
                    "VendorID": vendor_id,
                    "VendorCategory": vendor_category,
                    "InvoiceType": invoice_type,
                    "WaitingStage": stage,
                    "Status": status,
                    "StartDate": start_date.isoformat(),
                    "LastActivityTime": case_events[-1]["ActivityTime"],
                    "WaitingTimeHours": waiting_hours,
                    "ActivityCount": len(case_events),
                    "RequiresAttention": status in ["warning", "critical"]
                }
    
    return all_events, case_metadata

def main():
    """Main function to generate and save the daily event log"""
    print("Generating SAP Accounts Payable Daily Event Log...")
    
    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)
    
    # Generate data
    events, metadata = generate_daily_data()
    
    # Create DataFrame
    df = pd.DataFrame(events)
    
    # Save to CSV
    csv_path = "output/sap_ap_daily.csv"
    df.to_csv(csv_path, index=False)
    print(f"Saved CSV file: {csv_path}")
    print(f"Total events: {len(df)}")
    print(f"Total cases: {len(metadata)}")
    
    # Save to JSON with metadata
    json_data = {
        "metadata": {
            "FreezeTime": FREEZE_TIME,
            "TotalCases": len(metadata),
            "TotalEvents": len(df),
            "Activities": ACTIVITIES,
            "StageThresholds": STAGE_THRESHOLDS,
            "CaseDistribution": CASE_DISTRIBUTION
        },
        "events": events,
        "case_metadata": metadata
    }
    
    json_path = "output/sap_ap_daily.json"
    with open(json_path, 'w') as f:
        json.dump(json_data, f, indent=2)
    print(f"Saved JSON file: {json_path}")
    
    # Print summary statistics
    print("\nSummary Statistics:")
    print(f"FreezeTime: {FREEZE_TIME}")
    print(f"Total cases: {len(metadata)}")
    print(f"Total events: {len(df)}")
    print(f"Average events per case: {len(df) / len(metadata):.1f}")
    
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
    
    # Activity frequency
    activity_counts = df['ActivityName'].value_counts()
    print("\nActivity Frequency:")
    for activity, count in activity_counts.head(10).items():
        print(f"  {activity}: {count}")
    
    print("\nDaily event log generation completed successfully!")

if __name__ == "__main__":
    main() 