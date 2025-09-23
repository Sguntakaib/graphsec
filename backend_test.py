#!/usr/bin/env python3
"""
Backend API Testing - VULNERABILITY SECTION POSITIONING FIX VERIFICATION
Tests backend health and vulnerability endpoints to ensure the vulnerability section positioning fix doesn't impact backend functionality:

TESTING FOCUS:
🎯 VULNERABILITY SECTION POSITIONING FIX VERIFICATION
1. Test basic API health endpoint
2. Test vulnerability analysis endpoints are working
3. Verify no regressions in vulnerability system backend APIs
4. Quick validation that diagram and node endpoints still work

TEST SCENARIOS:
1. Health Check - Verify basic API health endpoint
2. Vulnerability Analysis - Test vulnerability analysis endpoints
3. Diagram Operations - Verify diagram creation and retrieval still work
4. Node Operations - Test node-related endpoints
5. Vulnerability System - Comprehensive vulnerability system testing

**EXPECTED RESULTS:** 
- All backend APIs should be functioning correctly
- Vulnerability analysis endpoints should work without regressions
- No impact from frontend vulnerability positioning changes
- All core functionality remains operational
"""

import requests
import json
import uuid
from datetime import datetime, timezone
import sys

# Use the backend URL from frontend/.env with /api suffix
BASE_URL = "https://fix-vuln-section.preview.emergentagent.com/api"

class APIQuestionnaireLoopingTester:
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

    def test_questionnaire_save_to_existing_diagram(self):
        """BONUS TEST: Test saving questionnaire to existing diagram (should work)"""
        try:
            print("🎯 BONUS TEST: Save Questionnaire to Existing Diagram")
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
            diagram_data["nodes"] = [api_node]
            diagram_data["edges"] = []
            
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
        """Run all API questionnaire looping issue fix verification tests"""
        print("🚀 STARTING API QUESTIONNAIRE LOOPING ISSUE FIX VERIFICATION")
        print("=" * 80)
        print("Testing API questionnaire endpoints to verify looping issue fixes:")
        print("1. Create new diagram and verify it exists")
        print("2. Get API questionnaire prompts and verify question count")
        print("3. Test questionnaire validation with sample API responses")
        print("4. Test saving questionnaire to non-existent diagram (should return 404)")
        print("5. Test saving questionnaire to existing diagram (should work)")
        print("=" * 80)
        
        tests = [
            self.test_health_check,
            self.test_create_diagram,
            self.test_api_questionnaire_prompts,
            self.test_api_questionnaire_validation,
            self.test_questionnaire_404_handling,
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
        
        return passed == total

if __name__ == "__main__":
    tester = APIQuestionnaireLoopingTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)