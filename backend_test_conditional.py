#!/usr/bin/env python3
"""
Backend API Testing - Conditional Questionnaire Dependency System
Tests the conditional questionnaire dependency system that enables:
1. WebApp questionnaire contains questions like "Do you use API?" and "Do you use Database?"
2. Backend endpoint to check dependencies based on questionnaire answers
3. When user answers "yes" to API/Database questions, those dependencies should be identified
"""

import requests
import json
import uuid
from datetime import datetime, timezone
import sys

# Use the backend URL from frontend/.env with /api suffix
BASE_URL = "https://node-detection.preview.emergentagent.com/api"

class ConditionalDependencyTester:
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
    # CONDITIONAL QUESTIONNAIRE DEPENDENCY SYSTEM TESTS
    # ============================================================================
    
    def test_webapp_questionnaire_contains_dependency_questions(self):
        """Test GET /api/intelligent-nodes/WebApp/prompts - Check if it contains conditional questions about API/Database usage"""
        try:
            response = self.session.get(f"{self.base_url}/intelligent-nodes/WebApp/prompts")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for prompts in response
                prompts = data.get("prompts", [])
                
                if len(prompts) == 0:
                    self.log_test("WebApp Dependency Questions", False, "No prompts found in WebApp intelligent-nodes questionnaire")
                    return False
                
                # Look for specific dependency questions
                api_questions = []
                database_questions = []
                
                for question in prompts:
                    question_text = question.get("question", "").lower()
                    question_id = question.get("id", "").lower()
                    
                    # Check for specific API dependency question
                    if "webapp_api_endpoints" in question_id or "api endpoints" in question_text:
                        api_questions.append(question)
                    
                    # Check for specific Database dependency question  
                    if "webapp_database_connection" in question_id or ("database" in question_text and "connect" in question_text):
                        database_questions.append(question)
                
                if len(api_questions) == 0:
                    self.log_test("WebApp Dependency Questions", False, 
                                f"No API dependency question found in WebApp intelligent-nodes questionnaire. Questions: {[q.get('question', q.get('id', 'Unknown')) for q in prompts[:5]]}")
                    return False
                
                if len(database_questions) == 0:
                    self.log_test("WebApp Dependency Questions", False, 
                                f"No Database dependency question found in WebApp intelligent-nodes questionnaire. Questions: {[q.get('question', q.get('id', 'Unknown')) for q in prompts[:5]]}")
                    return False
                
                self.log_test("WebApp Dependency Questions", True, 
                            f"WebApp intelligent-nodes questionnaire contains API and Database dependency questions")
                return True
            else:
                self.log_test("WebApp Dependency Questions", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("WebApp Dependency Questions", False, f"Error: {str(e)}")
            return False

    def test_check_dependencies_api_yes_database_no(self):
        """Test POST /api/intelligent-nodes/WebApp/check-dependencies - API=yes, Database=no"""
        try:
            request_data = {
                "answers": {
                    "webapp_api_endpoints": "yes",
                    "webapp_database_connection": "no"
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/intelligent-nodes/WebApp/check-dependencies",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Should return API dependency but not Database
                dependent_nodes = data.get("dependent_nodes", [])
                
                if "API" not in dependent_nodes:
                    self.log_test("Check Dependencies API=yes DB=no", False, 
                                f"Expected 'API' in dependent_nodes but got: {dependent_nodes}")
                    return False
                
                if "Database" in dependent_nodes:
                    self.log_test("Check Dependencies API=yes DB=no", False, 
                                f"Did not expect 'Database' in dependent_nodes but got: {dependent_nodes}")
                    return False
                
                self.log_test("Check Dependencies API=yes DB=no", True, 
                            f"Correctly identified API dependency only: {dependent_nodes}")
                return True
            else:
                self.log_test("Check Dependencies API=yes DB=no", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Check Dependencies API=yes DB=no", False, f"Error: {str(e)}")
            return False

    def test_check_dependencies_api_no_database_yes(self):
        """Test POST /api/intelligent-nodes/WebApp/check-dependencies - API=no, Database=yes"""
        try:
            request_data = {
                "answers": {
                    "webapp_api_endpoints": "no",
                    "webapp_database_connection": "yes"
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/intelligent-nodes/WebApp/check-dependencies",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Should return Database dependency but not API
                dependent_nodes = data.get("dependent_nodes", [])
                
                if "Database" not in dependent_nodes:
                    self.log_test("Check Dependencies API=no DB=yes", False, 
                                f"Expected 'Database' in dependent_nodes but got: {dependent_nodes}")
                    return False
                
                if "API" in dependent_nodes:
                    self.log_test("Check Dependencies API=no DB=yes", False, 
                                f"Did not expect 'API' in dependent_nodes but got: {dependent_nodes}")
                    return False
                
                self.log_test("Check Dependencies API=no DB=yes", True, 
                            f"Correctly identified Database dependency only: {dependent_nodes}")
                return True
            else:
                self.log_test("Check Dependencies API=no DB=yes", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Check Dependencies API=no DB=yes", False, f"Error: {str(e)}")
            return False

    def test_check_dependencies_both_yes(self):
        """Test POST /api/intelligent-nodes/WebApp/check-dependencies - API=yes, Database=yes"""
        try:
            request_data = {
                "answers": {
                    "webapp_api_endpoints": "yes",
                    "webapp_database_connection": "yes"
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/intelligent-nodes/WebApp/check-dependencies",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Should return both API and Database dependencies
                dependent_nodes = data.get("dependent_nodes", [])
                
                if "API" not in dependent_nodes:
                    self.log_test("Check Dependencies Both=yes", False, 
                                f"Expected 'API' in dependent_nodes but got: {dependent_nodes}")
                    return False
                
                if "Database" not in dependent_nodes:
                    self.log_test("Check Dependencies Both=yes", False, 
                                f"Expected 'Database' in dependent_nodes but got: {dependent_nodes}")
                    return False
                
                self.log_test("Check Dependencies Both=yes", True, 
                            f"Correctly identified both dependencies: {dependent_nodes}")
                return True
            else:
                self.log_test("Check Dependencies Both=yes", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Check Dependencies Both=yes", False, f"Error: {str(e)}")
            return False

    def test_check_dependencies_both_no(self):
        """Test POST /api/intelligent-nodes/WebApp/check-dependencies - API=no, Database=no"""
        try:
            request_data = {
                "answers": {
                    "webapp_api_endpoints": "no",
                    "webapp_database_connection": "no"
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/intelligent-nodes/WebApp/check-dependencies",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Should return empty dependencies
                dependent_nodes = data.get("dependent_nodes", [])
                
                if len(dependent_nodes) > 0:
                    self.log_test("Check Dependencies Both=no", False, 
                                f"Expected no dependent_nodes but got: {dependent_nodes}")
                    return False
                
                self.log_test("Check Dependencies Both=no", True, 
                            f"Correctly identified no dependencies: {dependent_nodes}")
                return True
            else:
                self.log_test("Check Dependencies Both=no", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Check Dependencies Both=no", False, f"Error: {str(e)}")
            return False

    def test_api_questionnaire_exists(self):
        """Test GET /api/questionnaires/API - Verify API questionnaire template exists"""
        try:
            response = self.session.get(f"{self.base_url}/questionnaires/API")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for prompts or questions in response
                prompts = data.get("prompts", [])
                questions = data.get("questions", [])
                security_branches = data.get("security_branches", [])
                
                all_questions = prompts + questions
                
                if len(all_questions) == 0 and len(security_branches) == 0:
                    self.log_test("API Questionnaire Exists", False, "API questionnaire has no questions/prompts/branches")
                    return False
                
                self.log_test("API Questionnaire Exists", True, 
                            f"API questionnaire exists with {len(all_questions)} questions and {len(security_branches)} branches")
                return True
            else:
                self.log_test("API Questionnaire Exists", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("API Questionnaire Exists", False, f"Error: {str(e)}")
            return False

    def test_database_questionnaire_exists(self):
        """Test GET /api/questionnaires/Database - Verify Database questionnaire template exists"""
        try:
            response = self.session.get(f"{self.base_url}/questionnaires/Database")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for prompts or questions in response
                prompts = data.get("prompts", [])
                questions = data.get("questions", [])
                security_branches = data.get("security_branches", [])
                
                all_questions = prompts + questions
                
                if len(all_questions) == 0 and len(security_branches) == 0:
                    self.log_test("Database Questionnaire Exists", False, "Database questionnaire has no questions/prompts/branches")
                    return False
                
                self.log_test("Database Questionnaire Exists", True, 
                            f"Database questionnaire exists with {len(all_questions)} questions and {len(security_branches)} branches")
                return True
            else:
                self.log_test("Database Questionnaire Exists", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Database Questionnaire Exists", False, f"Error: {str(e)}")
            return False

    # ============================================================================
    # Test Runner
    # ============================================================================
    
    def run_all_tests(self):
        """Run all conditional questionnaire dependency system tests"""
        print("🚀 Starting Conditional Questionnaire Dependency System Tests")
        print("=" * 80)
        
        tests = [
            # Basic connectivity
            self.test_health_check,
            
            # Core conditional dependency system tests
            self.test_webapp_questionnaire_contains_dependency_questions,
            self.test_check_dependencies_api_yes_database_no,
            self.test_check_dependencies_api_no_database_yes,
            self.test_check_dependencies_both_yes,
            self.test_check_dependencies_both_no,
            self.test_api_questionnaire_exists,
            self.test_database_questionnaire_exists,
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
        print("🎯 CONDITIONAL QUESTIONNAIRE DEPENDENCY SYSTEM TEST SUMMARY")
        print("=" * 80)
        print(f"✅ PASSED: {passed}")
        print(f"❌ FAILED: {failed}")
        print(f"📊 SUCCESS RATE: {(passed / (passed + failed) * 100):.1f}%")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED! Conditional questionnaire dependency system is working correctly.")
        else:
            print(f"\n⚠️  {failed} tests failed. Please review the failed tests above.")
        
        return passed, failed

def main():
    """Main test execution"""
    tester = ConditionalDependencyTester()
    passed, failed = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()