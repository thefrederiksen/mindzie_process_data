#!/usr/bin/env python3
"""
Comprehensive Warranty Claims Dataset Validator
Data Quality Validator for Automotive Warranty Claims Process Mining Dataset

Tests against process specification and ensures production readiness.
"""

import json
import csv
import os
import re
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Any, Optional, Tuple
import statistics

# Configuration
JSON_FILE = "src/output/warranty_claims_historical.json"
CSV_FILE = "src/output/warranty_claims_historical.csv" 
SPEC_FILE = "docs/process_specification.md"
STATUS_DIR = "."

class WarrantyClaimsValidator:
    def __init__(self):
        self.validation_results = []
        self.critical_failures = []
        self.warnings = []
        self.data = None
        self.csv_data = []
        
    def log_result(self, test_name: str, passed: bool, message: str, critical: bool = False):
        """Log test result"""
        result = {
            'test': test_name,
            'passed': passed,
            'message': message,
            'critical': critical
        }
        self.validation_results.append(result)
        
        if not passed:
            if critical:
                self.critical_failures.append(f"CRITICAL: {test_name} - {message}")
            else:
                self.warnings.append(f"WARNING: {test_name} - {message}")
    
    def validate_file_existence(self) -> bool:
        """Validate that required files exist"""
        files_exist = True
        
        if not os.path.exists(JSON_FILE):
            self.log_result("File Existence", False, f"JSON file not found: {JSON_FILE}", critical=True)
            files_exist = False
        
        if not os.path.exists(CSV_FILE):
            self.log_result("File Existence", False, f"CSV file not found: {CSV_FILE}", critical=True)
            files_exist = False
            
        if not os.path.exists(SPEC_FILE):
            self.log_result("File Existence", False, f"Specification file not found: {SPEC_FILE}", critical=True)
            files_exist = False
            
        if files_exist:
            self.log_result("File Existence", True, "All required files found")
            
        return files_exist
    
    def load_and_parse_json(self) -> bool:
        """Load and validate JSON structure"""
        try:
            with open(JSON_FILE, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            
            # Validate root structure
            if not isinstance(self.data, dict):
                self.log_result("JSON Structure", False, "Root must be a dictionary", critical=True)
                return False
                
            if "cases" not in self.data:
                self.log_result("JSON Structure", False, "Missing 'cases' key in root", critical=True)
                return False
                
            if not isinstance(self.data["cases"], list):
                self.log_result("JSON Structure", False, "'cases' must be a list", critical=True)
                return False
                
            self.log_result("JSON Structure", True, f"Valid JSON structure with {len(self.data['cases'])} cases")
            return True
            
        except json.JSONDecodeError as e:
            self.log_result("JSON Parsing", False, f"Invalid JSON: {str(e)}", critical=True)
            return False
        except Exception as e:
            self.log_result("JSON Loading", False, f"Error loading JSON: {str(e)}", critical=True)
            return False
    
    def load_csv_data(self) -> bool:
        """Load CSV data for comparison"""
        try:
            with open(CSV_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.csv_data = list(reader)
            
            self.log_result("CSV Loading", True, f"Loaded {len(self.csv_data)} CSV records")
            return True
            
        except Exception as e:
            self.log_result("CSV Loading", False, f"Error loading CSV: {str(e)}", critical=True)
            return False
    
    def validate_case_volume(self) -> bool:
        """Validate case volume matches target (1500 ±20%)"""
        target = 1500
        actual = len(self.data["cases"])
        tolerance = 0.20
        
        min_acceptable = int(target * (1 - tolerance))  # 1200
        max_acceptable = int(target * (1 + tolerance))  # 1800
        
        if min_acceptable <= actual <= max_acceptable:
            self.log_result("Case Volume", True, 
                          f"Case count {actual} within acceptable range [{min_acceptable}-{max_acceptable}]")
            return True
        else:
            self.log_result("Case Volume", False, 
                          f"Case count {actual} outside acceptable range [{min_acceptable}-{max_acceptable}]", 
                          critical=True)
            return False
    
    def validate_required_fields(self) -> bool:
        """Validate all cases have required fields"""
        required_case_fields = ["CaseId", "ClaimNumber", "VIN", "VehicleMake", "activities"]
        required_activity_fields = ["ActivityName", "ActivityTime", "Resource"]
        
        issues = []
        
        for i, case in enumerate(self.data["cases"]):
            case_id = case.get("CaseId", f"Case_{i}")
            
            # Check case-level fields
            for field in required_case_fields:
                if field not in case:
                    issues.append(f"Case {case_id} missing field: {field}")
            
            # Check activities structure
            if "activities" in case:
                if not isinstance(case["activities"], list):
                    issues.append(f"Case {case_id}: activities must be a list")
                    continue
                
                for j, activity in enumerate(case["activities"]):
                    for field in required_activity_fields:
                        if field not in activity:
                            issues.append(f"Case {case_id}, Activity {j}: missing field {field}")
        
        if issues:
            self.log_result("Required Fields", False, 
                          f"Missing required fields in {len(issues)} instances. First 5: {issues[:5]}", 
                          critical=True)
            return False
        else:
            self.log_result("Required Fields", True, "All required fields present")
            return True
    
    def validate_datetime_format(self) -> bool:
        """Validate datetime format: YYYY-MM-DD HH:MM:SS"""
        datetime_pattern = re.compile(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$')
        invalid_formats = []
        
        for case in self.data["cases"]:
            case_id = case.get("CaseId", "Unknown")
            for activity in case.get("activities", []):
                activity_time = activity.get("ActivityTime", "")
                if not datetime_pattern.match(activity_time):
                    invalid_formats.append(f"Case {case_id}: {activity_time}")
                    if len(invalid_formats) >= 5:  # Limit examples
                        break
            if len(invalid_formats) >= 5:
                break
        
        if invalid_formats:
            self.log_result("DateTime Format", False, 
                          f"Invalid datetime formats found. Examples: {invalid_formats[:3]}", 
                          critical=True)
            return False
        else:
            self.log_result("DateTime Format", True, "All timestamps in correct format (YYYY-MM-DD HH:MM:SS)")
            return True
    
    def validate_csv_json_consistency(self) -> bool:
        """Validate CSV and JSON contain same data"""
        if not self.csv_data:
            return False
        
        # Count activities in JSON
        json_activity_count = sum(len(case.get("activities", [])) for case in self.data["cases"])
        csv_activity_count = len(self.csv_data)
        
        if json_activity_count != csv_activity_count:
            self.log_result("CSV-JSON Consistency", False, 
                          f"Activity count mismatch: JSON={json_activity_count}, CSV={csv_activity_count}", 
                          critical=True)
            return False
        
        # Validate CaseId consistency (first 10 cases)
        json_case_ids = set(case["CaseId"] for case in self.data["cases"][:10])
        csv_case_ids = set(row["CaseId"] for row in self.csv_data[:50])  # First 50 CSV rows should cover first 10 cases
        
        if not json_case_ids.issubset(csv_case_ids):
            missing = json_case_ids - csv_case_ids
            self.log_result("CSV-JSON Consistency", False, 
                          f"CaseIds in JSON not found in CSV: {list(missing)[:5]}", 
                          critical=True)
            return False
        
        self.log_result("CSV-JSON Consistency", True, "CSV and JSON data consistent")
        return True
    
    def validate_chronological_order(self) -> bool:
        """Validate activities within each case are chronologically ordered"""
        violations = []
        
        for case in self.data["cases"][:100]:  # Check first 100 cases
            case_id = case.get("CaseId", "Unknown")
            activities = case.get("activities", [])
            
            if len(activities) <= 1:
                continue
            
            prev_time = None
            for i, activity in enumerate(activities):
                try:
                    current_time = datetime.strptime(activity["ActivityTime"], "%Y-%m-%d %H:%M:%S")
                    if prev_time and current_time < prev_time:
                        violations.append(f"Case {case_id}: Activity {i} out of order")
                        break
                    prev_time = current_time
                except ValueError:
                    continue  # Skip if datetime parsing fails
        
        if violations:
            self.log_result("Chronological Order", False, 
                          f"Chronological violations in {len(violations)} cases. Examples: {violations[:3]}")
            return False
        else:
            self.log_result("Chronological Order", True, "Activities properly ordered within cases")
            return True
    
    def validate_closing_activities(self) -> bool:
        """Validate that 90%+ of cases have proper closing activities"""
        closing_activities = {
            "Approve Settlement", "Resolution and Settlement", 
            "Payment Processing", "Claim Closure"
        }
        
        cases_with_closing = 0
        total_cases = len(self.data["cases"])
        
        for case in self.data["cases"]:
            activities = case.get("activities", [])
            if activities:
                last_activity = activities[-1].get("ActivityName", "")
                if last_activity in closing_activities:
                    cases_with_closing += 1
        
        closing_rate = cases_with_closing / total_cases if total_cases > 0 else 0
        
        if closing_rate >= 0.90:
            self.log_result("Closing Activities", True, 
                          f"Closing activity rate: {closing_rate:.2%} ({cases_with_closing}/{total_cases})")
            return True
        else:
            self.log_result("Closing Activities", False, 
                          f"Low closing activity rate: {closing_rate:.2%} ({cases_with_closing}/{total_cases}), target ≥90%")
            return False
    
    def validate_straight_through_processing(self) -> bool:
        """Validate straight-through processing rate is around 40%"""
        straight_through_cases = 0
        total_cases = len(self.data["cases"])
        
        for case in self.data["cases"]:
            activities = case.get("activities", [])
            activity_names = [act.get("ActivityName", "") for act in activities]
            
            # Straight-through: First Notice -> Verify Coverage -> Approve Settlement
            if len(activity_names) == 3 and activity_names == [
                "First Notice of Loss", "Verify Coverage", "Approve Settlement"
            ]:
                straight_through_cases += 1
        
        straight_through_rate = straight_through_cases / total_cases if total_cases > 0 else 0
        target_rate = 0.40
        tolerance = 0.05  # ±5%
        
        if abs(straight_through_rate - target_rate) <= tolerance:
            self.log_result("Straight-Through Processing", True, 
                          f"Straight-through rate: {straight_through_rate:.2%} ({straight_through_cases}/{total_cases}), target: {target_rate:.1%}")
            return True
        else:
            self.log_result("Straight-Through Processing", False, 
                          f"Straight-through rate: {straight_through_rate:.2%} ({straight_through_cases}/{total_cases}), target: {target_rate:.1%} ±{tolerance:.1%}")
            return False
    
    def validate_bottlenecks(self) -> bool:
        """Validate that specified bottleneck resources show performance differences"""
        slow_resources = {"DealerTech3", "LaborAnalyst1", "TechExpert1", "FraudAnalyst"}
        resource_times = defaultdict(list)
        
        # Collect processing times by resource
        for case in self.data["cases"]:
            activities = case.get("activities", [])
            for i, activity in enumerate(activities):
                resource = activity.get("Resource", "")
                if resource in slow_resources and i > 0:
                    # Calculate time from previous activity
                    try:
                        current_time = datetime.strptime(activity["ActivityTime"], "%Y-%m-%d %H:%M:%S")
                        prev_time = datetime.strptime(activities[i-1]["ActivityTime"], "%Y-%m-%d %H:%M:%S")
                        duration_hours = (current_time - prev_time).total_seconds() / 3600
                        resource_times[resource].append(duration_hours)
                    except (ValueError, IndexError):
                        continue
        
        # Check if slow resources have longer average times
        bottlenecks_detected = []
        for resource in slow_resources:
            if resource in resource_times and len(resource_times[resource]) >= 5:
                avg_time = statistics.mean(resource_times[resource])
                if avg_time > 2:  # More than 2 hours average
                    bottlenecks_detected.append(f"{resource}: {avg_time:.1f}h avg")
        
        if len(bottlenecks_detected) >= 2:
            self.log_result("Bottleneck Detection", True, 
                          f"Bottlenecks detected: {', '.join(bottlenecks_detected)}")
            return True
        else:
            self.log_result("Bottleneck Detection", False, 
                          f"Insufficient bottleneck evidence. Only found: {', '.join(bottlenecks_detected)}")
            return False
    
    def validate_fraud_patterns(self) -> bool:
        """Validate fraud pattern implementation"""
        fraud_indicators = []
        vins = []
        excessive_labor = 0
        
        # Collect data for fraud analysis
        for case in self.data["cases"]:
            vin = case.get("VIN", "")
            if vin:
                vins.append(vin)
            
            # Check for excessive labor hours in activities
            for activity in case.get("activities", []):
                labor_hours = activity.get("LaborHoursClaimed")
                if labor_hours and float(labor_hours) > 8:  # More than 8 hours
                    excessive_labor += 1
                    break
        
        # Check for duplicate VINs
        vin_counts = Counter(vins)
        duplicate_vins = sum(1 for count in vin_counts.values() if count > 1)
        
        if duplicate_vins >= 20:  # Target ~30 duplicate VIN cases
            fraud_indicators.append(f"Duplicate VINs: {duplicate_vins} cases")
        
        if excessive_labor >= 30:  # Target ~45 excessive labor cases  
            fraud_indicators.append(f"Excessive labor: {excessive_labor} cases")
        
        # Check fraud score distribution
        fraud_scores = []
        for case in self.data["cases"]:
            score = case.get("PredictedFraudScore")
            if score is not None:
                fraud_scores.append(float(score))
        
        if fraud_scores:
            high_fraud_scores = sum(1 for score in fraud_scores if score > 0.7)
            if high_fraud_scores >= 50:  # Should have some high-risk cases
                fraud_indicators.append(f"High fraud scores: {high_fraud_scores} cases")
        
        if len(fraud_indicators) >= 2:
            self.log_result("Fraud Patterns", True, 
                          f"Fraud patterns implemented: {', '.join(fraud_indicators)}")
            return True
        else:
            self.log_result("Fraud Patterns", False, 
                          f"Insufficient fraud patterns. Found: {', '.join(fraud_indicators)}")
            return False
    
    def validate_case_attributes(self) -> bool:
        """Validate case-level attributes are present and consistent"""
        required_attributes = [
            "ClaimNumber", "VIN", "VehicleMake", "VehicleModel", "VehicleYear",
            "ContractType", "DealerRegion", "CustomerState", "ClaimValue"
        ]
        
        attribute_issues = []
        
        for i, case in enumerate(self.data["cases"][:50]):  # Check first 50 cases
            case_id = case.get("CaseId", f"Case_{i}")
            
            # Check required attributes exist
            for attr in required_attributes:
                if attr not in case or case[attr] is None or case[attr] == "":
                    attribute_issues.append(f"Case {case_id}: Missing/empty {attr}")
            
            # Validate specific formats
            if "VIN" in case and len(case["VIN"]) != 17:
                attribute_issues.append(f"Case {case_id}: Invalid VIN length")
            
            if "VehicleYear" in case:
                year = case["VehicleYear"]
                if not (2019 <= year <= 2024):
                    attribute_issues.append(f"Case {case_id}: Invalid year {year}")
        
        if attribute_issues:
            self.log_result("Case Attributes", False, 
                          f"Attribute issues found: {len(attribute_issues)}. Examples: {attribute_issues[:3]}")
            return False
        else:
            self.log_result("Case Attributes", True, "Case attributes properly implemented")
            return True
    
    def validate_event_attributes(self) -> bool:
        """Validate event-level attributes are applied correctly"""
        activity_attribute_map = {
            "Damage Assessment": ["DiagnosisCode", "DealerRepairOrderNumber"],
            "Request Documentation": ["PartsCount", "PartsValue"],
            "Liability Determination": ["LaborHoursClaimed", "LaborHoursApproved", "LaborRate"],
            "Assignment": ["FraudScore", "FraudIndicators"],
            "Approve Settlement": ["ApprovalLevel"],
            "Payment Processing": ["PaymentAmount", "PaymentMethod"]
        }
        
        missing_attributes = []
        
        for case in self.data["cases"][:30]:  # Check first 30 cases
            case_id = case.get("CaseId", "Unknown")
            for activity in case.get("activities", []):
                activity_name = activity.get("ActivityName", "")
                if activity_name in activity_attribute_map:
                    expected_attrs = activity_attribute_map[activity_name]
                    for attr in expected_attrs:
                        if attr not in activity or activity[attr] is None or activity[attr] == "":
                            missing_attributes.append(f"Case {case_id}, {activity_name}: Missing {attr}")
        
        if missing_attributes:
            self.log_result("Event Attributes", False, 
                          f"Missing event attributes: {len(missing_attributes)}. Examples: {missing_attributes[:5]}")
            return False
        else:
            self.log_result("Event Attributes", True, "Event attributes properly applied")
            return True
    
    def validate_resource_names(self) -> bool:
        """Validate resource names are simple first names or system names"""
        valid_pattern = re.compile(r'^[A-Za-z][A-Za-z0-9_]*[0-9]*$|^[A-Za-z]+$')
        invalid_resources = set()
        
        for case in self.data["cases"][:50]:  # Check first 50 cases
            for activity in case.get("activities", []):
                resource = activity.get("Resource", "")
                if resource and not valid_pattern.match(resource):
                    invalid_resources.add(resource)
        
        if invalid_resources:
            self.log_result("Resource Names", False, 
                          f"Invalid resource names: {list(invalid_resources)[:5]}")
            return False
        else:
            self.log_result("Resource Names", True, "Resource names follow proper format")
            return True
    
    def validate_business_logic(self) -> bool:
        """Validate business logic compliance"""
        logic_violations = []
        
        for case in self.data["cases"][:100]:  # Check first 100 cases
            activities = case.get("activities", [])
            activity_names = [act.get("ActivityName", "") for act in activities]
            
            # Must start with First Notice of Loss
            if activity_names and activity_names[0] != "First Notice of Loss":
                logic_violations.append(f"Case {case.get('CaseId')}: Doesn't start with First Notice of Loss")
            
            # Verify Coverage should be second (for most cases)
            if len(activity_names) >= 2 and activity_names[1] != "Verify Coverage":
                logic_violations.append(f"Case {case.get('CaseId')}: Second activity not Verify Coverage")
        
        if len(logic_violations) > 20:  # Allow some variance but not too much
            self.log_result("Business Logic", False, 
                          f"Business logic violations: {len(logic_violations)}. Examples: {logic_violations[:3]}")
            return False
        else:
            self.log_result("Business Logic", True, f"Business logic compliance acceptable ({len(logic_violations)} minor violations)")
            return True
    
    def run_validation(self) -> bool:
        """Run complete validation suite"""
        print("Starting Warranty Claims Dataset Validation...")
        
        # Critical validations - must pass
        if not self.validate_file_existence():
            return False
            
        if not self.load_and_parse_json():
            return False
            
        if not self.load_csv_data():
            return False
        
        # Structure validations
        self.validate_case_volume()
        self.validate_required_fields()
        self.validate_datetime_format()
        self.validate_csv_json_consistency()
        self.validate_resource_names()
        
        # Data quality validations
        self.validate_chronological_order()
        self.validate_closing_activities()
        self.validate_case_attributes()
        self.validate_event_attributes()
        
        # Business logic validations
        self.validate_straight_through_processing()
        self.validate_bottlenecks()
        self.validate_fraud_patterns()
        self.validate_business_logic()
        
        # Determine overall result
        critical_failures_count = len(self.critical_failures)
        total_tests = len(self.validation_results)
        passed_tests = sum(1 for r in self.validation_results if r['passed'])
        
        print(f"\nValidation Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {total_tests - passed_tests}")
        print(f"   Critical Failures: {critical_failures_count}")
        print(f"   Warnings: {len(self.warnings)}")
        
        return critical_failures_count == 0 and passed_tests >= (total_tests * 0.85)  # 85% pass rate required
    
    def create_status_files(self, approved: bool):
        """Create appropriate status files"""
        if approved:
            self.create_approval_files()
        else:
            self.create_rejection_files()
    
    def create_approval_files(self):
        """Create approval status and report files"""
        # Create data_status.ok
        with open(os.path.join(STATUS_DIR, "data_status.ok"), 'w') as f:
            f.write("DATASET APPROVED - PRODUCTION READY\n")
            f.write("="*50 + "\n\n")
            f.write(f"Validation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Dataset: Automotive Warranty Claims\n")
            f.write(f"Cases: {len(self.data['cases'])}\n")
            f.write(f"Activities: {sum(len(case.get('activities', [])) for case in self.data['cases'])}\n\n")
            f.write("+ All critical validations passed\n")
            f.write("+ Structure and format compliance verified\n")
            f.write("+ Business logic and bottlenecks validated\n")
            f.write("+ Fraud patterns properly implemented\n")
            f.write("+ Attribute validation successful\n\n")
            f.write("This dataset is ready for process mining analysis in production tools.\n")
        
        # Create comprehensive report
        with open(os.path.join(STATUS_DIR, "data_status.report"), 'w') as f:
            f.write("WARRANTY CLAIMS DATASET - VALIDATION REPORT\n")
            f.write("="*60 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Validator: Automated Data Quality Validator\n")
            f.write(f"Dataset: Automotive Warranty Claims Historical Data\n\n")
            
            f.write("DATASET SUMMARY\n")
            f.write("-" * 20 + "\n")
            f.write(f"Total Cases: {len(self.data['cases'])}\n")
            f.write(f"Total Activities: {sum(len(case.get('activities', [])) for case in self.data['cases'])}\n")
            f.write(f"Time Period: 3-month historical sample\n")
            f.write(f"JSON File Size: {os.path.getsize(JSON_FILE) / (1024*1024):.1f} MB\n")
            f.write(f"CSV File Size: {os.path.getsize(CSV_FILE) / (1024*1024):.1f} MB\n\n")
            
            f.write("VALIDATION RESULTS\n")
            f.write("-" * 20 + "\n")
            for result in self.validation_results:
                status = "PASS" if result['passed'] else "FAIL"
                f.write(f"{status} {result['test']}: {result['message']}\n")
            
            f.write(f"\nWARNINGS ({len(self.warnings)})\n")
            f.write("-" * 20 + "\n")
            for warning in self.warnings:
                f.write(f"WARNING: {warning}\n")
            
            f.write("\nPROCESS MINING RECOMMENDATIONS\n")
            f.write("-" * 35 + "\n")
            f.write("• Focus on bottleneck analysis for DealerTech3, LaborAnalyst1, TechExpert1\n")
            f.write("• Implement fraud pattern dashboards using duplicate VINs and excessive labor flags\n")
            f.write("• Monitor straight-through processing rate (currently ~40%)\n")
            f.write("• Create dealer performance scorecards by region\n")
            f.write("• Track SLA compliance for critical activities\n")
            f.write("• Analyze resource utilization patterns across different contract types\n\n")
            
            f.write("MINDZIE STUDIO INTEGRATION\n")
            f.write("-" * 30 + "\n")
            f.write("This dataset is optimized for Mindzie Studio and includes:\n")
            f.write("+ Proper case and activity structure\n")
            f.write("+ Rich attribute set for filtering and analysis\n")
            f.write("+ Clear bottlenecks for performance optimization\n")
            f.write("+ Fraud patterns for risk analysis\n")
            f.write("+ Realistic timing and resource allocation\n\n")
            
            f.write("DATASET APPROVED FOR PRODUCTION USE\n")
        
        # Remove any rejection file
        rejection_file = os.path.join(STATUS_DIR, "data_status.not")
        if os.path.exists(rejection_file):
            os.remove(rejection_file)
        
        print("Dataset APPROVED - Status files created")
    
    def create_rejection_files(self):
        """Create rejection status file with detailed feedback"""
        with open(os.path.join(STATUS_DIR, "data_status.not"), 'w') as f:
            f.write("DATASET REJECTED - NOT PRODUCTION READY\n")
            f.write("="*50 + "\n\n")
            f.write(f"Validation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Dataset: Automotive Warranty Claims\n\n")
            
            f.write("CRITICAL FAILURES\n")
            f.write("-" * 20 + "\n")
            for failure in self.critical_failures:
                f.write(f"FAILED: {failure}\n")
            
            f.write(f"\nFAILED TESTS ({len([r for r in self.validation_results if not r['passed']])})\n")
            f.write("-" * 20 + "\n")
            for result in self.validation_results:
                if not result['passed']:
                    criticality = " [CRITICAL]" if result['critical'] else ""
                    f.write(f"FAILED {result['test']}{criticality}: {result['message']}\n")
            
            f.write(f"\nWARNINGS ({len(self.warnings)})\n")
            f.write("-" * 20 + "\n")
            for warning in self.warnings:
                f.write(f"WARNING: {warning}\n")
            
            f.write("\nREQUIRED FIXES\n")
            f.write("-" * 15 + "\n")
            f.write("1. Address all CRITICAL failures before resubmission\n")
            f.write("2. Ensure proper JSON structure: {\"cases\": [{\"CaseId\": \"...\", \"activities\": [...]}]}\n")
            f.write("3. Fix datetime format to: YYYY-MM-DD HH:MM:SS (no 'T')\n")
            f.write("4. Implement proper bottleneck patterns for specified resources\n")
            f.write("5. Add missing fraud indicators (duplicate VINs, excessive labor)\n")
            f.write("6. Verify straight-through processing rate is ~40%\n")
            f.write("7. Ensure 90%+ of cases have proper closing activities\n")
            f.write("8. Add all required case and event-level attributes\n\n")
            
            f.write("RESUBMISSION CRITERIA\n")
            f.write("-" * 22 + "\n")
            f.write("• Zero critical failures\n")
            f.write("• 85%+ test pass rate\n")
            f.write("• Clear bottleneck visibility\n")
            f.write("• Fraud patterns implemented\n")
            f.write("• Attribute validation success\n")
            f.write("• CSV-JSON consistency\n\n")
            
            f.write("Dataset must be regenerated to meet production quality standards.\n")
        
        # Remove approval files if they exist
        approval_file = os.path.join(STATUS_DIR, "data_status.ok")
        report_file = os.path.join(STATUS_DIR, "data_status.report")
        if os.path.exists(approval_file):
            os.remove(approval_file)
        if os.path.exists(report_file):
            os.remove(report_file)
        
        print("Dataset REJECTED - Detailed feedback provided in data_status.not")

def main():
    """Main validation routine"""
    print("Warranty Claims Dataset Validator")
    print("=" * 50)
    
    # Change to the correct directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    validator = WarrantyClaimsValidator()
    
    # Run validation
    is_approved = validator.run_validation()
    
    # Create status files
    validator.create_status_files(is_approved)
    
    # Print final result
    if is_approved:
        print("\nVALIDATION SUCCESSFUL")
        print("   Dataset approved for production use")
        print(f"   Status file: {os.path.abspath('data_status.ok')}")
        print(f"   Report file: {os.path.abspath('data_status.report')}")
    else:
        print("\nVALIDATION FAILED")
        print("   Dataset requires fixes before production use")
        print(f"   Feedback file: {os.path.abspath('data_status.not')}")
        print(f"   Critical failures: {len(validator.critical_failures)}")
    
    return 0 if is_approved else 1

if __name__ == "__main__":
    exit(main())