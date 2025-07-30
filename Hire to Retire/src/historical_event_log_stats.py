import json
import os
from datetime import datetime
from collections import Counter, defaultdict
import statistics

def analyze_process_problems(json_path):
    """Analyze the dataset for injected process problems"""
    
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    cases = data['cases']
    print(f"\n=== Hire to Retire Process Analysis ===")
    print(f"Total Cases: {len(cases)}")
    
    # Count different types of cases
    job_posted = len([c for c in cases if any(a['ActivityName'] == 'Job Posted' for a in c['activities'])])
    app_received = len([c for c in cases if any(a['ActivityName'] == 'Application Received' for a in c['activities'])])
    app_rejected = len([c for c in cases if any(a['ActivityName'] == 'Application Rejected' for a in c['activities'])])
    interviewed = len([c for c in cases if any(a['ActivityName'] == 'Interview Completed' for a in c['activities'])])
    interview_failed = len([c for c in cases if any(a['ActivityName'] == 'Interview Failed' for a in c['activities'])])
    offer_extended = len([c for c in cases if any(a['ActivityName'] == 'Offer Extended' for a in c['activities'])])
    offer_accepted = len([c for c in cases if any(a['ActivityName'] == 'Offer Accepted' for a in c['activities'])])
    offer_rejected = len([c for c in cases if any(a['ActivityName'] == 'Offer Rejected' for a in c['activities'])])
    
    print(f"\n=== Recruitment Funnel ===")
    print(f"Jobs Posted: {job_posted}")
    print(f"Applications Received: {app_received}")
    print(f"Applications Rejected: {app_rejected} ({app_rejected/app_received*100:.1f}%)")
    print(f"Interviews Completed: {interviewed} ({interviewed/app_received*100:.1f}% of applications)")
    print(f"Interviews Failed: {interview_failed} ({interview_failed/interviewed*100:.1f}% of interviewed)")
    print(f"Offers Extended: {offer_extended} ({offer_extended/interviewed*100:.1f}% of interviewed)")
    print(f"Offers Accepted: {offer_accepted} ({offer_accepted/offer_extended*100:.1f}% acceptance rate)")
    print(f"Offers Rejected: {offer_rejected} ({offer_rejected/offer_extended*100:.1f}% rejection rate)")
    
    # Ghost jobs analysis
    no_applications = job_posted - app_received
    stalled_after_posting = 0
    for case in cases:
        activities = [a['ActivityName'] for a in case['activities']]
        if 'Job Posted' in activities and len(activities) == 1:
            stalled_after_posting += 1
    
    print(f"\n=== Ghost Jobs & Stalled Processes ===")
    print(f"Jobs with no applications: {no_applications}")
    print(f"Jobs stalled after posting: {stalled_after_posting}")
    print(f"Total ghost jobs: {stalled_after_posting} ({stalled_after_posting/job_posted*100:.1f}% of posted jobs)")
    
    # Problem metrics
    problems = {
        'extended_time_to_fill': [],
        'interview_delays': [],
        'equipment_delays': [],
        'performance_review_delays': [],
        'leave_approval_delays': [],
        'promotion_delays': [],
        'short_notice_resignations': [],
        'early_turnover': [],
        'probation_failures': 0
    }
    
    # Process times
    recruitment_times = []
    onboarding_times = []
    
    for case in cases:
        activities = case['activities']
        activity_dict = {a['ActivityName']: datetime.fromisoformat(a['ActivityTime'].replace('Z', '')) 
                        for a in activities}
        
        # Recruitment time (Job Posted to Offer Accepted)
        if 'Job Posted' in activity_dict and 'Offer Accepted' in activity_dict:
            recruitment_time = (activity_dict['Offer Accepted'] - activity_dict['Job Posted']).days
            recruitment_times.append(recruitment_time)
            if recruitment_time > 90:  # 3+ months
                problems['extended_time_to_fill'].append(case['CaseId'])
        
        # Interview scheduling delays
        if 'Application Received' in activity_dict and 'Interview Completed' in activity_dict:
            interview_wait = (activity_dict['Interview Completed'] - activity_dict['Application Received']).days
            if interview_wait > 30:  # More than 30 days
                problems['interview_delays'].append(case['CaseId'])
        
        # Equipment delays
        if 'Onboarding Started' in activity_dict and 'Equipment Assigned' in activity_dict:
            equipment_wait = (activity_dict['Equipment Assigned'] - activity_dict['Onboarding Started']).days
            if equipment_wait > 3:  # More than 3 days
                problems['equipment_delays'].append(case['CaseId'])
                
        # Performance review delays
        perf_reviews = [a for a in activities if a['ActivityName'] == 'Performance Review']
        if len(perf_reviews) > 1:
            for i in range(1, len(perf_reviews)):
                gap = (datetime.fromisoformat(perf_reviews[i]['ActivityTime'].replace('Z', '')) - 
                      datetime.fromisoformat(perf_reviews[i-1]['ActivityTime'].replace('Z', ''))).days
                if gap > 395:  # More than 13 months
                    problems['performance_review_delays'].append(case['CaseId'])
                    break
        
        # Leave approval delays
        leave_pairs = []
        for i, activity in enumerate(activities):
            if activity['ActivityName'] == 'Leave Requested':
                # Find corresponding approval
                for j in range(i+1, len(activities)):
                    if activities[j]['ActivityName'] == 'Leave Approved':
                        request_time = datetime.fromisoformat(activity['ActivityTime'].replace('Z', ''))
                        approval_time = datetime.fromisoformat(activities[j]['ActivityTime'].replace('Z', ''))
                        delay = (approval_time - request_time).days
                        if delay > 3:
                            problems['leave_approval_delays'].append(case['CaseId'])
                        break
        
        # Promotion delays
        promotion_activities = [a for a in activities if a['ActivityName'] == 'Promotion Approved']
        perf_review_activities = [a for a in activities if a['ActivityName'] == 'Performance Review']
        
        for promo in promotion_activities:
            promo_time = datetime.fromisoformat(promo['ActivityTime'].replace('Z', ''))
            # Find most recent performance review before promotion
            recent_review = None
            for review in perf_review_activities:
                review_time = datetime.fromisoformat(review['ActivityTime'].replace('Z', ''))
                if review_time < promo_time:
                    recent_review = review_time
            
            if recent_review and (promo_time - recent_review).days > 90:  # More than 3 months
                problems['promotion_delays'].append(case['CaseId'])
        
        # Short notice resignations
        if 'Resignation Submitted' in activity_dict and 'Employment Ended' in activity_dict:
            notice_period = (activity_dict['Employment Ended'] - activity_dict['Resignation Submitted']).days
            if notice_period < 14:  # Less than 2 weeks
                problems['short_notice_resignations'].append(case['CaseId'])
        
        # Early turnover / probation failures
        if 'Probation Failed' in activity_dict:
            problems['probation_failures'] += 1
            problems['early_turnover'].append(case['CaseId'])
        elif 'Onboarding Started' in activity_dict and 'Employment Ended' in activity_dict:
            tenure = (activity_dict['Employment Ended'] - activity_dict['Onboarding Started']).days
            if tenure < 90:  # Less than 90 days
                problems['early_turnover'].append(case['CaseId'])
    
    # Print analysis results
    print("\n=== Process Problems Detected ===")
    
    # Calculate percentages based on relevant populations
    recruited_cases = [c for c in cases if any(a['ActivityName'] == 'Application Received' for a in c['activities'])]
    interviewed_cases = [c for c in cases if any(a['ActivityName'] == 'Interview Completed' for a in c['activities'])]
    hired_cases = [c for c in cases if any(a['ActivityName'] == 'Onboarding Started' for a in c['activities'])]
    resigned_cases = [c for c in cases if any(a['ActivityName'] == 'Resignation Submitted' for a in c['activities'])]
    
    print(f"\n=== Population Sizes ===")
    print(f"Total Cases: {len(cases)}")
    print(f"Recruited (received application): {len(recruited_cases)}")
    print(f"Interviewed: {len(interviewed_cases)}")
    print(f"Hired: {len(hired_cases)}")
    print(f"Resigned: {len(resigned_cases)}")
    
    print(f"\nRecruitment Problems:")
    print(f"  Extended Time-to-Fill (>90 days): {len(problems['extended_time_to_fill'])} cases ({len(problems['extended_time_to_fill'])/len(hired_cases)*100:.1f}% of hired)")
    print(f"  Interview Scheduling Delays (>30 days): {len(problems['interview_delays'])} cases ({len(problems['interview_delays'])/len(interviewed_cases)*100:.1f}% of interviewed)")
    
    print(f"\nOnboarding Problems:")
    print(f"  Equipment Delays (>3 days): {len(problems['equipment_delays'])} cases ({len(problems['equipment_delays'])/len(hired_cases)*100:.1f}% of hired)")
    print(f"  Early Turnover (<90 days): {len(problems['early_turnover'])} cases ({len(problems['early_turnover'])/len(hired_cases)*100:.1f}% of hired)")
    print(f"  Probation Failures: {problems['probation_failures']} cases ({problems['probation_failures']/len(hired_cases)*100:.1f}% of hired)")
    
    # Count employees with reviews and leaves
    employees_with_reviews = [c for c in hired_cases if any(a['ActivityName'] == 'Performance Review' for a in c['activities'])]
    employees_with_leaves = [c for c in hired_cases if any(a['ActivityName'] == 'Leave Requested' for a in c['activities'])]
    employees_with_promotions = [c for c in hired_cases if any(a['ActivityName'] == 'Promotion Approved' for a in c['activities'])]
    
    print(f"\nEmployment Lifecycle Problems:")
    print(f"  Performance Review Delays (>13 months): {len(problems['performance_review_delays'])} cases")
    if employees_with_reviews:
        print(f"    - {len(employees_with_reviews)} employees had reviews")
    print(f"  Leave Approval Delays (>3 days): {len(problems['leave_approval_delays'])} cases")
    if employees_with_leaves:
        print(f"    - {len(employees_with_leaves)} employees requested leave")
    print(f"  Promotion Processing Delays (>3 months): {len(problems['promotion_delays'])} cases")
    if employees_with_promotions:
        print(f"    - {len(employees_with_promotions)} employees were promoted")
    
    print(f"\nExit Process Problems:")
    print(f"  Short Notice Resignations (<14 days): {len(problems['short_notice_resignations'])} cases ({len(problems['short_notice_resignations'])/len(resigned_cases)*100:.1f}% of resignations)")
    
    # Recruitment funnel metrics
    if recruitment_times:
        print(f"\n=== Recruitment Metrics ===")
        print(f"Average Time-to-Fill: {statistics.mean(recruitment_times):.1f} days")
        print(f"Median Time-to-Fill: {statistics.median(recruitment_times):.1f} days")
        print(f"Max Time-to-Fill: {max(recruitment_times)} days")
        print(f"Min Time-to-Fill: {min(recruitment_times)} days")
    
    # Activity distribution by performer
    performer_counts = Counter()
    system_counts = Counter()
    
    for case in cases:
        for activity in case['activities']:
            performer_counts[activity['PerformedBy']] += 1
            system_counts[activity['SystemUsed']] += 1
    
    print(f"\n=== Workload Distribution ===")
    print("By Organization:")
    for org, count in sorted(performer_counts.items()):
        print(f"  {org}: {count} activities ({count/sum(performer_counts.values())*100:.1f}%)")
    
    print("\nBy System:")
    for system, count in sorted(system_counts.items()):
        print(f"  {system}: {count} activities ({count/sum(system_counts.values())*100:.1f}%)")
    
    # Data quality analysis
    print(f"\n=== Data Quality Issues ===")
    missing_dept = len([c for c in cases if c.get('Department') is None])
    missing_location = len([c for c in cases if c.get('Location') is None])
    missing_manager = len([c for c in cases if c.get('HiringManager') is None])
    
    print(f"Missing Department: {missing_dept} cases ({missing_dept/len(cases)*100:.1f}%)")
    print(f"Missing Location: {missing_location} cases ({missing_location/len(cases)*100:.1f}%)")
    print(f"Missing Hiring Manager: {missing_manager} cases ({missing_manager/len(cases)*100:.1f}%)")
    print(f"Total with missing data: {len([c for c in cases if c.get('Department') is None or c.get('Location') is None or c.get('HiringManager') is None])} cases")

def main():
    src_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(src_dir, 'output', 'hire_to_retire_year_to_date.json')
    
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found. Please run historical_event_log.py first.")
        return
    
    analyze_process_problems(json_path)

if __name__ == "__main__":
    main()