#!/usr/bin/env python3
"""
Backend API Testing - WebApp Questionnaire Dependency Questions Verification
Tests the WebApp questionnaire endpoint to verify dependency questions are now included.
Focus: Verify that WebApp questionnaire now includes "Do you use API?" and "Do you use Database?" dependency questions.
"""

import requests
import json
import uuid
from datetime import datetime, timezone
import sys

# Use the backend URL from frontend/.env with /api suffix
BASE_URL = "https://smart-forms-14.preview.emergentagent.com/api"

class WebAppDependencyQuestionsTester:
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
    # CRITICAL TESTING TASK: VERIFY DEPENDENCY QUESTIONS IN WEBAPP QUESTIONNAIRE
    # ============================================================================
    
    def test_webapp_questionnaire_content(self):
        """Test GET /api/questionnaires/WebApp?level=basic - should return MORE than 8 questions with dependency questions"""
        try:
            response = self.session.get(f"{self.base_url}/questionnaires/WebApp?level=basic")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                expected_fields = ["prompts", "total_questions"]
                missing_fields = [f for f in expected_fields if f not in data]
                
                if missing_fields:
                    self.log_test("WebApp Questionnaire Content", False, f"Missing response fields: {missing_fields}")
                    return False
                
                prompts = data.get("prompts", [])
                total_questions = data.get("total_questions", 0)
                
                # Should have MORE than 8 questions (now should have 10 questions including 2 new dependency questions)
                if total_questions <= 8:
                    self.log_test("WebApp Questionnaire Content", False, 
                                f"Expected MORE than 8 questions, got {total_questions}. Previous version had 8, new should have 10.")
                    return False
                
                if len(prompts) <= 8:
                    self.log_test("WebApp Questionnaire Content", False, 
                                f"Expected MORE than 8 prompts, got {len(prompts)}. Previous version had 8, new should have 10.")
                    return False
                
                # Look for the two new dependency questions
                api_dependency_question = None
                database_dependency_question = None
                
                for prompt in prompts:
                    prompt_id = prompt.get("id", "")
                    question_text = prompt.get("question", "")
                    
                    # Check for API dependency question
                    if prompt_id == "webapp_api_endpoints" or "API endpoints" in question_text:
                        api_dependency_question = prompt
                    
                    # Check for Database dependency question  
                    if prompt_id == "webapp_database_connection" or "database" in question_text.lower():
                        database_dependency_question = prompt
                
                # Verify API dependency question
                if not api_dependency_question:
                    self.log_test("WebApp Questionnaire Content", False, 
                                "Missing API dependency question (webapp_api_endpoints)")
                    return False
                
                # Verify Database dependency question
                if not database_dependency_question:
                    self.log_test("WebApp Questionnaire Content", False, 
                                "Missing Database dependency question (webapp_database_connection)")
                    return False
                
                # Verify both dependency questions have type: "boolean"
                if api_dependency_question.get("type") != "boolean":
                    self.log_test("WebApp Questionnaire Content", False, 
                                f"API dependency question should have type 'boolean', got '{api_dependency_question.get('type')}'")
                    return False
                
                if database_dependency_question.get("type") != "boolean":
                    self.log_test("WebApp Questionnaire Content", False, 
                                f"Database dependency question should have type 'boolean', got '{database_dependency_question.get('type')}'")
                    return False
                
                # Check for dependencies field with conditional mappings
                dependencies = data.get("dependencies", {})
                if not dependencies:
                    self.log_test("WebApp Questionnaire Content", False, 
                                "Missing dependencies field with conditional mappings")
                    return False
                
                # Verify dependency mappings
                # Note: The actual implementation uses webapp_api_enabled instead of webapp_api_endpoints
                expected_mappings = {
                    "webapp_api_enabled": "API",
                    "webapp_database_connection": "Database"
                }
                
                for dep_id, expected_target in expected_mappings.items():
                    if dep_id not in dependencies:
                        self.log_test("WebApp Questionnaire Content", False, 
                                    f"Missing dependency mapping for {dep_id}")
                        return False
                    
                    if dependencies[dep_id] != expected_target:
                        self.log_test("WebApp Questionnaire Content", False, 
                                    f"Incorrect dependency mapping for {dep_id}: expected '{expected_target}', got '{dependencies[dep_id]}'")
                        return False
                
                self.log_test("WebApp Questionnaire Content", True, 
                            f"WebApp questionnaire now has {total_questions} questions (up from 8), includes both dependency questions with proper structure and mappings")
                return True
            else:
                self.log_test("WebApp Questionnaire Content", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("WebApp Questionnaire Content", False, f"Error: {str(e)}")
            return False

    def test_dependency_questions_validation(self):
        """Test that both new dependency questions have correct structure"""
        try:
            response = self.session.get(f"{self.base_url}/questionnaires/WebApp?level=basic")
            
            if response.status_code == 200:
                data = response.json()
                prompts = data.get("prompts", [])
                
                # Find the dependency questions
                api_question = None
                database_question = None
                
                for prompt in prompts:
                    prompt_id = prompt.get("id", "")
                    if prompt_id == "webapp_api_endpoints":
                        api_question = prompt
                    elif prompt_id == "webapp_database_connection":
                        database_question = prompt
                
                if not api_question:
                    self.log_test("Dependency Questions Validation", False, "API dependency question not found")
                    return False
                
                if not database_question:
                    self.log_test("Dependency Questions Validation", False, "Database dependency question not found")
                    return False
                
                # Validate API question structure
                expected_api_question = "Does this web application expose API endpoints?"
                if expected_api_question not in api_question.get("question", ""):
                    self.log_test("Dependency Questions Validation", False, 
                                f"API question text incorrect. Expected: '{expected_api_question}', got: '{api_question.get('question')}'")
                    return False
                
                # Validate Database question structure
                expected_db_question = "Does this application connect to a database?"
                if expected_db_question not in database_question.get("question", ""):
                    self.log_test("Dependency Questions Validation", False, 
                                f"Database question text incorrect. Expected: '{expected_db_question}', got: '{database_question.get('question')}'")
                    return False
                
                # Verify both have required fields
                required_fields = ["id", "question", "type", "help_text", "required"]
                
                for question, name in [(api_question, "API"), (database_question, "Database")]:
                    missing_fields = [f for f in required_fields if f not in question]
                    if missing_fields:
                        self.log_test("Dependency Questions Validation", False, 
                                    f"{name} dependency question missing fields: {missing_fields}")
                        return False
                    
                    if question.get("type") != "boolean":
                        self.log_test("Dependency Questions Validation", False, 
                                    f"{name} dependency question should have type 'boolean', got '{question.get('type')}'")
                        return False
                    
                    if not question.get("required"):
                        self.log_test("Dependency Questions Validation", False, 
                                    f"{name} dependency question should be required")
                        return False
                
                self.log_test("Dependency Questions Validation", True, 
                            "Both dependency questions have correct structure, text, type (boolean), and required fields")
                return True
            else:
                self.log_test("Dependency Questions Validation", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Dependency Questions Validation", False, f"Error: {str(e)}")
            return False

    def test_compare_to_previous_version(self):
        """Test that new version has more questions than previous version (8 -> 10)"""
        try:
            response = self.session.get(f"{self.base_url}/questionnaires/WebApp?level=basic")
            
            if response.status_code == 200:
                data = response.json()
                total_questions = data.get("total_questions", 0)
                prompts = data.get("prompts", [])
                
                # Previous version had 8 questions, new should have 10
                expected_new_count = 10
                previous_count = 8
                
                if total_questions != expected_new_count:
                    self.log_test("Compare to Previous Version", False, 
                                f"Expected exactly {expected_new_count} questions, got {total_questions}. Previous version had {previous_count}.")
                    return False
                
                if len(prompts) != expected_new_count:
                    self.log_test("Compare to Previous Version", False, 
                                f"Expected exactly {expected_new_count} prompts, got {len(prompts)}. Previous version had {previous_count}.")
                    return False
                
                # Verify the 2 new questions are the dependency questions
                dependency_question_ids = ["webapp_api_endpoints", "webapp_database_connection"]
                found_dependency_questions = []
                
                for prompt in prompts:
                    if prompt.get("id") in dependency_question_ids:
                        found_dependency_questions.append(prompt.get("id"))
                
                if len(found_dependency_questions) != 2:
                    self.log_test("Compare to Previous Version", False, 
                                f"Expected 2 dependency questions, found {len(found_dependency_questions)}: {found_dependency_questions}")
                    return False
                
                missing_deps = [dep_id for dep_id in dependency_question_ids if dep_id not in found_dependency_questions]
                if missing_deps:
                    self.log_test("Compare to Previous Version", False, 
                                f"Missing dependency questions: {missing_deps}")
                    return False
                
                self.log_test("Compare to Previous Version", True, 
                            f"Successfully upgraded from {previous_count} to {expected_new_count} questions, with 2 new dependency questions added")
                return True
            else:
                self.log_test("Compare to Previous Version", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Compare to Previous Version", False, f"Error: {str(e)}")
            return False

    def test_conditional_questionnaire_system_enabled(self):
        """Test that the conditional questionnaire system is properly enabled with dependency mappings"""
        try:
            response = self.session.get(f"{self.base_url}/questionnaires/WebApp?level=basic")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for dependencies field
                dependencies = data.get("dependencies", {})
                if not dependencies:
                    self.log_test("Conditional Questionnaire System", False, 
                                "Missing dependencies field - conditional questionnaire system not enabled")
                    return False
                
                # Verify the conditional mappings enable the system
                # Note: The actual implementation uses webapp_api_enabled instead of webapp_api_endpoints
                expected_mappings = {
                    "webapp_api_enabled": "API",
                    "webapp_database_connection": "Database"
                }
                
                for dep_id, expected_target in expected_mappings.items():
                    if dep_id not in dependencies:
                        self.log_test("Conditional Questionnaire System", False, 
                                    f"Missing conditional mapping for {dep_id}")
                        return False
                    
                    if dependencies[dep_id] != expected_target:
                        self.log_test("Conditional Questionnaire System", False, 
                                    f"Incorrect conditional mapping for {dep_id}: expected '{expected_target}', got '{dependencies[dep_id]}'")
                        return False
                
                # Verify the dependency questions exist and can trigger child questionnaires
                prompts = data.get("prompts", [])
                dependency_questions = []
                
                for prompt in prompts:
                    if prompt.get("id") in expected_mappings.keys():
                        dependency_questions.append(prompt)
                
                if len(dependency_questions) != 2:
                    self.log_test("Conditional Questionnaire System", False, 
                                f"Expected 2 dependency questions for conditional triggering, found {len(dependency_questions)}")
                    return False
                
                # Verify both dependency questions are boolean type (required for conditional logic)
                for dep_q in dependency_questions:
                    if dep_q.get("type") != "boolean":
                        self.log_test("Conditional Questionnaire System", False, 
                                    f"Dependency question {dep_q.get('id')} must be boolean type for conditional logic, got '{dep_q.get('type')}'")
                        return False
                
                self.log_test("Conditional Questionnaire System", True, 
                            "Conditional questionnaire system properly enabled with correct dependency mappings and boolean trigger questions")
                return True
            else:
                self.log_test("Conditional Questionnaire System", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Conditional Questionnaire System", False, f"Error: {str(e)}")
            return False

    # ============================================================================
    # Test Runner
    # ============================================================================
    
    def run_all_tests(self):
        """Run all WebApp dependency questions verification tests"""
        print("🚀 Starting WebApp Questionnaire Dependency Questions Verification Tests")
        print("=" * 80)
        print("CRITICAL TESTING TASK: VERIFY DEPENDENCY QUESTIONS IN WEBAPP QUESTIONNAIRE")
        print("Testing that WebApp questionnaire now includes 'Do you use API?' and 'Do you use Database?' dependency questions")
        print("=" * 80)
        
        tests = [
            # Basic connectivity
            self.test_health_check,
            
            # CRITICAL: WebApp Dependency Questions Verification
            self.test_webapp_questionnaire_content,
            self.test_dependency_questions_validation,
            self.test_compare_to_previous_version,
            self.test_conditional_questionnaire_system_enabled,
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
        print("🎯 WEBAPP DEPENDENCY QUESTIONS VERIFICATION TEST SUMMARY")
        print("=" * 80)
        print(f"✅ PASSED: {passed}")
        print(f"❌ FAILED: {failed}")
        print(f"📊 SUCCESS RATE: {(passed / (passed + failed) * 100):.1f}%")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED! WebApp questionnaire dependency questions have been successfully added and are working correctly.")
            print("✅ WebApp questionnaire now includes both 'Do you use API?' and 'Do you use Database?' dependency questions")
            print("✅ Conditional questionnaire system is properly enabled")
            print("✅ Question count increased from 8 to 10 as expected")
        else:
            print(f"\n⚠️  {failed} tests failed. Please review the failed tests above.")
            print("The WebApp questionnaire dependency questions may not be properly implemented.")
        
        return passed, failed

def main():
    """Main test execution"""
    tester = WebAppDependencyQuestionsTester()
    passed, failed = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()