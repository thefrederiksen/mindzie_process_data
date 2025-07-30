# SAP Accounts Payable Process Mining Dataset

**Project:** Process mining analysis and real-time monitoring for SAP Accounts Payable processes  
**System:** SAP ERP Accounts Payable Module  
**Snapshot Date:** 2025-05-04 at 14:00:00  
**Location:** Corporate Finance Department  

## 🚀 Quick Start: Mindzie Studio Project

**Ready to explore?** Download the complete Mindzie Studio project with all data and process flow monitoring dashboards!

- **Project File:** `mindzie_studio/SAP Accounts Payable.mpz`
- **Requirements:** Mindzie Desktop or Mindzie Enterprise access
- **What's Included:** 
  - Complete SAP AP process data
  - Real-time process flow monitoring dashboards
  - Historical analysis and process mining models
  - Command centre configurations

Simply download the `.mpz` file and upload it to your Mindzie Studio environment to start exploring the SAP Accounts Payable process mining system immediately.

---

## Project Overview

This project demonstrates how to implement process mining analysis and real-time monitoring for SAP Accounts Payable processes. The goal is to show how process mining can be applied to financial processes to identify bottlenecks, optimize resource allocation, and improve operational efficiency.

### Key Objectives
- Demonstrate process mining analysis for SAP AP processes
- Show how to set up real-time monitoring for accounts payable operations
- Illustrate the transition from historical analysis to operational control
- Provide practical implementation guidance for SAP AP process optimization

## Data Structure

The project uses synthetic SAP Accounts Payable data that simulates invoice processing through various stages:

- **Invoice receipt and scanning**
- **Validation and three-way matching**
- **Approval workflows**
- **Payment processing and execution**
- **Document archiving and compliance**

### Event Log Structure

Each row in the event log represents a single activity for a single invoice processing case:

- **CaseId**: Uniquely identifies an invoice processing case (format: AP######)
- **ActivityName**: The step or event that occurred (e.g., Invoice Received, Invoice Scanned)
- **ActivityTime**: The timestamp when the activity was completed
- **VendorID**: Unique identifier for the vendor (all events for the same CaseId have the same VendorID)

### Example Row
| CaseId   | ActivityName   | ActivityTime        | VendorID |
|----------|---------------|---------------------|----------|
| AP123456 | Invoice Received | 2025-05-04 08:15:00 | V001     |

## Data Generation

The project uses a two-dataset approach:

### 1. Historical Dataset
- **Purpose**: Traditional process mining analysis (bottlenecks, rework, conformance)
- **Content**: 16 months of completed invoice processing cases
- **Script**: `src/historical_event_log.py`
- **Output**: 
  - `src/output/sap_ap_year_to_date.json`
  - `src/output/sap_ap_year_to_date.csv`

### 2. Current State Dataset (Real-time)
- **Purpose**: Real-time process flow monitoring
- **Content**: Daily data with all in-progress invoice cases
- **Script**: `src/daily_event_log.py`
- **Output**:
  - `src/output/sap_ap_daily.json`
  - `src/output/sap_ap_daily.csv`

### How to Generate Data

```bash
# Generate historical dataset
python src/historical_event_log.py

# Generate current state dataset
python src/daily_event_log.py
```

**Note**: Both scripts use a fixed random seed for reproducibility.

## FreezeTime (Snapshot Time)

The event log is generated as a snapshot of the Accounts Payable process at a specific point in time, called the **FreezeTime**. This is the reference time for all calculations of processing times and for determining which invoices are currently in progress versus completed.

```
"FreezeTime": "2025-05-04T14:00:00+00:00"
```

- All processing time calculations for in-progress cases are based on the difference between the FreezeTime and the timestamp of the last completed activity for each case
- The FreezeTime is set in the generator script and should always reflect the current snapshot time for the log

## SAP AP Process Flow

The typical invoice processing journey follows this path:

1. **Invoice Received** - Invoice enters the system
2. **Invoice Scanned** - Physical invoice is scanned and digitized
3. **Invoice Validation** - Invoice is validated against business rules
4. **Three-Way Match** - Invoice matched with PO and goods receipt (if applicable)
5. **Tax Calculation** - Tax amounts are calculated and verified
6. **Approval Requested** - Invoice is submitted for approval
7. **Manager Approval** - Manager approves the invoice
8. **Finance Approval** - Finance department approves (if required)
9. **GL Account Assignment** - General ledger accounts are assigned
10. **Cost Center Assignment** - Cost centers are assigned
11. **Payment Scheduled** - Payment is scheduled for processing
12. **Payment Executed** - Payment is executed and sent
13. **Payment Confirmed** - Payment is confirmed and reconciled
14. **Invoice Posted** - Invoice is posted to general ledger
15. **Document Archived** - Invoice and related documents are archived

## Key Features

### Process Mining Analysis
- **Bottleneck Identification**: Automatic detection of processing delays
- **Conformance Checking**: Validation against SAP standard processes
- **Resource Utilization**: Analysis of staff workload and efficiency
- **Variant Analysis**: Comparison of different process paths

### Real-Time Monitoring
- **Command Center Dashboards**: Real-time operational monitoring
- **Alert System**: Automated alerts for threshold violations
- **Resource Allocation**: Dynamic resource allocation based on workload
- **Performance Tracking**: Real-time KPI monitoring

### Financial Analysis
- **Cost Analysis**: Processing cost per invoice
- **Cash Flow Impact**: Payment timing and cash management
- **Vendor Analysis**: Vendor-specific performance metrics
- **Budget Analysis**: Cost center and department analysis

## SAP Integration Considerations

### Vendor Master Data
- Vendor information maintained in SAP vendor master records
- Vendor categories determine approval workflows and payment terms
- Vendor blocking/unblocking affects payment processing

### Purchase Order Integration
- Three-way matching with purchase orders and goods receipts
- Price and quantity variance tolerance limits
- Automatic posting to inventory accounts for goods invoices

### Approval Workflows
- Multi-level approval based on invoice amount and vendor category
- Electronic approval routing through SAP workflow engine
- Approval delegation and substitution rules

### Payment Processing
- Integration with SAP Financial Accounting (FI) module
- Automatic payment proposal generation
- Bank integration for electronic payments
- Payment method determination based on vendor master data

## Performance Targets

### Processing Efficiency
- **Invoice Processing Time**: < 48 hours average
- **Approval Cycle Time**: < 24 hours average
- **Payment Processing**: < 72 hours from approval
- **SLA Compliance**: > 95% within thresholds

### Quality Metrics
- **Error Rate**: < 5% rejected invoices
- **Data Quality**: > 98% complete data
- **Payment Accuracy**: 100% accurate payments
- **Compliance Rate**: 100% regulatory compliance

### Cost Targets
- **Processing Cost**: < $25 per invoice
- **Cost Reduction**: 10-15% improvement target
- **Efficiency Gain**: 15-20% process efficiency improvement
- **Productivity**: 20-25% staff productivity improvement

## Documentation

### Process Documentation
- **`docs/process_specifications.md`** - Complete process specification
- **`docs/process_current_day.md`** - Real-time monitoring setup
- **`docs/process_historical.md`** - Historical analysis setup
- **`docs/process_historical_analysis.md`** - Mindzie Studio analysis specifications

### Technical Documentation
- **`src/activities.json`** - Activity definitions
- **`src/requirements.txt`** - Python dependencies
- **`src/env_example.txt`** - Environment variables template

## Setup Instructions

### 1. Install Dependencies
```bash
cd src
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy environment template
copy env_example.txt .env
# Edit .env with your Mindzie Studio credentials
```

### 3. Generate Data
```bash
# Generate historical data
python historical_event_log.py

# Generate current day data
python daily_event_log.py

# Run statistics and validation
python historical_event_log_stats.py
python daily_event_log_stats.py
```

### 4. Upload to Mindzie Studio
```bash
# Upload historical dataset
python historical_dataset_upload.py

# Upload current day dataset
python daily_dataset_upload.py
```

## Mindzie Studio Integration

### Project Structure
- **`mindzie_studio/SAP Accounts Payable.mpz`** - Complete project file
- **`mindzie_studio/current_day/investigations/stages/`** - MCL files for waiting stages
- **`mindzie_studio/current_day/enrichments/`** - Stage time and duration enrichments

### Dashboard Configuration
- **Executive Dashboard**: High-level performance metrics
- **Operational Dashboard**: Real-time operational monitoring
- **Financial Dashboard**: Financial analysis and reporting

## Success Metrics

A successful SAP AP process mining implementation should achieve:

- **Process Efficiency**: 15-20% improvement in processing efficiency
- **Cost Reduction**: 10-15% reduction in processing costs
- **Quality Improvement**: < 2% error rate
- **Compliance Enhancement**: 100% audit compliance
- **Staff Productivity**: 20-25% productivity improvement

## Notes
- All data is synthetic and for process mining research and education only
- The generator uses a fixed random seed for reproducible results
- SAP-specific activities and workflows are modeled based on standard SAP AP processes
- Integration with actual SAP systems requires additional configuration and testing
- Performance targets should be adjusted based on organizational requirements 