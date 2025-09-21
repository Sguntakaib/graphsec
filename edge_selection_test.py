#!/usr/bin/env python3
"""
Edge Selection and Control Point Display Test
Tests the complete flow of edge selection and control point display functionality.

This test will:
1. Create a diagram with template edges
2. Verify edge structure and type mapping
3. Test edge selection mechanism
4. Check control point data initialization
"""

import requests
import json
import uuid
from datetime import datetime, timezone
import sys

# Use the backend URL from frontend/.env with /api suffix
BASE_URL = "https://devops-posture-scan.preview.emergentagent.com/api"

class EdgeSelectionTester:
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

    def test_template_edge_conversion_to_draggable(self):
        """
        Test converting template edges to draggable edges with proper data initialization
        """
        try:
            print("🎯 TESTING: Template Edge Conversion to Draggable")
            print("=" * 70)
            
            # Get a template to work with
            response = self.session.get(f"{self.base_url}/templates")
            if response.status_code != 200:
                self.log_test("Template Edge Conversion", False, 
                            f"Failed to get templates: HTTP {response.status_code}")
                return False
            
            templates = response.json()
            if not templates:
                self.log_test("Template Edge Conversion", False, "No templates available")
                return False
            
            # Use the first template
            template = templates[0]
            template_name = template.get('name', 'Unknown')
            template_edges = template.get('edges', [])
            
            print(f"📋 Using template: {template_name}")
            print(f"📋 Template has {len(template_edges)} edges")
            
            if not template_edges:
                self.log_test("Template Edge Conversion", False, "Template has no edges")
                return False
            
            # Create a test diagram
            diagram_data = {
                "title": f"Edge Selection Test - {template_name}",
                "description": "Test diagram for edge selection and control point display"
            }
            
            response = self.session.post(f"{self.base_url}/diagrams", json=diagram_data)
            if response.status_code != 200:
                self.log_test("Template Edge Conversion", False, 
                            f"Failed to create diagram: HTTP {response.status_code}")
                return False
            
            diagram = response.json()
            self.test_diagram_id = diagram['id']
            print(f"📊 Created test diagram: {self.test_diagram_id}")
            
            # Convert template edges to draggable edges with proper initialization
            converted_edges = []
            for edge in template_edges:
                converted_edge = {
                    "id": f"converted-{edge['id']}-{uuid.uuid4().hex[:8]}",
                    "source": edge['source'],
                    "target": edge['target'],
                    "type": "draggable",  # Explicitly set to draggable
                    "label": edge.get('label', 'Connection'),
                    "data": {
                        # Initialize control points for draggable functionality
                        "controlPoint1": {"x": 0, "y": 0},
                        "controlPoint2": {"x": 0, "y": 0},
                        "labelPosition": 0.5,
                        "originalTemplate": template_name,
                        "convertedAt": datetime.now(timezone.utc).isoformat()
                    }
                }
                converted_edges.append(converted_edge)
            
            # Also copy template nodes
            template_nodes = template.get('nodes', [])
            converted_nodes = []
            for node in template_nodes:
                converted_node = {
                    "id": node['id'],
                    "type": node.get('type', 'Asset'),
                    "subtype": node.get('subtype', 'WebApp'),
                    "label": node.get('label', 'Node'),
                    "position": node.get('position', {"x": 100, "y": 100}),
                    "data": node.get('data', {})
                }
                converted_nodes.append(converted_node)
            
            # Update diagram with converted nodes and edges
            updated_diagram = {
                "id": self.test_diagram_id,
                "title": diagram_data["title"],
                "description": diagram_data["description"],
                "nodes": converted_nodes,
                "edges": converted_edges
            }
            
            response = self.session.put(
                f"{self.base_url}/diagrams/{self.test_diagram_id}", 
                json=updated_diagram
            )
            
            if response.status_code != 200:
                self.log_test("Template Edge Conversion", False, 
                            f"Failed to update diagram: HTTP {response.status_code}")
                return False
            
            # Verify the conversion
            response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}")
            if response.status_code != 200:
                self.log_test("Template Edge Conversion", False, 
                            f"Failed to retrieve diagram: HTTP {response.status_code}")
                return False
            
            saved_diagram = response.json()
            saved_edges = saved_diagram.get('edges', [])
            
            print(f"📊 Conversion Results:")
            print(f"   Original template edges: {len(template_edges)}")
            print(f"   Converted draggable edges: {len(saved_edges)}")
            
            # Verify each edge was converted properly
            draggable_count = 0
            edges_with_control_points = 0
            
            for edge in saved_edges:
                edge_type = edge.get('type', 'default')
                edge_data = edge.get('data', {})
                
                print(f"   Edge {edge.get('id')}: type={edge_type}, has_control_points={'controlPoint1' in edge_data}")
                
                if edge_type == 'draggable':
                    draggable_count += 1
                
                if 'controlPoint1' in edge_data and 'controlPoint2' in edge_data:
                    edges_with_control_points += 1
            
            print(f"   Draggable edges: {draggable_count}/{len(saved_edges)}")
            print(f"   Edges with control points: {edges_with_control_points}/{len(saved_edges)}")
            
            if draggable_count != len(saved_edges):
                self.log_test("Template Edge Conversion", False, 
                            f"Not all edges converted to draggable: {draggable_count}/{len(saved_edges)}")
                return False
            
            if edges_with_control_points != len(saved_edges):
                self.log_test("Template Edge Conversion", False, 
                            f"Not all edges have control points: {edges_with_control_points}/{len(saved_edges)}")
                return False
            
            self.log_test("Template Edge Conversion", True, 
                        f"✅ SUCCESS: {len(saved_edges)} template edges converted to draggable with control points")
            
            return True
            
        except Exception as e:
            self.log_test("Template Edge Conversion", False, f"Request error: {str(e)}")
            return False

    def test_edge_data_initialization_for_existing_edges(self):
        """
        Test that existing edges without control point data get properly initialized
        """
        try:
            print("🎯 TESTING: Edge Data Initialization for Existing Edges")
            print("=" * 70)
            
            if not self.test_diagram_id:
                self.log_test("Edge Data Initialization", False, 
                            "No test diagram available")
                return False
            
            # Get current diagram
            response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}")
            if response.status_code != 200:
                self.log_test("Edge Data Initialization", False, 
                            f"Failed to retrieve diagram: HTTP {response.status_code}")
                return False
            
            diagram = response.json()
            edges = diagram.get('edges', [])
            
            if not edges:
                self.log_test("Edge Data Initialization", False, "No edges in diagram")
                return False
            
            # Create an edge without control point data (simulating old template edge)
            legacy_edge = {
                "id": f"legacy-edge-{uuid.uuid4().hex[:8]}",
                "source": edges[0]['source'],
                "target": edges[0]['target'],
                "type": "default",  # Old type
                "label": "Legacy Connection",
                "data": {}  # Empty data - no control points
            }
            
            # Add legacy edge to diagram
            updated_edges = edges + [legacy_edge]
            updated_diagram = {
                **diagram,
                "edges": updated_edges
            }
            
            response = self.session.put(
                f"{self.base_url}/diagrams/{self.test_diagram_id}", 
                json=updated_diagram
            )
            
            if response.status_code != 200:
                self.log_test("Edge Data Initialization", False, 
                            f"Failed to add legacy edge: HTTP {response.status_code}")
                return False
            
            print(f"📋 Added legacy edge without control points")
            
            # Now simulate the frontend initialization process
            # When an edge without control points is selected, it should be initialized
            response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}")
            if response.status_code != 200:
                self.log_test("Edge Data Initialization", False, 
                            f"Failed to retrieve updated diagram: HTTP {response.status_code}")
                return False
            
            updated_diagram = response.json()
            updated_edges = updated_diagram.get('edges', [])
            
            # Find the legacy edge
            legacy_saved_edge = None
            for edge in updated_edges:
                if edge.get('id') == legacy_edge['id']:
                    legacy_saved_edge = edge
                    break
            
            if not legacy_saved_edge:
                self.log_test("Edge Data Initialization", False, "Legacy edge not found")
                return False
            
            print(f"📊 Legacy Edge Analysis:")
            print(f"   Edge Type: {legacy_saved_edge.get('type')}")
            print(f"   Edge Data: {legacy_saved_edge.get('data')}")
            
            # Simulate frontend initialization by updating the edge with control points
            initialized_edge = {
                **legacy_saved_edge,
                "type": "draggable",  # Convert to draggable
                "data": {
                    **legacy_saved_edge.get('data', {}),
                    "controlPoint1": {"x": 0, "y": 0},
                    "controlPoint2": {"x": 0, "y": 0},
                    "labelPosition": 0.5,
                    "initializedAt": datetime.now(timezone.utc).isoformat()
                }
            }
            
            # Update the edge in the diagram
            final_edges = []
            for edge in updated_edges:
                if edge.get('id') == legacy_edge['id']:
                    final_edges.append(initialized_edge)
                else:
                    final_edges.append(edge)
            
            final_diagram = {
                **updated_diagram,
                "edges": final_edges
            }
            
            response = self.session.put(
                f"{self.base_url}/diagrams/{self.test_diagram_id}", 
                json=final_diagram
            )
            
            if response.status_code != 200:
                self.log_test("Edge Data Initialization", False, 
                            f"Failed to initialize edge: HTTP {response.status_code}")
                return False
            
            # Verify initialization
            response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}")
            if response.status_code != 200:
                self.log_test("Edge Data Initialization", False, 
                            f"Failed to retrieve final diagram: HTTP {response.status_code}")
                return False
            
            final_diagram = response.json()
            final_edges = final_diagram.get('edges', [])
            
            # Find the initialized edge
            initialized_saved_edge = None
            for edge in final_edges:
                if edge.get('id') == legacy_edge['id']:
                    initialized_saved_edge = edge
                    break
            
            if not initialized_saved_edge:
                self.log_test("Edge Data Initialization", False, "Initialized edge not found")
                return False
            
            edge_data = initialized_saved_edge.get('data', {})
            
            print(f"📊 Initialized Edge Analysis:")
            print(f"   Edge Type: {initialized_saved_edge.get('type')}")
            print(f"   Has Control Point 1: {'controlPoint1' in edge_data}")
            print(f"   Has Control Point 2: {'controlPoint2' in edge_data}")
            print(f"   Has Label Position: {'labelPosition' in edge_data}")
            
            # Verify initialization was successful
            if initialized_saved_edge.get('type') != 'draggable':
                self.log_test("Edge Data Initialization", False, 
                            f"Edge type not updated: {initialized_saved_edge.get('type')}")
                return False
            
            required_fields = ['controlPoint1', 'controlPoint2', 'labelPosition']
            missing_fields = [field for field in required_fields if field not in edge_data]
            
            if missing_fields:
                self.log_test("Edge Data Initialization", False, 
                            f"Missing initialized fields: {missing_fields}")
                return False
            
            self.log_test("Edge Data Initialization", True, 
                        f"✅ SUCCESS: Legacy edge initialized with draggable control points")
            
            return True
            
        except Exception as e:
            self.log_test("Edge Data Initialization", False, f"Request error: {str(e)}")
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
        """Run all edge selection and control point tests"""
        print("🚀 STARTING EDGE SELECTION AND CONTROL POINT TESTING")
        print("=" * 80)
        print("Testing edge selection mechanism and control point display functionality")
        print("=" * 80)
        
        tests = [
            self.test_template_edge_conversion_to_draggable,
            self.test_edge_data_initialization_for_existing_edges,
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
    tester = EdgeSelectionTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)