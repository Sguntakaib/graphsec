#!/usr/bin/env python3
"""
Enhanced Vulnerability Detection System - Comprehensive Backend API Tests
Tests all new vulnerability detection features including OWASP API Security Top 10 2023,
Enhanced Database Security, ProductDesignSecurity node type, and STRIDE questionnaires.
"""

import requests
import json
import uuid
from datetime import datetime, timezone
import sys

# Use the backend URL from frontend/.env with /api suffix
BASE_URL = "https://apiscan-fix.preview.emergentagent.com/api"

class EnhancedVulnerabilityTester:
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

    # ============================================================================
    # OWASP API Security Top 10 2023 Endpoints Testing
    # ============================================================================
    
    def test_owasp_api1_2023_broken_object_level_authorization(self):
        """Test POST /api/vulnerabilities/analyze/api1-2023 - Broken Object Level Authorization"""
        try:
            request_data = {
                "node_type": "API",
                "security_config": {
                    "object_level_authorization": "none",
                    "user_context_validation": False,
                    "data_sanitization": "no sanitization",
                    "rate_limiting": "none",
                    "business_flow_protection": False
                },
                "endpoints": [
                    {"path": "/api/users/{id}", "method": "GET", "authorization": "none"},
                    {"path": "/api/orders/{id}", "method": "PUT", "authorization": "basic"}
                ],
                "business_flows": [
                    {"name": "user_data_access", "rate_limit": None, "protection": "none"}
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/vulnerabilities/analyze/api1-2023",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure - updated to match actual API response
                expected_fields = ["vulnerabilities", "analysis_type", "total_count", "risk_assessment"]
                missing_fields = [f for f in expected_fields if f not in data]
                
                if missing_fields:
                    self.log_test("OWASP API1-2023", False, f"Missing response fields: {missing_fields}")
                    return False
                
                vulnerabilities = data.get("vulnerabilities", [])
                analysis_type = data.get("analysis_type", "")
                
                # Should generate vulnerabilities for insecure configuration
                if len(vulnerabilities) == 0:
                    self.log_test("OWASP API1-2023", False, "No vulnerabilities generated for insecure API configuration")
                    return False
                
                # Verify OWASP categorization in analysis_type
                if "API1:2023" not in analysis_type:
                    self.log_test("OWASP API1-2023", False, f"Incorrect analysis type: {analysis_type}")
                    return False
                
                self.log_test("OWASP API1-2023", True, 
                            f"Generated {len(vulnerabilities)} vulnerabilities for Broken Object Level Authorization")
                return True
            else:
                self.log_test("OWASP API1-2023", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("OWASP API1-2023", False, f"Error: {str(e)}")
            return False

    def test_owasp_api3_2023_broken_object_property_level_authorization(self):
        """Test POST /api/vulnerabilities/analyze/api3-2023 - Broken Object Property Level Authorization"""
        try:
            request_data = {
                "node_type": "API",
                "security_config": {
                    "property_level_authorization": "none",
                    "field_level_access_control": False,
                    "sensitive_data_exposure": "high",
                    "data_filtering": "none"
                },
                "endpoints": [
                    {"path": "/api/users/profile", "method": "GET", "sensitive_fields": ["ssn", "salary", "medical_records"]},
                    {"path": "/api/admin/users", "method": "GET", "sensitive_fields": ["password_hash", "api_keys"]}
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/vulnerabilities/analyze/api3-2023",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                vulnerabilities = data.get("vulnerabilities", [])
                analysis_type = data.get("analysis_type", "")
                
                if len(vulnerabilities) == 0:
                    self.log_test("OWASP API3-2023", False, "No vulnerabilities generated for property-level authorization issues")
                    return False
                
                if "API3:2023" not in analysis_type:
                    self.log_test("OWASP API3-2023", False, f"Incorrect analysis type: {analysis_type}")
                    return False
                
                self.log_test("OWASP API3-2023", True, 
                            f"Generated {len(vulnerabilities)} vulnerabilities for Broken Object Property Level Authorization")
                return True
            else:
                self.log_test("OWASP API3-2023", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("OWASP API3-2023", False, f"Error: {str(e)}")
            return False

    def test_owasp_api4_2023_unrestricted_resource_consumption(self):
        """Test POST /api/vulnerabilities/analyze/api4-2023 - Unrestricted Resource Consumption"""
        try:
            request_data = {
                "node_type": "API",
                "security_config": {
                    "rate_limiting": "none",
                    "resource_quotas": "none",
                    "request_size_limits": "none",
                    "timeout_controls": "none",
                    "concurrent_request_limits": "none"
                },
                "endpoints": [
                    {"path": "/api/search", "method": "POST", "resource_intensive": True},
                    {"path": "/api/reports/generate", "method": "POST", "resource_intensive": True},
                    {"path": "/api/upload", "method": "POST", "max_file_size": "unlimited"}
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/vulnerabilities/analyze/api4-2023",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                vulnerabilities = data.get("vulnerabilities", [])
                analysis_type = data.get("analysis_type", "")
                
                if len(vulnerabilities) == 0:
                    self.log_test("OWASP API4-2023", False, "No vulnerabilities generated for unrestricted resource consumption")
                    return False
                
                if "API4:2023" not in analysis_type:
                    self.log_test("OWASP API4-2023", False, f"Incorrect analysis type: {analysis_type}")
                    return False
                
                self.log_test("OWASP API4-2023", True, 
                            f"Generated {len(vulnerabilities)} vulnerabilities for Unrestricted Resource Consumption")
                return True
            else:
                self.log_test("OWASP API4-2023", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("OWASP API4-2023", False, f"Error: {str(e)}")
            return False

    def test_owasp_api6_2023_unrestricted_sensitive_business_flows(self):
        """Test POST /api/vulnerabilities/analyze/api6-2023 - Unrestricted Sensitive Business Flows"""
        try:
            request_data = {
                "node_type": "API",
                "security_config": {
                    "business_flow_protection": False,
                    "transaction_monitoring": "none",
                    "anomaly_detection": "none",
                    "flow_rate_limiting": "none"
                },
                "business_flows": [
                    {"name": "password_reset", "rate_limit": None, "protection": "none", "sensitive": True},
                    {"name": "money_transfer", "rate_limit": None, "protection": "none", "sensitive": True},
                    {"name": "account_creation", "rate_limit": None, "protection": "none", "sensitive": True}
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/vulnerabilities/analyze/api6-2023",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                vulnerabilities = data.get("vulnerabilities", [])
                analysis_type = data.get("analysis_type", "")
                
                if len(vulnerabilities) == 0:
                    self.log_test("OWASP API6-2023", False, "No vulnerabilities generated for unrestricted business flows")
                    return False
                
                if "API6:2023" not in analysis_type:
                    self.log_test("OWASP API6-2023", False, f"Incorrect analysis type: {analysis_type}")
                    return False
                
                self.log_test("OWASP API6-2023", True, 
                            f"Generated {len(vulnerabilities)} vulnerabilities for Unrestricted Sensitive Business Flows")
                return True
            else:
                self.log_test("OWASP API6-2023", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("OWASP API6-2023", False, f"Error: {str(e)}")
            return False

    def test_owasp_api7_2023_server_side_request_forgery(self):
        """Test POST /api/vulnerabilities/analyze/api7-2023 - Server-Side Request Forgery"""
        try:
            request_data = {
                "node_type": "API",
                "security_config": {
                    "url_validation": "none",
                    "internal_network_access": "unrestricted",
                    "request_filtering": "none",
                    "whitelist_validation": False
                },
                "endpoints": [
                    {"path": "/api/fetch-url", "method": "POST", "accepts_urls": True},
                    {"path": "/api/webhook", "method": "POST", "accepts_urls": True},
                    {"path": "/api/proxy", "method": "GET", "accepts_urls": True}
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/vulnerabilities/analyze/api7-2023",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                vulnerabilities = data.get("vulnerabilities", [])
                owasp_category = data.get("owasp_category", "")
                
                if len(vulnerabilities) == 0:
                    self.log_test("OWASP API7-2023", False, "No vulnerabilities generated for SSRF risks")
                    return False
                
                if "API7:2023" not in owasp_category:
                    self.log_test("OWASP API7-2023", False, f"Incorrect OWASP category: {owasp_category}")
                    return False
                
                self.log_test("OWASP API7-2023", True, 
                            f"Generated {len(vulnerabilities)} vulnerabilities for Server-Side Request Forgery")
                return True
            else:
                self.log_test("OWASP API7-2023", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("OWASP API7-2023", False, f"Error: {str(e)}")
            return False

    def test_owasp_api9_2023_improper_inventory_management(self):
        """Test POST /api/vulnerabilities/analyze/api9-2023 - Improper Inventory Management"""
        try:
            request_data = {
                "node_type": "API",
                "security_config": {
                    "api_inventory": "none",
                    "version_management": "poor",
                    "deprecated_endpoints": "many",
                    "documentation_accuracy": "poor",
                    "security_testing": "none"
                },
                "endpoints": [
                    {"path": "/api/v1/users", "version": "1.0", "deprecated": True, "documented": False},
                    {"path": "/api/v2/users", "version": "2.0", "deprecated": False, "documented": True},
                    {"path": "/api/internal/debug", "version": "unknown", "deprecated": False, "documented": False}
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/vulnerabilities/analyze/api9-2023",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                vulnerabilities = data.get("vulnerabilities", [])
                owasp_category = data.get("owasp_category", "")
                
                if len(vulnerabilities) == 0:
                    self.log_test("OWASP API9-2023", False, "No vulnerabilities generated for inventory management issues")
                    return False
                
                if "API9:2023" not in owasp_category:
                    self.log_test("OWASP API9-2023", False, f"Incorrect OWASP category: {owasp_category}")
                    return False
                
                self.log_test("OWASP API9-2023", True, 
                            f"Generated {len(vulnerabilities)} vulnerabilities for Improper Inventory Management")
                return True
            else:
                self.log_test("OWASP API9-2023", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("OWASP API9-2023", False, f"Error: {str(e)}")
            return False

    # ============================================================================
    # Enhanced Database Security Endpoints Testing
    # ============================================================================
    
    def test_database_privilege_escalation(self):
        """Test POST /api/vulnerabilities/analyze/privilege-escalation"""
        try:
            request_data = {
                "node_type": "Database",
                "security_config": {
                    "privilege_management": "static user privileges",
                    "role_based_access": False,
                    "privilege_escalation_monitoring": False,
                    "admin_account_security": "weak",
                    "service_account_management": "poor"
                },
                "database_config": {
                    "type": "PostgreSQL",
                    "version": "12.0",
                    "users": [
                        {"name": "app_user", "privileges": ["SELECT", "INSERT", "UPDATE", "DELETE"], "admin": False},
                        {"name": "admin_user", "privileges": ["ALL"], "admin": True}
                    ]
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/vulnerabilities/analyze/privilege-escalation",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                vulnerabilities = data.get("vulnerabilities", [])
                
                if len(vulnerabilities) == 0:
                    self.log_test("Database Privilege Escalation", False, "No vulnerabilities generated for privilege escalation risks")
                    return False
                
                self.log_test("Database Privilege Escalation", True, 
                            f"Generated {len(vulnerabilities)} vulnerabilities for privilege escalation analysis")
                return True
            else:
                self.log_test("Database Privilege Escalation", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Database Privilege Escalation", False, f"Error: {str(e)}")
            return False

    def test_database_config_drift(self):
        """Test POST /api/vulnerabilities/analyze/config-drift"""
        try:
            request_data = {
                "node_type": "Database",
                "security_config": {
                    "change_management": "no change management",
                    "configuration_monitoring": False,
                    "baseline_comparison": False,
                    "automated_compliance_checks": False,
                    "drift_detection": "none"
                },
                "configuration_state": {
                    "security_settings": {
                        "ssl_enabled": False,
                        "encryption_at_rest": False,
                        "audit_logging": False,
                        "password_policy": "weak"
                    },
                    "baseline_deviation": "high"
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/vulnerabilities/analyze/config-drift",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                vulnerabilities = data.get("vulnerabilities", [])
                
                if len(vulnerabilities) == 0:
                    self.log_test("Database Config Drift", False, "No vulnerabilities generated for configuration drift")
                    return False
                
                self.log_test("Database Config Drift", True, 
                            f"Generated {len(vulnerabilities)} vulnerabilities for configuration drift analysis")
                return True
            else:
                self.log_test("Database Config Drift", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Database Config Drift", False, f"Error: {str(e)}")
            return False

    def test_database_advanced_injection(self):
        """Test POST /api/vulnerabilities/analyze/advanced-injection"""
        try:
            request_data = {
                "node_type": "Database",
                "security_config": {
                    "stored_procedure_security": "no security measures",
                    "dynamic_query_protection": False,
                    "input_sanitization": "none",
                    "parameterized_queries": False,
                    "sql_injection_prevention": "none"
                },
                "application_interfaces": [
                    {"type": "web_app", "input_validation": "none", "query_type": "dynamic"},
                    {"type": "api", "input_validation": "basic", "query_type": "stored_procedures"},
                    {"type": "reporting", "input_validation": "none", "query_type": "dynamic"}
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/vulnerabilities/analyze/advanced-injection",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                vulnerabilities = data.get("vulnerabilities", [])
                
                if len(vulnerabilities) == 0:
                    self.log_test("Database Advanced Injection", False, "No vulnerabilities generated for advanced injection analysis")
                    return False
                
                self.log_test("Database Advanced Injection", True, 
                            f"Generated {len(vulnerabilities)} vulnerabilities for advanced injection analysis")
                return True
            else:
                self.log_test("Database Advanced Injection", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Database Advanced Injection", False, f"Error: {str(e)}")
            return False

    def test_database_insider_threat(self):
        """Test POST /api/vulnerabilities/analyze/insider-threat"""
        try:
            request_data = {
                "node_type": "Database",
                "security_config": {
                    "user_activity_monitoring": "no activity monitoring",
                    "privileged_user_monitoring": False,
                    "data_access_logging": False,
                    "behavioral_analytics": False,
                    "insider_threat_detection": "none"
                },
                "access_patterns": {
                    "privileged_users": 5,
                    "data_access_frequency": "high",
                    "after_hours_access": "frequent",
                    "unusual_query_patterns": "detected"
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/vulnerabilities/analyze/insider-threat",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                vulnerabilities = data.get("vulnerabilities", [])
                
                if len(vulnerabilities) == 0:
                    self.log_test("Database Insider Threat", False, "No vulnerabilities generated for insider threat analysis")
                    return False
                
                self.log_test("Database Insider Threat", True, 
                            f"Generated {len(vulnerabilities)} vulnerabilities for insider threat analysis")
                return True
            else:
                self.log_test("Database Insider Threat", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Database Insider Threat", False, f"Error: {str(e)}")
            return False

    def test_database_backup_security(self):
        """Test POST /api/vulnerabilities/analyze/backup-security"""
        try:
            request_data = {
                "node_type": "Database",
                "security_config": {
                    "backup_encryption": "unencrypted backups",
                    "backup_access_control": "weak",
                    "backup_integrity_verification": False,
                    "backup_retention_policy": "none",
                    "backup_location_security": "poor"
                },
                "backup_configuration": {
                    "frequency": "daily",
                    "location": "local_storage",
                    "encryption": False,
                    "access_controls": "basic",
                    "integrity_checks": False
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/vulnerabilities/analyze/backup-security",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                vulnerabilities = data.get("vulnerabilities", [])
                
                if len(vulnerabilities) == 0:
                    self.log_test("Database Backup Security", False, "No vulnerabilities generated for backup security analysis")
                    return False
                
                self.log_test("Database Backup Security", True, 
                            f"Generated {len(vulnerabilities)} vulnerabilities for backup security analysis")
                return True
            else:
                self.log_test("Database Backup Security", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Database Backup Security", False, f"Error: {str(e)}")
            return False

    # ============================================================================
    # ProductDesignSecurity Node Type Testing
    # ============================================================================
    
    def test_expanded_nodes_supported_types_includes_product_design_security(self):
        """Test GET /api/expanded-nodes/supported-types includes ProductDesignSecurity"""
        try:
            response = self.session.get(f"{self.base_url}/expanded-nodes/supported-types")
            
            if response.status_code == 200:
                data = response.json()
                supported_types = data.get("supported_types", [])
                total_count = data.get("total_count", 0)
                
                # Should now be 31 total instead of 30
                if total_count < 31:
                    self.log_test("ProductDesignSecurity Node Type", False, 
                                f"Expected at least 31 node types, got {total_count}")
                    return False
                
                # Check if ProductDesignSecurity is included
                type_names = [t.get("node_subtype") for t in supported_types if isinstance(t, dict)]
                
                if "ProductDesignSecurity" not in type_names:
                    self.log_test("ProductDesignSecurity Node Type", False, 
                                f"ProductDesignSecurity not found in supported types: {type_names}")
                    return False
                
                self.log_test("ProductDesignSecurity Node Type", True, 
                            f"ProductDesignSecurity found in {total_count} supported node types")
                return True
            else:
                self.log_test("ProductDesignSecurity Node Type", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("ProductDesignSecurity Node Type", False, f"Error: {str(e)}")
            return False

    # ============================================================================
    # STRIDE-based Questionnaire Testing
    # ============================================================================
    
    def test_stride_questionnaire_for_product_design_security(self):
        """Test GET /api/questionnaires/ProductDesignSecurity returns STRIDE-based questionnaire"""
        try:
            response = self.session.get(f"{self.base_url}/questionnaires/ProductDesignSecurity")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for questionnaire structure
                expected_fields = ["node_subtype", "prompts"]
                missing_fields = [f for f in expected_fields if f not in data]
                
                if missing_fields:
                    self.log_test("STRIDE Questionnaire", False, f"Missing fields: {missing_fields}")
                    return False
                
                prompts = data.get("prompts", [])
                
                # Should have STRIDE-based questions (at least 10 basic questions)
                if len(prompts) < 10:
                    self.log_test("STRIDE Questionnaire", False, 
                                f"Expected at least 10 STRIDE questions, got {len(prompts)}")
                    return False
                
                # Check for STRIDE-related content in questions
                stride_keywords = ["spoofing", "tampering", "repudiation", "information disclosure", 
                                 "denial of service", "elevation of privilege", "threat", "security"]
                
                stride_questions = []
                for prompt in prompts:
                    question = prompt.get("question", "").lower()
                    if any(keyword in question for keyword in stride_keywords):
                        stride_questions.append(prompt)
                
                if len(stride_questions) < 5:
                    self.log_test("STRIDE Questionnaire", False, 
                                f"Expected STRIDE-related questions, found only {len(stride_questions)}")
                    return False
                
                self.log_test("STRIDE Questionnaire", True, 
                            f"STRIDE questionnaire with {len(prompts)} questions, {len(stride_questions)} STRIDE-related")
                return True
            else:
                self.log_test("STRIDE Questionnaire", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("STRIDE Questionnaire", False, f"Error: {str(e)}")
            return False

    # ============================================================================
    # Fixed Issues Testing
    # ============================================================================
    
    def test_bulk_vulnerability_analysis_returns_list(self):
        """Test POST /api/vulnerabilities/bulk-analyze returns list format instead of dict"""
        try:
            request_data = {
                "nodes": [
                    {
                        "id": str(uuid.uuid4()),
                        "node_type": "API",
                        "security_config": {
                            "authentication": "none",
                            "authorization": "weak",
                            "input_validation": "minimal"
                        }
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "node_type": "Database",
                        "security_config": {
                            "encryption": "none",
                            "access_control": "basic",
                            "backup_security": "poor"
                        }
                    }
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/vulnerabilities/bulk-analyze",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Should return a list, not a dict
                if not isinstance(data, list):
                    self.log_test("Bulk Vulnerability Analysis", False, 
                                f"Expected list response, got {type(data)}")
                    return False
                
                # Should have results for both nodes
                if len(data) < 2:
                    self.log_test("Bulk Vulnerability Analysis", False, 
                                f"Expected results for 2 nodes, got {len(data)}")
                    return False
                
                # Each result should have vulnerabilities
                total_vulnerabilities = 0
                for result in data:
                    if "vulnerabilities" in result:
                        total_vulnerabilities += len(result["vulnerabilities"])
                
                if total_vulnerabilities == 0:
                    self.log_test("Bulk Vulnerability Analysis", False, 
                                "No vulnerabilities generated in bulk analysis")
                    return False
                
                self.log_test("Bulk Vulnerability Analysis", True, 
                            f"Bulk analysis returned list with {len(data)} results, {total_vulnerabilities} total vulnerabilities")
                return True
            else:
                self.log_test("Bulk Vulnerability Analysis", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Bulk Vulnerability Analysis", False, f"Error: {str(e)}")
            return False

    def test_enhanced_vulnerability_rule_triggering(self):
        """Test that vulnerability rule triggering logic generates vulnerabilities instead of 0"""
        try:
            # Test with a clearly insecure configuration that should trigger multiple rules
            request_data = {
                "node_type": "API",
                "security_config": {
                    "authentication": "none",
                    "authorization": "none",
                    "input_validation": "none",
                    "rate_limiting": "none",
                    "encryption": "none",
                    "logging": "none",
                    "error_handling": "verbose",
                    "cors_policy": "permissive"
                },
                "endpoints": [
                    {"path": "/api/admin", "method": "GET", "authorization": "none"},
                    {"path": "/api/users/{id}/delete", "method": "DELETE", "authorization": "none"},
                    {"path": "/api/sensitive-data", "method": "GET", "authorization": "none"}
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/vulnerabilities/analyze/api1-2023",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                vulnerabilities = data.get("vulnerabilities", [])
                
                # With such an insecure configuration, should generate multiple vulnerabilities
                if len(vulnerabilities) == 0:
                    self.log_test("Enhanced Rule Triggering", False, 
                                "No vulnerabilities generated for highly insecure configuration")
                    return False
                
                # Check that vulnerabilities have proper severity levels
                high_severity_count = sum(1 for v in vulnerabilities if v.get("severity") in ["High", "Critical"])
                
                if high_severity_count == 0:
                    self.log_test("Enhanced Rule Triggering", False, 
                                "No high/critical severity vulnerabilities for insecure configuration")
                    return False
                
                self.log_test("Enhanced Rule Triggering", True, 
                            f"Enhanced rule triggering generated {len(vulnerabilities)} vulnerabilities, {high_severity_count} high/critical")
                return True
            else:
                self.log_test("Enhanced Rule Triggering", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Enhanced Rule Triggering", False, f"Error: {str(e)}")
            return False

    # ============================================================================
    # API Contract Compliance Testing
    # ============================================================================
    
    def test_enhanced_vulnerability_request_format_compliance(self):
        """Test that all endpoints accept the new EnhancedVulnerabilityRequest format"""
        
        # Test the enhanced request format on multiple endpoints
        enhanced_request = {
            "node_type": "API",
            "security_config": {
                "authentication": "oauth2",
                "authorization": "rbac",
                "input_validation": "comprehensive",
                "rate_limiting": "adaptive",
                "encryption": "tls_1_3",
                "logging": "detailed",
                "monitoring": "real_time"
            },
            "endpoints": [
                {"path": "/api/secure", "method": "GET", "authorization": "required"}
            ],
            "business_flows": [
                {"name": "secure_transaction", "rate_limit": 100, "protection": "comprehensive"}
            ],
            "compliance_requirements": ["PCI_DSS", "GDPR", "SOX"],
            "threat_model": "STRIDE"
        }
        
        # Test endpoints that should accept this format
        test_endpoints = [
            "/vulnerabilities/analyze/api1-2023",
            "/vulnerabilities/analyze/api3-2023",
            "/vulnerabilities/analyze/api4-2023"
        ]
        
        success_count = 0
        
        for endpoint in test_endpoints:
            try:
                response = self.session.post(
                    f"{self.base_url}{endpoint}",
                    json=enhanced_request,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    success_count += 1
                elif response.status_code == 422:
                    # Validation error - check if it's due to format issues
                    error_text = response.text.lower()
                    if "validation" in error_text or "format" in error_text:
                        self.log_test("API Contract Compliance", False, 
                                    f"Endpoint {endpoint} rejected enhanced request format: {response.text}")
                        return False
                    
            except Exception as e:
                self.log_test("API Contract Compliance", False, 
                            f"Error testing {endpoint}: {str(e)}")
                return False
        
        if success_count == len(test_endpoints):
            self.log_test("API Contract Compliance", True, 
                        f"All {len(test_endpoints)} endpoints accept enhanced request format")
            return True
        else:
            self.log_test("API Contract Compliance", False, 
                        f"Only {success_count}/{len(test_endpoints)} endpoints accept enhanced format")
            return False

    # ============================================================================
    # Test Runner
    # ============================================================================
    
    def run_all_tests(self):
        """Run all enhanced vulnerability detection tests"""
        print("🚀 Starting Enhanced Vulnerability Detection System Tests")
        print("=" * 80)
        
        tests = [
            # Basic connectivity
            self.test_health_check,
            
            # OWASP API Security Top 10 2023 Endpoints (6 new endpoints)
            self.test_owasp_api1_2023_broken_object_level_authorization,
            self.test_owasp_api3_2023_broken_object_property_level_authorization,
            self.test_owasp_api4_2023_unrestricted_resource_consumption,
            self.test_owasp_api6_2023_unrestricted_sensitive_business_flows,
            self.test_owasp_api7_2023_server_side_request_forgery,
            self.test_owasp_api9_2023_improper_inventory_management,
            
            # Enhanced Database Security Endpoints (5 new endpoints)
            self.test_database_privilege_escalation,
            self.test_database_config_drift,
            self.test_database_advanced_injection,
            self.test_database_insider_threat,
            self.test_database_backup_security,
            
            # ProductDesignSecurity Node Type
            self.test_expanded_nodes_supported_types_includes_product_design_security,
            
            # STRIDE-based Questionnaire
            self.test_stride_questionnaire_for_product_design_security,
            
            # Fixed Issues
            self.test_bulk_vulnerability_analysis_returns_list,
            self.test_enhanced_vulnerability_rule_triggering,
            
            # API Contract Compliance
            self.test_enhanced_vulnerability_request_format_compliance
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ FAIL {test.__name__}: Unexpected error: {str(e)}")
                failed += 1
            
            print()  # Add spacing between tests
        
        # Print summary
        print("=" * 80)
        print("🎯 ENHANCED VULNERABILITY DETECTION SYSTEM TEST SUMMARY")
        print("=" * 80)
        print(f"✅ PASSED: {passed}")
        print(f"❌ FAILED: {failed}")
        print(f"📊 SUCCESS RATE: {(passed / (passed + failed) * 100):.1f}%")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED! Enhanced vulnerability detection system is working correctly.")
        else:
            print(f"\n⚠️  {failed} tests failed. Please review the failed tests above.")
        
        return passed, failed

def main():
    """Main test execution"""
    tester = EnhancedVulnerabilityTester()
    passed, failed = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()