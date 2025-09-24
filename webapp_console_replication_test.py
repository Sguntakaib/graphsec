#!/usr/bin/env python3
"""
WebApp Console Log Replication Test
Replicating the exact scenario from user's console logs to debug the 0 vulnerabilities issue

USER CONSOLE LOG EVIDENCE:
- "API Request: POST /vulnerabilities/analyze/asset-1758712778144" ✅ (WebApp)
- "API Response: 200 /vulnerabilities/analyze/asset-1758712778144" ✅ (WebApp) 
- Missing: "✅ Created X vulnerability nodes for node asset-1758712778144" ❌

SUCCESSFUL DATABASE COMPARISON:
- "API Request: POST /vulnerabilities/analyze/database-asset-1758712778144-1758712801642-0" ✅
- "API Response: 200 /vulnerabilities/analyze/database-asset-1758712778144-1758712801642-0" ✅  
- "✅ Created 3 vulnerability nodes for node database-asset-1758712778144-1758712801642-0" ✅

This test will replicate the exact scenario using realistic questionnaire responses
"""

import requests
import json
import uuid
from datetime import datetime, timezone
import sys

# Use the backend URL from frontend/.env with /api suffix
BASE_URL = "https://hover-popup-fix.preview.emergentagent.com/api"

class WebAppConsoleReplicationTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.test_results = []
        self.test_diagram_id = None
        self.webapp_node_id = "asset-1758712778144"  # Use exact node ID from console logs
        self.database_node_id = "database-asset-1758712778144-1758712801642-0"  # Use exact node ID from console logs
        
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
        """Test API health"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Check", True, f"API is healthy: {data['message']}")
                return True
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Connection error: {str(e)}")
            return False

    def setup_test_diagram_with_exact_nodes(self):
        """Create test diagram with exact node IDs from console logs"""
        try:
            print("🎯 SETUP: Creating Test Diagram with Exact Console Log Node IDs")
            print("=" * 80)
            
            # Create test diagram
            diagram_data = {
                "title": "Console Log Replication Test",
                "description": "Replicating exact scenario from user console logs"
            }
            
            response = self.session.post(f"{self.base_url}/diagrams", json=diagram_data)
            if response.status_code != 200:
                self.log_test("Setup Test Diagram", False, f"Failed to create diagram: HTTP {response.status_code}")
                return False
            
            diagram = response.json()
            self.test_diagram_id = diagram["id"]
            
            # Create WebApp node with exact ID from console logs
            webapp_node = {
                "id": self.webapp_node_id,
                "type": "Asset",
                "subtype": "WebApp",
                "label": "Console Log WebApp Node",
                "position": {"x": 200, "y": 200},
                "data": {
                    "criticality": "High",
                    "data_classification": "Confidential"
                }
            }
            
            # Create Database node with exact ID from console logs
            database_node = {
                "id": self.database_node_id,
                "type": "Asset", 
                "subtype": "Database",
                "label": "Console Log Database Node",
                "position": {"x": 400, "y": 200},
                "data": {
                    "criticality": "High",
                    "data_classification": "Confidential"
                }
            }
            
            # Update diagram with both nodes
            diagram["nodes"] = [webapp_node, database_node]
            diagram["edges"] = []
            
            update_response = self.session.put(f"{self.base_url}/diagrams/{self.test_diagram_id}", json=diagram)
            if update_response.status_code != 200:
                self.log_test("Setup Test Diagram", False, f"Failed to update diagram: HTTP {update_response.status_code}")
                return False
            
            print(f"   ✅ Created test diagram: {self.test_diagram_id}")
            print(f"   ✅ Created WebApp node with exact ID: {self.webapp_node_id}")
            print(f"   ✅ Created Database node with exact ID: {self.database_node_id}")
            
            self.log_test("Setup Test Diagram", True, "Test diagram with exact console log node IDs created successfully")
            return True
            
        except Exception as e:
            self.log_test("Setup Test Diagram", False, f"Setup error: {str(e)}")
            return False

    def test_webapp_with_realistic_questionnaire_responses(self):
        """Test WebApp with realistic questionnaire responses that should trigger multiple vulnerabilities"""
        try:
            print("🎯 TEST 1: WebApp with Realistic Questionnaire Responses (Should Create Multiple Vulnerabilities)")
            print("=" * 80)
            
            # Get actual WebApp questionnaire structure first
            prompts_response = self.session.get(f"{self.base_url}/intelligent-nodes/WebApp/prompts")
            if prompts_response.status_code != 200:
                self.log_test("WebApp Realistic Questionnaire Test", False, 
                            f"Failed to get WebApp prompts: HTTP {prompts_response.status_code}")
                return False
            
            prompts_data = prompts_response.json()
            prompts = prompts_data.get("prompts", [])
            
            print(f"📋 WebApp Questionnaire Structure:")
            print(f"   Total Questions: {len(prompts)}")
            
            # Create realistic questionnaire responses based on actual prompts
            # These responses should trigger multiple vulnerabilities
            realistic_responses = {}
            
            for prompt in prompts:
                question_id = prompt.get("id", "")
                question_text = prompt.get("question", "")
                options = prompt.get("options", [])
                
                print(f"   Question: {question_id} - {question_text}")
                
                # Set responses that should trigger vulnerabilities
                if "login" in question_id.lower() or "authentication" in question_id.lower():
                    # Choose weak authentication option
                    if options:
                        weak_auth_options = [opt for opt in options if "password" in opt.lower() and "mfa" not in opt.lower()]
                        if weak_auth_options:
                            realistic_responses[question_id] = weak_auth_options[0]
                        else:
                            realistic_responses[question_id] = options[0] if options else "Username/Password only"
                    else:
                        realistic_responses[question_id] = "Username/Password only"
                
                elif "api" in question_id.lower() and "endpoint" in question_id.lower():
                    # Enable API endpoints to trigger API-related vulnerabilities
                    realistic_responses[question_id] = "Yes" if "Yes" in options else (options[0] if options else "Yes")
                
                elif "database" in question_id.lower() and "connection" in question_id.lower():
                    # Enable database connection to trigger database-related vulnerabilities
                    realistic_responses[question_id] = "Yes" if "Yes" in options else (options[0] if options else "Yes")
                
                elif "validation" in question_id.lower() or "input" in question_id.lower():
                    # Choose weak input validation
                    if options:
                        weak_validation_options = [opt for opt in options if "client" in opt.lower() or "basic" in opt.lower()]
                        if weak_validation_options:
                            realistic_responses[question_id] = weak_validation_options[0]
                        else:
                            realistic_responses[question_id] = options[0] if options else "Basic client-side validation"
                    else:
                        realistic_responses[question_id] = "Basic client-side validation"
                
                elif "waf" in question_id.lower() or "firewall" in question_id.lower():
                    # No WAF protection
                    realistic_responses[question_id] = "No" if "No" in options else (options[-1] if options else "No")
                
                elif "deployment" in question_id.lower():
                    # Choose cloud deployment
                    if options:
                        cloud_options = [opt for opt in options if "cloud" in opt.lower() or "aws" in opt.lower() or "azure" in opt.lower()]
                        if cloud_options:
                            realistic_responses[question_id] = cloud_options[0]
                        else:
                            realistic_responses[question_id] = options[0] if options else "Cloud"
                    else:
                        realistic_responses[question_id] = "Cloud"
                
                else:
                    # Default to first option or a generic response
                    realistic_responses[question_id] = options[0] if options else "Default"
            
            print(f"\n📋 Realistic Questionnaire Responses:")
            for key, value in realistic_responses.items():
                print(f"   {key}: {value}")
            
            # Test vulnerability analysis with realistic responses
            vulnerability_request = {
                "node_id": self.webapp_node_id,
                "node_type": "WebApp",
                "questionnaire_responses": realistic_responses,
                "node_position": {"x": 200, "y": 200}
            }
            
            print(f"\n📊 Making API Request: POST /vulnerabilities/analyze/{self.webapp_node_id}")
            
            response = self.session.post(
                f"{self.base_url}/vulnerabilities/analyze/{self.webapp_node_id}",
                json=vulnerability_request
            )
            
            print(f"📊 API Response: {response.status_code} /vulnerabilities/analyze/{self.webapp_node_id}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("WebApp Realistic Questionnaire Test", False, 
                            f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("WebApp Realistic Questionnaire Test", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            # Analyze the response
            vulnerabilities = data.get("vulnerability_nodes", [])
            total_vulnerabilities = data.get("total_vulnerabilities", 0)
            overall_risk_score = data.get("overall_risk_score", 0)
            vulnerabilities_by_severity = data.get("vulnerabilities_by_severity", {})
            
            print(f"\n📊 WebApp Vulnerability Analysis Results:")
            print(f"   Total Vulnerabilities: {total_vulnerabilities}")
            print(f"   Overall Risk Score: {overall_risk_score}")
            print(f"   Vulnerabilities by Severity: {vulnerabilities_by_severity}")
            
            if total_vulnerabilities > 0:
                print(f"   ✅ Created {total_vulnerabilities} vulnerability nodes for node {self.webapp_node_id}")
                print(f"   Vulnerability Details:")
                for i, vuln in enumerate(vulnerabilities):
                    print(f"     {i+1}. {vuln.get('name', 'Unknown')} ({vuln.get('severity', 'Unknown')})")
                    print(f"        Category: {vuln.get('category', 'Unknown')}")
                    print(f"        Triggered by: {vuln.get('triggered_by_rule', 'Unknown')}")
                    print(f"        Risk Score: {vuln.get('risk_score', 0)}")
                
                # Check if we got multiple vulnerabilities as expected
                if total_vulnerabilities >= 3:
                    self.log_test("WebApp Realistic Questionnaire Test", True, 
                                f"✅ SUCCESS: Created {total_vulnerabilities} vulnerability nodes for WebApp (expected multiple)")
                    return True
                else:
                    self.log_test("WebApp Realistic Questionnaire Test", False, 
                                f"⚠️ PARTIAL: Only created {total_vulnerabilities} vulnerability nodes, expected 3+ like Database")
                    return False
            else:
                print(f"   ❌ NO VULNERABILITIES CREATED - This matches the user's issue!")
                print(f"   Missing: '✅ Created X vulnerability nodes for node {self.webapp_node_id}'")
                
                self.log_test("WebApp Realistic Questionnaire Test", False, 
                            f"❌ CRITICAL ISSUE REPRODUCED: WebApp returned 0 vulnerabilities with realistic responses")
                return False
            
        except Exception as e:
            self.log_test("WebApp Realistic Questionnaire Test", False, f"Request error: {str(e)}")
            return False

    def test_database_comparison_with_exact_node_id(self):
        """Test Database with exact node ID from console logs for comparison"""
        try:
            print("🎯 TEST 2: Database Comparison with Exact Console Log Node ID")
            print("=" * 80)
            
            # Create realistic Database questionnaire responses that should trigger vulnerabilities
            database_responses = {
                "database_authentication": "Username/Password only",
                "database_encryption_at_rest": "No encryption",
                "database_encryption_in_transit": "No encryption",
                "database_access_control": "Basic user accounts",
                "database_logging": "Minimal logging"
            }
            
            vulnerability_request = {
                "node_id": self.database_node_id,
                "node_type": "Database",
                "questionnaire_responses": database_responses,
                "node_position": {"x": 400, "y": 200}
            }
            
            print(f"📋 Database Questionnaire Responses:")
            for key, value in database_responses.items():
                print(f"   {key}: {value}")
            
            print(f"\n📊 Making API Request: POST /vulnerabilities/analyze/{self.database_node_id}")
            
            response = self.session.post(
                f"{self.base_url}/vulnerabilities/analyze/{self.database_node_id}",
                json=vulnerability_request
            )
            
            print(f"📊 API Response: {response.status_code} /vulnerabilities/analyze/{self.database_node_id}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("Database Comparison Test", False, 
                            f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Database Comparison Test", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            # Analyze the response
            vulnerabilities = data.get("vulnerability_nodes", [])
            total_vulnerabilities = data.get("total_vulnerabilities", 0)
            overall_risk_score = data.get("overall_risk_score", 0)
            
            print(f"\n📊 Database Vulnerability Analysis Results:")
            print(f"   Total Vulnerabilities: {total_vulnerabilities}")
            print(f"   Overall Risk Score: {overall_risk_score}")
            
            if total_vulnerabilities > 0:
                print(f"   ✅ Created {total_vulnerabilities} vulnerability nodes for node {self.database_node_id}")
                print(f"   Vulnerability Details:")
                for i, vuln in enumerate(vulnerabilities):
                    print(f"     {i+1}. {vuln.get('name', 'Unknown')} ({vuln.get('severity', 'Unknown')})")
                
                self.log_test("Database Comparison Test", True, 
                            f"✅ SUCCESS: Database created {total_vulnerabilities} vulnerability nodes (working correctly)")
                return True
            else:
                print(f"   ❌ Database also returned 0 vulnerabilities")
                self.log_test("Database Comparison Test", False, 
                            f"❌ Database also returned 0 vulnerabilities - broader system issue")
                return False
            
        except Exception as e:
            self.log_test("Database Comparison Test", False, f"Request error: {str(e)}")
            return False

    def test_vulnerability_rule_analysis(self):
        """Analyze available vulnerability rules to understand why WebApp might return fewer vulnerabilities"""
        try:
            print("🎯 TEST 3: Vulnerability Rule Analysis")
            print("=" * 80)
            
            # Get vulnerability rules
            rules_response = self.session.get(f"{self.base_url}/vulnerabilities/rules")
            
            if rules_response.status_code != 200:
                self.log_test("Vulnerability Rule Analysis", False, 
                            f"Failed to get vulnerability rules: HTTP {rules_response.status_code}")
                return False
            
            try:
                rules_data = rules_response.json()
            except json.JSONDecodeError as e:
                self.log_test("Vulnerability Rule Analysis", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            rules = rules_data.get("rules", [])
            
            print(f"📋 Vulnerability Rules Analysis:")
            print(f"   Total Rules: {len(rules)}")
            
            # Count rules by node type
            webapp_rules = [rule for rule in rules if rule.get("applicable_node_types", []) and "WebApp" in rule.get("applicable_node_types", [])]
            database_rules = [rule for rule in rules if rule.get("applicable_node_types", []) and "Database" in rule.get("applicable_node_types", [])]
            
            print(f"   WebApp Rules: {len(webapp_rules)}")
            print(f"   Database Rules: {len(database_rules)}")
            
            if webapp_rules:
                print(f"   WebApp Vulnerability Rules:")
                for i, rule in enumerate(webapp_rules[:10]):  # Show first 10
                    rule_id = rule.get("id", "Unknown")
                    description = rule.get("description", "No description")
                    conditions = rule.get("conditions", [])
                    print(f"     {i+1}. {rule_id}: {description}")
                    if conditions:
                        print(f"        Conditions: {len(conditions)} trigger conditions")
            
            if database_rules:
                print(f"   Database Vulnerability Rules:")
                for i, rule in enumerate(database_rules[:5]):  # Show first 5
                    rule_id = rule.get("id", "Unknown")
                    description = rule.get("description", "No description")
                    conditions = rule.get("conditions", [])
                    print(f"     {i+1}. {rule_id}: {description}")
                    if conditions:
                        print(f"        Conditions: {len(conditions)} trigger conditions")
            
            # Compare rule counts
            if len(webapp_rules) < len(database_rules):
                self.log_test("Vulnerability Rule Analysis", False, 
                            f"❌ POTENTIAL ISSUE: WebApp has fewer rules ({len(webapp_rules)}) than Database ({len(database_rules)})")
                return False
            else:
                self.log_test("Vulnerability Rule Analysis", True, 
                            f"✅ Rule counts seem adequate: WebApp ({len(webapp_rules)}), Database ({len(database_rules)})")
                return True
            
        except Exception as e:
            self.log_test("Vulnerability Rule Analysis", False, f"Request error: {str(e)}")
            return False

    def cleanup_test_data(self):
        """Clean up test data"""
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
        """Run all console log replication tests"""
        print("🚀 STARTING WEBAPP CONSOLE LOG REPLICATION TESTING")
        print("=" * 80)
        print("Replicating exact scenario from user console logs:")
        print("1. Test WebApp with realistic questionnaire responses (should create multiple vulnerabilities)")
        print("2. Test Database with exact node ID for comparison")
        print("3. Analyze vulnerability rules to understand rule coverage")
        print("=" * 80)
        
        tests = [
            self.test_health_check,
            self.setup_test_diagram_with_exact_nodes,
            self.test_webapp_with_realistic_questionnaire_responses,
            self.test_database_comparison_with_exact_node_id,
            self.test_vulnerability_rule_analysis,
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
        print(f"🏁 CONSOLE LOG REPLICATION TESTING COMPLETE: {passed}/{total} tests passed")
        print("=" * 80)
        
        # Print detailed results
        print("\n📊 DETAILED TEST RESULTS:")
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{status} {result['test']}: {result['message']}")
        
        # Summary for console log replication
        print("\n🔍 CONSOLE LOG REPLICATION SUMMARY:")
        if passed == total:
            print("✅ All tests passed - Unable to reproduce the 0 vulnerabilities issue")
            print("🔧 POSSIBLE EXPLANATIONS:")
            print("   1. Issue may be intermittent or related to specific questionnaire responses")
            print("   2. Issue may be related to caching or timing")
            print("   3. Issue may have been resolved in recent updates")
        else:
            print(f"❌ {total-passed} tests failed - Issue reproduced or other problems found")
            print("🔧 DEBUGGING FINDINGS:")
            
            failed_tests = [r for r in self.test_results if not r["success"]]
            for failed in failed_tests:
                if "CRITICAL ISSUE REPRODUCED" in failed["message"]:
                    print("   ❌ CRITICAL: Successfully reproduced the 0 vulnerabilities issue")
                    print("   🔍 ROOT CAUSE: WebApp vulnerability analysis returns 200 but creates 0 vulnerabilities")
                    print("   🔧 SOLUTION NEEDED: Investigate WebApp vulnerability rules and questionnaire field mapping")
                elif "fewer rules" in failed["message"]:
                    print("   ❌ RULE COVERAGE: WebApp has fewer vulnerability rules than Database")
                    print("   🔧 SOLUTION: Add more WebApp-specific vulnerability rules")
                elif "PARTIAL" in failed["message"]:
                    print("   ⚠️ PARTIAL ISSUE: WebApp creates some vulnerabilities but fewer than expected")
                    print("   🔧 SOLUTION: Review and enhance WebApp vulnerability rule triggers")
        
        return passed == total

if __name__ == "__main__":
    tester = WebAppConsoleReplicationTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)