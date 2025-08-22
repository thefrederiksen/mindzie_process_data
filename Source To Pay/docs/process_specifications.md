# Process Specifications: Source to Pay Event Log

## Introduction
This document outlines the process specifications for the Source to Pay (S2P) event log, including activities, case attributes, stage thresholds, and data generation rules. The Source to Pay process encompasses the complete procurement lifecycle from purchase requisition through payment processing. This specification applies to both historical analysis and real-time monitoring datasets.

---

## Activities Tracked
The following activities are logged in the Source to Pay event log:

### Purchase Requisition Phase
1. **Place Order** - Purchase requisition initiated by requester
2. **Receive Order** - Order received by procurement department
3. **Request Payment by Credit Card** - Alternative payment method request for credit card processing
4. **Request Payment by Bank Transfer** - Alternative payment method request for bank transfer processing

### Vendor Selection and Order Processing
5. **Process Order** - Initial order processing and validation
6. **Call Centers** - Contact vendor call centers for order clarification or issues
7. **Review Order Info** - Detailed review of order information by buyer
8. **Capture Customer Info** - Record or update customer/requester information
9. **Receive Invoice** - Invoice received from vendor (either electronically or physically)
10. **Receive Hard Copy** - Physical invoice or documents received

### Account Management
11. **Update Profile** - Update vendor or customer profile information
12. **Manage Account** - Account management activities and maintenance
13. **Review Invoice** - Detailed review of invoice for accuracy and compliance
14. **Create Payment** - Create payment record in the system

### Payment Processing
15. **Charge Credit** - Process credit card payment
16. **Notify Client** - Send notification to client/requester about order or payment status
17. **Authorize Payment** - Approval of payment by authorized personnel
18. **Update Customer Balance** - Update the customer's account balance after payment

### Invoice Management
19. **Make Billing Inquiry** - Query regarding billing or invoice details
20. **Sign In (Payroll Account)** - Access payroll system for payment processing
21. **Pay Cash** - Process cash payment (rare scenario)
22. **Identify or Verify Credit Card Info** - Validate credit card information
23. **Fill in Settlement Info** - Complete settlement details for payment

### Payment Methods and Validation
24. **Manage Payment** - Overall payment management and tracking
25. **Payment Method Selection** - Choose appropriate payment method
26. **Abstract Payment Method** - Abstract payment processing for various methods
27. **Default Payment Method** - Process using default payment configuration

### Verification and Completion
28. **Verify Successful Payment** - Confirm payment has been processed successfully
29. **Cancel Invoice** - Cancel an invoice due to errors or changes
30. **Start Event** - Process initiation marker
31. **End Event** - Process completion marker

### Validation Points
32. **Activity Validation Points** - System validation checkpoints throughout the process
33. **Sequence Flow** - Process flow tracking between activities
34. **Realization Iteration** - Iterative processing for complex orders

### Alternative Credit Card Process (Process B)
35. **Place Order (Credit Card)** - Direct credit card order placement
36. **Receive Order (Credit Card)** - Receive credit card order
37. **Request Payment by Credit Card (Direct)** - Direct credit card payment request
38. **Receive E-Invoice** - Electronic invoice receipt for credit card purchases

---

## Case Attributes
Each case includes the following attributes:

### Order Information
- **CaseId** - Unique identifier for the purchase order (format: PO######)
- **OrderType** - Type of purchase order (Standard, Express, Blanket, Contract)
- **OrderValue** - Total value of the order in USD (range: $10 - $1,000,000)
- **Currency** - Transaction currency (USD, EUR, GBP, etc.)
- **Priority** - Order priority (Low, Medium, High, Critical)
- **PaymentTerms** - Payment terms (Net30, Net60, Immediate, etc.)

### Vendor Information
- **VendorID** - Unique vendor identifier (format: V####)
- **VendorName** - Name of the vendor/supplier
- **VendorCategory** - Category of vendor (Equipment, Services, Materials, Software)
- **VendorRating** - Vendor performance rating (1-5 scale)
- **PreferredVendor** - Boolean indicating if vendor is preferred

### Requester Information
- **RequesterID** - Employee ID of requester (format: EMP####)
- **Department** - Requesting department
- **CostCenter** - Cost center for budget allocation
- **ApprovalLevel** - Required approval level based on amount

### Invoice Details
- **InvoiceNumber** - Vendor invoice number
- **InvoiceDate** - Date invoice was issued
- **InvoiceAmount** - Invoice amount (may differ from order value)
- **InvoiceStatus** - Current invoice status (Pending, Matched, Approved, Paid, Disputed)

### Payment Information
- **PaymentMethod** - Method of payment (Credit Card, Bank Transfer, Check, Cash)
- **PaymentStatus** - Current payment status
- **PaymentDate** - Date payment was processed
- **DiscountApplied** - Any early payment discount applied

---

## Stage Thresholds
The following waiting stages are monitored with medium and high thresholds (in business hours):

| Stage | Medium Threshold | High Threshold |
|-------|------------------|----------------|
| Waiting for Order Processing | 4 hours | 8 hours |
| Waiting for Vendor Selection | 8 hours | 24 hours |
| Waiting for Order Approval | 4 hours | 16 hours |
| Waiting for Invoice Receipt | 48 hours | 120 hours |
| Waiting for Invoice Matching | 8 hours | 24 hours |
| Waiting for Payment Approval | 8 hours | 24 hours |
| Waiting for Payment Processing | 4 hours | 16 hours |
| Waiting for Vendor Confirmation | 24 hours | 72 hours |
| Waiting for Credit Check | 2 hours | 8 hours |
| Waiting for Budget Verification | 4 hours | 16 hours |
| Waiting for Three-Way Match | 8 hours | 24 hours |
| Waiting for Dispute Resolution | 48 hours | 120 hours |

**Note**: All thresholds are measured in business hours (Monday-Friday, 8am-6pm)

---

## Process Flow

### Main Process Path (Standard Purchase Order)
The typical procurement journey follows this path:

1. **Initiation Phase** (always)
   - Place Order
   - Receive Order

2. **Order Processing** (always)
   - Process Order
   - Decision Point: "Orders OK?" 
     - Yes (85%): Continue to vendor selection
     - No (15%): Call Centers → Review Order Info → Capture Customer Info

3. **Vendor Selection and Ordering** (always)
   - Online shops with pre-request (60% probability)
   - Optional: Review order info for complex orders

4. **Invoice Receipt** (always)
   - Receive Invoice (electronic - 70%)
   - Receive Hard Copy (physical - 30%)
   - Invoice type determines processing path

5. **Invoice Processing** (always)
   - Review Invoice
   - Three-way matching (PO, Receipt, Invoice)
   - Decision Point: "Invoice matches?"
     - Yes (90%): Continue to payment
     - No (10%): Make Billing Inquiry → Manage Account → Update Profile

6. **Payment Authorization** (always)
   - Decision Point: "Ready to pay?"
     - Yes (95%): Continue to payment method selection
     - No (5%): Charge credit → Notify client → Return to review

7. **Payment Method Selection** (always)
   - Credit Card (25%)
     - Identify or Verify Credit Card Info
     - Abstract Payment Method
   - Bank Transfer (60%)
     - Sign In (Payroll Account)
     - Fill in Settlement Info
   - Check (14%)
     - Manage Payment
     - Default Payment Method
   - Cash (1%)
     - Pay Cash

8. **Payment Processing** (always)
   - Authorize Payment
   - Update Customer Balance
   - Verify Successful Payment

9. **Completion** (always)
   - Decision Point: "Payment successful?"
     - Yes (98%): End Event
     - No (2%): Cancel Invoice → Return to payment selection

### Alternative Process Path (Credit Card Direct Purchase)
For small, direct purchases (Process B):

1. **Place Order** (Credit Card)
2. **Receive Order**
3. **Request Payment by Credit Card**
4. **Receive E-Invoice**
5. **Process Payment** (simplified flow)
6. **End Event**

This path is used for:
- Purchases under $1,000 (30% of cases)
- Pre-approved vendors
- Emergency purchases

---

## Data Generation Rules

### FreezeTime (Snapshot Time)
- **Date**: Current date at 14:00:00 (2:00 PM)
- **Purpose**: Reference time for all waiting time calculations
- **Format**: ISO 8601 (e.g., "2025-05-04T14:00:00+00:00")

### Case Distribution
- **Completed Cases**: 500 total per week
  - Standard Purchase Orders: 350 cases (70%)
  - Credit Card Direct: 150 cases (30%)
  
- **In-Progress Cases**: Variable based on stage
  - Order Processing: 15-20 cases
  - Vendor Selection: 10-15 cases
  - Invoice Processing: 20-30 cases
  - Payment Processing: 15-25 cases
  - Dispute Resolution: 5-10 cases

### Order Value Distribution
- Under $1,000: 30%
- $1,000 - $10,000: 40%
- $10,000 - $100,000: 25%
- Over $100,000: 5%

### Payment Method Distribution
- Bank Transfer: 60%
- Credit Card: 25%
- Check: 14%
- Cash: 1%

### Process Variations
- **Three-way match success rate**: 90%
- **Invoice disputes**: 10% of cases
- **Rush orders**: 15% of cases
- **Vendor performance issues**: 5% of cases
- **Payment failures**: 2% of cases

### Time Generation
- **Business Hours**: Monday-Friday, 8:00 AM - 6:00 PM
- **Activity Intervals**: 
  - Automated activities: 1-5 minutes
  - Manual activities: 30 minutes - 4 hours
  - Approval activities: 2-8 hours
  - External activities (vendor): 1-5 business days
- **Random Seed**: Fixed at 42 for reproducibility
- **Weekend Processing**: Limited to automated activities only

### Resource Performance Factors
Different resources have varying performance levels:
- **Experienced Buyers**: 0.8x processing time
- **New Buyers**: 1.5x processing time
- **Automated Systems**: 0.1x processing time
- **Peak Hours (10am-2pm)**: 1.2x processing time
- **End of Month**: 1.3x processing time

---

## Roles and Resources

### Internal Roles
- **Requester** - Initiates purchase orders
- **Buyer** - Manages vendor selection and ordering
- **Accounts Payable Clerk** - Processes invoices and payments
- **Approver** - Authorizes orders and payments based on limits
- **Finance Manager** - Oversees payment processing
- **Procurement Specialist** - Handles complex orders and vendor management

### External Roles
- **Vendor** - Supplies goods/services and issues invoices
- **Bank** - Processes electronic payments
- **Credit Card Processor** - Handles credit card transactions

### System Resources
- **ERP System** - Core procurement and finance system
- **Payment Gateway** - Electronic payment processing
- **Invoice Management System** - Invoice receipt and matching
- **Vendor Portal** - Vendor interaction and document exchange

---

## Output Formats

### JSON Format
```json
{
  "FreezeTime": "2025-05-04T14:00:00+00:00",
  "cases": [
    {
      "CaseId": "PO123456",
      "OrderType": "Standard",
      "OrderValue": 25000.00,
      "Currency": "USD",
      "Priority": "Medium",
      "PaymentTerms": "Net30",
      "VendorID": "V1234",
      "VendorName": "Acme Supplies Inc",
      "VendorCategory": "Equipment",
      "VendorRating": 4.5,
      "PreferredVendor": true,
      "RequesterID": "EMP5678",
      "Department": "Operations",
      "CostCenter": "CC100",
      "ApprovalLevel": 2,
      "InvoiceNumber": "INV-2025-001234",
      "InvoiceDate": "2025-04-15",
      "InvoiceAmount": 24750.00,
      "InvoiceStatus": "Matched",
      "PaymentMethod": "Bank Transfer",
      "PaymentStatus": "Completed",
      "PaymentDate": "2025-05-01",
      "DiscountApplied": 250.00,
      "activities": [
        {
          "ActivityName": "Place Order",
          "ActivityTime": "2025-04-10T09:30:00+00:00",
          "Resource": "John Smith",
          "Role": "Requester"
        }
      ]
    }
  ]
}
```

### CSV Format
Each row represents one activity:
- CaseId, ActivityName, ActivityTime, Resource, Role, OrderType, OrderValue, Currency, Priority, PaymentTerms, VendorID, VendorName, VendorCategory, VendorRating, PreferredVendor, RequesterID, Department, CostCenter, ApprovalLevel, InvoiceNumber, InvoiceDate, InvoiceAmount, InvoiceStatus, PaymentMethod, PaymentStatus, PaymentDate, DiscountApplied

---

## Compliance and Audit Requirements

### Segregation of Duties
- Requester cannot approve own orders
- Buyer cannot approve payments
- Invoice processor cannot authorize payments

### Audit Trail Requirements
- All activities must be logged with timestamp and user
- Changes to orders must be tracked
- Payment authorizations must be documented
- Vendor changes require approval

### Compliance Checks
- Budget verification for all orders
- Vendor validation before first order
- Tax compliance verification
- Contract compliance for blanket orders

---

## Performance Metrics and KPIs

### Efficiency Metrics
- **Average Cycle Time**: Target < 10 business days
- **First-Time Match Rate**: Target > 85%
- **Electronic Invoice Rate**: Target > 75%
- **On-Time Payment Rate**: Target > 95%

### Quality Metrics
- **Invoice Accuracy**: Target > 95%
- **Vendor Satisfaction**: Target > 4.0/5.0
- **Dispute Rate**: Target < 5%
- **Payment Error Rate**: Target < 1%

### Cost Metrics
- **Processing Cost per Invoice**: Monitor trend
- **Early Payment Discount Capture**: Target > 80%
- **Maverick Spend**: Target < 10%

---

## Notes
- All data is synthetic and for process mining research and education only
- The generator uses a fixed random seed for reproducible results
- Case attributes are constant for all events within a case
- Business hours and holidays affect processing times
- The system supports both historical analysis and real-time monitoring datasets
- Stage durations are calculated based on the difference between FreezeTime and the last completed activity for in-progress cases
- Payment processing times vary significantly based on payment method and vendor setup
- International transactions may have additional compliance activities not shown in the base process