#!/usr/bin/env python3
"""
STRIDE Analysis Field Mapping Fix Validation
Tests the STRIDE analysis field mapping fix across all node types to ensure:
1. Database STRIDE Analysis - optimal security shows mitigated threats, not false positives
2. WebApp STRIDE Analysis - heuristic rules use correct webapp_* field names  
3. API STRIDE Analysis - heuristic rules use correct api_* field names
4. Mitigation Status - threats show as "mitigated" when best practices selected
5. Threat Count Validation - reasonable threat counts (not the original 13 false positives)

CRITICAL SUCCESS CRITERIA:
- Database optimal security: 0 vulnerabilities, ≤8 STRIDE threats, ≥90% mitigation
- WebApp optimal security: ≤5 STRIDE threats, ≥80% mitigation
- API optimal security: ≤4 STRIDE threats, ≥80% mitigation  
- All threat statuses should be "mitigated" or "partial" for good security configurations
- No false positive threats from field name mismatches
"""

import requests
import json
import uuid
from datetime import datetime, timezone
import sys

# Use the backend URL from frontend/.env with /api suffix
BASE_URL = "https://ui-enhancement-46.preview.emergentagent.com/api"

class StrideFieldMappingTester:
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

    def create_test_diagram(self):
        """Create a test diagram for STRIDE analysis"""
        try:
            diagram_data = {
                "title": "STRIDE Field Mapping Validation Diagram",
                "description": "Test diagram for validating STRIDE analysis field mapping fix"
            }
            
            response = self.session.post(f"{self.base_url}/diagrams", json=diagram_data)
            
            if response.status_code != 200:
                self.log_test("Create Test Diagram", False, f"HTTP {response.status_code}")
                return False
            
            data = response.json()
            self.test_diagram_id = data.get("id")
            
            if not self.test_diagram_id:
                self.log_test("Create Test Diagram", False, "No diagram ID returned")
                return False
            
            self.log_test("Create Test Diagram", True, f"Diagram created: {self.test_diagram_id}")
            return True
            
        except Exception as e:
            self.log_test("Create Test Diagram", False, f"Request error: {str(e)}")
            return False

    def test_database_optimal_security_stride(self):
        """Test Database with optimal security configuration - should show mitigated threats, not false positives"""
        try:
            print("🎯 TEST SCENARIO 1: Database with Optimal Security Configuration")
            print("=" * 80)
            
            # Create Database node with optimal security configuration
            database_node = {
                "id": f"database-optimal-{uuid.uuid4().hex[:8]}",
                "type": "Asset",
                "subtype": "Database",
                "label": "Optimal Security Database",
                "position": {"x": 200, "y": 200},
                "data": {
                    "criticality": "Critical",
                    "data_classification": "Restricted"
                }
            }
            
            # Add node to diagram
            diagram_response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}")
            if diagram_response.status_code != 200:
                self.log_test("Database Optimal Security STRIDE", False, "Cannot retrieve test diagram")
                return False
            
            diagram_data = diagram_response.json()
            diagram_data["nodes"] = [database_node]
            diagram_data["edges"] = []
            
            update_response = self.session.put(f"{self.base_url}/diagrams/{self.test_diagram_id}", json=diagram_data)
            if update_response.status_code != 200:
                self.log_test("Database Optimal Security STRIDE", False, "Failed to add Database node")
                return False
            
            print(f"   Database Node Created: {database_node['id']}")
            
            # Save optimal security questionnaire responses
            optimal_database_responses = {
                "responses": {
                    # Using correct database_* field names as per the fix
                    "database_authentication": "strong_mfa",  # Strong MFA
                    "database_encryption_at_rest": "tde_encryption",  # TDE encryption
                    "database_encryption_in_transit": "ssl_tls_enforced",  # SSL/TLS enforced
                    "database_access_control": "rbac_implemented",  # RBAC
                    "database_logging": "comprehensive_logging",  # Comprehensive logging
                    "database_backup_strategy": "automated_encrypted_backups",  # Automated encrypted backups
                    "database_network_security": "private_subnet_with_acls",  # Private subnet with ACLs
                    "database_patch_management": "automated_patching",  # Automated patching
                    "database_monitoring": "real_time_monitoring",  # Real-time monitoring
                    "database_disaster_recovery": "multi_region_replication",  # Multi-region replication
                    "database_compliance": "gdpr_sox_compliant",  # GDPR/SOX compliant
                    "database_vulnerability_scanning": "regular_automated_scans"  # Regular automated scans
                },
                "business_context": {
                    "criticality": "critical",
                    "data_classification": "restricted",
                    "compliance_requirements": ["GDPR", "SOX", "PCI-DSS"]
                }
            }
            
            # Save questionnaire responses
            questionnaire_response = self.session.post(
                f"{self.base_url}/diagrams/{self.test_diagram_id}/nodes/{database_node['id']}/questionnaire",
                json=optimal_database_responses
            )
            
            if questionnaire_response.status_code != 200:
                self.log_test("Database Optimal Security STRIDE", False, 
                            f"Failed to save questionnaire: HTTP {questionnaire_response.status_code}")
                return False
            
            print("   ✅ Optimal security questionnaire responses saved")
            
            # Run STRIDE analysis
            stride_response = self.session.post(f"{self.base_url}/diagrams/{self.test_diagram_id}/stride/analyze")
            
            if stride_response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = stride_response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = stride_response.text
                
                self.log_test("Database Optimal Security STRIDE", False, 
                            f"STRIDE analysis failed: HTTP {stride_response.status_code}: {error_detail}")
                return False
            
            try:
                stride_data = stride_response.json()
            except json.JSONDecodeError as e:
                self.log_test("Database Optimal Security STRIDE", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            # Analyze STRIDE results
            threats = stride_data.get("threats", [])
            analysis_summary = stride_data.get("analysis_summary", {})
            
            print(f"📊 Database Optimal Security STRIDE Results:")
            print(f"   Total Threats Found: {len(threats)}")
            print(f"   Analysis Summary: {analysis_summary}")
            
            # Check threat details
            mitigated_threats = 0
            false_positive_threats = 0
            threat_categories = {}
            
            for threat in threats:
                threat_status = threat.get("status", "unknown")
                threat_category = threat.get("category", "unknown")
                threat_title = threat.get("title", "unknown")
                
                # Count by category
                threat_categories[threat_category] = threat_categories.get(threat_category, 0) + 1
                
                # Count mitigated vs false positives
                if threat_status == "mitigated":
                    mitigated_threats += 1
                elif "false positive" in threat_title.lower() or threat_status == "false_positive":
                    false_positive_threats += 1
                
                print(f"     - {threat_title} ({threat_category}): {threat_status}")
            
            print(f"   Threat Categories: {threat_categories}")
            print(f"   Mitigated Threats: {mitigated_threats}")
            print(f"   False Positive Threats: {false_positive_threats}")
            
            # Get STRIDE coverage
            coverage_response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}/stride/coverage")
            
            if coverage_response.status_code == 200:
                try:
                    coverage_data = coverage_response.json()
                    mitigation_percentage = coverage_data.get("mitigation_percentage", 0)
                    total_threats = coverage_data.get("total_threats", 0)
                    mitigated_count = coverage_data.get("mitigated", 0)
                    
                    print(f"   STRIDE Coverage:")
                    print(f"     Total Threats: {total_threats}")
                    print(f"     Mitigated: {mitigated_count}")
                    print(f"     Mitigation Percentage: {mitigation_percentage}%")
                    
                except json.JSONDecodeError:
                    print("   ⚠️ Could not parse coverage data")
                    mitigation_percentage = 0
            else:
                print(f"   ⚠️ Coverage endpoint failed: HTTP {coverage_response.status_code}")
                mitigation_percentage = 0
            
            # Validate success criteria for Database optimal security
            success_criteria_met = True
            failure_reasons = []
            
            # Criterion 1: ≤8 STRIDE threats
            if len(threats) > 8:
                success_criteria_met = False
                failure_reasons.append(f"Too many threats: {len(threats)} > 8")
            
            # Criterion 2: ≥90% mitigation
            if mitigation_percentage < 90:
                success_criteria_met = False
                failure_reasons.append(f"Low mitigation: {mitigation_percentage}% < 90%")
            
            # Criterion 3: No false positive threats
            if false_positive_threats > 0:
                success_criteria_met = False
                failure_reasons.append(f"False positives detected: {false_positive_threats}")
            
            # Criterion 4: Most threats should be mitigated
            if len(threats) > 0 and (mitigated_threats / len(threats)) < 0.8:
                success_criteria_met = False
                failure_reasons.append(f"Low mitigated ratio: {mitigated_threats}/{len(threats)}")
            
            if success_criteria_met:
                self.log_test("Database Optimal Security STRIDE", True, 
                            f"✅ SUCCESS: {len(threats)} threats, {mitigation_percentage}% mitigation, {mitigated_threats} mitigated")
                return True
            else:
                self.log_test("Database Optimal Security STRIDE", False, 
                            f"❌ FAILED: {'; '.join(failure_reasons)}")
                return False
            
        except Exception as e:
            self.log_test("Database Optimal Security STRIDE", False, f"Request error: {str(e)}")
            return False

    def test_webapp_optimal_security_stride(self):
        """Test WebApp with optimal security configuration - should use correct webapp_* field names"""
        try:
            print("🎯 TEST SCENARIO 2: WebApp with Optimal Security Configuration")
            print("=" * 80)
            
            # Create WebApp node with optimal security configuration
            webapp_node = {
                "id": f"webapp-optimal-{uuid.uuid4().hex[:8]}",
                "type": "Asset",
                "subtype": "WebApp",
                "label": "Optimal Security WebApp",
                "position": {"x": 400, "y": 200},
                "data": {
                    "criticality": "High",
                    "data_classification": "Confidential"
                }
            }
            
            # Update diagram with WebApp node
            diagram_response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}")
            if diagram_response.status_code != 200:
                self.log_test("WebApp Optimal Security STRIDE", False, "Cannot retrieve test diagram")
                return False
            
            diagram_data = diagram_response.json()
            diagram_data["nodes"] = [webapp_node]
            diagram_data["edges"] = []
            
            update_response = self.session.put(f"{self.base_url}/diagrams/{self.test_diagram_id}", json=diagram_data)
            if update_response.status_code != 200:
                self.log_test("WebApp Optimal Security STRIDE", False, "Failed to add WebApp node")
                return False
            
            print(f"   WebApp Node Created: {webapp_node['id']}")
            
            # Save optimal security questionnaire responses with webapp_* field names
            optimal_webapp_responses = {
                "responses": {
                    # Using correct webapp_* field names as per the fix
                    "webapp_authentication": "oauth2_oidc",  # OAuth2/OIDC
                    "webapp_session_management": "secure_jwt_tokens",  # Secure JWT tokens
                    "webapp_input_validation": "comprehensive_validation",  # Comprehensive validation
                    "webapp_output_encoding": "context_aware_encoding",  # Context-aware encoding
                    "webapp_https_enforcement": "strict_https_only",  # HTTPS enforced
                    "webapp_authorization": "rbac_fine_grained",  # RBAC with fine-grained permissions
                    "webapp_csrf_protection": "double_submit_cookie",  # CSRF protection
                    "webapp_xss_protection": "content_security_policy",  # XSS protection
                    "webapp_security_headers": "comprehensive_headers",  # Security headers
                    "webapp_error_handling": "secure_error_pages",  # Secure error handling
                    "webapp_logging": "comprehensive_audit_logging",  # Comprehensive logging
                    "webapp_rate_limiting": "adaptive_rate_limiting"  # Rate limiting
                },
                "business_context": {
                    "criticality": "high",
                    "data_classification": "confidential",
                    "compliance_requirements": ["GDPR", "OWASP"]
                }
            }
            
            # Save questionnaire responses
            questionnaire_response = self.session.post(
                f"{self.base_url}/diagrams/{self.test_diagram_id}/nodes/{webapp_node['id']}/questionnaire",
                json=optimal_webapp_responses
            )
            
            if questionnaire_response.status_code != 200:
                self.log_test("WebApp Optimal Security STRIDE", False, 
                            f"Failed to save questionnaire: HTTP {questionnaire_response.status_code}")
                return False
            
            print("   ✅ Optimal security questionnaire responses saved")
            
            # Run STRIDE analysis
            stride_response = self.session.post(f"{self.base_url}/diagrams/{self.test_diagram_id}/stride/analyze")
            
            if stride_response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = stride_response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = stride_response.text
                
                self.log_test("WebApp Optimal Security STRIDE", False, 
                            f"STRIDE analysis failed: HTTP {stride_response.status_code}: {error_detail}")
                return False
            
            try:
                stride_data = stride_response.json()
            except json.JSONDecodeError as e:
                self.log_test("WebApp Optimal Security STRIDE", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            # Analyze STRIDE results
            threats = stride_data.get("threats", [])
            analysis_summary = stride_data.get("analysis_summary", {})
            
            print(f"📊 WebApp Optimal Security STRIDE Results:")
            print(f"   Total Threats Found: {len(threats)}")
            print(f"   Analysis Summary: {analysis_summary}")
            
            # Check threat details
            mitigated_threats = 0
            field_mapping_errors = 0
            threat_categories = {}
            
            for threat in threats:
                threat_status = threat.get("status", "unknown")
                threat_category = threat.get("category", "unknown")
                threat_title = threat.get("title", "unknown")
                threat_description = threat.get("description", "")
                
                # Count by category
                threat_categories[threat_category] = threat_categories.get(threat_category, 0) + 1
                
                # Count mitigated threats
                if threat_status == "mitigated":
                    mitigated_threats += 1
                
                # Check for field mapping errors (references to non-existent fields)
                if "field not found" in threat_description.lower() or "undefined field" in threat_description.lower():
                    field_mapping_errors += 1
                
                print(f"     - {threat_title} ({threat_category}): {threat_status}")
            
            print(f"   Threat Categories: {threat_categories}")
            print(f"   Mitigated Threats: {mitigated_threats}")
            print(f"   Field Mapping Errors: {field_mapping_errors}")
            
            # Get STRIDE coverage
            coverage_response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}/stride/coverage")
            
            if coverage_response.status_code == 200:
                try:
                    coverage_data = coverage_response.json()
                    mitigation_percentage = coverage_data.get("mitigation_percentage", 0)
                    total_threats = coverage_data.get("total_threats", 0)
                    mitigated_count = coverage_data.get("mitigated", 0)
                    
                    print(f"   STRIDE Coverage:")
                    print(f"     Total Threats: {total_threats}")
                    print(f"     Mitigated: {mitigated_count}")
                    print(f"     Mitigation Percentage: {mitigation_percentage}%")
                    
                except json.JSONDecodeError:
                    print("   ⚠️ Could not parse coverage data")
                    mitigation_percentage = 0
            else:
                print(f"   ⚠️ Coverage endpoint failed: HTTP {coverage_response.status_code}")
                mitigation_percentage = 0
            
            # Validate success criteria for WebApp optimal security
            success_criteria_met = True
            failure_reasons = []
            
            # Criterion 1: ≤5 STRIDE threats
            if len(threats) > 5:
                success_criteria_met = False
                failure_reasons.append(f"Too many threats: {len(threats)} > 5")
            
            # Criterion 2: ≥80% mitigation
            if mitigation_percentage < 80:
                success_criteria_met = False
                failure_reasons.append(f"Low mitigation: {mitigation_percentage}% < 80%")
            
            # Criterion 3: No field mapping errors
            if field_mapping_errors > 0:
                success_criteria_met = False
                failure_reasons.append(f"Field mapping errors: {field_mapping_errors}")
            
            # Criterion 4: Most threats should be mitigated
            if len(threats) > 0 and (mitigated_threats / len(threats)) < 0.7:
                success_criteria_met = False
                failure_reasons.append(f"Low mitigated ratio: {mitigated_threats}/{len(threats)}")
            
            if success_criteria_met:
                self.log_test("WebApp Optimal Security STRIDE", True, 
                            f"✅ SUCCESS: {len(threats)} threats, {mitigation_percentage}% mitigation, {mitigated_threats} mitigated")
                return True
            else:
                self.log_test("WebApp Optimal Security STRIDE", False, 
                            f"❌ FAILED: {'; '.join(failure_reasons)}")
                return False
            
        except Exception as e:
            self.log_test("WebApp Optimal Security STRIDE", False, f"Request error: {str(e)}")
            return False

    def test_api_optimal_security_stride(self):
        """Test API with optimal security configuration - should use correct api_* field names"""
        try:
            print("🎯 TEST SCENARIO 3: API with Optimal Security Configuration")
            print("=" * 80)
            
            # Create API node with optimal security configuration
            api_node = {
                "id": f"api-optimal-{uuid.uuid4().hex[:8]}",
                "type": "Asset",
                "subtype": "API",
                "label": "Optimal Security API",
                "position": {"x": 600, "y": 200},
                "data": {
                    "criticality": "High",
                    "data_classification": "Confidential"
                }
            }
            
            # Update diagram with API node
            diagram_response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}")
            if diagram_response.status_code != 200:
                self.log_test("API Optimal Security STRIDE", False, "Cannot retrieve test diagram")
                return False
            
            diagram_data = diagram_response.json()
            diagram_data["nodes"] = [api_node]
            diagram_data["edges"] = []
            
            update_response = self.session.put(f"{self.base_url}/diagrams/{self.test_diagram_id}", json=diagram_data)
            if update_response.status_code != 200:
                self.log_test("API Optimal Security STRIDE", False, "Failed to add API node")
                return False
            
            print(f"   API Node Created: {api_node['id']}")
            
            # Save optimal security questionnaire responses with api_* field names
            optimal_api_responses = {
                "responses": {
                    # Using correct api_* field names as per the fix
                    "api_authentication": "oauth2_jwt",  # OAuth2/JWT authentication
                    "api_authorization": "role_based_with_scopes",  # Role-based with scopes
                    "api_rate_limiting": "per_user_rate_limiting",  # Per-user rate limiting
                    "api_input_validation": "comprehensive_validation",  # Comprehensive validation
                    "api_output_sanitization": "context_aware_sanitization",  # Output sanitization
                    "api_https_enforcement": "strict_https_only",  # HTTPS enforced
                    "api_cors_policy": "restrictive_cors_policy",  # Restrictive CORS
                    "api_security_headers": "comprehensive_headers",  # Security headers
                    "api_error_handling": "secure_error_responses",  # Secure error handling
                    "api_logging": "comprehensive_audit_logging",  # Comprehensive logging
                    "api_versioning": "secure_api_versioning",  # Secure versioning
                    "api_documentation": "secure_documentation"  # Secure documentation
                },
                "business_context": {
                    "criticality": "high",
                    "data_classification": "confidential",
                    "compliance_requirements": ["OWASP API Top 10", "OAuth 2.0"]
                }
            }
            
            # Save questionnaire responses
            questionnaire_response = self.session.post(
                f"{self.base_url}/diagrams/{self.test_diagram_id}/nodes/{api_node['id']}/questionnaire",
                json=optimal_api_responses
            )
            
            if questionnaire_response.status_code != 200:
                self.log_test("API Optimal Security STRIDE", False, 
                            f"Failed to save questionnaire: HTTP {questionnaire_response.status_code}")
                return False
            
            print("   ✅ Optimal security questionnaire responses saved")
            
            # Run STRIDE analysis
            stride_response = self.session.post(f"{self.base_url}/diagrams/{self.test_diagram_id}/stride/analyze")
            
            if stride_response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = stride_response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = stride_response.text
                
                self.log_test("API Optimal Security STRIDE", False, 
                            f"STRIDE analysis failed: HTTP {stride_response.status_code}: {error_detail}")
                return False
            
            try:
                stride_data = stride_response.json()
            except json.JSONDecodeError as e:
                self.log_test("API Optimal Security STRIDE", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            # Analyze STRIDE results
            threats = stride_data.get("threats", [])
            analysis_summary = stride_data.get("analysis_summary", {})
            
            print(f"📊 API Optimal Security STRIDE Results:")
            print(f"   Total Threats Found: {len(threats)}")
            print(f"   Analysis Summary: {analysis_summary}")
            
            # Check threat details
            mitigated_threats = 0
            field_mapping_errors = 0
            threat_categories = {}
            
            for threat in threats:
                threat_status = threat.get("status", "unknown")
                threat_category = threat.get("category", "unknown")
                threat_title = threat.get("title", "unknown")
                threat_description = threat.get("description", "")
                
                # Count by category
                threat_categories[threat_category] = threat_categories.get(threat_category, 0) + 1
                
                # Count mitigated threats
                if threat_status == "mitigated":
                    mitigated_threats += 1
                
                # Check for field mapping errors (references to non-existent fields)
                if "field not found" in threat_description.lower() or "undefined field" in threat_description.lower():
                    field_mapping_errors += 1
                
                print(f"     - {threat_title} ({threat_category}): {threat_status}")
            
            print(f"   Threat Categories: {threat_categories}")
            print(f"   Mitigated Threats: {mitigated_threats}")
            print(f"   Field Mapping Errors: {field_mapping_errors}")
            
            # Get STRIDE coverage
            coverage_response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}/stride/coverage")
            
            if coverage_response.status_code == 200:
                try:
                    coverage_data = coverage_response.json()
                    mitigation_percentage = coverage_data.get("mitigation_percentage", 0)
                    total_threats = coverage_data.get("total_threats", 0)
                    mitigated_count = coverage_data.get("mitigated", 0)
                    
                    print(f"   STRIDE Coverage:")
                    print(f"     Total Threats: {total_threats}")
                    print(f"     Mitigated: {mitigated_count}")
                    print(f"     Mitigation Percentage: {mitigation_percentage}%")
                    
                except json.JSONDecodeError:
                    print("   ⚠️ Could not parse coverage data")
                    mitigation_percentage = 0
            else:
                print(f"   ⚠️ Coverage endpoint failed: HTTP {coverage_response.status_code}")
                mitigation_percentage = 0
            
            # Validate success criteria for API optimal security
            success_criteria_met = True
            failure_reasons = []
            
            # Criterion 1: ≤4 STRIDE threats
            if len(threats) > 4:
                success_criteria_met = False
                failure_reasons.append(f"Too many threats: {len(threats)} > 4")
            
            # Criterion 2: ≥80% mitigation
            if mitigation_percentage < 80:
                success_criteria_met = False
                failure_reasons.append(f"Low mitigation: {mitigation_percentage}% < 80%")
            
            # Criterion 3: No field mapping errors
            if field_mapping_errors > 0:
                success_criteria_met = False
                failure_reasons.append(f"Field mapping errors: {field_mapping_errors}")
            
            # Criterion 4: Most threats should be mitigated
            if len(threats) > 0 and (mitigated_threats / len(threats)) < 0.7:
                success_criteria_met = False
                failure_reasons.append(f"Low mitigated ratio: {mitigated_threats}/{len(threats)}")
            
            if success_criteria_met:
                self.log_test("API Optimal Security STRIDE", True, 
                            f"✅ SUCCESS: {len(threats)} threats, {mitigation_percentage}% mitigation, {mitigated_threats} mitigated")
                return True
            else:
                self.log_test("API Optimal Security STRIDE", False, 
                            f"❌ FAILED: {'; '.join(failure_reasons)}")
                return False
            
        except Exception as e:
            self.log_test("API Optimal Security STRIDE", False, f"Request error: {str(e)}")
            return False

    def test_threat_status_validation(self):
        """Test threat status validation - verify threats can be updated to mitigated status"""
        try:
            print("🎯 TEST SCENARIO 4: Threat Status Validation")
            print("=" * 80)
            
            # First, ensure we have some threats from previous tests
            stride_response = self.session.post(f"{self.base_url}/diagrams/{self.test_diagram_id}/stride/analyze")
            
            if stride_response.status_code != 200:
                self.log_test("Threat Status Validation", False, "Cannot run STRIDE analysis for threat status test")
                return False
            
            stride_data = stride_response.json()
            threats = stride_data.get("threats", [])
            
            if not threats:
                self.log_test("Threat Status Validation", False, "No threats found for status validation test")
                return False
            
            print(f"   Found {len(threats)} threats for status validation")
            
            # Test updating threat status to mitigated
            test_threat = threats[0]
            threat_id = test_threat.get("id")
            
            if not threat_id:
                self.log_test("Threat Status Validation", False, "No threat ID found for status update")
                return False
            
            # Update threat status to mitigated
            status_update = {"status": "mitigated"}
            
            update_response = self.session.patch(
                f"{self.base_url}/diagrams/{self.test_diagram_id}/stride/threats/{threat_id}",
                json=status_update
            )
            
            print(f"   Threat Status Update Response: HTTP {update_response.status_code}")
            
            if update_response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = update_response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = update_response.text
                
                self.log_test("Threat Status Validation", False, 
                            f"Failed to update threat status: HTTP {update_response.status_code}: {error_detail}")
                return False
            
            try:
                update_data = update_response.json()
            except json.JSONDecodeError as e:
                self.log_test("Threat Status Validation", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            # Verify the update was successful
            updated_status = update_data.get("status")
            
            if updated_status != "mitigated":
                self.log_test("Threat Status Validation", False, 
                            f"Threat status not updated correctly: {updated_status} != mitigated")
                return False
            
            print(f"   ✅ Threat {threat_id} status updated to: {updated_status}")
            
            # Verify coverage percentage increased
            coverage_response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}/stride/coverage")
            
            if coverage_response.status_code == 200:
                try:
                    coverage_data = coverage_response.json()
                    mitigation_percentage = coverage_data.get("mitigation_percentage", 0)
                    mitigated_count = coverage_data.get("mitigated", 0)
                    
                    print(f"   Updated STRIDE Coverage:")
                    print(f"     Mitigated: {mitigated_count}")
                    print(f"     Mitigation Percentage: {mitigation_percentage}%")
                    
                    if mitigated_count > 0:
                        self.log_test("Threat Status Validation", True, 
                                    f"✅ SUCCESS: Threat status updated, {mitigated_count} mitigated, {mitigation_percentage}% coverage")
                        return True
                    else:
                        self.log_test("Threat Status Validation", False, 
                                    "Threat status update did not reflect in coverage")
                        return False
                    
                except json.JSONDecodeError:
                    self.log_test("Threat Status Validation", False, "Could not parse coverage data")
                    return False
            else:
                self.log_test("Threat Status Validation", False, 
                            f"Coverage endpoint failed: HTTP {coverage_response.status_code}")
                return False
            
        except Exception as e:
            self.log_test("Threat Status Validation", False, f"Request error: {str(e)}")
            return False

    def test_regression_vulnerability_analysis(self):
        """Test regression - ensure vulnerability analysis still works correctly"""
        try:
            print("🎯 TEST SCENARIO 5: Regression Testing - Vulnerability Analysis")
            print("=" * 80)
            
            # Create a test node for vulnerability analysis
            test_node = {
                "id": f"vuln-test-{uuid.uuid4().hex[:8]}",
                "type": "Asset",
                "subtype": "Database",
                "label": "Vulnerability Test Database",
                "position": {"x": 300, "y": 300},
                "data": {
                    "criticality": "High",
                    "data_classification": "Confidential"
                }
            }
            
            # Update diagram with test node
            diagram_response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}")
            if diagram_response.status_code != 200:
                self.log_test("Regression Vulnerability Analysis", False, "Cannot retrieve test diagram")
                return False
            
            diagram_data = diagram_response.json()
            diagram_data["nodes"] = [test_node]
            diagram_data["edges"] = []
            
            update_response = self.session.put(f"{self.base_url}/diagrams/{self.test_diagram_id}", json=diagram_data)
            if update_response.status_code != 200:
                self.log_test("Regression Vulnerability Analysis", False, "Failed to add test node")
                return False
            
            print(f"   Test Node Created: {test_node['id']}")
            
            # Test vulnerability analysis
            vulnerability_request = {
                "node_id": test_node["id"],
                "node_type": "Database",
                "questionnaire_responses": {
                    "database_authentication": "basic_auth",  # Poor security
                    "database_encryption_at_rest": "no_encryption",  # Poor security
                    "database_encryption_in_transit": "no_ssl",  # Poor security
                    "database_access_control": "no_access_control",  # Poor security
                    "database_logging": "minimal_logging"  # Poor security
                },
                "node_position": {"x": 300, "y": 300}
            }
            
            response = self.session.post(
                f"{self.base_url}/vulnerabilities/analyze/{test_node['id']}",
                json=vulnerability_request
            )
            
            print(f"   Vulnerability Analysis Response: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("Regression Vulnerability Analysis", False, 
                            f"Vulnerability analysis failed: HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                vuln_data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Regression Vulnerability Analysis", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            # Verify vulnerability analysis results
            vulnerabilities = vuln_data.get("vulnerabilities", [])
            overall_risk_score = vuln_data.get("overall_risk_score", 0)
            
            print(f"   Vulnerabilities Found: {len(vulnerabilities)}")
            print(f"   Overall Risk Score: {overall_risk_score}")
            
            # For poor security configuration, we should find vulnerabilities
            if len(vulnerabilities) == 0:
                self.log_test("Regression Vulnerability Analysis", False, 
                            "No vulnerabilities found for poor security configuration")
                return False
            
            # Show vulnerability breakdown
            severity_counts = {}
            for vuln in vulnerabilities:
                severity = vuln.get("severity", "Unknown")
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            print(f"   Vulnerability Breakdown: {severity_counts}")
            
            self.log_test("Regression Vulnerability Analysis", True, 
                        f"✅ SUCCESS: Vulnerability analysis working, {len(vulnerabilities)} vulnerabilities found")
            return True
            
        except Exception as e:
            self.log_test("Regression Vulnerability Analysis", False, f"Request error: {str(e)}")
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
        """Run all STRIDE field mapping validation tests"""
        print("🚀 STARTING STRIDE ANALYSIS FIELD MAPPING FIX VALIDATION")
        print("=" * 80)
        print("Testing STRIDE analysis field mapping fix across all node types:")
        print("1. Database with optimal security - verify mitigated threats, not false positives")
        print("2. WebApp with optimal security - verify correct webapp_* field names")
        print("3. API with optimal security - verify correct api_* field names")
        print("4. Threat status validation - verify threats can be marked as mitigated")
        print("5. Regression testing - ensure vulnerability analysis still works")
        print("=" * 80)
        
        # Create test diagram first
        if not self.create_test_diagram():
            print("❌ Failed to create test diagram, aborting tests")
            return False
        
        tests = [
            self.test_database_optimal_security_stride,
            self.test_webapp_optimal_security_stride,
            self.test_api_optimal_security_stride,
            self.test_threat_status_validation,
            self.test_regression_vulnerability_analysis,
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
        
        # Summary for STRIDE field mapping fix validation
        if passed == total:
            print("\n🎉 STRIDE ANALYSIS FIELD MAPPING FIX VALIDATION: ALL TESTS PASSED")
            print("✅ Database optimal security: Shows mitigated threats, not false positives")
            print("✅ WebApp optimal security: Uses correct webapp_* field names")
            print("✅ API optimal security: Uses correct api_* field names")
            print("✅ Threat status validation: Threats can be marked as mitigated")
            print("✅ Regression testing: Vulnerability analysis still works correctly")
            print("✅ STRIDE analysis field mapping fix is working correctly across all node types")
        else:
            print(f"\n⚠️ STRIDE ANALYSIS FIELD MAPPING FIX VALIDATION: {total-passed} TESTS FAILED")
            print("❌ Some STRIDE analysis functionality may have issues")
            print("❌ Review failed tests above for details")
        
        return passed == total

if __name__ == "__main__":
    tester = StrideFieldMappingTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)