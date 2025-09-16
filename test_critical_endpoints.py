#!/usr/bin/env python3
"""
Critical Endpoints Test for Phase 1 Core Loop
Tests the 4 critical endpoints that were fixed
"""

import requests
import json
import sys

# Use the production URL from review request
BASE_URL = "https://auto-test-fix.preview.emergentagent.com/api"

class CriticalEndpointsTester:
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

    def test_questionnaire_completion_standalone(self):
        """Test POST /api/questionnaires/WebApp/complete in standalone mode"""
        try:
            # Use exact data structure from review request
            request_data = {
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
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for expected response fields
                expected_fields = ["completion_id", "findings", "risk_assessment", "recommendations"]
                missing_fields = [f for f in expected_fields if f not in data]
                
                if missing_fields:
                    self.log_test("POST /api/questionnaires/WebApp/complete", False, 
                                f"Missing expected fields: {missing_fields}. Response: {data}")
                    return False
                
                findings = data.get("findings", [])
                risk_assessment = data.get("risk_assessment", {})
                recommendations = data.get("recommendations", [])
                
                self.log_test("POST /api/questionnaires/WebApp/complete", True, 
                            f"✅ FIXED: Standalone mode working - {len(findings)} findings, "
                            f"risk score: {risk_assessment.get('risk_score', 'N/A')}, "
                            f"{len(recommendations)} recommendations")
                return True
                
            elif response.status_code == 500:
                error_text = response.text
                if "Node not found in diagram" in error_text:
                    self.log_test("POST /api/questionnaires/WebApp/complete", False, 
                                "❌ STILL FAILING: 'Node not found in diagram' error - standalone mode not working")
                    return False
                else:
                    self.log_test("POST /api/questionnaires/WebApp/complete", False, 
                                f"❌ HTTP 500 error: {error_text}")
                    return False
            else:
                self.log_test("POST /api/questionnaires/WebApp/complete", False, 
                            f"❌ HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("POST /api/questionnaires/WebApp/complete", False, f"❌ Error: {str(e)}")
            return False

    def test_questionnaire_get_with_security_branches(self):
        """Test GET /api/questionnaires/WebApp for security_branches field"""
        try:
            response = self.session.get(f"{self.base_url}/questionnaires/WebApp")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for security_branches field specifically
                if "security_branches" not in data:
                    self.log_test("GET /api/questionnaires/WebApp", False, 
                                f"❌ STILL FAILING: Missing 'security_branches' field. Response fields: {list(data.keys())}")
                    return False
                
                security_branches = data.get("security_branches", [])
                prompts = data.get("prompts", [])
                
                # Verify security_branches structure
                if not isinstance(security_branches, list):
                    self.log_test("GET /api/questionnaires/WebApp", False, 
                                f"❌ security_branches should be list, got: {type(security_branches)}")
                    return False
                
                self.log_test("GET /api/questionnaires/WebApp", True, 
                            f"✅ FIXED: security_branches field present - {len(security_branches)} branches, "
                            f"{len(prompts)} prompts")
                return True
                
            elif response.status_code == 500:
                error_text = response.text
                if "takes 2 positional arguments but 3 were given" in error_text:
                    self.log_test("GET /api/questionnaires/WebApp", False, 
                                "❌ STILL FAILING: Method signature error in create_security_branches")
                    return False
                else:
                    self.log_test("GET /api/questionnaires/WebApp", False, 
                                f"❌ HTTP 500 error: {error_text}")
                    return False
            else:
                self.log_test("GET /api/questionnaires/WebApp", False, 
                            f"❌ HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("GET /api/questionnaires/WebApp", False, f"❌ Error: {str(e)}")
            return False

    def test_standalone_simulation(self):
        """Test POST /api/simulate for standalone simulation"""
        try:
            # Create standalone simulation data with nodes and edges
            simulation_data = {
                "nodes": [
                    {
                        "id": "attacker-1",
                        "type": "Actor",
                        "subtype": "ExternalAttacker",
                        "label": "External Attacker",
                        "position": {"x": 100, "y": 100}
                    },
                    {
                        "id": "webapp-1", 
                        "type": "Asset",
                        "subtype": "WebApp",
                        "label": "Web Application",
                        "position": {"x": 300, "y": 100}
                    },
                    {
                        "id": "database-1",
                        "type": "Asset", 
                        "subtype": "Database",
                        "label": "Database",
                        "position": {"x": 500, "y": 100}
                    }
                ],
                "edges": [
                    {
                        "id": "edge-1",
                        "source": "attacker-1",
                        "target": "webapp-1",
                        "label": "Attack"
                    },
                    {
                        "id": "edge-2", 
                        "source": "webapp-1",
                        "target": "database-1",
                        "label": "Access"
                    }
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/simulate",
                json=simulation_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for expected response fields
                expected_fields = ["simulation_id", "attack_paths", "risk_analysis", "mitre_techniques", "recommendations"]
                missing_fields = [f for f in expected_fields if f not in data]
                
                if missing_fields:
                    self.log_test("POST /api/simulate", False, 
                                f"❌ Missing expected fields: {missing_fields}. Response fields: {list(data.keys())}")
                    return False
                
                attack_paths = data.get("attack_paths", [])
                risk_analysis = data.get("risk_analysis", {})
                mitre_techniques = data.get("mitre_techniques", [])
                recommendations = data.get("recommendations", [])
                
                self.log_test("POST /api/simulate", True, 
                            f"✅ WORKING: Standalone simulation successful - {len(attack_paths)} paths, "
                            f"{len(mitre_techniques)} MITRE techniques, {len(recommendations)} recommendations")
                return True
                
            else:
                self.log_test("POST /api/simulate", False, 
                            f"❌ HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("POST /api/simulate", False, f"❌ Error: {str(e)}")
            return False

    def test_standalone_rule_evaluation(self):
        """Test POST /api/rules/evaluate for standalone rule evaluation"""
        try:
            # Create standalone rule evaluation data
            rule_data = {
                "nodes": [
                    {
                        "id": "webapp-1",
                        "type": "Asset", 
                        "subtype": "WebApp",
                        "label": "Web Application",
                        "data": {"encryption_enabled": False, "authentication": "basic"}
                    },
                    {
                        "id": "database-1",
                        "type": "Asset",
                        "subtype": "Database", 
                        "label": "Database",
                        "data": {"encryption_at_rest": False, "access_control": "weak"}
                    }
                ],
                "edges": [
                    {
                        "id": "edge-1",
                        "source": "webapp-1",
                        "target": "database-1",
                        "label": "Connection"
                    }
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/rules/evaluate",
                json=rule_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for expected response fields
                expected_fields = ["evaluation_id", "triggered_rules", "risk_score", "recommendations"]
                missing_fields = [f for f in expected_fields if f not in data]
                
                if missing_fields:
                    self.log_test("POST /api/rules/evaluate", False, 
                                f"❌ Missing expected fields: {missing_fields}. Response fields: {list(data.keys())}")
                    return False
                
                triggered_rules = data.get("triggered_rules", [])
                risk_score = data.get("risk_score", 0)
                recommendations = data.get("recommendations", [])
                
                self.log_test("POST /api/rules/evaluate", True, 
                            f"✅ FIXED: Standalone rule evaluation working - {len(triggered_rules)} rules triggered, "
                            f"risk score: {risk_score}, {len(recommendations)} recommendations")
                return True
                
            elif response.status_code == 500:
                error_text = response.text
                if "has no attribute dict" in error_text or "has no attribute 'dict'" in error_text:
                    self.log_test("POST /api/rules/evaluate", False, 
                                "❌ STILL FAILING: RuleEvaluationResult.dict() serialization error")
                    return False
                else:
                    self.log_test("POST /api/rules/evaluate", False, 
                                f"❌ HTTP 500 error: {error_text}")
                    return False
            else:
                self.log_test("POST /api/rules/evaluate", False, 
                            f"❌ HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("POST /api/rules/evaluate", False, f"❌ Error: {str(e)}")
            return False

    def run_critical_tests(self):
        """Run the 4 critical endpoint tests"""
        print("🎯 Testing Phase 1 Critical Endpoints (Post-Fix Verification)")
        print(f"Testing against: {self.base_url}")
        print("=" * 80)
        
        tests = [
            ("POST /api/questionnaires/WebApp/complete", self.test_questionnaire_completion_standalone),
            ("GET /api/questionnaires/WebApp", self.test_questionnaire_get_with_security_branches),
            ("POST /api/simulate", self.test_standalone_simulation),
            ("POST /api/rules/evaluate", self.test_standalone_rule_evaluation)
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                self.log_test(test_name, False, f"Test execution error: {str(e)}")
                failed += 1
            
            print()  # Add spacing between tests
        
        # Print summary
        print("=" * 80)
        print(f"🎯 PHASE 1 CRITICAL ENDPOINTS SUMMARY")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Success Rate: {(passed/(passed+failed)*100):.1f}%")
        print("=" * 80)
        
        return passed, failed


if __name__ == "__main__":
    tester = CriticalEndpointsTester()
    passed, failed = tester.run_critical_tests()
    
    if failed == 0:
        print("\n✅ Phase 1 Critical Endpoints testing completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Phase 1 Critical Endpoints testing completed with failures!")
        sys.exit(1)