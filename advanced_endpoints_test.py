#!/usr/bin/env python3
"""
Focused tests for the 5 newly implemented advanced backend endpoints
Testing specific scenarios mentioned in the review request
"""

import requests
import json
import uuid
from datetime import datetime, timezone

# Use the production URL from frontend/.env
BASE_URL = "https://app-deployment-28.preview.emergentagent.com/api"

class AdvancedEndpointsTest:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.test_diagram_id = None
        
    def log_test(self, test_name, success, message=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
    def setup_test_diagram(self):
        """Create a test diagram with security nodes for advanced testing"""
        try:
            # Create basic diagram
            diagram_data = {
                "title": "Advanced Security Test Diagram",
                "description": "Test diagram for advanced endpoint validation"
            }
            
            response = self.session.post(
                f"{self.base_url}/diagrams",
                json=diagram_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                return False
                
            self.test_diagram_id = response.json()["id"]
            
            # Update with security nodes that have MITRE techniques
            security_data = {
                "id": self.test_diagram_id,
                "title": "Advanced Security Test Diagram",
                "description": "Test diagram for advanced endpoint validation",
                "nodes": [
                    {
                        "id": str(uuid.uuid4()),
                        "type": "Actor",
                        "subtype": "ExternalAttacker",
                        "label": "External Threat Actor",
                        "position": {"x": 100, "y": 100},
                        "data": {"description": "Advanced persistent threat"},
                        "mitre_ids": ["T1078", "T1484", "T1190", "T1213"],
                        "cve_ids": []
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "type": "Asset",
                        "subtype": "WebApp",
                        "label": "Web Application",
                        "position": {"x": 300, "y": 100},
                        "data": {"description": "Critical web application", "criticality": "High"},
                        "mitre_ids": [],
                        "cve_ids": []
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "type": "Surface",
                        "subtype": "SQLi",
                        "label": "SQL Injection",
                        "position": {"x": 200, "y": 100},
                        "data": {"description": "SQL injection vulnerability", "severity": "High"},
                        "mitre_ids": ["T1190", "T1213"],
                        "cve_ids": []
                    }
                ],
                "edges": [
                    {
                        "id": str(uuid.uuid4()),
                        "source": "actor1",
                        "target": "surface1",
                        "type": "attack",
                        "label": "Exploits vulnerability",
                        "data": {"likelihood": "High", "impact": "High"}
                    }
                ]
            }
            
            response = self.session.put(
                f"{self.base_url}/diagrams/{self.test_diagram_id}",
                json=security_data,
                headers={"Content-Type": "application/json"}
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"Setup failed: {str(e)}")
            return False
    
    def test_mitre_technique_lookup(self):
        """Test MITRE Technique Lookup API with specific technique IDs"""
        print("\n🔍 Testing MITRE Technique Lookup API")
        
        # Test with specific MITRE technique IDs mentioned in review request
        test_techniques = ["T1078", "T1484", "T1190", "T1213"]
        
        for technique_id in test_techniques:
            try:
                response = self.session.get(f"{self.base_url}/mitre/technique/{technique_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Verify response includes required fields
                    required_fields = ["technique_id", "name", "description", "tactics", "detection_difficulty"]
                    missing_fields = [f for f in required_fields if f not in data]
                    
                    if missing_fields:
                        self.log_test(f"MITRE Technique {technique_id}", False, f"Missing fields: {missing_fields}")
                        return False
                    
                    # Verify technique details
                    name = data.get("name", "")
                    tactics = data.get("tactics", [])
                    description = data.get("description", "")
                    
                    if not name or not description:
                        self.log_test(f"MITRE Technique {technique_id}", False, "Empty name or description")
                        return False
                    
                    self.log_test(f"MITRE Technique {technique_id}", True, 
                                f"Name: {name}, Tactics: {len(tactics)}, Detection: {data.get('detection_difficulty')}")
                else:
                    self.log_test(f"MITRE Technique {technique_id}", False, f"HTTP {response.status_code}")
                    return False
                    
            except Exception as e:
                self.log_test(f"MITRE Technique {technique_id}", False, f"Error: {str(e)}")
                return False
        
        return True
    
    def test_mitre_techniques_by_tactic(self):
        """Test MITRE Techniques by Tactic API with specific tactics"""
        print("\n🎯 Testing MITRE Techniques by Tactic API")
        
        # Test with specific MITRE tactics mentioned in review request
        test_tactics = ["Initial Access", "Persistence", "Defense Evasion"]
        
        for tactic in test_tactics:
            try:
                response = self.session.get(f"{self.base_url}/mitre/techniques/by-tactic/{tactic}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if not isinstance(data, list):
                        self.log_test(f"Techniques by Tactic {tactic}", False, f"Expected list, got {type(data)}")
                        return False
                    
                    if len(data) == 0:
                        self.log_test(f"Techniques by Tactic {tactic}", False, "No techniques returned")
                        return False
                    
                    # Verify structure of returned techniques
                    first_technique = data[0]
                    required_fields = ["technique_id", "name", "description", "impact_level", "complexity"]
                    missing_fields = [f for f in required_fields if f not in first_technique]
                    
                    if missing_fields:
                        self.log_test(f"Techniques by Tactic {tactic}", False, f"Missing fields: {missing_fields}")
                        return False
                    
                    self.log_test(f"Techniques by Tactic {tactic}", True, 
                                f"Retrieved {len(data)} techniques")
                else:
                    self.log_test(f"Techniques by Tactic {tactic}", False, f"HTTP {response.status_code}")
                    return False
                    
            except Exception as e:
                self.log_test(f"Techniques by Tactic {tactic}", False, f"Error: {str(e)}")
                return False
        
        return True
    
    def test_mitre_coverage_analysis(self):
        """Test MITRE Coverage Analysis API with existing diagrams"""
        print("\n📊 Testing MITRE Coverage Analysis API")
        
        if not self.test_diagram_id:
            self.log_test("MITRE Coverage Analysis", False, "No test diagram available")
            return False
        
        try:
            response = self.session.post(f"{self.base_url}/diagrams/{self.test_diagram_id}/analyze-coverage")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify coverage analysis fields
                required_fields = [
                    "tactics_covered", "techniques_analyzed", "detection_difficulty",
                    "recommended_mitigations", "data_sources_needed"
                ]
                
                missing_fields = [f for f in required_fields if f not in data]
                if missing_fields:
                    self.log_test("MITRE Coverage Analysis", False, f"Missing fields: {missing_fields}")
                    return False
                
                # Verify coverage analysis results
                tactics_covered = data.get("tactics_covered", [])
                techniques_analyzed = data.get("techniques_analyzed", 0)
                detection_difficulty = data.get("detection_difficulty", 0)
                
                if techniques_analyzed == 0:
                    self.log_test("MITRE Coverage Analysis", False, "No techniques analyzed")
                    return False
                
                # Check for suggested additional techniques
                suggested_techniques = data.get("suggested_additional_techniques", [])
                
                self.log_test("MITRE Coverage Analysis", True, 
                            f"Analyzed {techniques_analyzed} techniques, {len(tactics_covered)} tactics covered, "
                            f"detection difficulty: {detection_difficulty}, {len(suggested_techniques)} suggestions")
                return True
            else:
                self.log_test("MITRE Coverage Analysis", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("MITRE Coverage Analysis", False, f"Error: {str(e)}")
            return False
    
    def test_advanced_risk_analysis(self):
        """Test Advanced Risk Analysis API with diagrams that have simulation results"""
        print("\n⚠️ Testing Advanced Risk Analysis API")
        
        if not self.test_diagram_id:
            self.log_test("Advanced Risk Analysis", False, "No test diagram available")
            return False
        
        try:
            # First run a simulation to generate results
            sim_response = self.session.post(f"{self.base_url}/diagrams/{self.test_diagram_id}/simulate")
            
            if sim_response.status_code != 200:
                self.log_test("Advanced Risk Analysis - Simulation", False, f"Failed to create simulation: {sim_response.status_code}")
                return False
            
            # Now test the risk analysis endpoint
            response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}/risk-analysis")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify advanced risk analysis fields
                required_fields = [
                    "overall_risk_score", "risk_level", "attack_paths_count",
                    "mitre_techniques_count", "detection_coverage", "recommendations_count",
                    "risk_distribution", "top_attack_vectors", "critical_mitre_techniques", "coverage_gaps"
                ]
                
                missing_fields = [f for f in required_fields if f not in data]
                if missing_fields:
                    self.log_test("Advanced Risk Analysis", False, f"Missing fields: {missing_fields}")
                    return False
                
                # Verify enhanced algorithm outputs
                risk_score = data.get("overall_risk_score", 0)
                risk_level = data.get("risk_level", "Unknown")
                attack_paths_count = data.get("attack_paths_count", 0)
                risk_distribution = data.get("risk_distribution", {})
                
                # Verify risk distribution structure
                expected_risk_levels = ["critical", "high", "medium", "low"]
                missing_risk_levels = [level for level in expected_risk_levels if level not in risk_distribution]
                
                if missing_risk_levels:
                    self.log_test("Advanced Risk Analysis", False, f"Missing risk levels: {missing_risk_levels}")
                    return False
                
                self.log_test("Advanced Risk Analysis", True, 
                            f"Risk score: {risk_score}, Level: {risk_level}, "
                            f"Attack paths: {attack_paths_count}, "
                            f"Risk distribution: {risk_distribution}")
                return True
            elif response.status_code == 404:
                self.log_test("Advanced Risk Analysis", False, "No simulation results found")
                return False
            else:
                self.log_test("Advanced Risk Analysis", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Advanced Risk Analysis", False, f"Error: {str(e)}")
            return False
    
    def test_auto_layout_api(self):
        """Test Auto Layout API with NetworkX-based positioning"""
        print("\n🎨 Testing Auto Layout API")
        
        if not self.test_diagram_id:
            self.log_test("Auto Layout API", False, "No test diagram available")
            return False
        
        try:
            response = self.session.post(f"{self.base_url}/diagrams/{self.test_diagram_id}/auto-layout")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify auto-layout response fields
                required_fields = ["layout_positions", "algorithm", "node_count", "group_count"]
                
                missing_fields = [f for f in required_fields if f not in data]
                if missing_fields:
                    self.log_test("Auto Layout API", False, f"Missing fields: {missing_fields}")
                    return False
                
                # Verify NetworkX-based layout positioning
                layout_positions = data.get("layout_positions", {})
                algorithm = data.get("algorithm", "unknown")
                node_count = data.get("node_count", 0)
                group_count = data.get("group_count", 0)
                
                if not layout_positions:
                    self.log_test("Auto Layout API", False, "No layout positions generated")
                    return False
                
                # Verify position structure
                for node_id, position in layout_positions.items():
                    if not isinstance(position, dict) or "x" not in position or "y" not in position:
                        self.log_test("Auto Layout API", False, f"Invalid position format for node {node_id}")
                        return False
                
                self.log_test("Auto Layout API", True, 
                            f"Algorithm: {algorithm}, Nodes: {node_count}, "
                            f"Groups: {group_count}, Positions: {len(layout_positions)}")
                return True
            else:
                self.log_test("Auto Layout API", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Auto Layout API", False, f"Error: {str(e)}")
            return False
    
    def run_advanced_tests(self):
        """Run all advanced endpoint tests"""
        print("🚀 Starting Advanced Backend Endpoints Testing")
        print(f"📡 Testing against: {self.base_url}")
        print("=" * 80)
        
        # Setup test diagram
        if not self.setup_test_diagram():
            print("❌ Failed to setup test diagram")
            return False
        
        print(f"✅ Test diagram created: {self.test_diagram_id}")
        
        # Run the 5 advanced endpoint tests
        tests = [
            self.test_mitre_technique_lookup,
            self.test_mitre_techniques_by_tactic,
            self.test_mitre_coverage_analysis,
            self.test_advanced_risk_analysis,
            self.test_auto_layout_api
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    print(f"❌ {test.__name__} failed")
            except Exception as e:
                print(f"❌ {test.__name__} crashed: {str(e)}")
            print("-" * 40)
        
        print("=" * 80)
        print(f"📊 Advanced Endpoint Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All advanced endpoints are working correctly!")
            return True
        else:
            print(f"⚠️ {total - passed} advanced endpoint tests failed.")
            return False

def main():
    """Main test execution"""
    tester = AdvancedEndpointsTest()
    success = tester.run_advanced_tests()
    
    if success:
        print("\n✅ Advanced backend endpoint testing completed successfully!")
        return True
    else:
        print("\n❌ Advanced backend endpoint testing completed with failures!")
        return False

if __name__ == "__main__":
    main()