"""
EXPANDED INTELLIGENT NODE SYSTEM - PHASE 1
Revolutionary Security Modeling Platform
Enhanced Node Types with Security Architect-Grade Questionnaires

This module implements:
1. 25+ comprehensive node types covering modern architectures
2. Multi-layered security questionnaires (Basic/Advanced/Expert)
3. Enhanced risk calculation with probabilistic modeling
4. Basic threat intelligence integration
5. Advanced dependency management
"""

from typing import Dict, List, Optional, Any, Union, Set
from enum import Enum
from pydantic import BaseModel, Field
import logging
from dataclasses import dataclass
import json
import math

logger = logging.getLogger(__name__)

# EXPANDED SECURITY BRANCH TYPES
class SecurityBranchType(str, Enum):
    # Authentication & Authorization
    AUTHENTICATION = "Authentication"
    AUTHORIZATION = "Authorization"
    LOGIN = "Login"
    IAM = "IAM"
    MFA = "MFA"
    SSO = "SSO"
    
    # Network Security
    NETWORK_SECURITY = "NetworkSecurity"
    FIREWALL = "Firewall"
    VPN = "VPN"
    NETWORK_SEGMENTATION = "NetworkSegmentation"
    LOAD_BALANCER = "LoadBalancer"
    
    # Data Protection
    ENCRYPTION = "Encryption"
    DATA_CLASSIFICATION = "DataClassification"
    DATA_LOSS_PREVENTION = "DataLossPrevention"
    BACKUP = "Backup"
    KEY_MANAGEMENT = "KeyManagement"
    
    # Application Security
    API = "API"
    WAF = "WAF"
    INPUT_VALIDATION = "InputValidation"
    CORS = "CORS"
    RATE_LIMITING = "RateLimiting"
    CODE_SECURITY = "CodeSecurity"
    
    # Infrastructure Security
    OS_HARDENING = "OSHardening"
    PATCH_MANAGEMENT = "PatchManagement"
    VULNERABILITY_SCANNING = "VulnerabilityScanning"
    CONTAINER_SECURITY = "ContainerSecurity"
    
    # Monitoring & Compliance
    MONITORING = "Monitoring"
    LOGGING = "Logging"
    INCIDENT_RESPONSE = "IncidentResponse"
    COMPLIANCE = "Compliance"
    
    # Cloud Security
    CLOUD_SECURITY = "CloudSecurity"
    SERVERLESS_SECURITY = "ServerlessSecurity"
    CONTAINER_ORCHESTRATION = "ContainerOrchestration"
    
    # Database Security
    DATABASE = "Database"
    ACCESS_CONTROL = "AccessControl"
    
    # DevOps Security
    CI_CD_SECURITY = "CICDSecurity"
    SECRETS_MANAGEMENT = "SecretsManagement"
    SUPPLY_CHAIN = "SupplyChain"
    
    # Additional Security Branches
    DDoS_PROTECTION = "DDoSProtection"
    MESSAGE_SECURITY = "MessageSecurity"
    APPLICATION_SERVICES = "ApplicationServices"

class QuestionnaireLevel(str, Enum):
    BASIC = "basic"           # 5-8 questions
    ADVANCED = "advanced"     # 15-20 questions
    EXPERT = "expert"         # 25-30 questions

class ThreatLevel(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High" 
    MEDIUM = "Medium"
    LOW = "Low"
    MINIMAL = "Minimal"

class NodeCategory(str, Enum):
    CLOUD_INFRASTRUCTURE = "Cloud Infrastructure"
    SECURITY_SERVICES = "Security Services"
    NETWORK_COMPONENTS = "Network Components"
    CONTAINER_DEVOPS = "Container & DevOps"
    DATA_STORAGE = "Data & Storage"
    COMPUTE_SERVICES = "Compute Services"
    MONITORING_LOGGING = "Monitoring & Logging"
    APPLICATION_SERVICES = "Application Services"

@dataclass
class ThreatIntelligence:
    """Basic threat intelligence for node types"""
    cve_count: int = 0
    recent_threats: List[str] = None
    attack_vectors: List[str] = None
    mitre_techniques: List[str] = None
    threat_actors: List[str] = None
    
    def __post_init__(self):
        if self.recent_threats is None:
            self.recent_threats = []
        if self.attack_vectors is None:
            self.attack_vectors = []
        if self.mitre_techniques is None:
            self.mitre_techniques = []
        if self.threat_actors is None:
            self.threat_actors = []

@dataclass
class RiskMetrics:
    """Enhanced risk calculation metrics with probabilistic modeling"""
    
    def __init__(self):
        self.base_risk: float = 5.0
        self.attack_surface_score: float = 5.0
        self.vulnerability_score: float = 5.0
        self.control_effectiveness: float = 5.0
        self.business_impact: float = 5.0
        self.threat_probability: float = 0.5
        
        # Priority 1: Probabilistic Modeling Enhancement - NEW FIELDS
        self.confidence_interval: dict = {"lower_bound": 0.0, "upper_bound": 0.0, "confidence_level": 90}
        self.threat_likelihood: float = 0.5  # Probability of threat materialization (0-1)
        self.probabilistic_score: float = 0.0  # Monte Carlo simulation result
        self.uncertainty_factor: float = 0.1  # Uncertainty in risk assessment (0-1)
    
    def calculate_composite_risk(self) -> float:
        """Calculate composite risk using weighted formula"""
        # Weighted risk calculation
        weights = {
            'attack_surface': 0.25,
            'vulnerability': 0.25,
            'control_effectiveness': -0.20,  # Negative because better controls reduce risk
            'business_impact': 0.30,
            'threat_probability': 0.20
        }
        
        composite = (
            self.attack_surface_score * weights['attack_surface'] +
            self.vulnerability_score * weights['vulnerability'] +
            self.control_effectiveness * weights['control_effectiveness'] +
            self.business_impact * weights['business_impact'] +
            (self.threat_probability * 10) * weights['threat_probability']
        )
        
        return max(0.0, min(10.0, composite))
    
    def calculate_probabilistic_risk(self, num_simulations: int = 1000) -> dict:
        """Calculate probabilistic risk using Monte Carlo simulation"""
        import random
        import numpy as np
        
        simulation_results = []
        
        for _ in range(num_simulations):
            # Add uncertainty to each risk factor
            sim_attack_surface = max(0, min(10, 
                self.attack_surface_score + random.gauss(0, self.uncertainty_factor * 2)))
            sim_vulnerability = max(0, min(10, 
                self.vulnerability_score + random.gauss(0, self.uncertainty_factor * 2)))
            sim_control_eff = max(0, min(10, 
                self.control_effectiveness + random.gauss(0, self.uncertainty_factor * 1.5)))
            sim_business_impact = max(0, min(10, 
                self.business_impact + random.gauss(0, self.uncertainty_factor * 1)))
            sim_threat_prob = max(0, min(1, 
                self.threat_probability + random.gauss(0, self.uncertainty_factor * 0.2)))
            
            # Calculate risk for this simulation
            weights = {
                'attack_surface': 0.25,
                'vulnerability': 0.25,
                'control_effectiveness': -0.20,
                'business_impact': 0.30,
                'threat_probability': 0.20
            }
            
            sim_risk = (
                sim_attack_surface * weights['attack_surface'] +
                sim_vulnerability * weights['vulnerability'] +
                sim_control_eff * weights['control_effectiveness'] +
                sim_business_impact * weights['business_impact'] +
                (sim_threat_prob * 10) * weights['threat_probability']
            )
            
            simulation_results.append(max(0.0, min(10.0, sim_risk)))
        
        # Calculate statistics
        sim_array = np.array(simulation_results)
        mean_risk = float(np.mean(sim_array))
        std_risk = float(np.std(sim_array))
        percentile_5 = float(np.percentile(sim_array, 5))
        percentile_95 = float(np.percentile(sim_array, 95))
        
        # Update probabilistic fields
        self.probabilistic_score = mean_risk
        self.confidence_interval = (percentile_5, percentile_95)
        self.threat_likelihood = self.threat_probability
        
        return {
            "mean_risk": mean_risk,
            "standard_deviation": std_risk,
            "confidence_interval_90": (percentile_5, percentile_95),
            "risk_distribution": {
                "p5": percentile_5,
                "p25": float(np.percentile(sim_array, 25)),
                "p50": float(np.percentile(sim_array, 50)),
                "p75": float(np.percentile(sim_array, 75)),
                "p95": percentile_95
            },
            "probability_high_risk": float(np.sum(sim_array >= 7.0) / len(sim_array)),
            "probability_critical_risk": float(np.sum(sim_array >= 8.5) / len(sim_array))
        }

class ExpandedIntelligentNodeEngine:
    """Enhanced engine for comprehensive node types and security intelligence"""
    
    def __init__(self):
        self.node_templates = self._initialize_expanded_templates()
        self.threat_intelligence = self._initialize_threat_intelligence()
        self.risk_calculators = self._initialize_risk_calculators()
        # Priority 2: Bulk Risk Assessment Enhancement - NEW FEATURES
        self.correlation_cache = {}
        self.amplification_factors = self._initialize_amplification_factors()
    
    def _initialize_amplification_factors(self) -> dict:
        """Initialize risk amplification factors for node correlations"""
        return {
            # Network interconnectedness amplifies risk
            "network_density": {
                "low": 1.0,      # < 0.3 edge density
                "medium": 1.2,   # 0.3-0.7 edge density  
                "high": 1.5      # > 0.7 edge density
            },
            # Asset criticality combinations
            "critical_asset_cluster": {
                "single": 1.0,
                "pair": 1.3,
                "cluster": 1.8   # 3+ critical assets connected
            },
            # Control failure cascades
            "control_dependency": {
                "independent": 1.0,
                "dependent": 1.4,    # Controls depend on each other
                "cascade_risk": 2.0  # Single point of failure
            },
            # Attack surface concentration
            "surface_concentration": {
                "distributed": 1.0,
                "concentrated": 1.6,  # Multiple surfaces on same asset
                "overlapping": 2.2    # Surfaces enable each other
            }
        }
    
    def calculate_comprehensive_risk(self, node_subtype: str, responses: dict) -> dict:
        """Enhanced comprehensive risk calculation with probabilistic modeling"""
        try:
            # Get base risk metrics
            base_metrics = self._calculate_base_risk_metrics(node_subtype, responses)
            
            # Priority 1: Enhanced Probabilistic Modeling
            probabilistic_analysis = base_metrics.calculate_probabilistic_risk()
            
            # Calculate threat intelligence enhancement
            threat_enhancement = self._calculate_threat_intelligence_enhancement(node_subtype)
            
            # Apply probabilistic enhancements
            enhanced_risk = {
                "composite_risk_score": base_metrics.calculate_composite_risk(),
                "probabilistic_score": base_metrics.probabilistic_score,
                "confidence_interval": base_metrics.confidence_interval,
                "threat_likelihood": base_metrics.threat_likelihood,
                "uncertainty_factor": base_metrics.uncertainty_factor,
                
                # Enhanced risk breakdown
                "risk_components": {
                    "attack_surface_score": base_metrics.attack_surface_score,
                    "vulnerability_score": base_metrics.vulnerability_score,
                    "control_effectiveness": base_metrics.control_effectiveness,
                    "business_impact": base_metrics.business_impact,
                    "threat_probability": base_metrics.threat_probability
                },
                
                # Probabilistic analysis results
                "monte_carlo_analysis": probabilistic_analysis,
                
                # Threat intelligence integration
                "threat_intelligence_impact": threat_enhancement,
                
                # Risk level categorization
                "risk_level": self._categorize_risk_level(base_metrics.probabilistic_score),
                "risk_trend": self._calculate_risk_trend(node_subtype, responses),
                
                # Additional metrics
                "attack_complexity": self._assess_attack_complexity(node_subtype, responses),
                "defense_depth": self._assess_defense_depth(node_subtype, responses),
                "recovery_time": self._estimate_recovery_time(node_subtype, responses)
            }
            
            return enhanced_risk
            
        except Exception as e:
            logger.error(f"Risk calculation error for {node_subtype}: {str(e)}")
            return self._get_fallback_risk_assessment(node_subtype)
    
    def _calculate_base_risk_metrics(self, node_subtype: str, responses: dict) -> RiskMetrics:
        """Calculate base risk metrics with enhanced logic"""
        # Get node template for baseline risk factors
        template = self.node_templates.get(node_subtype, {})
        risk_factors = template.get("risk_factors", {})
        
        # Initialize base metrics
        metrics = RiskMetrics()
        
        # Calculate attack surface based on responses
        metrics.attack_surface_score = self._calculate_attack_surface_score(responses, risk_factors)
        
        # Calculate vulnerability score
        metrics.vulnerability_score = self._calculate_vulnerability_score(responses, risk_factors)
        
        # Calculate control effectiveness
        metrics.control_effectiveness = self._calculate_control_effectiveness_score(responses)
        
        # Calculate business impact
        metrics.business_impact = self._calculate_business_impact_score(responses)
        
        # Calculate threat probability with intelligence enhancement
        metrics.threat_probability = self._calculate_enhanced_threat_probability(node_subtype, responses)
        
        # Set uncertainty factor based on response completeness
        response_completeness = len([v for v in responses.values() if v]) / max(len(responses), 1)
        metrics.uncertainty_factor = 0.3 * (1 - response_completeness)  # Higher uncertainty with fewer responses
        
        return metrics
    
    def _calculate_enhanced_threat_probability(self, node_subtype: str, responses: dict) -> float:
        """Calculate threat probability enhanced with threat intelligence"""
        base_probability = 0.5
        
        # Get threat intelligence for this node type
        threat_intel = self.threat_intelligence.get(node_subtype, {})
        
        # Adjust based on recent threats
        recent_threats = threat_intel.get("recent_threats", [])
        if len(recent_threats) > 5:
            base_probability += 0.2
        elif len(recent_threats) > 2:
            base_probability += 0.1
        
        # Adjust based on CVE count
        cve_count = threat_intel.get("cve_count", 0)
        if cve_count > 100:
            base_probability += 0.15
        elif cve_count > 50:
            base_probability += 0.1
        
        # Adjust based on configuration responses
        high_risk_responses = self._identify_high_risk_responses(responses)
        base_probability += len(high_risk_responses) * 0.05
        
        return min(base_probability, 1.0)
    
    def _identify_high_risk_responses(self, responses: dict) -> list:
        """Identify responses that indicate higher risk"""
        high_risk_indicators = [
            "no_encryption", "public_access", "weak_authentication", 
            "no_monitoring", "no_backup", "default_config",
            "admin_access", "no_patching", "weak_passwords"
        ]
        
        return [key for key, value in responses.items() 
                if any(indicator in key.lower() for indicator in high_risk_indicators) 
                and value in [True, "yes", "enabled", "public", "weak", "none"]]
    
    def perform_bulk_risk_assessment(self, nodes_data: list, business_context: dict = None) -> dict:
        """Priority 2: Enhanced bulk risk assessment with cross-node correlations"""
        if not nodes_data:
            return {"error": "No nodes provided for assessment"}
        
        # Individual assessments
        individual_assessments = []
        overall_risk_scores = []
        
        for node_data in nodes_data:
            node_subtype = node_data.get("node_subtype")
            responses = node_data.get("responses", {})
            
            if not node_subtype:
                continue
            
            # Add business context to responses
            enhanced_responses = {**responses}
            if business_context:
                enhanced_responses.update(business_context)
            
            # Calculate individual risk
            risk_assessment = self.calculate_comprehensive_risk(node_subtype, enhanced_responses)
            
            individual_assessments.append({
                "node_id": node_data.get("node_id", f"node_{len(individual_assessments)}"),
                "node_subtype": node_subtype,
                "individual_risk": risk_assessment,
                "risk_score": risk_assessment.get("probabilistic_score", 5.0)
            })
            
            overall_risk_scores.append(risk_assessment.get("probabilistic_score", 5.0))
        
        # Priority 2: Cross-node correlation analysis
        cross_correlations = self._analyze_cross_node_correlations(individual_assessments)
        
        # Priority 2: Risk amplification factors
        amplification_analysis = self._calculate_risk_amplification(individual_assessments, cross_correlations)
        
        # Priority 2: Aggregated metrics
        aggregated_metrics = self._calculate_aggregated_metrics(individual_assessments, amplification_analysis)
        
        return {
            "assessment_results": individual_assessments,
            "aggregated_metrics": aggregated_metrics,
            "cross_node_correlations": cross_correlations,
            "risk_amplification": amplification_analysis,
            "assessment_summary": {
                "total_nodes": len(individual_assessments),
                "average_risk_score": sum(overall_risk_scores) / len(overall_risk_scores) if overall_risk_scores else 0,
                "highest_risk_score": max(overall_risk_scores) if overall_risk_scores else 0,
                "lowest_risk_score": min(overall_risk_scores) if overall_risk_scores else 0,
                "critical_nodes": len([s for s in overall_risk_scores if s >= 8.0]),
                "high_risk_nodes": len([s for s in overall_risk_scores if 6.0 <= s < 8.0]),
                "medium_risk_nodes": len([s for s in overall_risk_scores if 4.0 <= s < 6.0]),
                "low_risk_nodes": len([s for s in overall_risk_scores if s < 4.0])
            },
            "correlation_insights": self._generate_correlation_insights(cross_correlations),
            "bulk_recommendations": self._generate_bulk_recommendations(individual_assessments, amplification_analysis)
        }
    
    def _analyze_cross_node_correlations(self, assessments: list) -> dict:
        """Analyze correlations between different nodes"""
        correlations = {
            "node_type_correlations": {},
            "risk_pattern_correlations": {},
            "vulnerability_clustering": {},
            "control_dependencies": {}
        }
        
        # Group by node subtype
        type_groups = {}
        for assessment in assessments:
            subtype = assessment["node_subtype"]
            if subtype not in type_groups:
                type_groups[subtype] = []
            type_groups[subtype].append(assessment)
        
        # Analyze node type correlations
        for subtype, nodes in type_groups.items():
            if len(nodes) > 1:
                risk_scores = [node["risk_score"] for node in nodes]
                correlations["node_type_correlations"][subtype] = {
                    "count": len(nodes),
                    "avg_risk": sum(risk_scores) / len(risk_scores),
                    "risk_variance": self._calculate_variance(risk_scores),
                    "correlation_strength": self._assess_correlation_strength(risk_scores)
                }
        
        # Analyze risk pattern correlations
        high_risk_nodes = [a for a in assessments if a["risk_score"] >= 7.0]
        medium_risk_nodes = [a for a in assessments if 4.0 <= a["risk_score"] < 7.0]
        
        correlations["risk_pattern_correlations"] = {
            "high_risk_clusters": self._find_risk_clusters(high_risk_nodes),
            "medium_risk_clusters": self._find_risk_clusters(medium_risk_nodes),
            "isolated_high_risk": len(high_risk_nodes)
        }
        
        # Analyze vulnerability clustering
        correlations["vulnerability_clustering"] = self._analyze_vulnerability_clustering(assessments)
        
        return correlations
    
    def _calculate_risk_amplification(self, assessments: list, correlations: dict) -> dict:
        """Calculate risk amplification factors"""
        amplification = {
            "network_effects": {},
            "cascade_risks": {},
            "concentration_risks": {},
            "overall_amplification_factor": 1.0
        }
        
        # Network density amplification
        node_count = len(assessments)
        if node_count > 1:
            density_factor = self._calculate_network_density_amplification(assessments)
            amplification["network_effects"]["density_amplification"] = density_factor
            amplification["overall_amplification_factor"] *= density_factor
        
        # Critical asset clustering
        critical_assets = [a for a in assessments if a["risk_score"] >= 8.0]
        if len(critical_assets) > 1:
            cluster_factor = self.amplification_factors["critical_asset_cluster"]["cluster"]
            amplification["concentration_risks"]["critical_cluster_amplification"] = cluster_factor
            amplification["overall_amplification_factor"] *= cluster_factor
        
        # Control dependency analysis
        control_amplification = self._analyze_control_dependencies(assessments)
        amplification["cascade_risks"] = control_amplification
        if control_amplification.get("cascade_risk_factor", 1.0) > 1.0:
            amplification["overall_amplification_factor"] *= control_amplification["cascade_risk_factor"]
        
        return amplification
    
    def _calculate_aggregated_metrics(self, assessments: list, amplification: dict) -> dict:
        """Calculate comprehensive aggregated metrics"""
        if not assessments:
            return {}
        
        risk_scores = [a["risk_score"] for a in assessments]
        amplification_factor = amplification.get("overall_amplification_factor", 1.0)
        
        # Basic aggregations
        mean_risk = sum(risk_scores) / len(risk_scores)
        adjusted_mean_risk = min(mean_risk * amplification_factor, 10.0)
        
        aggregated = {
            "overall_risk_score": adjusted_mean_risk,
            "risk_distribution": {
                "mean": mean_risk,
                "median": self._calculate_median(risk_scores),
                "std_deviation": self._calculate_std_deviation(risk_scores),
                "percentiles": {
                    "p25": self._calculate_percentile(risk_scores, 25),
                    "p50": self._calculate_percentile(risk_scores, 50),
                    "p75": self._calculate_percentile(risk_scores, 75),
                    "p90": self._calculate_percentile(risk_scores, 90),
                    "p95": self._calculate_percentile(risk_scores, 95)
                }
            },
            "risk_categories": {
                "critical": len([s for s in risk_scores if s >= 8.0]),
                "high": len([s for s in risk_scores if 6.0 <= s < 8.0]),
                "medium": len([s for s in risk_scores if 4.0 <= s < 6.0]),
                "low": len([s for s in risk_scores if s < 4.0])
            },
            "amplification_effects": {
                "base_risk": mean_risk,
                "amplified_risk": adjusted_mean_risk,
                "amplification_factor": amplification_factor,
                "amplification_sources": list(amplification.keys())
            },
            "systemic_risk_indicators": {
                "risk_concentration": self._calculate_risk_concentration(risk_scores),
                "correlation_strength": self._calculate_overall_correlation_strength(assessments),
                "vulnerability_diversity": self._calculate_vulnerability_diversity(assessments)
            }
        }
        
        return aggregated
    
    # Helper methods for bulk assessment calculations
    def _calculate_variance(self, values: list) -> float:
        if len(values) <= 1:
            return 0.0
        mean = sum(values) / len(values)
        return sum((x - mean) ** 2 for x in values) / len(values)
    
    def _calculate_std_deviation(self, values: list) -> float:
        return math.sqrt(self._calculate_variance(values))
    
    def _calculate_median(self, values: list) -> float:
        sorted_values = sorted(values)
        n = len(sorted_values)
        if n % 2 == 0:
            return (sorted_values[n//2 - 1] + sorted_values[n//2]) / 2
        return sorted_values[n//2]
    
    def _calculate_percentile(self, values: list, percentile: int) -> float:
        sorted_values = sorted(values)
        index = (percentile / 100) * (len(sorted_values) - 1)
        if index.is_integer():
            return sorted_values[int(index)]
        lower = sorted_values[int(index)]
        upper = sorted_values[int(index) + 1]
        return lower + (upper - lower) * (index - int(index))
    
    def _find_risk_clusters(self, nodes: list) -> list:
        """Find clusters of related high-risk nodes"""
        # Simplified clustering - in practice would use more sophisticated algorithms
        clusters = []
        node_subtypes = {}
        
        for node in nodes:
            subtype = node["node_subtype"]
            if subtype not in node_subtypes:
                node_subtypes[subtype] = []
            node_subtypes[subtype].append(node)
        
        for subtype, subtype_nodes in node_subtypes.items():
            if len(subtype_nodes) > 1:
                clusters.append({
                    "cluster_type": subtype,
                    "node_count": len(subtype_nodes),
                    "avg_risk": sum(n["risk_score"] for n in subtype_nodes) / len(subtype_nodes)
                })
        
        return clusters
    
    def _generate_correlation_insights(self, correlations: dict) -> list:
        """Generate insights from correlation analysis"""
        insights = []
        
        # Node type correlation insights
        type_corr = correlations.get("node_type_correlations", {})
        for subtype, data in type_corr.items():
            if data["correlation_strength"] > 0.7:
                insights.append(f"Strong risk correlation detected in {subtype} nodes (correlation: {data['correlation_strength']:.2f})")
        
        # Risk pattern insights
        pattern_corr = correlations.get("risk_pattern_correlations", {})
        high_risk_clusters = pattern_corr.get("high_risk_clusters", [])
        if len(high_risk_clusters) > 0:
            insights.append(f"Identified {len(high_risk_clusters)} high-risk node clusters - may indicate systemic vulnerabilities")
        
        return insights
    
    def _generate_bulk_recommendations(self, assessments: list, amplification: dict) -> list:
        """Generate recommendations for bulk assessment"""
        recommendations = []
        
        amplification_factor = amplification.get("overall_amplification_factor", 1.0)
        
        if amplification_factor > 1.5:
            recommendations.append("HIGH PRIORITY: Risk amplification detected - systemic vulnerabilities may exist")
        
        critical_nodes = [a for a in assessments if a["risk_score"] >= 8.0]
        if len(critical_nodes) > len(assessments) * 0.3:
            recommendations.append("CRITICAL: High percentage of critical-risk nodes - immediate security review recommended")
        
        # Add specific recommendations based on correlation patterns
        recommendations.extend(self._generate_pattern_based_recommendations(assessments))
        
        return recommendations
    
    def _assess_correlation_strength(self, risk_scores: list) -> float:
        """Assess correlation strength between risk scores"""
        if len(risk_scores) < 2:
            return 0.0
        
        mean = sum(risk_scores) / len(risk_scores)
        variance = sum((x - mean) ** 2 for x in risk_scores) / len(risk_scores)
        
        # Higher variance means lower correlation
        # Scale to 0-1 where 1 is perfect correlation (no variance)
        max_possible_variance = 25  # For 0-10 scale
        correlation_strength = max(0, 1 - (variance / max_possible_variance))
        
        return correlation_strength
    
    def _analyze_vulnerability_clustering(self, assessments: list) -> dict:
        """Analyze clustering of vulnerabilities"""
        clustering = {
            "vulnerability_types": {},
            "geographic_clustering": {},  # Placeholder for future geo-analysis
            "temporal_clustering": {}     # Placeholder for future time-based analysis
        }
        
        # Group by common vulnerability indicators
        vuln_indicators = {}
        for assessment in assessments:
            individual_risk = assessment.get("individual_risk", {})
            risk_components = individual_risk.get("risk_components", {})
            
            vuln_score = risk_components.get("vulnerability_score", 0)
            if vuln_score >= 7.0:
                subtype = assessment["node_subtype"]
                if subtype not in vuln_indicators:
                    vuln_indicators[subtype] = 0
                vuln_indicators[subtype] += 1
        
        clustering["vulnerability_types"] = vuln_indicators
        return clustering
    
    def _calculate_network_density_amplification(self, assessments: list) -> float:
        """Calculate amplification factor based on network density"""
        node_count = len(assessments)
        
        # Simulate network density based on node types
        # In practice, would analyze actual network topology
        high_connectivity_types = ["API", "Database", "LoadBalancer", "WAF"]
        connected_nodes = sum(1 for a in assessments if a["node_subtype"] in high_connectivity_types)
        
        density = connected_nodes / node_count if node_count > 0 else 0
        
        if density > 0.7:
            return self.amplification_factors["network_density"]["high"]
        elif density > 0.3:
            return self.amplification_factors["network_density"]["medium"]
        else:
            return self.amplification_factors["network_density"]["low"]
    
    def _analyze_control_dependencies(self, assessments: list) -> dict:
        """Analyze control dependencies for cascade risk"""
        control_analysis = {
            "independent_controls": 0,
            "dependent_controls": 0,
            "cascade_risk_factor": 1.0
        }
        
        # Count control-type nodes
        control_nodes = [a for a in assessments if "Control" in a.get("node_subtype", "")]
        security_nodes = [a for a in assessments if a["node_subtype"] in ["WAF", "EDR", "IAM", "NetworkACL"]]
        
        total_controls = len(control_nodes) + len(security_nodes)
        
        if total_controls > 0:
            # Simple heuristic: assume some dependency if multiple controls exist
            if total_controls > 3:
                control_analysis["cascade_risk_factor"] = self.amplification_factors["control_dependency"]["cascade_risk"]
                control_analysis["dependent_controls"] = total_controls
            elif total_controls > 1:
                control_analysis["cascade_risk_factor"] = self.amplification_factors["control_dependency"]["dependent"]
                control_analysis["dependent_controls"] = total_controls
            else:
                control_analysis["independent_controls"] = total_controls
        
        return control_analysis
    
    def _calculate_risk_concentration(self, risk_scores: list) -> float:
        """Calculate risk concentration index"""
        if not risk_scores:
            return 0.0
        
        # Calculate Gini coefficient as a measure of concentration
        sorted_scores = sorted(risk_scores)
        n = len(sorted_scores)
        cumsum = sum((i + 1) * score for i, score in enumerate(sorted_scores))
        total = sum(sorted_scores)
        
        if total == 0:
            return 0.0
        
        gini = (2 * cumsum) / (n * total) - (n + 1) / n
        return gini
    
    def _calculate_overall_correlation_strength(self, assessments: list) -> float:
        """Calculate overall correlation strength across all nodes"""
        if len(assessments) < 2:
            return 0.0
        
        risk_scores = [a["risk_score"] for a in assessments]
        return self._assess_correlation_strength(risk_scores)
    
    def _calculate_vulnerability_diversity(self, assessments: list) -> float:
        """Calculate diversity of vulnerability types"""
        if not assessments:
            return 0.0
        
        # Count unique node subtypes as a proxy for vulnerability diversity
        unique_subtypes = set(a["node_subtype"] for a in assessments)
        total_nodes = len(assessments)
        
        # Diversity index (0-1, where 1 is maximum diversity)
        return len(unique_subtypes) / total_nodes if total_nodes > 0 else 0.0
    
    def _get_fallback_risk_assessment(self, node_subtype: str) -> dict:
        """Provide fallback risk assessment in case of errors"""
        return {
            "composite_risk_score": 5.0,
            "probabilistic_score": 5.0,
            "confidence_interval": (3.0, 7.0),
            "threat_likelihood": 0.5,
            "uncertainty_factor": 0.5,
            "risk_components": {
                "attack_surface_score": 5.0,
                "vulnerability_score": 5.0,
                "control_effectiveness": 5.0,
                "business_impact": 5.0,
                "threat_probability": 0.5
            },
            "monte_carlo_analysis": {
                "mean_risk": 5.0,
                "standard_deviation": 1.0,
                "confidence_interval_90": (3.0, 7.0),
                "risk_distribution": {
                    "p5": 3.0, "p25": 4.0, "p50": 5.0, "p75": 6.0, "p95": 7.0
                },
                "probability_high_risk": 0.1,
                "probability_critical_risk": 0.05
            },
            "threat_intelligence_impact": {"enhancement_factor": 1.0},
            "risk_level": "Medium",
            "risk_trend": "Stable",
            "attack_complexity": "Medium",
            "defense_depth": "Moderate",
            "recovery_time": "4-8 hours"
        }
    
    def _calculate_threat_intelligence_enhancement(self, node_subtype: str) -> dict:
        """Calculate threat intelligence enhancement factor"""
        threat_intel = self.threat_intelligence.get(node_subtype, {})
        
        enhancement_factor = 1.0
        details = {}
        
        # CVE impact
        cve_count = threat_intel.get("cve_count", 0)
        if cve_count > 100:
            enhancement_factor += 0.2
            details["cve_impact"] = "High"
        elif cve_count > 50:
            enhancement_factor += 0.1
            details["cve_impact"] = "Medium"
        else:
            details["cve_impact"] = "Low"
        
        # Recent threats impact
        recent_threats = len(threat_intel.get("recent_threats", []))
        if recent_threats > 5:
            enhancement_factor += 0.15
            details["threat_activity"] = "Very High"
        elif recent_threats > 2:
            enhancement_factor += 0.08
            details["threat_activity"] = "High"
        else:
            details["threat_activity"] = "Moderate"
        
        return {
            "enhancement_factor": enhancement_factor,
            "details": details,
            "threat_intelligence_score": min(enhancement_factor, 2.0)
        }
    
    def _categorize_risk_level(self, risk_score: float) -> str:
        """Categorize risk level based on score"""
        if risk_score >= 8.5:
            return "Critical"
        elif risk_score >= 7.0:
            return "High"
        elif risk_score >= 4.0:
            return "Medium"
        elif risk_score >= 2.0:
            return "Low"
        else:
            return "Minimal"
    
    def _calculate_risk_trend(self, node_subtype: str, responses: dict) -> str:
        """Calculate risk trend analysis"""
        # Simplified trend analysis - in practice would use historical data
        high_risk_indicators = self._identify_high_risk_responses(responses)
        
        if len(high_risk_indicators) > 3:
            return "Increasing"
        elif len(high_risk_indicators) > 1:
            return "Stable"
        else:
            return "Decreasing"
    
    def _assess_attack_complexity(self, node_subtype: str, responses: dict) -> str:
        """Assess attack complexity based on configuration"""
        complexity_score = 5.0  # Base medium complexity
        
        # Reduce complexity for common misconfigurations
        if any(indicator in str(responses).lower() for indicator in ["default", "weak", "none", "disabled"]):
            complexity_score -= 2.0
        
        # Increase complexity for good security practices
        if any(indicator in str(responses).lower() for indicator in ["mfa", "encrypted", "monitored", "restricted"]):
            complexity_score += 2.0
        
        if complexity_score >= 7.0:
            return "Very High"
        elif complexity_score >= 5.5:
            return "High"
        elif complexity_score >= 4.0:
            return "Medium"
        elif complexity_score >= 2.5:
            return "Low"
        else:
            return "Very Low"
    
    def _assess_defense_depth(self, node_subtype: str, responses: dict) -> str:
        """Assess defense in depth based on responses"""
        defense_indicators = ["firewall", "monitoring", "encryption", "backup", "access_control", "logging"]
        
        defense_count = sum(1 for indicator in defense_indicators 
                          if any(indicator in key.lower() for key in responses.keys()))
        
        if defense_count >= 5:
            return "Excellent"
        elif defense_count >= 3:
            return "Good"
        elif defense_count >= 2:
            return "Moderate"
        elif defense_count >= 1:
            return "Basic"
        else:
            return "Minimal"
    
    def _estimate_recovery_time(self, node_subtype: str, responses: dict) -> str:
        """Estimate recovery time based on configuration"""
        # Check for backup and recovery indicators
        recovery_indicators = responses.get("backup", False) or responses.get("disaster_recovery", False)
        monitoring = responses.get("monitoring", False)
        
        if recovery_indicators and monitoring:
            return "1-2 hours"
        elif recovery_indicators:
            return "2-4 hours"
        elif monitoring:
            return "4-8 hours"
        else:
            return "8+ hours"
        
    def _generate_pattern_based_recommendations(self, assessments: list) -> list:
        """Generate recommendations based on identified patterns"""
        recommendations = []
        
        # Check for common vulnerability patterns
        vulnerability_patterns = {}
        for assessment in assessments:
            subtype = assessment["node_subtype"]
            risk_score = assessment["risk_score"]
            
            if subtype not in vulnerability_patterns:
                vulnerability_patterns[subtype] = []
            vulnerability_patterns[subtype].append(risk_score)
        
        for subtype, scores in vulnerability_patterns.items():
            if len(scores) > 1 and sum(scores) / len(scores) > 7.0:
                recommendations.append(f"Pattern detected: All {subtype} nodes show high risk - review {subtype} security configuration standards")
        
        return recommendations
    
    def _initialize_expanded_templates(self) -> Dict[str, Dict]:
        """Initialize all 25+ node types with comprehensive templates"""
        templates = {}
        
        # ===== CLOUD INFRASTRUCTURE NODES =====
        
        # EC2 Instance
        templates["EC2"] = {
            "node_type": "Asset",
            "node_subtype": "EC2",
            "category": NodeCategory.CLOUD_INFRASTRUCTURE,
            "description": "Amazon EC2 Virtual Machine Instance",
            "required_branches": [
                SecurityBranchType.OS_HARDENING,
                SecurityBranchType.PATCH_MANAGEMENT,
                SecurityBranchType.ACCESS_CONTROL,
                SecurityBranchType.MONITORING,
                SecurityBranchType.ENCRYPTION
            ],
            "questionnaires": {
                QuestionnaireLevel.BASIC: [
                    {
                        "id": "ec2_os_type",
                        "question": "What operating system is running on this EC2 instance?",
                        "type": "single_choice",
                        "options": ["Amazon Linux 2", "Ubuntu", "Windows Server", "RHEL", "CentOS", "Custom AMI"],
                        "help_text": "Different OS types have varying security profiles and patch management requirements.",
                        "related_branch": SecurityBranchType.OS_HARDENING
                    },
                    {
                        "id": "ec2_instance_type",
                        "question": "What is the EC2 instance type and size?",
                        "type": "single_choice", 
                        "options": ["t3.micro", "t3.small", "m5.large", "c5.xlarge", "r5.2xlarge", "Other"],
                        "help_text": "Instance type affects performance, cost, and available security features.",
                        "related_branch": SecurityBranchType.CLOUD_SECURITY
                    },
                    {
                        "id": "ec2_public_ip",
                        "question": "Does this instance have a public IP address?",
                        "type": "boolean",
                        "help_text": "Public IPs increase attack surface and require additional security controls.",
                        "related_branch": SecurityBranchType.NETWORK_SECURITY
                    },
                    {
                        "id": "ec2_security_groups",
                        "question": "How are security groups configured?",
                        "type": "single_choice",
                        "options": ["Least Privilege (Minimal Ports)", "Standard Ports (22,80,443)", "Multiple Ports Open", "Wide Open (0.0.0.0/0)", "Unknown"],
                        "help_text": "Security groups act as virtual firewalls controlling inbound/outbound traffic.",
                        "related_branch": SecurityBranchType.FIREWALL
                    },
                    {
                        "id": "ec2_ssh_access",
                        "question": "How is SSH/RDP access configured?",
                        "type": "single_choice",
                        "options": ["Key-based Only", "Password + Key", "Password Only", "Disabled", "Unknown"],
                        "help_text": "SSH/RDP access methods significantly impact instance security.",
                        "related_branch": SecurityBranchType.AUTHENTICATION
                    }
                ],
                QuestionnaireLevel.ADVANCED: [
                    # Include all basic questions plus advanced ones
                    {
                        "id": "ec2_ebs_encryption",
                        "question": "Are EBS volumes encrypted at rest?",
                        "type": "single_choice",
                        "options": ["Yes - Customer Managed Keys", "Yes - AWS Managed Keys", "Partial Encryption", "No Encryption", "Unknown"],
                        "help_text": "EBS encryption protects data at rest using AES-256 encryption.",
                        "related_branch": SecurityBranchType.ENCRYPTION
                    },
                    {
                        "id": "ec2_iam_role",
                        "question": "Is an IAM role attached to this instance?",
                        "type": "single_choice",
                        "options": ["Yes - Least Privilege", "Yes - Broad Permissions", "Yes - Administrative", "No IAM Role", "Unknown"],
                        "help_text": "IAM roles provide secure access to AWS services without hardcoded credentials.",
                        "related_branch": SecurityBranchType.IAM
                    },
                    {
                        "id": "ec2_cloudwatch_monitoring",
                        "question": "What level of CloudWatch monitoring is enabled?",
                        "type": "single_choice",
                        "options": ["Detailed + Custom Metrics", "Detailed Monitoring", "Basic Monitoring", "No Monitoring", "Unknown"],
                        "help_text": "CloudWatch monitoring provides visibility into instance performance and security events.",
                        "related_branch": SecurityBranchType.MONITORING
                    },
                    {
                        "id": "ec2_patch_management",
                        "question": "How are OS patches managed?",
                        "type": "single_choice",
                        "options": ["AWS Systems Manager", "Automated Tools", "Manual Updates", "No Patch Management", "Unknown"],
                        "help_text": "Regular patching is critical for addressing security vulnerabilities.",
                        "related_branch": SecurityBranchType.PATCH_MANAGEMENT
                    },
                    {
                        "id": "ec2_antivirus",
                        "question": "Is antivirus/endpoint protection installed?",
                        "type": "single_choice",
                        "options": ["Enterprise EPP/EDR", "Basic Antivirus", "Cloud-native Protection", "No Protection", "Unknown"],
                        "help_text": "Endpoint protection helps detect and prevent malware infections.",
                        "related_branch": SecurityBranchType.MONITORING
                    }
                ],
                QuestionnaireLevel.EXPERT: [
                    {
                        "id": "ec2_incident_response_integration",
                        "question": "How is this instance integrated with incident response workflows?",
                        "type": "single_choice",
                        "options": ["Automated SOAR integration", "Manual playbooks", "Basic alerting", "No integration", "Unknown"],
                        "help_text": "Incident response integration ensures rapid response to security events.",
                        "related_branch": SecurityBranchType.INCIDENT_RESPONSE
                    },
                    {
                        "id": "ec2_vulnerability_assessment_schedule",
                        "question": "What is the vulnerability assessment schedule?",
                        "type": "single_choice",
                        "options": ["Continuous scanning", "Weekly scans", "Monthly scans", "Quarterly scans", "No regular scans"],
                        "help_text": "Regular vulnerability assessments are critical for maintaining security posture.",
                        "related_branch": SecurityBranchType.VULNERABILITY_SCANNING
                    },
                    {
                        "id": "ec2_compliance_framework_alignment",
                        "question": "Which compliance frameworks does this instance align with?",
                        "type": "multiple_choice",
                        "options": ["SOC 2", "ISO 27001", "PCI DSS", "HIPAA", "NIST", "CIS Controls", "None"],
                        "help_text": "Compliance framework alignment ensures adherence to security standards.",
                        "related_branch": SecurityBranchType.COMPLIANCE
                    },
                    {
                        "id": "ec2_network_micro_segmentation",
                        "question": "Is network micro-segmentation implemented?",
                        "type": "single_choice",
                        "options": ["Full micro-segmentation", "Partial segmentation", "Basic network isolation", "No segmentation", "Unknown"],
                        "help_text": "Micro-segmentation limits lateral movement in case of compromise.",
                        "related_branch": SecurityBranchType.NETWORK_SEGMENTATION
                    },
                    {
                        "id": "ec2_privilege_escalation_prevention",
                        "question": "What privilege escalation prevention measures are in place?",
                        "type": "multiple_choice",
                        "options": ["SELinux/AppArmor", "Sudo restrictions", "User account policies", "Kernel hardening", "Container isolation", "None"],
                        "help_text": "Privilege escalation prevention limits damage from compromised accounts.",
                        "related_branch": SecurityBranchType.ACCESS_CONTROL
                    },
                    {
                        "id": "ec2_data_classification_handling",
                        "question": "How is data classification implemented on this instance?",
                        "type": "single_choice",
                        "options": ["Automated classification", "Manual tagging", "Basic sensitivity levels", "No classification", "Unknown"],
                        "help_text": "Data classification ensures appropriate protection levels for different data types.",
                        "related_branch": SecurityBranchType.DATA_CLASSIFICATION
                    },
                    {
                        "id": "ec2_forensic_readiness",
                        "question": "What forensic readiness measures are implemented?",
                        "type": "multiple_choice",
                        "options": ["Comprehensive logging", "Memory dump capability", "Disk imaging", "Chain of custody", "Evidence preservation", "None"],
                        "help_text": "Forensic readiness enables effective investigation of security incidents.",
                        "related_branch": SecurityBranchType.INCIDENT_RESPONSE
                    },
                    {
                        "id": "ec2_threat_hunting_integration",
                        "question": "How is this instance integrated with threat hunting activities?",
                        "type": "single_choice",
                        "options": ["Active hunting integration", "Periodic analysis", "Alert-based review", "No hunting activities", "Unknown"],
                        "help_text": "Threat hunting integration enables proactive threat detection.",
                        "related_branch": SecurityBranchType.MONITORING
                    },
                    {
                        "id": "ec2_supply_chain_validation",
                        "question": "How is software supply chain validation performed?",
                        "type": "single_choice",
                        "options": ["Comprehensive validation", "Signature verification", "Basic checks", "No validation", "Unknown"],
                        "help_text": "Supply chain validation prevents installation of compromised software.",
                        "related_branch": SecurityBranchType.SUPPLY_CHAIN
                    },
                    {
                        "id": "ec2_zero_trust_implementation",
                        "question": "What zero trust principles are implemented?",
                        "type": "multiple_choice",
                        "options": ["Never trust, always verify", "Least privilege access", "Micro-segmentation", "Continuous monitoring", "Identity verification", "None"],
                        "help_text": "Zero trust implementation reduces attack surface and limits breach impact.",
                        "related_branch": SecurityBranchType.ACCESS_CONTROL
                    },
                    {
                        "id": "ec2_advanced_persistent_threat_detection",
                        "question": "What APT detection capabilities are deployed?",
                        "type": "single_choice",
                        "options": ["AI/ML-based detection", "Behavioral analysis", "Signature-based", "Basic monitoring", "No APT detection"],
                        "help_text": "APT detection is crucial for identifying sophisticated, long-term attacks.",
                        "related_branch": SecurityBranchType.MONITORING
                    },
                    {
                        "id": "ec2_security_orchestration",
                        "question": "How is security orchestration and automation implemented?",
                        "type": "single_choice",
                        "options": ["Full SOAR integration", "Partial automation", "Basic scripting", "Manual processes", "No orchestration"],
                        "help_text": "Security orchestration enables rapid, consistent response to threats.",
                        "related_branch": SecurityBranchType.INCIDENT_RESPONSE
                    },
                    {
                        "id": "ec2_insider_threat_monitoring",
                        "question": "What insider threat monitoring is in place?",
                        "type": "multiple_choice",
                        "options": ["User behavior analytics", "Privileged access monitoring", "Data access tracking", "Anomaly detection", "None"],
                        "help_text": "Insider threat monitoring detects malicious or negligent insider activities.",
                        "related_branch": SecurityBranchType.MONITORING
                    },
                    {
                        "id": "ec2_recovery_time_objective",
                        "question": "What is the Recovery Time Objective (RTO) for this instance?",
                        "type": "single_choice",
                        "options": ["< 1 hour", "1-4 hours", "4-24 hours", "> 24 hours", "Not defined"],
                        "help_text": "Defined RTO ensures appropriate backup and recovery capabilities.",
                        "related_branch": SecurityBranchType.BACKUP
                    },
                    {
                        "id": "ec2_security_metrics_kpis",
                        "question": "What security metrics and KPIs are tracked?",
                        "type": "multiple_choice",
                        "options": ["Mean time to detection", "Mean time to response", "Vulnerability remediation time", "Security incident count", "Compliance score", "None"],
                        "help_text": "Security metrics enable measurement and improvement of security posture.",
                        "related_branch": SecurityBranchType.MONITORING
                    },
                    {
                        "id": "ec2_third_party_risk_assessment",
                        "question": "How are third-party software risks assessed?",
                        "type": "single_choice",
                        "options": ["Comprehensive risk assessment", "Vendor security reviews", "Basic license checks", "No assessment", "Unknown"],
                        "help_text": "Third-party risk assessment is crucial for supply chain security.",
                        "related_branch": SecurityBranchType.SUPPLY_CHAIN
                    },
                    {
                        "id": "ec2_security_training_integration",
                        "question": "How are security training requirements integrated?",
                        "type": "single_choice",
                        "options": ["Mandatory training tracking", "Role-based training", "General awareness", "No training requirements", "Unknown"],
                        "help_text": "Security training integration ensures proper security practices by users.",
                        "related_branch": SecurityBranchType.COMPLIANCE
                    },
                    {
                        "id": "ec2_business_continuity_integration",
                        "question": "How is this instance integrated with business continuity plans?",
                        "type": "single_choice",
                        "options": ["Critical system designation", "Standard recovery procedures", "Basic backup inclusion", "No BCP integration", "Unknown"],
                        "help_text": "Business continuity integration ensures operational resilience.",
                        "related_branch": SecurityBranchType.BACKUP
                    },
                    {
                        "id": "ec2_regulatory_change_management",
                        "question": "How are regulatory changes managed for this instance?",
                        "type": "single_choice",
                        "options": ["Automated compliance monitoring", "Regular compliance reviews", "Manual tracking", "No change management", "Unknown"],
                        "help_text": "Regulatory change management ensures ongoing compliance.",
                        "related_branch": SecurityBranchType.COMPLIANCE
                    },
                    {
                        "id": "ec2_security_culture_integration",
                        "question": "How is security culture promoted for this instance?",
                        "type": "multiple_choice",
                        "options": ["Security champions program", "Regular security discussions", "Security awareness campaigns", "Security feedback loops", "None"],
                        "help_text": "Security culture integration promotes proactive security behaviors.",
                        "related_branch": SecurityBranchType.COMPLIANCE
                    },
                    {
                        "id": "ec2_emerging_threat_adaptation",
                        "question": "How does the security posture adapt to emerging threats?",
                        "type": "single_choice",
                        "options": ["Proactive threat intelligence", "Reactive updates", "Periodic reviews", "No adaptation process", "Unknown"],
                        "help_text": "Emerging threat adaptation ensures protection against new attack vectors.",
                        "related_branch": SecurityBranchType.MONITORING
                    },
                    {
                        "id": "ec2_security_investment_roi",
                        "question": "How is security investment ROI measured for this instance?",
                        "type": "single_choice",
                        "options": ["Quantitative risk reduction", "Cost-benefit analysis", "Compliance cost savings", "No ROI measurement", "Unknown"],
                        "help_text": "Security ROI measurement justifies and optimizes security investments.",
                        "related_branch": SecurityBranchType.COMPLIANCE
                    },
                    {
                        "id": "ec2_cross_platform_security_integration",
                        "question": "How is security integrated across different platforms?",
                        "type": "single_choice",
                        "options": ["Unified security platform", "Integrated SIEM", "Manual correlation", "Isolated systems", "Unknown"],
                        "help_text": "Cross-platform integration provides comprehensive security visibility.",
                        "related_branch": SecurityBranchType.MONITORING
                    },
                    {
                        "id": "ec2_quantum_computing_readiness",
                        "question": "What quantum computing readiness measures are in place?",
                        "type": "single_choice",
                        "options": ["Post-quantum cryptography", "Quantum-safe algorithms", "Future migration planning", "No quantum readiness", "Unknown"],
                        "help_text": "Quantum readiness prepares for future cryptographic threats.",
                        "related_branch": SecurityBranchType.ENCRYPTION
                    },
                    {
                        "id": "ec2_ai_ml_security_integration",
                        "question": "How is AI/ML integrated into security operations?",
                        "type": "multiple_choice",
                        "options": ["Automated threat detection", "Behavioral analysis", "Predictive analytics", "Anomaly detection", "None"],
                        "help_text": "AI/ML integration enhances threat detection and response capabilities.",
                        "related_branch": SecurityBranchType.MONITORING
                    }
                ]
            },
            "dependencies": {
                "ec2_database_connection": "RDS",
                "ec2_load_balancer": "LoadBalancer",
                "ec2_backup_enabled": "S3"
            },
            "threat_intelligence": ThreatIntelligence(
                cve_count=150,
                recent_threats=["SSH Brute Force", "Privilege Escalation", "Cryptomining"],
                attack_vectors=["Remote Code Execution", "Privilege Escalation", "Data Exfiltration"],
                mitre_techniques=["T1078", "T1190", "T1055", "T1083"],
                threat_actors=["APT29", "Lazarus", "FIN7"]
            ),
            "risk_factors": {
                "public_ip": 3.0,
                "wide_open_sg": 4.0,
                "password_auth": 2.5,
                "no_encryption": 2.0,
                "no_monitoring": 1.5,
                "no_patching": 3.5
            }
        }
        
        # Lambda Function
        templates["Lambda"] = {
            "node_type": "Asset",
            "node_subtype": "Lambda",
            "category": NodeCategory.COMPUTE_SERVICES,
            "description": "AWS Lambda Serverless Function",
            "required_branches": [
                SecurityBranchType.SERVERLESS_SECURITY,
                SecurityBranchType.IAM,
                SecurityBranchType.SECRETS_MANAGEMENT,
                SecurityBranchType.CODE_SECURITY,
                SecurityBranchType.MONITORING
            ],
            "questionnaires": {
                QuestionnaireLevel.BASIC: [
                    {
                        "id": "lambda_runtime",
                        "question": "What runtime is used for this Lambda function?",
                        "type": "single_choice",
                        "options": ["Python 3.11", "Node.js 18", "Java 17", "C# .NET 6", ".NET Core", "Go", "Ruby", "Custom Runtime"],
                        "help_text": "Different runtimes have varying security characteristics and update cycles.",
                        "related_branch": SecurityBranchType.SERVERLESS_SECURITY
                    },
                    {
                        "id": "lambda_execution_role",
                        "question": "How is the Lambda execution role configured?",
                        "type": "single_choice",
                        "options": ["Least Privilege (Minimal Permissions)", "Standard Permissions", "Broad Permissions", "Administrative Access", "Unknown"],
                        "help_text": "Execution roles determine what AWS services the function can access.",
                        "related_branch": SecurityBranchType.IAM
                    },
                    {
                        "id": "lambda_environment_variables",
                        "question": "How are sensitive values handled in environment variables?",
                        "type": "single_choice",
                        "options": ["AWS Secrets Manager", "Parameter Store", "KMS Encrypted", "Plain Text", "No Sensitive Data"],
                        "help_text": "Proper secrets management prevents credential exposure in serverless functions.",
                        "related_branch": SecurityBranchType.SECRETS_MANAGEMENT
                    },
                    {
                        "id": "lambda_vpc_config",
                        "question": "Is the Lambda function deployed in a VPC?",
                        "type": "single_choice",
                        "options": ["Yes - Private Subnets", "Yes - Public Subnets", "No VPC", "Unknown"],
                        "help_text": "VPC deployment provides network isolation but affects cold start performance.",
                        "related_branch": SecurityBranchType.NETWORK_SECURITY
                    },
                    {
                        "id": "lambda_logging",
                        "question": "What logging level is configured?",
                        "type": "single_choice",
                        "options": ["Comprehensive (Debug)", "Standard (Info)", "Minimal (Error)", "No Logging", "Unknown"],
                        "help_text": "Proper logging is essential for security monitoring and incident response.",
                        "related_branch": SecurityBranchType.LOGGING
                    }
                ],
                QuestionnaireLevel.ADVANCED: [
                    {
                        "id": "lambda_code_signing",
                        "question": "Is code signing enabled for this Lambda function?",
                        "type": "single_choice",
                        "options": ["Yes - AWS Signer", "Yes - Third-party", "No Code Signing", "Unknown"],
                        "help_text": "Code signing ensures function code integrity and authenticity.",
                        "related_branch": SecurityBranchType.CODE_SECURITY
                    },
                    {
                        "id": "lambda_dead_letter_queue",
                        "question": "Is a Dead Letter Queue (DLQ) configured?",
                        "type": "single_choice",
                        "options": ["Yes - SQS DLQ", "Yes - SNS DLQ", "No DLQ", "Unknown"],
                        "help_text": "DLQs help handle failed executions and prevent data loss.",
                        "related_branch": SecurityBranchType.MONITORING
                    },
                    {
                        "id": "lambda_reserved_concurrency",
                        "question": "Is reserved concurrency configured?",
                        "type": "single_choice",
                        "options": ["Yes - Conservative Limit", "Yes - High Limit", "No Limit Set", "Unknown"],
                        "help_text": "Reserved concurrency prevents resource exhaustion attacks.",
                        "related_branch": SecurityBranchType.SERVERLESS_SECURITY
                    },
                    {
                        "id": "lambda_layers_security",
                        "question": "How are Lambda layers managed for security?",
                        "type": "single_choice",
                        "options": ["Verified Internal Layers", "AWS Managed Layers", "Third-party Layers", "No Layers Used", "Unknown"],
                        "help_text": "Lambda layers can introduce security risks through dependencies.",
                        "related_branch": SecurityBranchType.SUPPLY_CHAIN
                    },
                    {
                        "id": "lambda_x_ray_tracing",
                        "question": "Is AWS X-Ray tracing enabled?",
                        "type": "single_choice",
                        "options": ["Active Tracing", "Passive Tracing", "No Tracing", "Unknown"],
                        "help_text": "X-Ray tracing provides visibility into function execution and dependencies.",
                        "related_branch": SecurityBranchType.MONITORING
                    },
                    {
                        "id": "lambda_function_url_security",
                        "question": "If using Function URLs, what authentication is configured?",
                        "type": "single_choice",
                        "options": ["AWS IAM Auth", "No Authentication", "Not Using Function URLs", "Unknown"],
                        "help_text": "Function URLs without proper authentication can expose functions publicly.",
                        "related_branch": SecurityBranchType.AUTHENTICATION
                    },
                    {
                        "id": "lambda_dependency_scanning",
                        "question": "Are function dependencies scanned for vulnerabilities?",
                        "type": "single_choice",
                        "options": ["Automated Scanning", "Manual Review", "Third-party Tools", "No Scanning", "Unknown"],
                        "help_text": "Dependency scanning helps identify vulnerable packages in function code.",
                        "related_branch": SecurityBranchType.VULNERABILITY_SCANNING
                    },
                    {
                        "id": "lambda_timeout_configuration",
                        "question": "How is the function timeout configured?",
                        "type": "single_choice",
                        "options": ["Conservative (< 30s)", "Moderate (30s-5min)", "High (> 5min)", "Default (3s)", "Unknown"],
                        "help_text": "Proper timeout configuration prevents resource exhaustion and hanging executions.",
                        "related_branch": SecurityBranchType.SERVERLESS_SECURITY
                    },
                    {
                        "id": "lambda_memory_allocation",
                        "question": "How is memory allocation configured for security?",
                        "type": "single_choice",
                        "options": ["Right-sized for workload", "Over-provisioned", "Under-provisioned", "Default settings", "Unknown"],
                        "help_text": "Proper memory allocation prevents resource exhaustion and performance issues.",
                        "related_branch": SecurityBranchType.SERVERLESS_SECURITY
                    },
                    {
                        "id": "lambda_event_source_security",
                        "question": "How are event sources secured?",
                        "type": "multiple_choice",
                        "options": ["Resource-based policies", "Event filtering", "Encryption in transit", "Access logging", "None"],
                        "help_text": "Event source security prevents unauthorized function invocations.",
                        "related_branch": SecurityBranchType.ACCESS_CONTROL
                    },
                    {
                        "id": "lambda_error_handling",
                        "question": "How is error handling implemented for security?",
                        "type": "single_choice",
                        "options": ["Comprehensive error handling", "Basic try-catch", "Minimal handling", "No error handling", "Unknown"],
                        "help_text": "Proper error handling prevents information disclosure through error messages.",
                        "related_branch": SecurityBranchType.CODE_SECURITY
                    },
                    {
                        "id": "lambda_provisioned_concurrency",
                        "question": "Is provisioned concurrency used for consistent performance?",
                        "type": "single_choice",
                        "options": ["Yes - Security-critical functions", "Yes - All functions", "No provisioned concurrency", "Unknown"],
                        "help_text": "Provisioned concurrency reduces cold start latency and improves security response times.",
                        "related_branch": SecurityBranchType.SERVERLESS_SECURITY
                    },
                    {
                        "id": "lambda_extension_security",
                        "question": "If using Lambda extensions, how are they secured?",
                        "type": "single_choice",
                        "options": ["AWS managed extensions", "Verified third-party", "Custom extensions", "No extensions", "Unknown"],
                        "help_text": "Lambda extensions can introduce security risks and should be carefully managed.",
                        "related_branch": SecurityBranchType.SUPPLY_CHAIN
                    },
                    {
                        "id": "lambda_vpc_endpoints",
                        "question": "Are VPC endpoints used for AWS service access?",
                        "type": "single_choice",
                        "options": ["Yes - Interface endpoints", "Yes - Gateway endpoints", "No VPC endpoints", "Not applicable", "Unknown"],
                        "help_text": "VPC endpoints provide secure access to AWS services without internet routing.",
                        "related_branch": SecurityBranchType.NETWORK_SECURITY
                    },
                    {
                        "id": "lambda_secrets_rotation",
                        "question": "Are secrets automatically rotated for this function?",
                        "type": "single_choice",
                        "options": ["Automatic rotation", "Manual rotation", "No rotation", "No secrets used", "Unknown"],
                        "help_text": "Regular secret rotation reduces the impact of credential compromise.",
                        "related_branch": SecurityBranchType.SECRETS_MANAGEMENT
                    },
                    {
                        "id": "lambda_cloudwatch_insights",
                        "question": "Is CloudWatch Logs Insights used for security analysis?",
                        "type": "single_choice",
                        "options": ["Yes - Active monitoring", "Yes - Occasional use", "No Insights", "Unknown"],
                        "help_text": "CloudWatch Logs Insights enables advanced log analysis for security events.",
                        "related_branch": SecurityBranchType.MONITORING
                    },
                    {
                        "id": "lambda_performance_monitoring",
                        "question": "What performance monitoring is in place for security?",
                        "type": "multiple_choice",
                        "options": ["CloudWatch metrics", "Custom metrics", "Third-party APM", "Performance alarms", "None"],
                        "help_text": "Performance monitoring can detect security-related resource exhaustion attacks.",
                        "related_branch": SecurityBranchType.MONITORING
                    }
                ],
                QuestionnaireLevel.EXPERT: [
                    {
                        "id": "lambda_serverless_security_architecture",
                        "question": "How is serverless security architecture designed for this function?",
                        "type": "single_choice",
                        "options": ["Defense in depth", "Zero trust serverless", "Basic isolation", "No specific architecture", "Unknown"],
                        "help_text": "Serverless security architecture ensures comprehensive protection across all layers.",
                        "related_branch": SecurityBranchType.SERVERLESS_SECURITY
                    },
                    {
                        "id": "lambda_advanced_threat_modeling",
                        "question": "Has advanced threat modeling been performed for this function?",
                        "type": "single_choice",
                        "options": ["Comprehensive STRIDE analysis", "Basic threat analysis", "Informal review", "No threat modeling", "Unknown"],
                        "help_text": "Advanced threat modeling identifies specific serverless attack vectors.",
                        "related_branch": SecurityBranchType.SERVERLESS_SECURITY
                    },
                    {
                        "id": "lambda_runtime_security_hardening",
                        "question": "What runtime security hardening measures are implemented?",
                        "type": "multiple_choice",
                        "options": ["Custom runtime patches", "Security-focused dependencies", "Runtime sandboxing", "Resource constraints", "None"],
                        "help_text": "Runtime hardening protects against execution environment vulnerabilities.",
                        "related_branch": SecurityBranchType.SERVERLESS_SECURITY
                    },
                    {
                        "id": "lambda_supply_chain_attestation",
                        "question": "How is software supply chain attestation implemented?",
                        "type": "single_choice",
                        "options": ["Full SLSA compliance", "Partial attestation", "Basic verification", "No attestation", "Unknown"],
                        "help_text": "Supply chain attestation ensures integrity of function dependencies.",
                        "related_branch": SecurityBranchType.SUPPLY_CHAIN
                    },
                    {
                        "id": "lambda_zero_day_protection",
                        "question": "What zero-day protection mechanisms are in place?",
                        "type": "multiple_choice",
                        "options": ["Behavioral monitoring", "Runtime protection", "Anomaly detection", "Sandboxing", "None"],
                        "help_text": "Zero-day protection defends against unknown vulnerabilities.",
                        "related_branch": SecurityBranchType.SERVERLESS_SECURITY
                    },
                    {
                        "id": "lambda_advanced_logging_analysis",
                        "question": "What advanced logging analysis is performed?",
                        "type": "single_choice",
                        "options": ["AI-powered analysis", "Machine learning detection", "Pattern recognition", "Basic log review", "No analysis"],
                        "help_text": "Advanced logging analysis identifies sophisticated attack patterns.",
                        "related_branch": SecurityBranchType.MONITORING
                    },
                    {
                        "id": "lambda_incident_forensics_capability",
                        "question": "What incident forensics capabilities are available?",
                        "type": "multiple_choice",
                        "options": ["Execution tracing", "Memory analysis", "Code path reconstruction", "Timeline analysis", "None"],
                        "help_text": "Forensics capabilities enable detailed incident investigation in serverless environments.",
                        "related_branch": SecurityBranchType.INCIDENT_RESPONSE
                    },
                    {
                        "id": "lambda_compliance_automation",
                        "question": "How is compliance automated for this function?",
                        "type": "single_choice",
                        "options": ["Continuous compliance monitoring", "Automated policy enforcement", "Regular compliance scans", "Manual compliance checks", "No automation"],
                        "help_text": "Compliance automation ensures consistent adherence to regulatory requirements.",
                        "related_branch": SecurityBranchType.COMPLIANCE
                    },
                    {
                        "id": "lambda_advanced_encryption_patterns",
                        "question": "What advanced encryption patterns are implemented?",
                        "type": "multiple_choice",
                        "options": ["Envelope encryption", "Client-side encryption", "Field-level encryption", "Homomorphic encryption", "None"],
                        "help_text": "Advanced encryption patterns provide enhanced data protection in serverless environments.",
                        "related_branch": SecurityBranchType.ENCRYPTION
                    },
                    {
                        "id": "lambda_serverless_attack_detection",
                        "question": "How are serverless-specific attacks detected?",
                        "type": "single_choice",
                        "options": ["Specialized serverless SIEM", "Custom detection rules", "Generic monitoring", "No specific detection", "Unknown"],
                        "help_text": "Serverless attack detection addresses unique serverless threat vectors.",
                        "related_branch": SecurityBranchType.MONITORING
                    },
                    {
                        "id": "lambda_quantum_safe_cryptography",
                        "question": "Is quantum-safe cryptography implemented?",
                        "type": "single_choice",
                        "options": ["Post-quantum algorithms", "Quantum-resistant protocols", "Hybrid approach", "Classical cryptography only", "Unknown"],
                        "help_text": "Quantum-safe cryptography protects against future quantum computing threats.",
                        "related_branch": SecurityBranchType.ENCRYPTION
                    },
                    {
                        "id": "lambda_advanced_dependency_management",
                        "question": "How is advanced dependency management implemented?",
                        "type": "multiple_choice",
                        "options": ["Software bill of materials", "Dependency pinning", "Vulnerability scanning", "License compliance", "None"],
                        "help_text": "Advanced dependency management reduces third-party security risks.",
                        "related_branch": SecurityBranchType.SUPPLY_CHAIN
                    },
                    {
                        "id": "lambda_business_logic_security",
                        "question": "How is business logic security validated?",
                        "type": "single_choice",
                        "options": ["Formal verification", "Comprehensive testing", "Code review", "Basic validation", "No validation"],
                        "help_text": "Business logic security prevents exploitation of application-specific vulnerabilities.",
                        "related_branch": SecurityBranchType.CODE_SECURITY
                    },
                    {
                        "id": "lambda_advanced_rate_limiting",
                        "question": "What advanced rate limiting mechanisms are implemented?",
                        "type": "multiple_choice",
                        "options": ["Adaptive rate limiting", "Distributed rate limiting", "User-based limits", "Resource-based limits", "None"],
                        "help_text": "Advanced rate limiting protects against sophisticated abuse patterns.",
                        "related_branch": SecurityBranchType.RATE_LIMITING
                    },
                    {
                        "id": "lambda_serverless_security_metrics",
                        "question": "What serverless-specific security metrics are tracked?",
                        "type": "multiple_choice",
                        "options": ["Cold start security time", "Function invocation patterns", "Resource utilization anomalies", "Execution path analysis", "None"],
                        "help_text": "Serverless security metrics provide visibility into function-specific security events.",
                        "related_branch": SecurityBranchType.MONITORING
                    },
                    {
                        "id": "lambda_advanced_secret_management",
                        "question": "How is advanced secret management implemented?",
                        "type": "single_choice",
                        "options": ["Runtime secret injection", "Dynamic secret generation", "Secret versioning", "Basic secret storage", "No secret management"],
                        "help_text": "Advanced secret management minimizes secret exposure in serverless environments.",
                        "related_branch": SecurityBranchType.SECRETS_MANAGEMENT
                    },
                    {
                        "id": "lambda_serverless_governance",
                        "question": "What serverless governance framework is in place?",
                        "type": "single_choice",
                        "options": ["Comprehensive governance", "Policy-based controls", "Basic guidelines", "No governance", "Unknown"],
                        "help_text": "Serverless governance ensures consistent security practices across functions.",
                        "related_branch": SecurityBranchType.COMPLIANCE
                    },
                    {
                        "id": "lambda_advanced_monitoring_correlation",
                        "question": "How is advanced monitoring correlation implemented?",
                        "type": "single_choice",
                        "options": ["Cross-service correlation", "Multi-dimensional analysis", "Basic correlation", "No correlation", "Unknown"],
                        "help_text": "Advanced correlation provides comprehensive visibility across serverless architectures.",
                        "related_branch": SecurityBranchType.MONITORING
                    },
                    {
                        "id": "lambda_serverless_disaster_recovery",
                        "question": "What serverless disaster recovery capabilities are implemented?",
                        "type": "multiple_choice",
                        "options": ["Multi-region deployment", "Function versioning", "State backup", "Automated failover", "None"],
                        "help_text": "Serverless disaster recovery ensures function availability during incidents.",
                        "related_branch": SecurityBranchType.BACKUP
                    },
                    {
                        "id": "lambda_advanced_performance_security",
                        "question": "How is performance security optimized?",
                        "type": "single_choice",
                        "options": ["Security-optimized performance", "Balanced approach", "Performance-first", "No optimization", "Unknown"],
                        "help_text": "Performance security balances security controls with serverless performance requirements.",
                        "related_branch": SecurityBranchType.SERVERLESS_SECURITY
                    },
                    {
                        "id": "lambda_serverless_threat_intelligence",
                        "question": "How is serverless threat intelligence integrated?",
                        "type": "single_choice",
                        "options": ["Serverless-specific feeds", "Generic threat intel", "Basic indicators", "No threat intelligence", "Unknown"],
                        "help_text": "Serverless threat intelligence provides relevant threat information for function-based architectures.",
                        "related_branch": SecurityBranchType.MONITORING
                    },
                    {
                        "id": "lambda_advanced_testing_security",
                        "question": "What advanced security testing is performed?",
                        "type": "multiple_choice",
                        "options": ["Serverless penetration testing", "Chaos engineering", "Security fuzzing", "Load testing", "None"],
                        "help_text": "Advanced security testing validates serverless security under various conditions.",
                        "related_branch": SecurityBranchType.VULNERABILITY_SCANNING
                    },
                    {
                        "id": "lambda_serverless_security_culture",
                        "question": "How is serverless security culture promoted?",
                        "type": "single_choice",
                        "options": ["Serverless security training", "Security-first development", "Basic awareness", "No specific culture", "Unknown"],
                        "help_text": "Serverless security culture ensures developers understand unique serverless security challenges.",
                        "related_branch": SecurityBranchType.COMPLIANCE
                    },
                    {
                        "id": "lambda_future_security_roadmap",
                        "question": "Is there a future security roadmap for serverless?",
                        "type": "single_choice",
                        "options": ["Comprehensive roadmap", "Technology evolution planning", "Basic future planning", "No roadmap", "Unknown"],
                        "help_text": "Future security roadmap ensures preparedness for evolving serverless security challenges.",
                        "related_branch": SecurityBranchType.COMPLIANCE
                    }
                ]
            },
            "threat_intelligence": ThreatIntelligence(
                cve_count=45,
                recent_threats=["Code Injection", "Dependency Vulnerabilities", "Over-privileged Functions"],
                attack_vectors=["Function Injection", "Event Manipulation", "Resource Exhaustion"],
                mitre_techniques=["T1055", "T1078", "T1133"],
                threat_actors=["Script Kiddies", "APT Groups"]
            )
        }
        
        # S3 Bucket
        templates["S3"] = {
            "node_type": "Asset", 
            "node_subtype": "S3",
            "category": NodeCategory.DATA_STORAGE,
            "description": "Amazon S3 Storage Bucket",
            "required_branches": [
                SecurityBranchType.ACCESS_CONTROL,
                SecurityBranchType.ENCRYPTION,
                SecurityBranchType.DATA_CLASSIFICATION,
                SecurityBranchType.BACKUP,
                SecurityBranchType.MONITORING
            ],
            "questionnaires": {
                QuestionnaireLevel.BASIC: [
                    {
                        "id": "s3_public_access",
                        "question": "Is this S3 bucket configured for public access?",
                        "type": "single_choice",
                        "options": ["Completely Private", "Public Read Only", "Public Read/Write", "Unknown Configuration"],
                        "help_text": "Public S3 buckets are a common source of data breaches.",
                        "related_branch": SecurityBranchType.ACCESS_CONTROL
                    },
                    {
                        "id": "s3_encryption",
                        "question": "What encryption is configured for objects?",
                        "type": "single_choice",
                        "options": ["SSE-KMS (Customer Managed)", "SSE-KMS (AWS Managed)", "SSE-S3", "No Encryption", "Unknown"],
                        "help_text": "S3 encryption protects data at rest from unauthorized access.",
                        "related_branch": SecurityBranchType.ENCRYPTION
                    },
                    {
                        "id": "s3_versioning",
                        "question": "Is object versioning enabled?",
                        "type": "boolean",
                        "help_text": "Versioning helps protect against accidental deletion and ransomware.",
                        "related_branch": SecurityBranchType.BACKUP
                    },
                    {
                        "id": "s3_data_type",
                        "question": "What type of data is stored in this bucket?",
                        "type": "single_choice",
                        "options": ["Public Content", "Internal Documents", "Customer Data", "Financial Records", "Healthcare Data", "Classified Information"],
                        "help_text": "Data classification determines required security controls.",
                        "related_branch": SecurityBranchType.DATA_CLASSIFICATION
                    },
                    {
                        "id": "s3_access_logging",
                        "question": "Is access logging enabled?",
                        "type": "boolean",
                        "help_text": "Access logs help track who accessed what data and when.",
                        "related_branch": SecurityBranchType.LOGGING
                    }
                ]
            },
            "threat_intelligence": ThreatIntelligence(
                cve_count=25,
                recent_threats=["Data Exposure", "Bucket Hijacking", "Ransomware"],
                attack_vectors=["Misconfiguration", "Credential Theft", "Privilege Escalation"],
                mitre_techniques=["T1530", "T1078", "T1083"],
                threat_actors=["Cybercriminals", "Insider Threats"]
            )
        }
        
        # RDS Database
        templates["RDS"] = {
            "node_type": "Asset",
            "node_subtype": "RDS", 
            "category": NodeCategory.DATA_STORAGE,
            "description": "Amazon RDS Database Instance",
            "required_branches": [
                SecurityBranchType.DATABASE,
                SecurityBranchType.ENCRYPTION,
                SecurityBranchType.ACCESS_CONTROL,
                SecurityBranchType.BACKUP,
                SecurityBranchType.MONITORING
            ],
            "questionnaires": {
                QuestionnaireLevel.BASIC: [
                    {
                        "id": "rds_engine",
                        "question": "What database engine is being used?",
                        "type": "single_choice",
                        "options": ["MySQL", "PostgreSQL", "MariaDB", "Oracle", "SQL Server", "Aurora MySQL", "Aurora PostgreSQL"],
                        "help_text": "Different database engines have different security features and vulnerabilities.",
                        "related_branch": SecurityBranchType.DATABASE
                    },
                    {
                        "id": "rds_public_access",
                        "question": "Is the RDS instance publicly accessible?",
                        "type": "boolean",
                        "help_text": "Publicly accessible databases have higher attack surface.",
                        "related_branch": SecurityBranchType.NETWORK_SECURITY
                    },
                    {
                        "id": "rds_encryption_at_rest",
                        "question": "Is encryption at rest enabled?",
                        "type": "single_choice",
                        "options": ["Yes - Customer Managed KMS", "Yes - AWS Managed", "No", "Unknown"],
                        "help_text": "Encryption at rest protects stored database data.",
                        "related_branch": SecurityBranchType.ENCRYPTION
                    },
                    {
                        "id": "rds_backup_retention",
                        "question": "What is the backup retention period?",
                        "type": "single_choice",
                        "options": ["35 days", "7-30 days", "1-7 days", "No Backups", "Unknown"],
                        "help_text": "Longer retention periods provide better recovery options.",
                        "related_branch": SecurityBranchType.BACKUP
                    },
                    {
                        "id": "rds_monitoring",
                        "question": "What monitoring is configured?",
                        "type": "multiple_choice",
                        "options": ["Performance Insights", "Enhanced Monitoring", "CloudWatch", "Database Activity Streams", "None"],
                        "help_text": "Comprehensive monitoring helps detect security issues.",
                        "related_branch": SecurityBranchType.MONITORING
                    }
                ]
            },
            "threat_intelligence": ThreatIntelligence(
                cve_count=89,
                recent_threats=["SQL Injection", "Privilege Escalation", "Data Exfiltration"],
                attack_vectors=["Authentication Bypass", "Buffer Overflow", "Configuration Exploit"],
                mitre_techniques=["T1190", "T1078", "T1005"],
                threat_actors=["APT40", "FIN7", "Conti"]
            )
        }
        
        # VPC (Virtual Private Cloud)
        templates["VPC"] = {
            "node_type": "Asset",
            "node_subtype": "VPC",
            "category": NodeCategory.NETWORK_COMPONENTS,
            "description": "Amazon Virtual Private Cloud",
            "required_branches": [
                SecurityBranchType.NETWORK_SECURITY,
                SecurityBranchType.NETWORK_SEGMENTATION,
                SecurityBranchType.FIREWALL,
                SecurityBranchType.MONITORING,
                SecurityBranchType.ACCESS_CONTROL
            ],
            "questionnaires": {
                QuestionnaireLevel.BASIC: [
                    {
                        "id": "vpc_cidr_block",
                        "question": "What is the VPC CIDR block size?",
                        "type": "single_choice",
                        "options": ["/16 (65,536 IPs)", "/20 (4,096 IPs)", "/24 (256 IPs)", "/28 (16 IPs)", "Custom Range"],
                        "help_text": "CIDR block size affects network segmentation and scalability.",
                        "related_branch": SecurityBranchType.NETWORK_SEGMENTATION
                    },
                    {
                        "id": "vpc_subnets",
                        "question": "How are subnets configured?",
                        "type": "single_choice",
                        "options": ["Public + Private Subnets", "Private Subnets Only", "Public Subnets Only", "Single Subnet", "Unknown"],
                        "help_text": "Proper subnet design provides network isolation and security.",
                        "related_branch": SecurityBranchType.NETWORK_SEGMENTATION
                    },
                    {
                        "id": "vpc_flow_logs",
                        "question": "Are VPC Flow Logs enabled?",
                        "type": "single_choice",
                        "options": ["Yes - All Traffic", "Yes - Rejected Traffic Only", "Yes - Accepted Traffic Only", "No Flow Logs", "Unknown"],
                        "help_text": "Flow logs provide network traffic visibility for security analysis.",
                        "related_branch": SecurityBranchType.MONITORING
                    },
                    {
                        "id": "vpc_nat_gateway",
                        "question": "How is outbound internet access configured for private subnets?",
                        "type": "single_choice",
                        "options": ["NAT Gateway", "NAT Instance", "No Outbound Access", "Direct Internet Access", "Unknown"],
                        "help_text": "NAT Gateways provide secure outbound internet access for private resources.",
                        "related_branch": SecurityBranchType.NETWORK_SECURITY
                    },
                    {
                        "id": "vpc_endpoints",
                        "question": "Are VPC endpoints configured for AWS services?",
                        "type": "single_choice",
                        "options": ["Gateway + Interface Endpoints", "Gateway Endpoints Only", "Interface Endpoints Only", "No VPC Endpoints", "Unknown"],
                        "help_text": "VPC endpoints provide private connectivity to AWS services.",
                        "related_branch": SecurityBranchType.NETWORK_SECURITY
                    }
                ]
            },
            "threat_intelligence": ThreatIntelligence(
                cve_count=12,
                recent_threats=["Network Reconnaissance", "Lateral Movement", "Traffic Interception"],
                attack_vectors=["Misconfiguration", "Privilege Escalation", "Network Scanning"],
                mitre_techniques=["T1018", "T1083", "T1090"],
                threat_actors=["Advanced Persistent Threats", "Insider Threats"]
            )
        }
        
        # ===== SECURITY SERVICES =====
        
        # WAF (Web Application Firewall)
        templates["WAF"] = {
            "node_type": "Control",
            "node_subtype": "WAF",
            "category": NodeCategory.SECURITY_SERVICES,
            "description": "Web Application Firewall",
            "required_branches": [
                SecurityBranchType.WAF,
                SecurityBranchType.MONITORING,
                SecurityBranchType.LOGGING,
                SecurityBranchType.RATE_LIMITING
            ],
            "questionnaires": {
                QuestionnaireLevel.BASIC: [
                    {
                        "id": "waf_type",
                        "question": "What type of WAF is deployed?",
                        "type": "single_choice",
                        "options": ["AWS WAF", "CloudFlare", "F5 BIG-IP", "Imperva", "Akamai", "Open Source", "Custom"],
                        "help_text": "Different WAF solutions provide varying levels of protection.",
                        "related_branch": SecurityBranchType.WAF
                    },
                    {
                        "id": "waf_rule_sets",
                        "question": "What rule sets are enabled?",
                        "type": "multiple_choice",
                        "options": ["OWASP Core Rule Set", "AWS Managed Rules", "SQL Injection Protection", "XSS Protection", "Rate Limiting", "Custom Rules"],
                        "help_text": "Comprehensive rule sets provide protection against common attacks.",
                        "related_branch": SecurityBranchType.WAF
                    },
                    {
                        "id": "waf_mode",
                        "question": "What is the WAF operating mode?",
                        "type": "single_choice",
                        "options": ["Block Mode", "Monitor Mode", "Mixed Mode", "Unknown"],
                        "help_text": "Block mode provides active protection, monitor mode provides visibility only.",
                        "related_branch": SecurityBranchType.WAF
                    },
                    {
                        "id": "waf_logging",
                        "question": "Is WAF logging configured?",
                        "type": "single_choice",
                        "options": ["All Requests", "Blocked Requests Only", "Sampled Requests", "No Logging", "Unknown"],
                        "help_text": "WAF logs are essential for security analysis and tuning.",
                        "related_branch": SecurityBranchType.LOGGING
                    }
                ]
            },
            "threat_intelligence": ThreatIntelligence(
                cve_count=8,
                recent_threats=["WAF Bypass", "Rule Evasion", "DDoS Attacks"],
                attack_vectors=["SQL Injection", "XSS", "Path Traversal", "HTTP Smuggling"],
                mitre_techniques=["T1190", "T1059", "T1055"],
                threat_actors=["Web Application Attackers", "Script Kiddies"]
            )
        }
        
        # IAM (Identity and Access Management)
        templates["IAM"] = {
            "node_type": "Control",
            "node_subtype": "IAM",
            "category": NodeCategory.SECURITY_SERVICES,
            "description": "Identity and Access Management Service",
            "required_branches": [
                SecurityBranchType.IAM,
                SecurityBranchType.AUTHENTICATION,
                SecurityBranchType.AUTHORIZATION,
                SecurityBranchType.MFA,
                SecurityBranchType.MONITORING
            ],
            "questionnaires": {
                QuestionnaireLevel.BASIC: [
                    {
                        "id": "iam_users_count",
                        "question": "How many IAM users are configured?",
                        "type": "single_choice",
                        "options": ["0-10 Users", "11-50 Users", "51-200 Users", "200+ Users", "Unknown"],
                        "help_text": "Large numbers of IAM users increase complexity and attack surface.",
                        "related_branch": SecurityBranchType.IAM
                    },
                    {
                        "id": "iam_root_account",
                        "question": "How is the root account secured?",
                        "type": "multiple_choice",
                        "options": ["MFA Enabled", "Strong Password", "Access Keys Deleted", "Rarely Used", "Hardware Security Key"],
                        "help_text": "Root account compromise can lead to complete AWS account takeover.",
                        "related_branch": SecurityBranchType.AUTHENTICATION
                    },
                    {
                        "id": "iam_password_policy",
                        "question": "What password policy is enforced?",
                        "type": "single_choice",
                        "options": ["Strong (12+ chars, complexity)", "Moderate (8+ chars)", "Basic (6+ chars)", "No Policy", "Unknown"],
                        "help_text": "Strong password policies reduce credential-based attacks.",
                        "related_branch": SecurityBranchType.AUTHENTICATION
                    },
                    {
                        "id": "iam_mfa_enforcement",
                        "question": "Is MFA enforced for users?",
                        "type": "single_choice",
                        "options": ["All Users", "Privileged Users Only", "Optional", "Not Enforced", "Unknown"],
                        "help_text": "MFA significantly reduces the risk of credential compromise.",
                        "related_branch": SecurityBranchType.MFA
                    },
                    {
                        "id": "iam_least_privilege",
                        "question": "Are least privilege principles followed?",
                        "type": "single_choice",
                        "options": ["Strictly Enforced", "Generally Followed", "Partially Implemented", "Not Implemented", "Unknown"],
                        "help_text": "Least privilege minimizes potential damage from compromised accounts.",
                        "related_branch": SecurityBranchType.AUTHORIZATION
                    }
                ]
            },
            "threat_intelligence": ThreatIntelligence(
                cve_count=23,
                recent_threats=["Credential Stuffing", "Privilege Escalation", "Account Takeover"],
                attack_vectors=["Weak Passwords", "MFA Bypass", "Token Theft", "Social Engineering"],
                mitre_techniques=["T1078", "T1110", "T1556", "T1134"],
                threat_actors=["APT29", "Lazarus", "FIN6"]
            )
        }
        
        # ===== CONTAINER & DEVOPS NODES =====
        
        # Kubernetes Cluster
        templates["Kubernetes"] = {
            "node_type": "Asset",
            "node_subtype": "Kubernetes",
            "category": NodeCategory.CONTAINER_DEVOPS,
            "description": "Kubernetes Container Orchestration Platform",
            "required_branches": [
                SecurityBranchType.CONTAINER_ORCHESTRATION,
                SecurityBranchType.CONTAINER_SECURITY,
                SecurityBranchType.NETWORK_SECURITY,
                SecurityBranchType.ACCESS_CONTROL,
                SecurityBranchType.MONITORING
            ],
            "questionnaires": {
                QuestionnaireLevel.BASIC: [
                    {
                        "id": "k8s_distribution",
                        "question": "What Kubernetes distribution is being used?",
                        "type": "single_choice",
                        "options": ["Amazon EKS", "Google GKE", "Azure AKS", "Vanilla Kubernetes", "OpenShift", "Rancher", "Other"],
                        "help_text": "Different distributions have varying security features and configurations.",
                        "related_branch": SecurityBranchType.CONTAINER_ORCHESTRATION
                    },
                    {
                        "id": "k8s_rbac",
                        "question": "Is Role-Based Access Control (RBAC) configured?",
                        "type": "single_choice",
                        "options": ["Comprehensive RBAC", "Basic RBAC", "Minimal RBAC", "No RBAC", "Unknown"],
                        "help_text": "RBAC controls who can access what resources in the cluster.",
                        "related_branch": SecurityBranchType.ACCESS_CONTROL
                    },
                    {
                        "id": "k8s_network_policies",
                        "question": "Are network policies implemented?",
                        "type": "single_choice",
                        "options": ["Comprehensive Policies", "Basic Segmentation", "Minimal Policies", "No Network Policies", "Unknown"],
                        "help_text": "Network policies control traffic between pods and services.",
                        "related_branch": SecurityBranchType.NETWORK_SECURITY
                    },
                    {
                        "id": "k8s_pod_security",
                        "question": "What pod security standards are enforced?",
                        "type": "single_choice",
                        "options": ["Restricted", "Baseline", "Privileged", "No Standards", "Unknown"],
                        "help_text": "Pod security standards control security-sensitive aspects of pod specification.",
                        "related_branch": SecurityBranchType.CONTAINER_SECURITY
                    },
                    {
                        "id": "k8s_image_scanning",
                        "question": "Is container image vulnerability scanning enabled?",
                        "type": "single_choice",
                        "options": ["Continuous Scanning", "Build-time Scanning", "Manual Scanning", "No Scanning", "Unknown"],
                        "help_text": "Image scanning helps identify vulnerabilities in container images.",
                        "related_branch": SecurityBranchType.VULNERABILITY_SCANNING
                    }
                ]
            },
            "threat_intelligence": ThreatIntelligence(
                cve_count=156,
                recent_threats=["Container Escape", "Privilege Escalation", "Resource Hijacking"],
                attack_vectors=["Misconfiguration", "Vulnerable Images", "API Server Exploit"],
                mitre_techniques=["T1611", "T1068", "T1610", "T1055"],
                threat_actors=["TeamTNT", "Hildegard", "Kinsing"]
            )
        }
        
        # CI/CD Pipeline
        templates["CICD"] = {
            "node_type": "Asset",
            "node_subtype": "CICD",
            "category": NodeCategory.CONTAINER_DEVOPS,
            "description": "Continuous Integration/Continuous Deployment Pipeline",
            "required_branches": [
                SecurityBranchType.CI_CD_SECURITY,
                SecurityBranchType.SECRETS_MANAGEMENT,
                SecurityBranchType.SUPPLY_CHAIN,
                SecurityBranchType.ACCESS_CONTROL,
                SecurityBranchType.CODE_SECURITY
            ],
            "questionnaires": {
                QuestionnaireLevel.BASIC: [
                    {
                        "id": "cicd_platform",
                        "question": "What CI/CD platform is being used?",
                        "type": "single_choice",
                        "options": ["GitHub Actions", "GitLab CI", "Jenkins", "Azure DevOps", "CircleCI", "Travis CI", "Custom Solution"],
                        "help_text": "Different platforms have varying security features and configurations.",
                        "related_branch": SecurityBranchType.CI_CD_SECURITY
                    },
                    {
                        "id": "cicd_secrets_management",
                        "question": "How are secrets managed in the pipeline?",
                        "type": "single_choice",
                        "options": ["Dedicated Secret Manager", "Platform Secret Store", "Environment Variables", "Hardcoded in Code", "Unknown"],
                        "help_text": "Proper secrets management prevents credential exposure in pipelines.",
                        "related_branch": SecurityBranchType.SECRETS_MANAGEMENT
                    },
                    {
                        "id": "cicd_security_scanning",
                        "question": "What security scanning is integrated?",
                        "type": "multiple_choice",
                        "options": ["SAST (Static Analysis)", "DAST (Dynamic Analysis)", "Dependency Scanning", "Container Scanning", "IaC Scanning", "None"],
                        "help_text": "Security scanning helps identify vulnerabilities early in development.",
                        "related_branch": SecurityBranchType.CODE_SECURITY
                    },
                    {
                        "id": "cicd_access_control",
                        "question": "How is pipeline access controlled?",
                        "type": "single_choice",
                        "options": ["Role-based Access", "Branch Protection", "Manual Approval", "Open Access", "Unknown"],
                        "help_text": "Access controls prevent unauthorized pipeline modifications.",
                        "related_branch": SecurityBranchType.ACCESS_CONTROL
                    },
                    {
                        "id": "cicd_supply_chain",
                        "question": "Are supply chain security measures implemented?",
                        "type": "multiple_choice",
                        "options": ["Dependency Scanning", "Software Bill of Materials (SBOM)", "Signed Commits", "Verified Dependencies", "None"],
                        "help_text": "Supply chain security prevents malicious code injection.",
                        "related_branch": SecurityBranchType.SUPPLY_CHAIN
                    }
                ]
            },
            "threat_intelligence": ThreatIntelligence(
                cve_count=78,
                recent_threats=["Supply Chain Attacks", "Pipeline Compromise", "Secret Exposure"],
                attack_vectors=["Malicious Dependencies", "Compromised Repositories", "Insider Threats"],
                mitre_techniques=["T1195", "T1078", "T1574", "T1564"],
                threat_actors=["SolarWinds Attackers", "CodeCov Incident", "npm Supply Chain Attacks"]
            )
        }
        
        # ===== ADDITIONAL CLOUD INFRASTRUCTURE NODES =====
        
        # Application Load Balancer
        templates["LoadBalancer"] = {
            "node_type": "Control",
            "node_subtype": "LoadBalancer",
            "category": NodeCategory.NETWORK_COMPONENTS,
            "description": "Application Load Balancer for Traffic Distribution",
            "required_branches": [
                SecurityBranchType.LOAD_BALANCER,
                SecurityBranchType.NETWORK_SECURITY,
                SecurityBranchType.MONITORING,
                SecurityBranchType.WAF
            ],
            "questionnaires": {
                QuestionnaireLevel.BASIC: [
                    {
                        "id": "lb_type",
                        "question": "What type of load balancer is configured?",
                        "type": "single_choice",
                        "options": ["Application Load Balancer", "Network Load Balancer", "Classic Load Balancer", "Gateway Load Balancer"],
                        "help_text": "Different load balancer types provide varying security features.",
                        "related_branch": SecurityBranchType.LOAD_BALANCER
                    },
                    {
                        "id": "lb_internet_facing",
                        "question": "Is the load balancer internet-facing?",
                        "type": "boolean",
                        "help_text": "Internet-facing load balancers have higher attack surface.",
                        "related_branch": SecurityBranchType.NETWORK_SECURITY
                    },
                    {
                        "id": "lb_ssl_termination",
                        "question": "How is SSL/TLS configured?",
                        "type": "single_choice",
                        "options": ["SSL Termination at LB", "End-to-End Encryption", "No SSL", "Mixed Configuration"],
                        "help_text": "SSL termination affects security posture and performance.",
                        "related_branch": SecurityBranchType.ENCRYPTION
                    }
                ]
            },
            "threat_intelligence": ThreatIntelligence(
                cve_count=32,
                recent_threats=["DDoS Attacks", "SSL/TLS Exploits", "Traffic Manipulation"],
                attack_vectors=["Protocol Exploitation", "Certificate Spoofing", "Resource Exhaustion"],
                mitre_techniques=["T1190", "T1557", "T1499"],
                threat_actors=["DDoS Groups", "Web Attackers"]
            )
        }
        
        # KMS (Key Management Service)
        templates["KMS"] = {
            "node_type": "Control",
            "node_subtype": "KMS",
            "category": NodeCategory.SECURITY_SERVICES,
            "description": "Key Management Service for Encryption",
            "required_branches": [
                SecurityBranchType.KEY_MANAGEMENT,
                SecurityBranchType.ENCRYPTION,
                SecurityBranchType.ACCESS_CONTROL,
                SecurityBranchType.COMPLIANCE
            ],
            "questionnaires": {
                QuestionnaireLevel.BASIC: [
                    {
                        "id": "kms_key_type",
                        "question": "What type of KMS keys are used?",
                        "type": "multiple_choice",
                        "options": ["Customer Managed Keys", "AWS Managed Keys", "CloudHSM Keys", "External Keys"],
                        "help_text": "Different key types provide varying levels of control and security.",
                        "related_branch": SecurityBranchType.KEY_MANAGEMENT
                    },
                    {
                        "id": "kms_key_rotation",
                        "question": "Is automatic key rotation enabled?",
                        "type": "boolean",
                        "help_text": "Key rotation reduces the impact of key compromise.",
                        "related_branch": SecurityBranchType.KEY_MANAGEMENT
                    },
                    {
                        "id": "kms_access_policies",
                        "question": "How are key access policies configured?",
                        "type": "single_choice",
                        "options": ["Least Privilege", "Role-based Access", "Broad Access", "Default Policies"],
                        "help_text": "Restrictive access policies prevent unauthorized key usage.",
                        "related_branch": SecurityBranchType.ACCESS_CONTROL
                    }
                ]
            },
            "threat_intelligence": ThreatIntelligence(
                cve_count=15,
                recent_threats=["Key Compromise", "Privilege Escalation", "Cryptographic Attacks"],
                attack_vectors=["Policy Misconfiguration", "Side-channel Attacks", "Key Extraction"],
                mitre_techniques=["T1552", "T1078", "T1140"],
                threat_actors=["APT Groups", "Cryptographic Attackers"]
            )
        }
        
        # CloudTrail
        templates["CloudTrail"] = {
            "node_type": "Control",
            "node_subtype": "CloudTrail",
            "category": NodeCategory.MONITORING_LOGGING,
            "description": "AWS CloudTrail for API Activity Logging",
            "required_branches": [
                SecurityBranchType.LOGGING,
                SecurityBranchType.MONITORING,
                SecurityBranchType.COMPLIANCE,
                SecurityBranchType.INCIDENT_RESPONSE
            ],
            "questionnaires": {
                QuestionnaireLevel.BASIC: [
                    {
                        "id": "cloudtrail_coverage",
                        "question": "What CloudTrail coverage is configured?",
                        "type": "single_choice",
                        "options": ["All Regions", "Single Region", "Multi-Region", "Organization Trail"],
                        "help_text": "Comprehensive coverage ensures complete audit logging.",
                        "related_branch": SecurityBranchType.LOGGING
                    },
                    {
                        "id": "cloudtrail_data_events",
                        "question": "Are data events logged?",
                        "type": "single_choice",
                        "options": ["All Data Events", "S3 Only", "Lambda Only", "No Data Events"],
                        "help_text": "Data events provide detailed activity tracking.",
                        "related_branch": SecurityBranchType.LOGGING
                    },
                    {
                        "id": "cloudtrail_log_integrity",
                        "question": "Is log file integrity validation enabled?",
                        "type": "boolean",
                        "help_text": "Integrity validation detects log tampering.",
                        "related_branch": SecurityBranchType.MONITORING
                    }
                ]
            },
            "threat_intelligence": ThreatIntelligence(
                cve_count=8,
                recent_threats=["Log Tampering", "Audit Evasion", "Compliance Violations"],
                attack_vectors=["Log Deletion", "Event Manipulation", "Access Bypass"],
                mitre_techniques=["T1562", "T1070", "T1078"],
                threat_actors=["Insider Threats", "Advanced Attackers"]
            )
        }
        
        # Security Groups
        templates["SecurityGroups"] = {
            "node_type": "Control",
            "node_subtype": "SecurityGroups",
            "category": NodeCategory.NETWORK_COMPONENTS,
            "description": "AWS Security Groups - Virtual Firewall Rules",
            "required_branches": [
                SecurityBranchType.FIREWALL,
                SecurityBranchType.NETWORK_SECURITY,
                SecurityBranchType.ACCESS_CONTROL
            ],
            "questionnaires": {
                QuestionnaireLevel.BASIC: [
                    {
                        "id": "sg_inbound_rules",
                        "question": "How are inbound rules configured?",
                        "type": "single_choice",
                        "options": ["Least Privilege (Specific IPs/Ports)", "Standard Ports", "Wide Open (0.0.0.0/0)", "Mixed Configuration"],
                        "help_text": "Restrictive inbound rules reduce attack surface.",
                        "related_branch": SecurityBranchType.FIREWALL
                    },
                    {
                        "id": "sg_outbound_rules",
                        "question": "How are outbound rules configured?",
                        "type": "single_choice",
                        "options": ["Restricted Outbound", "Standard Outbound", "Allow All", "Custom Rules"],
                        "help_text": "Outbound restrictions prevent data exfiltration.",
                        "related_branch": SecurityBranchType.FIREWALL
                    },
                    {
                        "id": "sg_unused_rules",
                        "question": "Are unused security group rules regularly reviewed?",
                        "type": "boolean",
                        "help_text": "Regular review prevents rule creep and reduces attack surface.",
                        "related_branch": SecurityBranchType.ACCESS_CONTROL
                    }
                ]
            },
            "threat_intelligence": ThreatIntelligence(
                cve_count=5,
                recent_threats=["Rule Misconfiguration", "Privilege Escalation", "Network Reconnaissance"],
                attack_vectors=["Open Ports", "Default Rules", "Rule Manipulation"],
                mitre_techniques=["T1018", "T1040", "T1046"],
                threat_actors=["Network Attackers", "Insider Threats"]
            )
        }
        
        # Docker Container
        templates["Docker"] = {
            "node_type": "Asset",
            "node_subtype": "Docker",
            "category": NodeCategory.CONTAINER_DEVOPS,
            "description": "Docker Container Runtime Environment",
            "required_branches": [
                SecurityBranchType.CONTAINER_SECURITY,
                SecurityBranchType.VULNERABILITY_SCANNING,
                SecurityBranchType.ACCESS_CONTROL,
                SecurityBranchType.MONITORING
            ],
            "questionnaires": {
                QuestionnaireLevel.BASIC: [
                    {
                        "id": "docker_base_image",
                        "question": "What base image is used?",
                        "type": "single_choice",
                        "options": ["Official Minimal (Alpine/Distroless)", "Official Standard", "Third-party", "Custom Built", "Unknown"],
                        "help_text": "Minimal official images reduce attack surface and vulnerabilities.",
                        "related_branch": SecurityBranchType.CONTAINER_SECURITY
                    },
                    {
                        "id": "docker_privileged_mode",
                        "question": "Is the container running in privileged mode?",
                        "type": "boolean",
                        "help_text": "Privileged containers have full host access and security risks.",
                        "related_branch": SecurityBranchType.ACCESS_CONTROL
                    },
                    {
                        "id": "docker_image_scanning",
                        "question": "Is container image vulnerability scanning performed?",
                        "type": "single_choice",
                        "options": ["Continuous Scanning", "Build-time Only", "Manual Scanning", "No Scanning"],
                        "help_text": "Regular scanning identifies vulnerabilities in container images.",
                        "related_branch": SecurityBranchType.VULNERABILITY_SCANNING
                    }
                ]
            },
            "threat_intelligence": ThreatIntelligence(
                cve_count=287,
                recent_threats=["Container Escape", "Malicious Images", "Runtime Exploits"],
                attack_vectors=["Privileged Escalation", "Image Poisoning", "Resource Abuse"],
                mitre_techniques=["T1611", "T1610", "T1055"],
                threat_actors=["TeamTNT", "Kinsing", "Hildegard"]
            )
        }
        
        # Message Queue
        templates["MessageQueue"] = {
            "node_type": "Asset",
            "node_subtype": "MessageQueue",
            "category": NodeCategory.APPLICATION_SERVICES,
            "description": "Message Queue Service (SQS/RabbitMQ/Kafka)",
            "required_branches": [
                SecurityBranchType.ENCRYPTION,
                SecurityBranchType.ACCESS_CONTROL,
                SecurityBranchType.MONITORING,
                SecurityBranchType.MESSAGE_SECURITY
            ],
            "questionnaires": {
                QuestionnaireLevel.BASIC: [
                    {
                        "id": "mq_type",
                        "question": "What message queue technology is used?",
                        "type": "single_choice",
                        "options": ["Amazon SQS", "Apache Kafka", "RabbitMQ", "Azure Service Bus", "Google Pub/Sub", "Redis", "Custom"],
                        "help_text": "Different queue technologies have varying security characteristics.",
                        "related_branch": SecurityBranchType.APPLICATION_SERVICES
                    },
                    {
                        "id": "mq_encryption_transit",
                        "question": "Is encryption in transit configured?",
                        "type": "boolean",
                        "help_text": "Encryption protects message data during transmission.",
                        "related_branch": SecurityBranchType.ENCRYPTION
                    },
                    {
                        "id": "mq_access_control",
                        "question": "How is access control configured?",
                        "type": "single_choice",
                        "options": ["IAM-based", "Certificate-based", "Username/Password", "API Keys", "No Authentication"],
                        "help_text": "Strong access control prevents unauthorized message access.",
                        "related_branch": SecurityBranchType.ACCESS_CONTROL
                    }
                ]
            },
            "threat_intelligence": ThreatIntelligence(
                cve_count=64,
                recent_threats=["Message Injection", "Queue Poisoning", "Denial of Service"],
                attack_vectors=["Unauthenticated Access", "Message Tampering", "Resource Exhaustion"],
                mitre_techniques=["T1190", "T1499", "T1565"],
                threat_actors=["Application Attackers", "Bot Networks"]
            )
        }
        
        # Monitoring Service
        templates["Monitoring"] = {
            "node_type": "Control",
            "node_subtype": "Monitoring", 
            "category": NodeCategory.MONITORING_LOGGING,
            "description": "Monitoring and Alerting Service (CloudWatch/Prometheus)",
            "required_branches": [
                SecurityBranchType.MONITORING,
                SecurityBranchType.LOGGING,
                SecurityBranchType.INCIDENT_RESPONSE,
                SecurityBranchType.COMPLIANCE
            ],
            "questionnaires": {
                QuestionnaireLevel.BASIC: [
                    {
                        "id": "monitoring_type",
                        "question": "What monitoring solution is deployed?",
                        "type": "single_choice",
                        "options": ["AWS CloudWatch", "Prometheus/Grafana", "Datadog", "New Relic", "Splunk", "ELK Stack", "Custom"],
                        "help_text": "Different monitoring solutions provide varying security capabilities.",
                        "related_branch": SecurityBranchType.MONITORING
                    },
                    {
                        "id": "monitoring_metrics",
                        "question": "What types of metrics are collected?",
                        "type": "multiple_choice",
                        "options": ["System Metrics", "Application Metrics", "Security Events", "User Activity", "Network Traffic", "Custom Metrics"],
                        "help_text": "Comprehensive metrics provide better security visibility.",
                        "related_branch": SecurityBranchType.MONITORING
                    },
                    {
                        "id": "monitoring_alerting",
                        "question": "How are security alerts configured?",
                        "type": "single_choice",
                        "options": ["Real-time Alerting", "Batch Alerting", "Manual Review", "No Alerting"],
                        "help_text": "Real-time alerting enables faster incident response.",
                        "related_branch": SecurityBranchType.INCIDENT_RESPONSE
                    }
                ]
            },
            "threat_intelligence": ThreatIntelligence(
                cve_count=43,
                recent_threats=["Monitoring Evasion", "Log Injection", "Alert Fatigue"],
                attack_vectors=["Blind Spot Exploitation", "False Positive Generation", "Data Poisoning"],
                mitre_techniques=["T1562", "T1070", "T1036"],
                threat_actors=["Advanced Persistent Threats", "Insider Threats"]
            )
        }
        
        # Content Delivery Network
        templates["CDN"] = {
            "node_type": "Control",
            "node_subtype": "CDN",
            "category": NodeCategory.NETWORK_COMPONENTS,
            "description": "Content Delivery Network (CloudFront/Cloudflare)",
            "required_branches": [
                SecurityBranchType.WAF,
                SecurityBranchType.ENCRYPTION,
                SecurityBranchType.MONITORING,
                SecurityBranchType.DDoS_PROTECTION
            ],
            "questionnaires": {
                QuestionnaireLevel.BASIC: [
                    {
                        "id": "cdn_provider",
                        "question": "What CDN provider is used?",
                        "type": "single_choice",
                        "options": ["Amazon CloudFront", "Cloudflare", "Azure CDN", "Google Cloud CDN", "Fastly", "KeyCDN", "Custom"],
                        "help_text": "Different CDN providers offer varying security features.",
                        "related_branch": SecurityBranchType.NETWORK_SECURITY
                    },
                    {
                        "id": "cdn_waf_integration",
                        "question": "Is WAF integrated with the CDN?",
                        "type": "boolean",
                        "help_text": "WAF integration provides application layer protection.",
                        "related_branch": SecurityBranchType.WAF
                    },
                    {
                        "id": "cdn_ssl_tls",
                        "question": "How is SSL/TLS configured?",
                        "type": "single_choice",
                        "options": ["TLS 1.3 Only", "TLS 1.2+", "Mixed Versions", "HTTP Only"],
                        "help_text": "Modern TLS versions provide better security.",
                        "related_branch": SecurityBranchType.ENCRYPTION
                    }
                ]
            },
            "threat_intelligence": ThreatIntelligence(
                cve_count=28,
                recent_threats=["Cache Poisoning", "Origin Exposure", "DDoS Attacks"],
                attack_vectors=["Edge Server Compromise", "Certificate Issues", "Misconfiguration"],
                mitre_techniques=["T1190", "T1499", "T1557"],
                threat_actors=["DDoS Groups", "Web Attackers"]
            )
        }
        
        # API Gateway
        templates["APIGateway"] = {
            "node_type": "Control",
            "node_subtype": "APIGateway",
            "category": NodeCategory.APPLICATION_SERVICES,
            "description": "API Gateway for API Management and Security",
            "required_branches": [
                SecurityBranchType.API,
                SecurityBranchType.AUTHENTICATION,
                SecurityBranchType.RATE_LIMITING,
                SecurityBranchType.MONITORING
            ],
            "questionnaires": {
                QuestionnaireLevel.BASIC: [
                    {
                        "id": "apigw_type",
                        "question": "What type of API Gateway is deployed?",
                        "type": "single_choice",
                        "options": ["AWS API Gateway", "Kong", "Ambassador", "Istio Gateway", "Nginx", "Custom"],
                        "help_text": "Different gateways provide varying security capabilities.",
                        "related_branch": SecurityBranchType.API
                    },
                    {
                        "id": "apigw_authentication",
                        "question": "What authentication methods are supported?",
                        "type": "multiple_choice",
                        "options": ["OAuth 2.0", "JWT", "API Keys", "IAM", "Custom Authorizers", "No Authentication"],
                        "help_text": "Strong authentication prevents unauthorized API access.",
                        "related_branch": SecurityBranchType.AUTHENTICATION
                    },
                    {
                        "id": "apigw_rate_limiting",
                        "question": "Is rate limiting configured?",
                        "type": "single_choice",
                        "options": ["Per-User Rate Limiting", "Global Rate Limiting", "Burst Limiting", "No Rate Limiting"],
                        "help_text": "Rate limiting prevents API abuse and DoS attacks.",
                        "related_branch": SecurityBranchType.RATE_LIMITING
                    }
                ]
            },
            "threat_intelligence": ThreatIntelligence(
                cve_count=52,
                recent_threats=["API Abuse", "Authentication Bypass", "Rate Limit Evasion"],
                attack_vectors=["Broken Authentication", "Excessive Data Exposure", "Injection Attacks"],
                mitre_techniques=["T1190", "T1078", "T1059"],
                threat_actors=["API Attackers", "Bot Networks"]
            )
        }
        
        # Network ACL
        templates["NetworkACL"] = {
            "node_type": "Control",
            "node_subtype": "NetworkACL",
            "category": NodeCategory.NETWORK_COMPONENTS,
            "description": "Network Access Control Lists",
            "required_branches": [
                SecurityBranchType.NETWORK_SECURITY,
                SecurityBranchType.FIREWALL,
                SecurityBranchType.ACCESS_CONTROL
            ],
            "questionnaires": {
                QuestionnaireLevel.BASIC: [
                    {
                        "id": "nacl_rules",
                        "question": "How are NACL rules configured?",
                        "type": "single_choice",
                        "options": ["Deny by Default", "Allow by Default", "Mixed Rules", "Default AWS Rules"],
                        "help_text": "Deny by default provides better security posture.",
                        "related_branch": SecurityBranchType.NETWORK_SECURITY
                    },
                    {
                        "id": "nacl_logging",
                        "question": "Is NACL traffic logging enabled?",
                        "type": "boolean",
                        "help_text": "Logging provides visibility into blocked traffic.",
                        "related_branch": SecurityBranchType.MONITORING
                    }
                ]
            },
            "threat_intelligence": ThreatIntelligence(
                cve_count=7,
                recent_threats=["Rule Bypass", "Network Reconnaissance", "Lateral Movement"],
                attack_vectors=["Misconfiguration", "Rule Gaps", "Protocol Tunneling"],
                mitre_techniques=["T1090", "T1046", "T1021"],
                threat_actors=["Network Attackers", "Advanced Threats"]
            )
        }
        
        # Secrets Manager  
        templates["SecretsManager"] = {
            "node_type": "Control",
            "node_subtype": "SecretsManager",
            "category": NodeCategory.SECURITY_SERVICES,
            "description": "Secrets Management Service",
            "required_branches": [
                SecurityBranchType.SECRETS_MANAGEMENT,
                SecurityBranchType.ENCRYPTION,
                SecurityBranchType.ACCESS_CONTROL,
                SecurityBranchType.COMPLIANCE
            ],
            "questionnaires": {
                QuestionnaireLevel.BASIC: [
                    {
                        "id": "secrets_type",
                        "question": "What secrets management solution is used?",
                        "type": "single_choice",
                        "options": ["AWS Secrets Manager", "HashiCorp Vault", "Azure Key Vault", "Google Secret Manager", "Kubernetes Secrets", "Custom"],
                        "help_text": "Different solutions provide varying security capabilities.",
                        "related_branch": SecurityBranchType.SECRETS_MANAGEMENT
                    },
                    {
                        "id": "secrets_rotation",
                        "question": "Is automatic secret rotation enabled?",
                        "type": "boolean",
                        "help_text": "Automatic rotation reduces the impact of secret compromise.",
                        "related_branch": SecurityBranchType.SECRETS_MANAGEMENT
                    },
                    {
                        "id": "secrets_access_control",
                        "question": "How is access to secrets controlled?",
                        "type": "single_choice",
                        "options": ["IAM Policies", "RBAC", "Service Accounts", "API Keys", "Basic Authentication"],
                        "help_text": "Strong access control prevents unauthorized secret access.",
                        "related_branch": SecurityBranchType.ACCESS_CONTROL
                    }
                ]
            },
            "threat_intelligence": ThreatIntelligence(
                cve_count=19,
                recent_threats=["Secret Exposure", "Privilege Escalation", "Credential Theft"],
                attack_vectors=["Configuration Errors", "Access Policy Bypass", "Log Exposure"],
                mitre_techniques=["T1552", "T1078", "T1083"],
                threat_actors=["Insider Threats", "APT Groups"]
            )
        }
        
        # Database Proxy
        templates["DatabaseProxy"] = {
            "node_type": "Control",
            "node_subtype": "DatabaseProxy",
            "category": NodeCategory.DATA_STORAGE,
            "description": "Database Proxy Service (RDS Proxy/ProxySQL)",
            "required_branches": [
                SecurityBranchType.DATABASE,
                SecurityBranchType.AUTHENTICATION,
                SecurityBranchType.MONITORING,
                SecurityBranchType.ACCESS_CONTROL
            ],
            "questionnaires": {
                QuestionnaireLevel.BASIC: [
                    {
                        "id": "db_proxy_type",
                        "question": "What database proxy solution is used?",
                        "type": "single_choice",
                        "options": ["AWS RDS Proxy", "ProxySQL", "PgBouncer", "Custom Proxy", "No Proxy"],
                        "help_text": "Database proxies can improve security and performance.",
                        "related_branch": SecurityBranchType.DATABASE
                    },
                    {
                        "id": "db_proxy_auth",
                        "question": "How does the proxy handle authentication?",
                        "type": "single_choice",
                        "options": ["IAM Authentication", "Connection Pooling", "Credential Management", "Pass-through", "Custom"],
                        "help_text": "Proxy authentication can centralize database access control.",
                        "related_branch": SecurityBranchType.AUTHENTICATION
                    }
                ]
            },
            "threat_intelligence": ThreatIntelligence(
                cve_count=25,
                recent_threats=["Connection Hijacking", "Credential Interception", "SQL Injection"],
                attack_vectors=["Proxy Bypass", "Authentication Weakness", "Protocol Exploitation"],
                mitre_techniques=["T1557", "T1078", "T1190"],
                threat_actors=["Database Attackers", "APT Groups"]
            )
        }
        
        # Backup Service
        templates["Backup"] = {
            "node_type": "Control",
            "node_subtype": "Backup",
            "category": NodeCategory.DATA_STORAGE,
            "description": "Backup and Recovery Service",
            "required_branches": [
                SecurityBranchType.BACKUP,
                SecurityBranchType.ENCRYPTION,
                SecurityBranchType.ACCESS_CONTROL,
                SecurityBranchType.COMPLIANCE
            ],
            "questionnaires": {
                QuestionnaireLevel.BASIC: [
                    {
                        "id": "backup_type",
                        "question": "What backup solution is used?",
                        "type": "single_choice",
                        "options": ["AWS Backup", "Native Database Backups", "Third-party Solution", "Custom Scripts", "No Automated Backups"],
                        "help_text": "Automated backup solutions provide better reliability.",
                        "related_branch": SecurityBranchType.BACKUP
                    },
                    {
                        "id": "backup_encryption",
                        "question": "Are backups encrypted?",
                        "type": "single_choice",
                        "options": ["Encrypted at Rest and Transit", "Encrypted at Rest Only", "Encrypted in Transit Only", "No Encryption"],
                        "help_text": "Encryption protects backup data from unauthorized access.",
                        "related_branch": SecurityBranchType.ENCRYPTION
                    },
                    {
                        "id": "backup_retention",
                        "question": "What is the backup retention policy?",
                        "type": "single_choice",
                        "options": ["Long-term (1+ years)", "Medium-term (3-12 months)", "Short-term (1-3 months)", "No Defined Policy"],
                        "help_text": "Appropriate retention periods support recovery and compliance.",
                        "related_branch": SecurityBranchType.BACKUP
                    }
                ]
            },
            "threat_intelligence": ThreatIntelligence(
                cve_count=31,
                recent_threats=["Ransomware", "Backup Corruption", "Data Theft"],
                attack_vectors=["Backup System Compromise", "Encryption Key Theft", "Access Control Bypass"],
                mitre_techniques=["T1490", "T1486", "T1005"],
                threat_actors=["Ransomware Groups", "Insider Threats"]
            )
        }
        
        # Certificate Manager
        templates["CertificateManager"] = {
            "node_type": "Control",
            "node_subtype": "CertificateManager",
            "category": NodeCategory.SECURITY_SERVICES,
            "description": "SSL/TLS Certificate Management Service",
            "required_branches": [
                SecurityBranchType.ENCRYPTION,
                SecurityBranchType.KEY_MANAGEMENT,
                SecurityBranchType.COMPLIANCE,
                SecurityBranchType.MONITORING
            ],
            "questionnaires": {
                QuestionnaireLevel.BASIC: [
                    {
                        "id": "cert_provider",
                        "question": "What certificate management solution is used?",
                        "type": "single_choice",
                        "options": ["AWS Certificate Manager", "Let's Encrypt", "Commercial CA", "Internal CA", "Self-signed"],
                        "help_text": "Different certificate sources have varying trust and security levels.",
                        "related_branch": SecurityBranchType.ENCRYPTION
                    },
                    {
                        "id": "cert_auto_renewal",
                        "question": "Is automatic certificate renewal configured?",
                        "type": "boolean",
                        "help_text": "Automatic renewal prevents certificate expiration issues.",
                        "related_branch": SecurityBranchType.KEY_MANAGEMENT
                    },
                    {
                        "id": "cert_monitoring",
                        "question": "Is certificate expiration monitoring enabled?",
                        "type": "boolean",
                        "help_text": "Monitoring alerts on upcoming certificate expirations.",
                        "related_branch": SecurityBranchType.MONITORING
                    }
                ]
            },
            "threat_intelligence": ThreatIntelligence(
                cve_count=12,
                recent_threats=["Certificate Spoofing", "Weak Certificates", "CA Compromise"],
                attack_vectors=["Certificate Pinning Bypass", "Man-in-the-Middle", "Certificate Authority Attack"],
                mitre_techniques=["T1557", "T1588", "T1608"],
                threat_actors=["Nation-state Actors", "Certificate Attackers"]
            )
        }
        
        # Route 53 DNS
        templates["DNS"] = {
            "node_type": "Control",
            "node_subtype": "DNS",
            "category": NodeCategory.NETWORK_COMPONENTS,
            "description": "DNS Service (Route 53/CloudFlare DNS)",
            "required_branches": [
                SecurityBranchType.NETWORK_SECURITY,
                SecurityBranchType.MONITORING,
                SecurityBranchType.DDoS_PROTECTION
            ],
            "questionnaires": {
                QuestionnaireLevel.BASIC: [
                    {
                        "id": "dns_provider",
                        "question": "What DNS provider is used?",
                        "type": "single_choice",
                        "options": ["AWS Route 53", "Cloudflare DNS", "Google Cloud DNS", "Azure DNS", "Internal DNS", "ISP DNS"],
                        "help_text": "Different DNS providers offer varying security and reliability features.",
                        "related_branch": SecurityBranchType.NETWORK_SECURITY
                    },
                    {
                        "id": "dns_dnssec",
                        "question": "Is DNSSEC enabled?",
                        "type": "boolean",
                        "help_text": "DNSSEC provides authentication and integrity for DNS responses.",
                        "related_branch": SecurityBranchType.NETWORK_SECURITY
                    },
                    {
                        "id": "dns_logging",
                        "question": "Is DNS query logging enabled?",
                        "type": "boolean",
                        "help_text": "DNS logging provides visibility into domain resolution patterns.",
                        "related_branch": SecurityBranchType.MONITORING
                    }
                ]
            },
            "threat_intelligence": ThreatIntelligence(
                cve_count=24,
                recent_threats=["DNS Hijacking", "Cache Poisoning", "DDoS Attacks"],
                attack_vectors=["DNS Spoofing", "Subdomain Takeover", "Amplification Attacks"],
                mitre_techniques=["T1584", "T1583", "T1499"],
                threat_actors=["DNS Hijackers", "DDoS Groups"]
            )
        }
        
        return templates
    
    def _initialize_threat_intelligence(self) -> Dict[str, ThreatIntelligence]:
        """Initialize threat intelligence database"""
        # This would connect to real threat intelligence feeds
        # For now, returning the embedded threat intelligence from templates
        return {}
    
    def _initialize_risk_calculators(self) -> Dict[str, Any]:
        """Initialize risk calculation algorithms"""
        return {
            "probabilistic_model": self._probabilistic_risk_model,
            "attack_surface_calculator": self._calculate_attack_surface,
            "control_effectiveness": self._assess_control_effectiveness
        }
    
    def _probabilistic_risk_model(self, node_type: str, config: Dict) -> RiskMetrics:
        """Enhanced probabilistic risk calculation"""
        base_risk = 5.0
        
        # Get node template
        template = self.node_templates.get(node_type, {})
        threat_intel = template.get("threat_intelligence", ThreatIntelligence())
        
        # Calculate components
        attack_surface = self._calculate_attack_surface(node_type, config)
        vulnerability_score = min(10.0, threat_intel.cve_count / 20.0)  # Normalize CVE count
        control_effectiveness = self._assess_control_effectiveness(config)
        business_impact = config.get("business_criticality", 5.0)
        threat_probability = len(threat_intel.recent_threats) / 10.0  # Normalize
        
        return RiskMetrics(
            base_risk=base_risk,
            attack_surface_score=attack_surface,
            vulnerability_score=vulnerability_score,
            control_effectiveness=control_effectiveness,
            business_impact=business_impact,
            threat_probability=min(1.0, threat_probability)
        )
    
    def _calculate_attack_surface(self, node_type: str, config: Dict) -> float:
        """Calculate attack surface score"""
        score = 5.0  # Base attack surface
        
        # Network exposure
        if config.get("public_access", False):
            score += 2.0
        if config.get("public_ip", False):
            score += 1.5
        
        # Service exposure
        open_ports = config.get("open_ports", [])
        score += len(open_ports) * 0.5
        
        # Authentication exposure
        if config.get("authentication") == "none":
            score += 3.0
        elif config.get("authentication") == "basic":
            score += 1.5
        
        return min(10.0, score)
    
    def _assess_control_effectiveness(self, config: Dict) -> float:
        """Assess effectiveness of security controls"""
        effectiveness = 5.0  # Base effectiveness
        
        # Positive controls
        if config.get("mfa_enabled", False):
            effectiveness += 1.5
        if config.get("encryption_enabled", False):
            effectiveness += 1.0
        if config.get("monitoring_enabled", False):
            effectiveness += 0.5
        if config.get("backup_enabled", False):
            effectiveness += 0.5
        
        # Negative factors
        if config.get("patching") == "never":
            effectiveness -= 2.0
        if config.get("logging") == "disabled":
            effectiveness -= 1.0
        
        return max(0.0, min(10.0, effectiveness))
    
    # Additional methods for expanded functionality
    def get_supported_node_types(self) -> List[str]:
        """Get list of all supported node types"""
        return list(self.node_templates.keys())
    
    def get_questionnaire_by_level(self, node_type: str, level: QuestionnaireLevel) -> List[Dict]:
        """Get questionnaire for specific level"""
        template = self.node_templates.get(node_type, {})
        questionnaires = template.get("questionnaires", {})
        return questionnaires.get(level, [])
    
    def calculate_comprehensive_risk(self, node_type: str, responses: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive risk assessment"""
        risk_metrics = self._probabilistic_risk_model(node_type, responses)
        composite_risk = risk_metrics.calculate_composite_risk()
        
        # Determine risk level
        if composite_risk >= 8.0:
            risk_level = ThreatLevel.CRITICAL
        elif composite_risk >= 6.0:
            risk_level = ThreatLevel.HIGH
        elif composite_risk >= 4.0:
            risk_level = ThreatLevel.MEDIUM
        elif composite_risk >= 2.0:
            risk_level = ThreatLevel.LOW
        else:
            risk_level = ThreatLevel.MINIMAL
        
        return {
            "composite_risk_score": round(composite_risk, 2),
            "risk_level": risk_level,
            "risk_components": {
                "attack_surface": round(risk_metrics.attack_surface_score, 2),
                "vulnerability_score": round(risk_metrics.vulnerability_score, 2),
                "control_effectiveness": round(risk_metrics.control_effectiveness, 2),
                "business_impact": round(risk_metrics.business_impact, 2),
                "threat_probability": round(risk_metrics.threat_probability, 2)
            },
            "threat_intelligence": self._get_threat_intelligence_summary(node_type)
        }
    
    def _get_threat_intelligence_summary(self, node_type: str) -> Dict[str, Any]:
        """Get threat intelligence summary for node type"""
        template = self.node_templates.get(node_type, {})
        threat_intel = template.get("threat_intelligence", ThreatIntelligence())
        
        return {
            "cve_count": threat_intel.cve_count,
            "recent_threats": threat_intel.recent_threats[:3],  # Top 3
            "primary_attack_vectors": threat_intel.attack_vectors[:3],
            "mitre_techniques": threat_intel.mitre_techniques[:5],
            "known_threat_actors": threat_intel.threat_actors[:3]
        }
    
    def generate_security_recommendations(self, node_type: str, responses: Dict[str, Any], risk_score: float) -> List[Dict[str, Any]]:
        """Generate prioritized security recommendations"""
        recommendations = []
        
        # Risk-based recommendations
        if risk_score >= 8.0:
            recommendations.append({
                "priority": "CRITICAL",
                "category": "Risk Mitigation",
                "recommendation": "Immediate security review required - Critical risk level detected",
                "impact": "High",
                "effort": "Medium"
            })
        
        # Node-specific recommendations based on responses
        template = self.node_templates.get(node_type, {})
        
        # Check for common security gaps
        if responses.get("public_access", False) and not responses.get("authentication", False):
            recommendations.append({
                "priority": "HIGH",
                "category": "Access Control",
                "recommendation": "Implement strong authentication for publicly accessible resources",
                "impact": "High",
                "effort": "Medium"
            })
        
        if not responses.get("encryption_enabled", False):
            recommendations.append({
                "priority": "HIGH",
                "category": "Data Protection",
                "recommendation": "Enable encryption at rest and in transit",
                "impact": "High",
                "effort": "Low"
            })
        
        if not responses.get("monitoring_enabled", False):
            recommendations.append({
                "priority": "MEDIUM",
                "category": "Monitoring",
                "recommendation": "Implement comprehensive security monitoring and alerting",
                "impact": "Medium",
                "effort": "Medium"
            })
        
        # Sort by priority
        priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 4))
        
    def _calculate_attack_surface_score(self, responses: dict, risk_factors: dict) -> float:
        """Calculate attack surface score based on responses"""
        base_score = 5.0
        
        # Check for public exposure
        if responses.get("public_access") or responses.get("public_ip"):
            base_score += 2.0
        
        # Check for network exposure
        if responses.get("network_exposure", "").lower() in ["high", "public", "internet"]:
            base_score += 1.5
        
        # Apply risk factors
        for factor_key, factor_value in risk_factors.items():
            if factor_key in responses and responses[factor_key]:
                base_score += factor_value
        
        return min(base_score, 10.0)
    
    def _calculate_vulnerability_score(self, responses: dict, risk_factors: dict) -> float:
        """Calculate vulnerability score based on responses"""
        base_score = 5.0
        
        # Check for known vulnerabilities
        vulnerability_indicators = ["unpatched", "outdated", "default_config", "weak_encryption"]
        for indicator in vulnerability_indicators:
            if any(indicator in key.lower() for key in responses.keys()):
                if responses.get(indicator) in [True, "yes", "enabled"]:
                    base_score += 1.0
        
        # Apply CVE-based risk factors
        cve_risk = risk_factors.get("cve_exposure", 0)
        base_score += cve_risk
        
        return min(base_score, 10.0)
    
    def _calculate_control_effectiveness_score(self, responses: dict) -> float:
        """Calculate control effectiveness score"""
        base_score = 5.0
        
        # Check for security controls
        security_controls = ["encryption", "monitoring", "access_control", "firewall", "backup"]
        control_count = 0
        
        for control in security_controls:
            if any(control in key.lower() for key in responses.keys()):
                if responses.get(control) in [True, "yes", "enabled", "strong", "comprehensive"]:
                    control_count += 1
                    base_score += 0.5
        
        # Bonus for comprehensive security
        if control_count >= 4:
            base_score += 1.0
        
        return min(base_score, 10.0)
    
    def _calculate_business_impact_score(self, responses: dict) -> float:
        """Calculate business impact score"""
        base_score = 5.0
        
        # Check for business criticality indicators
        if responses.get("business_critical") or responses.get("high_availability"):
            base_score += 2.0
        
        # Check for data sensitivity
        data_sensitivity = responses.get("data_sensitivity", "").lower()
        if data_sensitivity in ["high", "critical", "confidential"]:
            base_score += 1.5
        elif data_sensitivity in ["medium", "sensitive"]:
            base_score += 1.0
        
        # Check for regulatory requirements
        if responses.get("regulatory_compliance") or responses.get("compliance_required"):
            base_score += 1.0
        
        return min(base_score, 10.0)
    
    def generate_security_recommendations(self, node_subtype: str, responses: dict, risk_score: float) -> list:
        """Generate security recommendations based on risk assessment"""
        recommendations = []
        
        # High-level recommendations based on risk score
        if risk_score >= 8.0:
            recommendations.append({
                "priority": "CRITICAL",
                "category": "Immediate Action Required",
                "recommendation": "Immediate security review and remediation required - critical risk level detected",
                "rationale": f"Risk score of {risk_score:.1f} indicates severe security exposure"
            })
        
        # Specific recommendations based on responses
        if responses.get("public_access"):
            recommendations.append({
                "priority": "HIGH",
                "category": "Access Control",
                "recommendation": "Implement network access controls and restrict public exposure",
                "rationale": "Public access significantly increases attack surface"
            })
        
        if not responses.get("encryption"):
            recommendations.append({
                "priority": "HIGH",
                "category": "Data Protection",
                "recommendation": "Implement encryption for data at rest and in transit",
                "rationale": "Unencrypted data is vulnerable to interception and theft"
            })
        
        if not responses.get("monitoring"):
            recommendations.append({
                "priority": "MEDIUM",
                "category": "Detection",
                "recommendation": "Deploy comprehensive monitoring and logging",
                "rationale": "Monitoring is essential for threat detection and incident response"
            })
        
        return recommendations[:5]  # Return top 5 recommendations


# Global instance
expanded_node_engine = ExpandedIntelligentNodeEngine()