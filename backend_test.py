#!/usr/bin/env python3
"""
Conditional Questionnaire and Enhanced Vulnerability Detection System Tests
Tests the enhanced conditional questionnaire system and vulnerability detection with specific scenarios
as requested in the review request.
"""

import requests
import json
import uuid
from datetime import datetime, timezone
import sys

# Use the backend URL from frontend/.env with /api suffix
BASE_URL = "https://api-threat-detect.preview.emergentagent.com/api"

class ConditionalQuestionnaireVulnerabilityTester:
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
    # PRIORITY 1: Conditional Questionnaire System Testing
    # ============================================================================
    
    def test_conditional_questionnaire_api_endpoint(self):
        """Test GET /api/questionnaires/API/conditional - should return API questionnaire with api_type question first"""
        try:
            response = self.session.get(f"{self.base_url}/questionnaires/API/conditional")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                expected_fields = ["success", "questions", "conditional_info"]
                missing_fields = [f for f in expected_fields if f not in data]
                
                if missing_fields:
                    self.log_test("Conditional API Questionnaire", False, f"Missing response fields: {missing_fields}")
                    return False
                
                questions = data.get("questions", [])
                
                # Should have questions and first question should be api_type
                if len(questions) == 0:
                    self.log_test("Conditional API Questionnaire", False, "No questions returned")
                    return False
                
                first_question = questions[0]
                if first_question.get("question_id") != "api_type":
                    self.log_test("Conditional API Questionnaire", False, 
                                f"First question should be 'api_type', got '{first_question.get('question_id')}'")
                    return False
                
                # Verify api_type question has REST API and GraphQL options
                options = first_question.get("options", [])
                has_rest = any("REST API" in str(option) for option in options)
                has_graphql = any("GraphQL" in str(option) for option in options)
                
                if not (has_rest and has_graphql):
                    self.log_test("Conditional API Questionnaire", False, 
                                f"api_type question missing REST API or GraphQL options: {options}")
                    return False
                
                self.log_test("Conditional API Questionnaire", True, 
                            f"API conditional questionnaire with {len(questions)} questions, api_type question first")
                return True
            else:
                self.log_test("Conditional API Questionnaire", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Conditional API Questionnaire", False, f"Error: {str(e)}")
            return False

    def test_conditional_trigger_rest_api(self):
        """Test POST /api/questionnaires/API/conditional-trigger with REST API response"""
        try:
            request_data = {
                "question_id": "api_type",
                "response": "REST API"
            }
            
            response = self.session.post(
                f"{self.base_url}/questionnaires/API/conditional-trigger",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                expected_fields = ["success", "conditional_questions", "trigger_question"]
                missing_fields = [f for f in expected_fields if f not in data]
                
                if missing_fields:
                    self.log_test("Conditional Trigger REST API", False, f"Missing response fields: {missing_fields}")
                    return False
                
                triggered_questions = data.get("conditional_questions", [])
                
                # Should return REST-specific questions
                if len(triggered_questions) == 0:
                    self.log_test("Conditional Trigger REST API", False, "No REST-specific questions triggered")
                    return False
                
                # Check for REST-specific question content
                rest_keywords = ["endpoint", "http", "rest", "resource", "method"]
                rest_questions = []
                for question in triggered_questions:
                    question_text = question.get("question", "").lower()
                    if any(keyword in question_text for keyword in rest_keywords):
                        rest_questions.append(question)
                
                if len(rest_questions) == 0:
                    self.log_test("Conditional Trigger REST API", False, 
                                f"No REST-specific questions found in triggered questions")
                    return False
                
                self.log_test("Conditional Trigger REST API", True, 
                            f"Triggered {len(triggered_questions)} questions, {len(rest_questions)} REST-specific")
                return True
            else:
                self.log_test("Conditional Trigger REST API", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Conditional Trigger REST API", False, f"Error: {str(e)}")
            return False

    def test_conditional_trigger_graphql_api(self):
        """Test POST /api/questionnaires/API/conditional-trigger with GraphQL API response"""
        try:
            request_data = {
                "question_id": "api_type",
                "response": "GraphQL API"
            }
            
            response = self.session.post(
                f"{self.base_url}/questionnaires/API/conditional-trigger",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                expected_fields = ["success", "conditional_questions", "trigger_question"]
                missing_fields = [f for f in expected_fields if f not in data]
                
                if missing_fields:
                    self.log_test("Conditional Trigger GraphQL API", False, f"Missing response fields: {missing_fields}")
                    return False
                
                triggered_questions = data.get("conditional_questions", [])
                
                # Should return GraphQL-specific questions
                if len(triggered_questions) == 0:
                    self.log_test("Conditional Trigger GraphQL API", False, "No GraphQL-specific questions triggered")
                    return False
                
                # Check for GraphQL-specific question content
                graphql_keywords = ["graphql", "query", "mutation", "schema", "resolver"]
                graphql_questions = []
                for question in triggered_questions:
                    question_text = question.get("question", "").lower()
                    if any(keyword in question_text for keyword in graphql_keywords):
                        graphql_questions.append(question)
                
                if len(graphql_questions) == 0:
                    self.log_test("Conditional Trigger GraphQL API", False, 
                                f"No GraphQL-specific questions found in triggered questions")
                    return False
                
                self.log_test("Conditional Trigger GraphQL API", True, 
                            f"Triggered {len(triggered_questions)} questions, {len(graphql_questions)} GraphQL-specific")
                return True
            else:
                self.log_test("Conditional Trigger GraphQL API", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Conditional Trigger GraphQL API", False, f"Error: {str(e)}")
            return False

    def test_conditional_questionnaire_database_endpoint(self):
        """Test GET /api/questionnaires/Database/conditional - should return Database questionnaire with database_type question first"""
        try:
            response = self.session.get(f"{self.base_url}/questionnaires/Database/conditional")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                expected_fields = ["success", "questions", "conditional_info"]
                missing_fields = [f for f in expected_fields if f not in data]
                
                if missing_fields:
                    self.log_test("Conditional Database Questionnaire", False, f"Missing response fields: {missing_fields}")
                    return False
                
                questions = data.get("questions", [])
                
                # Should have questions and first question should be database_type
                if len(questions) == 0:
                    self.log_test("Conditional Database Questionnaire", False, "No questions returned")
                    return False
                
                first_question = questions[0]
                if first_question.get("question_id") != "database_type":
                    self.log_test("Conditional Database Questionnaire", False, 
                                f"First question should be 'database_type', got '{first_question.get('question_id')}'")
                    return False
                
                # Verify database_type question has MongoDB option
                options = first_question.get("options", [])
                has_mongodb = any("MongoDB" in str(option) for option in options)
                
                if not has_mongodb:
                    self.log_test("Conditional Database Questionnaire", False, 
                                f"database_type question missing MongoDB option: {options}")
                    return False
                
                self.log_test("Conditional Database Questionnaire", True, 
                            f"Database conditional questionnaire with {len(questions)} questions, database_type question first")
                return True
            else:
                self.log_test("Conditional Database Questionnaire", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Conditional Database Questionnaire", False, f"Error: {str(e)}")
            return False

    def test_conditional_trigger_mongodb(self):
        """Test POST /api/questionnaires/Database/conditional-trigger with MongoDB response"""
        try:
            request_data = {
                "question_id": "database_type",
                "response": "MongoDB"
            }
            
            response = self.session.post(
                f"{self.base_url}/questionnaires/Database/conditional-trigger",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                expected_fields = ["success", "conditional_questions", "trigger_question"]
                missing_fields = [f for f in expected_fields if f not in data]
                
                if missing_fields:
                    self.log_test("Conditional Trigger MongoDB", False, f"Missing response fields: {missing_fields}")
                    return False
                
                triggered_questions = data.get("conditional_questions", [])
                
                # Should return MongoDB-specific questions
                if len(triggered_questions) == 0:
                    self.log_test("Conditional Trigger MongoDB", False, "No MongoDB-specific questions triggered")
                    return False
                
                # Check for MongoDB-specific question content
                mongodb_keywords = ["mongodb", "nosql", "document", "collection", "aggregation"]
                mongodb_questions = []
                for question in triggered_questions:
                    question_text = question.get("question", "").lower()
                    if any(keyword in question_text for keyword in mongodb_keywords):
                        mongodb_questions.append(question)
                
                if len(mongodb_questions) == 0:
                    self.log_test("Conditional Trigger MongoDB", False, 
                                f"No MongoDB-specific questions found in triggered questions")
                    return False
                
                self.log_test("Conditional Trigger MongoDB", True, 
                            f"Triggered {len(triggered_questions)} questions, {len(mongodb_questions)} MongoDB-specific")
                return True
            else:
                self.log_test("Conditional Trigger MongoDB", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Conditional Trigger MongoDB", False, f"Error: {str(e)}")
            return False

    # ============================================================================
    # PRIORITY 2: Enhanced Vulnerability Detection Testing
    # ============================================================================
    
    def test_input_validation_vulnerability(self):
        """Test POST /api/vulnerabilities/analyze/test_node/enhanced with input validation vulnerability"""
        try:
            request_data = {
                "node_id": "test_node_api",
                "node_type": "API",
                "questionnaire_responses": {
                    "api_input_validation": "No validation",
                    "api_type": "REST API"
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/vulnerabilities/analyze/test_node/enhanced",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                expected_fields = ["vulnerabilities", "trigger_context", "missing_controls", "user_selections"]
                missing_fields = [f for f in expected_fields if f not in data]
                
                if missing_fields:
                    self.log_test("Input Validation Vulnerability", False, f"Missing response fields: {missing_fields}")
                    return False
                
                vulnerabilities = data.get("vulnerabilities", [])
                
                # Should detect SQL Injection vulnerability with Critical severity
                if len(vulnerabilities) == 0:
                    self.log_test("Input Validation Vulnerability", False, "No vulnerabilities detected for no input validation")
                    return False
                
                # Look for SQL Injection vulnerability with Critical severity
                sql_injection_vuln = None
                for vuln in vulnerabilities:
                    if "SQL Injection" in vuln.get("name", "") or "injection" in vuln.get("name", "").lower():
                        if vuln.get("severity") == "Critical":
                            sql_injection_vuln = vuln
                            break
                
                if not sql_injection_vuln:
                    self.log_test("Input Validation Vulnerability", False, 
                                f"SQL Injection vulnerability with Critical severity not found. Found: {[v.get('name') + ' (' + v.get('severity', 'Unknown') + ')' for v in vulnerabilities]}")
                    return False
                
                # Verify educational context is included
                trigger_context = data.get("trigger_context", {})
                missing_controls = data.get("missing_controls", [])
                user_selections = data.get("user_selections", {})
                
                if not trigger_context or not missing_controls:
                    self.log_test("Input Validation Vulnerability", False, 
                                "Missing educational context (trigger_context or missing_controls)")
                    return False
                
                self.log_test("Input Validation Vulnerability", True, 
                            f"Detected SQL Injection vulnerability with Critical severity and educational context")
                return True
            else:
                self.log_test("Input Validation Vulnerability", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Input Validation Vulnerability", False, f"Error: {str(e)}")
            return False

    def test_cors_misconfiguration_vulnerability(self):
        """Test CORS misconfiguration vulnerability detection"""
        try:
            request_data = {
                "node_id": "test_node_cors",
                "node_type": "API",
                "questionnaire_responses": {
                    "api_cors_configuration": "Permissive CORS"
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/vulnerabilities/analyze/test_node/enhanced",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                vulnerabilities = data.get("vulnerabilities", [])
                
                # Should detect CORS Misconfiguration with Medium severity
                if len(vulnerabilities) == 0:
                    self.log_test("CORS Misconfiguration Vulnerability", False, "No vulnerabilities detected for permissive CORS")
                    return False
                
                # Look for CORS Misconfiguration vulnerability with Medium severity
                cors_vuln = None
                for vuln in vulnerabilities:
                    if "CORS" in vuln.get("name", "") or "cors" in vuln.get("name", "").lower():
                        if vuln.get("severity") == "Medium":
                            cors_vuln = vuln
                            break
                
                if not cors_vuln:
                    self.log_test("CORS Misconfiguration Vulnerability", False, 
                                f"CORS Misconfiguration vulnerability with Medium severity not found. Found: {[v.get('name') + ' (' + v.get('severity', 'Unknown') + ')' for v in vulnerabilities]}")
                    return False
                
                self.log_test("CORS Misconfiguration Vulnerability", True, 
                            f"Detected CORS Misconfiguration vulnerability with Medium severity")
                return True
            else:
                self.log_test("CORS Misconfiguration Vulnerability", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("CORS Misconfiguration Vulnerability", False, f"Error: {str(e)}")
            return False

    def test_critical_data_exposure_vulnerability(self):
        """Test combined critical data exposure vulnerability detection"""
        try:
            request_data = {
                "node_id": "test_node_database",
                "node_type": "Database",
                "questionnaire_responses": {
                    "data_classification": "Confidential",
                    "encryption_at_rest": "No encryption",
                    "encryption_in_transit": "Unencrypted connections",
                    "access_control": "No access control"
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/vulnerabilities/analyze/test_node/enhanced",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                vulnerabilities = data.get("vulnerabilities", [])
                
                # Should detect Critical Data Exposure with Critical severity
                if len(vulnerabilities) == 0:
                    self.log_test("Critical Data Exposure Vulnerability", False, "No vulnerabilities detected for critical data exposure scenario")
                    return False
                
                # Look for Critical Data Exposure vulnerability with Critical severity
                data_exposure_vuln = None
                for vuln in vulnerabilities:
                    vuln_name = vuln.get("name", "").lower()
                    if ("data exposure" in vuln_name or "data breach" in vuln_name or "confidential" in vuln_name):
                        if vuln.get("severity") == "Critical":
                            data_exposure_vuln = vuln
                            break
                
                if not data_exposure_vuln:
                    self.log_test("Critical Data Exposure Vulnerability", False, 
                                f"Critical Data Exposure vulnerability with Critical severity not found. Found: {[v.get('name') + ' (' + v.get('severity', 'Unknown') + ')' for v in vulnerabilities]}")
                    return False
                
                self.log_test("Critical Data Exposure Vulnerability", True, 
                            f"Detected Critical Data Exposure vulnerability with Critical severity")
                return True
            else:
                self.log_test("Critical Data Exposure Vulnerability", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Critical Data Exposure Vulnerability", False, f"Error: {str(e)}")
            return False

    def test_waf_ddos_vulnerability(self):
        """Test WAF-related DDoS vulnerability detection"""
        try:
            request_data = {
                "node_type": "WebApp",
                "questionnaire_responses": {
                    "waf_deployment": "No WAF",
                    "rate_limiting": "No rate limiting"
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/vulnerabilities/analyze/test_node/enhanced",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                vulnerabilities = data.get("vulnerabilities", [])
                
                # Should detect DDoS vulnerability with Medium severity
                if len(vulnerabilities) == 0:
                    self.log_test("WAF DDoS Vulnerability", False, "No vulnerabilities detected for no WAF/rate limiting")
                    return False
                
                # Look for DDoS vulnerability with Medium severity
                ddos_vuln = None
                for vuln in vulnerabilities:
                    vuln_name = vuln.get("name", "").lower()
                    if ("ddos" in vuln_name or "denial of service" in vuln_name or "rate limit" in vuln_name):
                        if vuln.get("severity") == "Medium":
                            ddos_vuln = vuln
                            break
                
                if not ddos_vuln:
                    self.log_test("WAF DDoS Vulnerability", False, 
                                f"DDoS vulnerability with Medium severity not found. Found: {[v.get('name') + ' (' + v.get('severity', 'Unknown') + ')' for v in vulnerabilities]}")
                    return False
                
                self.log_test("WAF DDoS Vulnerability", True, 
                            f"Detected DDoS vulnerability with Medium severity")
                return True
            else:
                self.log_test("WAF DDoS Vulnerability", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("WAF DDoS Vulnerability", False, f"Error: {str(e)}")
            return False

    # ============================================================================
    # PRIORITY 3: Conditional Database Type Vulnerabilities Testing
    # ============================================================================
    
    def test_mongodb_nosql_injection(self):
        """Test MongoDB NoSQL injection vulnerability detection"""
        try:
            request_data = {
                "node_type": "Database",
                "questionnaire_responses": {
                    "database_type": "MongoDB",
                    "database_input_validation": "No validation",
                    "mongodb_authorization": "No authorization"
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/vulnerabilities/analyze/test_node/enhanced",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                vulnerabilities = data.get("vulnerabilities", [])
                
                # Should detect NoSQL Injection vulnerability with High severity
                if len(vulnerabilities) == 0:
                    self.log_test("MongoDB NoSQL Injection", False, "No vulnerabilities detected for MongoDB with no validation/authorization")
                    return False
                
                # Look for NoSQL Injection vulnerability with High severity
                nosql_injection_vuln = None
                for vuln in vulnerabilities:
                    vuln_name = vuln.get("name", "").lower()
                    if ("nosql injection" in vuln_name or "mongodb injection" in vuln_name or "injection" in vuln_name):
                        if vuln.get("severity") == "High":
                            nosql_injection_vuln = vuln
                            break
                
                if not nosql_injection_vuln:
                    self.log_test("MongoDB NoSQL Injection", False, 
                                f"NoSQL Injection vulnerability with High severity not found. Found: {[v.get('name') + ' (' + v.get('severity', 'Unknown') + ')' for v in vulnerabilities]}")
                    return False
                
                self.log_test("MongoDB NoSQL Injection", True, 
                            f"Detected NoSQL Injection vulnerability with High severity")
                return True
            else:
                self.log_test("MongoDB NoSQL Injection", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("MongoDB NoSQL Injection", False, f"Error: {str(e)}")
            return False

    # ============================================================================
    # Test Runner
    # ============================================================================
    
    def run_all_tests(self):
        """Run all conditional questionnaire and enhanced vulnerability detection tests"""
        print("🚀 Starting Conditional Questionnaire and Enhanced Vulnerability Detection Tests")
        print("=" * 80)
        
        tests = [
            # Basic connectivity
            self.test_health_check,
            
            # PRIORITY 1: Conditional Questionnaire System
            self.test_conditional_questionnaire_api_endpoint,
            self.test_conditional_trigger_rest_api,
            self.test_conditional_trigger_graphql_api,
            self.test_conditional_questionnaire_database_endpoint,
            self.test_conditional_trigger_mongodb,
            
            # PRIORITY 2: Enhanced Vulnerability Detection
            self.test_input_validation_vulnerability,
            self.test_cors_misconfiguration_vulnerability,
            self.test_critical_data_exposure_vulnerability,
            self.test_waf_ddos_vulnerability,
            
            # PRIORITY 3: Conditional Database Type Vulnerabilities
            self.test_mongodb_nosql_injection
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
        print("🎯 CONDITIONAL QUESTIONNAIRE & ENHANCED VULNERABILITY DETECTION TEST SUMMARY")
        print("=" * 80)
        print(f"✅ PASSED: {passed}")
        print(f"❌ FAILED: {failed}")
        print(f"📊 SUCCESS RATE: {(passed / (passed + failed) * 100):.1f}%")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED! Conditional questionnaire and enhanced vulnerability detection systems are working correctly.")
        else:
            print(f"\n⚠️  {failed} tests failed. Please review the failed tests above.")
        
        return passed, failed

def main():
    """Main test execution"""
    tester = ConditionalQuestionnaireVulnerabilityTester()
    passed, failed = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()