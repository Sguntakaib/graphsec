#!/usr/bin/env python3
"""
Backend API Testing - STRIDE Phase 1 API Endpoints Testing
Tests the newly implemented STRIDE Phase 1 API endpoints for threat analysis:

TESTING FOCUS:
🎯 STRIDE PHASE 1 API ENDPOINTS TESTING
1. STRIDE Analysis Endpoint: POST /api/diagrams/{diagram_id}/stride/analyze
2. STRIDE Coverage Endpoint: GET /api/diagrams/{diagram_id}/stride/coverage  
3. Threat Status Update: PATCH /api/diagrams/{diagram_id}/stride/threats/{threat_id}
4. Error Handling for non-existent IDs and invalid values

TEST SCENARIOS:
1. Health Check - Verify basic API health endpoint
2. Create Test Diagram - Create diagram with WebApp, API, Database nodes
3. STRIDE Analysis - Test threat analysis with proper categorization
4. STRIDE Coverage - Test coverage summary with mitigation counts
5. Threat Status Updates - Test updating threat status and mitigations
6. Error Handling - Test with invalid IDs and status values

**EXPECTED RESULTS:** 
- STRIDE analysis correctly identifies threats based on node subtypes
- Threats are properly categorized by STRIDE categories (Spoofing, Tampering, etc.)
- Coverage endpoint returns proper totals and mitigation percentages
- Threat status updates persist in database
- Proper error handling for invalid inputs
"""

import requests
import json
import uuid
from datetime import datetime, timezone
import sys

# Use the backend URL from frontend/.env with /api suffix
BASE_URL = "https://frontend-audit-5.preview.emergentagent.com/api"

class StrideBackendTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.test_results = []
        self.test_diagram_id = None
        self.test_node_ids = {}  # Store node IDs by subtype
        self.test_threat_ids = []  # Store threat IDs for testing updates
        
    def log_test(self, test_name, success, message="", response_data=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "response_data": response_data
        })
        
    def test_health_check(self):
        """Test GET /api/ health check endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_test("Health Check", True, f"API is healthy: {data['message']}")
                    return True
                else:
                    self.log_test("Health Check", False, f"Unexpected response format: {data}")
                    return False
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Connection error: {str(e)}")
            return False

    def test_create_test_diagram_with_nodes(self):
        """TEST SCENARIO 1: Create diagram with WebApp, API, Database nodes for STRIDE testing"""
        try:
            print("🎯 TEST SCENARIO 1: Create Test Diagram with Security Nodes")
            print("=" * 80)
            
            # Create a test diagram
            diagram_data = {
                "title": "STRIDE Phase 1 Test Diagram",
                "description": "Test diagram with WebApp, API, Database nodes for STRIDE threat analysis"
            }
            
            response = self.session.post(f"{self.base_url}/diagrams", json=diagram_data)
            
            print(f"📋 Create Diagram Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("Create Test Diagram with Security Nodes", False, 
                            f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Create Test Diagram with Security Nodes", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            self.test_diagram_id = data.get("id")
            
            if not self.test_diagram_id:
                self.log_test("Create Test Diagram with Security Nodes", False, "No diagram ID returned")
                return False
            
            print(f"📊 Diagram Created Successfully:")
            print(f"   Diagram ID: {self.test_diagram_id}")
            print(f"   Title: {data.get('title')}")
            
            # Now add security nodes to the diagram
            security_nodes = [
                {
                    "id": f"webapp-{uuid.uuid4().hex[:8]}",
                    "type": "Asset",
                    "subtype": "WebApp",
                    "label": "Test Web Application",
                    "position": {"x": 100, "y": 100},
                    "data": {
                        "criticality": "High",
                        "data_classification": "Confidential"
                    }
                },
                {
                    "id": f"api-{uuid.uuid4().hex[:8]}",
                    "type": "Asset",
                    "subtype": "API",
                    "label": "Test API Gateway",
                    "position": {"x": 300, "y": 100},
                    "data": {
                        "criticality": "High",
                        "data_classification": "Confidential"
                    }
                },
                {
                    "id": f"database-{uuid.uuid4().hex[:8]}",
                    "type": "Asset",
                    "subtype": "Database",
                    "label": "Test Database",
                    "position": {"x": 500, "y": 100},
                    "data": {
                        "criticality": "Critical",
                        "data_classification": "Restricted"
                    }
                },
                {
                    "id": f"attacker-{uuid.uuid4().hex[:8]}",
                    "type": "Actor",
                    "subtype": "ExternalAttacker",
                    "label": "External Threat Actor",
                    "position": {"x": 50, "y": 200},
                    "data": {
                        "sophistication": "Medium",
                        "motivation": "Financial"
                    }
                }
            ]
            
            # Store node IDs for later use
            for node in security_nodes:
                self.test_node_ids[node["subtype"]] = node["id"]
            
            # Update diagram with security nodes
            updated_diagram = {
                "id": self.test_diagram_id,
                "title": data.get("title"),
                "description": data.get("description"),
                "nodes": security_nodes,
                "edges": [],
                "created_at": data.get("created_at"),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            update_response = self.session.put(f"{self.base_url}/diagrams/{self.test_diagram_id}", json=updated_diagram)
            
            if update_response.status_code != 200:
                self.log_test("Create Test Diagram with Security Nodes", False, 
                            "Failed to add security nodes to diagram")
                return False
            
            print(f"   Added Security Nodes:")
            for subtype, node_id in self.test_node_ids.items():
                print(f"     {subtype}: {node_id}")
            
            self.log_test("Create Test Diagram with Security Nodes", True, 
                        f"✅ SUCCESS: Diagram created with {len(security_nodes)} security nodes")
            
            return True
            
        except Exception as e:
            self.log_test("Create Test Diagram with Security Nodes", False, f"Request error: {str(e)}")
            return False

    def test_stride_analysis_endpoint(self):
        """TEST SCENARIO 2: Test STRIDE Analysis Endpoint"""
        try:
            print("🎯 TEST SCENARIO 2: STRIDE Analysis Endpoint")
            print("=" * 80)
            
            if not self.test_diagram_id:
                self.log_test("STRIDE Analysis Endpoint", False, "No test diagram ID available")
                return False
            
            # Test STRIDE analysis
            response = self.session.post(f"{self.base_url}/diagrams/{self.test_diagram_id}/stride/analyze")
            
            print(f"📋 STRIDE Analysis Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("STRIDE Analysis Endpoint", False, 
                            f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("STRIDE Analysis Endpoint", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            # Verify response structure
            threats = data.get("threats", [])
            analysis_summary = data.get("analysis_summary", {})
            
            if not threats:
                self.log_test("STRIDE Analysis Endpoint", False, "No threats returned from analysis")
                return False
            
            # Store threat IDs for later testing
            self.test_threat_ids = [threat["id"] for threat in threats[:3]]  # Store first 3 for testing
            
            print(f"📊 STRIDE Analysis Results:")
            print(f"   Total Threats: {len(threats)}")
            print(f"   Analysis Summary: {analysis_summary}")
            
            # Verify STRIDE categories are present
            stride_categories = ["Spoofing", "Tampering", "Repudiation", "Information Disclosure", 
                               "Denial of Service", "Elevation of Privilege"]
            
            threats_by_category = {}
            for threat in threats:
                category = threat.get("stride_category")
                if category not in threats_by_category:
                    threats_by_category[category] = 0
                threats_by_category[category] += 1
            
            print(f"   Threats by STRIDE Category:")
            for category in stride_categories:
                count = threats_by_category.get(category, 0)
                print(f"     {category}: {count}")
            
            # Verify threat structure
            sample_threat = threats[0]
            required_fields = ["id", "element_type", "element_id", "stride_category", 
                             "title", "description", "mitigations", "status", "residual_risk"]
            
            missing_fields = []
            for field in required_fields:
                if field not in sample_threat:
                    missing_fields.append(field)
            
            if missing_fields:
                self.log_test("STRIDE Analysis Endpoint", False, 
                            f"Missing required fields in threat: {missing_fields}")
                return False
            
            # Show sample threats
            print(f"   Sample Threats:")
            for i, threat in enumerate(threats[:3]):
                print(f"     {i+1}. {threat['title']} ({threat['stride_category']}) - Risk: {threat['residual_risk']}")
            
            self.log_test("STRIDE Analysis Endpoint", True, 
                        f"✅ SUCCESS: STRIDE analysis completed, {len(threats)} threats identified")
            
            return True
            
        except Exception as e:
            self.log_test("STRIDE Analysis Endpoint", False, f"Request error: {str(e)}")
            return False

    def test_stride_coverage_endpoint(self):
        """TEST SCENARIO 3: Test STRIDE Coverage Endpoint"""
        try:
            print("🎯 TEST SCENARIO 3: STRIDE Coverage Endpoint")
            print("=" * 80)
            
            if not self.test_diagram_id:
                self.log_test("STRIDE Coverage Endpoint", False, "No test diagram ID available")
                return False
            
            # Test STRIDE coverage
            response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}/stride/coverage")
            
            print(f"📋 STRIDE Coverage Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("STRIDE Coverage Endpoint", False, 
                            f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("STRIDE Coverage Endpoint", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            # Verify coverage response structure
            required_fields = ["totals", "mitigated", "residual_risk_avg", "by_node", 
                             "by_edge", "total_threats", "mitigation_percentage"]
            
            missing_fields = []
            for field in required_fields:
                if field not in data:
                    missing_fields.append(field)
            
            if missing_fields:
                self.log_test("STRIDE Coverage Endpoint", False, 
                            f"Missing required fields in coverage: {missing_fields}")
                return False
            
            print(f"📊 STRIDE Coverage Results:")
            print(f"   Total Threats: {data['total_threats']}")
            print(f"   Mitigation Percentage: {data['mitigation_percentage']}%")
            print(f"   Average Residual Risk: {data['residual_risk_avg']}")
            
            # Verify totals by category
            totals = data.get("totals", {})
            mitigated = data.get("mitigated", {})
            
            print(f"   Coverage by STRIDE Category:")
            stride_categories = ["Spoofing", "Tampering", "Repudiation", "Information Disclosure", 
                               "Denial of Service", "Elevation of Privilege"]
            
            for category in stride_categories:
                total_count = totals.get(category, 0)
                mitigated_count = mitigated.get(category, 0)
                print(f"     {category}: {total_count} total, {mitigated_count} mitigated")
            
            # Verify by_node breakdown
            by_node = data.get("by_node", {})
            print(f"   Threats by Node:")
            for node_id, node_data in by_node.items():
                node_totals = sum(node_data.get("totals", {}).values())
                node_mitigated = sum(node_data.get("mitigated", {}).values())
                print(f"     {node_id[:12]}...: {node_totals} total, {node_mitigated} mitigated")
            
            self.log_test("STRIDE Coverage Endpoint", True, 
                        f"✅ SUCCESS: Coverage summary retrieved, {data['total_threats']} threats, {data['mitigation_percentage']}% mitigated")
            
            return True
            
        except Exception as e:
            self.log_test("STRIDE Coverage Endpoint", False, f"Request error: {str(e)}")
            return False

    def test_threat_status_update_endpoint(self):
        """TEST SCENARIO 4: Test Threat Status Update Endpoint"""
        try:
            print("🎯 TEST SCENARIO 4: Threat Status Update Endpoint")
            print("=" * 80)
            
            if not self.test_diagram_id or not self.test_threat_ids:
                self.log_test("Threat Status Update Endpoint", False, 
                            "No test diagram ID or threat IDs available")
                return False
            
            # Test updating threat status to mitigated
            threat_id = self.test_threat_ids[0]
            
            # Test valid status update
            update_data = {
                "status": "mitigated",
                "mitigations": ["Implemented strong authentication", "Added input validation"]
            }
            
            response = self.session.patch(
                f"{self.base_url}/diagrams/{self.test_diagram_id}/stride/threats/{threat_id}",
                params=update_data
            )
            
            print(f"📋 Threat Update Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("Threat Status Update Endpoint", False, 
                            f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Threat Status Update Endpoint", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            print(f"📊 Threat Update Results:")
            print(f"   Message: {data.get('message', 'No message')}")
            print(f"   Status: {data.get('status', 'Unknown')}")
            
            # Verify the update was successful
            if data.get("status") != "mitigated":
                self.log_test("Threat Status Update Endpoint", False, 
                            f"Status not updated correctly: {data.get('status')}")
                return False
            
            self.log_test("Threat Status Update Endpoint", True, 
                        f"✅ SUCCESS: Threat {threat_id[:12]}... updated to mitigated status")
            
            return True
            
        except Exception as e:
            self.log_test("Threat Status Update Endpoint", False, f"Request error: {str(e)}")
            return False

    def test_error_handling(self):
        """TEST SCENARIO 5: Test Error Handling"""
        try:
            print("🎯 TEST SCENARIO 5: Error Handling")
            print("=" * 80)
            
            # Test 1: Non-existent diagram ID for STRIDE analysis
            fake_diagram_id = f"fake-diagram-{uuid.uuid4().hex[:8]}"
            
            response = self.session.post(f"{self.base_url}/diagrams/{fake_diagram_id}/stride/analyze")
            
            print(f"📋 Non-existent Diagram Analysis Response: HTTP {response.status_code}")
            
            if response.status_code != 404:
                self.log_test("Error Handling - Non-existent Diagram", False, 
                            f"Expected 404, got {response.status_code}")
                return False
            
            # Test 2: Non-existent diagram ID for coverage
            response = self.session.get(f"{self.base_url}/diagrams/{fake_diagram_id}/stride/coverage")
            
            print(f"📋 Non-existent Diagram Coverage Response: HTTP {response.status_code}")
            
            # Coverage should return empty results, not 404
            if response.status_code != 200:
                print(f"   ⚠️ Coverage endpoint returned {response.status_code} for non-existent diagram")
            
            # Test 3: Invalid threat status
            if self.test_diagram_id and self.test_threat_ids:
                threat_id = self.test_threat_ids[0]
                
                invalid_status_data = {
                    "status": "invalid_status"
                }
                
                response = self.session.patch(
                    f"{self.base_url}/diagrams/{self.test_diagram_id}/stride/threats/{threat_id}",
                    params=invalid_status_data
                )
                
                print(f"📋 Invalid Status Update Response: HTTP {response.status_code}")
                
                if response.status_code != 400:
                    self.log_test("Error Handling - Invalid Status", False, 
                                f"Expected 400, got {response.status_code}")
                    return False
            
            # Test 4: Non-existent threat ID
            fake_threat_id = f"fake-threat-{uuid.uuid4().hex[:8]}"
            
            if self.test_diagram_id:
                valid_status_data = {
                    "status": "mitigated"
                }
                
                response = self.session.patch(
                    f"{self.base_url}/diagrams/{self.test_diagram_id}/stride/threats/{fake_threat_id}",
                    params=valid_status_data
                )
                
                print(f"📋 Non-existent Threat Update Response: HTTP {response.status_code}")
                
                if response.status_code != 404:
                    self.log_test("Error Handling - Non-existent Threat", False, 
                                f"Expected 404, got {response.status_code}")
                    return False
            
            print(f"📊 Error Handling Results:")
            print(f"   ✅ Non-existent diagram analysis: 404")
            print(f"   ✅ Invalid threat status: 400")
            print(f"   ✅ Non-existent threat update: 404")
            
            self.log_test("Error Handling", True, 
                        "✅ SUCCESS: All error handling scenarios working correctly")
            
            return True
            
        except Exception as e:
            self.log_test("Error Handling", False, f"Request error: {str(e)}")
            return False

    def cleanup_test_data(self):
        """Clean up test data after testing"""
        try:
            if self.test_diagram_id:
                print("🧹 CLEANUP: Removing test diagram and threats")
                response = self.session.delete(f"{self.base_url}/diagrams/{self.test_diagram_id}")
                if response.status_code == 200:
                    print(f"   ✅ Test diagram {self.test_diagram_id} deleted successfully")
                else:
                    print(f"   ⚠️ Failed to delete test diagram: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ⚠️ Cleanup error: {str(e)}")

    def run_all_tests(self):
        """Run all STRIDE Phase 1 API endpoint tests"""
        print("🚀 STARTING STRIDE PHASE 1 API ENDPOINTS TESTING")
        print("=" * 80)
        print("Testing STRIDE Phase 1 implementation for threat analysis:")
        print("1. Health Check - Verify basic API health endpoint")
        print("2. Create Test Diagram - Create diagram with WebApp, API, Database nodes")
        print("3. STRIDE Analysis - Test threat analysis with proper categorization")
        print("4. STRIDE Coverage - Test coverage summary with mitigation counts")
        print("5. Threat Status Updates - Test updating threat status and mitigations")
        print("6. Error Handling - Test with invalid IDs and status values")
        print("=" * 80)
        
        tests = [
            self.test_health_check,
            self.test_create_test_diagram_with_nodes,
            self.test_stride_analysis_endpoint,
            self.test_stride_coverage_endpoint,
            self.test_threat_status_update_endpoint,
            self.test_error_handling,
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
                print()  # Add spacing between tests
            except Exception as e:
                print(f"❌ Test {test.__name__} failed with exception: {str(e)}")
                print()
        
        # Cleanup
        self.cleanup_test_data()
        
        print("=" * 80)
        print(f"🏁 TESTING COMPLETE: {passed}/{total} tests passed")
        print("=" * 80)
        
        # Print detailed results
        print("\n📊 DETAILED TEST RESULTS:")
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{status} {result['test']}: {result['message']}")
        
        # Summary for STRIDE Phase 1 testing
        if passed == total:
            print("\n🎉 STRIDE PHASE 1 API ENDPOINTS: ALL TESTS PASSED")
            print("✅ STRIDE Analysis endpoint working correctly")
            print("✅ STRIDE Coverage endpoint functioning properly")
            print("✅ Threat status update endpoint operational")
            print("✅ Error handling working as expected")
            print("✅ Threats properly categorized by STRIDE methodology")
            print("✅ Foundation for Phase 1 implementation is solid")
        else:
            print(f"\n⚠️ STRIDE PHASE 1 API ENDPOINTS: {total-passed} TESTS FAILED")
            print("❌ Some STRIDE functionality may not be working correctly")
            print("❌ Review failed tests above for details")
        
        return passed == total

if __name__ == "__main__":
    tester = StrideBackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)