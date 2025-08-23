#!/usr/bin/env python3
"""
Car Insurance Warranty Claims Dataset Analysis Script
=====================================================

Comprehensive analysis script for the validated Car Insurance Warranty Claims dataset.
Performs statistical analysis, KPI calculations, bottleneck analysis, and fraud pattern detection.

Dataset Files:
- warranty_claims_historical.json
- warranty_claims_historical.csv

Specification:
- docs/process_specification.md

Author: Process Mining Data Analysis Agent
Date: 2025-08-22
"""

import json
import csv
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics
import os
import sys

class WarrantyClaimsAnalyzer:
    """Comprehensive analyzer for warranty claims process mining data"""
    
    def __init__(self, json_file_path, csv_file_path):
        self.json_file_path = json_file_path
        self.csv_file_path = csv_file_path
        self.cases_data = None
        self.events_df = None
        self.analysis_results = {}
        
    def load_data(self):
        """Load both JSON and CSV datasets"""
        print("Loading warranty claims datasets...")
        
        # Load JSON data
        with open(self.json_file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            self.cases_data = json_data['cases']
        
        # Load CSV data
        self.events_df = pd.read_csv(self.csv_file_path)
        self.events_df['ActivityTime'] = pd.to_datetime(self.events_df['ActivityTime'])
        
        print(f"Loaded {len(self.cases_data)} cases and {len(self.events_df)} events")
        
    def calculate_dataset_overview(self):
        """Calculate basic dataset statistics and overview"""
        print("\nCalculating dataset overview...")
        
        overview = {
            'total_cases': len(self.cases_data),
            'total_events': len(self.events_df),
            'date_range': {
                'start_date': self.events_df['ActivityTime'].min().strftime('%Y-%m-%d'),
                'end_date': self.events_df['ActivityTime'].max().strftime('%Y-%m-%d'),
                'duration_days': (self.events_df['ActivityTime'].max() - self.events_df['ActivityTime'].min()).days
            },
            'activities': {
                'unique_activities': self.events_df['ActivityName'].nunique(),
                'activity_list': sorted(self.events_df['ActivityName'].unique().tolist()),
                'activity_frequency': self.events_df['ActivityName'].value_counts().to_dict()
            },
            'resources': {
                'unique_resources': self.events_df['Resource'].nunique(),
                'resource_list': sorted(self.events_df['Resource'].unique().tolist()),
                'resource_workload': self.events_df['Resource'].value_counts().to_dict()
            },
            'systems': {
                'unique_systems': self.events_df['SystemUsed'].nunique(),
                'system_distribution': self.events_df['SystemUsed'].value_counts().to_dict()
            }
        }
        
        # Calculate case completion statistics
        completed_cases = 0
        pending_cases = 0
        closing_activities = ['Approve Settlement', 'Resolution and Settlement', 'Payment Processing', 'Claim Closure']
        
        for case in self.cases_data:
            activities = [activity['ActivityName'] for activity in case['activities']]
            if any(activity in closing_activities for activity in activities):
                completed_cases += 1
            else:
                pending_cases += 1
        
        overview['case_completion'] = {
            'completed_cases': completed_cases,
            'pending_cases': pending_cases,
            'completion_rate': completed_cases / len(self.cases_data) * 100
        }
        
        self.analysis_results['dataset_overview'] = overview
        
    def calculate_process_performance_metrics(self):
        """Calculate key process performance indicators"""
        print("Calculating process performance metrics...")
        
        performance = {}
        
        # Calculate case durations
        case_durations = []
        straight_through_cases = 0
        
        for case in self.cases_data:
            activities = case['activities']
            if len(activities) >= 2:
                start_time = pd.to_datetime(activities[0]['ActivityTime'])
                end_time = pd.to_datetime(activities[-1]['ActivityTime'])
                duration_hours = (end_time - start_time).total_seconds() / 3600
                case_durations.append(duration_hours)
                
                # Check for straight-through processing (First Notice -> Verify Coverage -> Approve Settlement)
                if (len(activities) == 3 and 
                    activities[0]['ActivityName'] == 'First Notice of Loss' and
                    activities[1]['ActivityName'] == 'Verify Coverage' and
                    activities[2]['ActivityName'] == 'Approve Settlement'):
                    straight_through_cases += 1
        
        performance['case_processing_times'] = {
            'average_hours': statistics.mean(case_durations) if case_durations else 0,
            'median_hours': statistics.median(case_durations) if case_durations else 0,
            'min_hours': min(case_durations) if case_durations else 0,
            'max_hours': max(case_durations) if case_durations else 0,
            'std_dev_hours': statistics.stdev(case_durations) if len(case_durations) > 1 else 0
        }
        
        performance['straight_through_processing'] = {
            'count': straight_through_cases,
            'rate_percentage': (straight_through_cases / len(self.cases_data)) * 100,
            'target_rate': 60,
            'current_vs_target': (straight_through_cases / len(self.cases_data)) * 100 - 60
        }
        
        # Calculate approval rates
        approved_cases = 0
        denied_cases = 0
        
        for case in self.cases_data:
            activities = [activity['ActivityName'] for activity in case['activities']]
            if 'Approve Settlement' in activities or 'Payment Processing' in activities:
                approved_cases += 1
            elif 'Resolution and Settlement' in activities:
                denied_cases += 1
        
        performance['approval_rates'] = {
            'approved_count': approved_cases,
            'denied_count': denied_cases,
            'approval_rate': (approved_cases / len(self.cases_data)) * 100,
            'denial_rate': (denied_cases / len(self.cases_data)) * 100
        }
        
        self.analysis_results['process_performance'] = performance
        
    def analyze_bottlenecks(self):
        """Identify and analyze process bottlenecks based on specification"""
        print("Analyzing process bottlenecks...")
        
        bottlenecks = {}
        
        # Analyze resource performance based on specification bottlenecks
        specified_bottlenecks = {
            'DealerTech3': {'activity': 'Damage Assessment', 'expected_factor': 0.6},
            'LaborAnalyst1': {'activity': 'Liability Determination', 'expected_factor': 0.7},
            'TechExpert1': {'activity': 'Claim Investigation', 'expected_factor': 0.5},
            'FraudAnalyst': {'activity': 'Assignment', 'expected_factor': 0.6}
        }
        
        for resource, spec in specified_bottlenecks.items():
            activity_name = spec['activity']
            expected_factor = spec['expected_factor']
            
            # Get events for this resource and activity
            resource_events = self.events_df[
                (self.events_df['Resource'] == resource) & 
                (self.events_df['ActivityName'] == activity_name)
            ]
            
            # Get average performance for this activity across all resources
            activity_events = self.events_df[self.events_df['ActivityName'] == activity_name]
            
            if len(resource_events) > 0 and len(activity_events) > 0:
                # Calculate duration statistics (using case completion as proxy)
                resource_case_ids = set(resource_events['CaseId'].unique())
                
                resource_durations = []
                all_durations = []
                
                for case in self.cases_data:
                    case_id = case['CaseId']
                    activities = case['activities']
                    
                    # Find the specific activity duration
                    for i, activity in enumerate(activities):
                        if activity['ActivityName'] == activity_name:
                            if i + 1 < len(activities):
                                start_time = pd.to_datetime(activity['ActivityTime'])
                                next_time = pd.to_datetime(activities[i + 1]['ActivityTime'])
                                duration = (next_time - start_time).total_seconds() / 3600
                                
                                if case_id in resource_case_ids:
                                    resource_durations.append(duration)
                                all_durations.append(duration)
                            break
                
                if resource_durations and all_durations:
                    avg_resource_duration = statistics.mean(resource_durations)
                    avg_all_duration = statistics.mean(all_durations)
                    performance_factor = avg_resource_duration / avg_all_duration if avg_all_duration > 0 else 1
                    
                    bottlenecks[resource] = {
                        'activity': activity_name,
                        'event_count': len(resource_events),
                        'avg_duration_hours': avg_resource_duration,
                        'overall_avg_duration_hours': avg_all_duration,
                        'performance_factor': performance_factor,
                        'expected_factor': expected_factor,
                        'bottleneck_confirmed': performance_factor > 1.2,  # 20% slower than average
                        'impact_severity': 'High' if performance_factor > 1.5 else 'Medium' if performance_factor > 1.2 else 'Low'
                    }
        
        # Analyze activity-level bottlenecks
        activity_bottlenecks = {}
        for activity in self.events_df['ActivityName'].unique():
            activity_events = self.events_df[self.events_df['ActivityName'] == activity]
            
            # Calculate waiting times (time between events in the same case)
            waiting_times = []
            for case in self.cases_data:
                activities = case['activities']
                for i, curr_activity in enumerate(activities):
                    if curr_activity['ActivityName'] == activity and i > 0:
                        prev_time = pd.to_datetime(activities[i-1]['ActivityTime'])
                        curr_time = pd.to_datetime(curr_activity['ActivityTime'])
                        wait_time = (curr_time - prev_time).total_seconds() / 3600
                        waiting_times.append(wait_time)
            
            if waiting_times:
                activity_bottlenecks[activity] = {
                    'event_count': len(activity_events),
                    'avg_waiting_time_hours': statistics.mean(waiting_times),
                    'max_waiting_time_hours': max(waiting_times),
                    'median_waiting_time_hours': statistics.median(waiting_times),
                    'bottleneck_risk': 'High' if statistics.mean(waiting_times) > 24 else 'Medium' if statistics.mean(waiting_times) > 8 else 'Low'
                }
        
        bottlenecks['resource_bottlenecks'] = bottlenecks
        bottlenecks['activity_bottlenecks'] = activity_bottlenecks
        
        self.analysis_results['bottleneck_analysis'] = bottlenecks
        
    def analyze_fraud_patterns(self):
        """Analyze fraud patterns and detection effectiveness"""
        print("Analyzing fraud patterns...")
        
        fraud_analysis = {}
        
        # Analyze fraud indicators
        fraud_events = self.events_df[self.events_df['ActivityName'] == 'Assignment'].copy()
        
        if not fraud_events.empty and 'FraudIndicators' in fraud_events.columns:
            fraud_indicators = fraud_events['FraudIndicators'].value_counts().to_dict()
            fraud_scores = fraud_events['FraudScore'].dropna()
            
            fraud_analysis['fraud_investigation'] = {
                'total_fraud_investigations': len(fraud_events),
                'fraud_indicators_distribution': fraud_indicators,
                'avg_fraud_score': fraud_scores.mean() if not fraud_scores.empty else 0,
                'high_risk_cases': len(fraud_scores[fraud_scores > 70]) if not fraud_scores.empty else 0
            }
        
        # Calculate predicted vs actual fraud
        high_fraud_score_cases = []
        actual_fraud_cases = []
        
        for case in self.cases_data:
            case_id = case['CaseId']
            fraud_score = case.get('PredictedFraudScore', 0)
            
            if fraud_score > 0.7:  # High predicted fraud score
                high_fraud_score_cases.append(case_id)
            
            # Check if case was actually flagged for fraud
            activities = [activity['ActivityName'] for activity in case['activities']]
            if 'Assignment' in activities:
                # Check if denied due to fraud
                denial_activities = [a for a in case['activities'] if a['ActivityName'] == 'Resolution and Settlement']
                if denial_activities:
                    denial_activity = denial_activities[0]
                    if denial_activity.get('DenialReason') == 'FraudSuspected':
                        actual_fraud_cases.append(case_id)
        
        fraud_analysis['fraud_prediction_accuracy'] = {
            'high_predicted_fraud_cases': len(high_fraud_score_cases),
            'actual_fraud_cases': len(actual_fraud_cases),
            'prediction_overlap': len(set(high_fraud_score_cases) & set(actual_fraud_cases)),
            'false_positives': len(set(high_fraud_score_cases) - set(actual_fraud_cases)),
            'false_negatives': len(set(actual_fraud_cases) - set(high_fraud_score_cases))
        }
        
        if len(actual_fraud_cases) > 0:
            detection_rate = len(set(high_fraud_score_cases) & set(actual_fraud_cases)) / len(actual_fraud_cases) * 100
        else:
            detection_rate = 0
            
        fraud_analysis['detection_effectiveness'] = {
            'detection_rate_percentage': detection_rate,
            'target_rate': 95,
            'gap_to_target': detection_rate - 95
        }
        
        self.analysis_results['fraud_analysis'] = fraud_analysis
        
    def calculate_kpis(self):
        """Calculate all KPIs as specified in the requirements"""
        print("Calculating KPIs against targets...")
        
        kpis = {}
        
        # 1. Average Claim Processing Time
        case_durations = []
        for case in self.cases_data:
            activities = case['activities']
            if len(activities) >= 2:
                start_time = pd.to_datetime(activities[0]['ActivityTime'])
                end_time = pd.to_datetime(activities[-1]['ActivityTime'])
                duration_hours = (end_time - start_time).total_seconds() / 3600
                case_durations.append(duration_hours)
        
        avg_processing_time = statistics.mean(case_durations) if case_durations else 0
        
        kpis['average_claim_processing_time'] = {
            'current_hours': avg_processing_time,
            'target_hours': 48,
            'current_vs_target_hours': avg_processing_time - 48,
            'performance': 'Below Target' if avg_processing_time > 48 else 'Above Target'
        }
        
        # 2. Straight-Through Processing Rate (calculated earlier)
        straight_through_rate = self.analysis_results['process_performance']['straight_through_processing']['rate_percentage']
        
        kpis['straight_through_processing_rate'] = {
            'current_percentage': straight_through_rate,
            'target_percentage': 60,
            'gap_to_target': straight_through_rate - 60,
            'performance': 'Below Target' if straight_through_rate < 60 else 'Above Target'
        }
        
        # 3. First-Time Approval Rate
        first_time_approvals = 0
        for case in self.cases_data:
            activities = [activity['ActivityName'] for activity in case['activities']]
            # Check if case went straight to approval without rework
            if ('Approve Settlement' in activities and 
                'Claim Closure' not in activities):
                first_time_approvals += 1
        
        first_time_approval_rate = (first_time_approvals / len(self.cases_data)) * 100
        
        kpis['first_time_approval_rate'] = {
            'current_percentage': first_time_approval_rate,
            'target_percentage': 85,
            'gap_to_target': first_time_approval_rate - 85,
            'performance': 'Below Target' if first_time_approval_rate < 85 else 'Above Target'
        }
        
        # 4. Fraud Detection Rate (calculated earlier)
        fraud_detection_rate = self.analysis_results['fraud_analysis']['detection_effectiveness']['detection_rate_percentage']
        
        kpis['fraud_detection_rate'] = {
            'current_percentage': fraud_detection_rate,
            'target_percentage': 95,
            'gap_to_target': fraud_detection_rate - 95,
            'performance': 'Below Target' if fraud_detection_rate < 95 else 'Above Target'
        }
        
        # 5. Cost per Claim (estimated based on processing complexity)
        total_events = len(self.events_df)
        estimated_cost_per_event = 3.5  # Estimated cost per processing event
        total_estimated_cost = total_events * estimated_cost_per_event
        cost_per_claim = total_estimated_cost / len(self.cases_data)
        
        kpis['cost_per_claim'] = {
            'current_usd': cost_per_claim,
            'target_usd': 25,
            'gap_to_target': cost_per_claim - 25,
            'performance': 'Above Target' if cost_per_claim < 25 else 'Below Target'
        }
        
        self.analysis_results['kpis'] = kpis
        
    def check_specification_compliance(self):
        """Check dataset compliance with process specification"""
        print("Checking specification compliance...")
        
        compliance = {}
        
        # Check expected vs actual case count
        expected_cases = 1500
        actual_cases = len(self.cases_data)
        
        compliance['case_count'] = {
            'expected': expected_cases,
            'actual': actual_cases,
            'compliance_percentage': (actual_cases / expected_cases) * 100,
            'status': 'Compliant' if actual_cases >= expected_cases * 0.95 else 'Non-Compliant'
        }
        
        # Check required activities presence
        expected_activities = [
            'First Notice of Loss', 'Verify Coverage', 'Damage Assessment',
            'Request Documentation', 'Liability Determination', 'Claim Investigation',
            'Assignment', 'Approve Settlement', 'Resolution and Settlement',
            'Payment Processing', 'Generate Payment Confirmation', 'Claim Closure'
        ]
        
        actual_activities = set(self.events_df['ActivityName'].unique())
        missing_activities = set(expected_activities) - actual_activities
        
        compliance['activity_coverage'] = {
            'expected_activities': len(expected_activities),
            'actual_activities': len(actual_activities),
            'missing_activities': list(missing_activities),
            'coverage_percentage': (len(actual_activities & set(expected_activities)) / len(expected_activities)) * 100
        }
        
        # Check bottleneck implementation
        expected_bottleneck_resources = ['DealerTech3', 'LaborAnalyst1', 'TechExpert1', 'FraudAnalyst']
        actual_resources = set(self.events_df['Resource'].unique())
        bottleneck_resources_present = set(expected_bottleneck_resources) & actual_resources
        
        compliance['bottleneck_implementation'] = {
            'expected_bottleneck_resources': len(expected_bottleneck_resources),
            'implemented_bottleneck_resources': len(bottleneck_resources_present),
            'implementation_rate': (len(bottleneck_resources_present) / len(expected_bottleneck_resources)) * 100,
            'missing_resources': list(set(expected_bottleneck_resources) - actual_resources)
        }
        
        self.analysis_results['specification_compliance'] = compliance
        
    def assess_process_mining_readiness(self):
        """Assess dataset readiness for process mining analysis"""
        print("Assessing process mining readiness...")
        
        readiness = {}
        
        # Check data quality dimensions
        # 1. Completeness
        required_fields = ['CaseId', 'ActivityName', 'ActivityTime', 'Resource']
        completeness_issues = {}
        
        for field in required_fields:
            if field in self.events_df.columns:
                null_count = self.events_df[field].isnull().sum()
                completeness_issues[field] = {
                    'null_count': null_count,
                    'completeness_percentage': ((len(self.events_df) - null_count) / len(self.events_df)) * 100
                }
        
        # 2. Consistency
        datetime_consistency = True
        try:
            pd.to_datetime(self.events_df['ActivityTime'])
        except:
            datetime_consistency = False
        
        # 3. Variant Analysis
        case_variants = {}
        for case in self.cases_data:
            activities = [activity['ActivityName'] for activity in case['activities']]
            variant = ' -> '.join(activities)
            case_variants[variant] = case_variants.get(variant, 0) + 1
        
        # Sort variants by frequency
        top_variants = dict(sorted(case_variants.items(), key=lambda x: x[1], reverse=True)[:10])
        
        readiness['data_quality'] = {
            'completeness_issues': completeness_issues,
            'datetime_consistency': datetime_consistency,
            'total_variants': len(case_variants),
            'top_variants': top_variants
        }
        
        # 4. Process Discovery Readiness Score
        actual_activities = set(self.events_df['ActivityName'].unique())
        score_components = {
            'case_count': min(100, (len(self.cases_data) / 1000) * 100),  # Target 1000+ cases
            'activity_variety': min(100, (len(actual_activities) / 10) * 100),  # Target 10+ activities
            'data_completeness': min([completeness_issues[field]['completeness_percentage'] 
                                    for field in required_fields if field in completeness_issues]),
            'temporal_consistency': 100 if datetime_consistency else 0,
            'variant_diversity': min(100, (len(case_variants) / 50) * 100)  # Target 50+ variants
        }
        
        overall_readiness_score = statistics.mean(score_components.values())
        
        readiness['process_mining_readiness_score'] = {
            'overall_score': overall_readiness_score,
            'score_components': score_components,
            'readiness_level': ('Excellent' if overall_readiness_score >= 90 else
                              'Good' if overall_readiness_score >= 75 else
                              'Fair' if overall_readiness_score >= 60 else 'Poor')
        }
        
        self.analysis_results['process_mining_readiness'] = readiness
        
    def run_complete_analysis(self):
        """Run all analysis components"""
        print("Starting comprehensive warranty claims analysis...")
        print("=" * 60)
        
        self.load_data()
        self.calculate_dataset_overview()
        self.calculate_process_performance_metrics()
        self.analyze_bottlenecks()
        self.analyze_fraud_patterns()
        self.calculate_kpis()
        self.check_specification_compliance()
        self.assess_process_mining_readiness()
        
        print("\nAnalysis completed successfully!")
        return self.analysis_results
        
    def generate_summary_report(self):
        """Generate a summary of key findings"""
        if not self.analysis_results:
            raise ValueError("Analysis must be run before generating summary")
        
        print("\n" + "=" * 60)
        print("WARRANTY CLAIMS ANALYSIS SUMMARY")
        print("=" * 60)
        
        # Dataset Overview
        overview = self.analysis_results['dataset_overview']
        print(f"\nDATASET OVERVIEW:")
        print(f"• Total Cases: {overview['total_cases']:,}")
        print(f"• Total Events: {overview['total_events']:,}")
        print(f"• Date Range: {overview['date_range']['start_date']} to {overview['date_range']['end_date']}")
        print(f"• Completion Rate: {overview['case_completion']['completion_rate']:.1f}%")
        
        # KPIs
        kpis = self.analysis_results['kpis']
        print(f"\nKEY PERFORMANCE INDICATORS:")
        print(f"• Avg Processing Time: {kpis['average_claim_processing_time']['current_hours']:.1f}h (Target: 48h)")
        print(f"• Straight-Through Rate: {kpis['straight_through_processing_rate']['current_percentage']:.1f}% (Target: 60%)")
        print(f"• First-Time Approval: {kpis['first_time_approval_rate']['current_percentage']:.1f}% (Target: 85%)")
        print(f"• Fraud Detection: {kpis['fraud_detection_rate']['current_percentage']:.1f}% (Target: 95%)")
        
        # Bottlenecks
        bottlenecks = self.analysis_results['bottleneck_analysis']['resource_bottlenecks']
        print(f"\nIDENTIFIED BOTTLENECKS:")
        for resource, data in bottlenecks.items():
            if isinstance(data, dict) and data.get('bottleneck_confirmed'):
                print(f"• {resource}: {data['performance_factor']:.2f}x slower ({data['activity']})")
        
        # Process Mining Readiness
        readiness = self.analysis_results['process_mining_readiness']
        score = readiness['process_mining_readiness_score']['overall_score']
        level = readiness['process_mining_readiness_score']['readiness_level']
        print(f"\nPROCESS MINING READINESS: {score:.1f}/100 ({level})")

def main():
    """Main execution function"""
    # File paths
    json_file = "C:/ReposMindzie/mindzie_process_data/Car Insurance Warranty Claims/src/output/warranty_claims_historical.json"
    csv_file = "C:/ReposMindzie/mindzie_process_data/Car Insurance Warranty Claims/src/output/warranty_claims_historical.csv"
    
    # Check if files exist
    if not os.path.exists(json_file):
        print(f"Error: JSON file not found: {json_file}")
        sys.exit(1)
    
    if not os.path.exists(csv_file):
        print(f"Error: CSV file not found: {csv_file}")
        sys.exit(1)
    
    # Create analyzer and run analysis
    analyzer = WarrantyClaimsAnalyzer(json_file, csv_file)
    results = analyzer.run_complete_analysis()
    analyzer.generate_summary_report()
    
    # Save results to JSON for further use (with circular reference handling)
    output_file = "C:/ReposMindzie/mindzie_process_data/Car Insurance Warranty Claims/src/analysis_results.json"
    try:
        # Create a simplified version for JSON serialization
        simplified_results = {}
        for key, value in results.items():
            if key == 'bottleneck_analysis':
                # Handle nested structure that might cause circular reference
                simplified_results[key] = {
                    'resource_bottlenecks': {k: v for k, v in value.items() if k != 'resource_bottlenecks'},
                    'activity_bottlenecks': value.get('activity_bottlenecks', {})
                }
            else:
                simplified_results[key] = value
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(simplified_results, f, indent=2, default=str)
        
        print(f"\nDetailed analysis results saved to: {output_file}")
    except Exception as e:
        print(f"\nNote: Could not save JSON results due to: {e}")
        print("Analysis completed successfully nonetheless.")

if __name__ == "__main__":
    main()