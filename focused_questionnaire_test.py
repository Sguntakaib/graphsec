#!/usr/bin/env python3
"""
Focused Questionnaire and Vulnerability Analysis System Tests
Tests the specific requirements from the review request with corrected API calls.
"""

import requests
import json
import uuid
from datetime import datetime, timezone
import sys

# Use the backend URL from frontend/.env with /api suffix
BASE_URL = "https://app-deployment-28.preview.emergentagent.com/api"

class FocusedQuestionnaireTester:
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

    def test_comprehensive_webapp_questionnaire_basic(self):
        """Test GET /api/questionnaires/WebApp - should return 8+ questions with required security topics"""
        try:
            response = self.session.get(f"{self.base_url}/questionnaires/WebApp")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for required fields
                if "prompts" not in data:
                    self.log_test("Comprehensive WebApp Questionnaire", False, "Missing 'prompts' field in response")
                    return False
                
                prompts = data.get("prompts", [])
                
                # Should have at least 8 questions for basic level
                if len(prompts) < 8:
                    self.log_test("Comprehensive WebApp Questionnaire", False, f"Expected at least 8 questions, got {len(prompts)}")
                    return False
                
                # Check for specific security questions mentioned in review request
                required_topics = [
                    "security headers", "logging", "authentication", "input validation", 
                    "https", "session management", "error handling", "data encryption"
                ]
                
                found_topics = []
                for prompt in prompts:
                    question_text = prompt.get("question", "").lower()
                    for topic in required_topics:
                        # More flexible matching
                        topic_words = topic.split()
                        if all(word in question_text for word in topic_words) or topic.replace(" ", "") in question_text.replace(" ", ""):
                            if topic not in found_topics:
                                found_topics.append(topic)
                
                # Check for completion_required and is_comprehensive flags
                completion_required = data.get("completion_required", False)
                is_comprehensive = data.get("is_comprehensive", False)
                
                success_criteria = [
                    (len(prompts) >= 8, f"Question count: {len(prompts)}/8+"),
                    (len(found_topics) >= 6, f"Security topics: {len(found_topics)}/8 ({found_topics})"),
                    (completion_required, f"completion_required: {completion_required}"),
                    (is_comprehensive, f"is_comprehensive: {is_comprehensive}")
                ]
                
                failed_criteria = [desc for passed, desc in success_criteria if not passed]
                
                if len(failed_criteria) == 0:
                    self.log_test("Comprehensive WebApp Questionnaire", True, 
                                f"All criteria met: {len(prompts)} questions, {len(found_topics)} security topics, flags set correctly")
                    return True
                else:
                    self.log_test("Comprehensive WebApp Questionnaire", False, 
                                f"Failed criteria: {failed_criteria}")
                    return False
            else:
                self.log_test("Comprehensive WebApp Questionnaire", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Comprehensive WebApp Questionnaire", False, f"Error: {str(e)}")
            return False

    def test_questionnaire_completion_validation(self):
        """Test that questionnaire completion works and generates appropriate response"""
        try:
            # Test with comprehensive questionnaire responses
            questionnaire_completion = {
                "responses": {
                    "authentication_method": "password_only",
                    "encryption_enabled": False,
                    "input_validation": "basic",
                    "security_headers": "disabled",
                    "logging_enabled": False,
                    "https_enforced": False,
                    "session_management": "basic",
                    "error_handling": "verbose"
                },
                "business_context": {
                    "criticality": "high",
                    "data_classification": "confidential"
                }
            }
            
            completion_response = self.session.post(
                f"{self.base_url}/questionnaires/WebApp/complete",
                json=questionnaire_completion,
                headers={"Content-Type": "application/json"}
            )
            
            if completion_response.status_code == 200:
                completion_data = completion_response.json()
                
                # Check for required response fields
                required_fields = ["completion_id", "node_subtype", "success", "processing_results"]
                missing_fields = [f for f in required_fields if f not in completion_data]
                
                if missing_fields:
                    self.log_test("Questionnaire Completion Validation", False, f"Missing response fields: {missing_fields}")
                    return False
                
                # Check processing results
                processing_results = completion_data.get("processing_results", {})
                if "processing_steps" not in processing_results:
                    self.log_test("Questionnaire Completion Validation", False, "Missing processing_steps in processing_results")
                    return False
                
                processing_steps = processing_results.get("processing_steps", [])
                if len(processing_steps) < 5:  # Should have multiple processing steps
                    self.log_test("Questionnaire Completion Validation", False, f"Too few processing steps: {len(processing_steps)}")
                    return False
                
                self.log_test("Questionnaire Completion Validation", True, 
                            f"Questionnaire completion successful with {len(processing_steps)} processing steps")
                return True
            else:
                self.log_test("Questionnaire Completion Validation", False, f"HTTP {completion_response.status_code}: {completion_response.text}")
                return False
                
        except Exception as e:
            self.log_test("Questionnaire Completion Validation", False, f"Error: {str(e)}")
            return False

    def test_bulk_vulnerability_analysis_with_proper_format(self):
        """Test bulk vulnerability analysis with correct node format"""
        try:
            # Test with properly formatted nodes
            bulk_analysis_data = {
                "nodes": [
                    {
                        "node_id": f"test-webapp-{uuid.uuid4().hex[:8]}",
                        "node_type": "WebApp",
                        "questionnaire_responses": {
                            "authentication_method": "password_only",
                            "encryption_enabled": False,
                            "input_validation": "none",
                            "security_headers": "disabled"
                        },
                        "position": {"x": 400, "y": 300}
                    }
                ]
            }
            
            analysis_response = self.session.post(
                f"{self.base_url}/vulnerabilities/bulk-analyze",
                json=bulk_analysis_data,
                headers={"Content-Type": "application/json"}
            )
            
            if analysis_response.status_code == 200:
                analysis_data = analysis_response.json()
                
                # Should return a list of analysis results
                if not isinstance(analysis_data, list):
                    self.log_test("Bulk Vulnerability Analysis", False, f"Expected list response, got: {type(analysis_data)}")
                    return False
                
                if len(analysis_data) == 0:
                    self.log_test("Bulk Vulnerability Analysis", False, "No analysis results returned")
                    return False
                
                result = analysis_data[0]
                
                # Check for required fields in result
                required_fields = ["node_id", "node_type", "total_vulnerabilities", "overall_risk_score"]
                missing_fields = [f for f in required_fields if f not in result]
                
                if missing_fields:
                    self.log_test("Bulk Vulnerability Analysis", False, f"Missing result fields: {missing_fields}")
                    return False
                
                # Check if vulnerabilities were detected for weak configuration
                total_vulns = result.get("total_vulnerabilities", 0)
                risk_score = result.get("overall_risk_score", 0)
                
                if "error" in result:
                    self.log_test("Bulk Vulnerability Analysis", False, f"Analysis error: {result['error']}")
                    return False
                
                self.log_test("Bulk Vulnerability Analysis", True, 
                            f"Analysis successful: {total_vulns} vulnerabilities, risk score: {risk_score}")
                return True
            else:
                self.log_test("Bulk Vulnerability Analysis", False, f"HTTP {analysis_response.status_code}: {analysis_response.text}")
                return False
                
        except Exception as e:
            self.log_test("Bulk Vulnerability Analysis", False, f"Error: {str(e)}")
            return False

    def test_smart_hierarchical_layout_algorithm(self):
        """Test POST /api/diagrams/{diagram_id}/auto-layout with smart_hierarchical algorithm"""
        try:
            # Create a test diagram first
            diagram_data = {
                "title": "Layout Test Diagram",
                "description": "Testing smart hierarchical layout algorithm"
            }
            
            diagram_response = self.session.post(
                f"{self.base_url}/diagrams",
                json=diagram_data,
                headers={"Content-Type": "application/json"}
            )
            
            if diagram_response.status_code != 200:
                self.log_test("Smart Hierarchical Layout", False, f"Failed to create test diagram: {diagram_response.text}")
                return False
            
            diagram = diagram_response.json()
            diagram_id = diagram.get("id")
            
            # Add some nodes to the diagram
            webapp_node = {
                "id": f"webapp-{uuid.uuid4().hex[:8]}",
                "type": "Asset",
                "subtype": "WebApp",
                "label": "Test Web Application",
                "position": {"x": 400, "y": 300},
                "data": {}
            }
            
            attacker_node = {
                "id": f"attacker-{uuid.uuid4().hex[:8]}",
                "type": "Actor",
                "subtype": "ExternalAttacker",
                "label": "External Attacker",
                "position": {"x": 200, "y": 200},
                "data": {}
            }
            
            diagram["nodes"] = [webapp_node, attacker_node]
            
            # Update diagram with nodes
            update_response = self.session.put(
                f"{self.base_url}/diagrams/{diagram_id}",
                json=diagram,
                headers={"Content-Type": "application/json"}
            )
            
            if update_response.status_code != 200:
                self.log_test("Smart Hierarchical Layout", False, f"Failed to update diagram: {update_response.text}")
                return False
            
            # Test the auto-layout endpoint with smart_hierarchical algorithm
            layout_response = self.session.post(
                f"{self.base_url}/diagrams/{diagram_id}/auto-layout",
                json={"algorithm": "smart_hierarchical"},
                headers={"Content-Type": "application/json"}
            )
            
            if layout_response.status_code == 200:
                data = layout_response.json()
                
                # Check for required response fields
                required_fields = ["layout_positions", "algorithm", "node_count"]
                missing_fields = [f for f in required_fields if f not in data]
                
                if missing_fields:
                    self.log_test("Smart Hierarchical Layout", False, f"Missing response fields: {missing_fields}")
                    return False
                
                if data.get("algorithm") != "smart_hierarchical":
                    self.log_test("Smart Hierarchical Layout", False, f"Wrong algorithm returned: {data.get('algorithm')}")
                    return False
                
                layout_positions = data.get("layout_positions", {})
                node_count = data.get("node_count", 0)
                
                if node_count != 2:
                    self.log_test("Smart Hierarchical Layout", False, f"Expected 2 nodes, got {node_count}")
                    return False
                
                if len(layout_positions) != 2:
                    self.log_test("Smart Hierarchical Layout", False, f"Expected 2 layout positions, got {len(layout_positions)}")
                    return False
                
                # Check that positions are valid
                for node_id, position in layout_positions.items():
                    if "x" not in position or "y" not in position:
                        self.log_test("Smart Hierarchical Layout", False, f"Invalid position for node {node_id}: {position}")
                        return False
                
                self.log_test("Smart Hierarchical Layout", True, 
                            f"Smart hierarchical layout generated for {node_count} nodes with valid positions")
                return True
            else:
                self.log_test("Smart Hierarchical Layout", False, f"HTTP {layout_response.status_code}: {layout_response.text}")
                return False
                
        except Exception as e:
            self.log_test("Smart Hierarchical Layout", False, f"Error: {str(e)}")
            return False

    def test_old_vs_new_questionnaire_system_comparison(self):
        """Compare old intelligent-nodes prompts vs new comprehensive questionnaires"""
        try:
            # Test old system (intelligent-nodes)
            old_response = self.session.get(f"{self.base_url}/intelligent-nodes/WebApp/prompts")
            
            # Test new system (comprehensive questionnaires)
            new_response = self.session.get(f"{self.base_url}/questionnaires/WebApp")
            
            if old_response.status_code == 200 and new_response.status_code == 200:
                old_data = old_response.json()
                new_data = new_response.json()
                
                old_prompts = old_data.get("prompts", [])
                new_prompts = new_data.get("prompts", [])
                
                old_count = len(old_prompts)
                new_count = len(new_prompts)
                
                # New system should have more questions
                if new_count <= old_count:
                    self.log_test("Old vs New System Comparison", False, 
                                f"New system should have more questions: new={new_count}, old={old_count}")
                    return False
                
                # Check for missing security topics in old system
                security_topics = ["security headers", "logging", "https", "session management", "error handling", "encryption"]
                
                old_topics = set()
                new_topics = set()
                
                for prompt in old_prompts:
                    question = prompt.get("question", "").lower()
                    for topic in security_topics:
                        if any(word in question for word in topic.split()):
                            old_topics.add(topic)
                
                for prompt in new_prompts:
                    question = prompt.get("question", "").lower()
                    for topic in security_topics:
                        if any(word in question for word in topic.split()):
                            new_topics.add(topic)
                
                missing_in_old = new_topics - old_topics
                
                if len(missing_in_old) == 0:
                    self.log_test("Old vs New System Comparison", False, 
                                "New system doesn't add any new security topics")
                    return False
                
                self.log_test("Old vs New System Comparison", True, 
                            f"New system has {new_count} questions vs old system {old_count}. New topics added: {list(missing_in_old)}")
                return True
            else:
                self.log_test("Old vs New System Comparison", False, 
                            f"Failed to fetch systems: old={old_response.status_code}, new={new_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Old vs New System Comparison", False, f"Error: {str(e)}")
            return False

    def test_integration_webapp_questionnaire_to_vulnerability_analysis(self):
        """Integration test: Create WebApp node, complete questionnaire, analyze vulnerabilities"""
        try:
            # Step 1: Get WebApp questionnaire
            questionnaire_response = self.session.get(f"{self.base_url}/questionnaires/WebApp")
            
            if questionnaire_response.status_code != 200:
                self.log_test("Integration Test", False, f"Failed to get questionnaire: {questionnaire_response.text}")
                return False
            
            questionnaire_data = questionnaire_response.json()
            prompts = questionnaire_data.get("prompts", [])
            
            if len(prompts) < 8:
                self.log_test("Integration Test", False, f"Insufficient questions in questionnaire: {len(prompts)}")
                return False
            
            # Step 2: Complete comprehensive questionnaire with weak security settings
            weak_responses = {
                "authentication_method": "password_only",
                "encryption_enabled": False,
                "input_validation": "none",
                "security_headers": "disabled",
                "logging_enabled": False,
                "https_enforced": False,
                "session_management": "basic",
                "error_handling": "verbose"
            }
            
            questionnaire_completion = {
                "responses": weak_responses,
                "business_context": {
                    "criticality": "high",
                    "data_classification": "confidential"
                }
            }
            
            completion_response = self.session.post(
                f"{self.base_url}/questionnaires/WebApp/complete",
                json=questionnaire_completion,
                headers={"Content-Type": "application/json"}
            )
            
            if completion_response.status_code != 200:
                self.log_test("Integration Test", False, f"Failed to complete questionnaire: {completion_response.text}")
                return False
            
            completion_data = completion_response.json()
            
            if not completion_data.get("success", False):
                self.log_test("Integration Test", False, f"Questionnaire completion not successful: {completion_data}")
                return False
            
            # Step 3: Analyze vulnerabilities with the completed questionnaire responses
            node_id = f"integration-webapp-{uuid.uuid4().hex[:8]}"
            
            bulk_analysis_data = {
                "nodes": [
                    {
                        "node_id": node_id,
                        "node_type": "WebApp",
                        "questionnaire_responses": weak_responses,
                        "position": {"x": 400, "y": 300}
                    }
                ]
            }
            
            analysis_response = self.session.post(
                f"{self.base_url}/vulnerabilities/bulk-analyze",
                json=bulk_analysis_data,
                headers={"Content-Type": "application/json"}
            )
            
            if analysis_response.status_code != 200:
                self.log_test("Integration Test", False, f"Failed vulnerability analysis: {analysis_response.text}")
                return False
            
            analysis_data = analysis_response.json()
            
            if not isinstance(analysis_data, list) or len(analysis_data) == 0:
                self.log_test("Integration Test", False, f"Invalid analysis response: {analysis_data}")
                return False
            
            result = analysis_data[0]
            
            # Step 4: Verify vulnerabilities include context and educational explanations
            total_vulns = result.get("total_vulnerabilities", 0)
            vulnerability_nodes = result.get("vulnerability_nodes", [])
            
            if total_vulns == 0:
                self.log_test("Integration Test", False, "No vulnerabilities detected despite weak configuration")
                return False
            
            # Check for educational content in vulnerabilities
            educational_content_found = False
            context_found = False
            
            for vuln in vulnerability_nodes:
                if "name" in vuln and "severity" in vuln:
                    educational_content_found = True
                if "category" in vuln or "owasp_category" in vuln:
                    context_found = True
            
            success_criteria = [
                (total_vulns > 0, f"Vulnerabilities detected: {total_vulns}"),
                (len(vulnerability_nodes) > 0, f"Vulnerability nodes: {len(vulnerability_nodes)}"),
                (educational_content_found, f"Educational content: {educational_content_found}"),
                (context_found, f"Context information: {context_found}")
            ]
            
            failed_criteria = [desc for passed, desc in success_criteria if not passed]
            
            if len(failed_criteria) == 0:
                self.log_test("Integration Test", True, 
                            f"Complete integration successful: questionnaire → {total_vulns} vulnerabilities with educational content")
                return True
            else:
                self.log_test("Integration Test", False, 
                            f"Integration issues: {failed_criteria}")
                return False
                
        except Exception as e:
            self.log_test("Integration Test", False, f"Error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all focused questionnaire and vulnerability analysis tests"""
        print("🚀 Starting Focused Questionnaire and Vulnerability Analysis System Tests")
        print("=" * 85)
        
        tests = [
            # Basic connectivity
            self.test_health_check,
            
            # CRITICAL TEST 1: Comprehensive WebApp Questionnaire System
            self.test_comprehensive_webapp_questionnaire_basic,
            
            # CRITICAL TEST 2: Questionnaire Completion Validation
            self.test_questionnaire_completion_validation,
            self.test_bulk_vulnerability_analysis_with_proper_format,
            
            # CRITICAL TEST 3: Improved Graph Layout
            self.test_smart_hierarchical_layout_algorithm,
            
            # CRITICAL TEST 4: Compare Old vs New System
            self.test_old_vs_new_questionnaire_system_comparison,
            
            # CRITICAL TEST 5: Integration Test
            self.test_integration_webapp_questionnaire_to_vulnerability_analysis
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
        print("=" * 85)
        print("🎯 FOCUSED QUESTIONNAIRE & VULNERABILITY ANALYSIS TEST SUMMARY")
        print("=" * 85)
        print(f"✅ PASSED: {passed}")
        print(f"❌ FAILED: {failed}")
        print(f"📊 SUCCESS RATE: {(passed / (passed + failed) * 100):.1f}%")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED! Questionnaire and vulnerability analysis systems are working correctly.")
        else:
            print(f"\n⚠️  {failed} tests failed. Please review the failed tests above.")
        
        return passed, failed

def main():
    """Main test execution"""
    tester = FocusedQuestionnaireTester()
    passed, failed = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()