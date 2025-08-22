#!/usr/bin/env python3
"""
Upload Hire to Retire historical dataset to Mindzie Studio
"""

import os
import json
import requests
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Configuration from .env file
TENANT_ID = os.getenv('TENANT_ID')
PROJECT_ID = os.getenv('PROJECT_ID')
API_KEY = os.getenv('API_KEY')

if not all([TENANT_ID, PROJECT_ID, API_KEY]):
    print("Error: Missing required environment variables.")
    print("Please create a .env file with TENANT_ID, PROJECT_ID, and API_KEY")
    exit(1)

# API configuration
BASE_URL = f"https://api.mindzie.com/v1/tenants/{TENANT_ID}/projects/{PROJECT_ID}"
HEADERS = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

def upload_dataset(file_path, dataset_name, dataset_type="historical"):
    """Upload a dataset to Mindzie Studio"""
    
    print(f"Uploading {dataset_name}...")
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found")
        return False
    
    # Load the data
    if file_path.endswith('.json'):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    elif file_path.endswith('.csv'):
        import csv
        data = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
    else:
        print(f"Error: Unsupported file format")
        return False
    
    # Prepare the upload payload
    payload = {
        "name": dataset_name,
        "type": dataset_type,
        "description": f"Hire to Retire {dataset_type} dataset - Complete employee lifecycle from recruitment to exit",
        "data_format": "event_log",
        "timestamp": datetime.now().isoformat(),
        "record_count": len(data),
        "data": data
    }
    
    # Make the API request
    try:
        response = requests.post(
            f"{BASE_URL}/datasets",
            headers=HEADERS,
            json=payload,
            timeout=300  # 5 minute timeout for large datasets
        )
        
        if response.status_code == 201:
            result = response.json()
            print(f"✓ Successfully uploaded {dataset_name}")
            print(f"  Dataset ID: {result.get('dataset_id')}")
            print(f"  Records uploaded: {result.get('record_count')}")
            return True
        else:
            print(f"✗ Failed to upload {dataset_name}")
            print(f"  Status code: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"✗ Upload timed out for {dataset_name}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Error uploading {dataset_name}: {str(e)}")
        return False

def check_connection():
    """Check connection to Mindzie API"""
    print("Checking connection to Mindzie API...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/info",
            headers=HEADERS,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✓ Successfully connected to Mindzie API")
            project_info = response.json()
            print(f"  Project: {project_info.get('name', 'Unknown')}")
            print(f"  Tenant: {project_info.get('tenant_name', 'Unknown')}")
            return True
        else:
            print("✗ Failed to connect to Mindzie API")
            print(f"  Status code: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Error connecting to Mindzie API: {str(e)}")
        return False

def main():
    """Main upload function"""
    print("=" * 60)
    print("Hire to Retire Historical Dataset Upload")
    print("=" * 60)
    
    # Check connection first
    if not check_connection():
        print("\nPlease check your .env configuration and network connection")
        return
    
    print("\nStarting dataset upload...")
    
    # Upload JSON dataset (preferred format)
    json_file = "output/hire_to_retire_historical.json"
    if os.path.exists(json_file):
        success = upload_dataset(
            json_file,
            "Hire to Retire Historical (JSON)",
            "historical"
        )
        if not success:
            print("Warning: JSON upload failed, trying CSV...")
    
    # Upload CSV dataset as backup
    csv_file = "output/hire_to_retire_historical.csv"
    if os.path.exists(csv_file):
        upload_dataset(
            csv_file,
            "Hire to Retire Historical (CSV)",
            "historical"
        )
    
    print("\n" + "=" * 60)
    print("Upload process completed")
    print("=" * 60)
    
    print("\nNext steps:")
    print("1. Log into Mindzie Studio")
    print("2. Navigate to your project")
    print("3. Check the Datasets section to verify upload")
    print("4. Create process mining analyses and dashboards")

if __name__ == "__main__":
    main()