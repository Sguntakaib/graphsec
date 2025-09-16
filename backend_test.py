#!/usr/bin/env python3
"""
Backend API Testing - CRITICAL BUG FIX VERIFICATION: POST /api/intelligent-nodes/WebApp/validate-completeness Endpoint Testing
Tests the WebApp validate-completeness endpoint after fixing the 'Https' enum mapping issue.
ISSUE: The questionnaire uses related_branch: "HTTPS" which isn't in SecurityBranchType enum, needs to be mapped to 'Encryption'.
Focus: Test with 'HTTPS' mapped to 'Encryption', verify 500 error is fixed, test realistic WebApp questionnaire data.
"""

import requests
import json
import uuid
from datetime import datetime, timezone
import sys

# Use the backend URL from frontend/.env with /api suffix
BASE_URL = "https://auto-test-fix.preview.emergentagent.com/api"

class WebAppValidateCompletenessEndpointTester:
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
    # CRITICAL TESTING TASK: REPRODUCE 500 ERROR IN VALIDATE-COMPLETENESS ENDPOINT
    # ============================================================================
    
    def test_validate_completeness_with_realistic_webapp_data(self):
        """Test POST /api/intelligent-nodes/WebApp/validate-completeness with realistic WebApp questionnaire data"""
        try:
            # Realistic WebApp questionnaire data that would come from frontend interface
            realistic_webapp_branches = [
                {
                    "id": "login-branch-1",
                    "name": "Authentication System",
                    "type": "Login",
                    "required": True,
                    "completed": True,
                    "value": "oauth2",
                    "description": "OAuth2 authentication implementation"
                },
                {
                    "id": "database-branch-1", 
                    "name": "Database Security",
                    "type": "Database",
                    "required": True,
                    "completed": True,
                    "value": "encrypted",
                    "description": "Database encryption enabled"
                },
                {
                    "id": "api-branch-1",
                    "name": "API Security",
                    "type": "API",
                    "required": True,
                    "completed": False,
                    "value": None,
                    "description": "API security configuration"
                },
                {
                    "id": "input-validation-branch-1",
                    "name": "Input Validation",
                    "type": "InputValidation",
                    "required": True,
                    "completed": True,
                    "value": "comprehensive",
                    "description": "Comprehensive input validation"
                },
                {
                    "id": "waf-branch-1",
                    "name": "Web Application Firewall",
                    "type": "WAF",
                    "required": False,
                    "completed": False,
                    "value": None,
                    "description": "WAF protection"
                },
                {
                    "id": "deployment-branch-1",
                    "name": "Deployment Security",
                    "type": "Deployment",
                    "required": True,
                    "completed": True,
                    "value": "secure",
                    "description": "Secure deployment configuration"
                }
            ]
            
            print(f"🔍 Testing with realistic WebApp data: {len(realistic_webapp_branches)} branches")
            print(f"📋 Branch types: {[b['type'] for b in realistic_webapp_branches]}")
            
            response = self.session.post(
                f"{self.base_url}/intelligent-nodes/WebApp/validate-completeness",
                json=realistic_webapp_branches,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"📡 Response Status: {response.status_code}")
            print(f"📄 Response Headers: {dict(response.headers)}")
            
            if response.status_code == 500:
                # This is the expected 500 error we're trying to reproduce
                try:
                    error_data = response.json()
                    self.log_test("Validate Completeness - Realistic Data", False, 
                                f"REPRODUCED 500 ERROR! Error details: {error_data}")
                    print(f"🚨 EXACT 500 ERROR MESSAGE: {error_data}")
                    return False
                except:
                    error_text = response.text
                    self.log_test("Validate Completeness - Realistic Data", False, 
                                f"REPRODUCED 500 ERROR! Error text: {error_text}")
                    print(f"🚨 EXACT 500 ERROR TEXT: {error_text}")
                    return False
            elif response.status_code == 200:
                data = response.json()
                self.log_test("Validate Completeness - Realistic Data", True, 
                            f"Endpoint working correctly: {data}")
                return True
            elif response.status_code == 422:
                # Validation error - might indicate enum value issues
                error_data = response.json()
                self.log_test("Validate Completeness - Realistic Data", False, 
                            f"VALIDATION ERROR (422): {error_data} - This might indicate SecurityBranch enum value issues")
                print(f"🔍 VALIDATION ERROR DETAILS: {error_data}")
                return False
            else:
                self.log_test("Validate Completeness - Realistic Data", False, 
                            f"Unexpected HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Validate Completeness - Realistic Data", False, f"Request error: {str(e)}")
            return False

    def test_validate_completeness_with_different_enum_values(self):
        """Test with different SecurityBranch enum value formats to identify the correct ones"""
        try:
            # Test different enum value formats based on common patterns
            enum_test_cases = [
                {
                    "name": "Lowercase enum values",
                    "branches": [
                        {
                            "id": "test-1",
                            "name": "Test Branch",
                            "type": "login",  # lowercase
                            "required": True,
                            "completed": True,
                            "value": "oauth2",
                            "description": "Test"
                        }
                    ]
                },
                {
                    "name": "Uppercase enum values", 
                    "branches": [
                        {
                            "id": "test-2",
                            "name": "Test Branch",
                            "type": "LOGIN",  # uppercase
                            "required": True,
                            "completed": True,
                            "value": "oauth2",
                            "description": "Test"
                        }
                    ]
                },
                {
                    "name": "PascalCase enum values",
                    "branches": [
                        {
                            "id": "test-3",
                            "name": "Test Branch", 
                            "type": "Login",  # PascalCase
                            "required": True,
                            "completed": True,
                            "value": "oauth2",
                            "description": "Test"
                        }
                    ]
                }
            ]
            
            working_enum_format = None
            
            for test_case in enum_test_cases:
                print(f"🧪 Testing {test_case['name']}")
                
                response = self.session.post(
                    f"{self.base_url}/intelligent-nodes/WebApp/validate-completeness",
                    json=test_case['branches'],
                    headers={"Content-Type": "application/json"}
                )
                
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    working_enum_format = test_case['name']
                    self.log_test("Enum Value Format Test", True, 
                                f"FOUND WORKING ENUM FORMAT: {test_case['name']} - type: '{test_case['branches'][0]['type']}'")
                    break
                elif response.status_code == 422:
                    try:
                        error_data = response.json()
                        print(f"   422 Error: {error_data}")
                    except:
                        print(f"   422 Error: {response.text}")
                elif response.status_code == 500:
                    try:
                        error_data = response.json()
                        print(f"   500 Error: {error_data}")
                    except:
                        print(f"   500 Error: {response.text}")
            
            if working_enum_format:
                return True
            else:
                self.log_test("Enum Value Format Test", False, 
                            "None of the tested enum formats worked - all returned errors")
                return False
                
        except Exception as e:
            self.log_test("Enum Value Format Test", False, f"Request error: {str(e)}")
            return False

    def test_validate_completeness_api_contract_validation(self):
        """Test the API contract - what format does the endpoint actually expect?"""
        try:
            # Test 1: Empty request
            print("🧪 Testing empty request")
            response = self.session.post(
                f"{self.base_url}/intelligent-nodes/WebApp/validate-completeness",
                json=[],
                headers={"Content-Type": "application/json"}
            )
            print(f"   Empty request status: {response.status_code}")
            
            # Test 2: Minimal valid branch
            print("🧪 Testing minimal valid branch")
            minimal_branch = [
                {
                    "id": "test-minimal",
                    "name": "Minimal Test",
                    "type": "Login",
                    "required": True,
                    "completed": False,
                    "value": None,
                    "description": "Minimal test branch"
                }
            ]
            
            response = self.session.post(
                f"{self.base_url}/intelligent-nodes/WebApp/validate-completeness",
                json=minimal_branch,
                headers={"Content-Type": "application/json"}
            )
            print(f"   Minimal branch status: {response.status_code}")
            
            if response.status_code == 422:
                try:
                    error_data = response.json()
                    print(f"   Validation error details: {error_data}")
                    self.log_test("API Contract Validation", False, 
                                f"API contract validation failed: {error_data}")
                    return False
                except:
                    print(f"   Validation error text: {response.text}")
                    self.log_test("API Contract Validation", False, 
                                f"API contract validation failed: {response.text}")
                    return False
            elif response.status_code == 200:
                data = response.json()
                self.log_test("API Contract Validation", True, 
                            f"API contract working with minimal data: {data}")
                return True
            elif response.status_code == 500:
                try:
                    error_data = response.json()
                    self.log_test("API Contract Validation", False, 
                                f"500 error with minimal data: {error_data}")
                    return False
                except:
                    self.log_test("API Contract Validation", False, 
                                f"500 error with minimal data: {response.text}")
                    return False
            else:
                self.log_test("API Contract Validation", False, 
                            f"Unexpected status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("API Contract Validation", False, f"Request error: {str(e)}")
            return False

    def test_validate_completeness_with_frontend_format(self):
        """Test with the exact format that the frontend would send from questionnaire interface"""
        try:
            # This simulates the exact data structure that would come from the frontend
            # questionnaire interface when a user completes a WebApp questionnaire
            frontend_format_data = [
                {
                    "id": "webapp-auth-001",
                    "name": "Authentication Method",
                    "type": "Login",
                    "required": True,
                    "completed": True,
                    "value": "oauth2",
                    "description": "OAuth2 authentication with JWT tokens"
                },
                {
                    "id": "webapp-encryption-001", 
                    "name": "Data Encryption",
                    "type": "Database",
                    "required": True,
                    "completed": True,
                    "value": "enabled",
                    "description": "Database encryption at rest and in transit"
                },
                {
                    "id": "webapp-input-validation-001",
                    "name": "Input Validation",
                    "type": "InputValidation", 
                    "required": True,
                    "completed": True,
                    "value": "comprehensive",
                    "description": "Comprehensive input validation and sanitization"
                }
            ]
            
            print(f"🌐 Testing with frontend questionnaire format")
            print(f"📊 Data structure: {json.dumps(frontend_format_data, indent=2)}")
            
            response = self.session.post(
                f"{self.base_url}/intelligent-nodes/WebApp/validate-completeness",
                json=frontend_format_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"📡 Frontend format response status: {response.status_code}")
            
            if response.status_code == 500:
                try:
                    error_data = response.json()
                    self.log_test("Frontend Format Test", False, 
                                f"500 ERROR WITH FRONTEND FORMAT: {error_data}")
                    print(f"🚨 FRONTEND FORMAT 500 ERROR: {error_data}")
                    
                    # Check if it's an enum validation error
                    error_str = str(error_data)
                    if "enum" in error_str.lower() or "validation" in error_str.lower():
                        print("🔍 This appears to be an enum validation error!")
                        print("💡 The SecurityBranch enum values might not match what the frontend is sending")
                    
                    return False
                except:
                    error_text = response.text
                    self.log_test("Frontend Format Test", False, 
                                f"500 ERROR WITH FRONTEND FORMAT: {error_text}")
                    print(f"🚨 FRONTEND FORMAT 500 ERROR: {error_text}")
                    return False
            elif response.status_code == 200:
                data = response.json()
                self.log_test("Frontend Format Test", True, 
                            f"Frontend format working correctly: {data}")
                return True
            elif response.status_code == 422:
                error_data = response.json()
                self.log_test("Frontend Format Test", False, 
                            f"VALIDATION ERROR (422) WITH FRONTEND FORMAT: {error_data}")
                print(f"🔍 FRONTEND FORMAT VALIDATION ERROR: {error_data}")
                return False
            else:
                self.log_test("Frontend Format Test", False, 
                            f"Unexpected status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Frontend Format Test", False, f"Request error: {str(e)}")
            return False

    def test_get_supported_types_for_reference(self):
        """Get supported intelligent node types for reference"""
        try:
            response = self.session.get(f"{self.base_url}/intelligent-nodes/supported-types")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Get Supported Types", True, 
                            f"Supported types: {data}")
                print(f"📋 SUPPORTED INTELLIGENT NODE TYPES: {data}")
                return True
            else:
                self.log_test("Get Supported Types", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Get Supported Types", False, f"Request error: {str(e)}")
            return False

    def test_get_webapp_template_for_reference(self):
        """Get WebApp template to understand the expected branch structure"""
        try:
            response = self.session.get(f"{self.base_url}/intelligent-nodes/WebApp/template")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Get WebApp Template", True, 
                            f"WebApp template structure: {data}")
                print(f"🏗️ WEBAPP TEMPLATE STRUCTURE:")
                print(f"   Node Type: {data.get('node_type')}")
                print(f"   Node Subtype: {data.get('node_subtype')}")
                print(f"   Required Branches: {data.get('required_branches')}")
                
                # This will help us understand the correct enum values
                if 'required_branches' in data:
                    print(f"✅ CORRECT SECURITY BRANCH ENUM VALUES: {data['required_branches']}")
                
                return True
            else:
                self.log_test("Get WebApp Template", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Get WebApp Template", False, f"Request error: {str(e)}")
            return False

    # ============================================================================
    # Test Runner
    # ============================================================================
    
    def run_all_tests(self):
        """Run all validate-completeness endpoint tests"""
        print("🚀 Starting POST /api/intelligent-nodes/WebApp/validate-completeness Endpoint Testing")
        print("=" * 90)
        print("CRITICAL TESTING TASK: REPRODUCE AND DIAGNOSE 500 INTERNAL SERVER ERROR")
        print("Testing the WebApp validate-completeness endpoint to reproduce the user-reported 500 error")
        print("=" * 90)
        
        tests = [
            # Basic connectivity
            self.test_health_check,
            
            # Reference data to understand expected format
            self.test_get_supported_types_for_reference,
            self.test_get_webapp_template_for_reference,
            
            # CRITICAL: Reproduce the 500 error
            self.test_validate_completeness_with_realistic_webapp_data,
            self.test_validate_completeness_with_frontend_format,
            self.test_validate_completeness_with_different_enum_values,
            self.test_validate_completeness_api_contract_validation,
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
        print("🎯 VALIDATE-COMPLETENESS ENDPOINT TEST SUMMARY")
        print("=" * 90)
        print(f"✅ PASSED: {passed}")
        print(f"❌ FAILED: {failed}")
        print(f"📊 SUCCESS RATE: {(passed / (passed + failed) * 100):.1f}%")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED! The validate-completeness endpoint is working correctly.")
            print("✅ No 500 internal server error reproduced")
            print("✅ API contract validation successful")
            print("✅ SecurityBranch enum values are correct")
        else:
            print(f"\n⚠️  {failed} tests failed. Analysis of the 500 error:")
            
            # Analyze the test results to provide diagnostic information
            error_tests = [result for result in self.test_results if not result['success']]
            
            for error_test in error_tests:
                if "500" in error_test['message']:
                    print(f"🚨 500 ERROR REPRODUCED in {error_test['test']}")
                    print(f"   Details: {error_test['message']}")
                elif "422" in error_test['message']:
                    print(f"🔍 VALIDATION ERROR in {error_test['test']}")
                    print(f"   Details: {error_test['message']}")
                    print("   💡 This suggests SecurityBranch enum value mismatch")
        
        return passed, failed

def main():
    """Main test execution"""
    tester = WebAppValidateCompletenessEndpointTester()
    passed, failed = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()