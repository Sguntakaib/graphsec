"""
DSL Rule Engine for Security Modeling Platform
Phase 2: Advanced Security Intelligence

This module implements:
1. YAML-based rule definition system
2. Rule engine for evaluating threat scenarios
3. Control gap detection
4. Security completeness scoring
"""

import yaml
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import re
import networkx as nx

logger = logging.getLogger(__name__)


class ImpactLevel(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class RuleCategory(str, Enum):
    WEB_SECURITY = "web_security"
    DATABASE_SECURITY = "database_security"
    API_SECURITY = "api_security"
    NETWORK_SECURITY = "network_security"
    IDENTITY_ACCESS = "identity_access"
    CLOUD_SECURITY = "cloud_security"


@dataclass
class RuleCondition:
    """Individual condition in a rule"""
    field: str
    operator: str  # ==, !=, in, not_in, contains, missing, exists
    value: Any
    negated: bool = False


@dataclass
class ThreatRule:
    """Complete threat rule definition"""
    id: str
    name: str
    description: str
    category: RuleCategory
    conditions: List[RuleCondition]
    outcome: Dict[str, Any]
    enabled: bool = True
    priority: int = 1
    mitre_techniques: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)


@dataclass
class RuleEvaluationResult:
    """Result of evaluating a rule against a diagram"""
    rule_id: str
    rule_name: str
    triggered: bool
    matching_nodes: List[str] = field(default_factory=list)
    attack_path: List[str] = field(default_factory=list)
    impact_level: ImpactLevel = ImpactLevel.LOW
    risk_score: float = 0.0
    recommendations: List[str] = field(default_factory=list)
    mitre_techniques: List[str] = field(default_factory=list)


@dataclass
class SecurityGap:
    """Identified security control gap"""
    gap_id: str
    node_id: str
    node_type: str
    missing_control: str
    severity: ImpactLevel
    description: str
    recommendations: List[str]
    affected_attack_paths: List[str] = field(default_factory=list)


@dataclass
class CompletenessAnalysis:
    """Security completeness analysis result"""
    overall_score: float
    completeness_percentage: float
    total_gaps: int
    critical_gaps: int
    high_gaps: int
    medium_gaps: int
    low_gaps: int
    gaps_by_category: Dict[str, int]
    improvement_recommendations: List[str]


class DSLRuleEngine:
    """Main DSL Rule Engine for security analysis"""
    
    def __init__(self, rules_directory: Optional[str] = None):
        self.rules: List[ThreatRule] = []
        self.rules_by_category: Dict[RuleCategory, List[ThreatRule]] = {}
        self.rules_directory = rules_directory or str(Path(__file__).parent / "security_rules")
        
        # Initialize with built-in rules
        self._initialize_builtin_rules()
        
        # Load external rules if directory exists
        if Path(self.rules_directory).exists():
            self.load_rules_from_directory(self.rules_directory)
    
    def _initialize_builtin_rules(self):
        """Initialize built-in security rules"""
        builtin_rules = self._get_builtin_rules()
        
        for rule_dict in builtin_rules:
            try:
                rule = self._parse_rule_dict(rule_dict)
                self.add_rule(rule)
            except Exception as e:
                logger.error(f"Failed to initialize built-in rule {rule_dict.get('id', 'unknown')}: {e}")
    
    def _get_builtin_rules(self) -> List[Dict[str, Any]]:
        """Get built-in security rules"""
        return [
            # SQL Injection Rules
            {
                "id": "rule.web.sql_injection",
                "name": "SQL Injection Vulnerability",
                "description": "Website connected to database without input validation controls",
                "category": "web_security",
                "conditions": [
                    {"field": "node.subtype", "operator": "==", "value": "WebApp"},
                    {"field": "connected_to.subtype", "operator": "==", "value": "Database"},
                    {"field": "missing_control", "operator": "==", "value": "InputValidation"}
                ],
                "outcome": {
                    "impact": "High",
                    "attack_path": "Web Application → SQL Injection → Database Compromise",
                    "recommendations": [
                        "Implement parameterized queries",
                        "Deploy input validation controls",
                        "Add Web Application Firewall (WAF)",
                        "Use stored procedures with proper validation"
                    ],
                    "risk_score": 8.5
                },
                "mitre_techniques": ["T1190", "T1213"],
                "priority": 1
            },
            
            # API Security Rules
            {
                "id": "rule.api.broken_authentication",
                "name": "Broken API Authentication",
                "description": "API endpoint without proper authentication controls",
                "category": "api_security",
                "conditions": [
                    {"field": "node.subtype", "operator": "==", "value": "API"},
                    {"field": "missing_control", "operator": "==", "value": "IAMPolicy"}
                ],
                "outcome": {
                    "impact": "High",
                    "attack_path": "External Access → Unauthenticated API → Data Exposure",
                    "recommendations": [
                        "Implement OAuth 2.0 or JWT authentication",
                        "Add API rate limiting",
                        "Deploy API gateway with authentication",
                        "Implement proper access controls"
                    ],
                    "risk_score": 7.8
                },
                "mitre_techniques": ["T1078", "T1190"],
                "priority": 1
            },
            
            # Database Security Rules  
            {
                "id": "rule.database.unencrypted_data",
                "name": "Unencrypted Database",
                "description": "Database storing sensitive data without encryption",
                "category": "database_security",
                "conditions": [
                    {"field": "node.subtype", "operator": "==", "value": "Database"},
                    {"field": "node.data_classification", "operator": "in", "value": ["Confidential", "Restricted"]},
                    {"field": "missing_control", "operator": "==", "value": "Encryption"}
                ],
                "outcome": {
                    "impact": "High",
                    "attack_path": "Database Access → Unencrypted Data → Data Breach",
                    "recommendations": [
                        "Enable database encryption at rest",
                        "Implement encryption in transit (TLS)",
                        "Use column-level encryption for sensitive data",
                        "Deploy database activity monitoring"
                    ],
                    "risk_score": 8.2
                },
                "mitre_techniques": ["T1213", "T1005"],
                "priority": 1
            },
            
            # Network Security Rules
            {
                "id": "rule.network.missing_waf",
                "name": "Missing Web Application Firewall",
                "description": "Web application exposed without WAF protection",
                "category": "web_security",
                "conditions": [
                    {"field": "node.subtype", "operator": "==", "value": "WebApp"},
                    {"field": "exposed_to", "operator": "==", "value": "Internet"},
                    {"field": "missing_control", "operator": "==", "value": "WAF"}
                ],
                "outcome": {
                    "impact": "Medium",
                    "attack_path": "Internet → Unprotected Web App → Application Attacks",
                    "recommendations": [
                        "Deploy Web Application Firewall",
                        "Configure OWASP rule sets",
                        "Enable DDoS protection",
                        "Implement rate limiting"
                    ],
                    "risk_score": 6.5
                },
                "mitre_techniques": ["T1190", "T1499"],
                "priority": 2
            },
            
            # Identity and Access Rules
            {
                "id": "rule.iam.weak_authentication",
                "name": "Weak Authentication Mechanism",
                "description": "Critical assets accessible with weak authentication",
                "category": "identity_access",
                "conditions": [
                    {"field": "node.criticality", "operator": "in", "value": ["Critical", "High"]},
                    {"field": "authentication_type", "operator": "==", "value": "Password"},
                    {"field": "missing_control", "operator": "==", "value": "MFA"}
                ],
                "outcome": {
                    "impact": "High",
                    "attack_path": "Credential Compromise → Weak Auth → Critical Asset Access",
                    "recommendations": [
                        "Implement Multi-Factor Authentication (MFA)",
                        "Deploy Single Sign-On (SSO)",
                        "Use certificate-based authentication",
                        "Implement zero-trust principles"
                    ],
                    "risk_score": 7.5
                },
                "mitre_techniques": ["T1078", "T1110"],
                "priority": 1
            },
            
            # Cloud Security Rules
            {
                "id": "rule.cloud.s3_public_bucket",
                "name": "Publicly Accessible S3 Bucket",
                "description": "S3 bucket with public read/write access",
                "category": "cloud_security",
                "conditions": [
                    {"field": "node.subtype", "operator": "==", "value": "S3Bucket"},
                    {"field": "node.public_access", "operator": "==", "value": True}
                ],
                "outcome": {
                    "impact": "Critical",
                    "attack_path": "Internet → Public S3 Bucket → Data Exposure",
                    "recommendations": [
                        "Remove public access permissions",
                        "Implement bucket policies with least privilege",
                        "Enable S3 access logging",
                        "Use IAM roles for access control"
                    ],
                    "risk_score": 9.0
                },
                "mitre_techniques": ["T1530", "T1213"],
                "priority": 1
            },
            
            # Attack Surface Rules
            {
                "id": "rule.surface.ssrf_vulnerability",
                "name": "Server-Side Request Forgery Risk",
                "description": "Application with SSRF vulnerability accessing internal resources",
                "category": "web_security", 
                "conditions": [
                    {"field": "node.subtype", "operator": "==", "value": "SSRF"},
                    {"field": "connected_to.subtype", "operator": "in", "value": ["IMDS", "Database", "VM"]}
                ],
                "outcome": {
                    "impact": "High",
                    "attack_path": "SSRF Vulnerability → Internal Resource Access → Privilege Escalation",
                    "recommendations": [
                        "Implement URL validation and allowlisting",
                        "Deploy egress proxy with filtering",
                        "Disable unnecessary protocols",
                        "Use network segmentation"
                    ],
                    "risk_score": 8.0
                },
                "mitre_techniques": ["T1190", "T1482"],
                "priority": 1
            },
            
            # Control Effectiveness Rules
            {
                "id": "rule.control.low_effectiveness",
                "name": "Low Effectiveness Security Control",
                "description": "Security control with insufficient effectiveness rating",
                "category": "network_security",
                "conditions": [
                    {"field": "node.type", "operator": "==", "value": "Control"},
                    {"field": "node.effectiveness", "operator": "<", "value": 60}
                ],
                "outcome": {
                    "impact": "Medium",
                    "attack_path": "Weak Control → Bypassed Protection → Asset Compromise",
                    "recommendations": [
                        "Review and improve control configuration",
                        "Update security control policies",
                        "Consider additional compensating controls",
                        "Regular effectiveness assessment"
                    ],
                    "risk_score": 5.5
                },
                "mitre_techniques": ["T1562"],
                "priority": 3
            },

            # Additional Web Security Rules
            {
                "id": "rule.web.xss_vulnerability",
                "name": "Cross-Site Scripting (XSS) Risk",
                "description": "Web application vulnerable to XSS attacks",
                "category": "web_security",
                "conditions": [
                    {"field": "node.subtype", "operator": "==", "value": "WebApp"},
                    {"field": "missing_control", "operator": "==", "value": "InputValidation"},
                    {"field": "node.public_access", "operator": "==", "value": True}
                ],
                "outcome": {
                    "impact": "High",
                    "attack_path": "Malicious Script → User Browser → Session Hijacking",
                    "recommendations": [
                        "Implement output encoding and input validation",
                        "Use Content Security Policy (CSP)",
                        "Deploy XSS protection headers",
                        "Regular security testing"
                    ],
                    "risk_score": 7.2
                },
                "mitre_techniques": ["T1189", "T1056"],
                "priority": 1
            },

            # API Security Rules
            {
                "id": "rule.api.idor_vulnerability", 
                "name": "Insecure Direct Object Reference",
                "description": "API endpoints vulnerable to IDOR attacks",
                "category": "api_security",
                "conditions": [
                    {"field": "node.subtype", "operator": "==", "value": "API"},
                    {"field": "missing_control", "operator": "==", "value": "Authorization"}
                ],
                "outcome": {
                    "impact": "High",
                    "attack_path": "API Request → Unauthorized Object Access → Data Exposure",
                    "recommendations": [
                        "Implement proper authorization checks",
                        "Use indirect object references",
                        "Validate user permissions for each request",
                        "Deploy API security gateway"
                    ],
                    "risk_score": 7.8
                },
                "mitre_techniques": ["T1190", "T1213"],
                "priority": 1
            },

            # Data Security Rules
            {
                "id": "rule.data.unprotected_pii",
                "name": "Unprotected Personal Information",
                "description": "Database containing PII without proper protection",
                "category": "database_security",
                "conditions": [
                    {"field": "node.subtype", "operator": "==", "value": "Database"},
                    {"field": "node.data_classification", "operator": "in", "value": ["PII", "PHI", "Confidential"]},
                    {"field": "missing_control", "operator": "==", "value": "DLP"}
                ],
                "outcome": {
                    "impact": "Critical",
                    "attack_path": "Database Access → Unprotected PII → Privacy Breach",
                    "recommendations": [
                        "Deploy Data Loss Prevention (DLP) controls",
                        "Implement data masking and anonymization",
                        "Enable database activity monitoring",
                        "Use field-level encryption for sensitive data"
                    ],
                    "risk_score": 9.2
                },
                "mitre_techniques": ["T1213", "T1005"],
                "priority": 1
            },

            # Cloud Security Rules
            {
                "id": "rule.cloud.weak_iam_policy",
                "name": "Overly Permissive IAM Policy",
                "description": "Cloud resources with excessive permissions",
                "category": "cloud_security",
                "conditions": [
                    {"field": "node.type", "operator": "==", "value": "Asset"},
                    {"field": "node.subtype", "operator": "in", "value": ["S3Bucket", "VM", "API"]},
                    {"field": "node.iam_policy", "operator": "contains", "value": "*"}
                ],
                "outcome": {
                    "impact": "High",
                    "attack_path": "Credential Compromise → Excessive Permissions → Lateral Movement",
                    "recommendations": [
                        "Implement principle of least privilege",
                        "Use specific resource ARNs instead of wildcards",
                        "Regular IAM policy review and cleanup",
                        "Enable AWS CloudTrail for monitoring"
                    ],
                    "risk_score": 8.1
                },
                "mitre_techniques": ["T1078", "T1484"],
                "priority": 1
            },

            # Network Security Rules
            {
                "id": "rule.network.missing_segmentation",
                "name": "Missing Network Segmentation",
                "description": "Critical assets without proper network isolation",
                "category": "network_security",
                "conditions": [
                    {"field": "node.criticality", "operator": "==", "value": "Critical"},
                    {"field": "missing_control", "operator": "==", "value": "NetworkACL"}
                ],
                "outcome": {
                    "impact": "High",
                    "attack_path": "Network Access → Lateral Movement → Critical Asset Compromise",
                    "recommendations": [
                        "Implement network segmentation",
                        "Deploy Network Access Control Lists (NACLs)",
                        "Use micro-segmentation for critical assets",
                        "Enable network monitoring and logging"
                    ],
                    "risk_score": 7.6
                },
                "mitre_techniques": ["T1021", "T1090"],
                "priority": 2
            },

            # Identity and Access Rules
            {
                "id": "rule.iam.privileged_account_risk",
                "name": "Unprotected Privileged Account",
                "description": "Privileged accounts without additional protection",
                "category": "identity_access",
                "conditions": [
                    {"field": "node.subtype", "operator": "==", "value": "PrivilegedAccount"},
                    {"field": "missing_control", "operator": "==", "value": "PAM"}
                ],
                "outcome": {
                    "impact": "Critical",
                    "attack_path": "Credential Compromise → Privileged Access → System Takeover",
                    "recommendations": [
                        "Implement Privileged Access Management (PAM)",
                        "Enable session recording for privileged access",
                        "Use just-in-time access provisioning",
                        "Regular privileged account auditing"
                    ],
                    "risk_score": 9.0
                },
                "mitre_techniques": ["T1078", "T1133"],
                "priority": 1
            },

            # Application Security Rules
            {
                "id": "rule.app.insecure_deserialization",
                "name": "Insecure Deserialization Vulnerability",
                "description": "Application vulnerable to deserialization attacks",
                "category": "web_security",
                "conditions": [
                    {"field": "node.subtype", "operator": "in", "value": ["WebApp", "API"]},
                    {"field": "node.uses_serialization", "operator": "==", "value": True},
                    {"field": "missing_control", "operator": "==", "value": "InputValidation"}
                ],
                "outcome": {
                    "impact": "Critical",
                    "attack_path": "Malicious Payload → Deserialization → Remote Code Execution",
                    "recommendations": [
                        "Avoid deserializing untrusted data",
                        "Implement integrity checks on serialized objects",
                        "Use safe serialization libraries",
                        "Monitor and log deserialization activities"
                    ],
                    "risk_score": 9.1
                },
                "mitre_techniques": ["T1190", "T1059"],
                "priority": 1
            },

            # Supply Chain Security Rules
            {
                "id": "rule.supply_chain.vulnerable_dependencies",
                "name": "Vulnerable Third-Party Dependencies",
                "description": "Application using components with known vulnerabilities",
                "category": "web_security",
                "conditions": [
                    {"field": "node.subtype", "operator": "in", "value": ["WebApp", "API"]},
                    {"field": "node.has_vulnerabilities", "operator": "==", "value": True}
                ],
                "outcome": {
                    "impact": "High",
                    "attack_path": "Vulnerable Component → Exploitation → Application Compromise",
                    "recommendations": [
                        "Regularly update all dependencies",
                        "Use dependency scanning tools",
                        "Implement Software Bill of Materials (SBOM)",
                        "Monitor for security advisories"
                    ],
                    "risk_score": 7.9
                },
                "mitre_techniques": ["T1195", "T1190"],
                "priority": 2
            },

            # Mobile Security Rules  
            {
                "id": "rule.mobile.insecure_storage",
                "name": "Insecure Mobile Data Storage",
                "description": "Mobile application storing sensitive data insecurely",
                "category": "web_security",
                "conditions": [
                    {"field": "node.subtype", "operator": "==", "value": "MobileApp"},
                    {"field": "missing_control", "operator": "==", "value": "Encryption"}
                ],
                "outcome": {
                    "impact": "High",
                    "attack_path": "Device Access → Unencrypted Storage → Data Theft",
                    "recommendations": [
                        "Use device keychain/keystore for sensitive data",
                        "Implement application-layer encryption",
                        "Avoid storing sensitive data locally",
                        "Use certificate pinning for API communications"
                    ],
                    "risk_score": 7.4
                },
                "mitre_techniques": ["T1005", "T1041"],
                "priority": 2
            },

            # Container Security Rules
            {
                "id": "rule.container.privileged_container",
                "name": "Privileged Container Risk",
                "description": "Container running with excessive privileges",
                "category": "cloud_security",
                "conditions": [
                    {"field": "node.subtype", "operator": "==", "value": "Container"},
                    {"field": "node.privileged", "operator": "==", "value": True}
                ],
                "outcome": {
                    "impact": "High",
                    "attack_path": "Container Escape → Host System Access → Lateral Movement",
                    "recommendations": [
                        "Run containers with minimal privileges",
                        "Use security contexts and pod security policies",
                        "Implement runtime security monitoring",
                        "Regular container image scanning"
                    ],
                    "risk_score": 8.3
                },
                "mitre_techniques": ["T1611", "T1068"],
                "priority": 1
            },

            # IoT Security Rules
            {
                "id": "rule.iot.default_credentials",
                "name": "IoT Device Default Credentials",
                "description": "IoT device using default or weak credentials",
                "category": "identity_access",
                "conditions": [
                    {"field": "node.subtype", "operator": "==", "value": "IoTDevice"},
                    {"field": "node.default_credentials", "operator": "==", "value": True}
                ],
                "outcome": {
                    "impact": "Medium",
                    "attack_path": "Default Credentials → Device Compromise → Network Access",
                    "recommendations": [
                        "Change all default passwords immediately",
                        "Implement strong authentication mechanisms",
                        "Use device certificates for authentication",
                        "Regular firmware updates and patching"
                    ],
                    "risk_score": 6.8
                },
                "mitre_techniques": ["T1078", "T1021"],
                "priority": 2
            }
        ]
    
    def _parse_rule_dict(self, rule_dict: Dict[str, Any]) -> ThreatRule:
        """Parse rule dictionary into ThreatRule object"""
        conditions = []
        for cond_dict in rule_dict.get("conditions", []):
            condition = RuleCondition(
                field=cond_dict["field"],
                operator=cond_dict["operator"],
                value=cond_dict["value"],
                negated=cond_dict.get("negated", False)
            )
            conditions.append(condition)
        
        return ThreatRule(
            id=rule_dict["id"],
            name=rule_dict["name"],
            description=rule_dict["description"],
            category=RuleCategory(rule_dict["category"]),
            conditions=conditions,
            outcome=rule_dict["outcome"],
            enabled=rule_dict.get("enabled", True),
            priority=rule_dict.get("priority", 1),
            mitre_techniques=rule_dict.get("mitre_techniques", []),
            references=rule_dict.get("references", [])
        )
    
    def add_rule(self, rule: ThreatRule):
        """Add a rule to the engine"""
        self.rules.append(rule)
        
        if rule.category not in self.rules_by_category:
            self.rules_by_category[rule.category] = []
        self.rules_by_category[rule.category].append(rule)
    
    def load_rules_from_directory(self, directory: str):
        """Load rules from YAML files in a directory"""
        rules_path = Path(directory)
        if not rules_path.exists():
            logger.warning(f"Rules directory {directory} does not exist")
            return
        
        for yaml_file in rules_path.glob("*.yaml"):
            try:
                self.load_rules_from_file(str(yaml_file))
            except Exception as e:
                logger.error(f"Failed to load rules from {yaml_file}: {e}")
    
    def load_rules_from_file(self, file_path: str):
        """Load rules from a YAML file"""
        try:
            with open(file_path, 'r') as f:
                rules_data = yaml.safe_load(f)
            
            for rule_dict in rules_data.get("rules", []):
                rule = self._parse_rule_dict(rule_dict)
                self.add_rule(rule)
                
            logger.info(f"Loaded {len(rules_data.get('rules', []))} rules from {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to load rules from {file_path}: {e}")
            raise
    
    def evaluate_rules(self, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> List[RuleEvaluationResult]:
        """Evaluate all rules against a security diagram"""
        results = []
        
        # Build graph for analysis
        graph = self._build_analysis_graph(nodes, edges)
        
        # Evaluate each rule
        for rule in self.rules:
            if not rule.enabled:
                continue
                
            try:
                result = self._evaluate_single_rule(rule, nodes, edges, graph)
                if result:
                    results.append(result)
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.id}: {e}")
        
        # Sort by priority and risk score
        results.sort(key=lambda x: (x.rule_id.split('.')[1], -x.risk_score))
        
        return results
    
    def _build_analysis_graph(self, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> nx.DiGraph:
        """Build NetworkX graph for analysis"""
        G = nx.DiGraph()
        
        # Add nodes with attributes
        for node in nodes:
            G.add_node(node["id"], **node)
        
        # Add edges
        for edge in edges:
            source = edge.get("source")
            target = edge.get("target") 
            if source and target and G.has_node(source) and G.has_node(target):
                G.add_edge(source, target, **edge)
        
        return G
    
    def _evaluate_single_rule(self, rule: ThreatRule, nodes: List[Dict[str, Any]], 
                             edges: List[Dict[str, Any]], graph: nx.DiGraph) -> Optional[RuleEvaluationResult]:
        """Evaluate a single rule against the diagram"""
        matching_nodes = []
        
        # Check conditions for each node
        for node in nodes:
            if self._node_matches_conditions(node, rule.conditions, nodes, edges, graph):
                matching_nodes.append(node["id"])
        
        if not matching_nodes:
            return None
        
        # Extract outcome data
        outcome = rule.outcome
        impact_level = ImpactLevel(outcome.get("impact", "Low"))
        risk_score = float(outcome.get("risk_score", 0.0))
        recommendations = outcome.get("recommendations", [])
        attack_path_str = outcome.get("attack_path", "")
        attack_path = [step.strip() for step in attack_path_str.split("→")] if attack_path_str else []
        
        return RuleEvaluationResult(
            rule_id=rule.id,
            rule_name=rule.name,
            triggered=True,
            matching_nodes=matching_nodes,
            attack_path=attack_path,
            impact_level=impact_level,
            risk_score=risk_score,
            recommendations=recommendations,
            mitre_techniques=rule.mitre_techniques
        )
    
    def _node_matches_conditions(self, node: Dict[str, Any], conditions: List[RuleCondition],
                                nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]], 
                                graph: nx.DiGraph) -> bool:
        """Check if a node matches all rule conditions"""
        for condition in conditions:
            if not self._evaluate_condition(condition, node, nodes, edges, graph):
                return False
        return True
    
    def _evaluate_condition(self, condition: RuleCondition, node: Dict[str, Any],
                           nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]], 
                           graph: nx.DiGraph) -> bool:
        """Evaluate a single condition"""
        field_parts = condition.field.split(".")
        
        if field_parts[0] == "node":
            # Direct node property
            value = self._get_nested_value(node, field_parts[1:])
            result = self._compare_values(value, condition.operator, condition.value)
            
        elif field_parts[0] == "connected_to":
            # Check connected nodes
            result = self._check_connected_nodes(node, condition, nodes, edges, graph)
            
        elif field_parts[0] == "missing_control":
            # Check for missing security controls
            result = self._check_missing_control(node, condition.value, nodes, edges, graph)
            
        elif field_parts[0] == "exposed_to":
            # Check exposure to external entities
            result = self._check_exposure(node, condition.value, nodes, edges, graph)
            
        elif field_parts[0] == "authentication_type":
            # Check authentication configuration
            result = self._check_authentication_type(node, condition.value, nodes)
            
        else:
            # Default to node property lookup
            value = self._get_nested_value(node, field_parts)
            result = self._compare_values(value, condition.operator, condition.value)
        
        return result if not condition.negated else not result
    
    def _get_nested_value(self, obj: Dict[str, Any], path: List[str]) -> Any:
        """Get nested value from dictionary"""
        current = obj
        for key in path:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current
    
    def _compare_values(self, actual: Any, operator: str, expected: Any) -> bool:
        """Compare values based on operator"""
        if actual is None:
            return operator in ["missing", "!="] or (operator == "==" and expected is None)
        
        if operator == "==":
            return actual == expected
        elif operator == "!=":
            return actual != expected
        elif operator == "in":
            return actual in expected if isinstance(expected, (list, tuple, set)) else False
        elif operator == "not_in":
            return actual not in expected if isinstance(expected, (list, tuple, set)) else True
        elif operator == "contains":
            return expected in str(actual)
        elif operator == "<":
            return float(actual) < float(expected)
        elif operator == ">":
            return float(actual) > float(expected)
        elif operator == "<=":
            return float(actual) <= float(expected)
        elif operator == ">=":
            return float(actual) >= float(expected)
        elif operator == "exists":
            return True
        elif operator == "missing":
            return False
        
        return False
    
    def _check_connected_nodes(self, node: Dict[str, Any], condition: RuleCondition,
                              nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]], 
                              graph: nx.DiGraph) -> bool:
        """Check if node is connected to nodes matching condition"""
        node_id = node["id"]
        
        # Get connected node IDs
        connected_ids = set()
        for edge in edges:
            if edge.get("source") == node_id:
                connected_ids.add(edge.get("target"))
            elif edge.get("target") == node_id:
                connected_ids.add(edge.get("source"))
        
        # Check connected nodes
        field_path = condition.field.split(".")[1:]  # Remove "connected_to"
        for connected_id in connected_ids:
            connected_node = next((n for n in nodes if n["id"] == connected_id), None)
            if connected_node:
                value = self._get_nested_value(connected_node, field_path)
                if self._compare_values(value, condition.operator, condition.value):
                    return True
        
        return False
    
    def _check_missing_control(self, node: Dict[str, Any], control_type: str,
                              nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]], 
                              graph: nx.DiGraph) -> bool:
        """Check if a required security control is missing"""
        node_id = node["id"]
        
        # Find connected control nodes
        control_nodes = []
        for edge in edges:
            target_id = None
            if edge.get("source") == node_id:
                target_id = edge.get("target")
            elif edge.get("target") == node_id:
                target_id = edge.get("source")
            
            if target_id:
                target_node = next((n for n in nodes if n["id"] == target_id), None)
                if target_node and target_node.get("type") == "Control":
                    control_nodes.append(target_node)
        
        # Check if required control type exists
        for control in control_nodes:
            if control.get("subtype") == control_type:
                return False  # Control exists, so not missing
        
        return True  # Control is missing
    
    def _check_exposure(self, node: Dict[str, Any], exposure_type: str,
                       nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]], 
                       graph: nx.DiGraph) -> bool:
        """Check if node is exposed to external entities"""
        node_id = node["id"]
        
        # Look for exposure through zones or direct connections
        for edge in edges:
            connected_id = None
            if edge.get("source") == node_id:
                connected_id = edge.get("target")
            elif edge.get("target") == node_id:
                connected_id = edge.get("source")
            
            if connected_id:
                connected_node = next((n for n in nodes if n["id"] == connected_id), None)
                if connected_node:
                    # Check if connected to Internet zone or external attacker
                    if (connected_node.get("subtype") == exposure_type or
                        connected_node.get("label", "").lower() == exposure_type.lower()):
                        return True
        
        return False
    
    def _check_authentication_type(self, node: Dict[str, Any], auth_type: str,
                                  nodes: List[Dict[str, Any]]) -> bool:
        """Check authentication type configuration"""
        # Look for authentication configuration in node data or attributes
        auth_config = node.get("authentication_type") or node.get("data", {}).get("authentication_type")
        return auth_config == auth_type if auth_config else False
    
    def detect_security_gaps(self, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> List[SecurityGap]:
        """Detect security control gaps in the diagram"""
        gaps = []
        
        # Define required controls by node type/subtype
        required_controls = {
            "WebApp": ["WAF", "InputValidation"],
            "API": ["IAMPolicy", "WAF"],
            "Database": ["Encryption", "IAMPolicy"],
            "S3Bucket": ["IAMPolicy", "Encryption"]
        }
        
        for node in nodes:
            if node.get("type") != "Asset":
                continue
                
            subtype = node.get("subtype")
            if subtype not in required_controls:
                continue
            
            node_id = node["id"]
            
            # Check for each required control
            for required_control in required_controls[subtype]:
                if self._check_missing_control(node, required_control, nodes, edges, None):
                    gap = SecurityGap(
                        gap_id=f"gap-{node_id}-{required_control.lower()}",
                        node_id=node_id,
                        node_type=subtype,
                        missing_control=required_control,
                        severity=self._determine_gap_severity(subtype, required_control, node),
                        description=f"{subtype} '{node.get('label', node_id)}' is missing {required_control} control",
                        recommendations=self._get_control_recommendations(required_control)
                    )
                    gaps.append(gap)
        
        return gaps
    
    def _determine_gap_severity(self, node_type: str, control_type: str, node: Dict[str, Any]) -> ImpactLevel:
        """Determine severity of a security gap"""
        criticality = node.get("criticality", "Medium")
        
        # High-impact combinations
        high_impact_combos = [
            ("Database", "Encryption"),
            ("WebApp", "InputValidation"),
            ("API", "IAMPolicy")
        ]
        
        if (node_type, control_type) in high_impact_combos:
            if criticality in ["Critical", "High"]:
                return ImpactLevel.CRITICAL
            else:
                return ImpactLevel.HIGH
        
        # Map criticality to impact
        if criticality == "Critical":
            return ImpactLevel.HIGH
        elif criticality == "High":
            return ImpactLevel.MEDIUM
        else:
            return ImpactLevel.LOW
    
    def _get_control_recommendations(self, control_type: str) -> List[str]:
        """Get recommendations for implementing a control"""
        recommendations = {
            "WAF": [
                "Deploy Web Application Firewall with OWASP rule sets",
                "Configure custom rules for application-specific threats",
                "Enable DDoS protection and rate limiting"
            ],
            "InputValidation": [
                "Implement server-side input validation",
                "Use parameterized queries for database access",
                "Sanitize all user inputs and file uploads"
            ],
            "IAMPolicy": [
                "Implement least-privilege access controls",
                "Use role-based access control (RBAC)",
                "Enable multi-factor authentication (MFA)"
            ],
            "Encryption": [
                "Enable encryption at rest for stored data",
                "Implement encryption in transit (TLS/SSL)",
                "Use strong encryption algorithms (AES-256)"
            ]
        }
        
        return recommendations.get(control_type, ["Implement appropriate security controls"])
    
    def calculate_completeness_score(self, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> CompletenessAnalysis:
        """Calculate security completeness score for a diagram"""
        
        # Get security gaps
        gaps = self.detect_security_gaps(nodes, edges)
        
        # Count gaps by severity
        critical_gaps = len([g for g in gaps if g.severity == ImpactLevel.CRITICAL])
        high_gaps = len([g for g in gaps if g.severity == ImpactLevel.HIGH])
        medium_gaps = len([g for g in gaps if g.severity == ImpactLevel.MEDIUM])
        low_gaps = len([g for g in gaps if g.severity == ImpactLevel.LOW])
        
        # Count asset nodes that need protection
        asset_nodes = [n for n in nodes if n.get("type") == "Asset"]
        total_assets = len(asset_nodes)
        
        if total_assets == 0:
            return CompletenessAnalysis(
                overall_score=0.0,
                completeness_percentage=0.0,
                total_gaps=0,
                critical_gaps=0,
                high_gaps=0,
                medium_gaps=0,
                low_gaps=0,
                gaps_by_category={},
                improvement_recommendations=["Add assets to analyze security completeness"]
            )
        
        # Calculate weighted score (critical gaps have more impact)
        gap_penalty = (critical_gaps * 4 + high_gaps * 2 + medium_gaps * 1 + low_gaps * 0.5)
        max_possible_gaps = total_assets * 3  # Assume average 3 controls per asset
        
        completeness_percentage = max(0, (max_possible_gaps - gap_penalty) / max_possible_gaps * 100)
        overall_score = completeness_percentage / 10  # Scale to 0-10
        
        # Group gaps by category
        gaps_by_category = {}
        for gap in gaps:
            category = gap.node_type
            gaps_by_category[category] = gaps_by_category.get(category, 0) + 1
        
        # Generate improvement recommendations
        recommendations = []
        if critical_gaps > 0:
            recommendations.append(f"Address {critical_gaps} critical security gaps immediately")
        if high_gaps > 0:
            recommendations.append(f"Resolve {high_gaps} high-priority security gaps")
        if completeness_percentage < 70:
            recommendations.append("Overall security posture needs significant improvement")
        if not any(n.get("type") == "Control" for n in nodes):
            recommendations.append("Add security controls to protect critical assets")
        
        return CompletenessAnalysis(
            overall_score=round(overall_score, 2),
            completeness_percentage=round(completeness_percentage, 1),
            total_gaps=len(gaps),
            critical_gaps=critical_gaps,
            high_gaps=high_gaps,
            medium_gaps=medium_gaps,
            low_gaps=low_gaps,
            gaps_by_category=gaps_by_category,
            improvement_recommendations=recommendations
        )
    
    def get_rules_by_category(self, category: RuleCategory) -> List[ThreatRule]:
        """Get rules filtered by category"""
        return self.rules_by_category.get(category, [])
    
    def get_rule_by_id(self, rule_id: str) -> Optional[ThreatRule]:
        """Get a specific rule by ID"""
        for rule in self.rules:
            if rule.id == rule_id:
                return rule
        return None
    
    def get_rule_statistics(self) -> Dict[str, Any]:
        """Get statistics about loaded rules"""
        stats = {
            "total_rules": len(self.rules),
            "enabled_rules": len([r for r in self.rules if r.enabled]),
            "rules_by_category": {cat.value: len(rules) for cat, rules in self.rules_by_category.items()},
            "rules_by_priority": {},
            "rules_with_mitre": len([r for r in self.rules if r.mitre_techniques])
        }
        
        # Count by priority
        for rule in self.rules:
            priority = rule.priority
            stats["rules_by_priority"][priority] = stats["rules_by_priority"].get(priority, 0) + 1
        
        return stats


# Global instance
dsl_rule_engine = DSLRuleEngine()