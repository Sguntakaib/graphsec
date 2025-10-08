#!/usr/bin/env python3
"""
Simple STRIDE debug - test without updating diagram
"""

import requests
import json

BASE_URL = "https://flowmap-enhance.preview.emergentagent.com/api"

def simple_stride_debug():
    session = requests.Session()
    
    # Create a diagram
    diagram_data = {
        "title": "Simple STRIDE Test",
        "description": "Simple test without updates"
    }
    
    print("1. Creating diagram...")
    response = session.post(f"{BASE_URL}/diagrams", json=diagram_data)
    print(f"   Create response: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   Failed to create: {response.text}")
        return
    
    data = response.json()
    diagram_id = data.get("id")
    print(f"   Created diagram ID: {diagram_id}")
    
    # Verify diagram exists immediately
    print("2. Verifying diagram exists...")
    get_response = session.get(f"{BASE_URL}/diagrams/{diagram_id}")
    print(f"   Get response: {get_response.status_code}")
    
    if get_response.status_code == 200:
        retrieved_data = get_response.json()
        print(f"   Retrieved diagram: {retrieved_data.get('title')}")
    else:
        print(f"   Failed to retrieve: {get_response.text}")
        return
    
    # Try STRIDE analysis on empty diagram
    print("3. Testing STRIDE analysis on empty diagram...")
    stride_response = session.post(f"{BASE_URL}/diagrams/{diagram_id}/stride/analyze")
    print(f"   STRIDE response: {stride_response.status_code}")
    
    if stride_response.status_code == 200:
        stride_data = stride_response.json()
        print(f"   STRIDE success: {len(stride_data.get('threats', []))} threats found")
        print(f"   Analysis summary: {stride_data.get('analysis_summary', {})}")
    else:
        try:
            error_data = stride_response.json()
            print(f"   STRIDE error: {error_data}")
        except:
            print(f"   STRIDE error text: {stride_response.text}")

if __name__ == "__main__":
    simple_stride_debug()