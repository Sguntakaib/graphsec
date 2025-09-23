#!/usr/bin/env python3
"""
Debug STRIDE issue - check if diagram exists in database
"""

import requests
import json

BASE_URL = "https://questionnaire-sync.preview.emergentagent.com/api"

def test_diagram_creation_and_retrieval():
    session = requests.Session()
    
    # Create a simple diagram
    diagram_data = {
        "title": "Debug STRIDE Test",
        "description": "Simple test diagram"
    }
    
    print("Creating diagram...")
    response = session.post(f"{BASE_URL}/diagrams", json=diagram_data)
    print(f"Create response: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        diagram_id = data.get("id")
        print(f"Created diagram ID: {diagram_id}")
        
        # Try to retrieve it
        print("Retrieving diagram...")
        get_response = session.get(f"{BASE_URL}/diagrams/{diagram_id}")
        print(f"Get response: {get_response.status_code}")
        
        if get_response.status_code == 200:
            retrieved_data = get_response.json()
            print(f"Retrieved diagram: {retrieved_data.get('title')}")
            
            # Now try STRIDE analysis
            print("Testing STRIDE analysis...")
            stride_response = session.post(f"{BASE_URL}/diagrams/{diagram_id}/stride/analyze")
            print(f"STRIDE response: {stride_response.status_code}")
            
            if stride_response.status_code != 200:
                try:
                    error_data = stride_response.json()
                    print(f"STRIDE error: {error_data}")
                except:
                    print(f"STRIDE error text: {stride_response.text}")
        else:
            print(f"Failed to retrieve diagram: {get_response.text}")
    else:
        print(f"Failed to create diagram: {response.text}")

if __name__ == "__main__":
    test_diagram_creation_and_retrieval()