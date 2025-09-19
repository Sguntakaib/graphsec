#!/usr/bin/env python3
"""
Phase 2 Integration Test for Vulnerability System APIs
Tests the specific requirements from the review request for Phase 2 frontend integration
"""

import requests
import json
import uuid
from datetime import datetime, timezone
import sys
import math

# Use the production URL from review request
BASE_URL = "https://label-position.preview.emergentagent.com/api"

class Phase2IntegrationTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.test_results = []
        
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
    
    def test_core_vulnerability_analysis_apis(self):
        """Test the main vulnerability analysis endpoints"""
        print("🔍 Testing Core Vulnerability Analysis APIs")
        
        # Create test nodes for each type
        test_nodes = [
            {
                "node_id": str(uuid.uuid4()),
                "node_type": "WebApp",
                "questionnaire_responses": {
                    "authentication_method": "basic",
                    "encryption_enabled": False,
                    "input_validation": "minimal",
                    "access_control": "weak"
                },
                "node_position": {"x": 400, "y": 300}
            },
            {
                "node_id": str(uuid.uuid4()),
                "node_type": "API",
                "questionnaire_responses": {
                    "authentication_method": "none",
                    "rate_limiting": False,
                    "input_validation": "none",
                    "cors_policy": "permissive"
                },
                "node_position": {"x": 500, "y": 200}
            },
            {
                "node_id": str(uuid.uuid4()),
                "node_type": "Database",
                "questionnaire_responses": {
                    "encryption_at_rest": False,
                    "encryption_in_transit": False,
                    "access_control": "weak",
                    "audit_logging": False
                },
                "node_position": {"x": 600, "y": 400}
            }
        ]
        
        analysis_results = []
        
        # Test POST /api/vulnerabilities/analyze/{node_id}
        for node_data in test_nodes:
            node_id = node_data["node_id"]
            node_type = node_data["node_type"]
            
            try:
                response = self.session.post(
                    f"{self.base_url}/vulnerabilities/analyze/{node_id}",
                    json=node_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    analysis_results.append((node_id, node_type, data))
                    
                    # Verify required fields
                    required_fields = [
                        "node_id", "node_type", "total_vulnerabilities", 
                        "vulnerability_nodes", "overall_risk_score"
                    ]
                    
                    missing_fields = [f for f in required_fields if f not in data]
                    if missing_fields:
                        self.log_test(f"Analyze {node_type} Node", False, f"Missing fields: {missing_fields}")
                        return False
                    
                    # Verify vulnerability nodes have required structure
                    vulnerability_nodes = data.get("vulnerability_nodes", [])
                    if not vulnerability_nodes:
                        self.log_test(f"Analyze {node_type} Node", False, "No vulnerabilities generated")
                        return False
                    
                    # Check first vulnerability node structure
                    first_vuln = vulnerability_nodes[0]
                    vuln_required_fields = ["id", "name", "severity", "risk_score", "position"]
                    vuln_missing_fields = [f for f in vuln_required_fields if f not in first_vuln]
                    
                    if vuln_missing_fields:
                        self.log_test(f"Analyze {node_type} Node", False, f"Vulnerability missing fields: {vuln_missing_fields}")
                        return False
                    
                    self.log_test(f"Analyze {node_type} Node", True, 
                                f"Generated {len(vulnerability_nodes)} vulnerabilities")
                else:
                    self.log_test(f"Analyze {node_type} Node", False, f"HTTP {response.status_code}: {response.text}")
                    return False
                    
            except Exception as e:
                self.log_test(f"Analyze {node_type} Node", False, f"Error: {str(e)}")
                return False
        
        # Test GET /api/vulnerabilities/{node_id}
        for node_id, node_type, _ in analysis_results:
            try:
                response = self.session.get(f"{self.base_url}/vulnerabilities/{node_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("total_vulnerabilities", 0) == 0:
                        self.log_test(f"Get {node_type} Vulnerabilities", False, "No vulnerabilities retrieved")
                        return False
                    
                    self.log_test(f"Get {node_type} Vulnerabilities", True, 
                                f"Retrieved {data.get('total_vulnerabilities')} vulnerabilities")
                else:
                    self.log_test(f"Get {node_type} Vulnerabilities", False, f"HTTP {response.status_code}")
                    return False
                    
            except Exception as e:
                self.log_test(f"Get {node_type} Vulnerabilities", False, f"Error: {str(e)}")
                return False
        
        # Test POST /api/vulnerabilities/remediate/{vuln_id}
        if analysis_results:
            _, _, first_analysis = analysis_results[0]
            vulnerability_nodes = first_analysis.get("vulnerability_nodes", [])
            
            if vulnerability_nodes:
                vuln_id = vulnerability_nodes[0]["id"]
                
                try:
                    response = self.session.post(f"{self.base_url}/vulnerabilities/remediate/{vuln_id}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        remediation_fields = ["vulnerability_id", "immediate_steps", "implementation_priority"]
                        missing_fields = [f for f in remediation_fields if f not in data]
                        
                        if missing_fields:
                            self.log_test("Remediation Guidance", False, f"Missing fields: {missing_fields}")
                            return False
                        
                        immediate_steps = data.get("immediate_steps", [])
                        if not immediate_steps:
                            self.log_test("Remediation Guidance", False, "No remediation steps provided")
                            return False
                        
                        self.log_test("Remediation Guidance", True, 
                                    f"Retrieved {len(immediate_steps)} remediation steps")
                    else:
                        self.log_test("Remediation Guidance", False, f"HTTP {response.status_code}")
                        return False
                        
                except Exception as e:
                    self.log_test("Remediation Guidance", False, f"Error: {str(e)}")
                    return False
        
        # Test GET /api/vulnerabilities/rules
        try:
            response = self.session.get(f"{self.base_url}/vulnerabilities/rules")
            
            if response.status_code == 200:
                data = response.json()
                
                total_rules = data.get("total_rules", 0)
                if total_rules == 0:
                    self.log_test("Vulnerability Rules", False, "No vulnerability rules found")
                    return False
                
                rules_by_type = data.get("rules_by_node_type", {})
                expected_types = ["WebApp", "API", "Database"]
                
                for node_type in expected_types:
                    if node_type not in rules_by_type or rules_by_type[node_type] == 0:
                        self.log_test("Vulnerability Rules", False, f"No rules for {node_type}")
                        return False
                
                self.log_test("Vulnerability Rules", True, 
                            f"Retrieved {total_rules} rules for all node types")
            else:
                self.log_test("Vulnerability Rules", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Vulnerability Rules", False, f"Error: {str(e)}")
            return False
        
        return True
    
    def test_bulk_analysis_testing(self):
        """Test bulk vulnerability analysis with WebApp, API, and Database nodes"""
        print("🔍 Testing Bulk Analysis")
        
        try:
            # Create test scenario with WebApp, API, and Database nodes
            nodes_data = [
                {
                    "node_id": str(uuid.uuid4()),
                    "node_type": "WebApp",
                    "questionnaire_responses": {
                        "authentication_method": "basic",
                        "encryption_enabled": False,
                        "input_validation": "minimal",
                        "access_control": "weak",
                        "session_management": "basic"
                    },
                    "position": {"x": 300, "y": 200}
                },
                {
                    "node_id": str(uuid.uuid4()),
                    "node_type": "API", 
                    "questionnaire_responses": {
                        "authentication_method": "none",
                        "rate_limiting": False,
                        "input_validation": "none",
                        "cors_policy": "permissive",
                        "api_versioning": False
                    },
                    "position": {"x": 500, "y": 300}
                },
                {
                    "node_id": str(uuid.uuid4()),
                    "node_type": "Database",
                    "questionnaire_responses": {
                        "encryption_at_rest": False,
                        "encryption_in_transit": False,
                        "access_control": "weak",
                        "audit_logging": False,
                        "backup_encryption": False
                    },
                    "position": {"x": 700, "y": 400}
                }
            ]
            
            request_data = {"nodes": nodes_data}
            
            response = self.session.post(
                f"{self.base_url}/vulnerabilities/bulk-analyze",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify bulk analysis structure
                required_fields = [
                    "analyzed_nodes", "successful_analyses", "total_vulnerabilities",
                    "average_risk_score", "results"
                ]
                
                missing_fields = [f for f in required_fields if f not in data]
                if missing_fields:
                    self.log_test("Bulk Analysis", False, f"Missing fields: {missing_fields}")
                    return False
                
                analyzed_nodes = data.get("analyzed_nodes", 0)
                successful_analyses = data.get("successful_analyses", 0)
                total_vulnerabilities = data.get("total_vulnerabilities", 0)
                
                if analyzed_nodes != 3:
                    self.log_test("Bulk Analysis", False, f"Expected 3 nodes, got {analyzed_nodes}")
                    return False
                
                if successful_analyses != 3:
                    self.log_test("Bulk Analysis", False, f"Expected 3 successful analyses, got {successful_analyses}")
                    return False
                
                if total_vulnerabilities == 0:
                    self.log_test("Bulk Analysis", False, "No vulnerabilities found in bulk analysis")
                    return False
                
                self.log_test("Bulk Analysis", True, 
                            f"Analyzed {analyzed_nodes} nodes, found {total_vulnerabilities} total vulnerabilities")
                return True
            else:
                self.log_test("Bulk Analysis", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Bulk Analysis", False, f"Error: {str(e)}")
            return False
    
    def test_owasp_top_10_coverage(self):
        """Verify OWASP Top 10 2023 coverage"""
        print("🔍 Testing OWASP Top 10 2023 Coverage")
        
        try:
            # Test with insecure configurations to trigger OWASP vulnerabilities
            test_cases = [
                ("WebApp", {
                    "authentication_method": "basic",
                    "encryption_enabled": False,
                    "input_validation": "minimal",
                    "access_control": "weak",
                    "session_management": "basic",
                    "csrf_protection": False,
                    "sql_injection_protection": False,
                    "security_headers": False
                }),
                ("API", {
                    "authentication_method": "none",
                    "rate_limiting": False,
                    "input_validation": "none",
                    "cors_policy": "permissive",
                    "api_versioning": False,
                    "request_size_limits": False,
                    "error_responses": "detailed"
                }),
                ("Database", {
                    "encryption_at_rest": False,
                    "encryption_in_transit": False,
                    "access_control": "weak",
                    "audit_logging": False,
                    "backup_encryption": False,
                    "network_security": "none",
                    "privilege_escalation": "possible"
                })
            ]
            
            all_owasp_categories = set()
            total_vulnerabilities = 0
            
            for node_type, questionnaire_data in test_cases:
                node_id = str(uuid.uuid4())
                
                request_data = {
                    "node_id": node_id,
                    "node_type": node_type,
                    "questionnaire_responses": questionnaire_data,
                    "node_position": {"x": 400, "y": 300}
                }
                
                response = self.session.post(
                    f"{self.base_url}/vulnerabilities/analyze/{node_id}",
                    json=request_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    vulnerability_nodes = data.get("vulnerability_nodes", [])
                    total_vulnerabilities += len(vulnerability_nodes)
                    
                    # Collect OWASP categories
                    for vuln in vulnerability_nodes:
                        owasp_category = vuln.get("owasp_category", "")
                        if owasp_category:
                            all_owasp_categories.add(owasp_category)
                else:
                    self.log_test("OWASP Coverage", False, f"Failed to analyze {node_type}: HTTP {response.status_code}")
                    return False
            
            # Check OWASP Top 10 2023 coverage
            owasp_2023_categories = [
                "A01:2023", "A02:2023", "A03:2023", "A04:2023", "A05:2023",
                "A06:2023", "A07:2023", "A08:2023", "A09:2023", "A10:2023"
            ]
            
            covered_categories = []
            for owasp_cat in owasp_2023_categories:
                if any(owasp_cat in found_cat for found_cat in all_owasp_categories):
                    covered_categories.append(owasp_cat)
            
            coverage_percentage = (len(covered_categories) / len(owasp_2023_categories)) * 100
            
            if coverage_percentage < 80:  # Expect at least 80% coverage
                self.log_test("OWASP Coverage", False, 
                            f"Insufficient OWASP 2023 coverage: {coverage_percentage:.1f}% ({len(covered_categories)}/10)")
                return False
            
            self.log_test("OWASP Coverage", True, 
                        f"OWASP 2023 coverage: {coverage_percentage:.1f}% ({len(covered_categories)}/10)")
            return True
            
        except Exception as e:
            self.log_test("OWASP Coverage", False, f"Error: {str(e)}")
            return False
    
    def test_mitre_attack_technique_mapping(self):
        """Verify MITRE ATT&CK technique mapping"""
        print("🔍 Testing MITRE ATT&CK Technique Mapping")
        
        try:
            node_id = str(uuid.uuid4())
            questionnaire_data = {
                "authentication_method": "basic",
                "encryption_enabled": False,
                "input_validation": "minimal",
                "access_control": "weak"
            }
            
            request_data = {
                "node_id": node_id,
                "node_type": "WebApp",
                "questionnaire_responses": questionnaire_data,
                "node_position": {"x": 400, "y": 300}
            }
            
            response = self.session.post(
                f"{self.base_url}/vulnerabilities/analyze/{node_id}",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                vulnerability_nodes = data.get("vulnerability_nodes", [])
                
                if not vulnerability_nodes:
                    self.log_test("MITRE Mapping", False, "No vulnerabilities to check MITRE mapping")
                    return False
                
                # Collect all MITRE techniques
                all_mitre_techniques = []
                for vuln in vulnerability_nodes:
                    mitre_techniques = vuln.get("mitre_techniques", [])
                    all_mitre_techniques.extend(mitre_techniques)
                
                if not all_mitre_techniques:
                    self.log_test("MITRE Mapping", False, "No MITRE techniques mapped to vulnerabilities")
                    return False
                
                # Verify MITRE technique format (should start with T and have numbers)
                valid_techniques = [t for t in all_mitre_techniques if t.startswith("T") and len(t) >= 5]
                
                if len(valid_techniques) != len(all_mitre_techniques):
                    self.log_test("MITRE Mapping", False, "Invalid MITRE technique format found")
                    return False
                
                unique_techniques = list(set(all_mitre_techniques))
                self.log_test("MITRE Mapping", True, 
                            f"Mapped {len(unique_techniques)} unique MITRE techniques: {unique_techniques[:5]}...")
                return True
            else:
                self.log_test("MITRE Mapping", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("MITRE Mapping", False, f"Error: {str(e)}")
            return False
    
    def test_smart_positioning_algorithm(self):
        """Verify orbital positioning with 120px radius and collision detection"""
        print("🔍 Testing Smart Positioning Algorithm")
        
        try:
            node_id = str(uuid.uuid4())
            parent_position = {"x": 400, "y": 300}
            
            request_data = {
                "node_id": node_id,
                "node_type": "WebApp",
                "questionnaire_responses": {
                    "authentication_method": "basic",
                    "encryption_enabled": False,
                    "input_validation": "minimal",
                    "access_control": "weak",
                    "session_management": "basic"
                },
                "node_position": parent_position
            }
            
            response = self.session.post(
                f"{self.base_url}/vulnerabilities/analyze/{node_id}",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                vulnerability_nodes = data.get("vulnerability_nodes", [])
                
                if not vulnerability_nodes:
                    self.log_test("Smart Positioning", False, "No vulnerabilities to test positioning")
                    return False
                
                # Verify all vulnerabilities have position coordinates
                positioned_vulns = [v for v in vulnerability_nodes if v.get("position")]
                if len(positioned_vulns) != len(vulnerability_nodes):
                    self.log_test("Smart Positioning", False, "Not all vulnerabilities have position data")
                    return False
                
                # Verify 120px radius positioning around parent node
                parent_x, parent_y = parent_position["x"], parent_position["y"]
                expected_radius = 120
                
                positioning_valid = True
                distances = []
                
                for vuln in vulnerability_nodes:
                    vuln_pos = vuln.get("position", {})
                    vuln_x, vuln_y = vuln_pos.get("x", 0), vuln_pos.get("y", 0)
                    
                    # Calculate distance from parent
                    distance = math.sqrt((vuln_x - parent_x) ** 2 + (vuln_y - parent_y) ** 2)
                    distances.append(distance)
                    
                    # Allow some tolerance for positioning algorithm (120px ± 40px)
                    if distance < 80 or distance > 160:
                        positioning_valid = False
                        break
                
                if not positioning_valid:
                    self.log_test("Smart Positioning", False, 
                                f"Vulnerability nodes not positioned correctly around parent (distances: {distances})")
                    return False
                
                # Verify collision detection (no overlapping positions)
                positions = [(v["position"]["x"], v["position"]["y"]) for v in vulnerability_nodes]
                unique_positions = set(positions)
                
                if len(unique_positions) != len(positions):
                    self.log_test("Smart Positioning", False, "Overlapping vulnerability positions detected")
                    return False
                
                # Verify auto-spacing based on vulnerability count
                avg_distance = sum(distances) / len(distances)
                
                self.log_test("Smart Positioning", True, 
                            f"Positioned {len(vulnerability_nodes)} vulnerabilities with orbital algorithm, "
                            f"avg distance: {avg_distance:.1f}px, collision detection working")
                return True
            else:
                self.log_test("Smart Positioning", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Smart Positioning", False, f"Error: {str(e)}")
            return False
    
    def test_api_response_structure(self):
        """Ensure all required fields are present in API responses"""
        print("🔍 Testing API Response Structure")
        
        try:
            node_id = str(uuid.uuid4())
            
            request_data = {
                "node_id": node_id,
                "node_type": "WebApp",
                "questionnaire_responses": {
                    "authentication_method": "basic",
                    "encryption_enabled": False,
                    "input_validation": "minimal"
                },
                "node_position": {"x": 400, "y": 300}
            }
            
            response = self.session.post(
                f"{self.base_url}/vulnerabilities/analyze/{node_id}",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check main response structure
                required_main_fields = [
                    "node_id", "node_type", "total_vulnerabilities", 
                    "vulnerabilities_by_severity", "vulnerability_nodes",
                    "overall_risk_score", "recommendations", "analysis_timestamp"
                ]
                
                missing_main_fields = [f for f in required_main_fields if f not in data]
                if missing_main_fields:
                    self.log_test("API Response Structure", False, f"Missing main fields: {missing_main_fields}")
                    return False
                
                # Check vulnerability_nodes array structure
                vulnerability_nodes = data.get("vulnerability_nodes", [])
                if not vulnerability_nodes:
                    self.log_test("API Response Structure", False, "No vulnerability nodes in response")
                    return False
                
                # Check first vulnerability node structure
                first_vuln = vulnerability_nodes[0]
                required_vuln_fields = [
                    "id", "name", "severity", "risk_score", "position",
                    "mitre_techniques", "owasp_category", "remediation_steps"
                ]
                
                missing_vuln_fields = [f for f in required_vuln_fields if f not in first_vuln]
                if missing_vuln_fields:
                    self.log_test("API Response Structure", False, f"Missing vulnerability fields: {missing_vuln_fields}")
                    return False
                
                # Verify position coordinates
                position = first_vuln.get("position", {})
                if "x" not in position or "y" not in position:
                    self.log_test("API Response Structure", False, "Missing position coordinates")
                    return False
                
                # Verify MITRE technique mappings
                mitre_techniques = first_vuln.get("mitre_techniques", [])
                if not mitre_techniques:
                    self.log_test("API Response Structure", False, "No MITRE technique mappings")
                    return False
                
                # Verify remediation_steps arrays
                remediation_steps = first_vuln.get("remediation_steps", [])
                if not remediation_steps:
                    self.log_test("API Response Structure", False, "No remediation steps provided")
                    return False
                
                # Verify OWASP category classifications
                owasp_category = first_vuln.get("owasp_category", "")
                if not owasp_category or "2023" not in owasp_category:
                    self.log_test("API Response Structure", False, "Missing or invalid OWASP category")
                    return False
                
                self.log_test("API Response Structure", True, 
                            f"All required fields present: {len(vulnerability_nodes)} vulnerability nodes with complete structure")
                return True
            else:
                self.log_test("API Response Structure", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("API Response Structure", False, f"Error: {str(e)}")
            return False
    
    def run_phase2_integration_tests(self):
        """Run all Phase 2 integration tests"""
        print("🚀 PHASE 2 VULNERABILITY SYSTEM INTEGRATION TESTING")
        print("=" * 80)
        print("Testing Phase 1 Vulnerability System APIs for Phase 2 frontend integration")
        print("Backend URL:", self.base_url)
        print("=" * 80)
        
        tests = [
            ("Core Vulnerability Analysis APIs", self.test_core_vulnerability_analysis_apis),
            ("Bulk Analysis Testing", self.test_bulk_analysis_testing),
            ("OWASP Top 10 2023 Coverage", self.test_owasp_top_10_coverage),
            ("MITRE ATT&CK Technique Mapping", self.test_mitre_attack_technique_mapping),
            ("Smart Positioning Algorithm", self.test_smart_positioning_algorithm),
            ("API Response Structure", self.test_api_response_structure)
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            print(f"\n🔍 Testing: {test_name}")
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
        print(f"🎯 PHASE 2 INTEGRATION TESTING SUMMARY")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Success Rate: {(passed/(passed+failed)*100):.1f}%")
        print("=" * 80)
        
        return passed, failed

def main():
    """Main test execution"""
    tester = Phase2IntegrationTester()
    passed, failed = tester.run_phase2_integration_tests()
    
    if failed == 0:
        print("\n✅ Phase 2 Integration testing completed successfully!")
        print("🚀 Phase 1 Vulnerability System is ready for Phase 2 frontend integration!")
        sys.exit(0)
    else:
        print("\n❌ Phase 2 Integration testing completed with failures!")
        print("🔧 Issues need to be resolved before Phase 2 frontend integration")
        sys.exit(1)

if __name__ == "__main__":
    main()