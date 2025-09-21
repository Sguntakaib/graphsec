#!/usr/bin/env python3
"""
Backend API Testing - CRITICAL ISSUES TESTING
Tests the two critical issues reported in the continuation request:

TESTING FOCUS:
🎯 CRITICAL ISSUE 1: VULNERABILITY ANALYSIS FOR API NODES
- Test POST /api/vulnerabilities/analyze/{node_id} with API node data
- Verify no "Cross-Site Request Forgery is not a valid VulnerabilityCategory" error
- Verify that all vulnerability categories are valid enum values

🎯 CRITICAL ISSUE 2: QUESTIONNAIRE SAVE ENDPOINTS
- GET /api/diagrams to get existing diagram
- POST /api/diagrams/{diagram_id}/nodes/{node_id}/questionnaire with sample questionnaire responses
- Verify HTTP 200 response instead of 500 errors

**EXPECTED RESULTS:** 
- Vulnerability analysis should work for API nodes without enum validation errors
- Questionnaire save endpoints should return HTTP 200 without 500 errors
"""

import requests
import json
import uuid
from datetime import datetime, timezone
import sys

# Use the backend URL from frontend/.env with /api suffix
BASE_URL = "https://security-mapper-1.preview.emergentagent.com/api"

class CriticalIssuesTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.test_results = []
        self.test_diagram_id = None
        self.test_node_id = None
        
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

    def create_test_diagram(self):
        """Create a test diagram for testing questionnaire save endpoints"""
        try:
            print("🎯 SETUP: Creating Test Diagram")
            print("=" * 80)
            
            # Create a test diagram
            diagram_data = {
                "title": "Test Diagram for Critical Issues",
                "description": "Test diagram for vulnerability analysis and questionnaire save testing"
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
                
                self.log_test("Create Test Diagram", False, 
                            f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Create Test Diagram", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            self.test_diagram_id = data.get("id")
            
            if not self.test_diagram_id:
                self.log_test("Create Test Diagram", False, "No diagram ID returned")
                return False
            
            print(f"📊 Test Diagram Created:")
            print(f"   Diagram ID: {self.test_diagram_id}")
            print(f"   Title: {data.get('title')}")
            
            # Now add an API node to the diagram
            api_node = {
                "id": f"api-node-{uuid.uuid4().hex[:8]}",
                "type": "Asset",
                "subtype": "API",
                "label": "Test API Node",
                "position": {"x": 200, "y": 100},
                "data": {
                    "criticality": "High",
                    "data_classification": "Confidential"
                }
            }
            
            self.test_node_id = api_node["id"]
            
            # Update diagram with the API node
            updated_diagram = data.copy()
            updated_diagram["nodes"] = [api_node]
            updated_diagram["edges"] = []
            
            response = self.session.put(f"{self.base_url}/diagrams/{self.test_diagram_id}", json=updated_diagram)
            
            if response.status_code != 200:
                self.log_test("Create Test Diagram", False, "Failed to add API node to diagram")
                return False
            
            print(f"   API Node ID: {self.test_node_id}")
            
            self.log_test("Create Test Diagram", True, 
                        f"✅ SUCCESS: Test diagram created with API node")
            
            return True
            
        except Exception as e:
            self.log_test("Create Test Diagram", False, f"Request error: {str(e)}")
            return False

    def test_vulnerability_analysis_api_nodes(self):
        """
        CRITICAL TEST: Test vulnerability analysis for API nodes
        
        This test verifies that:
        1. POST /api/vulnerabilities/analyze/{node_id} works with API node data
        2. No "Cross-Site Request Forgery is not a valid VulnerabilityCategory" error occurs
        3. All vulnerability categories are valid enum values
        """
        try:
            print("🎯 CRITICAL TEST: Vulnerability Analysis for API Nodes")
            print("=" * 80)
            
            if not self.test_node_id:
                self.log_test("Vulnerability Analysis API Nodes", False, "No test node ID available")
                return False
            
            response = self.session.post(f"{self.base_url}/vulnerabilities/analyze/{self.test_node_id}")
            
            print(f"📋 Vulnerability Analysis Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                # Check specifically for the Cross-Site Request Forgery error
                if "Cross-Site Request Forgery is not a valid VulnerabilityCategory" in str(error_detail):
                    self.log_test("Vulnerability Analysis API Nodes", False, 
                                f"❌ CRITICAL ERROR: Cross-Site Request Forgery enum validation error still present: {error_detail}")
                    return False
                
                self.log_test("Vulnerability Analysis API Nodes", False, 
                            f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Vulnerability Analysis API Nodes", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            # Verify response structure
            if not data.get("success"):
                self.log_test("Vulnerability Analysis API Nodes", False, 
                            f"Analysis failed: {data.get('message', 'Unknown error')}")
                return False
            
            vulnerabilities = data.get("vulnerabilities", [])
            analysis_summary = data.get("analysis_summary", {})
            
            print(f"📊 Vulnerability Analysis Results:")
            print(f"   Success: {data.get('success')}")
            print(f"   Node ID: {data.get('node_id')}")
            print(f"   Node Type: {data.get('node_type')}")
            print(f"   Vulnerabilities found: {len(vulnerabilities)}")
            print(f"   Analysis summary: {analysis_summary}")
            
            # Check for any vulnerability category validation errors in the vulnerabilities
            category_errors = []
            for vuln in vulnerabilities:
                category = vuln.get("category")
                if not category:
                    category_errors.append("Missing category")
                elif "not a valid" in str(category):
                    category_errors.append(f"Invalid category: {category}")
            
            if category_errors:
                self.log_test("Vulnerability Analysis API Nodes", False, 
                            f"Vulnerability category errors: {category_errors}")
                return False
            
            # Show sample vulnerabilities
            if vulnerabilities:
                print(f"   Sample vulnerabilities:")
                for i, vuln in enumerate(vulnerabilities[:3]):  # Show first 3
                    print(f"     {i+1}. {vuln.get('title', 'Unknown')} - {vuln.get('category', 'Unknown')} - {vuln.get('severity', 'Unknown')}")
            
            self.log_test("Vulnerability Analysis API Nodes", True, 
                        f"✅ SUCCESS: Vulnerability analysis completed for API node, {len(vulnerabilities)} vulnerabilities found, no enum validation errors")
            
            return True
            
        except Exception as e:
            self.log_test("Vulnerability Analysis API Nodes", False, f"Request error: {str(e)}")
            return False

    def test_questionnaire_save_endpoints(self):
        """
        CRITICAL TEST: Test questionnaire save endpoints
        
        This test verifies that:
        1. GET /api/diagrams works to get existing diagram
        2. POST /api/diagrams/{diagram_id}/nodes/{node_id}/questionnaire works without 500 errors
        3. Questionnaire responses are properly saved
        """
        try:
            print("🎯 CRITICAL TEST: Questionnaire Save Endpoints")
            print("=" * 80)
            
            # First, verify we can get diagrams
            response = self.session.get(f"{self.base_url}/diagrams")
            
            print(f"📋 Get Diagrams Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("Questionnaire Save Endpoints", False, 
                            f"Failed to get diagrams - HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                diagrams_data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Questionnaire Save Endpoints", False, 
                            f"Invalid JSON response from diagrams endpoint: {str(e)}")
                return False
            
            print(f"📊 Diagrams Retrieved: {len(diagrams_data)} diagrams found")
            
            if not self.test_diagram_id or not self.test_node_id:
                self.log_test("Questionnaire Save Endpoints", False, 
                            "No test diagram or node ID available")
                return False
            
            # Now test the questionnaire save endpoint
            questionnaire_data = {
                "responses": {
                    "api_type": "REST API",
                    "authentication_method": "oauth2",
                    "encryption_enabled": True,
                    "input_validation": "comprehensive",
                    "rate_limiting": True,
                    "logging_enabled": True
                },
                "business_context": {
                    "criticality": "high",
                    "data_classification": "confidential",
                    "compliance_requirements": ["GDPR", "SOX"]
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/diagrams/{self.test_diagram_id}/nodes/{self.test_node_id}/questionnaire",
                json=questionnaire_data
            )
            
            print(f"📋 Questionnaire Save Response Status: HTTP {response.status_code}")
            
            if response.status_code == 500:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("Questionnaire Save Endpoints", False, 
                            f"❌ CRITICAL ERROR: HTTP 500 error still present: {error_detail}")
                return False
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("Questionnaire Save Endpoints", False, 
                            f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                save_data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Questionnaire Save Endpoints", False, 
                            f"Invalid JSON response from questionnaire save: {str(e)}")
                return False
            
            print(f"📊 Questionnaire Save Results:")
            print(f"   Success: {save_data.get('success', False)}")
            print(f"   Message: {save_data.get('message', 'No message')}")
            print(f"   Diagram ID: {self.test_diagram_id}")
            print(f"   Node ID: {self.test_node_id}")
            
            if not save_data.get("success"):
                self.log_test("Questionnaire Save Endpoints", False, 
                            f"Questionnaire save failed: {save_data.get('message', 'Unknown error')}")
                return False
            
            self.log_test("Questionnaire Save Endpoints", True, 
                        f"✅ SUCCESS: Questionnaire save endpoint working, no 500 errors")
            
            return True
            
        except Exception as e:
            self.log_test("Questionnaire Save Endpoints", False, f"Request error: {str(e)}")
            return False

    def test_canvas_node_detection(self):
        """
        CRITICAL TEST: Test canvas node detection endpoint
        
        This test verifies that:
        1. POST /api/questionnaires/canvas/detect-nodes works with sample canvas nodes
        2. Detects different node types (Database, API, WebApp)
        3. Provides reuse recommendations correctly
        """
        try:
            print("🎯 CRITICAL TEST: Canvas Node Detection")
            print("=" * 80)
            
            # Test Database node detection
            database_detection_request = {
                "canvas_nodes": self.sample_canvas_nodes,
                "target_type": "Database"
            }
            
            response = self.session.post(
                f"{self.base_url}/questionnaires/canvas/detect-nodes",
                json=database_detection_request
            )
            
            print(f"📋 Database Detection Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("Canvas Node Detection", False, 
                            f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                db_data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Canvas Node Detection", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            # Verify Database detection results
            if not db_data.get("success"):
                self.log_test("Canvas Node Detection", False, 
                            "Database detection response success is false")
                return False
            
            db_existing_nodes = db_data.get("existing_nodes", [])
            db_existing_count = db_data.get("existing_nodes_count", 0)
            db_has_existing = db_data.get("has_existing_nodes", False)
            db_reuse_recommended = db_data.get("reuse_recommended", False)
            
            # We have 2 Database nodes in sample data
            expected_db_count = 2
            if db_existing_count != expected_db_count:
                self.log_test("Canvas Node Detection", False, 
                            f"Database detection count mismatch: {db_existing_count} vs {expected_db_count}")
                return False
            
            if not db_has_existing:
                self.log_test("Canvas Node Detection", False, 
                            "Database detection should show has_existing_nodes=true")
                return False
            
            if not db_reuse_recommended:
                self.log_test("Canvas Node Detection", False, 
                            "Database detection should recommend reuse")
                return False
            
            print(f"📊 Database Detection Results:")
            print(f"   Target type: {db_data.get('target_type')}")
            print(f"   Existing nodes count: {db_existing_count}")
            print(f"   Has existing nodes: {db_has_existing}")
            print(f"   Reuse recommended: {db_reuse_recommended}")
            print(f"   Detected nodes: {[node.get('label', 'Unknown') for node in db_existing_nodes]}")
            
            # Test API node detection
            api_detection_request = {
                "canvas_nodes": self.sample_canvas_nodes,
                "target_type": "API"
            }
            
            response = self.session.post(
                f"{self.base_url}/questionnaires/canvas/detect-nodes",
                json=api_detection_request
            )
            
            if response.status_code == 200:
                api_data = response.json()
                api_existing_count = api_data.get("existing_nodes_count", 0)
                print(f"📊 API Detection Results:")
                print(f"   API nodes detected: {api_existing_count}")
            
            # Test WebApp node detection
            webapp_detection_request = {
                "canvas_nodes": self.sample_canvas_nodes,
                "target_type": "WebApp"
            }
            
            response = self.session.post(
                f"{self.base_url}/questionnaires/canvas/detect-nodes",
                json=webapp_detection_request
            )
            
            if response.status_code == 200:
                webapp_data = response.json()
                webapp_existing_count = webapp_data.get("existing_nodes_count", 0)
                print(f"📊 WebApp Detection Results:")
                print(f"   WebApp nodes detected: {webapp_existing_count}")
            
            self.log_test("Canvas Node Detection", True, 
                        f"✅ SUCCESS: Database detection found {db_existing_count} nodes with reuse recommendation")
            
            return True
            
        except Exception as e:
            self.log_test("Canvas Node Detection", False, f"Request error: {str(e)}")
            return False

    def test_enhanced_conditional_questions(self):
        """
        CRITICAL TEST: Test enhanced conditional questions endpoint
        
        This test verifies that:
        1. POST /api/questionnaires/API/enhanced/conditional works with API type responses
        2. Database reuse decision processing works
        3. Web interface exposure triggers work
        4. Conditional questions are added based on responses
        """
        try:
            print("🎯 CRITICAL TEST: Enhanced Conditional Questions")
            print("=" * 80)
            
            # Test with REST API type response
            rest_api_request = {
                "responses": {
                    "api_type": "REST API",
                    "database_type": "MySQL",
                    "api_web_interface_exposure": "yes",
                    "api_external_services": "yes"
                },
                "canvas_nodes": self.sample_canvas_nodes,
                "level": "basic"
            }
            
            response = self.session.post(
                f"{self.base_url}/questionnaires/API/enhanced/conditional",
                json=rest_api_request
            )
            
            print(f"📋 REST API Conditional Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("Enhanced Conditional Questions", False, 
                            f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                rest_data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Enhanced Conditional Questions", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            # Verify REST API conditional response
            if not rest_data.get("success"):
                self.log_test("Enhanced Conditional Questions", False, 
                            "REST API conditional response success is false")
                return False
            
            rest_questions = rest_data.get("questions", [])
            rest_triggers = rest_data.get("triggers_detected", {})
            
            print(f"📊 REST API Conditional Results:")
            print(f"   Success: {rest_data.get('success')}")
            print(f"   Node subtype: {rest_data.get('node_subtype')}")
            print(f"   Total questions: {rest_data.get('total_questions')}")
            print(f"   Questions returned: {len(rest_questions)}")
            print(f"   Triggers detected: {rest_triggers}")
            
            # Test with GraphQL API type response
            graphql_api_request = {
                "responses": {
                    "api_type": "GraphQL API",
                    "database_reuse_decision": "reuse_existing",
                    "api_web_interface_exposure": "no"
                },
                "canvas_nodes": self.sample_canvas_nodes,
                "level": "basic"
            }
            
            response = self.session.post(
                f"{self.base_url}/questionnaires/API/enhanced/conditional",
                json=graphql_api_request
            )
            
            if response.status_code == 200:
                graphql_data = response.json()
                graphql_questions = graphql_data.get("questions", [])
                graphql_reuse_info = graphql_data.get("reuse_info", {})
                
                print(f"📊 GraphQL API Conditional Results:")
                print(f"   Questions returned: {len(graphql_questions)}")
                print(f"   Reuse info: {bool(graphql_reuse_info)}")
                print(f"   Database reuse decision processed: {'database_reuse_decision' in graphql_api_request['responses']}")
            
            # Test with SOAP API type response
            soap_api_request = {
                "responses": {
                    "api_type": "SOAP API",
                    "api_external_services": "Authentication,Payment"
                },
                "canvas_nodes": [],
                "level": "advanced"
            }
            
            response = self.session.post(
                f"{self.base_url}/questionnaires/API/enhanced/conditional",
                json=soap_api_request
            )
            
            if response.status_code == 200:
                soap_data = response.json()
                soap_questions = soap_data.get("questions", [])
                
                print(f"📊 SOAP API Conditional Results:")
                print(f"   Questions returned: {len(soap_questions)}")
            
            self.log_test("Enhanced Conditional Questions", True, 
                        f"✅ SUCCESS: Conditional questions working for REST API ({len(rest_questions)} questions), triggers detected")
            
            return True
            
        except Exception as e:
            self.log_test("Enhanced Conditional Questions", False, f"Request error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all enhanced API questionnaire tests"""
        print("🚀 STARTING ENHANCED API NODE QUESTIONNAIRE SYSTEM TESTING")
        print("=" * 80)
        print("Testing the new enhanced API Node questionnaire system with dynamic questions")
        print("=" * 80)
        
        tests = [
            self.test_health_check,
            self.test_enhanced_questionnaire_basic,
            self.test_enhanced_questionnaire_with_canvas_nodes,
            self.test_external_services_categories,
            self.test_canvas_node_detection,
            self.test_enhanced_conditional_questions,
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
    tester = EnhancedAPIQuestionnaireTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)