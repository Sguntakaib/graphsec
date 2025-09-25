#!/usr/bin/env python3
"""
Review Request Tests - Phase 2 Questionnaire System
Tests the specific endpoints requested in the review request
"""

import requests
import json

# Use the production URL from review request
BASE_URL = "https://enhance-planner.preview.emergentagent.com/api"

class ReviewRequestTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, success, message=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message
        })

    def test_primary_endpoint(self):
        """Test GET /api/questionnaires/{node_subtype}?level={level} - PRIMARY ENDPOINT"""
        test_cases = [
            # WebApp tests
            {"node_subtype": "WebApp", "level": "basic", "expected_count": 8},
            {"node_subtype": "WebApp", "level": "advanced", "expected_count": 18},
            {"node_subtype": "WebApp", "level": "expert", "expected_count": 28},
            # API tests
            {"node_subtype": "API", "level": "basic", "expected_count": 7},
            # Database tests
            {"node_subtype": "Database", "level": "basic", "expected_count": 8},
        ]
        
        all_passed = True
        
        for test_case in test_cases:
            node_subtype = test_case["node_subtype"]
            level = test_case["level"]
            expected_count = test_case["expected_count"]
            
            try:
                response = self.session.get(f"{self.base_url}/questionnaires/{node_subtype}?level={level}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check required response fields
                    required_fields = ["questions", "question_count", "level", "node_subtype", "security_branches", "metadata"]
                    missing_fields = [f for f in required_fields if f not in data]
                    
                    if missing_fields:
                        self.log_test(f"PRIMARY {node_subtype} {level}", False, 
                                    f"Missing required fields: {missing_fields}")
                        all_passed = False
                        continue
                    
                    # Verify question count matches expected
                    actual_count = data.get("question_count", 0)
                    questions = data.get("questions", [])
                    
                    if actual_count != expected_count:
                        self.log_test(f"PRIMARY {node_subtype} {level}", False, 
                                    f"Expected {expected_count} questions, got {actual_count}")
                        all_passed = False
                        continue
                    
                    if len(questions) != expected_count:
                        self.log_test(f"PRIMARY {node_subtype} {level}", False, 
                                    f"Questions array length {len(questions)} doesn't match question_count {actual_count}")
                        all_passed = False
                        continue
                    
                    # Verify level and node_subtype match request
                    if data.get("level") != level:
                        self.log_test(f"PRIMARY {node_subtype} {level}", False, 
                                    f"Level mismatch: expected {level}, got {data.get('level')}")
                        all_passed = False
                        continue
                    
                    if data.get("node_subtype") != node_subtype:
                        self.log_test(f"PRIMARY {node_subtype} {level}", False, 
                                    f"Node subtype mismatch: expected {node_subtype}, got {data.get('node_subtype')}")
                        all_passed = False
                        continue
                    
                    # Verify security_branches field is present
                    security_branches = data.get("security_branches", [])
                    if not isinstance(security_branches, list):
                        self.log_test(f"PRIMARY {node_subtype} {level}", False, 
                                    f"security_branches should be a list, got {type(security_branches)}")
                        all_passed = False
                        continue
                    
                    # Verify metadata field with threat intelligence
                    metadata = data.get("metadata", {})
                    if not isinstance(metadata, dict):
                        self.log_test(f"PRIMARY {node_subtype} {level}", False, 
                                    f"metadata should be a dict, got {type(metadata)}")
                        all_passed = False
                        continue
                    
                    # Verify questions have proper structure
                    if questions:
                        first_question = questions[0]
                        question_fields = ["id", "question", "type"]
                        missing_question_fields = [f for f in question_fields if f not in first_question]
                        
                        if missing_question_fields:
                            self.log_test(f"PRIMARY {node_subtype} {level}", False, 
                                        f"Questions missing fields: {missing_question_fields}")
                            all_passed = False
                            continue
                    
                    self.log_test(f"PRIMARY {node_subtype} {level}", True, 
                                f"✅ {actual_count} questions, security_branches present, metadata included")
                    
                elif response.status_code == 404:
                    self.log_test(f"PRIMARY {node_subtype} {level}", False, 
                                f"Questionnaire not found (404) - should be available")
                    all_passed = False
                else:
                    self.log_test(f"PRIMARY {node_subtype} {level}", False, 
                                f"HTTP {response.status_code}: {response.text}")
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"PRIMARY {node_subtype} {level}", False, f"Error: {str(e)}")
                all_passed = False
        
        return all_passed

    def test_alternative_endpoint(self):
        """Test GET /api/expanded-nodes/{node_subtype}/questionnaire/{level} - ALTERNATIVE ENDPOINT"""
        test_cases = [
            # WebApp tests
            {"node_subtype": "WebApp", "level": "basic", "expected_count": 8},
            {"node_subtype": "WebApp", "level": "advanced", "expected_count": 18},
            {"node_subtype": "WebApp", "level": "expert", "expected_count": 28},
            # API tests
            {"node_subtype": "API", "level": "basic", "expected_count": 7},
            # Database tests
            {"node_subtype": "Database", "level": "basic", "expected_count": 8},
        ]
        
        all_passed = True
        
        for test_case in test_cases:
            node_subtype = test_case["node_subtype"]
            level = test_case["level"]
            expected_count = test_case["expected_count"]
            
            try:
                response = self.session.get(f"{self.base_url}/expanded-nodes/{node_subtype}/questionnaire/{level}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check required response fields (may differ from primary endpoint)
                    required_fields = ["questions", "question_count", "level", "node_subtype"]
                    missing_fields = [f for f in required_fields if f not in data]
                    
                    if missing_fields:
                        self.log_test(f"ALTERNATIVE {node_subtype} {level}", False, 
                                    f"Missing required fields: {missing_fields}")
                        all_passed = False
                        continue
                    
                    # Verify question count matches expected
                    actual_count = data.get("question_count", 0)
                    questions = data.get("questions", [])
                    
                    if actual_count != expected_count:
                        self.log_test(f"ALTERNATIVE {node_subtype} {level}", False, 
                                    f"Expected {expected_count} questions, got {actual_count}")
                        all_passed = False
                        continue
                    
                    if len(questions) != expected_count:
                        self.log_test(f"ALTERNATIVE {node_subtype} {level}", False, 
                                    f"Questions array length {len(questions)} doesn't match question_count {actual_count}")
                        all_passed = False
                        continue
                    
                    # Verify level and node_subtype match request
                    if data.get("level") != level:
                        self.log_test(f"ALTERNATIVE {node_subtype} {level}", False, 
                                    f"Level mismatch: expected {level}, got {data.get('level')}")
                        all_passed = False
                        continue
                    
                    if data.get("node_subtype") != node_subtype:
                        self.log_test(f"ALTERNATIVE {node_subtype} {level}", False, 
                                    f"Node subtype mismatch: expected {node_subtype}, got {data.get('node_subtype')}")
                        all_passed = False
                        continue
                    
                    # Check for threat intelligence data (may be in different field)
                    has_threat_intel = "threat_intelligence" in data or "metadata" in data
                    if not has_threat_intel:
                        self.log_test(f"ALTERNATIVE {node_subtype} {level}", False, 
                                    "Missing threat intelligence data")
                        all_passed = False
                        continue
                    
                    # Verify questions have proper structure
                    if questions:
                        first_question = questions[0]
                        question_fields = ["id", "question", "type"]
                        missing_question_fields = [f for f in question_fields if f not in first_question]
                        
                        if missing_question_fields:
                            self.log_test(f"ALTERNATIVE {node_subtype} {level}", False, 
                                        f"Questions missing fields: {missing_question_fields}")
                            all_passed = False
                            continue
                    
                    self.log_test(f"ALTERNATIVE {node_subtype} {level}", True, 
                                f"✅ {actual_count} questions, threat intelligence present")
                    
                elif response.status_code == 404:
                    self.log_test(f"ALTERNATIVE {node_subtype} {level}", False, 
                                f"Questionnaire not found (404) - should be available")
                    all_passed = False
                else:
                    self.log_test(f"ALTERNATIVE {node_subtype} {level}", False, 
                                f"HTTP {response.status_code}: {response.text}")
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"ALTERNATIVE {node_subtype} {level}", False, f"Error: {str(e)}")
                all_passed = False
        
        return all_passed

    def test_format_comparison(self):
        """Compare response formats between primary and alternative endpoints"""
        test_case = {"node_subtype": "API", "level": "basic"}  # Use API since it's working
        
        try:
            # Get responses from both endpoints
            primary_response = self.session.get(f"{self.base_url}/questionnaires/{test_case['node_subtype']}?level={test_case['level']}")
            alternative_response = self.session.get(f"{self.base_url}/expanded-nodes/{test_case['node_subtype']}/questionnaire/{test_case['level']}")
            
            if primary_response.status_code == 200 and alternative_response.status_code == 200:
                primary_data = primary_response.json()
                alternative_data = alternative_response.json()
                
                # Compare core fields
                core_fields = ["questions", "question_count", "level", "node_subtype"]
                differences = []
                
                for field in core_fields:
                    primary_value = primary_data.get(field)
                    alternative_value = alternative_data.get(field)
                    
                    if primary_value != alternative_value:
                        differences.append(f"{field}: primary={primary_value}, alternative={alternative_value}")
                
                # Check unique fields
                primary_only = set(primary_data.keys()) - set(alternative_data.keys())
                alternative_only = set(alternative_data.keys()) - set(primary_data.keys())
                
                if primary_only:
                    differences.append(f"Primary-only fields: {list(primary_only)}")
                if alternative_only:
                    differences.append(f"Alternative-only fields: {list(alternative_only)}")
                
                if differences:
                    self.log_test("FORMAT COMPARISON", True, 
                                f"Format differences found: {'; '.join(differences)}")
                else:
                    self.log_test("FORMAT COMPARISON", True, 
                                "Response formats are identical")
                
                return True
            else:
                self.log_test("FORMAT COMPARISON", False, 
                            f"Failed to get responses: primary={primary_response.status_code}, alternative={alternative_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("FORMAT COMPARISON", False, f"Error: {str(e)}")
            return False

    def run_tests(self):
        """Run all review request tests"""
        print("🚀 PHASE 2 QUESTIONNAIRE SYSTEM ENDPOINT TESTING")
        print(f"Backend URL: {self.base_url}")
        print("=" * 80)
        
        print("\n🎯 TESTING PRIMARY ENDPOINT: GET /api/questionnaires/{node_subtype}?level={level}")
        print("-" * 80)
        result1 = self.test_primary_endpoint()
        
        print("\n🎯 TESTING ALTERNATIVE ENDPOINT: GET /api/expanded-nodes/{node_subtype}/questionnaire/{level}")
        print("-" * 80)
        result2 = self.test_alternative_endpoint()
        
        print("\n🎯 TESTING RESPONSE FORMAT COMPARISON")
        print("-" * 80)
        result3 = self.test_format_comparison()
        
        print("\n" + "=" * 80)
        print("📊 FINAL TEST RESULTS:")
        print(f"Primary Endpoint Tests: {'✅ PASS' if result1 else '❌ FAIL'}")
        print(f"Alternative Endpoint Tests: {'✅ PASS' if result2 else '❌ FAIL'}")
        print(f"Format Comparison: {'✅ PASS' if result3 else '❌ FAIL'}")
        
        total_passed = sum([result1, result2, result3])
        print(f"\nOverall: {total_passed}/3 test suites passed")
        
        return total_passed == 3

if __name__ == "__main__":
    tester = ReviewRequestTester()
    success = tester.run_tests()
    exit(0 if success else 1)