#!/usr/bin/env python3
"""
Detailed debug of STRIDE issue
"""

import requests
import json
import uuid
import time

BASE_URL = "https://flowmap-enhance.preview.emergentagent.com/api"

def detailed_stride_debug():
    session = requests.Session()
    
    # Create a diagram
    diagram_data = {
        "title": "Debug STRIDE Detailed Test",
        "description": "Detailed test diagram"
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
    
    # Add a simple node
    simple_node = {
        "id": f"webapp-{uuid.uuid4().hex[:8]}",
        "type": "Asset",
        "subtype": "WebApp",
        "label": "Test WebApp",
        "position": {"x": 100, "y": 100},
        "data": {"criticality": "High"}
    }
    
    print("2. Adding node to diagram...")
    diagram_data["nodes"] = [simple_node]
    diagram_data["edges"] = []
    
    update_response = session.put(f"{BASE_URL}/diagrams/{diagram_id}", json=diagram_data)
    print(f"   Update response: {update_response.status_code}")
    
    if update_response.status_code != 200:
        print(f"   Failed to update: {update_response.text}")
        return
    
    # Wait a moment
    time.sleep(1)
    
    # Verify diagram exists
    print("3. Verifying diagram exists...")
    get_response = session.get(f"{BASE_URL}/diagrams/{diagram_id}")
    print(f"   Get response: {get_response.status_code}")
    
    if get_response.status_code == 200:
        retrieved_data = get_response.json()
        print(f"   Retrieved diagram: {retrieved_data.get('title')}")
        print(f"   Nodes count: {len(retrieved_data.get('nodes', []))}")
        if retrieved_data.get('nodes'):
            print(f"   First node: {retrieved_data['nodes'][0]}")
    else:
        print(f"   Failed to retrieve: {get_response.text}")
        return
    
    # List all diagrams to see if it's there
    print("4. Listing all diagrams...")
    list_response = session.get(f"{BASE_URL}/diagrams")
    print(f"   List response: {list_response.status_code}")
    
    if list_response.status_code == 200:
        diagrams = list_response.json()
        print(f"   Total diagrams: {len(diagrams)}")
        found = False
        for diag in diagrams:
            if diag.get('id') == diagram_id:
                found = True
                print(f"   Found our diagram: {diag.get('title')}")
                break
        if not found:
            print(f"   Our diagram not found in list!")
    
    # Now try STRIDE analysis
    print("5. Testing STRIDE analysis...")
    stride_response = session.post(f"{BASE_URL}/diagrams/{diagram_id}/stride/analyze")
    print(f"   STRIDE response: {stride_response.status_code}")
    
    if stride_response.status_code == 200:
        stride_data = stride_response.json()
        print(f"   STRIDE success: {len(stride_data.get('threats', []))} threats found")
    else:
        try:
            error_data = stride_response.json()
            print(f"   STRIDE error: {error_data}")
        except:
            print(f"   STRIDE error text: {stride_response.text}")

if __name__ == "__main__":
    detailed_stride_debug()