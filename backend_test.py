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

# Use the production URL from frontend/.env
BASE_URL = "https://threatmap-layout.preview.emergentagent.com/api"

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
            self.test_auto_layout_endpoint
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

def main():
    """Main test execution"""
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