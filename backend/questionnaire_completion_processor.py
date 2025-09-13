"""
Questionnaire Completion Processor

This module handles the end-to-end flow when a questionnaire is completed:
1. Process questionnaire responses
2. Update node attributes based on responses
3. Run DSL rule evaluation on modified node + neighbors
4. Execute advanced simulation on affected subgraph
5. Generate findings with framework mappings
6. Persist findings to database
7. Trigger notifications/alerts if needed
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone

from findings_management import (
    FindingsManager, Finding, FindingSeverity, FindingSource,
    create_questionnaire_finding, create_rule_engine_finding, create_simulation_finding
)
from dsl_rule_engine import DSLRuleEngine
from advanced_simulation import AdvancedSimulationEngine
from intelligent_nodes import IntelligentNodeEngine

logger = logging.getLogger(__name__)

class QuestionnaireCompletionProcessor:
    """
    Processes questionnaire completions and orchestrates the end-to-end security analysis flow
    """
    
    def __init__(self, db, findings_manager: FindingsManager):
        self.db = db
        self.findings_manager = findings_manager
        self.dsl_rule_engine = DSLRuleEngine()
        self.intelligent_node_engine = IntelligentNodeEngine()
        
        logger.info("QuestionnaireCompletionProcessor initialized")
    
    async def process_questionnaire_completion(
        self,
        diagram_id: str,
        node_id: str,
        node_subtype: str,
        questionnaire_responses: Dict[str, Any],
        user_id: Optional[str] = None,
        business_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Complete end-to-end processing of questionnaire completion
        
        Args:
            diagram_id: ID of the diagram
            node_id: ID of the node that completed questionnaire
            node_subtype: Type of the node (WebApp, Database, etc.)
            questionnaire_responses: User's responses to questionnaire
            user_id: ID of user who completed questionnaire
            
        Returns:
            Dictionary containing processing results and generated findings
        """
        
        try:
            logger.info(f"Processing questionnaire completion for node {node_id} in diagram {diagram_id}")
            
            processing_results = {
                "diagram_id": diagram_id,
                "node_id": node_id,
                "node_subtype": node_subtype,
                "processed_at": datetime.now(timezone.utc).isoformat(),
                "findings_generated": [],
                "risk_analysis": {},
                "recommendations": [],
                "processing_steps": []
            }
            
            # Step 1: Update node attributes based on questionnaire responses
            updated_node = await self._update_node_attributes(
                diagram_id, node_id, node_subtype, questionnaire_responses
            )
            processing_results["processing_steps"].append("Node attributes updated")
            
            # Step 2: Generate findings from questionnaire analysis
            questionnaire_findings = await self._analyze_questionnaire_responses(
                diagram_id, node_id, node_subtype, questionnaire_responses
            )
            processing_results["processing_steps"].append(f"Generated {len(questionnaire_findings)} questionnaire findings")
            
            # Step 3: Get current diagram state for rule evaluation (support standalone mode)
            diagram = await self._get_diagram_with_updated_node(diagram_id, updated_node)
            if not diagram:
                # Create synthetic diagram for standalone mode
                logger.info(f"Creating synthetic diagram for standalone questionnaire completion")
                diagram = self._create_synthetic_diagram(diagram_id, updated_node)
                processing_results["processing_steps"].append("Created synthetic diagram for standalone mode")
            
            # Step 4: Run DSL rule evaluation on modified node and neighbors
            rule_findings = await self._evaluate_security_rules(
                diagram_id, diagram["nodes"], diagram["edges"], node_id
            )
            processing_results["processing_steps"].append(f"Generated {len(rule_findings)} rule evaluation findings")
            
            # Step 5: Execute advanced simulation on affected subgraph
            simulation_findings = await self._run_security_simulation(
                diagram_id, diagram["nodes"], diagram["edges"], node_id
            )
            processing_results["processing_steps"].append(f"Generated {len(simulation_findings)} simulation findings")
            
            # Step 6: Persist all findings to database
            all_findings = questionnaire_findings + rule_findings + simulation_findings
            persisted_findings = await self._persist_findings(all_findings, user_id)
            processing_results["findings_generated"] = [f.dict() for f in persisted_findings]
            processing_results["processing_steps"].append(f"Persisted {len(persisted_findings)} findings")
            
            # Step 7: Generate summary and recommendations
            summary = await self._generate_completion_summary(
                diagram_id, node_id, persisted_findings
            )
            processing_results.update(summary)
            processing_results["processing_steps"].append("Generated completion summary")
            
            # Step 8: Update diagram metadata with completion info
            await self._update_diagram_completion_metadata(
                diagram_id, node_id, len(persisted_findings), summary["overall_risk_score"]
            )
            processing_results["processing_steps"].append("Updated diagram metadata")
            
            logger.info(f"Questionnaire completion processing finished. Generated {len(persisted_findings)} findings.")
            return processing_results
            
        except Exception as e:
            logger.error(f"Error processing questionnaire completion: {e}")
            raise
    
    async def _update_node_attributes(
        self,
        diagram_id: str,
        node_id: str,
        node_subtype: str,
        responses: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update node attributes based on questionnaire responses"""
        
        try:
            # Convert questionnaire responses to node security attributes
            security_attributes = self._extract_security_attributes(node_subtype, responses)
            
            # Update the node in the diagram
            update_result = await self.db.diagrams.update_one(
                {"id": diagram_id, "nodes.id": node_id},
                {
                    "$set": {
                        "nodes.$.data.securityAttributes": security_attributes,
                        "nodes.$.data.questionnaireResponses": responses,
                        "nodes.$.data.lastQuestionnaireUpdate": datetime.now(timezone.utc).isoformat(),
                        "nodes.$.data.questionnaireCompleted": True
                    }
                }
            )
            
            if update_result.matched_count == 0:
                raise Exception(f"Node {node_id} not found in diagram {diagram_id}")
            
            # Return the updated node data
            diagram = await self.db.diagrams.find_one({"id": diagram_id})
            updated_node = next((node for node in diagram["nodes"] if node["id"] == node_id), None)
            
            logger.info(f"Updated node {node_id} with security attributes from questionnaire")
            return updated_node
            
        except Exception as e:
            logger.error(f"Error updating node attributes: {e}")
            raise
    
    def _extract_security_attributes(self, node_subtype: str, responses: Dict[str, Any]) -> Dict[str, Any]:
        """Convert questionnaire responses to structured security attributes"""
        
        security_attributes = {
            "encryption": {},
            "authentication": {},
            "authorization": {},
            "network_security": {},
            "logging_monitoring": {},
            "compliance": {},
            "risk_factors": []
        }
        
        # Node-specific attribute extraction
        if node_subtype.lower() == "webapp":
            security_attributes.update(self._extract_webapp_attributes(responses))
        elif node_subtype.lower() == "database":
            security_attributes.update(self._extract_database_attributes(responses))
        elif node_subtype.lower() == "api":
            security_attributes.update(self._extract_api_attributes(responses))
        elif node_subtype.lower() == "iam":
            security_attributes.update(self._extract_iam_attributes(responses))
        
        # Extract common security attributes
        security_attributes.update(self._extract_common_attributes(responses))
        
        return security_attributes
    
    def _extract_webapp_attributes(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """Extract WebApp-specific security attributes"""
        attributes = {}
        
        # Authentication attributes
        if "authentication_method" in responses:
            attributes["authentication"] = {
                "method": responses["authentication_method"],
                "multi_factor": responses.get("multi_factor_auth", False),
                "session_timeout": responses.get("session_timeout", 30)
            }
        
        # Input validation
        if "input_validation" in responses:
            attributes["input_validation"] = {
                "enabled": responses["input_validation"],
                "sanitization": responses.get("input_sanitization", False),
                "validation_framework": responses.get("validation_framework", "custom")
            }
        
        # HTTPS configuration
        if "https_enforcement" in responses:
            attributes["network_security"]["https_enforced"] = responses["https_enforcement"]
            attributes["network_security"]["tls_version"] = responses.get("tls_version", "1.2")
        
        return attributes
    
    def _extract_database_attributes(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """Extract Database-specific security attributes"""
        attributes = {}
        
        # Encryption attributes
        if "encryption_at_rest" in responses:
            attributes["encryption"] = {
                "at_rest": responses["encryption_at_rest"],
                "in_transit": responses.get("encryption_in_transit", False),
                "key_management": responses.get("key_management_service", "manual")
            }
        
        # Access control
        if "access_controls" in responses:
            attributes["authorization"] = {
                "rbac_enabled": responses.get("role_based_access", False),
                "principle_least_privilege": responses.get("least_privilege", False),
                "admin_access_restricted": responses.get("admin_restrictions", False)
            }
        
        return attributes
    
    def _extract_api_attributes(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """Extract API-specific security attributes"""
        attributes = {}
        
        # Authentication
        if "api_authentication" in responses:
            attributes["authentication"] = {
                "method": responses["api_authentication"],
                "token_expiration": responses.get("token_expiration", 3600),
                "refresh_tokens": responses.get("refresh_tokens", False)
            }
        
        # Rate limiting
        if "rate_limiting" in responses:
            attributes["rate_limiting"] = {
                "enabled": responses["rate_limiting"],
                "requests_per_minute": responses.get("rate_limit", 100),
                "burst_protection": responses.get("burst_protection", False)
            }
        
        return attributes
    
    def _extract_iam_attributes(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """Extract IAM-specific security attributes"""
        attributes = {}
        
        # Identity management
        if "identity_provider" in responses:
            attributes["identity_management"] = {
                "provider": responses["identity_provider"],
                "federation_enabled": responses.get("federation", False),
                "sso_enabled": responses.get("single_sign_on", False)
            }
        
        return attributes
    
    def _extract_common_attributes(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """Extract common security attributes applicable to all node types"""
        attributes = {}
        
        # Logging and monitoring
        if "security_logging" in responses:
            attributes["logging_monitoring"] = {
                "security_logging": responses["security_logging"],
                "log_retention": responses.get("log_retention_days", 90),
                "monitoring_alerts": responses.get("security_monitoring", False)
            }
        
        # Compliance
        compliance_frameworks = []
        for framework in ["pci_dss", "hipaa", "gdpr", "sox", "iso27001"]:
            if responses.get(framework, False):
                compliance_frameworks.append(framework.upper())
        
        if compliance_frameworks:
            attributes["compliance"]["frameworks"] = compliance_frameworks
        
        return attributes
    
    async def _analyze_questionnaire_responses(
        self,
        diagram_id: str,
        node_id: str,
        node_subtype: str,
        responses: Dict[str, Any]
    ) -> List[Finding]:
        """Analyze questionnaire responses and generate findings"""
        
        findings = []
        
        try:
            # Get questionnaire prompts for risk analysis
            prompts = self.intelligent_node_engine.get_security_prompts(node_subtype)
            
            for prompt in prompts:
                prompt_id = prompt.id
                user_response = responses.get(prompt_id)
                
                if user_response is not None:
                    # Analyze this specific response
                    risk_assessment = self._assess_response_risk(
                        prompt, user_response, node_subtype
                    )
                    
                    # Generate finding if risk is identified
                    if risk_assessment["risk_score"] > 3.0:  # Threshold for generating findings
                        finding = create_questionnaire_finding(
                            diagram_id=diagram_id,
                            node_id=node_id,
                            question_id=prompt_id,
                            question_text=prompt.question,
                            user_response=user_response,
                            risk_assessment=risk_assessment,
                            recommendations=risk_assessment.get("recommendations", [])
                        )
                        findings.append(finding)
            
            logger.info(f"Generated {len(findings)} findings from questionnaire analysis")
            return findings
            
        except Exception as e:
            logger.error(f"Error analyzing questionnaire responses: {e}")
            return []
    
    def _assess_response_risk(
        self,
        prompt: Any,
        user_response: Any,
        node_subtype: str
    ) -> Dict[str, Any]:
        """Assess risk level of a specific questionnaire response"""
        
        risk_assessment = {
            "risk_score": 0.0,
            "category": "General Security",
            "description": "No security issues identified",
            "recommendations": [],
            "framework_tags": [],
            "mitre_techniques": []
        }
        
        # High-risk patterns by response type
        high_risk_patterns = {
            # Authentication-related risks
            "authentication": {
                "no_authentication": {"score": 9.0, "description": "No authentication mechanism in place"},
                "weak_passwords": {"score": 7.0, "description": "Weak password policy"},
                "no_mfa": {"score": 6.0, "description": "Multi-factor authentication not implemented"}
            },
            # Encryption-related risks
            "encryption": {
                "no_encryption": {"score": 8.5, "description": "No encryption implemented"},
                "weak_encryption": {"score": 6.5, "description": "Weak encryption algorithm in use"},
                "no_tls": {"score": 8.0, "description": "TLS/HTTPS not enforced"}
            },
            # Input validation risks
            "input_validation": {
                "no_validation": {"score": 8.0, "description": "Input validation not implemented"},
                "basic_validation": {"score": 4.0, "description": "Basic input validation only"}
            }
        }
        
        # Analyze response based on prompt category and user answer
        prompt_text_lower = prompt.question.lower()
        
        # Check for authentication issues
        if "authentication" in prompt_text_lower or "login" in prompt_text_lower:
            risk_assessment["category"] = "Authentication"
            risk_assessment["framework_tags"] = ["ASVS-2", "OWASP-A07"]
            risk_assessment["mitre_techniques"] = ["T1078"]
            
            if isinstance(user_response, bool) and not user_response:
                risk_assessment.update(high_risk_patterns["authentication"]["no_authentication"])
                risk_assessment["recommendations"] = [
                    "Implement strong authentication mechanism",
                    "Enable multi-factor authentication",
                    "Enforce strong password policies"
                ]
            elif isinstance(user_response, str) and user_response.lower() in ["no", "none", "basic"]:
                risk_assessment.update(high_risk_patterns["authentication"]["weak_passwords"])
        
        # Check for encryption issues
        elif "encryption" in prompt_text_lower or "https" in prompt_text_lower or "tls" in prompt_text_lower:
            risk_assessment["category"] = "Encryption"
            risk_assessment["framework_tags"] = ["ASVS-9", "OWASP-A02"]
            risk_assessment["mitre_techniques"] = ["T1040", "T1557"]
            
            if isinstance(user_response, bool) and not user_response:
                risk_assessment.update(high_risk_patterns["encryption"]["no_encryption"])
                risk_assessment["recommendations"] = [
                    "Implement encryption at rest and in transit",
                    "Use strong encryption algorithms (AES-256)",
                    "Enforce HTTPS/TLS 1.3"
                ]
        
        # Check for input validation issues  
        elif "input" in prompt_text_lower or "validation" in prompt_text_lower:
            risk_assessment["category"] = "Input Validation"
            risk_assessment["framework_tags"] = ["ASVS-5", "OWASP-A03"]
            risk_assessment["mitre_techniques"] = ["T1190"]
            
            if isinstance(user_response, bool) and not user_response:
                risk_assessment.update(high_risk_patterns["input_validation"]["no_validation"])
                risk_assessment["recommendations"] = [
                    "Implement comprehensive input validation",
                    "Use parameterized queries to prevent SQL injection",
                    "Sanitize all user inputs"
                ]
        
        # Check for logging and monitoring issues
        elif "logging" in prompt_text_lower or "monitoring" in prompt_text_lower:
            risk_assessment["category"] = "Logging & Monitoring"
            risk_assessment["framework_tags"] = ["ASVS-7", "NIST-DE"]
            
            if isinstance(user_response, bool) and not user_response:
                risk_assessment["risk_score"] = 5.5
                risk_assessment["description"] = "Insufficient logging and monitoring"
                risk_assessment["recommendations"] = [
                    "Implement comprehensive security logging",
                    "Set up real-time monitoring and alerting",
                    "Establish log retention policies"
                ]
        
        return risk_assessment
    
    async def _get_diagram_with_updated_node(self, diagram_id: str, updated_node: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get diagram with the updated node included"""
        try:
            diagram = await self.db.diagrams.find_one({"id": diagram_id})
            if diagram:
                # Update the node in the diagram data
                for i, node in enumerate(diagram["nodes"]):
                    if node["id"] == updated_node["id"]:
                        diagram["nodes"][i] = updated_node
                        break
            return diagram
        except Exception as e:
            logger.error(f"Error getting updated diagram: {e}")
            return None
    
    async def _evaluate_security_rules(
        self,
        diagram_id: str,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]],
        updated_node_id: str
    ) -> List[Finding]:
        """Run DSL rule evaluation and generate findings"""
        
        findings = []
        
        try:
            # Run rule evaluation
            rule_results = self.dsl_rule_engine.evaluate_rules(nodes, edges)
            
            # Filter for rules that affect the updated node or its neighbors
            relevant_results = []
            neighbor_ids = self._get_neighbor_node_ids(updated_node_id, edges)
            target_nodes = {updated_node_id} | neighbor_ids
            
            for result in rule_results:
                # Check if rule affects target nodes
                matching_nodes = set(result.matching_nodes)
                if matching_nodes & target_nodes:
                    relevant_results.append(result)
            
            # Create findings from rule results
            for result in relevant_results:
                finding = create_rule_engine_finding(
                    diagram_id=diagram_id,
                    node_id=updated_node_id,  # Associate with the updated node
                    rule_id=result.rule_id,
                    rule_result=result.dict()
                )
                findings.append(finding)
            
            logger.info(f"Generated {len(findings)} findings from rule evaluation")
            return findings
            
        except Exception as e:
            logger.error(f"Error evaluating security rules: {e}")
            return []
    
    def _get_neighbor_node_ids(self, node_id: str, edges: List[Dict[str, Any]]) -> set:
        """Get IDs of nodes connected to the given node"""
        neighbors = set()
        
        for edge in edges:
            if edge.get("source") == node_id:
                neighbors.add(edge.get("target"))
            elif edge.get("target") == node_id:
                neighbors.add(edge.get("source"))
        
        return neighbors
    
    async def _run_security_simulation(
        self,
        diagram_id: str,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]],
        updated_node_id: str
    ) -> List[Finding]:
        """Run advanced simulation and generate findings"""
        
        findings = []
        
        try:
            # Create simulation engine instance
            simulation_engine = AdvancedSimulationEngine(nodes, edges)
            
            # Find attack paths that involve the updated node
            attack_paths = simulation_engine.find_attack_paths(max_paths=10, max_length=6)
            
            # Filter for paths that involve the updated node
            relevant_paths = []
            for path in attack_paths:
                path_nodes = set()
                for step in path.steps:
                    if hasattr(step, 'node_id'):
                        path_nodes.add(step.node_id)
                    elif isinstance(step, dict) and 'node_id' in step:
                        path_nodes.add(step['node_id'])
                
                if updated_node_id in path_nodes:
                    relevant_paths.append(path)
            
            # Create findings from attack paths
            for path in relevant_paths:
                if hasattr(path, 'dict'):
                    path_dict = path.dict()
                else:
                    path_dict = path.__dict__ if hasattr(path, '__dict__') else {"name": "Attack Path", "steps": []}
                
                finding = create_simulation_finding(
                    diagram_id=diagram_id,
                    attack_path=path_dict,
                    simulation_result={"simulation_type": "advanced", "paths_found": len(relevant_paths)}
                )
                findings.append(finding)
            
            logger.info(f"Generated {len(findings)} findings from simulation")
            return findings
            
        except Exception as e:
            logger.error(f"Error running security simulation: {e}")
            return []
    
    async def _persist_findings(self, findings: List[Finding], user_id: Optional[str] = None) -> List[Finding]:
        """Persist findings to database"""
        
        persisted_findings = []
        
        for finding in findings:
            if user_id:
                finding.created_by = user_id
                finding.updated_by = user_id
            
            try:
                persisted_finding = await self.findings_manager.create_finding(finding)
                persisted_findings.append(persisted_finding)
            except Exception as e:
                logger.error(f"Error persisting finding {finding.id}: {e}")
        
        logger.info(f"Persisted {len(persisted_findings)} of {len(findings)} findings")
        return persisted_findings
    
    async def _generate_completion_summary(
        self,
        diagram_id: str,
        node_id: str,
        findings: List[Finding]
    ) -> Dict[str, Any]:
        """Generate summary of questionnaire completion and findings"""
        
        summary = {
            "overall_risk_score": 0.0,
            "findings_count": len(findings),
            "severity_distribution": {},
            "top_recommendations": [],
            "compliance_impact": {},
            "risk_trends": {}
        }
        
        if not findings:
            return summary
        
        # Calculate overall risk score
        risk_scores = [f.risk_score for f in findings]
        summary["overall_risk_score"] = sum(risk_scores) / len(risk_scores)
        
        # Severity distribution
        severity_counts = {}
        for finding in findings:
            severity = finding.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        summary["severity_distribution"] = severity_counts
        
        # Top recommendations (from highest severity findings)
        high_severity_findings = [f for f in findings if f.severity in [FindingSeverity.CRITICAL, FindingSeverity.HIGH]]
        recommendations = []
        for finding in high_severity_findings[:5]:  # Top 5
            recommendations.extend(finding.recommendations)
        summary["top_recommendations"] = list(set(recommendations))[:10]  # Unique top 10
        
        # Compliance impact
        framework_counts = {}
        for finding in findings:
            for tag in finding.framework_tags:
                framework_counts[tag] = framework_counts.get(tag, 0) + 1
        summary["compliance_impact"] = framework_counts
        
        return summary
    
    async def _update_diagram_completion_metadata(
        self,
        diagram_id: str,
        node_id: str,
        findings_count: int,
        risk_score: float
    ) -> None:
        """Update diagram metadata with completion information"""
        
        try:
            await self.db.diagrams.update_one(
                {"id": diagram_id},
                {
                    "$set": {
                        f"metadata.node_completions.{node_id}": {
                            "completed_at": datetime.now(timezone.utc).isoformat(),
                            "findings_generated": findings_count,
                            "risk_score": risk_score
                        },
                        "metadata.last_questionnaire_completion": datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            logger.info(f"Updated diagram {diagram_id} completion metadata")
        except Exception as e:
            logger.error(f"Error updating diagram metadata: {e}")