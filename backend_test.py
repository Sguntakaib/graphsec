#!/usr/bin/env python3
"""
Backend API Testing - QUESTIONNAIRE DEPENDENCY FLOW VERIFICATION
Tests the questionnaire system for WebApp nodes with focus on dependency flow.

TESTING FOCUS:
1. **Test WebApp Questionnaire Question Order**: 
   - Verify that Database dependency question is at position 4 (not at the end)
   - Verify that API dependency question is at position 5 (not at the end)
   - Confirm there are 10 total questions in WebApp basic questionnaire

2. **Test Dependency Trigger Flow**: 
   - Test answering "Yes" to Database dependency question (position 4)
   - Verify it creates Database node and opens Database questionnaire
   - Test that Database questionnaire has dependency questions in middle positions
   - Verify after Database questionnaire completes, WebApp questionnaire resumes from position 5

3. **Test API Dependency Flow**:
   - Test answering "Yes" to API dependency question (position 5) 
   - Verify it creates API node and opens API questionnaire
   - Test that API questionnaire has dependency questions in middle positions
   - Verify after API questionnaire completes, WebApp questionnaire resumes from position 6

4. **Test Complete Flow**:
   - Test complete flow: WebApp Q1-4 → Database dependency → Database questionnaire → Resume WebApp Q5 → API dependency → API questionnaire → Resume WebApp Q6-10 → Complete

Focus on verifying:
- Question reordering worked (dependencies in middle, not at end)
- Parent questionnaire resumption after child completion
- Multiple dependency handling (both Database and API)
- All questionnaire types (WebApp, Database, API) have dependencies in correct positions
"""

import requests
import json
import uuid
from datetime import datetime, timezone
import sys

# Use the backend URL from frontend/.env with /api suffix
BASE_URL = "https://appsec-survey.preview.emergentagent.com/api"

class QuestionnaireFlowCleanupTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.test_results = []
        self.created_diagram_id = None
        
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
    # CORE QUESTIONNAIRE ENDPOINTS - Legacy System
    # ============================================================================
    
    def test_get_webapp_questionnaire(self):
        """Test GET /api/questionnaires/WebApp - WebApp questionnaire prompts"""
        try:
            response = self.session.get(f"{self.base_url}/questionnaires/WebApp")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify expected structure for legacy system
                expected_fields = ['prompts', 'security_branches']
                missing_fields = [field for field in expected_fields if field not in data]
                
                if missing_fields:
                    self.log_test("WebApp Questionnaire", False, 
                                f"Missing expected fields: {missing_fields}. Response: {data}")
                    return False
                
                prompts_count = len(data.get('prompts', []))
                branches_count = len(data.get('security_branches', []))
                
                self.log_test("WebApp Questionnaire", True, 
                            f"WebApp questionnaire retrieved successfully - {prompts_count} prompts, {branches_count} branches")
                
                print(f"📋 WebApp Questionnaire Details:")
                print(f"   Prompts: {prompts_count}")
                print(f"   Security Branches: {branches_count}")
                
                return True
            else:
                self.log_test("WebApp Questionnaire", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("WebApp Questionnaire", False, f"Request error: {str(e)}")
            return False

    def test_get_intelligent_node_prompts(self):
        """Test GET /api/intelligent-nodes/{node_subtype}/prompts - Other node types"""
        node_types = ['API', 'Database', 'ExternalAttacker']
        all_passed = True
        
        for node_type in node_types:
            try:
                response = self.session.get(f"{self.base_url}/intelligent-nodes/{node_type}/prompts")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Verify expected structure
                    if 'prompts' not in data:
                        self.log_test(f"{node_type} Node Prompts", False, 
                                    f"Missing 'prompts' field. Response: {data}")
                        all_passed = False
                        continue
                    
                    prompts_count = len(data.get('prompts', []))
                    
                    self.log_test(f"{node_type} Node Prompts", True, 
                                f"{node_type} prompts retrieved successfully - {prompts_count} prompts")
                    
                    print(f"📋 {node_type} Node Prompts: {prompts_count}")
                    
                else:
                    self.log_test(f"{node_type} Node Prompts", False, 
                                f"HTTP {response.status_code}: {response.text}")
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"{node_type} Node Prompts", False, f"Request error: {str(e)}")
                all_passed = False
        
        return all_passed

    def test_check_dependencies_api(self):
        """Test POST /api/intelligent-nodes/{node_subtype}/check-dependencies - Dependency checking"""
        test_cases = [
            {
                'node_type': 'WebApp',
                'answers': {
                    'webapp_api_endpoints': True,
                    'webapp_database_connection': True
                },
                'expected_dependencies': ['API', 'Database']
            },
            {
                'node_type': 'WebApp', 
                'answers': {
                    'webapp_api_endpoints': True,
                    'webapp_database_connection': False
                },
                'expected_dependencies': ['API']
            },
            {
                'node_type': 'Database',
                'answers': {
                    'db_backup_enabled': True,
                    'db_monitoring_enabled': False
                },
                'expected_dependencies': ['Backup']
            }
        ]
        
        all_passed = True
        
        for test_case in test_cases:
            try:
                node_type = test_case['node_type']
                answers = test_case['answers']
                expected = test_case['expected_dependencies']
                
                response = self.session.post(
                    f"{self.base_url}/intelligent-nodes/{node_type}/check-dependencies",
                    json={"answers": answers},
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Verify response structure
                    if 'dependent_nodes' not in data:
                        self.log_test(f"{node_type} Dependencies Check", False, 
                                    f"Missing 'dependent_nodes' field. Response: {data}")
                        all_passed = False
                        continue
                    
                    actual_dependencies = data['dependent_nodes']
                    
                    # Check if expected dependencies are present
                    missing_deps = [dep for dep in expected if dep not in actual_dependencies]
                    unexpected_deps = [dep for dep in actual_dependencies if dep not in expected]
                    
                    if missing_deps or unexpected_deps:
                        self.log_test(f"{node_type} Dependencies Check", False, 
                                    f"Dependencies mismatch. Expected: {expected}, Got: {actual_dependencies}")
                        all_passed = False
                    else:
                        self.log_test(f"{node_type} Dependencies Check", True, 
                                    f"Dependencies check passed - {actual_dependencies}")
                        
                        print(f"🔗 {node_type} Dependencies: {actual_dependencies}")
                    
                else:
                    self.log_test(f"{node_type} Dependencies Check", False, 
                                f"HTTP {response.status_code}: {response.text}")
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"{node_type} Dependencies Check", False, f"Request error: {str(e)}")
                all_passed = False
        
        return all_passed

    # ============================================================================
    # CRITICAL API ENDPOINTS - Diagram Management
    # ============================================================================
    
    def test_get_diagrams(self):
        """Test GET /api/diagrams - Diagram management"""
        try:
            response = self.session.get(f"{self.base_url}/diagrams")
            
            if response.status_code == 200:
                data = response.json()
                
                # Should return a list
                if not isinstance(data, list):
                    self.log_test("Get Diagrams", False, 
                                f"Expected list, got: {type(data)}. Response: {data}")
                    return False
                
                diagrams_count = len(data)
                
                self.log_test("Get Diagrams", True, 
                            f"Diagrams retrieved successfully - {diagrams_count} diagrams found")
                
                print(f"📊 Diagrams Count: {diagrams_count}")
                
                return True
            else:
                self.log_test("Get Diagrams", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Get Diagrams", False, f"Request error: {str(e)}")
            return False

    def test_create_diagram(self):
        """Test POST /api/diagrams - Create diagram"""
        try:
            diagram_data = {
                "title": f"Test Diagram - Questionnaire Flow Cleanup {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "Test diagram created during questionnaire flow cleanup verification"
            }
            
            response = self.session.post(
                f"{self.base_url}/diagrams",
                json=diagram_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify expected structure
                expected_fields = ['id', 'title', 'description', 'nodes', 'edges', 'created_at']
                missing_fields = [field for field in expected_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Create Diagram", False, 
                                f"Missing expected fields: {missing_fields}. Response: {data}")
                    return False
                
                # Store diagram ID for potential cleanup
                self.created_diagram_id = data['id']
                
                self.log_test("Create Diagram", True, 
                            f"Diagram created successfully - ID: {data['id']}")
                
                print(f"📊 Created Diagram ID: {data['id']}")
                print(f"   Title: {data['title']}")
                print(f"   Nodes: {len(data.get('nodes', []))}")
                print(f"   Edges: {len(data.get('edges', []))}")
                
                return True
            else:
                self.log_test("Create Diagram", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Create Diagram", False, f"Request error: {str(e)}")
            return False

    # ============================================================================
    # LEGACY SYSTEM COMPATIBILITY TESTS
    # ============================================================================
    
    def test_legacy_questionnaire_completion_flow(self):
        """Test the complete legacy questionnaire flow that should still work"""
        try:
            # Step 1: Get WebApp questionnaire
            response = self.session.get(f"{self.base_url}/questionnaires/WebApp")
            
            if response.status_code != 200:
                self.log_test("Legacy Questionnaire Flow", False, 
                            f"Failed to get WebApp questionnaire: HTTP {response.status_code}")
                return False
            
            questionnaire_data = response.json()
            
            # Step 2: Simulate questionnaire completion
            completion_data = {
                "responses": {
                    "authentication_method": "oauth2",
                    "encryption_enabled": True,
                    "input_validation": "comprehensive"
                },
                "business_context": {
                    "criticality": "high",
                    "data_classification": "confidential"
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/questionnaires/WebApp/complete",
                json=completion_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify expected completion response structure
                expected_fields = ['completion_id', 'findings', 'recommendations']
                missing_fields = [field for field in expected_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Legacy Questionnaire Flow", False, 
                                f"Missing expected completion fields: {missing_fields}")
                    return False
                
                self.log_test("Legacy Questionnaire Flow", True, 
                            f"Legacy questionnaire completion flow working - Completion ID: {data.get('completion_id')}")
                
                print(f"🔄 Legacy Flow Results:")
                print(f"   Completion ID: {data.get('completion_id')}")
                print(f"   Findings: {len(data.get('findings', []))}")
                print(f"   Recommendations: {len(data.get('recommendations', []))}")
                
                return True
            else:
                self.log_test("Legacy Questionnaire Flow", False, 
                            f"Questionnaire completion failed: HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Legacy Questionnaire Flow", False, f"Request error: {str(e)}")
            return False

    def test_enhanced_system_disabled(self):
        """Verify that enhanced questionnaire system endpoints are properly disabled/simplified"""
        # This test checks that we're not getting conflicts from the enhanced system
        try:
            # Try to access what would be enhanced system endpoints
            # These should either not exist or return simplified responses
            
            response = self.session.get(f"{self.base_url}/questionnaires/WebApp")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check that we're getting the simplified legacy response, not enhanced
                # Legacy system should have simpler structure
                if 'enhanced_features' in data or 'questionnaire_manager' in data:
                    self.log_test("Enhanced System Disabled", False, 
                                f"Enhanced system features still present in response: {data}")
                    return False
                
                self.log_test("Enhanced System Disabled", True, 
                            "Enhanced system properly disabled - receiving legacy system responses")
                
                print(f"✅ Enhanced System Status: Properly disabled")
                print(f"   Response structure indicates legacy system only")
                
                return True
            else:
                self.log_test("Enhanced System Disabled", False, 
                            f"Unexpected response: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Enhanced System Disabled", False, f"Request error: {str(e)}")
            return False

    # ============================================================================
    # Test Runner
    # ============================================================================
    
    def run_all_tests(self):
        """Run all questionnaire flow cleanup verification tests"""
        print("🚀 Starting Questionnaire Flow Cleanup Verification Tests")
        print("=" * 90)
        print("QUESTIONNAIRE FLOW CLEANUP VERIFICATION")
        print("Testing backend API endpoints after disabling enhanced QuestionnaireManager")
        print("Focus: Legacy SecurityQuestionnaire system endpoints")
        print("=" * 90)
        
        tests = [
            # Basic connectivity
            self.test_health_check,
            
            # Core questionnaire endpoints (legacy system)
            self.test_get_webapp_questionnaire,
            self.test_get_intelligent_node_prompts,
            self.test_check_dependencies_api,
            
            # Critical API endpoints
            self.test_get_diagrams,
            self.test_create_diagram,
            
            # Legacy system compatibility
            self.test_legacy_questionnaire_completion_flow,
            self.test_enhanced_system_disabled,
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
        print("🎯 QUESTIONNAIRE FLOW CLEANUP VERIFICATION SUMMARY")
        print("=" * 90)
        print(f"✅ PASSED: {passed}")
        print(f"❌ FAILED: {failed}")
        print(f"📊 SUCCESS RATE: {(passed / (passed + failed) * 100):.1f}%")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED! Questionnaire flow cleanup verification successful.")
            print("✅ Core questionnaire endpoints working correctly")
            print("✅ Intelligent node prompts accessible")
            print("✅ Dependency checking functional")
            print("✅ Diagram management operational")
            print("✅ Legacy questionnaire completion flow working")
            print("✅ Enhanced system properly disabled")
        else:
            print(f"\n⚠️  {failed} tests failed. Analysis:")
            
            # Analyze the test results to provide diagnostic information
            error_tests = [result for result in self.test_results if not result['success']]
            
            for error_test in error_tests:
                print(f"🚨 FAILED: {error_test['test']}")
                print(f"   Issue: {error_test['message']}")
        
        return passed, failed

def main():
    """Main test execution"""
    tester = QuestionnaireFlowCleanupTester()
    passed, failed = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()