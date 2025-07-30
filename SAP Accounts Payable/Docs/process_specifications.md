# Process Specifications: SAP Accounts Payable Event Log

## Introduction
This document outlines the process specifications for the SAP Accounts Payable (AP) event log, including activities, case attributes, stage thresholds, and data generation rules. This specification applies to both historical analysis and real-time monitoring datasets for accounts payable processes in SAP ERP systems.

---

## Activities Tracked
The following activities are logged in the SAP AP event log (as defined in `src/activities.json`):

1. **Invoice Received** - An invoice has been received from a vendor and entered into the system
2. **Invoice Scanned** - The physical invoice has been scanned and attached to the digital record
3. **Invoice Validation** - The invoice has been validated against purchase orders and receiving documents
4. **Three-Way Match** - The invoice has been matched with purchase order and goods receipt
5. **Price Variance Check** - Price variances between invoice and purchase order have been identified and reviewed
6. **Quantity Variance Check** - Quantity variances between invoice and goods receipt have been identified and reviewed
7. **Tax Calculation** - Tax amounts have been calculated and verified
8. **Approval Requested** - The invoice has been submitted for approval workflow
9. **Manager Approval** - A manager has approved the invoice for payment
10. **Finance Approval** - The finance department has approved the invoice
11. **Vendor Master Data Review** - Vendor information has been verified and updated if necessary
12. **Payment Terms Verification** - Payment terms have been verified and confirmed
13. **GL Account Assignment** - General ledger accounts have been assigned to the invoice
14. **Cost Center Assignment** - Cost centers have been assigned for expense allocation
15. **Payment Block Release** - Any payment blocks have been released
16. **Payment Scheduled** - The invoice has been scheduled for payment
17. **Payment Executed** - The payment has been executed and sent to the vendor
18. **Payment Confirmed** - The payment has been confirmed and reconciled
19. **Invoice Posted** - The invoice has been posted to the general ledger
20. **Document Archived** - The invoice and related documents have been archived

**Note**: The "Invoice Rejected" activity is generated in the code but not included in the activities.json file. Rejected invoices represent approximately 5% of total cases and are important for process improvement analysis.

---

## Case Attributes
Each case includes the following attributes (generated in `src/daily_event_log.py`):

- **CaseId** - Unique identifier for the invoice processing case (format: AP######)
- **VendorID** - Unique identifier for the vendor (format: V####)
- **InvoiceNumber** - Vendor's invoice number
- **PurchaseOrderNumber** - Associated purchase order number (if applicable)
- **InvoiceAmount** - Total invoice amount in USD
- **Currency** - Invoice currency (USD, EUR, CAD, etc.)
- **InvoiceType** - Type of invoice (Goods, Services, Expense, etc.)
- **PaymentTerms** - Payment terms (Net 30, Net 60, etc.)
- **Priority** - Processing priority (High, Medium, Low)
- **Department** - Department responsible for the expense
- **CostCenter** - Cost center code for expense allocation
- **GLAccount** - General ledger account number
- **TaxCode** - Tax code applied to the invoice
- **ApprovalLevel** - Required approval level (1-3 levels)
- **VendorCategory** - Vendor category (Strategic, Preferred, Standard, etc.)

---

## Stage Thresholds
The following processing stages are monitored with medium and high thresholds (in hours):

| Stage | Medium Threshold | High Threshold |
|-------|------------------|----------------|
| Waiting for Invoice Scanning | 2 | 8 |
| Waiting for Validation | 4 | 12 |
| Waiting for Three-Way Match | 2 | 8 |
| Waiting for Variance Review | 8 | 24 |
| Waiting for Approval | 24 | 72 |
| Waiting for GL Assignment | 2 | 8 |
| Waiting for Payment Scheduling | 4 | 12 |
| Waiting for Payment Execution | 8 | 24 |
| Waiting for Payment Confirmation | 4 | 12 |
| Waiting for Document Archiving | 24 | 72 |

---

## Process Flow
The typical invoice processing journey follows this path (with optional activities):

1. **Invoice Received** (always)
2. **Invoice Scanned** (always)
3. **Invoice Validation** (always)
4. **Three-Way Match** (85% probability for PO-based invoices)
5. **Price Variance Check** (30% probability)
6. **Quantity Variance Check** (25% probability)
7. **Tax Calculation** (always)
8. **Approval Requested** (always)
9. **Manager Approval** (always)
10. **Finance Approval** (60% probability for high-value invoices)
11. **Vendor Master Data Review** (20% probability)
12. **Payment Terms Verification** (always)
13. **GL Account Assignment** (always)
14. **Cost Center Assignment** (always)
15. **Payment Block Release** (15% probability)
16. **Payment Scheduled** (always)
17. **Payment Executed** (always)
18. **Payment Confirmed** (always)
19. **Invoice Posted** (always)
20. **Document Archived** (always)

---

## Data Generation Rules

### FreezeTime (Snapshot Time)
- **Date**: May 4th, 2025 at 14:00:00 (2:00 PM)
- **Purpose**: Reference time for all processing time calculations
- **Format**: "2025-05-04T14:00:00+00:00"

### Case Distribution
- **Completed Cases**: 150 total
  - Successfully Processed: 142 cases (95%)
  - Rejected: 8 cases (5%)
- **In-Progress Cases**: Variable based on stage thresholds
  - Invoice Scanning: 8 cases (6 OK, 2 warning)
  - Validation: 12 cases (9 OK, 3 warning)
  - Three-Way Match: 6 cases (5 OK, 1 warning)
  - Approval: 15 cases (10 OK, 3 warning, 2 critical)
  - GL Assignment: 4 cases (4 OK)
  - Payment Scheduling: 8 cases (6 OK, 2 warning)
  - Payment Execution: 6 cases (5 OK, 1 warning)
  - Document Archiving: 10 cases (8 OK, 2 warning)

### Time Generation
- **Activity Intervals**: 1-8 hours between activities
- **Random Seed**: Fixed at 42 for reproducibility
- **Backward Generation**: In-progress cases generate timestamps backward from FreezeTime
- **Forward Generation**: Completed cases generate timestamps forward from start time

---

## Output Formats

### JSON Format
```json
{
  "FreezeTime": "2025-05-04T14:00:00+00:00",
  "cases": [
    {
      "CaseId": "AP123456",
      "VendorID": "V001",
      "InvoiceNumber": "INV-2025-001",
      "PurchaseOrderNumber": "PO-2025-001",
      "InvoiceAmount": 1500.00,
      "Currency": "USD",
      "InvoiceType": "Goods",
      "PaymentTerms": "Net 30",
      "Priority": "Medium",
      "Department": "Procurement",
      "CostCenter": "CC001",
      "GLAccount": "5000",
      "TaxCode": "VAT",
      "ApprovalLevel": 2,
      "VendorCategory": "Preferred",
      "activities": [...]
    }
  ]
}
```

### CSV Format
Each row represents one activity:
- CaseId, ActivityName, ActivityTime, VendorID, InvoiceNumber, PurchaseOrderNumber, InvoiceAmount, Currency, InvoiceType, PaymentTerms, Priority, Department, CostCenter, GLAccount, TaxCode, ApprovalLevel, VendorCategory

---

## SAP-Specific Considerations

### Vendor Master Data
- Vendor information is maintained in SAP vendor master records
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

### Tax Handling
- Automatic tax calculation based on tax codes
- Integration with tax reporting and compliance
- Multi-jurisdiction tax handling

---

## Notes
- All data is synthetic and for process mining research and education only
- The generator uses a fixed random seed for reproducible results
- Case attributes are constant for all events within a case
- Rejected invoices are important for process improvement and vendor management
- The system supports both historical analysis and real-time monitoring datasets
- Stage durations are calculated based on the difference between FreezeTime and the last completed activity for in-progress cases
- SAP-specific activities and workflows are modeled based on standard SAP AP processes 