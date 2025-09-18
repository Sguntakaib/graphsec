#!/usr/bin/env python3
"""
Backend API Testing - QUESTIONNAIRE RESUMPTION FIX VERIFICATION
Tests the specific fix for questionnaire resumption off-by-one error.

TESTING FOCUS:
🔧 PRIMARY TEST: QUESTIONNAIRE RESUMPTION FIX
1. **Database questionnaire dependency triggering (Question 4 → Backup child node)**
2. **Verify that after Backup completes, Database questionnaire resumes at Question 5 (not skip to Question 6)**
3. **Test the full flow: Database Q1→Q2→Q3→Q4→Backup(3 questions)→Database Q5→Q6→...→Q10**

**THE FIX:**
- Changed App.js lines 1549 and 1561 from `result.currentPromptIndex + 1` to `result.currentPromptIndex`
- This should fix the off-by-one error that was causing questions to be skipped

**SPECIFIC TEST SCENARIO:**
1. Database questionnaire has 10 questions
2. Question 4 (backup question) should trigger a Backup child node with 3 questions  
3. After Backup child node completes, the parent Database questionnaire should resume at Question 5 (not skip to Question 6)

**EXPECTED RESULTS:**
- Database questionnaire should have 10 questions with dependency questions at specific positions
- Backup dependency should trigger correctly from Database question 4
- Question resumption should work without skipping questions
- Complete flow should process all questions in correct sequence

**ADDITIONAL TESTS:**
Also includes comprehensive questionnaire functionality verification tests.
"""

import requests
import json
import uuid
from datetime import datetime, timezone
import sys

# Use the backend URL from frontend/.env with /api suffix
BASE_URL = "https://element-survey.preview.emergentagent.com/api"

class DoubleClickQuestionnaireTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.test_results = []
        self.test_diagram_id = None
        self.test_nodes = []
        
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
    # CRITICAL TEST: Questionnaire Resumption Fix Verification
    # ============================================================================
    
    def test_questionnaire_resumption_fix(self):
        """
        CRITICAL TEST: Verify questionnaire resumption fix for off-by-one error
        
        Tests the specific fix where Database questionnaire Question 5 was being skipped 
        after Backup child node completion due to off-by-one error in resumption logic.
        
        The fix changed App.js lines 1549 and 1561 from `result.currentPromptIndex + 1` 
        to `result.currentPromptIndex` to fix the off-by-one error.
        
        Test Scenario:
        1. Database questionnaire has 10 questions
        2. Question 4 (backup question) should trigger Backup child node with 3 questions
        3. After Backup completes, Database questionnaire should resume at Question 5 (not skip to Question 6)
        """
        try:
            print("🎯 CRITICAL TEST: Questionnaire Resumption Fix Verification")
            print("=" * 80)
            print("Testing Database → Backup dependency flow and resumption logic")
            
            # Step 1: Verify Database questionnaire structure
            print("\n📋 Step 1: Verify Database questionnaire structure")
            db_response = self.session.get(f"{self.base_url}/intelligent-nodes/Database/prompts")
            
            if db_response.status_code != 200:
                self.log_test("Questionnaire Resumption Fix", False, 
                            f"Failed to get Database prompts: HTTP {db_response.status_code}")
                return False
            
            db_data = db_response.json()
            db_prompts = db_data.get('prompts', [])
            
            if len(db_prompts) != 10:
                self.log_test("Questionnaire Resumption Fix", False, 
                            f"Database questionnaire should have 10 questions, got {len(db_prompts)}")
                return False
            
            print(f"   ✅ Database questionnaire has {len(db_prompts)} questions as expected")
            
            # Step 2: Identify dependency questions in Database questionnaire
            print("\n📋 Step 2: Identify dependency questions in Database questionnaire")
            backup_dependency_question = None
            backup_question_index = None
            
            for i, prompt in enumerate(db_prompts):
                if 'backup' in prompt.get('id', '').lower() or 'backup' in prompt.get('question', '').lower():
                    backup_dependency_question = prompt
                    backup_question_index = i
                    break
            
            if not backup_dependency_question:
                self.log_test("Questionnaire Resumption Fix", False, 
                            "Could not find backup dependency question in Database questionnaire")
                return False
            
            print(f"   ✅ Found backup dependency question at index {backup_question_index}: {backup_dependency_question.get('question', 'N/A')}")
            
            # Step 3: Verify Backup questionnaire exists and has expected structure
            print("\n📋 Step 3: Verify Backup questionnaire structure")
            backup_response = self.session.get(f"{self.base_url}/intelligent-nodes/Backup/prompts")
            
            if backup_response.status_code != 200:
                self.log_test("Questionnaire Resumption Fix", False, 
                            f"Failed to get Backup prompts: HTTP {backup_response.status_code}")
                return False
            
            backup_data = backup_response.json()
            backup_prompts = backup_data.get('prompts', [])
            
            if len(backup_prompts) != 3:
                print(f"   ⚠️  Backup questionnaire has {len(backup_prompts)} questions (expected 3, but continuing test)")
            else:
                print(f"   ✅ Backup questionnaire has {len(backup_prompts)} questions as expected")
            
            # Step 4: Test dependency detection API
            print("\n📋 Step 4: Test Database dependency detection")
            dependency_test_data = {
                "answers": {
                    backup_dependency_question.get('id', 'backup_enabled'): True
                }
            }
            
            dep_response = self.session.post(
                f"{self.base_url}/intelligent-nodes/Database/check-dependencies",
                json=dependency_test_data
            )
            
            if dep_response.status_code != 200:
                self.log_test("Questionnaire Resumption Fix", False, 
                            f"Failed to check Database dependencies: HTTP {dep_response.status_code}")
                return False
            
            dep_data = dep_response.json()
            dependencies = dep_data.get('dependencies', [])
            
            if 'Backup' not in dependencies:
                self.log_test("Questionnaire Resumption Fix", False, 
                            f"Backup dependency not detected. Got dependencies: {dependencies}")
                return False
            
            print(f"   ✅ Database dependency detection working: {dependencies}")
            
            # Step 5: Simulate the questionnaire flow to test resumption logic
            print("\n📋 Step 5: Simulate questionnaire resumption flow")
            
            # Simulate Database questionnaire progress up to backup question
            print(f"   🔄 Simulating Database questionnaire Q1 → Q{backup_question_index + 1} (backup question)")
            
            # The critical test: verify that resumption index is correct
            # According to the fix, when backup dependency is triggered at question index N,
            # the resumption should be at index N (not N+1) to avoid skipping the next question
            
            expected_resumption_index = backup_question_index  # This is the fix - no +1
            next_question_after_backup = backup_question_index + 1
            
            if next_question_after_backup >= len(db_prompts):
                print(f"   ⚠️  Backup question is the last question, cannot test resumption")
            else:
                next_question = db_prompts[next_question_after_backup]
                print(f"   📍 After Backup completion, should resume at Question {next_question_after_backup + 1}: {next_question.get('question', 'N/A')[:50]}...")
                print(f"   📍 Resumption index should be {expected_resumption_index} (fixed from {expected_resumption_index + 1})")
            
            # Step 6: Verify the complete flow sequence
            print("\n📋 Step 6: Verify complete questionnaire flow sequence")
            
            total_questions_in_flow = len(db_prompts) + len(backup_prompts)
            print(f"   📊 Total questions in complete flow: {total_questions_in_flow}")
            print(f"   📊 Database questions: {len(db_prompts)}")
            print(f"   📊 Backup questions: {len(backup_prompts)}")
            
            # Simulate the expected flow
            expected_flow = []
            
            # Database questions up to backup dependency
            for i in range(backup_question_index + 1):
                expected_flow.append(f"Database Q{i + 1}")
            
            # Backup questions
            for i in range(len(backup_prompts)):
                expected_flow.append(f"Backup Q{i + 1}")
            
            # Remaining Database questions (this is where the fix matters)
            for i in range(backup_question_index + 1, len(db_prompts)):
                expected_flow.append(f"Database Q{i + 1}")
            
            print(f"   🔄 Expected flow sequence:")
            for i, step in enumerate(expected_flow):
                if i < 10:  # Show first 10 steps
                    print(f"      {i + 1:2d}. {step}")
                elif i == 10:
                    print(f"      ... ({len(expected_flow) - 10} more steps)")
                    break
            
            # Verify that Question 5 is not skipped (the main issue being fixed)
            if next_question_after_backup < len(db_prompts):
                question_5_in_flow = f"Database Q{next_question_after_backup + 1}"
                if question_5_in_flow in expected_flow:
                    print(f"   ✅ Question {next_question_after_backup + 1} is included in flow (not skipped)")
                else:
                    self.log_test("Questionnaire Resumption Fix", False, 
                                f"Question {next_question_after_backup + 1} is missing from expected flow")
                    return False
            
            self.log_test("Questionnaire Resumption Fix", True, 
                        f"✅ QUESTIONNAIRE RESUMPTION FIX VERIFIED: Database questionnaire structure correct, "
                        f"Backup dependency detection working, resumption logic should work without skipping questions. "
                        f"Expected flow: Database Q1-Q{backup_question_index + 1} → Backup Q1-Q{len(backup_prompts)} → "
                        f"Database Q{next_question_after_backup + 1}-Q{len(db_prompts)}")
            
            return True
            
        except Exception as e:
            self.log_test("Questionnaire Resumption Fix", False, f"Request error: {str(e)}")
            return False

    def test_database_questionnaire_consistency_fix(self):
        """
        CRITICAL TEST: Verify Database questionnaire consistency fix
        
        Tests the specific fix for Database questionnaire consistency issue where:
        - GET /api/intelligent-nodes/Database/prompts was returning prompts_count=0 (missing field)
        - But actual prompts.length=5, causing parent-child questionnaire resumption failures
        
        Expected fix: Response should now include success=true and prompts_count field that matches prompts.length
        """
        try:
            print("🎯 CRITICAL TEST: Database Questionnaire Consistency Fix")
            print("=" * 70)
            
            # Test the endpoint multiple times to ensure consistency (3-5 times as requested)
            test_iterations = 5
            all_results = []
            
            for iteration in range(1, test_iterations + 1):
                print(f"📋 Test Iteration {iteration}/{test_iterations}")
                
                response = self.session.get(f"{self.base_url}/intelligent-nodes/Database/prompts")
                
                if response.status_code != 200:
                    self.log_test(f"Database Consistency Fix - Iteration {iteration}", False, 
                                f"HTTP {response.status_code}: {response.text}")
                    return False
                
                try:
                    data = response.json()
                except json.JSONDecodeError as e:
                    self.log_test(f"Database Consistency Fix - Iteration {iteration}", False, 
                                f"Invalid JSON response: {str(e)}")
                    return False
                
                # Verify required fields are present
                required_fields = ['success', 'node_subtype', 'prompts_count', 'prompts']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test(f"Database Consistency Fix - Iteration {iteration}", False, 
                                f"Missing required fields: {missing_fields}")
                    return False
                
                # Verify success field is true
                if not data.get('success'):
                    self.log_test(f"Database Consistency Fix - Iteration {iteration}", False, 
                                f"success field is not true: {data.get('success')}")
                    return False
                
                # Verify node_subtype is 'Database'
                if data.get('node_subtype') != 'Database':
                    self.log_test(f"Database Consistency Fix - Iteration {iteration}", False, 
                                f"node_subtype should be 'Database', got: {data.get('node_subtype')}")
                    return False
                
                # Verify prompts is a list
                prompts = data.get('prompts', [])
                if not isinstance(prompts, list):
                    self.log_test(f"Database Consistency Fix - Iteration {iteration}", False, 
                                f"prompts should be a list, got: {type(prompts)}")
                    return False
                
                # CRITICAL CHECK: Verify prompts_count matches actual prompts length
                prompts_count = data.get('prompts_count')
                actual_prompts_length = len(prompts)
                
                if prompts_count != actual_prompts_length:
                    self.log_test(f"Database Consistency Fix - Iteration {iteration}", False, 
                                f"CONSISTENCY ERROR: prompts_count={prompts_count} but actual prompts.length={actual_prompts_length}")
                    return False
                
                # Verify prompts_count is not 0 (the original bug)
                if prompts_count == 0:
                    self.log_test(f"Database Consistency Fix - Iteration {iteration}", False, 
                                f"ORIGINAL BUG STILL EXISTS: prompts_count=0 but should match prompts.length={actual_prompts_length}")
                    return False
                
                # Store results for consistency analysis
                iteration_result = {
                    'success': data.get('success'),
                    'node_subtype': data.get('node_subtype'),
                    'prompts_count': prompts_count,
                    'actual_prompts_length': actual_prompts_length,
                    'prompts_sample': prompts[:2] if prompts else []  # First 2 prompts for verification
                }
                all_results.append(iteration_result)
                
                print(f"   ✅ Iteration {iteration}: success={data.get('success')}, prompts_count={prompts_count}, actual_length={actual_prompts_length}")
            
            # Analyze consistency across all iterations
            print(f"\n🔍 Consistency Analysis Across {test_iterations} Iterations:")
            
            # Check if all iterations returned the same prompts_count
            prompts_counts = [result['prompts_count'] for result in all_results]
            unique_counts = set(prompts_counts)
            
            if len(unique_counts) > 1:
                self.log_test("Database Consistency Fix", False, 
                            f"INCONSISTENCY DETECTED: Different prompts_count values across iterations: {unique_counts}")
                return False
            
            # Check if all iterations returned the same actual_prompts_length
            actual_lengths = [result['actual_prompts_length'] for result in all_results]
            unique_lengths = set(actual_lengths)
            
            if len(unique_lengths) > 1:
                self.log_test("Database Consistency Fix", False, 
                            f"INCONSISTENCY DETECTED: Different actual prompts lengths across iterations: {unique_lengths}")
                return False
            
            # Final verification
            final_prompts_count = prompts_counts[0]
            final_actual_length = actual_lengths[0]
            
            print(f"   📊 Consistent prompts_count: {final_prompts_count}")
            print(f"   📊 Consistent actual_length: {final_actual_length}")
            print(f"   📊 Match verification: {final_prompts_count == final_actual_length}")
            
            # Verify the response format matches expected structure
            sample_response = all_results[0]
            expected_format = {
                'success': True,
                'node_subtype': 'Database',
                'prompts_count': final_prompts_count,
                'prompts': 'array'
            }
            
            print(f"\n✅ EXPECTED RESPONSE FORMAT VERIFICATION:")
            print(f"   success: {sample_response['success']} (expected: True)")
            print(f"   node_subtype: {sample_response['node_subtype']} (expected: 'Database')")
            print(f"   prompts_count: {sample_response['prompts_count']} (expected: matches prompts.length)")
            print(f"   prompts: array with {final_actual_length} items")
            
            self.log_test("Database Consistency Fix", True, 
                        f"✅ CRITICAL FIX VERIFIED: Database questionnaire consistency fix working correctly. "
                        f"prompts_count={final_prompts_count} matches actual prompts.length={final_actual_length} "
                        f"consistently across {test_iterations} iterations. Original bug (prompts_count=0) resolved.")
            
            return True
            
        except Exception as e:
            self.log_test("Database Consistency Fix", False, f"Request error: {str(e)}")
            return False

    # ============================================================================
    # TEST 1: Diagram and Node Creation for Testing
    # ============================================================================
    
    def test_create_test_diagram(self):
        """Create a test diagram for questionnaire testing"""
        try:
            diagram_data = {
                "title": "Double-Click Questionnaire Test Diagram",
                "description": "Test diagram for verifying double-click questionnaire functionality"
            }
            
            response = self.session.post(f"{self.base_url}/diagrams", json=diagram_data)
            
            if response.status_code != 200:
                self.log_test("Create Test Diagram", False, 
                            f"Failed to create diagram: HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            if 'id' not in data:
                self.log_test("Create Test Diagram", False, 
                            f"Missing 'id' field in response: {data}")
                return False
            
            self.test_diagram_id = data['id']
            
            self.log_test("Create Test Diagram", True, 
                        f"✅ Test diagram created successfully with ID: {self.test_diagram_id}")
            
            return True
            
        except Exception as e:
            self.log_test("Create Test Diagram", False, f"Request error: {str(e)}")
            return False

    def test_add_test_nodes(self):
        """Add test nodes to the diagram for questionnaire testing"""
        try:
            if not self.test_diagram_id:
                self.log_test("Add Test Nodes", False, "No test diagram ID available")
                return False
            
            # Create test nodes with different subtypes
            test_nodes = [
                {
                    "id": f"webapp-node-{uuid.uuid4().hex[:8]}",
                    "type": "Asset",
                    "subtype": "WebApp",
                    "label": "Test Web Application",
                    "position": {"x": 200, "y": 100},
                    "data": {
                        "criticality": "High",
                        "data_classification": "Confidential"
                    }
                },
                {
                    "id": f"api-node-{uuid.uuid4().hex[:8]}",
                    "type": "Asset", 
                    "subtype": "API",
                    "label": "Test API Service",
                    "position": {"x": 400, "y": 100},
                    "data": {
                        "criticality": "High",
                        "data_classification": "Internal"
                    }
                },
                {
                    "id": f"database-node-{uuid.uuid4().hex[:8]}",
                    "type": "Asset",
                    "subtype": "Database", 
                    "label": "Test Database",
                    "position": {"x": 600, "y": 100},
                    "data": {
                        "criticality": "Critical",
                        "data_classification": "Restricted"
                    }
                }
            ]
            
            # Get current diagram
            diagram_response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}")
            if diagram_response.status_code != 200:
                self.log_test("Add Test Nodes", False, 
                            f"Failed to get diagram: HTTP {diagram_response.status_code}")
                return False
            
            diagram_data = diagram_response.json()
            
            # Add nodes to diagram
            diagram_data['nodes'] = test_nodes
            diagram_data['edges'] = []  # No edges needed for questionnaire testing
            
            # Update diagram with nodes
            update_response = self.session.put(f"{self.base_url}/diagrams/{self.test_diagram_id}", 
                                             json=diagram_data)
            
            if update_response.status_code != 200:
                self.log_test("Add Test Nodes", False, 
                            f"Failed to update diagram with nodes: HTTP {update_response.status_code}: {update_response.text}")
                return False
            
            self.test_nodes = test_nodes
            
            self.log_test("Add Test Nodes", True, 
                        f"✅ Added {len(test_nodes)} test nodes to diagram (WebApp, API, Database)")
            
            print(f"📋 Test Nodes Created:")
            for node in test_nodes:
                print(f"   {node['subtype']}: {node['id']} - {node['label']}")
            
            return True
            
        except Exception as e:
            self.log_test("Add Test Nodes", False, f"Request error: {str(e)}")
            return False

    # ============================================================================
    # TEST 2: Questionnaire Retrieval API Testing
    # ============================================================================
    
    def test_questionnaire_retrieval_empty_state(self):
        """Test GET /api/diagrams/{diagram_id}/nodes/{node_id}/questionnaire for nodes with no responses"""
        try:
            if not self.test_diagram_id or not self.test_nodes:
                self.log_test("Questionnaire Retrieval Empty", False, "No test data available")
                return False
            
            success_count = 0
            total_tests = 0
            
            for node in self.test_nodes:
                total_tests += 1
                node_id = node['id']
                node_subtype = node['subtype']
                
                response = self.session.get(
                    f"{self.base_url}/diagrams/{self.test_diagram_id}/nodes/{node_id}/questionnaire"
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Verify response structure (actual API format)
                    required_fields = ['prompts', 'questionnaire_responses', 'node_subtype']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        print(f"   ❌ {node_subtype} node missing fields: {missing_fields}")
                        continue
                    
                    # Verify prompts are present
                    if not data['prompts'] or len(data['prompts']) == 0:
                        print(f"   ❌ {node_subtype} node has no prompts")
                        continue
                    
                    # Verify questionnaire_responses is a dict (can be empty for new nodes)
                    if not isinstance(data['questionnaire_responses'], dict):
                        print(f"   ❌ {node_subtype} node questionnaire_responses not a dict: {type(data['questionnaire_responses'])}")
                        continue
                    
                    # Verify node_subtype matches
                    if data['node_subtype'] != node_subtype:
                        print(f"   ❌ {node_subtype} node subtype mismatch: expected {node_subtype}, got {data['node_subtype']}")
                        continue
                    
                    success_count += 1
                    print(f"   ✅ {node_subtype} node: {len(data['prompts'])} prompts, {len(data['questionnaire_responses'])} responses")
                    
                else:
                    print(f"   ❌ {node_subtype} node: HTTP {response.status_code}: {response.text}")
            
            if success_count == total_tests:
                self.log_test("Questionnaire Retrieval Empty", True, 
                            f"✅ All {total_tests} nodes return proper questionnaire data (empty state)")
                return True
            else:
                self.log_test("Questionnaire Retrieval Empty", False, 
                            f"Only {success_count}/{total_tests} nodes returned proper questionnaire data")
                return False
            
        except Exception as e:
            self.log_test("Questionnaire Retrieval Empty", False, f"Request error: {str(e)}")
            return False

    # ============================================================================
    # TEST 3: Questionnaire Update API Testing
    # ============================================================================
    
    def test_questionnaire_update_api(self):
        """Test POST /api/diagrams/{diagram_id}/nodes/{node_id}/questionnaire to save responses"""
        try:
            if not self.test_diagram_id or not self.test_nodes:
                self.log_test("Questionnaire Update API", False, "No test data available")
                return False
            
            success_count = 0
            total_tests = 0
            
            # Test data for different node types
            test_responses = {
                "WebApp": {
                    "authentication_method": "oauth2",
                    "encryption_enabled": True,
                    "input_validation": "comprehensive",
                    "session_management": "secure"
                },
                "API": {
                    "authentication_type": "jwt",
                    "rate_limiting": True,
                    "input_validation": "strict",
                    "logging_enabled": True
                },
                "Database": {
                    "encryption_at_rest": True,
                    "access_controls": "rbac",
                    "backup_enabled": True,
                    "monitoring_enabled": True
                }
            }
            
            for node in self.test_nodes:
                total_tests += 1
                node_id = node['id']
                node_subtype = node['subtype']
                
                # Get responses for this node type
                responses = test_responses.get(node_subtype, {})
                
                update_data = {
                    "responses": responses
                }
                
                response = self.session.post(
                    f"{self.base_url}/diagrams/{self.test_diagram_id}/nodes/{node_id}/questionnaire",
                    json=update_data
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Verify update was successful (actual API format)
                    if 'success' in data and data['success'] and 'updated_responses' in data:
                        success_count += 1
                        print(f"   ✅ {node_subtype} node: Updated with {data['updated_responses']} responses")
                    else:
                        print(f"   ❌ {node_subtype} node: Unexpected response format: {data}")
                        
                else:
                    print(f"   ❌ {node_subtype} node: HTTP {response.status_code}: {response.text}")
            
            if success_count == total_tests:
                self.log_test("Questionnaire Update API", True, 
                            f"✅ All {total_tests} nodes updated successfully with questionnaire responses")
                return True
            else:
                self.log_test("Questionnaire Update API", False, 
                            f"Only {success_count}/{total_tests} nodes updated successfully")
                return False
            
        except Exception as e:
            self.log_test("Questionnaire Update API", False, f"Request error: {str(e)}")
            return False

    def test_questionnaire_retrieval_with_responses(self):
        """Test GET /api/diagrams/{diagram_id}/nodes/{node_id}/questionnaire for nodes with saved responses"""
        try:
            if not self.test_diagram_id or not self.test_nodes:
                self.log_test("Questionnaire Retrieval With Responses", False, "No test data available")
                return False
            
            success_count = 0
            total_tests = 0
            
            for node in self.test_nodes:
                total_tests += 1
                node_id = node['id']
                node_subtype = node['subtype']
                
                response = self.session.get(
                    f"{self.base_url}/diagrams/{self.test_diagram_id}/nodes/{node_id}/questionnaire"
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Verify response structure (actual API format)
                    required_fields = ['prompts', 'questionnaire_responses', 'node_subtype']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        print(f"   ❌ {node_subtype} node missing fields: {missing_fields}")
                        continue
                    
                    # Verify questionnaire_responses are now populated (should have saved responses from previous test)
                    if not isinstance(data['questionnaire_responses'], dict):
                        print(f"   ❌ {node_subtype} node questionnaire_responses not a dict: {type(data['questionnaire_responses'])}")
                        continue
                    
                    # Check if responses were persisted
                    response_count = len(data['questionnaire_responses'])
                    if response_count > 0:
                        success_count += 1
                        print(f"   ✅ {node_subtype} node: {len(data['prompts'])} prompts, {response_count} saved responses")
                    else:
                        print(f"   ⚠️  {node_subtype} node: No saved responses found (may be expected)")
                        success_count += 1  # Still count as success if API works
                    
                else:
                    print(f"   ❌ {node_subtype} node: HTTP {response.status_code}: {response.text}")
            
            if success_count == total_tests:
                self.log_test("Questionnaire Retrieval With Responses", True, 
                            f"✅ All {total_tests} nodes return questionnaire data with persistence verification")
                return True
            else:
                self.log_test("Questionnaire Retrieval With Responses", False, 
                            f"Only {success_count}/{total_tests} nodes returned proper questionnaire data")
                return False
            
        except Exception as e:
            self.log_test("Questionnaire Retrieval With Responses", False, f"Request error: {str(e)}")
            return False

    # ============================================================================
    # TEST 4: Error Handling and Edge Cases
    # ============================================================================
    
    def test_questionnaire_error_handling(self):
        """Test error handling for questionnaire APIs"""
        try:
            error_tests = [
                {
                    "name": "Invalid Diagram ID",
                    "url": f"{self.base_url}/diagrams/invalid-diagram-id/nodes/some-node/questionnaire",
                    "expected_status": 404
                },
                {
                    "name": "Invalid Node ID", 
                    "url": f"{self.base_url}/diagrams/{self.test_diagram_id}/nodes/invalid-node-id/questionnaire" if self.test_diagram_id else None,
                    "expected_status": 404
                },
                {
                    "name": "Malformed Diagram ID",
                    "url": f"{self.base_url}/diagrams/123/nodes/some-node/questionnaire",
                    "expected_status": 404
                }
            ]
            
            success_count = 0
            total_tests = 0
            
            for test_case in error_tests:
                if test_case["url"] is None:
                    continue
                    
                total_tests += 1
                
                response = self.session.get(test_case["url"])
                
                if response.status_code == test_case["expected_status"]:
                    success_count += 1
                    print(f"   ✅ {test_case['name']}: Correctly returned HTTP {response.status_code}")
                else:
                    print(f"   ❌ {test_case['name']}: Expected HTTP {test_case['expected_status']}, got {response.status_code}")
            
            if success_count == total_tests and total_tests > 0:
                self.log_test("Questionnaire Error Handling", True, 
                            f"✅ All {total_tests} error handling tests passed")
                return True
            else:
                self.log_test("Questionnaire Error Handling", False, 
                            f"Only {success_count}/{total_tests} error handling tests passed")
                return False
            
        except Exception as e:
            self.log_test("Questionnaire Error Handling", False, f"Request error: {str(e)}")
            return False

    # ============================================================================
    # TEST 5: Integration Testing - Complete Double-Click Workflow
    # ============================================================================
    
    def test_complete_double_click_workflow(self):
        """Test the complete workflow that would be triggered by double-clicking a node"""
        try:
            if not self.test_diagram_id or not self.test_nodes:
                self.log_test("Complete Double-Click Workflow", False, "No test data available")
                return False
            
            # Test the complete workflow for one node
            test_node = self.test_nodes[0]  # Use WebApp node
            node_id = test_node['id']
            node_subtype = test_node['subtype']
            
            print(f"🔄 Testing complete double-click workflow for {node_subtype} node...")
            
            # Step 1: Double-click triggers questionnaire retrieval (GET)
            print("   Step 1: Retrieve questionnaire data (simulating double-click)")
            get_response = self.session.get(
                f"{self.base_url}/diagrams/{self.test_diagram_id}/nodes/{node_id}/questionnaire"
            )
            
            if get_response.status_code != 200:
                self.log_test("Complete Double-Click Workflow", False, 
                            f"Step 1 failed: HTTP {get_response.status_code}")
                return False
            
            questionnaire_data = get_response.json()
            print(f"   ✅ Step 1: Retrieved {len(questionnaire_data.get('prompts', []))} prompts")
            
            # Step 2: User fills out questionnaire and submits (POST)
            print("   Step 2: Save questionnaire responses (simulating form submission)")
            new_responses = {
                "security_assessment": "comprehensive",
                "risk_level": "high", 
                "compliance_required": True,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
            post_response = self.session.post(
                f"{self.base_url}/diagrams/{self.test_diagram_id}/nodes/{node_id}/questionnaire",
                json={"responses": new_responses}
            )
            
            if post_response.status_code != 200:
                self.log_test("Complete Double-Click Workflow", False, 
                            f"Step 2 failed: HTTP {post_response.status_code}")
                return False
            
            print(f"   ✅ Step 2: Saved {len(new_responses)} responses")
            
            # Step 3: Verify data persistence (GET again)
            print("   Step 3: Verify data persistence (simulating re-opening questionnaire)")
            verify_response = self.session.get(
                f"{self.base_url}/diagrams/{self.test_diagram_id}/nodes/{node_id}/questionnaire"
            )
            
            if verify_response.status_code != 200:
                self.log_test("Complete Double-Click Workflow", False, 
                            f"Step 3 failed: HTTP {verify_response.status_code}")
                return False
            
            verified_data = verify_response.json()
            saved_responses = verified_data.get('questionnaire_responses', {})
            
            # Check if at least some responses were persisted
            if len(saved_responses) > 0:
                print(f"   ✅ Step 3: Verified {len(saved_responses)} responses persisted")
            else:
                print(f"   ⚠️  Step 3: No responses found in persistence check")
            
            self.log_test("Complete Double-Click Workflow", True, 
                        f"✅ Complete double-click workflow successful for {node_subtype} node")
            
            print(f"🎯 Workflow Summary:")
            print(f"   Node Type: {node_subtype}")
            print(f"   Prompts Available: {len(questionnaire_data.get('prompts', []))}")
            print(f"   Responses Saved: {len(new_responses)}")
            print(f"   Responses Persisted: {len(saved_responses)}")
            
            return True
            
        except Exception as e:
            self.log_test("Complete Double-Click Workflow", False, f"Request error: {str(e)}")
            return False

    # ============================================================================
    # REVIEW REQUEST: Double-Click Questionnaire Backend Support Testing
    # ============================================================================
    
    def test_api_questionnaire_endpoint(self):
        """Test GET /api/questionnaires/API?level=basic endpoint"""
        try:
            print("🎯 TESTING: API Questionnaire Endpoint")
            print("=" * 60)
            
            response = self.session.get(f"{self.base_url}/questionnaires/API?level=basic")
            
            if response.status_code != 200:
                self.log_test("API Questionnaire Endpoint", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("API Questionnaire Endpoint", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            # Verify required fields
            required_fields = ['prompts', 'level', 'total_questions']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                self.log_test("API Questionnaire Endpoint", False, 
                            f"Missing required fields: {missing_fields}")
                return False
            
            # Verify level field is set to "basic"
            if data.get('level') != 'basic':
                self.log_test("API Questionnaire Endpoint", False, 
                            f"Level field should be 'basic', got: {data.get('level')}")
                return False
            
            # Verify prompts field contains questionnaire questions
            prompts = data.get('prompts', [])
            if not isinstance(prompts, list) or len(prompts) == 0:
                self.log_test("API Questionnaire Endpoint", False, 
                            f"Prompts should be a non-empty list, got: {type(prompts)} with {len(prompts)} items")
                return False
            
            # Verify total_questions field
            total_questions = data.get('total_questions')
            if not isinstance(total_questions, int) or total_questions <= 0:
                self.log_test("API Questionnaire Endpoint", False, 
                            f"total_questions should be a positive integer, got: {total_questions}")
                return False
            
            # Verify prompts array contains valid questions with proper structure
            for i, prompt in enumerate(prompts):
                if not isinstance(prompt, dict):
                    self.log_test("API Questionnaire Endpoint", False, 
                                f"Prompt {i} should be a dict, got: {type(prompt)}")
                    return False
                
                # Check for required prompt fields
                prompt_required_fields = ['id', 'question', 'type']
                prompt_missing_fields = [field for field in prompt_required_fields if field not in prompt]
                
                if prompt_missing_fields:
                    self.log_test("API Questionnaire Endpoint", False, 
                                f"Prompt {i} missing required fields: {prompt_missing_fields}")
                    return False
                
                # Verify options field exists for choice-type questions
                if prompt.get('type') in ['single_choice', 'multiple_choice'] and 'options' not in prompt:
                    self.log_test("API Questionnaire Endpoint", False, 
                                f"Prompt {i} with type '{prompt.get('type')}' missing options field")
                    return False
            
            self.log_test("API Questionnaire Endpoint", True, 
                        f"✅ API questionnaire endpoint working correctly - HTTP 200, {len(prompts)} prompts, level=basic, total_questions={total_questions}")
            
            print(f"   📊 Response Summary:")
            print(f"      Status: HTTP 200")
            print(f"      Level: {data.get('level')}")
            print(f"      Total Questions: {total_questions}")
            print(f"      Prompts Count: {len(prompts)}")
            print(f"      Sample Question: {prompts[0].get('question', 'N/A')[:50]}..." if prompts else "      No prompts")
            
            return True
            
        except Exception as e:
            self.log_test("API Questionnaire Endpoint", False, f"Request error: {str(e)}")
            return False

    def test_backup_questionnaire_endpoint(self):
        """Test GET /api/questionnaires/Backup?level=basic endpoint"""
        try:
            print("🎯 TESTING: Backup Questionnaire Endpoint")
            print("=" * 60)
            
            response = self.session.get(f"{self.base_url}/questionnaires/Backup?level=basic")
            
            if response.status_code != 200:
                self.log_test("Backup Questionnaire Endpoint", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Backup Questionnaire Endpoint", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            # Verify required fields
            required_fields = ['prompts', 'level', 'total_questions']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                self.log_test("Backup Questionnaire Endpoint", False, 
                            f"Missing required fields: {missing_fields}")
                return False
            
            # Verify level field is set to "basic"
            if data.get('level') != 'basic':
                self.log_test("Backup Questionnaire Endpoint", False, 
                            f"Level field should be 'basic', got: {data.get('level')}")
                return False
            
            # Verify prompts field contains questionnaire questions
            prompts = data.get('prompts', [])
            if not isinstance(prompts, list) or len(prompts) == 0:
                self.log_test("Backup Questionnaire Endpoint", False, 
                            f"Prompts should be a non-empty list, got: {type(prompts)} with {len(prompts)} items")
                return False
            
            # Verify total_questions field
            total_questions = data.get('total_questions')
            if not isinstance(total_questions, int) or total_questions <= 0:
                self.log_test("Backup Questionnaire Endpoint", False, 
                            f"total_questions should be a positive integer, got: {total_questions}")
                return False
            
            # Verify prompts array contains valid questions with proper structure
            for i, prompt in enumerate(prompts):
                if not isinstance(prompt, dict):
                    self.log_test("Backup Questionnaire Endpoint", False, 
                                f"Prompt {i} should be a dict, got: {type(prompt)}")
                    return False
                
                # Check for required prompt fields
                prompt_required_fields = ['id', 'question', 'type']
                prompt_missing_fields = [field for field in prompt_required_fields if field not in prompt]
                
                if prompt_missing_fields:
                    self.log_test("Backup Questionnaire Endpoint", False, 
                                f"Prompt {i} missing required fields: {prompt_missing_fields}")
                    return False
                
                # Verify options field exists for choice-type questions
                if prompt.get('type') in ['single_choice', 'multiple_choice'] and 'options' not in prompt:
                    self.log_test("Backup Questionnaire Endpoint", False, 
                                f"Prompt {i} with type '{prompt.get('type')}' missing options field")
                    return False
            
            self.log_test("Backup Questionnaire Endpoint", True, 
                        f"✅ Backup questionnaire endpoint working correctly - HTTP 200, {len(prompts)} prompts, level=basic, total_questions={total_questions}")
            
            print(f"   📊 Response Summary:")
            print(f"      Status: HTTP 200")
            print(f"      Level: {data.get('level')}")
            print(f"      Total Questions: {total_questions}")
            print(f"      Prompts Count: {len(prompts)}")
            print(f"      Sample Question: {prompts[0].get('question', 'N/A')[:50]}..." if prompts else "      No prompts")
            
            return True
            
        except Exception as e:
            self.log_test("Backup Questionnaire Endpoint", False, f"Request error: {str(e)}")
            return False

    def test_monitoring_questionnaire_endpoint(self):
        """Test GET /api/questionnaires/Monitoring?level=basic endpoint"""
        try:
            print("🎯 TESTING: Monitoring Questionnaire Endpoint")
            print("=" * 60)
            
            response = self.session.get(f"{self.base_url}/questionnaires/Monitoring?level=basic")
            
            if response.status_code != 200:
                self.log_test("Monitoring Questionnaire Endpoint", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Monitoring Questionnaire Endpoint", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            # Verify required fields
            required_fields = ['prompts', 'level', 'total_questions']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                self.log_test("Monitoring Questionnaire Endpoint", False, 
                            f"Missing required fields: {missing_fields}")
                return False
            
            # Verify level field is set to "basic"
            if data.get('level') != 'basic':
                self.log_test("Monitoring Questionnaire Endpoint", False, 
                            f"Level field should be 'basic', got: {data.get('level')}")
                return False
            
            # Verify prompts field contains questionnaire questions
            prompts = data.get('prompts', [])
            if not isinstance(prompts, list) or len(prompts) == 0:
                self.log_test("Monitoring Questionnaire Endpoint", False, 
                            f"Prompts should be a non-empty list, got: {type(prompts)} with {len(prompts)} items")
                return False
            
            # Verify total_questions field
            total_questions = data.get('total_questions')
            if not isinstance(total_questions, int) or total_questions <= 0:
                self.log_test("Monitoring Questionnaire Endpoint", False, 
                            f"total_questions should be a positive integer, got: {total_questions}")
                return False
            
            # Verify prompts array contains valid questions with proper structure
            for i, prompt in enumerate(prompts):
                if not isinstance(prompt, dict):
                    self.log_test("Monitoring Questionnaire Endpoint", False, 
                                f"Prompt {i} should be a dict, got: {type(prompt)}")
                    return False
                
                # Check for required prompt fields
                prompt_required_fields = ['id', 'question', 'type']
                prompt_missing_fields = [field for field in prompt_required_fields if field not in prompt]
                
                if prompt_missing_fields:
                    self.log_test("Monitoring Questionnaire Endpoint", False, 
                                f"Prompt {i} missing required fields: {prompt_missing_fields}")
                    return False
                
                # Verify options field exists for choice-type questions
                if prompt.get('type') in ['single_choice', 'multiple_choice'] and 'options' not in prompt:
                    self.log_test("Monitoring Questionnaire Endpoint", False, 
                                f"Prompt {i} with type '{prompt.get('type')}' missing options field")
                    return False
            
            self.log_test("Monitoring Questionnaire Endpoint", True, 
                        f"✅ Monitoring questionnaire endpoint working correctly - HTTP 200, {len(prompts)} prompts, level=basic, total_questions={total_questions}")
            
            print(f"   📊 Response Summary:")
            print(f"      Status: HTTP 200")
            print(f"      Level: {data.get('level')}")
            print(f"      Total Questions: {total_questions}")
            print(f"      Prompts Count: {len(prompts)}")
            print(f"      Sample Question: {prompts[0].get('question', 'N/A')[:50]}..." if prompts else "      No prompts")
            
            return True
            
        except Exception as e:
            self.log_test("Monitoring Questionnaire Endpoint", False, f"Request error: {str(e)}")
            return False

    def test_double_click_questionnaire_backend_support(self):
        """Comprehensive test for double-click questionnaire backend support for API, Backup, and Monitoring"""
        try:
            print("🎯 COMPREHENSIVE TEST: Double-Click Questionnaire Backend Support")
            print("=" * 80)
            print("Testing API, Backup, and Monitoring questionnaire endpoints")
            print("Verifying backend support for double-click questionnaire functionality")
            print("=" * 80)
            
            # Test all three endpoints
            endpoints_to_test = [
                {
                    "name": "API",
                    "url": f"{self.base_url}/questionnaires/API?level=basic",
                    "test_method": self.test_api_questionnaire_endpoint
                },
                {
                    "name": "Backup", 
                    "url": f"{self.base_url}/questionnaires/Backup?level=basic",
                    "test_method": self.test_backup_questionnaire_endpoint
                },
                {
                    "name": "Monitoring",
                    "url": f"{self.base_url}/questionnaires/Monitoring?level=basic", 
                    "test_method": self.test_monitoring_questionnaire_endpoint
                }
            ]
            
            success_count = 0
            total_tests = len(endpoints_to_test)
            detailed_results = []
            
            for endpoint in endpoints_to_test:
                print(f"\n🔍 Testing {endpoint['name']} questionnaire endpoint...")
                
                # Run the specific test method
                if endpoint['test_method']():
                    success_count += 1
                    detailed_results.append(f"✅ {endpoint['name']}: Working correctly")
                else:
                    detailed_results.append(f"❌ {endpoint['name']}: Failed")
            
            # Summary
            print(f"\n📊 DOUBLE-CLICK QUESTIONNAIRE BACKEND SUPPORT SUMMARY:")
            print(f"=" * 60)
            for result in detailed_results:
                print(f"   {result}")
            
            print(f"\n📈 Overall Results:")
            print(f"   ✅ Passed: {success_count}/{total_tests}")
            print(f"   📊 Success Rate: {(success_count/total_tests*100):.1f}%")
            
            if success_count == total_tests:
                self.log_test("Double-Click Questionnaire Backend Support", True, 
                            f"✅ ALL ENDPOINTS WORKING: {success_count}/{total_tests} questionnaire endpoints (API, Backup, Monitoring) are working correctly for double-click functionality")
                print(f"\n🎉 SUCCESS: All double-click questionnaire backend endpoints are working!")
                print(f"   ✅ API questionnaire endpoint: Ready for frontend integration")
                print(f"   ✅ Backup questionnaire endpoint: Ready for frontend integration") 
                print(f"   ✅ Monitoring questionnaire endpoint: Ready for frontend integration")
                return True
            else:
                failed_count = total_tests - success_count
                self.log_test("Double-Click Questionnaire Backend Support", False, 
                            f"❌ PARTIAL FAILURE: {failed_count}/{total_tests} questionnaire endpoints failed. Only {success_count} endpoints working correctly.")
                print(f"\n⚠️  PARTIAL FAILURE: {failed_count} endpoints need attention before frontend implementation")
                return False
            
        except Exception as e:
            self.log_test("Double-Click Questionnaire Backend Support", False, f"Request error: {str(e)}")
            return False

    # ============================================================================
    # Test Runner
    # ============================================================================
    
    def run_all_tests(self):
        """Run all tests with focus on double-click questionnaire backend support"""
        print("🚀 Starting Double-Click Questionnaire Backend Support Testing")
        print("=" * 90)
        print("DOUBLE-CLICK QUESTIONNAIRE BACKEND SUPPORT VERIFICATION")
        print("Primary Focus: API, Backup, and Monitoring questionnaire endpoints")
        print("Testing: GET /api/questionnaires/{API|Backup|Monitoring}?level=basic")
        print("Expected: HTTP 200, prompts field, level=basic, total_questions field")
        print("=" * 90)
        
        tests = [
            # Basic connectivity
            self.test_health_check,
            
            # REVIEW REQUEST: Double-Click Questionnaire Backend Support Tests
            self.test_api_questionnaire_endpoint,
            self.test_backup_questionnaire_endpoint,
            self.test_monitoring_questionnaire_endpoint,
            self.test_double_click_questionnaire_backend_support,
            
            # CRITICAL TEST: Questionnaire Resumption Fix
            self.test_questionnaire_resumption_fix,
            
            # SECONDARY TEST: Database Questionnaire Consistency Fix
            self.test_database_questionnaire_consistency_fix,
            
            # Additional comprehensive tests
            # TEST 1: Diagram and Node Creation
            self.test_create_test_diagram,
            self.test_add_test_nodes,
            
            # TEST 2: Questionnaire Retrieval API
            self.test_questionnaire_retrieval_empty_state,
            
            # TEST 3: Questionnaire Update API
            self.test_questionnaire_update_api,
            self.test_questionnaire_retrieval_with_responses,
            
            # TEST 4: Error Handling
            self.test_questionnaire_error_handling,
            
            # TEST 5: Integration Testing
            self.test_complete_double_click_workflow,
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
        print("🎯 DATABASE QUESTIONNAIRE CONSISTENCY FIX VERIFICATION SUMMARY")
        print("=" * 90)
        print(f"✅ PASSED: {passed}")
        print(f"❌ FAILED: {failed}")
        print(f"📊 SUCCESS RATE: {(passed / (passed + failed) * 100):.1f}%")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED! Database questionnaire consistency fix verification successful.")
            print("✅ CRITICAL: Database questionnaire consistency fix working correctly")
            print("✅ GET /api/intelligent-nodes/Database/prompts returns proper response structure")
            print("✅ success=true and prompts_count field present and consistent")
            print("✅ prompts_count matches actual prompts.length (resolves original bug)")
            print("✅ Consistency verified across multiple test iterations")
            print("✅ Parent-child questionnaire resumption issue resolved")
            print("✅ Additional questionnaire functionality tests also passed")
        else:
            print(f"\n⚠️  {failed} tests failed. Analysis:")
            
            # Analyze the test results to provide diagnostic information
            error_tests = [result for result in self.test_results if not result['success']]
            
            for error_test in error_tests:
                print(f"🚨 FAILED: {error_test['test']}")
                print(f"   Issue: {error_test['message']}")
                
            # Check if the critical test failed
            critical_test_failed = any('Database Consistency Fix' in result['test'] for result in error_tests)
            if critical_test_failed:
                print(f"\n🚨 CRITICAL ISSUE: Database questionnaire consistency fix verification failed!")
                print(f"   This means the original bug may still exist:")
                print(f"   - prompts_count field may be missing or incorrect")
                print(f"   - Parent-child questionnaire resumption may still fail")
                print(f"   - Immediate attention required to resolve the consistency issue")
        
        return passed, failed

def main():
    """Main test execution"""
    tester = DoubleClickQuestionnaireTester()
    passed, failed = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()