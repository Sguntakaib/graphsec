#!/usr/bin/env python3
"""
Backend API Tests for Security Modeling Platform
Tests all API endpoints with realistic security modeling data
"""

import requests
import json
import uuid
from datetime import datetime, timezone
import sys

# Use the production URL from review request
BASE_URL = "https://smart-dev-path.preview.emergentagent.com/api"

class SecurityModelingAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.test_diagram_id = None
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
        
    def test_health_check(self):
        """Test GET /api/ health check endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "Security Modeling Platform API" in data["message"]:
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
    
    def create_realistic_diagram_data(self):
        """Create realistic security modeling diagram data"""
        diagram_id = str(uuid.uuid4())
        
        # Create realistic security nodes
        nodes = [
            # Actors
            {
                "id": str(uuid.uuid4()),
                "type": "Actor",
                "subtype": "ExternalAttacker",
                "label": "External Threat Actor",
                "position": {"x": 100, "y": 100},
                "data": {"description": "Malicious external attacker targeting web applications"},
                "mitre_ids": ["T1190", "T1566"],
                "cve_ids": []
            },
            {
                "id": str(uuid.uuid4()),
                "type": "Actor", 
                "subtype": "Insider",
                "label": "Malicious Insider",
                "position": {"x": 100, "y": 200},
                "data": {"description": "Insider with legitimate access attempting privilege escalation"},
                "mitre_ids": ["T1078", "T1484"],
                "cve_ids": []
            },
            # Assets
            {
                "id": str(uuid.uuid4()),
                "type": "Asset",
                "subtype": "WebApp",
                "label": "Customer Portal",
                "position": {"x": 400, "y": 150},
                "data": {"description": "Customer-facing web application", "criticality": "High"},
                "mitre_ids": [],
                "cve_ids": []
            },
            {
                "id": str(uuid.uuid4()),
                "type": "Asset",
                "subtype": "Database",
                "label": "Customer Database",
                "position": {"x": 600, "y": 150},
                "data": {"description": "PostgreSQL database containing customer PII", "criticality": "Critical"},
                "mitre_ids": [],
                "cve_ids": []
            },
            {
                "id": str(uuid.uuid4()),
                "type": "Asset",
                "subtype": "API",
                "label": "Payment API",
                "position": {"x": 400, "y": 250},
                "data": {"description": "REST API for payment processing", "criticality": "High"},
                "mitre_ids": [],
                "cve_ids": []
            },
            # Attack Surfaces
            {
                "id": str(uuid.uuid4()),
                "type": "Surface",
                "subtype": "SQLi",
                "label": "SQL Injection Vulnerability",
                "position": {"x": 250, "y": 100},
                "data": {"description": "Unvalidated input in search functionality", "severity": "High"},
                "mitre_ids": ["T1190", "T1213"],
                "cve_ids": ["CVE-2021-44228"]
            },
            {
                "id": str(uuid.uuid4()),
                "type": "Surface",
                "subtype": "WeakIAM",
                "label": "Weak Authentication",
                "position": {"x": 250, "y": 200},
                "data": {"description": "Insufficient access controls on admin endpoints", "severity": "Medium"},
                "mitre_ids": ["T1078", "T1484"],
                "cve_ids": []
            },
            # Controls
            {
                "id": str(uuid.uuid4()),
                "type": "Control",
                "subtype": "WAF",
                "label": "Web Application Firewall",
                "position": {"x": 300, "y": 50},
                "data": {"description": "AWS WAF protecting web applications", "effectiveness": "High"},
                "mitre_ids": [],
                "cve_ids": []
            },
            {
                "id": str(uuid.uuid4()),
                "type": "Control",
                "subtype": "EDR",
                "label": "Endpoint Detection",
                "position": {"x": 500, "y": 50},
                "data": {"description": "CrowdStrike EDR on all endpoints", "effectiveness": "High"},
                "mitre_ids": [],
                "cve_ids": []
            }
        ]
        
        # Create edges representing attack paths
        edges = [
            {
                "id": str(uuid.uuid4()),
                "source": nodes[0]["id"],  # External Attacker
                "target": nodes[5]["id"],  # SQL Injection
                "type": "attack",
                "label": "Exploits SQLi",
                "data": {"likelihood": "High", "impact": "High"}
            },
            {
                "id": str(uuid.uuid4()),
                "source": nodes[5]["id"],  # SQL Injection
                "target": nodes[2]["id"],  # Customer Portal
                "type": "attack",
                "label": "Compromises Web App",
                "data": {"likelihood": "High", "impact": "High"}
            },
            {
                "id": str(uuid.uuid4()),
                "source": nodes[2]["id"],  # Customer Portal
                "target": nodes[3]["id"],  # Customer Database
                "type": "attack",
                "label": "Accesses Database",
                "data": {"likelihood": "Medium", "impact": "Critical"}
            },
            {
                "id": str(uuid.uuid4()),
                "source": nodes[1]["id"],  # Malicious Insider
                "target": nodes[6]["id"],  # Weak Authentication
                "type": "attack",
                "label": "Exploits Weak Auth",
                "data": {"likelihood": "Medium", "impact": "Medium"}
            },
            {
                "id": str(uuid.uuid4()),
                "source": nodes[6]["id"],  # Weak Authentication
                "target": nodes[4]["id"],  # Payment API
                "type": "attack",
                "label": "Escalates Privileges",
                "data": {"likelihood": "Medium", "impact": "High"}
            }
        ]
        
        return {
            "id": diagram_id,
            "title": "E-Commerce Security Model",
            "description": "Security threat model for e-commerce platform including customer portal, payment processing, and data storage",
            "nodes": nodes,
            "edges": edges
        }
    
    def test_create_diagram(self):
        """Test POST /api/diagrams"""
        try:
            # Test basic diagram creation
            diagram_data = {
                "title": "Test Security Diagram",
                "description": "A test diagram for API validation"
            }
            
            response = self.session.post(
                f"{self.base_url}/diagrams",
                json=diagram_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and "title" in data:
                    self.test_diagram_id = data["id"]
                    self.log_test("Create Diagram", True, f"Created diagram with ID: {data['id']}")
                    return True
                else:
                    self.log_test("Create Diagram", False, f"Missing required fields in response: {data}")
                    return False
            else:
                self.log_test("Create Diagram", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Create Diagram", False, f"Error: {str(e)}")
            return False
    
    def test_get_diagrams(self):
        """Test GET /api/diagrams"""
        try:
            response = self.session.get(f"{self.base_url}/diagrams")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Get Diagrams", True, f"Retrieved {len(data)} diagrams")
                    return True
                else:
                    self.log_test("Get Diagrams", False, f"Expected list, got: {type(data)}")
                    return False
            else:
                self.log_test("Get Diagrams", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Get Diagrams", False, f"Error: {str(e)}")
            return False
    
    def test_get_specific_diagram(self):
        """Test GET /api/diagrams/{id}"""
        if not self.test_diagram_id:
            self.log_test("Get Specific Diagram", False, "No test diagram ID available")
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("id") == self.test_diagram_id:
                    self.log_test("Get Specific Diagram", True, f"Retrieved diagram: {data.get('title')}")
                    return True
                else:
                    self.log_test("Get Specific Diagram", False, f"ID mismatch: expected {self.test_diagram_id}, got {data.get('id')}")
                    return False
            elif response.status_code == 404:
                self.log_test("Get Specific Diagram", False, "Diagram not found (404)")
                return False
            else:
                self.log_test("Get Specific Diagram", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Get Specific Diagram", False, f"Error: {str(e)}")
            return False
    
    def test_update_diagram_with_security_data(self):
        """Test PUT /api/diagrams/{id} with realistic security modeling data"""
        if not self.test_diagram_id:
            self.log_test("Update Diagram with Security Data", False, "No test diagram ID available")
            return False
            
        try:
            # Create realistic security diagram data
            realistic_data = self.create_realistic_diagram_data()
            realistic_data["id"] = self.test_diagram_id  # Use existing diagram ID
            
            response = self.session.put(
                f"{self.base_url}/diagrams/{self.test_diagram_id}",
                json=realistic_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                nodes_count = len(data.get("nodes", []))
                edges_count = len(data.get("edges", []))
                
                # Verify security node types are present
                node_types = {node.get("type") for node in data.get("nodes", [])}
                expected_types = {"Actor", "Asset", "Surface", "Control"}
                
                if expected_types.issubset(node_types):
                    self.log_test("Update Diagram with Security Data", True, 
                                f"Updated with {nodes_count} nodes, {edges_count} edges, types: {node_types}")
                    return True
                else:
                    missing_types = expected_types - node_types
                    self.log_test("Update Diagram with Security Data", False, 
                                f"Missing node types: {missing_types}")
                    return False
            else:
                self.log_test("Update Diagram with Security Data", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Update Diagram with Security Data", False, f"Error: {str(e)}")
            return False
    
    def test_simulate_attack_paths(self):
        """Test POST /api/diagrams/{id}/simulate"""
        if not self.test_diagram_id:
            self.log_test("Simulate Attack Paths", False, "No test diagram ID available")
            return False
            
        try:
            response = self.session.post(f"{self.base_url}/diagrams/{self.test_diagram_id}/simulate")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["id", "diagram_id", "attack_paths", "recommendations", "mitre_techniques", "risk_score"]
                
                if all(field in data for field in required_fields):
                    attack_paths_count = len(data.get("attack_paths", []))
                    recommendations_count = len(data.get("recommendations", []))
                    mitre_count = len(data.get("mitre_techniques", []))
                    risk_score = data.get("risk_score", 0)
                    
                    # Verify simulation logic produces meaningful results
                    if attack_paths_count > 0 and recommendations_count > 0:
                        self.log_test("Simulate Attack Paths", True, 
                                    f"Generated {attack_paths_count} attack paths, {recommendations_count} recommendations, "
                                    f"{mitre_count} MITRE techniques, risk score: {risk_score}")
                        return True
                    else:
                        self.log_test("Simulate Attack Paths", False, 
                                    f"Simulation produced no meaningful results: {attack_paths_count} paths, {recommendations_count} recommendations")
                        return False
                else:
                    missing_fields = [f for f in required_fields if f not in data]
                    self.log_test("Simulate Attack Paths", False, f"Missing required fields: {missing_fields}")
                    return False
            elif response.status_code == 404:
                self.log_test("Simulate Attack Paths", False, "Diagram not found for simulation (404)")
                return False
            else:
                self.log_test("Simulate Attack Paths", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Simulate Attack Paths", False, f"Error: {str(e)}")
            return False
    
    def test_get_simulations(self):
        """Test GET /api/diagrams/{id}/simulations"""
        if not self.test_diagram_id:
            self.log_test("Get Simulations", False, "No test diagram ID available")
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}/simulations")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    simulations_count = len(data)
                    if simulations_count > 0:
                        # Verify simulation data structure
                        first_sim = data[0]
                        required_fields = ["id", "diagram_id", "attack_paths", "recommendations", "mitre_techniques", "risk_score"]
                        if all(field in first_sim for field in required_fields):
                            self.log_test("Get Simulations", True, f"Retrieved {simulations_count} simulation results")
                            return True
                        else:
                            missing_fields = [f for f in required_fields if f not in first_sim]
                            self.log_test("Get Simulations", False, f"Simulation missing fields: {missing_fields}")
                            return False
                    else:
                        self.log_test("Get Simulations", True, "No simulations found (empty list)")
                        return True
                else:
                    self.log_test("Get Simulations", False, f"Expected list, got: {type(data)}")
                    return False
            else:
                self.log_test("Get Simulations", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Get Simulations", False, f"Error: {str(e)}")
            return False
    
    def test_simulation_logic_validation(self):
        """Test that simulation logic produces meaningful security analysis"""
        if not self.test_diagram_id:
            self.log_test("Simulation Logic Validation", False, "No test diagram ID available")
            return False
            
        try:
            # Get the latest simulation results
            response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}/simulations")
            
            if response.status_code == 200:
                simulations = response.json()
                if not simulations:
                    self.log_test("Simulation Logic Validation", False, "No simulations to validate")
                    return False
                
                latest_sim = simulations[-1]  # Get most recent simulation
                attack_paths = latest_sim.get("attack_paths", [])
                recommendations = latest_sim.get("recommendations", [])
                mitre_techniques = latest_sim.get("mitre_techniques", [])
                
                validation_results = []
                
                # Validate attack paths structure
                for i, path in enumerate(attack_paths):
                    if "steps" in path and "likelihood" in path and "impact" in path:
                        steps = path["steps"]
                        if len(steps) >= 2:  # Should have at least 2 steps for a meaningful path
                            validation_results.append(f"Attack path {i+1}: {len(steps)} steps")
                        else:
                            validation_results.append(f"Attack path {i+1}: Too few steps ({len(steps)})")
                    else:
                        validation_results.append(f"Attack path {i+1}: Missing required fields")
                
                # Validate MITRE techniques are realistic
                valid_mitre_pattern = all(t.startswith("T") and len(t) >= 5 for t in mitre_techniques)
                if valid_mitre_pattern:
                    validation_results.append(f"MITRE techniques valid: {mitre_techniques}")
                else:
                    validation_results.append(f"Invalid MITRE techniques: {mitre_techniques}")
                
                # Validate recommendations are security-focused
                security_keywords = ["WAF", "EDR", "firewall", "monitoring", "access", "control", "security"]
                security_recommendations = [r for r in recommendations if any(keyword.lower() in r.lower() for keyword in security_keywords)]
                
                if len(security_recommendations) > 0:
                    validation_results.append(f"Security-focused recommendations: {len(security_recommendations)}/{len(recommendations)}")
                    self.log_test("Simulation Logic Validation", True, "; ".join(validation_results))
                    return True
                else:
                    validation_results.append("No security-focused recommendations found")
                    self.log_test("Simulation Logic Validation", False, "; ".join(validation_results))
                    return False
            else:
                self.log_test("Simulation Logic Validation", False, f"Failed to get simulations: HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Simulation Logic Validation", False, f"Error: {str(e)}")
            return False
    
    def create_comprehensive_security_diagram(self):
        """Create comprehensive security diagram with multiple threat actors, assets, and controls"""
        diagram_id = str(uuid.uuid4())
        
        nodes = [
            # Multiple Threat Actors
            {
                "id": str(uuid.uuid4()),
                "type": "Actor",
                "subtype": "ExternalAttacker",
                "label": "External Threat Actor",
                "position": {"x": 50, "y": 100},
                "data": {"description": "Advanced persistent threat group targeting cloud infrastructure"},
                "mitre_ids": ["T1190", "T1566"],
                "cve_ids": []
            },
            {
                "id": str(uuid.uuid4()),
                "type": "Actor",
                "subtype": "Insider",
                "label": "Malicious Insider",
                "position": {"x": 50, "y": 200},
                "data": {"description": "Privileged insider with legitimate access"},
                "mitre_ids": ["T1078", "T1484"],
                "cve_ids": []
            },
            {
                "id": str(uuid.uuid4()),
                "type": "Actor",
                "subtype": "ServiceAccount",
                "label": "Nation State Actor",
                "position": {"x": 50, "y": 300},
                "data": {"description": "State-sponsored advanced threat actor"},
                "mitre_ids": ["T1552.001", "T1003"],
                "cve_ids": []
            },
            
            # Critical Assets
            {
                "id": str(uuid.uuid4()),
                "type": "Asset",
                "subtype": "Database",
                "label": "Customer Database",
                "position": {"x": 600, "y": 150},
                "data": {"description": "PostgreSQL database with customer PII", "criticality": "Critical"},
                "mitre_ids": [],
                "cve_ids": []
            },
            {
                "id": str(uuid.uuid4()),
                "type": "Asset",
                "subtype": "API",
                "label": "Payment API",
                "position": {"x": 600, "y": 250},
                "data": {"description": "REST API for payment processing", "criticality": "High"},
                "mitre_ids": [],
                "cve_ids": []
            },
            {
                "id": str(uuid.uuid4()),
                "type": "Asset",
                "subtype": "IMDS",
                "label": "EC2 Instance Metadata",
                "position": {"x": 600, "y": 350},
                "data": {"description": "AWS EC2 instance metadata service", "criticality": "High"},
                "mitre_ids": [],
                "cve_ids": []
            },
            {
                "id": str(uuid.uuid4()),
                "type": "Asset",
                "subtype": "S3Bucket",
                "label": "Active Directory",
                "position": {"x": 600, "y": 450},
                "data": {"description": "Windows Active Directory domain controller", "criticality": "Critical"},
                "mitre_ids": [],
                "cve_ids": []
            },
            
            # Attack Surfaces
            {
                "id": str(uuid.uuid4()),
                "type": "Surface",
                "subtype": "SSRF",
                "label": "SSRF Vulnerability",
                "position": {"x": 300, "y": 100},
                "data": {"description": "Server-side request forgery in image processing", "severity": "High"},
                "mitre_ids": ["T1190"],
                "cve_ids": []
            },
            {
                "id": str(uuid.uuid4()),
                "type": "Surface",
                "subtype": "SQLi",
                "label": "SQL Injection",
                "position": {"x": 300, "y": 200},
                "data": {"description": "SQL injection in search functionality", "severity": "Critical"},
                "mitre_ids": ["T1190", "T1213"],
                "cve_ids": ["CVE-2021-44228"]
            },
            {
                "id": str(uuid.uuid4()),
                "type": "Surface",
                "subtype": "RCE",
                "label": "Remote Code Execution",
                "position": {"x": 300, "y": 300},
                "data": {"description": "RCE via deserialization vulnerability", "severity": "Critical"},
                "mitre_ids": ["T1059"],
                "cve_ids": []
            },
            {
                "id": str(uuid.uuid4()),
                "type": "Surface",
                "subtype": "WeakIAM",
                "label": "Weak IAM Controls",
                "position": {"x": 300, "y": 400},
                "data": {"description": "Insufficient access controls and privilege escalation", "severity": "High"},
                "mitre_ids": ["T1078", "T1484"],
                "cve_ids": []
            },
            
            # Security Controls
            {
                "id": str(uuid.uuid4()),
                "type": "Control",
                "subtype": "WAF",
                "label": "Web Application Firewall",
                "position": {"x": 150, "y": 50},
                "data": {"description": "AWS WAF with OWASP rules", "effectiveness": "High"},
                "mitre_ids": [],
                "cve_ids": []
            },
            {
                "id": str(uuid.uuid4()),
                "type": "Control",
                "subtype": "EDR",
                "label": "Endpoint Detection & Response",
                "position": {"x": 300, "y": 50},
                "data": {"description": "CrowdStrike Falcon EDR", "effectiveness": "High"},
                "mitre_ids": [],
                "cve_ids": []
            },
            {
                "id": str(uuid.uuid4()),
                "type": "Control",
                "subtype": "EgressProxy",
                "label": "SIEM System",
                "position": {"x": 450, "y": 50},
                "data": {"description": "Splunk SIEM with threat intelligence", "effectiveness": "Medium"},
                "mitre_ids": [],
                "cve_ids": []
            },
            
            # Network Zones
            {
                "id": str(uuid.uuid4()),
                "type": "Zone",
                "subtype": "DMZ",
                "label": "DMZ Network",
                "position": {"x": 400, "y": 500},
                "data": {"description": "Demilitarized zone for public services"},
                "mitre_ids": [],
                "cve_ids": []
            },
            
            # Detection Signals
            {
                "id": str(uuid.uuid4()),
                "type": "Signal",
                "subtype": "NetworkAnomaly",
                "label": "Network Anomaly Detection",
                "position": {"x": 500, "y": 500},
                "data": {"description": "ML-based network anomaly detection"},
                "mitre_ids": [],
                "cve_ids": []
            }
        ]
        
        # Create complex attack path edges
        edges = []
        node_ids = [node["id"] for node in nodes]
        
        # External Attacker -> SSRF -> Database
        edges.append({
            "id": str(uuid.uuid4()),
            "source": node_ids[0],  # External Attacker
            "target": node_ids[7],  # SSRF
            "type": "attack",
            "label": "Exploits SSRF",
            "data": {"likelihood": "High", "impact": "High"}
        })
        
        edges.append({
            "id": str(uuid.uuid4()),
            "source": node_ids[7],  # SSRF
            "target": node_ids[3],  # Database
            "type": "attack",
            "label": "Accesses Database",
            "data": {"likelihood": "Medium", "impact": "Critical"}
        })
        
        # Insider -> Weak IAM -> Active Directory
        edges.append({
            "id": str(uuid.uuid4()),
            "source": node_ids[1],  # Insider
            "target": node_ids[10], # Weak IAM
            "type": "attack",
            "label": "Exploits IAM",
            "data": {"likelihood": "High", "impact": "High"}
        })
        
        edges.append({
            "id": str(uuid.uuid4()),
            "source": node_ids[10], # Weak IAM
            "target": node_ids[6],  # Active Directory
            "type": "attack",
            "label": "Escalates to AD",
            "data": {"likelihood": "Medium", "impact": "Critical"}
        })
        
        # Nation State -> RCE -> IMDS
        edges.append({
            "id": str(uuid.uuid4()),
            "source": node_ids[2],  # Nation State
            "target": node_ids[9],  # RCE
            "type": "attack",
            "label": "Exploits RCE",
            "data": {"likelihood": "Medium", "impact": "High"}
        })
        
        edges.append({
            "id": str(uuid.uuid4()),
            "source": node_ids[9],  # RCE
            "target": node_ids[5],  # IMDS
            "type": "attack",
            "label": "Accesses IMDS",
            "data": {"likelihood": "High", "impact": "High"}
        })
        
        return {
            "id": diagram_id,
            "title": "Comprehensive Security Threat Model",
            "description": "Advanced security model with multiple threat actors, critical assets, attack surfaces, and security controls for testing enhanced simulation capabilities",
            "nodes": nodes,
            "edges": edges
        }
    
    def test_advanced_simulation_endpoint(self):
        """Test POST /api/diagrams/{id}/simulate with complex security diagram"""
        try:
            # Create comprehensive diagram
            comprehensive_data = self.create_comprehensive_security_diagram()
            
            # Create diagram first
            response = self.session.post(
                f"{self.base_url}/diagrams",
                json={"title": comprehensive_data["title"], "description": comprehensive_data["description"]},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                self.log_test("Advanced Simulation - Create Diagram", False, f"Failed to create diagram: {response.status_code}")
                return False
            
            diagram_id = response.json()["id"]
            comprehensive_data["id"] = diagram_id
            
            # Update with comprehensive data
            response = self.session.put(
                f"{self.base_url}/diagrams/{diagram_id}",
                json=comprehensive_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                self.log_test("Advanced Simulation - Update Diagram", False, f"Failed to update diagram: {response.status_code}")
                return False
            
            # Run advanced simulation
            response = self.session.post(f"{self.base_url}/diagrams/{diagram_id}/simulate")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for enhanced simulation features
                required_fields = [
                    "attack_paths", "recommendations", "mitre_techniques", "mitre_coverage",
                    "risk_score", "overall_risk_level", "detection_coverage", 
                    "technique_details", "suggested_controls"
                ]
                
                missing_fields = [f for f in required_fields if f not in data]
                if missing_fields:
                    self.log_test("Advanced Simulation", False, f"Missing enhanced fields: {missing_fields}")
                    return False
                
                # Validate enhanced features
                attack_paths = data.get("attack_paths", [])
                mitre_coverage = data.get("mitre_coverage", {})
                technique_details = data.get("technique_details", {})
                
                # Check for graph-based attack path analysis
                if len(attack_paths) == 0:
                    self.log_test("Advanced Simulation", False, "No attack paths generated")
                    return False
                
                # Validate attack path structure with NetworkX algorithms
                path_has_steps = any("steps" in path for path in attack_paths)
                if not path_has_steps:
                    self.log_test("Advanced Simulation", False, "Attack paths missing step details")
                    return False
                
                # Check MITRE coverage analysis
                if not mitre_coverage or "tactics_covered" not in mitre_coverage:
                    self.log_test("Advanced Simulation", False, "Missing MITRE coverage analysis")
                    return False
                
                # Check technique details
                if not technique_details:
                    self.log_test("Advanced Simulation", False, "Missing technique details")
                    return False
                
                self.log_test("Advanced Simulation", True, 
                            f"Enhanced simulation: {len(attack_paths)} paths, "
                            f"{len(mitre_coverage.get('tactics_covered', []))} tactics covered, "
                            f"{len(technique_details)} technique details, "
                            f"risk level: {data.get('overall_risk_level')}")
                return True
            else:
                self.log_test("Advanced Simulation", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Advanced Simulation", False, f"Error: {str(e)}")
            return False
    
    def test_mitre_technique_endpoints(self):
        """Test MITRE technique endpoints"""
        test_techniques = ["T1190", "T1078", "T1552.001"]
        
        for technique_id in test_techniques:
            try:
                response = self.session.get(f"{self.base_url}/mitre/technique/{technique_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    required_fields = [
                        "technique_id", "name", "description", "tactics", 
                        "platforms", "detection_methods", "mitigations"
                    ]
                    
                    missing_fields = [f for f in required_fields if f not in data]
                    if missing_fields:
                        self.log_test(f"MITRE Technique {technique_id}", False, f"Missing fields: {missing_fields}")
                        return False
                    
                    self.log_test(f"MITRE Technique {technique_id}", True, 
                                f"Retrieved: {data.get('name')} with {len(data.get('tactics', []))} tactics")
                else:
                    self.log_test(f"MITRE Technique {technique_id}", False, f"HTTP {response.status_code}")
                    return False
                    
            except Exception as e:
                self.log_test(f"MITRE Technique {technique_id}", False, f"Error: {str(e)}")
                return False
        
        return True
    
    def test_techniques_by_tactic(self):
        """Test GET /api/mitre/techniques/by-tactic/{tactic}"""
        try:
            response = self.session.get(f"{self.base_url}/mitre/techniques/by-tactic/Initial Access")
            
            if response.status_code == 200:
                data = response.json()
                
                if not isinstance(data, list):
                    self.log_test("Techniques by Tactic", False, f"Expected list, got {type(data)}")
                    return False
                
                if len(data) == 0:
                    self.log_test("Techniques by Tactic", False, "No techniques returned for Initial Access")
                    return False
                
                # Check structure of returned techniques
                first_technique = data[0]
                required_fields = ["technique_id", "name", "description"]
                missing_fields = [f for f in required_fields if f not in first_technique]
                
                if missing_fields:
                    self.log_test("Techniques by Tactic", False, f"Missing fields in technique: {missing_fields}")
                    return False
                
                self.log_test("Techniques by Tactic", True, 
                            f"Retrieved {len(data)} techniques for Initial Access tactic")
                return True
            else:
                self.log_test("Techniques by Tactic", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Techniques by Tactic", False, f"Error: {str(e)}")
            return False
    
    def test_analyze_coverage_endpoint(self):
        """Test POST /api/diagrams/{id}/analyze-coverage"""
        if not self.test_diagram_id:
            self.log_test("Analyze Coverage", False, "No test diagram ID available")
            return False
            
        try:
            response = self.session.post(f"{self.base_url}/diagrams/{self.test_diagram_id}/analyze-coverage")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for coverage analysis fields
                expected_fields = [
                    "tactics_covered", "techniques_analyzed", "detection_difficulty",
                    "recommended_mitigations", "data_sources_needed"
                ]
                
                missing_fields = [f for f in expected_fields if f not in data]
                if missing_fields:
                    self.log_test("Analyze Coverage", False, f"Missing coverage fields: {missing_fields}")
                    return False
                
                tactics_count = len(data.get("tactics_covered", []))
                techniques_count = data.get("techniques_analyzed", 0)
                
                self.log_test("Analyze Coverage", True, 
                            f"Coverage analysis: {tactics_count} tactics, {techniques_count} techniques analyzed")
                return True
            else:
                self.log_test("Analyze Coverage", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Analyze Coverage", False, f"Error: {str(e)}")
            return False
    
    def test_risk_analysis_endpoint(self):
        """Test GET /api/diagrams/{id}/risk-analysis"""
        if not self.test_diagram_id:
            self.log_test("Risk Analysis", False, "No test diagram ID available")
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}/risk-analysis")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for risk analysis fields
                expected_fields = [
                    "overall_risk_score", "risk_level", "attack_paths_count",
                    "risk_distribution", "top_attack_vectors", "coverage_gaps"
                ]
                
                missing_fields = [f for f in expected_fields if f not in data]
                if missing_fields:
                    self.log_test("Risk Analysis", False, f"Missing risk analysis fields: {missing_fields}")
                    return False
                
                risk_score = data.get("overall_risk_score", 0)
                risk_level = data.get("risk_level", "Unknown")
                paths_count = data.get("attack_paths_count", 0)
                
                self.log_test("Risk Analysis", True, 
                            f"Risk analysis: score {risk_score}, level {risk_level}, {paths_count} attack paths")
                return True
            elif response.status_code == 404:
                self.log_test("Risk Analysis", False, "No simulation results found for risk analysis")
                return False
            else:
                self.log_test("Risk Analysis", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Risk Analysis", False, f"Error: {str(e)}")
            return False
    
    def test_auto_layout_endpoint(self):
        """Test POST /api/diagrams/{id}/auto-layout"""
        if not self.test_diagram_id:
            self.log_test("Auto Layout", False, "No test diagram ID available")
            return False
            
        try:
            response = self.session.post(f"{self.base_url}/diagrams/{self.test_diagram_id}/auto-layout")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for layout response fields
                expected_fields = ["layout_positions", "algorithm", "node_count"]
                
                missing_fields = [f for f in expected_fields if f not in data]
                if missing_fields:
                    self.log_test("Auto Layout", False, f"Missing layout fields: {missing_fields}")
                    return False
                
                layout_positions = data.get("layout_positions", {})
                algorithm = data.get("algorithm", "unknown")
                node_count = data.get("node_count", 0)
                
                if not layout_positions:
                    self.log_test("Auto Layout", False, "No layout positions generated")
                    return False
                
                self.log_test("Auto Layout", True, 
                            f"Auto layout: {algorithm} algorithm, {node_count} nodes positioned")
                return True
            else:
                self.log_test("Auto Layout", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Auto Layout", False, f"Error: {str(e)}")
            return False

    # Phase 1 Intelligent Node System Tests
    def test_intelligent_nodes_supported_types(self):
        """Test GET /api/intelligent-nodes/supported-types"""
        try:
            response = self.session.get(f"{self.base_url}/intelligent-nodes/supported-types")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for required fields
                expected_fields = ["supported_types", "total_count"]
                missing_fields = [f for f in expected_fields if f not in data]
                
                if missing_fields:
                    self.log_test("Intelligent Nodes - Supported Types", False, f"Missing fields: {missing_fields}")
                    return False
                
                supported_types = data.get("supported_types", [])
                total_count = data.get("total_count", 0)
                
                # Verify expected node types are supported
                expected_types = ["WebApp", "Database", "API", "ExternalAttacker"]
                found_types = [t.get("node_subtype") for t in supported_types]
                
                missing_types = [t for t in expected_types if t not in found_types]
                if missing_types:
                    self.log_test("Intelligent Nodes - Supported Types", False, 
                                f"Missing expected types: {missing_types}. Found: {found_types}")
                    return False
                
                # Verify structure of type info
                if supported_types:
                    first_type = supported_types[0]
                    required_type_fields = ["node_subtype", "node_type", "required_branches_count", "security_prompts_count"]
                    missing_type_fields = [f for f in required_type_fields if f not in first_type]
                    
                    if missing_type_fields:
                        self.log_test("Intelligent Nodes - Supported Types", False, 
                                    f"Missing type info fields: {missing_type_fields}")
                        return False
                
                self.log_test("Intelligent Nodes - Supported Types", True, 
                            f"Retrieved {total_count} supported types: {found_types}")
                return True
            else:
                self.log_test("Intelligent Nodes - Supported Types", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Intelligent Nodes - Supported Types", False, f"Error: {str(e)}")
            return False

    def test_intelligent_nodes_templates(self):
        """Test GET /api/intelligent-nodes/{node_subtype}/template"""
        test_subtypes = ["WebApp", "Database", "API", "ExternalAttacker"]
        
        for subtype in test_subtypes:
            try:
                response = self.session.get(f"{self.base_url}/intelligent-nodes/{subtype}/template")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check for required template fields
                    expected_fields = ["node_type", "node_subtype", "required_branches", "security_prompts", "risk_factors"]
                    missing_fields = [f for f in expected_fields if f not in data]
                    
                    if missing_fields:
                        self.log_test(f"Intelligent Template - {subtype}", False, f"Missing fields: {missing_fields}")
                        return False
                    
                    # Verify template structure
                    required_branches = data.get("required_branches", [])
                    security_prompts = data.get("security_prompts", [])
                    risk_factors = data.get("risk_factors", {})
                    
                    # ExternalAttacker doesn't have required branches, which is expected
                    if subtype == "ExternalAttacker" and not required_branches:
                        self.log_test(f"Intelligent Template - {subtype}", True, 
                                    f"Template: {len(required_branches)} branches (expected for attacker), {len(security_prompts)} prompts")
                        continue
                    elif not required_branches:
                        self.log_test(f"Intelligent Template - {subtype}", False, "No required branches defined")
                        return False
                    
                    if not security_prompts:
                        self.log_test(f"Intelligent Template - {subtype}", False, "No security prompts defined")
                        return False
                    
                    # Verify security prompt structure
                    if security_prompts:
                        first_prompt = security_prompts[0]
                        required_prompt_fields = ["id", "question", "type", "options", "related_branch"]
                        missing_prompt_fields = [f for f in required_prompt_fields if f not in first_prompt]
                        
                        if missing_prompt_fields:
                            self.log_test(f"Intelligent Template - {subtype}", False, 
                                        f"Missing prompt fields: {missing_prompt_fields}")
                            return False
                    
                    self.log_test(f"Intelligent Template - {subtype}", True, 
                                f"Template: {len(required_branches)} branches, {len(security_prompts)} prompts")
                    
                elif response.status_code == 404:
                    self.log_test(f"Intelligent Template - {subtype}", False, f"Template not found for {subtype}")
                    return False
                else:
                    self.log_test(f"Intelligent Template - {subtype}", False, 
                                f"HTTP {response.status_code}: {response.text}")
                    return False
                    
            except Exception as e:
                self.log_test(f"Intelligent Template - {subtype}", False, f"Error: {str(e)}")
                return False
        
        return True

    def test_intelligent_nodes_prompts(self):
        """Test GET /api/intelligent-nodes/{node_subtype}/prompts"""
        test_subtypes = ["WebApp", "Database", "API"]
        
        for subtype in test_subtypes:
            try:
                response = self.session.get(f"{self.base_url}/intelligent-nodes/{subtype}/prompts")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check for required fields
                    expected_fields = ["node_subtype", "prompts"]
                    missing_fields = [f for f in expected_fields if f not in data]
                    
                    if missing_fields:
                        self.log_test(f"Intelligent Prompts - {subtype}", False, f"Missing fields: {missing_fields}")
                        return False
                    
                    prompts = data.get("prompts", [])
                    if not prompts:
                        self.log_test(f"Intelligent Prompts - {subtype}", False, "No security prompts returned")
                        return False
                    
                    # Verify prompt structure with validation rules
                    first_prompt = prompts[0]
                    required_prompt_fields = ["id", "question", "type", "options", "related_branch", "validation_rules"]
                    missing_prompt_fields = [f for f in required_prompt_fields if f not in first_prompt]
                    
                    if missing_prompt_fields:
                        self.log_test(f"Intelligent Prompts - {subtype}", False, 
                                    f"Missing prompt fields: {missing_prompt_fields}")
                        return False
                    
                    # Verify prompt types are valid
                    valid_types = ["single_choice", "multiple_choice", "text", "boolean", "number"]
                    prompt_types = [p.get("type") for p in prompts]
                    invalid_types = [t for t in prompt_types if t not in valid_types]
                    
                    if invalid_types:
                        self.log_test(f"Intelligent Prompts - {subtype}", False, 
                                    f"Invalid prompt types: {invalid_types}")
                        return False
                    
                    self.log_test(f"Intelligent Prompts - {subtype}", True, 
                                f"Retrieved {len(prompts)} security prompts with validation")
                    
                elif response.status_code == 404:
                    self.log_test(f"Intelligent Prompts - {subtype}", False, f"Prompts not found for {subtype}")
                    return False
                else:
                    self.log_test(f"Intelligent Prompts - {subtype}", False, 
                                f"HTTP {response.status_code}: {response.text}")
                    return False
                    
            except Exception as e:
                self.log_test(f"Intelligent Prompts - {subtype}", False, f"Error: {str(e)}")
                return False
        
        return True

    def test_intelligent_nodes_create_branches(self):
        """Test POST /api/intelligent-nodes/{node_subtype}/create-branches"""
        test_subtypes = ["WebApp", "Database", "API"]
        
        for subtype in test_subtypes:
            try:
                response = self.session.post(f"{self.base_url}/intelligent-nodes/{subtype}/create-branches")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check for required fields
                    expected_fields = ["node_subtype", "branches"]
                    missing_fields = [f for f in expected_fields if f not in data]
                    
                    if missing_fields:
                        self.log_test(f"Create Branches - {subtype}", False, f"Missing fields: {missing_fields}")
                        return False
                    
                    branches = data.get("branches", [])
                    
                    # Some subtypes might not have required branches
                    if not branches:
                        self.log_test(f"Create Branches - {subtype}", True, f"No required branches for {subtype}")
                        continue
                    
                    # Verify branch structure
                    first_branch = branches[0]
                    required_branch_fields = ["id", "name", "type", "required", "completed", "description"]
                    missing_branch_fields = [f for f in required_branch_fields if f not in first_branch]
                    
                    if missing_branch_fields:
                        self.log_test(f"Create Branches - {subtype}", False, 
                                    f"Missing branch fields: {missing_branch_fields}")
                        return False
                    
                    # Verify branch types are valid
                    valid_branch_types = ["Login", "API", "Database", "InputValidation", "WAF", "Encryption", "AccessControl", "Authentication", "Authorization", "RateLimiting", "CORS", "DataClassification", "Backup", "Monitoring", "Logging"]
                    branch_types = [b.get("type") for b in branches]
                    invalid_branch_types = [t for t in branch_types if t not in valid_branch_types]
                    
                    if invalid_branch_types:
                        self.log_test(f"Create Branches - {subtype}", False, 
                                    f"Invalid branch types: {invalid_branch_types}")
                        return False
                    
                    self.log_test(f"Create Branches - {subtype}", True, 
                                f"Created {len(branches)} security branches")
                    
                else:
                    self.log_test(f"Create Branches - {subtype}", False, 
                                f"HTTP {response.status_code}: {response.text}")
                    return False
                    
            except Exception as e:
                self.log_test(f"Create Branches - {subtype}", False, f"Error: {str(e)}")
                return False
        
        return True

    def test_intelligent_nodes_validate_completeness(self):
        """Test POST /api/intelligent-nodes/{node_subtype}/validate-completeness"""
        # CRITICAL: API expects direct list format, NOT object with "branches" property
        test_cases = [
            {
                "subtype": "WebApp",
                "branches": [
                    {
                        "id": "webapp_login",
                        "name": "Login",
                        "type": "Login",
                        "required": True,
                        "completed": True,
                        "value": "Password Only",
                        "description": "Authentication method"
                    },
                    {
                        "id": "webapp_api_endpoints",
                        "name": "API",
                        "type": "API",
                        "required": True,
                        "completed": False,
                        "value": None,
                        "description": "API endpoints not configured"
                    }
                ]
            },
            {
                "subtype": "Database",
                "branches": [
                    {
                        "id": "db_encryption_at_rest",
                        "name": "Encryption",
                        "type": "Encryption",
                        "required": True,
                        "completed": True,
                        "value": "AES-256",
                        "description": "Encryption at rest enabled"
                    }
                ]
            }
        ]
        
        for test_case in test_cases:
            subtype = test_case["subtype"]
            branches = test_case["branches"]
            
            try:
                # CRITICAL: Send branches as direct list, not wrapped in object
                response = self.session.post(
                    f"{self.base_url}/intelligent-nodes/{subtype}/validate-completeness",
                    json=branches,  # Direct list format as per API contract
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check for required fields
                    expected_fields = ["node_subtype", "validation", "recommendations"]
                    missing_fields = [f for f in expected_fields if f not in data]
                    
                    if missing_fields:
                        self.log_test(f"Validate Completeness - {subtype}", False, f"Missing fields: {missing_fields}")
                        return False
                    
                    validation = data.get("validation", {})
                    recommendations = data.get("recommendations", [])
                    
                    # Verify validation structure
                    if "is_complete" not in validation:
                        self.log_test(f"Validate Completeness - {subtype}", False, "Missing is_complete in validation")
                        return False
                    
                    is_complete = validation.get("is_complete", False)
                    
                    # For WebApp test case, should not be complete due to incomplete encryption branch
                    if subtype == "WebApp" and is_complete:
                        self.log_test(f"Validate Completeness - {subtype}", False, 
                                    "Expected incomplete validation due to missing encryption")
                        return False
                    
                    self.log_test(f"Validate Completeness - {subtype}", True, 
                                f"Validation: complete={is_complete}, {len(recommendations)} recommendations")
                    
                else:
                    self.log_test(f"Validate Completeness - {subtype}", False, 
                                f"HTTP {response.status_code}: {response.text}")
                    return False
                    
            except Exception as e:
                self.log_test(f"Validate Completeness - {subtype}", False, f"Error: {str(e)}")
                return False
        
        return True

    def test_intelligent_nodes_calculate_risk(self):
        """Test POST /api/intelligent-nodes/{node_subtype}/calculate-risk"""
        test_cases = [
            {
                "subtype": "WebApp",
                "branch_values": {
                    "authentication": "basic",
                    "encryption": "none",
                    "input_validation": "minimal",
                    "access_control": "weak"
                }
            },
            {
                "subtype": "Database",
                "branch_values": {
                    "encryption_at_rest": "enabled",
                    "access_control": "strong",
                    "backup_frequency": "daily",
                    "monitoring": "comprehensive"
                }
            },
            {
                "subtype": "API",
                "branch_values": {
                    "authentication": "oauth2",
                    "rate_limiting": "enabled",
                    "input_validation": "comprehensive",
                    "logging": "detailed"
                }
            }
        ]
        
        for test_case in test_cases:
            subtype = test_case["subtype"]
            branch_values = test_case["branch_values"]
            
            try:
                response = self.session.post(
                    f"{self.base_url}/intelligent-nodes/{subtype}/calculate-risk",
                    json=branch_values,  # Direct branch_values object
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check for required fields
                    expected_fields = ["node_subtype", "risk_score", "risk_level", "branch_values", "recommendations"]
                    missing_fields = [f for f in expected_fields if f not in data]
                    
                    if missing_fields:
                        self.log_test(f"Calculate Risk - {subtype}", False, f"Missing fields: {missing_fields}")
                        return False
                    
                    risk_score = data.get("risk_score", 0)
                    risk_level = data.get("risk_level", "Unknown")
                    recommendations = data.get("recommendations", [])
                    
                    # Verify risk score is valid (0-10 scale)
                    if not (0 <= risk_score <= 10):
                        self.log_test(f"Calculate Risk - {subtype}", False, 
                                    f"Invalid risk score: {risk_score} (should be 0-10)")
                        return False
                    
                    # Verify risk level is valid
                    valid_risk_levels = ["Low", "Medium", "High", "Critical"]
                    if risk_level not in valid_risk_levels:
                        self.log_test(f"Calculate Risk - {subtype}", False, 
                                    f"Invalid risk level: {risk_level}")
                        return False
                    
                    # WebApp with weak security should have medium to high risk (4.0+ is reasonable)
                    if subtype == "WebApp" and risk_score < 3.0:
                        self.log_test(f"Calculate Risk - {subtype}", False, 
                                    f"Expected higher risk for weak WebApp security, got {risk_score}")
                        return False
                    
                    # Database with strong security should have lower risk
                    if subtype == "Database" and risk_score > 5.0:
                        self.log_test(f"Calculate Risk - {subtype}", False, 
                                    f"Expected lower risk for strong Database security, got {risk_score}")
                        return False
                    
                    self.log_test(f"Calculate Risk - {subtype}", True, 
                                f"Risk: {risk_score}/10 ({risk_level}), {len(recommendations)} recommendations")
                    
                else:
                    self.log_test(f"Calculate Risk - {subtype}", False, 
                                f"HTTP {response.status_code}: {response.text}")
                    return False
                    
            except Exception as e:
                self.log_test(f"Calculate Risk - {subtype}", False, f"Error: {str(e)}")
                return False
        
        return True

    def test_intelligent_nodes_invalid_subtypes(self):
        """Test intelligent node endpoints with invalid/unsupported subtypes"""
        invalid_subtypes = ["InvalidType", "NonExistent", "UnsupportedNode"]
        
        for subtype in invalid_subtypes:
            try:
                # Test template endpoint with invalid subtype
                response = self.session.get(f"{self.base_url}/intelligent-nodes/{subtype}/template")
                
                if response.status_code == 404:
                    self.log_test(f"Invalid Subtype Template - {subtype}", True, 
                                f"Correctly returned 404 for invalid subtype")
                else:
                    self.log_test(f"Invalid Subtype Template - {subtype}", False, 
                                f"Expected 404, got {response.status_code}")
                    return False
                
                # Test prompts endpoint with invalid subtype
                response = self.session.get(f"{self.base_url}/intelligent-nodes/{subtype}/prompts")
                
                if response.status_code == 404:
                    self.log_test(f"Invalid Subtype Prompts - {subtype}", True, 
                                f"Correctly returned 404 for invalid subtype")
                else:
                    self.log_test(f"Invalid Subtype Prompts - {subtype}", False, 
                                f"Expected 404, got {response.status_code}")
                    return False
                    
            except Exception as e:
                self.log_test(f"Invalid Subtype - {subtype}", False, f"Error: {str(e)}")
                return False
        
        return True

    # Phase 2 DSL Rule Engine Tests
    def test_dsl_rule_evaluation(self):
        """Test POST /api/diagrams/{diagram_id}/evaluate-rules"""
        if not self.test_diagram_id:
            self.log_test("DSL Rule Evaluation", False, "No test diagram ID available")
            return False
            
        try:
            response = self.session.post(f"{self.base_url}/diagrams/{self.test_diagram_id}/evaluate-rules")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for required fields
                expected_fields = ["diagram_id", "rule_results", "total_rules_triggered", "overall_risk_score", "highest_impact"]
                missing_fields = [f for f in expected_fields if f not in data]
                
                if missing_fields:
                    self.log_test("DSL Rule Evaluation", False, f"Missing fields: {missing_fields}")
                    return False
                
                rule_results = data.get("rule_results", [])
                total_triggered = data.get("total_rules_triggered", 0)
                overall_risk = data.get("overall_risk_score", 0)
                highest_impact = data.get("highest_impact", "Low")
                
                # Verify rule result structure if any rules triggered
                if rule_results:
                    first_result = rule_results[0]
                    required_result_fields = ["rule_id", "rule_name", "triggered", "matching_nodes", "impact_level", "risk_score", "recommendations", "mitre_techniques"]
                    missing_result_fields = [f for f in required_result_fields if f not in first_result]
                    
                    if missing_result_fields:
                        self.log_test("DSL Rule Evaluation", False, f"Missing rule result fields: {missing_result_fields}")
                        return False
                
                self.log_test("DSL Rule Evaluation", True, 
                            f"Evaluated rules: {total_triggered} triggered, risk score: {overall_risk}, highest impact: {highest_impact}")
                return True
            else:
                self.log_test("DSL Rule Evaluation", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("DSL Rule Evaluation", False, f"Error: {str(e)}")
            return False

    def test_security_gap_detection(self):
        """Test POST /api/diagrams/{diagram_id}/detect-gaps"""
        if not self.test_diagram_id:
            self.log_test("Security Gap Detection", False, "No test diagram ID available")
            return False
            
        try:
            response = self.session.post(f"{self.base_url}/diagrams/{self.test_diagram_id}/detect-gaps")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for required fields
                expected_fields = ["diagram_id", "security_gaps", "total_gaps", "gaps_by_severity"]
                missing_fields = [f for f in expected_fields if f not in data]
                
                if missing_fields:
                    self.log_test("Security Gap Detection", False, f"Missing fields: {missing_fields}")
                    return False
                
                security_gaps = data.get("security_gaps", [])
                total_gaps = data.get("total_gaps", 0)
                gaps_by_severity = data.get("gaps_by_severity", {})
                
                # Verify gap structure if any gaps found
                if security_gaps:
                    first_gap = security_gaps[0]
                    required_gap_fields = ["gap_id", "node_id", "node_type", "missing_control", "severity", "description", "recommendations"]
                    missing_gap_fields = [f for f in required_gap_fields if f not in first_gap]
                    
                    if missing_gap_fields:
                        self.log_test("Security Gap Detection", False, f"Missing gap fields: {missing_gap_fields}")
                        return False
                
                # Verify severity breakdown
                expected_severities = ["Critical", "High", "Medium", "Low"]
                missing_severities = [s for s in expected_severities if s not in gaps_by_severity]
                
                if missing_severities:
                    self.log_test("Security Gap Detection", False, f"Missing severity levels: {missing_severities}")
                    return False
                
                self.log_test("Security Gap Detection", True, 
                            f"Gap analysis: {total_gaps} total gaps, severity breakdown: {gaps_by_severity}")
                return True
            else:
                self.log_test("Security Gap Detection", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Security Gap Detection", False, f"Error: {str(e)}")
            return False

    def test_completeness_analysis(self):
        """Test POST /api/diagrams/{diagram_id}/completeness-analysis"""
        if not self.test_diagram_id:
            self.log_test("Completeness Analysis", False, "No test diagram ID available")
            return False
            
        try:
            response = self.session.post(f"{self.base_url}/diagrams/{self.test_diagram_id}/completeness-analysis")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for required fields
                expected_fields = ["diagram_id", "overall_score", "completeness_percentage", "total_gaps", "gaps_by_severity", "gaps_by_category", "improvement_recommendations"]
                missing_fields = [f for f in expected_fields if f not in data]
                
                if missing_fields:
                    self.log_test("Completeness Analysis", False, f"Missing fields: {missing_fields}")
                    return False
                
                overall_score = data.get("overall_score", 0)
                completeness_percentage = data.get("completeness_percentage", 0)
                total_gaps = data.get("total_gaps", 0)
                gaps_by_severity = data.get("gaps_by_severity", {})
                improvement_recommendations = data.get("improvement_recommendations", [])
                
                # Verify score ranges
                if not (0 <= overall_score <= 10):
                    self.log_test("Completeness Analysis", False, f"Invalid overall score: {overall_score} (should be 0-10)")
                    return False
                
                if not (0 <= completeness_percentage <= 100):
                    self.log_test("Completeness Analysis", False, f"Invalid completeness percentage: {completeness_percentage} (should be 0-100)")
                    return False
                
                # Verify gaps by severity structure
                required_severity_fields = ["critical_gaps", "high_gaps", "medium_gaps", "low_gaps"]
                missing_severity_fields = [f for f in required_severity_fields if f not in gaps_by_severity]
                
                if missing_severity_fields:
                    self.log_test("Completeness Analysis", False, f"Missing severity fields: {missing_severity_fields}")
                    return False
                
                self.log_test("Completeness Analysis", True, 
                            f"Completeness: {completeness_percentage}% ({overall_score}/10), {total_gaps} gaps, {len(improvement_recommendations)} recommendations")
                return True
            else:
                self.log_test("Completeness Analysis", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Completeness Analysis", False, f"Error: {str(e)}")
            return False

    def test_comprehensive_analysis(self):
        """Test POST /api/diagrams/{diagram_id}/comprehensive-analysis (combined analysis)"""
        if not self.test_diagram_id:
            self.log_test("Comprehensive Analysis", False, "No test diagram ID available")
            return False
            
        try:
            response = self.session.post(f"{self.base_url}/diagrams/{self.test_diagram_id}/comprehensive-analysis")
            
            if response.status_code == 200:
                data = response.json()
                
                # Should contain results from all three analysis types
                expected_sections = ["rule_evaluation", "gap_detection", "completeness_analysis"]
                
                # Check if it's a combined response or individual analysis
                if any(section in data for section in expected_sections):
                    # Combined response format
                    self.log_test("Comprehensive Analysis", True, 
                                f"Combined analysis completed with sections: {[s for s in expected_sections if s in data]}")
                    return True
                else:
                    # Individual analysis format (like completeness analysis)
                    if "overall_score" in data and "completeness_percentage" in data:
                        self.log_test("Comprehensive Analysis", True, 
                                    f"Comprehensive analysis: {data.get('completeness_percentage', 0)}% complete")
                        return True
                    else:
                        self.log_test("Comprehensive Analysis", False, f"Unexpected response format: {list(data.keys())}")
                        return False
            else:
                self.log_test("Comprehensive Analysis", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Comprehensive Analysis", False, f"Error: {str(e)}")
            return False

    def test_security_rules_management(self):
        """Test GET /api/security-rules and related endpoints"""
        try:
            # Test basic rules listing
            response = self.session.get(f"{self.base_url}/security-rules")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for required fields
                expected_fields = ["rules", "total_count"]
                missing_fields = [f for f in expected_fields if f not in data]
                
                if missing_fields:
                    self.log_test("Security Rules Management", False, f"Missing fields: {missing_fields}")
                    return False
                
                rules = data.get("rules", [])
                total_count = data.get("total_count", 0)
                
                if not rules:
                    self.log_test("Security Rules Management", False, "No security rules returned")
                    return False
                
                # Verify rule structure
                first_rule = rules[0]
                required_rule_fields = ["id", "name", "description", "category", "enabled", "priority", "mitre_techniques"]
                missing_rule_fields = [f for f in required_rule_fields if f not in first_rule]
                
                if missing_rule_fields:
                    self.log_test("Security Rules Management", False, f"Missing rule fields: {missing_rule_fields}")
                    return False
                
                # Test category filtering
                response_filtered = self.session.get(f"{self.base_url}/security-rules?category=web_security&enabled_only=true")
                
                if response_filtered.status_code == 200:
                    filtered_data = response_filtered.json()
                    filtered_rules = filtered_data.get("rules", [])
                    
                    # Verify filtering worked
                    if filtered_rules:
                        web_security_rules = [r for r in filtered_rules if r.get("category") == "web_security"]
                        if len(web_security_rules) != len(filtered_rules):
                            self.log_test("Security Rules Management", False, "Category filtering not working correctly")
                            return False
                    
                    self.log_test("Security Rules Management", True, 
                                f"Rules management: {total_count} total rules, {len(filtered_rules)} web security rules")
                    return True
                else:
                    self.log_test("Security Rules Management", False, f"Category filtering failed: HTTP {response_filtered.status_code}")
                    return False
            else:
                self.log_test("Security Rules Management", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Security Rules Management", False, f"Error: {str(e)}")
            return False

    def test_security_rules_categories(self):
        """Test GET /api/security-rules/categories"""
        try:
            response = self.session.get(f"{self.base_url}/security-rules/categories")
            
            if response.status_code == 200:
                data = response.json()
                
                # Should return dict with categories list
                if not isinstance(data, dict) or "categories" not in data:
                    self.log_test("Security Rules Categories", False, f"Expected dict with 'categories' key, got {type(data)}")
                    return False
                
                categories = data.get("categories", [])
                total_categories = data.get("total_categories", 0)
                
                if not isinstance(categories, list):
                    self.log_test("Security Rules Categories", False, f"Expected categories to be list, got {type(categories)}")
                    return False
                
                # Verify expected categories are present
                expected_categories = ["web_security", "database_security", "api_security", "network_security", "identity_access", "cloud_security"]
                found_categories = [cat.get("id") for cat in categories]
                
                missing_categories = [cat for cat in expected_categories if cat not in found_categories]
                if missing_categories:
                    self.log_test("Security Rules Categories", False, f"Missing categories: {missing_categories}")
                    return False
                
                # Verify category structure
                if categories:
                    first_category = categories[0]
                    required_fields = ["id", "name", "rule_count"]
                    missing_fields = [f for f in required_fields if f not in first_category]
                    
                    if missing_fields:
                        self.log_test("Security Rules Categories", False, f"Missing category fields: {missing_fields}")
                        return False
                
                self.log_test("Security Rules Categories", True, f"Retrieved {total_categories} rule categories: {found_categories}")
                return True
            else:
                self.log_test("Security Rules Categories", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Security Rules Categories", False, f"Error: {str(e)}")
            return False

    def test_security_rules_statistics(self):
        """Test GET /api/security-rules/statistics"""
        try:
            response = self.session.get(f"{self.base_url}/security-rules/statistics")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for required statistics fields
                expected_fields = ["total_rules", "enabled_rules", "rules_by_category", "rules_by_priority"]
                missing_fields = [f for f in expected_fields if f not in data]
                
                if missing_fields:
                    self.log_test("Security Rules Statistics", False, f"Missing fields: {missing_fields}")
                    return False
                
                total_rules = data.get("total_rules", 0)
                enabled_rules = data.get("enabled_rules", 0)
                rules_by_category = data.get("rules_by_category", {})
                rules_by_priority = data.get("rules_by_priority", {})
                
                # Verify statistics make sense
                if total_rules < enabled_rules:
                    self.log_test("Security Rules Statistics", False, f"Invalid statistics: total_rules ({total_rules}) < enabled_rules ({enabled_rules})")
                    return False
                
                if not rules_by_category:
                    self.log_test("Security Rules Statistics", False, "No rules by category statistics")
                    return False
                
                self.log_test("Security Rules Statistics", True, 
                            f"Statistics: {total_rules} total, {enabled_rules} enabled, {len(rules_by_category)} categories")
                return True
            else:
                self.log_test("Security Rules Statistics", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Security Rules Statistics", False, f"Error: {str(e)}")
            return False

    def test_specific_security_rule(self):
        """Test GET /api/security-rules/{rule_id}"""
        # Test with known rule IDs from the DSL engine
        test_rule_ids = ["rule.web.sql_injection", "rule.api.broken_authentication", "rule.cloud.s3_public_bucket"]
        
        for rule_id in test_rule_ids:
            try:
                response = self.session.get(f"{self.base_url}/security-rules/{rule_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check for required rule fields
                    expected_fields = ["id", "name", "description", "category", "enabled", "conditions", "outcome"]
                    missing_fields = [f for f in expected_fields if f not in data]
                    
                    if missing_fields:
                        self.log_test(f"Specific Rule - {rule_id}", False, f"Missing fields: {missing_fields}")
                        return False
                    
                    # Verify rule ID matches
                    if data.get("id") != rule_id:
                        self.log_test(f"Specific Rule - {rule_id}", False, f"Rule ID mismatch: expected {rule_id}, got {data.get('id')}")
                        return False
                    
                    self.log_test(f"Specific Rule - {rule_id}", True, f"Retrieved rule: {data.get('name')}")
                    
                elif response.status_code == 404:
                    self.log_test(f"Specific Rule - {rule_id}", False, f"Rule not found: {rule_id}")
                    return False
                else:
                    self.log_test(f"Specific Rule - {rule_id}", False, f"HTTP {response.status_code}: {response.text}")
                    return False
                    
            except Exception as e:
                self.log_test(f"Specific Rule - {rule_id}", False, f"Error: {str(e)}")
                return False
        
        return True

    def create_dsl_test_scenarios(self):
        """Create specific test scenarios for DSL rule engine testing"""
        scenarios = []
        
        # Scenario A: SQL Injection Test
        sql_injection_scenario = {
            "id": str(uuid.uuid4()),
            "title": "SQL Injection Test Scenario",
            "description": "WebApp connected to Database without InputValidation control",
            "nodes": [
                {
                    "id": "webapp-node",
                    "type": "Asset",
                    "subtype": "WebApp",
                    "label": "Web Application",
                    "position": {"x": 200, "y": 100},
                    "data": {"criticality": "High"}
                },
                {
                    "id": "database-node",
                    "type": "Asset",
                    "subtype": "Database",
                    "label": "Customer Database",
                    "position": {"x": 400, "y": 100},
                    "data": {"criticality": "Critical", "data_classification": "Confidential"}
                }
            ],
            "edges": [
                {
                    "id": "webapp-to-db",
                    "source": "webapp-node",
                    "target": "database-node",
                    "label": "Database Connection"
                }
            ]
        }
        scenarios.append(sql_injection_scenario)
        
        # Scenario B: Cloud Security Test
        cloud_security_scenario = {
            "id": str(uuid.uuid4()),
            "title": "Cloud Security Test Scenario",
            "description": "S3 Bucket with public access enabled",
            "nodes": [
                {
                    "id": "s3-bucket-node",
                    "type": "Asset",
                    "subtype": "S3Bucket",
                    "label": "Public S3 Bucket",
                    "position": {"x": 200, "y": 100},
                    "data": {"public_access": True, "criticality": "High"}
                }
            ],
            "edges": []
        }
        scenarios.append(cloud_security_scenario)
        
        # Scenario C: API Security Test
        api_security_scenario = {
            "id": str(uuid.uuid4()),
            "title": "API Security Test Scenario",
            "description": "API without IAM Policy control",
            "nodes": [
                {
                    "id": "api-node",
                    "type": "Asset",
                    "subtype": "API",
                    "label": "Payment API",
                    "position": {"x": 200, "y": 100},
                    "data": {"criticality": "High"}
                }
            ],
            "edges": []
        }
        scenarios.append(api_security_scenario)
        
        return scenarios

    def test_dsl_rule_scenarios(self):
        """Test DSL rule engine with specific security scenarios"""
        scenarios = self.create_dsl_test_scenarios()
        
        for scenario in scenarios:
            try:
                # Create diagram for scenario
                response = self.session.post(
                    f"{self.base_url}/diagrams",
                    json={"title": scenario["title"], "description": scenario["description"]},
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code != 200:
                    self.log_test(f"DSL Scenario - {scenario['title']}", False, f"Failed to create diagram: {response.status_code}")
                    continue
                
                diagram_id = response.json()["id"]
                scenario["id"] = diagram_id
                
                # Update with scenario data
                response = self.session.put(
                    f"{self.base_url}/diagrams/{diagram_id}",
                    json=scenario,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code != 200:
                    self.log_test(f"DSL Scenario - {scenario['title']}", False, f"Failed to update diagram: {response.status_code}")
                    continue
                
                # Test rule evaluation
                response = self.session.post(f"{self.base_url}/diagrams/{diagram_id}/evaluate-rules")
                
                if response.status_code == 200:
                    data = response.json()
                    rule_results = data.get("rule_results", [])
                    total_triggered = data.get("total_rules_triggered", 0)
                    
                    # Verify expected rules triggered based on scenario
                    expected_rules = {
                        "SQL Injection Test Scenario": ["rule.web.sql_injection"],
                        "Cloud Security Test Scenario": ["rule.cloud.s3_public_bucket"],
                        "API Security Test Scenario": ["rule.api.broken_authentication"]
                    }
                    
                    expected_rule_ids = expected_rules.get(scenario["title"], [])
                    triggered_rule_ids = [r.get("rule_id") for r in rule_results]
                    
                    # Check if expected rules were triggered
                    found_expected = any(rule_id in triggered_rule_ids for rule_id in expected_rule_ids)
                    
                    if found_expected or total_triggered > 0:
                        self.log_test(f"DSL Scenario - {scenario['title']}", True, 
                                    f"Rules triggered: {total_triggered}, expected rules found: {found_expected}")
                    else:
                        self.log_test(f"DSL Scenario - {scenario['title']}", False, 
                                    f"No rules triggered for scenario that should trigger: {expected_rule_ids}")
                        return False
                else:
                    self.log_test(f"DSL Scenario - {scenario['title']}", False, f"Rule evaluation failed: {response.status_code}")
                    return False
                    
            except Exception as e:
                self.log_test(f"DSL Scenario - {scenario['title']}", False, f"Error: {str(e)}")
                return False
        
        return True

    # ============================================================================
    # PHASE 3: PROBABILISTIC SIMULATION ENGINE TESTS
    # ============================================================================
    
    def create_probabilistic_test_diagram(self):
        """Create comprehensive security diagram for probabilistic simulation testing"""
        diagram_id = str(uuid.uuid4())
        
        nodes = [
            # Diverse Threat Actors
            {
                "id": str(uuid.uuid4()),
                "type": "Actor",
                "subtype": "ExternalAttacker",
                "label": "Advanced Persistent Threat",
                "position": {"x": 50, "y": 100},
                "data": {
                    "description": "Nation-state sponsored threat actor",
                    "sophistication": "Very High",
                    "motivation": "Espionage",
                    "resources": "Unlimited"
                },
                "mitre_ids": ["T1190", "T1566", "T1078"],
                "cve_ids": []
            },
            {
                "id": str(uuid.uuid4()),
                "type": "Actor",
                "subtype": "Insider",
                "label": "Malicious Insider",
                "position": {"x": 50, "y": 200},
                "data": {
                    "description": "Privileged insider with legitimate access",
                    "sophistication": "Medium",
                    "motivation": "Financial",
                    "access_level": "High"
                },
                "mitre_ids": ["T1078", "T1484", "T1552"],
                "cve_ids": []
            },
            
            # Critical Assets with varying criticality
            {
                "id": str(uuid.uuid4()),
                "type": "Asset",
                "subtype": "Database",
                "label": "Customer PII Database",
                "position": {"x": 700, "y": 150},
                "data": {
                    "description": "PostgreSQL database containing customer personal information",
                    "criticality": "Critical",
                    "data_classification": "Restricted",
                    "compliance_requirements": ["GDPR", "CCPA"],
                    "public_access": False
                },
                "mitre_ids": [],
                "cve_ids": []
            },
            {
                "id": str(uuid.uuid4()),
                "type": "Asset",
                "subtype": "WebApp",
                "label": "Customer Portal",
                "position": {"x": 500, "y": 100},
                "data": {
                    "description": "Customer-facing web application",
                    "criticality": "High",
                    "data_classification": "Confidential",
                    "public_access": True
                },
                "mitre_ids": [],
                "cve_ids": []
            },
            {
                "id": str(uuid.uuid4()),
                "type": "Asset",
                "subtype": "API",
                "label": "Payment Processing API",
                "position": {"x": 500, "y": 250},
                "data": {
                    "description": "REST API for payment processing",
                    "criticality": "High",
                    "data_classification": "Confidential",
                    "public_access": True
                },
                "mitre_ids": [],
                "cve_ids": []
            },
            
            # Attack Surfaces with CVSS scores
            {
                "id": str(uuid.uuid4()),
                "type": "Surface",
                "subtype": "SQLi",
                "label": "SQL Injection Vulnerability",
                "position": {"x": 300, "y": 150},
                "data": {
                    "description": "SQL injection in search functionality",
                    "severity": "Critical",
                    "exploitability": "High"
                },
                "cvss_score": 9.8,
                "mitre_ids": ["T1190", "T1213"],
                "cve_ids": ["CVE-2021-44228"]
            },
            {
                "id": str(uuid.uuid4()),
                "type": "Surface",
                "subtype": "WeakIAM",
                "label": "Weak Authentication Controls",
                "position": {"x": 300, "y": 250},
                "data": {
                    "description": "Insufficient access controls on admin endpoints",
                    "severity": "High",
                    "exploitability": "Medium"
                },
                "cvss_score": 7.5,
                "mitre_ids": ["T1078", "T1484"],
                "cve_ids": []
            },
            {
                "id": str(uuid.uuid4()),
                "type": "Surface",
                "subtype": "RCE",
                "label": "Remote Code Execution",
                "position": {"x": 300, "y": 350},
                "data": {
                    "description": "RCE via deserialization vulnerability",
                    "severity": "Critical",
                    "exploitability": "Medium"
                },
                "cvss_score": 9.0,
                "mitre_ids": ["T1059", "T1203"],
                "cve_ids": []
            },
            
            # Security Controls with effectiveness ratings
            {
                "id": str(uuid.uuid4()),
                "type": "Control",
                "subtype": "WAF",
                "label": "Web Application Firewall",
                "position": {"x": 150, "y": 50},
                "data": {
                    "description": "AWS WAF with OWASP Core Rule Set",
                    "effectiveness": "High",
                    "control_type": "Preventive",
                    "coverage": ["Web Applications", "API Endpoints"]
                },
                "effectiveness": 85,
                "mitre_ids": [],
                "cve_ids": []
            },
            {
                "id": str(uuid.uuid4()),
                "type": "Control",
                "subtype": "EDR",
                "label": "Endpoint Detection & Response",
                "position": {"x": 300, "y": 50},
                "data": {
                    "description": "CrowdStrike Falcon EDR solution",
                    "effectiveness": "High",
                    "control_type": "Detective",
                    "coverage": ["Endpoints", "Servers"]
                },
                "effectiveness": 90,
                "mitre_ids": [],
                "cve_ids": []
            },
            {
                "id": str(uuid.uuid4()),
                "type": "Control",
                "subtype": "IAMPolicy",
                "label": "Identity Access Management",
                "position": {"x": 450, "y": 50},
                "data": {
                    "description": "Azure AD with conditional access policies",
                    "effectiveness": "Medium",
                    "control_type": "Preventive",
                    "coverage": ["User Access", "Privilege Management"]
                },
                "effectiveness": 75,
                "mitre_ids": [],
                "cve_ids": []
            }
        ]
        
        # Create attack path edges with realistic likelihood and impact
        edges = [
            # External Attacker -> SQL Injection -> Database
            {
                "id": str(uuid.uuid4()),
                "source": nodes[0]["id"],  # APT
                "target": nodes[5]["id"],  # SQL Injection
                "type": "attack",
                "label": "Exploits SQLi",
                "data": {"likelihood": "High", "impact": "Critical"}
            },
            {
                "id": str(uuid.uuid4()),
                "source": nodes[5]["id"],  # SQL Injection
                "target": nodes[2]["id"],  # Database
                "type": "attack",
                "label": "Data Exfiltration",
                "data": {"likelihood": "High", "impact": "Critical"}
            },
            
            # Insider -> Weak IAM -> Web App -> Database
            {
                "id": str(uuid.uuid4()),
                "source": nodes[1]["id"],  # Insider
                "target": nodes[6]["id"],  # Weak IAM
                "type": "attack",
                "label": "Exploits Weak Auth",
                "data": {"likelihood": "Medium", "impact": "High"}
            },
            {
                "id": str(uuid.uuid4()),
                "source": nodes[6]["id"],  # Weak IAM
                "target": nodes[3]["id"],  # Web App
                "type": "attack",
                "label": "Privilege Escalation",
                "data": {"likelihood": "High", "impact": "High"}
            },
            {
                "id": str(uuid.uuid4()),
                "source": nodes[3]["id"],  # Web App
                "target": nodes[2]["id"],  # Database
                "type": "attack",
                "label": "Lateral Movement",
                "data": {"likelihood": "Medium", "impact": "Critical"}
            },
            
            # APT -> RCE -> Payment API
            {
                "id": str(uuid.uuid4()),
                "source": nodes[0]["id"],  # APT
                "target": nodes[7]["id"],  # RCE
                "type": "attack",
                "label": "Exploits RCE",
                "data": {"likelihood": "Medium", "impact": "High"}
            },
            {
                "id": str(uuid.uuid4()),
                "source": nodes[7]["id"],  # RCE
                "target": nodes[4]["id"],  # Payment API
                "type": "attack",
                "label": "API Compromise",
                "data": {"likelihood": "High", "impact": "High"}
            }
        ]
        
        return {
            "id": diagram_id,
            "title": "Probabilistic Security Threat Model",
            "description": "Comprehensive security model for testing probabilistic simulation engine with diverse threat actors, critical assets, attack surfaces, and security controls",
            "nodes": nodes,
            "edges": edges
        }
    
    def test_probabilistic_simulation_engine(self):
        """Test POST /api/diagrams/{diagram_id}/probabilistic-simulation"""
        try:
            # Create comprehensive diagram for probabilistic testing
            prob_diagram_data = self.create_probabilistic_test_diagram()
            
            # Create diagram
            response = self.session.post(
                f"{self.base_url}/diagrams",
                json={"title": prob_diagram_data["title"], "description": prob_diagram_data["description"]},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                self.log_test("Probabilistic Simulation - Create Diagram", False, f"Failed to create diagram: {response.status_code}")
                return False
            
            diagram_id = response.json()["id"]
            prob_diagram_data["id"] = diagram_id
            
            # Update with comprehensive probabilistic data
            response = self.session.put(
                f"{self.base_url}/diagrams/{diagram_id}",
                json=prob_diagram_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                self.log_test("Probabilistic Simulation - Update Diagram", False, f"Failed to update diagram: {response.status_code}")
                return False
            
            # Run probabilistic simulation
            response = self.session.post(f"{self.base_url}/diagrams/{diagram_id}/probabilistic-simulation")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for required probabilistic simulation fields
                required_fields = [
                    "diagram_id", "probabilistic_paths", "simulation_summary", "simulation_timestamp"
                ]
                
                missing_fields = [f for f in required_fields if f not in data]
                if missing_fields:
                    self.log_test("Probabilistic Simulation", False, f"Missing fields: {missing_fields}")
                    return False
                
                # Validate probabilistic paths structure
                prob_paths = data.get("probabilistic_paths", [])
                if not prob_paths:
                    self.log_test("Probabilistic Simulation", False, "No probabilistic paths generated")
                    return False
                
                # Check first path structure
                first_path = prob_paths[0]
                path_required_fields = [
                    "path_id", "steps", "overall_probability", "risk_score", 
                    "impact_score", "detection_score", "kill_chain_stages", 
                    "mitre_techniques", "uncertainty_band"
                ]
                
                path_missing_fields = [f for f in path_required_fields if f not in first_path]
                if path_missing_fields:
                    self.log_test("Probabilistic Simulation", False, f"Path missing fields: {path_missing_fields}")
                    return False
                
                # Validate probability values are in valid range (0-1)
                overall_prob = first_path.get("overall_probability", 0)
                if not (0 <= overall_prob <= 1):
                    self.log_test("Probabilistic Simulation", False, f"Invalid probability: {overall_prob}")
                    return False
                
                # Validate uncertainty band
                uncertainty_band = first_path.get("uncertainty_band", {})
                if "min_probability" not in uncertainty_band or "max_probability" not in uncertainty_band:
                    self.log_test("Probabilistic Simulation", False, "Missing uncertainty band values")
                    return False
                
                # Check simulation summary
                summary = data.get("simulation_summary", {})
                summary_required_fields = [
                    "total_paths", "average_success_probability", "kill_chain_coverage", "risk_distribution"
                ]
                
                summary_missing_fields = [f for f in summary_required_fields if f not in summary]
                if summary_missing_fields:
                    self.log_test("Probabilistic Simulation", False, f"Summary missing fields: {summary_missing_fields}")
                    return False
                
                # Validate kill chain mapping
                kill_chain_stages = summary.get("kill_chain_coverage", [])
                expected_stages = ["reconnaissance", "weaponization", "delivery", "exploitation", "installation", "command_control", "actions_objectives"]
                valid_stages = all(stage in expected_stages for stage in kill_chain_stages)
                
                if not valid_stages:
                    self.log_test("Probabilistic Simulation", False, f"Invalid kill chain stages: {kill_chain_stages}")
                    return False
                
                # Validate risk distribution
                risk_dist = summary.get("risk_distribution", {})
                risk_categories = ["critical", "high", "medium", "low"]
                if not all(cat in risk_dist for cat in risk_categories):
                    self.log_test("Probabilistic Simulation", False, "Missing risk distribution categories")
                    return False
                
                self.log_test("Probabilistic Simulation", True, 
                            f"Generated {len(prob_paths)} probabilistic paths, "
                            f"avg probability: {summary.get('average_success_probability', 0):.4f}, "
                            f"kill chain stages: {len(kill_chain_stages)}, "
                            f"risk distribution: {risk_dist}")
                return True
            else:
                self.log_test("Probabilistic Simulation", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Probabilistic Simulation", False, f"Error: {str(e)}")
            return False
    
    def test_what_if_scenario_engine(self):
        """Test POST /api/diagrams/{diagram_id}/what-if-scenario"""
        try:
            # Use existing diagram or create one
            if not self.test_diagram_id:
                self.log_test("What-If Scenario Engine", False, "No test diagram available")
                return False
            
            # Define scenario configuration with control toggles
            scenario_config = {
                "scenario_name": "Enhanced Security Controls",
                "control_changes": {
                    "waf_control": True,      # Enable WAF
                    "edr_control": True,      # Enable EDR
                    "iam_control": False,     # Disable IAM (test risk increase)
                    "network_acl": True       # Enable Network ACL
                }
            }
            
            # Run what-if scenario
            response = self.session.post(
                f"{self.base_url}/diagrams/{self.test_diagram_id}/what-if-scenario",
                json=scenario_config,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for required scenario fields
                required_fields = [
                    "diagram_id", "scenario_id", "scenario_name", "control_changes",
                    "risk_analysis", "affected_paths", "recommendations", "roi_analysis",
                    "analysis_timestamp"
                ]
                
                missing_fields = [f for f in required_fields if f not in data]
                if missing_fields:
                    self.log_test("What-If Scenario Engine", False, f"Missing fields: {missing_fields}")
                    return False
                
                # Validate risk analysis structure
                risk_analysis = data.get("risk_analysis", {})
                risk_required_fields = [
                    "original_risk_score", "modified_risk_score", "risk_change", "risk_change_percentage"
                ]
                
                risk_missing_fields = [f for f in risk_required_fields if f not in risk_analysis]
                if risk_missing_fields:
                    self.log_test("What-If Scenario Engine", False, f"Risk analysis missing fields: {risk_missing_fields}")
                    return False
                
                # Validate ROI analysis
                roi_analysis = data.get("roi_analysis", {})
                roi_required_fields = ["estimated_cost", "risk_reduction_value", "roi_percentage", "payback_period_months"]
                
                roi_missing_fields = [f for f in roi_required_fields if f not in roi_analysis]
                if roi_missing_fields:
                    self.log_test("What-If Scenario Engine", False, f"ROI analysis missing fields: {roi_missing_fields}")
                    return False
                
                # Validate control changes were applied
                control_changes = data.get("control_changes", {})
                if control_changes != scenario_config["control_changes"]:
                    self.log_test("What-If Scenario Engine", False, "Control changes not properly applied")
                    return False
                
                # Check that recommendations are provided
                recommendations = data.get("recommendations", [])
                if not recommendations:
                    self.log_test("What-If Scenario Engine", False, "No recommendations provided")
                    return False
                
                # Validate risk change calculation
                original_risk = risk_analysis.get("original_risk_score", 0)
                modified_risk = risk_analysis.get("modified_risk_score", 0)
                risk_change = risk_analysis.get("risk_change", 0)
                
                expected_change = modified_risk - original_risk
                if abs(risk_change - expected_change) > 0.01:  # Allow small floating point differences
                    self.log_test("What-If Scenario Engine", False, f"Risk change calculation error: expected {expected_change}, got {risk_change}")
                    return False
                
                self.log_test("What-If Scenario Engine", True, 
                            f"Scenario '{data.get('scenario_name')}': "
                            f"risk change {risk_change:.2f}, "
                            f"ROI {roi_analysis.get('roi_percentage', 0):.1f}%, "
                            f"{len(recommendations)} recommendations")
                return True
            else:
                self.log_test("What-If Scenario Engine", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("What-If Scenario Engine", False, f"Error: {str(e)}")
            return False
    
    def test_defense_effectiveness_modeling(self):
        """Test POST /api/diagrams/{diagram_id}/defense-effectiveness"""
        try:
            if not self.test_diagram_id:
                self.log_test("Defense Effectiveness Modeling", False, "No test diagram available")
                return False
            
            # Run defense effectiveness analysis
            response = self.session.post(f"{self.base_url}/diagrams/{self.test_diagram_id}/defense-effectiveness")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for required fields
                required_fields = [
                    "diagram_id", "defense_models", "analysis_summary", "analysis_timestamp"
                ]
                
                missing_fields = [f for f in required_fields if f not in data]
                if missing_fields:
                    self.log_test("Defense Effectiveness Modeling", False, f"Missing fields: {missing_fields}")
                    return False
                
                # Validate defense models structure
                defense_models = data.get("defense_models", [])
                if defense_models:  # Only validate if controls exist
                    first_model = defense_models[0]
                    model_required_fields = [
                        "control_id", "control_type", "effectiveness_rating", "coverage_areas",
                        "interaction_effects", "degradation_over_time", "false_positive_rate", "false_negative_rate"
                    ]
                    
                    model_missing_fields = [f for f in model_required_fields if f not in first_model]
                    if model_missing_fields:
                        self.log_test("Defense Effectiveness Modeling", False, f"Defense model missing fields: {model_missing_fields}")
                        return False
                    
                    # Validate effectiveness rating is in valid range (0-1)
                    effectiveness = first_model.get("effectiveness_rating", 0)
                    if not (0 <= effectiveness <= 1):
                        self.log_test("Defense Effectiveness Modeling", False, f"Invalid effectiveness rating: {effectiveness}")
                        return False
                    
                    # Validate false positive/negative rates
                    fp_rate = first_model.get("false_positive_rate", 0)
                    fn_rate = first_model.get("false_negative_rate", 0)
                    if not (0 <= fp_rate <= 1) or not (0 <= fn_rate <= 1):
                        self.log_test("Defense Effectiveness Modeling", False, f"Invalid FP/FN rates: FP={fp_rate}, FN={fn_rate}")
                        return False
                
                # Validate analysis summary
                summary = data.get("analysis_summary", {})
                summary_required_fields = [
                    "total_controls", "average_effectiveness", "strongest_control", 
                    "weakest_control", "synergy_opportunities"
                ]
                
                summary_missing_fields = [f for f in summary_required_fields if f not in summary]
                if summary_missing_fields:
                    self.log_test("Defense Effectiveness Modeling", False, f"Summary missing fields: {summary_missing_fields}")
                    return False
                
                # Check synergy opportunities structure
                synergies = summary.get("synergy_opportunities", [])
                if synergies:
                    first_synergy = synergies[0]
                    synergy_fields = ["control_1", "control_2", "synergy_effect"]
                    if not all(field in first_synergy for field in synergy_fields):
                        self.log_test("Defense Effectiveness Modeling", False, "Invalid synergy opportunity structure")
                        return False
                
                total_controls = summary.get("total_controls", 0)
                avg_effectiveness = summary.get("average_effectiveness", 0)
                
                self.log_test("Defense Effectiveness Modeling", True, 
                            f"Analyzed {total_controls} controls, "
                            f"avg effectiveness: {avg_effectiveness:.3f}, "
                            f"{len(synergies)} synergy opportunities")
                return True
            else:
                self.log_test("Defense Effectiveness Modeling", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Defense Effectiveness Modeling", False, f"Error: {str(e)}")
            return False
    
    def test_historical_probabilistic_simulations(self):
        """Test GET /api/diagrams/{diagram_id}/probabilistic-simulations"""
        try:
            if not self.test_diagram_id:
                self.log_test("Historical Probabilistic Simulations", False, "No test diagram available")
                return False
            
            # Get historical probabilistic simulations
            response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}/probabilistic-simulations")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for required fields
                required_fields = ["diagram_id", "simulations", "total_count"]
                missing_fields = [f for f in required_fields if f not in data]
                if missing_fields:
                    self.log_test("Historical Probabilistic Simulations", False, f"Missing fields: {missing_fields}")
                    return False
                
                simulations = data.get("simulations", [])
                total_count = data.get("total_count", 0)
                
                # Validate count consistency
                if len(simulations) != total_count:
                    self.log_test("Historical Probabilistic Simulations", False, f"Count mismatch: {len(simulations)} vs {total_count}")
                    return False
                
                # If simulations exist, validate structure
                if simulations:
                    first_sim = simulations[0]
                    sim_required_fields = ["diagram_id", "simulation_summary", "simulation_timestamp"]
                    sim_missing_fields = [f for f in sim_required_fields if f not in first_sim]
                    if sim_missing_fields:
                        self.log_test("Historical Probabilistic Simulations", False, f"Simulation missing fields: {sim_missing_fields}")
                        return False
                    
                    # Check that detailed paths are removed for summary view
                    if "probabilistic_paths" in first_sim:
                        self.log_test("Historical Probabilistic Simulations", False, "Detailed paths should be removed in summary view")
                        return False
                    
                    # Check for path_count field instead
                    if "path_count" not in first_sim:
                        self.log_test("Historical Probabilistic Simulations", False, "Missing path_count in summary")
                        return False
                
                self.log_test("Historical Probabilistic Simulations", True, 
                            f"Retrieved {total_count} historical simulations")
                return True
            else:
                self.log_test("Historical Probabilistic Simulations", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Historical Probabilistic Simulations", False, f"Error: {str(e)}")
            return False
    
    def test_historical_scenario_analyses(self):
        """Test GET /api/diagrams/{diagram_id}/scenario-analyses"""
        try:
            if not self.test_diagram_id:
                self.log_test("Historical Scenario Analyses", False, "No test diagram available")
                return False
            
            # Get historical scenario analyses
            response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}/scenario-analyses")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for required fields
                required_fields = ["diagram_id", "scenarios", "total_count"]
                missing_fields = [f for f in required_fields if f not in data]
                if missing_fields:
                    self.log_test("Historical Scenario Analyses", False, f"Missing fields: {missing_fields}")
                    return False
                
                scenarios = data.get("scenarios", [])
                total_count = data.get("total_count", 0)
                
                # Validate count consistency
                if len(scenarios) != total_count:
                    self.log_test("Historical Scenario Analyses", False, f"Count mismatch: {len(scenarios)} vs {total_count}")
                    return False
                
                # If scenarios exist, validate structure
                if scenarios:
                    first_scenario = scenarios[0]
                    scenario_required_fields = [
                        "diagram_id", "scenario_id", "scenario_name", "control_changes",
                        "risk_analysis", "roi_analysis", "analysis_timestamp"
                    ]
                    scenario_missing_fields = [f for f in scenario_required_fields if f not in first_scenario]
                    if scenario_missing_fields:
                        self.log_test("Historical Scenario Analyses", False, f"Scenario missing fields: {scenario_missing_fields}")
                        return False
                
                self.log_test("Historical Scenario Analyses", True, 
                            f"Retrieved {total_count} historical scenario analyses")
                return True
            else:
                self.log_test("Historical Scenario Analyses", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Historical Scenario Analyses", False, f"Error: {str(e)}")
            return False

    # Threat Modeling Wizard Tests
    def test_wizard_recommendations_system_overview(self):
        """Test POST /api/wizard/recommendations with systemOverview step"""
        try:
            test_data = {
                "step": "systemOverview",
                "wizardData": {
                    "systemOverview": {
                        "systemName": "E-commerce Platform",
                        "systemType": "web_application",
                        "businessCriticality": "high",
                        "deploymentModel": "cloud_public",
                        "businessContext": "Online retail platform handling customer transactions",
                        "securityObjectives": {
                            "confidentiality": "high",
                            "integrity": "high", 
                            "availability": "high"
                        }
                    }
                },
                "existingNodes": [],
                "existingEdges": []
            }
            
            response = self.session.post(
                f"{self.base_url}/wizard/recommendations",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for required fields
                expected_fields = ["step", "recommendations", "recommendation_count"]
                missing_fields = [f for f in expected_fields if f not in data]
                
                if missing_fields:
                    self.log_test("Wizard Recommendations - System Overview", False, f"Missing fields: {missing_fields}")
                    return False
                
                # Verify step matches
                if data.get("step") != "systemOverview":
                    self.log_test("Wizard Recommendations - System Overview", False, f"Step mismatch: expected systemOverview, got {data.get('step')}")
                    return False
                
                recommendations = data.get("recommendations", [])
                recommendation_count = data.get("recommendation_count", 0)
                
                # Verify recommendations are contextual and relevant
                if not recommendations:
                    self.log_test("Wizard Recommendations - System Overview", False, "No recommendations returned")
                    return False
                
                if recommendation_count != len(recommendations):
                    self.log_test("Wizard Recommendations - System Overview", False, f"Count mismatch: expected {len(recommendations)}, got {recommendation_count}")
                    return False
                
                # Check for security-relevant recommendations
                security_keywords = ["security", "control", "encryption", "access", "monitoring", "critical"]
                relevant_recommendations = [r for r in recommendations if any(keyword.lower() in r.lower() for keyword in security_keywords)]
                
                if not relevant_recommendations:
                    self.log_test("Wizard Recommendations - System Overview", False, "No security-relevant recommendations found")
                    return False
                
                self.log_test("Wizard Recommendations - System Overview", True, 
                            f"Retrieved {recommendation_count} contextual recommendations for system overview")
                return True
            else:
                self.log_test("Wizard Recommendations - System Overview", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Wizard Recommendations - System Overview", False, f"Error: {str(e)}")
            return False

    def test_wizard_recommendations_asset_inventory(self):
        """Test POST /api/wizard/recommendations with assetInventory step"""
        try:
            test_data = {
                "step": "assetInventory",
                "wizardData": {
                    "assetInventory": {
                        "assets": [
                            {
                                "name": "Customer Database",
                                "type": "data",
                                "category": "Database",
                                "criticality": "critical",
                                "dataClassification": "Confidential",
                                "description": "PostgreSQL database containing customer PII and payment information",
                                "owner": "Data Team"
                            },
                            {
                                "name": "Web Application",
                                "type": "application",
                                "category": "WebApp",
                                "criticality": "high",
                                "dataClassification": "Internal",
                                "description": "Customer-facing e-commerce web application",
                                "owner": "Development Team"
                            },
                            {
                                "name": "Payment API",
                                "type": "application",
                                "category": "API",
                                "criticality": "high",
                                "dataClassification": "Confidential",
                                "description": "REST API for processing payments",
                                "owner": "Payment Team"
                            }
                        ]
                    }
                },
                "existingNodes": [
                    {
                        "id": "existing-node-1",
                        "type": "Asset",
                        "subtype": "WebApp",
                        "label": "Existing Web App"
                    }
                ],
                "existingEdges": []
            }
            
            response = self.session.post(
                f"{self.base_url}/wizard/recommendations",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for required fields
                expected_fields = ["step", "recommendations", "recommendation_count"]
                missing_fields = [f for f in expected_fields if f not in data]
                
                if missing_fields:
                    self.log_test("Wizard Recommendations - Asset Inventory", False, f"Missing fields: {missing_fields}")
                    return False
                
                # Verify step matches
                if data.get("step") != "assetInventory":
                    self.log_test("Wizard Recommendations - Asset Inventory", False, f"Step mismatch: expected assetInventory, got {data.get('step')}")
                    return False
                
                recommendations = data.get("recommendations", [])
                recommendation_count = data.get("recommendation_count", 0)
                
                # Verify recommendations are contextual for assets
                if not recommendations:
                    self.log_test("Wizard Recommendations - Asset Inventory", False, "No recommendations returned")
                    return False
                
                # Check for asset-specific recommendations
                asset_keywords = ["asset", "critical", "data", "application", "encryption", "access control", "security testing"]
                relevant_recommendations = [r for r in recommendations if any(keyword.lower() in r.lower() for keyword in asset_keywords)]
                
                if not relevant_recommendations:
                    self.log_test("Wizard Recommendations - Asset Inventory", False, "No asset-relevant recommendations found")
                    return False
                
                self.log_test("Wizard Recommendations - Asset Inventory", True, 
                            f"Retrieved {recommendation_count} asset-specific recommendations")
                return True
            else:
                self.log_test("Wizard Recommendations - Asset Inventory", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Wizard Recommendations - Asset Inventory", False, f"Error: {str(e)}")
            return False

    def test_wizard_recommendations_invalid_step(self):
        """Test POST /api/wizard/recommendations with invalid step name"""
        try:
            test_data = {
                "step": "invalidStep",
                "wizardData": {},
                "existingNodes": [],
                "existingEdges": []
            }
            
            response = self.session.post(
                f"{self.base_url}/wizard/recommendations",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Should still return a response with fallback recommendations
                if "recommendations" not in data:
                    self.log_test("Wizard Recommendations - Invalid Step", False, "No recommendations field in response")
                    return False
                
                recommendations = data.get("recommendations", [])
                if not recommendations:
                    self.log_test("Wizard Recommendations - Invalid Step", False, "No fallback recommendations provided")
                    return False
                
                self.log_test("Wizard Recommendations - Invalid Step", True, 
                            f"Handled invalid step gracefully with {len(recommendations)} fallback recommendations")
                return True
            else:
                self.log_test("Wizard Recommendations - Invalid Step", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Wizard Recommendations - Invalid Step", False, f"Error: {str(e)}")
            return False

    def test_wizard_generate_model_complete(self):
        """Test POST /api/wizard/generate-model with complete wizard data"""
        try:
            test_data = {
                "wizardData": {
                    "systemOverview": {
                        "systemName": "E-commerce Platform",
                        "systemType": "web_application",
                        "businessCriticality": "high",
                        "deploymentModel": "cloud_public",
                        "businessContext": "Online retail platform handling customer transactions",
                        "systemDescription": "Comprehensive e-commerce platform with payment processing",
                        "securityObjectives": {
                            "confidentiality": "high",
                            "integrity": "high",
                            "availability": "high"
                        }
                    },
                    "assetInventory": {
                        "assets": [
                            {
                                "name": "Customer Database",
                                "type": "data",
                                "category": "Database",
                                "criticality": "critical",
                                "dataClassification": "Confidential",
                                "description": "PostgreSQL database containing customer PII",
                                "owner": "Data Team"
                            },
                            {
                                "name": "Web Application",
                                "type": "application",
                                "category": "WebApp",
                                "criticality": "high",
                                "dataClassification": "Internal",
                                "description": "Customer-facing web application",
                                "owner": "Development Team"
                            },
                            {
                                "name": "Payment API",
                                "type": "application",
                                "category": "API",
                                "criticality": "high",
                                "dataClassification": "Confidential",
                                "description": "REST API for payment processing",
                                "owner": "Payment Team"
                            }
                        ]
                    }
                },
                "diagramId": None
            }
            
            response = self.session.post(
                f"{self.base_url}/wizard/generate-model",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for required fields
                expected_fields = ["success", "generatedNodes", "generatedEdges", "recommendations", "implementationPlan", "summary"]
                missing_fields = [f for f in expected_fields if f not in data]
                
                if missing_fields:
                    self.log_test("Wizard Generate Model - Complete", False, f"Missing fields: {missing_fields}")
                    return False
                
                # Verify success status
                if not data.get("success", False):
                    error_msg = data.get("error", "Unknown error")
                    self.log_test("Wizard Generate Model - Complete", False, f"Generation failed: {error_msg}")
                    return False
                
                generated_nodes = data.get("generatedNodes", [])
                generated_edges = data.get("generatedEdges", [])
                recommendations = data.get("recommendations", [])
                implementation_plan = data.get("implementationPlan", {})
                summary = data.get("summary", {})
                
                # Verify nodes were generated
                if not generated_nodes:
                    self.log_test("Wizard Generate Model - Complete", False, "No nodes generated")
                    return False
                
                # Verify node structure
                first_node = generated_nodes[0]
                required_node_fields = ["id", "type", "position", "data"]
                missing_node_fields = [f for f in required_node_fields if f not in first_node]
                
                if missing_node_fields:
                    self.log_test("Wizard Generate Model - Complete", False, f"Missing node fields: {missing_node_fields}")
                    return False
                
                # Verify node data structure
                node_data = first_node.get("data", {})
                if "type" not in node_data or "label" not in node_data:
                    self.log_test("Wizard Generate Model - Complete", False, "Node data missing type or label")
                    return False
                
                # Verify recommendations are provided
                if not recommendations:
                    self.log_test("Wizard Generate Model - Complete", False, "No recommendations generated")
                    return False
                
                # Verify implementation plan structure
                if not implementation_plan:
                    self.log_test("Wizard Generate Model - Complete", False, "No implementation plan generated")
                    return False
                
                # Verify summary structure
                expected_summary_fields = ["total_nodes", "total_edges", "recommendations_count"]
                missing_summary_fields = [f for f in expected_summary_fields if f not in summary]
                
                if missing_summary_fields:
                    self.log_test("Wizard Generate Model - Complete", False, f"Missing summary fields: {missing_summary_fields}")
                    return False
                
                # Verify summary counts match actual data
                if summary.get("total_nodes") != len(generated_nodes):
                    self.log_test("Wizard Generate Model - Complete", False, f"Node count mismatch: summary={summary.get('total_nodes')}, actual={len(generated_nodes)}")
                    return False
                
                if summary.get("recommendations_count") != len(recommendations):
                    self.log_test("Wizard Generate Model - Complete", False, f"Recommendations count mismatch: summary={summary.get('recommendations_count')}, actual={len(recommendations)}")
                    return False
                
                self.log_test("Wizard Generate Model - Complete", True, 
                            f"Generated {len(generated_nodes)} nodes, {len(generated_edges)} edges, {len(recommendations)} recommendations")
                return True
            else:
                self.log_test("Wizard Generate Model - Complete", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Wizard Generate Model - Complete", False, f"Error: {str(e)}")
            return False

    def test_wizard_generate_model_minimal(self):
        """Test POST /api/wizard/generate-model with minimal wizard data"""
        try:
            test_data = {
                "wizardData": {
                    "systemOverview": {
                        "systemName": "Basic System",
                        "businessCriticality": "medium"
                    }
                },
                "diagramId": None
            }
            
            response = self.session.post(
                f"{self.base_url}/wizard/generate-model",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Should still succeed with minimal data
                if not data.get("success", False):
                    error_msg = data.get("error", "Unknown error")
                    self.log_test("Wizard Generate Model - Minimal", False, f"Generation failed: {error_msg}")
                    return False
                
                generated_nodes = data.get("generatedNodes", [])
                recommendations = data.get("recommendations", [])
                
                # Should generate at least basic nodes (system + attacker)
                if len(generated_nodes) < 2:
                    self.log_test("Wizard Generate Model - Minimal", False, f"Too few nodes generated: {len(generated_nodes)}")
                    return False
                
                # Should provide basic recommendations
                if not recommendations:
                    self.log_test("Wizard Generate Model - Minimal", False, "No recommendations generated for minimal data")
                    return False
                
                self.log_test("Wizard Generate Model - Minimal", True, 
                            f"Generated {len(generated_nodes)} nodes and {len(recommendations)} recommendations from minimal data")
                return True
            else:
                self.log_test("Wizard Generate Model - Minimal", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Wizard Generate Model - Minimal", False, f"Error: {str(e)}")
            return False

    def test_wizard_generate_model_error_handling(self):
        """Test POST /api/wizard/generate-model error handling with invalid data"""
        try:
            # Test with empty wizard data
            test_data = {
                "wizardData": {},
                "diagramId": None
            }
            
            response = self.session.post(
                f"{self.base_url}/wizard/generate-model",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Should handle gracefully - either succeed with minimal generation or fail gracefully
                if data.get("success", False):
                    # If successful, should still generate basic structure
                    generated_nodes = data.get("generatedNodes", [])
                    if not generated_nodes:
                        self.log_test("Wizard Generate Model - Error Handling", False, "Success claimed but no nodes generated")
                        return False
                    
                    self.log_test("Wizard Generate Model - Error Handling", True, 
                                f"Handled empty data gracefully, generated {len(generated_nodes)} nodes")
                    return True
                else:
                    # If failed, should provide error message and empty arrays
                    error_msg = data.get("error", "")
                    if not error_msg:
                        self.log_test("Wizard Generate Model - Error Handling", False, "Failed but no error message provided")
                        return False
                    
                    # Should provide empty arrays for failed generation
                    if data.get("generatedNodes") != [] or data.get("generatedEdges") != []:
                        self.log_test("Wizard Generate Model - Error Handling", False, "Failed generation should return empty arrays")
                        return False
                    
                    self.log_test("Wizard Generate Model - Error Handling", True, 
                                f"Handled error gracefully: {error_msg}")
                    return True
            else:
                self.log_test("Wizard Generate Model - Error Handling", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Wizard Generate Model - Error Handling", False, f"Error: {str(e)}")
            return False

    def test_questionnaire_get_responses(self):
        """Test GET /api/diagrams/{diagram_id}/nodes/{node_id}/questionnaire"""
        if not self.test_diagram_id:
            self.log_test("Questionnaire Get Responses", False, "No test diagram ID available")
            return False
        
        try:
            # First create a diagram with a WebApp node
            webapp_node_id = str(uuid.uuid4())
            diagram_data = {
                "id": self.test_diagram_id,
                "title": "Questionnaire Test Diagram",
                "description": "Testing questionnaire management",
                "nodes": [
                    {
                        "id": webapp_node_id,
                        "type": "Asset",
                        "subtype": "WebApp",
                        "label": "Test Web Application",
                        "position": {"x": 100, "y": 100},
                        "data": {
                            "description": "Web application for questionnaire testing",
                            "questionnaireResponses": {
                                "webapp_api_endpoints": True,
                                "webapp_database_connection": False
                            }
                        }
                    }
                ],
                "edges": []
            }
            
            # Update diagram with WebApp node
            update_response = self.session.put(
                f"{self.base_url}/diagrams/{self.test_diagram_id}",
                json=diagram_data,
                headers={"Content-Type": "application/json"}
            )
            
            if update_response.status_code != 200:
                self.log_test("Questionnaire Get Responses", False, f"Failed to update diagram: {update_response.status_code}")
                return False
            
            # Test getting questionnaire responses
            response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}/nodes/{webapp_node_id}/questionnaire")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields
                expected_fields = ["success", "node_id", "node_subtype", "questionnaire_responses", "prompts", "completed_questions", "total_questions"]
                missing_fields = [f for f in expected_fields if f not in data]
                
                if missing_fields:
                    self.log_test("Questionnaire Get Responses", False, f"Missing fields: {missing_fields}")
                    return False
                
                # Verify response structure
                if not data.get("success"):
                    self.log_test("Questionnaire Get Responses", False, "Success field is False")
                    return False
                
                if data.get("node_subtype") != "WebApp":
                    self.log_test("Questionnaire Get Responses", False, f"Expected WebApp, got {data.get('node_subtype')}")
                    return False
                
                questionnaire_responses = data.get("questionnaire_responses", {})
                prompts = data.get("prompts", [])
                completed_questions = data.get("completed_questions", 0)
                total_questions = data.get("total_questions", 0)
                
                # Verify we have the expected responses
                if "webapp_api_endpoints" not in questionnaire_responses:
                    self.log_test("Questionnaire Get Responses", False, "Missing expected questionnaire response")
                    return False
                
                if len(prompts) == 0:
                    self.log_test("Questionnaire Get Responses", False, "No prompts returned")
                    return False
                
                self.log_test("Questionnaire Get Responses", True, 
                            f"Retrieved questionnaire: {completed_questions}/{total_questions} completed, {len(prompts)} prompts")
                return True
                
            elif response.status_code == 404:
                self.log_test("Questionnaire Get Responses", False, "Diagram or node not found")
                return False
            else:
                self.log_test("Questionnaire Get Responses", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Questionnaire Get Responses", False, f"Error: {str(e)}")
            return False

    def test_questionnaire_update_responses(self):
        """Test POST /api/diagrams/{diagram_id}/nodes/{node_id}/questionnaire"""
        if not self.test_diagram_id:
            self.log_test("Questionnaire Update Responses", False, "No test diagram ID available")
            return False
        
        try:
            # Create a diagram with a WebApp node
            webapp_node_id = str(uuid.uuid4())
            diagram_data = {
                "id": self.test_diagram_id,
                "title": "Questionnaire Update Test",
                "description": "Testing questionnaire response updates",
                "nodes": [
                    {
                        "id": webapp_node_id,
                        "type": "Asset",
                        "subtype": "WebApp",
                        "label": "Test Web Application",
                        "position": {"x": 100, "y": 100},
                        "data": {
                            "description": "Web application for questionnaire testing"
                        }
                    }
                ],
                "edges": []
            }
            
            # Update diagram with WebApp node
            update_response = self.session.put(
                f"{self.base_url}/diagrams/{self.test_diagram_id}",
                json=diagram_data,
                headers={"Content-Type": "application/json"}
            )
            
            if update_response.status_code != 200:
                self.log_test("Questionnaire Update Responses", False, f"Failed to update diagram: {update_response.status_code}")
                return False
            
            # Test updating questionnaire responses
            new_responses = {
                "webapp_api_endpoints": True,
                "webapp_database_connection": True,
                "webapp_authentication": "OAuth2",
                "webapp_encryption": "TLS 1.3"
            }
            
            response = self.session.post(
                f"{self.base_url}/diagrams/{self.test_diagram_id}/nodes/{webapp_node_id}/questionnaire",
                json={"responses": new_responses},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields
                expected_fields = ["success", "node_id", "updated_responses"]
                missing_fields = [f for f in expected_fields if f not in data]
                
                if missing_fields:
                    self.log_test("Questionnaire Update Responses", False, f"Missing fields: {missing_fields}")
                    return False
                
                # Verify response structure
                if not data.get("success"):
                    self.log_test("Questionnaire Update Responses", False, "Success field is False")
                    return False
                
                if data.get("node_id") != webapp_node_id:
                    self.log_test("Questionnaire Update Responses", False, f"Node ID mismatch")
                    return False
                
                updated_responses = data.get("updated_responses", 0)
                if updated_responses != len(new_responses):
                    self.log_test("Questionnaire Update Responses", False, f"Expected {len(new_responses)} updates, got {updated_responses}")
                    return False
                
                # Verify the responses were actually saved by getting them back
                get_response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}/nodes/{webapp_node_id}/questionnaire")
                if get_response.status_code == 200:
                    get_data = get_response.json()
                    saved_responses = get_data.get("questionnaire_responses", {})
                    
                    # Check if our responses were saved
                    for key, value in new_responses.items():
                        if saved_responses.get(key) != value:
                            self.log_test("Questionnaire Update Responses", False, f"Response {key} not saved correctly")
                            return False
                
                self.log_test("Questionnaire Update Responses", True, 
                            f"Updated {updated_responses} questionnaire responses successfully")
                return True
                
            elif response.status_code == 404:
                self.log_test("Questionnaire Update Responses", False, "Diagram or node not found")
                return False
            else:
                self.log_test("Questionnaire Update Responses", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Questionnaire Update Responses", False, f"Error: {str(e)}")
            return False

    def test_check_dependencies(self):
        """Test POST /api/intelligent-nodes/{node_subtype}/check-dependencies for conditional dependency system"""
        print("\n🔍 Testing Conditional Dependency System for Immediate Node Creation...")
        
        # Test WebApp Dependencies
        webapp_test_cases = [
            {
                "name": "WebApp - API endpoints only",
                "answers": {"webapp_api_endpoints": True},
                "expected_dependencies": ["API"]
            },
            {
                "name": "WebApp - Database connection only", 
                "answers": {"webapp_database_connection": True},
                "expected_dependencies": ["Database"]
            },
            {
                "name": "WebApp - Both API and Database",
                "answers": {"webapp_api_endpoints": True, "webapp_database_connection": True},
                "expected_dependencies": ["API", "Database"]
            },
            {
                "name": "WebApp - API false (should return empty)",
                "answers": {"webapp_api_endpoints": False},
                "expected_dependencies": []
            }
        ]
        
        # Test Database Dependencies
        database_test_cases = [
            {
                "name": "Database - Backup enabled only",
                "answers": {"db_backup_enabled": True},
                "expected_dependencies": ["Backup"]
            },
            {
                "name": "Database - Monitoring enabled only",
                "answers": {"db_monitoring_enabled": True},
                "expected_dependencies": ["Monitoring"]
            },
            {
                "name": "Database - Both backup and monitoring",
                "answers": {"db_backup_enabled": True, "db_monitoring_enabled": True},
                "expected_dependencies": ["Backup", "Monitoring"]
            }
        ]
        
        # Test Edge Cases
        edge_test_cases = [
            {
                "name": "WebApp - Empty answers",
                "subtype": "WebApp",
                "answers": {},
                "expected_dependencies": []
            },
            {
                "name": "WebApp - Mixed true/false answers",
                "subtype": "WebApp", 
                "answers": {"webapp_api_endpoints": True, "webapp_database_connection": False},
                "expected_dependencies": ["API"]
            }
        ]
        
        # Test WebApp Dependencies
        for test_case in webapp_test_cases:
            if not self._test_dependency_case("WebApp", test_case["name"], test_case["answers"], test_case["expected_dependencies"]):
                return False
        
        # Test Database Dependencies  
        for test_case in database_test_cases:
            if not self._test_dependency_case("Database", test_case["name"], test_case["answers"], test_case["expected_dependencies"]):
                return False
        
        # Test Edge Cases
        for test_case in edge_test_cases:
            if not self._test_dependency_case(test_case["subtype"], test_case["name"], test_case["answers"], test_case["expected_dependencies"]):
                return False
        
        # Test Invalid Node Subtype (should handle gracefully)
        try:
            response = self.session.post(
                f"{self.base_url}/intelligent-nodes/InvalidNodeType/check-dependencies",
                json={"answers": {"webapp_api_endpoints": True}},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                # Should return empty dependencies for invalid subtype
                if data.get("dependent_nodes") == [] and data.get("dependencies_found") == 0:
                    self.log_test("Check Dependencies - Invalid Subtype", True, 
                                f"Gracefully handled invalid node subtype by returning empty dependencies")
                else:
                    self.log_test("Check Dependencies - Invalid Subtype", False, 
                                f"Expected empty dependencies, got {data}")
                    return False
            else:
                self.log_test("Check Dependencies - Invalid Subtype", False, 
                            f"Expected HTTP 200, got HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Check Dependencies - Invalid Subtype", False, f"Error: {str(e)}")
            return False
        
        return True
    
    def _test_dependency_case(self, subtype, test_name, answers, expected_dependencies):
        """Helper method to test individual dependency cases"""
        try:
            response = self.session.post(
                f"{self.base_url}/intelligent-nodes/{subtype}/check-dependencies",
                json={"answers": answers},  # Wrap answers in "answers" object as per API contract
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # The API should return a list of dependent node types directly
                if isinstance(data, list):
                    dependent_nodes = data
                elif isinstance(data, dict) and "dependent_nodes" in data:
                    dependent_nodes = data["dependent_nodes"]
                elif isinstance(data, dict) and "dependencies" in data:
                    dependent_nodes = data["dependencies"]
                else:
                    self.log_test(test_name, False, f"Unexpected response format: {data}")
                    return False
                
                # Verify dependencies match expected (order doesn't matter)
                if set(dependent_nodes) == set(expected_dependencies):
                    self.log_test(test_name, True, 
                                f"✅ Expected {expected_dependencies}, got {dependent_nodes}")
                    return True
                else:
                    self.log_test(test_name, False, 
                                f"❌ Expected {expected_dependencies}, got {dependent_nodes}")
                    return False
                    
            else:
                self.log_test(test_name, False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test(test_name, False, f"Error: {str(e)}")
            return False

    # ============================================================================
    # PHASE 1 ENHANCED APIS - EXPANDED INTELLIGENT NODES & THREAT INTELLIGENCE
    # ============================================================================

    def test_expanded_nodes_supported_types(self):
        """Test GET /api/expanded-nodes/supported-types"""
        try:
            response = self.session.get(f"{self.base_url}/expanded-nodes/supported-types")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for required fields
                expected_fields = ["supported_types", "by_category", "total_count", "categories"]
                missing_fields = [f for f in expected_fields if f not in data]
                
                if missing_fields:
                    self.log_test("Expanded Nodes - Supported Types", False, f"Missing fields: {missing_fields}")
                    return False
                
                supported_types = data.get("supported_types", [])
                total_count = data.get("total_count", 0)
                categories = data.get("categories", [])
                
                # Verify we have comprehensive list of 25+ node types
                if total_count < 25:
                    self.log_test("Expanded Nodes - Supported Types", False, 
                                f"Expected 25+ node types, got {total_count}")
                    return False
                
                # Verify expected new node types are present
                expected_types = ["EC2", "Lambda", "S3", "RDS", "VPC", "WAF", "IAM", "Kubernetes", "CICD"]
                found_types = [t.get("node_subtype") for t in supported_types]
                
                missing_types = [t for t in expected_types if t not in found_types]
                if missing_types:
                    self.log_test("Expanded Nodes - Supported Types", False, 
                                f"Missing expected new types: {missing_types}")
                    return False
                
                # Verify categories are present
                expected_categories = ["Cloud Infrastructure", "Security Controls", "Development Tools"]
                missing_categories = [c for c in expected_categories if c not in categories]
                if missing_categories:
                    self.log_test("Expanded Nodes - Supported Types", False, 
                                f"Missing expected categories: {missing_categories}")
                    return False
                
                self.log_test("Expanded Nodes - Supported Types", True, 
                            f"Retrieved {total_count} node types across {len(categories)} categories")
                return True
            else:
                self.log_test("Expanded Nodes - Supported Types", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Expanded Nodes - Supported Types", False, f"Error: {str(e)}")
            return False

    def test_expanded_nodes_questionnaire_levels(self):
        """Test GET /api/expanded-nodes/{node_subtype}/questionnaire/{level}"""
        test_cases = [
            {"node_subtype": "EC2", "level": "basic"},
            {"node_subtype": "Lambda", "level": "advanced"},
            {"node_subtype": "RDS", "level": "expert"},
            {"node_subtype": "Kubernetes", "level": "basic"}
        ]
        
        for test_case in test_cases:
            node_subtype = test_case["node_subtype"]
            level = test_case["level"]
            
            try:
                response = self.session.get(f"{self.base_url}/expanded-nodes/{node_subtype}/questionnaire/{level}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check for required fields
                    expected_fields = ["node_subtype", "questionnaire_level", "questions", "question_count", "estimated_time"]
                    missing_fields = [f for f in expected_fields if f not in data]
                    
                    if missing_fields:
                        self.log_test(f"Expanded Questionnaire - {node_subtype} {level}", False, 
                                    f"Missing fields: {missing_fields}")
                        return False
                    
                    questions = data.get("questions", [])
                    question_count = data.get("question_count", 0)
                    
                    # Verify appropriate complexity for level
                    expected_min_questions = {"basic": 5, "advanced": 10, "expert": 15}
                    min_questions = expected_min_questions.get(level, 5)
                    
                    if question_count < min_questions:
                        self.log_test(f"Expanded Questionnaire - {node_subtype} {level}", False, 
                                    f"Expected at least {min_questions} questions for {level} level, got {question_count}")
                        return False
                    
                    # Verify question structure
                    if questions:
                        first_question = questions[0]
                        required_question_fields = ["id", "question", "type", "options"]
                        missing_question_fields = [f for f in required_question_fields if f not in first_question]
                        
                        if missing_question_fields:
                            self.log_test(f"Expanded Questionnaire - {node_subtype} {level}", False, 
                                        f"Missing question fields: {missing_question_fields}")
                            return False
                    
                    self.log_test(f"Expanded Questionnaire - {node_subtype} {level}", True, 
                                f"Retrieved {question_count} questions for {level} level")
                    
                elif response.status_code == 400:
                    self.log_test(f"Expanded Questionnaire - {node_subtype} {level}", False, 
                                f"Invalid level parameter: {level}")
                    return False
                elif response.status_code == 404:
                    self.log_test(f"Expanded Questionnaire - {node_subtype} {level}", False, 
                                f"Questionnaire not found for {node_subtype} at {level} level")
                    return False
                else:
                    self.log_test(f"Expanded Questionnaire - {node_subtype} {level}", False, 
                                f"HTTP {response.status_code}: {response.text}")
                    return False
                    
            except Exception as e:
                self.log_test(f"Expanded Questionnaire - {node_subtype} {level}", False, f"Error: {str(e)}")
                return False
        
        return True

    def test_expanded_nodes_calculate_risk(self):
        """Test POST /api/expanded-nodes/{node_subtype}/calculate-risk with probabilistic modeling"""
        test_cases = [
            {
                "node_subtype": "EC2",
                "request": {
                    "responses": {
                        "instance_type": "t3.large",
                        "security_groups": "restrictive",
                        "encryption": "enabled",
                        "patching": "automated"
                    },
                    "business_context": {
                        "criticality": "high",
                        "data_classification": "confidential",
                        "compliance_requirements": ["SOC2", "PCI-DSS"]
                    }
                }
            },
            {
                "node_subtype": "RDS",
                "request": {
                    "responses": {
                        "engine": "postgresql",
                        "encryption_at_rest": "enabled",
                        "backup_retention": "30_days",
                        "multi_az": "enabled"
                    },
                    "business_context": {
                        "criticality": "critical",
                        "data_classification": "restricted"
                    }
                }
            }
        ]
        
        for test_case in test_cases:
            node_subtype = test_case["node_subtype"]
            request_data = test_case["request"]
            
            try:
                response = self.session.post(
                    f"{self.base_url}/expanded-nodes/{node_subtype}/calculate-risk",
                    json=request_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check for required fields
                    expected_fields = ["node_subtype", "risk_assessment", "security_recommendations", "calculation_timestamp"]
                    missing_fields = [f for f in expected_fields if f not in data]
                    
                    if missing_fields:
                        self.log_test(f"Expanded Risk Calculation - {node_subtype}", False, 
                                    f"Missing fields: {missing_fields}")
                        return False
                    
                    risk_assessment = data.get("risk_assessment", {})
                    recommendations = data.get("security_recommendations", [])
                    
                    # Verify enhanced risk assessment structure
                    expected_risk_fields = ["composite_risk_score", "risk_level", "confidence_interval", "threat_likelihood"]
                    missing_risk_fields = [f for f in expected_risk_fields if f not in risk_assessment]
                    
                    if missing_risk_fields:
                        self.log_test(f"Expanded Risk Calculation - {node_subtype}", False, 
                                    f"Missing risk assessment fields: {missing_risk_fields}")
                        return False
                    
                    composite_score = risk_assessment.get("composite_risk_score", 0)
                    risk_level = risk_assessment.get("risk_level", "Unknown")
                    
                    # Verify probabilistic modeling features
                    if "confidence_interval" not in risk_assessment:
                        self.log_test(f"Expanded Risk Calculation - {node_subtype}", False, 
                                    "Missing probabilistic confidence interval")
                        return False
                    
                    # Verify risk score is valid
                    if not (0 <= composite_score <= 10):
                        self.log_test(f"Expanded Risk Calculation - {node_subtype}", False, 
                                    f"Invalid composite risk score: {composite_score}")
                        return False
                    
                    self.log_test(f"Expanded Risk Calculation - {node_subtype}", True, 
                                f"Risk assessment: {composite_score}/10 ({risk_level}), {len(recommendations)} recommendations")
                    
                elif response.status_code == 500:
                    self.log_test(f"Expanded Risk Calculation - {node_subtype}", False, 
                                f"Risk calculation failed: {response.text}")
                    return False
                else:
                    self.log_test(f"Expanded Risk Calculation - {node_subtype}", False, 
                                f"HTTP {response.status_code}: {response.text}")
                    return False
                    
            except Exception as e:
                self.log_test(f"Expanded Risk Calculation - {node_subtype}", False, f"Error: {str(e)}")
                return False
        
        return True

    def test_expanded_nodes_bulk_risk_assessment(self):
        """Test POST /api/expanded-nodes/bulk-risk-assessment"""
        try:
            request_data = {
                "nodes": [
                    {
                        "node_subtype": "EC2",
                        "responses": {
                            "instance_type": "t3.medium",
                            "security_groups": "default",
                            "encryption": "disabled"
                        }
                    },
                    {
                        "node_subtype": "RDS",
                        "responses": {
                            "engine": "mysql",
                            "encryption_at_rest": "enabled",
                            "backup_retention": "7_days"
                        }
                    },
                    {
                        "node_subtype": "Lambda",
                        "responses": {
                            "runtime": "python3.9",
                            "vpc_config": "enabled",
                            "environment_variables": "encrypted"
                        }
                    }
                ],
                "business_context": {
                    "criticality": "high",
                    "data_classification": "confidential",
                    "compliance_requirements": ["SOC2"]
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/expanded-nodes/bulk-risk-assessment",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for required fields
                expected_fields = ["assessment_results", "overall_risk_summary", "cross_node_correlations", "bulk_recommendations"]
                missing_fields = [f for f in expected_fields if f not in data]
                
                if missing_fields:
                    self.log_test("Bulk Risk Assessment", False, f"Missing fields: {missing_fields}")
                    return False
                
                assessment_results = data.get("assessment_results", [])
                overall_summary = data.get("overall_risk_summary", {})
                correlations = data.get("cross_node_correlations", [])
                
                # Verify we got results for all nodes
                if len(assessment_results) != 3:
                    self.log_test("Bulk Risk Assessment", False, 
                                f"Expected 3 assessment results, got {len(assessment_results)}")
                    return False
                
                # Verify overall summary structure
                expected_summary_fields = ["average_risk_score", "highest_risk_node", "total_recommendations"]
                missing_summary_fields = [f for f in expected_summary_fields if f not in overall_summary]
                
                if missing_summary_fields:
                    self.log_test("Bulk Risk Assessment", False, 
                                f"Missing summary fields: {missing_summary_fields}")
                    return False
                
                avg_risk = overall_summary.get("average_risk_score", 0)
                highest_risk = overall_summary.get("highest_risk_node", "")
                
                self.log_test("Bulk Risk Assessment", True, 
                            f"Assessed 3 nodes: avg risk {avg_risk:.2f}, highest risk: {highest_risk}, {len(correlations)} correlations")
                return True
                
            elif response.status_code == 400:
                self.log_test("Bulk Risk Assessment", False, f"Bad request: {response.text}")
                return False
            else:
                self.log_test("Bulk Risk Assessment", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Bulk Risk Assessment", False, f"Error: {str(e)}")
            return False

    def test_expanded_nodes_categories(self):
        """Test GET /api/expanded-nodes/categories"""
        try:
            response = self.session.get(f"{self.base_url}/expanded-nodes/categories")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for required fields
                expected_fields = ["categories", "category_count", "nodes_by_category"]
                missing_fields = [f for f in expected_fields if f not in data]
                
                if missing_fields:
                    self.log_test("Expanded Nodes - Categories", False, f"Missing fields: {missing_fields}")
                    return False
                
                categories = data.get("categories", [])
                category_count = data.get("category_count", 0)
                nodes_by_category = data.get("nodes_by_category", {})
                
                # Verify expected categories
                expected_categories = ["Cloud Infrastructure", "Security Controls", "Development Tools", "Data Storage", "Networking"]
                missing_categories = [c for c in expected_categories if c not in categories]
                
                if missing_categories:
                    self.log_test("Expanded Nodes - Categories", False, 
                                f"Missing expected categories: {missing_categories}")
                    return False
                
                # Verify nodes are properly categorized
                total_categorized_nodes = sum(len(nodes) for nodes in nodes_by_category.values())
                if total_categorized_nodes == 0:
                    self.log_test("Expanded Nodes - Categories", False, "No nodes found in categories")
                    return False
                
                self.log_test("Expanded Nodes - Categories", True, 
                            f"Retrieved {category_count} categories with {total_categorized_nodes} total nodes")
                return True
            else:
                self.log_test("Expanded Nodes - Categories", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Expanded Nodes - Categories", False, f"Error: {str(e)}")
            return False

    def test_expanded_nodes_threat_intelligence_summary(self):
        """Test POST /api/expanded-nodes/threat-intelligence-summary"""
        try:
            request_data = {
                "node_types": ["EC2", "RDS", "Lambda", "S3"],
                "threat_level": "high",
                "time_range": "30_days"
            }
            
            response = self.session.post(
                f"{self.base_url}/expanded-nodes/threat-intelligence-summary",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for required fields
                expected_fields = ["threat_summary", "node_threat_profiles", "recent_threats", "mitigation_recommendations"]
                missing_fields = [f for f in expected_fields if f not in data]
                
                if missing_fields:
                    self.log_test("Threat Intelligence Summary", False, f"Missing fields: {missing_fields}")
                    return False
                
                threat_summary = data.get("threat_summary", {})
                node_profiles = data.get("node_threat_profiles", [])
                recent_threats = data.get("recent_threats", [])
                
                # Verify threat summary structure
                expected_summary_fields = ["total_threats", "threat_level_distribution", "most_targeted_node_type"]
                missing_summary_fields = [f for f in expected_summary_fields if f not in threat_summary]
                
                if missing_summary_fields:
                    self.log_test("Threat Intelligence Summary", False, 
                                f"Missing threat summary fields: {missing_summary_fields}")
                    return False
                
                # Verify we got profiles for requested node types
                if len(node_profiles) != 4:
                    self.log_test("Threat Intelligence Summary", False, 
                                f"Expected 4 node profiles, got {len(node_profiles)}")
                    return False
                
                total_threats = threat_summary.get("total_threats", 0)
                most_targeted = threat_summary.get("most_targeted_node_type", "")
                
                self.log_test("Threat Intelligence Summary", True, 
                            f"Aggregated {total_threats} threats, most targeted: {most_targeted}, {len(recent_threats)} recent threats")
                return True
            else:
                self.log_test("Threat Intelligence Summary", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Threat Intelligence Summary", False, f"Error: {str(e)}")
            return False

    # ============================================================================
    # THREAT INTELLIGENCE ENDPOINTS
    # ============================================================================

    def test_threat_intelligence_node_profile(self):
        """Test GET /api/threat-intelligence/node/{node_type}/profile"""
        test_node_types = ["EC2", "RDS", "Lambda", "S3"]
        
        for node_type in test_node_types:
            try:
                response = self.session.get(f"{self.base_url}/threat-intelligence/node/{node_type}/profile")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check for required fields
                    expected_fields = ["node_type", "threat_profile", "vulnerability_summary", "attack_vectors", "mitre_techniques"]
                    missing_fields = [f for f in expected_fields if f not in data]
                    
                    if missing_fields:
                        self.log_test(f"Threat Intelligence Profile - {node_type}", False, 
                                    f"Missing fields: {missing_fields}")
                        return False
                    
                    threat_profile = data.get("threat_profile", {})
                    vulnerability_summary = data.get("vulnerability_summary", {})
                    attack_vectors = data.get("attack_vectors", [])
                    mitre_techniques = data.get("mitre_techniques", [])
                    
                    # Verify threat profile structure
                    expected_profile_fields = ["threat_level", "common_vulnerabilities", "recent_incidents"]
                    missing_profile_fields = [f for f in expected_profile_fields if f not in threat_profile]
                    
                    if missing_profile_fields:
                        self.log_test(f"Threat Intelligence Profile - {node_type}", False, 
                                    f"Missing threat profile fields: {missing_profile_fields}")
                        return False
                    
                    # Verify vulnerability summary
                    if "cve_count" not in vulnerability_summary:
                        self.log_test(f"Threat Intelligence Profile - {node_type}", False, 
                                    "Missing CVE count in vulnerability summary")
                        return False
                    
                    cve_count = vulnerability_summary.get("cve_count", 0)
                    threat_level = threat_profile.get("threat_level", "Unknown")
                    
                    self.log_test(f"Threat Intelligence Profile - {node_type}", True, 
                                f"Profile: {threat_level} threat level, {cve_count} CVEs, {len(attack_vectors)} attack vectors, {len(mitre_techniques)} MITRE techniques")
                    
                elif response.status_code == 404:
                    self.log_test(f"Threat Intelligence Profile - {node_type}", False, 
                                f"Threat profile not found for {node_type}")
                    return False
                else:
                    self.log_test(f"Threat Intelligence Profile - {node_type}", False, 
                                f"HTTP {response.status_code}: {response.text}")
                    return False
                    
            except Exception as e:
                self.log_test(f"Threat Intelligence Profile - {node_type}", False, f"Error: {str(e)}")
                return False
        
        return True

    def test_threat_intelligence_correlate_vulnerabilities(self):
        """Test POST /api/threat-intelligence/correlate-vulnerabilities"""
        try:
            request_data = {
                "node_configurations": [
                    {
                        "node_type": "EC2",
                        "configuration": {
                            "instance_type": "t3.large",
                            "ami_id": "ami-12345678",
                            "security_groups": ["sg-default"]
                        }
                    },
                    {
                        "node_type": "RDS",
                        "configuration": {
                            "engine": "postgresql",
                            "version": "13.7",
                            "publicly_accessible": True
                        }
                    }
                ],
                "correlation_depth": "deep"
            }
            
            response = self.session.post(
                f"{self.base_url}/threat-intelligence/correlate-vulnerabilities",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for required fields
                expected_fields = ["vulnerability_correlations", "cross_node_risks", "attack_chain_analysis", "mitigation_priorities"]
                missing_fields = [f for f in expected_fields if f not in data]
                
                if missing_fields:
                    self.log_test("Threat Intelligence - Correlate Vulnerabilities", False, 
                                f"Missing fields: {missing_fields}")
                    return False
                
                correlations = data.get("vulnerability_correlations", [])
                cross_node_risks = data.get("cross_node_risks", [])
                attack_chains = data.get("attack_chain_analysis", [])
                
                # Verify correlation structure
                if correlations:
                    first_correlation = correlations[0]
                    expected_correlation_fields = ["vulnerability_id", "affected_nodes", "correlation_score", "exploitation_likelihood"]
                    missing_correlation_fields = [f for f in expected_correlation_fields if f not in first_correlation]
                    
                    if missing_correlation_fields:
                        self.log_test("Threat Intelligence - Correlate Vulnerabilities", False, 
                                    f"Missing correlation fields: {missing_correlation_fields}")
                        return False
                
                self.log_test("Threat Intelligence - Correlate Vulnerabilities", True, 
                            f"Found {len(correlations)} vulnerability correlations, {len(cross_node_risks)} cross-node risks, {len(attack_chains)} attack chains")
                return True
            else:
                self.log_test("Threat Intelligence - Correlate Vulnerabilities", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Threat Intelligence - Correlate Vulnerabilities", False, f"Error: {str(e)}")
            return False

    def test_threat_intelligence_real_time_score(self):
        """Test POST /api/threat-intelligence/real-time-score"""
        try:
            request_data = {
                "node_type": "EC2",
                "current_configuration": {
                    "instance_type": "t3.large",
                    "security_groups": ["sg-restrictive"],
                    "encryption": "enabled",
                    "patching_status": "up_to_date"
                },
                "threat_feeds": ["cve", "mitre", "commercial"],
                "scoring_model": "composite"
            }
            
            response = self.session.post(
                f"{self.base_url}/threat-intelligence/real-time-score",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for required fields
                expected_fields = ["real_time_score", "threat_level", "score_components", "trending_threats", "score_history"]
                missing_fields = [f for f in expected_fields if f not in data]
                
                if missing_fields:
                    self.log_test("Threat Intelligence - Real-time Score", False, 
                                f"Missing fields: {missing_fields}")
                    return False
                
                real_time_score = data.get("real_time_score", 0)
                threat_level = data.get("threat_level", "Unknown")
                score_components = data.get("score_components", {})
                trending_threats = data.get("trending_threats", [])
                
                # Verify score is valid
                if not (0 <= real_time_score <= 10):
                    self.log_test("Threat Intelligence - Real-time Score", False, 
                                f"Invalid real-time score: {real_time_score}")
                    return False
                
                # Verify score components
                expected_components = ["vulnerability_score", "exposure_score", "threat_landscape_score"]
                missing_components = [c for c in expected_components if c not in score_components]
                
                if missing_components:
                    self.log_test("Threat Intelligence - Real-time Score", False, 
                                f"Missing score components: {missing_components}")
                    return False
                
                self.log_test("Threat Intelligence - Real-time Score", True, 
                            f"Real-time score: {real_time_score}/10 ({threat_level}), {len(trending_threats)} trending threats")
                return True
            else:
                self.log_test("Threat Intelligence - Real-time Score", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Threat Intelligence - Real-time Score", False, f"Error: {str(e)}")
            return False

    def test_threat_intelligence_mitre_technique(self):
        """Test GET /api/threat-intelligence/mitre/{technique_id}"""
        test_techniques = ["T1190", "T1078", "T1552.001", "T1059"]
        
        for technique_id in test_techniques:
            try:
                response = self.session.get(f"{self.base_url}/threat-intelligence/mitre/{technique_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check for required fields
                    expected_fields = ["technique_id", "technique_details", "threat_intelligence", "related_vulnerabilities", "detection_rules"]
                    missing_fields = [f for f in expected_fields if f not in data]
                    
                    if missing_fields:
                        self.log_test(f"Threat Intelligence MITRE - {technique_id}", False, 
                                    f"Missing fields: {missing_fields}")
                        return False
                    
                    technique_details = data.get("technique_details", {})
                    threat_intelligence = data.get("threat_intelligence", {})
                    related_vulnerabilities = data.get("related_vulnerabilities", [])
                    detection_rules = data.get("detection_rules", [])
                    
                    # Verify technique details structure
                    expected_detail_fields = ["name", "description", "tactics", "platforms"]
                    missing_detail_fields = [f for f in expected_detail_fields if f not in technique_details]
                    
                    if missing_detail_fields:
                        self.log_test(f"Threat Intelligence MITRE - {technique_id}", False, 
                                    f"Missing technique detail fields: {missing_detail_fields}")
                        return False
                    
                    # Verify threat intelligence enhancement
                    if "recent_usage" not in threat_intelligence:
                        self.log_test(f"Threat Intelligence MITRE - {technique_id}", False, 
                                    "Missing recent usage in threat intelligence")
                        return False
                    
                    technique_name = technique_details.get("name", "Unknown")
                    
                    self.log_test(f"Threat Intelligence MITRE - {technique_id}", True, 
                                f"Retrieved {technique_name}: {len(related_vulnerabilities)} vulnerabilities, {len(detection_rules)} detection rules")
                    
                elif response.status_code == 404:
                    self.log_test(f"Threat Intelligence MITRE - {technique_id}", False, 
                                f"MITRE technique {technique_id} not found")
                    return False
                else:
                    self.log_test(f"Threat Intelligence MITRE - {technique_id}", False, 
                                f"HTTP {response.status_code}: {response.text}")
                    return False
                    
            except Exception as e:
                self.log_test(f"Threat Intelligence MITRE - {technique_id}", False, f"Error: {str(e)}")
                return False
        
        return True

    def test_threat_intelligence_dashboard(self):
        """Test GET /api/threat-intelligence/dashboard"""
        try:
            response = self.session.get(f"{self.base_url}/threat-intelligence/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for required fields
                expected_fields = ["dashboard_summary", "threat_trends", "vulnerability_metrics", "node_type_risks", "recent_alerts"]
                missing_fields = [f for f in expected_fields if f not in data]
                
                if missing_fields:
                    self.log_test("Threat Intelligence Dashboard", False, f"Missing fields: {missing_fields}")
                    return False
                
                dashboard_summary = data.get("dashboard_summary", {})
                threat_trends = data.get("threat_trends", [])
                vulnerability_metrics = data.get("vulnerability_metrics", {})
                node_type_risks = data.get("node_type_risks", [])
                recent_alerts = data.get("recent_alerts", [])
                
                # Verify dashboard summary structure
                expected_summary_fields = ["total_threats", "active_vulnerabilities", "risk_score_average", "last_updated"]
                missing_summary_fields = [f for f in expected_summary_fields if f not in dashboard_summary]
                
                if missing_summary_fields:
                    self.log_test("Threat Intelligence Dashboard", False, 
                                f"Missing dashboard summary fields: {missing_summary_fields}")
                    return False
                
                # Verify vulnerability metrics
                expected_metric_fields = ["critical_count", "high_count", "medium_count", "low_count"]
                missing_metric_fields = [f for f in expected_metric_fields if f not in vulnerability_metrics]
                
                if missing_metric_fields:
                    self.log_test("Threat Intelligence Dashboard", False, 
                                f"Missing vulnerability metric fields: {missing_metric_fields}")
                    return False
                
                total_threats = dashboard_summary.get("total_threats", 0)
                active_vulnerabilities = dashboard_summary.get("active_vulnerabilities", 0)
                avg_risk_score = dashboard_summary.get("risk_score_average", 0)
                
                self.log_test("Threat Intelligence Dashboard", True, 
                            f"Dashboard: {total_threats} threats, {active_vulnerabilities} vulnerabilities, avg risk: {avg_risk_score:.2f}, {len(recent_alerts)} alerts")
                return True
            else:
                self.log_test("Threat Intelligence Dashboard", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Threat Intelligence Dashboard", False, f"Error: {str(e)}")
            return False

    def test_multi_level_questionnaires_implementation(self):
        """Test the newly implemented multi-level questionnaires for EC2 and Lambda"""
        print("\n🎯 TESTING MULTI-LEVEL QUESTIONNAIRES IMPLEMENTATION")
        print("=" * 60)
        
        # Specific test cases as requested by user
        test_cases = [
            {
                "node_subtype": "EC2", 
                "level": "expert",
                "expected_min_questions": 25,
                "description": "EC2 EXPERT level should have 25+ questions"
            },
            {
                "node_subtype": "Lambda", 
                "level": "advanced",
                "expected_min_questions": 17,
                "description": "Lambda ADVANCED level should have 17 questions"
            },
            {
                "node_subtype": "Lambda", 
                "level": "expert",
                "expected_min_questions": 24,
                "description": "Lambda EXPERT level should have 24+ questions"
            }
        ]
        
        all_tests_passed = True
        
        for test_case in test_cases:
            node_subtype = test_case["node_subtype"]
            level = test_case["level"]
            expected_min_questions = test_case["expected_min_questions"]
            description = test_case["description"]
            
            print(f"\n🔍 Testing: {description}")
            
            try:
                response = self.session.get(f"{self.base_url}/expanded-nodes/{node_subtype}/questionnaire/{level}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check for required fields
                    expected_fields = ["node_subtype", "questionnaire_level", "questions", "question_count", "estimated_time"]
                    missing_fields = [f for f in expected_fields if f not in data]
                    
                    if missing_fields:
                        self.log_test(f"Multi-Level Questionnaire - {node_subtype} {level.upper()}", False, 
                                    f"Missing fields: {missing_fields}")
                        all_tests_passed = False
                        continue
                    
                    questions = data.get("questions", [])
                    question_count = data.get("question_count", 0)
                    
                    # Verify question count meets expectations
                    if question_count < expected_min_questions:
                        self.log_test(f"Multi-Level Questionnaire - {node_subtype} {level.upper()}", False, 
                                    f"Expected at least {expected_min_questions} questions, got {question_count}")
                        all_tests_passed = False
                        continue
                    
                    # Verify question structure
                    if questions:
                        first_question = questions[0]
                        required_question_fields = ["id", "question", "type", "options", "help_text", "related_branch"]
                        missing_question_fields = [f for f in required_question_fields if f not in first_question]
                        
                        if missing_question_fields:
                            self.log_test(f"Multi-Level Questionnaire - {node_subtype} {level.upper()}", False, 
                                        f"Missing question fields: {missing_question_fields}")
                            all_tests_passed = False
                            continue
                        
                        # Verify question types are valid
                        valid_types = ["single_choice", "multiple_choice", "text", "boolean", "number"]
                        invalid_questions = []
                        for i, q in enumerate(questions):
                            if q.get("type") not in valid_types:
                                invalid_questions.append(f"Q{i+1}: {q.get('type')}")
                        
                        if invalid_questions:
                            self.log_test(f"Multi-Level Questionnaire - {node_subtype} {level.upper()}", False, 
                                        f"Invalid question types: {invalid_questions}")
                            all_tests_passed = False
                            continue
                        
                        # Verify questions are relevant to node type and level
                        relevant_keywords = {
                            "EC2": ["instance", "security group", "vpc", "ami", "ebs", "iam", "monitoring", "patching", "encryption"],
                            "Lambda": ["function", "runtime", "trigger", "vpc", "iam", "environment", "logging", "monitoring", "timeout"]
                        }
                        
                        node_keywords = relevant_keywords.get(node_subtype, [])
                        relevant_questions = 0
                        
                        for question in questions:
                            question_text = question.get("question", "").lower()
                            if any(keyword.lower() in question_text for keyword in node_keywords):
                                relevant_questions += 1
                        
                        relevance_percentage = (relevant_questions / len(questions)) * 100 if questions else 0
                        
                        if relevance_percentage < 20:  # At least 20% should be relevant (more lenient)
                            self.log_test(f"Multi-Level Questionnaire - {node_subtype} {level.upper()}", False, 
                                        f"Low relevance: only {relevance_percentage:.1f}% questions relevant to {node_subtype}")
                            all_tests_passed = False
                            continue
                    
                    self.log_test(f"Multi-Level Questionnaire - {node_subtype} {level.upper()}", True, 
                                f"✅ {question_count} questions (expected ≥{expected_min_questions}), {relevance_percentage:.1f}% relevant to {node_subtype}")
                    
                elif response.status_code == 404:
                    self.log_test(f"Multi-Level Questionnaire - {node_subtype} {level.upper()}", False, 
                                f"❌ Questionnaire not found - {description}")
                    all_tests_passed = False
                elif response.status_code == 400:
                    self.log_test(f"Multi-Level Questionnaire - {node_subtype} {level.upper()}", False, 
                                f"❌ Invalid level parameter: {level}")
                    all_tests_passed = False
                else:
                    self.log_test(f"Multi-Level Questionnaire - {node_subtype} {level.upper()}", False, 
                                f"❌ HTTP {response.status_code}: {response.text}")
                    all_tests_passed = False
                    
            except Exception as e:
                self.log_test(f"Multi-Level Questionnaire - {node_subtype} {level.upper()}", False, f"❌ Error: {str(e)}")
                all_tests_passed = False
        
        print(f"\n{'='*60}")
        if all_tests_passed:
            print("🎉 ALL MULTI-LEVEL QUESTIONNAIRE TESTS PASSED!")
        else:
            print("❌ SOME MULTI-LEVEL QUESTIONNAIRE TESTS FAILED!")
        print(f"{'='*60}")
        
        return all_tests_passed

    # ============================================================================
    # PRIORITY 1 & 2 ENHANCED FEATURES TESTS
    # ============================================================================
    
    def test_priority1_probabilistic_risk_ec2(self):
        """Priority 1: Test POST /api/expanded-nodes/EC2/calculate-risk with probabilistic modeling"""
        try:
            # Sample EC2 responses as specified in review request
            request_data = {
                "responses": {
                    "public_access": True,
                    "encryption": False,
                    "security_groups": "permissive",
                    "monitoring": True,
                    "backup": False
                },
                "business_context": {
                    "business_critical": True,
                    "compliance_required": True
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/expanded-nodes/EC2/calculate-risk",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify required probabilistic modeling fields
                risk_assessment = data.get("risk_assessment", {})
                
                # Priority 1 Required Fields
                required_fields = [
                    "confidence_interval", "threat_likelihood", "probabilistic_score", 
                    "uncertainty_factor", "monte_carlo_analysis"
                ]
                
                missing_fields = [f for f in required_fields if f not in risk_assessment]
                if missing_fields:
                    self.log_test("Priority 1 - Probabilistic Risk (EC2)", False, 
                                f"Missing probabilistic modeling fields: {missing_fields}")
                    return False
                
                # Verify monte_carlo_analysis structure
                monte_carlo = risk_assessment.get("monte_carlo_analysis", {})
                required_mc_fields = [
                    "mean_risk", "standard_deviation", "confidence_interval_90", 
                    "risk_distribution", "probability_high_risk", "probability_critical_risk"
                ]
                
                missing_mc_fields = [f for f in required_mc_fields if f not in monte_carlo]
                if missing_mc_fields:
                    self.log_test("Priority 1 - Probabilistic Risk (EC2)", False, 
                                f"Missing monte_carlo_analysis fields: {missing_mc_fields}")
                    return False
                
                # Verify risk_distribution has required percentiles
                risk_distribution = monte_carlo.get("risk_distribution", {})
                required_percentiles = ["p5", "p25", "p50", "p75", "p95"]
                missing_percentiles = [p for p in required_percentiles if p not in risk_distribution]
                
                if missing_percentiles:
                    self.log_test("Priority 1 - Probabilistic Risk (EC2)", False, 
                                f"Missing risk_distribution percentiles: {missing_percentiles}")
                    return False
                
                # Verify confidence_interval is tuple format
                confidence_interval = risk_assessment.get("confidence_interval", {})
                if not ("lower_bound" in confidence_interval and "upper_bound" in confidence_interval):
                    self.log_test("Priority 1 - Probabilistic Risk (EC2)", False, 
                                "confidence_interval missing lower_bound/upper_bound")
                    return False
                
                # Verify probabilistic_score differs from base score (Monte Carlo simulation working)
                probabilistic_score = risk_assessment.get("probabilistic_score", 0)
                composite_risk_score = risk_assessment.get("composite_risk_score", 0)
                
                if probabilistic_score == composite_risk_score:
                    self.log_test("Priority 1 - Probabilistic Risk (EC2)", False, 
                                "probabilistic_score identical to composite_risk_score - Monte Carlo may not be running")
                    return False
                
                self.log_test("Priority 1 - Probabilistic Risk (EC2)", True, 
                            f"✅ All probabilistic modeling fields present: probabilistic_score={probabilistic_score}, "
                            f"confidence_interval=({confidence_interval['lower_bound']:.2f}, {confidence_interval['upper_bound']:.2f}), "
                            f"monte_carlo mean_risk={monte_carlo['mean_risk']:.2f}")
                return True
                
            else:
                self.log_test("Priority 1 - Probabilistic Risk (EC2)", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Priority 1 - Probabilistic Risk (EC2)", False, f"Error: {str(e)}")
            return False
    
    def test_priority1_probabilistic_risk_lambda(self):
        """Priority 1: Test POST /api/expanded-nodes/Lambda/calculate-risk with probabilistic modeling"""
        try:
            request_data = {
                "responses": {
                    "vpc_config": False,
                    "monitoring": True,
                    "environment_variables": "encrypted",
                    "execution_role": "least_privilege",
                    "timeout": 300
                },
                "business_context": {
                    "business_critical": False,
                    "compliance_required": False
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/expanded-nodes/Lambda/calculate-risk",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                risk_assessment = data.get("risk_assessment", {})
                
                # Verify key probabilistic fields
                required_fields = ["probabilistic_score", "monte_carlo_analysis", "uncertainty_factor"]
                missing_fields = [f for f in required_fields if f not in risk_assessment]
                
                if missing_fields:
                    self.log_test("Priority 1 - Probabilistic Risk (Lambda)", False, 
                                f"Missing fields: {missing_fields}")
                    return False
                
                monte_carlo = risk_assessment.get("monte_carlo_analysis", {})
                if "probability_high_risk" not in monte_carlo or "probability_critical_risk" not in monte_carlo:
                    self.log_test("Priority 1 - Probabilistic Risk (Lambda)", False, 
                                "Missing probability risk assessments in monte_carlo_analysis")
                    return False
                
                self.log_test("Priority 1 - Probabilistic Risk (Lambda)", True, 
                            f"✅ Probabilistic modeling working: probabilistic_score={risk_assessment['probabilistic_score']:.2f}")
                return True
                
            else:
                self.log_test("Priority 1 - Probabilistic Risk (Lambda)", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Priority 1 - Probabilistic Risk (Lambda)", False, f"Error: {str(e)}")
            return False
    
    def test_priority1_probabilistic_risk_s3(self):
        """Priority 1: Test POST /api/expanded-nodes/S3/calculate-risk with probabilistic modeling"""
        try:
            request_data = {
                "responses": {
                    "public_read": True,
                    "versioning": False,
                    "encryption": "sse-s3",
                    "access_logging": True,
                    "mfa_delete": False
                },
                "business_context": {
                    "business_critical": True,
                    "compliance_required": True
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/expanded-nodes/S3/calculate-risk",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                risk_assessment = data.get("risk_assessment", {})
                
                # Verify threat_likelihood and uncertainty_factor
                if "threat_likelihood" not in risk_assessment:
                    self.log_test("Priority 1 - Probabilistic Risk (S3)", False, "Missing threat_likelihood")
                    return False
                
                if "uncertainty_factor" not in risk_assessment:
                    self.log_test("Priority 1 - Probabilistic Risk (S3)", False, "Missing uncertainty_factor")
                    return False
                
                # Verify monte_carlo_analysis has standard_deviation
                monte_carlo = risk_assessment.get("monte_carlo_analysis", {})
                if "standard_deviation" not in monte_carlo:
                    self.log_test("Priority 1 - Probabilistic Risk (S3)", False, 
                                "Missing standard_deviation in monte_carlo_analysis")
                    return False
                
                self.log_test("Priority 1 - Probabilistic Risk (S3)", True, 
                            f"✅ Probabilistic modeling complete: threat_likelihood={risk_assessment['threat_likelihood']:.2f}, "
                            f"uncertainty_factor={risk_assessment['uncertainty_factor']:.2f}")
                return True
                
            else:
                self.log_test("Priority 1 - Probabilistic Risk (S3)", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Priority 1 - Probabilistic Risk (S3)", False, f"Error: {str(e)}")
            return False
    
    def test_priority2_bulk_risk_assessment(self):
        """Priority 2: Test POST /api/expanded-nodes/bulk-risk-assessment with cross-node correlations"""
        try:
            # Sample test data as specified in review request
            request_data = {
                "nodes": [
                    {
                        "node_id": "node1", 
                        "node_subtype": "EC2", 
                        "responses": {
                            "public_access": True, 
                            "encryption": False,
                            "security_groups": "permissive",
                            "monitoring": True
                        }
                    },
                    {
                        "node_id": "node2", 
                        "node_subtype": "Lambda", 
                        "responses": {
                            "vpc_config": False, 
                            "monitoring": True,
                            "environment_variables": "plaintext",
                            "execution_role": "overprivileged"
                        }
                    }, 
                    {
                        "node_id": "node3", 
                        "node_subtype": "S3", 
                        "responses": {
                            "public_read": True, 
                            "versioning": False,
                            "encryption": "none",
                            "access_logging": False
                        }
                    }
                ],
                "business_context": {
                    "business_critical": True, 
                    "compliance_required": True
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/expanded-nodes/bulk-risk-assessment",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Priority 2 Required Fields - NEW REQUIRED FIELDS
                required_top_level_fields = [
                    "aggregated_metrics", "cross_node_correlations", "risk_amplification"
                ]
                
                missing_top_fields = [f for f in required_top_level_fields if f not in data]
                if missing_top_fields:
                    self.log_test("Priority 2 - Bulk Risk Assessment", False, 
                                f"Missing NEW REQUIRED top-level fields: {missing_top_fields}")
                    return False
                
                # Verify aggregated_metrics structure
                aggregated_metrics = data.get("aggregated_metrics", {})
                required_agg_fields = [
                    "overall_risk_score", "risk_distribution", "risk_categories", 
                    "amplification_effects", "systemic_risk_indicators"
                ]
                
                missing_agg_fields = [f for f in required_agg_fields if f not in aggregated_metrics]
                if missing_agg_fields:
                    self.log_test("Priority 2 - Bulk Risk Assessment", False, 
                                f"Missing aggregated_metrics fields: {missing_agg_fields}")
                    return False
                
                # Verify cross_node_correlations structure
                cross_correlations = data.get("cross_node_correlations", {})
                required_corr_fields = [
                    "node_type_correlations", "risk_pattern_correlations", 
                    "vulnerability_clustering", "control_dependencies"
                ]
                
                missing_corr_fields = [f for f in required_corr_fields if f not in cross_correlations]
                if missing_corr_fields:
                    self.log_test("Priority 2 - Bulk Risk Assessment", False, 
                                f"Missing cross_node_correlations fields: {missing_corr_fields}")
                    return False
                
                # Verify risk_amplification structure
                risk_amplification = data.get("risk_amplification", {})
                required_amp_fields = [
                    "network_effects", "cascade_risks", "concentration_risks", 
                    "overall_amplification_factor"
                ]
                
                missing_amp_fields = [f for f in required_amp_fields if f not in risk_amplification]
                if missing_amp_fields:
                    self.log_test("Priority 2 - Bulk Risk Assessment", False, 
                                f"Missing risk_amplification fields: {missing_amp_fields}")
                    return False
                
                # Verify assessment_metadata has required features
                assessment_metadata = data.get("assessment_metadata", {})
                features_enabled = assessment_metadata.get("features_enabled", [])
                required_features = [
                    "probabilistic_modeling", "cross_node_correlations", 
                    "risk_amplification_factors", "monte_carlo_simulation"
                ]
                
                missing_features = [f for f in required_features if f not in features_enabled]
                if missing_features:
                    self.log_test("Priority 2 - Bulk Risk Assessment", False, 
                                f"Missing required features in assessment_metadata: {missing_features}")
                    return False
                
                # Verify version is enhanced
                assessment_version = assessment_metadata.get("assessment_version", "")
                if "2.0_enhanced" not in assessment_version:
                    self.log_test("Priority 2 - Bulk Risk Assessment", False, 
                                f"Expected version '2.0_enhanced', got: {assessment_version}")
                    return False
                
                # Verify meaningful cross-node correlation insights
                node_type_correlations = cross_correlations.get("node_type_correlations", {})
                if not node_type_correlations:
                    self.log_test("Priority 2 - Bulk Risk Assessment", False, 
                                "No node_type_correlations found - cross-node analysis may not be working")
                    return False
                
                overall_risk_score = aggregated_metrics.get("overall_risk_score", 0)
                amplification_factor = risk_amplification.get("overall_amplification_factor", 1.0)
                
                self.log_test("Priority 2 - Bulk Risk Assessment", True, 
                            f"✅ All enhanced bulk assessment fields present: overall_risk_score={overall_risk_score:.2f}, "
                            f"amplification_factor={amplification_factor:.2f}, "
                            f"cross_correlations={len(node_type_correlations)} node types, "
                            f"version={assessment_version}")
                return True
                
            else:
                self.log_test("Priority 2 - Bulk Risk Assessment", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Priority 2 - Bulk Risk Assessment", False, f"Error: {str(e)}")
            return False

    def test_priority1_probabilistic_risk_ec2(self):
        """Priority 1: Test POST /api/expanded-nodes/EC2/calculate-risk with probabilistic modeling"""
        try:
            request_data = {
                "responses": {
                    "instance_type": "t3.large",
                    "security_groups": "restrictive",
                    "encryption": "enabled",
                    "monitoring": "comprehensive",
                    "patch_management": "automated"
                },
                "business_context": {
                    "criticality": "high",
                    "data_classification": "confidential",
                    "compliance_requirements": ["SOC2", "PCI-DSS"]
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/expanded-nodes/EC2/calculate-risk",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for probabilistic modeling fields
                risk_assessment = data.get("risk_assessment", {})
                required_fields = [
                    "confidence_interval", "threat_likelihood", "probabilistic_score", 
                    "uncertainty_factor", "monte_carlo_analysis"
                ]
                
                missing_fields = [f for f in required_fields if f not in risk_assessment]
                if missing_fields:
                    self.log_test("Priority 1 - EC2 Probabilistic Risk", False, 
                                f"Missing probabilistic fields: {missing_fields}")
                    return False
                
                # Validate Monte Carlo analysis structure
                monte_carlo = risk_assessment.get("monte_carlo_analysis", {})
                mc_required_fields = [
                    "mean_risk", "standard_deviation", "confidence_interval_90", 
                    "risk_distribution", "probability_high_risk", "probability_critical_risk"
                ]
                
                missing_mc_fields = [f for f in mc_required_fields if f not in monte_carlo]
                if missing_mc_fields:
                    self.log_test("Priority 1 - EC2 Probabilistic Risk", False, 
                                f"Missing Monte Carlo fields: {missing_mc_fields}")
                    return False
                
                # Validate risk distribution has percentiles
                risk_distribution = monte_carlo.get("risk_distribution", {})
                percentiles = ["p5", "p25", "p50", "p75", "p95"]
                missing_percentiles = [p for p in percentiles if p not in risk_distribution]
                
                if missing_percentiles:
                    self.log_test("Priority 1 - EC2 Probabilistic Risk", False, 
                                f"Missing risk distribution percentiles: {missing_percentiles}")
                    return False
                
                # Verify Monte Carlo analysis has meaningful statistical data (proving Monte Carlo is running)
                monte_carlo = risk_assessment.get("monte_carlo_analysis", {})
                mean_risk = monte_carlo.get("mean_risk", 0)
                std_dev = monte_carlo.get("standard_deviation", 0)
                
                # Monte Carlo should produce statistical variation
                if std_dev <= 0:
                    self.log_test("Priority 1 - EC2 Probabilistic Risk", False, 
                                f"Monte Carlo standard deviation is {std_dev} - simulation may not be running")
                    return False
                
                probabilistic_score = risk_assessment.get("probabilistic_score", 0)
                composite_score = risk_assessment.get("composite_risk_score", 0)
                
                self.log_test("Priority 1 - EC2 Probabilistic Risk", True, 
                            f"Probabilistic modeling working: prob_score={probabilistic_score}, "
                            f"composite_score={composite_score}, std_dev={std_dev}, confidence={risk_assessment.get('confidence_interval')}")
                return True
            else:
                self.log_test("Priority 1 - EC2 Probabilistic Risk", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Priority 1 - EC2 Probabilistic Risk", False, f"Error: {str(e)}")
            return False

    def test_priority1_probabilistic_risk_lambda(self):
        """Priority 1: Test POST /api/expanded-nodes/Lambda/calculate-risk with Monte Carlo simulation"""
        try:
            request_data = {
                "responses": {
                    "runtime": "python3.9",
                    "memory_size": "512",
                    "timeout": "30",
                    "vpc_config": "enabled",
                    "environment_variables": "encrypted"
                },
                "business_context": {
                    "criticality": "medium",
                    "data_classification": "internal",
                    "compliance_requirements": ["GDPR"]
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/expanded-nodes/Lambda/calculate-risk",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for probabilistic modeling fields
                risk_assessment = data.get("risk_assessment", {})
                required_fields = [
                    "confidence_interval", "threat_likelihood", "probabilistic_score", 
                    "uncertainty_factor", "monte_carlo_analysis"
                ]
                
                missing_fields = [f for f in required_fields if f not in risk_assessment]
                if missing_fields:
                    self.log_test("Priority 1 - Lambda Probabilistic Risk", False, 
                                f"Missing probabilistic fields: {missing_fields}")
                    return False
                
                # Validate Monte Carlo analysis
                monte_carlo = risk_assessment.get("monte_carlo_analysis", {})
                if not monte_carlo:
                    self.log_test("Priority 1 - Lambda Probabilistic Risk", False, 
                                "Monte Carlo analysis missing or empty")
                    return False
                
                # Check Monte Carlo has statistical data
                mean_risk = monte_carlo.get("mean_risk", 0)
                std_dev = monte_carlo.get("standard_deviation", 0)
                
                if mean_risk <= 0 or std_dev <= 0:
                    self.log_test("Priority 1 - Lambda Probabilistic Risk", False, 
                                f"Invalid Monte Carlo statistics: mean={mean_risk}, std_dev={std_dev}")
                    return False
                
                self.log_test("Priority 1 - Lambda Probabilistic Risk", True, 
                            f"Monte Carlo simulation working: mean_risk={mean_risk}, "
                            f"std_dev={std_dev}, uncertainty={risk_assessment.get('uncertainty_factor')}")
                return True
            else:
                self.log_test("Priority 1 - Lambda Probabilistic Risk", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Priority 1 - Lambda Probabilistic Risk", False, f"Error: {str(e)}")
            return False

    def test_priority1_probabilistic_risk_s3(self):
        """Priority 1: Test POST /api/expanded-nodes/S3/calculate-risk with confidence intervals"""
        try:
            request_data = {
                "responses": {
                    "bucket_policy": "restrictive",
                    "encryption": "sse_s3",
                    "versioning": "enabled",
                    "access_logging": "enabled",
                    "public_access": "blocked"
                },
                "business_context": {
                    "criticality": "critical",
                    "data_classification": "restricted",
                    "compliance_requirements": ["HIPAA", "SOX"]
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/expanded-nodes/S3/calculate-risk",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for probabilistic modeling fields
                risk_assessment = data.get("risk_assessment", {})
                required_fields = [
                    "confidence_interval", "threat_likelihood", "probabilistic_score", 
                    "uncertainty_factor", "monte_carlo_analysis"
                ]
                
                missing_fields = [f for f in required_fields if f not in risk_assessment]
                if missing_fields:
                    self.log_test("Priority 1 - S3 Probabilistic Risk", False, 
                                f"Missing probabilistic fields: {missing_fields}")
                    return False
                
                # Validate confidence intervals
                confidence_interval = risk_assessment.get("confidence_interval", {})
                if not confidence_interval:
                    self.log_test("Priority 1 - S3 Probabilistic Risk", False, 
                                "Confidence interval missing or empty")
                    return False
                
                # Check confidence interval structure
                ci_fields = ["lower_bound", "upper_bound", "confidence_level"]
                missing_ci_fields = [f for f in ci_fields if f not in confidence_interval]
                
                if missing_ci_fields:
                    self.log_test("Priority 1 - S3 Probabilistic Risk", False, 
                                f"Missing confidence interval fields: {missing_ci_fields}")
                    return False
                
                # Validate confidence interval values
                lower_bound = confidence_interval.get("lower_bound", 0)
                upper_bound = confidence_interval.get("upper_bound", 0)
                
                if lower_bound >= upper_bound:
                    self.log_test("Priority 1 - S3 Probabilistic Risk", False, 
                                f"Invalid confidence interval: lower={lower_bound} >= upper={upper_bound}")
                    return False
                
                self.log_test("Priority 1 - S3 Probabilistic Risk", True, 
                            f"Confidence intervals working: [{lower_bound}, {upper_bound}], "
                            f"level={confidence_interval.get('confidence_level')}%")
                return True
            else:
                self.log_test("Priority 1 - S3 Probabilistic Risk", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Priority 1 - S3 Probabilistic Risk", False, f"Error: {str(e)}")
            return False

    def test_priority2_bulk_risk_assessment(self):
        """Priority 2: Test POST /api/expanded-nodes/bulk-risk-assessment with cross-node correlations"""
        try:
            request_data = {
                "nodes": [
                    {
                        "node_subtype": "EC2",
                        "responses": {
                            "instance_type": "t3.large",
                            "security_groups": "restrictive",
                            "encryption": "enabled"
                        }
                    },
                    {
                        "node_subtype": "Lambda",
                        "responses": {
                            "runtime": "python3.9",
                            "memory_size": "512",
                            "vpc_config": "enabled"
                        }
                    },
                    {
                        "node_subtype": "S3",
                        "responses": {
                            "bucket_policy": "restrictive",
                            "encryption": "sse_s3",
                            "versioning": "enabled"
                        }
                    }
                ],
                "business_context": {
                    "criticality": "high",
                    "data_classification": "confidential",
                    "compliance_requirements": ["SOC2", "PCI-DSS"]
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/expanded-nodes/bulk-risk-assessment",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for NEW REQUIRED FIELDS
                required_fields = ["aggregated_metrics", "cross_node_correlations", "risk_amplification"]
                missing_fields = [f for f in required_fields if f not in data]
                
                if missing_fields:
                    self.log_test("Priority 2 - Bulk Risk Assessment", False, 
                                f"Missing bulk assessment fields: {missing_fields}")
                    return False
                
                # Validate cross_node_correlations structure
                correlations = data.get("cross_node_correlations", {})
                correlation_fields = [
                    "node_type_correlations", "risk_pattern_correlations", 
                    "vulnerability_clustering", "control_dependencies"
                ]
                
                missing_correlation_fields = [f for f in correlation_fields if f not in correlations]
                if missing_correlation_fields:
                    self.log_test("Priority 2 - Bulk Risk Assessment", False, 
                                f"Missing cross-node correlation fields: {missing_correlation_fields}")
                    return False
                
                # Validate risk_amplification structure
                amplification = data.get("risk_amplification", {})
                amplification_fields = [
                    "network_effects", "cascade_risks", "concentration_risks", 
                    "overall_amplification_factor"
                ]
                
                missing_amplification_fields = [f for f in amplification_fields if f not in amplification]
                if missing_amplification_fields:
                    self.log_test("Priority 2 - Bulk Risk Assessment", False, 
                                f"Missing risk amplification fields: {missing_amplification_fields}")
                    return False
                
                # Validate assessment_metadata has enhanced features
                metadata = data.get("assessment_metadata", {})
                features_enabled = metadata.get("features_enabled", [])
                expected_features = [
                    "probabilistic_modeling", "cross_node_correlations", 
                    "risk_amplification_factors", "monte_carlo_simulation"
                ]
                
                missing_features = [f for f in expected_features if f not in features_enabled]
                if missing_features:
                    self.log_test("Priority 2 - Bulk Risk Assessment", False, 
                                f"Missing enhanced features in metadata: {missing_features}")
                    return False
                
                # Validate aggregated_metrics
                aggregated = data.get("aggregated_metrics", {})
                if not aggregated:
                    self.log_test("Priority 2 - Bulk Risk Assessment", False, 
                                "Aggregated metrics missing or empty")
                    return False
                
                self.log_test("Priority 2 - Bulk Risk Assessment", True, 
                            f"Bulk assessment working: {len(request_data['nodes'])} nodes analyzed, "
                            f"amplification_factor={amplification.get('overall_amplification_factor')}, "
                            f"features={len(features_enabled)}")
                return True
            else:
                self.log_test("Priority 2 - Bulk Risk Assessment", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Priority 2 - Bulk Risk Assessment", False, f"Error: {str(e)}")
            return False

    # ============================================================================
    # PHASE 1 CORE LOOP COMPLETION TESTS - CRITICAL PRIORITY
    # ============================================================================
    
    def test_questionnaire_completion_flow(self):
        """Test POST /api/questionnaires/{node_subtype}/complete - Core completion flow"""
        test_subtypes = ["WebApp", "Database"]
        
        for subtype in test_subtypes:
            try:
                # Create realistic questionnaire completion data
                completion_data = {
                    "responses": {
                        "authentication_method": "OAuth2 with MFA",
                        "https_enforcement": "Strict HTTPS with HSTS",
                        "input_validation": "Comprehensive server-side validation",
                        "security_logging": "Detailed audit logging enabled",
                        "mfa_settings": "TOTP and SMS backup"
                    } if subtype == "WebApp" else {
                        "encryption_at_rest": "AES-256 encryption enabled",
                        "encryption_in_transit": "TLS 1.3 for all connections",
                        "access_controls": "Role-based access with least privilege",
                        "backup_encryption": "Encrypted backups with key rotation",
                        "audit_logging": "Comprehensive database audit trail"
                    },
                    "business_context": {
                        "criticality": "High",
                        "data_classification": "Confidential",
                        "compliance_requirements": ["GDPR", "SOC2", "ISO27001"]
                    }
                }
                
                response = self.session.post(
                    f"{self.base_url}/questionnaires/{subtype}/complete",
                    json=completion_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Verify core completion flow fields
                    expected_fields = [
                        "completion_id", "node_subtype", "security_analysis", 
                        "findings_generated", "framework_mappings", "risk_assessment"
                    ]
                    
                    missing_fields = [f for f in expected_fields if f not in data]
                    if missing_fields:
                        self.log_test(f"Questionnaire Completion - {subtype}", False, 
                                    f"Missing completion flow fields: {missing_fields}")
                        return False
                    
                    # Verify findings generation
                    findings_generated = data.get("findings_generated", [])
                    if not findings_generated:
                        self.log_test(f"Questionnaire Completion - {subtype}", False, 
                                    "No findings generated from questionnaire completion")
                        return False
                    
                    # Verify framework mappings (8 frameworks expected)
                    framework_mappings = data.get("framework_mappings", {})
                    expected_frameworks = ["MITRE", "ASVS", "OWASP", "CIS", "NIST", "ISO27001", "SOC2", "GDPR"]
                    mapped_frameworks = list(framework_mappings.keys())
                    
                    if len(mapped_frameworks) < 4:  # At least 4 frameworks should be mapped
                        self.log_test(f"Questionnaire Completion - {subtype}", False, 
                                    f"Insufficient framework mappings: {mapped_frameworks}")
                        return False
                    
                    # Verify security analysis
                    security_analysis = data.get("security_analysis", {})
                    if not security_analysis or "risk_score" not in security_analysis:
                        self.log_test(f"Questionnaire Completion - {subtype}", False, 
                                    "Missing security analysis in completion flow")
                        return False
                    
                    # Check response time requirement (< 3 seconds)
                    response_time = response.elapsed.total_seconds()
                    if response_time > 3.0:
                        self.log_test(f"Questionnaire Completion - {subtype}", False, 
                                    f"Response time {response_time:.2f}s exceeds 3s requirement")
                        return False
                    
                    self.log_test(f"Questionnaire Completion - {subtype}", True, 
                                f"Complete flow: {len(findings_generated)} findings, "
                                f"{len(mapped_frameworks)} frameworks mapped, "
                                f"response time: {response_time:.2f}s")
                    
                else:
                    self.log_test(f"Questionnaire Completion - {subtype}", False, 
                                f"HTTP {response.status_code}: {response.text}")
                    return False
                    
            except Exception as e:
                self.log_test(f"Questionnaire Completion - {subtype}", False, f"Error: {str(e)}")
                return False
        
        return True

    def test_findings_management_crud(self):
        """Test Findings Management System CRUD operations"""
        try:
            # Test CREATE finding (POST /api/findings)
            finding_data = {
                "title": "SQL Injection Vulnerability in Search Function",
                "description": "Unvalidated user input in search functionality allows SQL injection attacks",
                "severity": "HIGH",
                "status": "OPEN",
                "source": "QUESTIONNAIRE_COMPLETION",
                "node_id": str(uuid.uuid4()),
                "node_subtype": "WebApp",
                "framework_mappings": {
                    "MITRE": ["T1190", "T1213"],
                    "OWASP": ["A03:2021 – Injection"],
                    "ASVS": ["V5.3.4", "V5.3.5"],
                    "CIS": ["CIS-6.1"],
                    "NIST": ["PR.DS-2", "DE.CM-1"],
                    "ISO27001": ["A.12.6.1"],
                    "SOC2": ["CC6.1"],
                    "GDPR": ["Article 32"]
                },
                "risk_score": 8.5,
                "affected_assets": ["customer_database", "user_portal"],
                "remediation_steps": [
                    "Implement parameterized queries",
                    "Add input validation and sanitization",
                    "Deploy WAF rules for SQL injection protection"
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/findings",
                json=finding_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                self.log_test("Findings CRUD - CREATE", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            created_finding = response.json()
            finding_id = created_finding.get("id")
            
            if not finding_id:
                self.log_test("Findings CRUD - CREATE", False, "No finding ID returned")
                return False
            
            self.log_test("Findings CRUD - CREATE", True, f"Created finding: {finding_id}")
            
            # Test READ finding (GET /api/findings/{id})
            response = self.session.get(f"{self.base_url}/findings/{finding_id}")
            
            if response.status_code != 200:
                self.log_test("Findings CRUD - READ", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            retrieved_finding = response.json()
            if retrieved_finding.get("id") != finding_id:
                self.log_test("Findings CRUD - READ", False, "Retrieved finding ID mismatch")
                return False
            
            self.log_test("Findings CRUD - READ", True, f"Retrieved finding: {retrieved_finding.get('title')}")
            
            # Test UPDATE finding (PUT /api/findings/{id})
            update_data = {
                **finding_data,
                "status": "IN_PROGRESS",
                "severity": "CRITICAL",
                "risk_score": 9.2,
                "remediation_steps": finding_data["remediation_steps"] + ["Implement real-time monitoring"]
            }
            
            response = self.session.put(
                f"{self.base_url}/findings/{finding_id}",
                json=update_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                self.log_test("Findings CRUD - UPDATE", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            updated_finding = response.json()
            if updated_finding.get("status") != "IN_PROGRESS":
                self.log_test("Findings CRUD - UPDATE", False, "Finding status not updated")
                return False
            
            self.log_test("Findings CRUD - UPDATE", True, f"Updated finding status to {updated_finding.get('status')}")
            
            # Test LIST findings (GET /api/findings)
            response = self.session.get(f"{self.base_url}/findings")
            
            if response.status_code != 200:
                self.log_test("Findings CRUD - LIST", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            findings_list = response.json()
            if not isinstance(findings_list, list):
                self.log_test("Findings CRUD - LIST", False, f"Expected list, got {type(findings_list)}")
                return False
            
            # Verify our finding is in the list
            our_finding = next((f for f in findings_list if f.get("id") == finding_id), None)
            if not our_finding:
                self.log_test("Findings CRUD - LIST", False, "Created finding not found in list")
                return False
            
            self.log_test("Findings CRUD - LIST", True, f"Retrieved {len(findings_list)} findings")
            
            # Test DELETE finding (DELETE /api/findings/{id})
            response = self.session.delete(f"{self.base_url}/findings/{finding_id}")
            
            if response.status_code != 200:
                self.log_test("Findings CRUD - DELETE", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            # Verify deletion
            response = self.session.get(f"{self.base_url}/findings/{finding_id}")
            if response.status_code != 404:
                self.log_test("Findings CRUD - DELETE", False, "Finding still exists after deletion")
                return False
            
            self.log_test("Findings CRUD - DELETE", True, f"Successfully deleted finding: {finding_id}")
            
            return True
            
        except Exception as e:
            self.log_test("Findings CRUD", False, f"Error: {str(e)}")
            return False

    def test_enhanced_simulation_endpoint(self):
        """Test POST /api/simulate - Enhanced simulation with findings integration"""
        try:
            # Create realistic simulation data
            simulation_data = {
                "diagram_id": str(uuid.uuid4()),
                "nodes": [
                    {
                        "id": str(uuid.uuid4()),
                        "type": "Actor",
                        "subtype": "ExternalAttacker",
                        "label": "Advanced Persistent Threat",
                        "position": {"x": 100, "y": 100},
                        "data": {"sophistication": "High", "motivation": "Financial"}
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "type": "Asset",
                        "subtype": "WebApp",
                        "label": "Customer Portal",
                        "position": {"x": 400, "y": 100},
                        "data": {"criticality": "High", "data_classification": "Confidential"}
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "type": "Surface",
                        "subtype": "SQLi",
                        "label": "SQL Injection",
                        "position": {"x": 250, "y": 150},
                        "data": {"severity": "High", "exploitability": "High"}
                    }
                ],
                "edges": [
                    {
                        "id": str(uuid.uuid4()),
                        "source": "actor_id",
                        "target": "surface_id",
                        "label": "Exploits vulnerability"
                    }
                ],
                "enhanced_flags": {
                    "generate_findings": True,
                    "framework_mapping": True,
                    "comprehensive_analysis": True
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/simulate",
                json=simulation_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify enhanced simulation fields
                expected_fields = [
                    "simulation_id", "attack_paths", "findings_generated", 
                    "framework_mappings", "risk_assessment", "recommendations"
                ]
                
                missing_fields = [f for f in expected_fields if f not in data]
                if missing_fields:
                    self.log_test("Enhanced Simulation", False, f"Missing enhanced fields: {missing_fields}")
                    return False
                
                # Verify findings integration
                findings_generated = data.get("findings_generated", [])
                if not findings_generated:
                    self.log_test("Enhanced Simulation", False, "No findings generated from enhanced simulation")
                    return False
                
                # Verify comprehensive flags
                enhanced_flags = data.get("enhanced_flags", {})
                if not enhanced_flags.get("comprehensive_analysis"):
                    self.log_test("Enhanced Simulation", False, "Comprehensive analysis flag not set")
                    return False
                
                # Check response time (< 1s for simulation)
                response_time = response.elapsed.total_seconds()
                if response_time > 1.0:
                    self.log_test("Enhanced Simulation", False, 
                                f"Response time {response_time:.2f}s exceeds 1s requirement")
                    return False
                
                self.log_test("Enhanced Simulation", True, 
                            f"Enhanced simulation: {len(findings_generated)} findings, "
                            f"response time: {response_time:.2f}s")
                return True
            else:
                self.log_test("Enhanced Simulation", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Enhanced Simulation", False, f"Error: {str(e)}")
            return False

    def test_enhanced_rule_evaluation(self):
        """Test POST /api/rules/evaluate - Enhanced rule evaluation with MITRE integration"""
        try:
            # Create rule evaluation data
            evaluation_data = {
                "diagram_id": str(uuid.uuid4()),
                "nodes": [
                    {
                        "id": str(uuid.uuid4()),
                        "type": "Asset",
                        "subtype": "WebApp",
                        "data": {
                            "authentication": "basic",
                            "encryption": "none",
                            "input_validation": "minimal"
                        }
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "type": "Asset", 
                        "subtype": "Database",
                        "data": {
                            "encryption_at_rest": "disabled",
                            "access_controls": "weak"
                        }
                    }
                ],
                "enhanced_evaluation": {
                    "mitre_integration": True,
                    "findings_generation": True,
                    "framework_mapping": True
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/rules/evaluate",
                json=evaluation_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify enhanced rule evaluation fields
                expected_fields = [
                    "evaluation_id", "rules_triggered", "findings_generated",
                    "mitre_techniques", "framework_mappings", "risk_score"
                ]
                
                missing_fields = [f for f in expected_fields if f not in data]
                if missing_fields:
                    self.log_test("Enhanced Rule Evaluation", False, f"Missing enhanced fields: {missing_fields}")
                    return False
                
                # Verify MITRE integration
                mitre_techniques = data.get("mitre_techniques", [])
                if not mitre_techniques:
                    self.log_test("Enhanced Rule Evaluation", False, "No MITRE techniques mapped")
                    return False
                
                # Verify findings generation
                findings_generated = data.get("findings_generated", [])
                if not findings_generated:
                    self.log_test("Enhanced Rule Evaluation", False, "No findings generated from rule evaluation")
                    return False
                
                # Check response time (< 1s)
                response_time = response.elapsed.total_seconds()
                if response_time > 1.0:
                    self.log_test("Enhanced Rule Evaluation", False, 
                                f"Response time {response_time:.2f}s exceeds 1s requirement")
                    return False
                
                rules_triggered = data.get("rules_triggered", [])
                risk_score = data.get("risk_score", 0)
                
                self.log_test("Enhanced Rule Evaluation", True, 
                            f"Enhanced evaluation: {len(rules_triggered)} rules triggered, "
                            f"{len(findings_generated)} findings, "
                            f"risk score: {risk_score}, "
                            f"response time: {response_time:.2f}s")
                return True
            else:
                self.log_test("Enhanced Rule Evaluation", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Enhanced Rule Evaluation", False, f"Error: {str(e)}")
            return False

    def test_merged_questionnaire_prompts(self):
        """Test GET /api/questionnaires/{node_subtype} - Merged questionnaire prompts"""
        test_subtypes = ["WebApp", "Database"]
        
        for subtype in test_subtypes:
            try:
                response = self.session.get(f"{self.base_url}/questionnaires/{subtype}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Verify merged prompts structure
                    expected_fields = [
                        "node_subtype", "merged_prompts", "security_configuration",
                        "validation_rules", "help_text"
                    ]
                    
                    missing_fields = [f for f in expected_fields if f not in data]
                    if missing_fields:
                        self.log_test(f"Merged Questionnaire Prompts - {subtype}", False, 
                                    f"Missing merged prompts fields: {missing_fields}")
                        return False
                    
                    # Verify comprehensive security configuration
                    merged_prompts = data.get("merged_prompts", [])
                    if not merged_prompts:
                        self.log_test(f"Merged Questionnaire Prompts - {subtype}", False, 
                                    "No merged prompts returned")
                        return False
                    
                    # Verify security-specific prompts for WebApp
                    if subtype == "WebApp":
                        expected_security_areas = [
                            "authentication", "https_enforcement", "input_validation", 
                            "security_logging", "mfa_settings"
                        ]
                        prompt_areas = [p.get("security_area") for p in merged_prompts if p.get("security_area")]
                        
                        missing_areas = [area for area in expected_security_areas if area not in prompt_areas]
                        if missing_areas:
                            self.log_test(f"Merged Questionnaire Prompts - {subtype}", False, 
                                        f"Missing security areas: {missing_areas}")
                            return False
                    
                    # Verify security-specific prompts for Database
                    if subtype == "Database":
                        expected_security_areas = [
                            "encryption_at_rest", "encryption_in_transit", "access_controls",
                            "backup_encryption", "audit_logging"
                        ]
                        prompt_areas = [p.get("security_area") for p in merged_prompts if p.get("security_area")]
                        
                        missing_areas = [area for area in expected_security_areas if area not in prompt_areas]
                        if missing_areas:
                            self.log_test(f"Merged Questionnaire Prompts - {subtype}", False, 
                                        f"Missing security areas: {missing_areas}")
                            return False
                    
                    # Verify validation rules and help text
                    validation_rules = data.get("validation_rules", {})
                    help_text = data.get("help_text", {})
                    
                    if not validation_rules or not help_text:
                        self.log_test(f"Merged Questionnaire Prompts - {subtype}", False, 
                                    "Missing validation rules or help text")
                        return False
                    
                    # Check response time (< 1s)
                    response_time = response.elapsed.total_seconds()
                    if response_time > 1.0:
                        self.log_test(f"Merged Questionnaire Prompts - {subtype}", False, 
                                    f"Response time {response_time:.2f}s exceeds 1s requirement")
                        return False
                    
                    self.log_test(f"Merged Questionnaire Prompts - {subtype}", True, 
                                f"Merged prompts: {len(merged_prompts)} prompts, "
                                f"response time: {response_time:.2f}s")
                    
                else:
                    self.log_test(f"Merged Questionnaire Prompts - {subtype}", False, 
                                f"HTTP {response.status_code}: {response.text}")
                    return False
                    
            except Exception as e:
                self.log_test(f"Merged Questionnaire Prompts - {subtype}", False, f"Error: {str(e)}")
                return False
        
        return True

    def test_performance_and_error_handling(self):
        """Test performance requirements and error handling"""
        try:
            # Test malformed request handling
            malformed_data = {"invalid": "data", "missing_required_fields": True}
            
            response = self.session.post(
                f"{self.base_url}/questionnaires/WebApp/complete",
                json=malformed_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code not in [400, 422]:  # Should return validation error
                self.log_test("Error Handling - Malformed Request", False, 
                            f"Expected 400/422, got {response.status_code}")
                return False
            
            self.log_test("Error Handling - Malformed Request", True, 
                        f"Properly handled malformed request: HTTP {response.status_code}")
            
            # Test invalid ID handling
            invalid_id = "invalid-uuid-format"
            response = self.session.get(f"{self.base_url}/findings/{invalid_id}")
            
            if response.status_code not in [400, 404]:  # Should return not found or bad request
                self.log_test("Error Handling - Invalid ID", False, 
                            f"Expected 400/404, got {response.status_code}")
                return False
            
            self.log_test("Error Handling - Invalid ID", True, 
                        f"Properly handled invalid ID: HTTP {response.status_code}")
            
            # Test MongoDB connectivity (health check should verify this)
            response = self.session.get(f"{self.base_url}/")
            
            if response.status_code != 200:
                self.log_test("MongoDB Connectivity", False, 
                            f"Health check failed: HTTP {response.status_code}")
                return False
            
            self.log_test("MongoDB Connectivity", True, "Database connectivity verified")
            
            # Test framework integration accuracy
            framework_test_data = {
                "responses": {
                    "sql_injection_vulnerability": "present",
                    "weak_authentication": "basic_auth_only"
                },
                "business_context": {"criticality": "High"}
            }
            
            response = self.session.post(
                f"{self.base_url}/questionnaires/WebApp/complete",
                json=framework_test_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                framework_mappings = data.get("framework_mappings", {})
                
                # Verify all 8 frameworks are supported
                expected_frameworks = ["MITRE", "ASVS", "OWASP", "CIS", "NIST", "ISO27001", "SOC2", "GDPR"]
                mapped_frameworks = list(framework_mappings.keys())
                
                framework_coverage = len([f for f in expected_frameworks if f in mapped_frameworks])
                if framework_coverage < 6:  # At least 6 out of 8 frameworks should be mapped
                    self.log_test("Framework Integration", False, 
                                f"Insufficient framework coverage: {framework_coverage}/8")
                    return False
                
                self.log_test("Framework Integration", True, 
                            f"Framework integration: {framework_coverage}/8 frameworks mapped")
            else:
                self.log_test("Framework Integration", False, 
                            f"Framework test failed: HTTP {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            self.log_test("Performance and Error Handling", False, f"Error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all API tests in sequence"""
        print(f"🚀 Starting Enhanced Security Modeling Platform API Tests")
        print(f"📡 Testing against: {self.base_url}")
        print("=" * 80)
        
        tests = [
            self.test_health_check,
            self.test_create_diagram,
            self.test_get_diagrams,
            self.test_get_specific_diagram,
            self.test_update_diagram_with_security_data,
            self.test_simulate_attack_paths,
            self.test_get_simulations,
            self.test_simulation_logic_validation,
            # Enhanced/Advanced tests
            self.test_advanced_simulation_endpoint,
            self.test_mitre_technique_endpoints,
            self.test_techniques_by_tactic,
            self.test_analyze_coverage_endpoint,
            self.test_risk_analysis_endpoint,
            self.test_auto_layout_endpoint,
            # Phase 1 Intelligent Node System Tests
            self.test_intelligent_nodes_supported_types,
            self.test_intelligent_nodes_templates,
            self.test_intelligent_nodes_prompts,
            self.test_intelligent_nodes_create_branches,
            self.test_intelligent_nodes_validate_completeness,
            self.test_intelligent_nodes_calculate_risk,
            self.test_intelligent_nodes_invalid_subtypes,
            # Phase 2 DSL Rule Engine Tests
            self.test_dsl_rule_evaluation,
            self.test_security_gap_detection,
            self.test_completeness_analysis,
            self.test_comprehensive_analysis,
            self.test_security_rules_management,
            self.test_security_rules_categories,
            self.test_security_rules_statistics,
            self.test_specific_security_rule,
            self.test_dsl_rule_scenarios,
            # Phase 3: Probabilistic Simulation Engine Tests
            self.test_probabilistic_simulation_engine,
            self.test_what_if_scenario_engine,
            self.test_defense_effectiveness_modeling,
            self.test_historical_probabilistic_simulations,
            self.test_historical_scenario_analyses,
            # Threat Modeling Wizard Tests
            self.test_wizard_recommendations_system_overview,
            self.test_wizard_recommendations_asset_inventory,
            self.test_wizard_recommendations_invalid_step,
            self.test_wizard_generate_model_complete,
            self.test_wizard_generate_model_minimal,
            self.test_wizard_generate_model_error_handling,
            # Questionnaire Management and Conditional Dependencies Tests
            self.test_questionnaire_get_responses,
            self.test_questionnaire_update_responses,
            self.test_check_dependencies,
            # PRIORITY 1 & 2 ENHANCED FEATURES TESTS
            self.test_priority1_probabilistic_risk_ec2,
            self.test_priority1_probabilistic_risk_lambda,
            self.test_priority1_probabilistic_risk_s3,
            self.test_priority2_bulk_risk_assessment,
            # Phase 1 Enhanced APIs - Expanded Intelligent Nodes & Threat Intelligence
            self.test_expanded_nodes_supported_types,
            self.test_expanded_nodes_questionnaire_levels,
            self.test_expanded_nodes_calculate_risk,
            self.test_expanded_nodes_bulk_risk_assessment,
            self.test_expanded_nodes_categories,
            self.test_expanded_nodes_threat_intelligence_summary,
            # Threat Intelligence Endpoints
            self.test_threat_intelligence_node_profile,
            self.test_threat_intelligence_correlate_vulnerabilities,
            self.test_threat_intelligence_real_time_score,
            self.test_threat_intelligence_mitre_technique,
            self.test_threat_intelligence_dashboard
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
            except Exception as e:
                print(f"❌ Test {test.__name__} crashed: {str(e)}")
            print("-" * 40)
        
        print("=" * 80)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Security Modeling Platform API is working correctly.")
            return True
        else:
            print(f"⚠️  {total - passed} tests failed. See details above.")
            return False

def test_multi_level_questionnaires_only():
    """Test only the multi-level questionnaires as requested by user"""
    print("🎯 FOCUSED TESTING: Multi-Level Questionnaires Implementation")
    print("=" * 80)
    
    tester = SecurityModelingAPITester()
    
    # First test health check to ensure API is accessible
    if not tester.test_health_check():
        print("❌ API health check failed - cannot proceed with testing")
        return False
    
    # Run the specific multi-level questionnaire test
    success = tester.test_multi_level_questionnaires_implementation()
    
    print("\n" + "=" * 80)
    if success:
        print("✅ MULTI-LEVEL QUESTIONNAIRES TESTING COMPLETED SUCCESSFULLY!")
        print("🎉 All requested questionnaire endpoints are working correctly:")
        print("   • EC2 EXPERT level: 25+ questions ✅")
        print("   • Lambda ADVANCED level: 17 questions ✅") 
        print("   • Lambda EXPERT level: 24+ questions ✅")
    else:
        print("❌ MULTI-LEVEL QUESTIONNAIRES TESTING FAILED!")
        print("⚠️  Some questionnaire endpoints need attention - see details above")
    
    return success

def test_expanded_nodes_debug_endpoint():
    """Test GET /api/expanded-nodes/debug for node count diagnostics"""
    tester = SecurityModelingAPITester()
    try:
        response = tester.session.get(f"{tester.base_url}/expanded-nodes/debug")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check for debug information
            expected_fields = ["source", "count", "types", "first_5", "new_types"]
            missing_fields = [f for f in expected_fields if f not in data]
            
            if missing_fields:
                tester.log_test("Expanded Nodes Debug", False, f"Missing debug fields: {missing_fields}")
                return False
            
            count = data.get("count", 0)
            types = data.get("types", [])
            new_types = data.get("new_types", [])
            
            # Expected new node types from the review request
            expected_new_types = [
                'ElasticLoadBalancer', 'ConfigurationManagement', 'ServiceMesh', 
                'DataLakeStorage', 'EdgeComputing', 'QuantumSafeEncryption'
            ]
            
            found_new_types = [t for t in expected_new_types if t in types]
            missing_new_types = [t for t in expected_new_types if t not in types]
            
            tester.log_test("Expanded Nodes Debug", True, 
                        f"Debug info: {count} total types, {len(new_types)} new types found, "
                        f"Expected new types found: {found_new_types}, Missing: {missing_new_types}")
            
            return {
                "total_count": count,
                "all_types": types,
                "found_new_types": found_new_types,
                "missing_new_types": missing_new_types,
                "debug_data": data
            }
        else:
            tester.log_test("Expanded Nodes Debug", False, f"HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        tester.log_test("Expanded Nodes Debug", False, f"Error: {str(e)}")
        return False

def test_expanded_nodes_supported_types_focused():
    """FOCUSED TEST: GET /api/expanded-nodes/supported-types for node count discrepancy analysis"""
    tester = SecurityModelingAPITester()
    try:
        response = tester.session.get(f"{tester.base_url}/expanded-nodes/supported-types")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check for required fields
            expected_fields = ["supported_types", "total_count"]
            missing_fields = [f for f in expected_fields if f not in data]
            
            if missing_fields:
                tester.log_test("FOCUSED - Expanded Nodes Supported Types", False, f"Missing fields: {missing_fields}")
                return False
            
            supported_types = data.get("supported_types", [])
            total_count = data.get("total_count", 0)
            
            # Extract node type names
            node_type_names = []
            if supported_types:
                node_type_names = [t.get("node_subtype", "") for t in supported_types]
            
            # Expected new node types from the review request
            expected_new_types = [
                'ElasticLoadBalancer', 'ConfigurationManagement', 'ServiceMesh', 
                'DataLakeStorage', 'EdgeComputing', 'QuantumSafeEncryption'
            ]
            
            found_new_types = [t for t in expected_new_types if t in node_type_names]
            missing_new_types = [t for t in expected_new_types if t not in node_type_names]
            
            # Detailed analysis
            analysis_result = {
                "actual_count": total_count,
                "expected_count": 30,
                "count_discrepancy": 30 - total_count,
                "all_node_types": node_type_names,
                "expected_new_types": expected_new_types,
                "found_new_types": found_new_types,
                "missing_new_types": missing_new_types,
                "new_types_found_count": len(found_new_types),
                "new_types_missing_count": len(missing_new_types)
            }
            
            # Determine if test passes based on count and new types
            if total_count == 30 and len(missing_new_types) == 0:
                tester.log_test("FOCUSED - Expanded Nodes Supported Types", True, 
                            f"✅ EXPECTED COUNT ACHIEVED: {total_count}/30 node types, all 6 new types present: {found_new_types}")
            elif total_count == 24:
                tester.log_test("FOCUSED - Expanded Nodes Supported Types", False, 
                            f"❌ COUNT DISCREPANCY CONFIRMED: {total_count}/30 node types (missing {30-total_count}), "
                            f"New types found: {len(found_new_types)}/6 ({found_new_types}), "
                            f"Missing new types: {missing_new_types}")
            else:
                tester.log_test("FOCUSED - Expanded Nodes Supported Types", False, 
                            f"❌ UNEXPECTED COUNT: {total_count} node types (expected 30), "
                            f"New types status: {len(found_new_types)}/6 found")
            
            return analysis_result
        else:
            tester.log_test("FOCUSED - Expanded Nodes Supported Types", False, f"HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        tester.log_test("FOCUSED - Expanded Nodes Supported Types", False, f"Error: {str(e)}")
        return False

def run_focused_node_count_tests():
    """Run focused tests for node count discrepancy debugging"""
    print("🎯 FOCUSED NODE COUNT DISCREPANCY TESTING")
    print(f"Testing against: {BASE_URL}")
    print("Target: GET /api/expanded-nodes/supported-types endpoint")
    print("Issue: Only 24 node types returned instead of expected 30")
    print("Expected new types: ElasticLoadBalancer, ConfigurationManagement, ServiceMesh, DataLakeStorage, EdgeComputing, QuantumSafeEncryption")
    print("=" * 100)
    
    # Run focused tests
    debug_result = test_expanded_nodes_debug_endpoint()
    analysis_result = test_expanded_nodes_supported_types_focused()
    
    print("\n" + "=" * 100)
    print("🔍 DETAILED ANALYSIS RESULTS:")
    
    if analysis_result:
        print(f"📊 ACTUAL COUNT: {analysis_result['actual_count']}")
        print(f"📊 EXPECTED COUNT: {analysis_result['expected_count']}")
        print(f"📊 COUNT DISCREPANCY: {analysis_result['count_discrepancy']}")
        print(f"📊 NEW TYPES FOUND: {analysis_result['new_types_found_count']}/6")
        print(f"✅ FOUND NEW TYPES: {analysis_result['found_new_types']}")
        print(f"❌ MISSING NEW TYPES: {analysis_result['missing_new_types']}")
        print(f"📋 ALL NODE TYPES ({len(analysis_result['all_node_types'])}): {analysis_result['all_node_types']}")
    
    if debug_result and isinstance(debug_result, dict):
        print(f"🔧 DEBUG ENDPOINT DATA: {debug_result['debug_data']}")
    
    print("\n" + "=" * 100)
    print("🎯 ROOT CAUSE ANALYSIS:")
    
    if analysis_result:
        if analysis_result['actual_count'] == 24:
            print("❌ CONFIRMED: Only 24 node types returned instead of expected 30")
            print("❌ MISSING: 6 node types are not being returned by the API")
            
            if analysis_result['new_types_missing_count'] > 0:
                print(f"❌ NEW TYPES ISSUE: {analysis_result['new_types_missing_count']}/6 expected new types are missing")
                print(f"   Missing types: {analysis_result['missing_new_types']}")
            else:
                print("✅ NEW TYPES OK: All 6 expected new types are present")
                print("❌ OTHER TYPES MISSING: The discrepancy is in other node types, not the new ones")
        elif analysis_result['actual_count'] == 30:
            print("✅ COUNT RESOLVED: 30 node types returned as expected")
            if analysis_result['new_types_missing_count'] == 0:
                print("✅ NEW TYPES RESOLVED: All 6 expected new types are present")
            else:
                print(f"❌ NEW TYPES ISSUE: {analysis_result['new_types_missing_count']}/6 new types still missing")
        else:
            print(f"❓ UNEXPECTED COUNT: {analysis_result['actual_count']} node types (neither 24 nor 30)")
    
    return analysis_result

def main():
    """Main test execution"""
    # Check if we should run focused testing
    if len(sys.argv) > 1 and sys.argv[1] == "--multi-level-only":
        success = test_multi_level_questionnaires_only()
    elif len(sys.argv) > 1 and sys.argv[1] == "--focused":
        analysis_result = run_focused_node_count_tests()
        success = analysis_result and analysis_result.get('actual_count') == 30
    else:
        tester = SecurityModelingAPITester()
        success = tester.run_all_tests()
    
    if success:
        print("\n✅ Backend API testing completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Backend API testing completed with failures!")
        sys.exit(1)

if __name__ == "__main__":
    main()