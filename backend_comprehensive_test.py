#!/usr/bin/env python3
"""
Backend API Testing - COLLAPSIBLE MENU AND ENHANCED RIGHT PANEL SUPPORT
Tests the backend APIs to ensure all existing functionality still works correctly after implementing 
the collapsible menu and enhanced right panel features.

TESTING FOCUS:
🎯 PRIMARY TEST: BACKEND SUPPORT FOR ENHANCED UI FEATURES

1. **Core API Health Check:**
   - Verify basic API endpoints are responding
   - Test GET /api/ health endpoint

2. **Diagram Management:**
   - Test diagram creation, loading, and saving functionality
   - Verify GET /api/diagrams, POST /api/diagrams, PUT /api/diagrams/{id}

3. **Node Management:**
   - Test node creation and questionnaire endpoints
   - Verify node information retrieval for right panel display

4. **Security Questionnaire System:**
   - Verify questionnaire endpoints for WebApp, API, Database nodes
   - Test GET /api/questionnaires/{node_subtype} endpoints
   - Ensure questionnaire data supports right panel information display

5. **Intelligent Node System:**
   - Test intelligent node endpoints that support the new right panel information display
   - Verify GET /api/intelligent-nodes/{node_subtype}/prompts endpoints
   - Test node information endpoints for immediate display on single click

**EXPECTED RESULTS:** 
- All core API endpoints should be functional
- Questionnaire endpoints should return proper data for right panel display
- Intelligent node endpoints should support immediate information display
- Node information should be available for single-click display in right panel
"""

import requests
import json
import uuid
from datetime import datetime, timezone
import sys

# Use the backend URL from frontend/.env with /api suffix
BASE_URL = "https://vulnstride-popup.preview.emergentagent.com/api"

class ComprehensiveBackendTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.test_results = []
        self.test_diagram_id = None
        self.test_node_ids = []
        
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
        
    def test_core_api_health_check(self):
        """Test GET /api/ health check endpoint"""
        try:
            print("🎯 TESTING: Core API Health Check")
            print("=" * 50)
            
            response = self.session.get(f"{self.base_url}/")
            print(f"📋 Response Status: HTTP {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "Security Modeling Platform API" in data["message"]:
                    self.log_test("Core API Health Check", True, 
                                f"✅ API is healthy: {data['message']}")
                    return True
                else:
                    self.log_test("Core API Health Check", False, 
                                f"Unexpected response format: {data}")
                    return False
            else:
                self.log_test("Core API Health Check", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Core API Health Check", False, f"Connection error: {str(e)}")
            return False

    def test_diagram_management_apis(self):
        """Test diagram creation, loading, and saving functionality"""
        try:
            print("🎯 TESTING: Diagram Management APIs")
            print("=" * 50)
            
            # Test 1: Create diagram (POST /api/diagrams)
            diagram_data = {
                "title": f"Enhanced UI Test Diagram {uuid.uuid4().hex[:8]}",
                "description": "Test diagram for collapsible menu and enhanced right panel features"
            }
            
            response = self.session.post(f"{self.base_url}/diagrams", json=diagram_data)
            print(f"📋 Create Diagram Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                self.log_test("Diagram Management - Create", False, 
                            f"Failed to create diagram: HTTP {response.status_code}")
                return False
            
            diagram = response.json()
            self.test_diagram_id = diagram.get("id")
            
            if not self.test_diagram_id:
                self.log_test("Diagram Management - Create", False, "No diagram ID returned")
                return False
            
            print(f"📋 Created diagram: {self.test_diagram_id}")
            
            # Test 2: List diagrams (GET /api/diagrams)
            response = self.session.get(f"{self.base_url}/diagrams")
            print(f"📋 List Diagrams Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                self.log_test("Diagram Management - List", False, 
                            f"Failed to list diagrams: HTTP {response.status_code}")
                return False
            
            diagrams = response.json()
            if not isinstance(diagrams, list):
                self.log_test("Diagram Management - List", False, 
                            "Diagrams response is not a list")
                return False
            
            print(f"📋 Found {len(diagrams)} diagrams")
            
            # Test 3: Get specific diagram (GET /api/diagrams/{id})
            response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}")
            print(f"📋 Get Diagram Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                self.log_test("Diagram Management - Get", False, 
                            f"Failed to get diagram: HTTP {response.status_code}")
                return False
            
            retrieved_diagram = response.json()
            if retrieved_diagram.get("id") != self.test_diagram_id:
                self.log_test("Diagram Management - Get", False, 
                            "Retrieved diagram ID doesn't match")
                return False
            
            # Test 4: Update diagram (PUT /api/diagrams/{id})
            updated_data = retrieved_diagram.copy()
            updated_data["description"] = "Updated for enhanced UI testing"
            updated_data["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            response = self.session.put(f"{self.base_url}/diagrams/{self.test_diagram_id}", 
                                      json=updated_data)
            print(f"📋 Update Diagram Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                self.log_test("Diagram Management - Update", False, 
                            f"Failed to update diagram: HTTP {response.status_code}")
                return False
            
            self.log_test("Diagram Management APIs", True, 
                        "✅ All diagram management APIs working correctly")
            return True
            
        except Exception as e:
            self.log_test("Diagram Management APIs", False, f"Request error: {str(e)}")
            return False

    def test_node_management_apis(self):
        """Test node creation and management for right panel display"""
        try:
            print("🎯 TESTING: Node Management APIs")
            print("=" * 50)
            
            if not self.test_diagram_id:
                self.log_test("Node Management APIs", False, "No test diagram available")
                return False
            
            # Create test nodes for different subtypes
            test_nodes = [
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
                        "data_classification": "Internal"
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
                }
            ]
            
            self.test_node_ids = [node["id"] for node in test_nodes]
            
            # Get current diagram
            response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}")
            if response.status_code != 200:
                self.log_test("Node Management APIs", False, "Failed to get current diagram")
                return False
            
            current_diagram = response.json()
            
            # Add nodes to diagram
            updated_diagram = current_diagram.copy()
            updated_diagram["nodes"] = test_nodes
            updated_diagram["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            response = self.session.put(f"{self.base_url}/diagrams/{self.test_diagram_id}", 
                                      json=updated_diagram)
            print(f"📋 Add Nodes Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                self.log_test("Node Management APIs", False, 
                            f"Failed to add nodes: HTTP {response.status_code}")
                return False
            
            # Verify nodes were added
            response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}")
            if response.status_code != 200:
                self.log_test("Node Management APIs", False, "Failed to verify nodes")
                return False
            
            updated_diagram = response.json()
            nodes = updated_diagram.get("nodes", [])
            
            if len(nodes) != len(test_nodes):
                self.log_test("Node Management APIs", False, 
                            f"Expected {len(test_nodes)} nodes, found {len(nodes)}")
                return False
            
            # Verify node data structure for right panel display
            for node in nodes:
                required_fields = ["id", "type", "subtype", "label", "position"]
                missing_fields = [field for field in required_fields if field not in node]
                
                if missing_fields:
                    self.log_test("Node Management APIs", False, 
                                f"Node {node.get('id', 'unknown')} missing fields: {missing_fields}")
                    return False
            
            print(f"📋 Successfully created {len(nodes)} nodes with proper structure")
            
            self.log_test("Node Management APIs", True, 
                        "✅ Node management APIs working correctly for right panel display")
            return True
            
        except Exception as e:
            self.log_test("Node Management APIs", False, f"Request error: {str(e)}")
            return False

    def test_security_questionnaire_endpoints(self):
        """Test questionnaire endpoints for WebApp, API, Database nodes"""
        try:
            print("🎯 TESTING: Security Questionnaire System")
            print("=" * 50)
            
            # Test questionnaire endpoints for different node subtypes
            node_subtypes = ["WebApp", "API", "Database"]
            questionnaire_results = {}
            
            for subtype in node_subtypes:
                print(f"📋 Testing questionnaire for {subtype}...")
                
                # Test GET /api/questionnaires/{node_subtype}
                response = self.session.get(f"{self.base_url}/questionnaires/{subtype}")
                print(f"   Status: HTTP {response.status_code}")
                
                if response.status_code != 200:
                    self.log_test(f"Questionnaire - {subtype}", False, 
                                f"HTTP {response.status_code}: Failed to get questionnaire")
                    continue
                
                try:
                    questionnaire_data = response.json()
                except json.JSONDecodeError:
                    self.log_test(f"Questionnaire - {subtype}", False, 
                                "Invalid JSON response")
                    continue
                
                # Verify questionnaire structure for right panel display
                required_fields = ["prompts"]
                missing_fields = [field for field in required_fields if field not in questionnaire_data]
                
                if missing_fields:
                    self.log_test(f"Questionnaire - {subtype}", False, 
                                f"Missing required fields: {missing_fields}")
                    continue
                
                prompts = questionnaire_data.get("prompts", [])
                if not isinstance(prompts, list) or len(prompts) == 0:
                    self.log_test(f"Questionnaire - {subtype}", False, 
                                "No prompts found in questionnaire")
                    continue
                
                # Verify prompt structure
                valid_prompts = 0
                for prompt in prompts:
                    if isinstance(prompt, dict) and "question" in prompt:
                        valid_prompts += 1
                
                if valid_prompts == 0:
                    self.log_test(f"Questionnaire - {subtype}", False, 
                                "No valid prompts found")
                    continue
                
                questionnaire_results[subtype] = {
                    "total_prompts": len(prompts),
                    "valid_prompts": valid_prompts,
                    "has_level": "level" in questionnaire_data,
                    "has_total_questions": "total_questions" in questionnaire_data
                }
                
                print(f"   ✅ {subtype}: {valid_prompts} valid prompts found")
            
            # Verify all subtypes were successful
            successful_subtypes = len(questionnaire_results)
            if successful_subtypes != len(node_subtypes):
                self.log_test("Security Questionnaire System", False, 
                            f"Only {successful_subtypes}/{len(node_subtypes)} questionnaire endpoints working")
                return False
            
            print(f"📊 Questionnaire Results:")
            for subtype, results in questionnaire_results.items():
                print(f"   {subtype}: {results['valid_prompts']} prompts, level={results['has_level']}, total_questions={results['has_total_questions']}")
            
            self.log_test("Security Questionnaire System", True, 
                        f"✅ All {successful_subtypes} questionnaire endpoints working correctly")
            return True
            
        except Exception as e:
            self.log_test("Security Questionnaire System", False, f"Request error: {str(e)}")
            return False

    def test_intelligent_node_endpoints(self):
        """Test intelligent node endpoints that support right panel information display"""
        try:
            print("🎯 TESTING: Intelligent Node System")
            print("=" * 50)
            
            # Test intelligent node endpoints for different subtypes
            node_subtypes = ["WebApp", "API", "Database"]
            intelligent_node_results = {}
            
            for subtype in node_subtypes:
                print(f"📋 Testing intelligent node prompts for {subtype}...")
                
                # Test GET /api/intelligent-nodes/{node_subtype}/prompts
                response = self.session.get(f"{self.base_url}/intelligent-nodes/{subtype}/prompts")
                print(f"   Status: HTTP {response.status_code}")
                
                if response.status_code != 200:
                    self.log_test(f"Intelligent Node - {subtype}", False, 
                                f"HTTP {response.status_code}: Failed to get intelligent node prompts")
                    continue
                
                try:
                    prompts_data = response.json()
                except json.JSONDecodeError:
                    self.log_test(f"Intelligent Node - {subtype}", False, 
                                "Invalid JSON response")
                    continue
                
                # Verify response structure for right panel display
                required_fields = ["success", "node_subtype"]
                missing_fields = [field for field in required_fields if field not in prompts_data]
                
                if missing_fields:
                    self.log_test(f"Intelligent Node - {subtype}", False, 
                                f"Missing required fields: {missing_fields}")
                    continue
                
                if not prompts_data.get("success", False):
                    self.log_test(f"Intelligent Node - {subtype}", False, 
                                "Response indicates failure")
                    continue
                
                if prompts_data.get("node_subtype") != subtype:
                    self.log_test(f"Intelligent Node - {subtype}", False, 
                                f"Node subtype mismatch: expected {subtype}, got {prompts_data.get('node_subtype')}")
                    continue
                
                # Check for prompts count (indicates available information for right panel)
                prompts_count = prompts_data.get("prompts_count", 0)
                if prompts_count == 0:
                    self.log_test(f"Intelligent Node - {subtype}", False, 
                                "No prompts available for right panel display")
                    continue
                
                intelligent_node_results[subtype] = {
                    "prompts_count": prompts_count,
                    "success": prompts_data.get("success", False),
                    "has_level": "level" in prompts_data
                }
                
                print(f"   ✅ {subtype}: {prompts_count} prompts available for right panel")
            
            # Verify all subtypes were successful
            successful_subtypes = len(intelligent_node_results)
            if successful_subtypes != len(node_subtypes):
                self.log_test("Intelligent Node System", False, 
                            f"Only {successful_subtypes}/{len(node_subtypes)} intelligent node endpoints working")
                return False
            
            print(f"📊 Intelligent Node Results:")
            for subtype, results in intelligent_node_results.items():
                print(f"   {subtype}: {results['prompts_count']} prompts, success={results['success']}")
            
            self.log_test("Intelligent Node System", True, 
                        f"✅ All {successful_subtypes} intelligent node endpoints working correctly")
            return True
            
        except Exception as e:
            self.log_test("Intelligent Node System", False, f"Request error: {str(e)}")
            return False

    def test_node_information_for_right_panel(self):
        """Test that node information is available for immediate display in right panel"""
        try:
            print("🎯 TESTING: Node Information for Right Panel Display")
            print("=" * 60)
            
            if not self.test_diagram_id or not self.test_node_ids:
                self.log_test("Node Information for Right Panel", False, 
                            "No test nodes available")
                return False
            
            # Get current diagram with nodes
            response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}")
            if response.status_code != 200:
                self.log_test("Node Information for Right Panel", False, 
                            "Failed to get diagram with nodes")
                return False
            
            diagram = response.json()
            nodes = diagram.get("nodes", [])
            
            if len(nodes) == 0:
                self.log_test("Node Information for Right Panel", False, 
                            "No nodes found in diagram")
                return False
            
            # Test each node for right panel information availability
            nodes_with_info = 0
            
            for node in nodes:
                node_id = node.get("id")
                node_subtype = node.get("subtype")
                
                print(f"📋 Testing node information for {node_subtype} ({node_id[:8]}...)...")
                
                # Check if node has basic information for right panel display
                required_info = ["id", "type", "subtype", "label", "position"]
                has_required_info = all(field in node for field in required_info)
                
                if not has_required_info:
                    print(f"   ❌ Missing required information")
                    continue
                
                # Check if node has additional data for enhanced display
                node_data = node.get("data", {})
                has_additional_data = isinstance(node_data, dict) and len(node_data) > 0
                
                # For right panel display, we need questionnaire information
                # Test if questionnaire is available for this node subtype
                questionnaire_available = False
                if node_subtype in ["WebApp", "API", "Database"]:
                    # Quick check if questionnaire endpoint works
                    response = self.session.get(f"{self.base_url}/questionnaires/{node_subtype}")
                    if response.status_code == 200:
                        questionnaire_available = True
                
                # Test if intelligent node information is available
                intelligent_info_available = False
                if node_subtype in ["WebApp", "API", "Database"]:
                    response = self.session.get(f"{self.base_url}/intelligent-nodes/{node_subtype}/prompts")
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            if data.get("success", False):
                                intelligent_info_available = True
                        except:
                            pass
                
                print(f"   📊 Node Information Analysis:")
                print(f"      Basic info: {has_required_info}")
                print(f"      Additional data: {has_additional_data}")
                print(f"      Questionnaire available: {questionnaire_available}")
                print(f"      Intelligent info available: {intelligent_info_available}")
                
                # Node is ready for right panel if it has basic info and at least one source of detailed info
                if has_required_info and (questionnaire_available or intelligent_info_available):
                    nodes_with_info += 1
                    print(f"   ✅ Node ready for right panel display")
                else:
                    print(f"   ❌ Node not ready for right panel display")
            
            if nodes_with_info == 0:
                self.log_test("Node Information for Right Panel", False, 
                            "No nodes have sufficient information for right panel display")
                return False
            
            success_rate = (nodes_with_info / len(nodes)) * 100
            
            print(f"📊 Right Panel Information Results:")
            print(f"   Total nodes: {len(nodes)}")
            print(f"   Nodes with right panel info: {nodes_with_info}")
            print(f"   Success rate: {success_rate:.1f}%")
            
            if success_rate >= 80:  # At least 80% of nodes should have right panel info
                self.log_test("Node Information for Right Panel", True, 
                            f"✅ {nodes_with_info}/{len(nodes)} nodes ready for right panel display ({success_rate:.1f}%)")
                return True
            else:
                self.log_test("Node Information for Right Panel", False, 
                            f"Insufficient nodes ready for right panel: {nodes_with_info}/{len(nodes)} ({success_rate:.1f}%)")
                return False
            
        except Exception as e:
            self.log_test("Node Information for Right Panel", False, f"Request error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all comprehensive backend tests"""
        print("🚀 STARTING COMPREHENSIVE BACKEND TESTING")
        print("=" * 80)
        print("Testing backend APIs for collapsible menu and enhanced right panel support")
        print("=" * 80)
        
        tests = [
            self.test_core_api_health_check,
            self.test_diagram_management_apis,
            self.test_node_management_apis,
            self.test_security_questionnaire_endpoints,
            self.test_intelligent_node_endpoints,
            self.test_node_information_for_right_panel,
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
        
        print("=" * 80)
        print(f"🏁 TESTING COMPLETE: {passed}/{total} tests passed")
        print("=" * 80)
        
        # Print detailed results
        print("\n📊 DETAILED TEST RESULTS:")
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{status} {result['test']}: {result['message']}")
        
        return passed == total

if __name__ == "__main__":
    tester = ComprehensiveBackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)