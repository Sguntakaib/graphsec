#!/usr/bin/env python3
"""
Dependency Check Testing
Tests the dependency checking functionality to understand how parent-child relationships work.
"""

import requests
import json
import uuid
from datetime import datetime, timezone
import sys

# Use the backend URL from frontend/.env with /api suffix
BASE_URL = "https://statuschange-notify.preview.emergentagent.com/api"

class DependencyCheckTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        
    def test_webapp_dependency_check(self):
        """Test WebApp dependency checking"""
        try:
            print("🎯 TESTING: WebApp Dependency Check")
            print("=" * 80)
            
            # Test WebApp dependency check with database connection enabled
            request_data = {
                "answers": {
                    "authentication_method": "oauth2",
                    "encryption_enabled": True,
                    "input_validation": "comprehensive",
                    "webapp_database_connection": True,  # This should trigger Database dependency
                    "webapp_api_endpoints": False,
                    "webapp_external_services": False
                }
            }
            
            response = self.session.post(f"{self.base_url}/intelligent-nodes/WebApp/check-dependencies", json=request_data)
            
            print(f"📋 Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                print(f"❌ FAIL: HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                print(f"❌ FAIL: Invalid JSON response: {str(e)}")
                return False
            
            print(f"📊 WebApp Dependency Check Results:")
            print(f"   Success: {data.get('success', False)}")
            print(f"   Node subtype: {data.get('node_subtype', 'None')}")
            print(f"   Dependent nodes: {data.get('dependent_nodes', [])}")
            print(f"   Dependencies found: {data.get('dependencies_found', 0)}")
            
            # Check if Database dependency was found
            dependent_nodes = data.get('dependent_nodes', [])
            database_dependencies = [node for node in dependent_nodes if 'Database' in str(node)]
            
            if database_dependencies:
                print(f"✅ SUCCESS: Database dependency detected: {database_dependencies}")
                return True
            else:
                print(f"❌ FAIL: Database dependency not detected")
                return False
            
        except Exception as e:
            print(f"❌ FAIL: Request error: {str(e)}")
            return False

    def test_database_dependency_check(self):
        """Test Database dependency checking"""
        try:
            print("🎯 TESTING: Database Dependency Check")
            print("=" * 80)
            
            # Test Database dependency check with backup enabled
            request_data = {
                "answers": {
                    "db_type": "PostgreSQL",
                    "db_encryption_at_rest": "AES-256",
                    "db_backup_enabled": True,  # This should trigger Backup dependency
                    "db_access_control": ["Role-Based Access", "User Authentication"],
                    "db_monitoring_enabled": True  # This should trigger Monitoring dependency
                }
            }
            
            response = self.session.post(f"{self.base_url}/intelligent-nodes/Database/check-dependencies", json=request_data)
            
            print(f"📋 Response Status: HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(error_data))
                except:
                    error_detail = response.text
                
                print(f"❌ FAIL: HTTP {response.status_code}: {error_detail}")
                return False
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                print(f"❌ FAIL: Invalid JSON response: {str(e)}")
                return False
            
            print(f"📊 Database Dependency Check Results:")
            print(f"   Success: {data.get('success', False)}")
            print(f"   Node subtype: {data.get('node_subtype', 'None')}")
            print(f"   Dependent nodes: {data.get('dependent_nodes', [])}")
            print(f"   Dependencies found: {data.get('dependencies_found', 0)}")
            
            # Check if Backup dependency was found
            dependent_nodes = data.get('dependent_nodes', [])
            backup_dependencies = [node for node in dependent_nodes if 'Backup' in str(node)]
            
            if backup_dependencies:
                print(f"✅ SUCCESS: Backup dependency detected: {backup_dependencies}")
                return True
            else:
                print(f"❌ FAIL: Backup dependency not detected")
                return False
            
        except Exception as e:
            print(f"❌ FAIL: Request error: {str(e)}")
            return False

    def test_questionnaire_endpoints(self):
        """Test available questionnaire endpoints"""
        try:
            print("🎯 TESTING: Available Questionnaire Endpoints")
            print("=" * 80)
            
            # Test WebApp questionnaire endpoint
            response = self.session.get(f"{self.base_url}/questionnaires/WebApp")
            print(f"📋 WebApp Questionnaire: HTTP {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Success: {data.get('success', False)}")
                print(f"   Prompts count: {data.get('prompts_count', 0)}")
            
            # Test Database questionnaire endpoint
            response = self.session.get(f"{self.base_url}/questionnaires/Database")
            print(f"📋 Database Questionnaire: HTTP {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Success: {data.get('success', False)}")
                print(f"   Prompts count: {data.get('prompts_count', 0)}")
            
            # Test Backup questionnaire endpoint
            response = self.session.get(f"{self.base_url}/questionnaires/Backup")
            print(f"📋 Backup Questionnaire: HTTP {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Success: {data.get('success', False)}")
                print(f"   Prompts count: {data.get('prompts_count', 0)}")
            
            return True
            
        except Exception as e:
            print(f"❌ FAIL: Request error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all dependency check tests"""
        print("🚀 STARTING DEPENDENCY CHECK TESTING")
        print("=" * 80)
        
        tests = [
            self.test_webapp_dependency_check,
            self.test_database_dependency_check,
            self.test_questionnaire_endpoints,
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
        
        return passed == total

if __name__ == "__main__":
    tester = DependencyCheckTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)