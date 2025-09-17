#!/usr/bin/env python3
"""
Questionnaire Navigation Fix Validation Tests
Tests specific questionnaire-related backend APIs to ensure navigation fixes didn't break backend functionality
"""

import requests
import json
import sys

# Use the production URL from frontend/.env
BASE_URL = "https://layout-builder-1.preview.emergentagent.com/api"

class QuestionnaireAPITester:
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
                if "message" in data and "Security Modeling Platform API" in data["message"]:
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
    
    def test_intelligent_nodes_supported_types(self):
        """Test GET /api/intelligent-nodes/supported-types"""
        try:
            response = self.session.get(f"{self.base_url}/intelligent-nodes/supported-types")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for required fields
                expected_fields = ["supported_types", "total_count"]
                missing_fields = [f for f in expected_fields if f not in data]
                
                if missing_fields:
                    self.log_test("Intelligent Nodes - Supported Types", False, f"Missing fields: {missing_fields}")
                    return False
                
                supported_types = data.get("supported_types", [])
                total_count = data.get("total_count", 0)
                
                # Verify expected node types are supported
                expected_types = ["WebApp", "Database", "API", "ExternalAttacker"]
                found_types = [t.get("node_subtype") for t in supported_types]
                
                missing_types = [t for t in expected_types if t not in found_types]
                if missing_types:
                    self.log_test("Intelligent Nodes - Supported Types", False, 
                                f"Missing expected types: {missing_types}. Found: {found_types}")
                    return False
                
                # Verify structure of type info
                if supported_types:
                    first_type = supported_types[0]
                    required_type_fields = ["node_subtype", "node_type", "required_branches_count", "security_prompts_count"]
                    missing_type_fields = [f for f in required_type_fields if f not in first_type]
                    
                    if missing_type_fields:
                        self.log_test("Intelligent Nodes - Supported Types", False, 
                                    f"Missing type info fields: {missing_type_fields}")
                        return False
                
                self.log_test("Intelligent Nodes - Supported Types", True, 
                            f"Retrieved {total_count} supported types: {found_types}")
                return True
            else:
                self.log_test("Intelligent Nodes - Supported Types", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Intelligent Nodes - Supported Types", False, f"Error: {str(e)}")
            return False

    def test_webapp_prompts(self):
        """Test GET /api/intelligent-nodes/WebApp/prompts"""
        try:
            response = self.session.get(f"{self.base_url}/intelligent-nodes/WebApp/prompts")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for required fields
                expected_fields = ["node_subtype", "prompts"]
                missing_fields = [f for f in expected_fields if f not in data]
                
                if missing_fields:
                    self.log_test("WebApp Prompts", False, f"Missing fields: {missing_fields}")
                    return False
                
                prompts = data.get("prompts", [])
                node_subtype = data.get("node_subtype")
                
                if node_subtype != "WebApp":
                    self.log_test("WebApp Prompts", False, f"Expected node_subtype 'WebApp', got '{node_subtype}'")
                    return False
                
                if not prompts:
                    self.log_test("WebApp Prompts", False, "No security prompts returned")
                    return False
                
                # Verify prompt structure with validation rules
                first_prompt = prompts[0]
                required_prompt_fields = ["id", "question", "type", "options", "related_branch", "validation_rules"]
                missing_prompt_fields = [f for f in required_prompt_fields if f not in first_prompt]
                
                if missing_prompt_fields:
                    self.log_test("WebApp Prompts", False, 
                                f"Missing prompt fields: {missing_prompt_fields}")
                    return False
                
                # Verify prompt types are valid
                valid_types = ["single_choice", "multiple_choice", "text", "boolean", "number"]
                prompt_types = [p.get("type") for p in prompts]
                invalid_types = [t for t in prompt_types if t not in valid_types]
                
                if invalid_types:
                    self.log_test("WebApp Prompts", False, 
                                f"Invalid prompt types: {invalid_types}")
                    return False
                
                self.log_test("WebApp Prompts", True, 
                            f"Retrieved {len(prompts)} security prompts with validation")
                return True
                
            elif response.status_code == 404:
                self.log_test("WebApp Prompts", False, "Prompts not found for WebApp")
                return False
            else:
                self.log_test("WebApp Prompts", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("WebApp Prompts", False, f"Error: {str(e)}")
            return False

    def test_webapp_check_dependencies(self):
        """Test POST /api/intelligent-nodes/WebApp/check-dependencies with sample answers"""
        # Test different scenarios for WebApp dependencies
        test_scenarios = [
            {
                "name": "API endpoints only",
                "answers": {
                    "api_endpoints": True,
                    "database_connection": False,
                    "external_services": False,
                    "file_uploads": False,
                    "user_authentication": True
                },
                "expected_dependencies": ["API"]
            },
            {
                "name": "Database connection only", 
                "answers": {
                    "api_endpoints": False,
                    "database_connection": True,
                    "external_services": False,
                    "file_uploads": False,
                    "user_authentication": True
                },
                "expected_dependencies": ["Database"]
            },
            {
                "name": "Both API and Database",
                "answers": {
                    "api_endpoints": True,
                    "database_connection": True,
                    "external_services": False,
                    "file_uploads": False,
                    "user_authentication": True
                },
                "expected_dependencies": ["API", "Database"]
            },
            {
                "name": "No dependencies",
                "answers": {
                    "api_endpoints": False,
                    "database_connection": False,
                    "external_services": False,
                    "file_uploads": False,
                    "user_authentication": False
                },
                "expected_dependencies": []
            }
        ]
        
        for scenario in test_scenarios:
            try:
                response = self.session.post(
                    f"{self.base_url}/intelligent-nodes/WebApp/check-dependencies",
                    json=scenario["answers"],
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    dependencies = response.json()
                    
                    # Verify response is a list
                    if not isinstance(dependencies, list):
                        self.log_test(f"WebApp Dependencies - {scenario['name']}", False, 
                                    f"Expected list, got {type(dependencies)}")
                        return False
                    
                    # Check if dependencies match expected
                    expected = set(scenario["expected_dependencies"])
                    actual = set(dependencies)
                    
                    if expected == actual:
                        self.log_test(f"WebApp Dependencies - {scenario['name']}", True, 
                                    f"Correct dependencies: {dependencies}")
                    else:
                        self.log_test(f"WebApp Dependencies - {scenario['name']}", False, 
                                    f"Expected {list(expected)}, got {dependencies}")
                        return False
                        
                else:
                    self.log_test(f"WebApp Dependencies - {scenario['name']}", False, 
                                f"HTTP {response.status_code}: {response.text}")
                    return False
                    
            except Exception as e:
                self.log_test(f"WebApp Dependencies - {scenario['name']}", False, f"Error: {str(e)}")
                return False
        
        return True

    def run_all_tests(self):
        """Run all questionnaire-related tests"""
        print("🧪 Starting Questionnaire Navigation Fix Validation Tests")
        print("=" * 60)
        
        tests = [
            self.test_health_check,
            self.test_intelligent_nodes_supported_types,
            self.test_webapp_prompts,
            self.test_webapp_check_dependencies
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
        
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("✅ All questionnaire-related backend APIs are working correctly!")
            print("🎯 Navigation fixes did not break backend functionality")
        else:
            failed = total - passed
            print(f"❌ {failed} test(s) failed - backend functionality may be impacted")
        
        return passed == total

if __name__ == "__main__":
    tester = QuestionnaireAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)