"""
STRIDE Threat Analysis Engine

Implements STRIDE (Spoofing, Tampering, Repudiation, Information Disclosure, 
Denial of Service, Elevation of Privilege) threat modeling for security diagrams.

Based on Phase 1 requirements from roadmap.txt
"""

from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import uuid
import logging

logger = logging.getLogger(__name__)

class StrideCategory(str, Enum):
    SPOOFING = "Spoofing"
    TAMPERING = "Tampering" 
    REPUDIATION = "Repudiation"
    INFORMATION_DISCLOSURE = "Information Disclosure"
    DENIAL_OF_SERVICE = "Denial of Service"
    ELEVATION_OF_PRIVILEGE = "Elevation of Privilege"

class ThreatStatus(str, Enum):
    OPEN = "open"
    MITIGATED = "mitigated"
    PARTIAL = "partial"

class ElementType(str, Enum):
    NODE = "node"
    EDGE = "edge"

class Threat(BaseModel):
    """STRIDE Threat Model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    diagram_id: str
    element_type: ElementType
    element_id: str
    stride_category: StrideCategory
    title: str
    description: str
    references: Dict[str, List[str]] = {"mitre": [], "owasp": []}
    mitigations: List[str] = []  # control_ids or suggestions
    status: ThreatStatus = ThreatStatus.OPEN
    residual_risk: float = 0.0  # 0-10 scale
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StrideRuleEngine:
    """Engine for determining STRIDE threats based on node/edge properties and questionnaire responses"""
    
    def __init__(self):
        self.node_threat_rules = self._initialize_node_threat_rules()
        self.edge_threat_rules = self._initialize_edge_threat_rules()
    
    def _initialize_node_threat_rules(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize threat rules for different node subtypes"""
        return {
            # WebApp Threats
            "WebApp": [
                {
                    "stride_category": StrideCategory.SPOOFING,
                    "title": "Authentication Bypass",
                    "description": "Web application may be vulnerable to authentication bypass attacks",
                    "conditions": lambda responses: responses.get("authentication_method") in ["none", "basic"],
                    "residual_risk": 7.5,
                    "mitigations": ["Implement MFA", "Strong authentication protocols"],
                    "references": {"owasp": ["A07:2021"], "mitre": ["T1078"]}
                },
                {
                    "stride_category": StrideCategory.TAMPERING,
                    "title": "Data Integrity Compromise",
                    "description": "Lack of input validation may allow data tampering",
                    "conditions": lambda responses: responses.get("input_validation") == "none",
                    "residual_risk": 8.0,
                    "mitigations": ["Implement server-side validation", "Use integrity checks"],
                    "references": {"owasp": ["A03:2021"], "mitre": ["T1565"]}
                },
                {
                    "stride_category": StrideCategory.INFORMATION_DISCLOSURE,
                    "title": "Sensitive Data Exposure",
                    "description": "Insufficient encryption may lead to data exposure",
                    "conditions": lambda responses: not responses.get("encryption_enabled", False),
                    "residual_risk": 6.5,
                    "mitigations": ["Enable HTTPS/TLS", "Encrypt sensitive data"],
                    "references": {"owasp": ["A02:2021"], "mitre": ["T1041"]}
                },
                {
                    "stride_category": StrideCategory.DENIAL_OF_SERVICE,
                    "title": "Resource Exhaustion",
                    "description": "Missing rate limiting may allow DoS attacks",
                    "conditions": lambda responses: not responses.get("rate_limiting", False),
                    "residual_risk": 5.5,
                    "mitigations": ["Implement rate limiting", "Resource monitoring"],
                    "references": {"owasp": ["A06:2021"], "mitre": ["T1499"]}
                },
                {
                    "stride_category": StrideCategory.ELEVATION_OF_PRIVILEGE,
                    "title": "Authorization Flaws",
                    "description": "Weak authorization controls may allow privilege escalation",
                    "conditions": lambda responses: responses.get("authorization_model") in ["none", "basic"],
                    "residual_risk": 7.0,
                    "mitigations": ["Implement RBAC", "Least privilege principle"],
                    "references": {"owasp": ["A01:2021"], "mitre": ["T1068"]}
                }
            ],
            
            # API Threats
            "API": [
                {
                    "stride_category": StrideCategory.SPOOFING,
                    "title": "API Key Spoofing",
                    "description": "Weak API authentication may allow spoofing attacks",
                    "conditions": lambda responses: responses.get("authentication_method") in ["none", "api_key_only"],
                    "residual_risk": 6.8,
                    "mitigations": ["Implement OAuth 2.0", "JWT tokens with short expiry"],
                    "references": {"owasp": ["API2:2023"], "mitre": ["T1078"]}
                },
                {
                    "stride_category": StrideCategory.INFORMATION_DISCLOSURE,
                    "title": "API Data Leakage", 
                    "description": "Excessive data exposure through API responses",
                    "conditions": lambda responses: not responses.get("response_filtering", False),
                    "residual_risk": 7.2,
                    "mitigations": ["Implement response filtering", "Data minimization"],
                    "references": {"owasp": ["API3:2023"], "mitre": ["T1213"]}
                },
                {
                    "stride_category": StrideCategory.DENIAL_OF_SERVICE,
                    "title": "API Rate Limit Abuse",
                    "description": "Missing rate limiting allows API abuse and DoS",
                    "conditions": lambda responses: not responses.get("rate_limiting", False),
                    "residual_risk": 6.0,
                    "mitigations": ["API rate limiting", "Request throttling"],
                    "references": {"owasp": ["API4:2023"], "mitre": ["T1499"]}
                }
            ],
            
            # Database Threats
            "Database": [
                {
                    "stride_category": StrideCategory.SPOOFING,
                    "title": "Database Authentication Bypass",
                    "description": "Weak database authentication may allow unauthorized access",
                    "conditions": lambda responses: responses.get("authentication_method") == "none",
                    "residual_risk": 8.5,
                    "mitigations": ["Strong database authentication", "Network segmentation"],
                    "references": {"owasp": ["A07:2021"], "mitre": ["T1078"]}
                },
                {
                    "stride_category": StrideCategory.TAMPERING,
                    "title": "SQL Injection",
                    "description": "Insufficient input validation may allow SQL injection",
                    "conditions": lambda responses: not responses.get("parameterized_queries", False),
                    "residual_risk": 9.0,
                    "mitigations": ["Parameterized queries", "Input validation"],
                    "references": {"owasp": ["A03:2021"], "mitre": ["T1190"]}
                },
                {
                    "stride_category": StrideCategory.INFORMATION_DISCLOSURE,
                    "title": "Data Encryption Missing",
                    "description": "Unencrypted database storage may expose sensitive data",
                    "conditions": lambda responses: not responses.get("encryption_at_rest", False),
                    "residual_risk": 7.8,
                    "mitigations": ["Database encryption", "TDE implementation"],
                    "references": {"owasp": ["A02:2021"], "mitre": ["T1005"]}
                },
                {
                    "stride_category": StrideCategory.REPUDIATION,
                    "title": "Insufficient Database Logging",
                    "description": "Missing audit logs prevent non-repudiation",
                    "conditions": lambda responses: not responses.get("audit_logging", False),
                    "residual_risk": 4.5,
                    "mitigations": ["Enable database audit logging", "Log monitoring"],
                    "references": {"owasp": ["A09:2021"], "mitre": ["T1562"]}
                }
            ],
            
            # ExternalAttacker Threats (Actor)
            "ExternalAttacker": [
                {
                    "stride_category": StrideCategory.SPOOFING,
                    "title": "Identity Spoofing Attack",
                    "description": "External attacker may attempt identity spoofing",
                    "conditions": lambda responses: True,  # Always applicable for external attackers
                    "residual_risk": 6.0,
                    "mitigations": ["Strong authentication", "Identity verification"],
                    "references": {"mitre": ["T1078", "T1134"]}
                },
                {
                    "stride_category": StrideCategory.ELEVATION_OF_PRIVILEGE,
                    "title": "Privilege Escalation Attempt",
                    "description": "External attacker may attempt privilege escalation",
                    "conditions": lambda responses: True,
                    "residual_risk": 7.5,
                    "mitigations": ["Least privilege", "Access controls"],
                    "references": {"mitre": ["T1068", "T1055"]}
                }
            ]
        }
    
    def _initialize_edge_threat_rules(self) -> List[Dict[str, Any]]:
        """Initialize threat rules for edges based on properties"""
        return [
            {
                "stride_category": StrideCategory.TAMPERING,
                "title": "Unencrypted Data Flow",
                "description": "Data transmission without encryption may allow tampering",
                "conditions": lambda edge: edge.get("protocol", "").lower() in ["http", "ftp", "telnet"],
                "residual_risk": 7.0,
                "mitigations": ["Use HTTPS/TLS", "Encrypt data in transit"],
                "references": {"owasp": ["A02:2021"], "mitre": ["T1040"]}
            },
            {
                "stride_category": StrideCategory.INFORMATION_DISCLOSURE,
                "title": "Data Interception Risk",
                "description": "Unencrypted communication may allow data interception",
                "conditions": lambda edge: not edge.get("encryption", False),
                "residual_risk": 6.8,
                "mitigations": ["Enable TLS encryption", "VPN tunneling"],
                "references": {"owasp": ["A02:2021"], "mitre": ["T1040"]}
            },
            {
                "stride_category": StrideCategory.SPOOFING,
                "title": "Authentication Missing",
                "description": "Communication without authentication may allow spoofing",
                "conditions": lambda edge: edge.get("auth", "none") == "none",
                "residual_risk": 5.5,
                "mitigations": ["Implement mutual authentication", "Certificate-based auth"],
                "references": {"mitre": ["T1078"]}
            }
        ]
    
    def analyze_node_threats(self, node: Dict[str, Any], questionnaire_responses: Dict[str, Any] = None, diagram_id: str = "") -> List[Threat]:
        """Analyze STRIDE threats for a single node"""
        threats = []
        node_subtype = node.get("subtype", "")
        node_id = node.get("id", "")
        
        if not questionnaire_responses:
            questionnaire_responses = {}
        
        # 1) Use explicit questionnaire-to-STRIDE mapping
        try:
            from stride_mapping import map_responses_to_threats  # local import to avoid cycles
            mapped = map_responses_to_threats(node_subtype, questionnaire_responses, node_id=node_id, diagram_id="", node_meta=node)
            threats.extend(mapped)
        except Exception as e:
            logger.warning(f"STRIDE mapping failed for node {node_id} of type {node_subtype}: {e}")
        
        # 2) Apply heuristic rules as fallback/augmentation
        rules = self.node_threat_rules.get(node_subtype, [])
        for rule in rules:
            try:
                if rule["conditions"](questionnaire_responses):
                    threat = Threat(
                        diagram_id="",  # set by caller later
                        element_type=ElementType.NODE,
                        element_id=node_id,
                        stride_category=rule["stride_category"],
                        title=rule["title"],
                        description=rule["description"],
                        residual_risk=rule["residual_risk"],
                        mitigations=rule["mitigations"],
                        references=rule["references"],
                    )
                    threats.append(threat)
            except Exception as e:
                logger.warning(f"Error evaluating threat rule for {node_subtype}: {e}")
        
        return threats
    
    def analyze_edge_threats(self, edge: Dict[str, Any]) -> List[Threat]:
        """Analyze STRIDE threats for a single edge"""
        threats = []
        edge_id = edge.get("id", "")
        edge_data = edge.get("data", {})
        
        for rule in self.edge_threat_rules:
            try:
                if rule["conditions"](edge_data):
                    threat = Threat(
                        diagram_id="",  # Will be set by caller
                        element_type=ElementType.EDGE,
                        element_id=edge_id,
                        stride_category=rule["stride_category"],
                        title=rule["title"],
                        description=rule["description"],
                        residual_risk=rule["residual_risk"],
                        mitigations=rule["mitigations"],
                        references=rule["references"]
                    )
                    threats.append(threat)
            except Exception as e:
                logger.warning(f"Error evaluating edge threat rule: {e}")
        
        return threats

class StrideThreatAnalyzer:
    """Main STRIDE analysis orchestrator"""
    
    def __init__(self):
        self.rule_engine = StrideRuleEngine()
    
    async def analyze_diagram_threats(self, diagram: Dict[str, Any], 
                                   questionnaire_data: Dict[str, Dict[str, Any]] = None) -> List[Threat]:
        """
        Analyze STRIDE threats for entire diagram
        """
        threats: List[Threat] = []
        diagram_id = diagram.get("id", "")
        nodes = diagram.get("nodes", [])
        edges = diagram.get("edges", [])
        
        if not questionnaire_data:
            questionnaire_data = {}
        
        # Analyze node threats (mapping + heuristic rules)
        for node in nodes:
            node_id = node.get("id", "")
            node_responses = questionnaire_data.get(node_id, {})
            node_threats = self.rule_engine.analyze_node_threats(node, node_responses)
            
            # Set diagram_id and de-duplicate (title + category + element)
            seen = set()
            for t in node_threats:
                t.diagram_id = diagram_id
                key = (t.element_id, t.stride_category.value, t.title)
                if key in seen:
                    continue
                seen.add(key)
                threats.append(t)
        
        # Analyze edge threats
        for edge in edges:
            edge_threats = self.rule_engine.analyze_edge_threats(edge)
            for t in edge_threats:
                t.diagram_id = diagram_id
                threats.append(t)
        
        logger.info(f"STRIDE analysis complete: {len(threats)} threats identified for diagram {diagram_id}")
        return threats
    
    def calculate_coverage_summary(self, threats: List[Threat]) -> Dict[str, Any]:
        """Calculate STRIDE coverage summary from threat list"""
        category_counts = {category.value: 0 for category in StrideCategory}
        mitigated_counts = {category.value: 0 for category in StrideCategory}
        total_risk = 0.0
        threat_count = 0
        by_node: Dict[str, Any] = {}
        by_edge: Dict[str, Any] = {}
        
        for threat in threats:
            category = threat.stride_category.value
            category_counts[category] += 1
            if threat.status in [ThreatStatus.MITIGATED, ThreatStatus.PARTIAL]:
                mitigated_counts[category] += 1
            total_risk += threat.residual_risk
            threat_count += 1
            
            if threat.element_type == ElementType.NODE:
                if threat.element_id not in by_node:
                    by_node[threat.element_id] = {"totals": {cat.value: 0 for cat in StrideCategory}, "mitigated": {cat.value: 0 for cat in StrideCategory}}
                by_node[threat.element_id]["totals"][category] += 1
                if threat.status in [ThreatStatus.MITIGATED, ThreatStatus.PARTIAL]:
                    by_node[threat.element_id]["mitigated"][category] += 1
            elif threat.element_type == ElementType.EDGE:
                if threat.element_id not in by_edge:
                    by_edge[threat.element_id] = {"totals": {cat.value: 0 for cat in StrideCategory}, "mitigated": {cat.value: 0 for cat in StrideCategory}}
                by_edge[threat.element_id]["totals"][category] += 1
                if threat.status in [ThreatStatus.MITIGATED, ThreatStatus.PARTIAL]:
                    by_edge[threat.element_id]["mitigated"][category] += 1
        
        residual_risk_avg = total_risk / max(threat_count, 1)
        return {
            "totals": category_counts,
            "mitigated": mitigated_counts,
            "residual_risk_avg": round(residual_risk_avg, 2),
            "by_node": by_node,
            "by_edge": by_edge,
            "total_threats": threat_count,
            "mitigation_percentage": round((sum(mitigated_counts.values()) / max(threat_count, 1)) * 100, 1)
        }

# Global analyzer instance
stride_analyzer = StrideThreatAnalyzer()