"""
STRIDE Questionnaire-to-Threat Mapping (Extended)
- Declarative mapping from questionnaire answers to STRIDE threats
- Adds criticality/data classification risk multipliers
- Returns explanation metadata for UI transparency
"""
from __future__ import annotations
from typing import Dict, List, Optional
from dataclasses import dataclass
from stride_engine import Threat, StrideCategory, ThreatStatus, ElementType

@dataclass
class OptionImpact:
    category: StrideCategory
    effect: str  # "increase" | "mitigate" | "partial"
    title: str
    description: str
    mitigations: List[str]
    residual_risk: float
    status_override: Optional[ThreatStatus] = None

# Multipliers based on node criticality / data classification
CRITICALITY_MULTIPLIER = {
    "High": 1.25,
    "Medium": 1.0,
    "Low": 0.85,
}
DATA_CLASSIFICATION_MULTIPLIER = {
    "Highly Confidential": 1.25,
    "Confidential": 1.15,
    "Internal": 1.0,
    "Public": 0.85,
}

def _status_for(effect: str, override: Optional[ThreatStatus]) -> ThreatStatus:
    if override is not None:
        return override
    if effect == "increase":
        return ThreatStatus.OPEN
    if effect == "partial":
        return ThreatStatus.PARTIAL
    return ThreatStatus.MITIGATED

# Utility to scale risk with meta
def _apply_risk_multipliers(base: float, node_meta: Dict) -> float:
    meta = node_meta or {}
    criticality = (meta.get("data", {}) or {}).get("criticality") or meta.get("criticality")
    classification = (meta.get("data", {}) or {}).get("data_classification") or meta.get("data_classification")
    m1 = CRITICALITY_MULTIPLIER.get(criticality, 1.0)
    m2 = DATA_CLASSIFICATION_MULTIPLIER.get(classification, 1.0)
    # Cap at 10.0
    return round(min(10.0, max(0.0, base * m1 * m2)), 1)

# Question label lookup for explanations
QUESTION_LABELS = {
    # WebApp
    "webapp_authentication_method": "What authentication method is implemented?",
    "webapp_input_validation": "How is input validation implemented?",
    "webapp_https_enforcement": "Is HTTPS enforced?",
    "webapp_session_management": "How are user sessions managed?",
    "webapp_error_handling": "How are application errors handled?",
    "webapp_logging_monitoring": "What logging and monitoring is in place?",
    "webapp_data_encryption": "How is sensitive data encrypted?",
    "webapp_security_headers": "Are security headers implemented?",
    "webapp_authorization_model": "What authorization model is implemented?",
    "webapp_rate_limiting": "Is rate limiting implemented?",
    # API
    "api_authentication_method": "What authentication method does the API use?",
    "api_authorization_model": "How is API authorization implemented?",
    "api_rate_limiting": "Is rate limiting implemented?",
    "api_input_validation": "How is API input validation implemented?",
    "api_https_enforcement": "Is HTTPS enforced for all API calls?",
    "api_error_handling": "How are API errors handled?",
    "api_logging_monitoring": "What API logging and monitoring is in place?",
    # Database
    "database_authentication": "How is database authentication configured?",
    "database_encryption_at_rest": "Is data encrypted at rest?",
    "database_encryption_in_transit": "Is data encrypted in transit?",
    "database_access_control": "How is database access controlled?",
    "database_logging": "What database logging is configured?",
    "database_network_security": "How is database network access secured?",
}

# WebApp mappings (extended)
WEBAPP_MAPPINGS: Dict[str, Dict[str, List[OptionImpact]]] = {
    "webapp_authentication_method": {
        "No Authentication": [
            OptionImpact(StrideCategory.SPOOFING, "increase", "No Authentication Allows Spoofing", "Absence of authentication enables identity spoofing and unauthorized access.", ["Introduce OAuth2/OIDC or SAML", "Add MFA across user flows"], 8.0)
        ],
        "Username/Password only": [
            OptionImpact(StrideCategory.SPOOFING, "increase", "Weak Authentication Susceptible to Credential Abuse", "Basic username/password without MFA is vulnerable to brute force and credential stuffing.", ["Enable MFA", "Rate limit logins", "Block breached passwords"], 6.5)
        ],
        "Username/Password with MFA": [
            OptionImpact(StrideCategory.SPOOFING, "mitigate", "Multi-Factor Authentication Mitigates Spoofing", "MFA significantly raises the bar against identity spoofing.", ["Maintain MFA for privileged/external access"], 2.0)
        ],
        "OAuth2/OIDC": [
            OptionImpact(StrideCategory.SPOOFING, "mitigate", "Federated Auth Mitigates Spoofing", "Standards-based token auth reduces spoofing risk when configured securely.", ["Short-lived tokens", "Harden token validation"], 1.5)
        ],
        "SAML": [
            OptionImpact(StrideCategory.SPOOFING, "mitigate", "SAML SSO Mitigates Spoofing", "Enterprise SSO with strong policies reduces identity spoofing.", ["Strong IdP policies", "Session binding"], 1.8)
        ],
    },
    "webapp_authorization_model": {
        "No authorization": [
            OptionImpact(StrideCategory.ELEVATION_OF_PRIVILEGE, "increase", "No Authorization Enables Privilege Escalation", "No role checks or scope limitations allow unrestricted actions.", ["Introduce RBAC with fine-grained permissions"], 7.5)
        ],
        "Simple permissions": [
            OptionImpact(StrideCategory.ELEVATION_OF_PRIVILEGE, "partial", "Simple Permissions Provide Limited Control", "Coarse permissions may still overgrant access.", ["Adopt RBAC"], 4.0, status_override=ThreatStatus.PARTIAL)
        ],
        "RBAC with fine-grained permissions": [
            OptionImpact(StrideCategory.ELEVATION_OF_PRIVILEGE, "mitigate", "RBAC + Fine-Grained Permissions Mitigate Elevation", "Least privilege reduces escalation paths.", ["Periodic access reviews"], 2.0)
        ],
        "RBAC with basic roles": [
            OptionImpact(StrideCategory.ELEVATION_OF_PRIVILEGE, "partial", "Basic RBAC Partially Mitigates Elevation", "Broad roles may still grant excessive privileges.", ["Refine role granularity"], 3.5, status_override=ThreatStatus.PARTIAL)
        ],
    },
    "webapp_input_validation": {
        "No validation": [
            OptionImpact(StrideCategory.TAMPERING, "increase", "Missing Input Validation Enables Tampering", "Lack of server-side validation allows injection and data corruption.", ["Implement comprehensive server-side validation", "Sanitization"], 8.0)
        ],
        "Client-side only": [
            OptionImpact(StrideCategory.TAMPERING, "increase", "Client-Only Validation is Bypassable", "Client checks can be bypassed easily.", ["Enforce server-side validation"], 7.0)
        ],
        "Basic validation": [
            OptionImpact(StrideCategory.TAMPERING, "partial", "Basic Validation Provides Limited Protection", "Simple checks reduce but do not eliminate injection/tampering risk.", ["Adopt centralized validation with schemas"], 4.5, status_override=ThreatStatus.PARTIAL)
        ],
        "Comprehensive server-side validation": [
            OptionImpact(StrideCategory.TAMPERING, "mitigate", "Strong Validation Mitigates Tampering", "Robust server-side validation reduces injection/tampering risk.", ["Maintain validation libraries", "Centralize validation"], 2.0)
        ],
    },
    "webapp_https_enforcement": {
        "HTTP only": [
            OptionImpact(StrideCategory.INFORMATION_DISCLOSURE, "increase", "Unencrypted Traffic Exposes Data", "HTTP allows interception and leakage of sensitive data.", ["Force HTTPS", "Enable HSTS"], 7.0)
        ],
        "Mixed HTTP/HTTPS": [
            OptionImpact(StrideCategory.INFORMATION_DISCLOSURE, "increase", "Mixed Transport Security Risks", "Inconsistent HTTPS leads to leakage on unencrypted paths.", ["Enforce HTTPS everywhere", "Eliminate HTTP endpoints"], 6.0)
        ],
        "HTTPS preferred": [
            OptionImpact(StrideCategory.INFORMATION_DISCLOSURE, "partial", "HTTPS Preferred but Not Enforced", "Some risk remains where HTTP may still be accepted.", ["Redirect HTTP->HTTPS", "Harden TLS"], 3.0, status_override=ThreatStatus.PARTIAL)
        ],
        "HTTPS only (HSTS enabled)": [
            OptionImpact(StrideCategory.INFORMATION_DISCLOSURE, "mitigate", "Strict HTTPS Mitigates Info Disclosure", "HSTS prevents downgrade and ensures encrypted transit.", ["Monitor TLS posture"], 1.5)
        ],
    },
    # webapp_session_management moved to later in file with complete options
    "webapp_error_handling": {
        "No error handling": [
            OptionImpact(StrideCategory.INFORMATION_DISCLOSURE, "increase", "No Error Handling Causes Info Disclosure", "Unhandled exceptions and verbose responses leak sensitive information.", ["Centralize error handlers", "Return generic messages"], 6.5)
        ],
        "Detailed error messages": [
            OptionImpact(StrideCategory.INFORMATION_DISCLOSURE, "increase", "Detailed Errors Reveal Sensitive Information", "Technical details aid attackers.", ["Use generic responses", "Secure server-side logging"], 5.5)
        ],
        "Generic error messages": [
            OptionImpact(StrideCategory.INFORMATION_DISCLOSURE, "partial", "Generic Errors Reduce But Don’t Eliminate Risk", "Safer user messages with possible backend leakage if not configured.", ["Review error propagation"], 3.0, status_override=ThreatStatus.PARTIAL)
        ],
        "Secure error handling (no info disclosure)": [
            OptionImpact(StrideCategory.INFORMATION_DISCLOSURE, "mitigate", "Secure Error Handling Mitigates Disclosure", "Sensitive details are never exposed in client responses.", ["Centralize handlers", "Security-focused logging"], 1.5)
        ],
    },
    "webapp_logging_monitoring": {
        "No logging": [
            OptionImpact(StrideCategory.REPUDIATION, "increase", "No Logging Enables Repudiation", "Lack of audit trails prevents accountability and forensics.", ["Enable security event logging", "Centralize logs"], 6.0)
        ],
        "Minimal logging": [
            OptionImpact(StrideCategory.REPUDIATION, "increase", "Minimal Logging Insufficient for Non-Repudiation", "Limited events reduce traceability and investigative value.", ["Expand audit scope", "Alerts on anomalies"], 5.0)
        ],
        "Basic application logging": [
            OptionImpact(StrideCategory.REPUDIATION, "partial", "Basic Logging Provides Partial Evidence", "Covers common events but may miss security-sensitive trails.", ["Add auth/access logs", "Retention & monitoring"], 3.0, status_override=ThreatStatus.PARTIAL)
        ],
        "Comprehensive security logging": [
            OptionImpact(StrideCategory.REPUDIATION, "mitigate", "Comprehensive Logging Mitigates Repudiation", "Full auditability supports investigations and compliance.", ["SIEM integration", "Alerting"], 1.5)
        ],
    },
    "webapp_data_encryption": {
        "No encryption": [
            OptionImpact(StrideCategory.INFORMATION_DISCLOSURE, "increase", "Unencrypted Data May Leak", "Plaintext storage/transit exposes sensitive data.", ["Encrypt at rest and in transit"], 8.0)
        ],
        "Basic encryption": [
            OptionImpact(StrideCategory.INFORMATION_DISCLOSURE, "partial", "Basic Encryption Leaves Gaps", "May use weak algorithms or incomplete coverage.", ["Adopt strong standards", "Key rotation"], 4.0, status_override=ThreatStatus.PARTIAL)
        ],
        "Encryption in transit only": [
            OptionImpact(StrideCategory.INFORMATION_DISCLOSURE, "partial", "Only Transit Encryption is Insufficient", "Stored data remains exposed.", ["Add at-rest encryption"], 4.5, status_override=ThreatStatus.PARTIAL)
        ],
        "Encryption at rest and in transit": [
            OptionImpact(StrideCategory.INFORMATION_DISCLOSURE, "mitigate", "Comprehensive Encryption Mitigates Disclosure", "Protects sensitive data across storage and transport.", ["Key rotation", "Crypto agility"], 2.0)
        ],
    },
    "webapp_security_headers": {
        "No security headers": [
            OptionImpact(StrideCategory.INFORMATION_DISCLOSURE, "increase", "Missing Security Headers Increase Risk", "Lack of CSP/HSTS/XFO leaves room for disclosure and clickjacking.", ["Implement CSP, HSTS, XFO, XCTO"], 6.0)
        ],
        "Minimal headers": [
            OptionImpact(StrideCategory.INFORMATION_DISCLOSURE, "increase", "Minimal Headers Provide Insufficient Protection", "Common web-based attacks remain feasible.", ["Adopt comprehensive header set"], 4.5)
        ],
        "Basic headers": [
            OptionImpact(StrideCategory.INFORMATION_DISCLOSURE, "partial", "Basic Headers Partially Reduce Risk", "Some protections present but not comprehensive.", ["Harden CSP & HSTS"], 3.0, status_override=ThreatStatus.PARTIAL)
        ],
        "Comprehensive security headers": [
            OptionImpact(StrideCategory.INFORMATION_DISCLOSURE, "mitigate", "Comprehensive Headers Mitigate Disclosure", "Well-configured CSP/HSTS/XFO/XCTO protect against several web risks.", ["Continuous header audits"], 1.5)
        ],
    },
    "webapp_session_management": {
        "No session management": [
            OptionImpact(StrideCategory.ELEVATION_OF_PRIVILEGE, "increase", "No Sessions Facilitate Privilege Abuse", "Lack of session controls enables fixation/hijacking patterns.", ["Use secure cookies", "Rotate session IDs", "Short timeouts"], 6.5)
        ],
        "Basic sessions": [
            OptionImpact(StrideCategory.ELEVATION_OF_PRIVILEGE, "partial", "Basic Sessions Provide Limited Protection", "Minimal features leave room for escalation attacks.", ["Harden cookie flags", "Implement rotation"], 4.0, status_override=ThreatStatus.PARTIAL)
        ],
        "Standard sessions": [
            OptionImpact(StrideCategory.ELEVATION_OF_PRIVILEGE, "partial", "Standard Sessions Provide Basic Protection", "Standard session handling with reasonable security but may lack advanced protections.", ["Add session rotation", "Enhance security"], 3.5, status_override=ThreatStatus.PARTIAL)
        ],
        "Secure session management": [
            OptionImpact(StrideCategory.ELEVATION_OF_PRIVILEGE, "mitigate", "Secure Sessions Mitigate Elevation", "Strong session practices reduce privilege escalation avenues.", ["Harden SameSite/HttpOnly/Secure flags"], 2.0)
        ],
    },
    "webapp_rate_limiting": {
        "No rate limiting": [
            OptionImpact(StrideCategory.DENIAL_OF_SERVICE, "increase", "Missing Throttling Enables DoS", "Unlimited requests enable resource exhaustion.", ["Introduce per-user limits", "Adaptive throttling"], 6.5)
        ],
        "Basic throttling": [
            OptionImpact(StrideCategory.DENIAL_OF_SERVICE, "partial", "Basic Throttling Partially Prevents DoS", "Simple caps reduce but don't stop abusive patterns.", ["Use adaptive/dynamic limits"], 4.0, status_override=ThreatStatus.PARTIAL)
        ],
        "Fixed rate limiting": [
            OptionImpact(StrideCategory.DENIAL_OF_SERVICE, "partial", "Fixed Rate Limiting Partially Prevents DoS", "Static limits may not adapt to legitimate traffic patterns.", ["Introduce adaptive limiting"], 3.5, status_override=ThreatStatus.PARTIAL)
        ],
        "Adaptive rate limiting": [
            OptionImpact(StrideCategory.DENIAL_OF_SERVICE, "mitigate", "Adaptive Rate Limiting Mitigates DoS", "Per-user adaptive controls reduce attack surface.", ["Monitor anomalies"], 2.0)
        ],
    },
}

# API mappings (extended)
API_MAPPINGS: Dict[str, Dict[str, List[OptionImpact]]] = {
    "api_authentication_method": {
        "No Authentication": [
            OptionImpact(StrideCategory.SPOOFING, "increase", "Public API Enables Spoofing", "Unauthenticated endpoints allow identity misuse and unauthorized access.", ["Require OAuth2/JWT or API keys"], 7.5)
        ],
        "Basic Authentication": [
            OptionImpact(StrideCategory.SPOOFING, "increase", "Basic Auth Susceptible to Abuse", "Reusable basic credentials are easily compromised.", ["Use OAuth2/JWT", "Short-lived tokens"], 6.5)
        ],
        "API Keys": [
            OptionImpact(StrideCategory.SPOOFING, "partial", "API Keys Provide Moderate Protection", "Depends on key storage/rotation.", ["Rotate keys", "Restrict scope"], 3.5, status_override=ThreatStatus.PARTIAL)
        ],
        "OAuth2/JWT": [
            OptionImpact(StrideCategory.SPOOFING, "mitigate", "Strong Token Auth Mitigates Spoofing", "Tokens with proper claims & expiry resist spoofing.", ["Scope least privilege", "Rotate keys"], 2.0)
        ],
    },
    "api_authorization_model": {
        "No authorization": [
            OptionImpact(StrideCategory.ELEVATION_OF_PRIVILEGE, "increase", "No Authorization Enables Privilege Escalation", "Absence of checks allows unrestricted actions.", ["Introduce RBAC with scopes"], 7.5)
        ],
        "API key permissions": [
            OptionImpact(StrideCategory.ELEVATION_OF_PRIVILEGE, "partial", "API Key Permissions Offer Limited Control", "Coarse-grained permissions.", ["Prefer RBAC"], 4.0, status_override=ThreatStatus.PARTIAL)
        ],
        "Simple role-based": [
            OptionImpact(StrideCategory.ELEVATION_OF_PRIVILEGE, "partial", "Basic RBAC Partially Mitigates Elevation", "Broad roles may still grant excessive privileges.", ["Refine scopes & roles"], 3.5, status_override=ThreatStatus.PARTIAL)
        ],
        "Role-based with scopes": [
            OptionImpact(StrideCategory.ELEVATION_OF_PRIVILEGE, "mitigate", "RBAC + Scopes Mitigate Elevation", "Least privilege reduces escalation paths.", ["Review scope granularity"], 2.0)
        ],
    },
    "api_rate_limiting": {
        "No rate limiting": [
            OptionImpact(StrideCategory.DENIAL_OF_SERVICE, "increase", "Missing Throttling Enables DoS", "Unlimited calls enable resource exhaustion.", ["Apply per-user/global limits"], 6.5)
        ],
        "Basic throttling": [
            OptionImpact(StrideCategory.DENIAL_OF_SERVICE, "partial", "Basic Throttling Partially Prevents DoS", "Simple caps reduce abuse.", ["Introduce dynamic limits"], 4.0, status_override=ThreatStatus.PARTIAL)
        ],
        "Global rate limiting": [
            OptionImpact(StrideCategory.DENIAL_OF_SERVICE, "partial", "Global Limits Provide Shared Protection", "Protects service but may affect legitimate users.", ["Layer per-user limits"], 3.0, status_override=ThreatStatus.PARTIAL)
        ],
        "Per-user rate limiting": [
            OptionImpact(StrideCategory.DENIAL_OF_SERVICE, "mitigate", "Per-user Limits Mitigate DoS", "Fair usage controls reduce attack surface.", ["Adaptive throttling"], 2.0)
        ],
    },
    "api_input_validation": {
        "No validation": [
            OptionImpact(StrideCategory.TAMPERING, "increase", "No Validation Enables Tampering", "Unvalidated inputs allow injection and data tampering.", ["Schema validation + sanitization"], 8.0)
        ],
        "Basic validation": [
            OptionImpact(StrideCategory.TAMPERING, "partial", "Basic Validation Provides Limited Protection", "Simple checks reduce but do not eliminate tampering risk.", ["Schema validation"], 4.5, status_override=ThreatStatus.PARTIAL)
        ],
        "Schema validation + sanitization": [
            OptionImpact(StrideCategory.TAMPERING, "mitigate", "Schema Validation Mitigates Tampering", "Contracts and sanitization prevent injections.", ["Centralize schemas"], 2.0)
        ],
    },
    "api_https_enforcement": {
        "HTTP only": [
            OptionImpact(StrideCategory.INFORMATION_DISCLOSURE, "increase", "Unencrypted API Traffic Exposes Data", "Plaintext transit leaks sensitive information.", ["Force HTTPS"], 7.0)
        ],
        "Mixed HTTP/HTTPS": [
            OptionImpact(StrideCategory.INFORMATION_DISCLOSURE, "increase", "Mixed Transport Security Risks", "Inconsistent HTTPS leaves gaps.", ["Enforce HTTPS"], 6.0)
        ],
        "HTTPS preferred": [
            OptionImpact(StrideCategory.INFORMATION_DISCLOSURE, "partial", "HTTPS Preferred but Not Enforced", "Residual risk from HTTP fallbacks.", ["Enforce HTTPS"], 3.0, status_override=ThreatStatus.PARTIAL)
        ],
        "HTTPS only": [
            OptionImpact(StrideCategory.INFORMATION_DISCLOSURE, "mitigate", "HTTPS Everywhere Mitigates Disclosure", "TLS protects data in transit.", ["TLS hardening"], 2.0)
        ],
    },
    "api_error_handling": {
        "No error handling": [
            OptionImpact(StrideCategory.INFORMATION_DISCLOSURE, "increase", "No Error Handling Causes Info Disclosure", "Unhandled errors leak details.", ["Centralize handlers"], 6.0)
        ],
        "Detailed error info": [
            OptionImpact(StrideCategory.INFORMATION_DISCLOSURE, "increase", "Detailed Errors Reveal Sensitive Information", "Verbose details aid attackers.", ["Return generic responses"], 5.0)
        ],
        "Generic error messages": [
            OptionImpact(StrideCategory.INFORMATION_DISCLOSURE, "partial", "Generic Errors Partially Reduce Risk", "Lower disclosure but not guaranteed.", ["Audit error paths"], 3.0, status_override=ThreatStatus.PARTIAL)
        ],
        "Secure error responses": [
            OptionImpact(StrideCategory.INFORMATION_DISCLOSURE, "mitigate", "Secure Error Handling Mitigates Disclosure", "No sensitive details exposed.", ["Logging segregation"], 1.5)
        ],
    },
    "api_logging_monitoring": {
        "No logging": [
            OptionImpact(StrideCategory.REPUDIATION, "increase", "No Logging Enables Repudiation", "No audit trail for API access/events.", ["Enable API audit logs"], 6.0)
        ],
        "Minimal logging": [
            OptionImpact(StrideCategory.REPUDIATION, "increase", "Minimal Logging Insufficient for Non-Repudiation", "Limited events reduce traceability.", ["Expand audit scope"], 5.0)
        ],
        "Basic request logging": [
            OptionImpact(StrideCategory.REPUDIATION, "partial", "Basic Logging Provides Partial Evidence", "Captures requests but may miss auth/security events.", ["Add auth/error logs"], 3.0, status_override=ThreatStatus.PARTIAL)
        ],
        "Comprehensive API logging": [
            OptionImpact(StrideCategory.REPUDIATION, "mitigate", "Comprehensive Logging Mitigates Repudiation", "Full auditability with monitoring.", ["SIEM integration"], 1.5)
        ],
    },
}

# Database mappings (extended)
DATABASE_MAPPINGS: Dict[str, Dict[str, List[OptionImpact]]] = {
    "database_authentication": {
        "No authentication": [
            OptionImpact(StrideCategory.SPOOFING, "increase", "No DB Auth Allows Spoofing", "Unauthenticated DB access enables identity spoofing and data theft.", ["Enforce auth with MFA"], 8.5)
        ],
        "Basic authentication": [
            OptionImpact(StrideCategory.SPOOFING, "increase", "Weak DB Auth Susceptible to Abuse", "Simple credentials are easily compromised.", ["Strong auth + MFA"], 6.5)
        ],
        "Username/password with complexity": [
            OptionImpact(StrideCategory.SPOOFING, "partial", "Complex Passwords Offer Partial Protection", "Improves baseline but lacks MFA.", ["Adopt MFA"], 3.5, status_override=ThreatStatus.PARTIAL)
        ],
        "Strong authentication with MFA": [
            OptionImpact(StrideCategory.SPOOFING, "mitigate", "Strong DB Auth Mitigates Spoofing", "Multi-factor DB auth resists credential abuse.", ["Centralize IAM"], 2.0)
        ],
    },
    "database_encryption_at_rest": {
        "No encryption": [
            OptionImpact(StrideCategory.INFORMATION_DISCLOSURE, "increase", "DB Data at Rest Exposed", "Plaintext storage risks large-scale disclosure.", ["Enable TDE"], 8.0)
        ],
        "Disk encryption": [
            OptionImpact(StrideCategory.INFORMATION_DISCLOSURE, "partial", "Disk Encryption Provides Partial Protection", "Data may be unencrypted while DB runs.", ["Adopt TDE"], 4.0, status_override=ThreatStatus.PARTIAL)
        ],
        "File-level encryption": [
            OptionImpact(StrideCategory.INFORMATION_DISCLOSURE, "partial", "File-level Encryption is Incomplete", "Logs/tmp may remain unencrypted.", ["Adopt TDE"], 3.5, status_override=ThreatStatus.PARTIAL)
        ],
        "Transparent Data Encryption (TDE)": [
            OptionImpact(StrideCategory.INFORMATION_DISCLOSURE, "mitigate", "TDE Mitigates Disclosure", "At-rest encryption protects stored data.", ["Key rotation"], 2.0)
        ],
    },
    "database_encryption_in_transit": {
        "Unencrypted connections": [
            OptionImpact(StrideCategory.INFORMATION_DISCLOSURE, "increase", "DB Traffic Exposed", "Unencrypted DB connections can be intercepted.", ["Enforce TLS"], 7.0)
        ],
        "SSL/TLS available": [
            OptionImpact(StrideCategory.INFORMATION_DISCLOSURE, "partial", "TLS Available but Not Enforced", "Some connections may remain in plaintext.", ["Require TLS"], 3.0, status_override=ThreatStatus.PARTIAL)
        ],
        "SSL/TLS enforced": [
            OptionImpact(StrideCategory.INFORMATION_DISCLOSURE, "mitigate", "TLS Mitigates Disclosure", "Encrypted transport protects DB traffic.", ["TLS hardening"], 2.0)
        ],
    },
    "database_access_control": {
        "No access control": [
            OptionImpact(StrideCategory.ELEVATION_OF_PRIVILEGE, "increase", "No DB Access Control Enables Privilege Abuse", "Unrestricted access allows unauthorized operations.", ["Implement RBAC & least privilege"], 7.5)
        ],
        "Shared accounts": [
            OptionImpact(StrideCategory.ELEVATION_OF_PRIVILEGE, "increase", "Shared Accounts Obscure Accountability", "Lack of user attribution complicates control and forensics.", ["Per-user accounts", "RBAC"], 5.5)
        ],
        "Basic user roles": [
            OptionImpact(StrideCategory.ELEVATION_OF_PRIVILEGE, "partial", "Basic Roles Provide Limited Control", "Broad roles may overgrant access.", ["Refine role granularity"], 3.5, status_override=ThreatStatus.PARTIAL)
        ],
        "Role-based access with least privilege": [
            OptionImpact(StrideCategory.ELEVATION_OF_PRIVILEGE, "mitigate", "RBAC + Least Privilege Mitigate Elevation", "Granular roles reduce unnecessary privileges.", ["Periodic access reviews"], 2.0)
        ],
    },
    "database_logging": {
        "No logging": [
            OptionImpact(StrideCategory.REPUDIATION, "increase", "No Audit Trail Enables Repudiation", "Lack of logs prevents accountability and forensic analysis.", ["Enable audit logging"], 6.0)
        ],
        "Connection logging only": [
            OptionImpact(StrideCategory.REPUDIATION, "increase", "Connection-Only Logs Insufficient", "Does not capture data access or admin actions.", ["Enable audit logs for queries & DDL"], 5.0)
        ],
        "Basic query logging": [
            OptionImpact(StrideCategory.REPUDIATION, "partial", "Basic Query Logs Provide Partial Evidence", "Improves traceability but may miss admin/security events.", ["Full audit trail"], 3.0, status_override=ThreatStatus.PARTIAL)
        ],
        "Comprehensive audit logging": [
            OptionImpact(StrideCategory.REPUDIATION, "mitigate", "Audit Logging Mitigates Repudiation", "Detailed logs support non-repudiation.", ["Centralize logs", "Retention policies"], 2.0)
        ],
    },
    "database_network_security": {
        "No network security": [
            OptionImpact(StrideCategory.INFORMATION_DISCLOSURE, "increase", "No Network Security Exposes DB", "Open networks enable interception and lateral movement.", ["Private networking", "Firewall rules"], 6.5)
        ],
        "Network restrictions": [
            OptionImpact(StrideCategory.INFORMATION_DISCLOSURE, "partial", "Basic Network Restrictions Provide Limited Protection", "Allowlists without segmentation leave gaps.", ["Segment networks", "VPN"], 3.5, status_override=ThreatStatus.PARTIAL)
        ],
        "Firewall protection": [
            OptionImpact(StrideCategory.INFORMATION_DISCLOSURE, "partial", "Firewall Provides Some Protection", "Needs segmentation and monitoring to be effective.", ["SIEM + segmentation"], 3.0, status_override=ThreatStatus.PARTIAL)
        ],
        "Private network with firewall": [
            OptionImpact(StrideCategory.INFORMATION_DISCLOSURE, "mitigate", "Private Network + Firewall Mitigate Disclosure", "Restricted access path reduces exposure.", ["Zero trust principles"], 2.0)
        ],
    },
}

NODE_TYPE_TO_MAPPINGS = {
    "WebApp": WEBAPP_MAPPINGS,
    "API": API_MAPPINGS,
    "Database": DATABASE_MAPPINGS,
}

def map_responses_to_threats(node_subtype: str, responses: Dict[str, str], node_id: str, diagram_id: str, node_meta: Optional[Dict] = None) -> List[Threat]:
    """Translate questionnaire responses into STRIDE threats via mapping tables."""
    out: List[Threat] = []
    mapping = NODE_TYPE_TO_MAPPINGS.get(node_subtype)
    if not mapping:
        return out

    for qid, answer in responses.items():
        options = mapping.get(qid)
        if not options:
            continue
        impacts = options.get(str(answer))
        if not impacts:
            continue
        for impact in impacts:
            status = _status_for(impact.effect, impact.status_override)
            risk = _apply_risk_multipliers(impact.residual_risk, node_meta or {})
            threat = Threat(
                diagram_id=diagram_id,
                element_type=ElementType.NODE,
                element_id=node_id,
                stride_category=impact.category,
                title=impact.title,
                description=impact.description,
                mitigations=impact.mitigations,
                residual_risk=risk,
                status=status,
            )
            # Attach explanation for UI in references. Keep existing OWASP/MITRE keys too.
            qlabel = QUESTION_LABELS.get(qid, qid)
            threat.references = {
                "mitre": threat.references.get("mitre", []) if threat.references else [],
                "owasp": threat.references.get("owasp", []) if threat.references else [],
                "derived_from": [f"{qlabel}: {answer}"]
            }
            out.append(threat)
    return out