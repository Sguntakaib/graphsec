#!/usr/bin/env python3
"""
VERIFICATION TEST: Confirm that the validate-completeness endpoint 500 error has been fixed
This test specifically verifies the fix for the user-reported 500 error after frontend enum mapping updates.

CRITICAL TEST SCENARIOS:
1. Test POST /api/intelligent-nodes/WebApp/validate-completeness with EXACT frontend request format
2. Verify PascalCase enum values (Login, Database, API, InputValidation, WAF, Deployment) work correctly
3. Confirm endpoint returns HTTP 200 instead of HTTP 500
4. Test both working and error scenarios to ensure proper enum validation
"""

import requests
import json
import sys

# Backend URL from the review request
BASE_URL = "https://appsec-survey.preview.emergentagent.com/api"

class ValidateCompletenessVerificationTester:
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
        
    def test_frontend_enum_mapping_fix_verification(self):
        """CRITICAL: Verify the frontend enum mapping fix works correctly"""
        try:
            # This is the EXACT request format that the frontend now sends
            # with PascalCase enum values as per the fix
            frontend_request_data = [
                {
                    "id": "webapp-login-branch",
                    "name": "Authentication System",
                    "type": "Login",  # PascalCase - this was the fix
                    "required": True,
                    "completed": True,
                    "value": "oauth2",
                    "description": "OAuth2 authentication implementation"
                },
                {
                    "id": "webapp-database-branch",
                    "name": "Database Security",
                    "type": "Database",  # PascalCase - this was the fix
                    "required": True,
                    "completed": True,
                    "value": "encrypted",
                    "description": "Database encryption enabled"
                },
                {
                    "id": "webapp-api-branch",
                    "name": "API Security",
                    "type": "API",  # PascalCase - this was the fix
                    "required": True,
                    "completed": False,
                    "value": None,
                    "description": "API security configuration"
                },
                {
                    "id": "webapp-input-validation-branch",
                    "name": "Input Validation",
                    "type": "InputValidation",  # PascalCase - this was the fix
                    "required": True,
                    "completed": True,
                    "value": "comprehensive",
                    "description": "Comprehensive input validation"
                },
                {
                    "id": "webapp-waf-branch",
                    "name": "Web Application Firewall",
                    "type": "WAF",  # PascalCase - this was the fix
                    "required": False,
                    "completed": False,
                    "value": None,
                    "description": "WAF protection"
                },
                {
                    "id": "webapp-deployment-branch",
                    "name": "Deployment Security",
                    "type": "Deployment",  # PascalCase - this was the fix
                    "required": True,
                    "completed": True,
                    "value": "secure",
                    "description": "Secure deployment configuration"
                }
            ]
            
            print("🎯 VERIFICATION TEST: Frontend Enum Mapping Fix")
            print(f"📋 Testing with PascalCase enum values: {[b['type'] for b in frontend_request_data]}")
            
            response = self.session.post(
                f"{self.base_url}/intelligent-nodes/WebApp/validate-completeness",
                json=frontend_request_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"📡 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Frontend Enum Mapping Fix", True, 
                            f"✅ VERIFICATION SUCCESSFUL: Endpoint returns HTTP 200 with PascalCase enums. Response: {data}")
                print("🎉 SUCCESS: The 500 error has been FIXED!")
                print("✅ Frontend enum mapping with PascalCase values works correctly")
                print(f"📊 Validation Result: {data}")
                return True
            elif response.status_code == 500:
                try:
                    error_data = response.json()
                    self.log_test("Frontend Enum Mapping Fix", False, 
                                f"❌ VERIFICATION FAILED: Still getting HTTP 500 error: {error_data}")
                    print("🚨 FAILURE: The 500 error is NOT FIXED!")
                    print(f"💥 Error Details: {error_data}")
                    return False
                except:
                    error_text = response.text
                    self.log_test("Frontend Enum Mapping Fix", False, 
                                f"❌ VERIFICATION FAILED: Still getting HTTP 500 error: {error_text}")
                    print("🚨 FAILURE: The 500 error is NOT FIXED!")
                    print(f"💥 Error Text: {error_text}")
                    return False
            else:
                self.log_test("Frontend Enum Mapping Fix", False, 
                            f"❌ UNEXPECTED STATUS: Expected 200 or 500, got {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Frontend Enum Mapping Fix", False, f"❌ REQUEST ERROR: {str(e)}")
            return False

    def test_old_enum_format_still_fails(self):
        """Verify that the old lowercase enum format still returns 500 (as expected)"""
        try:
            # This is the OLD format that was causing the 500 error
            old_format_data = [
                {
                    "id": "test-branch",
                    "name": "Test Branch",
                    "type": "login",  # lowercase - this should still cause 500
                    "required": True,
                    "completed": True,
                    "value": "oauth2",
                    "description": "Test branch"
                }
            ]
            
            print("🧪 Testing old lowercase enum format (should still fail)")
            
            response = self.session.post(
                f"{self.base_url}/intelligent-nodes/WebApp/validate-completeness",
                json=old_format_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"📡 Old format response status: {response.status_code}")
            
            if response.status_code == 500:
                self.log_test("Old Enum Format Validation", True, 
                            "✅ CORRECT: Old lowercase enum format still returns 500 as expected")
                print("✅ CORRECT: Old format still fails (proper validation)")
                return True
            else:
                self.log_test("Old Enum Format Validation", False, 
                            f"❌ UNEXPECTED: Old format should return 500 but got {response.status_code}")
                print(f"⚠️  UNEXPECTED: Old format returned {response.status_code} instead of 500")
                return False
                
        except Exception as e:
            self.log_test("Old Enum Format Validation", False, f"❌ REQUEST ERROR: {str(e)}")
            return False

    def test_mixed_case_scenarios(self):
        """Test various enum case scenarios to ensure proper validation"""
        try:
            test_cases = [
                {
                    "name": "All PascalCase (should work)",
                    "data": [{"id": "test", "name": "Test", "type": "Login", "required": True, "completed": True, "value": "test", "description": "Test"}],
                    "expected_status": 200
                },
                {
                    "name": "Mixed case (should fail)",
                    "data": [{"id": "test", "name": "Test", "type": "login", "required": True, "completed": True, "value": "test", "description": "Test"}],
                    "expected_status": 500
                },
                {
                    "name": "All uppercase (should fail)",
                    "data": [{"id": "test", "name": "Test", "type": "LOGIN", "required": True, "completed": True, "value": "test", "description": "Test"}],
                    "expected_status": 500
                }
            ]
            
            all_passed = True
            
            for test_case in test_cases:
                print(f"🧪 Testing: {test_case['name']}")
                
                response = self.session.post(
                    f"{self.base_url}/intelligent-nodes/WebApp/validate-completeness",
                    json=test_case['data'],
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == test_case['expected_status']:
                    print(f"   ✅ CORRECT: Got expected status {response.status_code}")
                else:
                    print(f"   ❌ WRONG: Expected {test_case['expected_status']}, got {response.status_code}")
                    all_passed = False
            
            if all_passed:
                self.log_test("Mixed Case Scenarios", True, "✅ All enum case scenarios behave correctly")
                return True
            else:
                self.log_test("Mixed Case Scenarios", False, "❌ Some enum case scenarios failed")
                return False
                
        except Exception as e:
            self.log_test("Mixed Case Scenarios", False, f"❌ REQUEST ERROR: {str(e)}")
            return False

    def test_response_structure_validation(self):
        """Verify the response structure is correct when the endpoint works"""
        try:
            # Use correct PascalCase format
            test_data = [
                {
                    "id": "test-login",
                    "name": "Login Test",
                    "type": "Login",
                    "required": True,
                    "completed": True,
                    "value": "oauth2",
                    "description": "Test login branch"
                }
            ]
            
            response = self.session.post(
                f"{self.base_url}/intelligent-nodes/WebApp/validate-completeness",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required response fields
                required_fields = ['node_subtype', 'validation', 'recommendations']
                validation_fields = ['is_complete', 'completion_percentage', 'missing_branches', 'completed_count', 'required_count']
                
                missing_fields = []
                for field in required_fields:
                    if field not in data:
                        missing_fields.append(field)
                
                if 'validation' in data:
                    for field in validation_fields:
                        if field not in data['validation']:
                            missing_fields.append(f"validation.{field}")
                
                if not missing_fields:
                    self.log_test("Response Structure", True, 
                                f"✅ Response structure is correct: {data}")
                    print("✅ Response structure validation passed")
                    return True
                else:
                    self.log_test("Response Structure", False, 
                                f"❌ Missing required fields: {missing_fields}")
                    return False
            else:
                self.log_test("Response Structure", False, 
                            f"❌ Cannot validate structure, got HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Response Structure", False, f"❌ REQUEST ERROR: {str(e)}")
            return False

    def run_verification_tests(self):
        """Run all verification tests"""
        print("🎯 VERIFICATION TEST: validate-completeness endpoint 500 error fix")
        print("=" * 80)
        print("TESTING: Confirm that frontend enum mapping fix resolved the 500 error")
        print("BACKEND URL:", self.base_url)
        print("=" * 80)
        
        tests = [
            self.test_frontend_enum_mapping_fix_verification,  # CRITICAL TEST
            self.test_old_enum_format_still_fails,
            self.test_mixed_case_scenarios,
            self.test_response_structure_validation,
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
        print("=" * 80)
        print("🎯 VERIFICATION TEST SUMMARY")
        print("=" * 80)
        print(f"✅ PASSED: {passed}")
        print(f"❌ FAILED: {failed}")
        print(f"📊 SUCCESS RATE: {(passed / (passed + failed) * 100):.1f}%")
        
        if failed == 0:
            print("\n🎉 VERIFICATION SUCCESSFUL!")
            print("✅ The validate-completeness endpoint 500 error has been FIXED")
            print("✅ Frontend enum mapping with PascalCase values works correctly")
            print("✅ Endpoint now returns HTTP 200 instead of HTTP 500")
            print("✅ Response structure is correct")
            print("\n💡 CONCLUSION: The user's reported 500 error has been resolved!")
        else:
            print(f"\n⚠️  VERIFICATION FAILED: {failed} tests failed")
            print("🚨 The 500 error may NOT be fully resolved")
            
            # Show critical test result
            critical_test = next((r for r in self.test_results if "Frontend Enum Mapping Fix" in r['test']), None)
            if critical_test and not critical_test['success']:
                print("💥 CRITICAL: The main verification test failed!")
                print(f"   Details: {critical_test['message']}")
        
        return passed, failed

def main():
    """Main test execution"""
    tester = ValidateCompletenessVerificationTester()
    passed, failed = tester.run_verification_tests()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()