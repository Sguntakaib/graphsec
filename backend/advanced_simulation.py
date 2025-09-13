"""
Advanced Simulation Engine for Security Modeling Platform
Implements sophisticated attack path analysis using graph algorithms
"""

import networkx as nx
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)

class AttackComplexity(Enum):
    LOW = 1.0
    MEDIUM = 0.7
    HIGH = 0.4

class ImpactLevel(Enum):
    LOW = 1.0
    MEDIUM = 2.0
    HIGH = 3.0
    CRITICAL = 4.0

@dataclass
class AttackStep:
    source_node: str
    target_node: str
    technique: str
    complexity: AttackComplexity
    impact: ImpactLevel
    detection_likelihood: float
    mitre_id: str = ""
    description: str = ""

@dataclass
class AttackPath:
    steps: List[AttackStep]
    total_complexity: float
    total_impact: float
    detection_score: float
    likelihood: str
    risk_score: float
    mitre_techniques: List[str]

class AdvancedSimulationEngine:
    """
    Advanced simulation engine using graph theory and security intelligence
    """
    
    def __init__(self, nodes: Optional[List[Dict[str, Any]]] = None, edges: Optional[List[Dict[str, Any]]] = None):
        """
        Initialize simulation engine with optional nodes and edges
        
        Args:
            nodes: List of node dictionaries for the diagram
            edges: List of edge dictionaries for the diagram
        """
        self.graph = nx.DiGraph()
        self.mitre_database = self._load_mitre_techniques()
        self.cve_database = self._load_cve_data()
        
        # Initialize graph with provided nodes and edges
        if nodes and edges:
            self._build_graph(nodes, edges)
        
    def _load_mitre_techniques(self) -> Dict[str, Dict[str, Any]]:
        """Load MITRE ATT&CK technique database (simplified version)"""
        return {
            "T1190": {
                "name": "Exploit Public-Facing Application",
                "description": "Adversaries may attempt to take advantage of a weakness in an Internet-facing computer or program",
                "impact": "HIGH",
                "complexity": "MEDIUM",
                "detection_difficulty": 0.6,
                "platforms": ["Linux", "Windows", "macOS", "Network"]
            },
            "T1078": {
                "name": "Valid Accounts",
                "description": "Adversaries may obtain and abuse credentials of existing accounts",
                "impact": "HIGH", 
                "complexity": "LOW",
                "detection_difficulty": 0.8,
                "platforms": ["Linux", "Windows", "macOS", "SaaS", "Office 365", "Azure AD"]
            },
            "T1566": {
                "name": "Phishing",
                "description": "Adversaries may send phishing messages to gain access to victim systems",
                "impact": "MEDIUM",
                "complexity": "LOW",
                "detection_difficulty": 0.4,
                "platforms": ["Linux", "Windows", "macOS"]
            },
            "T1213": {
                "name": "Data from Information Repositories",
                "description": "Adversaries may leverage information repositories to mine valuable information",
                "impact": "HIGH",
                "complexity": "LOW",
                "detection_difficulty": 0.7,
                "platforms": ["Linux", "Windows", "macOS", "SaaS"]
            },
            "T1552.001": {
                "name": "Credentials In Files",
                "description": "Adversaries may search local file systems and remote file shares for files containing insecurely stored credentials",
                "impact": "HIGH",
                "complexity": "LOW", 
                "detection_difficulty": 0.6,
                "platforms": ["Linux", "Windows", "macOS"]
            },
            "T1484": {
                "name": "Domain Policy Modification",
                "description": "Adversaries may modify domain policy to maintain access and modify system configurations",
                "impact": "HIGH",
                "complexity": "MEDIUM",
                "detection_difficulty": 0.8,
                "platforms": ["Windows", "Azure AD", "Office 365"]
            },
            "T1059": {
                "name": "Command and Scripting Interpreter",
                "description": "Adversaries may abuse command and script interpreters to execute commands",
                "impact": "HIGH",
                "complexity": "LOW",
                "detection_difficulty": 0.5,
                "platforms": ["Linux", "Windows", "macOS"]
            }
        }
    
    def _load_cve_data(self) -> Dict[str, Dict[str, Any]]:
        """Load CVE database (simplified version)"""
        return {
            "CVE-2021-44228": {
                "name": "Log4j Remote Code Execution",
                "description": "Apache Log4j2 JNDI features do not protect against attacker controlled LDAP",
                "cvss_score": 10.0,
                "complexity": "LOW",
                "impact": "CRITICAL",
                "exploit_available": True
            },
            "CVE-2021-34527": {
                "name": "PrintNightmare",
                "description": "Windows Print Spooler Remote Code Execution Vulnerability",
                "cvss_score": 8.8,
                "complexity": "LOW", 
                "impact": "HIGH",
                "exploit_available": True
            }
        }
    
    def build_security_graph(self, nodes: List[Dict], edges: List[Dict]) -> nx.DiGraph:
        """Build NetworkX graph from security model nodes and edges"""
        self.graph.clear()
        
        # Add nodes with attributes
        for node in nodes:
            self.graph.add_node(
                node['id'],
                node_type=node.get('type', ''),
                subtype=node.get('subtype', ''),
                label=node.get('label', ''),
                data=node.get('data', {}),
                mitre_ids=node.get('mitre_ids', []),
                cve_ids=node.get('cve_ids', [])
            )
        
        # Add edges with weights based on attack complexity
        for edge in edges:
            weight = self._calculate_edge_weight(edge)
            self.graph.add_edge(
                edge['source'],
                edge['target'],
                weight=weight,
                edge_type=edge.get('type', 'default'),
                label=edge.get('label', ''),
                data=edge.get('data', {})
            )
        
        return self.graph
    
    def _calculate_edge_weight(self, edge: Dict) -> float:
        """Calculate edge weight based on attack complexity and likelihood"""
        base_weight = 1.0
        
        # Adjust weight based on edge data
        edge_data = edge.get('data', {})
        likelihood = edge_data.get('likelihood', 'Medium').lower()
        impact = edge_data.get('impact', 'Medium').lower()
        
        likelihood_weights = {'low': 0.3, 'medium': 0.6, 'high': 0.9}
        impact_weights = {'low': 0.25, 'medium': 0.5, 'high': 0.75, 'critical': 1.0}
        
        weight = base_weight * likelihood_weights.get(likelihood, 0.6) * impact_weights.get(impact, 0.5)
        return weight
    
    def find_attack_paths(self, max_paths: int = 10, max_length: int = 6) -> List[AttackPath]:
        """Find all possible attack paths using advanced graph algorithms"""
        attack_paths = []
        
        # Find all actor nodes (attack sources)
        actors = [n for n, d in self.graph.nodes(data=True) if d.get('node_type') == 'Actor']
        
        # Find all high-value asset nodes (attack targets)
        assets = [n for n, d in self.graph.nodes(data=True) 
                 if d.get('node_type') == 'Asset' and 
                 d.get('subtype') in ['Database', 'S3Bucket', 'API', 'IMDS']]
        
        logger.info(f"Found {len(actors)} actors and {len(assets)} critical assets")
        
        for actor in actors:
            for asset in assets:
                # Find multiple paths between actor and asset
                try:
                    if nx.has_path(self.graph, actor, asset):
                        # Get all simple paths (no cycles)
                        paths = list(nx.all_simple_paths(
                            self.graph, actor, asset, cutoff=max_length
                        ))
                        
                        # Sort paths by length and complexity
                        paths = sorted(paths, key=len)[:max_paths//2]
                        
                        for path in paths:
                            attack_path = self._analyze_attack_path(path)
                            if attack_path:
                                attack_paths.append(attack_path)
                                
                except nx.NetworkXNoPath:
                    continue
                except Exception as e:
                    logger.error(f"Error finding path from {actor} to {asset}: {e}")
                    continue
        
        # Sort paths by risk score and return top results
        attack_paths.sort(key=lambda x: x.risk_score, reverse=True)
        return attack_paths[:max_paths]
    
    def _analyze_attack_path(self, path: List[str]) -> Optional[AttackPath]:
        """Analyze a single attack path and calculate metrics"""
        if len(path) < 2:
            return None
            
        steps = []
        total_complexity = 0.0
        total_impact = 0.0
        detection_score = 0.0
        mitre_techniques = set()
        
        for i in range(len(path) - 1):
            source = path[i]
            target = path[i + 1]
            
            # Get node data
            source_data = self.graph.nodes[source]
            target_data = self.graph.nodes[target]
            edge_data = self.graph.edges[source, target]
            
            # Determine attack technique based on node types and MITRE IDs
            technique, mitre_id = self._determine_attack_technique(source_data, target_data)
            
            # Calculate step complexity and impact
            complexity = self._calculate_step_complexity(source_data, target_data, edge_data)
            impact = self._calculate_step_impact(target_data)
            detection_likelihood = self._calculate_detection_likelihood(technique, mitre_id)
            
            step = AttackStep(
                source_node=source_data.get('label', source),
                target_node=target_data.get('label', target),
                technique=technique,
                complexity=complexity,
                impact=impact,
                detection_likelihood=detection_likelihood,
                mitre_id=mitre_id,
                description=f"Attack from {source_data.get('label')} to {target_data.get('label')}"
            )
            
            steps.append(step)
            total_complexity += complexity.value
            total_impact += impact.value
            detection_score += detection_likelihood
            
            if mitre_id:
                mitre_techniques.add(mitre_id)
        
        # Calculate overall metrics
        avg_complexity = total_complexity / len(steps)
        avg_detection = detection_score / len(steps)
        
        # Calculate likelihood based on complexity
        if avg_complexity >= 0.8:
            likelihood = "High"
        elif avg_complexity >= 0.5:
            likelihood = "Medium"
        else:
            likelihood = "Low"
        
        # Calculate risk score (0-10 scale)
        risk_score = min((total_impact * (1 - avg_detection) * avg_complexity), 10.0)
        
        return AttackPath(
            steps=steps,
            total_complexity=avg_complexity,
            total_impact=total_impact,
            detection_score=avg_detection,
            likelihood=likelihood,
            risk_score=risk_score,
            mitre_techniques=list(mitre_techniques)
        )
    
    def _determine_attack_technique(self, source_data: Dict, target_data: Dict) -> Tuple[str, str]:
        """Determine the attack technique based on source and target node types"""
        source_type = source_data.get('node_type', '')
        target_type = target_data.get('node_type', '')
        target_subtype = target_data.get('subtype', '')
        
        # Check if target has specific MITRE techniques
        target_mitre = target_data.get('mitre_ids', [])
        if target_mitre:
            mitre_id = target_mitre[0]
            if mitre_id in self.mitre_database:
                return self.mitre_database[mitre_id]['name'], mitre_id
        
        # Default techniques based on node type combinations
        if source_type == 'Actor' and target_type == 'Surface':
            if target_subtype == 'SQLi':
                return "SQL Injection Attack", "T1190"
            elif target_subtype == 'SSRF':
                return "Server-Side Request Forgery", "T1190"
            elif target_subtype == 'WeakIAM':
                return "Abuse Valid Accounts", "T1078"
            else:
                return "Exploit Public Application", "T1190"
        
        elif target_type == 'Asset':
            if target_subtype == 'Database':
                return "Data Exfiltration", "T1213"
            elif target_subtype == 'IMDS':
                return "Instance Metadata Access", "T1552.001"
            else:
                return "Asset Compromise", "T1190"
        
        return "Generic Attack", ""
    
    def _calculate_step_complexity(self, source_data: Dict, target_data: Dict, edge_data: Dict) -> AttackComplexity:
        """Calculate attack step complexity"""
        # Base complexity from edge weight
        weight = edge_data.get('weight', 0.5)
        
        # Adjust based on target type
        target_type = target_data.get('subtype', '')
        
        high_complexity_targets = ['EDR', 'WAF', 'EgressProxy']
        medium_complexity_targets = ['IAMPolicy', 'NetworkACL', 'Database']
        
        if target_type in high_complexity_targets:
            return AttackComplexity.HIGH
        elif target_type in medium_complexity_targets:
            return AttackComplexity.MEDIUM
        elif weight > 0.7:
            return AttackComplexity.LOW
        elif weight > 0.4:
            return AttackComplexity.MEDIUM
        else:
            return AttackComplexity.HIGH
    
    def _calculate_step_impact(self, target_data: Dict) -> ImpactLevel:
        """Calculate impact level of compromising target"""
        target_type = target_data.get('node_type', '')
        target_subtype = target_data.get('subtype', '')
        
        critical_assets = ['Database', 'IMDS']
        high_assets = ['API', 'S3Bucket', 'WebApp']
        
        if target_type == 'Asset':
            if target_subtype in critical_assets:
                return ImpactLevel.CRITICAL
            elif target_subtype in high_assets:
                return ImpactLevel.HIGH
            else:
                return ImpactLevel.MEDIUM
        elif target_type == 'Surface':
            return ImpactLevel.HIGH
        else:
            return ImpactLevel.LOW
    
    def _calculate_detection_likelihood(self, technique: str, mitre_id: str) -> float:
        """Calculate likelihood of detection for this technique"""
        if mitre_id in self.mitre_database:
            return 1.0 - self.mitre_database[mitre_id].get('detection_difficulty', 0.5)
        return 0.5  # Default 50% detection likelihood
    
    def generate_recommendations(self, attack_paths: List[AttackPath], nodes: List[Dict]) -> List[str]:
        """Generate security recommendations based on attack paths"""
        recommendations = []
        
        # Analyze existing controls
        existing_controls = set()
        for node in nodes:
            if node.get('type') == 'Control':
                existing_controls.add(node.get('subtype', ''))
        
        # Count attack techniques
        technique_counts = {}
        for path in attack_paths:
            for technique in path.mitre_techniques:
                technique_counts[technique] = technique_counts.get(technique, 0) + 1
        
        # Generate recommendations based on common techniques
        for technique, count in sorted(technique_counts.items(), key=lambda x: x[1], reverse=True):
            if technique in self.mitre_database:
                tech_data = self.mitre_database[technique]
                
                if technique == "T1190" and "WAF" not in existing_controls:
                    recommendations.append(
                        "Deploy Web Application Firewall (WAF) to protect against exploitation of public-facing applications"
                    )
                elif technique == "T1078" and "IAMPolicy" not in existing_controls:
                    recommendations.append(
                        "Implement strong Identity and Access Management (IAM) policies with least privilege principle"
                    )
                elif technique == "T1213" and "EgressProxy" not in existing_controls:
                    recommendations.append(
                        "Configure egress proxy to monitor and control data exfiltration attempts"
                    )
                elif technique == "T1552.001":
                    recommendations.append(
                        "Secure cloud instance metadata service (IMDSv2) and implement network controls"
                    )
        
        # General recommendations based on attack path analysis
        if len(attack_paths) > 5:
            recommendations.append(
                "Consider network segmentation to reduce attack surface and limit lateral movement"
            )
        
        high_risk_paths = [p for p in attack_paths if p.risk_score > 7.0]
        if high_risk_paths:
            recommendations.append(
                f"Address {len(high_risk_paths)} high-risk attack paths by implementing additional controls"
            )
        
        return recommendations[:10]  # Return top 10 recommendations
    
    def calculate_overall_risk_score(self, attack_paths: List[AttackPath]) -> float:
        """Calculate overall security posture risk score"""
        if not attack_paths:
            return 2.0  # Low risk if no attack paths found
        
        # Calculate weighted average based on path likelihood and impact
        total_weighted_risk = 0.0
        total_weight = 0.0
        
        for path in attack_paths:
            # Weight by complexity (easier paths are more concerning)
            weight = 1.0 / path.total_complexity if path.total_complexity > 0 else 1.0
            total_weighted_risk += path.risk_score * weight
            total_weight += weight
        
        avg_risk = total_weighted_risk / total_weight if total_weight > 0 else 0.0
        
        # Apply modifier based on number of attack paths
        path_modifier = min(len(attack_paths) * 0.1, 2.0)
        
        return min(avg_risk + path_modifier, 10.0)