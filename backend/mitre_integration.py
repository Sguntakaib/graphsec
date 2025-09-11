"""
MITRE ATT&CK Integration Module
Provides comprehensive MITRE ATT&CK technique database and analysis
"""

import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class MitreTechnique:
    technique_id: str
    name: str
    description: str
    tactics: List[str]
    platforms: List[str]
    data_sources: List[str]
    detection_methods: List[str]
    mitigations: List[str]
    references: List[str]
    kill_chain_phases: List[str]
    impact_level: str
    complexity: str
    detection_difficulty: float

class MitreAttackDatabase:
    """Comprehensive MITRE ATT&CK technique database"""
    
    def __init__(self):
        self.techniques = self._load_techniques()
        self.tactics = self._load_tactics()
        self.mitigations = self._load_mitigations()
    
    def _load_techniques(self) -> Dict[str, MitreTechnique]:
        """Load comprehensive MITRE ATT&CK technique database"""
        return {
            "T1190": MitreTechnique(
                technique_id="T1190",
                name="Exploit Public-Facing Application",
                description="Adversaries may attempt to take advantage of a weakness in an Internet-facing computer or program using software, data, or commands in order to cause unintended or unanticipated behavior.",
                tactics=["Initial Access"],
                platforms=["Linux", "Windows", "macOS", "Network"],
                data_sources=["Application Log", "Network Traffic", "Web Application Firewall"],
                detection_methods=[
                    "Monitor for suspicious network traffic patterns",
                    "Analyze web application logs for exploitation attempts",
                    "Implement WAF rules to detect common attack patterns"
                ],
                mitigations=[
                    "Application Isolation and Sandboxing",
                    "Network Segmentation", 
                    "Privileged Process Integrity",
                    "Update Software",
                    "Vulnerability Scanning"
                ],
                references=[
                    "https://attack.mitre.org/techniques/T1190/",
                    "https://owasp.org/www-project-top-ten/"
                ],
                kill_chain_phases=["Exploitation"],
                impact_level="HIGH",
                complexity="MEDIUM",
                detection_difficulty=0.6
            ),
            
            "T1078": MitreTechnique(
                technique_id="T1078",
                name="Valid Accounts",
                description="Adversaries may obtain and abuse credentials of existing accounts as a means of gaining Initial Access, Persistence, Privilege Escalation, or Defense Evasion.",
                tactics=["Defense Evasion", "Persistence", "Privilege Escalation", "Initial Access"],
                platforms=["Linux", "Windows", "macOS", "SaaS", "Office 365", "Azure AD", "Google Workspace"],
                data_sources=["Authentication Logs", "Process Monitoring", "Account Usage"],
                detection_methods=[
                    "Monitor for unusual login patterns and locations",
                    "Implement behavioral analytics for user accounts",
                    "Track privileged account usage and access patterns"
                ],
                mitigations=[
                    "Multi-factor Authentication",
                    "Privileged Account Management",
                    "Account Use Policies",
                    "Password Policies"
                ],
                references=[
                    "https://attack.mitre.org/techniques/T1078/",
                    "https://docs.microsoft.com/en-us/azure/active-directory/identity-protection/"
                ],
                kill_chain_phases=["Exploitation", "Installation", "Command and Control"],
                impact_level="HIGH",
                complexity="LOW",
                detection_difficulty=0.8
            ),
            
            "T1566": MitreTechnique(
                technique_id="T1566",
                name="Phishing",
                description="Adversaries may send phishing messages to gain access to victim systems. All forms of phishing are electronically delivered social engineering attacks.",
                tactics=["Initial Access"],
                platforms=["Linux", "Windows", "macOS", "Office 365", "SaaS", "Google Workspace"],
                data_sources=["Email Gateway", "Network Traffic", "File Monitoring"],
                detection_methods=[
                    "Email security gateways with threat intelligence",
                    "User behavior analytics for suspicious link clicks",
                    "DNS monitoring for malicious domains"
                ],
                mitigations=[
                    "Antivirus/Antimalware",
                    "Network Intrusion Prevention",
                    "Restrict Web-Based Content",
                    "User Training"
                ],
                references=[
                    "https://attack.mitre.org/techniques/T1566/",
                    "https://www.anti-phishing.org/"
                ],
                kill_chain_phases=["Delivery", "Exploitation"],
                impact_level="MEDIUM",
                complexity="LOW",
                detection_difficulty=0.4
            ),
            
            "T1213": MitreTechnique(
                technique_id="T1213",
                name="Data from Information Repositories",
                description="Adversaries may leverage information repositories to mine valuable information. Information repositories are tools that allow for storage of information.",
                tactics=["Collection"],
                platforms=["Linux", "Windows", "macOS", "SaaS", "Office 365", "Google Workspace"],
                data_sources=["API Monitoring", "Data Loss Prevention", "Authentication Logs"],
                detection_methods=[
                    "Monitor for unusual API calls to data repositories",
                    "Implement data loss prevention (DLP) solutions",
                    "Track bulk data access patterns"
                ],
                mitigations=[
                    "Data Backup",
                    "Data Loss Prevention",
                    "Multi-factor Authentication",
                    "Remote Data Storage"
                ],
                references=[
                    "https://attack.mitre.org/techniques/T1213/",
                    "https://www.microsoft.com/en-us/security/business/threat-protection/data-loss-prevention"
                ],
                kill_chain_phases=["Actions on Objectives"],
                impact_level="HIGH",
                complexity="LOW",
                detection_difficulty=0.7
            ),
            
            "T1552.001": MitreTechnique(
                technique_id="T1552.001",
                name="Credentials In Files",
                description="Adversaries may search local file systems and remote file shares for files containing insecurely stored credentials.",
                tactics=["Credential Access"],
                platforms=["Linux", "Windows", "macOS"],
                data_sources=["File Monitoring", "Process Command-line Parameters"],
                detection_methods=[
                    "Monitor for access to credential files",
                    "Implement file integrity monitoring",
                    "Track unusual file system access patterns"
                ],
                mitigations=[
                    "Encrypt Sensitive Information",
                    "Password Policies",
                    "Privileged Process Integrity",
                    "Restrict File and Directory Permissions"
                ],
                references=[
                    "https://attack.mitre.org/techniques/T1552/001/",
                    "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-metadata.html"
                ],
                kill_chain_phases=["Credential Access"],
                impact_level="HIGH",
                complexity="LOW",
                detection_difficulty=0.6
            ),
            
            "T1484": MitreTechnique(
                technique_id="T1484",
                name="Domain Policy Modification",
                description="Adversaries may modify domain policy to maintain access and bypass defenses. Domain policy modification may include altering domain Group Policy Objects (GPOs).",
                tactics=["Defense Evasion", "Privilege Escalation"],
                platforms=["Windows", "Azure AD", "Office 365"],
                data_sources=["Windows Event Logs", "Azure AD Logs", "Process Monitoring"],
                detection_methods=[
                    "Monitor for changes to domain policies and GPOs",
                    "Implement privileged access monitoring",
                    "Track administrative account usage"
                ],
                mitigations=[
                    "Privileged Account Management",
                    "Audit",
                    "Multi-factor Authentication"
                ],
                references=[
                    "https://attack.mitre.org/techniques/T1484/",
                    "https://docs.microsoft.com/en-us/windows-server/identity/ad-ds/plan/security-best-practices/"
                ],
                kill_chain_phases=["Privilege Escalation", "Defense Evasion"],
                impact_level="HIGH",
                complexity="MEDIUM",
                detection_difficulty=0.8
            ),
            
            "T1059": MitreTechnique(
                technique_id="T1059",
                name="Command and Scripting Interpreter",
                description="Adversaries may abuse command and script interpreters to execute commands, scripts, or binaries.",
                tactics=["Execution"],
                platforms=["Linux", "Windows", "macOS"],
                data_sources=["Process Monitoring", "Command History", "PowerShell Logs"],
                detection_methods=[
                    "Monitor for suspicious command line execution",
                    "Implement script block logging",
                    "Analyze process creation events"
                ],
                mitigations=[
                    "Application Isolation and Sandboxing",
                    "Code Signing",
                    "Disable or Remove Feature or Program",
                    "Execution Prevention"
                ],
                references=[
                    "https://attack.mitre.org/techniques/T1059/",
                    "https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_logging"
                ],
                kill_chain_phases=["Execution"],
                impact_level="HIGH",
                complexity="LOW",
                detection_difficulty=0.5
            ),
            
            "T1021": MitreTechnique(
                technique_id="T1021",
                name="Remote Services",
                description="Adversaries may use Valid Accounts to log into a service specifically designed to accept remote connections.",
                tactics=["Lateral Movement"],
                platforms=["Linux", "Windows", "macOS"],
                data_sources=["Authentication Logs", "Network Connection Creation", "Process Monitoring"],
                detection_methods=[
                    "Monitor for unusual remote service connections",
                    "Track authentication events across systems",
                    "Implement network segmentation monitoring"
                ],
                mitigations=[
                    "Disable or Remove Feature or Program",
                    "Limit Access to Resource Over Network",
                    "Multi-factor Authentication",
                    "Network Segmentation"
                ],
                references=[
                    "https://attack.mitre.org/techniques/T1021/"
                ],
                kill_chain_phases=["Lateral Movement"],
                impact_level="MEDIUM",
                complexity="MEDIUM",
                detection_difficulty=0.6
            ),
            
            "T1003": MitreTechnique(
                technique_id="T1003",
                name="OS Credential Dumping",
                description="Adversaries may attempt to dump credentials to obtain account login and credential material.",
                tactics=["Credential Access"],
                platforms=["Linux", "Windows", "macOS"],
                data_sources=["Process Monitoring", "File Monitoring", "API Monitoring"],
                detection_methods=[
                    "Monitor for credential dumping tools",
                    "Implement endpoint detection and response",
                    "Track LSASS process access"
                ],
                mitigations=[
                    "Credential Access Protection",
                    "Operating System Configuration",
                    "Password Policies",
                    "Privileged Process Integrity"
                ],
                references=[
                    "https://attack.mitre.org/techniques/T1003/"
                ],
                kill_chain_phases=["Credential Access"],
                impact_level="HIGH",
                complexity="MEDIUM",
                detection_difficulty=0.7
            )
        }
    
    def _load_tactics(self) -> Dict[str, Dict[str, Any]]:
        """Load MITRE ATT&CK tactics"""
        return {
            "Initial Access": {
                "description": "The adversary is trying to get into your network.",
                "techniques_count": 9,
                "common_techniques": ["T1190", "T1566", "T1078"]
            },
            "Execution": {
                "description": "The adversary is trying to run malicious code.",
                "techniques_count": 12,
                "common_techniques": ["T1059", "T1053", "T1569"]
            },
            "Persistence": {
                "description": "The adversary is trying to maintain their foothold.",
                "techniques_count": 19,
                "common_techniques": ["T1078", "T1053", "T1543"]
            },
            "Privilege Escalation": {
                "description": "The adversary is trying to gain higher-level permissions.",
                "techniques_count": 13,
                "common_techniques": ["T1078", "T1055", "T1068"]
            },
            "Defense Evasion": {
                "description": "The adversary is trying to avoid being detected.",
                "techniques_count": 40,
                "common_techniques": ["T1078", "T1055", "T1027"]
            },
            "Credential Access": {
                "description": "The adversary is trying to steal account names and passwords.",
                "techniques_count": 15,
                "common_techniques": ["T1003", "T1552", "T1110"]
            },
            "Discovery": {
                "description": "The adversary is trying to figure out your environment.",
                "techniques_count": 29,
                "common_techniques": ["T1082", "T1016", "T1033"]
            },
            "Lateral Movement": {
                "description": "The adversary is trying to move through your environment.",
                "techniques_count": 9,
                "common_techniques": ["T1021", "T1080", "T1550"]
            },
            "Collection": {
                "description": "The adversary is trying to gather data of interest.",
                "techniques_count": 17,
                "common_techniques": ["T1213", "T1005", "T1039"]
            },
            "Command and Control": {
                "description": "The adversary is trying to communicate with compromised systems.",
                "techniques_count": 16,
                "common_techniques": ["T1071", "T1573", "T1090"]
            },
            "Exfiltration": {
                "description": "The adversary is trying to steal data.",
                "techniques_count": 9,
                "common_techniques": ["T1041", "T1048", "T1567"]
            },
            "Impact": {
                "description": "The adversary is trying to manipulate, interrupt, or destroy your systems and data.",
                "techniques_count": 13,
                "common_techniques": ["T1486", "T1490", "T1498"]
            }
        }
    
    def _load_mitigations(self) -> Dict[str, Dict[str, Any]]:
        """Load MITRE ATT&CK mitigations"""
        return {
            "M1047": {
                "name": "Audit",
                "description": "Perform audits or scans of systems, permissions, insecure software, insecure configurations, etc.",
                "applicable_techniques": ["T1078", "T1484"]
            },
            "M1015": {
                "name": "Active Directory Configuration",
                "description": "Configure Active Directory to prevent use of certain techniques.",
                "applicable_techniques": ["T1484", "T1078"]
            },
            "M1049": {
                "name": "Antivirus/Antimalware",
                "description": "Use signatures or heuristics to identify malicious software.",
                "applicable_techniques": ["T1566", "T1059"]
            },
            "M1013": {
                "name": "Application Developer Guidance",
                "description": "This mitigation describes any guidance or training given to developers of applications.",
                "applicable_techniques": ["T1190"]
            },
            "M1048": {
                "name": "Application Isolation and Sandboxing",
                "description": "Restrict execution of code to a virtual environment on or in transit to an endpoint system.",
                "applicable_techniques": ["T1190", "T1059"]
            },
            "M1036": {
                "name": "Account Use Policies",
                "description": "Configure features related to account use like account lockout policies.",
                "applicable_techniques": ["T1078"]
            },
            "M1017": {
                "name": "User Training",
                "description": "Train users to be aware of access or manipulation attempts by an adversary.",
                "applicable_techniques": ["T1566"]
            },
            "M1032": {
                "name": "Multi-factor Authentication",
                "description": "Use two or more pieces of evidence to authenticate to a system.",
                "applicable_techniques": ["T1078", "T1021", "T1213"]
            }
        }
    
    def get_technique(self, technique_id: str) -> Optional[MitreTechnique]:
        """Get detailed information about a specific technique"""
        return self.techniques.get(technique_id)
    
    def get_techniques_by_tactic(self, tactic: str) -> List[MitreTechnique]:
        """Get all techniques for a specific tactic"""
        return [tech for tech in self.techniques.values() if tactic in tech.tactics]
    
    def get_detection_methods(self, technique_id: str) -> List[str]:
        """Get detection methods for a specific technique"""
        technique = self.get_technique(technique_id)
        return technique.detection_methods if technique else []
    
    def get_mitigations(self, technique_id: str) -> List[str]:
        """Get mitigations for a specific technique"""
        technique = self.get_technique(technique_id)
        return technique.mitigations if technique else []
    
    def analyze_attack_coverage(self, attack_techniques: List[str]) -> Dict[str, Any]:
        """Analyze MITRE ATT&CK coverage of an attack scenario"""
        coverage = {
            "tactics_covered": set(),
            "techniques_analyzed": len(attack_techniques),
            "kill_chain_coverage": [],
            "detection_difficulty": 0.0,
            "recommended_mitigations": set(),
            "data_sources_needed": set()
        }
        
        total_difficulty = 0.0
        valid_techniques = 0
        
        for tech_id in attack_techniques:
            technique = self.get_technique(tech_id)
            if technique:
                coverage["tactics_covered"].update(technique.tactics)
                coverage["kill_chain_coverage"].extend(technique.kill_chain_phases)
                coverage["recommended_mitigations"].update(technique.mitigations)
                coverage["data_sources_needed"].update(technique.data_sources)
                total_difficulty += technique.detection_difficulty
                valid_techniques += 1
        
        if valid_techniques > 0:
            coverage["detection_difficulty"] = total_difficulty / valid_techniques
        
        # Convert sets to lists for JSON serialization
        coverage["tactics_covered"] = list(coverage["tactics_covered"])
        coverage["recommended_mitigations"] = list(coverage["recommended_mitigations"])
        coverage["data_sources_needed"] = list(coverage["data_sources_needed"])
        
        return coverage
    
    def suggest_additional_techniques(self, current_techniques: List[str], node_types: List[str]) -> List[str]:
        """Suggest additional techniques based on current attack path and node types"""
        suggestions = []
        
        # Map node types to likely additional techniques
        node_technique_map = {
            'Database': ['T1003', 'T1213'],
            'WebApp': ['T1190', 'T1059'],
            'API': ['T1190', 'T1213'],
            'S3Bucket': ['T1552.001', 'T1213'],
            'VM': ['T1021', 'T1003', 'T1059'],
            'IMDS': ['T1552.001']
        }
        
        for node_type in node_types:
            if node_type in node_technique_map:
                for technique in node_technique_map[node_type]:
                    if technique not in current_techniques and technique not in suggestions:
                        suggestions.append(technique)
        
        return suggestions[:5]  # Return top 5 suggestions