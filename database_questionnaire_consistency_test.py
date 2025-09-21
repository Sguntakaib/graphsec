#!/usr/bin/env python3
"""
Database Questionnaire Length Inconsistency Investigation
=========================================================

CRITICAL ISSUE INVESTIGATION:
Database questionnaire is returning inconsistent question counts, causing resumption failures.

SPECIFIC TESTS:
1. Test Database questionnaire endpoint multiple times for consistency
2. Compare with other questionnaire endpoints (WebApp, API)
3. Check response structure for total_questions vs actual prompts.length
4. Look for caching or state issues

CONTEXT FROM USER LOGS:
- Database questionnaire shows "0/5 questions answered" (suggests 5 questions)
- But resumption fails with "Resume index 4 is beyond questionnaire length 3" (suggests 3 questions)
- This inconsistency breaks parent-child questionnaire resumption

EXPECTED OUTCOME:
Database questionnaire endpoint should return consistent question count every time.
"""

import requests
import json
import time
from datetime import datetime

# Use the backend URL from frontend/.env with /api suffix
BASE_URL = "https://recursive-loop-fix.preview.emergentagent.com/api"

class DatabaseQuestionnaireConsistencyTester:
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
            "response_data": response_data,
            "timestamp": datetime.now().isoformat()
        })
        
    def test_health_check(self):
        """Test API connectivity"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Check", True, f"API is healthy: {data.get('message', 'OK')}")
                return True
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Connection error: {str(e)}")
            return False

    def test_database_questionnaire_consistency(self):
        """Test Database questionnaire endpoint multiple times for consistency"""
        print("\n🔍 TESTING DATABASE QUESTIONNAIRE CONSISTENCY")
        print("=" * 60)
        
        try:
            endpoint = f"{self.base_url}/questionnaires/Database?level=basic"
            test_runs = 5
            results = []
            
            print(f"📋 Testing endpoint: GET {endpoint}")
            print(f"🔄 Running {test_runs} consecutive tests...")
            
            for i in range(test_runs):
                print(f"\n   Test Run #{i+1}:")
                
                response = self.session.get(endpoint)
                
                if response.status_code != 200:
                    print(f"   ❌ HTTP {response.status_code}: {response.text}")
                    results.append({
                        "run": i+1,
                        "status": "error",
                        "status_code": response.status_code,
                        "error": response.text
                    })
                    continue
                
                try:
                    data = response.json()
                    
                    # Extract key metrics
                    prompts = data.get('prompts', [])
                    total_questions = data.get('total_questions', 0)
                    actual_prompts_count = len(prompts)
                    
                    result = {
                        "run": i+1,
                        "status": "success",
                        "total_questions_field": total_questions,
                        "actual_prompts_count": actual_prompts_count,
                        "prompts_length": len(prompts),
                        "success": data.get('success', False),
                        "level": data.get('level', 'unknown'),
                        "node_subtype": data.get('node_subtype', 'unknown'),
                        "response_keys": list(data.keys())
                    }
                    
                    results.append(result)
                    
                    print(f"   ✅ Success: {data.get('success', False)}")
                    print(f"   📊 total_questions field: {total_questions}")
                    print(f"   📊 actual prompts.length: {actual_prompts_count}")
                    print(f"   📊 level: {data.get('level', 'unknown')}")
                    print(f"   📊 node_subtype: {data.get('node_subtype', 'unknown')}")
                    
                    # Check for inconsistency
                    if total_questions != actual_prompts_count:
                        print(f"   ⚠️  INCONSISTENCY DETECTED: total_questions ({total_questions}) != prompts.length ({actual_prompts_count})")
                    
                except json.JSONDecodeError as e:
                    print(f"   ❌ JSON decode error: {str(e)}")
                    results.append({
                        "run": i+1,
                        "status": "json_error",
                        "error": str(e)
                    })
                
                # Small delay between requests
                time.sleep(0.5)
            
            # Analyze consistency
            successful_runs = [r for r in results if r.get('status') == 'success']
            
            if not successful_runs:
                self.log_test("Database Questionnaire Consistency", False, 
                            f"No successful runs out of {test_runs} attempts")
                return False
            
            # Check for consistency across runs
            first_run = successful_runs[0]
            inconsistencies = []
            
            for run in successful_runs[1:]:
                if run['total_questions_field'] != first_run['total_questions_field']:
                    inconsistencies.append(f"total_questions varies: run {first_run['run']}={first_run['total_questions_field']}, run {run['run']}={run['total_questions_field']}")
                
                if run['actual_prompts_count'] != first_run['actual_prompts_count']:
                    inconsistencies.append(f"prompts.length varies: run {first_run['run']}={first_run['actual_prompts_count']}, run {run['run']}={run['actual_prompts_count']}")
            
            # Check internal consistency (total_questions vs prompts.length)
            internal_inconsistencies = []
            for run in successful_runs:
                if run['total_questions_field'] != run['actual_prompts_count']:
                    internal_inconsistencies.append(f"Run {run['run']}: total_questions ({run['total_questions_field']}) != prompts.length ({run['actual_prompts_count']})")
            
            print(f"\n📊 CONSISTENCY ANALYSIS:")
            print(f"   Successful runs: {len(successful_runs)}/{test_runs}")
            
            if inconsistencies:
                print(f"   ❌ CROSS-RUN INCONSISTENCIES FOUND:")
                for inconsistency in inconsistencies:
                    print(f"      • {inconsistency}")
            else:
                print(f"   ✅ Cross-run consistency: PASSED")
            
            if internal_inconsistencies:
                print(f"   ❌ INTERNAL INCONSISTENCIES FOUND:")
                for inconsistency in internal_inconsistencies:
                    print(f"      • {inconsistency}")
            else:
                print(f"   ✅ Internal consistency: PASSED")
            
            # Overall result
            has_issues = bool(inconsistencies or internal_inconsistencies)
            
            if has_issues:
                self.log_test("Database Questionnaire Consistency", False, 
                            f"Inconsistencies found: {len(inconsistencies)} cross-run, {len(internal_inconsistencies)} internal",
                            {"results": results, "inconsistencies": inconsistencies, "internal_inconsistencies": internal_inconsistencies})
                return False
            else:
                self.log_test("Database Questionnaire Consistency", True, 
                            f"All {len(successful_runs)} runs consistent: total_questions={first_run['total_questions_field']}, prompts.length={first_run['actual_prompts_count']}",
                            {"results": results})
                return True
                
        except Exception as e:
            self.log_test("Database Questionnaire Consistency", False, f"Test error: {str(e)}")
            return False

    def test_compare_questionnaire_endpoints(self):
        """Compare Database questionnaire with WebApp and API questionnaires"""
        print("\n🔍 COMPARING QUESTIONNAIRE ENDPOINTS")
        print("=" * 60)
        
        try:
            endpoints = [
                ("WebApp", f"{self.base_url}/questionnaires/WebApp?level=basic"),
                ("API", f"{self.base_url}/questionnaires/API?level=basic"),
                ("Database", f"{self.base_url}/questionnaires/Database?level=basic")
            ]
            
            results = {}
            
            for name, endpoint in endpoints:
                print(f"\n📋 Testing {name} questionnaire:")
                
                response = self.session.get(endpoint)
                
                if response.status_code != 200:
                    print(f"   ❌ HTTP {response.status_code}: {response.text}")
                    results[name] = {"status": "error", "status_code": response.status_code}
                    continue
                
                try:
                    data = response.json()
                    
                    prompts = data.get('prompts', [])
                    total_questions = data.get('total_questions', 0)
                    actual_prompts_count = len(prompts)
                    
                    result = {
                        "status": "success",
                        "total_questions_field": total_questions,
                        "actual_prompts_count": actual_prompts_count,
                        "success": data.get('success', False),
                        "level": data.get('level', 'unknown'),
                        "node_subtype": data.get('node_subtype', 'unknown'),
                        "consistent": total_questions == actual_prompts_count
                    }
                    
                    results[name] = result
                    
                    print(f"   ✅ Success: {result['success']}")
                    print(f"   📊 total_questions: {total_questions}")
                    print(f"   📊 prompts.length: {actual_prompts_count}")
                    print(f"   📊 Internal consistency: {'✅ PASS' if result['consistent'] else '❌ FAIL'}")
                    
                except json.JSONDecodeError as e:
                    print(f"   ❌ JSON decode error: {str(e)}")
                    results[name] = {"status": "json_error", "error": str(e)}
            
            # Analysis
            successful_results = {k: v for k, v in results.items() if v.get('status') == 'success'}
            
            print(f"\n📊 COMPARISON ANALYSIS:")
            print(f"   Successful endpoints: {len(successful_results)}/{len(endpoints)}")
            
            # Check which endpoints have internal consistency issues
            inconsistent_endpoints = [name for name, result in successful_results.items() if not result.get('consistent', False)]
            
            if inconsistent_endpoints:
                print(f"   ❌ ENDPOINTS WITH INTERNAL INCONSISTENCIES:")
                for name in inconsistent_endpoints:
                    result = successful_results[name]
                    print(f"      • {name}: total_questions ({result['total_questions_field']}) != prompts.length ({result['actual_prompts_count']})")
            else:
                print(f"   ✅ All endpoints internally consistent")
            
            # Show question counts for comparison
            print(f"\n📊 QUESTION COUNTS BY ENDPOINT:")
            for name, result in successful_results.items():
                if result.get('status') == 'success':
                    print(f"   {name}: {result['actual_prompts_count']} questions")
            
            # Focus on Database endpoint
            database_result = results.get('Database', {})
            if database_result.get('status') == 'success':
                database_consistent = database_result.get('consistent', False)
                database_count = database_result.get('actual_prompts_count', 0)
                
                if database_consistent:
                    self.log_test("Compare Questionnaire Endpoints", True, 
                                f"Database questionnaire internally consistent with {database_count} questions",
                                {"results": results})
                    return True
                else:
                    self.log_test("Compare Questionnaire Endpoints", False, 
                                f"Database questionnaire internally inconsistent: total_questions ({database_result['total_questions_field']}) != prompts.length ({database_result['actual_prompts_count']})",
                                {"results": results})
                    return False
            else:
                self.log_test("Compare Questionnaire Endpoints", False, 
                            f"Database questionnaire endpoint failed: {database_result}",
                            {"results": results})
                return False
                
        except Exception as e:
            self.log_test("Compare Questionnaire Endpoints", False, f"Test error: {str(e)}")
            return False

    def test_intelligent_nodes_database_prompts(self):
        """Test the alternative Database prompts endpoint"""
        print("\n🔍 TESTING INTELLIGENT NODES DATABASE PROMPTS")
        print("=" * 60)
        
        try:
            endpoint = f"{self.base_url}/intelligent-nodes/Database/prompts"
            
            print(f"📋 Testing endpoint: GET {endpoint}")
            
            response = self.session.get(endpoint)
            
            if response.status_code != 200:
                print(f"   ❌ HTTP {response.status_code}: {response.text}")
                self.log_test("Intelligent Nodes Database Prompts", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
            
            try:
                data = response.json()
                
                prompts = data.get('prompts', [])
                prompts_count = data.get('prompts_count', 0)
                actual_prompts_count = len(prompts)
                
                print(f"   ✅ Success: {data.get('success', False)}")
                print(f"   📊 prompts_count field: {prompts_count}")
                print(f"   📊 actual prompts.length: {actual_prompts_count}")
                print(f"   📊 node_subtype: {data.get('node_subtype', 'unknown')}")
                
                # Check consistency
                consistent = prompts_count == actual_prompts_count
                print(f"   📊 Internal consistency: {'✅ PASS' if consistent else '❌ FAIL'}")
                
                if consistent:
                    self.log_test("Intelligent Nodes Database Prompts", True, 
                                f"Intelligent nodes Database endpoint consistent with {actual_prompts_count} prompts",
                                {"data": data})
                    return True
                else:
                    self.log_test("Intelligent Nodes Database Prompts", False, 
                                f"Intelligent nodes Database endpoint inconsistent: prompts_count ({prompts_count}) != prompts.length ({actual_prompts_count})",
                                {"data": data})
                    return False
                    
            except json.JSONDecodeError as e:
                print(f"   ❌ JSON decode error: {str(e)}")
                self.log_test("Intelligent Nodes Database Prompts", False, f"JSON decode error: {str(e)}")
                return False
                
        except Exception as e:
            self.log_test("Intelligent Nodes Database Prompts", False, f"Test error: {str(e)}")
            return False

    def test_database_questionnaire_detailed_analysis(self):
        """Detailed analysis of Database questionnaire response structure"""
        print("\n🔍 DETAILED DATABASE QUESTIONNAIRE ANALYSIS")
        print("=" * 60)
        
        try:
            endpoint = f"{self.base_url}/questionnaires/Database?level=basic"
            
            response = self.session.get(endpoint)
            
            if response.status_code != 200:
                print(f"   ❌ HTTP {response.status_code}: {response.text}")
                self.log_test("Database Questionnaire Detailed Analysis", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
            
            try:
                data = response.json()
                
                print(f"📋 Response Structure Analysis:")
                print(f"   Response keys: {list(data.keys())}")
                
                # Analyze each key
                for key, value in data.items():
                    if key == 'prompts':
                        print(f"   📊 {key}: {type(value).__name__} with {len(value) if isinstance(value, list) else 'N/A'} items")
                        if isinstance(value, list) and len(value) > 0:
                            print(f"      First prompt keys: {list(value[0].keys()) if isinstance(value[0], dict) else 'Not a dict'}")
                    else:
                        print(f"   📊 {key}: {type(value).__name__} = {value}")
                
                # Check for the specific issue mentioned in user logs
                prompts = data.get('prompts', [])
                total_questions = data.get('total_questions', 0)
                actual_count = len(prompts)
                
                print(f"\n🎯 SPECIFIC ISSUE ANALYSIS:")
                print(f"   User reported: Shows '0/5 questions answered' but fails with 'Resume index 4 is beyond questionnaire length 3'")
                print(f"   Current response: total_questions={total_questions}, prompts.length={actual_count}")
                
                # Check if this matches the user's issue
                if total_questions == 5 and actual_count == 3:
                    print(f"   🚨 EXACT ISSUE REPRODUCED: total_questions=5 but prompts.length=3")
                    self.log_test("Database Questionnaire Detailed Analysis", False, 
                                f"EXACT USER ISSUE REPRODUCED: total_questions=5 but prompts.length=3",
                                {"data": data})
                    return False
                elif total_questions != actual_count:
                    print(f"   ⚠️  SIMILAR ISSUE: total_questions={total_questions} but prompts.length={actual_count}")
                    self.log_test("Database Questionnaire Detailed Analysis", False, 
                                f"Similar inconsistency: total_questions={total_questions} but prompts.length={actual_count}",
                                {"data": data})
                    return False
                else:
                    print(f"   ✅ No inconsistency detected in current response")
                    self.log_test("Database Questionnaire Detailed Analysis", True, 
                                f"Response structure consistent: total_questions={total_questions}, prompts.length={actual_count}",
                                {"data": data})
                    return True
                    
            except json.JSONDecodeError as e:
                print(f"   ❌ JSON decode error: {str(e)}")
                self.log_test("Database Questionnaire Detailed Analysis", False, f"JSON decode error: {str(e)}")
                return False
                
        except Exception as e:
            self.log_test("Database Questionnaire Detailed Analysis", False, f"Test error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all database questionnaire consistency tests"""
        print("🚀 DATABASE QUESTIONNAIRE LENGTH INCONSISTENCY INVESTIGATION")
        print("=" * 80)
        print("CRITICAL ISSUE: Database questionnaire returning inconsistent question counts")
        print("USER REPORT: Shows '0/5 questions' but fails with 'Resume index 4 beyond length 3'")
        print("GOAL: Identify and document the inconsistency for main agent to fix")
        print("=" * 80)
        
        tests = [
            self.test_health_check,
            self.test_database_questionnaire_consistency,
            self.test_compare_questionnaire_endpoints,
            self.test_intelligent_nodes_database_prompts,
            self.test_database_questionnaire_detailed_analysis,
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
        print("🎯 DATABASE QUESTIONNAIRE CONSISTENCY INVESTIGATION SUMMARY")
        print("=" * 80)
        print(f"✅ PASSED: {passed}")
        print(f"❌ FAILED: {failed}")
        print(f"📊 SUCCESS RATE: {(passed / (passed + failed) * 100):.1f}%")
        
        # Analyze results for main agent
        failed_tests = [result for result in self.test_results if not result['success']]
        
        if failed_tests:
            print(f"\n🚨 CRITICAL ISSUES FOUND:")
            for failed_test in failed_tests:
                print(f"   • {failed_test['test']}: {failed_test['message']}")
        
        # Specific recommendations
        print(f"\n📋 RECOMMENDATIONS FOR MAIN AGENT:")
        
        if any("inconsistent" in result['message'].lower() for result in failed_tests):
            print("   🔧 INCONSISTENCY CONFIRMED: Database questionnaire has total_questions != prompts.length")
            print("   🔧 ACTION REQUIRED: Fix the Database questionnaire endpoint to return consistent counts")
            print("   🔧 CHECK: Verify database.yaml file has correct number of questions")
            print("   🔧 CHECK: Verify questionnaire loading logic for Database node type")
        
        if passed == len(tests):
            print("   ✅ NO INCONSISTENCIES DETECTED: Database questionnaire appears consistent")
            print("   🔧 INVESTIGATE: Issue may be intermittent or context-dependent")
            print("   🔧 MONITOR: Check for caching or state management issues")
        
        return passed, failed

def main():
    """Main test execution"""
    tester = DatabaseQuestionnaireConsistencyTester()
    passed, failed = tester.run_all_tests()
    
    # Exit with appropriate code
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)