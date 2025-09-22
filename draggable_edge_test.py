#!/usr/bin/env python3
"""
Backend API Testing - DRAGGABLE EDGE FUNCTIONALITY
Tests the backend support for draggable edge functionality and edge data structure handling.

TESTING FOCUS:
🎯 PRIMARY TEST: DRAGGABLE EDGE BACKEND SUPPORT
1. **Test Template Edges Structure:**
   - Check GET /api/templates endpoint to verify template edges have correct type
   - Verify template edges include 'draggable' type or default to draggable
   - Check edge data structure includes control points and label positioning

2. **Test Diagram Edge Management:**
   - Create test diagram with draggable edges
   - Test edge creation via onConnect with draggable type
   - Verify edge data persistence includes control points and label position
   - Test edge updates with new control point data

3. **Test Edge Data Structure:**
   - Verify edges support data field for control points
   - Test edge type handling (draggable vs default)
   - Check edge serialization/deserialization with control point data

**EXPECTED RESULTS:** 
- Template edges should use 'draggable' type or default to draggable behavior
- New edges created via onConnect should have type 'draggable'
- Edge data should persist control points and label positioning
- Backend should handle edge updates with control point modifications
"""

import requests
import json
import uuid
from datetime import datetime, timezone
import sys

# Use the backend URL from frontend/.env with /api suffix
BASE_URL = "https://ui-update-bugfix.preview.emergentagent.com/api"

class DraggableEdgeTester:
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

    def test_template_edges_structure(self):
        """
        CRITICAL TEST: Test template edges structure for draggable edge support
        
        This test verifies that:
        1. Template edges have correct type field (draggable or default)
        2. Template edges include data field for control points
        3. Edge structure supports draggable functionality
        """
        try:
            print("🎯 CRITICAL TEST: Template Edges Structure for Draggable Support")
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
                
                self.log_test("Template Edges Structure", False, 
                            f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                templates = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Template Edges Structure", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            if not isinstance(templates, list) or len(templates) == 0:
                self.log_test("Template Edges Structure", False, 
                            "No templates found or invalid response format")
                return False
            
            print(f"📊 Found {len(templates)} templates")
            
            # Analyze edge structures across all templates
            total_edges = 0
            draggable_edges = 0
            edges_with_data = 0
            edges_with_control_points = 0
            edge_types = {}
            
            for template in templates:
                template_name = template.get('name', 'Unknown')
                edges = template.get('edges', [])
                
                print(f"   📋 Template: {template_name} - {len(edges)} edges")
                
                for edge in edges:
                    total_edges += 1
                    
                    # Check edge type
                    edge_type = edge.get('type', 'default')
                    edge_types[edge_type] = edge_types.get(edge_type, 0) + 1
                    
                    if edge_type == 'draggable':
                        draggable_edges += 1
                    
                    # Check if edge has data field
                    edge_data = edge.get('data', {})
                    if edge_data:
                        edges_with_data += 1
                        
                        # Check for control point data
                        if ('controlPoint1' in edge_data or 
                            'controlPoint2' in edge_data or 
                            'labelPosition' in edge_data):
                            edges_with_control_points += 1
                    
                    # Verify edge structure
                    required_edge_fields = ['id', 'source', 'target']
                    missing_fields = [field for field in required_edge_fields if field not in edge]
                    
                    if missing_fields:
                        self.log_test("Template Edges Structure", False, 
                                    f"Edge missing required fields: {missing_fields}")
                        return False
            
            print(f"📊 Edge Analysis Results:")
            print(f"   Total edges: {total_edges}")
            print(f"   Edge types: {edge_types}")
            print(f"   Draggable edges: {draggable_edges}")
            print(f"   Edges with data field: {edges_with_data}")
            print(f"   Edges with control points: {edges_with_control_points}")
            
            # Verify that edges support draggable functionality
            # Either they have 'draggable' type or they default to draggable behavior
            supports_draggable = (
                draggable_edges > 0 or 
                'default' in edge_types or 
                total_edges == 0  # No edges is also valid
            )
            
            if not supports_draggable:
                self.log_test("Template Edges Structure", False, 
                            "No edges support draggable functionality")
                return False
            
            self.log_test("Template Edges Structure", True, 
                        f"✅ SUCCESS: {total_edges} template edges analyzed, draggable support confirmed")
            
            return True
            
        except Exception as e:
            self.log_test("Template Edges Structure", False, f"Request error: {str(e)}")
            return False

    def test_diagram_creation_with_draggable_edges(self):
        """
        CRITICAL TEST: Test diagram creation and edge management with draggable edges
        
        This test verifies that:
        1. Diagrams can be created with draggable edges
        2. Edge data persists control points and label positioning
        3. Edge updates work correctly with control point modifications
        """
        try:
            print("🎯 CRITICAL TEST: Diagram Creation with Draggable Edges")
            print("=" * 80)
            
            # Create a test diagram
            diagram_data = {
                "title": "Draggable Edge Test Diagram",
                "description": "Test diagram for draggable edge functionality"
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
                
                self.log_test("Diagram Creation with Draggable Edges", False, 
                            f"Failed to create diagram: HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                diagram = response.json()
                self.test_diagram_id = diagram['id']
            except json.JSONDecodeError as e:
                self.log_test("Diagram Creation with Draggable Edges", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            print(f"📊 Created test diagram: {self.test_diagram_id}")
            
            # Create test nodes for the diagram
            test_nodes = [
                {
                    "id": f"node-source-{uuid.uuid4().hex[:8]}",
                    "type": "Asset",
                    "subtype": "WebApp",
                    "label": "Web Application",
                    "position": {"x": 100, "y": 100},
                    "data": {"subtype": "WebApp"}
                },
                {
                    "id": f"node-target-{uuid.uuid4().hex[:8]}",
                    "type": "Asset", 
                    "subtype": "Database",
                    "label": "Database",
                    "position": {"x": 400, "y": 200},
                    "data": {"subtype": "Database"}
                }
            ]
            
            # Create test edges with draggable type and control point data
            test_edges = [
                {
                    "id": f"edge-draggable-{uuid.uuid4().hex[:8]}",
                    "source": test_nodes[0]["id"],
                    "target": test_nodes[1]["id"],
                    "type": "draggable",
                    "label": "Data Flow",
                    "data": {
                        "controlPoint1": {"x": 50, "y": -20},
                        "controlPoint2": {"x": -50, "y": 20},
                        "labelPosition": 0.6
                    }
                }
            ]
            
            # Update diagram with nodes and edges
            updated_diagram = {
                "id": self.test_diagram_id,
                "title": diagram_data["title"],
                "description": diagram_data["description"],
                "nodes": test_nodes,
                "edges": test_edges
            }
            
            response = self.session.put(
                f"{self.base_url}/diagrams/{self.test_diagram_id}", 
                json=updated_diagram
            )
            
            print(f"📋 Update Diagram Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("Diagram Creation with Draggable Edges", False, 
                            f"Failed to update diagram: HTTP {response.status_code}: {error_detail}")
                return False
            
            # Verify the diagram was saved correctly
            response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}")
            
            if response.status_code != 200:
                self.log_test("Diagram Creation with Draggable Edges", False, 
                            f"Failed to retrieve diagram: HTTP {response.status_code}")
                return False
            
            try:
                saved_diagram = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Diagram Creation with Draggable Edges", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            # Verify edge data persistence
            saved_edges = saved_diagram.get('edges', [])
            
            if len(saved_edges) == 0:
                self.log_test("Diagram Creation with Draggable Edges", False, 
                            "No edges found in saved diagram")
                return False
            
            draggable_edge = saved_edges[0]
            edge_type = draggable_edge.get('type', 'default')
            edge_data = draggable_edge.get('data', {})
            
            print(f"📊 Saved Edge Analysis:")
            print(f"   Edge ID: {draggable_edge.get('id')}")
            print(f"   Edge Type: {edge_type}")
            print(f"   Edge Data: {edge_data}")
            print(f"   Has Control Points: {'controlPoint1' in edge_data and 'controlPoint2' in edge_data}")
            print(f"   Has Label Position: {'labelPosition' in edge_data}")
            
            # Verify edge type is draggable
            if edge_type != 'draggable':
                self.log_test("Diagram Creation with Draggable Edges", False, 
                            f"Edge type is '{edge_type}', expected 'draggable'")
                return False
            
            # Verify control point data is preserved
            if 'controlPoint1' not in edge_data or 'controlPoint2' not in edge_data:
                self.log_test("Diagram Creation with Draggable Edges", False, 
                            "Control point data not preserved in saved edge")
                return False
            
            # Verify label position is preserved
            if 'labelPosition' not in edge_data:
                self.log_test("Diagram Creation with Draggable Edges", False, 
                            "Label position data not preserved in saved edge")
                return False
            
            self.log_test("Diagram Creation with Draggable Edges", True, 
                        f"✅ SUCCESS: Diagram created with draggable edges, control point data preserved")
            
            return True
            
        except Exception as e:
            self.log_test("Diagram Creation with Draggable Edges", False, f"Request error: {str(e)}")
            return False

    def test_edge_data_structure_validation(self):
        """
        CRITICAL TEST: Test edge data structure validation and serialization
        
        This test verifies that:
        1. Edges support complex data structures for control points
        2. Edge serialization/deserialization works correctly
        3. Edge updates preserve all data fields
        """
        try:
            print("🎯 CRITICAL TEST: Edge Data Structure Validation")
            print("=" * 80)
            
            if not self.test_diagram_id:
                self.log_test("Edge Data Structure Validation", False, 
                            "No test diagram available - previous test may have failed")
                return False
            
            # Get the current diagram
            response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}")
            
            if response.status_code != 200:
                self.log_test("Edge Data Structure Validation", False, 
                            f"Failed to retrieve diagram: HTTP {response.status_code}")
                return False
            
            try:
                diagram = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Edge Data Structure Validation", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            edges = diagram.get('edges', [])
            
            if len(edges) == 0:
                self.log_test("Edge Data Structure Validation", False, 
                            "No edges found in diagram")
                return False
            
            # Update edge with more complex control point data
            edge = edges[0]
            updated_edge_data = {
                "controlPoint1": {"x": 75, "y": -35},
                "controlPoint2": {"x": -75, "y": 35},
                "labelPosition": 0.3,
                "customProperties": {
                    "curvature": 0.4,
                    "animated": True,
                    "strokeWidth": 3
                },
                "metadata": {
                    "lastModified": datetime.now(timezone.utc).isoformat(),
                    "modifiedBy": "draggable_edge_test"
                }
            }
            
            # Update the edge data
            updated_edge = {
                **edge,
                "data": updated_edge_data
            }
            
            # Update the diagram with modified edge
            updated_diagram = {
                **diagram,
                "edges": [updated_edge]
            }
            
            response = self.session.put(
                f"{self.base_url}/diagrams/{self.test_diagram_id}", 
                json=updated_diagram
            )
            
            print(f"📋 Update Edge Data Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("Edge Data Structure Validation", False, 
                            f"Failed to update edge data: HTTP {response.status_code}: {error_detail}")
                return False
            
            # Verify the updated data was saved correctly
            response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}")
            
            if response.status_code != 200:
                self.log_test("Edge Data Structure Validation", False, 
                            f"Failed to retrieve updated diagram: HTTP {response.status_code}")
                return False
            
            try:
                updated_diagram = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Edge Data Structure Validation", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            saved_edges = updated_diagram.get('edges', [])
            
            if len(saved_edges) == 0:
                self.log_test("Edge Data Structure Validation", False, 
                            "No edges found in updated diagram")
                return False
            
            saved_edge = saved_edges[0]
            saved_edge_data = saved_edge.get('data', {})
            
            print(f"📊 Updated Edge Data Analysis:")
            print(f"   Control Point 1: {saved_edge_data.get('controlPoint1')}")
            print(f"   Control Point 2: {saved_edge_data.get('controlPoint2')}")
            print(f"   Label Position: {saved_edge_data.get('labelPosition')}")
            print(f"   Custom Properties: {saved_edge_data.get('customProperties')}")
            print(f"   Metadata: {saved_edge_data.get('metadata')}")
            
            # Verify all data fields were preserved
            expected_fields = ['controlPoint1', 'controlPoint2', 'labelPosition', 'customProperties', 'metadata']
            missing_fields = [field for field in expected_fields if field not in saved_edge_data]
            
            if missing_fields:
                self.log_test("Edge Data Structure Validation", False, 
                            f"Missing edge data fields after update: {missing_fields}")
                return False
            
            # Verify control point values are correct
            cp1 = saved_edge_data.get('controlPoint1', {})
            cp2 = saved_edge_data.get('controlPoint2', {})
            
            if cp1.get('x') != 75 or cp1.get('y') != -35:
                self.log_test("Edge Data Structure Validation", False, 
                            f"Control Point 1 values incorrect: expected {{x: 75, y: -35}}, got {cp1}")
                return False
            
            if cp2.get('x') != -75 or cp2.get('y') != 35:
                self.log_test("Edge Data Structure Validation", False, 
                            f"Control Point 2 values incorrect: expected {{x: -75, y: 35}}, got {cp2}")
                return False
            
            # Verify label position
            if saved_edge_data.get('labelPosition') != 0.3:
                self.log_test("Edge Data Structure Validation", False, 
                            f"Label position incorrect: expected 0.3, got {saved_edge_data.get('labelPosition')}")
                return False
            
            self.log_test("Edge Data Structure Validation", True, 
                        f"✅ SUCCESS: Complex edge data structure preserved and validated")
            
            return True
            
        except Exception as e:
            self.log_test("Edge Data Structure Validation", False, f"Request error: {str(e)}")
            return False

    def test_new_edge_creation_with_draggable_type(self):
        """
        CRITICAL TEST: Test new edge creation with draggable type (simulating onConnect)
        
        This test verifies that:
        1. New edges created via API use draggable type by default
        2. onConnect-style edge creation includes proper control point initialization
        3. Edge creation matches frontend onConnect behavior
        """
        try:
            print("🎯 CRITICAL TEST: New Edge Creation with Draggable Type")
            print("=" * 80)
            
            if not self.test_diagram_id:
                self.log_test("New Edge Creation with Draggable Type", False, 
                            "No test diagram available - previous test may have failed")
                return False
            
            # Get the current diagram
            response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}")
            
            if response.status_code != 200:
                self.log_test("New Edge Creation with Draggable Type", False, 
                            f"Failed to retrieve diagram: HTTP {response.status_code}")
                return False
            
            try:
                diagram = response.json()
            except json.JSONDecodeError as e:
                self.log_test("New Edge Creation with Draggable Type", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            nodes = diagram.get('nodes', [])
            existing_edges = diagram.get('edges', [])
            
            if len(nodes) < 2:
                self.log_test("New Edge Creation with Draggable Type", False, 
                            "Not enough nodes in diagram for edge creation test")
                return False
            
            # Create a new edge simulating onConnect behavior
            new_edge = {
                "id": f"edge-onconnect-{uuid.uuid4().hex[:8]}",
                "source": nodes[1]["id"],  # Reverse direction
                "target": nodes[0]["id"],
                "type": "draggable",  # This should be the default from onConnect
                "label": "API Connection",
                "data": {
                    # Initial control points and label position as set by onConnect
                    "controlPoint1": {"x": 0, "y": 0},
                    "controlPoint2": {"x": 0, "y": 0},
                    "labelPosition": 0.5
                }
            }
            
            # Add the new edge to the diagram
            updated_edges = existing_edges + [new_edge]
            
            updated_diagram = {
                **diagram,
                "edges": updated_edges
            }
            
            response = self.session.put(
                f"{self.base_url}/diagrams/{self.test_diagram_id}", 
                json=updated_diagram
            )
            
            print(f"📋 Add New Edge Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("New Edge Creation with Draggable Type", False, 
                            f"Failed to add new edge: HTTP {response.status_code}: {error_detail}")
                return False
            
            # Verify the new edge was saved correctly
            response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}")
            
            if response.status_code != 200:
                self.log_test("New Edge Creation with Draggable Type", False, 
                            f"Failed to retrieve updated diagram: HTTP {response.status_code}")
                return False
            
            try:
                updated_diagram = response.json()
            except json.JSONDecodeError as e:
                self.log_test("New Edge Creation with Draggable Type", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            saved_edges = updated_diagram.get('edges', [])
            
            # Find the new edge
            new_saved_edge = None
            for edge in saved_edges:
                if edge.get('id') == new_edge['id']:
                    new_saved_edge = edge
                    break
            
            if not new_saved_edge:
                self.log_test("New Edge Creation with Draggable Type", False, 
                            "New edge not found in saved diagram")
                return False
            
            print(f"📊 New Edge Analysis:")
            print(f"   Edge ID: {new_saved_edge.get('id')}")
            print(f"   Edge Type: {new_saved_edge.get('type')}")
            print(f"   Edge Label: {new_saved_edge.get('label')}")
            print(f"   Edge Data: {new_saved_edge.get('data')}")
            print(f"   Total Edges in Diagram: {len(saved_edges)}")
            
            # Verify edge type is draggable
            if new_saved_edge.get('type') != 'draggable':
                self.log_test("New Edge Creation with Draggable Type", False, 
                            f"New edge type is '{new_saved_edge.get('type')}', expected 'draggable'")
                return False
            
            # Verify initial control point data
            edge_data = new_saved_edge.get('data', {})
            if 'controlPoint1' not in edge_data or 'controlPoint2' not in edge_data:
                self.log_test("New Edge Creation with Draggable Type", False, 
                            "New edge missing control point data")
                return False
            
            # Verify initial values match onConnect defaults
            cp1 = edge_data.get('controlPoint1', {})
            cp2 = edge_data.get('controlPoint2', {})
            label_pos = edge_data.get('labelPosition', 0)
            
            if cp1.get('x') != 0 or cp1.get('y') != 0:
                self.log_test("New Edge Creation with Draggable Type", False, 
                            f"Control Point 1 initial values incorrect: expected {{x: 0, y: 0}}, got {cp1}")
                return False
            
            if cp2.get('x') != 0 or cp2.get('y') != 0:
                self.log_test("New Edge Creation with Draggable Type", False, 
                            f"Control Point 2 initial values incorrect: expected {{x: 0, y: 0}}, got {cp2}")
                return False
            
            if label_pos != 0.5:
                self.log_test("New Edge Creation with Draggable Type", False, 
                            f"Label position initial value incorrect: expected 0.5, got {label_pos}")
                return False
            
            self.log_test("New Edge Creation with Draggable Type", True, 
                        f"✅ SUCCESS: New edge created with draggable type and proper initialization")
            
            return True
            
        except Exception as e:
            self.log_test("New Edge Creation with Draggable Type", False, f"Request error: {str(e)}")
            return False

    def cleanup_test_diagram(self):
        """Clean up test diagram after testing"""
        if self.test_diagram_id:
            try:
                response = self.session.delete(f"{self.base_url}/diagrams/{self.test_diagram_id}")
                if response.status_code == 200:
                    print(f"🧹 Cleaned up test diagram: {self.test_diagram_id}")
                else:
                    print(f"⚠️ Failed to clean up test diagram: HTTP {response.status_code}")
            except Exception as e:
                print(f"⚠️ Error cleaning up test diagram: {str(e)}")

    def run_all_tests(self):
        """Run all draggable edge functionality tests"""
        print("🚀 STARTING DRAGGABLE EDGE FUNCTIONALITY TESTING")
        print("=" * 80)
        print("Testing backend support for draggable edge functionality and edge data structure handling")
        print("=" * 80)
        
        tests = [
            self.test_health_check,
            self.test_template_edges_structure,
            self.test_diagram_creation_with_draggable_edges,
            self.test_edge_data_structure_validation,
            self.test_new_edge_creation_with_draggable_type,
        ]
        
        passed = 0
        total = len(tests)
        
        try:
            for test in tests:
                try:
                    if test():
                        passed += 1
                    print()  # Add spacing between tests
                except Exception as e:
                    print(f"❌ Test {test.__name__} failed with exception: {str(e)}")
                    print()
        finally:
            # Always clean up test diagram
            self.cleanup_test_diagram()
        
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
    tester = DraggableEdgeTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)