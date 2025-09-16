#!/usr/bin/env python3
"""
Critical Phase 1 Core Loop Endpoint Tests
Tests the 4 specific endpoints mentioned in the review request with exact data structures
"""

import requests
import json
import sys

# Use the production URL from review request
BASE_URL = "https://questionnaire-debug.preview.emergentagent.com/api"

def test_endpoint_1_questionnaire_complete():
    """
    ENDPOINT 1: POST /api/questionnaires/{node_subtype}/complete
    Test with WebApp subtype using exact data structure from review request
    """
    print("🔍 ENDPOINT 1: POST /api/questionnaires/WebApp/complete")
    
    # Use exact data structure from review request
    test_data = {
        "responses": {
            "authentication_method": "oauth2",
            "encryption_enabled": True,
            "input_validation": "comprehensive"
        },
        "business_context": {
            "criticality": "high", 
            "data_classification": "confidential"
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/questionnaires/WebApp/complete",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200 or response.status_code == 201:
            data = response.json()
            print(f"   ✅ SUCCESS: HTTP {response.status_code} with completion response")
            print(f"   Response keys: {list(data.keys())}")
            return True
        elif response.status_code == 400:
            error_text = response.text
            if "questionnaire_responses are required" in error_text:
                print(f"   ❌ FAILED: HTTP 400 'questionnaire_responses are required' - parameter structure issue")
            else:
                print(f"   ❌ FAILED: HTTP 400 - {error_text}")
            return False
        elif response.status_code == 500:
            error_text = response.text
            if "diagram_id and node_id are required" in error_text:
                print(f"   ❌ FAILED: HTTP 500 'diagram_id and node_id are required' - not standalone")
            else:
                print(f"   ❌ FAILED: HTTP 500 - {error_text}")
            return False
        else:
            print(f"   ❌ FAILED: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ FAILED: Connection error - {str(e)}")
        return False

def test_endpoint_2_questionnaire_get():
    """
    ENDPOINT 2: GET /api/questionnaires/{node_subtype}
    Test with WebApp to verify security_branches field presence
    """
    print("🔍 ENDPOINT 2: GET /api/questionnaires/WebApp")
    
    try:
        response = requests.get(f"{BASE_URL}/questionnaires/WebApp")
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response keys: {list(data.keys())}")
            
            # Check for security_branches field specifically
            if "security_branches" in data:
                security_branches = data.get("security_branches", [])
                print(f"   ✅ SUCCESS: HTTP 200 with security_branches field ({len(security_branches)} branches)")
                return True
            else:
                print(f"   ❌ FAILED: Missing security_branches field, only has: {list(data.keys())}")
                return False
        else:
            print(f"   ❌ FAILED: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ FAILED: Connection error - {str(e)}")
        return False

def test_endpoint_3_simulate():
    """
    ENDPOINT 3: POST /api/simulate
    Test standalone simulation with nodes/edges data
    """
    print("🔍 ENDPOINT 3: POST /api/simulate")
    
    # Sample data with nodes and edges arrays
    test_data = {
        "nodes": [
            {
                "id": "webapp-1",
                "type": "Asset",
                "subtype": "WebApp",
                "label": "Customer Portal",
                "security_attributes": {
                    "authentication": "oauth2",
                    "encryption": "tls1.3",
                    "input_validation": "comprehensive"
                }
            },
            {
                "id": "db-1", 
                "type": "Asset",
                "subtype": "Database",
                "label": "Customer Database",
                "security_attributes": {
                    "encryption_at_rest": True,
                    "access_control": "rbac"
                }
            },
            {
                "id": "attacker-1",
                "type": "Actor",
                "subtype": "ExternalAttacker",
                "label": "External Threat Actor"
            }
        ],
        "edges": [
            {
                "id": "edge-1",
                "source": "attacker-1",
                "target": "webapp-1",
                "type": "attack",
                "label": "Initial Access"
            },
            {
                "id": "edge-2", 
                "source": "webapp-1",
                "target": "db-1",
                "type": "attack",
                "label": "Data Access"
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/simulate",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response keys: {list(data.keys())}")
            
            # Check for ALL required fields from review request
            required_fields = ["simulation_id", "attack_paths", "risk_analysis", "mitre_techniques", "recommendations"]
            missing_fields = [f for f in required_fields if f not in data]
            
            if not missing_fields:
                print(f"   ✅ SUCCESS: HTTP 200 with all required fields: {required_fields}")
                return True
            else:
                print(f"   ❌ FAILED: Missing required fields: {missing_fields}")
                return False
        else:
            print(f"   ❌ FAILED: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ FAILED: Connection error - {str(e)}")
        return False

def test_endpoint_4_rules_evaluate():
    """
    ENDPOINT 4: POST /api/rules/evaluate
    Test standalone rule evaluation
    """
    print("🔍 ENDPOINT 4: POST /api/rules/evaluate")
    
    # Sample nodes/edges data structure
    test_data = {
        "nodes": [
            {
                "id": "webapp-1",
                "type": "Asset", 
                "subtype": "WebApp",
                "label": "Customer Portal",
                "security_attributes": {
                    "authentication": "basic",
                    "encryption": "none",
                    "input_validation": "minimal"
                }
            },
            {
                "id": "db-1",
                "type": "Asset",
                "subtype": "Database", 
                "label": "Customer Database",
                "security_attributes": {
                    "encryption_at_rest": False,
                    "access_control": "weak"
                }
            }
        ],
        "edges": [
            {
                "id": "edge-1",
                "source": "webapp-1",
                "target": "db-1",
                "type": "connection",
                "label": "Database Access"
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/rules/evaluate",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ SUCCESS: HTTP 200 response")
            print(f"   Response keys: {list(data.keys())}")
            return True
        elif response.status_code == 500:
            error_text = response.text
            if "RuleEvaluationResult object has no attribute category" in error_text:
                print(f"   ❌ FAILED: HTTP 500 'RuleEvaluationResult object has no attribute category' - implementation error")
            else:
                print(f"   ❌ FAILED: HTTP 500 - {error_text}")
            return False
        else:
            print(f"   ❌ FAILED: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ FAILED: Connection error - {str(e)}")
        return False

def main():
    """Run all 4 critical endpoint tests"""
    print("🎯 CRITICAL PHASE 1 CORE LOOP ENDPOINT VERIFICATION")
    print("Testing 4 critical endpoints with exact data structures from review request")
    print("=" * 80)
    
    # Test health check first
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print(f"❌ API health check failed: HTTP {response.status_code}")
            return False
        print("✅ API health check passed")
    except Exception as e:
        print(f"❌ API health check failed: {str(e)}")
        return False
    
    print()
    
    # Run the 4 critical tests
    tests = [
        ("ENDPOINT 1: POST /api/questionnaires/WebApp/complete", test_endpoint_1_questionnaire_complete),
        ("ENDPOINT 2: GET /api/questionnaires/WebApp", test_endpoint_2_questionnaire_get),
        ("ENDPOINT 3: POST /api/simulate", test_endpoint_3_simulate),
        ("ENDPOINT 4: POST /api/rules/evaluate", test_endpoint_4_rules_evaluate)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"   ❌ FAILED: Test execution error - {str(e)}")
            failed += 1
        print()
    
    # Print summary
    print("=" * 80)
    print(f"🎯 CRITICAL PHASE 1 CORE LOOP TEST RESULTS")
    print(f"✅ Passed: {passed}/4")
    print(f"❌ Failed: {failed}/4")
    print(f"📊 Success Rate: {(passed/4*100):.1f}%")
    
    if failed > 0:
        print(f"🚨 CRITICAL ISSUES: {failed} endpoints need fixes")
    else:
        print("🎉 ALL CRITICAL ENDPOINTS WORKING!")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)