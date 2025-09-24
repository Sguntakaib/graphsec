#!/usr/bin/env python3
"""
Canvas Node Detection System Backend API Testing
Tests the core API endpoints that support the enhanced canvas node detection functionality.

REVIEW REQUEST FOCUS:
🎯 Test the enhanced canvas node detection system implemented in the dependency handling

CRITICAL ENDPOINTS TO TEST:
1. GET /api/diagrams - Verify diagram listing works
2. POST /api/diagrams - Test creating new diagrams  
3. PUT /api/diagrams/{id} - Test updating diagrams with nodes and edges
4. GET /api/questionnaires/WebApp?level=basic - Verify WebApp questionnaire system  
5. GET /api/questionnaires/API?level=basic - Verify API questionnaire system
6. GET /api/questionnaires/Database?level=basic - Verify Database questionnaire system

SCOPE: Backend API testing only - verify backend supports enhanced frontend canvas detection system.
"""

import requests
import json
import uuid
from datetime import datetime, timezone
import sys

# Use the backend URL from frontend/.env with /api suffix
BASE_URL = "https://vulnstride-popup.preview.emergentagent.com/api"

class CanvasNodeDetectionTester:
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
            print("🎯 TESTING: Health Check Endpoint")
            print("=" * 60)
            
            response = self.session.get(f"{self.base_url}/")
            print(f"📋 Response Status: HTTP {response.status_code}")
            
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

    def test_diagrams_list(self):
        """
        CRITICAL TEST 1: GET /api/diagrams - Verify diagram listing works
        """
        try:
            print("🎯 CRITICAL TEST 1: GET /api/diagrams - Diagram Listing")
            print("=" * 60)
            
            response = self.session.get(f"{self.base_url}/diagrams")
            print(f"📋 Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("Diagrams List", False, f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Diagrams List", False, f"Invalid JSON response: {str(e)}")
                return False
            
            # Verify response is a list
            if not isinstance(data, list):
                self.log_test("Diagrams List", False, f"Expected list response, got {type(data)}")
                return False
            
            print(f"📊 Diagrams List Results:")
            print(f"   Total diagrams: {len(data)}")
            print(f"   Response type: {type(data)}")
            
            # If there are diagrams, verify structure
            if data:
                first_diagram = data[0]
                required_fields = ["id", "title", "nodes", "edges", "created_at"]
                missing_fields = [field for field in required_fields if field not in first_diagram]
                
                if missing_fields:
                    self.log_test("Diagrams List", False, f"Missing fields in diagram: {missing_fields}")
                    return False
                
                print(f"   Sample diagram ID: {first_diagram.get('id')}")
                print(f"   Sample diagram title: {first_diagram.get('title')}")
                print(f"   Sample diagram nodes: {len(first_diagram.get('nodes', []))}")
                print(f"   Sample diagram edges: {len(first_diagram.get('edges', []))}")
            
            self.log_test("Diagrams List", True, f"✅ SUCCESS: Retrieved {len(data)} diagrams")
            return True
            
        except Exception as e:
            self.log_test("Diagrams List", False, f"Request error: {str(e)}")
            return False

    def test_diagrams_create(self):
        """
        CRITICAL TEST 2: POST /api/diagrams - Test creating new diagrams
        """
        try:
            print("🎯 CRITICAL TEST 2: POST /api/diagrams - Create New Diagram")
            print("=" * 60)
            
            # Create test diagram data
            test_diagram = {
                "title": f"Canvas Node Detection Test Diagram {uuid.uuid4().hex[:8]}",
                "description": "Test diagram for canvas node detection system testing"
            }
            
            response = self.session.post(f"{self.base_url}/diagrams", json=test_diagram)
            print(f"📋 Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("Diagrams Create", False, f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Diagrams Create", False, f"Invalid JSON response: {str(e)}")
                return False
            
            # Verify response structure
            required_fields = ["id", "title", "description", "nodes", "edges", "created_at"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                self.log_test("Diagrams Create", False, f"Missing fields in response: {missing_fields}")
                return False
            
            # Store diagram ID for later tests
            self.test_diagram_id = data.get("id")
            
            print(f"📊 Diagram Create Results:")
            print(f"   Created diagram ID: {self.test_diagram_id}")
            print(f"   Title: {data.get('title')}")
            print(f"   Description: {data.get('description')}")
            print(f"   Initial nodes: {len(data.get('nodes', []))}")
            print(f"   Initial edges: {len(data.get('edges', []))}")
            print(f"   Created at: {data.get('created_at')}")
            
            self.log_test("Diagrams Create", True, f"✅ SUCCESS: Created diagram with ID {self.test_diagram_id}")
            return True
            
        except Exception as e:
            self.log_test("Diagrams Create", False, f"Request error: {str(e)}")
            return False

    def test_diagrams_update(self):
        """
        CRITICAL TEST 3: PUT /api/diagrams/{id} - Test updating diagrams with nodes and edges
        """
        try:
            print("🎯 CRITICAL TEST 3: PUT /api/diagrams/{id} - Update Diagram with Nodes and Edges")
            print("=" * 60)
            
            if not self.test_diagram_id:
                self.log_test("Diagrams Update", False, "No test diagram ID available")
                return False
            
            # Create sample nodes and edges for canvas node detection testing
            sample_nodes = [
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
                    "label": "REST API Gateway",
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
                    "label": "User Database",
                    "position": {"x": 500, "y": 100},
                    "data": {
                        "criticality": "Critical",
                        "data_classification": "Restricted"
                    }
                }
            ]
            
            sample_edges = [
                {
                    "id": f"edge-{uuid.uuid4().hex[:8]}",
                    "source": sample_nodes[0]["id"],
                    "target": sample_nodes[1]["id"],
                    "type": "has_dependency",
                    "label": "API Dependency",
                    "data": {}
                },
                {
                    "id": f"edge-{uuid.uuid4().hex[:8]}",
                    "source": sample_nodes[1]["id"],
                    "target": sample_nodes[2]["id"],
                    "type": "has_dependency", 
                    "label": "Database Dependency",
                    "data": {}
                }
            ]
            
            # Create updated diagram data
            updated_diagram = {
                "id": self.test_diagram_id,
                "title": "Canvas Node Detection Test Diagram - Updated",
                "description": "Updated test diagram with nodes and edges for canvas detection",
                "nodes": sample_nodes,
                "edges": sample_edges,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            response = self.session.put(f"{self.base_url}/diagrams/{self.test_diagram_id}", json=updated_diagram)
            print(f"📋 Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("Diagrams Update", False, f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Diagrams Update", False, f"Invalid JSON response: {str(e)}")
                return False
            
            # Verify update was successful
            if data.get("id") != self.test_diagram_id:
                self.log_test("Diagrams Update", False, f"ID mismatch: {data.get('id')} vs {self.test_diagram_id}")
                return False
            
            updated_nodes = data.get("nodes", [])
            updated_edges = data.get("edges", [])
            
            if len(updated_nodes) != len(sample_nodes):
                self.log_test("Diagrams Update", False, f"Node count mismatch: {len(updated_nodes)} vs {len(sample_nodes)}")
                return False
            
            if len(updated_edges) != len(sample_edges):
                self.log_test("Diagrams Update", False, f"Edge count mismatch: {len(updated_edges)} vs {len(sample_edges)}")
                return False
            
            print(f"📊 Diagram Update Results:")
            print(f"   Updated diagram ID: {data.get('id')}")
            print(f"   Updated title: {data.get('title')}")
            print(f"   Nodes added: {len(updated_nodes)}")
            print(f"   Edges added: {len(updated_edges)}")
            print(f"   Node types: {[node.get('subtype') for node in updated_nodes]}")
            print(f"   Edge types: {[edge.get('type') for edge in updated_edges]}")
            print(f"   Updated at: {data.get('updated_at')}")
            
            self.log_test("Diagrams Update", True, f"✅ SUCCESS: Updated diagram with {len(updated_nodes)} nodes and {len(updated_edges)} edges")
            return True
            
        except Exception as e:
            self.log_test("Diagrams Update", False, f"Request error: {str(e)}")
            return False

    def test_webapp_questionnaire(self):
        """
        CRITICAL TEST 4: GET /api/questionnaires/WebApp?level=basic - Verify WebApp questionnaire system
        """
        try:
            print("🎯 CRITICAL TEST 4: GET /api/questionnaires/WebApp?level=basic - WebApp Questionnaire")
            print("=" * 60)
            
            response = self.session.get(f"{self.base_url}/questionnaires/WebApp", params={"level": "basic"})
            print(f"📋 Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("WebApp Questionnaire", False, f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("WebApp Questionnaire", False, f"Invalid JSON response: {str(e)}")
                return False
            
            # Verify required response fields
            required_fields = ["node_subtype", "level", "total_questions", "prompts"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                self.log_test("WebApp Questionnaire", False, f"Missing required fields: {missing_fields}")
                return False
            
            # Verify node subtype
            if data.get("node_subtype") != "WebApp":
                self.log_test("WebApp Questionnaire", False, f"Wrong node subtype: {data.get('node_subtype')}")
                return False
            
            # Verify level
            if data.get("level") != "basic":
                self.log_test("WebApp Questionnaire", False, f"Wrong level: {data.get('level')}")
                return False
            
            # Verify prompts structure
            prompts = data.get("prompts", [])
            if not prompts:
                self.log_test("WebApp Questionnaire", False, "No prompts returned")
                return False
            
            # Check first prompt structure
            first_prompt = prompts[0]
            prompt_required_fields = ["id", "question", "type"]
            prompt_missing_fields = [field for field in prompt_required_fields if field not in first_prompt]
            
            if prompt_missing_fields:
                self.log_test("WebApp Questionnaire", False, f"Missing prompt fields: {prompt_missing_fields}")
                return False
            
            print(f"📊 WebApp Questionnaire Results:")
            print(f"   Node subtype: {data.get('node_subtype')}")
            print(f"   Level: {data.get('level')}")
            print(f"   Total questions: {data.get('total_questions')}")
            print(f"   Prompts count: {len(prompts)}")
            print(f"   Sample question: {first_prompt.get('question', 'N/A')[:50]}...")
            print(f"   Sample question type: {first_prompt.get('type')}")
            print(f"   Questionnaire type: {data.get('questionnaire_type', 'N/A')}")
            print(f"   Security branches: {len(data.get('security_branches', []))}")
            
            self.log_test("WebApp Questionnaire", True, f"✅ SUCCESS: WebApp questionnaire returned {len(prompts)} prompts")
            return True
            
        except Exception as e:
            self.log_test("WebApp Questionnaire", False, f"Request error: {str(e)}")
            return False

    def test_api_questionnaire(self):
        """
        CRITICAL TEST 5: GET /api/questionnaires/API?level=basic - Verify API questionnaire system
        """
        try:
            print("🎯 CRITICAL TEST 5: GET /api/questionnaires/API?level=basic - API Questionnaire")
            print("=" * 60)
            
            response = self.session.get(f"{self.base_url}/questionnaires/API", params={"level": "basic"})
            print(f"📋 Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("API Questionnaire", False, f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("API Questionnaire", False, f"Invalid JSON response: {str(e)}")
                return False
            
            # Verify required response fields
            required_fields = ["node_subtype", "level", "total_questions", "prompts"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                self.log_test("API Questionnaire", False, f"Missing required fields: {missing_fields}")
                return False
            
            # Verify node subtype
            if data.get("node_subtype") != "API":
                self.log_test("API Questionnaire", False, f"Wrong node subtype: {data.get('node_subtype')}")
                return False
            
            # Verify level
            if data.get("level") != "basic":
                self.log_test("API Questionnaire", False, f"Wrong level: {data.get('level')}")
                return False
            
            # Verify prompts structure
            prompts = data.get("prompts", [])
            if not prompts:
                self.log_test("API Questionnaire", False, "No prompts returned")
                return False
            
            # Check first prompt structure
            first_prompt = prompts[0]
            prompt_required_fields = ["id", "question", "type"]
            prompt_missing_fields = [field for field in prompt_required_fields if field not in first_prompt]
            
            if prompt_missing_fields:
                self.log_test("API Questionnaire", False, f"Missing prompt fields: {prompt_missing_fields}")
                return False
            
            print(f"📊 API Questionnaire Results:")
            print(f"   Node subtype: {data.get('node_subtype')}")
            print(f"   Level: {data.get('level')}")
            print(f"   Total questions: {data.get('total_questions')}")
            print(f"   Prompts count: {len(prompts)}")
            print(f"   Sample question: {first_prompt.get('question', 'N/A')[:50]}...")
            print(f"   Sample question type: {first_prompt.get('type')}")
            print(f"   Questionnaire type: {data.get('questionnaire_type', 'N/A')}")
            print(f"   Security branches: {len(data.get('security_branches', []))}")
            
            self.log_test("API Questionnaire", True, f"✅ SUCCESS: API questionnaire returned {len(prompts)} prompts")
            return True
            
        except Exception as e:
            self.log_test("API Questionnaire", False, f"Request error: {str(e)}")
            return False

    def test_database_questionnaire(self):
        """
        CRITICAL TEST 6: GET /api/questionnaires/Database?level=basic - Verify Database questionnaire system
        """
        try:
            print("🎯 CRITICAL TEST 6: GET /api/questionnaires/Database?level=basic - Database Questionnaire")
            print("=" * 60)
            
            response = self.session.get(f"{self.base_url}/questionnaires/Database", params={"level": "basic"})
            print(f"📋 Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("Database Questionnaire", False, f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Database Questionnaire", False, f"Invalid JSON response: {str(e)}")
                return False
            
            # Verify required response fields
            required_fields = ["node_subtype", "level", "total_questions", "prompts"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                self.log_test("Database Questionnaire", False, f"Missing required fields: {missing_fields}")
                return False
            
            # Verify node subtype
            if data.get("node_subtype") != "Database":
                self.log_test("Database Questionnaire", False, f"Wrong node subtype: {data.get('node_subtype')}")
                return False
            
            # Verify level
            if data.get("level") != "basic":
                self.log_test("Database Questionnaire", False, f"Wrong level: {data.get('level')}")
                return False
            
            # Verify prompts structure
            prompts = data.get("prompts", [])
            if not prompts:
                self.log_test("Database Questionnaire", False, "No prompts returned")
                return False
            
            # Check first prompt structure
            first_prompt = prompts[0]
            prompt_required_fields = ["id", "question", "type"]
            prompt_missing_fields = [field for field in prompt_required_fields if field not in first_prompt]
            
            if prompt_missing_fields:
                self.log_test("Database Questionnaire", False, f"Missing prompt fields: {prompt_missing_fields}")
                return False
            
            print(f"📊 Database Questionnaire Results:")
            print(f"   Node subtype: {data.get('node_subtype')}")
            print(f"   Level: {data.get('level')}")
            print(f"   Total questions: {data.get('total_questions')}")
            print(f"   Prompts count: {len(prompts)}")
            print(f"   Sample question: {first_prompt.get('question', 'N/A')[:50]}...")
            print(f"   Sample question type: {first_prompt.get('type')}")
            print(f"   Questionnaire type: {data.get('questionnaire_type', 'N/A')}")
            print(f"   Security branches: {len(data.get('security_branches', []))}")
            
            self.log_test("Database Questionnaire", True, f"✅ SUCCESS: Database questionnaire returned {len(prompts)} prompts")
            return True
            
        except Exception as e:
            self.log_test("Database Questionnaire", False, f"Request error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all canvas node detection system tests"""
        print("🚀 STARTING CANVAS NODE DETECTION SYSTEM BACKEND API TESTING")
        print("=" * 80)
        print("Testing core API endpoints that support enhanced canvas node detection functionality")
        print("=" * 80)
        
        tests = [
            self.test_health_check,
            self.test_diagrams_list,
            self.test_diagrams_create,
            self.test_diagrams_update,
            self.test_webapp_questionnaire,
            self.test_api_questionnaire,
            self.test_database_questionnaire,
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
    tester = CanvasNodeDetectionTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)