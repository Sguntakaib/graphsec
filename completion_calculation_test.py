#!/usr/bin/env python3
"""
Backend API Testing - COMPLETION CALCULATION FIXES VERIFICATION
Tests the completion calculation fixes as requested in the review:

TESTING FOCUS:
🎯 COMPLETION CALCULATION FIXES VERIFICATION
- Frontend-Backend mapping fixes: 'API' → 'ApiSecurity', 'SSL/TLS' → 'Encryption'
- Backend validation API should properly match frontend branch types
- Completion percentage calculation should work correctly
- No HTTP 500 errors from validation endpoints
- SecurityBranchType enum matching should work

TEST SCENARIOS:
1. Test API node questionnaire validation with new branch mappings
2. Test completion percentage calculation accuracy
3. Test that backend recognizes all completed branches properly
4. Test no HTTP 500 errors from validation endpoints
5. Test SecurityBranchType enum matching with frontend mappings

**EXPECTED RESULTS:** 
- API nodes should show correct completion % (not 71.4% when 5/7 done)
- Backend validation should properly match frontend branch types
- Notifications should show accurate completion percentages
- No HTTP 500 errors from validation endpoints
"""

import requests
import json
import uuid
from datetime import datetime, timezone
import sys

# Use the backend URL from frontend/.env with /api suffix
BASE_URL = "https://design-enhance-v2.preview.emergentagent.com/api"

class CompletionCalculationTester:
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

    def test_api_validation_with_new_mappings(self):
        """TEST SCENARIO 1: Test API node questionnaire validation with new branch mappings"""
        try:
            print("🎯 TEST SCENARIO 1: API Node Validation with New Branch Mappings")
            print("=" * 80)
            
            # Test with the new frontend-backend mappings
            # 'API' → 'ApiSecurity', 'SSL/TLS' → 'Encryption'
            validation_data = [
                {
                    "id": "api_authentication_method",
                    "name": "api_authentication_method",
                    "type": "Authentication",
                    "required": True,
                    "completed": True,
                    "value": "OAuth 2.0",
                    "description": "API authentication method"
                },
                {
                    "id": "api_endpoints",
                    "name": "api_endpoints", 
                    "type": "ApiSecurity",  # NEW MAPPING: 'API' → 'ApiSecurity'
                    "required": True,
                    "completed": True,
                    "value": "REST API with proper versioning",
                    "description": "API security configuration"
                },
                {
                    "id": "ssl_tls_config",
                    "name": "ssl_tls_config",
                    "type": "Encryption",  # NEW MAPPING: 'SSL/TLS' → 'Encryption'
                    "required": True,
                    "completed": True,
                    "value": "TLS 1.3 enabled",
                    "description": "SSL/TLS encryption configuration"
                },
                {
                    "id": "input_validation",
                    "name": "input_validation",
                    "type": "InputValidation",
                    "required": True,
                    "completed": True,
                    "value": "Comprehensive validation",
                    "description": "Input validation configuration"
                },
                {
                    "id": "rate_limiting",
                    "name": "rate_limiting",
                    "type": "RateLimiting",
                    "required": True,
                    "completed": True,
                    "value": "Implemented with proper limits",
                    "description": "Rate limiting configuration"
                }
            ]
            
            print(f"📋 Testing with {len(validation_data)} completed branches:")
            for branch in validation_data:
                print(f"   - {branch['type']}: {branch['value']}")
            
            response = self.session.post(
                f"{self.base_url}/intelligent-nodes/API/validate-completeness",
                json=validation_data
            )
            
            print(f"📋 API Validation Response Status: HTTP {response.status_code}")
            
            if response.status_code == 500:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("API Validation with New Mappings", False, 
                            f"❌ CRITICAL: HTTP 500 error with new mappings: {error_detail}")
                return False
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("API Validation with New Mappings", False, 
                            f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("API Validation with New Mappings", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            # Verify validation response structure
            validation = data.get("validation", {})
            
            if not validation:
                self.log_test("API Validation with New Mappings", False, 
                            "No validation data returned")
                return False
            
            is_complete = validation.get("is_complete", False)
            completion_percentage = validation.get("completion_percentage", 0)
            completed_count = validation.get("completed_count", 0)
            required_count = validation.get("required_count", 0)
            
            print(f"📊 API Validation Results with New Mappings:")
            print(f"   Is Complete: {is_complete}")
            print(f"   Completion Percentage: {completion_percentage}%")
            print(f"   Completed Count: {completed_count}")
            print(f"   Required Count: {required_count}")
            
            # Check if completion percentage is accurate
            expected_percentage = (completed_count / required_count * 100) if required_count > 0 else 0
            percentage_diff = abs(completion_percentage - expected_percentage)
            
            if percentage_diff > 1.0:  # Allow 1% tolerance
                self.log_test("API Validation with New Mappings", False, 
                            f"❌ COMPLETION CALCULATION ERROR: Expected {expected_percentage}%, got {completion_percentage}%")
                return False
            
            # Verify that all 5 branches are recognized
            if completed_count != 5:
                self.log_test("API Validation with New Mappings", False, 
                            f"❌ BRANCH RECOGNITION ERROR: Expected 5 completed branches, got {completed_count}")
                return False
            
            self.log_test("API Validation with New Mappings", True, 
                        f"✅ SUCCESS: New mappings work correctly, {completion_percentage}% completion calculated accurately")
            
            return True
            
        except Exception as e:
            self.log_test("API Validation with New Mappings", False, f"Request error: {str(e)}")
            return False

    def test_completion_percentage_accuracy(self):
        """TEST SCENARIO 2: Test completion percentage calculation accuracy"""
        try:
            print("🎯 TEST SCENARIO 2: Completion Percentage Calculation Accuracy")
            print("=" * 80)
            
            # Test with partial completion (3 out of 7 branches)
            partial_validation_data = [
                {
                    "id": "api_authentication",
                    "name": "api_authentication",
                    "type": "Authentication",
                    "required": True,
                    "completed": True,
                    "value": "OAuth 2.0",
                    "description": "API authentication"
                },
                {
                    "id": "api_security",
                    "name": "api_security", 
                    "type": "ApiSecurity",
                    "required": True,
                    "completed": True,
                    "value": "Secured endpoints",
                    "description": "API security"
                },
                {
                    "id": "encryption",
                    "name": "encryption",
                    "type": "Encryption",
                    "required": True,
                    "completed": True,
                    "value": "TLS 1.3",
                    "description": "Encryption"
                },
                {
                    "id": "input_validation",
                    "name": "input_validation",
                    "type": "InputValidation",
                    "required": True,
                    "completed": False,
                    "value": None,
                    "description": "Input validation - not completed"
                },
                {
                    "id": "rate_limiting",
                    "name": "rate_limiting",
                    "type": "RateLimiting",
                    "required": True,
                    "completed": False,
                    "value": None,
                    "description": "Rate limiting - not completed"
                },
                {
                    "id": "authorization",
                    "name": "authorization",
                    "type": "Authorization",
                    "required": True,
                    "completed": False,
                    "value": None,
                    "description": "Authorization - not completed"
                },
                {
                    "id": "logging",
                    "name": "logging",
                    "type": "Logging",
                    "required": True,
                    "completed": False,
                    "value": None,
                    "description": "Logging - not completed"
                }
            ]
            
            completed_branches = [b for b in partial_validation_data if b['completed']]
            total_branches = len(partial_validation_data)
            expected_percentage = (len(completed_branches) / total_branches) * 100
            
            print(f"📋 Testing partial completion:")
            print(f"   Completed branches: {len(completed_branches)}")
            print(f"   Total branches: {total_branches}")
            print(f"   Expected percentage: {expected_percentage:.1f}%")
            
            response = self.session.post(
                f"{self.base_url}/intelligent-nodes/API/validate-completeness",
                json=partial_validation_data
            )
            
            print(f"📋 Partial Validation Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("Completion Percentage Accuracy", False, 
                            f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Completion Percentage Accuracy", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            validation = data.get("validation", {})
            completion_percentage = validation.get("completion_percentage", 0)
            completed_count = validation.get("completed_count", 0)
            required_count = validation.get("required_count", 0)
            
            print(f"📊 Partial Completion Results:")
            print(f"   Completion Percentage: {completion_percentage}%")
            print(f"   Completed Count: {completed_count}")
            print(f"   Required Count: {required_count}")
            
            # Check accuracy of completion percentage
            calculated_percentage = (completed_count / required_count * 100) if required_count > 0 else 0
            percentage_diff = abs(completion_percentage - calculated_percentage)
            
            if percentage_diff > 1.0:  # Allow 1% tolerance
                self.log_test("Completion Percentage Accuracy", False, 
                            f"❌ CALCULATION ERROR: Expected {calculated_percentage:.1f}%, got {completion_percentage}%")
                return False
            
            # Verify the specific issue mentioned in review: "not 71.4% when 5/7 done"
            if completed_count == 5 and required_count == 7:
                expected_5_of_7 = (5/7) * 100  # Should be ~71.43%
                if abs(completion_percentage - expected_5_of_7) > 1.0:
                    self.log_test("Completion Percentage Accuracy", False, 
                                f"❌ 5/7 CALCULATION ERROR: Expected {expected_5_of_7:.1f}%, got {completion_percentage}%")
                    return False
            
            self.log_test("Completion Percentage Accuracy", True, 
                        f"✅ SUCCESS: Completion percentage calculated accurately: {completion_percentage}%")
            
            return True
            
        except Exception as e:
            self.log_test("Completion Percentage Accuracy", False, f"Request error: {str(e)}")
            return False

    def test_backend_branch_recognition(self):
        """TEST SCENARIO 3: Test that backend recognizes all completed branches properly"""
        try:
            print("🎯 TEST SCENARIO 3: Backend Branch Recognition")
            print("=" * 80)
            
            # Test with all the new frontend mappings
            all_mappings_data = [
                {
                    "id": "authentication",
                    "name": "authentication",
                    "type": "Authentication",
                    "required": True,
                    "completed": True,
                    "value": "OAuth 2.0",
                    "description": "Authentication"
                },
                {
                    "id": "api_security",
                    "name": "api_security",
                    "type": "ApiSecurity",  # Frontend 'API' → Backend 'ApiSecurity'
                    "required": True,
                    "completed": True,
                    "value": "Secured",
                    "description": "API Security"
                },
                {
                    "id": "ssl_tls",
                    "name": "ssl_tls",
                    "type": "Encryption",  # Frontend 'SSL/TLS' → Backend 'Encryption'
                    "required": True,
                    "completed": True,
                    "value": "TLS 1.3",
                    "description": "SSL/TLS Encryption"
                },
                {
                    "id": "input_validation",
                    "name": "input_validation",
                    "type": "InputValidation",
                    "required": True,
                    "completed": True,
                    "value": "Comprehensive",
                    "description": "Input Validation"
                },
                {
                    "id": "authorization",
                    "name": "authorization",
                    "type": "Authorization",
                    "required": True,
                    "completed": True,
                    "value": "RBAC",
                    "description": "Authorization"
                },
                {
                    "id": "rate_limiting",
                    "name": "rate_limiting",
                    "type": "RateLimiting",
                    "required": True,
                    "completed": True,
                    "value": "Implemented",
                    "description": "Rate Limiting"
                },
                {
                    "id": "logging",
                    "name": "logging",
                    "type": "Logging",
                    "required": True,
                    "completed": True,
                    "value": "Comprehensive",
                    "description": "Logging"
                }
            ]
            
            print(f"📋 Testing branch recognition with {len(all_mappings_data)} branches:")
            for branch in all_mappings_data:
                print(f"   - {branch['type']}: {branch['completed']}")
            
            response = self.session.post(
                f"{self.base_url}/intelligent-nodes/API/validate-completeness",
                json=all_mappings_data
            )
            
            print(f"📋 Branch Recognition Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("Backend Branch Recognition", False, 
                            f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Backend Branch Recognition", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            validation = data.get("validation", {})
            completed_count = validation.get("completed_count", 0)
            required_count = validation.get("required_count", 0)
            missing_branches = validation.get("missing_branches", [])
            
            print(f"📊 Branch Recognition Results:")
            print(f"   Completed Count: {completed_count}")
            print(f"   Required Count: {required_count}")
            print(f"   Missing Branches: {missing_branches}")
            
            # All branches should be recognized as completed
            if completed_count != len(all_mappings_data):
                self.log_test("Backend Branch Recognition", False, 
                            f"❌ RECOGNITION ERROR: Expected {len(all_mappings_data)} completed, got {completed_count}")
                return False
            
            # No branches should be missing
            if missing_branches:
                self.log_test("Backend Branch Recognition", False, 
                            f"❌ MISSING BRANCHES: {missing_branches}")
                return False
            
            self.log_test("Backend Branch Recognition", True, 
                        f"✅ SUCCESS: All {completed_count} branches recognized correctly")
            
            return True
            
        except Exception as e:
            self.log_test("Backend Branch Recognition", False, f"Request error: {str(e)}")
            return False

    def test_no_http_500_errors(self):
        """TEST SCENARIO 4: Test no HTTP 500 errors from validation endpoints"""
        try:
            print("🎯 TEST SCENARIO 4: No HTTP 500 Errors from Validation")
            print("=" * 80)
            
            # Test various scenarios that might cause 500 errors
            test_scenarios = [
                {
                    "name": "Empty validation data",
                    "data": []
                },
                {
                    "name": "Single branch with new mapping",
                    "data": [
                        {
                            "id": "api_security",
                            "name": "api_security",
                            "type": "ApiSecurity",
                            "required": True,
                            "completed": True,
                            "value": "Secured",
                            "description": "API Security"
                        }
                    ]
                },
                {
                    "name": "Mixed completion states",
                    "data": [
                        {
                            "id": "api_security",
                            "name": "api_security",
                            "type": "ApiSecurity",
                            "required": True,
                            "completed": True,
                            "value": "Secured",
                            "description": "API Security"
                        },
                        {
                            "id": "encryption",
                            "name": "encryption",
                            "type": "Encryption",
                            "required": True,
                            "completed": False,
                            "value": None,
                            "description": "Encryption not configured"
                        }
                    ]
                }
            ]
            
            all_passed = True
            
            for scenario in test_scenarios:
                print(f"   Testing: {scenario['name']}")
                
                response = self.session.post(
                    f"{self.base_url}/intelligent-nodes/API/validate-completeness",
                    json=scenario['data']
                )
                
                print(f"   Response Status: HTTP {response.status_code}")
                
                if response.status_code == 500:
                    error_detail = "Unknown error"
                    try:
                        error_data = response.json()
                        error_detail = error_data.get('detail', str(error_data))
                    except:
                        error_detail = response.text
                    
                    print(f"   ❌ HTTP 500 ERROR: {error_detail}")
                    all_passed = False
                elif response.status_code == 200:
                    print(f"   ✅ SUCCESS: No 500 error")
                else:
                    print(f"   ⚠️ Non-200 status (but not 500): {response.status_code}")
            
            if all_passed:
                self.log_test("No HTTP 500 Errors", True, 
                            "✅ SUCCESS: No HTTP 500 errors encountered in any scenario")
            else:
                self.log_test("No HTTP 500 Errors", False, 
                            "❌ CRITICAL: HTTP 500 errors encountered")
            
            return all_passed
            
        except Exception as e:
            self.log_test("No HTTP 500 Errors", False, f"Request error: {str(e)}")
            return False

    def test_security_branch_type_enum_matching(self):
        """TEST SCENARIO 5: Test SecurityBranchType enum matching with frontend mappings"""
        try:
            print("🎯 TEST SCENARIO 5: SecurityBranchType Enum Matching")
            print("=" * 80)
            
            # Test all the critical enum mappings mentioned in the review
            enum_mapping_tests = [
                {
                    "frontend_value": "API",
                    "backend_enum": "ApiSecurity",
                    "description": "API security mapping"
                },
                {
                    "frontend_value": "SSL/TLS", 
                    "backend_enum": "Encryption",
                    "description": "SSL/TLS encryption mapping"
                },
                {
                    "frontend_value": "Authentication",
                    "backend_enum": "Authentication", 
                    "description": "Authentication mapping"
                },
                {
                    "frontend_value": "Input Validation",
                    "backend_enum": "InputValidation",
                    "description": "Input validation mapping"
                }
            ]
            
            all_mappings_passed = True
            
            for mapping_test in enum_mapping_tests:
                print(f"   Testing mapping: {mapping_test['frontend_value']} → {mapping_test['backend_enum']}")
                
                test_data = [
                    {
                        "id": f"test_{mapping_test['backend_enum'].lower()}",
                        "name": f"test_{mapping_test['backend_enum'].lower()}",
                        "type": mapping_test['backend_enum'],
                        "required": True,
                        "completed": True,
                        "value": "Test value",
                        "description": mapping_test['description']
                    }
                ]
                
                response = self.session.post(
                    f"{self.base_url}/intelligent-nodes/API/validate-completeness",
                    json=test_data
                )
                
                print(f"   Response Status: HTTP {response.status_code}")
                
                if response.status_code == 500:
                    error_detail = "Unknown error"
                    try:
                        error_data = response.json()
                        error_detail = error_data.get('detail', str(error_data))
                    except:
                        error_detail = response.text
                    
                    print(f"   ❌ ENUM ERROR: {error_detail}")
                    all_mappings_passed = False
                elif response.status_code == 200:
                    try:
                        data = response.json()
                        validation = data.get("validation", {})
                        completed_count = validation.get("completed_count", 0)
                        
                        if completed_count == 1:
                            print(f"   ✅ SUCCESS: Enum {mapping_test['backend_enum']} recognized")
                        else:
                            print(f"   ❌ RECOGNITION ERROR: Expected 1 completed, got {completed_count}")
                            all_mappings_passed = False
                    except Exception as e:
                        print(f"   ❌ RESPONSE ERROR: {str(e)}")
                        all_mappings_passed = False
                else:
                    print(f"   ❌ HTTP ERROR: {response.status_code}")
                    all_mappings_passed = False
            
            if all_mappings_passed:
                self.log_test("SecurityBranchType Enum Matching", True, 
                            "✅ SUCCESS: All critical enum mappings work correctly")
            else:
                self.log_test("SecurityBranchType Enum Matching", False, 
                            "❌ CRITICAL: Some enum mappings failed")
            
            return all_mappings_passed
            
        except Exception as e:
            self.log_test("SecurityBranchType Enum Matching", False, f"Request error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all completion calculation fix verification tests"""
        print("🚀 STARTING COMPLETION CALCULATION FIXES VERIFICATION")
        print("=" * 80)
        print("Testing completion calculation fixes as requested in review:")
        print("1. API node questionnaire validation with new branch mappings")
        print("2. Completion percentage calculation accuracy")
        print("3. Backend branch recognition")
        print("4. No HTTP 500 errors from validation endpoints")
        print("5. SecurityBranchType enum matching with frontend mappings")
        print("=" * 80)
        
        tests = [
            self.test_health_check,
            self.test_api_validation_with_new_mappings,
            self.test_completion_percentage_accuracy,
            self.test_backend_branch_recognition,
            self.test_no_http_500_errors,
            self.test_security_branch_type_enum_matching,
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
    tester = CompletionCalculationTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)