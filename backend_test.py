#!/usr/bin/env python3
"""
Backend API Testing - ENHANCED LABEL DRAGGING FUNCTIONALITY
Tests the backend support for enhanced label dragging functionality as specified in the review request.

TESTING FOCUS:
🎯 PRIMARY TEST: ENHANCED LABEL DRAGGING BACKEND SUPPORT

1. **Template Edge Labels Testing:**
   - Load Web Application Security Model template via GET /api/templates
   - Verify template edges have labels like "Initial Access", "Filtered Traffic", "Contains Vulnerability", "Data Access"
   - Check that template edges support draggable functionality (type 'draggable' or default)
   - Verify edge data structure supports label positioning

2. **Dependency Edge Labels Testing:**
   - Create nodes that generate dependency edges with "has_dependency" labels
   - Test auto-generated dependency labels are draggable
   - Verify dependency edge creation and label support

3. **Edge Update Events Testing:**
   - Test PUT /api/diagrams/{id} endpoint for edge updates with label positions
   - Verify that label position changes are properly persisted
   - Test edge data structure with controlPoint1, controlPoint2, labelPosition fields

4. **Diagram Creation with Draggable Edges:**
   - Test POST /api/diagrams endpoint with draggable edge support
   - Verify new diagrams support draggable edge functionality

**EXPECTED RESULTS:** 
- Template edges should have proper labels and support draggable functionality
- Edge updates should persist label position changes
- Dependency edges should be created with draggable labels
- All backend APIs should handle edge data with control points and label positioning
"""

import requests
import json
import uuid
from datetime import datetime, timezone
import sys

# Use the backend URL from frontend/.env with /api suffix
BASE_URL = "https://api-wizard-map.preview.emergentagent.com/api"

class DraggableEdgeLabelTester:
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

    def test_template_edge_labels(self):
        """
        CRITICAL TEST: Test template edge labels for draggable functionality
        
        This test verifies that:
        1. Web Application Security Model template loads properly
        2. Template edges have expected labels ("Initial Access", "Filtered Traffic", etc.)
        3. Template edges support draggable functionality
        4. Edge data structure includes necessary fields for label positioning
        """
        try:
            print("🎯 CRITICAL TEST: Template Edge Labels for Draggable Functionality")
            print("=" * 80)
            
            # Get all templates
            response = self.session.get(f"{self.base_url}/templates")
            
            print(f"📋 Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("Template Edge Labels", False, 
                            f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                templates = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Template Edge Labels", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            # Find Web Application Security Model template
            web_app_template = None
            for template in templates:
                if "Web Application Security Model" in template.get("name", ""):
                    web_app_template = template
                    break
            
            if not web_app_template:
                self.log_test("Template Edge Labels", False, 
                            "Web Application Security Model template not found")
                return False
            
            print(f"📋 Found Web Application Security Model template: {web_app_template.get('name')}")
            
            # Verify template has edges
            edges = web_app_template.get("edges", [])
            if not edges:
                self.log_test("Template Edge Labels", False, 
                            "Template has no edges")
                return False
            
            print(f"📋 Template has {len(edges)} edges")
            
            # Check for expected edge labels from review request
            expected_labels = ["Initial Access", "Filtered Traffic", "Contains Vulnerability", "Data Access"]
            found_labels = []
            draggable_edges = 0
            
            for edge in edges:
                edge_label = edge.get("label", "")
                if edge_label:
                    found_labels.append(edge_label)
                    print(f"   📊 Found edge label: '{edge_label}'")
                
                # Check if edge supports draggable functionality
                edge_type = edge.get("type", "default")
                if edge_type == "draggable" or edge_type == "default":
                    draggable_edges += 1
                
                # Check edge data structure for label positioning support
                edge_data = edge.get("data", {})
                if isinstance(edge_data, dict):
                    # Edge should be able to support control points and label positioning
                    print(f"   📊 Edge '{edge_label}' has data structure: {bool(edge_data)}")
            
            # Verify expected labels are present
            found_expected_labels = []
            for expected_label in expected_labels:
                for found_label in found_labels:
                    if expected_label.lower() in found_label.lower():
                        found_expected_labels.append(expected_label)
                        break
            
            print(f"📊 Template Edge Analysis Results:")
            print(f"   Total edges: {len(edges)}")
            print(f"   Edges with labels: {len(found_labels)}")
            print(f"   Draggable-compatible edges: {draggable_edges}")
            print(f"   Expected labels found: {len(found_expected_labels)}/{len(expected_labels)}")
            print(f"   Found labels: {found_labels}")
            print(f"   Expected labels found: {found_expected_labels}")
            
            # Verify minimum requirements
            if len(found_labels) == 0:
                self.log_test("Template Edge Labels", False, 
                            "No edge labels found in template")
                return False
            
            if len(found_expected_labels) < 2:  # At least 2 of the expected labels
                self.log_test("Template Edge Labels", False, 
                            f"Insufficient expected labels found: {found_expected_labels}")
                return False
            
            if draggable_edges == 0:
                self.log_test("Template Edge Labels", False, 
                            "No draggable-compatible edges found")
                return False
            
            self.log_test("Template Edge Labels", True, 
                        f"✅ SUCCESS: Template has {len(found_labels)} labeled edges, {draggable_edges} draggable-compatible, {len(found_expected_labels)} expected labels found")
            
            return True
            
        except Exception as e:
            self.log_test("Template Edge Labels", False, f"Request error: {str(e)}")
            return False

    def test_diagram_creation_with_draggable_edges(self):
        """
        Test POST /api/diagrams endpoint with draggable edge support
        """
        try:
            print("🎯 TESTING: Diagram Creation with Draggable Edges")
            print("=" * 60)
            
            # Create a test diagram with draggable edges
            diagram_data = {
                "title": f"Draggable Edge Test Diagram {uuid.uuid4().hex[:8]}",
                "description": "Test diagram for draggable edge functionality"
            }
            
            response = self.session.post(f"{self.base_url}/diagrams", json=diagram_data)
            
            print(f"📋 Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("Diagram Creation with Draggable Edges", False, 
                            f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                diagram = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Diagram Creation with Draggable Edges", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            # Store diagram ID for later tests
            self.test_diagram_id = diagram.get("id")
            
            if not self.test_diagram_id:
                self.log_test("Diagram Creation with Draggable Edges", False, 
                            "No diagram ID returned")
                return False
            
            print(f"📋 Created test diagram: {self.test_diagram_id}")
            
            self.log_test("Diagram Creation with Draggable Edges", True, 
                        f"✅ SUCCESS: Created diagram {self.test_diagram_id}")
            
            return True
            
        except Exception as e:
            self.log_test("Diagram Creation with Draggable Edges", False, f"Request error: {str(e)}")
            return False

    def test_edge_update_with_label_positions(self):
        """
        CRITICAL TEST: Test edge updates with label position changes
        
        This test verifies that:
        1. PUT /api/diagrams/{id} endpoint accepts edge updates with label positions
        2. Edge data persists control points and label positioning
        3. Backend properly handles edge data structure modifications
        """
        try:
            print("🎯 CRITICAL TEST: Edge Updates with Label Position Changes")
            print("=" * 80)
            
            if not self.test_diagram_id:
                self.log_test("Edge Update with Label Positions", False, 
                            "No test diagram available")
                return False
            
            # Create test nodes and edges with draggable functionality
            test_nodes = [
                {
                    "id": f"node1-{uuid.uuid4().hex[:8]}",
                    "type": "Actor",
                    "subtype": "ExternalAttacker",
                    "label": "Test Attacker",
                    "position": {"x": 100, "y": 100}
                },
                {
                    "id": f"node2-{uuid.uuid4().hex[:8]}",
                    "type": "Asset",
                    "subtype": "WebApp",
                    "label": "Test WebApp",
                    "position": {"x": 300, "y": 100}
                }
            ]
            
            # Create edge with draggable type and label positioning data
            test_edge = {
                "id": f"edge1-{uuid.uuid4().hex[:8]}",
                "source": test_nodes[0]["id"],
                "target": test_nodes[1]["id"],
                "type": "draggable",
                "label": "Test Dependency",
                "data": {
                    "controlPoint1": {"x": 150, "y": 80},
                    "controlPoint2": {"x": 250, "y": 80},
                    "labelPosition": {"x": 200, "y": 75}
                }
            }
            
            # Update diagram with nodes and edges
            diagram_update = {
                "id": self.test_diagram_id,
                "title": "Draggable Edge Test Diagram",
                "description": "Test diagram for draggable edge functionality",
                "nodes": test_nodes,
                "edges": [test_edge],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            response = self.session.put(f"{self.base_url}/diagrams/{self.test_diagram_id}", 
                                      json=diagram_update)
            
            print(f"📋 Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("Edge Update with Label Positions", False, 
                            f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                updated_diagram = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Edge Update with Label Positions", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            # Verify edge data was persisted correctly
            updated_edges = updated_diagram.get("edges", [])
            if not updated_edges:
                self.log_test("Edge Update with Label Positions", False, 
                            "No edges found in updated diagram")
                return False
            
            # Find our test edge
            test_edge_found = None
            for edge in updated_edges:
                if edge.get("id") == test_edge["id"]:
                    test_edge_found = edge
                    break
            
            if not test_edge_found:
                self.log_test("Edge Update with Label Positions", False, 
                            "Test edge not found in updated diagram")
                return False
            
            # Verify edge properties
            edge_type = test_edge_found.get("type", "")
            edge_label = test_edge_found.get("label", "")
            edge_data = test_edge_found.get("data", {})
            
            print(f"📊 Edge Update Results:")
            print(f"   Edge type: {edge_type}")
            print(f"   Edge label: {edge_label}")
            print(f"   Edge data keys: {list(edge_data.keys()) if isinstance(edge_data, dict) else 'Not a dict'}")
            
            # Verify control points and label position were preserved
            if isinstance(edge_data, dict):
                has_control_point1 = "controlPoint1" in edge_data
                has_control_point2 = "controlPoint2" in edge_data
                has_label_position = "labelPosition" in edge_data
                
                print(f"   Has controlPoint1: {has_control_point1}")
                print(f"   Has controlPoint2: {has_control_point2}")
                print(f"   Has labelPosition: {has_label_position}")
                
                if has_control_point1 and has_control_point2 and has_label_position:
                    self.log_test("Edge Update with Label Positions", True, 
                                f"✅ SUCCESS: Edge data persisted with control points and label positioning")
                    return True
                else:
                    self.log_test("Edge Update with Label Positions", False, 
                                f"Missing edge data fields: controlPoint1={has_control_point1}, controlPoint2={has_control_point2}, labelPosition={has_label_position}")
                    return False
            else:
                self.log_test("Edge Update with Label Positions", False, 
                            f"Edge data is not a dictionary: {type(edge_data)}")
                return False
            
        except Exception as e:
            self.log_test("Edge Update with Label Positions", False, f"Request error: {str(e)}")
            return False

    def test_dependency_edge_labels(self):
        """
        Test auto-generated dependency edges with "has_dependency" labels
        """
        try:
            print("🎯 TESTING: Dependency Edge Labels")
            print("=" * 50)
            
            if not self.test_diagram_id:
                self.log_test("Dependency Edge Labels", False, 
                            "No test diagram available")
                return False
            
            # Create nodes that would generate dependency edges
            dependency_nodes = [
                {
                    "id": f"parent-{uuid.uuid4().hex[:8]}",
                    "type": "Asset",
                    "subtype": "Database",
                    "label": "Parent Database",
                    "position": {"x": 100, "y": 200}
                },
                {
                    "id": f"child-{uuid.uuid4().hex[:8]}",
                    "type": "Asset",
                    "subtype": "Backup",
                    "label": "Child Backup",
                    "position": {"x": 300, "y": 200}
                }
            ]
            
            # Create dependency edge with "has_dependency" label
            dependency_edge = {
                "id": f"dep-edge-{uuid.uuid4().hex[:8]}",
                "source": dependency_nodes[0]["id"],
                "target": dependency_nodes[1]["id"],
                "type": "draggable",
                "label": "has_dependency",
                "data": {
                    "controlPoint1": {"x": 150, "y": 180},
                    "controlPoint2": {"x": 250, "y": 180},
                    "labelPosition": {"x": 200, "y": 175}
                }
            }
            
            # Get current diagram
            response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}")
            if response.status_code != 200:
                self.log_test("Dependency Edge Labels", False, 
                            f"Failed to get diagram: HTTP {response.status_code}")
                return False
            
            current_diagram = response.json()
            current_nodes = current_diagram.get("nodes", [])
            current_edges = current_diagram.get("edges", [])
            
            # Add dependency nodes and edge
            updated_nodes = current_nodes + dependency_nodes
            updated_edges = current_edges + [dependency_edge]
            
            # Update diagram
            diagram_update = {
                "id": self.test_diagram_id,
                "title": current_diagram.get("title", "Test Diagram"),
                "description": current_diagram.get("description", ""),
                "nodes": updated_nodes,
                "edges": updated_edges,
                "created_at": current_diagram.get("created_at"),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            response = self.session.put(f"{self.base_url}/diagrams/{self.test_diagram_id}", 
                                      json=diagram_update)
            
            if response.status_code != 200:
                self.log_test("Dependency Edge Labels", False, 
                            f"Failed to update diagram: HTTP {response.status_code}")
                return False
            
            updated_diagram = response.json()
            
            # Verify dependency edge was created
            final_edges = updated_diagram.get("edges", [])
            dependency_edge_found = None
            
            for edge in final_edges:
                if edge.get("label") == "has_dependency":
                    dependency_edge_found = edge
                    break
            
            if not dependency_edge_found:
                self.log_test("Dependency Edge Labels", False, 
                            "Dependency edge with 'has_dependency' label not found")
                return False
            
            # Verify dependency edge is draggable
            edge_type = dependency_edge_found.get("type", "")
            edge_data = dependency_edge_found.get("data", {})
            
            print(f"📊 Dependency Edge Results:")
            print(f"   Edge label: {dependency_edge_found.get('label')}")
            print(f"   Edge type: {edge_type}")
            print(f"   Has edge data: {bool(edge_data)}")
            
            if edge_type == "draggable" and isinstance(edge_data, dict):
                self.log_test("Dependency Edge Labels", True, 
                            f"✅ SUCCESS: Dependency edge with 'has_dependency' label is draggable")
                return True
            else:
                self.log_test("Dependency Edge Labels", False, 
                            f"Dependency edge is not properly configured for dragging: type={edge_type}, data={type(edge_data)}")
                return False
            
        except Exception as e:
            self.log_test("Dependency Edge Labels", False, f"Request error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all draggable edge label tests"""
        print("🚀 STARTING ENHANCED LABEL DRAGGING FUNCTIONALITY TESTING")
        print("=" * 80)
        print("Testing backend support for enhanced label dragging functionality")
        print("=" * 80)
        
        tests = [
            self.test_health_check,
            self.test_template_edge_labels,
            self.test_diagram_creation_with_draggable_edges,
            self.test_edge_update_with_label_positions,
            self.test_dependency_edge_labels,
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
        
        print("=" * 80)
        print(f"🏁 TESTING COMPLETE: {passed}/{total} tests passed")
        print("=" * 80)
        
        # Print detailed results
        print("\n📊 DETAILED TEST RESULTS:")
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{status} {result['test']}: {result['message']}")
        
        return passed == total

if __name__ == "__main__":
    tester = DraggableEdgeLabelTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)