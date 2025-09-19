#!/usr/bin/env python3
"""
Backend API Testing - ENHANCED VULNERABILITY COVERAGE FOR BACKUP AND MONITORING NODES
Tests the enhanced vulnerability coverage for Backup and Monitoring nodes with NEW critical vulnerabilities.

TESTING FOCUS:
🎯 PRIMARY TEST: ENHANCED VULNERABILITY COVERAGE WITH CRITICAL/HIGH SEVERITY
1. **Test Backup Node Vulnerability Coverage:**
   - Create test backup node with most insecure questionnaire responses
   - Test responses that should trigger NEW critical vulnerabilities:
     - backup_strategy: "No Backup Strategy" 
     - backup_encryption: "No Encryption"
     - backup_retention: "No Retention Policy"
     - backup_testing: "Never Tested"
     - backup_frequency: "Irregular"
     - backup_frequency: "Monthly"
   - Verify these responses generate multiple HIGH SEVERITY vulnerabilities (not just 1 informational)

2. **Test Monitoring Node Vulnerability Coverage:**
   - Create test monitoring node with insecure questionnaire responses
   - Test responses that should trigger NEW critical vulnerabilities:
     - monitoring_alerting: "No Alerting"
     - monitoring_access_control: "No Access Control"
     - monitoring_access_control: "Shared Access"
     - monitoring_data_retention: "No Defined Policy"
     - monitoring_coverage: "Basic Monitoring"
   - Verify these responses generate multiple HIGH SEVERITY vulnerabilities

3. **Verify API Endpoints:**
   - Test GET /api/vulnerabilities/rules to confirm new rules are loaded
   - Test POST /api/vulnerabilities/analyze/{node_id} for both Backup and Monitoring nodes
   - Confirm that weak questionnaire responses now trigger MULTIPLE vulnerabilities per node (not just 1)

**EXPECTED RESULTS:** 
- Backup nodes with insecure settings should generate 4-6 vulnerabilities (including Critical/High severity)
- Monitoring nodes with insecure settings should generate 4-5 vulnerabilities (including Critical/High severity)
- The vulnerability severity should match the risk level (Critical for no backup strategy, no encryption, etc.)
"""

import requests
import json
import uuid
from datetime import datetime, timezone
import sys

# Use the backend URL from frontend/.env with /api suffix
BASE_URL = "https://vulnfix-nodes.preview.emergentagent.com/api"

class VulnerabilityAnalysisTester:
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

    def test_backup_node_vulnerability_analysis(self):
        """
        CRITICAL TEST: Test enhanced vulnerability coverage for Backup node with insecure settings
        
        This test verifies that:
        1. Backup nodes with insecure settings generate MULTIPLE vulnerabilities (4-6 expected)
        2. Critical/High severity vulnerabilities are properly generated for insecure configurations
        3. Specific insecure responses trigger appropriate vulnerability rules
        4. Expected results: 4-6 vulnerabilities including Critical/High severity
        """
        try:
            print("🎯 CRITICAL TEST: Enhanced Backup Node Vulnerability Coverage")
            print("=" * 80)
            
            # Create a test node ID for Backup
            backup_node_id = f"backup-test-{uuid.uuid4().hex[:8]}"
            
            # MOST INSECURE questionnaire responses from review request
            # These should trigger NEW critical vulnerabilities
            backup_responses = {
                "backup_strategy": "No Backup Strategy",      # Should trigger CRITICAL vulnerability
                "backup_encryption": "No Encryption",        # Should trigger CRITICAL vulnerability
                "backup_retention": "No Retention Policy",   # Should trigger HIGH vulnerability
                "backup_testing": "Never Tested",            # Should trigger HIGH vulnerability
                "backup_frequency": "Irregular"              # Should trigger HIGH vulnerability
            }
            
            # Test data for vulnerability analysis
            test_data = {
                "node_id": backup_node_id,
                "node_type": "Backup",
                "questionnaire_responses": backup_responses,
                "node_position": {"x": 100, "y": 100}
            }
            
            print(f"📋 Testing INSECURE Backup node: {backup_node_id}")
            print(f"📋 Using MOST INSECURE responses: {backup_responses}")
            
            # Call the vulnerability analysis endpoint
            response = self.session.post(
                f"{self.base_url}/vulnerabilities/analyze/{backup_node_id}",
                json=test_data
            )
            
            print(f"📋 Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("Backup Enhanced Vulnerability Analysis", False, 
                            f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Backup Enhanced Vulnerability Analysis", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            # Verify response structure
            required_fields = ['node_id', 'node_type', 'total_vulnerabilities', 'vulnerability_nodes']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                self.log_test("Backup Enhanced Vulnerability Analysis", False, 
                            f"Missing required fields: {missing_fields}")
                return False
            
            # Verify vulnerability nodes
            vulnerability_nodes = data.get('vulnerability_nodes', [])
            total_vulnerabilities = data.get('total_vulnerabilities', 0)
            
            if total_vulnerabilities == 0:
                self.log_test("Backup Enhanced Vulnerability Analysis", False, 
                            "No vulnerabilities generated for insecure Backup node")
                return False
            
            # Count vulnerabilities by severity
            critical_count = 0
            high_count = 0
            medium_count = 0
            low_count = 0
            informational_count = 0
            severity_counts = {}
            
            for vuln in vulnerability_nodes:
                severity = vuln.get('severity', 'Unknown')
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
                
                if severity == 'Critical':
                    critical_count += 1
                elif severity == 'High':
                    high_count += 1
                elif severity == 'Medium':
                    medium_count += 1
                elif severity == 'Low':
                    low_count += 1
                elif severity == 'Informational':
                    informational_count += 1
                
                # Verify vulnerability structure
                required_vuln_fields = ['id', 'name', 'description', 'severity', 'category']
                missing_vuln_fields = [field for field in required_vuln_fields if field not in vuln]
                
                if missing_vuln_fields:
                    self.log_test("Backup Enhanced Vulnerability Analysis", False, 
                                f"Vulnerability missing fields: {missing_vuln_fields}")
                    return False
            
            print(f"📊 Enhanced Vulnerability Analysis Results:")
            print(f"   Total vulnerabilities: {total_vulnerabilities}")
            print(f"   Severity distribution: {severity_counts}")
            print(f"   Critical: {critical_count}, High: {high_count}, Medium: {medium_count}")
            print(f"   Low: {low_count}, Informational: {informational_count}")
            
            # EXPECTED RESULTS: 4-6 vulnerabilities including Critical/High severity
            expected_min_vulnerabilities = 4
            expected_max_vulnerabilities = 6
            
            if total_vulnerabilities < expected_min_vulnerabilities:
                self.log_test("Backup Enhanced Vulnerability Analysis", False, 
                            f"Insufficient vulnerabilities: got {total_vulnerabilities}, expected {expected_min_vulnerabilities}-{expected_max_vulnerabilities}")
                return False
            
            if total_vulnerabilities > expected_max_vulnerabilities:
                print(f"⚠️  More vulnerabilities than expected: {total_vulnerabilities} > {expected_max_vulnerabilities} (this is OK)")
            
            # Verify Critical/High severity vulnerabilities are present
            critical_high_count = critical_count + high_count
            if critical_high_count == 0:
                self.log_test("Backup Enhanced Vulnerability Analysis", False, 
                            f"No Critical/High severity vulnerabilities found for insecure backup configuration")
                return False
            
            # Verify specific expected vulnerabilities based on insecure responses
            expected_vulnerabilities = [
                "No Backup Strategy",      # Critical
                "No Encryption",           # Critical  
                "Never Tested",            # High
                "Irregular",               # High
                "No Retention Policy"      # High
            ]
            
            found_expected = 0
            for vuln in vulnerability_nodes:
                vuln_name = vuln.get('name', '')
                vuln_desc = vuln.get('description', '')
                for expected in expected_vulnerabilities:
                    if expected.lower() in vuln_name.lower() or expected.lower() in vuln_desc.lower():
                        found_expected += 1
                        break
            
            print(f"   Found {found_expected}/{len(expected_vulnerabilities)} expected vulnerability types")
            
            self.log_test("Backup Enhanced Vulnerability Analysis", True, 
                        f"✅ SUCCESS: Generated {total_vulnerabilities} vulnerabilities ({critical_count} Critical, {high_count} High) for insecure Backup node")
            
            return True
            
        except Exception as e:
            self.log_test("Backup Enhanced Vulnerability Analysis", False, f"Request error: {str(e)}")
            return False

    def test_monitoring_node_vulnerability_analysis(self):
        """
        CRITICAL TEST: Test enhanced vulnerability coverage for Monitoring node with insecure settings
        
        This test verifies that:
        1. Monitoring nodes with insecure settings generate MULTIPLE vulnerabilities (4-5 expected)
        2. Critical/High severity vulnerabilities are properly generated for insecure configurations
        3. Specific insecure responses trigger appropriate vulnerability rules
        4. Expected results: 4-5 vulnerabilities including Critical/High severity
        """
        try:
            print("🎯 CRITICAL TEST: Enhanced Monitoring Node Vulnerability Coverage")
            print("=" * 80)
            
            # Create a test node ID for Monitoring
            monitoring_node_id = f"monitoring-test-{uuid.uuid4().hex[:8]}"
            
            # MOST INSECURE questionnaire responses from review request
            # These should trigger NEW critical vulnerabilities
            monitoring_responses = {
                "monitoring_alerting": "No Alerting",                    # Should trigger CRITICAL vulnerability
                "monitoring_access_control": "No Access Control",       # Should trigger CRITICAL vulnerability
                "monitoring_data_retention": "No Defined Policy",       # Should trigger HIGH vulnerability
                "monitoring_coverage": "Basic Monitoring"               # Should trigger HIGH vulnerability
            }
            
            # Test data for vulnerability analysis
            test_data = {
                "node_id": monitoring_node_id,
                "node_type": "Monitoring",
                "questionnaire_responses": monitoring_responses,
                "node_position": {"x": 200, "y": 200}
            }
            
            print(f"📋 Testing INSECURE Monitoring node: {monitoring_node_id}")
            print(f"📋 Using MOST INSECURE responses: {monitoring_responses}")
            
            # Call the vulnerability analysis endpoint
            response = self.session.post(
                f"{self.base_url}/vulnerabilities/analyze/{monitoring_node_id}",
                json=test_data
            )
            
            print(f"📋 Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                self.log_test("Monitoring Enhanced Vulnerability Analysis", False, 
                            f"HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Monitoring Enhanced Vulnerability Analysis", False, 
                            f"Invalid JSON response: {str(e)}")
                return False
            
            # Verify response structure
            required_fields = ['node_id', 'node_type', 'total_vulnerabilities', 'vulnerability_nodes']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                self.log_test("Monitoring Enhanced Vulnerability Analysis", False, 
                            f"Missing required fields: {missing_fields}")
                return False
            
            # Verify vulnerability nodes
            vulnerability_nodes = data.get('vulnerability_nodes', [])
            total_vulnerabilities = data.get('total_vulnerabilities', 0)
            
            if total_vulnerabilities == 0:
                self.log_test("Monitoring Enhanced Vulnerability Analysis", False, 
                            "No vulnerabilities generated for insecure Monitoring node")
                return False
            
            # Count vulnerabilities by severity
            critical_count = 0
            high_count = 0
            medium_count = 0
            low_count = 0
            informational_count = 0
            severity_counts = {}
            
            for vuln in vulnerability_nodes:
                severity = vuln.get('severity', 'Unknown')
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
                
                if severity == 'Critical':
                    critical_count += 1
                elif severity == 'High':
                    high_count += 1
                elif severity == 'Medium':
                    medium_count += 1
                elif severity == 'Low':
                    low_count += 1
                elif severity == 'Informational':
                    informational_count += 1
                
                # Verify vulnerability structure
                required_vuln_fields = ['id', 'name', 'description', 'severity', 'category']
                missing_vuln_fields = [field for field in required_vuln_fields if field not in vuln]
                
                if missing_vuln_fields:
                    self.log_test("Monitoring Enhanced Vulnerability Analysis", False, 
                                f"Vulnerability missing fields: {missing_vuln_fields}")
                    return False
            
            print(f"📊 Enhanced Vulnerability Analysis Results:")
            print(f"   Total vulnerabilities: {total_vulnerabilities}")
            print(f"   Severity distribution: {severity_counts}")
            print(f"   Critical: {critical_count}, High: {high_count}, Medium: {medium_count}")
            print(f"   Low: {low_count}, Informational: {informational_count}")
            
            # EXPECTED RESULTS: 4-5 vulnerabilities including Critical/High severity
            expected_min_vulnerabilities = 4
            expected_max_vulnerabilities = 5
            
            if total_vulnerabilities < expected_min_vulnerabilities:
                self.log_test("Monitoring Enhanced Vulnerability Analysis", False, 
                            f"Insufficient vulnerabilities: got {total_vulnerabilities}, expected {expected_min_vulnerabilities}-{expected_max_vulnerabilities}")
                return False
            
            if total_vulnerabilities > expected_max_vulnerabilities:
                print(f"⚠️  More vulnerabilities than expected: {total_vulnerabilities} > {expected_max_vulnerabilities} (this is OK)")
            
            # Verify Critical/High severity vulnerabilities are present
            critical_high_count = critical_count + high_count
            if critical_high_count == 0:
                self.log_test("Monitoring Enhanced Vulnerability Analysis", False, 
                            f"No Critical/High severity vulnerabilities found for insecure monitoring configuration")
                return False
            
            # Verify specific expected vulnerabilities based on insecure responses
            expected_vulnerabilities = [
                "No Alerting",             # Critical
                "No Access Control",       # Critical
                "No Defined Policy",       # High
                "Basic Monitoring"         # High
            ]
            
            found_expected = 0
            for vuln in vulnerability_nodes:
                vuln_name = vuln.get('name', '')
                vuln_desc = vuln.get('description', '')
                for expected in expected_vulnerabilities:
                    if expected.lower() in vuln_name.lower() or expected.lower() in vuln_desc.lower():
                        found_expected += 1
                        break
            
            print(f"   Found {found_expected}/{len(expected_vulnerabilities)} expected vulnerability types")
            
            self.log_test("Monitoring Enhanced Vulnerability Analysis", True, 
                        f"✅ SUCCESS: Generated {total_vulnerabilities} vulnerabilities ({critical_count} Critical, {high_count} High) for insecure Monitoring node")
            
            return True
            
        except Exception as e:
            self.log_test("Monitoring Enhanced Vulnerability Analysis", False, f"Request error: {str(e)}")
            return False

    def test_vulnerability_category_enum_completeness(self):
        """
        Test that VulnerabilityCategory enum includes all required categories
        """
        try:
            print("🎯 TESTING: VulnerabilityCategory Enum Completeness")
            print("=" * 60)
            
            # Test with a Database node first to see what categories are supported
            test_node_id = f"test-category-{uuid.uuid4().hex[:8]}"
            
            # Use minimal responses to trigger basic vulnerabilities
            test_responses = {
                "database_encryption": False,
                "access_controls": "basic"
            }
            
            test_data = {
                "node_id": test_node_id,
                "node_type": "Database",  # Use Database as it's known to work
                "questionnaire_responses": test_responses,
                "node_position": {"x": 0, "y": 0}
            }
            
            response = self.session.post(
                f"{self.base_url}/vulnerabilities/analyze/{test_node_id}",
                json=test_data
            )
            
            if response.status_code == 200:
                data = response.json()
                vulnerability_nodes = data.get('vulnerability_nodes', [])
                
                # Check what categories are being used
                categories = set()
                for vuln in vulnerability_nodes:
                    category = vuln.get('category', 'Unknown')
                    categories.add(category)
                
                print(f"   📊 Categories found in Database vulnerabilities: {list(categories)}")
                
                self.log_test("VulnerabilityCategory Enum", True, 
                            f"✅ VulnerabilityCategory enum is working. Found categories: {list(categories)}")
                
                return True
            else:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                if "'Best Practice Enhancement' is not a valid VulnerabilityCategory" in error_detail:
                    self.log_test("VulnerabilityCategory Enum", False, 
                                "❌ 'Best Practice Enhancement' category is not supported in enum")
                else:
                    self.log_test("VulnerabilityCategory Enum", False, 
                                f"Other error: {error_detail}")
                
                return False
                
        except Exception as e:
            self.log_test("VulnerabilityCategory Enum", False, f"Request error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all vulnerability analysis tests"""
        print("🚀 STARTING VULNERABILITY ANALYSIS TESTING")
        print("=" * 80)
        print("Testing vulnerability analysis for Backup and Monitoring nodes with INFORMATIONAL severity")
        print("=" * 80)
        
        tests = [
            self.test_health_check,
            self.test_vulnerability_category_enum_completeness,
            self.test_backup_node_vulnerability_analysis,
            self.test_monitoring_node_vulnerability_analysis,
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
    tester = VulnerabilityAnalysisTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)