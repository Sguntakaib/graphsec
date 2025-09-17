#!/usr/bin/env python3
"""
Phase 2 Questionnaire System Tests for Security Modeling Platform
Tests the newly implemented Phase 2 questionnaire system for three critical priority node types
"""

import requests
import json
import sys

# Use the production URL from review request
BASE_URL = "https://fullstack-impl-1.preview.emergentagent.com/api"

class Phase2QuestionnaireTester:
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

    def test_phase2_webapp_questionnaire_basic(self):
        """Test WebApp Basic questionnaire (Expected: 8 questions)"""
        try:
            response = self.session.get(f"{self.base_url}/questionnaires/WebApp?level=basic")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for required fields
                expected_fields = ["questions", "metadata", "level", "node_subtype"]
                missing_fields = [f for f in expected_fields if f not in data]
                
                if missing_fields:
                    self.log_test("Phase 2 WebApp Basic Questionnaire", False, f"Missing fields: {missing_fields}")
                    return False
                
                questions = data.get("questions", [])
                level = data.get("level", "")
                node_subtype = data.get("node_subtype", "")
                
                # Verify question count matches expected (8 for basic)
                expected_count = 8
                if len(questions) != expected_count:
                    self.log_test("Phase 2 WebApp Basic Questionnaire", False, 
                                f"Expected {expected_count} questions, got {len(questions)}")
                    return False
                
                # Verify level and subtype
                if level != "basic" or node_subtype != "WebApp":
                    self.log_test("Phase 2 WebApp Basic Questionnaire", False, 
                                f"Incorrect level ({level}) or subtype ({node_subtype})")
                    return False
                
                # Verify question structure and content quality
                if questions:
                    first_question = questions[0]
                    required_question_fields = ["id", "question", "type", "category"]
                    missing_question_fields = [f for f in required_question_fields if f not in first_question]
                    
                    if missing_question_fields:
                        self.log_test("Phase 2 WebApp Basic Questionnaire", False, 
                                    f"Missing question fields: {missing_question_fields}")
                        return False
                
                # Check for threat intelligence data
                metadata = data.get("metadata", {})
                threat_intelligence = metadata.get("threat_intelligence", {})
                
                self.log_test("Phase 2 WebApp Basic Questionnaire", True, 
                            f"✅ Basic level: {len(questions)} questions, threat intel: {bool(threat_intelligence)}")
                return True
            else:
                self.log_test("Phase 2 WebApp Basic Questionnaire", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Phase 2 WebApp Basic Questionnaire", False, f"Error: {str(e)}")
            return False

    def test_phase2_webapp_questionnaire_advanced(self):
        """Test WebApp Advanced questionnaire (Expected: 18 questions)"""
        try:
            response = self.session.get(f"{self.base_url}/questionnaires/WebApp?level=advanced")
            
            if response.status_code == 200:
                data = response.json()
                questions = data.get("questions", [])
                level = data.get("level", "")
                
                # Verify question count matches expected (18 for advanced)
                expected_count = 18
                if len(questions) != expected_count:
                    self.log_test("Phase 2 WebApp Advanced Questionnaire", False, 
                                f"Expected {expected_count} questions, got {len(questions)}")
                    return False
                
                if level != "advanced":
                    self.log_test("Phase 2 WebApp Advanced Questionnaire", False, 
                                f"Incorrect level: {level}")
                    return False
                
                self.log_test("Phase 2 WebApp Advanced Questionnaire", True, 
                            f"✅ Advanced level: {len(questions)} questions")
                return True
            else:
                self.log_test("Phase 2 WebApp Advanced Questionnaire", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Phase 2 WebApp Advanced Questionnaire", False, f"Error: {str(e)}")
            return False

    def test_phase2_webapp_questionnaire_expert(self):
        """Test WebApp Expert questionnaire (Expected: 28 questions)"""
        try:
            response = self.session.get(f"{self.base_url}/questionnaires/WebApp?level=expert")
            
            if response.status_code == 200:
                data = response.json()
                questions = data.get("questions", [])
                level = data.get("level", "")
                
                # Verify question count matches expected (28 for expert)
                expected_count = 28
                if len(questions) != expected_count:
                    self.log_test("Phase 2 WebApp Expert Questionnaire", False, 
                                f"Expected {expected_count} questions, got {len(questions)}")
                    return False
                
                if level != "expert":
                    self.log_test("Phase 2 WebApp Expert Questionnaire", False, 
                                f"Incorrect level: {level}")
                    return False
                
                self.log_test("Phase 2 WebApp Expert Questionnaire", True, 
                            f"✅ Expert level: {len(questions)} questions")
                return True
            else:
                self.log_test("Phase 2 WebApp Expert Questionnaire", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Phase 2 WebApp Expert Questionnaire", False, f"Error: {str(e)}")
            return False

    def test_phase2_api_questionnaire_basic(self):
        """Test API Basic questionnaire (Expected: 7 questions)"""
        try:
            response = self.session.get(f"{self.base_url}/questionnaires/API?level=basic")
            
            if response.status_code == 200:
                data = response.json()
                questions = data.get("questions", [])
                level = data.get("level", "")
                node_subtype = data.get("node_subtype", "")
                
                # Verify question count matches expected (7 for basic)
                expected_count = 7
                if len(questions) != expected_count:
                    self.log_test("Phase 2 API Basic Questionnaire", False, 
                                f"Expected {expected_count} questions, got {len(questions)}")
                    return False
                
                if level != "basic" or node_subtype != "API":
                    self.log_test("Phase 2 API Basic Questionnaire", False, 
                                f"Incorrect level ({level}) or subtype ({node_subtype})")
                    return False
                
                self.log_test("Phase 2 API Basic Questionnaire", True, 
                            f"✅ Basic level: {len(questions)} questions")
                return True
            else:
                self.log_test("Phase 2 API Basic Questionnaire", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Phase 2 API Basic Questionnaire", False, f"Error: {str(e)}")
            return False

    def test_phase2_api_questionnaire_advanced(self):
        """Test API Advanced questionnaire (Expected: 17 questions)"""
        try:
            response = self.session.get(f"{self.base_url}/questionnaires/API?level=advanced")
            
            if response.status_code == 200:
                data = response.json()
                questions = data.get("questions", [])
                level = data.get("level", "")
                
                # Verify question count matches expected (17 for advanced)
                expected_count = 17
                if len(questions) != expected_count:
                    self.log_test("Phase 2 API Advanced Questionnaire", False, 
                                f"Expected {expected_count} questions, got {len(questions)}")
                    return False
                
                if level != "advanced":
                    self.log_test("Phase 2 API Advanced Questionnaire", False, 
                                f"Incorrect level: {level}")
                    return False
                
                self.log_test("Phase 2 API Advanced Questionnaire", True, 
                            f"✅ Advanced level: {len(questions)} questions")
                return True
            else:
                self.log_test("Phase 2 API Advanced Questionnaire", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Phase 2 API Advanced Questionnaire", False, f"Error: {str(e)}")
            return False

    def test_phase2_api_questionnaire_expert(self):
        """Test API Expert questionnaire (Expected: 25 questions)"""
        try:
            response = self.session.get(f"{self.base_url}/questionnaires/API?level=expert")
            
            if response.status_code == 200:
                data = response.json()
                questions = data.get("questions", [])
                level = data.get("level", "")
                
                # Verify question count matches expected (25 for expert)
                expected_count = 25
                if len(questions) != expected_count:
                    self.log_test("Phase 2 API Expert Questionnaire", False, 
                                f"Expected {expected_count} questions, got {len(questions)}")
                    return False
                
                if level != "expert":
                    self.log_test("Phase 2 API Expert Questionnaire", False, 
                                f"Incorrect level: {level}")
                    return False
                
                self.log_test("Phase 2 API Expert Questionnaire", True, 
                            f"✅ Expert level: {len(questions)} questions")
                return True
            else:
                self.log_test("Phase 2 API Expert Questionnaire", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Phase 2 API Expert Questionnaire", False, f"Error: {str(e)}")
            return False

    def test_phase2_database_questionnaire_basic(self):
        """Test Database Basic questionnaire (Expected: 8 questions)"""
        try:
            response = self.session.get(f"{self.base_url}/questionnaires/Database?level=basic")
            
            if response.status_code == 200:
                data = response.json()
                questions = data.get("questions", [])
                level = data.get("level", "")
                node_subtype = data.get("node_subtype", "")
                
                # Verify question count matches expected (8 for basic)
                expected_count = 8
                if len(questions) != expected_count:
                    self.log_test("Phase 2 Database Basic Questionnaire", False, 
                                f"Expected {expected_count} questions, got {len(questions)}")
                    return False
                
                if level != "basic" or node_subtype != "Database":
                    self.log_test("Phase 2 Database Basic Questionnaire", False, 
                                f"Incorrect level ({level}) or subtype ({node_subtype})")
                    return False
                
                self.log_test("Phase 2 Database Basic Questionnaire", True, 
                            f"✅ Basic level: {len(questions)} questions")
                return True
            else:
                self.log_test("Phase 2 Database Basic Questionnaire", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Phase 2 Database Basic Questionnaire", False, f"Error: {str(e)}")
            return False

    def test_phase2_database_questionnaire_advanced(self):
        """Test Database Advanced questionnaire (Expected: 19 questions)"""
        try:
            response = self.session.get(f"{self.base_url}/questionnaires/Database?level=advanced")
            
            if response.status_code == 200:
                data = response.json()
                questions = data.get("questions", [])
                level = data.get("level", "")
                
                # Verify question count matches expected (19 for advanced)
                expected_count = 19
                if len(questions) != expected_count:
                    self.log_test("Phase 2 Database Advanced Questionnaire", False, 
                                f"Expected {expected_count} questions, got {len(questions)}")
                    return False
                
                if level != "advanced":
                    self.log_test("Phase 2 Database Advanced Questionnaire", False, 
                                f"Incorrect level: {level}")
                    return False
                
                self.log_test("Phase 2 Database Advanced Questionnaire", True, 
                            f"✅ Advanced level: {len(questions)} questions")
                return True
            else:
                self.log_test("Phase 2 Database Advanced Questionnaire", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Phase 2 Database Advanced Questionnaire", False, f"Error: {str(e)}")
            return False

    def test_phase2_database_questionnaire_expert(self):
        """Test Database Expert questionnaire (Expected: 27 questions)"""
        try:
            response = self.session.get(f"{self.base_url}/questionnaires/Database?level=expert")
            
            if response.status_code == 200:
                data = response.json()
                questions = data.get("questions", [])
                level = data.get("level", "")
                
                # Verify question count matches expected (27 for expert)
                expected_count = 27
                if len(questions) != expected_count:
                    self.log_test("Phase 2 Database Expert Questionnaire", False, 
                                f"Expected {expected_count} questions, got {len(questions)}")
                    return False
                
                if level != "expert":
                    self.log_test("Phase 2 Database Expert Questionnaire", False, 
                                f"Incorrect level: {level}")
                    return False
                
                self.log_test("Phase 2 Database Expert Questionnaire", True, 
                            f"✅ Expert level: {len(questions)} questions")
                return True
            else:
                self.log_test("Phase 2 Database Expert Questionnaire", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Phase 2 Database Expert Questionnaire", False, f"Error: {str(e)}")
            return False

    def test_phase2_questionnaire_structure_validation(self):
        """Test questionnaire structure and content quality across all levels"""
        try:
            test_cases = [
                ("WebApp", "basic"),
                ("API", "advanced"), 
                ("Database", "expert")
            ]
            
            for node_subtype, level in test_cases:
                response = self.session.get(f"{self.base_url}/questionnaires/{node_subtype}?level={level}")
                
                if response.status_code != 200:
                    self.log_test("Phase 2 Questionnaire Structure Validation", False, 
                                f"Failed to get {node_subtype} {level}: HTTP {response.status_code}")
                    return False
                
                data = response.json()
                questions = data.get("questions", [])
                
                # Validate question structure
                for i, question in enumerate(questions):
                    required_fields = ["id", "question", "type", "category"]
                    missing_fields = [f for f in required_fields if f not in question]
                    
                    if missing_fields:
                        self.log_test("Phase 2 Questionnaire Structure Validation", False, 
                                    f"{node_subtype} {level} Q{i+1} missing fields: {missing_fields}")
                        return False
                    
                    # Validate question content quality (security-focused)
                    question_text = question.get("question", "").lower()
                    security_keywords = ["security", "authentication", "encryption", "access", "vulnerability", 
                                       "threat", "risk", "compliance", "audit", "monitoring", "logging"]
                    
                    if not any(keyword in question_text for keyword in security_keywords):
                        self.log_test("Phase 2 Questionnaire Structure Validation", False, 
                                    f"{node_subtype} {level} Q{i+1} not security-focused: {question.get('question', '')}")
                        return False
                
                # Validate metadata and dependencies
                metadata = data.get("metadata", {})
                if not metadata:
                    self.log_test("Phase 2 Questionnaire Structure Validation", False, 
                                f"{node_subtype} {level} missing metadata")
                    return False
            
            self.log_test("Phase 2 Questionnaire Structure Validation", True, 
                        "✅ All questionnaires have proper structure and security-focused content")
            return True
            
        except Exception as e:
            self.log_test("Phase 2 Questionnaire Structure Validation", False, f"Error: {str(e)}")
            return False

    def test_phase2_3level_scaling_system(self):
        """Test the 3-level scaling system is working properly"""
        try:
            scaling_validation = []
            
            # Test WebApp scaling: Basic(8) -> Advanced(18) -> Expert(28)
            webapp_basic = self.session.get(f"{self.base_url}/questionnaires/WebApp?level=basic")
            webapp_advanced = self.session.get(f"{self.base_url}/questionnaires/WebApp?level=advanced")
            webapp_expert = self.session.get(f"{self.base_url}/questionnaires/WebApp?level=expert")
            
            if all(r.status_code == 200 for r in [webapp_basic, webapp_advanced, webapp_expert]):
                basic_count = len(webapp_basic.json().get("questions", []))
                advanced_count = len(webapp_advanced.json().get("questions", []))
                expert_count = len(webapp_expert.json().get("questions", []))
                
                if basic_count == 8 and advanced_count == 18 and expert_count == 28:
                    scaling_validation.append(f"WebApp: {basic_count}→{advanced_count}→{expert_count} ✅")
                else:
                    scaling_validation.append(f"WebApp: {basic_count}→{advanced_count}→{expert_count} ❌")
            
            # Test API scaling: Basic(7) -> Advanced(17) -> Expert(25)
            api_basic = self.session.get(f"{self.base_url}/questionnaires/API?level=basic")
            api_advanced = self.session.get(f"{self.base_url}/questionnaires/API?level=advanced")
            api_expert = self.session.get(f"{self.base_url}/questionnaires/API?level=expert")
            
            if all(r.status_code == 200 for r in [api_basic, api_advanced, api_expert]):
                basic_count = len(api_basic.json().get("questions", []))
                advanced_count = len(api_advanced.json().get("questions", []))
                expert_count = len(api_expert.json().get("questions", []))
                
                if basic_count == 7 and advanced_count == 17 and expert_count == 25:
                    scaling_validation.append(f"API: {basic_count}→{advanced_count}→{expert_count} ✅")
                else:
                    scaling_validation.append(f"API: {basic_count}→{advanced_count}→{expert_count} ❌")
            
            # Test Database scaling: Basic(8) -> Advanced(19) -> Expert(27)
            db_basic = self.session.get(f"{self.base_url}/questionnaires/Database?level=basic")
            db_advanced = self.session.get(f"{self.base_url}/questionnaires/Database?level=advanced")
            db_expert = self.session.get(f"{self.base_url}/questionnaires/Database?level=expert")
            
            if all(r.status_code == 200 for r in [db_basic, db_advanced, db_expert]):
                basic_count = len(db_basic.json().get("questions", []))
                advanced_count = len(db_advanced.json().get("questions", []))
                expert_count = len(db_expert.json().get("questions", []))
                
                if basic_count == 8 and advanced_count == 19 and expert_count == 27:
                    scaling_validation.append(f"Database: {basic_count}→{advanced_count}→{expert_count} ✅")
                else:
                    scaling_validation.append(f"Database: {basic_count}→{advanced_count}→{expert_count} ❌")
            
            # Check if all scaling is correct
            all_correct = all("✅" in validation for validation in scaling_validation)
            
            if all_correct:
                self.log_test("Phase 2 3-Level Scaling System", True, 
                            f"✅ 3-level scaling working: {'; '.join(scaling_validation)}")
                return True
            else:
                self.log_test("Phase 2 3-Level Scaling System", False, 
                            f"❌ Scaling issues: {'; '.join(scaling_validation)}")
                return False
            
        except Exception as e:
            self.log_test("Phase 2 3-Level Scaling System", False, f"Error: {str(e)}")
            return False

    def run_phase2_tests(self):
        """Run all Phase 2 questionnaire tests"""
        print("🚀 Starting Phase 2 Questionnaire System Tests")
        print("=" * 60)
        
        tests = [
            self.test_phase2_webapp_questionnaire_basic,
            self.test_phase2_webapp_questionnaire_advanced,
            self.test_phase2_webapp_questionnaire_expert,
            self.test_phase2_api_questionnaire_basic,
            self.test_phase2_api_questionnaire_advanced,
            self.test_phase2_api_questionnaire_expert,
            self.test_phase2_database_questionnaire_basic,
            self.test_phase2_database_questionnaire_advanced,
            self.test_phase2_database_questionnaire_expert,
            self.test_phase2_questionnaire_structure_validation,
            self.test_phase2_3level_scaling_system
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
            except Exception as e:
                print(f"❌ Test {test.__name__} crashed: {str(e)}")
            print("-" * 40)
        
        print("=" * 60)
        print(f"📊 Phase 2 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All Phase 2 questionnaire tests passed!")
            return True
        else:
            print(f"⚠️  {total - passed} tests failed. See details above.")
            return False

if __name__ == "__main__":
    tester = Phase2QuestionnaireTester()
    success = tester.run_phase2_tests()
    sys.exit(0 if success else 1)