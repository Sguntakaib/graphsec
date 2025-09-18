#!/usr/bin/env python3
"""
Comprehensive Questionnaire and Vulnerability Analysis System Tests
Tests the comprehensive questionnaire system fixes as requested in the review request.

CRITICAL TESTS NEEDED:
1. Comprehensive WebApp Questionnaire System (8 questions basic, 18 advanced, 28 expert)
2. Questionnaire Completion Validation (requires ALL questions answered)
3. Improved Graph Layout (smart_hierarchical algorithm with orbital positioning)
4. Compare Old vs New System (6 questions vs 8+ questions)
5. Integration Test (WebApp node → questionnaire → vulnerability analysis)
"""

import requests
import json
import uuid
from datetime import datetime, timezone
import sys

# Use the backend URL from frontend/.env with /api suffix
BASE_URL = "https://devvulnscan.preview.emergentagent.com/api"

class ComprehensiveQuestionnaireTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.test_results = []
        self.test_diagram_id = None
        
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
    # CRITICAL TEST 1: Comprehensive WebApp Questionnaire System
    # ============================================================================
    
    def test_webapp_questionnaire_basic_level(self):
        """Test GET /api/questionnaires/WebApp - should return 8 questions for basic level"""
        try:
            response = self.session.get(f"{self.base_url}/questionnaires/WebApp")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for required fields
                if "prompts" not in data:
                    self.log_test("WebApp Basic Questionnaire", False, "Missing 'prompts' field in response")
                    return False
                
                prompts = data.get("prompts", [])
                
                # Should have at least 8 questions for basic level
                if len(prompts) < 8:
                    self.log_test("WebApp Basic Questionnaire", False, f"Expected at least 8 questions, got {len(prompts)}")
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
                        if topic.replace(" ", "") in question_text.replace(" ", "") or any(word in question_text for word in topic.split()):
                            if topic not in found_topics:
                                found_topics.append(topic)
                
                missing_topics = [topic for topic in required_topics if topic not in found_topics]
                
                # Check for completion_required and is_comprehensive flags
                completion_required = data.get("completion_required", False)
                is_comprehensive = data.get("is_comprehensive", False)
                
                if not completion_required:
                    self.log_test("WebApp Basic Questionnaire", False, "completion_required flag not set to true")
                    return False
                
                if not is_comprehensive:
                    self.log_test("WebApp Basic Questionnaire", False, "is_comprehensive flag not set to true")
                    return False
                
                if len(missing_topics) > 2:  # Allow some flexibility
                    self.log_test("WebApp Basic Questionnaire", False, 
                                f"Missing key security topics: {missing_topics}. Found: {found_topics}")
                    return False
                
                self.log_test("WebApp Basic Questionnaire", True, 
                            f"Found {len(prompts)} questions with {len(found_topics)}/8 required security topics, completion_required=true, is_comprehensive=true")
                return True
            else:
                self.log_test("WebApp Basic Questionnaire", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("WebApp Basic Questionnaire", False, f"Error: {str(e)}")
            return False

    def test_webapp_questionnaire_advanced_level(self):
        """Test GET /api/questionnaires/WebApp?level=advanced - should return 18 questions"""
        try:
            response = self.session.get(f"{self.base_url}/questionnaires/WebApp?level=advanced")
            
            if response.status_code == 200:
                data = response.json()
                prompts = data.get("prompts", [])
                
                # Should have at least 18 questions for advanced level
                if len(prompts) < 18:
                    self.log_test("WebApp Advanced Questionnaire", False, f"Expected at least 18 questions, got {len(prompts)}")
                    return False
                
                self.log_test("WebApp Advanced Questionnaire", True, f"Found {len(prompts)} questions for advanced level")
                return True
            else:
                self.log_test("WebApp Advanced Questionnaire", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("WebApp Advanced Questionnaire", False, f"Error: {str(e)}")
            return False

    def test_webapp_questionnaire_expert_level(self):
        """Test GET /api/questionnaires/WebApp?level=expert - should return 28 questions"""
        try:
            response = self.session.get(f"{self.base_url}/questionnaires/WebApp?level=expert")
            
            if response.status_code == 200:
                data = response.json()
                prompts = data.get("prompts", [])
                
                # Should have at least 28 questions for expert level
                if len(prompts) < 28:
                    self.log_test("WebApp Expert Questionnaire", False, f"Expected at least 28 questions, got {len(prompts)}")
                    return False
                
                self.log_test("WebApp Expert Questionnaire", True, f"Found {len(prompts)} questions for expert level")
                return True
            else:
                self.log_test("WebApp Expert Questionnaire", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("WebApp Expert Questionnaire", False, f"Error: {str(e)}")
            return False

    # ============================================================================
    # CRITICAL TEST 2: Questionnaire Completion Validation
    # ============================================================================
    
    def test_vulnerability_analysis_requires_complete_questionnaire(self):
        """Test that vulnerability analysis requires ALL questions to be answered first"""
        try:
            # Create a test diagram first
            diagram_data = {
                "title": "Test Vulnerability Analysis Validation",
                "description": "Testing questionnaire completion validation"
            }
            
            diagram_response = self.session.post(
                f"{self.base_url}/diagrams",
                json=diagram_data,
                headers={"Content-Type": "application/json"}
            )
            
            if diagram_response.status_code != 200:
                self.log_test("Vulnerability Analysis Validation", False, f"Failed to create test diagram: {diagram_response.text}")
                return False
            
            diagram = diagram_response.json()
            diagram_id = diagram.get("id")
            self.test_diagram_id = diagram_id
            
            # Add a WebApp node to the diagram
            webapp_node = {
                "id": f"webapp-{uuid.uuid4().hex[:8]}",
                "type": "Asset",
                "subtype": "WebApp",
                "label": "Test Web Application",
                "position": {"x": 400, "y": 300},
                "data": {}
            }
            
            diagram["nodes"] = [webapp_node]
            
            # Update diagram with the node
            update_response = self.session.put(
                f"{self.base_url}/diagrams/{diagram_id}",
                json=diagram,
                headers={"Content-Type": "application/json"}
            )
            
            if update_response.status_code != 200:
                self.log_test("Vulnerability Analysis Validation", False, f"Failed to update diagram: {update_response.text}")
                return False
            
            # Try to analyze vulnerabilities without completing questionnaire
            bulk_analysis_data = {
                "nodes": [webapp_node]
            }
            
            analysis_response = self.session.post(
                f"{self.base_url}/vulnerabilities/bulk-analyze",
                json=bulk_analysis_data,
                headers={"Content-Type": "application/json"}
            )
            
            # Should fail or warn about incomplete questionnaire
            if analysis_response.status_code == 200:
                data = analysis_response.json()
                
                # Check if there's a warning about incomplete questionnaire
                if "error" in data or "warning" in data or "incomplete" in str(data).lower():
                    self.log_test("Vulnerability Analysis Validation", True, 
                                "System correctly requires questionnaire completion before vulnerability analysis")
                    return True
                else:
                    # If it proceeds without validation, that's a problem
                    self.log_test("Vulnerability Analysis Validation", False, 
                                "System allows vulnerability analysis without completing questionnaire")
                    return False
            else:
                # If it returns an error, check if it's about questionnaire completion
                error_text = analysis_response.text.lower()
                if "questionnaire" in error_text or "complete" in error_text or "answer" in error_text:
                    self.log_test("Vulnerability Analysis Validation", True, 
                                f"System correctly blocks analysis with error: {analysis_response.text}")
                    return True
                else:
                    self.log_test("Vulnerability Analysis Validation", False, 
                                f"Unexpected error (not questionnaire-related): {analysis_response.text}")
                    return False
                
        except Exception as e:
            self.log_test("Vulnerability Analysis Validation", False, f"Error: {str(e)}")
            return False

    def test_bulk_analysis_incomplete_vs_complete_questionnaires(self):
        """Test bulk analysis endpoint with incomplete vs complete questionnaires"""
        try:
            # Test with incomplete questionnaire responses
            incomplete_node = {
                "id": f"webapp-incomplete-{uuid.uuid4().hex[:8]}",
                "type": "Asset",
                "subtype": "WebApp",
                "label": "Incomplete WebApp",
                "position": {"x": 200, "y": 200},
                "questionnaire_responses": {
                    "authentication_method": "password_only"
                    # Missing other required responses
                }
            }
            
            incomplete_data = {
                "nodes": [incomplete_node]
            }
            
            incomplete_response = self.session.post(
                f"{self.base_url}/vulnerabilities/bulk-analyze",
                json=incomplete_data,
                headers={"Content-Type": "application/json"}
            )
            
            # Test with complete questionnaire responses
            complete_node = {
                "id": f"webapp-complete-{uuid.uuid4().hex[:8]}",
                "type": "Asset",
                "subtype": "WebApp",
                "label": "Complete WebApp",
                "position": {"x": 600, "y": 200},
                "questionnaire_responses": {
                    "authentication_method": "oauth2",
                    "encryption_enabled": True,
                    "input_validation": "comprehensive",
                    "security_headers": "enabled",
                    "logging_enabled": True,
                    "https_enforced": True,
                    "session_management": "secure",
                    "error_handling": "secure"
                }
            }
            
            complete_data = {
                "nodes": [complete_node]
            }
            
            complete_response = self.session.post(
                f"{self.base_url}/vulnerabilities/bulk-analyze",
                json=complete_data,
                headers={"Content-Type": "application/json"}
            )
            
            # Compare responses
            incomplete_success = incomplete_response.status_code == 200
            complete_success = complete_response.status_code == 200
            
            if incomplete_success and complete_success:
                incomplete_data = incomplete_response.json()
                complete_data = complete_response.json()
                
                # Complete questionnaire should generate more comprehensive analysis
                incomplete_vulns = len(incomplete_data.get("vulnerability_nodes", []))
                complete_vulns = len(complete_data.get("vulnerability_nodes", []))
                
                if complete_vulns > incomplete_vulns:
                    self.log_test("Bulk Analysis Comparison", True, 
                                f"Complete questionnaire generates more comprehensive analysis: {complete_vulns} vs {incomplete_vulns} vulnerabilities")
                    return True
                else:
                    self.log_test("Bulk Analysis Comparison", False, 
                                f"Complete questionnaire should generate more analysis: {complete_vulns} vs {incomplete_vulns} vulnerabilities")
                    return False
            else:
                # Check if incomplete fails appropriately
                if not incomplete_success and complete_success:
                    self.log_test("Bulk Analysis Comparison", True, 
                                "Incomplete questionnaire correctly rejected, complete questionnaire processed")
                    return True
                else:
                    self.log_test("Bulk Analysis Comparison", False, 
                                f"Unexpected response pattern: incomplete={incomplete_response.status_code}, complete={complete_response.status_code}")
                    return False
                
        except Exception as e:
            self.log_test("Bulk Analysis Comparison", False, f"Error: {str(e)}")
            return False

    # ============================================================================
    # CRITICAL TEST 3: Improved Graph Layout
    # ============================================================================
    
    def test_smart_hierarchical_layout_algorithm(self):
        """Test POST /api/diagrams/{diagram_id}/auto-layout with smart_hierarchical algorithm"""
        try:
            if not self.test_diagram_id:
                self.log_test("Smart Hierarchical Layout", False, "No test diagram available")
                return False
            
            # Test the auto-layout endpoint with smart_hierarchical algorithm
            layout_response = self.session.post(
                f"{self.base_url}/diagrams/{self.test_diagram_id}/auto-layout",
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
                if not layout_positions:
                    self.log_test("Smart Hierarchical Layout", False, "No layout positions returned")
                    return False
                
                self.log_test("Smart Hierarchical Layout", True, 
                            f"Smart hierarchical layout generated for {data.get('node_count')} nodes")
                return True
            else:
                self.log_test("Smart Hierarchical Layout", False, f"HTTP {layout_response.status_code}: {layout_response.text}")
                return False
                
        except Exception as e:
            self.log_test("Smart Hierarchical Layout", False, f"Error: {str(e)}")
            return False

    def test_vulnerability_dense_scenario_layout(self):
        """Test layout handling for vulnerability-dense scenarios (15+ vulnerabilities around 4-5 main nodes)"""
        try:
            # Create a diagram with 5 main nodes and 15+ vulnerability nodes
            vulnerability_dense_diagram = {
                "title": "Vulnerability Dense Test Diagram",
                "description": "Testing layout with 15+ vulnerabilities around 5 main nodes",
                "nodes": [],
                "edges": []
            }
            
            # Create 5 main nodes
            main_nodes = []
            for i in range(5):
                node = {
                    "id": f"main-node-{i}",
                    "type": "Asset",
                    "subtype": "WebApp",
                    "label": f"Main Node {i+1}",
                    "position": {"x": 200 + (i * 200), "y": 300},
                    "data": {}
                }
                main_nodes.append(node)
                vulnerability_dense_diagram["nodes"].append(node)
            
            # Create 15+ vulnerability nodes (3-4 per main node)
            vulnerability_nodes = []
            for i, main_node in enumerate(main_nodes):
                vuln_count = 3 if i < 2 else 4  # 3+3+4+4+4 = 18 vulnerabilities
                for j in range(vuln_count):
                    vuln_node = {
                        "id": f"vuln-{i}-{j}",
                        "type": "vulnerability",
                        "subtype": "SecurityVulnerability",
                        "label": f"Vulnerability {i+1}-{j+1}",
                        "position": {"x": 0, "y": 0},  # Will be positioned by layout
                        "parent_node_id": main_node["id"],
                        "data": {
                            "severity": "High",
                            "name": f"Test Vulnerability {i+1}-{j+1}"
                        }
                    }
                    vulnerability_nodes.append(vuln_node)
                    vulnerability_dense_diagram["nodes"].append(vuln_node)
            
            # Create the diagram
            create_response = self.session.post(
                f"{self.base_url}/diagrams",
                json=vulnerability_dense_diagram,
                headers={"Content-Type": "application/json"}
            )
            
            if create_response.status_code != 200:
                self.log_test("Vulnerability Dense Layout", False, f"Failed to create dense diagram: {create_response.text}")
                return False
            
            dense_diagram = create_response.json()
            dense_diagram_id = dense_diagram.get("id")
            
            # Test auto-layout on the dense diagram
            layout_response = self.session.post(
                f"{self.base_url}/diagrams/{dense_diagram_id}/auto-layout",
                json={"algorithm": "smart_hierarchical"},
                headers={"Content-Type": "application/json"}
            )
            
            if layout_response.status_code == 200:
                data = layout_response.json()
                layout_positions = data.get("layout_positions", {})
                
                # Verify all nodes have positions
                total_nodes = len(main_nodes) + len(vulnerability_nodes)
                positioned_nodes = len(layout_positions)
                
                if positioned_nodes < total_nodes:
                    self.log_test("Vulnerability Dense Layout", False, 
                                f"Not all nodes positioned: {positioned_nodes}/{total_nodes}")
                    return False
                
                # Check orbital positioning for vulnerability nodes
                orbital_positioned = 0
                for vuln_node in vulnerability_nodes:
                    vuln_id = vuln_node["id"]
                    parent_id = vuln_node["parent_node_id"]
                    
                    if vuln_id in layout_positions and parent_id in layout_positions:
                        vuln_pos = layout_positions[vuln_id]
                        parent_pos = layout_positions[parent_id]
                        
                        # Calculate distance from parent
                        dx = vuln_pos["x"] - parent_pos["x"]
                        dy = vuln_pos["y"] - parent_pos["y"]
                        distance = (dx**2 + dy**2)**0.5
                        
                        # Should be positioned at orbital distance (around 120-250px)
                        if 100 <= distance <= 300:
                            orbital_positioned += 1
                
                orbital_percentage = (orbital_positioned / len(vulnerability_nodes)) * 100
                
                if orbital_percentage >= 80:  # At least 80% should be orbitally positioned
                    self.log_test("Vulnerability Dense Layout", True, 
                                f"Successfully positioned {positioned_nodes} nodes with {orbital_percentage:.1f}% orbital positioning")
                    return True
                else:
                    self.log_test("Vulnerability Dense Layout", False, 
                                f"Poor orbital positioning: only {orbital_percentage:.1f}% of vulnerabilities properly positioned")
                    return False
            else:
                self.log_test("Vulnerability Dense Layout", False, f"Layout failed: HTTP {layout_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Vulnerability Dense Layout", False, f"Error: {str(e)}")
            return False

    # ============================================================================
    # CRITICAL TEST 4: Compare Old vs New System
    # ============================================================================
    
    def test_old_vs_new_questionnaire_system(self):
        """Compare old intelligent-nodes prompts (6 questions) vs new comprehensive system (8+ questions)"""
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
                if new_count > old_count:
                    # Check for missing security topics in old system
                    old_topics = set()
                    new_topics = set()
                    
                    for prompt in old_prompts:
                        question = prompt.get("question", "").lower()
                        if "security" in question or "header" in question:
                            old_topics.add("security_headers")
                        if "log" in question:
                            old_topics.add("logging")
                        if "auth" in question:
                            old_topics.add("authentication")
                        if "valid" in question:
                            old_topics.add("validation")
                        if "https" in question or "ssl" in question:
                            old_topics.add("https")
                        if "session" in question:
                            old_topics.add("session")
                        if "error" in question:
                            old_topics.add("error_handling")
                        if "encrypt" in question:
                            old_topics.add("encryption")
                    
                    for prompt in new_prompts:
                        question = prompt.get("question", "").lower()
                        if "security" in question or "header" in question:
                            new_topics.add("security_headers")
                        if "log" in question:
                            new_topics.add("logging")
                        if "auth" in question:
                            new_topics.add("authentication")
                        if "valid" in question:
                            new_topics.add("validation")
                        if "https" in question or "ssl" in question:
                            new_topics.add("https")
                        if "session" in question:
                            new_topics.add("session")
                        if "error" in question:
                            new_topics.add("error_handling")
                        if "encrypt" in question:
                            new_topics.add("encryption")
                    
                    missing_in_old = new_topics - old_topics
                    
                    self.log_test("Old vs New System Comparison", True, 
                                f"New system has {new_count} questions vs old system {old_count}. New topics added: {list(missing_in_old)}")
                    return True
                else:
                    self.log_test("Old vs New System Comparison", False, 
                                f"New system should have more questions: new={new_count}, old={old_count}")
                    return False
            else:
                self.log_test("Old vs New System Comparison", False, 
                            f"Failed to fetch systems: old={old_response.status_code}, new={new_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Old vs New System Comparison", False, f"Error: {str(e)}")
            return False

    # ============================================================================
    # CRITICAL TEST 5: Integration Test
    # ============================================================================
    
    def test_end_to_end_integration(self):
        """Create WebApp node, complete comprehensive questionnaire, then analyze vulnerabilities"""
        try:
            # Create a new diagram for integration test
            integration_diagram = {
                "title": "End-to-End Integration Test",
                "description": "Testing complete flow: WebApp → Questionnaire → Vulnerability Analysis"
            }
            
            create_response = self.session.post(
                f"{self.base_url}/diagrams",
                json=integration_diagram,
                headers={"Content-Type": "application/json"}
            )
            
            if create_response.status_code != 200:
                self.log_test("End-to-End Integration", False, f"Failed to create diagram: {create_response.text}")
                return False
            
            diagram = create_response.json()
            diagram_id = diagram.get("id")
            
            # Step 1: Create WebApp node
            webapp_node = {
                "id": f"integration-webapp-{uuid.uuid4().hex[:8]}",
                "type": "Asset",
                "subtype": "WebApp",
                "label": "Integration Test WebApp",
                "position": {"x": 400, "y": 300},
                "data": {}
            }
            
            diagram["nodes"] = [webapp_node]
            
            update_response = self.session.put(
                f"{self.base_url}/diagrams/{diagram_id}",
                json=diagram,
                headers={"Content-Type": "application/json"}
            )
            
            if update_response.status_code != 200:
                self.log_test("End-to-End Integration", False, f"Failed to add WebApp node: {update_response.text}")
                return False
            
            # Step 2: Complete comprehensive questionnaire
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
            
            if completion_response.status_code != 200:
                self.log_test("End-to-End Integration", False, f"Failed to complete questionnaire: {completion_response.text}")
                return False
            
            completion_data = completion_response.json()
            
            # Step 3: Analyze vulnerabilities
            analysis_data = {
                "nodes": [webapp_node],
                "questionnaire_responses": questionnaire_completion["responses"]
            }
            
            analysis_response = self.session.post(
                f"{self.base_url}/vulnerabilities/bulk-analyze",
                json=analysis_data,
                headers={"Content-Type": "application/json"}
            )
            
            if analysis_response.status_code == 200:
                analysis_result = analysis_response.json()
                vulnerabilities = analysis_result.get("vulnerability_nodes", [])
                
                if len(vulnerabilities) == 0:
                    self.log_test("End-to-End Integration", False, "No vulnerabilities detected despite weak configuration")
                    return False
                
                # Step 4: Verify vulnerabilities include user answer context and educational explanations
                context_found = False
                educational_found = False
                
                for vuln in vulnerabilities:
                    # Check for user answer context
                    if "trigger_context" in vuln or "user_selections" in vuln or "missing_controls" in vuln:
                        context_found = True
                    
                    # Check for educational explanations
                    if "description" in vuln or "remediation" in vuln or "educational" in str(vuln).lower():
                        educational_found = True
                
                if context_found and educational_found:
                    self.log_test("End-to-End Integration", True, 
                                f"Complete integration successful: {len(vulnerabilities)} vulnerabilities with context and educational content")
                    return True
                else:
                    self.log_test("End-to-End Integration", False, 
                                f"Missing context ({context_found}) or educational content ({educational_found}) in vulnerabilities")
                    return False
            else:
                self.log_test("End-to-End Integration", False, f"Vulnerability analysis failed: HTTP {analysis_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("End-to-End Integration", False, f"Error: {str(e)}")
            return False

    # ============================================================================
    # Test Runner
    # ============================================================================
    
    def run_all_tests(self):
        """Run all comprehensive questionnaire and vulnerability analysis tests"""
        print("🚀 Starting Comprehensive Questionnaire and Vulnerability Analysis System Tests")
        print("=" * 90)
        
        tests = [
            # Basic connectivity
            self.test_health_check,
            
            # CRITICAL TEST 1: Comprehensive WebApp Questionnaire System
            self.test_webapp_questionnaire_basic_level,
            self.test_webapp_questionnaire_advanced_level,
            self.test_webapp_questionnaire_expert_level,
            
            # CRITICAL TEST 2: Questionnaire Completion Validation
            self.test_vulnerability_analysis_requires_complete_questionnaire,
            self.test_bulk_analysis_incomplete_vs_complete_questionnaires,
            
            # CRITICAL TEST 3: Improved Graph Layout
            self.test_smart_hierarchical_layout_algorithm,
            self.test_vulnerability_dense_scenario_layout,
            
            # CRITICAL TEST 4: Compare Old vs New System
            self.test_old_vs_new_questionnaire_system,
            
            # CRITICAL TEST 5: Integration Test
            self.test_end_to_end_integration
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
        print("🎯 COMPREHENSIVE QUESTIONNAIRE & VULNERABILITY ANALYSIS TEST SUMMARY")
        print("=" * 90)
        print(f"✅ PASSED: {passed}")
        print(f"❌ FAILED: {failed}")
        print(f"📊 SUCCESS RATE: {(passed / (passed + failed) * 100):.1f}%")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED! Comprehensive questionnaire and vulnerability analysis systems are working correctly.")
        else:
            print(f"\n⚠️  {failed} tests failed. Please review the failed tests above.")
        
        return passed, failed

def main():
    """Main test execution"""
    tester = ComprehensiveQuestionnaireTester()
    passed, failed = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()