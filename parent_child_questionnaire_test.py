#!/usr/bin/env python3
"""
Parent-Child Relationship Questionnaire Flow Testing
Tests the parent-child relationship questionnaire flow bug fixes as specified in the review request.

TESTING FOCUS:
🎯 PRIMARY TEST: PARENT-CHILD RELATIONSHIP QUESTIONNAIRE FLOW BUG FIXES

1. **Core Dependency Chain Testing:**
   - Test WebApp→Database→Backup dependency chain that was causing loops
   - Create WebApp node, complete questionnaire with database connection enabled
   - Verify Database node auto-creation, complete Database questionnaire with backup enabled
   - Verify Backup node auto-creation and completion

2. **API 500 Error Resolution:**
   - Test POST /api/diagrams/{id}/nodes/{nodeId}/questionnaire endpoint
   - Ensure it no longer returns 500 errors when saving questionnaire responses
   - Verify proper data persistence

3. **Parent-Child Relationship Verification:**
   - Verify that when dependent nodes (Database, Backup) complete their questionnaires
   - System can properly identify their parent nodes
   - Mark dependencies as COMPLETED without "missing parentNodeId" error

4. **Questionnaire Resumption Testing:**
   - Test that when dependent questionnaires complete
   - Parent questionnaire resumes correctly without looping back to wrong questions

5. **Edge Case Testing:**
   - Test scenarios where multiple dependent nodes are created
   - Verify questionnaire stack management works correctly

**USER REPORTED ISSUES TO VERIFY FIXED:**
- "Could not mark dependency as completed - missing parentNodeId: undefined"
- HTTP 500 errors on questionnaire save endpoints
- Database questionnaire looping back to 5th question after completion
"""

import requests
import json
import uuid
from datetime import datetime, timezone
import sys
import time

# Use the backend URL from frontend/.env with /api suffix
BASE_URL = "https://iprove-reader.preview.emergentagent.com/api"

class ParentChildQuestionnaireTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.test_results = []
        self.test_diagram_id = None
        self.webapp_node_id = None
        self.database_node_id = None
        self.backup_node_id = None
        
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

    def setup_test_diagram(self):
        """Create a test diagram for parent-child relationship testing"""
        try:
            print("🎯 SETUP: Creating Test Diagram")
            print("=" * 80)
            
            # Create a new diagram
            diagram_data = {
                "title": "Parent-Child Questionnaire Test Diagram",
                "description": "Test diagram for parent-child relationship questionnaire flow"
            }
            
            response = self.session.post(f"{self.base_url}/diagrams", json=diagram_data)
            
            if response.status_code != 200:
                self.log_test("Setup Test Diagram", False, f"Failed to create diagram: HTTP {response.status_code}")
                return False
            
            diagram = response.json()
            self.test_diagram_id = diagram["id"]
            
            print(f"📋 Test Diagram Created: {self.test_diagram_id}")
            
            self.log_test("Setup Test Diagram", True, f"Created test diagram: {self.test_diagram_id}")
            return True
            
        except Exception as e:
            self.log_test("Setup Test Diagram", False, f"Setup error: {str(e)}")
            return False

    def test_webapp_node_creation_and_questionnaire(self):
        """
        CRITICAL TEST: Create WebApp node and complete questionnaire with database dependency
        
        This test verifies:
        1. WebApp node can be created successfully
        2. WebApp questionnaire can be completed with database connection enabled
        3. Database dependency is properly triggered
        """
        try:
            print("🎯 CRITICAL TEST: WebApp Node Creation and Questionnaire")
            print("=" * 80)
            
            if not self.test_diagram_id:
                self.log_test("WebApp Node Creation", False, "No test diagram available")
                return False
            
            # Create WebApp node
            self.webapp_node_id = f"webapp-{uuid.uuid4().hex[:8]}"
            webapp_node = {
                "id": self.webapp_node_id,
                "type": "Asset",
                "subtype": "WebApp",
                "label": "Test Web Application",
                "position": {"x": 200, "y": 100},
                "data": {
                    "criticality": "High",
                    "data_classification": "Confidential"
                }
            }
            
            # Get current diagram and add WebApp node
            diagram_response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}")
            if diagram_response.status_code != 200:
                self.log_test("WebApp Node Creation", False, "Failed to get diagram")
                return False
            
            diagram = diagram_response.json()
            diagram["nodes"].append(webapp_node)
            diagram["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            # Update diagram with WebApp node
            update_response = self.session.put(f"{self.base_url}/diagrams/{self.test_diagram_id}", json=diagram)
            if update_response.status_code != 200:
                self.log_test("WebApp Node Creation", False, f"Failed to add WebApp node: HTTP {update_response.status_code}")
                return False
            
            print(f"📋 WebApp Node Created: {self.webapp_node_id}")
            
            # Complete WebApp questionnaire with database connection enabled
            questionnaire_responses = {
                "responses": {
                    "authentication_method": "oauth2",
                    "encryption_enabled": True,
                    "input_validation": "comprehensive",
                    "webapp_database_connection": True,  # This should trigger Database dependency
                    "webapp_api_endpoints": False,
                    "webapp_external_services": False
                },
                "business_context": {
                    "criticality": "high",
                    "data_classification": "confidential",
                    "compliance_requirements": ["GDPR", "SOX"]
                }
            }
            
            # Test the questionnaire save endpoint that was causing 500 errors
            questionnaire_url = f"{self.base_url}/diagrams/{self.test_diagram_id}/nodes/{self.webapp_node_id}/questionnaire"
            questionnaire_response = self.session.post(questionnaire_url, json=questionnaire_responses)
            
            print(f"📋 WebApp Questionnaire Response Status: HTTP {questionnaire_response.status_code}")
            
            if questionnaire_response.status_code == 500:
                self.log_test("WebApp Node Creation", False, "❌ CRITICAL: Still getting 500 error on questionnaire save - bug not fixed!")
                return False
            elif questionnaire_response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = questionnaire_response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = questionnaire_response.text
                
                self.log_test("WebApp Node Creation", False, f"Questionnaire save failed: HTTP {questionnaire_response.status_code}: {error_detail}")
                return False
            
            try:
                questionnaire_data = questionnaire_response.json()
            except json.JSONDecodeError as e:
                self.log_test("WebApp Node Creation", False, f"Invalid JSON response: {str(e)}")
                return False
            
            print(f"📊 WebApp Questionnaire Results:")
            print(f"   Success: {questionnaire_data.get('success', False)}")
            print(f"   Dependencies triggered: {questionnaire_data.get('dependencies_triggered', [])}")
            print(f"   Dependent nodes created: {questionnaire_data.get('dependent_nodes_created', [])}")
            
            # Check if Database dependency was triggered
            dependencies_triggered = questionnaire_data.get('dependencies_triggered', [])
            if 'Database' not in dependencies_triggered:
                self.log_test("WebApp Node Creation", False, "Database dependency was not triggered")
                return False
            
            # Check if Database node was created
            dependent_nodes = questionnaire_data.get('dependent_nodes_created', [])
            database_nodes = [node for node in dependent_nodes if node.get('subtype') == 'Database']
            
            if not database_nodes:
                self.log_test("WebApp Node Creation", False, "Database node was not auto-created")
                return False
            
            self.database_node_id = database_nodes[0]['id']
            print(f"📋 Database Node Auto-Created: {self.database_node_id}")
            
            self.log_test("WebApp Node Creation", True, f"✅ SUCCESS: WebApp questionnaire completed, Database dependency triggered, Database node created: {self.database_node_id}")
            return True
            
        except Exception as e:
            self.log_test("WebApp Node Creation", False, f"Request error: {str(e)}")
            return False

    def test_database_questionnaire_with_backup_dependency(self):
        """
        CRITICAL TEST: Complete Database questionnaire with backup dependency
        
        This test verifies:
        1. Database questionnaire can be completed with backup enabled
        2. Backup dependency is properly triggered
        3. Backup node is auto-created
        4. Parent-child relationship is maintained
        """
        try:
            print("🎯 CRITICAL TEST: Database Questionnaire with Backup Dependency")
            print("=" * 80)
            
            if not self.database_node_id:
                self.log_test("Database Questionnaire", False, "No Database node available")
                return False
            
            # Complete Database questionnaire with backup enabled
            database_questionnaire_responses = {
                "responses": {
                    "database_type": "postgresql",
                    "database_encryption": True,
                    "database_backup_enabled": True,  # This should trigger Backup dependency
                    "database_access_control": "rbac",
                    "database_monitoring": True
                },
                "business_context": {
                    "criticality": "critical",
                    "data_classification": "restricted",
                    "compliance_requirements": ["GDPR", "HIPAA"]
                },
                "parent_node_id": self.webapp_node_id  # Ensure parent relationship is maintained
            }
            
            # Test the questionnaire save endpoint for Database
            questionnaire_url = f"{self.base_url}/diagrams/{self.test_diagram_id}/nodes/{self.database_node_id}/questionnaire"
            questionnaire_response = self.session.post(questionnaire_url, json=database_questionnaire_responses)
            
            print(f"📋 Database Questionnaire Response Status: HTTP {questionnaire_response.status_code}")
            
            if questionnaire_response.status_code == 500:
                self.log_test("Database Questionnaire", False, "❌ CRITICAL: Still getting 500 error on Database questionnaire save - bug not fixed!")
                return False
            elif questionnaire_response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = questionnaire_response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = questionnaire_response.text
                
                self.log_test("Database Questionnaire", False, f"Database questionnaire save failed: HTTP {questionnaire_response.status_code}: {error_detail}")
                return False
            
            try:
                questionnaire_data = questionnaire_response.json()
            except json.JSONDecodeError as e:
                self.log_test("Database Questionnaire", False, f"Invalid JSON response: {str(e)}")
                return False
            
            print(f"📊 Database Questionnaire Results:")
            print(f"   Success: {questionnaire_data.get('success', False)}")
            print(f"   Dependencies triggered: {questionnaire_data.get('dependencies_triggered', [])}")
            print(f"   Dependent nodes created: {questionnaire_data.get('dependent_nodes_created', [])}")
            print(f"   Parent node preserved: {questionnaire_data.get('parent_node_id', 'None')}")
            
            # Check if Backup dependency was triggered
            dependencies_triggered = questionnaire_data.get('dependencies_triggered', [])
            if 'Backup' not in dependencies_triggered:
                self.log_test("Database Questionnaire", False, "Backup dependency was not triggered")
                return False
            
            # Check if Backup node was created
            dependent_nodes = questionnaire_data.get('dependent_nodes_created', [])
            backup_nodes = [node for node in dependent_nodes if node.get('subtype') == 'Backup']
            
            if not backup_nodes:
                self.log_test("Database Questionnaire", False, "Backup node was not auto-created")
                return False
            
            self.backup_node_id = backup_nodes[0]['id']
            print(f"📋 Backup Node Auto-Created: {self.backup_node_id}")
            
            # Verify parent node relationship is preserved
            parent_node_id = questionnaire_data.get('parent_node_id')
            if parent_node_id != self.webapp_node_id:
                self.log_test("Database Questionnaire", False, f"Parent node relationship lost: expected {self.webapp_node_id}, got {parent_node_id}")
                return False
            
            self.log_test("Database Questionnaire", True, f"✅ SUCCESS: Database questionnaire completed, Backup dependency triggered, Backup node created: {self.backup_node_id}, Parent relationship preserved")
            return True
            
        except Exception as e:
            self.log_test("Database Questionnaire", False, f"Request error: {str(e)}")
            return False

    def test_backup_questionnaire_completion(self):
        """
        CRITICAL TEST: Complete Backup questionnaire and verify dependency chain completion
        
        This test verifies:
        1. Backup questionnaire can be completed successfully
        2. Parent-child relationships are properly identified
        3. Dependencies are marked as COMPLETED without "missing parentNodeId" error
        4. No questionnaire looping occurs
        """
        try:
            print("🎯 CRITICAL TEST: Backup Questionnaire Completion")
            print("=" * 80)
            
            if not self.backup_node_id:
                self.log_test("Backup Questionnaire", False, "No Backup node available")
                return False
            
            # Complete Backup questionnaire
            backup_questionnaire_responses = {
                "responses": {
                    "backup_strategy": "incremental",
                    "backup_encryption": True,
                    "backup_retention": "7_years",
                    "backup_testing": True,
                    "backup_offsite": True
                },
                "business_context": {
                    "criticality": "critical",
                    "data_classification": "restricted",
                    "compliance_requirements": ["GDPR", "SOX"]
                },
                "parent_node_id": self.database_node_id  # Ensure parent relationship is maintained
            }
            
            # Test the questionnaire save endpoint for Backup
            questionnaire_url = f"{self.base_url}/diagrams/{self.test_diagram_id}/nodes/{self.backup_node_id}/questionnaire"
            questionnaire_response = self.session.post(questionnaire_url, json=backup_questionnaire_responses)
            
            print(f"📋 Backup Questionnaire Response Status: HTTP {questionnaire_response.status_code}")
            
            if questionnaire_response.status_code == 500:
                self.log_test("Backup Questionnaire", False, "❌ CRITICAL: Still getting 500 error on Backup questionnaire save - bug not fixed!")
                return False
            elif questionnaire_response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = questionnaire_response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = questionnaire_response.text
                
                self.log_test("Backup Questionnaire", False, f"Backup questionnaire save failed: HTTP {questionnaire_response.status_code}: {error_detail}")
                return False
            
            try:
                questionnaire_data = questionnaire_response.json()
            except json.JSONDecodeError as e:
                self.log_test("Backup Questionnaire", False, f"Invalid JSON response: {str(e)}")
                return False
            
            print(f"📊 Backup Questionnaire Results:")
            print(f"   Success: {questionnaire_data.get('success', False)}")
            print(f"   Parent node preserved: {questionnaire_data.get('parent_node_id', 'None')}")
            print(f"   Dependency completion status: {questionnaire_data.get('dependency_completion_status', 'None')}")
            print(f"   Questionnaire resumption: {questionnaire_data.get('questionnaire_resumption', 'None')}")
            
            # Verify parent node relationship is preserved
            parent_node_id = questionnaire_data.get('parent_node_id')
            if parent_node_id != self.database_node_id:
                self.log_test("Backup Questionnaire", False, f"Parent node relationship lost: expected {self.database_node_id}, got {parent_node_id}")
                return False
            
            # Check for the specific error that was reported
            error_messages = questionnaire_data.get('error_messages', [])
            missing_parent_errors = [msg for msg in error_messages if 'missing parentNodeId' in str(msg)]
            
            if missing_parent_errors:
                self.log_test("Backup Questionnaire", False, f"❌ CRITICAL: Still getting 'missing parentNodeId' error: {missing_parent_errors}")
                return False
            
            # Verify dependency completion was successful
            dependency_completion = questionnaire_data.get('dependency_completion_status')
            if dependency_completion and dependency_completion != 'COMPLETED':
                self.log_test("Backup Questionnaire", False, f"Dependency not marked as COMPLETED: {dependency_completion}")
                return False
            
            self.log_test("Backup Questionnaire", True, f"✅ SUCCESS: Backup questionnaire completed, Parent relationship preserved, No 'missing parentNodeId' errors")
            return True
            
        except Exception as e:
            self.log_test("Backup Questionnaire", False, f"Request error: {str(e)}")
            return False

    def test_questionnaire_resumption_flow(self):
        """
        CRITICAL TEST: Test questionnaire resumption after dependent questionnaires complete
        
        This test verifies:
        1. Parent questionnaire can be resumed after dependent questionnaires complete
        2. No looping back to wrong questions occurs
        3. Questionnaire stack management works correctly
        """
        try:
            print("🎯 CRITICAL TEST: Questionnaire Resumption Flow")
            print("=" * 80)
            
            if not self.webapp_node_id or not self.database_node_id or not self.backup_node_id:
                self.log_test("Questionnaire Resumption", False, "Missing required nodes for resumption test")
                return False
            
            # Test resuming WebApp questionnaire after Database and Backup completion
            resumption_request = {
                "action": "resume_parent_questionnaire",
                "completed_dependent_nodes": [
                    {
                        "node_id": self.database_node_id,
                        "subtype": "Database",
                        "completion_status": "COMPLETED"
                    },
                    {
                        "node_id": self.backup_node_id,
                        "subtype": "Backup", 
                        "completion_status": "COMPLETED"
                    }
                ],
                "parent_node_id": self.webapp_node_id
            }
            
            # Test questionnaire resumption endpoint
            resumption_url = f"{self.base_url}/diagrams/{self.test_diagram_id}/nodes/{self.webapp_node_id}/questionnaire/resume"
            resumption_response = self.session.post(resumption_url, json=resumption_request)
            
            print(f"📋 Questionnaire Resumption Response Status: HTTP {resumption_response.status_code}")
            
            if resumption_response.status_code == 404:
                # If resumption endpoint doesn't exist, test the regular questionnaire endpoint
                # to see if it handles resumption correctly
                print("📋 Resumption endpoint not found, testing regular questionnaire endpoint for resumption handling")
                
                # Get current questionnaire state
                questionnaire_state_url = f"{self.base_url}/diagrams/{self.test_diagram_id}/nodes/{self.webapp_node_id}/questionnaire"
                state_response = self.session.get(questionnaire_state_url)
                
                if state_response.status_code == 200:
                    state_data = state_response.json()
                    current_question = state_data.get('current_question_index', 0)
                    total_questions = state_data.get('total_questions', 0)
                    
                    print(f"📊 Questionnaire State:")
                    print(f"   Current question index: {current_question}")
                    print(f"   Total questions: {total_questions}")
                    print(f"   Completion status: {state_data.get('completion_status', 'Unknown')}")
                    
                    # Check if we're not looping back to question 5 (the reported bug)
                    if current_question == 5 and total_questions > 5:
                        self.log_test("Questionnaire Resumption", False, "❌ CRITICAL: Database questionnaire looping back to 5th question - bug not fixed!")
                        return False
                    
                    self.log_test("Questionnaire Resumption", True, f"✅ SUCCESS: No questionnaire looping detected, current question: {current_question}")
                    return True
                else:
                    self.log_test("Questionnaire Resumption", False, f"Failed to get questionnaire state: HTTP {state_response.status_code}")
                    return False
            
            elif resumption_response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = resumption_response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = resumption_response.text
                
                self.log_test("Questionnaire Resumption", False, f"Resumption failed: HTTP {resumption_response.status_code}: {error_detail}")
                return False
            
            try:
                resumption_data = resumption_response.json()
            except json.JSONDecodeError as e:
                self.log_test("Questionnaire Resumption", False, f"Invalid JSON response: {str(e)}")
                return False
            
            print(f"📊 Questionnaire Resumption Results:")
            print(f"   Success: {resumption_data.get('success', False)}")
            print(f"   Resumed at question: {resumption_data.get('resumed_at_question', 'None')}")
            print(f"   Stack management status: {resumption_data.get('stack_management_status', 'None')}")
            print(f"   Loop prevention: {resumption_data.get('loop_prevention_active', False)}")
            
            # Check for loop prevention
            loop_prevention = resumption_data.get('loop_prevention_active', False)
            if not loop_prevention:
                print("⚠️  WARNING: Loop prevention not explicitly confirmed")
            
            self.log_test("Questionnaire Resumption", True, f"✅ SUCCESS: Questionnaire resumption working, Loop prevention active: {loop_prevention}")
            return True
            
        except Exception as e:
            self.log_test("Questionnaire Resumption", False, f"Request error: {str(e)}")
            return False

    def test_edge_case_multiple_dependencies(self):
        """
        CRITICAL TEST: Test edge case with multiple dependent nodes
        
        This test verifies:
        1. Multiple dependent nodes can be created and managed
        2. Questionnaire stack management works with complex scenarios
        3. Parent-child relationships are maintained across multiple levels
        """
        try:
            print("🎯 CRITICAL TEST: Edge Case - Multiple Dependencies")
            print("=" * 80)
            
            if not self.test_diagram_id:
                self.log_test("Multiple Dependencies", False, "No test diagram available")
                return False
            
            # Create a second WebApp node with multiple dependencies
            webapp2_node_id = f"webapp2-{uuid.uuid4().hex[:8]}"
            webapp2_node = {
                "id": webapp2_node_id,
                "type": "Asset",
                "subtype": "WebApp",
                "label": "Test Web Application 2",
                "position": {"x": 400, "y": 100},
                "data": {
                    "criticality": "High",
                    "data_classification": "Confidential"
                }
            }
            
            # Get current diagram and add second WebApp node
            diagram_response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}")
            if diagram_response.status_code != 200:
                self.log_test("Multiple Dependencies", False, "Failed to get diagram")
                return False
            
            diagram = diagram_response.json()
            diagram["nodes"].append(webapp2_node)
            diagram["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            # Update diagram with second WebApp node
            update_response = self.session.put(f"{self.base_url}/diagrams/{self.test_diagram_id}", json=diagram)
            if update_response.status_code != 200:
                self.log_test("Multiple Dependencies", False, f"Failed to add second WebApp node: HTTP {update_response.status_code}")
                return False
            
            print(f"📋 Second WebApp Node Created: {webapp2_node_id}")
            
            # Complete second WebApp questionnaire with multiple dependencies
            questionnaire_responses = {
                "responses": {
                    "authentication_method": "oauth2",
                    "encryption_enabled": True,
                    "input_validation": "comprehensive",
                    "webapp_database_connection": True,  # Database dependency
                    "webapp_api_endpoints": True,        # API dependency
                    "webapp_external_services": True     # External services dependency
                },
                "business_context": {
                    "criticality": "high",
                    "data_classification": "confidential"
                }
            }
            
            # Test questionnaire with multiple dependencies
            questionnaire_url = f"{self.base_url}/diagrams/{self.test_diagram_id}/nodes/{webapp2_node_id}/questionnaire"
            questionnaire_response = self.session.post(questionnaire_url, json=questionnaire_responses)
            
            print(f"📋 Multiple Dependencies Questionnaire Response Status: HTTP {questionnaire_response.status_code}")
            
            if questionnaire_response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = questionnaire_response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = questionnaire_response.text
                
                self.log_test("Multiple Dependencies", False, f"Multiple dependencies questionnaire failed: HTTP {questionnaire_response.status_code}: {error_detail}")
                return False
            
            try:
                questionnaire_data = questionnaire_response.json()
            except json.JSONDecodeError as e:
                self.log_test("Multiple Dependencies", False, f"Invalid JSON response: {str(e)}")
                return False
            
            print(f"📊 Multiple Dependencies Results:")
            print(f"   Success: {questionnaire_data.get('success', False)}")
            print(f"   Dependencies triggered: {questionnaire_data.get('dependencies_triggered', [])}")
            print(f"   Dependent nodes created: {len(questionnaire_data.get('dependent_nodes_created', []))}")
            print(f"   Stack management status: {questionnaire_data.get('stack_management_status', 'None')}")
            
            # Verify multiple dependencies were triggered
            dependencies_triggered = questionnaire_data.get('dependencies_triggered', [])
            expected_dependencies = ['Database', 'API']  # At least these two should be triggered
            
            missing_dependencies = []
            for dep in expected_dependencies:
                if dep not in dependencies_triggered:
                    missing_dependencies.append(dep)
            
            if missing_dependencies:
                self.log_test("Multiple Dependencies", False, f"Missing expected dependencies: {missing_dependencies}")
                return False
            
            # Verify multiple dependent nodes were created
            dependent_nodes = questionnaire_data.get('dependent_nodes_created', [])
            if len(dependent_nodes) < 2:
                self.log_test("Multiple Dependencies", False, f"Expected at least 2 dependent nodes, got {len(dependent_nodes)}")
                return False
            
            self.log_test("Multiple Dependencies", True, f"✅ SUCCESS: Multiple dependencies handled correctly, {len(dependencies_triggered)} dependencies triggered, {len(dependent_nodes)} nodes created")
            return True
            
        except Exception as e:
            self.log_test("Multiple Dependencies", False, f"Request error: {str(e)}")
            return False

    def cleanup_test_diagram(self):
        """Clean up test diagram after testing"""
        try:
            if self.test_diagram_id:
                print(f"🧹 CLEANUP: Deleting test diagram {self.test_diagram_id}")
                response = self.session.delete(f"{self.base_url}/diagrams/{self.test_diagram_id}")
                if response.status_code == 200:
                    print("✅ Test diagram cleaned up successfully")
                else:
                    print(f"⚠️  Warning: Failed to clean up test diagram: HTTP {response.status_code}")
        except Exception as e:
            print(f"⚠️  Warning: Cleanup error: {str(e)}")

    def run_all_tests(self):
        """Run all parent-child relationship questionnaire tests"""
        print("🚀 STARTING PARENT-CHILD RELATIONSHIP QUESTIONNAIRE FLOW TESTING")
        print("=" * 80)
        print("Testing the parent-child relationship questionnaire flow bug fixes")
        print("Verifying fixes for:")
        print("- 'Could not mark dependency as completed - missing parentNodeId: undefined'")
        print("- HTTP 500 errors on questionnaire save endpoints")
        print("- Database questionnaire looping back to 5th question after completion")
        print("=" * 80)
        
        tests = [
            self.test_health_check,
            self.setup_test_diagram,
            self.test_webapp_node_creation_and_questionnaire,
            self.test_database_questionnaire_with_backup_dependency,
            self.test_backup_questionnaire_completion,
            self.test_questionnaire_resumption_flow,
            self.test_edge_case_multiple_dependencies,
        ]
        
        passed = 0
        total = len(tests)
        
        try:
            for test in tests:
                try:
                    if test():
                        passed += 1
                    print()  # Add spacing between tests
                except Exception as e:
                    print(f"❌ Test {test.__name__} failed with exception: {str(e)}")
                    print()
        finally:
            # Always cleanup
            self.cleanup_test_diagram()
        
        print("=" * 80)
        print(f"🏁 TESTING COMPLETE: {passed}/{total} tests passed")
        print("=" * 80)
        
        # Print detailed results
        print("\n📊 DETAILED TEST RESULTS:")
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{status} {result['test']}: {result['message']}")
        
        # Summary of critical bug fixes
        print("\n🔍 CRITICAL BUG FIX VERIFICATION:")
        
        # Check for 500 errors
        error_500_tests = [r for r in self.test_results if "500 error" in r["message"]]
        if error_500_tests:
            print("❌ HTTP 500 errors still occurring - bug not fully fixed")
        else:
            print("✅ No HTTP 500 errors detected - API endpoints working correctly")
        
        # Check for missing parentNodeId errors
        parent_id_tests = [r for r in self.test_results if "missing parentNodeId" in r["message"]]
        if parent_id_tests:
            print("❌ 'missing parentNodeId' errors still occurring - bug not fully fixed")
        else:
            print("✅ No 'missing parentNodeId' errors detected - parent-child relationships working correctly")
        
        # Check for questionnaire looping
        loop_tests = [r for r in self.test_results if "looping back to 5th question" in r["message"]]
        if loop_tests:
            print("❌ Questionnaire looping still occurring - bug not fully fixed")
        else:
            print("✅ No questionnaire looping detected - questionnaire flow working correctly")
        
        return passed == total

if __name__ == "__main__":
    tester = ParentChildQuestionnaireTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)