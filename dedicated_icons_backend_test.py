#!/usr/bin/env python3
"""
Backend API Testing - Dedicated Icon Functionality Support
Tests backend endpoints that support the dedicated icon functionality for Security Nodes application.

TESTING FOCUS:
🎯 DEDICATED ICON FUNCTIONALITY BACKEND SUPPORT TESTING
1. Node Subtype Information: Verify backend provides correct subtype data for icon mapping
2. Node Creation: Test that nodes are created with proper subtype information
3. Node Retrieval: Verify nodes return correct subtype data for frontend icon rendering
4. Template System: Test that templates provide nodes with correct subtypes
5. Questionnaire System: Verify questionnaire endpoints support all node subtypes with icons

TEST SCENARIOS:
1. Health Check - Verify basic API health endpoint
2. Create Test Diagram - Create diagram for testing node operations
3. Node Subtype Support - Test creation of nodes with different subtypes (WebApp, API, Database, etc.)
4. Template System - Verify templates provide nodes with correct subtype information
5. Questionnaire Support - Test questionnaire endpoints for nodes with dedicated icons
6. Node Retrieval - Verify nodes return proper subtype data for icon mapping

**EXPECTED RESULTS:** 
- Backend provides correct subtype information for all node types with dedicated icons
- Node creation preserves subtype data needed for frontend icon mapping
- Template system includes proper subtype information
- Questionnaire endpoints support all node subtypes that have dedicated icons
- Node retrieval returns complete subtype data for frontend icon rendering
"""

import requests
import json
import uuid
from datetime import datetime, timezone
import sys

# Use the backend URL from frontend/.env with /api suffix
BASE_URL = "https://element-iconography.preview.emergentagent.com/api"

class DedicatedIconsBackendTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.test_results = []
        self.test_diagram_id = None
        
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

    def test_create_test_diagram(self):
        """TEST SCENARIO 1: Create a test diagram for node operations"""
        try:
            print("🎯 TEST SCENARIO 1: Create Test Diagram for Icon Testing")
            print("=" * 80)
            
            diagram_data = {
                "title": "Dedicated Icons Test Diagram",
                "description": "Test diagram for verifying backend support for dedicated icon functionality"
            }
            
            response = self.session.post(f"{self.base_url}/diagrams", json=diagram_data)
            
            print(f"📋 Create Diagram Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("Create Test Diagram", False, 
                            f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Create Test Diagram", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            self.test_diagram_id = data.get("id")
            
            if not self.test_diagram_id:
                self.log_test("Create Test Diagram", False, "No diagram ID returned")
                return False
            
            print(f"📊 Test Diagram Created Successfully:")
            print(f"   Diagram ID: {self.test_diagram_id}")
            print(f"   Title: {data.get('title')}")
            
            self.log_test("Create Test Diagram", True, 
                        f"✅ SUCCESS: Test diagram created (ID: {self.test_diagram_id})")
            
            return True
            
        except Exception as e:
            self.log_test("Create Test Diagram", False, f"Request error: {str(e)}")
            return False

    def test_node_subtype_support(self):
        """TEST SCENARIO 2: Test backend support for nodes with dedicated icon subtypes"""
        try:
            print("🎯 TEST SCENARIO 2: Node Subtype Support for Dedicated Icons")
            print("=" * 80)
            
            if not self.test_diagram_id:
                self.log_test("Node Subtype Support", False, "No test diagram ID available")
                return False
            
            # Define nodes with subtypes that have dedicated icons
            test_nodes = [
                {
                    "id": f"webapp-{uuid.uuid4().hex[:8]}",
                    "type": "Asset",
                    "subtype": "WebApp",
                    "label": "Web Application",
                    "position": {"x": 100, "y": 100},
                    "data": {
                        "criticality": "High",
                        "data_classification": "Confidential"
                    }
                },
                {
                    "id": f"api-{uuid.uuid4().hex[:8]}",
                    "type": "Asset", 
                    "subtype": "API",
                    "label": "API Gateway",
                    "position": {"x": 300, "y": 100},
                    "data": {
                        "criticality": "High",
                        "data_classification": "Confidential"
                    }
                },
                {
                    "id": f"database-{uuid.uuid4().hex[:8]}",
                    "type": "Asset",
                    "subtype": "Database", 
                    "label": "Production Database",
                    "position": {"x": 500, "y": 100},
                    "data": {
                        "criticality": "Critical",
                        "data_classification": "Restricted"
                    }
                },
                {
                    "id": f"s3bucket-{uuid.uuid4().hex[:8]}",
                    "type": "Asset",
                    "subtype": "S3Bucket",
                    "label": "Cloud Storage",
                    "position": {"x": 700, "y": 100},
                    "data": {
                        "criticality": "Medium",
                        "data_classification": "Internal"
                    }
                },
                {
                    "id": f"vm-{uuid.uuid4().hex[:8]}",
                    "type": "Asset",
                    "subtype": "VM",
                    "label": "Virtual Machine",
                    "position": {"x": 100, "y": 300},
                    "data": {
                        "criticality": "Medium",
                        "data_classification": "Internal"
                    }
                }
            ]
            
            # Get current diagram
            diagram_response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}")
            if diagram_response.status_code != 200:
                self.log_test("Node Subtype Support", False, "Cannot retrieve test diagram")
                return False
            
            diagram_data = diagram_response.json()
            diagram_data["nodes"] = test_nodes
            diagram_data["edges"] = diagram_data.get("edges", [])
            
            # Update diagram with test nodes
            update_response = self.session.put(f"{self.base_url}/diagrams/{self.test_diagram_id}", json=diagram_data)
            
            print(f"📋 Update Diagram Response Status: HTTP {update_response.status_code}")
            
            if update_response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = update_response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = update_response.text
                
                self.log_test("Node Subtype Support", False, 
                            f"HTTP {update_response.status_code}: {error_detail}")
                return False
            
            # Verify nodes were created with correct subtype information
            verify_response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}")
            if verify_response.status_code != 200:
                self.log_test("Node Subtype Support", False, "Cannot verify created nodes")
                return False
            
            verified_data = verify_response.json()
            created_nodes = verified_data.get("nodes", [])
            
            print(f"📊 Node Subtype Support Results:")
            print(f"   Nodes Created: {len(created_nodes)}")
            
            # Verify each node has correct subtype information
            subtype_verification = {}
            for node in created_nodes:
                node_subtype = node.get("subtype")
                node_type = node.get("type")
                node_label = node.get("label")
                
                if node_subtype:
                    subtype_verification[node_subtype] = {
                        "type": node_type,
                        "label": node_label,
                        "has_subtype": True,
                        "subtype_value": node_subtype
                    }
                    print(f"   ✅ {node_label}: type={node_type}, subtype={node_subtype}")
                else:
                    print(f"   ❌ {node_label}: Missing subtype information")
                    subtype_verification[node_label] = {
                        "type": node_type,
                        "label": node_label,
                        "has_subtype": False,
                        "subtype_value": None
                    }
            
            # Check if all expected subtypes are present
            expected_subtypes = ["WebApp", "API", "Database", "S3Bucket", "VM"]
            missing_subtypes = []
            
            for expected in expected_subtypes:
                if expected not in subtype_verification:
                    missing_subtypes.append(expected)
            
            if missing_subtypes:
                self.log_test("Node Subtype Support", False, 
                            f"Missing subtypes: {missing_subtypes}")
                return False
            
            # Verify all nodes have subtype information
            nodes_without_subtypes = [k for k, v in subtype_verification.items() if not v["has_subtype"]]
            if nodes_without_subtypes:
                self.log_test("Node Subtype Support", False, 
                            f"Nodes without subtype: {nodes_without_subtypes}")
                return False
            
            self.log_test("Node Subtype Support", True, 
                        f"✅ SUCCESS: All {len(expected_subtypes)} node subtypes supported with proper data")
            
            return True
            
        except Exception as e:
            self.log_test("Node Subtype Support", False, f"Request error: {str(e)}")
            return False

    def test_template_system_subtype_support(self):
        """TEST SCENARIO 3: Test template system provides nodes with correct subtypes"""
        try:
            print("🎯 TEST SCENARIO 3: Template System Subtype Support")
            print("=" * 80)
            
            # Get available templates
            response = self.session.get(f"{self.base_url}/templates")
            
            print(f"📋 Get Templates Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("Template System Subtype Support", False, 
                            f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                templates = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Template System Subtype Support", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            print(f"📊 Template System Results:")
            print(f"   Available Templates: {len(templates)}")
            
            # Analyze templates for subtype information
            template_subtypes = set()
            template_analysis = {}
            
            for template in templates:
                template_name = template.get("name", "Unknown")
                template_nodes = template.get("nodes", [])
                
                template_analysis[template_name] = {
                    "node_count": len(template_nodes),
                    "subtypes": []
                }
                
                print(f"   📋 Template: {template_name}")
                print(f"      Nodes: {len(template_nodes)}")
                
                for node in template_nodes:
                    node_subtype = node.get("subtype")
                    node_type = node.get("type")
                    node_label = node.get("label", "Unknown")
                    
                    if node_subtype:
                        template_subtypes.add(node_subtype)
                        template_analysis[template_name]["subtypes"].append(node_subtype)
                        print(f"         ✅ {node_label}: {node_type}/{node_subtype}")
                    else:
                        print(f"         ❌ {node_label}: Missing subtype")
            
            # Check for key subtypes that should have dedicated icons
            key_subtypes = ["WebApp", "API", "Database", "WAF", "EDR"]
            found_key_subtypes = []
            
            for subtype in key_subtypes:
                if subtype in template_subtypes:
                    found_key_subtypes.append(subtype)
            
            print(f"   🎯 Key Subtypes Found: {found_key_subtypes}")
            print(f"   📊 Total Unique Subtypes: {len(template_subtypes)}")
            print(f"   📋 All Subtypes: {sorted(list(template_subtypes))}")
            
            if len(found_key_subtypes) == 0:
                self.log_test("Template System Subtype Support", False, 
                            "No key subtypes found in templates")
                return False
            
            self.log_test("Template System Subtype Support", True, 
                        f"✅ SUCCESS: Templates provide {len(template_subtypes)} unique subtypes, including {len(found_key_subtypes)} key subtypes")
            
            return True
            
        except Exception as e:
            self.log_test("Template System Subtype Support", False, f"Request error: {str(e)}")
            return False

    def test_questionnaire_subtype_support(self):
        """TEST SCENARIO 4: Test questionnaire endpoints support nodes with dedicated icons"""
        try:
            print("🎯 TEST SCENARIO 4: Questionnaire Subtype Support")
            print("=" * 80)
            
            # Test questionnaire support for key subtypes with dedicated icons
            key_subtypes = ["WebApp", "API", "Database"]
            questionnaire_results = {}
            
            for subtype in key_subtypes:
                print(f"   🔍 Testing questionnaire support for {subtype}...")
                
                # Test getting prompts for this subtype
                response = self.session.get(f"{self.base_url}/intelligent-nodes/{subtype}/prompts")
                
                print(f"      📋 {subtype} Prompts Response: HTTP {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        prompts_count = data.get("prompts_count", 0)
                        success = data.get("success", False)
                        node_subtype = data.get("node_subtype")
                        
                        questionnaire_results[subtype] = {
                            "supported": True,
                            "prompts_count": prompts_count,
                            "success": success,
                            "node_subtype": node_subtype
                        }
                        
                        print(f"      ✅ {subtype}: {prompts_count} prompts, success={success}")
                        
                        if node_subtype != subtype:
                            print(f"      ⚠️ {subtype}: Subtype mismatch - expected {subtype}, got {node_subtype}")
                        
                    except json.JSONDecodeError as e:
                        questionnaire_results[subtype] = {
                            "supported": False,
                            "error": f"JSON decode error: {str(e)}"
                        }
                        print(f"      ❌ {subtype}: JSON decode error")
                        
                else:
                    questionnaire_results[subtype] = {
                        "supported": False,
                        "status_code": response.status_code,
                        "error": response.text[:100]
                    }
                    print(f"      ❌ {subtype}: HTTP {response.status_code}")
            
            print(f"📊 Questionnaire Subtype Support Results:")
            
            supported_count = 0
            total_prompts = 0
            
            for subtype, result in questionnaire_results.items():
                if result.get("supported", False):
                    supported_count += 1
                    total_prompts += result.get("prompts_count", 0)
                    print(f"   ✅ {subtype}: {result.get('prompts_count', 0)} prompts")
                else:
                    print(f"   ❌ {subtype}: {result.get('error', 'Not supported')}")
            
            print(f"   📊 Summary: {supported_count}/{len(key_subtypes)} subtypes supported")
            print(f"   📋 Total Prompts: {total_prompts}")
            
            if supported_count == 0:
                self.log_test("Questionnaire Subtype Support", False, 
                            "No questionnaire support found for key subtypes")
                return False
            
            if supported_count < len(key_subtypes):
                self.log_test("Questionnaire Subtype Support", False, 
                            f"Only {supported_count}/{len(key_subtypes)} subtypes supported")
                return False
            
            self.log_test("Questionnaire Subtype Support", True, 
                        f"✅ SUCCESS: All {supported_count} key subtypes have questionnaire support with {total_prompts} total prompts")
            
            return True
            
        except Exception as e:
            self.log_test("Questionnaire Subtype Support", False, f"Request error: {str(e)}")
            return False

    def test_node_retrieval_subtype_data(self):
        """TEST SCENARIO 5: Test node retrieval returns proper subtype data for icon mapping"""
        try:
            print("🎯 TEST SCENARIO 5: Node Retrieval Subtype Data")
            print("=" * 80)
            
            if not self.test_diagram_id:
                self.log_test("Node Retrieval Subtype Data", False, "No test diagram ID available")
                return False
            
            # Retrieve the test diagram with nodes
            response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}")
            
            print(f"📋 Get Diagram Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("Node Retrieval Subtype Data", False, 
                            f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                diagram_data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Node Retrieval Subtype Data", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            nodes = diagram_data.get("nodes", [])
            
            print(f"📊 Node Retrieval Results:")
            print(f"   Retrieved Nodes: {len(nodes)}")
            
            # Analyze retrieved nodes for subtype data completeness
            subtype_analysis = {
                "nodes_with_subtype": 0,
                "nodes_without_subtype": 0,
                "subtypes_found": set(),
                "complete_nodes": [],
                "incomplete_nodes": []
            }
            
            for node in nodes:
                node_id = node.get("id", "Unknown")
                node_type = node.get("type", "Unknown")
                node_subtype = node.get("subtype")
                node_label = node.get("label", "Unknown")
                
                if node_subtype:
                    subtype_analysis["nodes_with_subtype"] += 1
                    subtype_analysis["subtypes_found"].add(node_subtype)
                    subtype_analysis["complete_nodes"].append({
                        "id": node_id,
                        "type": node_type,
                        "subtype": node_subtype,
                        "label": node_label
                    })
                    print(f"   ✅ {node_label}: {node_type}/{node_subtype}")
                else:
                    subtype_analysis["nodes_without_subtype"] += 1
                    subtype_analysis["incomplete_nodes"].append({
                        "id": node_id,
                        "type": node_type,
                        "label": node_label
                    })
                    print(f"   ❌ {node_label}: Missing subtype data")
            
            print(f"   📊 Analysis Summary:")
            print(f"      Nodes with subtype: {subtype_analysis['nodes_with_subtype']}")
            print(f"      Nodes without subtype: {subtype_analysis['nodes_without_subtype']}")
            print(f"      Unique subtypes: {len(subtype_analysis['subtypes_found'])}")
            print(f"      Subtypes found: {sorted(list(subtype_analysis['subtypes_found']))}")
            
            # Check if we have the expected subtypes for dedicated icons
            expected_subtypes = {"WebApp", "API", "Database", "S3Bucket", "VM"}
            found_expected = expected_subtypes.intersection(subtype_analysis["subtypes_found"])
            
            print(f"      Expected subtypes found: {len(found_expected)}/{len(expected_subtypes)}")
            print(f"      Found: {sorted(list(found_expected))}")
            
            if subtype_analysis["nodes_without_subtype"] > 0:
                self.log_test("Node Retrieval Subtype Data", False, 
                            f"{subtype_analysis['nodes_without_subtype']} nodes missing subtype data")
                return False
            
            if len(found_expected) == 0:
                self.log_test("Node Retrieval Subtype Data", False, 
                            "No expected subtypes found in retrieved nodes")
                return False
            
            self.log_test("Node Retrieval Subtype Data", True, 
                        f"✅ SUCCESS: All {subtype_analysis['nodes_with_subtype']} nodes have subtype data, {len(found_expected)} expected subtypes found")
            
            return True
            
        except Exception as e:
            self.log_test("Node Retrieval Subtype Data", False, f"Request error: {str(e)}")
            return False

    def test_comprehensive_icon_mapping_support(self):
        """TEST SCENARIO 6: Comprehensive test of backend support for all icon mappings"""
        try:
            print("🎯 TEST SCENARIO 6: Comprehensive Icon Mapping Support")
            print("=" * 80)
            
            # Define all subtypes that should have dedicated icons based on frontend code
            icon_subtypes = {
                # Actor subtypes
                "ExternalAttacker": "Shield",
                "Insider": "Users", 
                "ServiceAccount": "Settings",
                
                # Asset subtypes
                "WebApp": "Globe",
                "API": "Zap",
                "Database": "Database",
                "S3Bucket": "HardDrive",
                "VM": "Monitor",
                "IMDS": "FileText",
                
                # Surface subtypes
                "SSRF": "Bug",
                "SQLi": "Database", 
                "IDOR": "Lock",
                "RCE": "Cpu",
                "WeakIAM": "Users",
                
                # Control subtypes
                "WAF": "Shield",
                "EDR": "Eye",
                "EgressProxy": "Router",
                "IAMPolicy": "Users",
                "NetworkACL": "Network",
                
                # Additional subtypes
                "Backup": "HardDrive",
                "Monitoring": "Monitor",
                "Container": "Container",
                "LoadBalancer": "Router",
                "CDN": "Wifi"
            }
            
            print(f"📊 Testing backend support for {len(icon_subtypes)} subtypes with dedicated icons:")
            
            # Test a sample of these subtypes to verify backend support
            test_subtypes = ["WebApp", "API", "Database", "WAF", "EDR", "Backup", "Monitoring"]
            support_results = {}
            
            for subtype in test_subtypes:
                print(f"   🔍 Testing {subtype} (icon: {icon_subtypes.get(subtype, 'Unknown')})...")
                
                # Test if questionnaire system supports this subtype
                response = self.session.get(f"{self.base_url}/intelligent-nodes/{subtype}/prompts")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        success = data.get("success", False)
                        prompts_count = data.get("prompts_count", 0)
                        
                        support_results[subtype] = {
                            "supported": success,
                            "prompts_count": prompts_count,
                            "icon": icon_subtypes.get(subtype, "Unknown")
                        }
                        
                        if success:
                            print(f"      ✅ {subtype}: Supported with {prompts_count} prompts")
                        else:
                            print(f"      ⚠️ {subtype}: Response received but success=false")
                            
                    except json.JSONDecodeError:
                        support_results[subtype] = {
                            "supported": False,
                            "error": "JSON decode error",
                            "icon": icon_subtypes.get(subtype, "Unknown")
                        }
                        print(f"      ❌ {subtype}: JSON decode error")
                else:
                    support_results[subtype] = {
                        "supported": False,
                        "status_code": response.status_code,
                        "icon": icon_subtypes.get(subtype, "Unknown")
                    }
                    print(f"      ❌ {subtype}: HTTP {response.status_code}")
            
            # Analyze results
            supported_count = sum(1 for result in support_results.values() if result.get("supported", False))
            total_prompts = sum(result.get("prompts_count", 0) for result in support_results.values() if result.get("supported", False))
            
            print(f"📊 Comprehensive Icon Mapping Support Results:")
            print(f"   Subtypes Tested: {len(test_subtypes)}")
            print(f"   Subtypes Supported: {supported_count}")
            print(f"   Total Prompts Available: {total_prompts}")
            print(f"   Support Rate: {(supported_count/len(test_subtypes)*100):.1f}%")
            
            # List supported subtypes with their icons
            print(f"   ✅ Supported Subtypes:")
            for subtype, result in support_results.items():
                if result.get("supported", False):
                    print(f"      {subtype} → {result['icon']} ({result['prompts_count']} prompts)")
            
            # List unsupported subtypes
            unsupported = [subtype for subtype, result in support_results.items() if not result.get("supported", False)]
            if unsupported:
                print(f"   ❌ Unsupported Subtypes: {unsupported}")
            
            if supported_count == 0:
                self.log_test("Comprehensive Icon Mapping Support", False, 
                            "No subtypes with dedicated icons are supported by backend")
                return False
            
            # Consider it successful if at least 70% of tested subtypes are supported
            success_threshold = 0.7
            success_rate = supported_count / len(test_subtypes)
            
            if success_rate >= success_threshold:
                self.log_test("Comprehensive Icon Mapping Support", True, 
                            f"✅ SUCCESS: {supported_count}/{len(test_subtypes)} subtypes supported ({success_rate*100:.1f}% success rate)")
                return True
            else:
                self.log_test("Comprehensive Icon Mapping Support", False, 
                            f"Low support rate: {supported_count}/{len(test_subtypes)} subtypes supported ({success_rate*100:.1f}%)")
                return False
            
        except Exception as e:
            self.log_test("Comprehensive Icon Mapping Support", False, f"Request error: {str(e)}")
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
        """Run all dedicated icons backend support tests"""
        print("🚀 STARTING DEDICATED ICON FUNCTIONALITY BACKEND SUPPORT TESTING")
        print("=" * 80)
        print("Testing backend endpoints that support dedicated icon functionality:")
        print("1. Health check - verify API is operational")
        print("2. Create test diagram - prepare test environment")
        print("3. Node subtype support - test creation of nodes with dedicated icon subtypes")
        print("4. Template system subtype support - verify templates provide correct subtype data")
        print("5. Questionnaire subtype support - test questionnaire endpoints for icon subtypes")
        print("6. Node retrieval subtype data - verify nodes return proper subtype information")
        print("7. Comprehensive icon mapping support - test backend support for all icon mappings")
        print("=" * 80)
        
        tests = [
            self.test_health_check,
            self.test_create_test_diagram,
            self.test_node_subtype_support,
            self.test_template_system_subtype_support,
            self.test_questionnaire_subtype_support,
            self.test_node_retrieval_subtype_data,
            self.test_comprehensive_icon_mapping_support,
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
        
        # Summary for dedicated icons backend support
        if passed == total:
            print("\n🎉 DEDICATED ICON FUNCTIONALITY BACKEND SUPPORT: ALL TESTS PASSED")
            print("✅ Backend provides complete subtype information for dedicated icon mapping")
            print("✅ Node creation and retrieval preserves subtype data needed for frontend icons")
            print("✅ Template system includes proper subtype information for icon rendering")
            print("✅ Questionnaire endpoints support all major node subtypes with dedicated icons")
            print("✅ Backend fully supports the dedicated icon functionality requirements")
        else:
            print(f"\n⚠️ DEDICATED ICON FUNCTIONALITY BACKEND SUPPORT: {total-passed} TESTS FAILED")
            print("❌ Some backend functionality may not fully support dedicated icon requirements")
            print("❌ Review failed tests above for details")
        
        return passed == total

if __name__ == "__main__":
    tester = DedicatedIconsBackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)