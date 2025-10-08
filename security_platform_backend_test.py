#!/usr/bin/env python3
"""
Security Modeling Platform Backend Testing - Post UI Simplification Verification
Tests all core backend functionality after UI simplification changes to ensure no regressions.

TESTING SCOPE:
🎯 CORE API HEALTH: Verify all main endpoints are responding correctly
🎯 NODE MANAGEMENT: Test node creation, questionnaire functionality, and data persistence
🎯 SECURITY ANALYSIS: Verify vulnerability analysis and STRIDE analysis still work
🎯 DRAG-AND-DROP BACKEND SUPPORT: Ensure all drag-drop functionality has proper API support

FOCUS AREAS:
- Diagram creation and node management APIs
- Questionnaire endpoints for all node types (WebApp, API, Database)  
- Vulnerability analysis for simplified nodes
- STRIDE analysis functionality
- Template and connection type APIs

CONTEXT: UI elements were simplified to be cleaner and more minimal (like workflow builders) 
but need to ensure all backend functionality remains intact. The changes were purely visual - 
node styling, library items, and CSS improvements.

**EXPECTED RESULTS:** 
- All core API endpoints respond correctly
- Node creation and questionnaire flow works for all node types
- Vulnerability analysis works with simplified node data
- STRIDE analysis functions properly
- Template system supports drag-and-drop operations
- No backend regressions from UI simplification changes
"""

import requests
import json
import uuid
from datetime import datetime, timezone
import sys

# Use the backend URL from frontend/.env with /api suffix
BASE_URL = "https://element-iconography.preview.emergentagent.com/api"

class SecurityPlatformBackendTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.test_results = []
        self.test_diagram_id = None
        self.test_nodes = {}  # Store created test nodes by type
        
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
        
    def test_core_api_health(self):
        """TEST 1: Core API Health - Verify main endpoints responding"""
        try:
            print("🎯 TEST 1: Core API Health Check")
            print("=" * 80)
            
            # Test main health endpoint
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "Security Modeling Platform API" in data["message"]:
                    print(f"   ✅ Health Check: {data['message']}")
                    self.log_test("Core API Health", True, f"API is healthy: {data['message']}")
                    return True
                else:
                    self.log_test("Core API Health", False, f"Unexpected health response: {data}")
                    return False
            else:
                self.log_test("Core API Health", False, f"Health check failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Core API Health", False, f"Connection error: {str(e)}")
            return False

    def test_diagram_management_apis(self):
        """TEST 2: Diagram Creation and Management APIs"""
        try:
            print("🎯 TEST 2: Diagram Management APIs")
            print("=" * 80)
            
            # Create a test diagram
            diagram_data = {
                "title": "Security Platform UI Simplification Test",
                "description": "Test diagram to verify backend functionality after UI simplification"
            }
            
            response = self.session.post(f"{self.base_url}/diagrams", json=diagram_data)
            
            if response.status_code != 200:
                self.log_test("Diagram Management APIs", False, f"Failed to create diagram: HTTP {response.status_code}")
                return False
            
            data = response.json()
            self.test_diagram_id = data.get("id")
            
            if not self.test_diagram_id:
                self.log_test("Diagram Management APIs", False, "No diagram ID returned")
                return False
            
            print(f"   ✅ Diagram Created: {self.test_diagram_id}")
            
            # Test diagram retrieval
            get_response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}")
            if get_response.status_code != 200:
                self.log_test("Diagram Management APIs", False, "Failed to retrieve created diagram")
                return False
            
            # Test diagram listing
            list_response = self.session.get(f"{self.base_url}/diagrams")
            if list_response.status_code != 200:
                self.log_test("Diagram Management APIs", False, "Failed to list diagrams")
                return False
            
            diagrams = list_response.json()
            print(f"   ✅ Diagram Operations: Created, Retrieved, Listed ({len(diagrams)} total)")
            
            self.log_test("Diagram Management APIs", True, f"All diagram operations successful, ID: {self.test_diagram_id}")
            return True
            
        except Exception as e:
            self.log_test("Diagram Management APIs", False, f"Request error: {str(e)}")
            return False

    def test_node_creation_and_questionnaires(self):
        """TEST 3: Node Management - Creation and Questionnaire Functionality"""
        try:
            print("🎯 TEST 3: Node Management - Creation and Questionnaires")
            print("=" * 80)
            
            if not self.test_diagram_id:
                self.log_test("Node Management", False, "No test diagram available")
                return False
            
            # Test node types: WebApp, API, Database
            node_types = [
                {"subtype": "WebApp", "label": "Test Web Application", "pos": {"x": 100, "y": 100}},
                {"subtype": "API", "label": "Test API Service", "pos": {"x": 300, "y": 100}},
                {"subtype": "Database", "label": "Test Database", "pos": {"x": 500, "y": 100}}
            ]
            
            success_count = 0
            
            for node_config in node_types:
                subtype = node_config["subtype"]
                
                # Test questionnaire prompts for each node type
                prompts_response = self.session.get(f"{self.base_url}/intelligent-nodes/{subtype}/prompts")
                
                if prompts_response.status_code != 200:
                    print(f"   ❌ {subtype} Prompts: HTTP {prompts_response.status_code}")
                    continue
                
                prompts_data = prompts_response.json()
                if not prompts_data.get("success"):
                    print(f"   ❌ {subtype} Prompts: API returned success=false")
                    continue
                
                prompts_count = prompts_data.get("prompts_count", 0)
                print(f"   ✅ {subtype} Questionnaire: {prompts_count} prompts available")
                
                # Create node in diagram
                test_node = {
                    "id": f"{subtype.lower()}-node-{uuid.uuid4().hex[:8]}",
                    "type": "Asset",
                    "subtype": subtype,
                    "label": node_config["label"],
                    "position": node_config["pos"],
                    "data": {
                        "criticality": "High",
                        "data_classification": "Confidential"
                    }
                }
                
                # Get current diagram and add node
                diagram_response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}")
                if diagram_response.status_code != 200:
                    continue
                
                diagram_data = diagram_response.json()
                current_nodes = diagram_data.get("nodes", [])
                current_nodes.append(test_node)
                diagram_data["nodes"] = current_nodes
                
                # Update diagram with new node
                update_response = self.session.put(f"{self.base_url}/diagrams/{self.test_diagram_id}", json=diagram_data)
                if update_response.status_code == 200:
                    self.test_nodes[subtype] = test_node["id"]
                    print(f"   ✅ {subtype} Node Created: {test_node['id']}")
                    success_count += 1
                else:
                    print(f"   ❌ {subtype} Node Creation Failed: HTTP {update_response.status_code}")
            
            if success_count == len(node_types):
                self.log_test("Node Management", True, f"All {success_count} node types created with questionnaires")
                return True
            else:
                self.log_test("Node Management", False, f"Only {success_count}/{len(node_types)} node types successful")
                return False
                
        except Exception as e:
            self.log_test("Node Management", False, f"Request error: {str(e)}")
            return False

    def test_vulnerability_analysis(self):
        """TEST 4: Security Analysis - Vulnerability Analysis"""
        try:
            print("🎯 TEST 4: Security Analysis - Vulnerability Analysis")
            print("=" * 80)
            
            if not self.test_nodes:
                self.log_test("Vulnerability Analysis", False, "No test nodes available")
                return False
            
            success_count = 0
            
            # Test vulnerability analysis for each node type
            for node_type, node_id in self.test_nodes.items():
                print(f"   Testing {node_type} vulnerability analysis...")
                
                # Create realistic questionnaire responses for each node type
                if node_type == "WebApp":
                    questionnaire_responses = {
                        "webapp_authentication": "oauth2",
                        "webapp_encryption": True,
                        "webapp_input_validation": "comprehensive",
                        "webapp_session_management": "secure",
                        "webapp_error_handling": "secure"
                    }
                elif node_type == "API":
                    questionnaire_responses = {
                        "api_type": "REST API",
                        "api_protocol": "HTTPS",
                        "api_auth_method": "OAuth 2.0",
                        "api_authorization": "RBAC",
                        "api_rate_limiting": "implemented",
                        "api_input_validation": "comprehensive",
                        "api_cors_policy": "restrictive"
                    }
                elif node_type == "Database":
                    questionnaire_responses = {
                        "database_authentication": "strong_mfa",
                        "database_encryption_at_rest": "tde_enabled",
                        "database_encryption_in_transit": "ssl_tls_enforced",
                        "database_logging": "comprehensive_audit",
                        "database_access_control": "rbac_implemented"
                    }
                
                vulnerability_request = {
                    "node_id": node_id,
                    "node_type": node_type,
                    "questionnaire_responses": questionnaire_responses,
                    "node_position": {"x": 200, "y": 200}
                }
                
                response = self.session.post(
                    f"{self.base_url}/vulnerabilities/analyze/{node_id}",
                    json=vulnerability_request
                )
                
                if response.status_code == 200:
                    data = response.json()
                    vulnerabilities = data.get("vulnerabilities", [])
                    risk_score = data.get("overall_risk_score", 0)
                    
                    print(f"     ✅ {node_type}: {len(vulnerabilities)} vulnerabilities, risk score: {risk_score}")
                    success_count += 1
                else:
                    print(f"     ❌ {node_type}: HTTP {response.status_code}")
            
            if success_count == len(self.test_nodes):
                self.log_test("Vulnerability Analysis", True, f"All {success_count} node types analyzed successfully")
                return True
            else:
                self.log_test("Vulnerability Analysis", False, f"Only {success_count}/{len(self.test_nodes)} analyses successful")
                return False
                
        except Exception as e:
            self.log_test("Vulnerability Analysis", False, f"Request error: {str(e)}")
            return False

    def test_stride_analysis(self):
        """TEST 5: Security Analysis - STRIDE Analysis"""
        try:
            print("🎯 TEST 5: Security Analysis - STRIDE Analysis")
            print("=" * 80)
            
            if not self.test_diagram_id:
                self.log_test("STRIDE Analysis", False, "No test diagram available")
                return False
            
            # Test STRIDE analysis
            stride_response = self.session.post(f"{self.base_url}/diagrams/{self.test_diagram_id}/stride/analyze")
            
            if stride_response.status_code != 200:
                self.log_test("STRIDE Analysis", False, f"STRIDE analysis failed: HTTP {stride_response.status_code}")
                return False
            
            stride_data = stride_response.json()
            threats = stride_data.get("threats", [])
            analysis_summary = stride_data.get("analysis_summary", {})
            
            print(f"   ✅ STRIDE Analysis: {len(threats)} threats identified")
            
            # Test STRIDE coverage
            coverage_response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}/stride/coverage")
            
            if coverage_response.status_code != 200:
                self.log_test("STRIDE Analysis", False, f"STRIDE coverage failed: HTTP {coverage_response.status_code}")
                return False
            
            coverage_data = coverage_response.json()
            total_threats = coverage_data.get("total_threats", 0)
            mitigation_percentage = coverage_data.get("mitigation_percentage", 0)
            
            print(f"   ✅ STRIDE Coverage: {total_threats} total threats, {mitigation_percentage}% mitigated")
            
            # Test threat mitigation update if we have threats
            if threats:
                threat_id = threats[0].get("id")
                if threat_id:
                    mitigation_response = self.session.patch(
                        f"{self.base_url}/diagrams/{self.test_diagram_id}/stride/threats/{threat_id}",
                        json={"status": "mitigated"}
                    )
                    
                    if mitigation_response.status_code == 200:
                        print(f"   ✅ Threat Mitigation: Successfully updated threat status")
                    else:
                        print(f"   ⚠️ Threat Mitigation: HTTP {mitigation_response.status_code}")
            
            self.log_test("STRIDE Analysis", True, f"STRIDE analysis complete: {len(threats)} threats, {mitigation_percentage}% mitigated")
            return True
            
        except Exception as e:
            self.log_test("STRIDE Analysis", False, f"Request error: {str(e)}")
            return False

    def test_template_and_drag_drop_support(self):
        """TEST 6: Template System and Drag-and-Drop Backend Support"""
        try:
            print("🎯 TEST 6: Template System and Drag-and-Drop Support")
            print("=" * 80)
            
            # Test template listing
            templates_response = self.session.get(f"{self.base_url}/templates")
            
            if templates_response.status_code != 200:
                self.log_test("Template and Drag-Drop Support", False, f"Template listing failed: HTTP {templates_response.status_code}")
                return False
            
            templates = templates_response.json()
            print(f"   ✅ Templates Available: {len(templates)} templates")
            
            # Test auto-layout (drag-drop positioning support)
            if self.test_diagram_id:
                layout_response = self.session.post(f"{self.base_url}/diagrams/{self.test_diagram_id}/auto-layout")
                
                if layout_response.status_code == 200:
                    layout_data = layout_response.json()
                    layout_positions = layout_data.get("layout_positions", {})
                    algorithm = layout_data.get("algorithm", "unknown")
                    
                    print(f"   ✅ Auto-Layout: {len(layout_positions)} positions calculated using {algorithm}")
                else:
                    print(f"   ⚠️ Auto-Layout: HTTP {layout_response.status_code}")
            
            # Test layout algorithms availability
            algorithms_response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}/layout-algorithms")
            
            if algorithms_response.status_code == 200:
                algorithms_data = algorithms_response.json()
                algorithms = algorithms_data.get("algorithms", [])
                print(f"   ✅ Layout Algorithms: {len(algorithms)} algorithms available")
            else:
                print(f"   ⚠️ Layout Algorithms: HTTP {algorithms_response.status_code}")
            
            # Test template application (drag-drop template support)
            if templates and self.test_diagram_id:
                template_id = templates[0].get("id")
                if template_id:
                    apply_response = self.session.post(f"{self.base_url}/templates/{template_id}/apply/{self.test_diagram_id}")
                    
                    if apply_response.status_code == 200:
                        apply_data = apply_response.json()
                        nodes_added = apply_data.get("nodes_added", 0)
                        edges_added = apply_data.get("edges_added", 0)
                        print(f"   ✅ Template Application: {nodes_added} nodes, {edges_added} edges added")
                    else:
                        print(f"   ⚠️ Template Application: HTTP {apply_response.status_code}")
            
            self.log_test("Template and Drag-Drop Support", True, f"Template system operational: {len(templates)} templates available")
            return True
            
        except Exception as e:
            self.log_test("Template and Drag-Drop Support", False, f"Request error: {str(e)}")
            return False

    def test_questionnaire_data_persistence(self):
        """TEST 7: Questionnaire Data Persistence"""
        try:
            print("🎯 TEST 7: Questionnaire Data Persistence")
            print("=" * 80)
            
            if not self.test_diagram_id or not self.test_nodes:
                self.log_test("Questionnaire Data Persistence", False, "No test diagram or nodes available")
                return False
            
            success_count = 0
            
            # Test saving questionnaire data for each node type
            for node_type, node_id in self.test_nodes.items():
                print(f"   Testing {node_type} questionnaire persistence...")
                
                # Create realistic questionnaire data
                if node_type == "WebApp":
                    questionnaire_data = {
                        "responses": {
                            "webapp_authentication": "oauth2",
                            "webapp_encryption": True,
                            "webapp_input_validation": "comprehensive",
                            "webapp_session_management": "secure"
                        },
                        "business_context": {
                            "criticality": "high",
                            "data_classification": "confidential"
                        }
                    }
                elif node_type == "API":
                    questionnaire_data = {
                        "responses": {
                            "api_type": "REST API",
                            "api_auth_method": "OAuth 2.0",
                            "api_rate_limiting": True,
                            "api_input_validation": "comprehensive"
                        },
                        "business_context": {
                            "criticality": "high",
                            "data_classification": "confidential"
                        }
                    }
                elif node_type == "Database":
                    questionnaire_data = {
                        "responses": {
                            "database_authentication": "strong_mfa",
                            "database_encryption_at_rest": "tde_enabled",
                            "database_encryption_in_transit": "ssl_tls_enforced"
                        },
                        "business_context": {
                            "criticality": "critical",
                            "data_classification": "restricted"
                        }
                    }
                
                # Save questionnaire data
                save_response = self.session.post(
                    f"{self.base_url}/diagrams/{self.test_diagram_id}/nodes/{node_id}/questionnaire",
                    json=questionnaire_data
                )
                
                if save_response.status_code == 200:
                    save_data = save_response.json()
                    if save_data.get("success"):
                        print(f"     ✅ {node_type}: Questionnaire data saved successfully")
                        success_count += 1
                    else:
                        print(f"     ❌ {node_type}: Save failed - {save_data.get('message', 'Unknown error')}")
                else:
                    print(f"     ❌ {node_type}: HTTP {save_response.status_code}")
            
            if success_count == len(self.test_nodes):
                self.log_test("Questionnaire Data Persistence", True, f"All {success_count} questionnaires saved successfully")
                return True
            else:
                self.log_test("Questionnaire Data Persistence", False, f"Only {success_count}/{len(self.test_nodes)} saves successful")
                return False
                
        except Exception as e:
            self.log_test("Questionnaire Data Persistence", False, f"Request error: {str(e)}")
            return False

    def cleanup_test_data(self):
        """Clean up test data after testing"""
        try:
            if self.test_diagram_id:
                print("🧹 CLEANUP: Removing test diagram")
                response = self.session.delete(f"{self.base_url}/diagrams/{self.test_diagram_id}")
                if response.status_code == 200:
                    print(f"   ✅ Test diagram {self.test_diagram_id} deleted successfully")
                else:
                    print(f"   ⚠️ Failed to delete test diagram: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ⚠️ Cleanup error: {str(e)}")

    def run_all_tests(self):
        """Run all Security Modeling Platform backend tests"""
        print("🚀 STARTING SECURITY MODELING PLATFORM BACKEND TESTING")
        print("=" * 80)
        print("Testing backend functionality after UI simplification changes:")
        print("1. Core API Health - Verify main endpoints responding")
        print("2. Diagram Management - Creation and retrieval APIs")
        print("3. Node Management - Creation and questionnaire functionality")
        print("4. Vulnerability Analysis - Security analysis for simplified nodes")
        print("5. STRIDE Analysis - Threat analysis functionality")
        print("6. Template System - Drag-and-drop backend support")
        print("7. Data Persistence - Questionnaire data saving")
        print("=" * 80)
        
        tests = [
            self.test_core_api_health,
            self.test_diagram_management_apis,
            self.test_node_creation_and_questionnaires,
            self.test_vulnerability_analysis,
            self.test_stride_analysis,
            self.test_template_and_drag_drop_support,
            self.test_questionnaire_data_persistence,
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
        
        # Summary for Security Modeling Platform backend verification
        if passed == total:
            print("\n🎉 SECURITY MODELING PLATFORM BACKEND VERIFICATION: ALL TESTS PASSED")
            print("✅ Core API health endpoints responding correctly")
            print("✅ Node management and questionnaire functionality working")
            print("✅ Security analysis (vulnerability + STRIDE) operational")
            print("✅ Template system and drag-drop backend support confirmed")
            print("✅ Data persistence working correctly")
            print("✅ UI simplification changes have NO impact on backend functionality")
        else:
            print(f"\n⚠️ SECURITY MODELING PLATFORM BACKEND VERIFICATION: {total-passed} TESTS FAILED")
            print("❌ Some backend functionality may be impacted by UI changes")
            print("❌ Review failed tests above for details")
        
        return passed == total

if __name__ == "__main__":
    tester = SecurityPlatformBackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)