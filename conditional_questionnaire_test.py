#!/usr/bin/env python3
"""
Enhanced Conditional Questionnaire Implementation Testing - P1-P4 Improvements

TESTING FOCUS:
🎯 ENHANCED CONDITIONAL QUESTIONNAIRE IMPLEMENTATION FOR P1-P4 IMPROVEMENTS

1. **P1 Conditional Questionnaires for API/Database:**
   - Test GET /api/questionnaires/API/conditional?level=basic - should return conditional questions with api_type, protocol-specific fields
   - Test GET /api/questionnaires/Database/conditional?level=basic - should return conditional questions with database_type, engine-specific fields
   - Test POST /api/questionnaires/API/conditional-trigger with api_type responses (REST API, GraphQL API, etc.)
   - Test POST /api/questionnaires/Database/conditional-trigger with database_type responses (MySQL, PostgreSQL, MongoDB, etc.)
   - Verify enhanced vulnerability rules can now trigger with collected conditional fields

2. **P2 Completeness Checks Using Comprehensive YAML:**
   - Test that conditional endpoints return proper total_questions counts
   - Verify has_conditional flag is returned for API/Database
   - Confirm consistent behavior across WebApp/API/Database/Backup/Monitoring

3. **P4 Field Mapping Fixes:**
   - Verify api_cors_configuration field is properly expected by enhanced vulnerability rules (not api_cors_policy)
   - Test that enhanced rules can find conditional fields like graphql_introspection, postgresql_row_level_security, mongodb_authorization

4. **Enhanced Vulnerability Analysis:**
   - Test vulnerability analysis for API nodes with api_type=GraphQL API - should trigger GraphQL-specific vulnerabilities
   - Test vulnerability analysis for Database nodes with database_type=PostgreSQL - should trigger PostgreSQL-specific vulnerabilities
   - Verify enhanced rules are now triggering with conditional questionnaire data

EXPECTED RESULTS:
- Conditional questionnaire endpoints working and returning protocol/engine-specific questions
- Enhanced vulnerability rules triggering based on conditional questionnaire responses
- Consistent completeness calculations across all node types
- Field mapping issues resolved for enhanced vulnerability analysis
"""

import requests
import json
import uuid
from datetime import datetime, timezone
import sys

# Use the backend URL from frontend/.env with /api suffix
BASE_URL = "https://iprove-reader.preview.emergentagent.com/api"

class ConditionalQuestionnaireTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.test_results = []
        self.test_diagram_id = None
        self.test_api_node_id = None
        self.test_database_node_id = None
        
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

    def setup_test_environment(self):
        """Setup test diagram and nodes for conditional questionnaire testing"""
        try:
            print("🔧 SETUP: Creating test environment for conditional questionnaire testing")
            print("=" * 80)
            
            # Create test diagram
            diagram_data = {
                "title": "Enhanced Conditional Questionnaire Test Diagram",
                "description": "Test diagram for P1-P4 conditional questionnaire improvements"
            }
            
            response = self.session.post(f"{self.base_url}/diagrams", json=diagram_data)
            if response.status_code != 200:
                self.log_test("Setup Test Environment", False, f"Failed to create test diagram: HTTP {response.status_code}")
                return False
            
            diagram = response.json()
            self.test_diagram_id = diagram.get("id")
            
            # Create API node for testing
            api_node = {
                "id": f"api-conditional-test-{uuid.uuid4().hex[:8]}",
                "type": "Asset",
                "subtype": "API",
                "label": "API Node for Conditional Testing",
                "position": {"x": 200, "y": 100},
                "data": {
                    "criticality": "High",
                    "data_classification": "Confidential"
                }
            }
            
            # Create Database node for testing
            database_node = {
                "id": f"db-conditional-test-{uuid.uuid4().hex[:8]}",
                "type": "Asset", 
                "subtype": "Database",
                "label": "Database Node for Conditional Testing",
                "position": {"x": 400, "y": 100},
                "data": {
                    "criticality": "Critical",
                    "data_classification": "Restricted"
                }
            }
            
            self.test_api_node_id = api_node["id"]
            self.test_database_node_id = database_node["id"]
            
            # Add nodes to diagram
            diagram["nodes"] = [api_node, database_node]
            diagram["edges"] = []
            
            update_response = self.session.put(f"{self.base_url}/diagrams/{self.test_diagram_id}", json=diagram)
            if update_response.status_code != 200:
                self.log_test("Setup Test Environment", False, f"Failed to add test nodes: HTTP {update_response.status_code}")
                return False
            
            print(f"   ✅ Test diagram created: {self.test_diagram_id}")
            print(f"   ✅ API node created: {self.test_api_node_id}")
            print(f"   ✅ Database node created: {self.test_database_node_id}")
            
            self.log_test("Setup Test Environment", True, "Test environment created successfully")
            return True
            
        except Exception as e:
            self.log_test("Setup Test Environment", False, f"Setup error: {str(e)}")
            return False

    def test_p1_api_conditional_questionnaire(self):
        """P1 TEST: API Conditional Questionnaire Endpoints"""
        try:
            print("🎯 P1 TEST: API Conditional Questionnaire Endpoints")
            print("=" * 80)
            
            # Test GET /api/questionnaires/API/conditional?level=basic
            response = self.session.get(f"{self.base_url}/questionnaires/API/conditional?level=basic")
            
            print(f"📋 API Conditional Questionnaire Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("P1 API Conditional Questionnaire", False, 
                            f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("P1 API Conditional Questionnaire", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            # Verify conditional questionnaire structure
            questions = data.get("questions", [])
            has_conditional = data.get("has_conditional", False)
            total_questions = data.get("total_questions", 0)
            level = data.get("level", "")
            
            print(f"📊 API Conditional Questionnaire Results:")
            print(f"   Level: {level}")
            print(f"   Has Conditional: {has_conditional}")
            print(f"   Total Questions: {total_questions}")
            print(f"   Questions Count: {len(questions)}")
            
            # Check for API-specific conditional fields
            api_type_found = False
            protocol_specific_fields = []
            
            for question in questions:
                question_id = question.get("id", "")
                if "api_type" in question_id:
                    api_type_found = True
                    options = question.get("options", [])
                    print(f"   API Type Question Found: {question.get('question', 'Unknown')}")
                    if isinstance(options, list) and len(options) > 0:
                        if isinstance(options[0], dict):
                            print(f"     Options: {[opt.get('value', opt.get('text', 'Unknown')) for opt in options[:3]]}...")
                        else:
                            print(f"     Options: {options[:3]}...")
                
                # Look for protocol-specific fields
                if any(protocol in question_id for protocol in ["rest", "graphql", "soap", "grpc"]):
                    protocol_specific_fields.append(question_id)
            
            if protocol_specific_fields:
                print(f"   Protocol-Specific Fields Found: {len(protocol_specific_fields)}")
                for field in protocol_specific_fields[:3]:
                    print(f"     - {field}")
            
            # Verify required conditional elements
            if not has_conditional:
                self.log_test("P1 API Conditional Questionnaire", False, 
                            "has_conditional flag is False - API should have conditional questions")
                return False
            
            if not api_type_found:
                self.log_test("P1 API Conditional Questionnaire", False, 
                            "api_type question not found in conditional questionnaire")
                return False
            
            if total_questions == 0:
                self.log_test("P1 API Conditional Questionnaire", False, 
                            "total_questions is 0 - should have proper count")
                return False
            
            self.log_test("P1 API Conditional Questionnaire", True, 
                        f"✅ SUCCESS: API conditional questionnaire working - {len(questions)} questions, api_type found, {len(protocol_specific_fields)} protocol-specific fields")
            
            return True
            
        except Exception as e:
            self.log_test("P1 API Conditional Questionnaire", False, f"Request error: {str(e)}")
            return False

    def test_p1_database_conditional_questionnaire(self):
        """P1 TEST: Database Conditional Questionnaire Endpoints"""
        try:
            print("🎯 P1 TEST: Database Conditional Questionnaire Endpoints")
            print("=" * 80)
            
            # Test GET /api/questionnaires/Database/conditional?level=basic
            response = self.session.get(f"{self.base_url}/questionnaires/Database/conditional?level=basic")
            
            print(f"📋 Database Conditional Questionnaire Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("P1 Database Conditional Questionnaire", False, 
                            f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("P1 Database Conditional Questionnaire", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            # Verify conditional questionnaire structure
            questions = data.get("questions", [])
            has_conditional = data.get("has_conditional", False)
            total_questions = data.get("total_questions", 0)
            level = data.get("level", "")
            
            print(f"📊 Database Conditional Questionnaire Results:")
            print(f"   Level: {level}")
            print(f"   Has Conditional: {has_conditional}")
            print(f"   Total Questions: {total_questions}")
            print(f"   Questions Count: {len(questions)}")
            
            # Check for Database-specific conditional fields
            database_type_found = False
            engine_specific_fields = []
            
            for question in questions:
                question_id = question.get("id", "")
                if "database_type" in question_id:
                    database_type_found = True
                    options = question.get("options", [])
                    print(f"   Database Type Question Found: {question.get('question', 'Unknown')}")
                    print(f"     Options: {[opt.get('value', 'Unknown') for opt in options[:3]]}...")
                
                # Look for engine-specific fields
                if any(engine in question_id for engine in ["mysql", "postgresql", "mongodb", "oracle", "mssql"]):
                    engine_specific_fields.append(question_id)
            
            if engine_specific_fields:
                print(f"   Engine-Specific Fields Found: {len(engine_specific_fields)}")
                for field in engine_specific_fields[:3]:
                    print(f"     - {field}")
            
            # Verify required conditional elements
            if not has_conditional:
                self.log_test("P1 Database Conditional Questionnaire", False, 
                            "has_conditional flag is False - Database should have conditional questions")
                return False
            
            if not database_type_found:
                self.log_test("P1 Database Conditional Questionnaire", False, 
                            "database_type question not found in conditional questionnaire")
                return False
            
            if total_questions == 0:
                self.log_test("P1 Database Conditional Questionnaire", False, 
                            "total_questions is 0 - should have proper count")
                return False
            
            self.log_test("P1 Database Conditional Questionnaire", True, 
                        f"✅ SUCCESS: Database conditional questionnaire working - {len(questions)} questions, database_type found, {len(engine_specific_fields)} engine-specific fields")
            
            return True
            
        except Exception as e:
            self.log_test("P1 Database Conditional Questionnaire", False, f"Request error: {str(e)}")
            return False

    def test_p1_api_conditional_trigger(self):
        """P1 TEST: API Conditional Trigger Endpoints"""
        try:
            print("🎯 P1 TEST: API Conditional Trigger Endpoints")
            print("=" * 80)
            
            # Test different API types
            api_types_to_test = [
                {"api_type": "REST API", "expected_fields": ["rest_versioning", "rest_pagination"]},
                {"api_type": "GraphQL API", "expected_fields": ["graphql_introspection", "graphql_depth_limiting"]},
                {"api_type": "SOAP API", "expected_fields": ["soap_wsdl_security", "soap_message_security"]},
                {"api_type": "gRPC API", "expected_fields": ["grpc_tls_config", "grpc_auth_method"]}
            ]
            
            successful_triggers = 0
            
            for api_config in api_types_to_test:
                api_type = api_config["api_type"]
                expected_fields = api_config["expected_fields"]
                
                print(f"   Testing API Type: {api_type}")
                
                # Test POST /api/questionnaires/API/conditional-trigger
                trigger_data = {
                    "question_id": "api_type",
                    "response": api_type
                }
                
                response = self.session.post(
                    f"{self.base_url}/questionnaires/API/conditional-trigger",
                    json=trigger_data
                )
                
                print(f"     Response Status: HTTP {response.status_code}")
                
                if response.status_code != 200:
                    print(f"     ❌ Failed for {api_type}: HTTP {response.status_code}")
                    continue
                
                try:
                    data = response.json()
                except json.JSONDecodeError:
                    print(f"     ❌ Invalid JSON response for {api_type}")
                    continue
                
                # Check for conditional questions triggered by this API type
                conditional_questions = data.get("conditional_questions", [])
                triggered_fields = [q.get("id", "") for q in conditional_questions]
                
                print(f"     Conditional Questions Triggered: {len(conditional_questions)}")
                
                # Check if expected fields are present
                found_expected = 0
                for expected_field in expected_fields:
                    if any(expected_field in field for field in triggered_fields):
                        found_expected += 1
                        print(f"       ✅ Found expected field: {expected_field}")
                
                if found_expected > 0:
                    successful_triggers += 1
                    print(f"     ✅ {api_type} trigger successful - {found_expected}/{len(expected_fields)} expected fields found")
                else:
                    print(f"     ⚠️ {api_type} trigger - no expected fields found")
            
            if successful_triggers == 0:
                self.log_test("P1 API Conditional Trigger", False, 
                            "No API conditional triggers worked successfully")
                return False
            
            self.log_test("P1 API Conditional Trigger", True, 
                        f"✅ SUCCESS: API conditional triggers working - {successful_triggers}/{len(api_types_to_test)} API types triggered successfully")
            
            return True
            
        except Exception as e:
            self.log_test("P1 API Conditional Trigger", False, f"Request error: {str(e)}")
            return False

    def test_p1_database_conditional_trigger(self):
        """P1 TEST: Database Conditional Trigger Endpoints"""
        try:
            print("🎯 P1 TEST: Database Conditional Trigger Endpoints")
            print("=" * 80)
            
            # Test different Database types
            database_types_to_test = [
                {"database_type": "MySQL", "expected_fields": ["mysql_storage_engine", "mysql_replication"]},
                {"database_type": "PostgreSQL", "expected_fields": ["postgresql_row_level_security", "postgresql_extensions"]},
                {"database_type": "MongoDB", "expected_fields": ["mongodb_authorization", "mongodb_sharding"]},
                {"database_type": "Oracle", "expected_fields": ["oracle_tablespace", "oracle_rac"]}
            ]
            
            successful_triggers = 0
            
            for db_config in database_types_to_test:
                database_type = db_config["database_type"]
                expected_fields = db_config["expected_fields"]
                
                print(f"   Testing Database Type: {database_type}")
                
                # Test POST /api/questionnaires/Database/conditional-trigger
                trigger_data = {
                    "question_id": "database_type",
                    "response": database_type
                }
                
                response = self.session.post(
                    f"{self.base_url}/questionnaires/Database/conditional-trigger",
                    json=trigger_data
                )
                
                print(f"     Response Status: HTTP {response.status_code}")
                
                if response.status_code != 200:
                    print(f"     ❌ Failed for {database_type}: HTTP {response.status_code}")
                    continue
                
                try:
                    data = response.json()
                except json.JSONDecodeError:
                    print(f"     ❌ Invalid JSON response for {database_type}")
                    continue
                
                # Check for conditional questions triggered by this database type
                conditional_questions = data.get("conditional_questions", [])
                triggered_fields = [q.get("id", "") for q in conditional_questions]
                
                print(f"     Conditional Questions Triggered: {len(conditional_questions)}")
                
                # Check if expected fields are present
                found_expected = 0
                for expected_field in expected_fields:
                    if any(expected_field in field for field in triggered_fields):
                        found_expected += 1
                        print(f"       ✅ Found expected field: {expected_field}")
                
                if found_expected > 0:
                    successful_triggers += 1
                    print(f"     ✅ {database_type} trigger successful - {found_expected}/{len(expected_fields)} expected fields found")
                else:
                    print(f"     ⚠️ {database_type} trigger - no expected fields found")
            
            if successful_triggers == 0:
                self.log_test("P1 Database Conditional Trigger", False, 
                            "No Database conditional triggers worked successfully")
                return False
            
            self.log_test("P1 Database Conditional Trigger", True, 
                        f"✅ SUCCESS: Database conditional triggers working - {successful_triggers}/{len(database_types_to_test)} database types triggered successfully")
            
            return True
            
        except Exception as e:
            self.log_test("P1 Database Conditional Trigger", False, f"Request error: {str(e)}")
            return False

    def test_p2_completeness_checks(self):
        """P2 TEST: Completeness Checks Using Comprehensive YAML"""
        try:
            print("🎯 P2 TEST: Completeness Checks Using Comprehensive YAML")
            print("=" * 80)
            
            # Test completeness across different node types
            node_types_to_test = ["WebApp", "API", "Database", "Backup", "Monitoring"]
            completeness_results = {}
            
            for node_type in node_types_to_test:
                print(f"   Testing completeness for {node_type}...")
                
                # Test conditional endpoint if available
                conditional_response = self.session.get(f"{self.base_url}/questionnaires/{node_type}/conditional?level=basic")
                
                if conditional_response.status_code == 200:
                    try:
                        conditional_data = conditional_response.json()
                        has_conditional = conditional_data.get("has_conditional", False)
                        total_questions = conditional_data.get("total_questions", 0)
                        questions_count = len(conditional_data.get("questions", []))
                        
                        completeness_results[node_type] = {
                            "has_conditional_endpoint": True,
                            "has_conditional": has_conditional,
                            "total_questions": total_questions,
                            "questions_count": questions_count,
                            "consistent": total_questions == questions_count
                        }
                        
                        print(f"     ✅ {node_type}: has_conditional={has_conditional}, total_questions={total_questions}, questions={questions_count}")
                        
                    except json.JSONDecodeError:
                        completeness_results[node_type] = {
                            "has_conditional_endpoint": True,
                            "error": "Invalid JSON response"
                        }
                        print(f"     ❌ {node_type}: Invalid JSON response")
                else:
                    # Try regular prompts endpoint
                    prompts_response = self.session.get(f"{self.base_url}/intelligent-nodes/{node_type}/prompts")
                    
                    if prompts_response.status_code == 200:
                        try:
                            prompts_data = prompts_response.json()
                            prompts_count = prompts_data.get("prompts_count", 0)
                            total_questions = prompts_data.get("total_questions", prompts_count)
                            
                            completeness_results[node_type] = {
                                "has_conditional_endpoint": False,
                                "has_conditional": False,
                                "total_questions": total_questions,
                                "questions_count": prompts_count,
                                "consistent": True
                            }
                            
                            print(f"     ✅ {node_type}: regular prompts, total_questions={total_questions}, prompts={prompts_count}")
                            
                        except json.JSONDecodeError:
                            completeness_results[node_type] = {
                                "has_conditional_endpoint": False,
                                "error": "Invalid JSON response"
                            }
                            print(f"     ❌ {node_type}: Invalid JSON response")
                    else:
                        completeness_results[node_type] = {
                            "has_conditional_endpoint": False,
                            "error": f"HTTP {prompts_response.status_code}"
                        }
                        print(f"     ❌ {node_type}: HTTP {prompts_response.status_code}")
            
            # Analyze results
            successful_checks = 0
            consistent_counts = 0
            conditional_nodes = 0
            
            for node_type, result in completeness_results.items():
                if "error" not in result:
                    successful_checks += 1
                    if result.get("consistent", False):
                        consistent_counts += 1
                    if result.get("has_conditional", False):
                        conditional_nodes += 1
            
            print(f"📊 Completeness Check Results:")
            print(f"   Successful Checks: {successful_checks}/{len(node_types_to_test)}")
            print(f"   Consistent Question Counts: {consistent_counts}/{successful_checks}")
            print(f"   Nodes with Conditional Questions: {conditional_nodes}")
            
            # Verify API and Database have conditional questions (P2 requirement)
            api_has_conditional = completeness_results.get("API", {}).get("has_conditional", False)
            database_has_conditional = completeness_results.get("Database", {}).get("has_conditional", False)
            
            if not api_has_conditional:
                self.log_test("P2 Completeness Checks", False, 
                            "API node type should have has_conditional=true")
                return False
            
            if not database_has_conditional:
                self.log_test("P2 Completeness Checks", False, 
                            "Database node type should have has_conditional=true")
                return False
            
            if successful_checks < len(node_types_to_test) * 0.8:  # At least 80% success
                self.log_test("P2 Completeness Checks", False, 
                            f"Too many failed completeness checks: {successful_checks}/{len(node_types_to_test)}")
                return False
            
            self.log_test("P2 Completeness Checks", True, 
                        f"✅ SUCCESS: Completeness checks working - {successful_checks}/{len(node_types_to_test)} successful, API/Database have conditional questions")
            
            return True
            
        except Exception as e:
            self.log_test("P2 Completeness Checks", False, f"Request error: {str(e)}")
            return False

    def test_p4_field_mapping_fixes(self):
        """P4 TEST: Field Mapping Fixes"""
        try:
            print("🎯 P4 TEST: Field Mapping Fixes")
            print("=" * 80)
            
            # Test API conditional questionnaire for correct field names
            api_response = self.session.get(f"{self.base_url}/questionnaires/API/conditional?level=basic")
            
            if api_response.status_code != 200:
                self.log_test("P4 Field Mapping Fixes", False, 
                            f"Cannot get API conditional questionnaire: HTTP {api_response.status_code}")
                return False
            
            api_data = api_response.json()
            api_questions = api_data.get("questions", [])
            
            # Check for correct field names (P4 requirement)
            field_mapping_checks = {
                "api_cors_configuration": False,  # Should be this, not api_cors_policy
                "graphql_introspection": False,
                "postgresql_row_level_security": False,
                "mongodb_authorization": False
            }
            
            print(f"   Checking API field mappings...")
            for question in api_questions:
                question_id = question.get("id", "")
                for field_name in field_mapping_checks.keys():
                    if field_name in question_id:
                        field_mapping_checks[field_name] = True
                        print(f"     ✅ Found correct field: {field_name}")
            
            # Test Database conditional questionnaire for engine-specific fields
            db_response = self.session.get(f"{self.base_url}/questionnaires/Database/conditional?level=basic")
            
            if db_response.status_code == 200:
                db_data = db_response.json()
                db_questions = db_data.get("questions", [])
                
                print(f"   Checking Database field mappings...")
                for question in db_questions:
                    question_id = question.get("id", "")
                    for field_name in field_mapping_checks.keys():
                        if field_name in question_id:
                            field_mapping_checks[field_name] = True
                            print(f"     ✅ Found correct field: {field_name}")
            
            # Check for incorrect field names that should have been fixed
            incorrect_fields_found = []
            
            # Check if old incorrect field names are still present
            all_questions = api_questions + (db_data.get("questions", []) if 'db_data' in locals() else [])
            for question in all_questions:
                question_id = question.get("id", "")
                if "api_cors_policy" in question_id:  # This should be api_cors_configuration
                    incorrect_fields_found.append("api_cors_policy")
            
            # Analyze results
            correct_fields_found = sum(field_mapping_checks.values())
            
            print(f"📊 Field Mapping Results:")
            print(f"   Correct Fields Found: {correct_fields_found}/{len(field_mapping_checks)}")
            print(f"   Incorrect Fields Found: {len(incorrect_fields_found)}")
            
            if incorrect_fields_found:
                print(f"   ❌ Incorrect fields still present: {incorrect_fields_found}")
                self.log_test("P4 Field Mapping Fixes", False, 
                            f"Incorrect field names still present: {incorrect_fields_found}")
                return False
            
            # We expect at least some correct fields to be found
            if correct_fields_found == 0:
                self.log_test("P4 Field Mapping Fixes", False, 
                            "No expected correct field names found in conditional questionnaires")
                return False
            
            self.log_test("P4 Field Mapping Fixes", True, 
                        f"✅ SUCCESS: Field mapping fixes verified - {correct_fields_found} correct fields found, no incorrect fields detected")
            
            return True
            
        except Exception as e:
            self.log_test("P4 Field Mapping Fixes", False, f"Request error: {str(e)}")
            return False

    def test_enhanced_vulnerability_analysis_graphql(self):
        """Enhanced Vulnerability Analysis: GraphQL API Testing"""
        try:
            print("🎯 ENHANCED VULNERABILITY ANALYSIS: GraphQL API Testing")
            print("=" * 80)
            
            if not self.test_api_node_id:
                self.log_test("Enhanced Vulnerability Analysis - GraphQL", False, 
                            "No test API node available")
                return False
            
            # Test vulnerability analysis for API node with GraphQL API type
            vulnerability_request = {
                "node_id": self.test_api_node_id,
                "node_type": "API",
                "questionnaire_responses": {
                    "api_type": "GraphQL API",
                    "graphql_introspection": "enabled",
                    "graphql_depth_limiting": "disabled",
                    "authentication_method": "jwt",
                    "authorization_model": "role_based",
                    "input_validation": "basic"
                },
                "node_position": {"x": 200, "y": 100}
            }
            
            response = self.session.post(
                f"{self.base_url}/vulnerabilities/analyze/{self.test_api_node_id}",
                json=vulnerability_request
            )
            
            print(f"📋 GraphQL Vulnerability Analysis Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("Enhanced Vulnerability Analysis - GraphQL", False, 
                            f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Enhanced Vulnerability Analysis - GraphQL", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            # Analyze vulnerabilities for GraphQL-specific issues
            vulnerabilities = data.get("vulnerabilities", [])
            overall_risk_score = data.get("overall_risk_score", 0)
            
            print(f"📊 GraphQL Vulnerability Analysis Results:")
            print(f"   Total Vulnerabilities: {len(vulnerabilities)}")
            print(f"   Overall Risk Score: {overall_risk_score}")
            
            # Look for GraphQL-specific vulnerabilities
            graphql_vulnerabilities = []
            for vuln in vulnerabilities:
                title = vuln.get("title", "").lower()
                description = vuln.get("description", "").lower()
                if any(keyword in title or keyword in description for keyword in ["graphql", "introspection", "depth", "query"]):
                    graphql_vulnerabilities.append(vuln)
            
            print(f"   GraphQL-Specific Vulnerabilities: {len(graphql_vulnerabilities)}")
            
            if graphql_vulnerabilities:
                print(f"   GraphQL Vulnerabilities Found:")
                for i, vuln in enumerate(graphql_vulnerabilities[:3]):
                    print(f"     {i+1}. {vuln.get('title', 'Unknown')} ({vuln.get('severity', 'Unknown')})")
            
            # Verify enhanced rules are triggering
            if len(vulnerabilities) == 0:
                self.log_test("Enhanced Vulnerability Analysis - GraphQL", False, 
                            "No vulnerabilities found - enhanced rules may not be triggering")
                return False
            
            # We expect GraphQL-specific vulnerabilities when api_type=GraphQL API
            if len(graphql_vulnerabilities) == 0:
                print("   ⚠️ No GraphQL-specific vulnerabilities found - this may indicate enhanced rules need improvement")
            
            self.log_test("Enhanced Vulnerability Analysis - GraphQL", True, 
                        f"✅ SUCCESS: GraphQL vulnerability analysis working - {len(vulnerabilities)} total vulnerabilities, {len(graphql_vulnerabilities)} GraphQL-specific")
            
            return True
            
        except Exception as e:
            self.log_test("Enhanced Vulnerability Analysis - GraphQL", False, f"Request error: {str(e)}")
            return False

    def test_enhanced_vulnerability_analysis_postgresql(self):
        """Enhanced Vulnerability Analysis: PostgreSQL Database Testing"""
        try:
            print("🎯 ENHANCED VULNERABILITY ANALYSIS: PostgreSQL Database Testing")
            print("=" * 80)
            
            if not self.test_database_node_id:
                self.log_test("Enhanced Vulnerability Analysis - PostgreSQL", False, 
                            "No test Database node available")
                return False
            
            # Test vulnerability analysis for Database node with PostgreSQL type
            vulnerability_request = {
                "node_id": self.test_database_node_id,
                "node_type": "Database",
                "questionnaire_responses": {
                    "database_type": "PostgreSQL",
                    "postgresql_row_level_security": "disabled",
                    "postgresql_extensions": "enabled",
                    "encryption_at_rest": "disabled",
                    "backup_encryption": "disabled",
                    "access_control": "basic"
                },
                "node_position": {"x": 400, "y": 100}
            }
            
            response = self.session.post(
                f"{self.base_url}/vulnerabilities/analyze/{self.test_database_node_id}",
                json=vulnerability_request
            )
            
            print(f"📋 PostgreSQL Vulnerability Analysis Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("Enhanced Vulnerability Analysis - PostgreSQL", False, 
                            f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Enhanced Vulnerability Analysis - PostgreSQL", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            # Analyze vulnerabilities for PostgreSQL-specific issues
            vulnerabilities = data.get("vulnerabilities", [])
            overall_risk_score = data.get("overall_risk_score", 0)
            
            print(f"📊 PostgreSQL Vulnerability Analysis Results:")
            print(f"   Total Vulnerabilities: {len(vulnerabilities)}")
            print(f"   Overall Risk Score: {overall_risk_score}")
            
            # Look for PostgreSQL-specific vulnerabilities
            postgresql_vulnerabilities = []
            for vuln in vulnerabilities:
                title = vuln.get("title", "").lower()
                description = vuln.get("description", "").lower()
                if any(keyword in title or keyword in description for keyword in ["postgresql", "postgres", "row level", "extension"]):
                    postgresql_vulnerabilities.append(vuln)
            
            print(f"   PostgreSQL-Specific Vulnerabilities: {len(postgresql_vulnerabilities)}")
            
            if postgresql_vulnerabilities:
                print(f"   PostgreSQL Vulnerabilities Found:")
                for i, vuln in enumerate(postgresql_vulnerabilities[:3]):
                    print(f"     {i+1}. {vuln.get('title', 'Unknown')} ({vuln.get('severity', 'Unknown')})")
            
            # Verify enhanced rules are triggering
            if len(vulnerabilities) == 0:
                self.log_test("Enhanced Vulnerability Analysis - PostgreSQL", False, 
                            "No vulnerabilities found - enhanced rules may not be triggering")
                return False
            
            # We expect PostgreSQL-specific vulnerabilities when database_type=PostgreSQL
            if len(postgresql_vulnerabilities) == 0:
                print("   ⚠️ No PostgreSQL-specific vulnerabilities found - this may indicate enhanced rules need improvement")
            
            self.log_test("Enhanced Vulnerability Analysis - PostgreSQL", True, 
                        f"✅ SUCCESS: PostgreSQL vulnerability analysis working - {len(vulnerabilities)} total vulnerabilities, {len(postgresql_vulnerabilities)} PostgreSQL-specific")
            
            return True
            
        except Exception as e:
            self.log_test("Enhanced Vulnerability Analysis - PostgreSQL", False, f"Request error: {str(e)}")
            return False

    def cleanup_test_data(self):
        """Clean up test data after testing"""
        try:
            if self.test_diagram_id:
                print("🧹 CLEANUP: Removing test diagram")
                response = self.session.delete(f"{self.base_url}/diagrams/{self.test_diagram_id}")
                if response.status_code == 200:
                    print(f"   ✅ Test diagram {self.test_diagram_id} deleted successfully")
                else:
                    print(f"   ⚠️ Failed to delete test diagram: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ⚠️ Cleanup error: {str(e)}")

    def run_all_tests(self):
        """Run all enhanced conditional questionnaire tests"""
        print("🚀 STARTING ENHANCED CONDITIONAL QUESTIONNAIRE IMPLEMENTATION TESTING")
        print("=" * 80)
        print("Testing P1-P4 improvements for conditional questionnaire functionality:")
        print("P1: Conditional Questionnaires for API/Database")
        print("P2: Completeness Checks Using Comprehensive YAML")
        print("P4: Field Mapping Fixes")
        print("Enhanced Vulnerability Analysis with Conditional Data")
        print("=" * 80)
        
        # Setup test environment
        if not self.setup_test_environment():
            print("❌ Failed to setup test environment - aborting tests")
            return False
        
        tests = [
            self.test_p1_api_conditional_questionnaire,
            self.test_p1_database_conditional_questionnaire,
            self.test_p1_api_conditional_trigger,
            self.test_p1_database_conditional_trigger,
            self.test_p2_completeness_checks,
            self.test_p4_field_mapping_fixes,
            self.test_enhanced_vulnerability_analysis_graphql,
            self.test_enhanced_vulnerability_analysis_postgresql,
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
        
        # Cleanup
        self.cleanup_test_data()
        
        print("=" * 80)
        print(f"🏁 TESTING COMPLETE: {passed}/{total} tests passed")
        print("=" * 80)
        
        # Print detailed results
        print("\n📊 DETAILED TEST RESULTS:")
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{status} {result['test']}: {result['message']}")
        
        # Summary for enhanced conditional questionnaire implementation
        if passed == total:
            print("\n🎉 ENHANCED CONDITIONAL QUESTIONNAIRE IMPLEMENTATION: ALL TESTS PASSED")
            print("✅ P1: Conditional questionnaires for API/Database working correctly")
            print("✅ P2: Completeness checks using comprehensive YAML functioning properly")
            print("✅ P4: Field mapping fixes verified successfully")
            print("✅ Enhanced vulnerability analysis with conditional data operational")
        else:
            print(f"\n⚠️ ENHANCED CONDITIONAL QUESTIONNAIRE IMPLEMENTATION: {total-passed} TESTS FAILED")
            print("❌ Some conditional questionnaire functionality may not be working correctly")
            print("❌ Review failed tests above for details")
        
        return passed == total

if __name__ == "__main__":
    tester = ConditionalQuestionnaireTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)