#!/usr/bin/env python3
"""
STRIDE Analysis API Testing - Hover Popup Score Investigation
Tests the STRIDE analysis API endpoints to understand data structure and verify score calculation.

TESTING FOCUS:
🎯 STRIDE API STRUCTURE AND SCORE CALCULATION DEBUGGING
1. STRIDE Analysis Endpoint: POST /api/diagrams/{id}/stride/analyze
2. Threat Data Structure: Analyze threats array structure and node associations
3. Risk Score Calculation: Verify how risk_score is calculated and stored in threat objects
4. Single Node vs Full Diagram: Test if API works with single node requests vs requiring full diagram nodes

DEBUGGING GOAL:
The user reports STRIDE scores show as 0.0 in hover popups. The hover handler makes STRIDE analysis calls 
for individual nodes but scores aren't displaying correctly. Need to understand the exact API data format 
to fix the score extraction logic.

TEST SCENARIOS:
1. Health Check - Verify basic API health endpoint
2. Create Test Diagram - Create diagram with WebApp, API, Database nodes with questionnaire responses
3. STRIDE Analysis - Test threat analysis with actual nodes and verify response structure
4. Single Node Analysis - Test if STRIDE analysis works for individual nodes
5. Score Extraction - Verify how risk scores are stored and can be extracted per node
6. Threat Association - Verify how threats are associated with specific nodes
"""

import requests
import json
import uuid
from datetime import datetime, timezone
import sys

# Use the backend URL from frontend/.env with /api suffix
BASE_URL = "https://flowmap-enhance.preview.emergentagent.com/api"

class StrideAnalysisTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.test_results = []
        self.test_diagram_id = None
        self.test_nodes = {}  # Store created test nodes
        
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

    def test_create_diagram_with_nodes(self):
        """Create a test diagram with WebApp, API, and Database nodes with realistic questionnaire responses"""
        try:
            print("🎯 TEST SCENARIO 1: Create Diagram with Realistic Nodes")
            print("=" * 80)
            
            # Create a test diagram
            diagram_data = {
                "title": "STRIDE Analysis Test Diagram",
                "description": "Test diagram for STRIDE score calculation debugging"
            }
            
            response = self.session.post(f"{self.base_url}/diagrams", json=diagram_data)
            
            print(f"📋 Create Diagram Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = self._get_error_detail(response)
                self.log_test("Create Diagram with Nodes", False, 
                            f"HTTP {response.status_code}: {error_detail}")
                return False
            
            data = response.json()
            self.test_diagram_id = data.get("id")
            
            if not self.test_diagram_id:
                self.log_test("Create Diagram with Nodes", False, "No diagram ID returned")
                return False
            
            print(f"📊 Diagram Created: {self.test_diagram_id}")
            
            # Create realistic nodes with questionnaire responses
            nodes_to_create = [
                {
                    "id": f"webapp-{uuid.uuid4().hex[:8]}",
                    "type": "Asset",
                    "subtype": "WebApp",
                    "label": "E-commerce Web Application",
                    "position": {"x": 200, "y": 100},
                    "data": {
                        "criticality": "High",
                        "data_classification": "Confidential",
                        "questionnaire_responses": {
                            "webapp_authentication": "oauth2",
                            "webapp_session_management": "secure_cookies",
                            "webapp_input_validation": "comprehensive",
                            "webapp_encryption": "tls_1_3",
                            "webapp_error_handling": "secure_logging",
                            "webapp_access_control": "rbac"
                        }
                    }
                },
                {
                    "id": f"api-{uuid.uuid4().hex[:8]}",
                    "type": "Asset", 
                    "subtype": "API",
                    "label": "Payment Processing API",
                    "position": {"x": 400, "y": 100},
                    "data": {
                        "criticality": "Critical",
                        "data_classification": "Restricted",
                        "questionnaire_responses": {
                            "api_type": "REST API",
                            "api_authentication_method": "oauth2_bearer",
                            "api_rate_limiting": "implemented",
                            "api_input_validation": "comprehensive",
                            "api_encryption": "tls_1_3",
                            "api_cors_policy": "restrictive",
                            "api_logging": "comprehensive"
                        }
                    }
                },
                {
                    "id": f"database-{uuid.uuid4().hex[:8]}",
                    "type": "Asset",
                    "subtype": "Database", 
                    "label": "Customer Database",
                    "position": {"x": 600, "y": 100},
                    "data": {
                        "criticality": "Critical",
                        "data_classification": "Restricted",
                        "questionnaire_responses": {
                            "database_authentication": "strong_mfa",
                            "database_encryption_at_rest": "tde_enabled",
                            "database_encryption_in_transit": "ssl_enforced",
                            "database_access_control": "rbac_implemented",
                            "database_logging": "comprehensive_audit",
                            "database_backup_encryption": "encrypted_backups"
                        }
                    }
                }
            ]
            
            # Store node references
            for node in nodes_to_create:
                self.test_nodes[node["subtype"]] = node["id"]
            
            # Create edges between nodes
            edges_to_create = [
                {
                    "id": f"edge-webapp-api-{uuid.uuid4().hex[:8]}",
                    "source": self.test_nodes["WebApp"],
                    "target": self.test_nodes["API"],
                    "label": "API Calls",
                    "type": "data_flow"
                },
                {
                    "id": f"edge-api-db-{uuid.uuid4().hex[:8]}",
                    "source": self.test_nodes["API"],
                    "target": self.test_nodes["Database"],
                    "label": "Data Access",
                    "type": "data_flow"
                }
            ]
            
            # Update diagram with nodes and edges
            diagram_update = {
                "id": self.test_diagram_id,
                "title": diagram_data["title"],
                "description": diagram_data["description"],
                "nodes": nodes_to_create,
                "edges": edges_to_create,
                "created_at": data.get("created_at"),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            update_response = self.session.put(f"{self.base_url}/diagrams/{self.test_diagram_id}", json=diagram_update)
            
            if update_response.status_code != 200:
                error_detail = self._get_error_detail(update_response)
                self.log_test("Create Diagram with Nodes", False, 
                            f"Failed to update diagram with nodes: {error_detail}")
                return False
            
            print(f"📊 Nodes Created:")
            for subtype, node_id in self.test_nodes.items():
                print(f"   {subtype}: {node_id}")
            print(f"   Edges: {len(edges_to_create)} connections")
            
            self.log_test("Create Diagram with Nodes", True, 
                        f"✅ SUCCESS: Diagram created with {len(nodes_to_create)} nodes and {len(edges_to_create)} edges")
            
            return True
            
        except Exception as e:
            self.log_test("Create Diagram with Nodes", False, f"Request error: {str(e)}")
            return False

    def test_stride_analysis_structure(self):
        """Test STRIDE analysis endpoint and examine response structure"""
        try:
            print("🎯 TEST SCENARIO 2: STRIDE Analysis API Structure")
            print("=" * 80)
            
            if not self.test_diagram_id:
                self.log_test("STRIDE Analysis Structure", False, "No test diagram available")
                return False
            
            # Test STRIDE analysis on the full diagram
            response = self.session.post(f"{self.base_url}/diagrams/{self.test_diagram_id}/stride/analyze")
            
            print(f"📋 STRIDE Analysis Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = self._get_error_detail(response)
                self.log_test("STRIDE Analysis Structure", False, 
                            f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("STRIDE Analysis Structure", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            print(f"📊 STRIDE Analysis Response Structure:")
            print(f"   Response Keys: {list(data.keys())}")
            
            # Examine threats array structure
            threats = data.get("threats", [])
            print(f"   Total Threats Found: {len(threats)}")
            
            if threats:
                print(f"   Sample Threat Structure:")
                sample_threat = threats[0]
                print(f"     Threat Keys: {list(sample_threat.keys())}")
                
                # Check for risk score in threat
                risk_score = sample_threat.get("risk_score")
                print(f"     Risk Score: {risk_score} (type: {type(risk_score)})")
                
                # Check for affected nodes
                affected_nodes = sample_threat.get("affected_nodes", [])
                node_associations = sample_threat.get("node_associations", [])
                print(f"     Affected Nodes: {affected_nodes}")
                print(f"     Node Associations: {node_associations}")
                
                # Check STRIDE category
                stride_category = sample_threat.get("stride_category")
                print(f"     STRIDE Category: {stride_category}")
                
                # Show first few threats with their scores
                print(f"   Threat Details:")
                for i, threat in enumerate(threats[:3]):
                    threat_id = threat.get("id", "Unknown")
                    title = threat.get("title", "Unknown")
                    risk_score = threat.get("risk_score", 0.0)
                    category = threat.get("stride_category", "Unknown")
                    nodes = threat.get("affected_nodes", [])
                    print(f"     {i+1}. {title}")
                    print(f"        ID: {threat_id}")
                    print(f"        Risk Score: {risk_score}")
                    print(f"        Category: {category}")
                    print(f"        Affected Nodes: {nodes}")
            
            # Check analysis summary
            analysis_summary = data.get("analysis_summary", {})
            print(f"   Analysis Summary: {analysis_summary}")
            
            # Store response for further analysis
            self.stride_response = data
            
            self.log_test("STRIDE Analysis Structure", True, 
                        f"✅ SUCCESS: STRIDE analysis completed, found {len(threats)} threats")
            
            return True
            
        except Exception as e:
            self.log_test("STRIDE Analysis Structure", False, f"Request error: {str(e)}")
            return False

    def test_single_node_stride_analysis(self):
        """Test if STRIDE analysis works for individual nodes"""
        try:
            print("🎯 TEST SCENARIO 3: Single Node STRIDE Analysis")
            print("=" * 80)
            
            if not self.test_diagram_id or not self.test_nodes:
                self.log_test("Single Node STRIDE Analysis", False, "No test data available")
                return False
            
            # Test with WebApp node specifically
            webapp_node_id = self.test_nodes.get("WebApp")
            if not webapp_node_id:
                self.log_test("Single Node STRIDE Analysis", False, "No WebApp node available")
                return False
            
            print(f"   Testing STRIDE analysis for WebApp node: {webapp_node_id}")
            
            # Try to analyze just the WebApp node by creating a minimal diagram
            single_node_diagram = {
                "title": "Single Node STRIDE Test",
                "description": "Test STRIDE analysis for single node",
                "nodes": [
                    {
                        "id": webapp_node_id,
                        "type": "Asset",
                        "subtype": "WebApp",
                        "label": "E-commerce Web Application",
                        "position": {"x": 200, "y": 100},
                        "data": {
                            "criticality": "High",
                            "data_classification": "Confidential",
                            "questionnaire_responses": {
                                "webapp_authentication": "oauth2",
                                "webapp_session_management": "secure_cookies",
                                "webapp_input_validation": "comprehensive",
                                "webapp_encryption": "tls_1_3",
                                "webapp_error_handling": "secure_logging",
                                "webapp_access_control": "rbac"
                            }
                        }
                    }
                ],
                "edges": []
            }
            
            # Create temporary diagram for single node test
            temp_diagram_response = self.session.post(f"{self.base_url}/diagrams", json={
                "title": single_node_diagram["title"],
                "description": single_node_diagram["description"]
            })
            
            if temp_diagram_response.status_code != 200:
                self.log_test("Single Node STRIDE Analysis", False, "Failed to create temp diagram")
                return False
            
            temp_diagram_data = temp_diagram_response.json()
            temp_diagram_id = temp_diagram_data.get("id")
            
            # Update with single node
            single_node_diagram["id"] = temp_diagram_id
            single_node_diagram["created_at"] = temp_diagram_data.get("created_at")
            single_node_diagram["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            update_response = self.session.put(f"{self.base_url}/diagrams/{temp_diagram_id}", json=single_node_diagram)
            
            if update_response.status_code != 200:
                self.log_test("Single Node STRIDE Analysis", False, "Failed to update temp diagram")
                return False
            
            # Now test STRIDE analysis on single node diagram
            response = self.session.post(f"{self.base_url}/diagrams/{temp_diagram_id}/stride/analyze")
            
            print(f"📋 Single Node STRIDE Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = self._get_error_detail(response)
                self.log_test("Single Node STRIDE Analysis", False, 
                            f"HTTP {response.status_code}: {error_detail}")
                # Cleanup temp diagram
                self.session.delete(f"{self.base_url}/diagrams/{temp_diagram_id}")
                return False
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Single Node STRIDE Analysis", False, 
                            f"Invalid JSON response: {str(e)}")
                # Cleanup temp diagram
                self.session.delete(f"{self.base_url}/diagrams/{temp_diagram_id}")
                return False
            
            threats = data.get("threats", [])
            print(f"📊 Single Node STRIDE Results:")
            print(f"   Threats Found: {len(threats)}")
            
            if threats:
                print(f"   WebApp-specific Threats:")
                for i, threat in enumerate(threats):
                    title = threat.get("title", "Unknown")
                    risk_score = threat.get("risk_score", 0.0)
                    category = threat.get("stride_category", "Unknown")
                    affected_nodes = threat.get("affected_nodes", [])
                    print(f"     {i+1}. {title}")
                    print(f"        Risk Score: {risk_score}")
                    print(f"        Category: {category}")
                    print(f"        Affected Nodes: {affected_nodes}")
            
            # Cleanup temp diagram
            cleanup_response = self.session.delete(f"{self.base_url}/diagrams/{temp_diagram_id}")
            print(f"   Temp diagram cleanup: HTTP {cleanup_response.status_code}")
            
            self.log_test("Single Node STRIDE Analysis", True, 
                        f"✅ SUCCESS: Single node STRIDE analysis works, found {len(threats)} threats")
            
            return True
            
        except Exception as e:
            self.log_test("Single Node STRIDE Analysis", False, f"Request error: {str(e)}")
            return False

    def test_stride_score_extraction(self):
        """Test how to extract STRIDE scores per node from the API response"""
        try:
            print("🎯 TEST SCENARIO 4: STRIDE Score Extraction Logic")
            print("=" * 80)
            
            if not hasattr(self, 'stride_response') or not self.stride_response:
                self.log_test("STRIDE Score Extraction", False, "No STRIDE response data available")
                return False
            
            threats = self.stride_response.get("threats", [])
            
            print(f"📊 Score Extraction Analysis:")
            print(f"   Total Threats: {len(threats)}")
            
            # Group threats by affected nodes to calculate per-node scores
            node_threats = {}
            node_scores = {}
            
            for threat in threats:
                risk_score = threat.get("risk_score", 0.0)
                affected_nodes = threat.get("affected_nodes", [])
                
                # Handle different ways nodes might be associated
                if not affected_nodes:
                    # Check for other node association fields
                    node_associations = threat.get("node_associations", [])
                    target_node = threat.get("target_node")
                    source_node = threat.get("source_node")
                    
                    if node_associations:
                        affected_nodes = node_associations
                    elif target_node:
                        affected_nodes = [target_node]
                    elif source_node:
                        affected_nodes = [source_node]
                
                # Associate threat with nodes
                for node_id in affected_nodes:
                    if node_id not in node_threats:
                        node_threats[node_id] = []
                        node_scores[node_id] = []
                    
                    node_threats[node_id].append(threat)
                    node_scores[node_id].append(risk_score)
            
            print(f"   Node-Threat Associations:")
            for node_id, threats_list in node_threats.items():
                scores = node_scores[node_id]
                avg_score = sum(scores) / len(scores) if scores else 0.0
                max_score = max(scores) if scores else 0.0
                
                # Try to match with our test nodes
                node_type = "Unknown"
                for subtype, test_node_id in self.test_nodes.items():
                    if test_node_id == node_id:
                        node_type = subtype
                        break
                
                print(f"     Node: {node_id} ({node_type})")
                print(f"       Threats: {len(threats_list)}")
                print(f"       Scores: {scores}")
                print(f"       Average Score: {avg_score:.2f}")
                print(f"       Max Score: {max_score:.2f}")
            
            # Test different score extraction methods
            print(f"   Score Extraction Methods:")
            
            # Method 1: Average score per node
            print(f"     Method 1 - Average Score per Node:")
            for node_id, scores in node_scores.items():
                avg_score = sum(scores) / len(scores) if scores else 0.0
                node_type = "Unknown"
                for subtype, test_node_id in self.test_nodes.items():
                    if test_node_id == node_id:
                        node_type = subtype
                        break
                print(f"       {node_type}: {avg_score:.2f}")
            
            # Method 2: Maximum score per node
            print(f"     Method 2 - Maximum Score per Node:")
            for node_id, scores in node_scores.items():
                max_score = max(scores) if scores else 0.0
                node_type = "Unknown"
                for subtype, test_node_id in self.test_nodes.items():
                    if test_node_id == node_id:
                        node_type = subtype
                        break
                print(f"       {node_type}: {max_score:.2f}")
            
            # Method 3: Total risk score per node
            print(f"     Method 3 - Total Risk Score per Node:")
            for node_id, scores in node_scores.items():
                total_score = sum(scores)
                node_type = "Unknown"
                for subtype, test_node_id in self.test_nodes.items():
                    if test_node_id == node_id:
                        node_type = subtype
                        break
                print(f"       {node_type}: {total_score:.2f}")
            
            # Check if any scores are 0.0 (the reported issue)
            zero_score_nodes = []
            for node_id, scores in node_scores.items():
                if not scores or all(score == 0.0 for score in scores):
                    zero_score_nodes.append(node_id)
            
            if zero_score_nodes:
                print(f"   ⚠️ ISSUE FOUND: Nodes with 0.0 scores: {zero_score_nodes}")
                print(f"     This matches the reported hover popup issue!")
            else:
                print(f"   ✅ All nodes have non-zero scores")
            
            self.log_test("STRIDE Score Extraction", True, 
                        f"✅ SUCCESS: Score extraction analysis completed, {len(node_scores)} nodes analyzed")
            
            return True
            
        except Exception as e:
            self.log_test("STRIDE Score Extraction", False, f"Analysis error: {str(e)}")
            return False

    def test_stride_coverage_endpoint(self):
        """Test STRIDE coverage endpoint for additional score information"""
        try:
            print("🎯 TEST SCENARIO 5: STRIDE Coverage Endpoint")
            print("=" * 80)
            
            if not self.test_diagram_id:
                self.log_test("STRIDE Coverage Endpoint", False, "No test diagram available")
                return False
            
            response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}/stride/coverage")
            
            print(f"📋 STRIDE Coverage Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = self._get_error_detail(response)
                self.log_test("STRIDE Coverage Endpoint", False, 
                            f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("STRIDE Coverage Endpoint", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            print(f"📊 STRIDE Coverage Response:")
            print(f"   Response Keys: {list(data.keys())}")
            
            # Check for coverage metrics
            totals = data.get("totals", {})
            mitigated = data.get("mitigated", {})
            residual_risk_avg = data.get("residual_risk_avg", 0.0)
            total_threats = data.get("total_threats", 0)
            mitigation_percentage = data.get("mitigation_percentage", 0.0)
            
            print(f"   Coverage Metrics:")
            print(f"     Total Threats: {total_threats}")
            print(f"     Mitigation Percentage: {mitigation_percentage}%")
            print(f"     Residual Risk Average: {residual_risk_avg}")
            print(f"     Totals: {totals}")
            print(f"     Mitigated: {mitigated}")
            
            # Check if coverage provides per-node information
            if isinstance(totals, dict):
                print(f"   Per-Category Totals:")
                for category, count in totals.items():
                    print(f"     {category}: {count}")
            
            if isinstance(mitigated, dict):
                print(f"   Per-Category Mitigated:")
                for category, count in mitigated.items():
                    print(f"     {category}: {count}")
            
            self.log_test("STRIDE Coverage Endpoint", True, 
                        f"✅ SUCCESS: STRIDE coverage endpoint working, {total_threats} total threats")
            
            return True
            
        except Exception as e:
            self.log_test("STRIDE Coverage Endpoint", False, f"Request error: {str(e)}")
            return False

    def test_hover_popup_scenario(self):
        """Test the exact scenario that hover popups would use"""
        try:
            print("🎯 TEST SCENARIO 6: Hover Popup Scenario Simulation")
            print("=" * 80)
            
            if not self.test_diagram_id or not self.test_nodes:
                self.log_test("Hover Popup Scenario", False, "No test data available")
                return False
            
            print("   Simulating hover popup STRIDE score requests...")
            
            # Simulate what the hover popup would do for each node
            for node_type, node_id in self.test_nodes.items():
                print(f"   Testing hover popup for {node_type} node: {node_id}")
                
                # The hover popup likely calls STRIDE analysis for the full diagram
                # then extracts scores for the specific node
                response = self.session.post(f"{self.base_url}/diagrams/{self.test_diagram_id}/stride/analyze")
                
                if response.status_code != 200:
                    print(f"     ❌ STRIDE analysis failed for {node_type}")
                    continue
                
                try:
                    data = response.json()
                    threats = data.get("threats", [])
                    
                    # Extract threats affecting this specific node
                    node_threats = []
                    node_scores = []
                    
                    for threat in threats:
                        affected_nodes = threat.get("affected_nodes", [])
                        
                        # Check various ways the node might be referenced
                        if (node_id in affected_nodes or 
                            threat.get("target_node") == node_id or
                            threat.get("source_node") == node_id or
                            node_id in threat.get("node_associations", [])):
                            
                            node_threats.append(threat)
                            risk_score = threat.get("risk_score", 0.0)
                            node_scores.append(risk_score)
                    
                    # Calculate score for hover popup display
                    if node_scores:
                        avg_score = sum(node_scores) / len(node_scores)
                        max_score = max(node_scores)
                        total_score = sum(node_scores)
                    else:
                        avg_score = max_score = total_score = 0.0
                    
                    print(f"     {node_type} STRIDE Scores:")
                    print(f"       Threats: {len(node_threats)}")
                    print(f"       Individual Scores: {node_scores}")
                    print(f"       Average: {avg_score:.2f}")
                    print(f"       Maximum: {max_score:.2f}")
                    print(f"       Total: {total_score:.2f}")
                    
                    # This is what would be displayed in hover popup
                    hover_score = avg_score  # or max_score, depending on implementation
                    print(f"       Hover Popup Score: {hover_score:.2f}")
                    
                    if hover_score == 0.0:
                        print(f"       ⚠️ ISSUE: {node_type} shows 0.0 score (matches reported bug)")
                    else:
                        print(f"       ✅ {node_type} has valid score")
                
                except json.JSONDecodeError:
                    print(f"     ❌ Invalid JSON response for {node_type}")
                
                print()
            
            self.log_test("Hover Popup Scenario", True, 
                        f"✅ SUCCESS: Hover popup scenario simulation completed")
            
            return True
            
        except Exception as e:
            self.log_test("Hover Popup Scenario", False, f"Simulation error: {str(e)}")
            return False

    def _get_error_detail(self, response):
        """Extract error detail from response"""
        try:
            error_data = response.json()
            return error_data.get('detail', str(error_data))
        except:
            return response.text

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
        """Run all STRIDE analysis tests"""
        print("🚀 STARTING STRIDE ANALYSIS API TESTING FOR HOVER POPUP DEBUGGING")
        print("=" * 80)
        print("Testing STRIDE analysis endpoints to understand data structure and score calculation:")
        print("1. Test basic API health endpoint")
        print("2. Create diagram with realistic nodes and questionnaire responses")
        print("3. Test STRIDE analysis API structure and response format")
        print("4. Test single node STRIDE analysis capability")
        print("5. Analyze score extraction methods for hover popups")
        print("6. Test STRIDE coverage endpoint for additional metrics")
        print("7. Simulate exact hover popup scenario")
        print("=" * 80)
        
        tests = [
            self.test_health_check,
            self.test_create_diagram_with_nodes,
            self.test_stride_analysis_structure,
            self.test_single_node_stride_analysis,
            self.test_stride_score_extraction,
            self.test_stride_coverage_endpoint,
            self.test_hover_popup_scenario,
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
        
        # Summary for STRIDE analysis debugging
        if passed == total:
            print("\n🎉 STRIDE ANALYSIS API TESTING: ALL TESTS PASSED")
            print("✅ STRIDE analysis endpoints are working correctly")
            print("✅ API response structure documented and analyzed")
            print("✅ Score extraction methods identified and tested")
            print("✅ Hover popup scenario simulated successfully")
        else:
            print(f"\n⚠️ STRIDE ANALYSIS API TESTING: {total-passed} TESTS FAILED")
            print("❌ Some STRIDE functionality may have issues")
            print("❌ Review failed tests above for debugging information")
        
        return passed == total

if __name__ == "__main__":
    tester = StrideAnalysisTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)