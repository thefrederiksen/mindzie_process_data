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
        # Print key fields if present
        for key in ["datasetId", "datasetName", "rowCount", "skippedRows", "rowIssues", "warnings", "message"]:
            if key in result:
                print(f"{key.replace('_', ' ').title()}: {result[key]}")
        # Print row issues in detail if present
        if "rowIssues" in result and result["rowIssues"]:
            print("Row Issues:")
            for issue in result["rowIssues"]:
                print(f"  - {issue}")
        # Print warnings if present
        if "warnings" in result and result["warnings"]:
            print("Warnings:")
            for warning in result["warnings"]:
                print(f"  - {warning}")
        # Print full response for debugging
        print("Full API response:")
        print(json.dumps(result, indent=2))
    else:
        print("API returned:", result)

def create_data_set(csv_path, dataset_name, tenant_id, project_id, api_key):
    """Create a new dataset in Mindzie Studio"""
    url = f"{API_BASE_URL}/api/{tenant_id}/{project_id}/Dataset/csv"
    
    # Open the CSV file
    with open(csv_path, 'rb') as f:
        files = {'file': (os.path.basename(csv_path), f, 'text/csv')}
        
        # Configure dataset mapping for HR data
        data = {
            'datasetName': dataset_name,
            'caseIdColumn': 'CaseId',
            'activityNameColumn': 'ActivityName',
            'activityTimeColumn': 'ActivityTime',
            'resourceColumn': 'PerformedBy',  # Using PerformedBy as resource
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
    """Update an existing dataset in Mindzie Studio"""
    url = f"{API_BASE_URL}/api/{tenant_id}/{project_id}/Dataset/{dataset_id}/csv"
    
    # Open the CSV file
    with open(csv_path, 'rb') as f:
        files = {'file': (os.path.basename(csv_path), f, 'text/csv')}
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
    """Get all datasets from Mindzie Studio project"""
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
    print("Generating Hire to Retire historical event log...")
    try:
        subprocess.run(['python', os.path.join(os.path.dirname(__file__), 'historical_event_log.py')], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error generating event log: {e}")
        return
    
    # Load .env and get configuration
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if not os.path.exists(env_path):
        print(f"Error: .env file not found at {env_path}")
        print("Please create a .env file with TENANT_ID, PROJECT_ID, and API_KEY")
        return
    
    load_dotenv(env_path)
    tenant_id = os.getenv('TENANT_ID')
    project_id = os.getenv('PROJECT_ID')
    api_key = os.getenv('API_KEY')
    
    # Validate environment variables
    if not all([tenant_id, project_id, api_key]):
        print("Error: Missing required environment variables.")
        print("Please ensure .env file contains TENANT_ID, PROJECT_ID, and API_KEY")
        return
    
    print(f"Tenant ID: {tenant_id}")
    print(f"Project ID: {project_id}")
    print("API Key: [REDACTED]")
    
    # Define paths and dataset name
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    csv_path = os.path.join(output_dir, 'hire_to_retire_year_to_date.csv')
    dataset_name = 'Hire to Retire - Historical'
    
    # Check if CSV file exists
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        print("Please run historical_event_log.py first to generate the data")
        return
    
    # Get file size for information
    file_size = os.path.getsize(csv_path) / (1024 * 1024)  # Convert to MB
    print(f"CSV file size: {file_size:.2f} MB")
    
    # Get existing datasets
    print("\nFetching existing datasets...")
    datasets = get_all_datasets(tenant_id, project_id, api_key)
    print("Datasets response type:", type(datasets))
    
    # Extract the list of datasets from the correct key
    if isinstance(datasets, dict):
        for key in ['Items', 'datasets', 'items', 'data']:
            if key in datasets:
                datasets = datasets[key]
                break
    
    if not isinstance(datasets, list):
        print("Unexpected datasets response format. Treating as empty list.")
        datasets = []
    
    print(f"Found {len(datasets)} existing datasets")
    
    # Check if dataset already exists
    dataset = next((d for d in datasets if isinstance(d, dict) and d.get('datasetName') == dataset_name), None)
    
    if dataset:
        print(f"\nDataset '{dataset_name}' exists with ID: {dataset['datasetId']}")
        print("Updating existing dataset...")
        result = update_data_set(dataset['datasetId'], csv_path, tenant_id, project_id, api_key)
        print_result_report(result, "Update")
    else:
        print(f"\nDataset '{dataset_name}' does not exist. Creating new dataset...")
        result = create_data_set(csv_path, dataset_name, tenant_id, project_id, api_key)
        print_result_report(result, "Create")
    
    # Additional information
    if result and 'datasetId' in result:
        print(f"\n✅ Dataset successfully uploaded!")
        print(f"Dataset ID: {result['datasetId']}")
        print(f"Dataset Name: {dataset_name}")
        print(f"Row Count: {result.get('rowCount', 'Unknown')}")
        print("\nNext steps:")
        print("1. Open Mindzie Studio")
        print("2. Navigate to your project")
        print("3. Go to Datasets section")
        print(f"4. Look for '{dataset_name}' dataset")
        print("5. Create process models and analyses")

if __name__ == "__main__":
    main()