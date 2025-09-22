#!/usr/bin/env python3
"""
Backend API Testing - MONITORING QUESTIONNAIRE 404 FIX VERIFICATION
Tests the newly added Monitoring questionnaire functionality that was causing 404 errors.

TESTING FOCUS:
🔧 PRIMARY TEST:
1. **Test GET /api/intelligent-nodes/Monitoring/prompts endpoint**
   - Should return HTTP 200 (not 404)
   - Should contain monitoring questionnaire prompts
   - Verify response includes proper structure with prompts and node_subtype

🔧 VERIFICATION TESTS:
2. **Test that other intelligent node endpoints still work:**
   - GET /api/intelligent-nodes/Backup/prompts (this was working before)
   - GET /api/intelligent-nodes/supported-types (should now include Monitoring)

**EXPECTED RESULTS:**
- Monitoring endpoint should return success with monitoring security prompts
- No more 404 errors for Monitoring questionnaire
- Response should match the format: {success: true, prompts_count: X, node_subtype: 'Monitoring'}

**CONTEXT:** 
This fixes the exact issue shown in user console logs where GET /api/intelligent-nodes/Monitoring/prompts 
was returning 404. The fix adds the missing Monitoring IntelligentNodeTemplate to the main 
intelligent_nodes.py file, following the same pattern as the previously fixed Backup questionnaire.
"""

import requests
import json
import sys

# Use the backend URL from frontend/.env with /api suffix
BASE_URL = "https://update-depth-fix.preview.emergentagent.com/api"

class MonitoringQuestionnaireFixTester:
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
    # 🔧 PRIMARY TEST: Monitoring Questionnaire 404 Fix
    # ============================================================================
    
    def test_monitoring_questionnaire_prompts(self):
        """🔧 PRIMARY TEST: Test GET /api/intelligent-nodes/Monitoring/prompts endpoint"""
        try:
            print("🔧 Testing Monitoring questionnaire endpoint that was causing 404 errors...")
            
            response = self.session.get(f"{self.base_url}/intelligent-nodes/Monitoring/prompts")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure (actual API format)
                required_fields = ['prompts', 'node_subtype']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Monitoring Questionnaire Prompts", False, 
                                f"Missing required fields: {missing_fields}")
                    return False
                
                # Verify node_subtype is Monitoring
                if data.get('node_subtype') != 'Monitoring':
                    self.log_test("Monitoring Questionnaire Prompts", False, 
                                f"Wrong node_subtype: expected 'Monitoring', got '{data.get('node_subtype')}'")
                    return False
                
                # Verify prompts are present and reasonable count
                prompts = data.get('prompts', [])
                if not prompts or len(prompts) < 3:  # Should have at least 3 monitoring prompts
                    self.log_test("Monitoring Questionnaire Prompts", False, 
                                f"Too few prompts: expected at least 3, got {len(prompts)}")
                    return False
                
                self.log_test("Monitoring Questionnaire Prompts", True, 
                            f"✅ Monitoring endpoint returns HTTP 200 with {len(prompts)} prompts, node_subtype='Monitoring'")
                
                print(f"   📊 Response Details:")
                print(f"      Node Subtype: {data.get('node_subtype')}")
                print(f"      Prompts Count: {len(prompts)}")
                print(f"      Sample Prompt IDs: {[p.get('id', 'unknown') for p in prompts[:3]]}")
                
                return True
                
            elif response.status_code == 404:
                self.log_test("Monitoring Questionnaire Prompts", False, 
                            f"❌ STILL GETTING 404! Monitoring questionnaire not fixed: {response.text}")
                return False
            else:
                self.log_test("Monitoring Questionnaire Prompts", False, 
                            f"Unexpected HTTP status: {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Monitoring Questionnaire Prompts", False, f"Request error: {str(e)}")
            return False

    # ============================================================================
    # 🔧 VERIFICATION TESTS: Other Intelligent Node Endpoints
    # ============================================================================
    
    def test_backup_questionnaire_prompts(self):
        """🔧 VERIFICATION: Test GET /api/intelligent-nodes/Backup/prompts endpoint (should still work)"""
        try:
            print("🔧 Verifying Backup questionnaire endpoint still works...")
            
            response = self.session.get(f"{self.base_url}/intelligent-nodes/Backup/prompts")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify basic structure (actual API format)
                if data.get('node_subtype') == 'Backup' and 'prompts' in data:
                    prompts = data.get('prompts', [])
                    self.log_test("Backup Questionnaire Prompts", True, 
                                f"✅ Backup endpoint still works: {len(prompts)} prompts")
                    return True
                else:
                    self.log_test("Backup Questionnaire Prompts", False, 
                                f"Invalid response structure: missing node_subtype or prompts")
                    return False
            else:
                self.log_test("Backup Questionnaire Prompts", False, 
                            f"Backup endpoint failed: HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Backup Questionnaire Prompts", False, f"Request error: {str(e)}")
            return False
    
    def test_supported_types_includes_monitoring(self):
        """🔧 VERIFICATION: Test GET /api/intelligent-nodes/supported-types includes Monitoring"""
        try:
            print("🔧 Verifying supported-types endpoint includes Monitoring...")
            
            response = self.session.get(f"{self.base_url}/intelligent-nodes/supported-types")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if response has supported_types field
                if 'supported_types' not in data:
                    self.log_test("Supported Types Includes Monitoring", False, 
                                f"Missing 'supported_types' field: {data}")
                    return False
                
                supported_types = data['supported_types']
                
                # Extract node_subtype values from the list of objects
                node_subtypes = [item.get('node_subtype') for item in supported_types if isinstance(item, dict)]
                
                # Verify Monitoring is in the list
                if 'Monitoring' in node_subtypes:
                    self.log_test("Supported Types Includes Monitoring", True, 
                                f"✅ Monitoring is in supported types: {node_subtypes}")
                    
                    # Also verify Backup is still there
                    if 'Backup' in node_subtypes:
                        print(f"   ✅ Backup is also in supported types (good)")
                    else:
                        print(f"   ⚠️  Backup not in supported types: {node_subtypes}")
                    
                    return True
                else:
                    self.log_test("Supported Types Includes Monitoring", False, 
                                f"❌ Monitoring NOT in supported types: {node_subtypes}")
                    return False
            else:
                self.log_test("Supported Types Includes Monitoring", False, 
                            f"Supported types endpoint failed: HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Supported Types Includes Monitoring", False, f"Request error: {str(e)}")
            return False

    # ============================================================================
    # Test Runner
    # ============================================================================
    
    def run_monitoring_questionnaire_tests(self):
        """Run all Monitoring questionnaire 404 fix tests"""
        print("🚀 Starting Monitoring Questionnaire 404 Fix Tests")
        print("=" * 90)
        print("🔧 MONITORING QUESTIONNAIRE 404 FIX VERIFICATION")
        print("Testing the newly added Monitoring questionnaire functionality that was causing 404 errors")
        print("Focus: GET /api/intelligent-nodes/Monitoring/prompts endpoint")
        print("=" * 90)
        
        tests = [
            # Basic connectivity
            self.test_health_check,
            
            # 🔧 PRIMARY TEST: Monitoring Questionnaire 404 Fix
            self.test_monitoring_questionnaire_prompts,
            
            # 🔧 VERIFICATION TESTS: Other Intelligent Node Endpoints
            self.test_backup_questionnaire_prompts,
            self.test_supported_types_includes_monitoring,
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
        print("=" * 90)
        print("🎯 MONITORING QUESTIONNAIRE 404 FIX SUMMARY")
        print("=" * 90)
        print(f"✅ PASSED: {passed}")
        print(f"❌ FAILED: {failed}")
        print(f"📊 SUCCESS RATE: {(passed / (passed + failed) * 100):.1f}%")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED! Monitoring questionnaire 404 fix verification successful.")
            print("✅ GET /api/intelligent-nodes/Monitoring/prompts returns HTTP 200 (not 404)")
            print("✅ Monitoring questionnaire contains proper security prompts")
            print("✅ Response includes correct structure with prompts and node_subtype")
            print("✅ Backup questionnaire endpoint still works correctly")
            print("✅ Supported types endpoint includes Monitoring")
            print("✅ No more 404 errors for Monitoring questionnaire!")
        else:
            print(f"\n⚠️  {failed} tests failed. Analysis:")
            
            # Analyze the test results to provide diagnostic information
            error_tests = [result for result in self.test_results if not result['success']]
            
            for error_test in error_tests:
                print(f"🚨 FAILED: {error_test['test']}")
                print(f"   Issue: {error_test['message']}")
        
        return passed, failed

def main():
    """Main test execution"""
    tester = MonitoringQuestionnaireFixTester()
    passed, failed = tester.run_monitoring_questionnaire_tests()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()