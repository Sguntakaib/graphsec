"""
Probabilistic Simulation Engine for Security Modeling Platform
Phase 3: Advanced Intelligence - Probabilistic Attack Path Analysis

This module implements:
1. Weighted Attack Path Analysis with probabilistic graph traversal
2. Dynamic Risk Calculation with real-time updates
3. What-If Scenario Engine with control toggles
4. Multi-Step Attack Chains and Defense Effectiveness Modeling
"""

import math
import random
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import networkx as nx
import numpy as np
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class AttackComplexity(str, Enum):
    VERY_LOW = "Very Low"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    VERY_HIGH = "Very High"


class ControlEffectiveness(str, Enum):
    MINIMAL = "Minimal"
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"
    MAXIMUM = "Maximum"


@dataclass
class ProbabilisticEdge:
    """Edge with probabilistic weights"""
    source: str
    target: str
    base_probability: float  # 0.0 to 1.0
    vulnerability_score: float  # CVSS or custom score
    control_coverage: float  # 0.0 to 1.0 (effectiveness of controls)
    attack_complexity: AttackComplexity
    detection_likelihood: float  # 0.0 to 1.0
    success_probability: float = 0.0  # Calculated: vulnerability * (1 - control_coverage)
    
    def __post_init__(self):
        """Calculate success probability based on vulnerability and control coverage"""
        # Base formula: P(success) = Vulnerability × (1 - ControlCoverage) × ComplexityFactor
        complexity_factor = {
            AttackComplexity.VERY_LOW: 1.0,
            AttackComplexity.LOW: 0.8,
            AttackComplexity.MEDIUM: 0.6,
            AttackComplexity.HIGH: 0.4,
            AttackComplexity.VERY_HIGH: 0.2
        }
        
        factor = complexity_factor.get(self.attack_complexity, 0.6)
        self.success_probability = min(
            self.vulnerability_score * (1 - self.control_coverage) * factor,
            1.0
        )


@dataclass
class ProbabilisticAttackPath:
    """Attack path with probabilistic analysis"""
    path_id: str
    steps: List[str]  # Node IDs in attack sequence
    overall_probability: float  # Combined probability of success
    risk_score: float  # Probability × Impact
    impact_score: float  # Business impact if attack succeeds
    detection_score: float  # Probability of being detected
    kill_chain_stages: List[str]  # MITRE kill chain stages
    mitre_techniques: List[str]
    time_to_compromise: float  # Estimated time in hours
    defense_bypassed: List[str]  # Controls that would be bypassed
    uncertainty_band: Tuple[float, float]  # (min_probability, max_probability)


@dataclass
class ScenarioAnalysis:
    """What-if scenario analysis result"""
    scenario_id: str
    scenario_name: str
    modified_controls: Dict[str, bool]  # Control ID -> enabled/disabled
    original_risk_score: float
    modified_risk_score: float
    risk_change: float  # Positive = increased risk, negative = reduced risk
    affected_paths: List[str]  # Path IDs affected by changes
    recommendations: List[str]
    roi_analysis: Dict[str, float]  # Cost-benefit analysis


@dataclass
class DefenseEffectivenessModel:
    """Model for analyzing defense effectiveness"""
    control_id: str
    control_type: str
    effectiveness_rating: float  # 0.0 to 1.0
    coverage_areas: List[str]  # Attack techniques it covers
    interaction_effects: Dict[str, float]  # How it interacts with other controls
    degradation_over_time: float  # How effectiveness decreases without maintenance
    false_positive_rate: float
    false_negative_rate: float


class ProbabilisticSimulationEngine:
    """Advanced probabilistic simulation engine"""
    
    def __init__(self):
        self.security_graph = nx.DiGraph()
        self.probabilistic_edges: Dict[str, ProbabilisticEdge] = {}
        self.defense_models: Dict[str, DefenseEffectivenessModel] = {}
        self.kill_chain_mapping = self._initialize_kill_chain_mapping()
        
    def _initialize_kill_chain_mapping(self) -> Dict[str, List[str]]:
        """Initialize MITRE kill chain stage mapping"""
        return {
            "reconnaissance": ["T1595", "T1590", "T1589"],
            "weaponization": ["T1588", "T1587"],
            "delivery": ["T1566", "T1190", "T1200"],
            "exploitation": ["T1190", "T1203", "T1068"],
            "installation": ["T1547", "T1543", "T1574"],
            "command_control": ["T1071", "T1090", "T1573"],
            "actions_objectives": ["T1213", "T1005", "T1041", "T1486"]
        }
        
    def build_probabilistic_graph(self, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]):
        """Build probabilistic security graph with weighted edges"""
        self.security_graph.clear()
        self.probabilistic_edges.clear()
        
        # Add nodes with enhanced attributes
        for node in nodes:
            enhanced_attrs = self._enhance_node_attributes(node)
            self.security_graph.add_node(node["id"], **enhanced_attrs)
        
        # Add probabilistic edges
        for edge in edges:
            prob_edge = self._create_probabilistic_edge(edge, nodes)
            edge_id = f"{edge['source']}-{edge['target']}"
            self.probabilistic_edges[edge_id] = prob_edge
            
            # Add to NetworkX graph with probabilistic weights
            self.security_graph.add_edge(
                edge["source"],
                edge["target"],
                weight=prob_edge.success_probability,
                prob_edge=prob_edge,
                **edge
            )
    
    def _enhance_node_attributes(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance node attributes for probabilistic analysis"""
        enhanced = node.copy()
        
        # Add probabilistic attributes based on node type
        if node.get("type") == "Asset":
            enhanced["impact_multiplier"] = self._calculate_impact_multiplier(node)
            enhanced["attack_surface"] = self._calculate_attack_surface(node)
            
        elif node.get("type") == "Control":
            enhanced["effectiveness_score"] = self._calculate_control_effectiveness(node)
            enhanced["coverage_scope"] = self._determine_coverage_scope(node)
            
        elif node.get("type") == "Surface":
            enhanced["exploitability_score"] = self._calculate_exploitability(node)
            enhanced["prevalence"] = self._calculate_vulnerability_prevalence(node)
            
        return enhanced
    
    def _calculate_impact_multiplier(self, asset_node: Dict[str, Any]) -> float:
        """Calculate impact multiplier based on asset criticality"""
        criticality_map = {
            "Critical": 1.0,
            "High": 0.8,
            "Medium": 0.5,
            "Low": 0.2
        }
        return criticality_map.get(asset_node.get("criticality", "Medium"), 0.5)
    
    def _calculate_attack_surface(self, asset_node: Dict[str, Any]) -> float:
        """Calculate attack surface score"""
        base_surface = 0.5
        
        # Increase surface for public-facing assets
        if asset_node.get("public_access", False):
            base_surface += 0.3
            
        # Increase based on complexity
        subtype = asset_node.get("subtype", "")
        complexity_bonus = {
            "WebApp": 0.2,
            "API": 0.3,
            "Database": 0.1,
            "S3Bucket": 0.15
        }
        
        return min(base_surface + complexity_bonus.get(subtype, 0), 1.0)
    
    def _calculate_control_effectiveness(self, control_node: Dict[str, Any]) -> float:
        """Calculate control effectiveness score"""
        # Use existing effectiveness or calculate based on type
        existing_eff = control_node.get("effectiveness", 75)
        return min(existing_eff / 100.0, 1.0)
    
    def _determine_coverage_scope(self, control_node: Dict[str, Any]) -> List[str]:
        """Determine what attack techniques a control covers"""
        control_coverage = {
            "WAF": ["T1190", "T1499", "T1078"],
            "EDR": ["T1059", "T1055", "T1543"],
            "IAMPolicy": ["T1078", "T1110", "T1550"],
            "NetworkACL": ["T1021", "T1090", "T1573"],
            "EgressProxy": ["T1041", "T1071", "T1105"]
        }
        
        subtype = control_node.get("subtype", "")
        return control_coverage.get(subtype, [])
    
    def _calculate_exploitability(self, surface_node: Dict[str, Any]) -> float:
        """Calculate exploitability score for attack surface"""
        cvss_score = surface_node.get("cvss_score", 5.0)
        return min(cvss_score / 10.0, 1.0)
    
    def _calculate_vulnerability_prevalence(self, surface_node: Dict[str, Any]) -> float:
        """Calculate how common this vulnerability type is"""
        prevalence_map = {
            "SQLi": 0.8,
            "XSS": 0.7,
            "SSRF": 0.4,
            "RCE": 0.6,
            "IDOR": 0.5,
            "WeakIAM": 0.9
        }
        
        subtype = surface_node.get("subtype", "")
        return prevalence_map.get(subtype, 0.5)
    
    def _create_probabilistic_edge(self, edge: Dict[str, Any], nodes: List[Dict[str, Any]]) -> ProbabilisticEdge:
        """Create probabilistic edge with calculated weights"""
        source_node = next((n for n in nodes if n["id"] == edge["source"]), {})
        target_node = next((n for n in nodes if n["id"] == edge["target"]), {})
        
        # Calculate base probability based on node types and connection
        base_prob = self._calculate_base_probability(source_node, target_node, edge)
        
        # Calculate vulnerability score
        vuln_score = self._calculate_edge_vulnerability(source_node, target_node)
        
        # Calculate control coverage for this edge
        control_coverage = self._calculate_edge_control_coverage(edge, nodes)
        
        # Determine attack complexity
        complexity = self._determine_attack_complexity(source_node, target_node)
        
        # Calculate detection likelihood
        detection_likelihood = self._calculate_detection_likelihood(source_node, target_node, nodes)
        
        return ProbabilisticEdge(
            source=edge["source"],
            target=edge["target"],
            base_probability=base_prob,
            vulnerability_score=vuln_score,
            control_coverage=control_coverage,
            attack_complexity=complexity,
            detection_likelihood=detection_likelihood
        )
    
    def _calculate_base_probability(self, source: Dict, target: Dict, edge: Dict) -> float:
        """Calculate base probability for edge traversal"""
        source_type = source.get("type", "")
        target_type = target.get("type", "")
        
        # Base probabilities for different attack patterns
        if source_type == "Actor" and target_type == "Asset":
            return 0.3  # Direct attack on asset
        elif source_type == "Actor" and target_type == "Surface":
            return 0.7  # Attacker exploiting vulnerability
        elif source_type == "Surface" and target_type == "Asset":
            return 0.8  # Vulnerability leading to asset compromise
        elif source_type == "Control" and target_type == "Asset":
            return 0.1  # Control should protect, not attack
        else:
            return 0.4  # Default probability
    
    def _calculate_edge_vulnerability(self, source: Dict, target: Dict) -> float:
        """Calculate vulnerability score for edge"""
        # If target is a surface, use its exploitability
        if target.get("type") == "Surface":
            return target.get("exploitability_score", 0.5)
        
        # If source is surface, use its score
        if source.get("type") == "Surface":
            return source.get("exploitability_score", 0.5)
        
        # For asset nodes, use attack surface
        if target.get("type") == "Asset":
            return target.get("attack_surface", 0.5)
        
        return 0.4  # Default
    
    def _calculate_edge_control_coverage(self, edge: Dict, nodes: List[Dict]) -> float:
        """Calculate control coverage affecting this edge"""
        source_id = edge["source"]
        target_id = edge["target"]
        
        # Find control nodes that might affect this edge
        relevant_controls = []
        for node in nodes:
            if node.get("type") == "Control":
                # Check if control is connected to source or target
                if self._is_control_relevant(node, source_id, target_id, nodes):
                    effectiveness = node.get("effectiveness_score", 0.5)
                    relevant_controls.append(effectiveness)
        
        if not relevant_controls:
            return 0.0  # No control coverage
        
        # Combine control effectiveness (defense in depth)
        combined_effectiveness = 1.0
        for effectiveness in relevant_controls:
            combined_effectiveness *= (1.0 - effectiveness)
        
        return 1.0 - combined_effectiveness
    
    def _is_control_relevant(self, control: Dict, source_id: str, target_id: str, nodes: List[Dict]) -> bool:
        """Check if a control is relevant to an attack edge"""
        # Simplified: assume control is relevant if it's connected to either source or target
        # In real implementation, would check network topology and control scope
        return True  # For now, assume all controls provide some coverage
    
    def _determine_attack_complexity(self, source: Dict, target: Dict) -> AttackComplexity:
        """Determine attack complexity based on source and target"""
        source_type = source.get("type")
        target_type = target.get("type")
        
        # Simple heuristics - in practice would be more sophisticated
        if source_type == "Actor" and target_type == "Surface":
            if target.get("subtype") in ["SQLi", "XSS"]:
                return AttackComplexity.LOW
            elif target.get("subtype") in ["RCE", "SSRF"]:
                return AttackComplexity.MEDIUM
            else:
                return AttackComplexity.HIGH
        
        return AttackComplexity.MEDIUM
    
    def _calculate_detection_likelihood(self, source: Dict, target: Dict, nodes: List[Dict]) -> float:
        """Calculate likelihood of detecting this attack step"""
        # Check for detection controls (EDR, SIEM, etc.)
        detection_controls = [n for n in nodes if n.get("type") == "Control" and 
                            n.get("subtype") in ["EDR", "SIEM", "IDS"]]
        
        if not detection_controls:
            return 0.2  # Low detection without proper controls
        
        # Combine detection capabilities
        combined_detection = 1.0
        for control in detection_controls:
            effectiveness = control.get("effectiveness_score", 0.5)
            combined_detection *= (1.0 - effectiveness * 0.8)  # Detection is harder than prevention
        
        return 1.0 - combined_detection
    
    def find_probabilistic_attack_paths(self, max_paths: int = 10, max_length: int = 6) -> List[ProbabilisticAttackPath]:
        """Find attack paths using probabilistic analysis"""
        attack_paths = []
        
        # Find all actor nodes (attack sources)
        actor_nodes = [n for n, attrs in self.security_graph.nodes(data=True) 
                      if attrs.get("type") == "Actor"]
        
        # Find all asset nodes (attack targets)
        asset_nodes = [n for n, attrs in self.security_graph.nodes(data=True) 
                      if attrs.get("type") == "Asset"]
        
        path_counter = 0
        for actor in actor_nodes:
            for asset in asset_nodes:
                if path_counter >= max_paths:
                    break
                
                # Find probabilistic paths between actor and asset
                try:
                    paths = list(nx.all_simple_paths(self.security_graph, actor, asset, cutoff=max_length))
                    
                    for path in paths[:3]:  # Limit paths per actor-asset pair
                        if path_counter >= max_paths:
                            break
                        
                        prob_path = self._analyze_probabilistic_path(path)
                        if prob_path and prob_path.overall_probability > 0.1:  # Filter low-probability paths
                            attack_paths.append(prob_path)
                            path_counter += 1
                
                except nx.NetworkXNoPath:
                    continue
        
        # Sort by risk score (probability × impact)
        attack_paths.sort(key=lambda p: p.risk_score, reverse=True)
        return attack_paths[:max_paths]
    
    def _analyze_probabilistic_path(self, node_path: List[str]) -> Optional[ProbabilisticAttackPath]:
        """Analyze a single attack path probabilistically"""
        if len(node_path) < 2:
            return None
        
        # Calculate overall probability (product of edge probabilities)
        overall_probability = 1.0
        detection_probabilities = []
        mitre_techniques = []
        defense_bypassed = []
        
        for i in range(len(node_path) - 1):
            source = node_path[i]
            target = node_path[i + 1]
            edge_id = f"{source}-{target}"
            
            if edge_id in self.probabilistic_edges:
                prob_edge = self.probabilistic_edges[edge_id]
                overall_probability *= prob_edge.success_probability
                detection_probabilities.append(prob_edge.detection_likelihood)
                
                # Add MITRE techniques based on edge type
                techniques = self._get_edge_mitre_techniques(source, target)
                mitre_techniques.extend(techniques)
        
        # Calculate combined detection score
        detection_score = 1.0 - np.prod([1.0 - p for p in detection_probabilities])
        
        # Calculate impact score based on target asset
        target_node = self.security_graph.nodes[node_path[-1]]
        impact_score = target_node.get("impact_multiplier", 0.5)
        
        # Calculate risk score
        risk_score = overall_probability * impact_score * 10  # Scale to 0-10
        
        # Estimate time to compromise
        time_to_compromise = len(node_path) * 2.5  # Rough estimate in hours
        
        # Calculate uncertainty band
        uncertainty = overall_probability * 0.2  # 20% uncertainty
        uncertainty_band = (
            max(0, overall_probability - uncertainty),
            min(1, overall_probability + uncertainty)
        )
        
        # Map to kill chain stages
        kill_chain_stages = self._map_to_kill_chain(mitre_techniques)
        
        return ProbabilisticAttackPath(
            path_id=f"path-{'-'.join(node_path)}",
            steps=node_path,
            overall_probability=overall_probability,
            risk_score=risk_score,
            impact_score=impact_score,
            detection_score=detection_score,
            kill_chain_stages=kill_chain_stages,
            mitre_techniques=list(set(mitre_techniques)),
            time_to_compromise=time_to_compromise,
            defense_bypassed=defense_bypassed,
            uncertainty_band=uncertainty_band
        )
    
    def _get_edge_mitre_techniques(self, source_id: str, target_id: str) -> List[str]:
        """Get MITRE techniques for an attack edge"""
        source_attrs = self.security_graph.nodes[source_id]
        target_attrs = self.security_graph.nodes[target_id]
        
        # Map node types and subtypes to MITRE techniques
        technique_mapping = {
            ("Actor", "Surface"): ["T1190", "T1078"],
            ("Surface", "Asset"): ["T1213", "T1005"],
            ("Actor", "Asset"): ["T1078", "T1213"]
        }
        
        source_type = source_attrs.get("type")
        target_type = target_attrs.get("type")
        
        return technique_mapping.get((source_type, target_type), ["T1027"])
    
    def _map_to_kill_chain(self, techniques: List[str]) -> List[str]:
        """Map MITRE techniques to kill chain stages"""
        stages = set()
        
        for technique in techniques:
            for stage, stage_techniques in self.kill_chain_mapping.items():
                if technique in stage_techniques:
                    stages.add(stage)
        
        return sorted(list(stages))
    
    def run_what_if_scenario(self, control_changes: Dict[str, bool], 
                           original_paths: List[ProbabilisticAttackPath]) -> ScenarioAnalysis:
        """Run what-if scenario by toggling controls"""
        scenario_id = f"scenario-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Calculate original risk score
        original_risk = sum(path.risk_score for path in original_paths)
        
        # Temporarily modify graph based on control changes
        modified_edges = self._apply_control_changes(control_changes)
        
        # Recalculate attack paths
        modified_paths = self.find_probabilistic_attack_paths()
        modified_risk = sum(path.risk_score for path in modified_paths)
        
        # Restore original edges
        self._restore_edges(modified_edges)
        
        # Analyze changes
        risk_change = modified_risk - original_risk
        affected_paths = [path.path_id for path in modified_paths 
                         if path.path_id not in [p.path_id for p in original_paths]]
        
        # Generate recommendations
        recommendations = self._generate_scenario_recommendations(control_changes, risk_change)
        
        # Simple ROI analysis
        roi_analysis = self._calculate_roi_analysis(control_changes, risk_change)
        
        return ScenarioAnalysis(
            scenario_id=scenario_id,
            scenario_name=f"Modified {len(control_changes)} controls",
            modified_controls=control_changes,
            original_risk_score=original_risk,
            modified_risk_score=modified_risk,
            risk_change=risk_change,
            affected_paths=affected_paths,
            recommendations=recommendations,
            roi_analysis=roi_analysis
        )
    
    def _apply_control_changes(self, control_changes: Dict[str, bool]) -> Dict[str, ProbabilisticEdge]:
        """Apply control changes to the graph and return modified edges"""
        modified_edges = {}
        
        for control_id, enabled in control_changes.items():
            # Find edges affected by this control
            for edge_id, prob_edge in self.probabilistic_edges.items():
                if self._control_affects_edge(control_id, edge_id):
                    # Store original edge
                    modified_edges[edge_id] = prob_edge
                    
                    # Modify control coverage
                    if enabled:
                        # Control is enabled - increase coverage
                        prob_edge.control_coverage = min(prob_edge.control_coverage + 0.3, 1.0)
                    else:
                        # Control is disabled - decrease coverage
                        prob_edge.control_coverage = max(prob_edge.control_coverage - 0.3, 0.0)
                    
                    # Recalculate success probability
                    prob_edge.__post_init__()
                    
                    # Update graph edge weight
                    source, target = edge_id.split('-')
                    self.security_graph[source][target]['weight'] = prob_edge.success_probability
        
        return modified_edges
    
    def _control_affects_edge(self, control_id: str, edge_id: str) -> bool:
        """Check if a control affects a specific edge"""
        # Simplified: assume all controls affect all edges
        # In practice, would check control scope and network topology
        return True
    
    def _restore_edges(self, original_edges: Dict[str, ProbabilisticEdge]):
        """Restore original edge probabilities"""
        for edge_id, original_edge in original_edges.items():
            self.probabilistic_edges[edge_id] = original_edge
            source, target = edge_id.split('-')
            self.security_graph[source][target]['weight'] = original_edge.success_probability
    
    def _generate_scenario_recommendations(self, control_changes: Dict[str, bool], 
                                         risk_change: float) -> List[str]:
        """Generate recommendations based on scenario results"""
        recommendations = []
        
        if risk_change < -1.0:
            recommendations.append("This control configuration significantly reduces risk - consider implementation")
        elif risk_change > 1.0:
            recommendations.append("This configuration increases risk - reconsider these changes")
        
        enabled_controls = [c for c, enabled in control_changes.items() if enabled]
        disabled_controls = [c for c, enabled in control_changes.items() if not enabled]
        
        if enabled_controls:
            recommendations.append(f"Enabling {', '.join(enabled_controls)} provides additional security")
        
        if disabled_controls:
            recommendations.append(f"Disabling {', '.join(disabled_controls)} may increase vulnerability")
        
        return recommendations
    
    def _calculate_roi_analysis(self, control_changes: Dict[str, bool], risk_change: float) -> Dict[str, float]:
        """Calculate simple ROI analysis for control changes"""
        # Simplified ROI calculation
        estimated_cost = len([c for c, enabled in control_changes.items() if enabled]) * 10000  # $10k per control
        risk_reduction_value = abs(risk_change) * 50000  # $50k per risk point reduced
        
        roi = (risk_reduction_value - estimated_cost) / estimated_cost if estimated_cost > 0 else 0
        
        return {
            "estimated_cost": estimated_cost,
            "risk_reduction_value": risk_reduction_value,
            "roi_percentage": roi * 100,
            "payback_period_months": 12 / max(roi, 0.1) if roi > 0 else 999
        }
    
    def analyze_defense_effectiveness(self, nodes: List[Dict[str, Any]]) -> List[DefenseEffectivenessModel]:
        """Analyze effectiveness of defense controls"""
        defense_models = []
        
        control_nodes = [n for n in nodes if n.get("type") == "Control"]
        
        for control in control_nodes:
            effectiveness_model = DefenseEffectivenessModel(
                control_id=control["id"],
                control_type=control.get("subtype", "Unknown"),
                effectiveness_rating=control.get("effectiveness_score", 0.5),
                coverage_areas=control.get("coverage_scope", []),
                interaction_effects=self._calculate_interaction_effects(control, control_nodes),
                degradation_over_time=self._estimate_degradation_rate(control),
                false_positive_rate=self._estimate_false_positive_rate(control),
                false_negative_rate=self._estimate_false_negative_rate(control)
            )
            defense_models.append(effectiveness_model)
        
        return defense_models
    
    def _calculate_interaction_effects(self, control: Dict, all_controls: List[Dict]) -> Dict[str, float]:
        """Calculate how controls interact with each other"""
        interactions = {}
        
        control_type = control.get("subtype")
        
        # Define synergistic effects between control types
        synergies = {
            "WAF": {"EDR": 0.2, "SIEM": 0.15},
            "EDR": {"SIEM": 0.25, "NetworkACL": 0.1},
            "IAMPolicy": {"MFA": 0.3, "SIEM": 0.2}
        }
        
        for other_control in all_controls:
            if other_control["id"] != control["id"]:
                other_type = other_control.get("subtype")
                synergy = synergies.get(control_type, {}).get(other_type, 0.0)
                if synergy > 0:
                    interactions[other_control["id"]] = synergy
        
        return interactions
    
    def _estimate_degradation_rate(self, control: Dict) -> float:
        """Estimate how quickly control effectiveness degrades"""
        # Simplified model - in practice would be based on control type and maintenance
        control_type = control.get("subtype", "")
        
        degradation_rates = {
            "WAF": 0.05,      # 5% per month without updates
            "EDR": 0.03,      # 3% per month
            "IAMPolicy": 0.01, # 1% per month
            "NetworkACL": 0.02 # 2% per month
        }
        
        return degradation_rates.get(control_type, 0.04)
    
    def _estimate_false_positive_rate(self, control: Dict) -> float:
        """Estimate false positive rate for detection controls"""
        control_type = control.get("subtype", "")
        
        fp_rates = {
            "WAF": 0.1,      # 10% false positives
            "EDR": 0.05,     # 5% false positives
            "IDS": 0.15,     # 15% false positives
            "SIEM": 0.08     # 8% false positives
        }
        
        return fp_rates.get(control_type, 0.1)
    
    def _estimate_false_negative_rate(self, control: Dict) -> float:
        """Estimate false negative rate for detection controls"""
        effectiveness = control.get("effectiveness_score", 0.5)
        # Inverse relationship: higher effectiveness = lower false negatives
        return 1.0 - effectiveness


# Global instance
probabilistic_engine = ProbabilisticSimulationEngine()