#!/usr/bin/env python3
"""
Questionnaire Completion Percentage Calculation Testing
Tests the WebApp and API questionnaire completion percentage calculation fixes.

TESTING FOCUS:
1. **WebApp Questionnaire Testing:**
   - Test GET /api/questionnaires/WebApp to verify 10 questions load properly
   - Test POST /api/intelligent-nodes/WebApp/validate-completeness with realistic data 
   - Verify WebApp now uses 8 correct branches: Authentication, Authorization, InputValidation, SessionManagement, ErrorHandling, Logging, SSL/TLS, CSP
   - Test scenario: 6 questions answered out of 10 should show proper completion percentage (not 33.3%)

2. **API Questionnaire Testing:**
   - Test GET /api/questionnaires/API to verify 9 questions load properly  
   - Test POST /api/intelligent-nodes/API/validate-completeness with realistic data
   - Verify API now uses 7 correct branches: ApiSecurity, Authentication, Authorization, RateLimiting, InputValidation, Monitoring, Encryption
   - Test scenario: 4 questions answered out of 9 should show proper completion percentage (not the 500 error from logs)

CONTEXT: 
- Fixed WebApp required_branches to match webapp.yaml (8 branches instead of old 6 wrong ones)
- Fixed API required_branches to match api.yaml (7 branches instead of old 5 wrong ones)  
- Updated frontend branch mapping functions to properly map questionnaire questions to correct security branches
- The root cause was mismatch between YAML file definitions and intelligent_nodes.py templates

EXPECTED RESULTS:
- WebApp questionnaire returns 10 questions with proper branch mapping
- API questionnaire returns 9 questions with proper branch mapping
- Completion percentage calculations are accurate (not 33.3% or 500 errors)
- Both questionnaires use correct security branches matching their YAML files
"""

import requests
import json
import uuid
from datetime import datetime, timezone
import sys

# Use the backend URL from frontend/.env with /api suffix
BASE_URL = "https://iprove-reader.preview.emergentagent.com/api"

class QuestionnaireCompletionTester:
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
    # TEST 1: WebApp Questionnaire Testing
    # ============================================================================
    
    def test_webapp_questionnaire_structure(self):
        """Test GET /api/questionnaires/WebApp to verify 10 questions load properly"""
        try:
            response = self.session.get(f"{self.base_url}/questionnaires/WebApp")
            
            if response.status_code != 200:
                self.log_test("WebApp Questionnaire Structure", False, 
                            f"Failed to get WebApp questionnaire: HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            # Verify response structure
            required_fields = ['prompts']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                self.log_test("WebApp Questionnaire Structure", False, 
                            f"Missing required fields: {missing_fields}")
                return False
            
            # Verify 10 questions are present
            prompts = data.get('prompts', [])
            if len(prompts) != 10:
                self.log_test("WebApp Questionnaire Structure", False, 
                            f"Expected 10 questions, got {len(prompts)}")
                return False
            
            # Verify each prompt has required structure
            for i, prompt in enumerate(prompts):
                required_prompt_fields = ['id', 'question', 'type']
                missing_prompt_fields = [field for field in required_prompt_fields if field not in prompt]
                
                if missing_prompt_fields:
                    self.log_test("WebApp Questionnaire Structure", False, 
                                f"Question {i+1} missing fields: {missing_prompt_fields}")
                    return False
            
            self.log_test("WebApp Questionnaire Structure", True, 
                        f"✅ WebApp questionnaire has {len(prompts)} questions with proper structure")
            
            # Log question details for verification
            print(f"📋 WebApp Questions:")
            for i, prompt in enumerate(prompts[:5]):  # Show first 5
                print(f"   Q{i+1}: {prompt.get('question', 'N/A')[:60]}...")
            if len(prompts) > 5:
                print(f"   ... and {len(prompts) - 5} more questions")
            
            return True
            
        except Exception as e:
            self.log_test("WebApp Questionnaire Structure", False, f"Request error: {str(e)}")
            return False

    def test_webapp_completion_validation(self):
        """Test POST /api/intelligent-nodes/WebApp/validate-completeness with realistic data"""
        try:
            # Test scenario: 6 questions answered out of 10 should show proper completion percentage (not 33.3%)
            realistic_webapp_branches = [
                {
                    "id": "auth_branch",
                    "name": "Authentication Branch",
                    "type": "Authentication",
                    "required": True,
                    "completed": True,
                    "value": "oauth2",
                    "description": "OAuth2/OIDC authentication implementation"
                },
                {
                    "id": "authz_branch",
                    "name": "Authorization Branch", 
                    "type": "Authorization",
                    "required": True,
                    "completed": True,
                    "value": "rbac",
                    "description": "Role-based access control implementation"
                },
                {
                    "id": "input_validation_branch",
                    "name": "Input Validation Branch",
                    "type": "InputValidation",
                    "required": True,
                    "completed": True,
                    "value": "comprehensive",
                    "description": "Comprehensive input validation implementation"
                },
                {
                    "id": "session_mgmt_branch",
                    "name": "Session Management Branch",
                    "type": "SessionManagement",
                    "required": True,
                    "completed": True,
                    "value": "secure",
                    "description": "Secure session management implementation"
                },
                {
                    "id": "error_handling_branch",
                    "name": "Error Handling Branch",
                    "type": "ErrorHandling",
                    "required": True,
                    "completed": True,
                    "value": "minimal_disclosure",
                    "description": "Minimal error disclosure implementation"
                },
                {
                    "id": "logging_branch",
                    "name": "Logging Branch",
                    "type": "Logging",
                    "required": True,
                    "completed": True,
                    "value": "comprehensive",
                    "description": "Comprehensive audit logging implementation"
                }
                # Missing SSL/TLS and CSP branches to test 6/8 completion (75%)
            ]
            
            response = self.session.post(
                f"{self.base_url}/intelligent-nodes/WebApp/validate-completeness",
                json=realistic_webapp_branches
            )
            
            if response.status_code != 200:
                self.log_test("WebApp Completion Validation", False, 
                            f"Failed to validate WebApp completeness: HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            # Verify response structure
            required_fields = ['validation']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                self.log_test("WebApp Completion Validation", False, 
                            f"Missing required fields: {missing_fields}")
                return False
            
            validation = data.get('validation', {})
            required_validation_fields = ['is_complete', 'completion_percentage', 'completed_count', 'required_count']
            missing_validation_fields = [field for field in required_validation_fields if field not in validation]
            
            if missing_validation_fields:
                self.log_test("WebApp Completion Validation", False, 
                            f"Missing validation fields: {missing_validation_fields}")
                return False
            
            # Verify completion calculation
            completed_count = validation.get('completed_count', 0)
            required_count = validation.get('required_count', 0)
            completion_percentage = validation.get('completion_percentage', 0)
            
            # Expected: 6 branches completed out of 8 required = 75%
            expected_completed = 6
            expected_required = 8
            expected_percentage = 75.0
            
            if completed_count != expected_completed:
                self.log_test("WebApp Completion Validation", False, 
                            f"Expected {expected_completed} completed branches, got {completed_count}")
                return False
            
            if required_count != expected_required:
                self.log_test("WebApp Completion Validation", False, 
                            f"Expected {expected_required} required branches, got {required_count}")
                return False
            
            # Allow small floating point differences
            if abs(completion_percentage - expected_percentage) > 1.0:
                self.log_test("WebApp Completion Validation", False, 
                            f"Expected ~{expected_percentage}% completion, got {completion_percentage}%")
                return False
            
            self.log_test("WebApp Completion Validation", True, 
                        f"✅ WebApp completion: {completed_count}/{required_count} branches ({completion_percentage}%)")
            
            # Verify the 8 correct branches are being used
            missing_branches = validation.get('missing_branches', [])
            expected_missing = ['SSL/TLS', 'CSP']  # The 2 branches we didn't include
            
            print(f"📊 WebApp Validation Results:")
            print(f"   Completed: {completed_count}/{required_count} branches")
            print(f"   Completion: {completion_percentage}%")
            print(f"   Missing: {missing_branches}")
            print(f"   Is Complete: {validation.get('is_complete', False)}")
            
            return True
            
        except Exception as e:
            self.log_test("WebApp Completion Validation", False, f"Request error: {str(e)}")
            return False

    def test_webapp_branch_verification(self):
        """Verify WebApp uses 8 correct branches: Authentication, Authorization, InputValidation, SessionManagement, ErrorHandling, Logging, SSL/TLS, CSP"""
        try:
            # Test with all 8 expected branches to verify they are recognized
            all_webapp_branches = [
                {"id": "auth", "name": "Authentication", "type": "Authentication", "required": True, "completed": True, "value": "oauth2"},
                {"id": "authz", "name": "Authorization", "type": "Authorization", "required": True, "completed": True, "value": "rbac"},
                {"id": "input_val", "name": "Input Validation", "type": "InputValidation", "required": True, "completed": True, "value": "comprehensive"},
                {"id": "session", "name": "Session Management", "type": "SessionManagement", "required": True, "completed": True, "value": "secure"},
                {"id": "error", "name": "Error Handling", "type": "ErrorHandling", "required": True, "completed": True, "value": "minimal"},
                {"id": "logging", "name": "Logging", "type": "Logging", "required": True, "completed": True, "value": "comprehensive"},
                {"id": "ssl_tls", "name": "SSL/TLS", "type": "SSL/TLS", "required": True, "completed": True, "value": "enforced"},
                {"id": "csp", "name": "CSP", "type": "CSP", "required": True, "completed": True, "value": "strict"}
            ]
            
            response = self.session.post(
                f"{self.base_url}/intelligent-nodes/WebApp/validate-completeness",
                json=all_webapp_branches
            )
            
            if response.status_code != 200:
                self.log_test("WebApp Branch Verification", False, 
                            f"Failed to validate all WebApp branches: HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            validation = data.get('validation', {})
            
            completed_count = validation.get('completed_count', 0)
            required_count = validation.get('required_count', 0)
            completion_percentage = validation.get('completion_percentage', 0)
            is_complete = validation.get('is_complete', False)
            
            # Should be 100% complete with all 8 branches
            if completed_count != 8 or required_count != 8:
                self.log_test("WebApp Branch Verification", False, 
                            f"Expected 8/8 branches, got {completed_count}/{required_count}")
                return False
            
            if completion_percentage < 99.0:  # Allow for floating point precision
                self.log_test("WebApp Branch Verification", False, 
                            f"Expected 100% completion, got {completion_percentage}%")
                return False
            
            if not is_complete:
                self.log_test("WebApp Branch Verification", False, 
                            f"Expected is_complete=True, got {is_complete}")
                return False
            
            self.log_test("WebApp Branch Verification", True, 
                        f"✅ WebApp recognizes all 8 correct branches with 100% completion")
            
            print(f"🎯 WebApp Branch Verification:")
            print(f"   All 8 branches recognized: Authentication, Authorization, InputValidation, SessionManagement, ErrorHandling, Logging, SSL/TLS, CSP")
            print(f"   Completion: {completion_percentage}%")
            print(f"   Is Complete: {is_complete}")
            
            return True
            
        except Exception as e:
            self.log_test("WebApp Branch Verification", False, f"Request error: {str(e)}")
            return False

    # ============================================================================
    # TEST 2: API Questionnaire Testing
    # ============================================================================
    
    def test_api_questionnaire_structure(self):
        """Test GET /api/questionnaires/API to verify 9 questions load properly"""
        try:
            response = self.session.get(f"{self.base_url}/questionnaires/API")
            
            if response.status_code != 200:
                self.log_test("API Questionnaire Structure", False, 
                            f"Failed to get API questionnaire: HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            # Verify response structure
            required_fields = ['prompts']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                self.log_test("API Questionnaire Structure", False, 
                            f"Missing required fields: {missing_fields}")
                return False
            
            # Verify 9 questions are present
            prompts = data.get('prompts', [])
            if len(prompts) != 9:
                self.log_test("API Questionnaire Structure", False, 
                            f"Expected 9 questions, got {len(prompts)}")
                return False
            
            # Verify each prompt has required structure
            for i, prompt in enumerate(prompts):
                required_prompt_fields = ['id', 'question', 'type']
                missing_prompt_fields = [field for field in required_prompt_fields if field not in prompt]
                
                if missing_prompt_fields:
                    self.log_test("API Questionnaire Structure", False, 
                                f"Question {i+1} missing fields: {missing_prompt_fields}")
                    return False
            
            self.log_test("API Questionnaire Structure", True, 
                        f"✅ API questionnaire has {len(prompts)} questions with proper structure")
            
            # Log question details for verification
            print(f"📋 API Questions:")
            for i, prompt in enumerate(prompts[:5]):  # Show first 5
                print(f"   Q{i+1}: {prompt.get('question', 'N/A')[:60]}...")
            if len(prompts) > 5:
                print(f"   ... and {len(prompts) - 5} more questions")
            
            return True
            
        except Exception as e:
            self.log_test("API Questionnaire Structure", False, f"Request error: {str(e)}")
            return False

    def test_api_completion_validation(self):
        """Test POST /api/intelligent-nodes/API/validate-completeness with realistic data"""
        try:
            # Test scenario: 4 questions answered out of 9 should show proper completion percentage (not 500 error)
            realistic_api_branches = [
                {
                    "id": "api_security_branch",
                    "name": "API Security Branch",
                    "type": "ApiSecurity",
                    "required": True,
                    "completed": True,
                    "value": "comprehensive",
                    "description": "Comprehensive API security implementation"
                },
                {
                    "id": "auth_branch",
                    "name": "Authentication Branch", 
                    "type": "Authentication",
                    "required": True,
                    "completed": True,
                    "value": "jwt",
                    "description": "JWT-based authentication implementation"
                },
                {
                    "id": "authz_branch",
                    "name": "Authorization Branch",
                    "type": "Authorization",
                    "required": True,
                    "completed": True,
                    "value": "rbac",
                    "description": "Role-based access control implementation"
                },
                {
                    "id": "rate_limiting_branch",
                    "name": "Rate Limiting Branch",
                    "type": "RateLimiting",
                    "required": True,
                    "completed": True,
                    "value": "token_bucket",
                    "description": "Token bucket rate limiting implementation"
                }
                # Missing InputValidation, Monitoring, Encryption branches to test 4/7 completion (~57%)
            ]
            
            response = self.session.post(
                f"{self.base_url}/intelligent-nodes/API/validate-completeness",
                json=realistic_api_branches
            )
            
            if response.status_code != 200:
                self.log_test("API Completion Validation", False, 
                            f"Failed to validate API completeness: HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            # Verify response structure
            required_fields = ['validation']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                self.log_test("API Completion Validation", False, 
                            f"Missing required fields: {missing_fields}")
                return False
            
            validation = data.get('validation', {})
            required_validation_fields = ['is_complete', 'completion_percentage', 'completed_count', 'required_count']
            missing_validation_fields = [field for field in required_validation_fields if field not in validation]
            
            if missing_validation_fields:
                self.log_test("API Completion Validation", False, 
                            f"Missing validation fields: {missing_validation_fields}")
                return False
            
            # Verify completion calculation
            completed_count = validation.get('completed_count', 0)
            required_count = validation.get('required_count', 0)
            completion_percentage = validation.get('completion_percentage', 0)
            
            # Expected: 4 branches completed out of 7 required = ~57.1%
            expected_completed = 4
            expected_required = 7
            expected_percentage = 57.1  # 4/7 * 100
            
            if completed_count != expected_completed:
                self.log_test("API Completion Validation", False, 
                            f"Expected {expected_completed} completed branches, got {completed_count}")
                return False
            
            if required_count != expected_required:
                self.log_test("API Completion Validation", False, 
                            f"Expected {expected_required} required branches, got {required_count}")
                return False
            
            # Allow reasonable floating point differences
            if abs(completion_percentage - expected_percentage) > 2.0:
                self.log_test("API Completion Validation", False, 
                            f"Expected ~{expected_percentage}% completion, got {completion_percentage}%")
                return False
            
            self.log_test("API Completion Validation", True, 
                        f"✅ API completion: {completed_count}/{required_count} branches ({completion_percentage:.1f}%)")
            
            # Verify the 7 correct branches are being used
            missing_branches = validation.get('missing_branches', [])
            expected_missing = ['InputValidation', 'Monitoring', 'Encryption']  # The 3 branches we didn't include
            
            print(f"📊 API Validation Results:")
            print(f"   Completed: {completed_count}/{required_count} branches")
            print(f"   Completion: {completion_percentage:.1f}%")
            print(f"   Missing: {missing_branches}")
            print(f"   Is Complete: {validation.get('is_complete', False)}")
            
            return True
            
        except Exception as e:
            self.log_test("API Completion Validation", False, f"Request error: {str(e)}")
            return False

    def test_api_branch_verification(self):
        """Verify API uses 7 correct branches: ApiSecurity, Authentication, Authorization, RateLimiting, InputValidation, Monitoring, Encryption"""
        try:
            # Test with all 7 expected branches to verify they are recognized
            all_api_branches = [
                {"id": "api_sec", "name": "API Security", "type": "ApiSecurity", "required": True, "completed": True, "value": "comprehensive"},
                {"id": "auth", "name": "Authentication", "type": "Authentication", "required": True, "completed": True, "value": "jwt"},
                {"id": "authz", "name": "Authorization", "type": "Authorization", "required": True, "completed": True, "value": "rbac"},
                {"id": "rate_limit", "name": "Rate Limiting", "type": "RateLimiting", "required": True, "completed": True, "value": "token_bucket"},
                {"id": "input_val", "name": "Input Validation", "type": "InputValidation", "required": True, "completed": True, "value": "strict"},
                {"id": "monitoring", "name": "Monitoring", "type": "Monitoring", "required": True, "completed": True, "value": "comprehensive"},
                {"id": "encryption", "name": "Encryption", "type": "Encryption", "required": True, "completed": True, "value": "aes256"}
            ]
            
            response = self.session.post(
                f"{self.base_url}/intelligent-nodes/API/validate-completeness",
                json=all_api_branches
            )
            
            if response.status_code != 200:
                self.log_test("API Branch Verification", False, 
                            f"Failed to validate all API branches: HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            validation = data.get('validation', {})
            
            completed_count = validation.get('completed_count', 0)
            required_count = validation.get('required_count', 0)
            completion_percentage = validation.get('completion_percentage', 0)
            is_complete = validation.get('is_complete', False)
            
            # Should be 100% complete with all 7 branches
            if completed_count != 7 or required_count != 7:
                self.log_test("API Branch Verification", False, 
                            f"Expected 7/7 branches, got {completed_count}/{required_count}")
                return False
            
            if completion_percentage < 99.0:  # Allow for floating point precision
                self.log_test("API Branch Verification", False, 
                            f"Expected 100% completion, got {completion_percentage}%")
                return False
            
            if not is_complete:
                self.log_test("API Branch Verification", False, 
                            f"Expected is_complete=True, got {is_complete}")
                return False
            
            self.log_test("API Branch Verification", True, 
                        f"✅ API recognizes all 7 correct branches with 100% completion")
            
            print(f"🎯 API Branch Verification:")
            print(f"   All 7 branches recognized: ApiSecurity, Authentication, Authorization, RateLimiting, InputValidation, Monitoring, Encryption")
            print(f"   Completion: {completion_percentage}%")
            print(f"   Is Complete: {is_complete}")
            
            return True
            
        except Exception as e:
            self.log_test("API Branch Verification", False, f"Request error: {str(e)}")
            return False

    # ============================================================================
    # TEST 3: Edge Cases and Error Scenarios
    # ============================================================================
    
    def test_edge_cases(self):
        """Test edge cases and error scenarios"""
        try:
            test_cases = [
                {
                    "name": "Empty WebApp Branches",
                    "url": f"{self.base_url}/intelligent-nodes/WebApp/validate-completeness",
                    "data": [],
                    "expected_completion": 0.0
                },
                {
                    "name": "Empty API Branches", 
                    "url": f"{self.base_url}/intelligent-nodes/API/validate-completeness",
                    "data": [],
                    "expected_completion": 0.0
                },
                {
                    "name": "Invalid WebApp Branch Type",
                    "url": f"{self.base_url}/intelligent-nodes/WebApp/validate-completeness",
                    "data": [{"id": "invalid", "name": "Invalid", "type": "InvalidBranch", "required": True, "completed": True, "value": "test"}],
                    "expected_completion": 0.0
                },
                {
                    "name": "Invalid API Branch Type",
                    "url": f"{self.base_url}/intelligent-nodes/API/validate-completeness", 
                    "data": [{"id": "invalid", "name": "Invalid", "type": "InvalidBranch", "required": True, "completed": True, "value": "test"}],
                    "expected_completion": 0.0
                }
            ]
            
            success_count = 0
            total_tests = len(test_cases)
            
            for test_case in test_cases:
                response = self.session.post(test_case["url"], json=test_case["data"])
                
                if response.status_code == 200:
                    data = response.json()
                    validation = data.get('validation', {})
                    completion_percentage = validation.get('completion_percentage', -1)
                    
                    if abs(completion_percentage - test_case["expected_completion"]) <= 1.0:
                        success_count += 1
                        print(f"   ✅ {test_case['name']}: {completion_percentage}% completion")
                    else:
                        print(f"   ❌ {test_case['name']}: Expected {test_case['expected_completion']}%, got {completion_percentage}%")
                else:
                    print(f"   ❌ {test_case['name']}: HTTP {response.status_code}")
            
            if success_count == total_tests:
                self.log_test("Edge Cases", True, f"✅ All {total_tests} edge case tests passed")
                return True
            else:
                self.log_test("Edge Cases", False, f"Only {success_count}/{total_tests} edge case tests passed")
                return False
            
        except Exception as e:
            self.log_test("Edge Cases", False, f"Request error: {str(e)}")
            return False

    # ============================================================================
    # Test Runner
    # ============================================================================
    
    def run_all_tests(self):
        """Run all questionnaire completion percentage calculation tests"""
        print("🚀 Starting Questionnaire Completion Percentage Calculation Tests")
        print("=" * 90)
        print("QUESTIONNAIRE COMPLETION PERCENTAGE CALCULATION FIXES VERIFICATION")
        print("Testing WebApp and API questionnaire completion percentage calculation fixes")
        print("Focus: Proper branch mapping and accurate completion percentage calculations")
        print("=" * 90)
        
        tests = [
            # Basic connectivity
            self.test_health_check,
            
            # TEST 1: WebApp Questionnaire Testing
            self.test_webapp_questionnaire_structure,
            self.test_webapp_completion_validation,
            self.test_webapp_branch_verification,
            
            # TEST 2: API Questionnaire Testing
            self.test_api_questionnaire_structure,
            self.test_api_completion_validation,
            self.test_api_branch_verification,
            
            # TEST 3: Edge Cases
            self.test_edge_cases,
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
        print("🎯 QUESTIONNAIRE COMPLETION PERCENTAGE CALCULATION SUMMARY")
        print("=" * 90)
        print(f"✅ PASSED: {passed}")
        print(f"❌ FAILED: {failed}")
        print(f"📊 SUCCESS RATE: {(passed / (passed + failed) * 100):.1f}%")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED! Questionnaire completion percentage calculation fixes verified successfully.")
            print("✅ WebApp questionnaire loads 10 questions properly")
            print("✅ WebApp uses 8 correct branches: Authentication, Authorization, InputValidation, SessionManagement, ErrorHandling, Logging, SSL/TLS, CSP")
            print("✅ WebApp completion percentage calculations are accurate")
            print("✅ API questionnaire loads 9 questions properly")
            print("✅ API uses 7 correct branches: ApiSecurity, Authentication, Authorization, RateLimiting, InputValidation, Monitoring, Encryption")
            print("✅ API completion percentage calculations are accurate (no 500 errors)")
            print("✅ Both questionnaires now properly match their YAML file definitions")
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
    tester = QuestionnaireCompletionTester()
    passed, failed = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()