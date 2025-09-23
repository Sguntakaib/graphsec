#!/usr/bin/env python3
"""
Phase 1 Enhanced APIs Testing for Security Modeling Platform
Tests the specific EXPANDED INTELLIGENT NODES and THREAT INTELLIGENCE endpoints
"""

import requests
import json
import uuid
from datetime import datetime, timezone
import sys

# Use the production URL from frontend/.env
BASE_URL = "https://rule-alignment.preview.emergentagent.com/api"

class Phase1EnhancedAPITester:
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
    
    # ============================================================================
    # EXPANDED INTELLIGENT NODES ENDPOINTS (6 endpoints)
    # ============================================================================
    
    def test_expanded_nodes_supported_types(self):
        """Test GET /api/expanded-nodes/supported-types - Should return 25+ comprehensive node types"""
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
                by_category = data.get("by_category", {})
                
                # Check if we have 25+ node types as expected
                if total_count < 25:
                    self.log_test("Expanded Nodes - Supported Types", False, 
                                f"Expected 25+ node types, got {total_count}")
                    return False
                
                # Check for expected categories
                expected_categories = [
                    "Cloud Infrastructure", "Security Services", "Network Components", 
                    "Container & DevOps", "Data & Storage", "Compute Services", 
                    "Monitoring & Logging", "Application Services"
                ]
                
                found_categories = set(categories)
                missing_categories = [cat for cat in expected_categories if cat not in found_categories]
                
                if missing_categories:
                    self.log_test("Expanded Nodes - Supported Types", False, 
                                f"Missing expected categories: {missing_categories}. Found: {list(found_categories)}")
                    return False
                
                # Check for expected node types
                expected_node_types = [
                    "EC2", "Lambda", "S3", "RDS", "VPC", "WAF", "IAM", 
                    "Kubernetes", "CICD", "LoadBalancer", "KMS", "CloudTrail"
                ]
                
                found_node_types = [t.get("node_subtype") for t in supported_types]
                missing_node_types = [nt for nt in expected_node_types if nt not in found_node_types]
                
                if missing_node_types:
                    self.log_test("Expanded Nodes - Supported Types", False, 
                                f"Missing expected node types: {missing_node_types}")
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
    
    def test_expanded_nodes_questionnaire(self):
        """Test GET /api/expanded-nodes/{node_subtype}/questionnaire/{level}"""
        test_cases = [
            {"node_type": "EC2", "level": "basic", "expected_questions": (5, 8)},
            {"node_type": "Lambda", "level": "advanced", "expected_questions": (15, 20)},
            {"node_type": "RDS", "level": "expert", "expected_questions": (25, 30)},
            {"node_type": "Kubernetes", "level": "basic", "expected_questions": (5, 8)},
            {"node_type": "S3", "level": "advanced", "expected_questions": (15, 20)},
            {"node_type": "VPC", "level": "expert", "expected_questions": (25, 30)},
            {"node_type": "WAF", "level": "basic", "expected_questions": (5, 8)},
            {"node_type": "IAM", "level": "advanced", "expected_questions": (15, 20)}
        ]
        
        for test_case in test_cases:
            node_type = test_case["node_type"]
            level = test_case["level"]
            min_questions, max_questions = test_case["expected_questions"]
            
            try:
                response = self.session.get(
                    f"{self.base_url}/expanded-nodes/{node_type}/questionnaire/{level}"
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check for required fields
                    expected_fields = ["node_subtype", "questionnaire_level", "questions", "question_count"]
                    missing_fields = [f for f in expected_fields if f not in data]
                    
                    if missing_fields:
                        self.log_test(f"Expanded Questionnaire - {node_type} {level}", False, 
                                    f"Missing fields: {missing_fields}")
                        return False
                    
                    questions = data.get("questions", [])
                    question_count = data.get("question_count", 0)
                    
                    # Verify question count is within expected range
                    if not (min_questions <= question_count <= max_questions):
                        self.log_test(f"Expanded Questionnaire - {node_type} {level}", False, 
                                    f"Expected {min_questions}-{max_questions} questions, got {question_count}")
                        return False
                    
                    # Verify question structure
                    if questions:
                        first_question = questions[0]
                        required_question_fields = ["id", "question", "type", "options", "help_text", "related_branch"]
                        missing_question_fields = [f for f in required_question_fields if f not in first_question]
                        
                        if missing_question_fields:
                            self.log_test(f"Expanded Questionnaire - {node_type} {level}", False, 
                                        f"Missing question fields: {missing_question_fields}")
                            return False
                    
                    self.log_test(f"Expanded Questionnaire - {node_type} {level}", True, 
                                f"Retrieved {question_count} questions")
                    
                elif response.status_code == 400:
                    self.log_test(f"Expanded Questionnaire - {node_type} {level}", False, 
                                f"Invalid level parameter: {response.text}")
                    return False
                elif response.status_code == 404:
                    self.log_test(f"Expanded Questionnaire - {node_type} {level}", False, 
                                f"Questionnaire not found")
                    return False
                else:
                    self.log_test(f"Expanded Questionnaire - {node_type} {level}", False, 
                                f"HTTP {response.status_code}: {response.text}")
                    return False
                    
            except Exception as e:
                self.log_test(f"Expanded Questionnaire - {node_type} {level}", False, f"Error: {str(e)}")
                return False
        
        return True
    
    def test_expanded_nodes_calculate_risk(self):
        """Test POST /api/expanded-nodes/{node_subtype}/calculate-risk with probabilistic modeling"""
        test_cases = [
            {
                "node_type": "EC2",
                "responses": {
                    "instance_type": "t3.large",
                    "public_access": "yes",
                    "security_groups": "default",
                    "encryption": "disabled",
                    "monitoring": "basic"
                },
                "business_context": {
                    "criticality": "high",
                    "data_classification": "confidential",
                    "compliance_requirements": ["SOC2", "GDPR"]
                }
            },
            {
                "node_type": "RDS",
                "responses": {
                    "engine": "postgresql",
                    "public_access": "no",
                    "encryption_at_rest": "enabled",
                    "backup_retention": "7_days",
                    "multi_az": "enabled"
                },
                "business_context": {
                    "criticality": "critical",
                    "data_classification": "restricted",
                    "compliance_requirements": ["PCI-DSS", "HIPAA"]
                }
            },
            {
                "node_type": "Lambda",
                "responses": {
                    "runtime": "python3.9",
                    "vpc_config": "enabled",
                    "environment_variables": "encrypted",
                    "execution_role": "least_privilege",
                    "logging": "enabled"
                },
                "business_context": {
                    "criticality": "medium",
                    "data_classification": "internal",
                    "compliance_requirements": ["SOC2"]
                }
            },
            {
                "node_type": "Kubernetes",
                "responses": {
                    "version": "1.28",
                    "rbac_enabled": "yes",
                    "network_policies": "enabled",
                    "pod_security_standards": "restricted",
                    "secrets_encryption": "enabled"
                },
                "business_context": {
                    "criticality": "high",
                    "data_classification": "confidential",
                    "compliance_requirements": ["SOC2", "ISO27001"]
                }
            }
        ]
        
        for test_case in test_cases:
            node_type = test_case["node_type"]
            
            try:
                response = self.session.post(
                    f"{self.base_url}/expanded-nodes/{node_type}/calculate-risk",
                    json=test_case,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check for required fields
                    expected_fields = ["node_subtype", "risk_assessment", "security_recommendations"]
                    missing_fields = [f for f in expected_fields if f not in data]
                    
                    if missing_fields:
                        self.log_test(f"Expanded Risk Calculation - {node_type}", False, 
                                    f"Missing fields: {missing_fields}")
                        return False
                    
                    risk_assessment = data.get("risk_assessment", {})
                    
                    # Check for probabilistic modeling fields
                    expected_risk_fields = [
                        "confidence_interval", "threat_likelihood", "probabilistic_score"
                    ]
                    missing_risk_fields = [f for f in expected_risk_fields if f not in risk_assessment]
                    
                    if missing_risk_fields:
                        self.log_test(f"Expanded Risk Calculation - {node_type}", False, 
                                    f"Missing probabilistic modeling fields: {missing_risk_fields}")
                        return False
                    
                    probabilistic_score = risk_assessment.get("probabilistic_score", 0)
                    confidence_interval = risk_assessment.get("confidence_interval", {})
                    threat_likelihood = risk_assessment.get("threat_likelihood", 0)
                    
                    # Verify probabilistic score is valid
                    if not (0 <= probabilistic_score <= 10):
                        self.log_test(f"Expanded Risk Calculation - {node_type}", False, 
                                    f"Invalid probabilistic score: {probabilistic_score}")
                        return False
                    
                    self.log_test(f"Expanded Risk Calculation - {node_type}", True, 
                                f"Probabilistic score: {probabilistic_score}, likelihood: {threat_likelihood}")
                    
                elif response.status_code == 500:
                    self.log_test(f"Expanded Risk Calculation - {node_type}", False, 
                                f"Risk calculation failed: {response.text}")
                    return False
                else:
                    self.log_test(f"Expanded Risk Calculation - {node_type}", False, 
                                f"HTTP {response.status_code}: {response.text}")
                    return False
                    
            except Exception as e:
                self.log_test(f"Expanded Risk Calculation - {node_type}", False, f"Error: {str(e)}")
                return False
        
        return True
    
    def test_bulk_risk_assessment(self):
        """Test POST /api/expanded-nodes/bulk-risk-assessment"""
        try:
            bulk_request = {
                "nodes": [
                    {
                        "node_subtype": "EC2",
                        "responses": {
                            "instance_type": "t3.large",
                            "public_access": "yes",
                            "security_groups": "restrictive",
                            "encryption": "enabled"
                        }
                    },
                    {
                        "node_subtype": "RDS",
                        "responses": {
                            "engine": "postgresql",
                            "public_access": "no",
                            "encryption_at_rest": "enabled",
                            "backup_retention": "30_days"
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
                    "compliance_requirements": ["SOC2", "GDPR"]
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/expanded-nodes/bulk-risk-assessment",
                json=bulk_request,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for required fields
                expected_fields = ["assessment_results", "aggregated_metrics", "cross_node_correlations"]
                missing_fields = [f for f in expected_fields if f not in data]
                
                if missing_fields:
                    self.log_test("Bulk Risk Assessment", False, f"Missing fields: {missing_fields}")
                    return False
                
                assessment_results = data.get("assessment_results", [])
                aggregated_metrics = data.get("aggregated_metrics", {})
                cross_node_correlations = data.get("cross_node_correlations", [])
                
                # Verify we got results for all nodes
                if len(assessment_results) != 3:
                    self.log_test("Bulk Risk Assessment", False, 
                                f"Expected 3 assessment results, got {len(assessment_results)}")
                    return False
                
                # Check for aggregated metrics
                if "overall_risk_score" not in aggregated_metrics:
                    self.log_test("Bulk Risk Assessment", False, "Missing overall_risk_score in aggregated metrics")
                    return False
                
                self.log_test("Bulk Risk Assessment", True, 
                            f"Assessed {len(assessment_results)} nodes, {len(cross_node_correlations)} correlations found")
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
                expected_fields = ["categories", "category_descriptions", "node_type_mappings"]
                missing_fields = [f for f in expected_fields if f not in data]
                
                if missing_fields:
                    self.log_test("Expanded Nodes - Categories", False, f"Missing fields: {missing_fields}")
                    return False
                
                categories = data.get("categories", [])
                category_descriptions = data.get("category_descriptions", {})
                node_type_mappings = data.get("node_type_mappings", {})
                
                # Check for expected categories
                expected_categories = [
                    "Cloud Infrastructure", "Security Services", "Network Components", 
                    "Container & DevOps", "Data & Storage", "Compute Services", 
                    "Monitoring & Logging", "Application Services"
                ]
                
                missing_categories = [cat for cat in expected_categories if cat not in categories]
                if missing_categories:
                    self.log_test("Expanded Nodes - Categories", False, 
                                f"Missing expected categories: {missing_categories}")
                    return False
                
                # Verify each category has descriptions and mappings
                for category in categories:
                    if category not in category_descriptions:
                        self.log_test("Expanded Nodes - Categories", False, 
                                    f"Missing description for category: {category}")
                        return False
                    
                    if category not in node_type_mappings:
                        self.log_test("Expanded Nodes - Categories", False, 
                                    f"Missing node type mappings for category: {category}")
                        return False
                
                self.log_test("Expanded Nodes - Categories", True, 
                            f"Retrieved {len(categories)} categories with descriptions and mappings")
                return True
            else:
                self.log_test("Expanded Nodes - Categories", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Expanded Nodes - Categories", False, f"Error: {str(e)}")
            return False
    
    def test_threat_intelligence_summary(self):
        """Test POST /api/expanded-nodes/threat-intelligence-summary"""
        try:
            request_data = {
                "node_types": ["EC2", "RDS", "Lambda", "Kubernetes", "S3"],
                "include_cve_data": True,
                "include_mitre_techniques": True,
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
                expected_fields = ["threat_summary", "cve_data", "mitre_techniques", "aggregated_intelligence"]
                missing_fields = [f for f in expected_fields if f not in data]
                
                if missing_fields:
                    self.log_test("Threat Intelligence Summary", False, f"Missing fields: {missing_fields}")
                    return False
                
                threat_summary = data.get("threat_summary", {})
                cve_data = data.get("cve_data", {})
                mitre_techniques = data.get("mitre_techniques", {})
                
                # Verify we got data for requested node types
                requested_types = set(request_data["node_types"])
                summary_types = set(threat_summary.keys())
                
                if not requested_types.issubset(summary_types):
                    missing_types = requested_types - summary_types
                    self.log_test("Threat Intelligence Summary", False, 
                                f"Missing threat summary for node types: {missing_types}")
                    return False
                
                self.log_test("Threat Intelligence Summary", True, 
                            f"Retrieved threat intelligence for {len(summary_types)} node types")
                return True
            else:
                self.log_test("Threat Intelligence Summary", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Threat Intelligence Summary", False, f"Error: {str(e)}")
            return False
    
    # ============================================================================
    # THREAT INTELLIGENCE ENDPOINTS (5 endpoints)
    # ============================================================================
    
    def test_threat_intelligence_node_profile(self):
        """Test GET /api/threat-intelligence/node/{node_type}/profile"""
        test_node_types = ["EC2", "Lambda", "S3", "RDS", "Kubernetes"]
        
        for node_type in test_node_types:
            try:
                response = self.session.get(f"{self.base_url}/threat-intelligence/node/{node_type}/profile")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check for required fields
                    expected_fields = ["node_type", "threat_profile", "cve_data", "recent_threats", "attack_vectors", "mitre_techniques"]
                    missing_fields = [f for f in expected_fields if f not in data]
                    
                    if missing_fields:
                        self.log_test(f"Threat Intelligence Profile - {node_type}", False, 
                                    f"Missing fields: {missing_fields}")
                        return False
                    
                    threat_profile = data.get("threat_profile", {})
                    cve_data = data.get("cve_data", {})
                    recent_threats = data.get("recent_threats", [])
                    attack_vectors = data.get("attack_vectors", [])
                    mitre_techniques = data.get("mitre_techniques", [])
                    
                    # Verify comprehensive threat profile
                    if not threat_profile:
                        self.log_test(f"Threat Intelligence Profile - {node_type}", False, 
                                    "Empty threat profile")
                        return False
                    
                    self.log_test(f"Threat Intelligence Profile - {node_type}", True, 
                                f"Profile: {len(recent_threats)} recent threats, {len(attack_vectors)} attack vectors, {len(mitre_techniques)} MITRE techniques")
                    
                elif response.status_code == 404:
                    self.log_test(f"Threat Intelligence Profile - {node_type}", False, 
                                f"Profile not found for {node_type}")
                    return False
                else:
                    self.log_test(f"Threat Intelligence Profile - {node_type}", False, 
                                f"HTTP {response.status_code}: {response.text}")
                    return False
                    
            except Exception as e:
                self.log_test(f"Threat Intelligence Profile - {node_type}", False, f"Error: {str(e)}")
                return False
        
        return True
    
    def test_correlate_vulnerabilities(self):
        """Test POST /api/threat-intelligence/correlate-vulnerabilities"""
        try:
            request_data = {
                "node_types": ["EC2", "RDS", "Lambda"],
                "vulnerability_sources": ["CVE", "NVD", "vendor_advisories"],
                "correlation_depth": "deep",
                "include_attack_patterns": True
            }
            
            response = self.session.post(
                f"{self.base_url}/threat-intelligence/correlate-vulnerabilities",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for required fields
                expected_fields = ["correlation_results", "shared_attack_patterns", "amplification_factors", "risk_correlations"]
                missing_fields = [f for f in expected_fields if f not in data]
                
                if missing_fields:
                    self.log_test("Correlate Vulnerabilities", False, f"Missing fields: {missing_fields}")
                    return False
                
                correlation_results = data.get("correlation_results", [])
                shared_attack_patterns = data.get("shared_attack_patterns", [])
                amplification_factors = data.get("amplification_factors", {})
                
                # Verify correlation analysis
                if not correlation_results:
                    self.log_test("Correlate Vulnerabilities", False, "No correlation results found")
                    return False
                
                self.log_test("Correlate Vulnerabilities", True, 
                            f"Found {len(correlation_results)} correlations, {len(shared_attack_patterns)} shared patterns")
                return True
            else:
                self.log_test("Correlate Vulnerabilities", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Correlate Vulnerabilities", False, f"Error: {str(e)}")
            return False
    
    def test_real_time_threat_score(self):
        """Test POST /api/threat-intelligence/real-time-score"""
        try:
            request_data = {
                "node_configuration": {
                    "node_type": "EC2",
                    "instance_type": "t3.large",
                    "public_access": True,
                    "security_groups": ["sg-default"],
                    "encryption": False,
                    "monitoring": "basic"
                },
                "security_controls": {
                    "waf_enabled": False,
                    "ids_enabled": True,
                    "backup_enabled": True,
                    "patch_management": "manual"
                },
                "exposure_factors": {
                    "internet_facing": True,
                    "data_classification": "confidential",
                    "compliance_scope": ["SOC2", "GDPR"]
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/threat-intelligence/real-time-score",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for required fields
                expected_fields = ["real_time_score", "score_breakdown", "threat_factors", "mitigation_recommendations"]
                missing_fields = [f for f in expected_fields if f not in data]
                
                if missing_fields:
                    self.log_test("Real-time Threat Score", False, f"Missing fields: {missing_fields}")
                    return False
                
                real_time_score = data.get("real_time_score", 0)
                score_breakdown = data.get("score_breakdown", {})
                threat_factors = data.get("threat_factors", [])
                
                # Verify score is valid
                if not (0 <= real_time_score <= 10):
                    self.log_test("Real-time Threat Score", False, 
                                f"Invalid real-time score: {real_time_score}")
                    return False
                
                # Verify score adjustments based on controls and exposures
                if not score_breakdown:
                    self.log_test("Real-time Threat Score", False, "Missing score breakdown")
                    return False
                
                self.log_test("Real-time Threat Score", True, 
                            f"Real-time score: {real_time_score}, {len(threat_factors)} threat factors")
                return True
            else:
                self.log_test("Real-time Threat Score", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Real-time Threat Score", False, f"Error: {str(e)}")
            return False
    
    def test_mitre_technique_details(self):
        """Test GET /api/threat-intelligence/mitre/{technique_id}"""
        test_techniques = ["T1078", "T1190", "T1055", "T1083", "T1110"]
        
        for technique_id in test_techniques:
            try:
                response = self.session.get(f"{self.base_url}/threat-intelligence/mitre/{technique_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check for required fields (enhanced MITRE details)
                    expected_fields = [
                        "technique_id", "name", "description", "tactics", "platforms",
                        "data_sources", "detection_methods", "mitigations", "threat_intelligence"
                    ]
                    missing_fields = [f for f in expected_fields if f not in data]
                    
                    if missing_fields:
                        self.log_test(f"MITRE Technique Details - {technique_id}", False, 
                                    f"Missing fields: {missing_fields}")
                        return False
                    
                    threat_intelligence = data.get("threat_intelligence", {})
                    
                    # Verify enhanced threat intelligence data
                    if not threat_intelligence:
                        self.log_test(f"MITRE Technique Details - {technique_id}", False, 
                                    "Missing enhanced threat intelligence data")
                        return False
                    
                    self.log_test(f"MITRE Technique Details - {technique_id}", True, 
                                f"Enhanced details: {data.get('name')}")
                    
                elif response.status_code == 404:
                    self.log_test(f"MITRE Technique Details - {technique_id}", False, 
                                f"Technique not found: {technique_id}")
                    return False
                else:
                    self.log_test(f"MITRE Technique Details - {technique_id}", False, 
                                f"HTTP {response.status_code}: {response.text}")
                    return False
                    
            except Exception as e:
                self.log_test(f"MITRE Technique Details - {technique_id}", False, f"Error: {str(e)}")
                return False
        
        return True
    
    def test_threat_intelligence_dashboard(self):
        """Test GET /api/threat-intelligence/dashboard"""
        try:
            response = self.session.get(f"{self.base_url}/threat-intelligence/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for required fields
                expected_fields = [
                    "overall_threat_landscape", "trending_threats", "risk_metrics",
                    "threat_actor_activity", "vulnerability_trends", "mitigation_effectiveness"
                ]
                missing_fields = [f for f in expected_fields if f not in data]
                
                if missing_fields:
                    self.log_test("Threat Intelligence Dashboard", False, f"Missing fields: {missing_fields}")
                    return False
                
                overall_threat_landscape = data.get("overall_threat_landscape", {})
                trending_threats = data.get("trending_threats", [])
                risk_metrics = data.get("risk_metrics", {})
                
                # Verify comprehensive dashboard data
                if not overall_threat_landscape:
                    self.log_test("Threat Intelligence Dashboard", False, "Missing overall threat landscape")
                    return False
                
                if not trending_threats:
                    self.log_test("Threat Intelligence Dashboard", False, "No trending threats data")
                    return False
                
                if not risk_metrics:
                    self.log_test("Threat Intelligence Dashboard", False, "Missing risk metrics")
                    return False
                
                self.log_test("Threat Intelligence Dashboard", True, 
                            f"Dashboard: {len(trending_threats)} trending threats, comprehensive risk metrics")
                return True
            else:
                self.log_test("Threat Intelligence Dashboard", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Threat Intelligence Dashboard", False, f"Error: {str(e)}")
            return False
    
    def test_review_request_specific_apis(self):
        """Test the specific Phase 1 Enhanced APIs mentioned in the review request"""
        print("🎯 REVIEW REQUEST SPECIFIC API TESTS")
        print("-" * 50)
        
        # 1. Multi-Level Questionnaires - Test specific levels for EC2
        print("1. Testing Multi-Level Questionnaires for EC2...")
        levels = [("basic", 5, 8), ("advanced", 15, 20), ("expert", 25, 30)]
        
        for level, min_q, max_q in levels:
            try:
                response = self.session.get(f"{self.base_url}/expanded-nodes/EC2/questionnaire/{level}")
                if response.status_code == 200:
                    data = response.json()
                    if "questions" in data:
                        q_count = len(data["questions"])
                        if min_q <= q_count <= max_q:
                            self.log_test(f"EC2 Questionnaire {level}", True, f"{q_count} questions (expected {min_q}-{max_q})")
                        else:
                            self.log_test(f"EC2 Questionnaire {level}", False, f"{q_count} questions outside range {min_q}-{max_q}")
                    else:
                        self.log_test(f"EC2 Questionnaire {level}", False, "Missing 'questions' field")
                else:
                    self.log_test(f"EC2 Questionnaire {level}", False, f"HTTP {response.status_code}")
            except Exception as e:
                self.log_test(f"EC2 Questionnaire {level}", False, f"Error: {str(e)}")
        
        # 2. Categories API - Test direct category mapping
        print("\n2. Testing Categories API for direct mapping...")
        try:
            response = self.session.get(f"{self.base_url}/expanded-nodes/categories")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and "categories" not in data:
                    category_keys = list(data.keys())
                    if category_keys:
                        self.log_test("Categories API Direct Mapping", True, f"Direct mapping with {len(category_keys)} categories")
                    else:
                        self.log_test("Categories API Direct Mapping", False, "Empty direct mapping")
                else:
                    self.log_test("Categories API Direct Mapping", False, "Returns categories array instead of direct mapping")
            else:
                self.log_test("Categories API Direct Mapping", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Categories API Direct Mapping", False, f"Error: {str(e)}")
        
        # 3. Enhanced Risk Calculation - Test 'risk_factors' field
        print("\n3. Testing Enhanced Risk Calculation for 'risk_factors' field...")
        try:
            test_data = {
                "responses": {
                    "instance_type": "t3.large",
                    "security_groups": "restrictive",
                    "encryption_enabled": True,
                    "monitoring_enabled": True,
                    "backup_strategy": "automated"
                },
                "business_context": {
                    "criticality": "high",
                    "data_classification": "confidential",
                    "compliance_requirements": ["SOC2", "GDPR"]
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/expanded-nodes/EC2/calculate-risk",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "risk_factors" in data:
                    risk_factors = data.get("risk_factors", {})
                    self.log_test("Enhanced Risk Calculation", True, f"'risk_factors' field present with {len(risk_factors)} factors")
                else:
                    self.log_test("Enhanced Risk Calculation", False, "'risk_factors' field missing from response")
            else:
                self.log_test("Enhanced Risk Calculation", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Enhanced Risk Calculation", False, f"Error: {str(e)}")
        
        # 4. Bulk Risk Assessment - Test field names
        print("\n4. Testing Bulk Risk Assessment field names...")
        try:
            test_data = {
                "assessments": [
                    {
                        "node_type": "EC2",
                        "responses": {"instance_type": "t3.large", "security_groups": "restrictive"},
                        "business_context": {"criticality": "high"}
                    },
                    {
                        "node_type": "RDS", 
                        "responses": {"engine": "postgresql", "encryption_enabled": True},
                        "business_context": {"criticality": "critical"}
                    }
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/expanded-nodes/bulk-risk-assessment",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                expected_fields = ["individual_assessments", "overall_risk_summary"]
                missing_fields = [f for f in expected_fields if f not in data]
                
                if not missing_fields:
                    individual_count = len(data.get("individual_assessments", []))
                    self.log_test("Bulk Risk Assessment Fields", True, f"Correct field names: {individual_count} individual assessments")
                else:
                    self.log_test("Bulk Risk Assessment Fields", False, f"Missing expected fields: {missing_fields}")
            else:
                self.log_test("Bulk Risk Assessment Fields", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Bulk Risk Assessment Fields", False, f"Error: {str(e)}")
        
        # 5. Threat Intelligence Summary - Test field names
        print("\n5. Testing Threat Intelligence Summary field names...")
        try:
            test_data = {
                "node_types": ["EC2", "RDS", "S3"],
                "time_range": "30d",
                "include_cve_data": True,
                "threat_sources": ["mitre", "cve", "threat_feeds"]
            }
            
            response = self.session.post(
                f"{self.base_url}/expanded-nodes/threat-intelligence-summary",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                expected_fields = ["node_type_summaries", "cross_cutting_threats", "threat_trends", "recommendations"]
                missing_fields = [f for f in expected_fields if f not in data]
                
                if not missing_fields:
                    node_summaries_count = len(data.get("node_type_summaries", {}))
                    cross_threats_count = len(data.get("cross_cutting_threats", []))
                    self.log_test("Threat Intelligence Summary Fields", True, f"Correct field names: {node_summaries_count} node summaries, {cross_threats_count} cross-cutting threats")
                else:
                    self.log_test("Threat Intelligence Summary Fields", False, f"Missing expected fields: {missing_fields}")
            else:
                self.log_test("Threat Intelligence Summary Fields", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Threat Intelligence Summary Fields", False, f"Error: {str(e)}")

    def run_all_tests(self):
        """Run the specific review request tests"""
        print("🚀 Starting Phase 1 Enhanced APIs Testing - Review Request Focus")
        print(f"📡 Testing against: {self.base_url}")
        print("=" * 80)
        
        # Run the specific review request tests
        self.test_review_request_specific_apis()
        
        # Summary
        print("\n" + "=" * 80)
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed < total:
            print(f"⚠️  {total - passed} tests failed. See details above.")
            failed_tests = [result for result in self.test_results if not result["success"]]
            print("\n❌ FAILED TESTS:")
            for failed in failed_tests:
                print(f"   - {failed['test']}: {failed['message']}")
        else:
            print("✅ All Phase 1 Enhanced API tests passed!")
        
        return passed == total

if __name__ == "__main__":
    tester = Phase1EnhancedAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)