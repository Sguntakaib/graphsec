#!/usr/bin/env python3
"""
Backend API Testing - Focus on validate-completeness endpoint
Tests the failing POST /api/intelligent-nodes/WebApp/validate-completeness endpoint
as reported by the user throwing 500 error.
"""

import requests
import json
import uuid
from datetime import datetime, timezone
import sys

# Use the backend URL from frontend/.env with /api suffix
BASE_URL = "https://webapp-validator.preview.emergentagent.com/api"

class ValidateCompletenessEndpointTester:
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

    def test_validate_completeness_endpoint_basic(self):
        """Test POST /api/intelligent-nodes/WebApp/validate-completeness with basic data"""
        try:
            # Based on test_result.md, this endpoint should accept direct list format
            request_data = [
                {
                    "id": "login-branch",
                    "name": "Login Security",
                    "type": "Login",
                    "required": True,
                    "completed": True,
                    "value": "oauth2",
                    "description": "Authentication method configuration"
                },
                {
                    "id": "encryption-branch", 
                    "name": "Data Encryption",
                    "type": "Encryption",
                    "required": True,
                    "completed": True,
                    "value": "enabled",
                    "description": "Data encryption configuration"
                }
            ]
            
            response = self.session.post(
                f"{self.base_url}/intelligent-nodes/WebApp/validate-completeness",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Response Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            print(f"Response Text: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Expected fields based on test_result.md
                expected_fields = ["completion_percentage", "is_complete", "recommendations"]
                missing_fields = [f for f in expected_fields if f not in data]
                
                if missing_fields:
                    self.log_test("Validate Completeness Basic", False, 
                                f"Missing expected fields: {missing_fields}. Got: {list(data.keys())}")
                    return False
                
                completion_percentage = data.get("completion_percentage")
                is_complete = data.get("is_complete")
                recommendations = data.get("recommendations", [])
                
                # Validate data types
                if not isinstance(completion_percentage, (int, float)):
                    self.log_test("Validate Completeness Basic", False, 
                                f"completion_percentage should be numeric, got: {type(completion_percentage)}")
                    return False
                
                if not isinstance(is_complete, bool):
                    self.log_test("Validate Completeness Basic", False, 
                                f"is_complete should be boolean, got: {type(is_complete)}")
                    return False
                
                if not isinstance(recommendations, list):
                    self.log_test("Validate Completeness Basic", False, 
                                f"recommendations should be list, got: {type(recommendations)}")
                    return False
                
                self.log_test("Validate Completeness Basic", True, 
                            f"Endpoint working - completion: {completion_percentage}%, complete: {is_complete}, recommendations: {len(recommendations)}")
                return True
                
            elif response.status_code == 500:
                # This is the reported error - capture the exact error message
                error_text = response.text
                self.log_test("Validate Completeness Basic", False, 
                            f"HTTP 500 Internal Server Error: {error_text}")
                return False
            else:
                self.log_test("Validate Completeness Basic", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Validate Completeness Basic", False, f"Error: {str(e)}")
            return False

    def test_validate_completeness_endpoint_empty_list(self):
        """Test POST /api/intelligent-nodes/WebApp/validate-completeness with empty list"""
        try:
            request_data = []
            
            response = self.session.post(
                f"{self.base_url}/intelligent-nodes/WebApp/validate-completeness",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Empty List Test - Status: {response.status_code}")
            print(f"Empty List Test - Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                completion_percentage = data.get("completion_percentage", 0)
                is_complete = data.get("is_complete", False)
                
                # Empty list should result in 0% completion and not complete
                if completion_percentage == 0 and is_complete == False:
                    self.log_test("Validate Completeness Empty List", True, 
                                f"Empty list handled correctly - 0% completion, not complete")
                    return True
                else:
                    self.log_test("Validate Completeness Empty List", False, 
                                f"Empty list not handled correctly - completion: {completion_percentage}%, complete: {is_complete}")
                    return False
            else:
                self.log_test("Validate Completeness Empty List", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Validate Completeness Empty List", False, f"Error: {str(e)}")
            return False

    def test_validate_completeness_endpoint_incomplete_branches(self):
        """Test POST /api/intelligent-nodes/WebApp/validate-completeness with incomplete branches"""
        try:
            request_data = [
                {
                    "id": "login-branch",
                    "name": "Login Security", 
                    "type": "Login",
                    "required": True,
                    "completed": False,  # Not completed
                    "value": None,
                    "description": "Authentication method configuration"
                },
                {
                    "id": "encryption-branch",
                    "name": "Data Encryption",
                    "type": "Encryption", 
                    "required": True,
                    "completed": True,
                    "value": "enabled",
                    "description": "Data encryption configuration"
                },
                {
                    "id": "validation-branch",
                    "name": "Input Validation",
                    "type": "InputValidation",
                    "required": True,
                    "completed": False,  # Not completed
                    "value": None,
                    "description": "Input validation configuration"
                }
            ]
            
            response = self.session.post(
                f"{self.base_url}/intelligent-nodes/WebApp/validate-completeness",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Incomplete Branches Test - Status: {response.status_code}")
            print(f"Incomplete Branches Test - Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                completion_percentage = data.get("completion_percentage", 0)
                is_complete = data.get("is_complete", True)
                recommendations = data.get("recommendations", [])
                
                # Should be partially complete (33.3% - 1 out of 3 completed)
                expected_percentage = 33.3
                if abs(completion_percentage - expected_percentage) < 5:  # Allow some tolerance
                    if is_complete == False and len(recommendations) > 0:
                        self.log_test("Validate Completeness Incomplete", True, 
                                    f"Incomplete branches handled correctly - {completion_percentage}% completion, not complete, {len(recommendations)} recommendations")
                        return True
                    else:
                        self.log_test("Validate Completeness Incomplete", False, 
                                    f"Incomplete branches logic error - complete: {is_complete}, recommendations: {len(recommendations)}")
                        return False
                else:
                    self.log_test("Validate Completeness Incomplete", False, 
                                f"Completion percentage incorrect - expected ~{expected_percentage}%, got {completion_percentage}%")
                    return False
            else:
                self.log_test("Validate Completeness Incomplete", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Validate Completeness Incomplete", False, f"Error: {str(e)}")
            return False

    def test_validate_completeness_endpoint_malformed_data(self):
        """Test POST /api/intelligent-nodes/WebApp/validate-completeness with malformed data"""
        try:
            # Test with object instead of list (previous API contract issue)
            request_data = {
                "branches": [
                    {
                        "id": "login-branch",
                        "name": "Login Security",
                        "type": "Login",
                        "required": True,
                        "completed": True,
                        "value": "oauth2"
                    }
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/intelligent-nodes/WebApp/validate-completeness",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Malformed Data Test - Status: {response.status_code}")
            print(f"Malformed Data Test - Response: {response.text}")
            
            # This should fail with proper error message
            if response.status_code == 422 or response.status_code == 400:
                self.log_test("Validate Completeness Malformed", True, 
                            f"Malformed data properly rejected with HTTP {response.status_code}")
                return True
            elif response.status_code == 500:
                self.log_test("Validate Completeness Malformed", False, 
                            f"HTTP 500 error for malformed data - should be 400/422: {response.text}")
                return False
            else:
                self.log_test("Validate Completeness Malformed", False, 
                            f"Unexpected response for malformed data - HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Validate Completeness Malformed", False, f"Error: {str(e)}")
            return False

    def test_backend_logs_check(self):
        """Check backend logs for any errors"""
        try:
            import subprocess
            result = subprocess.run(
                ["tail", "-n", "50", "/var/log/supervisor/backend.err.log"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                log_content = result.stdout
                if log_content.strip():
                    print(f"Backend Error Logs (last 50 lines):")
                    print("=" * 50)
                    print(log_content)
                    print("=" * 50)
                    
                    # Check for specific errors related to validate-completeness
                    if "validate-completeness" in log_content.lower() or "intelligent-nodes" in log_content.lower():
                        self.log_test("Backend Logs Check", False, 
                                    "Found errors related to validate-completeness in backend logs")
                        return False
                    else:
                        self.log_test("Backend Logs Check", True, 
                                    "Backend logs checked - no validate-completeness specific errors")
                        return True
                else:
                    self.log_test("Backend Logs Check", True, "No recent backend errors in logs")
                    return True
            else:
                self.log_test("Backend Logs Check", False, f"Could not read backend logs: {result.stderr}")
                return False
                
        except Exception as e:
            self.log_test("Backend Logs Check", False, f"Error checking logs: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all validate-completeness endpoint tests"""
        print("🚀 Starting Validate-Completeness Endpoint Tests")
        print("=" * 80)
        
        tests = [
            # Basic connectivity
            self.test_health_check,
            
            # Validate-completeness endpoint tests
            self.test_validate_completeness_endpoint_basic,
            self.test_validate_completeness_endpoint_empty_list,
            self.test_validate_completeness_endpoint_incomplete_branches,
            self.test_validate_completeness_endpoint_malformed_data,
            
            # Backend logs check
            self.test_backend_logs_check
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
        print("🎯 VALIDATE-COMPLETENESS ENDPOINT TEST SUMMARY")
        print("=" * 80)
        print(f"✅ PASSED: {passed}")
        print(f"❌ FAILED: {failed}")
        print(f"📊 SUCCESS RATE: {(passed / (passed + failed) * 100):.1f}%")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED! Validate-completeness endpoint is working correctly.")
        else:
            print(f"\n⚠️  {failed} tests failed. Please review the failed tests above.")
        
        return passed, failed

def main():
    """Main test execution"""
    tester = ValidateCompletenessEndpointTester()
    passed, failed = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()