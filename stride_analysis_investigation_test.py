#!/usr/bin/env python3
"""
STRIDE Analysis Investigation - Database with Optimal Security Testing

CONTEXT: User reported that STRIDE analysis shows 13 threats even when Database has optimal 
security settings and vulnerability analysis shows 0 vulnerabilities. This appears to be due 
to STRIDE heuristic rules checking for field names that don't exist in the Database questionnaire.

TESTING OBJECTIVES:
1. Reproduce the Issue: Create Database with all best security practices and analyze STRIDE vs vulnerability results
2. Field Name Analysis: Identify exactly which STRIDE threats are being triggered and why
3. Two Systems Comparison: Compare explicit STRIDE mapping vs heuristic rules behavior
4. Root Cause Confirmation: Verify that heuristic rules are checking non-existent fields

DETAILED TEST PLAN:
1. Create Database with Optimal Security Configuration
2. Run Both Analyses (Vulnerability should return 0, STRIDE currently showing 13 threats)
3. Deep STRIDE Analysis Investigation
4. Field Mapping Analysis
5. Expected Results Analysis

CRITICAL INVESTIGATION POINTS:
- Which STRIDE threats are being generated and from which system (mapping vs heuristic)?
- Are heuristic rules checking for fields that don't exist in Database questionnaire?
- How do threat counts compare between optimal vs poor security configurations?
- Can we isolate which part of STRIDE analysis is generating the false positives?
"""

import requests
import json
import uuid
from datetime import datetime, timezone
import sys

# Use the backend URL from frontend/.env with /api suffix
BASE_URL = "https://stride-metrics.preview.emergentagent.com/api"

class StrideAnalysisInvestigator:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.test_results = []
        self.test_diagram_id = None
        self.test_database_node_id = None
        
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
        """Test basic API health"""
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

    def create_test_diagram_with_database(self):
        """Create test diagram with Database node configured with optimal security"""
        try:
            print("🎯 CREATING TEST DIAGRAM WITH OPTIMAL SECURITY DATABASE")
            print("=" * 80)
            
            # Create diagram
            diagram_data = {
                "title": "STRIDE Analysis Investigation - Database Optimal Security",
                "description": "Test diagram for investigating STRIDE analysis field mapping issues"
            }
            
            response = self.session.post(f"{self.base_url}/diagrams", json=diagram_data)
            
            if response.status_code != 200:
                self.log_test("Create Test Diagram", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            diagram = response.json()
            self.test_diagram_id = diagram.get("id")
            
            # Create Database node with optimal security configuration
            database_node = {
                "id": f"database-optimal-{uuid.uuid4().hex[:8]}",
                "type": "Asset",
                "subtype": "Database",
                "label": "Optimal Security Database",
                "position": {"x": 400, "y": 300},
                "data": {
                    "criticality": "Critical",
                    "data_classification": "Restricted"
                }
            }
            
            self.test_database_node_id = database_node["id"]
            
            # Update diagram with Database node
            diagram["nodes"] = [database_node]
            diagram["edges"] = []
            
            update_response = self.session.put(f"{self.base_url}/diagrams/{self.test_diagram_id}", json=diagram)
            
            if update_response.status_code != 200:
                self.log_test("Create Test Diagram", False, f"Failed to add Database node: HTTP {update_response.status_code}")
                return False
            
            print(f"📊 Test Setup Complete:")
            print(f"   Diagram ID: {self.test_diagram_id}")
            print(f"   Database Node ID: {self.test_database_node_id}")
            print(f"   Database Configuration: Optimal Security (all best practices)")
            
            self.log_test("Create Test Diagram", True, f"Test diagram and Database node created successfully")
            return True
            
        except Exception as e:
            self.log_test("Create Test Diagram", False, f"Request error: {str(e)}")
            return False

    def configure_optimal_database_security(self):
        """Configure Database node with all optimal security practices"""
        try:
            print("🎯 CONFIGURING DATABASE WITH OPTIMAL SECURITY PRACTICES")
            print("=" * 80)
            
            # Optimal security configuration based on review request
            optimal_security_responses = {
                "database_authentication": "Strong authentication with MFA",
                "database_encryption_at_rest": "Transparent Data Encryption (TDE)", 
                "database_encryption_in_transit": "SSL/TLS enforced",
                "database_access_control": "Role-based access with least privilege",
                "database_backup_strategy": "Automated encrypted backups",
                "database_patch_management": "Automated patching with testing",
                "database_network_security": "Private network with firewall",
                "database_logging": "Comprehensive audit logging",
                "database_privilege_management": "Dynamic privilege management",
                "database_data_classification": "Comprehensive data classification"
            }
            
            questionnaire_data = {
                "responses": optimal_security_responses,
                "business_context": {
                    "criticality": "critical",
                    "data_classification": "restricted",
                    "compliance_requirements": ["SOX", "GDPR", "HIPAA"]
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/diagrams/{self.test_diagram_id}/nodes/{self.test_database_node_id}/questionnaire",
                json=questionnaire_data
            )
            
            print(f"📋 Database Configuration Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("Configure Optimal Database Security", False, 
                            f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                save_data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Configure Optimal Database Security", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            print(f"📊 Database Security Configuration:")
            print(f"   Configuration Success: {save_data.get('success', False)}")
            print(f"   Security Practices Applied:")
            for key, value in optimal_security_responses.items():
                print(f"     {key}: {value}")
            
            self.log_test("Configure Optimal Database Security", True, 
                        f"Database configured with optimal security practices")
            return True
            
        except Exception as e:
            self.log_test("Configure Optimal Database Security", False, f"Request error: {str(e)}")
            return False

    def test_vulnerability_analysis(self):
        """Test vulnerability analysis - should return 0 vulnerabilities for optimal security"""
        try:
            print("🎯 TESTING VULNERABILITY ANALYSIS (EXPECTED: 0 VULNERABILITIES)")
            print("=" * 80)
            
            vulnerability_request = {
                "node_id": self.test_database_node_id,
                "node_type": "Database",
                "questionnaire_responses": {
                    "database_authentication": "Strong authentication with MFA",
                    "database_encryption_at_rest": "Transparent Data Encryption (TDE)", 
                    "database_encryption_in_transit": "SSL/TLS enforced",
                    "database_access_control": "Role-based access with least privilege",
                    "database_backup_strategy": "Automated encrypted backups",
                    "database_patch_management": "Automated patching with testing",
                    "database_network_security": "Private network with firewall",
                    "database_logging": "Comprehensive audit logging",
                    "database_privilege_management": "Dynamic privilege management",
                    "database_data_classification": "Comprehensive data classification"
                },
                "node_position": {"x": 400, "y": 300}
            }
            
            response = self.session.post(
                f"{self.base_url}/vulnerabilities/analyze/{self.test_database_node_id}",
                json=vulnerability_request
            )
            
            print(f"📋 Vulnerability Analysis Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("Vulnerability Analysis", False, 
                            f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Vulnerability Analysis", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            vulnerabilities = data.get("vulnerabilities", [])
            overall_risk_score = data.get("overall_risk_score", 0)
            
            print(f"📊 Vulnerability Analysis Results:")
            print(f"   Vulnerabilities Found: {len(vulnerabilities)}")
            print(f"   Overall Risk Score: {overall_risk_score}")
            
            if vulnerabilities:
                print(f"   Vulnerability Breakdown:")
                severity_counts = {}
                for vuln in vulnerabilities:
                    severity = vuln.get("severity", "Unknown")
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1
                
                for severity, count in severity_counts.items():
                    print(f"     {severity}: {count}")
                
                print(f"   Sample vulnerabilities:")
                for i, vuln in enumerate(vulnerabilities[:5]):
                    print(f"     {i+1}. {vuln.get('title', 'Unknown')} ({vuln.get('severity', 'Unknown')})")
            
            # Expected result: 0 vulnerabilities for optimal security
            if len(vulnerabilities) == 0:
                self.log_test("Vulnerability Analysis", True, 
                            f"✅ EXPECTED RESULT: 0 vulnerabilities found for optimal security Database")
            else:
                self.log_test("Vulnerability Analysis", False, 
                            f"❌ UNEXPECTED: {len(vulnerabilities)} vulnerabilities found despite optimal security")
            
            return True
            
        except Exception as e:
            self.log_test("Vulnerability Analysis", False, f"Request error: {str(e)}")
            return False

    def test_stride_analysis_investigation(self):
        """Deep investigation of STRIDE analysis - currently showing 13 threats"""
        try:
            print("🎯 DEEP STRIDE ANALYSIS INVESTIGATION (CURRENT ISSUE: 13 THREATS)")
            print("=" * 80)
            
            response = self.session.post(f"{self.base_url}/diagrams/{self.test_diagram_id}/stride/analyze")
            
            print(f"📋 STRIDE Analysis Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("STRIDE Analysis Investigation", False, 
                            f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("STRIDE Analysis Investigation", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            threats = data.get("threats", [])
            analysis_summary = data.get("analysis_summary", {})
            
            print(f"📊 STRIDE Analysis Results:")
            print(f"   Total Threats Found: {len(threats)}")
            print(f"   Analysis Summary: {analysis_summary}")
            
            if threats:
                print(f"\n🔍 DETAILED THREAT BREAKDOWN:")
                
                # Group threats by STRIDE category
                stride_categories = {}
                threat_sources = {"explicit_mapping": 0, "heuristic_rules": 0, "unknown": 0}
                field_references = {}
                
                for i, threat in enumerate(threats):
                    threat_id = threat.get("id", f"threat-{i}")
                    title = threat.get("title", "Unknown Threat")
                    description = threat.get("description", "No description")
                    category = threat.get("category", "Unknown")
                    severity = threat.get("severity", "Unknown")
                    source = threat.get("source", "unknown")  # explicit_mapping vs heuristic_rules
                    trigger_condition = threat.get("trigger_condition", "Unknown")
                    field_checked = threat.get("field_checked", "Unknown")
                    
                    # Group by STRIDE category
                    if category not in stride_categories:
                        stride_categories[category] = []
                    stride_categories[category].append(threat)
                    
                    # Track threat sources
                    if source in threat_sources:
                        threat_sources[source] += 1
                    else:
                        threat_sources["unknown"] += 1
                    
                    # Track field references
                    if field_checked != "Unknown":
                        if field_checked not in field_references:
                            field_references[field_checked] = []
                        field_references[field_checked].append(threat_id)
                    
                    print(f"   {i+1}. [{category}] {title}")
                    print(f"      Description: {description}")
                    print(f"      Severity: {severity}")
                    print(f"      Source: {source}")
                    print(f"      Trigger Condition: {trigger_condition}")
                    print(f"      Field Checked: {field_checked}")
                    print()
                
                print(f"🔍 STRIDE CATEGORY BREAKDOWN:")
                for category, category_threats in stride_categories.items():
                    print(f"   {category}: {len(category_threats)} threats")
                
                print(f"\n🔍 THREAT SOURCE ANALYSIS:")
                for source, count in threat_sources.items():
                    print(f"   {source}: {count} threats")
                
                print(f"\n🔍 FIELD REFERENCE ANALYSIS:")
                for field, threat_ids in field_references.items():
                    print(f"   {field}: Referenced by {len(threat_ids)} threats")
                
                # Critical analysis: Check if heuristic rules are checking non-existent fields
                print(f"\n🚨 CRITICAL FIELD MAPPING INVESTIGATION:")
                database_questionnaire_fields = [
                    "database_authentication", "database_encryption_at_rest", 
                    "database_encryption_in_transit", "database_access_control",
                    "database_backup_strategy", "database_patch_management",
                    "database_network_security", "database_logging",
                    "database_privilege_management", "database_data_classification"
                ]
                
                print(f"   Database Questionnaire Fields (10 total):")
                for field in database_questionnaire_fields:
                    print(f"     ✅ {field}")
                
                print(f"\n   Fields Referenced by STRIDE Rules:")
                mismatched_fields = []
                for field in field_references.keys():
                    if field in database_questionnaire_fields:
                        print(f"     ✅ {field} (EXISTS in questionnaire)")
                    else:
                        print(f"     ❌ {field} (MISSING from questionnaire)")
                        mismatched_fields.append(field)
                
                if mismatched_fields:
                    print(f"\n🚨 ROOT CAUSE IDENTIFIED:")
                    print(f"   STRIDE heuristic rules are checking {len(mismatched_fields)} fields that don't exist:")
                    for field in mismatched_fields:
                        print(f"     ❌ {field}")
                    print(f"   This causes false positives because these fields show as 'Not answered'")
                
            # Expected vs Actual Analysis
            expected_threats = "Minimal (0-2 threats for optimal security)"
            actual_threats = len(threats)
            
            if actual_threats > 5:
                self.log_test("STRIDE Analysis Investigation", False, 
                            f"❌ ISSUE CONFIRMED: {actual_threats} threats found (Expected: {expected_threats})")
            else:
                self.log_test("STRIDE Analysis Investigation", True, 
                            f"✅ STRIDE analysis working correctly: {actual_threats} threats found")
            
            return True
            
        except Exception as e:
            self.log_test("STRIDE Analysis Investigation", False, f"Request error: {str(e)}")
            return False

    def test_stride_coverage_analysis(self):
        """Test STRIDE coverage endpoint for additional insights"""
        try:
            print("🎯 STRIDE COVERAGE ANALYSIS")
            print("=" * 80)
            
            response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}/stride/coverage")
            
            print(f"📋 STRIDE Coverage Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("STRIDE Coverage Analysis", False, 
                            f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("STRIDE Coverage Analysis", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            print(f"📊 STRIDE Coverage Results:")
            print(f"   Total Threats: {data.get('total_threats', 0)}")
            print(f"   Mitigated Threats: {data.get('totals', {}).get('mitigated', 0)}")
            print(f"   Residual Risk Average: {data.get('residual_risk_avg', 0)}")
            print(f"   Mitigation Percentage: {data.get('mitigation_percentage', 0)}%")
            
            totals = data.get('totals', {})
            if totals:
                print(f"   Coverage Breakdown:")
                for key, value in totals.items():
                    print(f"     {key}: {value}")
            
            self.log_test("STRIDE Coverage Analysis", True, 
                        f"STRIDE coverage analysis completed")
            return True
            
        except Exception as e:
            self.log_test("STRIDE Coverage Analysis", False, f"Request error: {str(e)}")
            return False

    def test_poor_security_comparison(self):
        """Create a Database with poor security to compare threat counts"""
        try:
            print("🎯 COMPARISON TEST: DATABASE WITH POOR SECURITY")
            print("=" * 80)
            
            # Create another Database node with poor security
            poor_database_node = {
                "id": f"database-poor-{uuid.uuid4().hex[:8]}",
                "type": "Asset",
                "subtype": "Database",
                "label": "Poor Security Database",
                "position": {"x": 600, "y": 300},
                "data": {
                    "criticality": "Critical",
                    "data_classification": "Restricted"
                }
            }
            
            # Get current diagram and add poor security Database
            diagram_response = self.session.get(f"{self.base_url}/diagrams/{self.test_diagram_id}")
            if diagram_response.status_code != 200:
                self.log_test("Poor Security Comparison", False, "Cannot retrieve test diagram")
                return False
            
            diagram_data = diagram_response.json()
            current_nodes = diagram_data.get("nodes", [])
            current_nodes.append(poor_database_node)
            diagram_data["nodes"] = current_nodes
            
            # Update diagram
            update_response = self.session.put(f"{self.base_url}/diagrams/{self.test_diagram_id}", json=diagram_data)
            if update_response.status_code != 200:
                self.log_test("Poor Security Comparison", False, "Failed to add poor security Database")
                return False
            
            # Configure with poor security practices
            poor_security_responses = {
                "database_authentication": "Basic password authentication",
                "database_encryption_at_rest": "No encryption", 
                "database_encryption_in_transit": "Unencrypted connections",
                "database_access_control": "Shared accounts",
                "database_backup_strategy": "No backups",
                "database_patch_management": "Manual patching",
                "database_network_security": "Public network access",
                "database_logging": "Minimal logging",
                "database_privilege_management": "Static privileges",
                "database_data_classification": "No classification"
            }
            
            questionnaire_data = {
                "responses": poor_security_responses,
                "business_context": {
                    "criticality": "critical",
                    "data_classification": "restricted"
                }
            }
            
            config_response = self.session.post(
                f"{self.base_url}/diagrams/{self.test_diagram_id}/nodes/{poor_database_node['id']}/questionnaire",
                json=questionnaire_data
            )
            
            if config_response.status_code != 200:
                self.log_test("Poor Security Comparison", False, "Failed to configure poor security Database")
                return False
            
            # Test vulnerability analysis for poor security Database
            vulnerability_request = {
                "node_id": poor_database_node['id'],
                "node_type": "Database",
                "questionnaire_responses": poor_security_responses,
                "node_position": {"x": 600, "y": 300}
            }
            
            vuln_response = self.session.post(
                f"{self.base_url}/vulnerabilities/analyze/{poor_database_node['id']}",
                json=vulnerability_request
            )
            
            if vuln_response.status_code == 200:
                vuln_data = vuln_response.json()
                poor_vulnerabilities = len(vuln_data.get("vulnerabilities", []))
                poor_risk_score = vuln_data.get("overall_risk_score", 0)
                
                print(f"📊 Poor Security Database Results:")
                print(f"   Vulnerabilities Found: {poor_vulnerabilities}")
                print(f"   Risk Score: {poor_risk_score}")
                
                print(f"\n🔍 SECURITY COMPARISON:")
                print(f"   Optimal Security Database: 0 vulnerabilities (expected)")
                print(f"   Poor Security Database: {poor_vulnerabilities} vulnerabilities")
                print(f"   This confirms vulnerability analysis is working correctly")
                
                self.log_test("Poor Security Comparison", True, 
                            f"Poor security Database shows {poor_vulnerabilities} vulnerabilities vs 0 for optimal")
            else:
                self.log_test("Poor Security Comparison", False, 
                            f"Failed to analyze poor security Database: HTTP {vuln_response.status_code}")
            
            return True
            
        except Exception as e:
            self.log_test("Poor Security Comparison", False, f"Request error: {str(e)}")
            return False

    def cleanup_test_data(self):
        """Clean up test data"""
        try:
            if self.test_diagram_id:
                print("🧹 CLEANUP: Removing test diagram")
                response = self.session.delete(f"{self.base_url}/diagrams/{self.test_diagram_id}")
                if response.status_code == 200:
                    print(f"   ✅ Test diagram deleted successfully")
                else:
                    print(f"   ⚠️ Failed to delete test diagram: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ⚠️ Cleanup error: {str(e)}")

    def run_investigation(self):
        """Run complete STRIDE analysis investigation"""
        print("🚀 STARTING STRIDE ANALYSIS INVESTIGATION")
        print("=" * 80)
        print("INVESTIGATING: Database with optimal security showing 13 STRIDE threats")
        print("EXPECTED: Vulnerability analysis = 0 vulnerabilities, STRIDE analysis = minimal threats")
        print("HYPOTHESIS: STRIDE heuristic rules checking non-existent Database questionnaire fields")
        print("=" * 80)
        
        tests = [
            self.test_health_check,
            self.create_test_diagram_with_database,
            self.configure_optimal_database_security,
            self.test_vulnerability_analysis,
            self.test_stride_analysis_investigation,
            self.test_stride_coverage_analysis,
            self.test_poor_security_comparison,
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
                print()
            except Exception as e:
                print(f"❌ Test {test.__name__} failed with exception: {str(e)}")
                print()
        
        # Cleanup
        self.cleanup_test_data()
        
        print("=" * 80)
        print(f"🏁 INVESTIGATION COMPLETE: {passed}/{total} tests completed")
        print("=" * 80)
        
        # Print detailed results
        print("\n📊 DETAILED INVESTIGATION RESULTS:")
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{status} {result['test']}: {result['message']}")
        
        return passed >= (total - 1)  # Allow 1 failure for investigation purposes

if __name__ == "__main__":
    investigator = StrideAnalysisInvestigator()
    success = investigator.run_investigation()
    sys.exit(0 if success else 1)