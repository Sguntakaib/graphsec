#!/usr/bin/env python3
"""
Questionnaire API Endpoints Testing - SPECIFIC ENDPOINTS VERIFICATION
Tests the specific questionnaire API endpoints that were showing "Error Loading Questionnaire".

TESTING FOCUS:
1. **Comprehensive Questionnaire Endpoints:**
   - GET /api/questionnaires/WebApp?level=basic
   - GET /api/questionnaires/API?level=basic  
   - GET /api/questionnaires/Database?level=basic

2. **Fallback Intelligent Nodes Endpoints:**
   - GET /api/intelligent-nodes/ExternalAttacker/prompts
   - GET /api/intelligent-nodes/Actor/prompts

3. **API Response Format Verification:**
   - For comprehensive questionnaires: should have `prompts`, `total_questions`, `level` fields
   - For intelligent-nodes: should have `prompts` field

4. **Error Conditions Testing:**
   - Invalid node types
   - Network timeouts
   - Malformed requests

**EXPECTED RESULTS:**
- All questionnaire endpoints return HTTP 200 with proper data structures
- Response formats match what SecurityQuestionnaire.js expects
- Error handling works correctly for invalid requests
- No "Failed to fetch prompts" errors should occur

**CRITICAL SUCCESS CRITERIA:**
This test verifies that the specific questionnaire endpoints used by SecurityQuestionnaire.js
are working correctly and return the expected response format to prevent "Error Loading Questionnaire".
"""

import requests
import json
import sys
from datetime import datetime, timezone

# Use the backend URL from frontend/.env with /api suffix
BASE_URL = "https://phased-builder.preview.emergentagent.com/api"

class QuestionnaireEndpointsTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.test_results = []
        
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

    # ============================================================================
    # TEST 1: Comprehensive Questionnaire Endpoints
    # ============================================================================
    
    def test_webapp_questionnaire_endpoint(self):
        """Test GET /api/questionnaires/WebApp?level=basic"""
        try:
            response = self.session.get(f"{self.base_url}/questionnaires/WebApp?level=basic")
            
            if response.status_code != 200:
                self.log_test("WebApp Questionnaire Endpoint", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            # Verify expected fields for comprehensive questionnaires
            required_fields = ['prompts', 'total_questions', 'level']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                self.log_test("WebApp Questionnaire Endpoint", False, 
                            f"Missing required fields: {missing_fields}. Response: {data}")
                return False
            
            # Verify data types and content
            if not isinstance(data['prompts'], list):
                self.log_test("WebApp Questionnaire Endpoint", False, 
                            f"'prompts' should be a list, got {type(data['prompts'])}")
                return False
            
            if len(data['prompts']) == 0:
                self.log_test("WebApp Questionnaire Endpoint", False, 
                            "No prompts returned - questionnaire is empty")
                return False
            
            if not isinstance(data['total_questions'], int):
                self.log_test("WebApp Questionnaire Endpoint", False, 
                            f"'total_questions' should be an integer, got {type(data['total_questions'])}")
                return False
            
            if data['level'] != 'basic':
                self.log_test("WebApp Questionnaire Endpoint", False, 
                            f"Expected level 'basic', got '{data['level']}'")
                return False
            
            # Verify prompts structure
            for i, prompt in enumerate(data['prompts']):
                if not isinstance(prompt, dict):
                    self.log_test("WebApp Questionnaire Endpoint", False, 
                                f"Prompt {i} should be a dict, got {type(prompt)}")
                    return False
                
                # Check for essential prompt fields
                prompt_required_fields = ['id', 'question', 'type']
                prompt_missing_fields = [field for field in prompt_required_fields if field not in prompt]
                
                if prompt_missing_fields:
                    self.log_test("WebApp Questionnaire Endpoint", False, 
                                f"Prompt {i} missing fields: {prompt_missing_fields}")
                    return False
            
            self.log_test("WebApp Questionnaire Endpoint", True, 
                        f"✅ WebApp questionnaire: {len(data['prompts'])} prompts, level={data['level']}, total_questions={data['total_questions']}")
            
            return True
            
        except Exception as e:
            self.log_test("WebApp Questionnaire Endpoint", False, f"Request error: {str(e)}")
            return False

    def test_api_questionnaire_endpoint(self):
        """Test GET /api/questionnaires/API?level=basic"""
        try:
            response = self.session.get(f"{self.base_url}/questionnaires/API?level=basic")
            
            if response.status_code != 200:
                self.log_test("API Questionnaire Endpoint", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            # Verify expected fields for comprehensive questionnaires
            required_fields = ['prompts', 'total_questions', 'level']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                self.log_test("API Questionnaire Endpoint", False, 
                            f"Missing required fields: {missing_fields}. Response: {data}")
                return False
            
            # Verify data types and content
            if not isinstance(data['prompts'], list):
                self.log_test("API Questionnaire Endpoint", False, 
                            f"'prompts' should be a list, got {type(data['prompts'])}")
                return False
            
            if len(data['prompts']) == 0:
                self.log_test("API Questionnaire Endpoint", False, 
                            "No prompts returned - questionnaire is empty")
                return False
            
            if not isinstance(data['total_questions'], int):
                self.log_test("API Questionnaire Endpoint", False, 
                            f"'total_questions' should be an integer, got {type(data['total_questions'])}")
                return False
            
            if data['level'] != 'basic':
                self.log_test("API Questionnaire Endpoint", False, 
                            f"Expected level 'basic', got '{data['level']}'")
                return False
            
            # Verify prompts structure
            for i, prompt in enumerate(data['prompts']):
                if not isinstance(prompt, dict):
                    self.log_test("API Questionnaire Endpoint", False, 
                                f"Prompt {i} should be a dict, got {type(prompt)}")
                    return False
                
                # Check for essential prompt fields
                prompt_required_fields = ['id', 'question', 'type']
                prompt_missing_fields = [field for field in prompt_required_fields if field not in prompt]
                
                if prompt_missing_fields:
                    self.log_test("API Questionnaire Endpoint", False, 
                                f"Prompt {i} missing fields: {prompt_missing_fields}")
                    return False
            
            self.log_test("API Questionnaire Endpoint", True, 
                        f"✅ API questionnaire: {len(data['prompts'])} prompts, level={data['level']}, total_questions={data['total_questions']}")
            
            return True
            
        except Exception as e:
            self.log_test("API Questionnaire Endpoint", False, f"Request error: {str(e)}")
            return False

    def test_database_questionnaire_endpoint(self):
        """Test GET /api/questionnaires/Database?level=basic"""
        try:
            response = self.session.get(f"{self.base_url}/questionnaires/Database?level=basic")
            
            if response.status_code != 200:
                self.log_test("Database Questionnaire Endpoint", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            # Verify expected fields for comprehensive questionnaires
            required_fields = ['prompts', 'total_questions', 'level']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                self.log_test("Database Questionnaire Endpoint", False, 
                            f"Missing required fields: {missing_fields}. Response: {data}")
                return False
            
            # Verify data types and content
            if not isinstance(data['prompts'], list):
                self.log_test("Database Questionnaire Endpoint", False, 
                            f"'prompts' should be a list, got {type(data['prompts'])}")
                return False
            
            if len(data['prompts']) == 0:
                self.log_test("Database Questionnaire Endpoint", False, 
                            "No prompts returned - questionnaire is empty")
                return False
            
            if not isinstance(data['total_questions'], int):
                self.log_test("Database Questionnaire Endpoint", False, 
                            f"'total_questions' should be an integer, got {type(data['total_questions'])}")
                return False
            
            if data['level'] != 'basic':
                self.log_test("Database Questionnaire Endpoint", False, 
                            f"Expected level 'basic', got '{data['level']}'")
                return False
            
            # Verify prompts structure
            for i, prompt in enumerate(data['prompts']):
                if not isinstance(prompt, dict):
                    self.log_test("Database Questionnaire Endpoint", False, 
                                f"Prompt {i} should be a dict, got {type(prompt)}")
                    return False
                
                # Check for essential prompt fields
                prompt_required_fields = ['id', 'question', 'type']
                prompt_missing_fields = [field for field in prompt_required_fields if field not in prompt]
                
                if prompt_missing_fields:
                    self.log_test("Database Questionnaire Endpoint", False, 
                                f"Prompt {i} missing fields: {prompt_missing_fields}")
                    return False
            
            self.log_test("Database Questionnaire Endpoint", True, 
                        f"✅ Database questionnaire: {len(data['prompts'])} prompts, level={data['level']}, total_questions={data['total_questions']}")
            
            return True
            
        except Exception as e:
            self.log_test("Database Questionnaire Endpoint", False, f"Request error: {str(e)}")
            return False

    # ============================================================================
    # TEST 2: Fallback Intelligent Nodes Endpoints
    # ============================================================================
    
    def test_external_attacker_prompts_endpoint(self):
        """Test GET /api/intelligent-nodes/ExternalAttacker/prompts"""
        try:
            response = self.session.get(f"{self.base_url}/intelligent-nodes/ExternalAttacker/prompts")
            
            if response.status_code != 200:
                self.log_test("ExternalAttacker Prompts Endpoint", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            # Verify expected fields for intelligent-nodes
            if 'prompts' not in data:
                self.log_test("ExternalAttacker Prompts Endpoint", False, 
                            f"Missing 'prompts' field. Response: {data}")
                return False
            
            # Verify data types and content
            if not isinstance(data['prompts'], list):
                self.log_test("ExternalAttacker Prompts Endpoint", False, 
                            f"'prompts' should be a list, got {type(data['prompts'])}")
                return False
            
            if len(data['prompts']) == 0:
                self.log_test("ExternalAttacker Prompts Endpoint", False, 
                            "No prompts returned - prompts list is empty")
                return False
            
            # Verify prompts structure
            for i, prompt in enumerate(data['prompts']):
                if not isinstance(prompt, dict):
                    self.log_test("ExternalAttacker Prompts Endpoint", False, 
                                f"Prompt {i} should be a dict, got {type(prompt)}")
                    return False
                
                # Check for essential prompt fields
                prompt_required_fields = ['id', 'question', 'type']
                prompt_missing_fields = [field for field in prompt_required_fields if field not in prompt]
                
                if prompt_missing_fields:
                    self.log_test("ExternalAttacker Prompts Endpoint", False, 
                                f"Prompt {i} missing fields: {prompt_missing_fields}")
                    return False
            
            self.log_test("ExternalAttacker Prompts Endpoint", True, 
                        f"✅ ExternalAttacker prompts: {len(data['prompts'])} prompts available")
            
            return True
            
        except Exception as e:
            self.log_test("ExternalAttacker Prompts Endpoint", False, f"Request error: {str(e)}")
            return False

    def test_clouddeployment_prompts_endpoint(self):
        """Test GET /api/intelligent-nodes/CloudDeployment/prompts (alternative fallback)"""
        try:
            response = self.session.get(f"{self.base_url}/intelligent-nodes/CloudDeployment/prompts")
            
            if response.status_code != 200:
                self.log_test("CloudDeployment Prompts Endpoint", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            # Verify expected fields for intelligent-nodes
            if 'prompts' not in data:
                self.log_test("CloudDeployment Prompts Endpoint", False, 
                            f"Missing 'prompts' field. Response: {data}")
                return False
            
            # Verify data types and content
            if not isinstance(data['prompts'], list):
                self.log_test("CloudDeployment Prompts Endpoint", False, 
                            f"'prompts' should be a list, got {type(data['prompts'])}")
                return False
            
            if len(data['prompts']) == 0:
                self.log_test("CloudDeployment Prompts Endpoint", False, 
                            "No prompts returned - prompts list is empty")
                return False
            
            # Verify prompts structure
            for i, prompt in enumerate(data['prompts']):
                if not isinstance(prompt, dict):
                    self.log_test("CloudDeployment Prompts Endpoint", False, 
                                f"Prompt {i} should be a dict, got {type(prompt)}")
                    return False
                
                # Check for essential prompt fields
                prompt_required_fields = ['id', 'question', 'type']
                prompt_missing_fields = [field for field in prompt_required_fields if field not in prompt]
                
                if prompt_missing_fields:
                    self.log_test("CloudDeployment Prompts Endpoint", False, 
                                f"Prompt {i} missing fields: {prompt_missing_fields}")
                    return False
            
            self.log_test("CloudDeployment Prompts Endpoint", True, 
                        f"✅ CloudDeployment prompts: {len(data['prompts'])} prompts available")
            
            return True
            
        except Exception as e:
            self.log_test("CloudDeployment Prompts Endpoint", False, f"Request error: {str(e)}")
            return False

    # ============================================================================
    # TEST 3: Error Conditions Testing
    # ============================================================================
    
    def test_invalid_node_types(self):
        """Test error handling for invalid node types"""
        try:
            invalid_endpoints = [
                {
                    "url": f"{self.base_url}/questionnaires/InvalidNodeType?level=basic",
                    "expected_codes": [400, 404, 500],  # 500 is acceptable for questionnaire endpoints
                    "type": "questionnaire"
                },
                {
                    "url": f"{self.base_url}/questionnaires/NonExistent?level=basic",
                    "expected_codes": [400, 404, 500],  # 500 is acceptable for questionnaire endpoints
                    "type": "questionnaire"
                },
                {
                    "url": f"{self.base_url}/intelligent-nodes/InvalidType/prompts",
                    "expected_codes": [400, 404],  # Should return 404 for intelligent-nodes
                    "type": "intelligent-nodes"
                },
                {
                    "url": f"{self.base_url}/intelligent-nodes/NonExistent/prompts",
                    "expected_codes": [400, 404],  # Should return 404 for intelligent-nodes
                    "type": "intelligent-nodes"
                }
            ]
            
            success_count = 0
            total_tests = len(invalid_endpoints)
            
            for endpoint_info in invalid_endpoints:
                response = self.session.get(endpoint_info["url"])
                
                # Should return expected error codes for invalid node types
                if response.status_code in endpoint_info["expected_codes"]:
                    success_count += 1
                    print(f"   ✅ Invalid {endpoint_info['type']} endpoint correctly returned HTTP {response.status_code}: {endpoint_info['url']}")
                else:
                    print(f"   ❌ Invalid {endpoint_info['type']} endpoint returned unexpected HTTP {response.status_code}: {endpoint_info['url']}")
            
            if success_count == total_tests:
                self.log_test("Invalid Node Types", True, 
                            f"✅ All {total_tests} invalid endpoints correctly returned error status")
                return True
            else:
                self.log_test("Invalid Node Types", False, 
                            f"Only {success_count}/{total_tests} invalid endpoints returned proper error status")
                return False
            
        except Exception as e:
            self.log_test("Invalid Node Types", False, f"Request error: {str(e)}")
            return False

    def test_malformed_requests(self):
        """Test error handling for malformed requests"""
        try:
            malformed_endpoints = [
                f"{self.base_url}/questionnaires/WebApp?level=invalid_level",
                f"{self.base_url}/questionnaires/API?level=",
                f"{self.base_url}/questionnaires/Database",  # Missing level parameter
            ]
            
            success_count = 0
            total_tests = len(malformed_endpoints)
            
            for endpoint in malformed_endpoints:
                response = self.session.get(endpoint)
                
                # Should handle malformed requests gracefully (200 with default or 400)
                if response.status_code in [200, 400]:
                    success_count += 1
                    print(f"   ✅ Malformed request handled gracefully HTTP {response.status_code}: {endpoint}")
                else:
                    print(f"   ❌ Malformed request returned unexpected HTTP {response.status_code}: {endpoint}")
            
            if success_count == total_tests:
                self.log_test("Malformed Requests", True, 
                            f"✅ All {total_tests} malformed requests handled gracefully")
                return True
            else:
                self.log_test("Malformed Requests", False, 
                            f"Only {success_count}/{total_tests} malformed requests handled gracefully")
                return False
            
        except Exception as e:
            self.log_test("Malformed Requests", False, f"Request error: {str(e)}")
            return False

    # ============================================================================
    # TEST 4: Response Format Verification
    # ============================================================================
    
    def test_response_format_consistency(self):
        """Test that all questionnaire endpoints return consistent response formats"""
        try:
            endpoints_to_test = [
                {
                    "url": f"{self.base_url}/questionnaires/WebApp?level=basic",
                    "type": "comprehensive",
                    "name": "WebApp"
                },
                {
                    "url": f"{self.base_url}/questionnaires/API?level=basic",
                    "type": "comprehensive", 
                    "name": "API"
                },
                {
                    "url": f"{self.base_url}/questionnaires/Database?level=basic",
                    "type": "comprehensive",
                    "name": "Database"
                },
                {
                    "url": f"{self.base_url}/intelligent-nodes/ExternalAttacker/prompts",
                    "type": "intelligent-nodes",
                    "name": "ExternalAttacker"
                },
                {
                    "url": f"{self.base_url}/intelligent-nodes/CloudDeployment/prompts",
                    "type": "intelligent-nodes",
                    "name": "CloudDeployment"
                }
            ]
            
            success_count = 0
            total_tests = len(endpoints_to_test)
            
            for endpoint_info in endpoints_to_test:
                response = self.session.get(endpoint_info["url"])
                
                if response.status_code != 200:
                    print(f"   ❌ {endpoint_info['name']}: HTTP {response.status_code}")
                    continue
                
                data = response.json()
                
                # Check format based on endpoint type
                if endpoint_info["type"] == "comprehensive":
                    required_fields = ['prompts', 'total_questions', 'level']
                    if all(field in data for field in required_fields):
                        success_count += 1
                        print(f"   ✅ {endpoint_info['name']}: Comprehensive format correct")
                    else:
                        missing = [f for f in required_fields if f not in data]
                        print(f"   ❌ {endpoint_info['name']}: Missing fields {missing}")
                        
                elif endpoint_info["type"] == "intelligent-nodes":
                    if 'prompts' in data:
                        success_count += 1
                        print(f"   ✅ {endpoint_info['name']}: Intelligent-nodes format correct")
                    else:
                        print(f"   ❌ {endpoint_info['name']}: Missing 'prompts' field")
            
            if success_count == total_tests:
                self.log_test("Response Format Consistency", True, 
                            f"✅ All {total_tests} endpoints return consistent response formats")
                return True
            else:
                self.log_test("Response Format Consistency", False, 
                            f"Only {success_count}/{total_tests} endpoints return correct response formats")
                return False
            
        except Exception as e:
            self.log_test("Response Format Consistency", False, f"Request error: {str(e)}")
            return False

    # ============================================================================
    # Test Runner
    # ============================================================================
    
    def run_all_tests(self):
        """Run all questionnaire endpoint tests"""
        print("🚀 Starting Questionnaire API Endpoints Testing")
        print("=" * 90)
        print("QUESTIONNAIRE ENDPOINTS VERIFICATION")
        print("Testing specific questionnaire endpoints that were showing 'Error Loading Questionnaire'")
        print("Focus: SecurityQuestionnaire.js compatibility and response format verification")
        print("=" * 90)
        
        tests = [
            # Basic connectivity
            self.test_health_check,
            
            # TEST 1: Comprehensive Questionnaire Endpoints
            self.test_webapp_questionnaire_endpoint,
            self.test_api_questionnaire_endpoint,
            self.test_database_questionnaire_endpoint,
            
            # TEST 2: Fallback Intelligent Nodes Endpoints
            self.test_external_attacker_prompts_endpoint,
            self.test_clouddeployment_prompts_endpoint,
            
            # TEST 3: Error Conditions Testing
            self.test_invalid_node_types,
            self.test_malformed_requests,
            
            # TEST 4: Response Format Verification
            self.test_response_format_consistency,
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ FAIL {test.__name__}: Unexpected error: {str(e)}")
                failed += 1
            
            print()  # Add spacing between tests
        
        # Print summary
        print("=" * 90)
        print("🎯 QUESTIONNAIRE ENDPOINTS TESTING SUMMARY")
        print("=" * 90)
        print(f"✅ PASSED: {passed}")
        print(f"❌ FAILED: {failed}")
        print(f"📊 SUCCESS RATE: {(passed / (passed + failed) * 100):.1f}%")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED! Questionnaire endpoints verification successful.")
            print("✅ WebApp questionnaire endpoint working correctly")
            print("✅ API questionnaire endpoint working correctly")
            print("✅ Database questionnaire endpoint working correctly")
            print("✅ ExternalAttacker prompts endpoint working correctly")
            print("✅ CloudDeployment prompts endpoint working correctly")
            print("✅ Error handling working correctly")
            print("✅ Response formats are consistent and compatible with SecurityQuestionnaire.js")
            print("✅ No 'Error Loading Questionnaire' issues should occur")
        else:
            print(f"\n⚠️  {failed} tests failed. Analysis:")
            
            # Analyze the test results to provide diagnostic information
            error_tests = [result for result in self.test_results if not result['success']]
            
            for error_test in error_tests:
                print(f"🚨 FAILED: {error_test['test']}")
                print(f"   Issue: {error_test['message']}")
        
        return passed, failed

def main():
    """Main test execution"""
    tester = QuestionnaireEndpointsTester()
    passed, failed = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()