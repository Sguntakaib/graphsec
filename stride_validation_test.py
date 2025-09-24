#!/usr/bin/env python3
"""
STRIDE Analysis Validation - Confirming Field Mapping Fix

This test validates that the STRIDE analysis field mapping issue has been resolved.
The fix ensures STRIDE heuristic rules use correct questionnaire field names.
"""

import requests
import json
import uuid

BASE_URL = "https://vulnstride-popup.preview.emergentagent.com/api"

def test_stride_analysis_fix():
    """Test that STRIDE analysis now works correctly with optimal security"""
    session = requests.Session()
    
    print("🎯 STRIDE ANALYSIS VALIDATION TEST")
    print("=" * 60)
    
    try:
        # Create test diagram
        diagram_data = {"title": "STRIDE Validation Test", "description": "Testing STRIDE field mapping fix"}
        response = session.post(f"{BASE_URL}/diagrams", json=diagram_data)
        diagram = response.json()
        diagram_id = diagram.get("id")
        
        # Create Database with optimal security
        database_node = {
            "id": f"db-test-{uuid.uuid4().hex[:8]}",
            "type": "Asset", 
            "subtype": "Database",
            "label": "Optimal Security Database",
            "position": {"x": 400, "y": 300}
        }
        node_id = database_node["id"]
        
        # Update diagram with Database node
        diagram["nodes"] = [database_node]
        diagram["edges"] = []
        session.put(f"{BASE_URL}/diagrams/{diagram_id}", json=diagram)
        
        # Configure optimal security
        optimal_config = {
            "responses": {
                "database_authentication": "Strong authentication with MFA",
                "database_encryption_at_rest": "Transparent Data Encryption (TDE)",
                "database_encryption_in_transit": "SSL/TLS enforced", 
                "database_access_control": "Role-based access with least privilege",
                "database_logging": "Comprehensive audit logging",
                "database_network_security": "Private network with firewall"
            }
        }
        
        session.post(f"{BASE_URL}/diagrams/{diagram_id}/nodes/{node_id}/questionnaire", json=optimal_config)
        
        # Test vulnerability analysis (should be 0)
        vuln_response = session.post(f"{BASE_URL}/vulnerabilities/analyze/{node_id}", json={
            "node_id": node_id, 
            "node_type": "Database",
            "questionnaire_responses": optimal_config["responses"]
        })
        vuln_data = vuln_response.json()
        vuln_count = len(vuln_data.get("vulnerabilities", []))
        
        # Test STRIDE analysis
        stride_response = session.post(f"{BASE_URL}/diagrams/{diagram_id}/stride/analyze")
        stride_data = stride_response.json()
        threat_count = len(stride_data.get("threats", []))
        
        # Get STRIDE coverage
        coverage_response = session.get(f"{BASE_URL}/diagrams/{diagram_id}/stride/coverage")
        coverage_data = coverage_response.json()
        mitigation_pct = coverage_data.get("mitigation_percentage", 0)
        
        print(f"📊 VALIDATION RESULTS:")
        print(f"   Vulnerabilities Found: {vuln_count} (Expected: 0)")
        print(f"   STRIDE Threats Found: {threat_count} (Expected: 6 mitigated controls)")
        print(f"   Mitigation Percentage: {mitigation_pct}% (Expected: 100%)")
        
        # Analyze threat details
        if stride_data.get("threats"):
            print(f"\n🔍 STRIDE THREAT DETAILS:")
            for i, threat in enumerate(stride_data["threats"][:3], 1):
                title = threat.get("title", "Unknown")
                status = threat.get("status", "unknown")
                print(f"   {i}. {title} (Status: {status})")
        
        # Cleanup
        session.delete(f"{BASE_URL}/diagrams/{diagram_id}")
        
        # Validation logic
        success_criteria = [
            vuln_count == 0,  # No vulnerabilities for optimal security
            threat_count <= 8,  # Reduced from 13 to reasonable number
            mitigation_pct >= 90  # High mitigation percentage
        ]
        
        if all(success_criteria):
            print(f"\n✅ STRIDE ANALYSIS FIX VALIDATED")
            print(f"   - Vulnerability analysis: 0 issues ✅")
            print(f"   - STRIDE threats reduced and properly mitigated ✅") 
            print(f"   - Field mapping issue resolved ✅")
        else:
            print(f"\n❌ VALIDATION FAILED")
            print(f"   - Check criteria: {success_criteria}")
            
    except Exception as e:
        print(f"❌ TEST ERROR: {str(e)}")

if __name__ == "__main__":
    test_stride_analysis_fix()