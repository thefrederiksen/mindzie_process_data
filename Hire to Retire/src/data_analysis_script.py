#!/usr/bin/env python3
"""
Hire to Retire Process Mining Dataset - Statistical Analysis Script
==================================================================

This script performs comprehensive statistical analysis on the validated 
Hire to Retire process mining dataset, calculating key performance indicators
and generating insights for business stakeholders.

Author: Data Report Writer Agent
Dataset: hire_to_retire_historical.csv/json
Validation Status: APPROVED (data_status.ok)
"""

import json
import csv
import pandas as pd
from datetime import datetime, timedelta
import statistics
from collections import Counter, defaultdict
import os
import sys

class HireToRetireAnalyzer:
    """Comprehensive analyzer for Hire to Retire process mining data"""
    
    def __init__(self, csv_path, json_path):
        self.csv_path = csv_path
        self.json_path = json_path
        self.df = None
        self.cases_data = None
        self.analysis_results = {}
        
    def load_data(self):
        """Load both CSV and JSON datasets"""
        try:
            # Load CSV data
            self.df = pd.read_csv(self.csv_path)
            self.df['ActivityTime'] = pd.to_datetime(self.df['ActivityTime'])
            
            # Load JSON data
            with open(self.json_path, 'r', encoding='utf-8') as f:
                self.cases_data = json.load(f)
                
            print(f">> Loaded {len(self.df)} events from {len(self.cases_data)} cases")
            return True
            
        except Exception as e:
            print(f">> Error loading data: {e}")
            return False
    
    def basic_statistics(self):
        """Calculate basic dataset statistics"""
        stats = {
            'total_events': len(self.df),
            'total_cases': len(self.cases_data),
            'unique_activities': self.df['ActivityName'].nunique(),
            'activity_list': sorted(self.df['ActivityName'].unique()),
            'date_range': {
                'start': self.df['ActivityTime'].min().strftime('%Y-%m-%d'),
                'end': self.df['ActivityTime'].max().strftime('%Y-%m-%d')
            },
            'departments': dict(self.df['Department'].value_counts()),
            'locations': dict(self.df['Location'].value_counts()),
            'resources': dict(self.df['Resource'].value_counts())
        }
        
        self.analysis_results['basic_stats'] = stats
        return stats
    
    def calculate_time_to_fill(self):
        """Calculate Time to Fill KPI (Job Posted to Offer Accepted)"""
        time_to_fill_data = []
        
        for case in self.cases_data:
            activities = {act['ActivityName']: datetime.fromisoformat(act['ActivityTime']) 
                         for act in case['activities']}
            
            if 'Job Posted' in activities and 'Offer Accepted' in activities:
                ttf_days = (activities['Offer Accepted'] - activities['Job Posted']).days
                time_to_fill_data.append({
                    'case_id': case['CaseId'],
                    'department': case['Department'],
                    'location': case['Location'],
                    'days': ttf_days
                })
        
        if time_to_fill_data:
            ttf_values = [item['days'] for item in time_to_fill_data]
            ttf_stats = {
                'count': len(ttf_values),
                'average_days': round(statistics.mean(ttf_values), 1),
                'median_days': round(statistics.median(ttf_values), 1),
                'min_days': min(ttf_values),
                'max_days': max(ttf_values),
                'target_days': 30,
                'cases_over_target': len([x for x in ttf_values if x > 30]),
                'percentage_over_target': round(len([x for x in ttf_values if x > 30]) / len(ttf_values) * 100, 1),
                'by_department': {}
            }
            
            # Calculate by department
            dept_data = defaultdict(list)
            for item in time_to_fill_data:
                dept_data[item['department']].append(item['days'])
                
            for dept, values in dept_data.items():
                ttf_stats['by_department'][dept] = {
                    'count': len(values),
                    'average_days': round(statistics.mean(values), 1),
                    'over_target': len([x for x in values if x > 30])
                }
                
            self.analysis_results['time_to_fill'] = ttf_stats
            return ttf_stats
        
        return None
    
    def analyze_bottlenecks(self):
        """Analyze performance bottlenecks as specified in process specification"""
        bottleneck_analysis = {
            'peter_interview_delays': {'resource': 'Peter', 'activity': 'Interview Completed', 'performance_factor': 0.7},
            'david_equipment_delays': {'resource': 'David', 'activity': 'Equipment Assigned', 'performance_factor': 0.6},
            'robert_review_delays': {'resource': 'Robert', 'activity': 'Performance Review', 'performance_factor': 0.5},
            'system_integration_delays': {'resource': 'System', 'activities': ['Application Received', 'Onboarding Started', 'Equipment Assigned', 'Employment Ended'], 'performance_factor': 0.3}
        }
        
        # Analyze Peter's interview performance
        peter_interviews = self.df[(self.df['Resource'] == 'Peter') & (self.df['ActivityName'] == 'Interview Completed')]
        other_interviews = self.df[(self.df['Resource'] != 'Peter') & (self.df['ActivityName'] == 'Interview Completed')]
        
        bottleneck_results = {}
        
        if len(peter_interviews) > 0 and len(other_interviews) > 0:
            # Calculate average time between Application Received and Interview Completed
            peter_delays = self._calculate_interview_delays(peter_interviews['CaseId'].tolist())
            other_delays = self._calculate_interview_delays(other_interviews['CaseId'].tolist())
            
            bottleneck_results['peter_analysis'] = {
                'cases_handled': len(peter_interviews),
                'average_delay_days': round(statistics.mean(peter_delays) if peter_delays else 0, 1),
                'comparison_avg': round(statistics.mean(other_delays) if other_delays else 0, 1),
                'performance_impact': 'Significantly slower' if peter_delays and other_delays and statistics.mean(peter_delays) > statistics.mean(other_delays) * 1.3 else 'Within normal range'
            }
        
        # Analyze David's equipment assignment performance
        david_equipment = self.df[(self.df['Resource'] == 'David') & (self.df['ActivityName'] == 'Equipment Assigned')]
        other_equipment = self.df[(self.df['Resource'] != 'David') & (self.df['ActivityName'] == 'Equipment Assigned')]
        
        if len(david_equipment) > 0:
            bottleneck_results['david_analysis'] = {
                'cases_handled': len(david_equipment),
                'total_equipment_cases': len(self.df[self.df['ActivityName'] == 'Equipment Assigned']),
                'percentage_of_workload': round(len(david_equipment) / len(self.df[self.df['ActivityName'] == 'Equipment Assigned']) * 100, 1)
            }
        
        # Analyze Robert's review performance
        robert_reviews = self.df[(self.df['Resource'] == 'Robert') & (self.df['ActivityName'] == 'Performance Review')]
        
        if len(robert_reviews) > 0:
            bottleneck_results['robert_analysis'] = {
                'cases_handled': len(robert_reviews),
                'total_review_cases': len(self.df[self.df['ActivityName'] == 'Performance Review']),
                'percentage_of_workload': round(len(robert_reviews) / len(self.df[self.df['ActivityName'] == 'Performance Review']) * 100, 1)
            }
        
        self.analysis_results['bottleneck_analysis'] = bottleneck_results
        return bottleneck_results
    
    def _calculate_interview_delays(self, case_ids):
        """Helper function to calculate delays between Application Received and Interview Completed"""
        delays = []
        
        for case_id in case_ids:
            case_events = self.df[self.df['CaseId'] == case_id].sort_values('ActivityTime')
            
            app_received = case_events[case_events['ActivityName'] == 'Application Received']
            interview_completed = case_events[case_events['ActivityName'] == 'Interview Completed']
            
            if not app_received.empty and not interview_completed.empty:
                delay_days = (interview_completed.iloc[0]['ActivityTime'] - app_received.iloc[0]['ActivityTime']).days
                delays.append(delay_days)
                
        return delays
    
    def process_flow_analysis(self):
        """Analyze process flows and success rates"""
        flow_stats = {
            'recruitment_funnel': {},
            'completion_rates': {},
            'rejection_analysis': {}
        }
        
        # Count activities
        activity_counts = dict(self.df['ActivityName'].value_counts())
        
        # Calculate recruitment funnel
        job_posted = activity_counts.get('Job Posted', 0)
        app_received = activity_counts.get('Application Received', 0)
        interviews = activity_counts.get('Interview Completed', 0)
        offers_extended = activity_counts.get('Offer Extended', 0)
        offers_accepted = activity_counts.get('Offer Accepted', 0)
        
        flow_stats['recruitment_funnel'] = {
            'job_posted': job_posted,
            'application_received': app_received,
            'screening_pass_rate': round((app_received / job_posted * 100) if job_posted > 0 else 0, 1),
            'interview_completed': interviews,
            'interview_rate': round((interviews / app_received * 100) if app_received > 0 else 0, 1),
            'offers_extended': offers_extended,
            'offer_rate': round((offers_extended / interviews * 100) if interviews > 0 else 0, 1),
            'offers_accepted': offers_accepted,
            'acceptance_rate': round((offers_accepted / offers_extended * 100) if offers_extended > 0 else 0, 1)
        }
        
        # Count rejections
        rejections = {
            'application_rejected': activity_counts.get('Application Rejected', 0),
            'interview_failed': activity_counts.get('Interview Failed', 0),
            'offer_rejected': activity_counts.get('Offer Rejected', 0),
            'probation_failed': activity_counts.get('Probation Failed', 0)
        }
        
        flow_stats['rejection_analysis'] = rejections
        
        # Calculate completion rates for hired employees
        onboarding_started = activity_counts.get('Onboarding Started', 0)
        probation_completed = activity_counts.get('Probation Completed', 0)
        employment_ended = activity_counts.get('Employment Ended', 0)
        
        flow_stats['completion_rates'] = {
            'onboarding_started': onboarding_started,
            'probation_completed': probation_completed,
            'probation_success_rate': round((probation_completed / onboarding_started * 100) if onboarding_started > 0 else 0, 1),
            'employment_ended': employment_ended,
            'retention_rate': round(((probation_completed - employment_ended) / probation_completed * 100) if probation_completed > 0 else 0, 1)
        }
        
        self.analysis_results['process_flows'] = flow_stats
        return flow_stats
    
    def resource_performance_analysis(self):
        """Analyze resource performance and workload distribution"""
        resource_stats = {}
        
        # Overall resource activity counts
        resource_activity = self.df.groupby(['Resource', 'ActivityName']).size().unstack(fill_value=0)
        
        # Focus on key bottleneck resources
        key_resources = ['Peter', 'David', 'Robert', 'System']
        
        for resource in key_resources:
            if resource in self.df['Resource'].values:
                resource_data = self.df[self.df['Resource'] == resource]
                
                resource_stats[resource] = {
                    'total_activities': len(resource_data),
                    'activity_breakdown': dict(resource_data['ActivityName'].value_counts()),
                    'departments_served': list(resource_data['Department'].unique()),
                    'locations_served': list(resource_data['Location'].unique())
                }
        
        self.analysis_results['resource_performance'] = resource_stats
        return resource_stats
    
    def compliance_analysis(self):
        """Analyze process compliance and SLA adherence"""
        compliance_stats = {
            'sla_adherence': {},
            'standard_flow_compliance': 0,
            'missing_activities': {}
        }
        
        # Check SLA adherence for key activities
        sla_rules = {
            'Interview_Completed': 14,  # 14 days from application
            'Offer_Extended': 5,        # 5 days after interview  
            'Equipment_Assigned': 1,    # 1 day after onboarding start
            'Leave_Approved': 1         # 1 day response time
        }
        
        # Calculate standard flow compliance (cases following expected sequence)
        standard_flow_count = 0
        total_hired_cases = 0
        
        for case in self.cases_data:
            activities = [act['ActivityName'] for act in case['activities']]
            
            # Check if case was hired (has Offer Accepted)
            if 'Offer Accepted' in activities:
                total_hired_cases += 1
                
                # Check standard sequence: Job Posted -> Application Received -> Interview Completed -> Offer Extended -> Offer Accepted
                expected_sequence = ['Job Posted', 'Application Received', 'Interview Completed', 'Offer Extended', 'Offer Accepted']
                
                if self._follows_sequence(activities, expected_sequence):
                    standard_flow_count += 1
        
        compliance_stats['standard_flow_compliance'] = round((standard_flow_count / total_hired_cases * 100) if total_hired_cases > 0 else 0, 1)
        compliance_stats['total_hired_cases'] = total_hired_cases
        compliance_stats['standard_flow_cases'] = standard_flow_count
        
        self.analysis_results['compliance'] = compliance_stats
        return compliance_stats
    
    def _follows_sequence(self, activities, expected_sequence):
        """Check if activities follow the expected sequence"""
        activity_positions = {}
        for i, activity in enumerate(activities):
            if activity not in activity_positions:
                activity_positions[activity] = i
                
        for i in range(len(expected_sequence) - 1):
            current_activity = expected_sequence[i]
            next_activity = expected_sequence[i + 1]
            
            if current_activity in activity_positions and next_activity in activity_positions:
                if activity_positions[current_activity] >= activity_positions[next_activity]:
                    return False
            elif current_activity not in activity_positions or next_activity not in activity_positions:
                return False
                
        return True
    
    def generate_kpi_dashboard(self):
        """Generate KPI dashboard with target vs actual performance"""
        kpis = {
            'time_to_fill': {
                'target': 30,
                'actual': self.analysis_results.get('time_to_fill', {}).get('average_days', 0),
                'unit': 'days',
                'status': 'BEHIND_TARGET'
            },
            'offer_acceptance_rate': {
                'target': 85,
                'actual': self.analysis_results.get('process_flows', {}).get('recruitment_funnel', {}).get('acceptance_rate', 0),
                'unit': '%',
                'status': 'MEETING_TARGET'
            },
            'process_compliance_rate': {
                'target': 95,
                'actual': self.analysis_results.get('compliance', {}).get('standard_flow_compliance', 0),
                'unit': '%',
                'status': 'BEHIND_TARGET'
            }
        }
        
        # Set status based on performance
        for kpi_name, kpi_data in kpis.items():
            if kpi_data['actual'] >= kpi_data['target']:
                kpi_data['status'] = 'MEETING_TARGET'
            elif kpi_data['actual'] >= kpi_data['target'] * 0.9:
                kpi_data['status'] = 'APPROACHING_TARGET'
            else:
                kpi_data['status'] = 'BEHIND_TARGET'
        
        self.analysis_results['kpi_dashboard'] = kpis
        return kpis
    
    def run_full_analysis(self):
        """Execute complete analysis pipeline"""
        print(">> Starting Hire to Retire Process Mining Analysis...")
        print("=" * 60)
        
        if not self.load_data():
            return False
        
        print(">> Calculating basic statistics...")
        self.basic_statistics()
        
        print(">> Analyzing Time to Fill KPI...")
        self.calculate_time_to_fill()
        
        print(">> Identifying performance bottlenecks...")
        self.analyze_bottlenecks()
        
        print(">> Analyzing process flows...")
        self.process_flow_analysis()
        
        print(">> Evaluating resource performance...")
        self.resource_performance_analysis()
        
        print(">> Checking compliance metrics...")
        self.compliance_analysis()
        
        print(">> Generating KPI dashboard...")
        self.generate_kpi_dashboard()
        
        print(">> Analysis complete!")
        return True
    
    def save_results(self, output_file):
        """Save analysis results to JSON file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.analysis_results, f, indent=2, default=str)
            print(f">> Results saved to {output_file}")
            return True
        except Exception as e:
            print(f">> Error saving results: {e}")
            return False
    
    def print_summary(self):
        """Print executive summary of findings"""
        print("\n" + "=" * 60)
        print(">> EXECUTIVE SUMMARY - KEY FINDINGS")
        print("=" * 60)
        
        basic = self.analysis_results.get('basic_stats', {})
        ttf = self.analysis_results.get('time_to_fill', {})
        flows = self.analysis_results.get('process_flows', {})
        bottlenecks = self.analysis_results.get('bottleneck_analysis', {})
        
        print(f">> Dataset Overview:")
        print(f"   * Total Cases: {basic.get('total_cases', 0):,}")
        print(f"   * Total Events: {basic.get('total_events', 0):,}")
        print(f"   * Date Range: {basic.get('date_range', {}).get('start', 'N/A')} to {basic.get('date_range', {}).get('end', 'N/A')}")
        
        print(f"\n>> Time to Fill Performance:")
        print(f"   * Average: {ttf.get('average_days', 0)} days (Target: 30 days)")
        print(f"   * Cases over target: {ttf.get('cases_over_target', 0)} ({ttf.get('percentage_over_target', 0)}%)")
        
        print(f"\n>> Recruitment Funnel:")
        funnel = flows.get('recruitment_funnel', {})
        print(f"   * Application Rate: {funnel.get('screening_pass_rate', 0)}%")
        print(f"   * Interview Rate: {funnel.get('interview_rate', 0)}%")
        print(f"   * Offer Acceptance: {funnel.get('acceptance_rate', 0)}%")
        
        print(f"\n>> Bottleneck Evidence:")
        if 'peter_analysis' in bottlenecks:
            print(f"   * Peter (Interviews): Handled {bottlenecks['peter_analysis'].get('cases_handled', 0)} cases")
        if 'david_analysis' in bottlenecks:
            print(f"   * David (Equipment): {bottlenecks['david_analysis'].get('percentage_of_workload', 0)}% of workload")
        if 'robert_analysis' in bottlenecks:
            print(f"   * Robert (Reviews): {bottlenecks['robert_analysis'].get('percentage_of_workload', 0)}% of workload")


def main():
    """Main execution function"""
    # Set file paths
    base_dir = r"C:\ReposMindzie\mindzie_process_data\Hire to Retire\src\output"
    csv_file = os.path.join(base_dir, "hire_to_retire_historical.csv")
    json_file = os.path.join(base_dir, "hire_to_retire_historical.json")
    results_file = os.path.join(base_dir, "analysis_results.json")
    
    # Check if files exist
    if not os.path.exists(csv_file):
        print(f">> CSV file not found: {csv_file}")
        return False
        
    if not os.path.exists(json_file):
        print(f">> JSON file not found: {json_file}")
        return False
    
    # Initialize analyzer
    analyzer = HireToRetireAnalyzer(csv_file, json_file)
    
    # Run analysis
    if analyzer.run_full_analysis():
        analyzer.save_results(results_file)
        analyzer.print_summary()
        
        print(f"\n>> Analysis complete! Results saved to:")
        print(f"   >> {results_file}")
        return True
    else:
        print(">> Analysis failed!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)