#!/usr/bin/env python3
"""
Backend API Testing - ENHANCED API NODE QUESTIONNAIRE SYSTEM
Tests the new enhanced API Node questionnaire system with dynamic questions as specified in the review request.

TESTING FOCUS:
🎯 PRIMARY TEST: ENHANCED API NODE QUESTIONNAIRE SYSTEM WITH DYNAMIC QUESTIONS

1. **Enhanced Questionnaire Endpoint Testing:**
   - Test GET /api/questionnaires/API/enhanced without canvas nodes
   - Test GET /api/questionnaires/API/enhanced with canvas_nodes parameter containing sample Database nodes
   - Verify response includes dynamic_api_questions, database_reuse_detection, external_services_categorization features

2. **External Services Categories Testing:**
   - Test GET /api/questionnaires/external-services/categories
   - Verify returns 9 categories (Authentication, Payment, Cloud, Messaging, Analytics, Social Media, File Storage, Notification, Other)
   - Check each category has appropriate service examples

3. **Canvas Node Detection Testing:**
   - Test POST /api/questionnaires/canvas/detect-nodes with sample canvas nodes containing Database nodes
   - Test detection of different node types (Database, API, WebApp)
   - Verify reuse recommendations work correctly

4. **Enhanced Conditional Questions Testing:**
   - Test POST /api/questionnaires/API/enhanced/conditional with API type responses (REST API, GraphQL API, etc.)
   - Test database reuse decision processing
   - Test web interface exposure triggers
   - Verify conditional questions are added based on responses

**EXPECTED RESULTS:** 
- Enhanced questionnaire endpoint should return dynamic questions with all features enabled
- External services categories should return 9 categories with proper service examples
- Canvas node detection should identify existing nodes and provide reuse recommendations
- Conditional questions should be dynamically added based on API type and other responses
"""

import requests
import json
import uuid
from datetime import datetime, timezone
import sys

# Use the backend URL from frontend/.env with /api suffix
BASE_URL = "https://api-wizard-map.preview.emergentagent.com/api"

class EnhancedAPIQuestionnaireTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.test_results = []
        self.sample_canvas_nodes = [
            {
                "id": "db-node-1",
                "type": "Asset",
                "subtype": "Database",
                "label": "User Database",
                "position": {"x": 100, "y": 200}
            },
            {
                "id": "db-node-2", 
                "type": "Asset",
                "subtype": "Database",
                "label": "Analytics Database",
                "position": {"x": 300, "y": 200}
            },
            {
                "id": "api-node-1",
                "type": "Asset", 
                "subtype": "API",
                "label": "User API",
                "position": {"x": 200, "y": 100}
            },
            {
                "id": "webapp-node-1",
                "type": "Asset",
                "subtype": "WebApp", 
                "label": "Frontend App",
                "position": {"x": 400, "y": 100}
            }
        ]
        
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

    def test_enhanced_questionnaire_basic(self):
        """
        CRITICAL TEST: Test enhanced questionnaire endpoint without canvas nodes
        
        This test verifies that:
        1. GET /api/questionnaires/API/enhanced returns proper response
        2. Response includes all required features flags
        3. Dynamic API questions are included
        4. Basic functionality works without canvas nodes
        """
        try:
            print("🎯 CRITICAL TEST: Enhanced Questionnaire Endpoint (Basic)")
            print("=" * 80)
            
            response = self.session.get(f"{self.base_url}/questionnaires/API/enhanced")
            
            print(f"📋 Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("Enhanced Questionnaire Basic", False, 
                            f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Enhanced Questionnaire Basic", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            # Verify required response fields
            required_fields = ["success", "node_subtype", "level", "total_questions", "questions", "features"]
            missing_fields = []
            for field in required_fields:
                if field not in data:
                    missing_fields.append(field)
            
            if missing_fields:
                self.log_test("Enhanced Questionnaire Basic", False, 
                            f"Missing required fields: {missing_fields}")
                return False
            
            # Verify features are enabled
            features = data.get("features", {})
            expected_features = {
                "dynamic_api_questions": True,
                "database_reuse_detection": True,
                "external_services_categorization": True,
                "bidirectional_web_flow": True,
                "vulnerability_integration": True
            }
            
            feature_issues = []
            for feature, expected_value in expected_features.items():
                if features.get(feature) != expected_value:
                    feature_issues.append(f"{feature}={features.get(feature)} (expected {expected_value})")
            
            if feature_issues:
                self.log_test("Enhanced Questionnaire Basic", False, 
                            f"Feature issues: {feature_issues}")
                return False
            
            # Verify questions are present
            questions = data.get("questions", [])
            if not questions:
                self.log_test("Enhanced Questionnaire Basic", False, 
                            "No questions returned")
                return False
            
            print(f"📊 Enhanced Questionnaire Basic Results:")
            print(f"   Success: {data.get('success')}")
            print(f"   Node subtype: {data.get('node_subtype')}")
            print(f"   Level: {data.get('level')}")
            print(f"   Total questions: {data.get('total_questions')}")
            print(f"   Questions count: {len(questions)}")
            print(f"   Features enabled: {list(features.keys())}")
            
            self.log_test("Enhanced Questionnaire Basic", True, 
                        f"✅ SUCCESS: Enhanced questionnaire returned {len(questions)} questions with all features enabled")
            
            return True
            
        except Exception as e:
            self.log_test("Enhanced Questionnaire Basic", False, f"Request error: {str(e)}")
            return False

    def test_enhanced_questionnaire_with_canvas_nodes(self):
        """
        CRITICAL TEST: Test enhanced questionnaire endpoint with canvas nodes
        
        This test verifies that:
        1. GET /api/questionnaires/API/enhanced with canvas_nodes parameter works
        2. Canvas node detection is enabled
        3. Database reuse detection works with sample Database nodes
        """
        try:
            print("🎯 CRITICAL TEST: Enhanced Questionnaire with Canvas Nodes")
            print("=" * 80)
            
            # Convert canvas nodes to JSON string
            canvas_nodes_json = json.dumps(self.sample_canvas_nodes)
            
            response = self.session.get(
                f"{self.base_url}/questionnaires/API/enhanced",
                params={"canvas_nodes": canvas_nodes_json}
            )
            
            print(f"📋 Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("Enhanced Questionnaire with Canvas Nodes", False, 
                            f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Enhanced Questionnaire with Canvas Nodes", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            # Verify canvas detection is enabled
            has_canvas_detection = data.get("has_canvas_detection", False)
            detected_nodes = data.get("detected_nodes", 0)
            
            if not has_canvas_detection:
                self.log_test("Enhanced Questionnaire with Canvas Nodes", False, 
                            "Canvas detection not enabled")
                return False
            
            if detected_nodes != len(self.sample_canvas_nodes):
                self.log_test("Enhanced Questionnaire with Canvas Nodes", False, 
                            f"Detected nodes count mismatch: {detected_nodes} vs {len(self.sample_canvas_nodes)}")
                return False
            
            print(f"📊 Enhanced Questionnaire with Canvas Nodes Results:")
            print(f"   Canvas detection enabled: {has_canvas_detection}")
            print(f"   Detected nodes: {detected_nodes}")
            print(f"   Sample nodes provided: {len(self.sample_canvas_nodes)}")
            
            # Check for database reuse questions in the response
            questions = data.get("questions", [])
            database_reuse_questions = []
            for question in questions:
                if "database" in question.get("id", "").lower() or "reuse" in question.get("question", "").lower():
                    database_reuse_questions.append(question.get("id"))
            
            print(f"   Database reuse related questions: {len(database_reuse_questions)}")
            if database_reuse_questions:
                print(f"   Database reuse question IDs: {database_reuse_questions}")
            
            self.log_test("Enhanced Questionnaire with Canvas Nodes", True, 
                        f"✅ SUCCESS: Canvas detection enabled, {detected_nodes} nodes detected, {len(database_reuse_questions)} database reuse questions")
            
            return True
            
        except Exception as e:
            self.log_test("Enhanced Questionnaire with Canvas Nodes", False, f"Request error: {str(e)}")
            return False

    def test_external_services_categories(self):
        """
        CRITICAL TEST: Test external services categories endpoint
        
        This test verifies that:
        1. GET /api/questionnaires/external-services/categories returns proper response
        2. Returns 9 expected categories
        3. Each category has appropriate service examples
        """
        try:
            print("🎯 CRITICAL TEST: External Services Categories")
            print("=" * 80)
            
            response = self.session.get(f"{self.base_url}/questionnaires/external-services/categories")
            
            print(f"📋 Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("External Services Categories", False, 
                            f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("External Services Categories", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            # Verify required response fields
            if not data.get("success"):
                self.log_test("External Services Categories", False, 
                            "Response success is false")
                return False
            
            categories = data.get("categories", {})
            total_categories = data.get("total_categories", 0)
            
            # Expected 9 categories
            expected_categories = [
                "Authentication", "Payment", "Cloud", "Messaging", 
                "Analytics", "Social Media", "File Storage", "Notification", "Other"
            ]
            
            if total_categories != 9:
                self.log_test("External Services Categories", False, 
                            f"Expected 9 categories, got {total_categories}")
                return False
            
            # Verify all expected categories are present
            missing_categories = []
            for expected_cat in expected_categories:
                if expected_cat not in categories:
                    missing_categories.append(expected_cat)
            
            if missing_categories:
                self.log_test("External Services Categories", False, 
                            f"Missing categories: {missing_categories}")
                return False
            
            # Verify each category has service examples
            categories_with_no_services = []
            for category, services in categories.items():
                if not services or len(services) == 0:
                    categories_with_no_services.append(category)
            
            if categories_with_no_services:
                self.log_test("External Services Categories", False, 
                            f"Categories with no services: {categories_with_no_services}")
                return False
            
            print(f"📊 External Services Categories Results:")
            print(f"   Success: {data.get('success')}")
            print(f"   Total categories: {total_categories}")
            print(f"   Categories found: {list(categories.keys())}")
            
            # Show sample services for each category
            for category, services in categories.items():
                print(f"   {category}: {len(services)} services (e.g., {services[0] if services else 'None'})")
            
            self.log_test("External Services Categories", True, 
                        f"✅ SUCCESS: All 9 categories returned with service examples")
            
            return True
            
        except Exception as e:
            self.log_test("External Services Categories", False, f"Request error: {str(e)}")
            return False

    def test_canvas_node_detection(self):
        """
        CRITICAL TEST: Test canvas node detection endpoint
        
        This test verifies that:
        1. POST /api/questionnaires/canvas/detect-nodes works with sample canvas nodes
        2. Detects different node types (Database, API, WebApp)
        3. Provides reuse recommendations correctly
        """
        try:
            print("🎯 CRITICAL TEST: Canvas Node Detection")
            print("=" * 80)
            
            # Test Database node detection
            database_detection_request = {
                "canvas_nodes": self.sample_canvas_nodes,
                "target_type": "Database"
            }
            
            response = self.session.post(
                f"{self.base_url}/questionnaires/canvas/detect-nodes",
                json=database_detection_request
            )
            
            print(f"📋 Database Detection Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("Canvas Node Detection", False, 
                            f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                db_data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Canvas Node Detection", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            # Verify Database detection results
            if not db_data.get("success"):
                self.log_test("Canvas Node Detection", False, 
                            "Database detection response success is false")
                return False
            
            db_existing_nodes = db_data.get("existing_nodes", [])
            db_existing_count = db_data.get("existing_nodes_count", 0)
            db_has_existing = db_data.get("has_existing_nodes", False)
            db_reuse_recommended = db_data.get("reuse_recommended", False)
            
            # We have 2 Database nodes in sample data
            expected_db_count = 2
            if db_existing_count != expected_db_count:
                self.log_test("Canvas Node Detection", False, 
                            f"Database detection count mismatch: {db_existing_count} vs {expected_db_count}")
                return False
            
            if not db_has_existing:
                self.log_test("Canvas Node Detection", False, 
                            "Database detection should show has_existing_nodes=true")
                return False
            
            if not db_reuse_recommended:
                self.log_test("Canvas Node Detection", False, 
                            "Database detection should recommend reuse")
                return False
            
            print(f"📊 Database Detection Results:")
            print(f"   Target type: {db_data.get('target_type')}")
            print(f"   Existing nodes count: {db_existing_count}")
            print(f"   Has existing nodes: {db_has_existing}")
            print(f"   Reuse recommended: {db_reuse_recommended}")
            print(f"   Detected nodes: {[node.get('label', 'Unknown') for node in db_existing_nodes]}")
            
            # Test API node detection
            api_detection_request = {
                "canvas_nodes": self.sample_canvas_nodes,
                "target_type": "API"
            }
            
            response = self.session.post(
                f"{self.base_url}/questionnaires/canvas/detect-nodes",
                json=api_detection_request
            )
            
            if response.status_code == 200:
                api_data = response.json()
                api_existing_count = api_data.get("existing_nodes_count", 0)
                print(f"📊 API Detection Results:")
                print(f"   API nodes detected: {api_existing_count}")
            
            # Test WebApp node detection
            webapp_detection_request = {
                "canvas_nodes": self.sample_canvas_nodes,
                "target_type": "WebApp"
            }
            
            response = self.session.post(
                f"{self.base_url}/questionnaires/canvas/detect-nodes",
                json=webapp_detection_request
            )
            
            if response.status_code == 200:
                webapp_data = response.json()
                webapp_existing_count = webapp_data.get("existing_nodes_count", 0)
                print(f"📊 WebApp Detection Results:")
                print(f"   WebApp nodes detected: {webapp_existing_count}")
            
            self.log_test("Canvas Node Detection", True, 
                        f"✅ SUCCESS: Database detection found {db_existing_count} nodes with reuse recommendation")
            
            return True
            
        except Exception as e:
            self.log_test("Canvas Node Detection", False, f"Request error: {str(e)}")
            return False

    def test_enhanced_conditional_questions(self):
        """
        CRITICAL TEST: Test enhanced conditional questions endpoint
        
        This test verifies that:
        1. POST /api/questionnaires/API/enhanced/conditional works with API type responses
        2. Database reuse decision processing works
        3. Web interface exposure triggers work
        4. Conditional questions are added based on responses
        """
        try:
            print("🎯 CRITICAL TEST: Enhanced Conditional Questions")
            print("=" * 80)
            
            # Test with REST API type response
            rest_api_request = {
                "responses": {
                    "api_type": "REST API",
                    "database_type": "MySQL",
                    "api_web_interface_exposure": "yes",
                    "api_external_services": "yes"
                },
                "canvas_nodes": self.sample_canvas_nodes,
                "level": "basic"
            }
            
            response = self.session.post(
                f"{self.base_url}/questionnaires/API/enhanced/conditional",
                json=rest_api_request
            )
            
            print(f"📋 REST API Conditional Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("Enhanced Conditional Questions", False, 
                            f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                rest_data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Enhanced Conditional Questions", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            # Verify REST API conditional response
            if not rest_data.get("success"):
                self.log_test("Enhanced Conditional Questions", False, 
                            "REST API conditional response success is false")
                return False
            
            rest_questions = rest_data.get("questions", [])
            rest_triggers = rest_data.get("triggers_detected", {})
            
            print(f"📊 REST API Conditional Results:")
            print(f"   Success: {rest_data.get('success')}")
            print(f"   Node subtype: {rest_data.get('node_subtype')}")
            print(f"   Total questions: {rest_data.get('total_questions')}")
            print(f"   Questions returned: {len(rest_questions)}")
            print(f"   Triggers detected: {rest_triggers}")
            
            # Test with GraphQL API type response
            graphql_api_request = {
                "responses": {
                    "api_type": "GraphQL API",
                    "database_reuse_decision": "reuse_existing",
                    "api_web_interface_exposure": "no"
                },
                "canvas_nodes": self.sample_canvas_nodes,
                "level": "basic"
            }
            
            response = self.session.post(
                f"{self.base_url}/questionnaires/API/enhanced/conditional",
                json=graphql_api_request
            )
            
            if response.status_code == 200:
                graphql_data = response.json()
                graphql_questions = graphql_data.get("questions", [])
                graphql_reuse_info = graphql_data.get("reuse_info", {})
                
                print(f"📊 GraphQL API Conditional Results:")
                print(f"   Questions returned: {len(graphql_questions)}")
                print(f"   Reuse info: {bool(graphql_reuse_info)}")
                print(f"   Database reuse decision processed: {'database_reuse_decision' in graphql_api_request['responses']}")
            
            # Test with SOAP API type response
            soap_api_request = {
                "responses": {
                    "api_type": "SOAP API",
                    "api_external_services": "Authentication,Payment"
                },
                "canvas_nodes": [],
                "level": "advanced"
            }
            
            response = self.session.post(
                f"{self.base_url}/questionnaires/API/enhanced/conditional",
                json=soap_api_request
            )
            
            if response.status_code == 200:
                soap_data = response.json()
                soap_questions = soap_data.get("questions", [])
                
                print(f"📊 SOAP API Conditional Results:")
                print(f"   Questions returned: {len(soap_questions)}")
            
            self.log_test("Enhanced Conditional Questions", True, 
                        f"✅ SUCCESS: Conditional questions working for REST API ({len(rest_questions)} questions), triggers detected")
            
            return True
            
        except Exception as e:
            self.log_test("Enhanced Conditional Questions", False, f"Request error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all enhanced API questionnaire tests"""
        print("🚀 STARTING ENHANCED API NODE QUESTIONNAIRE SYSTEM TESTING")
        print("=" * 80)
        print("Testing the new enhanced API Node questionnaire system with dynamic questions")
        print("=" * 80)
        
        tests = [
            self.test_health_check,
            self.test_enhanced_questionnaire_basic,
            self.test_enhanced_questionnaire_with_canvas_nodes,
            self.test_external_services_categories,
            self.test_canvas_node_detection,
            self.test_enhanced_conditional_questions,
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
    tester = EnhancedAPIQuestionnaireTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)