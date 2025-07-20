import os
import json
from collections import Counter, defaultdict
from datetime import datetime

# Locate the Output directory relative to this script
script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, 'Output')
json_path = os.path.join(output_dir, 'alderaan_year_to_date.json')

with open(json_path, 'r') as f:
    data = json.load(f)

cases = data['cases']

# --- Basic Stats ---
total_cases = len(cases)
total_activities = sum(len(case['activities']) for case in cases)
print(f"Total cases: {total_cases}")
print(f"Total activities: {total_activities}")

# --- Per Day Stats ---
cases_per_day = defaultdict(int)
activities_per_day = defaultdict(int)
for case in cases:
    if case['activities']:
        # Use the date of the first activity as the case's day
        day = case['activities'][0]['ActivityTime'][:10]
        cases_per_day[day] += 1
        activities_per_day[day] += len(case['activities'])

print("\nCases per day (sample):")
for day in sorted(cases_per_day.keys())[:7]:
    print(f"  {day}: {cases_per_day[day]} cases, {activities_per_day[day]} activities")
print("  ...")

# --- Per Week Stats ---
cases_per_week = defaultdict(int)
activities_per_week = defaultdict(int)
for day in cases_per_day:
    dt = datetime.strptime(day, "%Y-%m-%d")
    year_week = dt.strftime("%Y-W%U")
    cases_per_week[year_week] += cases_per_day[day]
    activities_per_week[year_week] += activities_per_day[day]

print("\nCases per week (sample):")
for week in sorted(cases_per_week.keys())[:5]:
    print(f"  {week}: {cases_per_week[week]} cases, {activities_per_week[week]} activities")
print("  ...")

# --- Per Month Stats ---
cases_per_month = defaultdict(int)
activities_per_month = defaultdict(int)
for day in cases_per_day:
    month = day[:7]
    cases_per_month[month] += cases_per_day[day]
    activities_per_month[month] += activities_per_day[day]

print("\nCases per month:")
for month in sorted(cases_per_month.keys()):
    print(f"  {month}: {cases_per_month[month]} cases, {activities_per_month[month]} activities")

# --- Busiest Day, Week, Month ---
busiest_day = max(cases_per_day.items(), key=lambda x: x[1])
busiest_week = max(cases_per_week.items(), key=lambda x: x[1])
busiest_month = max(cases_per_month.items(), key=lambda x: x[1])
print(f"\nBusiest day: {busiest_day[0]} ({busiest_day[1]} cases)")
print(f"Busiest week: {busiest_week[0]} ({busiest_week[1]} cases)")
print(f"Busiest month: {busiest_month[0]} ({busiest_month[1]} cases)")

# --- Breakdown of Last Activity Types ---
last_activity_counter = Counter()
for case in cases:
    if case['activities']:
        last_act = case['activities'][-1]['ActivityName']
        last_activity_counter[last_act] += 1
print("\nBreakdown by Last Activity:")
for activity, count in last_activity_counter.most_common():
    print(f"  {activity}: {count}")

# --- Ready for further expansion: anomaly detection, resource stats, etc. --- 