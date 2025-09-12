"""
THREAT INTELLIGENCE INTEGRATION - PHASE 1
Basic Threat Intelligence System for Security Modeling Platform

This module implements:
1. CVE database integration 
2. MITRE ATT&CK technique mapping
3. Basic threat feed processing
4. Vulnerability correlation
5. Real-time threat scoring
"""

import asyncio
import aiohttp
import logging
import json
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import re

logger = logging.getLogger(__name__)

class ThreatSeverity(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High" 
    MEDIUM = "Medium"
    LOW = "Low"
    INFO = "Info"

class ThreatCategory(str, Enum):
    VULNERABILITY = "Vulnerability"
    MALWARE = "Malware"
    APT = "APT"
    BOTNET = "Botnet"
    PHISHING = "Phishing"
    RANSOMWARE = "Ransomware"
    DATA_BREACH = "Data Breach"

@dataclass
class CVEIntelligence:
    """CVE vulnerability intelligence"""
    cve_id: str
    cvss_score: float
    severity: ThreatSeverity
    description: str
    published_date: str
    affected_products: List[str] = field(default_factory=list)
    attack_vector: str = ""
    attack_complexity: str = ""
    exploit_available: bool = False
    exploit_maturity: str = "Unknown"
    mitre_techniques: List[str] = field(default_factory=list)

@dataclass 
class ThreatIndicator:
    """General threat indicator"""
    indicator_id: str
    indicator_type: str  # IP, Domain, Hash, etc.
    value: str
    severity: ThreatSeverity
    category: ThreatCategory
    description: str
    first_seen: str
    last_seen: str
    confidence: float  # 0.0 - 1.0
    source: str
    tags: List[str] = field(default_factory=list)
    mitre_techniques: List[str] = field(default_factory=list)

@dataclass
class NodeThreatProfile:
    """Threat profile for a specific node type"""
    node_type: str
    total_cves: int
    recent_cves: List[CVEIntelligence]
    high_risk_cves: List[CVEIntelligence] 
    threat_indicators: List[ThreatIndicator]
    attack_patterns: List[str]
    mitre_techniques: Set[str]
    threat_score: float  # 0.0 - 10.0
    last_updated: str

class ThreatIntelligenceEngine:
    """Enhanced threat intelligence engine for security modeling"""
    
    def __init__(self):
        self.cve_cache = {}
        self.threat_cache = {}
        self.mitre_techniques_map = self._load_mitre_techniques()
        self.node_threat_profiles = {}
        
    def _load_mitre_techniques(self) -> Dict[str, Dict]:
        """Load MITRE ATT&CK techniques mapping"""
        # Basic MITRE techniques for phase 1
        # In production, this would load from MITRE ATT&CK dataset
        return {
            "T1078": {
                "name": "Valid Accounts",
                "tactic": "Initial Access",
                "description": "Adversaries may obtain and abuse credentials of existing accounts",
                "detection": "Monitor authentication logs for unusual activity"
            },
            "T1190": {
                "name": "Exploit Public-Facing Application",
                "tactic": "Initial Access", 
                "description": "Adversaries may attempt to take advantage of a weakness in an Internet-facing computer or program",
                "detection": "Monitor application logs for exploitation attempts"
            },
            "T1055": {
                "name": "Process Injection",
                "tactic": "Privilege Escalation",
                "description": "Adversaries may inject code into processes in order to evade process-based defenses",
                "detection": "Monitor process behavior and injection attempts"
            },
            "T1083": {
                "name": "File and Directory Discovery",
                "tactic": "Discovery",
                "description": "Adversaries may enumerate files and directories or may search in specific locations",
                "detection": "Monitor file system access patterns"
            },
            "T1110": {
                "name": "Brute Force",
                "tactic": "Credential Access",
                "description": "Adversaries may use brute force techniques to gain access to accounts",
                "detection": "Monitor for multiple failed authentication attempts"
            },
            "T1530": {
                "name": "Data from Cloud Storage Object",
                "tactic": "Collection",
                "description": "Adversaries may access data objects from improperly secured cloud storage",
                "detection": "Monitor cloud storage access logs"
            },
            "T1611": {
                "name": "Escape to Host",
                "tactic": "Privilege Escalation",
                "description": "Adversaries may break out of a container to gain access to the underlying host",
                "detection": "Monitor container runtime for escape attempts"
            },
            "T1068": {
                "name": "Exploitation for Privilege Escalation", 
                "tactic": "Privilege Escalation",
                "description": "Adversaries may exploit software vulnerabilities in an attempt to elevate privileges",
                "detection": "Monitor for unusual privilege escalation activity"
            },
            "T1610": {
                "name": "Deploy Container",
                "tactic": "Defense Evasion",
                "description": "Adversaries may deploy a container into an environment to facilitate execution",
                "detection": "Monitor container deployment and runtime activity"
            },
            "T1018": {
                "name": "Remote System Discovery", 
                "tactic": "Discovery",
                "description": "Adversaries may attempt to get a listing of other systems by IP address, hostname, or other logical identifier",
                "detection": "Monitor network discovery activities"
            }
        }
    
    async def get_node_threat_profile(self, node_type: str, force_refresh: bool = False) -> NodeThreatProfile:
        """Get comprehensive threat profile for a node type"""
        cache_key = f"threat_profile_{node_type}"
        
        # Check cache first
        if not force_refresh and cache_key in self.node_threat_profiles:
            cached_profile = self.node_threat_profiles[cache_key]
            # Check if cache is still fresh (1 hour)
            cache_time = datetime.fromisoformat(cached_profile.last_updated.replace('Z', '+00:00'))
            if datetime.now().timestamp() - cache_time.timestamp() < 3600:
                return cached_profile
        
        # Generate new threat profile
        profile = await self._generate_threat_profile(node_type)
        self.node_threat_profiles[cache_key] = profile
        return profile
    
    async def _generate_threat_profile(self, node_type: str) -> NodeThreatProfile:
        """Generate threat profile for specific node type"""
        
        # Map node types to CVE product names and categories
        node_cve_mapping = {
            "EC2": ["amazon_ec2", "aws_ec2", "amazon_linux", "ubuntu", "windows_server"],
            "Lambda": ["aws_lambda", "serverless", "python", "nodejs", "java"],
            "S3": ["amazon_s3", "aws_s3", "cloud_storage"],
            "RDS": ["amazon_rds", "mysql", "postgresql", "oracle", "mongodb"],
            "VPC": ["amazon_vpc", "aws_vpc", "networking"],
            "WAF": ["aws_waf", "web_application_firewall", "cloudflare"],
            "IAM": ["aws_iam", "identity_management", "authentication"],
            "Kubernetes": ["kubernetes", "k8s", "container", "docker"],
            "CICD": ["jenkins", "github_actions", "gitlab", "ci_cd"],
            "WebApp": ["web_application", "apache", "nginx", "tomcat"],
            "Database": ["database", "sql", "nosql", "mysql", "postgresql"],
            "API": ["api", "rest", "graphql", "web_service"]
        }
        
        # Get CVE data
        search_terms = node_cve_mapping.get(node_type, [node_type.lower()])
        cve_data = await self._fetch_cve_data(search_terms)
        
        # Get threat indicators
        threat_indicators = await self._fetch_threat_indicators(node_type)
        
        # Calculate threat score
        threat_score = self._calculate_threat_score(cve_data, threat_indicators)
        
        # Extract MITRE techniques
        mitre_techniques = set()
        for cve in cve_data["recent_cves"] + cve_data["high_risk_cves"]:
            mitre_techniques.update(cve.mitre_techniques)
        
        # Generate attack patterns
        attack_patterns = self._generate_attack_patterns(node_type, cve_data)
        
        return NodeThreatProfile(
            node_type=node_type,
            total_cves=cve_data["total_count"],
            recent_cves=cve_data["recent_cves"],
            high_risk_cves=cve_data["high_risk_cves"],
            threat_indicators=threat_indicators,
            attack_patterns=attack_patterns,
            mitre_techniques=mitre_techniques,
            threat_score=threat_score,
            last_updated=datetime.now().isoformat()
        )
    
    async def _fetch_cve_data(self, search_terms: List[str]) -> Dict[str, Any]:
        """Fetch CVE data for given search terms"""
        # Simulated CVE data for Phase 1
        # In production, this would query NIST NVD API or other CVE databases
        
        simulated_cves = self._generate_simulated_cves(search_terms)
        
        return {
            "total_count": len(simulated_cves),
            "recent_cves": [cve for cve in simulated_cves if self._is_recent_cve(cve)],
            "high_risk_cves": [cve for cve in simulated_cves if cve.cvss_score >= 7.0]
        }
    
    def _generate_simulated_cves(self, search_terms: List[str]) -> List[CVEIntelligence]:
        """Generate realistic simulated CVE data for demonstration"""
        cves = []
        
        # Base CVE templates for different node types
        cve_templates = {
            "ec2": [
                ("Remote Code Execution", 9.8, "Critical", "T1190"),
                ("Privilege Escalation", 7.8, "High", "T1068"),
                ("Information Disclosure", 6.5, "Medium", "T1083")
            ],
            "lambda": [
                ("Code Injection", 8.1, "High", "T1055"),
                ("Dependency Vulnerability", 7.5, "High", "T1190"),
                ("Information Leakage", 5.3, "Medium", "T1083")
            ],
            "s3": [
                ("Data Exposure", 7.5, "High", "T1530"),
                ("Access Control Bypass", 8.0, "High", "T1078"),
                ("Configuration Error", 6.0, "Medium", "T1083")
            ],
            "kubernetes": [
                ("Container Escape", 9.0, "Critical", "T1611"),
                ("Privilege Escalation", 8.5, "High", "T1068"),
                ("Resource Hijacking", 7.0, "High", "T1610")
            ]
        }
        
        # Generate CVEs based on search terms
        cve_counter = 1
        for term in search_terms[:3]:  # Limit to first 3 terms
            if term in cve_templates:
                templates = cve_templates[term]
            else:
                templates = [("Generic Vulnerability", 6.0, "Medium", "T1190")]
            
            for desc, score, severity, technique in templates:
                cve_id = f"CVE-2024-{10000 + cve_counter:05d}"
                cves.append(CVEIntelligence(
                    cve_id=cve_id,
                    cvss_score=score,
                    severity=ThreatSeverity(severity),
                    description=f"{desc} in {term}",
                    published_date=(datetime.now() - timedelta(days=cve_counter * 5)).isoformat(),
                    affected_products=[term],
                    attack_vector="Network" if score > 7.0 else "Local",
                    attack_complexity="Low" if score > 8.0 else "High",
                    exploit_available=score > 7.5,
                    exploit_maturity="Functional" if score > 8.0 else "Proof-of-Concept",
                    mitre_techniques=[technique]
                ))
                cve_counter += 1
        
        return cves
    
    def _is_recent_cve(self, cve: CVEIntelligence, days: int = 90) -> bool:
        """Check if CVE is recent (within specified days)"""
        try:
            cve_date = datetime.fromisoformat(cve.published_date.replace('Z', '+00:00'))
            cutoff_date = datetime.now() - timedelta(days=days)
            return cve_date >= cutoff_date
        except:
            return False
    
    async def _fetch_threat_indicators(self, node_type: str) -> List[ThreatIndicator]:
        """Fetch threat indicators for node type"""
        # Simulated threat indicators for Phase 1
        indicators = []
        
        indicator_templates = {
            "EC2": [
                ("Cryptomining Malware", "High", "Malware"),
                ("SSH Brute Force", "Medium", "APT"),
                ("Privilege Escalation Tools", "High", "APT")
            ],
            "Lambda": [
                ("Malicious Dependencies", "Medium", "Malware"),
                ("Code Injection Attempts", "High", "APT")
            ],
            "S3": [
                ("Data Exfiltration Tools", "High", "Data Breach"),
                ("Bucket Enumeration", "Medium", "APT")
            ],
            "Kubernetes": [
                ("Container Escape Exploits", "Critical", "APT"),
                ("Resource Hijacking", "High", "Malware")
            ]
        }
        
        templates = indicator_templates.get(node_type, [("Generic Threat", "Medium", "APT")])
        
        for i, (desc, severity, category) in enumerate(templates):
            indicators.append(ThreatIndicator(
                indicator_id=f"TI-{node_type}-{i+1:03d}",
                indicator_type="Behavior",
                value=desc,
                severity=ThreatSeverity(severity),
                category=ThreatCategory(category),
                description=f"{desc} targeting {node_type} components",
                first_seen=(datetime.now() - timedelta(days=30)).isoformat(),
                last_seen=datetime.now().isoformat(),
                confidence=0.8,
                source="Threat Intelligence Feed",
                tags=[node_type.lower(), category.lower()],
                mitre_techniques=["T1190", "T1078"]
            ))
        
        return indicators
    
    def _calculate_threat_score(self, cve_data: Dict, threat_indicators: List[ThreatIndicator]) -> float:
        """Calculate overall threat score for node type"""
        score = 0.0
        
        # CVE-based scoring
        high_risk_count = len(cve_data["high_risk_cves"])
        recent_count = len(cve_data["recent_cves"])
        total_count = cve_data["total_count"]
        
        # Base score from CVE volume
        cve_score = min(5.0, total_count / 20.0)  # Max 5.0 from volume
        
        # High-risk CVE bonus
        if high_risk_count > 0:
            cve_score += min(3.0, high_risk_count * 0.5)
        
        # Recent CVE bonus
        if recent_count > 0:
            cve_score += min(2.0, recent_count * 0.3)
        
        score += cve_score
        
        # Threat indicator scoring
        for indicator in threat_indicators:
            if indicator.severity == ThreatSeverity.CRITICAL:
                score += 1.5
            elif indicator.severity == ThreatSeverity.HIGH:
                score += 1.0
            elif indicator.severity == ThreatSeverity.MEDIUM:
                score += 0.5
        
        return min(10.0, score)
    
    def _generate_attack_patterns(self, node_type: str, cve_data: Dict) -> List[str]:
        """Generate common attack patterns for node type"""
        patterns = []
        
        pattern_mapping = {
            "EC2": [
                "SSH Brute Force → Privilege Escalation → Lateral Movement",
                "Web Shell Upload → Remote Code Execution → Data Exfiltration",
                "Vulnerability Exploitation → Container Escape → Host Compromise"
            ],
            "Lambda": [
                "Malicious Dependency → Code Injection → Privilege Escalation",
                "Event Manipulation → Function Abuse → Data Access",
                "Cold Start Exploit → Memory Corruption → Code Execution"
            ],
            "S3": [
                "Misconfiguration Discovery → Data Enumeration → Mass Download",
                "Credential Theft → API Abuse → Data Exfiltration",
                "Privilege Escalation → Bucket Takeover → Ransomware"
            ],
            "Kubernetes": [
                "Pod Compromise → Container Escape → Node Takeover",
                "RBAC Bypass → Privilege Escalation → Cluster Admin",
                "Supply Chain Attack → Malicious Image → Runtime Exploit"
            ]
        }
        
        # Get patterns for node type or generic patterns
        base_patterns = pattern_mapping.get(node_type, [
            "Initial Access → Privilege Escalation → Persistence",
            "Vulnerability Exploitation → Lateral Movement → Exfiltration"
        ])
        
        # Add CVE-specific patterns
        for cve in cve_data["high_risk_cves"][:3]:  # Top 3 high-risk CVEs
            if cve.cvss_score >= 9.0:
                patterns.append(f"Exploit {cve.cve_id} → {cve.description}")
        
        return base_patterns + patterns
    
    async def correlate_vulnerabilities(self, node_configs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Correlate vulnerabilities across multiple nodes"""
        correlations = []
        overall_risk = 0.0
        
        for config in node_configs:
            node_type = config.get("node_type", "Unknown")
            profile = await self.get_node_threat_profile(node_type)
            
            # Look for correlation patterns
            for other_config in node_configs:
                if other_config == config:
                    continue
                
                other_type = other_config.get("node_type", "Unknown")
                other_profile = await self.get_node_threat_profile(other_type)
                
                # Check for common MITRE techniques
                common_techniques = profile.mitre_techniques.intersection(other_profile.mitre_techniques)
                if len(common_techniques) >= 2:
                    correlations.append({
                        "node_types": [node_type, other_type],
                        "common_techniques": list(common_techniques),
                        "risk_amplification": len(common_techniques) * 0.5,
                        "description": f"Shared attack techniques between {node_type} and {other_type}"
                    })
            
            overall_risk += profile.threat_score
        
        return {
            "correlations": correlations,
            "overall_risk_score": round(overall_risk / max(len(node_configs), 1), 2),
            "total_nodes_analyzed": len(node_configs),
            "correlation_count": len(correlations),
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def get_mitre_technique_details(self, technique_id: str) -> Optional[Dict[str, Any]]:
        """Get details for a specific MITRE ATT&CK technique"""
        return self.mitre_techniques_map.get(technique_id)
    
    async def get_real_time_threat_score(self, node_type: str, configuration: Dict[str, Any]) -> float:
        """Calculate real-time threat score based on current configuration"""
        profile = await self.get_node_threat_profile(node_type)
        base_score = profile.threat_score
        
        # Adjust score based on configuration
        config_modifiers = {
            "public_access": 2.0,
            "weak_authentication": 1.5,
            "no_encryption": 1.0,
            "outdated_version": 1.5,
            "default_credentials": 3.0,
            "no_monitoring": 0.5
        }
        
        for factor, modifier in config_modifiers.items():
            if configuration.get(factor, False):
                base_score += modifier
        
        # Apply positive controls
        positive_controls = {
            "mfa_enabled": -1.0,
            "encryption_enabled": -0.5,
            "monitoring_enabled": -0.5,
            "regular_updates": -1.0,
            "network_segmentation": -0.5
        }
        
        for control, modifier in positive_controls.items():
            if configuration.get(control, False):
                base_score += modifier
        
        return max(0.0, min(10.0, base_score))

# Global threat intelligence engine instance
threat_intelligence_engine = ThreatIntelligenceEngine()