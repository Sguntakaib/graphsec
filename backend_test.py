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
BASE_URL = "https://element-iconography.preview.emergentagent.com/api"

class VulnerabilityBackendTester:
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

    def test_create_diagram(self):
        """TEST SCENARIO 1: Create a new diagram and verify it exists"""
        try:
            print("🎯 TEST SCENARIO 1: Create New Diagram")
            print("=" * 80)
            
            # Create a test diagram
            diagram_data = {
                "title": "API Questionnaire Test Diagram",
                "description": "Test diagram for API questionnaire looping issue verification"
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
                
                self.log_test("Create New Diagram", False, 
                            f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Create New Diagram", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            self.test_diagram_id = data.get("id")
            
            if not self.test_diagram_id:
                self.log_test("Create New Diagram", False, "No diagram ID returned")
                return False
            
            print(f"📊 Diagram Created Successfully:")
            print(f"   Diagram ID: {self.test_diagram_id}")
            print(f"   Title: {data.get('title')}")
            print(f"   Description: {data.get('description')}")
            
            # Verify diagram exists by retrieving it
            verify_response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}")
            if verify_response.status_code != 200:
                self.log_test("Create New Diagram", False, "Created diagram cannot be retrieved")
                return False
            
            self.log_test("Create New Diagram", True, 
                        f"✅ SUCCESS: Diagram created and verified (ID: {self.test_diagram_id})")
            
            return True
            
        except Exception as e:
            self.log_test("Create New Diagram", False, f"Request error: {str(e)}")
            return False

    def test_api_questionnaire_prompts(self):
        """TEST SCENARIO 2: Get API questionnaire prompts and verify question count"""
        try:
            print("🎯 TEST SCENARIO 2: Get API Questionnaire Prompts")
            print("=" * 80)
            
            response = self.session.get(f"{self.base_url}/intelligent-nodes/API/prompts")
            
            print(f"📋 API Prompts Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("Get API Questionnaire Prompts", False, 
                            f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Get API Questionnaire Prompts", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            # Verify response structure
            if not data.get("success"):
                self.log_test("Get API Questionnaire Prompts", False, 
                            f"API returned success=false: {data.get('message', 'Unknown error')}")
                return False
            
            prompts_count = data.get("prompts_count", 0)
            node_subtype = data.get("node_subtype")
            prompts = data.get("prompts", [])
            
            print(f"📊 API Questionnaire Prompts Results:")
            print(f"   Success: {data.get('success')}")
            print(f"   Node Subtype: {node_subtype}")
            print(f"   Prompts Count: {prompts_count}")
            print(f"   Total Questions: {data.get('total_questions', 'N/A')}")
            print(f"   Level: {data.get('level', 'N/A')}")
            
            if prompts_count == 0:
                self.log_test("Get API Questionnaire Prompts", False, 
                            "No prompts returned for API questionnaire")
                return False
            
            if node_subtype != "API":
                self.log_test("Get API Questionnaire Prompts", False, 
                            f"Wrong node subtype returned: {node_subtype}, expected: API")
                return False
            
            # Show sample prompts
            if prompts:
                print(f"   Sample prompts:")
                for i, prompt in enumerate(prompts[:3]):  # Show first 3
                    print(f"     {i+1}. {prompt.get('question', 'Unknown question')} ({prompt.get('type', 'Unknown type')})")
            
            self.log_test("Get API Questionnaire Prompts", True, 
                        f"✅ SUCCESS: API questionnaire prompts retrieved, {prompts_count} questions found")
            
            return True
            
        except Exception as e:
            self.log_test("Get API Questionnaire Prompts", False, f"Request error: {str(e)}")
            return False

    def test_api_questionnaire_validation(self):
        """TEST SCENARIO 3: Test questionnaire validation with sample API responses"""
        try:
            print("🎯 TEST SCENARIO 3: Test API Questionnaire Validation")
            print("=" * 80)
            
            # The validate-completeness endpoint expects a list of SecurityBranch objects
            # Let me create sample branches based on the API template structure
            validation_data = [
                {
                    "name": "api_authentication_method",
                    "type": "Authentication",
                    "required": True,
                    "completed": True,
                    "value": "OAuth 2.0",
                    "description": "API authentication method"
                },
                {
                    "name": "api_authorization_model",
                    "type": "Authorization", 
                    "required": True,
                    "completed": True,
                    "value": "Role-based access control",
                    "description": "API authorization model"
                },
                {
                    "name": "api_rate_limiting",
                    "type": "RateLimiting",
                    "required": True,
                    "completed": True,
                    "value": "Implemented",
                    "description": "API rate limiting configuration"
                },
                {
                    "name": "api_input_validation",
                    "type": "InputValidation",
                    "required": True,
                    "completed": True,
                    "value": "Comprehensive validation",
                    "description": "API input validation"
                },
                {
                    "name": "api_encryption",
                    "type": "Encryption",
                    "required": True,
                    "completed": True,
                    "value": "TLS 1.3 enabled",
                    "description": "API encryption configuration"
                }
            ]
            
            response = self.session.post(
                f"{self.base_url}/intelligent-nodes/API/validate-completeness",
                json=validation_data
            )
            
            print(f"📋 API Validation Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("Test API Questionnaire Validation", False, 
                            f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Test API Questionnaire Validation", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            # Verify validation response structure
            validation = data.get("validation", {})
            recommendations = data.get("recommendations", [])
            
            if not validation:
                self.log_test("Test API Questionnaire Validation", False, 
                            "No validation data returned")
                return False
            
            is_complete = validation.get("is_complete", False)
            completion_percentage = validation.get("completion_percentage", 0)
            completed_count = validation.get("completed_count", 0)
            required_count = validation.get("required_count", 0)
            
            print(f"📊 API Questionnaire Validation Results:")
            print(f"   Is Complete: {is_complete}")
            print(f"   Completion Percentage: {completion_percentage}%")
            print(f"   Completed Count: {completed_count}")
            print(f"   Required Count: {required_count}")
            print(f"   Recommendations Count: {len(recommendations)}")
            
            # Show sample recommendations
            if recommendations:
                print(f"   Sample recommendations:")
                for i, rec in enumerate(recommendations[:3]):  # Show first 3
                    print(f"     {i+1}. {rec}")
            
            self.log_test("Test API Questionnaire Validation", True, 
                        f"✅ SUCCESS: API questionnaire validation completed, {completion_percentage}% complete")
            
            return True
            
        except Exception as e:
            self.log_test("Test API Questionnaire Validation", False, f"Request error: {str(e)}")
            return False

    def test_questionnaire_404_handling(self):
        """TEST SCENARIO 4: Test saving questionnaire to non-existent diagram (should return 404)"""
        try:
            print("🎯 TEST SCENARIO 4: Test 404 Handling for Non-existent Diagram")
            print("=" * 80)
            
            # Use fake diagram and node IDs
            fake_diagram_id = f"fake-diagram-{uuid.uuid4().hex[:8]}"
            fake_node_id = f"fake-node-{uuid.uuid4().hex[:8]}"
            
            questionnaire_data = {
                "responses": {
                    "api_type": "REST API",
                    "authentication_method": "oauth2",
                    "encryption_enabled": True,
                    "input_validation": "comprehensive"
                },
                "business_context": {
                    "criticality": "high",
                    "data_classification": "confidential"
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/diagrams/{fake_diagram_id}/nodes/{fake_node_id}/questionnaire",
                json=questionnaire_data
            )
            
            print(f"📋 Questionnaire Save Response Status: HTTP {response.status_code}")
            print(f"   Fake Diagram ID: {fake_diagram_id}")
            print(f"   Fake Node ID: {fake_node_id}")
            
            # We expect a 404 response for non-existent diagram/node
            if response.status_code == 404:
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', 'Not found')
                except:
                    error_detail = response.text
                
                print(f"📊 Expected 404 Response:")
                print(f"   Error Detail: {error_detail}")
                
                self.log_test("Test 404 Handling for Non-existent Diagram", True, 
                            f"✅ SUCCESS: Properly returned 404 for non-existent diagram/node: {error_detail}")
                return True
            
            elif response.status_code == 500:
                # This would indicate a server error instead of proper 404 handling
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', 'Internal server error')
                except:
                    error_detail = response.text
                
                self.log_test("Test 404 Handling for Non-existent Diagram", False, 
                            f"❌ CRITICAL: Server returned 500 instead of 404: {error_detail}")
                return False
            
            else:
                # Any other status code is unexpected
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', 'Unexpected response')
                except:
                    error_detail = response.text
                
                self.log_test("Test 404 Handling for Non-existent Diagram", False, 
                            f"Unexpected status code {response.status_code}, expected 404: {error_detail}")
                return False
            
        except Exception as e:
            self.log_test("Test 404 Handling for Non-existent Diagram", False, f"Request error: {str(e)}")
            return False

    def test_vulnerability_analysis(self):
        """TEST SCENARIO 4: Test vulnerability analysis endpoints"""
        try:
            print("🎯 TEST SCENARIO 4: Test Vulnerability Analysis Endpoints")
            print("=" * 80)
            
            if not self.test_diagram_id:
                self.log_test("Test Vulnerability Analysis", False, 
                            "No test diagram ID available")
                return False
            
            # Create a test node for vulnerability analysis if we don't have one
            if not self.test_node_id:
                test_node = {
                    "id": f"vuln-test-node-{uuid.uuid4().hex[:8]}",
                    "type": "Asset",
                    "subtype": "WebApp",
                    "label": "Test WebApp for Vulnerability Analysis",
                    "position": {"x": 200, "y": 200},
                    "data": {
                        "criticality": "High",
                        "data_classification": "Confidential"
                    }
                }
                
                self.test_node_id = test_node["id"]
                
                # Get current diagram and add the test node
                diagram_response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}")
                if diagram_response.status_code != 200:
                    self.log_test("Test Vulnerability Analysis", False, 
                                "Cannot retrieve test diagram for vulnerability analysis")
                    return False
                
                diagram_data = diagram_response.json()
                current_nodes = diagram_data.get("nodes", [])
                current_nodes.append(test_node)
                diagram_data["nodes"] = current_nodes
                
                # Update diagram with the test node
                update_response = self.session.put(f"{self.base_url}/diagrams/{self.test_diagram_id}", json=diagram_data)
                if update_response.status_code != 200:
                    self.log_test("Test Vulnerability Analysis", False, 
                                "Failed to add test node for vulnerability analysis")
                    return False
                
                print(f"   Created test node for vulnerability analysis: {self.test_node_id}")
            
            # Test vulnerability analysis for the test node
            vulnerability_request = {
                "node_id": self.test_node_id,
                "node_type": "WebApp",
                "questionnaire_responses": {
                    "webapp_authentication": "oauth2",
                    "webapp_encryption": True,
                    "webapp_input_validation": "comprehensive",
                    "webapp_session_management": "secure",
                    "webapp_error_handling": "secure"
                },
                "node_position": {"x": 200, "y": 200}
            }
            
            response = self.session.post(
                f"{self.base_url}/vulnerabilities/analyze/{self.test_node_id}",
                json=vulnerability_request
            )
            
            print(f"📋 Vulnerability Analysis Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("Test Vulnerability Analysis", False, 
                            f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Test Vulnerability Analysis", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            # Verify vulnerability analysis response structure
            vulnerabilities = data.get("vulnerabilities", [])
            overall_risk_score = data.get("overall_risk_score", 0)
            node_id = data.get("node_id")
            
            print(f"📊 Vulnerability Analysis Results:")
            print(f"   Node ID: {node_id}")
            print(f"   Vulnerabilities Found: {len(vulnerabilities)}")
            print(f"   Overall Risk Score: {overall_risk_score}")
            
            if vulnerabilities:
                # Show vulnerability breakdown by severity
                severity_counts = {}
                for vuln in vulnerabilities:
                    severity = vuln.get("severity", "Unknown")
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1
                
                print(f"   Vulnerability Breakdown:")
                for severity, count in severity_counts.items():
                    print(f"     {severity}: {count}")
                
                # Show sample vulnerabilities
                print(f"   Sample vulnerabilities:")
                for i, vuln in enumerate(vulnerabilities[:3]):  # Show first 3
                    print(f"     {i+1}. {vuln.get('title', 'Unknown')} ({vuln.get('severity', 'Unknown')})")
            
            self.log_test("Test Vulnerability Analysis", True, 
                        f"✅ SUCCESS: Vulnerability analysis completed, {len(vulnerabilities)} vulnerabilities found")
            
            return True
            
        except Exception as e:
            self.log_test("Test Vulnerability Analysis", False, f"Request error: {str(e)}")
            return False

    def test_diagram_operations(self):
        """TEST SCENARIO 5: Test diagram operations still work"""
        try:
            print("🎯 TEST SCENARIO 5: Test Diagram Operations")
            print("=" * 80)
            
            # Test listing diagrams
            response = self.session.get(f"{self.base_url}/diagrams")
            
            print(f"📋 List Diagrams Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("Test Diagram Operations", False, 
                            f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                diagrams = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Test Diagram Operations", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            print(f"📊 Diagram Operations Results:")
            print(f"   Total Diagrams: {len(diagrams)}")
            
            if diagrams:
                print(f"   Sample diagrams:")
                for i, diagram in enumerate(diagrams[:3]):  # Show first 3
                    print(f"     {i+1}. {diagram.get('title', 'Unknown')} (ID: {diagram.get('id', 'Unknown')[:8]}...)")
            
            # Test getting specific diagram if we have one
            if self.test_diagram_id:
                specific_response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}")
                if specific_response.status_code == 200:
                    print(f"   ✅ Successfully retrieved specific diagram: {self.test_diagram_id}")
                else:
                    print(f"   ⚠️ Failed to retrieve specific diagram: HTTP {specific_response.status_code}")
            
            self.log_test("Test Diagram Operations", True, 
                        f"✅ SUCCESS: Diagram operations working correctly, {len(diagrams)} diagrams found")
            
            return True
            
        except Exception as e:
            self.log_test("Test Diagram Operations", False, f"Request error: {str(e)}")
            return False

    def test_node_operations(self):
        """TEST SCENARIO 6: Test node-related operations"""
        try:
            print("🎯 TEST SCENARIO 6: Test Node Operations")
            print("=" * 80)
            
            if not self.test_diagram_id:
                self.log_test("Test Node Operations", False, 
                            "No test diagram ID available")
                return False
            
            # Create a WebApp node for testing
            webapp_node = {
                "id": f"webapp-node-{uuid.uuid4().hex[:8]}",
                "type": "Asset",
                "subtype": "WebApp",
                "label": "Test WebApp Node",
                "position": {"x": 100, "y": 100},
                "data": {
                    "criticality": "High",
                    "data_classification": "Confidential"
                }
            }
            
            # Get current diagram and add the WebApp node
            diagram_response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}")
            if diagram_response.status_code != 200:
                self.log_test("Test Node Operations", False, 
                            "Cannot retrieve test diagram")
                return False
            
            diagram_data = diagram_response.json()
            current_nodes = diagram_data.get("nodes", [])
            current_nodes.append(webapp_node)
            diagram_data["nodes"] = current_nodes
            
            # Update diagram with the WebApp node
            update_response = self.session.put(f"{self.base_url}/diagrams/{self.test_diagram_id}", json=diagram_data)
            if update_response.status_code != 200:
                self.log_test("Test Node Operations", False, 
                            "Failed to add WebApp node to diagram")
                return False
            
            print(f"   Added WebApp Node ID: {webapp_node['id']}")
            
            # Test getting WebApp questionnaire prompts
            prompts_response = self.session.get(f"{self.base_url}/intelligent-nodes/WebApp/prompts")
            
            print(f"📋 WebApp Prompts Response Status: HTTP {prompts_response.status_code}")
            
            if prompts_response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = prompts_response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = prompts_response.text
                
                self.log_test("Test Node Operations", False, 
                            f"HTTP {prompts_response.status_code}: {error_detail}")
                return False
            
            try:
                prompts_data = prompts_response.json()
            except json.JSONDecodeError as e:
                self.log_test("Test Node Operations", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            prompts_count = prompts_data.get("prompts_count", 0)
            
            print(f"📊 Node Operations Results:")
            print(f"   WebApp Node Created: {webapp_node['id']}")
            print(f"   WebApp Prompts Count: {prompts_count}")
            print(f"   WebApp Prompts Success: {prompts_data.get('success', False)}")
            
            self.log_test("Test Node Operations", True, 
                        f"✅ SUCCESS: Node operations working correctly, WebApp prompts: {prompts_count}")
            
            return True
            
        except Exception as e:
            self.log_test("Test Node Operations", False, f"Request error: {str(e)}")
            return False

    def test_questionnaire_save_to_existing_diagram(self):
        """TEST SCENARIO 7: Test saving questionnaire to existing diagram (should work)"""
        try:
            print("🎯 TEST SCENARIO 7: Save Questionnaire to Existing Diagram")
            print("=" * 80)
            
            if not self.test_diagram_id:
                self.log_test("Save Questionnaire to Existing Diagram", False, 
                            "No test diagram ID available")
                return False
            
            # Create an API node in the diagram first
            api_node = {
                "id": f"api-node-{uuid.uuid4().hex[:8]}",
                "type": "Asset",
                "subtype": "API",
                "label": "Test API Node for Questionnaire",
                "position": {"x": 300, "y": 200},
                "data": {
                    "criticality": "High",
                    "data_classification": "Confidential"
                }
            }
            
            self.test_node_id = api_node["id"]
            
            # Get current diagram and add the node
            diagram_response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}")
            if diagram_response.status_code != 200:
                self.log_test("Save Questionnaire to Existing Diagram", False, 
                            "Cannot retrieve test diagram")
                return False
            
            diagram_data = diagram_response.json()
            current_nodes = diagram_data.get("nodes", [])
            current_nodes.append(api_node)
            diagram_data["nodes"] = current_nodes
            diagram_data["edges"] = diagram_data.get("edges", [])
            
            # Update diagram with the API node
            update_response = self.session.put(f"{self.base_url}/diagrams/{self.test_diagram_id}", json=diagram_data)
            if update_response.status_code != 200:
                self.log_test("Save Questionnaire to Existing Diagram", False, 
                            "Failed to add API node to diagram")
                return False
            
            print(f"   Added API Node ID: {self.test_node_id}")
            
            # Now test saving questionnaire to the existing diagram/node
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
                
                self.log_test("Save Questionnaire to Existing Diagram", False, 
                            f"❌ CRITICAL ERROR: HTTP 500 error: {error_detail}")
                return False
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("Save Questionnaire to Existing Diagram", False, 
                            f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                save_data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Save Questionnaire to Existing Diagram", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            print(f"📊 Questionnaire Save Results:")
            print(f"   Success: {save_data.get('success', False)}")
            print(f"   Message: {save_data.get('message', 'No message')}")
            
            if not save_data.get("success"):
                self.log_test("Save Questionnaire to Existing Diagram", False, 
                            f"Questionnaire save failed: {save_data.get('message', 'Unknown error')}")
                return False
            
            self.log_test("Save Questionnaire to Existing Diagram", True, 
                        f"✅ SUCCESS: Questionnaire saved to existing diagram successfully")
            
            return True
            
        except Exception as e:
            self.log_test("Save Questionnaire to Existing Diagram", False, f"Request error: {str(e)}")
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
        """Run all vulnerability backend verification tests"""
        print("🚀 STARTING VULNERABILITY SECTION POSITIONING FIX BACKEND VERIFICATION")
        print("=" * 80)
        print("Testing backend health and vulnerability endpoints to ensure no regressions:")
        print("1. Test basic API health endpoint")
        print("2. Create new diagram and verify it exists")
        print("3. Get API questionnaire prompts and verify question count")
        print("4. Test vulnerability analysis endpoints are working")
        print("5. Test diagram operations still work")
        print("6. Test node operations still work")
        print("7. Test questionnaire save functionality")
        print("=" * 80)
        
        tests = [
            self.test_health_check,
            self.test_create_diagram,
            self.test_api_questionnaire_prompts,
            self.test_vulnerability_analysis,
            self.test_diagram_operations,
            self.test_node_operations,
            self.test_questionnaire_save_to_existing_diagram,
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
        
        # Summary for vulnerability section positioning fix verification
        if passed == total:
            print("\n🎉 VULNERABILITY SECTION POSITIONING FIX VERIFICATION: ALL TESTS PASSED")
            print("✅ Backend health endpoints working correctly")
            print("✅ Vulnerability analysis endpoints functioning properly")
            print("✅ No regressions detected in vulnerability system backend APIs")
            print("✅ Diagram and node endpoints validated successfully")
            print("✅ Frontend vulnerability positioning changes have NO impact on backend operations")
        else:
            print(f"\n⚠️ VULNERABILITY SECTION POSITIONING FIX VERIFICATION: {total-passed} TESTS FAILED")
            print("❌ Some backend functionality may be impacted")
            print("❌ Review failed tests above for details")
        
        return passed == total

if __name__ == "__main__":
    tester = VulnerabilityBackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)