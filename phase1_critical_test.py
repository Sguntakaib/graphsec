#!/usr/bin/env python3
"""
Phase 1 Core Loop Critical Endpoints Test
Tests the 4 critical Phase 1 Core Loop endpoints that were previously marked as "CRITICAL ENDPOINT FIXED"
"""

import requests
import json
import sys

# Use the production URL from review request
BASE_URL = "https://iprove-reader.preview.emergentagent.com/api"

class Phase1CriticalEndpointTester:
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
        
    def test_phase1_questionnaire_complete_endpoint(self):
        """Test POST /api/questionnaires/{node_subtype}/complete - Critical Phase 1 endpoint"""
        try:
            # Test data structure from review request
            test_data = {
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
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for expected response fields (updated based on actual API response)
                expected_fields = ["findings", "recommendations"]  # Core required fields
                missing_fields = [f for f in expected_fields if f not in data]
                
                if missing_fields:
                    self.log_test("Phase 1 - Questionnaire Complete", False, 
                                f"Missing expected fields: {missing_fields}. Got: {list(data.keys())}")
                    return False
                
                findings = data.get("findings", [])
                recommendations = data.get("recommendations", [])
                
                self.log_test("Phase 1 - Questionnaire Complete", True, 
                            f"Standalone questionnaire completion working: {len(findings)} findings, {len(recommendations)} recommendations")
                return True
            else:
                self.log_test("Phase 1 - Questionnaire Complete", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Phase 1 - Questionnaire Complete", False, f"Error: {str(e)}")
            return False
    
    def test_phase1_questionnaire_get_endpoint(self):
        """Test GET /api/questionnaires/{node_subtype} - Critical Phase 1 endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/questionnaires/WebApp")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for security_branches field specifically
                if "security_branches" not in data:
                    self.log_test("Phase 1 - Questionnaire Get", False, 
                                f"Missing security_branches field. Got: {list(data.keys())}")
                    return False
                
                # Check for prompts field
                if "prompts" not in data:
                    self.log_test("Phase 1 - Questionnaire Get", False, 
                                f"Missing prompts field. Got: {list(data.keys())}")
                    return False
                
                security_branches = data.get("security_branches", [])
                prompts = data.get("prompts", [])
                
                self.log_test("Phase 1 - Questionnaire Get", True, 
                            f"Questionnaire endpoint working: {len(security_branches)} branches, {len(prompts)} prompts")
                return True
            else:
                self.log_test("Phase 1 - Questionnaire Get", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Phase 1 - Questionnaire Get", False, f"Error: {str(e)}")
            return False
    
    def test_phase1_simulate_endpoint(self):
        """Test POST /api/simulate - Critical Phase 1 standalone simulation endpoint"""
        try:
            # Test standalone simulation with nodes/edges data structure
            test_data = {
                "nodes": [
                    {
                        "id": "actor1",
                        "type": "Actor",
                        "subtype": "ExternalAttacker",
                        "label": "External Attacker",
                        "position": {"x": 100, "y": 100}
                    },
                    {
                        "id": "asset1",
                        "type": "Asset",
                        "subtype": "WebApp",
                        "label": "Web Application",
                        "position": {"x": 300, "y": 100}
                    },
                    {
                        "id": "surface1",
                        "type": "Surface",
                        "subtype": "SQLi",
                        "label": "SQL Injection",
                        "position": {"x": 200, "y": 150}
                    }
                ],
                "edges": [
                    {
                        "id": "edge1",
                        "source": "actor1",
                        "target": "surface1",
                        "label": "Exploits"
                    },
                    {
                        "id": "edge2",
                        "source": "surface1",
                        "target": "asset1",
                        "label": "Compromises"
                    }
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/simulate",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for expected response fields
                expected_fields = ["simulation_id", "attack_paths", "risk_analysis", "mitre_techniques", "recommendations"]
                missing_fields = [f for f in expected_fields if f not in data]
                
                if missing_fields:
                    self.log_test("Phase 1 - Simulate Standalone", False, 
                                f"Missing expected fields: {missing_fields}. Got: {list(data.keys())}")
                    return False
                
                simulation_id = data.get("simulation_id")
                attack_paths = data.get("attack_paths", [])
                risk_analysis = data.get("risk_analysis", {})
                mitre_techniques = data.get("mitre_techniques", [])
                recommendations = data.get("recommendations", [])
                
                if not simulation_id:
                    self.log_test("Phase 1 - Simulate Standalone", False, "Missing simulation_id")
                    return False
                
                self.log_test("Phase 1 - Simulate Standalone", True, 
                            f"Standalone simulation working: ID={simulation_id}, {len(attack_paths)} paths, {len(mitre_techniques)} techniques, {len(recommendations)} recommendations")
                return True
            else:
                self.log_test("Phase 1 - Simulate Standalone", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Phase 1 - Simulate Standalone", False, f"Error: {str(e)}")
            return False
    
    def test_phase1_rules_evaluate_endpoint(self):
        """Test POST /api/rules/evaluate - Critical Phase 1 standalone rule evaluation endpoint"""
        try:
            # Test standalone rule evaluation
            test_data = {
                "nodes": [
                    {
                        "id": "webapp1",
                        "type": "Asset",
                        "subtype": "WebApp",
                        "label": "Web Application",
                        "data": {"encryption": "none", "authentication": "basic"}
                    },
                    {
                        "id": "db1",
                        "type": "Asset",
                        "subtype": "Database",
                        "label": "Database",
                        "data": {"encryption_at_rest": "disabled", "access_control": "weak"}
                    }
                ],
                "edges": [
                    {
                        "id": "edge1",
                        "source": "webapp1",
                        "target": "db1",
                        "label": "Connects to"
                    }
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/rules/evaluate",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for expected response fields
                expected_fields = ["evaluation_id", "triggered_rules", "risk_score", "recommendations"]
                missing_fields = [f for f in expected_fields if f not in data]
                
                if missing_fields:
                    self.log_test("Phase 1 - Rules Evaluate", False, 
                                f"Missing expected fields: {missing_fields}. Got: {list(data.keys())}")
                    return False
                
                evaluation_id = data.get("evaluation_id")
                triggered_rules = data.get("triggered_rules", [])
                risk_score = data.get("risk_score", 0)
                recommendations = data.get("recommendations", [])
                
                if not evaluation_id:
                    self.log_test("Phase 1 - Rules Evaluate", False, "Missing evaluation_id")
                    return False
                
                # Verify no RuleEvaluationResult attribute errors
                if isinstance(triggered_rules, list) and len(triggered_rules) > 0:
                    first_rule = triggered_rules[0]
                    if not isinstance(first_rule, dict):
                        self.log_test("Phase 1 - Rules Evaluate", False, 
                                    f"Invalid triggered_rules format: {type(first_rule)}")
                        return False
                
                self.log_test("Phase 1 - Rules Evaluate", True, 
                            f"Standalone rule evaluation working: ID={evaluation_id}, {len(triggered_rules)} rules triggered, risk_score={risk_score}, {len(recommendations)} recommendations")
                return True
            else:
                self.log_test("Phase 1 - Rules Evaluate", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Phase 1 - Rules Evaluate", False, f"Error: {str(e)}")
            return False

    def run_critical_tests(self):
        """Run all Phase 1 critical endpoint tests"""
        print("🎯 Starting Phase 1 Core Loop Critical Endpoints Testing")
        print(f"Testing against: {self.base_url}")
        print("=" * 80)
        
        # Critical endpoint tests in priority order
        tests = [
            self.test_phase1_questionnaire_complete_endpoint,
            self.test_phase1_questionnaire_get_endpoint,
            self.test_phase1_simulate_endpoint,
            self.test_phase1_rules_evaluate_endpoint
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
        
        print("=" * 80)
        print(f"🎯 Phase 1 Critical Test Results: {passed} passed, {failed} failed")
        print(f"📊 Success Rate: {(passed / (passed + failed)) * 100:.1f}%")
        
        if failed > 0:
            print("\n❌ Failed Critical Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        return passed, failed

if __name__ == "__main__":
    tester = Phase1CriticalEndpointTester()
    passed, failed = tester.run_critical_tests()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)