#!/usr/bin/env python3
"""
Focused Routing Fix Test for ProductDesignSecurity Questionnaire Endpoint
Tests the specific routing fix mentioned in the review request.
"""

import requests
import json
import uuid
import sys

# Use the backend URL from frontend/.env with /api suffix
BASE_URL = "https://phased-builder.preview.emergentagent.com/api"

class RoutingFixTester:
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
        
    def test_stride_questionnaire_endpoint(self):
        """Test GET /api/questionnaires/ProductDesignSecurity returns STRIDE-based questionnaire"""
        try:
            response = self.session.get(f"{self.base_url}/questionnaires/ProductDesignSecurity")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for required fields
                required_fields = ["questionnaire_type", "stride_categories", "prompts"]
                missing_fields = [f for f in required_fields if f not in data]
                
                if missing_fields:
                    self.log_test("STRIDE Questionnaire Endpoint", False, 
                                f"Missing required fields: {missing_fields}")
                    return False
                
                # Verify questionnaire_type
                questionnaire_type = data.get("questionnaire_type", "")
                if "STRIDE-based Threat Modeling" not in questionnaire_type:
                    self.log_test("STRIDE Questionnaire Endpoint", False, 
                                f"Expected 'STRIDE-based Threat Modeling', got: {questionnaire_type}")
                    return False
                
                # Verify stride_categories array
                stride_categories = data.get("stride_categories", [])
                expected_categories = ["Spoofing", "Tampering", "Repudiation", "Information Disclosure", "Denial of Service", "Elevation of Privilege"]
                
                if not all(cat in stride_categories for cat in expected_categories):
                    self.log_test("STRIDE Questionnaire Endpoint", False, 
                                f"Missing STRIDE categories. Expected: {expected_categories}, Got: {stride_categories}")
                    return False
                
                # Verify prompts exist
                prompts = data.get("prompts", [])
                if len(prompts) == 0:
                    self.log_test("STRIDE Questionnaire Endpoint", False, 
                                "No prompts found in questionnaire")
                    return False
                
                # Verify it's loading from product_design_security.yaml file (check node_subtype)
                node_subtype = data.get("node_subtype", "")
                if node_subtype != "ProductDesignSecurity":
                    self.log_test("STRIDE Questionnaire Endpoint", False, 
                                f"Expected node_subtype 'ProductDesignSecurity', got: {node_subtype}")
                    return False
                
                self.log_test("STRIDE Questionnaire Endpoint", True, 
                            f"STRIDE questionnaire loaded correctly with {len(prompts)} prompts and {len(stride_categories)} categories")
                return True
                
            else:
                self.log_test("STRIDE Questionnaire Endpoint", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("STRIDE Questionnaire Endpoint", False, f"Error: {str(e)}")
            return False

    def test_bulk_vulnerability_analysis_with_product_design_security(self):
        """Test POST /api/vulnerabilities/bulk-analyze with ProductDesignSecurity node type"""
        try:
            request_data = {
                "nodes": [
                    {
                        "node_id": str(uuid.uuid4()),
                        "node_type": "ProductDesignSecurity",
                        "questionnaire_responses": {
                            "threat_modeling_approach": "STRIDE",
                            "security_requirements": "comprehensive",
                            "threat_identification": "systematic",
                            "risk_assessment": "quantitative",
                            "mitigation_strategies": "defense_in_depth"
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
                
                # Should return a list
                if not isinstance(data, list):
                    self.log_test("Bulk Vulnerability Analysis", False, 
                                f"Expected list response, got {type(data)}")
                    return False
                
                # Should have results for the ProductDesignSecurity node
                if len(data) == 0:
                    self.log_test("Bulk Vulnerability Analysis", False, 
                                "No results returned for ProductDesignSecurity node")
                    return False
                
                result = data[0]
                
                # Check if it processed ProductDesignSecurity correctly
                node_type = result.get("node_type", "")
                if node_type != "ProductDesignSecurity":
                    self.log_test("Bulk Vulnerability Analysis", False, 
                                f"Expected node_type 'ProductDesignSecurity', got: {node_type}")
                    return False
                
                # Check if it has vulnerability analysis results
                if "total_vulnerabilities" not in result:
                    self.log_test("Bulk Vulnerability Analysis", False, 
                                "Missing total_vulnerabilities field in result")
                    return False
                
                self.log_test("Bulk Vulnerability Analysis", True, 
                            f"Successfully processed ProductDesignSecurity node with {result.get('total_vulnerabilities', 0)} vulnerabilities")
                return True
                
            else:
                self.log_test("Bulk Vulnerability Analysis", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Bulk Vulnerability Analysis", False, f"Error: {str(e)}")
            return False

    def test_route_ordering_fix(self):
        """Test that specific ProductDesignSecurity route is matched instead of generic route"""
        try:
            # Test the specific route
            specific_response = self.session.get(f"{self.base_url}/questionnaires/ProductDesignSecurity")
            
            # Test a generic route for comparison
            generic_response = self.session.get(f"{self.base_url}/questionnaires/WebApp")
            
            if specific_response.status_code == 200 and generic_response.status_code == 200:
                specific_data = specific_response.json()
                generic_data = generic_response.json()
                
                # The specific route should return STRIDE-based questionnaire
                specific_type = specific_data.get("questionnaire_type", "")
                generic_type = generic_data.get("questionnaire_type", "")
                
                # Specific should be STRIDE-based
                if "STRIDE-based" not in specific_type:
                    self.log_test("Route Ordering Fix", False, 
                                f"Specific route not returning STRIDE-based questionnaire: {specific_type}")
                    return False
                
                # Generic should not be STRIDE-based (should be different)
                if specific_type == generic_type:
                    self.log_test("Route Ordering Fix", False, 
                                "Specific and generic routes returning same questionnaire type")
                    return False
                
                # Specific should have stride_categories
                if "stride_categories" not in specific_data:
                    self.log_test("Route Ordering Fix", False, 
                                "Specific route missing stride_categories")
                    return False
                
                # Generic should not have stride_categories (or different structure)
                if "stride_categories" in generic_data and generic_data["stride_categories"] == specific_data["stride_categories"]:
                    self.log_test("Route Ordering Fix", False, 
                                "Generic route has same stride_categories as specific route")
                    return False
                
                self.log_test("Route Ordering Fix", True, 
                            f"Route ordering working correctly - specific route returns STRIDE-based, generic returns different type")
                return True
                
            else:
                self.log_test("Route Ordering Fix", False, 
                            f"Route responses failed - Specific: {specific_response.status_code}, Generic: {generic_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Route Ordering Fix", False, f"Error: {str(e)}")
            return False

    def run_focused_tests(self):
        """Run the focused routing fix tests"""
        print("🎯 Starting Focused Routing Fix Tests for ProductDesignSecurity")
        print("=" * 80)
        
        tests = [
            self.test_stride_questionnaire_endpoint,
            self.test_bulk_vulnerability_analysis_with_product_design_security,
            self.test_route_ordering_fix
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
        print("🎯 FOCUSED ROUTING FIX TEST SUMMARY")
        print("=" * 80)
        print(f"✅ PASSED: {passed}")
        print(f"❌ FAILED: {failed}")
        print(f"📊 SUCCESS RATE: {(passed / (passed + failed) * 100):.1f}%")
        
        if failed == 0:
            print("\n🎉 ALL ROUTING FIX TESTS PASSED! ProductDesignSecurity routing is working correctly.")
        else:
            print(f"\n⚠️  {failed} tests failed. Please review the failed tests above.")
        
        return passed, failed

def main():
    """Main test execution"""
    tester = RoutingFixTester()
    passed, failed = tester.run_focused_tests()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()