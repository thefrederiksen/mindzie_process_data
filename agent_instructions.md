# Agent Instructions: Creating Sample Process Mining Datasets

## Overview
This document provides instructions for creating new sample process mining datasets based on the lessons learned from the Emergency Department project. These instructions ensure consistency and completeness across all sample datasets while allowing for domain-specific customization.

---

## Required Directory Structure

Every sample dataset should follow this directory structure:

```
[domain_name]/
├── docs/
│   ├── process_specifications.md
│   ├── process_current_day.md
│   ├── process_historical.md
│   └── process_historical_analysis.md
├── src/
│   ├── activities.json
│   ├── daily_event_log.py
│   ├── daily_event_log_stats.py
│   ├── daily_dataset_upload.py
│   ├── historical_event_log.py
│   ├── historical_event_log_stats.py
│   ├── historical_dataset_upload.py
│   ├── mindzie_swagger.json
│   └── output/
│       ├── [domain]_daily.json
│       ├── [domain]_daily.csv
│       ├── [domain]_year_to_date.json
│       └── [domain]_year_to_date.csv
├── mindzie_studio/
│   ├── [domain_name].mpz
│   └── current_day/
│       ├── enrichments/
│       │   ├── 1. stage_times/
│       │   └── 2. durations/
│       └── investigations/
│           └── stages/
│               ├── waiting_for_[stage1].mcl
│               ├── waiting_for_[stage2].mcl
│               └── ...
├── images/
├── README.md
└── LICENSE (optional)
```

---

## Core Components (Always Required)

### 1. Documentation (docs/)
**Always include these four documents:**

- **`process_specifications.md`** - Complete process specification including:
  - Activities tracked (20-25 activities recommended)
  - Case attributes with realistic domain values
  - Stage thresholds (medium/high) in appropriate time units
  - Process flow with probability distributions
  - Data generation rules
  - Output formats (JSON and CSV)
  - Domain-specific considerations

- **`process_current_day.md`** - Real-time monitoring setup and current day analysis
- **`process_historical.md`** - Historical analysis setup and data generation approach
- **`process_historical_analysis.md`** - Mindzie Studio analysis specifications including:
  - Dashboard requirements and layouts
  - Key performance indicators (KPIs) to track
  - Process mining analysis objectives
  - Bottleneck identification strategies
  - Conformance checking requirements
  - Resource utilization analysis
  - Timeline and milestone tracking

### 2. Source Code (src/)
**Always include these core files:**

- **`activities.json`** - Activity definitions with descriptions
- **`daily_event_log.py`** - Real-time dataset generator
- **`daily_event_log_stats.py`** - **CRITICAL**: Statistics and evaluation report for current day data
- **`daily_dataset_upload.py`** - Upload script for current data
- **`historical_event_log.py`** - Historical dataset generator
- **`historical_event_log_stats.py`** - **CRITICAL**: Statistics and evaluation report for historical data
- **`historical_dataset_upload.py`** - Upload script for historical data
- **`mindzie_swagger.json`** - API specification for Mindzie integration
- **`requirements.txt`** - **CRITICAL**: Python dependencies list
- **`.env.example`** - Environment variables template

### 3. Mindzie Studio Integration (mindzie_studio/)
**Always include:**

- **Project file** (`.mpz`) with complete dataset and dashboards
- **current_day/investigations/stages/** - MCL files for each waiting stage
- **current_day/enrichments/** - Stage time and duration enrichments

### 4. Output Data (src/output/)
**Always generate:**

- Daily dataset (JSON and CSV)
- Historical dataset (JSON and CSV)
- Consistent naming: `[domain]_daily.*` and `[domain]_year_to_date.*`

### 5. Statistics and Evaluation (CRITICAL)
**Always implement comprehensive statistics scripts:**

- **`daily_event_log_stats.py`** - Must include:
  - Case count validation (completed vs in-progress)
  - Activity frequency analysis
  - Stage duration statistics
  - Threshold compliance checking
  - Data quality metrics
  - Process flow validation
  - Summary report generation

- **`historical_event_log_stats.py`** - Must include:
  - Complete case analysis
  - Process performance metrics
  - Bottleneck identification
  - Resource utilization statistics
  - Timeline analysis
  - Conformance checking results
  - Comprehensive evaluation report

### 6. Dependency Management (CRITICAL)
**Always include dependency management files:**

- **`requirements.txt`** - Must include:
  - All Python package dependencies with versions
  - Core packages: `pandas`, `numpy`, `requests`, `python-dotenv`
  - Domain-specific packages as needed
  - Version pinning for reproducibility

- **`.env.example`** - Must include:
  - Template for environment variables
  - API keys and configuration placeholders
  - Clear documentation of required variables
  - Example values where appropriate

---

## Optional Components

### Presentation Directory
- **Exclude by default** - Not needed for every dataset
- Only include if creating specific presentation materials
- Can be added later if needed

### images Directory
- **Include if needed** - For screenshots, diagrams, or visual assets
- Can be empty initially

---

## Key Design Principles

### 1. Realistic Process Flow
- Model actual business processes, not idealized ones
- Include common variations and exceptions
- Use realistic probability distributions for optional activities
- Include rejection/error paths (5-10% of cases)

### 2. Appropriate Time Scales
- **Healthcare**: Minutes to hours (patient care)
- **Finance**: Hours to days (payment processing)
- **Manufacturing**: Hours to weeks (production cycles)
- **Logistics**: Hours to days (shipping/delivery)

### 3. Meaningful Case Attributes
- Include 10-15 relevant attributes per case
- Use realistic data distributions
- Ensure attributes are constant within a case
- Include both categorical and numerical attributes

### 4. Stage Thresholds
- Set realistic medium/high thresholds
- Base on industry standards or best practices
- Use appropriate time units (minutes, hours, days)
- Include 8-12 key waiting stages

### 5. Data Volume
- **Historical**: 1000-5000 completed cases
- **Current Day**: 50-200 in-progress cases
- **Rejection Rate**: 5-10% of total cases

---

## Code Templates

### Starter Template for daily_event_log.py
```python
import random
random.seed(42)
import json
from datetime import datetime, timedelta
import os
import csv

# Standard utility functions
def load_activities(src_dir):
    with open(os.path.join(src_dir, 'activities.json'), 'r') as f:
        return json.load(f)

def random_case_id(used_case_ids, prefix="CASE"):
    while True:
        cid = f"{prefix}{random.randint(100000, 999999)}"
        if cid not in used_case_ids:
            used_case_ids.add(cid)
            return cid

def generate_timestamp(base_time, min_minutes=5, max_minutes=30):
    """Generate realistic timestamp with business hours consideration"""
    minutes = random.randint(min_minutes, max_minutes)
    return base_time + timedelta(minutes=minutes)

# Domain-specific generation logic goes here
```

### Required Statistics Template
```python
def generate_statistics_report(event_log_path):
    """Generate comprehensive statistics report"""
    stats = {
        "total_cases": 0,
        "completed_cases": 0,
        "in_progress_cases": 0,
        "activity_frequencies": {},
        "stage_durations": {},
        "threshold_violations": {},
        "data_quality_metrics": {}
    }
    # Implementation here
    return stats
```

### Common Utility Functions
- Case ID generation with domain-specific prefixes
- Timestamp generation with business hours logic
- Attribute value generation with realistic distributions
- Process path selection based on probabilities
- Data validation and integrity checks

---

## Enhanced Process Flow Guidelines

### Visual Flow Requirements
- Create process flow diagrams showing all possible paths
- Include decision points with clear branching logic
- Mark optional activities with probability percentages
- Show loop-back paths for rework scenarios
- Indicate rejection/error endpoints

### Decision Tree Templates
```
Start -> Activity A -> Decision Point 1
                       ├─ (70%) -> Activity B -> ...
                       ├─ (20%) -> Activity C -> ...
                       └─ (10%) -> Error/Rejection
```

### Path Specifications
- **Minimum path length**: 5-7 activities for simple processes
- **Maximum path length**: 15-20 activities for complex processes
- **Loop patterns**: Maximum 2-3 iterations for rework
- **Branching factor**: 2-4 options at decision points

### Complex Process Patterns
1. **Parallel activities**: Multiple activities happening simultaneously
2. **Conditional branching**: Based on case attributes
3. **Time-based routing**: Different paths based on time of day/week
4. **Resource-based routing**: Path selection based on availability
5. **Exception handling**: Clear error and recovery paths

---

## Data Validation Requirements

### Domain-Specific Validation Rules

#### Healthcare
- Patient age must be 0-120 years
- Triage levels must be 1-5
- Vital signs within realistic ranges
- Treatment codes must match diagnosis
- Timestamps must respect clinical workflows

#### Finance
- Amount fields must be positive
- Currency codes must be valid ISO codes
- Approval limits must be respected
- Document numbers must be unique
- Processing times within business hours

#### Manufacturing
- Quantity must be positive integers
- Quality scores 0-100
- Equipment IDs must exist
- Batch numbers must be unique
- Lead times must be realistic

### Cross-Field Validation
- Start time < End time for all activities
- Case attributes consistent throughout case
- Resource assignments don't overlap
- Monetary values match across activities
- Status transitions follow valid sequences

### Data Integrity Checks
```python
def validate_event_log(events):
    validations = {
        "timestamp_order": check_timestamp_order(events),
        "attribute_consistency": check_attribute_consistency(events),
        "required_fields": check_required_fields(events),
        "value_ranges": check_value_ranges(events),
        "business_rules": check_business_rules(events)
    }
    return validations
```

---

## Performance Benchmarks

### Target Generation Times
- **Small dataset (1000 cases)**: < 10 seconds
- **Medium dataset (5000 cases)**: < 60 seconds
- **Large dataset (10000 cases)**: < 5 minutes

### Memory Usage Guidelines
- Maximum memory usage: 2GB for generation
- Streaming output for large datasets
- Batch processing for uploads

### API Upload Performance
- Chunk size: 1000 records per upload
- Retry logic: 3 attempts with exponential backoff
- Timeout: 30 seconds per request
- Concurrent uploads: Maximum 3

### Dashboard Refresh Rates
- Real-time dashboards: 30-60 second refresh
- Historical analysis: 5-15 minute refresh
- Stage calculations: < 5 seconds

---

## Testing Strategy

### Unit Testing Requirements
```python
# test_generators.py
def test_case_id_generation():
    """Test unique case ID generation"""
    
def test_timestamp_generation():
    """Test realistic timestamp generation"""
    
def test_activity_flow():
    """Test valid activity sequences"""
```

### Integration Testing
1. Generate sample data
2. Validate against schema
3. Upload to test environment
4. Verify dashboard display
5. Check stage calculations

### Performance Testing
- Load testing with maximum dataset size
- Memory profiling during generation
- API stress testing
- Dashboard response time testing

### Data Quality Acceptance Criteria
- 100% valid timestamps
- No duplicate case IDs
- All required fields populated
- Business rules compliance > 95%
- Statistical distributions within 5% of target

---

## Environment Configuration

### .env.example Template
```bash
# Mindzie Studio Configuration
TENANT_ID=your-tenant-id-here
PROJECT_ID=your-project-id-here
API_KEY=your-api-key-here

# Optional Configuration
API_BASE_URL=https://www.mindziestudio.com
LOG_LEVEL=INFO
OUTPUT_FORMAT=both  # json, csv, or both
MAX_RETRIES=3
CHUNK_SIZE=1000

# Domain-Specific Settings
BUSINESS_HOURS_ONLY=true
TIMEZONE=UTC
```

### Python Version Requirements
- Minimum: Python 3.7
- Recommended: Python 3.9+
- Virtual environment recommended

### Dependency Management
```txt
# requirements.txt template
pandas>=1.3.0,<2.0.0
numpy>=1.21.0,<2.0.0
requests>=2.26.0,<3.0.0
python-dotenv>=0.19.0,<1.0.0
# Domain-specific additions below
```

---

## Monitoring and Alerting

### Metrics to Track
1. **Generation metrics**:
   - Cases generated per minute
   - Error rate during generation
   - Memory usage peak
   
2. **Upload metrics**:
   - Upload success rate
   - Average upload time
   - Failed upload reasons

3. **Data quality metrics**:
   - Invalid record percentage
   - Missing field rate
   - Business rule violations

### Logging Requirements
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('process_mining_generator.log'),
        logging.StreamHandler()
    ]
)
```

### Error Reporting Standards
- Log all errors with full context
- Include timestamp, case ID, activity
- Categorize errors (data, network, logic)
- Summary report at end of generation

---

## Domain-Specific Templates

### Healthcare Starter Pack
```json
{
  "activities": [
    "Registration", "Triage", "Examination", "Diagnosis", 
    "Treatment", "Discharge"
  ],
  "case_attributes": [
    "patient_id", "age", "gender", "triage_level", 
    "arrival_mode", "chief_complaint"
  ],
  "stages": [
    "Waiting for Triage", "Waiting for Doctor", 
    "Waiting for Test Results", "Waiting for Discharge"
  ],
  "kpis": [
    "Door to Doctor Time", "Length of Stay", 
    "Left Without Being Seen Rate"
  ]
}
```

### Finance Starter Pack
```json
{
  "activities": [
    "Invoice Receipt", "Validation", "Approval", 
    "Payment Processing", "Reconciliation"
  ],
  "case_attributes": [
    "invoice_number", "vendor_id", "amount", 
    "currency", "department", "approver"
  ],
  "stages": [
    "Waiting for Validation", "Waiting for Approval", 
    "Waiting for Payment", "Waiting for Reconciliation"
  ],
  "kpis": [
    "Invoice Processing Time", "First Time Right Rate", 
    "Payment Accuracy", "Vendor Satisfaction"
  ]
}
```

---

## Mindzie Studio Best Practices

### Dashboard Design Patterns
1. **Overview dashboard**: High-level KPIs and trends
2. **Operational dashboard**: Real-time monitoring
3. **Analytical dashboard**: Deep-dive analysis
4. **Executive dashboard**: Summary metrics

### MCL File Optimization
- Use efficient queries
- Minimize calculation complexity
- Cache frequently used results
- Index key fields

### Performance Tuning
- Limit dashboard refresh frequency
- Use sampling for large datasets
- Optimize stage calculations
- Implement progressive loading

### User Role Configurations
- **Operators**: Real-time monitoring access
- **Analysts**: Full analytical capabilities
- **Managers**: KPI and summary views
- **Executives**: High-level dashboards only

---

## Versioning and Migration

### Dataset Versioning Strategy
```
v1.0.0 - Initial release
v1.1.0 - Added new attributes
v1.2.0 - Modified activity flow
v2.0.0 - Breaking changes to schema
```

### Schema Evolution Guidelines
1. Always maintain backwards compatibility in minor versions
2. Document all schema changes in CHANGELOG.md
3. Provide migration scripts for major versions
4. Test migrations on sample data

### Migration Script Template
```python
def migrate_v1_to_v2(old_data):
    """Migrate data from v1 schema to v2 schema"""
    new_data = []
    for record in old_data:
        # Transformation logic
        new_record = transform_record(record)
        new_data.append(new_record)
    return new_data
```

---

## Domain-Specific Considerations

### Healthcare (Emergency Department, Surgery, etc.)
- Patient-centric processes
- Time-critical activities
- Multiple service providers
- Regulatory compliance requirements
- Integration with medical systems

### Finance (Accounts Payable, Accounts Receivable, etc.)
- Document-driven processes
- Approval workflows
- Compliance and audit trails
- Integration with ERP systems
- Multi-currency considerations

### Manufacturing (Production, Quality Control, etc.)
- Material flow processes
- Quality checkpoints
- Equipment and resource constraints
- Supply chain integration
- Regulatory compliance

### Logistics (Shipping, Delivery, etc.)
- Location-based processes
- External dependencies
- Real-time tracking requirements
- Multi-modal transportation
- Customs and regulatory requirements

---

## Implementation Checklist

### Phase 1: Planning
- [ ] Define domain and process scope
- [ ] Research industry standards and best practices
- [ ] Identify key activities and decision points
- [ ] Design case attributes and data distributions
- [ ] Set stage thresholds and time scales

### Phase 2: Documentation
- [ ] Create process_specifications.md
- [ ] Create process_current_day.md
- [ ] Create process_historical.md
- [ ] Create process_historical_analysis.md
- [ ] Create README.md

### Phase 3: Data Generation
- [ ] Create activities.json
- [ ] **CRITICAL**: Create requirements.txt with all dependencies
- [ ] **CRITICAL**: Create .env.example template
- [ ] Implement daily_event_log.py
- [ ] Implement historical_event_log.py
- [ ] **CRITICAL**: Create comprehensive statistics scripts
- [ ] Generate sample datasets
- [ ] **CRITICAL**: Run statistics scripts and validate data quality

### Phase 4: Mindzie Integration
- [ ] Create MCL files for waiting stages
- [ ] Set up enrichments
- [ ] Create project file (.mpz)
- [ ] Test dashboard functionality

### Phase 5: Validation
- [ ] Verify data quality and consistency
- [ ] Test process flow logic
- [ ] Validate stage calculations
- [ ] **CRITICAL**: Run statistics scripts and verify expected vs actual results
- [ ] **CRITICAL**: Validate case counts, activity frequencies, and stage durations
- [ ] **CRITICAL**: Check threshold compliance and data distributions
- [ ] Review documentation completeness

---

## Quality Standards

### Data Quality
- Consistent timestamp formats (ISO 8601)
- Realistic activity durations
- Proper case attribute distributions
- No data gaps or inconsistencies
- **Statistics validation**: Generated data must match expected distributions and counts

### Documentation Quality
- Clear and comprehensive process descriptions
- Realistic business scenarios
- Complete technical specifications
- Proper formatting and structure

### Code Quality
- Well-documented Python scripts
- Consistent naming conventions
- Error handling and validation
- Reproducible results (fixed random seeds)

---

## Common Pitfalls to Avoid

1. **Over-simplified processes** - Include realistic complexity and variations
2. **Unrealistic time scales** - Research industry standards
3. **Missing error paths** - Include rejection and exception handling
4. **Inconsistent data** - Ensure all attributes are properly distributed
5. **Poor documentation** - Write comprehensive, clear documentation
6. **Missing Mindzie integration** - Always include MCL files and project setup

---

## Success Metrics

A successful sample dataset should:
- Generate realistic, consistent data
- Provide meaningful process insights
- Include complete documentation
- Work seamlessly with Mindzie Studio
- Demonstrate real-world process complexity
- Support both historical and real-time analysis

---

## Notes
- Always use a fixed random seed (42) for reproducibility
- Include comprehensive error handling and validation
- **CRITICAL**: Statistics scripts are essential for data validation - never skip them
- **CRITICAL**: Always include requirements.txt and .env.example for dependency management
- Test all components thoroughly before finalizing
- Keep documentation up-to-date with code changes
- Consider future extensibility and maintenance 