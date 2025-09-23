#!/usr/bin/env python3
"""
Expanded Intelligent Nodes API Tests - Phase 1 Enhanced APIs
Tests the specific endpoints requested in the review for Phase 1 Enhanced APIs implementation
"""

import requests
import json
import uuid
from datetime import datetime, timezone
import sys

# Use the production URL from review request
BASE_URL = "https://phased-builder.preview.emergentagent.com/api"

class ExpandedNodesAPITester:
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
    
    def test_expanded_nodes_supported_types(self):
        """Test GET /api/expanded-nodes/supported-types - Verify returns 30 node types with enhanced metadata"""
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
                
                # Verify we have 30 node types as expected
                if total_count != 30:
                    self.log_test("Expanded Nodes - Supported Types", False, 
                                f"Expected 30 node types, got {total_count}")
                    return False
                
                # Verify expected node types are present (EC2, Lambda, S3 for testing)
                expected_types = ["EC2", "Lambda", "S3", "RDS", "VPC", "WAF", "IAM", "Kubernetes", "CICD"]
                found_types = [t.get("node_subtype") for t in supported_types]
                
                missing_types = [t for t in expected_types if t not in found_types]
                if missing_types:
                    self.log_test("Expanded Nodes - Supported Types", False, 
                                f"Missing expected types: {missing_types}. Found: {found_types[:10]}...")
                    return False
                
                # Verify enhanced metadata structure
                if supported_types:
                    first_type = supported_types[0]
                    required_metadata_fields = ["node_subtype", "node_type", "category", "description", 
                                              "threat_intelligence", "questionnaire_levels", "questionnaire_counts"]
                    missing_metadata_fields = [f for f in required_metadata_fields if f not in first_type]
                    
                    if missing_metadata_fields:
                        self.log_test("Expanded Nodes - Supported Types", False, 
                                    f"Missing enhanced metadata fields: {missing_metadata_fields}")
                        return False
                
                # Verify comprehensive categories
                if len(categories) < 5:
                    self.log_test("Expanded Nodes - Supported Types", False, 
                                f"Expected comprehensive categories, got only {len(categories)}: {categories}")
                    return False
                
                self.log_test("Expanded Nodes - Supported Types", True, 
                            f"✅ Retrieved {total_count} node types with enhanced metadata across {len(categories)} categories")
                return True
            else:
                self.log_test("Expanded Nodes - Supported Types", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Expanded Nodes - Supported Types", False, f"Error: {str(e)}")
            return False

    def test_expanded_nodes_categories(self):
        """Test GET /api/expanded-nodes/categories - Verify comprehensive category data with descriptions"""
        try:
            response = self.session.get(f"{self.base_url}/expanded-nodes/categories")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for comprehensive category structure
                if not isinstance(data, dict):
                    self.log_test("Expanded Nodes - Categories", False, f"Expected dict, got {type(data)}")
                    return False
                
                # Verify we have comprehensive categories
                expected_categories = ["Infrastructure", "Security", "Development", "Monitoring", "Storage"]
                found_categories = list(data.keys())
                
                missing_categories = [c for c in expected_categories if c not in found_categories]
                if missing_categories:
                    self.log_test("Expanded Nodes - Categories", False, 
                                f"Missing expected categories: {missing_categories}. Found: {found_categories}")
                    return False
                
                # Verify each category has descriptions and node type mappings
                for category, category_data in data.items():
                    if not isinstance(category_data, list):
                        self.log_test("Expanded Nodes - Categories", False, 
                                    f"Category {category} should contain list of node types")
                        return False
                    
                    if len(category_data) == 0:
                        self.log_test("Expanded Nodes - Categories", False, 
                                    f"Category {category} is empty")
                        return False
                    
                    # Verify node type structure in category
                    first_node = category_data[0]
                    if not isinstance(first_node, dict) or "node_subtype" not in first_node:
                        self.log_test("Expanded Nodes - Categories", False, 
                                    f"Invalid node structure in category {category}")
                        return False
                
                total_nodes_in_categories = sum(len(nodes) for nodes in data.values())
                
                self.log_test("Expanded Nodes - Categories", True, 
                            f"✅ Retrieved {len(found_categories)} comprehensive categories with {total_nodes_in_categories} total node mappings")
                return True
            else:
                self.log_test("Expanded Nodes - Categories", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Expanded Nodes - Categories", False, f"Error: {str(e)}")
            return False

    def test_expanded_nodes_multi_level_questionnaires(self):
        """Test GET /api/expanded-nodes/{node_subtype}/questionnaire/{level} - Test multi-level questionnaires"""
        test_cases = [
            {"node_subtype": "EC2", "level": "basic", "expected_min_questions": 5, "expected_max_questions": 8},
            {"node_subtype": "EC2", "level": "advanced", "expected_min_questions": 15, "expected_max_questions": 20},
            {"node_subtype": "EC2", "level": "expert", "expected_min_questions": 25, "expected_max_questions": 30},
            {"node_subtype": "Lambda", "level": "basic", "expected_min_questions": 5, "expected_max_questions": 8},
            {"node_subtype": "Lambda", "level": "advanced", "expected_min_questions": 15, "expected_max_questions": 20},
            {"node_subtype": "S3", "level": "basic", "expected_min_questions": 5, "expected_max_questions": 8},
            {"node_subtype": "S3", "level": "expert", "expected_min_questions": 25, "expected_max_questions": 30},
        ]
        
        for test_case in test_cases:
            node_subtype = test_case["node_subtype"]
            level = test_case["level"]
            expected_min = test_case["expected_min_questions"]
            expected_max = test_case["expected_max_questions"]
            
            try:
                response = self.session.get(f"{self.base_url}/expanded-nodes/{node_subtype}/questionnaire/{level}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check for required questionnaire fields
                    expected_fields = ["node_subtype", "questionnaire_level", "questions", "metadata"]
                    missing_fields = [f for f in expected_fields if f not in data]
                    
                    if missing_fields:
                        self.log_test(f"Multi-Level Questionnaire - {node_subtype} {level}", False, 
                                    f"Missing fields: {missing_fields}")
                        return False
                    
                    questions = data.get("questions", [])
                    questionnaire_level = data.get("questionnaire_level", "")
                    metadata = data.get("metadata", {})
                    
                    # Verify question count is within expected range
                    question_count = len(questions)
                    if not (expected_min <= question_count <= expected_max):
                        self.log_test(f"Multi-Level Questionnaire - {node_subtype} {level}", False, 
                                    f"Expected {expected_min}-{expected_max} questions, got {question_count}")
                        return False
                    
                    # Verify questionnaire level matches request
                    if questionnaire_level.lower() != level.lower():
                        self.log_test(f"Multi-Level Questionnaire - {node_subtype} {level}", False, 
                                    f"Level mismatch: requested {level}, got {questionnaire_level}")
                        return False
                    
                    # Verify question structure
                    if questions:
                        first_question = questions[0]
                        required_question_fields = ["id", "question", "type", "options"]
                        missing_question_fields = [f for f in required_question_fields if f not in first_question]
                        
                        if missing_question_fields:
                            self.log_test(f"Multi-Level Questionnaire - {node_subtype} {level}", False, 
                                        f"Missing question fields: {missing_question_fields}")
                            return False
                    
                    # Verify metadata contains threat intelligence
                    if "threat_intelligence" not in data:
                        self.log_test(f"Multi-Level Questionnaire - {node_subtype} {level}", False, 
                                    "Missing threat intelligence integration")
                        return False
                    
                    self.log_test(f"Multi-Level Questionnaire - {node_subtype} {level}", True, 
                                f"✅ {question_count} questions ({expected_min}-{expected_max} expected)")
                    
                elif response.status_code == 400:
                    self.log_test(f"Multi-Level Questionnaire - {node_subtype} {level}", False, 
                                f"Invalid level parameter: {response.text}")
                    return False
                elif response.status_code == 404:
                    self.log_test(f"Multi-Level Questionnaire - {node_subtype} {level}", False, 
                                f"Questionnaire not found for {node_subtype} {level}")
                    return False
                else:
                    self.log_test(f"Multi-Level Questionnaire - {node_subtype} {level}", False, 
                                f"HTTP {response.status_code}: {response.text}")
                    return False
                    
            except Exception as e:
                self.log_test(f"Multi-Level Questionnaire - {node_subtype} {level}", False, f"Error: {str(e)}")
                return False
        
        return True

    def test_expanded_nodes_enhanced_risk_calculation(self):
        """Test POST /api/expanded-nodes/{node_subtype}/calculate-risk - Test enhanced risk calculation with probabilistic modeling"""
        test_case = {
            "node_subtype": "EC2",
            "request_data": {
                "responses": {
                    "ec2_public_ip": True,
                    "ec2_security_groups": "Wide Open (0.0.0.0/0)",
                    "ec2_ssh_access": "Password Only",
                    "ec2_encryption": False,
                    "ec2_monitoring": "Basic CloudWatch",
                    "ec2_patch_management": "Manual"
                },
                "business_context": {
                    "criticality": "High",
                    "data_classification": "Confidential",
                    "compliance_requirements": ["SOX", "PCI-DSS"],
                    "environment": "Production"
                }
            }
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/expanded-nodes/{test_case['node_subtype']}/calculate-risk",
                json=test_case["request_data"],
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for enhanced risk calculation fields
                expected_fields = ["node_subtype", "risk_assessment", "security_recommendations", "calculation_timestamp", "input_summary"]
                missing_fields = [f for f in expected_fields if f not in data]
                
                if missing_fields:
                    self.log_test("Enhanced Risk Calculation - EC2", False, f"Missing fields: {missing_fields}")
                    return False
                
                risk_assessment = data.get("risk_assessment", {})
                
                # Verify probabilistic modeling fields are present
                expected_probabilistic_fields = ["confidence_interval", "threat_likelihood", "probabilistic_score", "monte_carlo_analysis"]
                missing_probabilistic_fields = [f for f in expected_probabilistic_fields if f not in risk_assessment]
                
                if missing_probabilistic_fields:
                    self.log_test("Enhanced Risk Calculation - EC2", False, 
                                f"Missing probabilistic modeling fields: {missing_probabilistic_fields}")
                    return False
                
                # Verify risk assessment structure
                required_risk_fields = ["composite_risk_score", "risk_level", "risk_factors"]
                missing_risk_fields = [f for f in required_risk_fields if f not in risk_assessment]
                
                if missing_risk_fields:
                    self.log_test("Enhanced Risk Calculation - EC2", False, 
                                f"Missing risk assessment fields: {missing_risk_fields}")
                    return False
                
                # Verify probabilistic modeling values
                confidence_interval = risk_assessment.get("confidence_interval", {})
                if not isinstance(confidence_interval, dict) or "lower" not in confidence_interval or "upper" not in confidence_interval:
                    self.log_test("Enhanced Risk Calculation - EC2", False, 
                                "Invalid confidence_interval structure")
                    return False
                
                threat_likelihood = risk_assessment.get("threat_likelihood", 0)
                if not (0 <= threat_likelihood <= 1):
                    self.log_test("Enhanced Risk Calculation - EC2", False, 
                                f"Invalid threat_likelihood: {threat_likelihood} (should be 0-1)")
                    return False
                
                probabilistic_score = risk_assessment.get("probabilistic_score", 0)
                if not (0 <= probabilistic_score <= 10):
                    self.log_test("Enhanced Risk Calculation - EC2", False, 
                                f"Invalid probabilistic_score: {probabilistic_score} (should be 0-10)")
                    return False
                
                monte_carlo_analysis = risk_assessment.get("monte_carlo_analysis", {})
                if not isinstance(monte_carlo_analysis, dict):
                    self.log_test("Enhanced Risk Calculation - EC2", False, 
                                "Missing monte_carlo_analysis structure")
                    return False
                
                # Verify security recommendations are context-aware
                security_recommendations = data.get("security_recommendations", [])
                if len(security_recommendations) == 0:
                    self.log_test("Enhanced Risk Calculation - EC2", False, 
                                "No security recommendations provided")
                    return False
                
                composite_risk_score = risk_assessment.get("composite_risk_score", 0)
                risk_level = risk_assessment.get("risk_level", "Unknown")
                
                self.log_test("Enhanced Risk Calculation - EC2", True, 
                            f"✅ Probabilistic risk assessment: score {composite_risk_score}, level {risk_level}, "
                            f"likelihood {threat_likelihood:.2f}, {len(security_recommendations)} recommendations")
                return True
            else:
                self.log_test("Enhanced Risk Calculation - EC2", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Enhanced Risk Calculation - EC2", False, f"Error: {str(e)}")
            return False

    def test_expanded_nodes_bulk_risk_assessment(self):
        """Test POST /api/expanded-nodes/bulk-risk-assessment - Test bulk assessment with cross-node correlations"""
        test_data = {
            "nodes": [
                {
                    "node_subtype": "EC2",
                    "responses": {
                        "ec2_public_ip": True,
                        "ec2_security_groups": "Wide Open (0.0.0.0/0)",
                        "ec2_ssh_access": "Password Only",
                        "ec2_encryption": False
                    }
                },
                {
                    "node_subtype": "RDS",
                    "responses": {
                        "rds_public_access": True,
                        "rds_encryption": False,
                        "rds_backup_retention": 1,
                        "rds_multi_az": False
                    }
                },
                {
                    "node_subtype": "S3",
                    "responses": {
                        "s3_public_read": True,
                        "s3_public_write": False,
                        "s3_encryption": False,
                        "s3_versioning": False
                    }
                }
            ],
            "business_context": {
                "environment": "Production",
                "criticality": "High",
                "compliance_requirements": ["PCI-DSS", "SOX"]
            }
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/expanded-nodes/bulk-risk-assessment",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for bulk assessment fields
                expected_fields = ["individual_assessments", "aggregated_metrics", "cross_node_correlations", "overall_risk_summary"]
                missing_fields = [f for f in expected_fields if f not in data]
                
                if missing_fields:
                    self.log_test("Bulk Risk Assessment", False, f"Missing fields: {missing_fields}")
                    return False
                
                individual_assessments = data.get("individual_assessments", [])
                aggregated_metrics = data.get("aggregated_metrics", {})
                cross_node_correlations = data.get("cross_node_correlations", [])
                overall_risk_summary = data.get("overall_risk_summary", {})
                
                # Verify individual assessments for each node
                if len(individual_assessments) != 3:
                    self.log_test("Bulk Risk Assessment", False, 
                                f"Expected 3 individual assessments, got {len(individual_assessments)}")
                    return False
                
                # Verify aggregated metrics structure
                expected_aggregated_fields = ["total_risk_score", "average_risk_score", "highest_risk_node", "risk_distribution"]
                missing_aggregated_fields = [f for f in expected_aggregated_fields if f not in aggregated_metrics]
                
                if missing_aggregated_fields:
                    self.log_test("Bulk Risk Assessment", False, 
                                f"Missing aggregated metrics: {missing_aggregated_fields}")
                    return False
                
                # Verify cross-node correlations
                if len(cross_node_correlations) == 0:
                    self.log_test("Bulk Risk Assessment", False, 
                                "No cross-node correlations identified")
                    return False
                
                # Verify correlation structure
                first_correlation = cross_node_correlations[0]
                expected_correlation_fields = ["correlation_type", "involved_nodes", "risk_amplification", "description"]
                missing_correlation_fields = [f for f in expected_correlation_fields if f not in first_correlation]
                
                if missing_correlation_fields:
                    self.log_test("Bulk Risk Assessment", False, 
                                f"Missing correlation fields: {missing_correlation_fields}")
                    return False
                
                # Verify overall risk summary
                expected_summary_fields = ["composite_risk_score", "risk_level", "critical_findings_count"]
                missing_summary_fields = [f for f in expected_summary_fields if f not in overall_risk_summary]
                
                if missing_summary_fields:
                    self.log_test("Bulk Risk Assessment", False, 
                                f"Missing risk summary fields: {missing_summary_fields}")
                    return False
                
                total_risk_score = aggregated_metrics.get("total_risk_score", 0)
                correlations_count = len(cross_node_correlations)
                composite_risk_score = overall_risk_summary.get("composite_risk_score", 0)
                
                self.log_test("Bulk Risk Assessment", True, 
                            f"✅ Bulk assessment: {len(individual_assessments)} nodes, "
                            f"total risk {total_risk_score}, {correlations_count} correlations, "
                            f"composite score {composite_risk_score}")
                return True
            else:
                self.log_test("Bulk Risk Assessment", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Bulk Risk Assessment", False, f"Error: {str(e)}")
            return False

    def test_expanded_nodes_threat_intelligence_summary(self):
        """Test POST /api/expanded-nodes/threat-intelligence-summary - Test threat intelligence integration"""
        test_data = {
            "node_types": ["EC2", "Lambda", "S3", "RDS", "VPC"],
            "threat_context": {
                "time_range": "last_30_days",
                "severity_threshold": "medium",
                "include_cve_data": True,
                "include_attack_patterns": True
            }
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/expanded-nodes/threat-intelligence-summary",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for threat intelligence fields
                expected_fields = ["node_type_summaries", "cross_cutting_threats", "threat_trends", "recommendations"]
                missing_fields = [f for f in expected_fields if f not in data]
                
                if missing_fields:
                    self.log_test("Threat Intelligence Summary", False, f"Missing fields: {missing_fields}")
                    return False
                
                node_type_summaries = data.get("node_type_summaries", {})
                cross_cutting_threats = data.get("cross_cutting_threats", [])
                threat_trends = data.get("threat_trends", {})
                recommendations = data.get("recommendations", [])
                
                # Verify node type summaries for each requested type
                requested_types = test_data["node_types"]
                missing_summaries = [t for t in requested_types if t not in node_type_summaries]
                
                if missing_summaries:
                    self.log_test("Threat Intelligence Summary", False, 
                                f"Missing node type summaries: {missing_summaries}")
                    return False
                
                # Verify node type summary structure
                first_node_type = list(node_type_summaries.keys())[0]
                first_summary = node_type_summaries[first_node_type]
                
                expected_summary_fields = ["cve_count", "recent_threats", "attack_vectors", "threat_score"]
                missing_summary_fields = [f for f in expected_summary_fields if f not in first_summary]
                
                if missing_summary_fields:
                    self.log_test("Threat Intelligence Summary", False, 
                                f"Missing summary fields for {first_node_type}: {missing_summary_fields}")
                    return False
                
                # Verify cross-cutting threats
                if len(cross_cutting_threats) == 0:
                    self.log_test("Threat Intelligence Summary", False, 
                                "No cross-cutting threats identified")
                    return False
                
                # Verify threat trends structure
                expected_trend_fields = ["trending_threats", "emerging_vulnerabilities", "attack_pattern_changes"]
                missing_trend_fields = [f for f in expected_trend_fields if f not in threat_trends]
                
                if missing_trend_fields:
                    self.log_test("Threat Intelligence Summary", False, 
                                f"Missing threat trend fields: {missing_trend_fields}")
                    return False
                
                # Verify recommendations are threat-intelligence driven
                if len(recommendations) == 0:
                    self.log_test("Threat Intelligence Summary", False, 
                                "No threat intelligence recommendations provided")
                    return False
                
                total_cve_count = sum(summary.get("cve_count", 0) for summary in node_type_summaries.values())
                total_threats = len(cross_cutting_threats)
                
                self.log_test("Threat Intelligence Summary", True, 
                            f"✅ Threat intelligence: {len(node_type_summaries)} node types, "
                            f"{total_cve_count} total CVEs, {total_threats} cross-cutting threats, "
                            f"{len(recommendations)} recommendations")
                return True
            else:
                self.log_test("Threat Intelligence Summary", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Threat Intelligence Summary", False, f"Error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all expanded intelligent nodes API tests"""
        print("🚀 Starting Expanded Intelligent Nodes API Tests...")
        print(f"Testing against: {self.base_url}")
        print("=" * 80)
        
        # Phase 1 Enhanced APIs - Expanded Intelligent Nodes Tests
        tests = [
            ("🎯 Expanded Nodes - Supported Types (30 nodes)", self.test_expanded_nodes_supported_types),
            ("🎯 Expanded Nodes - Categories", self.test_expanded_nodes_categories),
            ("🎯 Multi-Level Questionnaires", self.test_expanded_nodes_multi_level_questionnaires),
            ("🎯 Enhanced Risk Calculation", self.test_expanded_nodes_enhanced_risk_calculation),
            ("🎯 Bulk Risk Assessment", self.test_expanded_nodes_bulk_risk_assessment),
            ("🎯 Threat Intelligence Summary", self.test_expanded_nodes_threat_intelligence_summary),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            print(f"\n🧪 Running: {test_name}")
            try:
                if test_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                self.log_test(test_name, False, f"Unexpected error: {str(e)}")
                failed += 1
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 EXPANDED INTELLIGENT NODES TEST SUMMARY")
        print("=" * 80)
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed / (passed + failed) * 100):.1f}%")
        
        if failed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['message']}")
        
        return passed, failed

if __name__ == "__main__":
    tester = ExpandedNodesAPITester()
    passed, failed = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)