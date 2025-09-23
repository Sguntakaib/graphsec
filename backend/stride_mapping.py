"""
STRIDE Questionnaire-to-Threat Mapping

Purpose:
- Convert questionnaire responses (question_id -&gt; selected option) into STRIDE threats
- Aligns each answer option to either:
  • increase risk for a STRIDE category (create OPEN threat)
  • demonstrate mitigation for a STRIDE category (create MITIGATED threat)

This complements the heuristic rules in StrideRuleEngine by using explicit mappings
from the questionnaires. Mappings here are minimal viable set for WebApp, API,
Database and can be extended incrementally.
"""
from __future__ import annotations
from typing import Dict, List
from dataclasses import dataclass
from .stride_engine import Threat, StrideCategory, ThreatStatus, ElementType

@dataclass
class OptionImpact:
    category: StrideCategory
    effect: str  # "increase" | "mitigate"
    title: str
    description: str
    mitigations: List[str]
    residual_risk: float

# Minimal MVP mappings to start. Extend as needed.
# Keys must exactly match questionnaire IDs and option strings from YAML
WEBAPP_MAPPINGS: Dict[str, Dict[str, List[OptionImpact]]] = {
    "webapp_authentication_method": {
        "No Authentication": [
            OptionImpact(
                category=StrideCategory.SPOOFING,
                effect="increase",
                title="No Authentication Allows Spoofing",
                description="Absence of authentication enables identity spoofing and unauthorized access.",
                mitigations=["Introduce strong authentication (OAuth2/OIDC, SAML, or MFA)"],
                residual_risk=8.0,
            )
        ],
        "Username/Password only": [
            OptionImpact(
                category=StrideCategory.SPOOFING,
                effect="increase",
                title="Weak Authentication Susceptible to Credential Abuse",
                description="Basic username/password without MFA is vulnerable to brute force and credential stuffing.",
                mitigations=["Enable MFA", "Rate limit logins", "Credential stuffing protections"],
                residual_risk=6.5,
            )
        ],
        "Username/Password with MFA": [
            OptionImpact(
                category=StrideCategory.SPOOFING,
                effect="mitigate",
                title="Multi-Factor Authentication Mitigates Spoofing",
                description="MFA significantly raises bar against identity spoofing.",
                mitigations=["Maintain MFA for all privileged and external access"],
                residual_risk=2.0,
            )
        ],
        "OAuth2/OIDC": [
            OptionImpact(
                category=StrideCategory.SPOOFING,
                effect="mitigate",
                title="Federated Auth Mitigates Spoofing",
                description="Standards-based token auth reduces spoofing risk when configured securely.",
                mitigations=["Use short-lived tokens", "Harden token validation"],
                residual_risk=1.5,
            )
        ],
        "SAML": [
            OptionImpact(
                category=StrideCategory.SPOOFING,
                effect="mitigate",
                title="SAML SSO Mitigates Spoofing",
                description="Enterprise SSO with strong policies reduces identity spoofing.",
                mitigations=["Strong IdP policies", "Session binding"],
                residual_risk=1.8,
            )
        ],
    },
    "webapp_input_validation": {
        "No validation": [
            OptionImpact(
                category=StrideCategory.TAMPERING,
                effect="increase",
                title="Missing Input Validation Enables Tampering",
                description="Lack of server-side validation allows injection and data corruption.",
                mitigations=["Implement comprehensive server-side validation", "Sanitization"],
                residual_risk=8.0,
            )
        ],
        "Client-side only": [
            OptionImpact(
                category=StrideCategory.TAMPERING,
                effect="increase",
                title="Client-Only Validation is Bypassable",
                description="Attackers can bypass client logic leading to tampering and injections.",
                mitigations=["Enforce server-side validation"],
                residual_risk=7.0,
            )
        ],
        "Comprehensive server-side validation": [
            OptionImpact(
                category=StrideCategory.TAMPERING,
                effect="mitigate",
                title="Strong Validation Mitigates Tampering",
                description="Robust server-side validation reduces injection/tampering risk.",
                mitigations=["Maintain validation libraries", "Centralize validation"],
                residual_risk=2.0,
            )
        ],
    },
    "webapp_https_enforcement": {
        "HTTP only": [
            OptionImpact(
                category=StrideCategory.INFORMATION_DISCLOSURE,
                effect="increase",
                title="Unencrypted Traffic Exposes Data",
                description="HTTP allows interception and leakage of sensitive data.",
                mitigations=["Force HTTPS", "Enable HSTS"],
                residual_risk=7.0,
            )
        ],
        "Mixed HTTP/HTTPS": [
            OptionImpact(
                category=StrideCategory.INFORMATION_DISCLOSURE,
                effect="increase",
                title="Mixed Transport Security Risks",
                description="Inconsistent HTTPS leads to leakage on unencrypted paths.",
                mitigations=["Enforce HTTPS everywhere", "Eliminate HTTP endpoints"],
                residual_risk=6.0,
            )
        ],
        "HTTPS only (HSTS enabled)": [
            OptionImpact(
                category=StrideCategory.INFORMATION_DISCLOSURE,
                effect="mitigate",
                title="Strict HTTPS Mitigates Info Disclosure",
                description="HSTS prevents downgrade and ensures encrypted transit.",
                mitigations=["Monitor TLS posture"],
                residual_risk=1.5,
            )
        ],
    },
    "webapp_session_management": {
        "No session management": [
            OptionImpact(
                category=StrideCategory.ELEVATION_OF_PRIVILEGE,
                effect="increase",
                title="No Sessions Facilitate Privilege Abuse",
                description="Lack of session controls enables fixation/hijacking patterns.",
                mitigations=["Use secure cookies", "Rotate session IDs", "Short timeouts"],
                residual_risk=6.5,
            )
        ],
        "Secure session management": [
            OptionImpact(
                category=StrideCategory.ELEVATION_OF_PRIVILEGE,
                effect="mitigate",
                title="Secure Sessions Mitigate Elevation",
                description="Strong session practices reduce privilege escalation avenues.",
                mitigations=["Harden SameSite/HttpOnly/Secure flags"],
                residual_risk=2.0,
            )
        ],
    },
    "webapp_data_encryption": {
        "No encryption": [
            OptionImpact(
                category=StrideCategory.INFORMATION_DISCLOSURE,
                effect="increase",
                title="Unencrypted Data May Leak",
                description="Plaintext storage/transit exposes sensitive data.",
                mitigations=["Encrypt at rest &amp; in transit"],
                residual_risk=8.0,
            )
        ],
        "Encryption at rest and in transit": [
            OptionImpact(
                category=StrideCategory.INFORMATION_DISCLOSURE,
                effect="mitigate",
                title="Comprehensive Encryption Mitigates Disclosure",
                description="Protects sensitive data across storage and transport.",
                mitigations=["Key rotation", "Crypto agility"],
                residual_risk=2.0,
            )
        ],
    },
}

API_MAPPINGS: Dict[str, Dict[str, List[OptionImpact]]] = {
    "api_authentication_method": {
        "No Authentication": [
            OptionImpact(StrideCategory.SPOOFING, "increase", "Public API Enables Spoofing", "Unauthenticated endpoints allow identity misuse and unauthorized access.", ["Require OAuth2/JWT or API keys"], 7.5)
        ],
        "Basic Authentication": [
            OptionImpact(StrideCategory.SPOOFING, "increase", "Basic Auth Susceptible to Abuse", "Reusable basic credentials are easily compromised.", ["Use OAuth2/JWT", "Short-lived tokens"], 6.5)
        ],
        "OAuth2/JWT": [
            OptionImpact(StrideCategory.SPOOFING, "mitigate", "Strong Token Auth Mitigates Spoofing", "Tokens with proper claims &amp; expiry resist spoofing.", ["Scope least privilege", "Rotate keys"], 2.0)
        ],
    },
    "api_rate_limiting": {
        "No rate limiting": [
            OptionImpact(StrideCategory.DENIAL_OF_SERVICE, "increase", "Missing Throttling Enables DoS", "Unlimited calls enable resource exhaustion.", ["Apply per-user/global limits"], 6.5)
        ],
        "Per-user rate limiting": [
            OptionImpact(StrideCategory.DENIAL_OF_SERVICE, "mitigate", "Per-user Limits Mitigate DoS", "Fair usage controls reduce attack surface.", ["Adaptive throttling"], 2.0)
        ],
    },
    "api_input_validation": {
        "No validation": [
            OptionImpact(StrideCategory.TAMPERING, "increase", "No Validation Enables Tampering", "Unvalidated inputs allow injection and data tampering.", ["Schema validation + sanitization"], 8.0)
        ],
        "Schema validation + sanitization": [
            OptionImpact(StrideCategory.TAMPERING, "mitigate", "Schema Validation Mitigates Tampering", "Contracts and sanitization prevent injections.", ["Centralize schemas"], 2.0)
        ],
    },
    "api_https_enforcement": {
        "HTTP only": [
            OptionImpact(StrideCategory.INFORMATION_DISCLOSURE, "increase", "Unencrypted API Traffic Exposes Data", "Plaintext transit leaks sensitive information.", ["Force HTTPS"], 7.0)
        ],
        "HTTPS only": [
            OptionImpact(StrideCategory.INFORMATION_DISCLOSURE, "mitigate", "HTTPS Everywhere Mitigates Disclosure", "TLS protects data in transit.", ["TLS hardening"], 2.0)
        ],
    },
    "api_authorization_model": {
        "No authorization": [
            OptionImpact(StrideCategory.ELEVATION_OF_PRIVILEGE, "increase", "No Authorization Enables Privilege Escalation", "Absence of authorization checks allows unrestricted actions.", ["Introduce RBAC with scopes"], 7.5)
        ],
        "Role-based with scopes": [
            OptionImpact(StrideCategory.ELEVATION_OF_PRIVILEGE, "mitigate", "RBAC + Scopes Mitigate Elevation", "Least privilege authorization reduces escalation paths.", ["Review scope granularity"], 2.0)
        ],
    },
}

DATABASE_MAPPINGS: Dict[str, Dict[str, List[OptionImpact]]] = {
    "database_authentication": {
        "No authentication": [
            OptionImpact(StrideCategory.SPOOFING, "increase", "No DB Auth Allows Spoofing", "Unauthenticated DB access enables identity spoofing and data theft.", ["Enforce auth with MFA"], 8.5)
        ],
        "Strong authentication with MFA": [
            OptionImpact(StrideCategory.SPOOFING, "mitigate", "Strong DB Auth Mitigates Spoofing", "Multi-factor DB auth resists credential abuse.", ["Centralize IAM"], 2.0)
        ],
    },
    "database_encryption_at_rest": {
        "No encryption": [
            OptionImpact(StrideCategory.INFORMATION_DISCLOSURE, "increase", "DB Data at Rest Exposed", "Plaintext storage risks large-scale disclosure.", ["Enable TDE"], 8.0)
        ],
        "Transparent Data Encryption (TDE)": [
            OptionImpact(StrideCategory.INFORMATION_DISCLOSURE, "mitigate", "TDE Mitigates Disclosure", "At-rest encryption protects stored data.", ["Key rotation"], 2.0)
        ],
    },
    "database_encryption_in_transit": {
        "Unencrypted connections": [
            OptionImpact(StrideCategory.INFORMATION_DISCLOSURE, "increase", "DB Traffic Exposed", "Unencrypted DB connections can be intercepted.", ["Enforce TLS"], 7.0)
        ],
        "SSL/TLS enforced": [
            OptionImpact(StrideCategory.INFORMATION_DISCLOSURE, "mitigate", "TLS Mitigates Disclosure", "Encrypted transport protects DB traffic.", ["TLS hardening"], 2.0)
        ],
    },
    "database_logging": {
        "No logging": [
            OptionImpact(StrideCategory.REPUDIATION, "increase", "No Audit Trail Enables Repudiation", "Lack of logs prevents accountability and forensic analysis.", ["Enable audit logging"], 6.0)
        ],
        "Comprehensive audit logging": [
            OptionImpact(StrideCategory.REPUDIATION, "mitigate", "Audit Logging Mitigates Repudiation", "Detailed logs support non-repudiation.", ["Centralize logs", "Retention policies"], 2.0)
        ],
    },
}

NODE_TYPE_TO_MAPPINGS = {
    "WebApp": WEBAPP_MAPPINGS,
    "API": API_MAPPINGS,
    "Database": DATABASE_MAPPINGS,
}

def map_responses_to_threats(node_subtype: str, responses: Dict[str, str], node_id: str, diagram_id: str) -> List[Threat]:
    """Translate questionnaire responses into STRIDE threats via mapping tables."""
    out: List[Threat] = []
    mapping = NODE_TYPE_TO_MAPPINGS.get(node_subtype)
    if not mapping:
        return out

    for qid, answer in responses.items():
        if qid not in mapping:
            continue
        # Normalize exact option strings
        option_impacts = mapping[qid].get(str(answer))
        if not option_impacts:
            continue
        for impact in option_impacts:
            status = ThreatStatus.OPEN if impact.effect == "increase" else ThreatStatus.MITIGATED
            out.append(
                Threat(
                    diagram_id=diagram_id,
                    element_type=ElementType.NODE,
                    element_id=node_id,
                    stride_category=impact.category,
                    title=impact.title,
                    description=impact.description,
                    mitigations=impact.mitigations,
                    residual_risk=impact.residual_risk,
                    status=status,
                )
            )
    return out