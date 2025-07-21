import os
import requests
from dotenv import load_dotenv
import json
import subprocess

API_BASE_URL = 'https://www.mindziestudio.com'  # No trailing slash

HEADERS = {}

def print_result_report(result, action):
    print(f"\n=== {action} Dataset Report ===")
    if not result:
        print("No result returned from API.")
        return
    if isinstance(result, dict):
        for key in ["datasetId", "datasetName", "rowCount", "skippedRows", "rowIssues", "warnings", "message"]:
            if key in result:
                print(f"{key.replace('_', ' ').title()}: {result[key]}")
        if "rowIssues" in result and result["rowIssues"]:
            print("Row Issues:")
            for issue in result["rowIssues"]:
                print(f"  - {issue}")
        if "warnings" in result and result["warnings"]:
            print("Warnings:")
            for warning in result["warnings"]:
                print(f"  - {warning}")
        print("Full API response:")
        print(json.dumps(result, indent=2))
    else:
        print("API returned:", result)

def create_data_set(csv_path, dataset_name, tenant_id, project_id, api_key):
    url = f"{API_BASE_URL}/api/{tenant_id}/{project_id}/Dataset/csv"
    files = {'file': (os.path.basename(csv_path), open(csv_path, 'rb'), 'text/csv')}
    data = {
        'datasetName': dataset_name,
        'caseIdColumn': 'CaseId',
        'activityNameColumn': 'ActivityName',
        'activityTimeColumn': 'ActivityTime',
        'resourceColumn': 'Resource',
        'cultureInfo': 'en-US'
    }
    headers = {'Authorization': f'Bearer {api_key}'}
    try:
        response = requests.post(url, headers=headers, files=files, data=data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error creating dataset: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print("Response content:", e.response.text)
        return None

def update_data_set(dataset_id, csv_path, tenant_id, project_id, api_key):
    url = f"{API_BASE_URL}/api/{tenant_id}/{project_id}/Dataset/{dataset_id}/csv"
    files = {'file': (os.path.basename(csv_path), open(csv_path, 'rb'), 'text/csv')}
    data = {'cultureInfo': 'en-US'}
    headers = {'Authorization': f'Bearer {api_key}'}
    try:
        response = requests.put(url, headers=headers, files=files, data=data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error updating dataset: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print("Response content:", e.response.text)
        return None

def get_all_datasets(tenant_id, project_id, api_key):
    url = f"{API_BASE_URL}/api/{tenant_id}/{project_id}/Dataset"
    headers = {'Authorization': f'Bearer {api_key}'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()  # May be a dict with 'Items' key
    except Exception as e:
        print(f"Error fetching datasets: {e}")
        return []

def main():
    # Generate the historical event log before uploading
    print("Generating historical event log...")
    subprocess.run(['python', os.path.join(os.path.dirname(__file__), 'historical_event_log.py')], check=True)
    # Load .env and get keys
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
    tenant_id = os.getenv('TENANT_ID')
    project_id = os.getenv('PROJECT_ID')
    api_key = os.getenv('API_KEY')
    print(f"Tenant ID: {tenant_id}")
    print(f"Project ID: {project_id}")
    output_dir = os.path.join(os.path.dirname(__file__), 'Output')
    csv_path = os.path.join(output_dir, 'alderaan_year_to_date.csv')
    dataset_name = 'Alderaan Year to Date'
    datasets = get_all_datasets(tenant_id, project_id, api_key)
    print("Datasets response:", datasets)  # Debug print

    # Extract the list of datasets from the correct key
    if isinstance(datasets, dict):
        for key in ['Items', 'datasets', 'items', 'data']:
            if key in datasets:
                datasets = datasets[key]
                break

    if not isinstance(datasets, list):
        print("Unexpected datasets response format.")
        datasets = []

    # Use 'datasetName' for comparison
    dataset = next((d for d in datasets if isinstance(d, dict) and d.get('datasetName') == dataset_name), None)
    if dataset:
        print(f"Dataset '{dataset_name}' exists. Updating dataset...")
        result = update_data_set(dataset['datasetId'], csv_path, tenant_id, project_id, api_key)
        print_result_report(result, "Update")
    else:
        print(f"Dataset '{dataset_name}' does not exist. Creating new dataset...")
        result = create_data_set(csv_path, dataset_name, tenant_id, project_id, api_key)
        print_result_report(result, "Create")

if __name__ == "__main__":
    main() 