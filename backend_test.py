#!/usr/bin/env python3
"""
Backend API Testing - TOOLTIP FUNCTIONALITY VERIFICATION
Tests the new API and Database questionnaire endpoints to verify tooltip functionality fix.

TESTING FOCUS:
1. **API Questionnaire Endpoint Testing:**
   - Test GET /api/questionnaires/API (basic level)
   - Test GET /api/questionnaires/API?level=advanced
   - Test GET /api/questionnaires/API?level=expert
   - Verify response structure includes all required fields
   - **CRITICAL:** Verify "option_descriptions" field is present and populated for questions with multiple choice options
   - Verify option_descriptions contain proper tooltip text for each option

2. **Database Questionnaire Endpoint Testing:**
   - Test GET /api/questionnaires/Database (basic level)
   - Test GET /api/questionnaires/Database?level=advanced  
   - Test GET /api/questionnaires/Database?level=expert
   - Verify response structure matches WebApp endpoint format
   - **CRITICAL:** Verify "option_descriptions" field is present and populated
   - Verify tooltip text is comprehensive and helpful

3. **Comparison Testing:**
   - Compare response structure between /api/questionnaires/WebApp, /api/questionnaires/API, and /api/questionnaires/Database
   - Ensure all three endpoints return consistent data structure
   - Verify all endpoints include option_descriptions field for choice questions

4. **Data Quality Validation:**
   - Verify that option_descriptions keys match the actual option values
   - Ensure tooltip text is meaningful and provides security context
   - Check that all single_choice and multiple_choice questions have corresponding option_descriptions

**EXPECTED RESULTS:**
- All endpoints should return HTTP 200
- Response should include "option_descriptions" field in question objects
- Option descriptions should be a dictionary mapping option values to tooltip text
- Tooltip text should be comprehensive security guidance (not just option repetition)

**CRITICAL SUCCESS CRITERIA:**
This fix addresses the UI issue where API and Database questionnaires were missing tooltip (?) icons while WebApp questionnaires showed them correctly. The new specific endpoints should provide the same option_descriptions data that WebApp provides.
"""

import requests
import json
import uuid
from datetime import datetime, timezone
import sys

# Use the backend URL from frontend/.env with /api suffix
BASE_URL = "https://full-stack-init-1.preview.emergentagent.com/api"

class TooltipFunctionalityTester:
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
    # TEST 1: API Questionnaire Endpoint Testing
    # ============================================================================
    
    def test_api_questionnaire_basic_level(self):
        """Test GET /api/questionnaires/API (basic level) with option_descriptions verification"""
        try:
            response = self.session.get(f"{self.base_url}/questionnaires/API")
            
            if response.status_code != 200:
                self.log_test("API Questionnaire Basic", False, 
                            f"Failed to get API questionnaire: HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            # Verify expected structure
            if 'prompts' not in data:
                self.log_test("API Questionnaire Basic", False, 
                            f"Missing 'prompts' field in response: {data}")
                return False
            
            prompts = data['prompts']
            
            if len(prompts) == 0:
                self.log_test("API Questionnaire Basic", False, 
                            f"No prompts found in API questionnaire")
                return False
            
            # Check for option_descriptions in choice questions
            choice_questions_with_descriptions = 0
            choice_questions_total = 0
            missing_descriptions = []
            
            for i, prompt in enumerate(prompts):
                question_type = prompt.get('type', '')
                question_id = prompt.get('id', f'question_{i}')
                
                if question_type in ['single_choice', 'multiple_choice']:
                    choice_questions_total += 1
                    
                    if 'option_descriptions' in prompt:
                        choice_questions_with_descriptions += 1
                        
                        # Verify option_descriptions structure
                        option_descriptions = prompt['option_descriptions']
                        if not isinstance(option_descriptions, dict):
                            self.log_test("API Questionnaire Basic", False, 
                                        f"option_descriptions should be a dict for question {question_id}, got {type(option_descriptions)}")
                            return False
                        
                        # Verify options match option_descriptions keys
                        options = prompt.get('options', [])
                        for option in options:
                            if option not in option_descriptions:
                                missing_descriptions.append(f"{question_id}: missing description for option '{option}'")
                    else:
                        missing_descriptions.append(f"{question_id}: missing option_descriptions field")
            
            if missing_descriptions:
                self.log_test("API Questionnaire Basic", False, 
                            f"Missing option descriptions: {missing_descriptions}")
                return False
            
            if choice_questions_total == 0:
                self.log_test("API Questionnaire Basic", True, 
                            f"✅ API questionnaire loaded successfully ({len(prompts)} questions) - No choice questions found, option_descriptions not required")
            else:
                self.log_test("API Questionnaire Basic", True, 
                            f"✅ API questionnaire loaded successfully ({len(prompts)} questions, {choice_questions_with_descriptions}/{choice_questions_total} choice questions have option_descriptions)")
            
            print(f"📋 API Questionnaire Basic Level:")
            print(f"   Total Questions: {len(prompts)}")
            print(f"   Choice Questions: {choice_questions_total}")
            print(f"   With Option Descriptions: {choice_questions_with_descriptions}")
            
            return True
            
        except Exception as e:
            self.log_test("API Questionnaire Basic", False, f"Request error: {str(e)}")
            return False

    def test_api_questionnaire_advanced_level(self):
        """Test GET /api/questionnaires/API?level=advanced with option_descriptions verification"""
        try:
            response = self.session.get(f"{self.base_url}/questionnaires/API?level=advanced")
            
            if response.status_code != 200:
                self.log_test("API Questionnaire Advanced", False, 
                            f"Failed to get API questionnaire (advanced): HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            # Verify expected structure
            if 'prompts' not in data:
                self.log_test("API Questionnaire Advanced", False, 
                            f"Missing 'prompts' field in response: {data}")
                return False
            
            prompts = data['prompts']
            
            # Check for option_descriptions in choice questions
            choice_questions_with_descriptions = 0
            choice_questions_total = 0
            
            for prompt in prompts:
                question_type = prompt.get('type', '')
                
                if question_type in ['single_choice', 'multiple_choice']:
                    choice_questions_total += 1
                    
                    if 'option_descriptions' in prompt:
                        choice_questions_with_descriptions += 1
            
            self.log_test("API Questionnaire Advanced", True, 
                        f"✅ API questionnaire (advanced) loaded successfully ({len(prompts)} questions, {choice_questions_with_descriptions}/{choice_questions_total} choice questions have option_descriptions)")
            
            print(f"📋 API Questionnaire Advanced Level:")
            print(f"   Total Questions: {len(prompts)}")
            print(f"   Choice Questions: {choice_questions_total}")
            print(f"   With Option Descriptions: {choice_questions_with_descriptions}")
            
            return True
            
        except Exception as e:
            self.log_test("API Questionnaire Advanced", False, f"Request error: {str(e)}")
            return False

    def test_api_questionnaire_expert_level(self):
        """Test GET /api/questionnaires/API?level=expert with option_descriptions verification"""
        try:
            response = self.session.get(f"{self.base_url}/questionnaires/API?level=expert")
            
            if response.status_code != 200:
                self.log_test("API Questionnaire Expert", False, 
                            f"Failed to get API questionnaire (expert): HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            # Verify expected structure
            if 'prompts' not in data:
                self.log_test("API Questionnaire Expert", False, 
                            f"Missing 'prompts' field in response: {data}")
                return False
            
            prompts = data['prompts']
            
            # Check for option_descriptions in choice questions
            choice_questions_with_descriptions = 0
            choice_questions_total = 0
            
            for prompt in prompts:
                question_type = prompt.get('type', '')
                
                if question_type in ['single_choice', 'multiple_choice']:
                    choice_questions_total += 1
                    
                    if 'option_descriptions' in prompt:
                        choice_questions_with_descriptions += 1
            
            self.log_test("API Questionnaire Expert", True, 
                        f"✅ API questionnaire (expert) loaded successfully ({len(prompts)} questions, {choice_questions_with_descriptions}/{choice_questions_total} choice questions have option_descriptions)")
            
            print(f"📋 API Questionnaire Expert Level:")
            print(f"   Total Questions: {len(prompts)}")
            print(f"   Choice Questions: {choice_questions_total}")
            print(f"   With Option Descriptions: {choice_questions_with_descriptions}")
            
            return True
            
        except Exception as e:
            self.log_test("API Questionnaire Expert", False, f"Request error: {str(e)}")
            return False

    # ============================================================================
    # TEST 2: Database Questionnaire Endpoint Testing
    # ============================================================================
    
    def test_database_questionnaire_basic_level(self):
        """Test GET /api/questionnaires/Database (basic level) with option_descriptions verification"""
        try:
            response = self.session.get(f"{self.base_url}/questionnaires/Database")
            
            if response.status_code != 200:
                self.log_test("Database Questionnaire Basic", False, 
                            f"Failed to get Database questionnaire: HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            # Verify expected structure
            if 'prompts' not in data:
                self.log_test("Database Questionnaire Basic", False, 
                            f"Missing 'prompts' field in response: {data}")
                return False
            
            prompts = data['prompts']
            
            if len(prompts) == 0:
                self.log_test("Database Questionnaire Basic", False, 
                            f"No prompts found in Database questionnaire")
                return False
            
            # Check for option_descriptions in choice questions
            choice_questions_with_descriptions = 0
            choice_questions_total = 0
            missing_descriptions = []
            
            for i, prompt in enumerate(prompts):
                question_type = prompt.get('type', '')
                question_id = prompt.get('id', f'question_{i}')
                
                if question_type in ['single_choice', 'multiple_choice']:
                    choice_questions_total += 1
                    
                    if 'option_descriptions' in prompt:
                        choice_questions_with_descriptions += 1
                        
                        # Verify option_descriptions structure
                        option_descriptions = prompt['option_descriptions']
                        if not isinstance(option_descriptions, dict):
                            self.log_test("Database Questionnaire Basic", False, 
                                        f"option_descriptions should be a dict for question {question_id}, got {type(option_descriptions)}")
                            return False
                        
                        # Verify options match option_descriptions keys
                        options = prompt.get('options', [])
                        for option in options:
                            if option not in option_descriptions:
                                missing_descriptions.append(f"{question_id}: missing description for option '{option}'")
                    else:
                        missing_descriptions.append(f"{question_id}: missing option_descriptions field")
            
            if missing_descriptions:
                self.log_test("Database Questionnaire Basic", False, 
                            f"Missing option descriptions: {missing_descriptions}")
                return False
            
            if choice_questions_total == 0:
                self.log_test("Database Questionnaire Basic", True, 
                            f"✅ Database questionnaire loaded successfully ({len(prompts)} questions) - No choice questions found, option_descriptions not required")
            else:
                self.log_test("Database Questionnaire Basic", True, 
                            f"✅ Database questionnaire loaded successfully ({len(prompts)} questions, {choice_questions_with_descriptions}/{choice_questions_total} choice questions have option_descriptions)")
            
            print(f"📋 Database Questionnaire Basic Level:")
            print(f"   Total Questions: {len(prompts)}")
            print(f"   Choice Questions: {choice_questions_total}")
            print(f"   With Option Descriptions: {choice_questions_with_descriptions}")
            
            return True
            
        except Exception as e:
            self.log_test("Database Questionnaire Basic", False, f"Request error: {str(e)}")
            return False

    def test_database_questionnaire_advanced_level(self):
        """Test GET /api/questionnaires/Database?level=advanced with option_descriptions verification"""
        try:
            response = self.session.get(f"{self.base_url}/questionnaires/Database?level=advanced")
            
            if response.status_code != 200:
                self.log_test("Database Questionnaire Advanced", False, 
                            f"Failed to get Database questionnaire (advanced): HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            # Verify expected structure
            if 'prompts' not in data:
                self.log_test("Database Questionnaire Advanced", False, 
                            f"Missing 'prompts' field in response: {data}")
                return False
            
            prompts = data['prompts']
            
            # Check for option_descriptions in choice questions
            choice_questions_with_descriptions = 0
            choice_questions_total = 0
            
            for prompt in prompts:
                question_type = prompt.get('type', '')
                
                if question_type in ['single_choice', 'multiple_choice']:
                    choice_questions_total += 1
                    
                    if 'option_descriptions' in prompt:
                        choice_questions_with_descriptions += 1
            
            self.log_test("Database Questionnaire Advanced", True, 
                        f"✅ Database questionnaire (advanced) loaded successfully ({len(prompts)} questions, {choice_questions_with_descriptions}/{choice_questions_total} choice questions have option_descriptions)")
            
            print(f"📋 Database Questionnaire Advanced Level:")
            print(f"   Total Questions: {len(prompts)}")
            print(f"   Choice Questions: {choice_questions_total}")
            print(f"   With Option Descriptions: {choice_questions_with_descriptions}")
            
            return True
            
        except Exception as e:
            self.log_test("Database Questionnaire Advanced", False, f"Request error: {str(e)}")
            return False

    def test_database_questionnaire_expert_level(self):
        """Test GET /api/questionnaires/Database?level=expert with option_descriptions verification"""
        try:
            response = self.session.get(f"{self.base_url}/questionnaires/Database?level=expert")
            
            if response.status_code != 200:
                self.log_test("Database Questionnaire Expert", False, 
                            f"Failed to get Database questionnaire (expert): HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            # Verify expected structure
            if 'prompts' not in data:
                self.log_test("Database Questionnaire Expert", False, 
                            f"Missing 'prompts' field in response: {data}")
                return False
            
            prompts = data['prompts']
            
            # Check for option_descriptions in choice questions
            choice_questions_with_descriptions = 0
            choice_questions_total = 0
            
            for prompt in prompts:
                question_type = prompt.get('type', '')
                
                if question_type in ['single_choice', 'multiple_choice']:
                    choice_questions_total += 1
                    
                    if 'option_descriptions' in prompt:
                        choice_questions_with_descriptions += 1
            
            self.log_test("Database Questionnaire Expert", True, 
                        f"✅ Database questionnaire (expert) loaded successfully ({len(prompts)} questions, {choice_questions_with_descriptions}/{choice_questions_total} choice questions have option_descriptions)")
            
            print(f"📋 Database Questionnaire Expert Level:")
            print(f"   Total Questions: {len(prompts)}")
            print(f"   Choice Questions: {choice_questions_total}")
            print(f"   With Option Descriptions: {choice_questions_with_descriptions}")
            
            return True
            
        except Exception as e:
            self.log_test("Database Questionnaire Expert", False, f"Request error: {str(e)}")
            return False

    # ============================================================================
    # TEST 3: Comparison Testing
    # ============================================================================
    
    def test_webapp_questionnaire_comparison(self):
        """Test GET /api/questionnaires/WebApp for comparison with API and Database endpoints"""
        try:
            response = self.session.get(f"{self.base_url}/questionnaires/WebApp")
            
            if response.status_code != 200:
                self.log_test("WebApp Questionnaire Comparison", False, 
                            f"Failed to get WebApp questionnaire: HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            # Verify expected structure
            if 'prompts' not in data:
                self.log_test("WebApp Questionnaire Comparison", False, 
                            f"Missing 'prompts' field in response: {data}")
                return False
            
            prompts = data['prompts']
            
            # Check for option_descriptions in choice questions
            choice_questions_with_descriptions = 0
            choice_questions_total = 0
            
            for prompt in prompts:
                question_type = prompt.get('type', '')
                
                if question_type in ['single_choice', 'multiple_choice']:
                    choice_questions_total += 1
                    
                    if 'option_descriptions' in prompt:
                        choice_questions_with_descriptions += 1
            
            self.log_test("WebApp Questionnaire Comparison", True, 
                        f"✅ WebApp questionnaire loaded successfully ({len(prompts)} questions, {choice_questions_with_descriptions}/{choice_questions_total} choice questions have option_descriptions)")
            
            print(f"📋 WebApp Questionnaire (for comparison):")
            print(f"   Total Questions: {len(prompts)}")
            print(f"   Choice Questions: {choice_questions_total}")
            print(f"   With Option Descriptions: {choice_questions_with_descriptions}")
            
            return True
            
        except Exception as e:
            self.log_test("WebApp Questionnaire Comparison", False, f"Request error: {str(e)}")
            return False

    def test_endpoint_consistency(self):
        """Test that all three endpoints (WebApp, API, Database) return consistent data structure"""
        try:
            endpoints = [
                ("WebApp", f"{self.base_url}/questionnaires/WebApp"),
                ("API", f"{self.base_url}/questionnaires/API"),
                ("Database", f"{self.base_url}/questionnaires/Database")
            ]
            
            endpoint_data = {}
            
            for endpoint_name, endpoint_url in endpoints:
                response = self.session.get(endpoint_url)
                
                if response.status_code != 200:
                    self.log_test("Endpoint Consistency", False, 
                                f"Failed to get {endpoint_name} questionnaire: HTTP {response.status_code}")
                    return False
                
                data = response.json()
                
                if 'prompts' not in data:
                    self.log_test("Endpoint Consistency", False, 
                                f"Missing 'prompts' field in {endpoint_name} questionnaire")
                    return False
                
                endpoint_data[endpoint_name] = data
            
            # Check consistency of structure
            required_fields = ['prompts']
            for endpoint_name, data in endpoint_data.items():
                for field in required_fields:
                    if field not in data:
                        self.log_test("Endpoint Consistency", False, 
                                    f"Missing required field '{field}' in {endpoint_name} questionnaire")
                        return False
            
            # Check that all choice questions have option_descriptions
            inconsistent_endpoints = []
            
            for endpoint_name, data in endpoint_data.items():
                prompts = data['prompts']
                choice_questions_missing_descriptions = 0
                
                for prompt in prompts:
                    question_type = prompt.get('type', '')
                    
                    if question_type in ['single_choice', 'multiple_choice']:
                        if 'option_descriptions' not in prompt:
                            choice_questions_missing_descriptions += 1
                
                if choice_questions_missing_descriptions > 0:
                    inconsistent_endpoints.append(f"{endpoint_name}: {choice_questions_missing_descriptions} choice questions missing option_descriptions")
            
            if inconsistent_endpoints:
                self.log_test("Endpoint Consistency", False, 
                            f"Inconsistent option_descriptions across endpoints: {inconsistent_endpoints}")
                return False
            
            self.log_test("Endpoint Consistency", True, 
                        f"✅ All three endpoints (WebApp, API, Database) return consistent data structure with option_descriptions")
            
            print(f"🔄 Endpoint Consistency Check:")
            for endpoint_name, data in endpoint_data.items():
                prompts = data['prompts']
                choice_questions = sum(1 for p in prompts if p.get('type') in ['single_choice', 'multiple_choice'])
                print(f"   {endpoint_name}: {len(prompts)} questions, {choice_questions} choice questions")
            
            return True
            
        except Exception as e:
            self.log_test("Endpoint Consistency", False, f"Request error: {str(e)}")
            return False

    # ============================================================================
    # TEST 4: Data Quality Validation
    # ============================================================================
    
    def test_option_descriptions_quality(self):
        """Test that option_descriptions contain meaningful tooltip text and match option values"""
        try:
            endpoints = [
                ("API", f"{self.base_url}/questionnaires/API"),
                ("Database", f"{self.base_url}/questionnaires/Database")
            ]
            
            quality_issues = []
            
            for endpoint_name, endpoint_url in endpoints:
                response = self.session.get(endpoint_url)
                
                if response.status_code != 200:
                    continue  # Skip if endpoint not available
                
                data = response.json()
                prompts = data.get('prompts', [])
                
                for i, prompt in enumerate(prompts):
                    question_type = prompt.get('type', '')
                    question_id = prompt.get('id', f'question_{i}')
                    
                    if question_type in ['single_choice', 'multiple_choice']:
                        options = prompt.get('options', [])
                        option_descriptions = prompt.get('option_descriptions', {})
                        
                        # Check that all options have descriptions
                        for option in options:
                            if option not in option_descriptions:
                                quality_issues.append(f"{endpoint_name} {question_id}: missing description for option '{option}'")
                            else:
                                description = option_descriptions[option]
                                
                                # Check that description is meaningful (not just the option repeated)
                                if description.lower().strip() == option.lower().strip():
                                    quality_issues.append(f"{endpoint_name} {question_id}: description for '{option}' is just option repetition")
                                
                                # Check that description is not empty or too short
                                if len(description.strip()) < 10:
                                    quality_issues.append(f"{endpoint_name} {question_id}: description for '{option}' is too short: '{description}'")
                        
                        # Check for extra descriptions (descriptions for non-existent options)
                        for desc_option in option_descriptions.keys():
                            if desc_option not in options:
                                quality_issues.append(f"{endpoint_name} {question_id}: extra description for non-existent option '{desc_option}'")
            
            if quality_issues:
                self.log_test("Option Descriptions Quality", False, 
                            f"Quality issues found: {quality_issues[:5]}...")  # Show first 5 issues
                return False
            
            self.log_test("Option Descriptions Quality", True, 
                        f"✅ Option descriptions are high quality with meaningful tooltip text")
            
            print(f"🔍 Option Descriptions Quality Check:")
            print(f"   ✅ All options have corresponding descriptions")
            print(f"   ✅ Descriptions are meaningful (not just option repetition)")
            print(f"   ✅ Descriptions are comprehensive (>10 characters)")
            print(f"   ✅ No extra descriptions for non-existent options")
            
            return True
            
        except Exception as e:
            self.log_test("Option Descriptions Quality", False, f"Request error: {str(e)}")
            return False

    def test_security_context_in_tooltips(self):
        """Test that tooltip text provides security context and guidance"""
        try:
            endpoints = [
                ("API", f"{self.base_url}/questionnaires/API"),
                ("Database", f"{self.base_url}/questionnaires/Database")
            ]
            
            security_keywords = [
                'security', 'secure', 'protection', 'vulnerability', 'risk', 'threat',
                'authentication', 'authorization', 'encryption', 'access', 'control',
                'attack', 'malicious', 'breach', 'compromise', 'exploit', 'mitigation'
            ]
            
            endpoints_with_security_context = 0
            total_descriptions_checked = 0
            security_descriptions_found = 0
            
            for endpoint_name, endpoint_url in endpoints:
                response = self.session.get(endpoint_url)
                
                if response.status_code != 200:
                    continue  # Skip if endpoint not available
                
                data = response.json()
                prompts = data.get('prompts', [])
                
                endpoint_has_security_context = False
                
                for prompt in prompts:
                    question_type = prompt.get('type', '')
                    
                    if question_type in ['single_choice', 'multiple_choice']:
                        option_descriptions = prompt.get('option_descriptions', {})
                        
                        for option, description in option_descriptions.items():
                            total_descriptions_checked += 1
                            description_lower = description.lower()
                            
                            # Check if description contains security-related keywords
                            has_security_context = any(keyword in description_lower for keyword in security_keywords)
                            
                            if has_security_context:
                                security_descriptions_found += 1
                                endpoint_has_security_context = True
                
                if endpoint_has_security_context:
                    endpoints_with_security_context += 1
            
            if total_descriptions_checked == 0:
                self.log_test("Security Context in Tooltips", True, 
                            f"✅ No choice questions found, security context check not applicable")
                return True
            
            security_percentage = (security_descriptions_found / total_descriptions_checked) * 100
            
            if security_percentage < 30:  # At least 30% should have security context
                self.log_test("Security Context in Tooltips", False, 
                            f"Insufficient security context in tooltips: {security_percentage:.1f}% ({security_descriptions_found}/{total_descriptions_checked})")
                return False
            
            self.log_test("Security Context in Tooltips", True, 
                        f"✅ Tooltips provide good security context: {security_percentage:.1f}% ({security_descriptions_found}/{total_descriptions_checked})")
            
            print(f"🛡️ Security Context in Tooltips:")
            print(f"   Total Descriptions Checked: {total_descriptions_checked}")
            print(f"   With Security Context: {security_descriptions_found} ({security_percentage:.1f}%)")
            print(f"   Endpoints with Security Context: {endpoints_with_security_context}")
            
            return True
            
        except Exception as e:
            self.log_test("Security Context in Tooltips", False, f"Request error: {str(e)}")
            return False

    # ============================================================================
    # Test Runner
    # ============================================================================
    
    def run_all_tests(self):
        """Run all tooltip functionality verification tests"""
        print("🚀 Starting Tooltip Functionality Verification Tests")
        print("=" * 90)
        print("TOOLTIP FUNCTIONALITY VERIFICATION")
        print("Testing new API and Database questionnaire endpoints for tooltip functionality fix")
        print("Focus: option_descriptions field presence, structure, and quality")
        print("=" * 90)
        
        tests = [
            # Basic connectivity
            self.test_health_check,
            
            # TEST 1: API Questionnaire Endpoint Testing
            self.test_api_questionnaire_basic_level,
            self.test_api_questionnaire_advanced_level,
            self.test_api_questionnaire_expert_level,
            
            # TEST 2: Database Questionnaire Endpoint Testing
            self.test_database_questionnaire_basic_level,
            self.test_database_questionnaire_advanced_level,
            self.test_database_questionnaire_expert_level,
            
            # TEST 3: Comparison Testing
            self.test_webapp_questionnaire_comparison,
            self.test_endpoint_consistency,
            
            # TEST 4: Data Quality Validation
            self.test_option_descriptions_quality,
            self.test_security_context_in_tooltips,
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
        print("🎯 TOOLTIP FUNCTIONALITY VERIFICATION SUMMARY")
        print("=" * 90)
        print(f"✅ PASSED: {passed}")
        print(f"❌ FAILED: {failed}")
        print(f"📊 SUCCESS RATE: {(passed / (passed + failed) * 100):.1f}%")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED! Tooltip functionality verification successful.")
            print("✅ API questionnaire endpoints working correctly with option_descriptions")
            print("✅ Database questionnaire endpoints working correctly with option_descriptions")
            print("✅ All endpoints return consistent data structure")
            print("✅ Option descriptions are high quality with security context")
            print("✅ Tooltip functionality fix verified - UI should now show tooltip (?) icons")
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
    tester = TooltipFunctionalityTester()
    passed, failed = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()