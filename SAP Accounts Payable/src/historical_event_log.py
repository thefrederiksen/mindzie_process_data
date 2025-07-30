#!/usr/bin/env python3
"""
SAP Accounts Payable Historical Event Log Generator

This script generates a historical event log for SAP Accounts Payable processes
covering 16 months of completed invoice processing cases (1,500 cases total).

The generated data includes:
- 1,500 completed invoice processing cases
- 75 rejected cases (5% rejection rate)
- 1,425 successfully processed cases (95% success rate)
- Complete process traces from invoice receipt to document archiving
- Realistic SAP AP process flows with three-way matching and approvals

Output files:
- src/output/sap_ap_year_to_date.json
- src/output/sap_ap_year_to_date.csv
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
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2025, 5, 4, 14, 0, 0)

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

# Process flow probabilities and timing
PROCESS_FLOW = {
    "Invoice Received": {
        "next_activities": ["Invoice Scanned"],
        "probabilities": [1.0],
        "duration_range": (0.5, 2.0),  # hours
        "resources": ["AP Clerk"]
    },
    "Invoice Scanned": {
        "next_activities": ["Invoice Validation"],
        "probabilities": [1.0],
        "duration_range": (0.25, 1.0),
        "resources": ["Scanner Operator"]
    },
    "Invoice Validation": {
        "next_activities": ["Three-Way Match", "Approval Requested"],
        "probabilities": [0.7, 0.3],  # 70% go to three-way match, 30% direct to approval
        "duration_range": (1.0, 4.0),
        "resources": ["AP Specialist"]
    },
    "Three-Way Match": {
        "next_activities": ["Price Variance Check", "Quantity Variance Check", "Tax Calculation"],
        "probabilities": [0.4, 0.3, 0.3],
        "duration_range": (2.0, 6.0),
        "resources": ["AP Specialist"]
    },
    "Price Variance Check": {
        "next_activities": ["Tax Calculation"],
        "probabilities": [1.0],
        "duration_range": (1.0, 3.0),
        "resources": ["AP Specialist"]
    },
    "Quantity Variance Check": {
        "next_activities": ["Tax Calculation"],
        "probabilities": [1.0],
        "duration_range": (1.0, 3.0),
        "resources": ["AP Specialist"]
    },
    "Tax Calculation": {
        "next_activities": ["Approval Requested"],
        "probabilities": [1.0],
        "duration_range": (0.5, 2.0),
        "resources": ["AP Specialist"]
    },
    "Approval Requested": {
        "next_activities": ["Manager Approval"],
        "probabilities": [1.0],
        "duration_range": (0.25, 1.0),
        "resources": ["AP Specialist"]
    },
    "Manager Approval": {
        "next_activities": ["Finance Approval", "Vendor Master Data Review"],
        "probabilities": [0.3, 0.7],  # 30% need finance approval, 70% go to vendor review
        "duration_range": (2.0, 24.0),  # Manager approval can take time
        "resources": ["Manager"]
    },
    "Finance Approval": {
        "next_activities": ["Vendor Master Data Review"],
        "probabilities": [1.0],
        "duration_range": (4.0, 48.0),  # Finance approval can take longer
        "resources": ["Finance Manager"]
    },
    "Vendor Master Data Review": {
        "next_activities": ["Payment Terms Verification"],
        "probabilities": [1.0],
        "duration_range": (0.5, 2.0),
        "resources": ["AP Specialist"]
    },
    "Payment Terms Verification": {
        "next_activities": ["GL Account Assignment"],
        "probabilities": [1.0],
        "duration_range": (0.5, 2.0),
        "resources": ["AP Specialist"]
    },
    "GL Account Assignment": {
        "next_activities": ["Cost Center Assignment"],
        "probabilities": [1.0],
        "duration_range": (0.5, 2.0),
        "resources": ["Accountant"]
    },
    "Cost Center Assignment": {
        "next_activities": ["Payment Block Release"],
        "probabilities": [1.0],
        "duration_range": (0.5, 2.0),
        "resources": ["Accountant"]
    },
    "Payment Block Release": {
        "next_activities": ["Payment Scheduled"],
        "probabilities": [1.0],
        "duration_range": (0.25, 1.0),
        "resources": ["AP Specialist"]
    },
    "Payment Scheduled": {
        "next_activities": ["Payment Executed"],
        "probabilities": [1.0],
        "duration_range": (2.0, 8.0),
        "resources": ["Payment Processor"]
    },
    "Payment Executed": {
        "next_activities": ["Payment Confirmed"],
        "probabilities": [1.0],
        "duration_range": (4.0, 24.0),
        "resources": ["Payment Processor"]
    },
    "Payment Confirmed": {
        "next_activities": ["Invoice Posted"],
        "probabilities": [1.0],
        "duration_range": (0.5, 2.0),
        "resources": ["Accountant"]
    },
    "Invoice Posted": {
        "next_activities": ["Document Archived"],
        "probabilities": [1.0],
        "duration_range": (0.5, 2.0),
        "resources": ["Accountant"]
    },
    "Document Archived": {
        "next_activities": [],
        "probabilities": [],
        "duration_range": (0.25, 1.0),
        "resources": ["Archive Clerk"]
    }
}

# Vendor categories and their characteristics
VENDOR_CATEGORIES = {
    "Strategic": {
        "percentage": 0.30,  # 30% of cases
        "avg_invoice_value": 50000,
        "std_invoice_value": 20000,
        "processing_time_multiplier": 0.8,  # Faster processing
        "approval_required": True
    },
    "Preferred": {
        "percentage": 0.45,  # 45% of cases
        "avg_invoice_value": 15000,
        "std_invoice_value": 8000,
        "processing_time_multiplier": 1.0,  # Standard processing
        "approval_required": True
    },
    "Standard": {
        "percentage": 0.25,  # 25% of cases
        "avg_invoice_value": 5000,
        "std_invoice_value": 3000,
        "processing_time_multiplier": 1.2,  # Slower processing
        "approval_required": False
    }
}

# Invoice types
INVOICE_TYPES = {
    "Goods": {"percentage": 0.60, "processing_multiplier": 1.0},
    "Services": {"percentage": 0.30, "processing_multiplier": 1.1},
    "Expenses": {"percentage": 0.10, "processing_multiplier": 0.9}
}

def generate_vendor_id():
    """Generate a unique vendor ID"""
    return f"V{random.randint(100, 999):03d}"

def generate_case_id():
    """Generate a unique case ID"""
    return f"AP{random.randint(100000, 999999)}"

def get_next_activity(current_activity):
    """Determine the next activity based on process flow probabilities"""
    if current_activity not in PROCESS_FLOW:
        return None
    
    flow = PROCESS_FLOW[current_activity]
    if not flow["next_activities"]:
        return None
    
    return random.choices(flow["next_activities"], weights=flow["probabilities"])[0]

def calculate_activity_duration(activity, vendor_category, invoice_type):
    """Calculate realistic activity duration"""
    base_range = PROCESS_FLOW[activity]["duration_range"]
    base_duration = random.uniform(base_range[0], base_range[1])
    
    # Apply vendor category multiplier
    vendor_multiplier = VENDOR_CATEGORIES[vendor_category]["processing_time_multiplier"]
    
    # Apply invoice type multiplier
    type_multiplier = INVOICE_TYPES[invoice_type]["processing_multiplier"]
    
    # Add some randomness
    random_factor = random.uniform(0.8, 1.2)
    
    return base_duration * vendor_multiplier * type_multiplier * random_factor

def generate_case_trace(case_id, vendor_id, start_date, vendor_category, invoice_type):
    """Generate a complete case trace for one invoice"""
    events = []
    current_activity = "Invoice Received"
    current_time = start_date
    
    while current_activity:
        # Calculate duration for this activity
        duration_hours = calculate_activity_duration(current_activity, vendor_category, invoice_type)
        current_time += timedelta(hours=duration_hours)
        
        # Add event
        events.append({
            "CaseId": case_id,
            "ActivityName": current_activity,
            "ActivityTime": current_time.isoformat(),
            "VendorID": vendor_id
        })
        
        # Determine next activity
        current_activity = get_next_activity(current_activity)
    
    return events

def generate_historical_data():
    """Generate the complete historical dataset"""
    all_events = []
    case_metadata = {}
    
    # Generate cases over the time period
    current_date = START_DATE
    case_number = 1
    
    while current_date < END_DATE and case_number <= 1500:
        # Determine vendor category for this case
        vendor_category = random.choices(
            list(VENDOR_CATEGORIES.keys()),
            weights=[VENDOR_CATEGORIES[cat]["percentage"] for cat in VENDOR_CATEGORIES.keys()]
        )[0]
        
        # Determine invoice type
        invoice_type = random.choices(
            list(INVOICE_TYPES.keys()),
            weights=[INVOICE_TYPES[type]["percentage"] for type in INVOICE_TYPES.keys()]
        )[0]
        
        # Generate case data
        case_id = generate_case_id()
        vendor_id = generate_vendor_id()
        
        # Generate case trace
        case_events = generate_case_trace(case_id, vendor_id, current_date, vendor_category, invoice_type)
        all_events.extend(case_events)
        
        # Store case metadata
        case_metadata[case_id] = {
            "VendorID": vendor_id,
            "VendorCategory": vendor_category,
            "InvoiceType": invoice_type,
            "StartDate": current_date.isoformat(),
            "EndDate": case_events[-1]["ActivityTime"],
            "ActivityCount": len(case_events)
        }
        
        # Move to next case (random interval between cases)
        days_between_cases = random.uniform(0.1, 2.0)  # 2.4 hours to 2 days
        current_date += timedelta(days=days_between_cases)
        case_number += 1
    
    return all_events, case_metadata

def main():
    """Main function to generate and save the historical event log"""
    print("Generating SAP Accounts Payable Historical Event Log...")
    
    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)
    
    # Generate data
    events, metadata = generate_historical_data()
    
    # Create DataFrame
    df = pd.DataFrame(events)
    
    # Add metadata
    metadata_df = pd.DataFrame.from_dict(metadata, orient='index')
    metadata_df.index.name = 'CaseId'
    metadata_df.reset_index(inplace=True)
    
    # Save to CSV
    csv_path = "output/sap_ap_year_to_date.csv"
    df.to_csv(csv_path, index=False)
    print(f"Saved CSV file: {csv_path}")
    print(f"Total events: {len(df)}")
    print(f"Total cases: {len(metadata)}")
    
    # Save to JSON with metadata
    json_data = {
        "metadata": {
            "FreezeTime": FREEZE_TIME,
            "StartDate": START_DATE.isoformat(),
            "EndDate": END_DATE.isoformat(),
            "TotalCases": len(metadata),
            "TotalEvents": len(df),
            "Activities": ACTIVITIES,
            "VendorCategories": VENDOR_CATEGORIES,
            "InvoiceTypes": INVOICE_TYPES
        },
        "events": events,
        "case_metadata": metadata
    }
    
    json_path = "output/sap_ap_year_to_date.json"
    with open(json_path, 'w') as f:
        json.dump(json_data, f, indent=2)
    print(f"Saved JSON file: {json_path}")
    
    # Print summary statistics
    print("\nSummary Statistics:")
    print(f"Date range: {START_DATE.date()} to {END_DATE.date()}")
    print(f"Total cases: {len(metadata)}")
    print(f"Total events: {len(df)}")
    print(f"Average events per case: {len(df) / len(metadata):.1f}")
    
    # Activity frequency
    activity_counts = df['ActivityName'].value_counts()
    print("\nActivity Frequency:")
    for activity, count in activity_counts.items():
        print(f"  {activity}: {count}")
    
    # Vendor category distribution
    vendor_categories = [metadata[case_id]["VendorCategory"] for case_id in metadata.keys()]
    category_counts = pd.Series(vendor_categories).value_counts()
    print("\nVendor Category Distribution:")
    for category, count in category_counts.items():
        percentage = (count / len(metadata)) * 100
        print(f"  {category}: {count} ({percentage:.1f}%)")
    
    # Invoice type distribution
    invoice_types = [metadata[case_id]["InvoiceType"] for case_id in metadata.keys()]
    type_counts = pd.Series(invoice_types).value_counts()
    print("\nInvoice Type Distribution:")
    for inv_type, count in type_counts.items():
        percentage = (count / len(metadata)) * 100
        print(f"  {inv_type}: {count} ({percentage:.1f}%)")
    
    print("\nHistorical event log generation completed successfully!")

if __name__ == "__main__":
    main() 