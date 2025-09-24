"""
Context-Aware STRIDE Threat Analysis

This module implements intelligent threat analysis that only applies threats
where they are contextually relevant based on:
1. Application architecture and data flow
2. Attack surface and exposure
3. Data sensitivity and processing
4. Existing security controls
"""

from typing import Dict, List, Any, Optional
from stride_engine import Threat, StrideCategory, ThreatStatus, ElementType
import uuid
from datetime import datetime, timezone

class ContextualThreatAnalyzer:
    """Analyzes threats based on application context and architecture"""
    
    def __init__(self):
        pass
    
    def analyze_context_aware_threats(self, 
                                    node: Dict[str, Any], 
                                    responses: Dict[str, Any],
                                    diagram_context: Dict[str, Any] = None) -> List[Threat]:
        """
        Analyze threats based on actual application context
        
        Args:
            node: Node information (type, subtype, metadata)
            responses: Questionnaire responses
            diagram_context: Full diagram context (other nodes, edges, infrastructure)
        
        Returns:
            List of contextually relevant threats
        """
        threats = []
        node_id = node.get("id", "")
        
        # Analyze application characteristics
        app_context = self._analyze_application_context(responses)
        
        # Only apply threats where contextually relevant
        if app_context["processes_user_input"]:
            threats.extend(self._analyze_input_threats(responses, node_id))
            
        if app_context["handles_sensitive_data"]:
            threats.extend(self._analyze_data_threats(responses, node_id))
            
        if app_context["exposed_to_public"]:
            threats.extend(self._analyze_exposure_threats(responses, node_id))
            
        if app_context["manages_user_sessions"]:
            threats.extend(self._analyze_session_threats(responses, node_id))
            
        return threats
    
    def _analyze_application_context(self, responses: Dict[str, Any]) -> Dict[str, bool]:
        """Determine application characteristics from responses"""
        
        # Does it process user input?
        processes_user_input = (
            responses.get("webapp_database_connection") == "True" or
            responses.get("webapp_api_endpoints") == "True" or
            responses.get("webapp_input_validation") in ["Comprehensive server-side validation", "Basic validation", "Client-side only"]
        )
        
        # Does it handle sensitive data?
        handles_sensitive_data = (
            responses.get("webapp_authentication_method") not in ["No Authentication", "Unknown"] or
            responses.get("webapp_database_connection") == "True" or
            responses.get("webapp_data_encryption") != "No encryption"
        )
        
        # Is it exposed to public?
        exposed_to_public = (
            responses.get("webapp_authentication_method") in ["No Authentication"] or
            # Could be enhanced by checking diagram for WAF/CDN protection
            True  # Default assumption - could be made smarter
        )
        
        # Does it manage user sessions?
        manages_user_sessions = (
            responses.get("webapp_session_management") not in ["No session management", "Unknown"] and
            responses.get("webapp_authentication_method") not in ["No Authentication", "Unknown"]
        )
        
        return {
            "processes_user_input": processes_user_input,
            "handles_sensitive_data": handles_sensitive_data,
            "exposed_to_public": exposed_to_public,
            "manages_user_sessions": manages_user_sessions,
        }
    
    def _analyze_input_threats(self, responses: Dict[str, Any], node_id: str) -> List[Threat]:
        """Analyze input-related threats only for apps that process input"""
        threats = []
        
        validation_method = responses.get("webapp_input_validation")
        
        # Only create tampering threats if weak validation AND processes input
        if validation_method in ["No validation", "Client-side only"]:
            threat = Threat(
                diagram_id="",
                element_type=ElementType.NODE,
                element_id=node_id,
                stride_category=StrideCategory.TAMPERING,
                title="Input Validation Weakness Enables Tampering",
                description=f"Application processes user input but uses {validation_method.lower()}, enabling injection attacks",
                residual_risk=8.0 if validation_method == "No validation" else 7.0,
                mitigations=["Implement comprehensive server-side validation", "Use parameterized queries"],
                references={"owasp": ["A03:2021"], "mitre": ["T1190"]}
            )
            threats.append(threat)
        elif validation_method == "Basic validation":
            # Only partial threat if basic validation
            threat = Threat(
                diagram_id="",
                element_type=ElementType.NODE,
                element_id=node_id,
                stride_category=StrideCategory.TAMPERING,
                title="Basic Validation May Miss Advanced Attacks",
                description="Application processes user input with basic validation, may be vulnerable to sophisticated injection",
                residual_risk=4.5,
                status=ThreatStatus.PARTIAL,
                mitigations=["Enhance validation with schemas", "Add input sanitization"],
                references={"owasp": ["A03:2021"], "mitre": ["T1190"]}
            )
            threats.append(threat)
            
        return threats
    
    def _analyze_data_threats(self, responses: Dict[str, Any], node_id: str) -> List[Threat]:
        """Analyze data protection threats only for apps handling sensitive data"""
        threats = []
        
        https_enforcement = responses.get("webapp_https_enforcement")
        
        # Only create disclosure threats if handles sensitive data AND weak transport
        if https_enforcement in ["HTTP only", "Mixed HTTP/HTTPS"]:
            threat = Threat(
                diagram_id="",
                element_type=ElementType.NODE,
                element_id=node_id,
                stride_category=StrideCategory.INFORMATION_DISCLOSURE,
                title="Sensitive Data Transmitted Over Insecure Channel",
                description=f"Application handles sensitive data but uses {https_enforcement.lower()}, enabling interception",
                residual_risk=7.0 if https_enforcement == "HTTP only" else 6.0,
                mitigations=["Enforce HTTPS", "Enable HSTS"],
                references={"owasp": ["A02:2021"], "mitre": ["T1040"]}
            )
            threats.append(threat)
        elif https_enforcement == "HTTPS preferred":
            # Only partial threat if HTTPS preferred for sensitive data
            threat = Threat(
                diagram_id="",
                element_type=ElementType.NODE,
                element_id=node_id,
                stride_category=StrideCategory.INFORMATION_DISCLOSURE,
                title="HTTPS Not Enforced for Sensitive Data",
                description="Application handles sensitive data but doesn't enforce HTTPS, allowing potential downgrade attacks",
                residual_risk=3.0,
                status=ThreatStatus.PARTIAL,
                mitigations=["Enforce HTTPS redirect", "Add HSTS headers"],
                references={"owasp": ["A02:2021"], "mitre": ["T1040"]}
            )
            threats.append(threat)
            
        return threats
    
    def _analyze_exposure_threats(self, responses: Dict[str, Any], node_id: str) -> List[Threat]:
        """Analyze exposure-related threats only for publicly exposed applications"""
        threats = []
        
        # Check if application is actually exposed and vulnerable to DoS
        rate_limiting = responses.get("webapp_rate_limiting", "Unknown")
        
        # Only create DoS threats if exposed AND no rate limiting
        if rate_limiting in ["No rate limiting", "Basic throttling"]:
            threat = Threat(
                diagram_id="",
                element_type=ElementType.NODE,
                element_id=node_id,
                stride_category=StrideCategory.DENIAL_OF_SERVICE,
                title="Public Application Vulnerable to Resource Exhaustion",
                description=f"Publicly exposed application with {rate_limiting.lower()} vulnerable to DoS attacks",
                residual_risk=6.5 if rate_limiting == "No rate limiting" else 4.0,
                status=ThreatStatus.PARTIAL if rate_limiting == "Basic throttling" else ThreatStatus.OPEN,
                mitigations=["Implement adaptive rate limiting", "Deploy CDN/WAF protection"],
                references={"owasp": ["A06:2021"], "mitre": ["T1499"]}
            )
            threats.append(threat)
            
        return threats
    
    def _analyze_session_threats(self, responses: Dict[str, Any], node_id: str) -> List[Threat]:
        """Analyze session-related threats only for applications with user sessions"""
        threats = []
        
        session_mgmt = responses.get("webapp_session_management")
        
        # Only create session threats if manages sessions AND weak implementation
        if session_mgmt in ["Basic sessions", "Standard sessions"]:
            risk_level = 4.0 if session_mgmt == "Standard sessions" else 5.0
            threat = Threat(
                diagram_id="",
                element_type=ElementType.NODE,
                element_id=node_id,
                stride_category=StrideCategory.ELEVATION_OF_PRIVILEGE,
                title="Session Management Weaknesses Enable Privilege Escalation",
                description=f"Application manages user sessions with {session_mgmt.lower()}, vulnerable to session-based attacks",
                residual_risk=risk_level,
                status=ThreatStatus.PARTIAL,
                mitigations=["Implement secure session management", "Add session rotation", "Enable secure cookie flags"],
                references={"owasp": ["A07:2021"], "mitre": ["T1078"]}
            )
            threats.append(threat)
            
        return threats

# Global instance
contextual_analyzer = ContextualThreatAnalyzer()