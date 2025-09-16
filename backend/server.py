from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime, timezone
from enum import Enum
import asyncio
from concurrent.futures import ThreadPoolExecutor
import networkx as nx
import math
from dataclasses import asdict

# Import advanced simulation modules
from advanced_simulation import AdvancedSimulationEngine
from mitre_integration import MitreAttackDatabase
from intelligent_nodes import intelligent_node_engine, SecurityBranch, SecurityPrompt, IntelligentNodeTemplate
from expanded_intelligent_nodes import ExpandedIntelligentNodeEngine, QuestionnaireLevel
from questionnaire_loader import get_questionnaire_loader, QuestionnaireLevel as LoaderQuestionnaireLevel
from threat_intelligence import threat_intelligence_engine, ThreatIntelligenceEngine
from dsl_rule_engine import dsl_rule_engine, RuleEvaluationResult, SecurityGap, CompletenessAnalysis
from probabilistic_simulation import probabilistic_engine, ProbabilisticAttackPath, ScenarioAnalysis, DefenseEffectivenessModel

# Import new core loop completion modules
from findings_management import FindingsManager, Finding, FindingSeverity, FindingStatus, FindingSource, FindingsFilter, FindingsSummary
from questionnaire_completion_processor import QuestionnaireCompletionProcessor

# Import vulnerability analysis modules
from vulnerability_engine import vulnerability_engine, VulnerabilityAnalysisResult, VulnerabilityNode, VulnerabilitySeverity
from questionnaire_analyzer import questionnaire_analyzer

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Initialize advanced components
simulation_engine = AdvancedSimulationEngine()
mitre_db = MitreAttackDatabase()
executor = ThreadPoolExecutor(max_workers=4)

# Initialize expanded intelligent node engine
expanded_node_engine = ExpandedIntelligentNodeEngine()
questionnaire_loader = get_questionnaire_loader()

# Initialize findings management and questionnaire completion processing
findings_manager = FindingsManager(db)
questionnaire_processor = QuestionnaireCompletionProcessor(db, findings_manager)

# Default Security Templates Data
def get_default_templates():
    """Get pre-built security templates for common architectures"""
    return [
        {
            "name": "Web Application Security Model",
            "description": "Comprehensive security model for a modern web application with database backend",
            "category": TemplateCategory.WEB_APPLICATION,
            "use_case": "Model security threats for web applications exposed to the internet",
            "complexity": "Intermediate",
            "tags": ["web", "database", "authentication", "WAF"],
            "compliance_frameworks": ["NIST CSF", "OWASP Top 10"],
            "estimated_time": "10-15 minutes",
            "nodes": [
                {
                    "id": "internet-zone",
                    "type": "Zone",
                    "subtype": "Internet",
                    "label": "Internet",
                    "position": {"x": 100, "y": 50},
                    "description": "Untrusted public internet space",
                    "trust_level": "Untrusted"
                },
                {
                    "id": "external-attacker",
                    "type": "Actor",
                    "subtype": "ExternalAttacker", 
                    "label": "External Attacker",
                    "position": {"x": 100, "y": 150},
                    "sophistication": "Medium",
                    "motivation": "Financial"
                },
                {
                    "id": "waf",
                    "type": "Control",
                    "subtype": "WAF",
                    "label": "Web Application Firewall",
                    "position": {"x": 300, "y": 50},
                    "effectiveness": 85,
                    "control_type": "Preventive"
                },
                {
                    "id": "web-app",
                    "type": "Asset",
                    "subtype": "WebApp",
                    "label": "Web Application",
                    "position": {"x": 500, "y": 150},
                    "criticality": "High",
                    "data_classification": "Confidential"
                },
                {
                    "id": "sql-injection",
                    "type": "Surface",
                    "subtype": "SQLi",
                    "label": "SQL Injection",
                    "position": {"x": 400, "y": 250},
                    "cvss_score": 9.8,
                    "exploitability": "High"
                },
                {
                    "id": "database",
                    "type": "Asset",
                    "subtype": "Database",
                    "label": "Production Database",
                    "position": {"x": 700, "y": 250},
                    "criticality": "Critical",
                    "data_classification": "Restricted"
                }
            ],
            "edges": [
                {
                    "id": "attacker-to-waf",
                    "source": "external-attacker",
                    "target": "waf",
                    "label": "Initial Access"
                },
                {
                    "id": "waf-to-webapp",
                    "source": "waf",
                    "target": "web-app",
                    "label": "Filtered Traffic"
                },
                {
                    "id": "webapp-to-sqli",
                    "source": "web-app",
                    "target": "sql-injection",
                    "label": "Contains Vulnerability"
                },
                {
                    "id": "sqli-to-database",
                    "source": "sql-injection",
                    "target": "database",
                    "label": "Data Access"
                }
            ]
        },
        {
            "name": "Zero Trust Architecture",
            "description": "Zero trust security model with identity verification and micro-segmentation",
            "category": TemplateCategory.ZERO_TRUST,
            "use_case": "Implement zero trust principles for enterprise environments",
            "complexity": "Advanced",
            "tags": ["zero-trust", "identity", "micro-segmentation", "continuous-verification"],
            "compliance_frameworks": ["NIST Zero Trust", "CISA Zero Trust"],
            "estimated_time": "20-25 minutes",
            "nodes": [
                {
                    "id": "external-user",
                    "type": "Actor",
                    "subtype": "ExternalAttacker",
                    "label": "External User",
                    "position": {"x": 100, "y": 100},
                    "sophistication": "Low",
                    "motivation": "Access"
                },
                {
                    "id": "identity-provider",
                    "type": "Control",
                    "subtype": "IAMPolicy",
                    "label": "Identity Provider",
                    "position": {"x": 300, "y": 100},
                    "effectiveness": 95,
                    "control_type": "Preventive"
                },
                {
                    "id": "policy-engine",
                    "type": "Control",
                    "subtype": "IAMPolicy",
                    "label": "Policy Decision Point",
                    "position": {"x": 500, "y": 100},
                    "effectiveness": 90,
                    "control_type": "Preventive"
                },
                {
                    "id": "secure-enclave",
                    "type": "Zone",
                    "subtype": "SecureEnclave",
                    "label": "Secure Enclave",
                    "position": {"x": 700, "y": 100},
                    "trust_level": "High",
                    "security_level": "Maximum"
                },
                {
                    "id": "critical-asset",
                    "type": "Asset",
                    "subtype": "Database",
                    "label": "Critical Data",
                    "position": {"x": 700, "y": 250},
                    "criticality": "Critical",
                    "data_classification": "Restricted"
                },
                {
                    "id": "network-segmentation",
                    "type": "Control",
                    "subtype": "NetworkACL",
                    "label": "Micro-segmentation",
                    "position": {"x": 500, "y": 250},
                    "effectiveness": 80,
                    "control_type": "Preventive"
                }
            ],
            "edges": [
                {
                    "id": "user-to-identity",
                    "source": "external-user",
                    "target": "identity-provider",
                    "label": "Authentication"
                },
                {
                    "id": "identity-to-policy",
                    "source": "identity-provider",
                    "target": "policy-engine",
                    "label": "Identity Verification"
                },
                {
                    "id": "policy-to-enclave",
                    "source": "policy-engine",
                    "target": "secure-enclave",
                    "label": "Access Decision"
                },
                {
                    "id": "enclave-to-asset",
                    "source": "secure-enclave",
                    "target": "critical-asset",
                    "label": "Protected Access"
                },
                {
                    "id": "segmentation-protects-asset",
                    "source": "network-segmentation",
                    "target": "critical-asset",
                    "label": "Network Protection"
                }
            ]
        },
        {
            "name": "Cloud Native Security",
            "description": "Container and Kubernetes security model with cloud-native controls",
            "category": TemplateCategory.CLOUD_NATIVE,
            "use_case": "Secure containerized applications in Kubernetes environments",
            "complexity": "Advanced", 
            "tags": ["kubernetes", "containers", "cloud", "microservices"],
            "compliance_frameworks": ["CIS Kubernetes", "NIST SP 800-190"],
            "estimated_time": "15-20 minutes",
            "nodes": [
                {
                    "id": "developer",
                    "type": "Actor",
                    "subtype": "Insider",
                    "label": "Developer",
                    "position": {"x": 100, "y": 100},
                    "sophistication": "Low",
                    "motivation": "Productivity"
                },
                {
                    "id": "container-registry",
                    "type": "Asset",
                    "subtype": "S3Bucket",
                    "label": "Container Registry",
                    "position": {"x": 300, "y": 100},
                    "criticality": "High",
                    "data_classification": "Internal"
                },
                {
                    "id": "kubernetes-cluster",
                    "type": "Asset",
                    "subtype": "VM",
                    "label": "Kubernetes Cluster",
                    "position": {"x": 500, "y": 100},
                    "criticality": "Critical",
                    "data_classification": "Restricted"
                },
                {
                    "id": "pod-security",
                    "type": "Control",
                    "subtype": "IAMPolicy",
                    "label": "Pod Security Standards",
                    "position": {"x": 400, "y": 200},
                    "effectiveness": 85,
                    "control_type": "Preventive"
                },
                {
                    "id": "network-policies",
                    "type": "Control",
                    "subtype": "NetworkACL",
                    "label": "Network Policies",
                    "position": {"x": 600, "y": 200},
                    "effectiveness": 90,
                    "control_type": "Preventive"
                },
                {
                    "id": "container-escape",
                    "type": "Surface",
                    "subtype": "RCE",
                    "label": "Container Escape",
                    "position": {"x": 500, "y": 300},
                    "cvss_score": 8.4,
                    "exploitability": "Medium"
                }
            ],
            "edges": [
                {
                    "id": "dev-to-registry",
                    "source": "developer",
                    "target": "container-registry",
                    "label": "Push Images"
                },
                {
                    "id": "registry-to-cluster",
                    "source": "container-registry",
                    "target": "kubernetes-cluster",
                    "label": "Pull Images"
                },
                {
                    "id": "pod-security-protects",
                    "source": "pod-security",
                    "target": "kubernetes-cluster",
                    "label": "Security Controls"
                },
                {
                    "id": "network-policies-protect",
                    "source": "network-policies",
                    "target": "kubernetes-cluster",
                    "label": "Network Isolation"
                },
                {
                    "id": "cluster-has-vulnerability",
                    "source": "kubernetes-cluster",
                    "target": "container-escape",
                    "label": "Contains Risk"
                }
            ]
        },
        {
            "name": "API Security Gateway",
            "description": "Comprehensive API security model with authentication, rate limiting, and threat protection",
            "category": TemplateCategory.API_SECURITY,
            "use_case": "Secure REST/GraphQL APIs with comprehensive protection layers",
            "complexity": "Intermediate",
            "tags": ["API", "authentication", "rate-limiting", "OAuth"],
            "compliance_frameworks": ["OWASP API Top 10", "OAuth 2.0"],
            "estimated_time": "12-18 minutes",
            "nodes": [
                {
                    "id": "mobile-app",
                    "type": "Actor",
                    "subtype": "ExternalAttacker",
                    "label": "Mobile App",
                    "position": {"x": 100, "y": 100},
                    "sophistication": "Low",
                    "motivation": "Functionality"
                },
                {
                    "id": "api-gateway",
                    "type": "Asset",
                    "subtype": "API",
                    "label": "API Gateway",
                    "position": {"x": 300, "y": 100},
                    "criticality": "High",
                    "data_classification": "Confidential"
                },
                {
                    "id": "oauth-server",
                    "type": "Control",
                    "subtype": "IAMPolicy",
                    "label": "OAuth Authorization Server",
                    "position": {"x": 300, "y": 200},
                    "effectiveness": 90,
                    "control_type": "Preventive"
                },
                {
                    "id": "rate-limiter",
                    "type": "Control",
                    "subtype": "WAF",
                    "label": "Rate Limiting",
                    "position": {"x": 400, "y": 50},
                    "effectiveness": 80,
                    "control_type": "Preventive"
                },
                {
                    "id": "api-abuse",
                    "type": "Surface",
                    "subtype": "IDOR",
                    "label": "API Abuse",
                    "position": {"x": 500, "y": 150},
                    "cvss_score": 7.5,
                    "exploitability": "Medium"
                },
                {
                    "id": "backend-service",
                    "type": "Asset",
                    "subtype": "WebApp",
                    "label": "Backend Service",
                    "position": {"x": 600, "y": 100},
                    "criticality": "High",
                    "data_classification": "Confidential"
                }
            ],
            "edges": [
                {
                    "id": "app-to-gateway",
                    "source": "mobile-app",
                    "target": "api-gateway",
                    "label": "API Requests"
                },
                {
                    "id": "gateway-to-oauth",
                    "source": "api-gateway",
                    "target": "oauth-server",
                    "label": "Token Validation"
                },
                {
                    "id": "rate-limiter-protects-gateway",
                    "source": "rate-limiter",
                    "target": "api-gateway",
                    "label": "DDoS Protection"
                },
                {
                    "id": "gateway-has-vulnerability",
                    "source": "api-gateway",
                    "target": "api-abuse",
                    "label": "Contains Risk"
                },
                {
                    "id": "gateway-to-backend",
                    "source": "api-gateway",
                    "target": "backend-service",
                    "label": "Processed Requests"
                }
            ]
        }
    ]

async def initialize_default_templates():
    """Initialize default templates if they don't exist"""
    try:
        # Check if templates already exist
        existing_count = await db.templates.count_documents({})
        if existing_count > 0:
            logger.info(f"Templates already initialized: {existing_count} templates found")
            return
        
        default_templates = get_default_templates()
        template_docs = []
        
        for template_data in default_templates:
            template = SecurityTemplate(**template_data)
            prepared_data = prepare_for_mongo(template.dict())
            template_docs.append(prepared_data)
        
        if template_docs:
            await db.templates.insert_many(template_docs)
            logger.info(f"Initialized {len(template_docs)} default templates")
        
    except Exception as e:
        logger.error(f"Failed to initialize default templates: {e}")

# Initialize templates on startup
@app.on_event("startup")
async def startup_event():
    await initialize_default_templates()

# Security Node Types
class NodeType(str, Enum):
    ACTOR = "Actor"
    ASSET = "Asset"
    SURFACE = "Surface"
    CONTROL = "Control"
    ZONE = "Zone"
    SIGNAL = "Signal"

class ActorSubtype(str, Enum):
    EXTERNAL_ATTACKER = "ExternalAttacker"
    INSIDER = "Insider"
    SERVICE_ACCOUNT = "ServiceAccount"

class AssetSubtype(str, Enum):
    WEB_APP = "WebApp"
    API = "API"
    DATABASE = "Database"
    S3_BUCKET = "S3Bucket"
    VM = "VM"
    MOBILE_APP = "MobileApp"
    IMDS = "IMDS"

class SurfaceSubtype(str, Enum):
    SSRF = "SSRF"
    SQLI = "SQLi"
    IDOR = "IDOR"
    RCE = "RCE"
    XSS = "XSS"
    WEAK_IAM = "WeakIAM"

class ControlSubtype(str, Enum):
    WAF = "WAF"
    EDR = "EDR"
    EGRESS_PROXY = "EgressProxy"
    IAM_POLICY = "IAMPolicy"
    NETWORK_ACL = "NetworkACL"

# Models
class SecurityNode(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: NodeType
    subtype: str
    label: str
    position: Dict[str, float] = {"x": 0, "y": 0}
    data: Dict[str, Any] = {}
    mitre_ids: List[str] = []
    cve_ids: List[str] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SecurityEdge(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source: str
    target: str
    type: str = "default"
    label: str = ""
    data: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SecurityDiagram(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str = ""
    nodes: List[SecurityNode] = []
    edges: List[SecurityEdge] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DiagramCreate(BaseModel):
    title: str
    description: str = ""

class EnhancedSimulationResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    diagram_id: str
    attack_paths: List[Dict[str, Any]] = []
    recommendations: List[str] = []
    mitre_techniques: List[str] = []
    mitre_coverage: Dict[str, Any] = {}
    risk_score: float = 0.0
    overall_risk_level: str = "Low"
    detection_coverage: float = 0.0
    technique_details: Dict[str, Any] = {}
    suggested_controls: List[str] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Alias for backward compatibility
SimulationResult = EnhancedSimulationResult

# Template System Models
class TemplateCategory(str, Enum):
    WEB_APPLICATION = "Web Application"
    CLOUD_NATIVE = "Cloud Native"
    ZERO_TRUST = "Zero Trust"
    ENTERPRISE = "Enterprise Network"
    IOT_DEVICE = "IoT Device"
    API_SECURITY = "API Security"
    DEVSECOPS = "DevSecOps"
    FINANCIAL = "Financial Services"

class SecurityTemplate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    category: TemplateCategory
    use_case: str
    complexity: str  # Basic, Intermediate, Advanced
    nodes: List[SecurityNode] = []
    edges: List[SecurityEdge] = []
    tags: List[str] = []
    author: str = "System"
    version: str = "1.0"
    preview_image: Optional[str] = None
    compliance_frameworks: List[str] = []  # NIST, ISO27001, etc.
    estimated_time: str = "5-10 minutes"  # Setup time estimate
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TemplateCreate(BaseModel):
    name: str
    description: str
    category: TemplateCategory
    use_case: str
    complexity: str = "Basic"
    tags: List[str] = []
    nodes: List[SecurityNode] = []
    edges: List[SecurityEdge] = []
    compliance_frameworks: List[str] = []

# Helper functions
def prepare_for_mongo(data):
    """Prepare data for MongoDB storage"""
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, list):
                data[key] = [prepare_for_mongo(item) if isinstance(item, dict) else item for item in value]
            elif isinstance(value, dict):
                data[key] = prepare_for_mongo(value)
    return data

def parse_from_mongo(item):
    """Parse data from MongoDB"""
    if isinstance(item, dict):
        for key, value in item.items():
            if key.endswith('_at') and isinstance(value, str):
                try:
                    item[key] = datetime.fromisoformat(value)
                except ValueError:
                    pass
            elif isinstance(value, list):
                item[key] = [parse_from_mongo(sub_item) if isinstance(sub_item, dict) else sub_item for sub_item in value]
            elif isinstance(value, dict):
                item[key] = parse_from_mongo(value)
    return item

# Routes
@api_router.get("/")
async def root():
    return {"message": "Security Modeling Platform API"}

# Diagram Routes
@api_router.post("/diagrams", response_model=SecurityDiagram)
async def create_diagram(diagram: DiagramCreate):
    diagram_obj = SecurityDiagram(**diagram.dict())
    diagram_dict = prepare_for_mongo(diagram_obj.dict())
    await db.diagrams.insert_one(diagram_dict)
    return diagram_obj

@api_router.get("/diagrams", response_model=List[SecurityDiagram])
async def get_diagrams():
    diagrams = await db.diagrams.find().to_list(1000)
    return [SecurityDiagram(**parse_from_mongo(diagram)) for diagram in diagrams]

@api_router.get("/diagrams/{diagram_id}", response_model=SecurityDiagram)
async def get_diagram(diagram_id: str):
    diagram = await db.diagrams.find_one({"id": diagram_id})
    if not diagram:
        raise HTTPException(status_code=404, detail="Diagram not found")
    return SecurityDiagram(**parse_from_mongo(diagram))

@api_router.put("/diagrams/{diagram_id}", response_model=SecurityDiagram)
async def update_diagram(diagram_id: str, diagram: SecurityDiagram):
    diagram.updated_at = datetime.now(timezone.utc)
    diagram_dict = prepare_for_mongo(diagram.dict())
    result = await db.diagrams.replace_one({"id": diagram_id}, diagram_dict)
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Diagram not found")
    return diagram

@api_router.delete("/diagrams/{diagram_id}")
async def delete_diagram(diagram_id: str):
    result = await db.diagrams.delete_one({"id": diagram_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Diagram not found")
    return {"message": "Diagram deleted successfully"}

# Simulation Routes
@api_router.post("/diagrams/{diagram_id}/simulate", response_model=EnhancedSimulationResult)
async def simulate_attack_paths(diagram_id: str):
    diagram = await db.diagrams.find_one({"id": diagram_id})
    if not diagram:
        raise HTTPException(status_code=404, detail="Diagram not found")
    
    # Run advanced simulation in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    
    def run_simulation():
        try:
            # Build security graph
            nodes = diagram.get("nodes", [])
            edges = diagram.get("edges", [])
            
            simulation_engine.build_security_graph(nodes, edges)
            
            # Find attack paths using advanced algorithms
            attack_paths = simulation_engine.find_attack_paths(max_paths=15, max_length=8)
            
            # Generate recommendations
            recommendations = simulation_engine.generate_recommendations(attack_paths, nodes)
            
            # Calculate overall risk score
            overall_risk_score = simulation_engine.calculate_overall_risk_score(attack_paths)
            
            # Get MITRE techniques from attack paths
            all_mitre_techniques = []
            for path in attack_paths:
                all_mitre_techniques.extend(path.mitre_techniques)
            unique_techniques = list(set(all_mitre_techniques))
            
            # Analyze MITRE coverage
            mitre_coverage = mitre_db.analyze_attack_coverage(unique_techniques)
            
            # Get technique details
            technique_details = {}
            for tech_id in unique_techniques:
                technique = mitre_db.get_technique(tech_id)
                if technique:
                    technique_details[tech_id] = {
                        "name": technique.name,
                        "description": technique.description,
                        "tactics": technique.tactics,
                        "impact_level": technique.impact_level,
                        "complexity": technique.complexity,
                        "detection_methods": technique.detection_methods[:3],  # Top 3
                        "mitigations": technique.mitigations[:3]  # Top 3
                    }
            
            # Determine overall risk level
            if overall_risk_score >= 8.0:
                risk_level = "Critical"
            elif overall_risk_score >= 6.0:
                risk_level = "High"
            elif overall_risk_score >= 4.0:
                risk_level = "Medium"
            else:
                risk_level = "Low"
            
            # Calculate detection coverage
            detection_coverage = mitre_coverage.get("detection_difficulty", 0.0)
            
            # Suggest additional controls
            node_types = [node.get("subtype", "") for node in nodes if node.get("type") == "Asset"]
            additional_techniques = mitre_db.suggest_additional_techniques(unique_techniques, node_types)
            suggested_controls = []
            
            for tech_id in additional_techniques:
                mitigations = mitre_db.get_mitigations(tech_id)
                suggested_controls.extend(mitigations[:2])  # Top 2 per technique
            
            suggested_controls = list(set(suggested_controls))[:10]  # Top 10 unique
            
            # Format attack paths for frontend
            formatted_paths = []
            for path in attack_paths:
                formatted_path = {
                    "steps": [
                        {
                            "node": step.source_node,
                            "action": f"{step.technique} -> {step.target_node}",
                            "mitre_id": step.mitre_id,
                            "complexity": step.complexity.name,
                            "impact": step.impact.name,
                            "detection_likelihood": round(step.detection_likelihood * 100, 1)
                        }
                        for step in path.steps
                    ],
                    "likelihood": path.likelihood,
                    "risk_score": round(path.risk_score, 2),
                    "total_impact": round(path.total_impact, 2),
                    "detection_score": round(path.detection_score * 100, 1),
                    "mitre_techniques": path.mitre_techniques
                }
                formatted_paths.append(formatted_path)
            
            return {
                "attack_paths": formatted_paths,
                "recommendations": recommendations,
                "mitre_techniques": unique_techniques,
                "mitre_coverage": mitre_coverage,
                "risk_score": round(overall_risk_score, 2),
                "overall_risk_level": risk_level,
                "detection_coverage": round(detection_coverage * 100, 1),
                "technique_details": technique_details,
                "suggested_controls": suggested_controls
            }
            
        except Exception as e:
            logger.error(f"Simulation error: {str(e)}")
            # Fallback to basic simulation
            return {
                "attack_paths": [],
                "recommendations": ["Unable to complete advanced analysis. Please check diagram connectivity."],
                "mitre_techniques": [],
                "mitre_coverage": {},
                "risk_score": 0.0,
                "overall_risk_level": "Unknown",
                "detection_coverage": 0.0,
                "technique_details": {},
                "suggested_controls": []
            }
    
    simulation_result = await loop.run_in_executor(executor, run_simulation)
    
    # Create and save simulation result
    enhanced_result = EnhancedSimulationResult(
        diagram_id=diagram_id,
        **simulation_result
    )
    
    # Save simulation result to database
    result_dict = prepare_for_mongo(enhanced_result.dict())
    await db.simulations.insert_one(result_dict)
    
    return enhanced_result

@api_router.get("/diagrams/{diagram_id}/simulations", response_model=List[EnhancedSimulationResult])
async def get_simulations(diagram_id: str):
    simulations = await db.simulations.find({"diagram_id": diagram_id}).to_list(1000)
    return [EnhancedSimulationResult(**parse_from_mongo(sim)) for sim in simulations]

# Advanced Analysis Routes
@api_router.get("/mitre/technique/{technique_id}")
async def get_mitre_technique(technique_id: str):
    """Get detailed information about a MITRE ATT&CK technique"""
    technique = mitre_db.get_technique(technique_id)
    if not technique:
        raise HTTPException(status_code=404, detail="MITRE technique not found")
    
    return {
        "technique_id": technique.technique_id,
        "name": technique.name,
        "description": technique.description,
        "tactics": technique.tactics,
        "platforms": technique.platforms,
        "data_sources": technique.data_sources,
        "detection_methods": technique.detection_methods,
        "mitigations": technique.mitigations,
        "references": technique.references,
        "impact_level": technique.impact_level,
        "complexity": technique.complexity,
        "detection_difficulty": technique.detection_difficulty
    }

@api_router.get("/mitre/techniques/by-tactic/{tactic}")
async def get_techniques_by_tactic(tactic: str):
    """Get all MITRE techniques for a specific tactic"""
    techniques = mitre_db.get_techniques_by_tactic(tactic)
    return [
        {
            "technique_id": tech.technique_id,
            "name": tech.name,
            "description": tech.description[:200] + "..." if len(tech.description) > 200 else tech.description,
            "impact_level": tech.impact_level,
            "complexity": tech.complexity
        }
        for tech in techniques
    ]

@api_router.post("/diagrams/{diagram_id}/analyze-coverage")
async def analyze_mitre_coverage(diagram_id: str):
    """Analyze MITRE ATT&CK coverage of a security diagram"""
    diagram = await db.diagrams.find_one({"id": diagram_id})
    if not diagram:
        raise HTTPException(status_code=404, detail="Diagram not found")
    
    # Extract MITRE techniques from diagram nodes
    nodes = diagram.get("nodes", [])
    all_techniques = []
    
    for node in nodes:
        mitre_ids = node.get("mitre_ids", [])
        all_techniques.extend(mitre_ids)
    
    # Analyze coverage
    coverage = mitre_db.analyze_attack_coverage(all_techniques)
    
    # Add node type suggestions
    node_types = [node.get("subtype", "") for node in nodes if node.get("type") == "Asset"]
    suggested_techniques = mitre_db.suggest_additional_techniques(all_techniques, node_types)
    
    coverage["suggested_additional_techniques"] = [
        {
            "technique_id": tech_id,
            "name": mitre_db.get_technique(tech_id).name if mitre_db.get_technique(tech_id) else "Unknown",
            "reason": "Based on asset types in diagram"
        }
        for tech_id in suggested_techniques
    ]
    
    return coverage

@api_router.get("/diagrams/{diagram_id}/risk-analysis")
async def get_risk_analysis(diagram_id: str):
    """Get comprehensive risk analysis for a diagram"""
    # Get latest simulation
    latest_sim = await db.simulations.find_one(
        {"diagram_id": diagram_id}, 
        sort=[("created_at", -1)]
    )
    
    if not latest_sim:
        raise HTTPException(status_code=404, detail="No simulation results found")
    
    simulation = EnhancedSimulationResult(**parse_from_mongo(latest_sim))
    
    # Calculate additional risk metrics
    risk_analysis = {
        "overall_risk_score": simulation.risk_score,
        "risk_level": simulation.overall_risk_level,
        "attack_paths_count": len(simulation.attack_paths),
        "mitre_techniques_count": len(simulation.mitre_techniques),
        "detection_coverage": simulation.detection_coverage,
        "recommendations_count": len(simulation.recommendations),
        "risk_distribution": {
            "critical": len([p for p in simulation.attack_paths if p.get("risk_score", 0) >= 8]),
            "high": len([p for p in simulation.attack_paths if 6 <= p.get("risk_score", 0) < 8]),
            "medium": len([p for p in simulation.attack_paths if 4 <= p.get("risk_score", 0) < 6]),
            "low": len([p for p in simulation.attack_paths if p.get("risk_score", 0) < 4])
        },
        "top_attack_vectors": simulation.attack_paths[:5],  # Top 5 most dangerous
        "critical_mitre_techniques": [
            tech_id for tech_id, details in simulation.technique_details.items()
            if details.get("impact_level") == "HIGH"
        ],
        "coverage_gaps": simulation.mitre_coverage.get("recommended_mitigations", [])[:5]
    }
    
    return risk_analysis

def _smart_hierarchical_layout(G: nx.DiGraph, nodes: List[Dict]) -> Dict[str, Dict[str, float]]:
    """Smart hierarchical layout based on security model semantics"""
    
    # Define security layer hierarchy
    layer_order = {
        "Zone": 0,      # Network zones at the top
        "Actor": 1,     # Threat actors 
        "Surface": 2,   # Attack surfaces
        "Asset": 3,     # Protected assets
        "Control": 4,   # Security controls
        "Signal": 5     # Detection signals
    }
    
    # Group nodes by type and layer
    layers = {}
    for node in nodes:
        node_type = node.get("type", "Unknown")
        layer = layer_order.get(node_type, 3)  # Default to asset layer
        
        if layer not in layers:
            layers[layer] = []
        layers[layer].append(node)
    
    layout_positions = {}
    layer_height = 200
    base_y = 100
    
    for layer_idx, layer_nodes in layers.items():
        y_pos = base_y + (layer_idx * layer_height)
        
        # Calculate spacing for nodes in this layer
        total_width = max(1200, len(layer_nodes) * 250)
        node_spacing = total_width / max(len(layer_nodes), 1)
        start_x = -(total_width / 2) + (node_spacing / 2)
        
        # Position nodes in layer with smart grouping by subtype
        subtype_groups = {}
        for node in layer_nodes:
            subtype = node.get("subtype", "default")
            if subtype not in subtype_groups:
                subtype_groups[subtype] = []
            subtype_groups[subtype].append(node)
        
        x_offset = start_x
        for subtype, subtype_nodes in subtype_groups.items():
            for i, node in enumerate(subtype_nodes):
                layout_positions[node["id"]] = {
                    "x": x_offset + (i * 150),
                    "y": y_pos
                }
            x_offset += len(subtype_nodes) * 150 + 100  # Gap between subtypes
    
    return layout_positions

def _circular_layout_by_type(G: nx.DiGraph, nodes: List[Dict]) -> Dict[str, Dict[str, float]]:
    """Circular layout with nodes grouped by type"""
    
    # Group nodes by type
    type_groups = {}
    for node in nodes:
        node_type = node.get("type", "Unknown")
        if node_type not in type_groups:
            type_groups[node_type] = []
        type_groups[node_type].append(node)
    
    layout_positions = {}
    center_x, center_y = 400, 300
    
    if len(type_groups) == 1:
        # Single type - simple circle
        radius = 200
        nodes_list = list(type_groups.values())[0]
        for i, node in enumerate(nodes_list):
            angle = 2 * math.pi * i / len(nodes_list)
            layout_positions[node["id"]] = {
                "x": center_x + radius * math.cos(angle),
                "y": center_y + radius * math.sin(angle)
            }
    else:
        # Multiple types - concentric circles
        base_radius = 150
        for type_idx, (node_type, type_nodes) in enumerate(type_groups.items()):
            radius = base_radius + (type_idx * 120)
            for i, node in enumerate(type_nodes):
                angle = 2 * math.pi * i / len(type_nodes)
                layout_positions[node["id"]] = {
                    "x": center_x + radius * math.cos(angle),
                    "y": center_y + radius * math.sin(angle)
                }
    
    return layout_positions

def _layered_security_layout(G: nx.DiGraph, nodes: List[Dict]) -> Dict[str, Dict[str, float]]:
    """Security-focused layered layout (Outside-In approach)"""
    
    # Define security perimeter layers (outside to inside)
    security_layers = {
        "Internet": 0,
        "ExternalAttacker": 0,
        "DMZ": 1,
        "WAF": 1,
        "EgressProxy": 1,
        "Internal": 2,
        "WebApp": 2,
        "API": 2,
        "SecureEnclave": 3,
        "Database": 3,
        "ActiveDirectory": 3
    }
    
    # Group nodes by security layer
    layers = {}
    for node in nodes:
        subtype = node.get("subtype", "default")
        layer = security_layers.get(subtype, 2)  # Default to internal layer
        
        if layer not in layers:
            layers[layer] = []
        layers[layer].append(node)
    
    layout_positions = {}
    center_x, center_y = 400, 300
    base_radius = 100
    
    for layer_idx, layer_nodes in layers.items():
        radius = base_radius + (layer_idx * 150)
        
        for i, node in enumerate(layer_nodes):
            angle = 2 * math.pi * i / len(layer_nodes)
            layout_positions[node["id"]] = {
                "x": center_x + radius * math.cos(angle),
                "y": center_y + radius * math.sin(angle)
            }
    
    return layout_positions

def _network_topology_layout(G: nx.DiGraph, nodes: List[Dict]) -> Dict[str, Dict[str, float]]:
    """Network topology-aware layout using graph structure"""
    
    if len(nodes) <= 1:
        return {nodes[0]["id"]: {"x": 400, "y": 300}} if nodes else {}
    
    # Use NetworkX's hierarchical layout if graph is a DAG
    try:
        if nx.is_directed_acyclic_graph(G):
            # Layered layout for DAGs
            layers = list(nx.topological_generations(G))
            layout_positions = {}
            
            layer_height = 200
            for layer_idx, layer_nodes in enumerate(layers):
                y_pos = 100 + (layer_idx * layer_height)
                node_spacing = 800 / max(len(layer_nodes), 1)
                
                for i, node_id in enumerate(layer_nodes):
                    layout_positions[node_id] = {
                        "x": 100 + (i * node_spacing),
                        "y": y_pos
                    }
            
            return layout_positions
        else:
            # Use spring layout for cyclic graphs
            pos = nx.spring_layout(G, k=2, iterations=50)
            return _scale_layout(pos, 800, 600)
            
    except:
        # Fallback to spring layout
        pos = nx.spring_layout(G, k=2, iterations=50)
        return _scale_layout(pos, 800, 600)

def _scale_layout(pos: Dict, width: int, height: int) -> Dict[str, Dict[str, float]]:
    """Scale NetworkX layout to desired dimensions"""
    if not pos:
        return {}
    
    # Get min/max coordinates
    x_coords = [coord[0] for coord in pos.values()]
    y_coords = [coord[1] for coord in pos.values()]
    
    min_x, max_x = min(x_coords), max(x_coords)
    min_y, max_y = min(y_coords), max(y_coords)
    
    # Avoid division by zero
    x_range = max_x - min_x if max_x != min_x else 1
    y_range = max_y - min_y if max_y != min_y else 1
    
    # Scale and center
    layout_positions = {}
    for node_id, (x, y) in pos.items():
        scaled_x = ((x - min_x) / x_range) * (width - 100) + 50
        scaled_y = ((y - min_y) / y_range) * (height - 100) + 50
        
        layout_positions[node_id] = {
            "x": scaled_x,
            "y": scaled_y
        }
    
    return layout_positions

@api_router.post("/diagrams/{diagram_id}/auto-layout")
async def auto_layout_diagram(diagram_id: str, algorithm: Optional[str] = "smart_hierarchical"):
    """Generate automatic layout for diagram nodes with advanced algorithms"""
    from typing import Dict, List, Tuple
    
    diagram = await db.diagrams.find_one({"id": diagram_id})
    if not diagram:
        raise HTTPException(status_code=404, detail="Diagram not found")
    
    nodes = diagram.get("nodes", [])
    edges = diagram.get("edges", [])
    
    if not nodes:
        return {"layout_positions": {}, "algorithm": algorithm, "node_count": 0}
    
    # Create NetworkX graph
    G = nx.DiGraph()
    
    # Add nodes with attributes
    for node in nodes:
        G.add_node(node["id"], 
                  type=node.get("type", "Unknown"),
                  subtype=node.get("subtype", ""),
                  label=node.get("label", ""))
    
    # Add edges
    for edge in edges:
        source = edge.get("source")
        target = edge.get("target")
        if source and target and G.has_node(source) and G.has_node(target):
            G.add_edge(source, target)
    
    layout_positions = {}
    
    if algorithm == "smart_hierarchical":
        # Enhanced hierarchical layout based on security relationships
        layout_positions = _smart_hierarchical_layout(G, nodes)
        
    elif algorithm == "force_directed":
        # Spring layout with custom parameters
        if len(nodes) > 1:
            pos = nx.spring_layout(G, k=3, iterations=50, seed=42)
            # Scale and center the layout
            layout_positions = _scale_layout(pos, 800, 600)
        else:
            layout_positions = {nodes[0]["id"]: {"x": 400, "y": 300}}
            
    elif algorithm == "circular":
        # Circular layout with node type grouping
        layout_positions = _circular_layout_by_type(G, nodes)
        
    elif algorithm == "layered_security":
        # Security-focused layered layout
        layout_positions = _layered_security_layout(G, nodes)
        
    elif algorithm == "network_topology":
        # Network topology-aware layout
        layout_positions = _network_topology_layout(G, nodes)
        
    else:
        # Default to smart hierarchical
        layout_positions = _smart_hierarchical_layout(G, nodes)
    
    return {
        "layout_positions": layout_positions,
        "algorithm": algorithm,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "graph_info": {
            "is_connected": nx.is_connected(G.to_undirected()),
            "node_types": list(set(node.get("type", "Unknown") for node in nodes)),
            "density": nx.density(G) if len(nodes) > 1 else 0
        }
    }

# Enhanced Auto-Layout API with algorithm selection
@api_router.get("/diagrams/{diagram_id}/layout-algorithms")
async def get_available_layout_algorithms():
    """Get available auto-layout algorithms"""
    return {
        "algorithms": [
            {
                "id": "smart_hierarchical",
                "name": "Smart Hierarchical",
                "description": "Security-aware hierarchical layout based on threat model semantics",
                "best_for": "Security models with clear asset/threat relationships",
                "complexity": "O(n)"
            },
            {
                "id": "force_directed", 
                "name": "Force-Directed",
                "description": "Spring-based layout that minimizes edge crossings",
                "best_for": "General network diagrams with natural clustering",
                "complexity": "O(n²)"
            },
            {
                "id": "circular",
                "name": "Circular",
                "description": "Circular layout with nodes grouped by type",
                "best_for": "Showing relationships between different security domains",
                "complexity": "O(n)"
            },
            {
                "id": "layered_security",
                "name": "Layered Security",
                "description": "Concentric circles representing security perimeters",
                "best_for": "Defense-in-depth security architectures",
                "complexity": "O(n)"
            },
            {
                "id": "network_topology",
                "name": "Network Topology",
                "description": "Graph structure-aware layout using topological analysis",
                "best_for": "Complex network diagrams with hierarchical structure",
                "complexity": "O(n log n)"
            }
        ]
    }

# Template Management APIs
@api_router.get("/templates", response_model=List[SecurityTemplate])
async def get_templates(category: Optional[str] = None, complexity: Optional[str] = None):
    """Get all security templates with optional filtering"""
    query = {}
    if category:
        query["category"] = category
    if complexity:
        query["complexity"] = complexity
    
    templates = await db.templates.find(query).to_list(length=None)
    return [parse_from_mongo(template) for template in templates]

@api_router.get("/templates/{template_id}", response_model=SecurityTemplate)
async def get_template(template_id: str):
    """Get a specific template by ID"""
    template = await db.templates.find_one({"id": template_id})
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return parse_from_mongo(template)

@api_router.post("/templates", response_model=SecurityTemplate)
async def create_template(template: TemplateCreate):
    """Create a new security template"""
    template_data = SecurityTemplate(**template.dict())
    prepared_data = prepare_for_mongo(template_data.dict())
    await db.templates.insert_one(prepared_data)
    return template_data

@api_router.put("/templates/{template_id}", response_model=SecurityTemplate)
async def update_template(template_id: str, template: TemplateCreate):
    """Update an existing template"""
    existing = await db.templates.find_one({"id": template_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Template not found")
    
    updated_data = template.dict()
    updated_data["updated_at"] = datetime.now(timezone.utc)
    prepared_data = prepare_for_mongo(updated_data)
    
    await db.templates.update_one({"id": template_id}, {"$set": prepared_data})
    
    # Return the updated template
    updated_template = await db.templates.find_one({"id": template_id})
    return parse_from_mongo(updated_template)

@api_router.delete("/templates/{template_id}")
async def delete_template(template_id: str):
    """Delete a template"""
    result = await db.templates.delete_one({"id": template_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"message": "Template deleted successfully"}

@api_router.post("/templates/{template_id}/apply/{diagram_id}")
async def apply_template_to_diagram(template_id: str, diagram_id: str):
    """Apply a template to an existing diagram"""
    # Get template
    template = await db.templates.find_one({"id": template_id})
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Get diagram
    diagram = await db.diagrams.find_one({"id": diagram_id})
    if not diagram:
        raise HTTPException(status_code=404, detail="Diagram not found")
    
    # Apply template nodes and edges to diagram
    template_nodes = template.get("nodes", [])
    template_edges = template.get("edges", [])
    
    # Generate new IDs for template nodes to avoid conflicts
    node_id_mapping = {}
    new_nodes = []
    
    for node in template_nodes:
        old_id = node["id"]
        new_id = f"template-{old_id}-{uuid.uuid4().hex[:8]}"
        node_id_mapping[old_id] = new_id
        
        new_node = node.copy()
        new_node["id"] = new_id
        new_nodes.append(new_node)
    
    # Update edge IDs to match new node IDs
    new_edges = []
    for edge in template_edges:
        new_edge = edge.copy()
        new_edge["id"] = f"template-edge-{uuid.uuid4().hex[:8]}"
        new_edge["source"] = node_id_mapping.get(edge["source"], edge["source"])
        new_edge["target"] = node_id_mapping.get(edge["target"], edge["target"])
        new_edges.append(new_edge)
    
    # Combine with existing diagram nodes and edges
    existing_nodes = diagram.get("nodes", [])
    existing_edges = diagram.get("edges", [])
    
    updated_nodes = existing_nodes + new_nodes
    updated_edges = existing_edges + new_edges
    
    # Update diagram
    update_data = {
        "nodes": updated_nodes,
        "edges": updated_edges,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.diagrams.update_one({"id": diagram_id}, {"$set": update_data})
    
    return {
        "message": "Template applied successfully",
        "nodes_added": len(new_nodes),
        "edges_added": len(new_edges),
        "template_name": template.get("name", "Unknown")
    }

@api_router.get("/templates/categories")
async def get_template_categories():
    """Get available template categories"""
    return [{"id": cat.value, "name": cat.value} for cat in TemplateCategory]

# Intelligent Node System APIs - Phase 1
@api_router.get("/intelligent-nodes/{node_subtype}/template")
async def get_node_template(node_subtype: str):
    """Get intelligent template for a specific node subtype"""
    template = intelligent_node_engine.get_node_template(node_subtype)
    if not template:
        raise HTTPException(status_code=404, detail=f"No intelligent template found for {node_subtype}")
    
    return {
        "node_type": template.node_type,
        "node_subtype": template.node_subtype,
        "required_branches": [branch.value for branch in template.required_branches],
        "security_prompts": [
            {
                "id": prompt.id,
                "question": prompt.question,
                "type": prompt.type.value,
                "options": prompt.options,
                "default_value": prompt.default_value,
                "help_text": prompt.help_text,
                "related_branch": prompt.related_branch.value
            } for prompt in template.security_prompts
        ],
        "risk_factors": template.risk_factors
    }

@api_router.get("/intelligent-nodes/{node_subtype}/prompts")
async def get_security_prompts(node_subtype: str):
    """Get security prompts for guided node configuration"""
    prompts = intelligent_node_engine.get_security_prompts(node_subtype)
    if not prompts:
        raise HTTPException(status_code=404, detail=f"No security prompts found for {node_subtype}")
    
    return {
        "node_subtype": node_subtype,
        "prompts": [
            {
                "id": prompt.id,
                "question": prompt.question,
                "type": prompt.type.value,
                "options": prompt.options,
                "default_value": prompt.default_value,
                "help_text": prompt.help_text,
                "related_branch": prompt.related_branch.value,
                "validation_rules": prompt.validation_rules
            } for prompt in prompts
        ]
    }

@api_router.post("/intelligent-nodes/{node_subtype}/create-branches")
async def create_security_branches(node_subtype: str):
    """Create required security branches for a node"""
    branches = intelligent_node_engine.create_security_branches(node_subtype)
    if not branches:
        return {"message": f"No required branches for {node_subtype}", "branches": []}
    
    return {
        "node_subtype": node_subtype,
        "branches": [
            {
                "id": branch.id,
                "name": branch.name,
                "type": branch.type.value,
                "required": branch.required,
                "completed": branch.completed,
                "value": branch.value,
                "description": branch.description
            } for branch in branches
        ]
    }

@api_router.post("/intelligent-nodes/{node_subtype}/validate-completeness")
async def validate_node_completeness(
    node_subtype: str, 
    branches: List[Dict[str, Any]]
):
    """Validate if a node configuration is complete"""
    # Convert dict branches to SecurityBranch objects
    security_branches = []
    for branch_data in branches:
        branch = SecurityBranch(
            id=branch_data.get("id", ""),
            name=branch_data.get("name", ""),
            type=branch_data.get("type", "LOGIN"),
            required=branch_data.get("required", True),
            completed=branch_data.get("completed", False),
            value=branch_data.get("value"),
            description=branch_data.get("description", "")
        )
        security_branches.append(branch)
    
    validation_result = intelligent_node_engine.validate_node_completeness(node_subtype, security_branches)
    
    return {
        "node_subtype": node_subtype,
        "validation": validation_result,
        "recommendations": intelligent_node_engine.generate_security_recommendations(node_subtype, security_branches)
    }

@api_router.post("/intelligent-nodes/{node_subtype}/calculate-risk")
async def calculate_node_risk(
    node_subtype: str,
    branch_values: Dict[str, Any]
):
    """Calculate risk score based on node configuration"""
    risk_score = intelligent_node_engine.calculate_node_risk_score(node_subtype, branch_values)
    
    risk_level = "Low"
    if risk_score >= 8.0:
        risk_level = "Critical"
    elif risk_score >= 6.0:
        risk_level = "High"
    elif risk_score >= 4.0:
        risk_level = "Medium"
    
    return {
        "node_subtype": node_subtype,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "branch_values": branch_values,
        "recommendations": intelligent_node_engine.generate_security_recommendations(
            node_subtype, 
            []  # Pass empty list since we only have branch_values, not SecurityBranch objects
        )
    }

@api_router.get("/intelligent-nodes/supported-types")
async def get_supported_intelligent_types():
    """Get list of node types that support intelligent expansion"""
    supported_types = list(intelligent_node_engine.node_templates.keys())
    
    type_info = []
    for node_subtype in supported_types:
        template = intelligent_node_engine.get_node_template(node_subtype)
        if template:
            type_info.append({
                "node_subtype": node_subtype,
                "node_type": template.node_type,
                "required_branches_count": len(template.required_branches),
                "security_prompts_count": len(template.security_prompts),
                "has_risk_factors": len(template.risk_factors) > 0
            })
    
    return {
        "supported_types": type_info,
        "total_count": len(supported_types)
    }

# ============================================================================
# EXPANDED INTELLIGENT NODES ENDPOINTS - PHASE 1 ENHANCEMENT
# ============================================================================

@api_router.get("/expanded-nodes/debug")
async def debug_expanded_types():
    """Debug endpoint to see what expanded engine returns"""
    try:
        supported_types = expanded_node_engine.get_supported_node_types()
        return {
            "source": "expanded_node_engine",
            "count": len(supported_types),
            "types": supported_types,
            "first_5": supported_types[:5] if supported_types else [],
            "new_types": [t for t in supported_types if t in ['ElasticLoadBalancer', 'ConfigurationManagement', 'ServiceMesh', 'DataLakeStorage', 'EdgeComputing', 'QuantumSafeEncryption']]
        }
    except Exception as e:
        return {"error": str(e)}

@api_router.get("/expanded-nodes/supported-types")
async def get_expanded_supported_types():
    """Get all supported node types with enhanced metadata and questionnaire information"""
    supported_types = expanded_node_engine.get_supported_node_types()
    
    type_info = []
    for node_type in supported_types:
        template = expanded_node_engine.node_templates.get(node_type, {})
        threat_intel = template.get("threat_intelligence", {})
        questionnaires = template.get("questionnaires", {})
        
        if template:
            # Count questionnaire questions for each level
            level_counts = {}
            for level_name, questions in questionnaires.items():
                level_counts[level_name.value if hasattr(level_name, 'value') else str(level_name)] = len(questions)
            
            type_info.append({
                "node_subtype": node_type,
                "node_type": template.get("node_type", "Asset"),
                "category": template.get("category", "Unknown"),
                "description": template.get("description", ""),
                "threat_intelligence": {
                    "cve_count": threat_intel.cve_count if hasattr(threat_intel, 'cve_count') else 0,
                    "recent_threat_count": len(threat_intel.recent_threats) if hasattr(threat_intel, 'recent_threats') else 0
                },
                "questionnaire_levels": list(level_counts.keys()),
                "questionnaire_counts": level_counts,
                "required_branches_count": len(template.get("required_branches", [])),
                "has_dependencies": False  # We can implement this later if needed
            })
    
    # Group by category
    categories = {}
    for info in type_info:
        category = info["category"]
        if category not in categories:
            categories[category] = []
        categories[category].append(info)
    
    return {
        "supported_types": type_info,
        "by_category": categories,
        "total_count": len(supported_types),
        "categories": list(categories.keys())
    }

@api_router.get("/expanded-nodes/{node_subtype}/questionnaire/{level}")
async def get_expanded_questionnaire(node_subtype: str, level: str):
    """Get questionnaire for specific node type and level (basic/advanced/expert)"""
    try:
        questionnaire_level = LoaderQuestionnaireLevel(level.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid questionnaire level. Must be one of: {[l.value for l in LoaderQuestionnaireLevel]}")
    
    # Use the new file-based questionnaire system
    response = questionnaire_loader.create_questionnaire_response(node_subtype, questionnaire_level)
    
    if "error" in response:
        raise HTTPException(status_code=404, detail=response["error"])
    
    # Add threat intelligence from the old system for now
    try:
        threat_intelligence = expanded_node_engine._get_threat_intelligence_summary(node_subtype)
    except:
        threat_intelligence = {}
    
    response["threat_intelligence"] = threat_intelligence
    return response

def _extract_risk_factors(node_subtype: str, enhanced_responses: Dict[str, Any], risk_assessment: Dict[str, Any]) -> Dict[str, Any]:
    """Extract and structure risk factors from responses and assessment"""
    risk_factors = {}
    
    # Extract key risk indicators from responses
    for key, value in enhanced_responses.items():
        if value and key in ['encryption_enabled', 'access_controls', 'monitoring_enabled', 'backup_strategy', 'network_segmentation']:
            risk_factors[key] = {
                "value": value,
                "impact": "positive" if value else "negative"
            }
    
    # Add risk assessment components
    if "risk_components" in risk_assessment:
        risk_factors["assessment_components"] = risk_assessment["risk_components"]
    
    # Add composite risk score
    if "composite_risk_score" in risk_assessment:
        risk_factors["composite_score"] = risk_assessment["composite_risk_score"]
    
    return risk_factors

@api_router.post("/expanded-nodes/{node_subtype}/calculate-risk")
async def calculate_expanded_risk(node_subtype: str, request: Dict[str, Any]):
    """Calculate comprehensive risk assessment using enhanced probabilistic model"""
    responses = request.get("responses", {})
    business_context = request.get("business_context", {})
    
    # Add business context to responses for risk calculation
    enhanced_responses = {**responses, **business_context}
    
    try:
        risk_assessment = expanded_node_engine.calculate_comprehensive_risk(node_subtype, enhanced_responses)
        recommendations = expanded_node_engine.generate_security_recommendations(
            node_subtype, 
            enhanced_responses, 
            risk_assessment["composite_risk_score"]
        )
        
        return {
            "node_subtype": node_subtype,
            "risk_assessment": risk_assessment,
            "risk_factors": _extract_risk_factors(node_subtype, enhanced_responses, risk_assessment),
            "security_recommendations": recommendations,
            "calculation_timestamp": datetime.now(timezone.utc).isoformat(),
            "input_summary": {
                "response_count": len(responses),
                "business_context_provided": len(business_context) > 0,
                "risk_factors_analyzed": len([k for k, v in enhanced_responses.items() if v])
            }
        }
    
    except Exception as e:
        logger.error(f"Risk calculation error for {node_subtype}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Risk calculation failed: {str(e)}")

@api_router.post("/expanded-nodes/bulk-risk-assessment")
async def bulk_risk_assessment(request: Dict[str, Any]):
    """Priority 2: Enhanced bulk risk assessment for multiple nodes simultaneously with cross-node correlations"""
    nodes_data = request.get("nodes", [])
    business_context = request.get("business_context", {})
    
    if not nodes_data:
        raise HTTPException(status_code=400, detail="No nodes provided for assessment")
    
    try:
        # Use the enhanced bulk assessment method
        bulk_result = expanded_node_engine.perform_bulk_risk_assessment(nodes_data, business_context)
        
        # Add comprehensive metadata
        bulk_result["assessment_metadata"] = {
            "assessment_timestamp": datetime.now(timezone.utc).isoformat(),
            "assessment_version": "2.0_enhanced",
            "features_enabled": [
                "probabilistic_modeling",
                "cross_node_correlations", 
                "risk_amplification_factors",
                "monte_carlo_simulation"
            ],
            "business_context_applied": len(business_context) > 0
        }
        
        return bulk_result
        
    except Exception as e:
        logger.error(f"Bulk risk assessment error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Bulk risk assessment failed: {str(e)}")

@api_router.get("/expanded-nodes/categories")
async def get_node_categories():
    """Get all available node categories with descriptions"""
    categories_info = {}
    
    for node_type in expanded_node_engine.get_supported_node_types():
        template = expanded_node_engine.node_templates.get(node_type, {})
        category = template.get("category", "Unknown")
        
        if category not in categories_info:
            categories_info[category] = []
        
        # Add node type information to category
        node_info = {
            "node_subtype": node_type,
            "node_type": template.get("node_type", "Asset"),
            "description": template.get("description", ""),
            "threat_intelligence": {
                "cve_count": 0,
                "recent_threats": []
            }
        }
        
        # Add threat intelligence if available
        threat_intel = template.get("threat_intelligence", {})
        if hasattr(threat_intel, 'cve_count'):
            node_info["threat_intelligence"]["cve_count"] = threat_intel.cve_count
        if hasattr(threat_intel, 'recent_threats'):
            node_info["threat_intelligence"]["recent_threats"] = list(threat_intel.recent_threats)[:3]  # Top 3
        
        categories_info[category].append(node_info)
    
    # Return direct category mapping instead of categories array
    return categories_info

@api_router.post("/expanded-nodes/threat-intelligence-summary")
async def get_threat_intelligence_summary(request: Dict[str, Any]):
    """Get aggregated threat intelligence for selected node types"""
    node_types = request.get("node_types", [])
    
    if not node_types:
        raise HTTPException(status_code=400, detail="No node types provided")
    
    aggregated_intelligence = {
        "total_cve_count": 0,
        "all_threats": set(),
        "all_attack_vectors": set(),
        "all_mitre_techniques": set(),
        "all_threat_actors": set(),
        "node_summaries": []
    }
    
    for node_type in node_types:
        if node_type in expanded_node_engine.node_templates:
            threat_summary = expanded_node_engine._get_threat_intelligence_summary(node_type)
            template = expanded_node_engine.node_templates[node_type]
            
            aggregated_intelligence["total_cve_count"] += threat_summary["cve_count"]
            aggregated_intelligence["all_threats"].update(threat_summary["recent_threats"])
            aggregated_intelligence["all_attack_vectors"].update(threat_summary["primary_attack_vectors"])
            aggregated_intelligence["all_mitre_techniques"].update(threat_summary["mitre_techniques"])
            aggregated_intelligence["all_threat_actors"].update(threat_summary["known_threat_actors"])
            
            aggregated_intelligence["node_summaries"].append({
                "node_type": node_type,
                "category": template.get("category", "Unknown"),
                "threat_summary": threat_summary
            })
    
    # Convert sets to lists and limit to top items
    return {
        "node_type_summaries": aggregated_intelligence["node_summaries"],  # Changed from node_summaries
        "cross_cutting_threats": {  # New field combining multiple threat categories
            "unique_threats": list(aggregated_intelligence["all_threats"])[:10],
            "unique_attack_vectors": list(aggregated_intelligence["all_attack_vectors"])[:10],
            "unique_mitre_techniques": list(aggregated_intelligence["all_mitre_techniques"])[:15],
            "unique_threat_actors": list(aggregated_intelligence["all_threat_actors"])[:10]
        },
        "threat_trends": {  # Changed from aggregated_intelligence
            "total_cve_count": aggregated_intelligence["total_cve_count"],
            "threat_landscape_evolution": "Analysis based on recent threat intelligence data",
            "emerging_patterns": list(aggregated_intelligence["all_threats"])[:5]
        },
        "recommendations": [  # New field with actionable recommendations
            "Implement multi-layered defense strategies across all analyzed node types",
            "Prioritize patching for CVE vulnerabilities identified in the threat intelligence",
            "Enhance monitoring for identified MITRE ATT&CK techniques",
            "Strengthen controls against identified attack vectors",
            "Develop incident response procedures for known threat actor TTPs"
        ],
        "summary_stats": {
            "nodes_analyzed": len(node_types),
            "total_unique_threats": len(aggregated_intelligence["all_threats"]),
            "total_unique_attack_vectors": len(aggregated_intelligence["all_attack_vectors"]),
            "total_mitre_techniques": len(aggregated_intelligence["all_mitre_techniques"]),
            "total_threat_actors": len(aggregated_intelligence["all_threat_actors"])
        },
        "analysis_timestamp": datetime.now(timezone.utc).isoformat()
    }

# ============================================================================
# THREAT INTELLIGENCE ENDPOINTS - PHASE 1 ENHANCEMENT  
# ============================================================================

@api_router.get("/threat-intelligence/node/{node_type}/profile")
async def get_node_threat_profile(node_type: str, force_refresh: bool = False):
    """Get comprehensive threat intelligence profile for a node type"""
    try:
        profile = await threat_intelligence_engine.get_node_threat_profile(node_type, force_refresh)
        
        return {
            "node_type": node_type,
            "threat_profile": {
                "total_cves": profile.total_cves,
                "recent_cves_count": len(profile.recent_cves),
                "high_risk_cves_count": len(profile.high_risk_cves),
                "threat_indicators_count": len(profile.threat_indicators),
                "threat_score": profile.threat_score,
                "threat_level": "Critical" if profile.threat_score >= 8.0 else 
                              "High" if profile.threat_score >= 6.0 else
                              "Medium" if profile.threat_score >= 4.0 else "Low",
                "mitre_techniques": list(profile.mitre_techniques),
                "attack_patterns": profile.attack_patterns,
                "last_updated": profile.last_updated
            },
            "recent_cves": [
                {
                    "cve_id": cve.cve_id,
                    "cvss_score": cve.cvss_score,
                    "severity": cve.severity.value,
                    "description": cve.description,
                    "published_date": cve.published_date,
                    "exploit_available": cve.exploit_available,
                    "mitre_techniques": cve.mitre_techniques
                } for cve in profile.recent_cves[:5]  # Latest 5
            ],
            "high_risk_cves": [
                {
                    "cve_id": cve.cve_id,
                    "cvss_score": cve.cvss_score,
                    "severity": cve.severity.value,
                    "description": cve.description,
                    "exploit_available": cve.exploit_available,
                    "mitre_techniques": cve.mitre_techniques
                } for cve in profile.high_risk_cves[:5]  # Top 5 high-risk
            ],
            "threat_indicators": [
                {
                    "indicator_id": indicator.indicator_id,
                    "indicator_type": indicator.indicator_type,
                    "value": indicator.value,
                    "severity": indicator.severity.value,
                    "category": indicator.category.value,
                    "confidence": indicator.confidence,
                    "description": indicator.description,
                    "tags": indicator.tags
                } for indicator in profile.threat_indicators[:5]  # Top 5 indicators
            ]
        }
    
    except Exception as e:
        logger.error(f"Threat profile error for {node_type}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get threat profile: {str(e)}")

@api_router.post("/threat-intelligence/correlate-vulnerabilities")
async def correlate_vulnerabilities(request: Dict[str, Any]):
    """Correlate vulnerabilities across multiple nodes"""
    node_configs = request.get("node_configs", [])
    
    if not node_configs:
        raise HTTPException(status_code=400, detail="No node configurations provided")
    
    try:
        correlation_result = await threat_intelligence_engine.correlate_vulnerabilities(node_configs)
        
        return {
            "correlation_analysis": correlation_result,
            "risk_summary": {
                "overall_risk_level": "Critical" if correlation_result["overall_risk_score"] >= 8.0 else
                                     "High" if correlation_result["overall_risk_score"] >= 6.0 else
                                     "Medium" if correlation_result["overall_risk_score"] >= 4.0 else "Low",
                "correlation_strength": "High" if correlation_result["correlation_count"] >= 3 else
                                       "Medium" if correlation_result["correlation_count"] >= 1 else "Low",
                "recommendation": "Immediate attention required for correlated vulnerabilities" if correlation_result["correlation_count"] >= 3 else
                                 "Review correlated attack vectors" if correlation_result["correlation_count"] >= 1 else
                                 "Monitor for emerging correlations"
            }
        }
    
    except Exception as e:
        logger.error(f"Vulnerability correlation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Correlation analysis failed: {str(e)}")

@api_router.post("/threat-intelligence/real-time-score")
async def get_real_time_threat_score(request: Dict[str, Any]):
    """Calculate real-time threat score based on current configuration"""
    node_type = request.get("node_type")
    configuration = request.get("configuration", {})
    
    if not node_type:
        raise HTTPException(status_code=400, detail="Node type is required")
    
    try:
        threat_score = await threat_intelligence_engine.get_real_time_threat_score(node_type, configuration)
        
        # Get base profile for comparison
        profile = await threat_intelligence_engine.get_node_threat_profile(node_type)
        baseline_score = profile.threat_score
        
        score_delta = threat_score - baseline_score
        
        return {
            "node_type": node_type,
            "real_time_threat_score": round(threat_score, 2),
            "baseline_threat_score": round(baseline_score, 2),
            "score_delta": round(score_delta, 2),
            "threat_level": "Critical" if threat_score >= 8.0 else
                           "High" if threat_score >= 6.0 else
                           "Medium" if threat_score >= 4.0 else "Low",
            "risk_factors": {
                "configuration_impact": "Increases Risk" if score_delta > 0 else "Reduces Risk" if score_delta < 0 else "Neutral",
                "impact_magnitude": abs(score_delta),
                "primary_concerns": _identify_primary_concerns(configuration, score_delta)
            },
            "recommendations": _generate_threat_recommendations(node_type, configuration, threat_score),
            "calculation_timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    except Exception as e:
        logger.error(f"Real-time threat scoring error for {node_type}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Threat scoring failed: {str(e)}")

def _identify_primary_concerns(configuration: Dict[str, Any], score_delta: float) -> List[str]:
    """Identify primary security concerns from configuration"""
    concerns = []
    
    if configuration.get("public_access", False):
        concerns.append("Public exposure increases attack surface")
    if configuration.get("weak_authentication", False):
        concerns.append("Weak authentication enables credential attacks")
    if configuration.get("no_encryption", False):
        concerns.append("Lack of encryption exposes data")
    if configuration.get("default_credentials", False):
        concerns.append("Default credentials are easily exploited")
    if configuration.get("outdated_version", False):
        concerns.append("Outdated software contains known vulnerabilities")
    
    if score_delta < 0:  # Positive security controls
        if configuration.get("mfa_enabled", False):
            concerns.append("MFA significantly reduces credential risk")
        if configuration.get("encryption_enabled", False):
            concerns.append("Encryption protects data confidentiality")
        if configuration.get("monitoring_enabled", False):
            concerns.append("Monitoring enables threat detection")
    
    return concerns[:5]  # Top 5 concerns

def _generate_threat_recommendations(node_type: str, configuration: Dict[str, Any], threat_score: float) -> List[Dict[str, str]]:
    """Generate threat-specific recommendations"""
    recommendations = []
    
    if threat_score >= 8.0:
        recommendations.append({
            "priority": "CRITICAL",
            "action": "Immediate security review required",
            "rationale": "Critical threat level detected"
        })
    
    if configuration.get("public_access", False) and not configuration.get("mfa_enabled", False):
        recommendations.append({
            "priority": "HIGH",
            "action": "Implement multi-factor authentication",
            "rationale": "Public access without MFA is high-risk"
        })
    
    if configuration.get("no_encryption", False):
        recommendations.append({
            "priority": "HIGH", 
            "action": "Enable encryption at rest and in transit",
            "rationale": "Unencrypted data is vulnerable to interception"
        })
    
    if not configuration.get("monitoring_enabled", False):
        recommendations.append({
            "priority": "MEDIUM",
            "action": "Implement security monitoring and alerting",
            "rationale": "Monitoring enables early threat detection"
        })
    
    if configuration.get("outdated_version", False):
        recommendations.append({
            "priority": "HIGH",
            "action": "Update to latest version with security patches",
            "rationale": "Outdated software contains known vulnerabilities"
        })
    
    return recommendations[:5]  # Top 5 recommendations

@api_router.get("/threat-intelligence/mitre/{technique_id}")
async def get_mitre_technique_details(technique_id: str):
    """Get details for a specific MITRE ATT&CK technique"""
    technique_details = threat_intelligence_engine.get_mitre_technique_details(technique_id)
    
    if not technique_details:
        raise HTTPException(status_code=404, detail=f"MITRE technique {technique_id} not found")
    
    return {
        "technique_id": technique_id,
        "technique_details": technique_details,
        "related_techniques": [
            tid for tid, details in threat_intelligence_engine.mitre_techniques_map.items() 
            if details.get("tactic") == technique_details.get("tactic") and tid != technique_id
        ][:5]  # Related techniques in same tactic
    }

@api_router.get("/threat-intelligence/dashboard")
async def get_threat_intelligence_dashboard():
    """Get overall threat intelligence dashboard data"""
    try:
        # Get threat profiles for major node types
        major_node_types = ["EC2", "Lambda", "S3", "RDS", "Kubernetes", "WebApp", "Database", "API"]
        dashboard_data = {
            "overall_stats": {
                "total_node_types": len(major_node_types),
                "total_cves": 0,
                "high_risk_nodes": 0,
                "average_threat_score": 0.0
            },
            "threat_trends": [],
            "top_threats": [],
            "mitre_technique_coverage": {},
            "node_risk_distribution": {}
        }
        
        total_threat_score = 0.0
        all_techniques = set()
        
        for node_type in major_node_types:
            try:
                profile = await threat_intelligence_engine.get_node_threat_profile(node_type)
                
                dashboard_data["overall_stats"]["total_cves"] += profile.total_cves
                total_threat_score += profile.threat_score
                
                if profile.threat_score >= 7.0:
                    dashboard_data["overall_stats"]["high_risk_nodes"] += 1
                
                all_techniques.update(profile.mitre_techniques)
                
                # Risk distribution
                risk_level = "Critical" if profile.threat_score >= 8.0 else \
                           "High" if profile.threat_score >= 6.0 else \
                           "Medium" if profile.threat_score >= 4.0 else "Low"
                
                dashboard_data["node_risk_distribution"][node_type] = {
                    "threat_score": profile.threat_score,
                    "risk_level": risk_level,
                    "cve_count": profile.total_cves,
                    "recent_cves": len(profile.recent_cves)
                }
                
                # Top threats from recent CVEs
                for cve in profile.recent_cves[:3]:
                    dashboard_data["top_threats"].append({
                        "threat_id": cve.cve_id,
                        "description": cve.description,
                        "severity": cve.severity.value,
                        "cvss_score": cve.cvss_score,
                        "affected_node_types": [node_type],
                        "published_date": cve.published_date
                    })
            
            except Exception as e:
                logger.warning(f"Failed to get profile for {node_type}: {str(e)}")
                continue
        
        # Calculate averages
        dashboard_data["overall_stats"]["average_threat_score"] = round(
            total_threat_score / len(major_node_types), 2
        )
        
        # MITRE technique coverage
        technique_tactics = {}
        for technique_id in all_techniques:
            technique_details = threat_intelligence_engine.get_mitre_technique_details(technique_id)
            if technique_details:
                tactic = technique_details.get("tactic", "Unknown")
                if tactic not in technique_tactics:
                    technique_tactics[tactic] = []
                technique_tactics[tactic].append(technique_id)
        
        dashboard_data["mitre_technique_coverage"] = {
            "total_techniques": len(all_techniques),
            "by_tactic": technique_tactics,
            "coverage_percentage": round((len(all_techniques) / 200) * 100, 1)  # Assume ~200 total techniques
        }
        
        # Sort top threats by CVSS score
        dashboard_data["top_threats"] = sorted(
            dashboard_data["top_threats"], 
            key=lambda x: x["cvss_score"], 
            reverse=True
        )[:10]
        
        return {
            "dashboard_data": dashboard_data,
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "data_freshness": "Real-time simulation data for Phase 1"
        }
        
    except Exception as e:
        logger.error(f"Dashboard generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Dashboard generation failed: {str(e)}")

# DSL Rule Engine APIs - Phase 2
@api_router.post("/diagrams/{diagram_id}/evaluate-rules")
async def evaluate_security_rules(diagram_id: str):
    """Evaluate DSL security rules against a diagram"""
    diagram = await db.diagrams.find_one({"id": diagram_id})
    if not diagram:
        raise HTTPException(status_code=404, detail="Diagram not found")
    
    nodes = diagram.get("nodes", [])
    edges = diagram.get("edges", [])
    
    if not nodes:
        return {
            "diagram_id": diagram_id,
            "rule_results": [],
            "total_rules_triggered": 0,
            "overall_risk_score": 0.0,
            "highest_impact": "Low"
        }
    
    # Evaluate rules using DSL engine
    rule_results = dsl_rule_engine.evaluate_rules(nodes, edges)
    
    # Calculate overall metrics
    total_triggered = len(rule_results)
    overall_risk = sum(result.risk_score for result in rule_results) / max(total_triggered, 1)
    
    # Determine highest impact
    impact_levels = [result.impact_level.value for result in rule_results]
    if "Critical" in impact_levels:
        highest_impact = "Critical"
    elif "High" in impact_levels:
        highest_impact = "High"
    elif "Medium" in impact_levels:
        highest_impact = "Medium"
    else:
        highest_impact = "Low"
    
    # Format results for frontend
    formatted_results = []
    for result in rule_results:
        formatted_results.append({
            "rule_id": result.rule_id,
            "rule_name": result.rule_name,
            "triggered": result.triggered,
            "matching_nodes": result.matching_nodes,
            "attack_path": result.attack_path,
            "impact_level": result.impact_level.value,
            "risk_score": result.risk_score,
            "recommendations": result.recommendations,
            "mitre_techniques": result.mitre_techniques
        })
    
    return {
        "diagram_id": diagram_id,
        "rule_results": formatted_results,
        "total_rules_triggered": total_triggered,
        "overall_risk_score": round(overall_risk, 2),
        "highest_impact": highest_impact,
        "evaluation_timestamp": datetime.now(timezone.utc).isoformat()
    }

@api_router.post("/diagrams/{diagram_id}/detect-gaps")
async def detect_security_gaps(diagram_id: str):
    """Detect security control gaps in a diagram"""
    diagram = await db.diagrams.find_one({"id": diagram_id})
    if not diagram:
        raise HTTPException(status_code=404, detail="Diagram not found")
    
    nodes = diagram.get("nodes", [])
    edges = diagram.get("edges", [])
    
    # Detect gaps using DSL engine
    gaps = dsl_rule_engine.detect_security_gaps(nodes, edges)
    
    # Format gaps for frontend
    formatted_gaps = []
    for gap in gaps:
        formatted_gaps.append({
            "gap_id": gap.gap_id,
            "node_id": gap.node_id,
            "node_type": gap.node_type,
            "missing_control": gap.missing_control,
            "severity": gap.severity.value,
            "description": gap.description,
            "recommendations": gap.recommendations,
            "affected_attack_paths": gap.affected_attack_paths
        })
    
    # Group gaps by severity
    gaps_by_severity = {
        "Critical": len([g for g in gaps if g.severity.value == "Critical"]),
        "High": len([g for g in gaps if g.severity.value == "High"]),
        "Medium": len([g for g in gaps if g.severity.value == "Medium"]),
        "Low": len([g for g in gaps if g.severity.value == "Low"])
    }
    
    return {
        "diagram_id": diagram_id,
        "security_gaps": formatted_gaps,
        "total_gaps": len(gaps),
        "gaps_by_severity": gaps_by_severity,
        "analysis_timestamp": datetime.now(timezone.utc).isoformat()
    }

@api_router.post("/diagrams/{diagram_id}/completeness-analysis")
async def analyze_security_completeness(diagram_id: str):
    """Analyze security completeness of a diagram"""
    diagram = await db.diagrams.find_one({"id": diagram_id})
    if not diagram:
        raise HTTPException(status_code=404, detail="Diagram not found")
    
    nodes = diagram.get("nodes", [])
    edges = diagram.get("edges", [])
    
    # Calculate completeness using DSL engine
    analysis = dsl_rule_engine.calculate_completeness_score(nodes, edges)
    
    return {
        "diagram_id": diagram_id,
        "overall_score": analysis.overall_score,
        "completeness_percentage": analysis.completeness_percentage,
        "total_gaps": analysis.total_gaps,
        "gaps_by_severity": {
            "critical_gaps": analysis.critical_gaps,
            "high_gaps": analysis.high_gaps,
            "medium_gaps": analysis.medium_gaps,
            "low_gaps": analysis.low_gaps
        },
        "gaps_by_category": analysis.gaps_by_category,
        "improvement_recommendations": analysis.improvement_recommendations,
        "analysis_timestamp": datetime.now(timezone.utc).isoformat()
    }

@api_router.get("/security-rules")
async def get_security_rules(category: Optional[str] = None, enabled_only: bool = True):
    """Get available security rules"""
    if category:
        try:
            from dsl_rule_engine import RuleCategory
            cat_enum = RuleCategory(category)
            rules = dsl_rule_engine.get_rules_by_category(cat_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid category: {category}")
    else:
        rules = dsl_rule_engine.rules
    
    if enabled_only:
        rules = [rule for rule in rules if rule.enabled]
    
    # Format rules for frontend
    formatted_rules = []
    for rule in rules:
        formatted_rules.append({
            "id": rule.id,
            "name": rule.name,
            "description": rule.description,
            "category": rule.category.value,
            "enabled": rule.enabled,
            "priority": rule.priority,
            "mitre_techniques": rule.mitre_techniques,
            "references": rule.references,
            "conditions_count": len(rule.conditions),
            "impact": rule.outcome.get("impact", "Unknown"),
            "risk_score": rule.outcome.get("risk_score", 0.0)
        })
    
    return {
        "rules": formatted_rules,
        "total_count": len(formatted_rules),
        "filter_applied": {"category": category, "enabled_only": enabled_only}
    }

@api_router.get("/security-rules/categories")
async def get_security_rule_categories():
    """Get available security rule categories"""
    from dsl_rule_engine import RuleCategory
    
    categories = []
    for category in RuleCategory:
        rule_count = len(dsl_rule_engine.get_rules_by_category(category))
        categories.append({
            "id": category.value,
            "name": category.value.replace("_", " ").title(),
            "rule_count": rule_count
        })
    
    return {
        "categories": categories,
        "total_categories": len(categories)
    }

@api_router.get("/security-rules/statistics")
async def get_rule_engine_statistics():
    """Get statistics about the rule engine"""
    return dsl_rule_engine.get_rule_statistics()

@api_router.get("/security-rules/{rule_id}")
async def get_security_rule(rule_id: str):
    """Get detailed information about a specific security rule"""
    rule = dsl_rule_engine.get_rule_by_id(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Security rule not found")
    
    # Format conditions for frontend
    formatted_conditions = []
    for condition in rule.conditions:
        formatted_conditions.append({
            "field": condition.field,
            "operator": condition.operator,
            "value": condition.value,
            "negated": condition.negated
        })
    
    return {
        "id": rule.id,
        "name": rule.name,
        "description": rule.description,
        "category": rule.category.value,
        "conditions": formatted_conditions,
        "outcome": rule.outcome,
        "enabled": rule.enabled,
        "priority": rule.priority,
        "mitre_techniques": rule.mitre_techniques,
        "references": rule.references
    }

@api_router.post("/diagrams/{diagram_id}/comprehensive-analysis")
async def run_comprehensive_security_analysis(diagram_id: str):
    """Run comprehensive security analysis combining rules, gaps, and completeness"""
    diagram = await db.diagrams.find_one({"id": diagram_id})
    if not diagram:
        raise HTTPException(status_code=404, detail="Diagram not found")
    
    nodes = diagram.get("nodes", [])
    edges = diagram.get("edges", [])
    
    if not nodes:
        return {
            "diagram_id": diagram_id,
            "analysis_summary": {
                "overall_risk_score": 0.0,
                "completeness_percentage": 0.0,
                "total_rules_triggered": 0,
                "total_gaps": 0,
                "recommendations": ["Add security nodes to begin analysis"]
            },
            "rule_evaluation": {"rule_results": []},
            "gap_analysis": {"security_gaps": []},
            "completeness_analysis": {"improvement_recommendations": []}
        }
    
    # Run all analyses
    rule_results = dsl_rule_engine.evaluate_rules(nodes, edges)
    gaps = dsl_rule_engine.detect_security_gaps(nodes, edges)
    completeness = dsl_rule_engine.calculate_completeness_score(nodes, edges)
    
    # Calculate overall metrics
    overall_risk = sum(result.risk_score for result in rule_results) / max(len(rule_results), 1)
    
    # Combine recommendations
    all_recommendations = []
    all_recommendations.extend(completeness.improvement_recommendations)
    
    # Add top rule recommendations
    for result in rule_results[:3]:  # Top 3 triggered rules
        all_recommendations.extend(result.recommendations[:2])  # Top 2 recommendations each
    
    # Remove duplicates and limit
    unique_recommendations = list(dict.fromkeys(all_recommendations))[:10]
    
    # Format comprehensive results
    formatted_rule_results = []
    for result in rule_results:
        formatted_rule_results.append({
            "rule_id": result.rule_id,
            "rule_name": result.rule_name,
            "impact_level": result.impact_level.value,
            "risk_score": result.risk_score,
            "matching_nodes": result.matching_nodes,
            "attack_path": result.attack_path,
            "recommendations": result.recommendations
        })
    
    formatted_gaps = []
    for gap in gaps:
        formatted_gaps.append({
            "gap_id": gap.gap_id,
            "node_id": gap.node_id,
            "missing_control": gap.missing_control,
            "severity": gap.severity.value,
            "description": gap.description,
            "recommendations": gap.recommendations
        })
    
    return {
        "diagram_id": diagram_id,
        "analysis_summary": {
            "overall_risk_score": round(overall_risk, 2),
            "completeness_percentage": completeness.completeness_percentage,
            "total_rules_triggered": len(rule_results),
            "total_gaps": len(gaps),
            "critical_issues": completeness.critical_gaps + len([r for r in rule_results if r.impact_level.value == "Critical"]),
            "recommendations": unique_recommendations
        },
        "rule_evaluation": {
            "rule_results": formatted_rule_results,
            "total_triggered": len(rule_results)
        },
        "gap_analysis": {
            "security_gaps": formatted_gaps,
            "gaps_by_severity": {
                "Critical": completeness.critical_gaps,
                "High": completeness.high_gaps,
                "Medium": completeness.medium_gaps,
                "Low": completeness.low_gaps
            }
        },
        "completeness_analysis": {
            "overall_score": completeness.overall_score,
            "completeness_percentage": completeness.completeness_percentage,
            "improvement_recommendations": completeness.improvement_recommendations
        },
        "analysis_timestamp": datetime.now(timezone.utc).isoformat()
    }

# ============================================================================
# PHASE 3: PROBABILISTIC SIMULATION ENGINE API ENDPOINTS
# ============================================================================

@api_router.post("/diagrams/{diagram_id}/probabilistic-simulation")
async def run_probabilistic_simulation(diagram_id: str):
    """Run probabilistic attack path simulation with weighted graph analysis"""
    diagram = await db.diagrams.find_one({"id": diagram_id})
    if not diagram:
        raise HTTPException(status_code=404, detail="Diagram not found")
    
    nodes = diagram.get("nodes", [])
    edges = diagram.get("edges", [])
    
    if not nodes or not edges:
        return {
            "diagram_id": diagram_id,
            "probabilistic_paths": [],
            "simulation_summary": {
                "total_paths": 0,
                "average_success_probability": 0.0,
                "highest_risk_path": None,
                "kill_chain_coverage": []
            },
            "error": "Insufficient nodes or edges for probabilistic analysis"
        }
    
    # Run probabilistic simulation in thread pool
    loop = asyncio.get_event_loop()
    
    def run_prob_simulation():
        try:
            # Build probabilistic graph
            probabilistic_engine.build_probabilistic_graph(nodes, edges)
            
            # Find probabilistic attack paths
            prob_paths = probabilistic_engine.find_probabilistic_attack_paths(max_paths=15, max_length=8)
            
            # Format results for frontend
            formatted_paths = []
            for path in prob_paths:
                formatted_path = {
                    "path_id": path.path_id,
                    "steps": [{"node_id": node_id, "node_label": _get_node_label(node_id, nodes)} 
                             for node_id in path.steps],
                    "overall_probability": round(path.overall_probability, 4),
                    "risk_score": round(path.risk_score, 2),
                    "impact_score": round(path.impact_score, 2),
                    "detection_score": round(path.detection_score, 4),
                    "kill_chain_stages": path.kill_chain_stages,
                    "mitre_techniques": path.mitre_techniques,
                    "time_to_compromise": path.time_to_compromise,
                    "uncertainty_band": {
                        "min_probability": round(path.uncertainty_band[0], 4),
                        "max_probability": round(path.uncertainty_band[1], 4)
                    }
                }
                formatted_paths.append(formatted_path)
            
            # Calculate simulation summary
            if prob_paths:
                avg_probability = sum(p.overall_probability for p in prob_paths) / len(prob_paths)
                highest_risk_path = max(prob_paths, key=lambda p: p.risk_score)
                all_kill_chain_stages = set()
                for path in prob_paths:
                    all_kill_chain_stages.update(path.kill_chain_stages)
            else:
                avg_probability = 0.0
                highest_risk_path = None
                all_kill_chain_stages = set()
            
            summary = {
                "total_paths": len(prob_paths),
                "average_success_probability": round(avg_probability, 4),
                "highest_risk_path": {
                    "path_id": highest_risk_path.path_id,
                    "risk_score": round(highest_risk_path.risk_score, 2),
                    "probability": round(highest_risk_path.overall_probability, 4)
                } if highest_risk_path else None,
                "kill_chain_coverage": sorted(list(all_kill_chain_stages)),
                "risk_distribution": {
                    "critical": len([p for p in prob_paths if p.risk_score >= 8]),
                    "high": len([p for p in prob_paths if 6 <= p.risk_score < 8]),
                    "medium": len([p for p in prob_paths if 4 <= p.risk_score < 6]),
                    "low": len([p for p in prob_paths if p.risk_score < 4])
                }
            }
            
            return {
                "probabilistic_paths": formatted_paths,
                "simulation_summary": summary
            }
            
        except Exception as e:
            logger.error(f"Probabilistic simulation error: {str(e)}")
            return {
                "probabilistic_paths": [],
                "simulation_summary": {
                    "total_paths": 0,
                    "average_success_probability": 0.0,
                    "highest_risk_path": None,
                    "kill_chain_coverage": []
                },
                "error": f"Simulation failed: {str(e)}"
            }
    
    simulation_result = await loop.run_in_executor(executor, run_prob_simulation)
    
    # Add diagram ID and timestamp
    result = {
        "diagram_id": diagram_id,
        **simulation_result,
        "simulation_timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    # Save simulation result to database (in background to avoid serialization issues)
    try:
        result_dict = prepare_for_mongo(result.copy())
        await db.probabilistic_simulations.insert_one(result_dict)
    except Exception as e:
        logger.error(f"Failed to save probabilistic simulation to database: {e}")
    
    return result

def _get_node_label(node_id: str, nodes: List[Dict]) -> str:
    """Get node label by ID"""
    for node in nodes:
        if node.get("id") == node_id:
            return node.get("label", node_id)
    return node_id

@api_router.post("/diagrams/{diagram_id}/what-if-scenario")
async def run_what_if_scenario(diagram_id: str, scenario_config: Dict[str, Any]):
    """Run what-if scenario analysis by toggling security controls"""
    diagram = await db.diagrams.find_one({"id": diagram_id})
    if not diagram:
        raise HTTPException(status_code=404, detail="Diagram not found")
    
    nodes = diagram.get("nodes", [])
    edges = diagram.get("edges", [])
    
    # Extract control changes from scenario config
    control_changes = scenario_config.get("control_changes", {})
    scenario_name = scenario_config.get("scenario_name", "Unnamed Scenario")
    
    if not control_changes:
        raise HTTPException(status_code=400, detail="No control changes specified in scenario")
    
    # Run scenario analysis in thread pool
    loop = asyncio.get_event_loop()
    
    def run_scenario():
        try:
            # Build probabilistic graph
            probabilistic_engine.build_probabilistic_graph(nodes, edges)
            
            # Get original attack paths
            original_paths = probabilistic_engine.find_probabilistic_attack_paths(max_paths=10)
            
            # Run what-if scenario
            scenario_result = probabilistic_engine.run_what_if_scenario(control_changes, original_paths)
            scenario_result.scenario_name = scenario_name
            
            # Format result for frontend
            return {
                "scenario_id": scenario_result.scenario_id,
                "scenario_name": scenario_result.scenario_name,
                "control_changes": scenario_result.modified_controls,
                "risk_analysis": {
                    "original_risk_score": round(scenario_result.original_risk_score, 2),
                    "modified_risk_score": round(scenario_result.modified_risk_score, 2),
                    "risk_change": round(scenario_result.risk_change, 2),
                    "risk_change_percentage": round((scenario_result.risk_change / max(scenario_result.original_risk_score, 0.1)) * 100, 1)
                },
                "affected_paths": scenario_result.affected_paths,
                "recommendations": scenario_result.recommendations,
                "roi_analysis": scenario_result.roi_analysis
            }
            
        except Exception as e:
            logger.error(f"What-if scenario error: {str(e)}")
            return {
                "scenario_id": f"failed-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                "error": f"Scenario analysis failed: {str(e)}"
            }
    
    scenario_result = await loop.run_in_executor(executor, run_scenario)
    
    # Add metadata
    result = {
        "diagram_id": diagram_id,
        **scenario_result,
        "analysis_timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    # Save scenario result (in background to avoid serialization issues)
    try:
        result_dict = prepare_for_mongo(result.copy())
        await db.scenario_analyses.insert_one(result_dict)
    except Exception as e:
        logger.error(f"Failed to save scenario analysis to database: {e}")
    
    return result

@api_router.post("/diagrams/{diagram_id}/defense-effectiveness")
async def analyze_defense_effectiveness(diagram_id: str):
    """Analyze effectiveness of defense controls with interaction modeling"""
    diagram = await db.diagrams.find_one({"id": diagram_id})
    if not diagram:
        raise HTTPException(status_code=404, detail="Diagram not found")
    
    nodes = diagram.get("nodes", [])
    
    # Filter control nodes
    control_nodes = [n for n in nodes if n.get("type") == "Control"]
    
    if not control_nodes:
        return {
            "diagram_id": diagram_id,
            "defense_models": [],
            "analysis_summary": {
                "total_controls": 0,
                "average_effectiveness": 0.0,
                "strongest_control": None,
                "weakest_control": None,
                "synergy_opportunities": []
            },
            "message": "No security controls found in diagram"
        }
    
    # Run defense analysis in thread pool
    loop = asyncio.get_event_loop()
    
    def analyze_defenses():
        try:
            # Analyze defense effectiveness
            defense_models = probabilistic_engine.analyze_defense_effectiveness(nodes)
            
            # Format for frontend
            formatted_models = []
            for model in defense_models:
                formatted_model = {
                    "control_id": model.control_id,
                    "control_type": model.control_type,
                    "effectiveness_rating": round(model.effectiveness_rating, 3),
                    "coverage_areas": model.coverage_areas,
                    "interaction_effects": {k: round(v, 3) for k, v in model.interaction_effects.items()},
                    "degradation_over_time": round(model.degradation_over_time, 3),
                    "false_positive_rate": round(model.false_positive_rate, 3),
                    "false_negative_rate": round(model.false_negative_rate, 3)
                }
                formatted_models.append(formatted_model)
            
            # Calculate summary statistics
            if defense_models:
                effectiveness_scores = [m.effectiveness_rating for m in defense_models]
                avg_effectiveness = sum(effectiveness_scores) / len(effectiveness_scores)
                strongest = max(defense_models, key=lambda m: m.effectiveness_rating)
                weakest = min(defense_models, key=lambda m: m.effectiveness_rating)
                
                # Find synergy opportunities
                synergies = []
                for model in defense_models:
                    for other_control, effect in model.interaction_effects.items():
                        if effect > 0.1:  # Significant synergy
                            synergies.append({
                                "control_1": model.control_id,
                                "control_2": other_control,
                                "synergy_effect": round(effect, 3)
                            })
            else:
                avg_effectiveness = 0.0
                strongest = weakest = None
                synergies = []
            
            summary = {
                "total_controls": len(defense_models),
                "average_effectiveness": round(avg_effectiveness, 3),
                "strongest_control": {
                    "control_id": strongest.control_id,
                    "control_type": strongest.control_type,
                    "effectiveness": round(strongest.effectiveness_rating, 3)
                } if strongest else None,
                "weakest_control": {
                    "control_id": weakest.control_id,
                    "control_type": weakest.control_type,
                    "effectiveness": round(weakest.effectiveness_rating, 3)
                } if weakest else None,
                "synergy_opportunities": synergies[:5]  # Top 5 synergies
            }
            
            return {
                "defense_models": formatted_models,
                "analysis_summary": summary
            }
            
        except Exception as e:
            logger.error(f"Defense effectiveness analysis error: {str(e)}")
            return {
                "defense_models": [],
                "analysis_summary": {
                    "total_controls": 0,
                    "average_effectiveness": 0.0,
                    "strongest_control": None,
                    "weakest_control": None,
                    "synergy_opportunities": []
                },
                "error": f"Analysis failed: {str(e)}"
            }
    
    analysis_result = await loop.run_in_executor(executor, analyze_defenses)
    
    # Add metadata
    result = {
        "diagram_id": diagram_id,
        **analysis_result,
        "analysis_timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    return result

@api_router.get("/diagrams/{diagram_id}/probabilistic-simulations")
async def get_probabilistic_simulations(diagram_id: str):
    """Get historical probabilistic simulation results"""
    simulations = await db.probabilistic_simulations.find({"diagram_id": diagram_id}).sort("simulation_timestamp", -1).to_list(20)
    
    formatted_simulations = []
    for sim in simulations:
        formatted_sim = parse_from_mongo(sim)
        # Remove large arrays for summary view
        if "probabilistic_paths" in formatted_sim:
            formatted_sim["path_count"] = len(formatted_sim["probabilistic_paths"])
            del formatted_sim["probabilistic_paths"]  # Remove detailed paths for summary
        formatted_simulations.append(formatted_sim)
    
    return {
        "diagram_id": diagram_id,
        "simulations": formatted_simulations,
        "total_count": len(formatted_simulations)
    }

@api_router.get("/diagrams/{diagram_id}/scenario-analyses")
async def get_scenario_analyses(diagram_id: str):
    """Get historical what-if scenario analyses"""
    scenarios = await db.scenario_analyses.find({"diagram_id": diagram_id}).sort("analysis_timestamp", -1).to_list(20)
    
    formatted_scenarios = []
    for scenario in scenarios:
        formatted_scenario = parse_from_mongo(scenario)
        formatted_scenarios.append(formatted_scenario)
    
    return {
        "diagram_id": diagram_id,
        "scenarios": formatted_scenarios,
        "total_count": len(formatted_scenarios)
    }

# ============================================================================
# THREAT MODELING WIZARD ENDPOINTS
# ============================================================================

class WizardRecommendationRequest(BaseModel):
    step: str = Field(..., description="Current wizard step ID")
    wizardData: Dict[str, Any] = Field(default_factory=dict, description="Current wizard data")
    existingNodes: List[Dict[str, Any]] = Field(default_factory=list, description="Existing diagram nodes")
    existingEdges: List[Dict[str, Any]] = Field(default_factory=list, description="Existing diagram edges")

class WizardGenerationRequest(BaseModel):
    wizardData: Dict[str, Any] = Field(..., description="Complete wizard data")
    diagramId: Optional[str] = Field(None, description="Existing diagram ID to update")

@api_router.post("/wizard/recommendations")
async def get_wizard_recommendations(request: WizardRecommendationRequest):
    """Get contextual recommendations for current wizard step"""
    try:
        step = request.step
        wizard_data = request.wizardData
        existing_nodes = request.existingNodes
        existing_edges = request.existingEdges
        
        # Generate contextual recommendations based on step and current data
        recommendations = []
        
        if step == "systemOverview":
            recommendations = generate_system_overview_recommendations(wizard_data)
        elif step == "assetInventory":
            recommendations = generate_asset_recommendations(wizard_data, existing_nodes)
        elif step == "boundaries":
            recommendations = generate_boundary_recommendations(wizard_data)
        elif step == "dataflows":
            recommendations = generate_dataflow_recommendations(wizard_data)
        elif step == "threats":
            recommendations = generate_threat_recommendations(wizard_data)
        elif step == "surfaces":
            recommendations = generate_attack_surface_recommendations(wizard_data)
        elif step == "controls":
            recommendations = generate_control_recommendations(wizard_data)
        elif step == "risk":
            recommendations = generate_risk_recommendations(wizard_data)
        elif step == "compliance":
            recommendations = generate_compliance_recommendations(wizard_data)
        elif step == "implementation":
            recommendations = generate_implementation_recommendations(wizard_data)
        else:
            recommendations = ["Continue with the current step to receive specific recommendations."]
        
        return {
            "step": step,
            "recommendations": recommendations,
            "recommendation_count": len(recommendations)
        }
        
    except Exception as e:
        logger.error(f"Wizard recommendations error: {str(e)}")
        # Fallback recommendations
        fallback_recommendations = {
            "systemOverview": [
                "Define clear system boundaries and scope",
                "Identify primary business objectives and stakeholders",
                "Document key technical components and architecture"
            ],
            "assetInventory": [
                "Classify assets by business criticality",
                "Include both technical and business assets",
                "Consider data assets, systems, and processes"
            ],
            "boundaries": [
                "Define trust zones based on security requirements",
                "Identify boundaries between internal and external systems",
                "Consider network segmentation and access controls"
            ]
        }
        
        return {
            "step": request.step,
            "recommendations": fallback_recommendations.get(request.step, ["Continue with the current step."]),
            "recommendation_count": len(fallback_recommendations.get(request.step, []))
        }

@api_router.post("/wizard/generate-model")
async def generate_threat_model_from_wizard(request: WizardGenerationRequest):
    """Generate a complete threat model based on wizard data"""
    try:
        wizard_data = request.wizardData
        diagram_id = request.diagramId
        
        # Generate nodes and edges based on wizard data
        generated_nodes = []
        generated_edges = []
        recommendations = []
        
        # Process system overview
        if "systemOverview" in wizard_data:
            system_overview = wizard_data["systemOverview"]
            
            # Create system node if it doesn't exist
            system_node = {
                "id": f"system-{uuid.uuid4()}",
                "type": "custom",
                "position": {"x": 400, "y": 200},
                "data": {
                    "type": "Asset",
                    "subtype": "System",
                    "label": system_overview.get("systemName", "System"),
                    "description": system_overview.get("systemDescription", ""),
                    "criticality": system_overview.get("businessCriticality", "medium"),
                    "securityObjectives": system_overview.get("securityObjectives", {})
                }
            }
            generated_nodes.append(system_node)
        
        # Process assets
        if "assetInventory" in wizard_data and "assets" in wizard_data["assetInventory"]:
            assets = wizard_data["assetInventory"]["assets"]
            
            for i, asset in enumerate(assets):
                asset_node = {
                    "id": f"asset-{uuid.uuid4()}",
                    "type": "custom", 
                    "position": {"x": 200 + (i * 150), "y": 400},
                    "data": {
                        "type": "Asset",
                        "subtype": asset.get("category", asset.get("type", "Asset")),
                        "label": asset.get("name", f"Asset {i+1}"),
                        "description": asset.get("description", ""),
                        "criticality": asset.get("criticality", "medium"),
                        "dataClassification": asset.get("dataClassification", ""),
                        "owner": asset.get("owner", "")
                    }
                }
                generated_nodes.append(asset_node)
        
        # Generate basic threat actors
        external_attacker = {
            "id": f"attacker-{uuid.uuid4()}",
            "type": "custom",
            "position": {"x": 100, "y": 100},
            "data": {
                "type": "Actor",
                "subtype": "ExternalAttacker",
                "label": "External Attacker",
                "description": "External threat actor attempting to compromise the system"
            }
        }
        generated_nodes.append(external_attacker)
        
        # Generate recommendations based on wizard data
        recommendations = generate_comprehensive_recommendations(wizard_data)
        
        # Create implementation plan
        implementation_plan = {
            "priority_actions": recommendations[:5] if recommendations else [],
            "timeline": "2-4 weeks for initial implementation",
            "success_metrics": [
                "Reduced attack surface area",
                "Improved security control coverage",
                "Enhanced threat detection capabilities"
            ]
        }
        
        return {
            "success": True,
            "generatedNodes": generated_nodes,
            "generatedEdges": generated_edges,
            "recommendations": recommendations,
            "implementationPlan": implementation_plan,
            "summary": {
                "total_nodes": len(generated_nodes),
                "total_edges": len(generated_edges),
                "recommendations_count": len(recommendations)
            }
        }
        
    except Exception as e:
        logger.error(f"Model generation error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "generatedNodes": [],
            "generatedEdges": [],
            "recommendations": ["Error generating model. Please try again."],
            "implementationPlan": {}
        }

# Helper functions for recommendations
def generate_system_overview_recommendations(wizard_data):
    recommendations = []
    system_data = wizard_data.get("systemOverview", {})
    
    if not system_data.get("systemName"):
        recommendations.append("Provide a clear, descriptive system name")
    
    if not system_data.get("businessContext"):
        recommendations.append("Document the business context and value proposition")
    
    if system_data.get("businessCriticality") == "critical":
        recommendations.append("Consider implementing additional security controls for critical systems")
        recommendations.append("Ensure comprehensive monitoring and incident response procedures")
    
    security_objectives = system_data.get("securityObjectives", {})
    if security_objectives.get("confidentiality") == "high":
        recommendations.append("Implement strong encryption and access controls")
    
    if security_objectives.get("availability") == "high":
        recommendations.append("Design for high availability with redundancy and failover")
    
    return recommendations

def generate_asset_recommendations(wizard_data, existing_nodes):
    recommendations = []
    asset_data = wizard_data.get("assetInventory", {})
    assets = asset_data.get("assets", [])
    
    if len(assets) == 0:
        recommendations.append("Add at least 3-5 key assets to create a meaningful threat model")
        return recommendations
    
    critical_assets = [a for a in assets if a.get("criticality") == "critical"]
    if critical_assets:
        recommendations.append(f"Focus additional security controls on {len(critical_assets)} critical assets")
    
    # Check for common asset types
    data_assets = [a for a in assets if a.get("type") == "data"]
    if data_assets:
        recommendations.append("Ensure data assets have appropriate encryption and access controls")
    
    applications = [a for a in assets if a.get("type") == "application"]
    if applications:
        recommendations.append("Implement secure coding practices and regular security testing for applications")
    
    return recommendations

def generate_boundary_recommendations(wizard_data):
    recommendations = []
    boundary_data = wizard_data.get("boundaries", {})
    
    recommendations.extend([
        "Define clear trust boundaries between different security zones",
        "Implement network segmentation to isolate critical assets",
        "Consider zero-trust principles for boundary controls"
    ])
    
    return recommendations

def generate_dataflow_recommendations(wizard_data):
    recommendations = []
    
    recommendations.extend([
        "Encrypt data in transit between all components",
        "Implement data loss prevention (DLP) controls",
        "Monitor and log all data flows for security analysis"
    ])
    
    return recommendations

def generate_threat_recommendations(wizard_data):
    recommendations = []
    
    recommendations.extend([
        "Consider both internal and external threat actors",
        "Assess threat actor capabilities and motivations",
        "Map threats to specific attack techniques (MITRE ATT&CK)"
    ])
    
    return recommendations

def generate_attack_surface_recommendations(wizard_data):
    recommendations = []
    
    recommendations.extend([
        "Minimize exposed services and interfaces",
        "Implement input validation and sanitization",
        "Regular vulnerability scanning and penetration testing"
    ])
    
    return recommendations

def generate_control_recommendations(wizard_data):
    recommendations = []
    
    recommendations.extend([
        "Implement defense-in-depth security controls",
        "Ensure controls cover prevention, detection, and response",
        "Regular testing and validation of security controls"
    ])
    
    return recommendations

def generate_risk_recommendations(wizard_data):
    recommendations = []
    
    recommendations.extend([
        "Conduct quantitative risk assessments where possible",
        "Prioritize risks based on business impact",
        "Develop risk treatment plans for high-priority risks"
    ])
    
    return recommendations

def generate_compliance_recommendations(wizard_data):
    recommendations = []
    
    recommendations.extend([
        "Map security controls to relevant compliance frameworks",
        "Implement continuous compliance monitoring",
        "Document compliance evidence and audit trails"
    ])
    
    return recommendations

def generate_implementation_recommendations(wizard_data):
    recommendations = []
    
    recommendations.extend([
        "Develop phased implementation roadmap",
        "Assign clear ownership and accountability",
        "Establish metrics and KPIs for success measurement"
    ])
    
    return recommendations

def generate_comprehensive_recommendations(wizard_data):
    """Generate comprehensive recommendations based on all wizard data"""
    recommendations = []
    
    # System-level recommendations
    system_data = wizard_data.get("systemOverview", {})
    if system_data.get("deploymentModel") == "cloud_public":
        recommendations.append("Implement cloud security best practices and shared responsibility model")
    
    # Asset-based recommendations
    asset_data = wizard_data.get("assetInventory", {})
    assets = asset_data.get("assets", [])
    
    if any(a.get("dataClassification") == "Confidential" for a in assets):
        recommendations.append("Implement data loss prevention (DLP) controls")
    
    if any(a.get("type") == "application" for a in assets):
        recommendations.append("Conduct regular application security assessments")
    
    # General security recommendations
    recommendations.extend([
        "Implement multi-factor authentication for all user accounts",
        "Deploy network segmentation and micro-segmentation",
        "Establish comprehensive logging and monitoring",
        "Create incident response and disaster recovery plans",
        "Conduct regular security awareness training"
    ])
    
    return recommendations[:10]  # Limit to top 10 recommendations

# Additional helper functions for other wizard steps
def generate_boundary_recommendations(wizard_data):
    return [
        "Define trust zones based on security requirements",
        "Identify boundaries between internal and external systems",
        "Consider network segmentation and access controls"
    ]

def generate_dataflow_recommendations(wizard_data):
    return [
        "Map all data inputs and outputs",
        "Identify sensitive data paths",
        "Document authentication and authorization flows"
    ]

def generate_threat_recommendations(wizard_data):
    return [
        "Consider internal and external threat actors",
        "Analyze threat motivations and capabilities", 
        "Reference MITRE ATT&CK framework for threat intelligence"
    ]

def generate_attack_surface_recommendations(wizard_data):
    return [
        "Identify all system entry points",
        "Analyze network-accessible services",
        "Consider physical and social attack vectors"
    ]

def generate_control_recommendations(wizard_data):
    return [
        "Map existing security controls to assets",
        "Identify control gaps and redundancies",
        "Consider preventive, detective, and corrective controls"
    ]

def generate_risk_recommendations(wizard_data):
    return [
        "Calculate risk using impact and likelihood",
        "Prioritize risks by business impact",
        "Consider risk appetite and tolerance"
    ]

def generate_compliance_recommendations(wizard_data):
    return [
        "Map to relevant frameworks (SOC2, ISO 27001, NIST)",
        "Identify compliance requirements",
        "Document control mappings"
    ]

def generate_implementation_recommendations(wizard_data):
    return [
        "Prioritize recommendations by risk reduction",
        "Consider implementation complexity and cost",
        "Create actionable timeline and ownership"
    ]

# Questionnaire Management Routes
@api_router.get("/diagrams/{diagram_id}/nodes/{node_id}/questionnaire")
async def get_node_questionnaire_responses(diagram_id: str, node_id: str):
    """Get questionnaire responses for a specific node"""
    try:
        diagram = await db.diagrams.find_one({"id": diagram_id})
        if not diagram:
            raise HTTPException(status_code=404, detail="Diagram not found")
        
        # Find the node in the diagram
        node = None
        for n in diagram.get("nodes", []):
            if n.get("id") == node_id:
                node = n
                break
        
        if not node:
            raise HTTPException(status_code=404, detail="Node not found")
        
        # Get questionnaire responses from node data
        questionnaire_data = node.get("data", {}).get("questionnaireResponses", {})
        node_subtype = node.get("subtype", "")
        
        # Get the original prompts for this node type
        prompts = intelligent_node_engine.get_security_prompts(node_subtype)
        
        return {
            "success": True,
            "node_id": node_id,
            "node_subtype": node_subtype,
            "questionnaire_responses": questionnaire_data,
            "prompts": [prompt.dict() for prompt in prompts],
            "completed_questions": len([q for q in questionnaire_data.values() if q is not None]),
            "total_questions": len(prompts)
        }
        
    except Exception as e:
        logger.error(f"Error getting questionnaire responses: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/diagrams/{diagram_id}/nodes/{node_id}/questionnaire")
async def update_node_questionnaire_responses(diagram_id: str, node_id: str, request: dict):
    """Update questionnaire responses for a specific node"""
    try:
        responses = request.get("responses", {})
        
        # Update the node's questionnaire data
        result = await db.diagrams.update_one(
            {"id": diagram_id, "nodes.id": node_id},
            {
                "$set": {
                    "nodes.$.data.questionnaireResponses": responses,
                    "nodes.$.data.lastQuestionnaireUpdate": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Diagram or node not found")
        
        return {
            "success": True,
            "node_id": node_id,
            "updated_responses": len(responses)
        }
        
    except Exception as e:
        logger.error(f"Error updating questionnaire responses: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/intelligent-nodes/{node_subtype}/check-dependencies")
async def check_node_dependencies(node_subtype: str, request: dict):
    """Check which dependent nodes should be created based on questionnaire answers"""
    try:
        answers = request.get("answers", {})
        
        # Get dependent nodes that should be created
        dependent_nodes = intelligent_node_engine.check_conditional_dependencies(node_subtype, answers)
        
        return {
            "success": True,
            "node_subtype": node_subtype,
            "dependent_nodes": dependent_nodes,
            "dependencies_found": len(dependent_nodes)
        }
        
    except Exception as e:
        logger.error(f"Error checking dependencies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

#====================================================================================================
# PHASE 1: CORE LOOP COMPLETION - ENHANCED API ROUTES
#====================================================================================================

@api_router.post("/questionnaires/{node_subtype}/complete")
async def complete_questionnaire(
    node_subtype: str, 
    request: dict
):
    """
    Complete questionnaire processing with end-to-end flow:
    1. Process questionnaire responses
    2. Run rule evaluation and simulation
    3. Generate and persist findings
    4. Return comprehensive results
    """
    try:
        # Support both formats: with diagram context and standalone completion
        diagram_id = request.get("diagram_id") or str(uuid.uuid4())
        node_id = request.get("node_id") or str(uuid.uuid4())
        
        # Validate required data - support both parameter formats
        questionnaire_responses = request.get("questionnaire_responses") or request.get("responses")
        if not questionnaire_responses:
            raise HTTPException(status_code=400, detail="questionnaire_responses or responses are required")
        
        user_id = request.get("user_id")
        business_context = request.get("business_context", {})
        
        # Process questionnaire completion with full end-to-end flow
        results = await questionnaire_processor.process_questionnaire_completion(
            diagram_id=diagram_id,
            node_id=node_id,
            node_subtype=node_subtype,
            questionnaire_responses=questionnaire_responses,
            user_id=user_id,
            business_context=business_context
        )
        
        return {
            "completion_id": str(uuid.uuid4()),
            "node_subtype": node_subtype,
            "findings": results.get("findings_generated", []),
            "risk_assessment": results.get("risk_assessment", {}),
            "recommendations": results.get("recommendations", []),
            "framework_mappings": results.get("framework_mappings", {}),
            "success": True,
            "message": f"Questionnaire completed successfully for {node_subtype} node",
            "processing_results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing questionnaire: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/simulate")
async def enhanced_simulate(request: dict):
    """
    Enhanced simulation endpoint with comprehensive flags and options
    """
    try:
        diagram_id = request.get("diagram_id")
        simulation_type = request.get("type", "advanced")  # advanced, probabilistic, comprehensive
        max_paths = request.get("max_paths", 10)
        max_length = request.get("max_length", 6)
        include_mitre = request.get("include_mitre", True)
        include_recommendations = request.get("include_recommendations", True)
        
        # Support standalone simulation without existing diagram
        if not diagram_id:
            diagram_id = str(uuid.uuid4())
            nodes = request.get("nodes", [])
            edges = request.get("edges", [])
        else:
            # Get diagram data
            diagram = await db.diagrams.find_one({"id": diagram_id})
            if not diagram:
                raise HTTPException(status_code=404, detail="Diagram not found")
            
            nodes = diagram.get("nodes", [])
            edges = diagram.get("edges", [])
        
        if simulation_type == "advanced":
            # Use advanced simulation engine
            simulation_engine = AdvancedSimulationEngine(nodes, edges)
            attack_paths = simulation_engine.find_attack_paths(max_paths=max_paths, max_length=max_length)
            
            results = {
                "simulation_type": "advanced",
                "attack_paths": [path.dict() if hasattr(path, 'dict') else str(path) for path in attack_paths],
                "total_paths": len(attack_paths),
                "diagram_id": diagram_id
            }
            
        elif simulation_type == "probabilistic":
            # Use probabilistic simulation
            prob_results = probabilistic_engine.run_scenario_analysis(nodes, edges)
            results = {
                "simulation_type": "probabilistic",
                "scenario_analysis": prob_results.dict() if hasattr(prob_results, 'dict') else str(prob_results),
                "diagram_id": diagram_id
            }
            
        else:  # comprehensive
            # Run both advanced and probabilistic
            simulation_engine = AdvancedSimulationEngine(nodes, edges)
            attack_paths = simulation_engine.find_attack_paths(max_paths=max_paths, max_length=max_length)
            prob_results = probabilistic_engine.run_scenario_analysis(nodes, edges)
            
            results = {
                "simulation_type": "comprehensive",
                "advanced_simulation": {
                    "attack_paths": [path.dict() if hasattr(path, 'dict') else str(path) for path in attack_paths],
                    "total_paths": len(attack_paths)
                },
                "probabilistic_simulation": prob_results.dict() if hasattr(prob_results, 'dict') else str(prob_results),
                "diagram_id": diagram_id
            }
        
        if include_mitre:
            # Add MITRE technique analysis
            mitre_analysis = await get_mitre_analysis_for_diagram(diagram_id)
            results["mitre_analysis"] = mitre_analysis
        
        if include_recommendations:
            # Generate security recommendations
            recommendations = await generate_security_recommendations(nodes, edges)
            results["recommendations"] = recommendations
        
        return {
            "success": True,
            "simulation_id": str(uuid.uuid4()),
            "attack_paths": results.get("attack_paths", results.get("advanced_simulation", {}).get("attack_paths", [])),
            "risk_analysis": {
                "total_paths": results.get("total_paths", results.get("advanced_simulation", {}).get("total_paths", 0)),
                "simulation_type": results.get("simulation_type", "advanced"),
                "diagram_id": diagram_id
            },
            "mitre_techniques": results.get("mitre_analysis", {}).get("techniques", []),
            "recommendations": results.get("recommendations", []),
            "detailed_results": results  # Keep original structure for advanced use
        }
        
    except Exception as e:
        logger.error(f"Error in enhanced simulation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/rules/evaluate")
async def enhanced_rule_evaluation(request: dict):
    """
    Enhanced rule evaluation endpoint with impact assessment
    """
    try:
        diagram_id = request.get("diagram_id")
        node_filter = request.get("node_filter", [])  # Specific nodes to evaluate
        rule_categories = request.get("rule_categories", [])  # Specific rule categories
        include_recommendations = request.get("include_recommendations", True)
        include_mitre = request.get("include_mitre", True)
        
        # Support standalone rule evaluation without existing diagram
        if not diagram_id:
            diagram_id = str(uuid.uuid4())
            nodes = request.get("nodes", [])
            edges = request.get("edges", [])
        else:
            # Get diagram data
            diagram = await db.diagrams.find_one({"id": diagram_id})
            if not diagram:
                raise HTTPException(status_code=404, detail="Diagram not found")
            
            nodes = diagram.get("nodes", [])
            edges = diagram.get("edges", [])
        
        # Filter nodes if specified
        if node_filter:
            nodes = [node for node in nodes if node.get("id") in node_filter]
        
        # Run rule evaluation
        rule_results = dsl_rule_engine.evaluate_rules(nodes, edges)
        
        # Filter by rule categories if specified
        if rule_categories:
            # Get the rule categories by looking up rules by ID
            filtered_results = []
            for result in rule_results:
                # Get the rule by ID to check its category
                rule = dsl_rule_engine.get_rule_by_id(result.rule_id) if hasattr(dsl_rule_engine, 'get_rule_by_id') else None
                if rule and hasattr(rule, 'category') and rule.category in rule_categories:
                    filtered_results.append(result)
                elif not rule_categories:  # If no categories specified, include all
                    filtered_results.append(result)
            rule_results = filtered_results
        
        # Calculate impact assessment
        impact_assessment = {
            "total_rules_triggered": len(rule_results),
            "severity_distribution": {},
            "categories_affected": set(),
            "overall_risk_score": 0.0,
            "critical_issues": [],
            "recommendations_summary": []
        }
        
        total_risk = 0.0
        for result in rule_results:
            # Update severity distribution
            severity = result.impact_level
            impact_assessment["severity_distribution"][severity] = impact_assessment["severity_distribution"].get(severity, 0) + 1
            
            # Track categories - get category from the rule by ID
            rule = dsl_rule_engine.get_rule_by_id(result.rule_id) if hasattr(dsl_rule_engine, 'get_rule_by_id') else None
            if rule and hasattr(rule, 'category'):
                impact_assessment["categories_affected"].add(str(rule.category))
            
            # Accumulate risk
            total_risk += result.risk_score
            
            # Track critical issues
            if result.impact_level == "Critical":
                impact_assessment["critical_issues"].append({
                    "rule_name": result.rule_name,
                    "affected_nodes": result.matching_nodes,
                    "risk_score": result.risk_score
                })
            
            # Collect recommendations
            if include_recommendations:
                impact_assessment["recommendations_summary"].extend(result.recommendations)
        
        # Calculate overall risk score
        if rule_results:
            impact_assessment["overall_risk_score"] = total_risk / len(rule_results)
        
        # Convert set to list for JSON serialization
        impact_assessment["categories_affected"] = list(impact_assessment["categories_affected"])
        
        # Remove duplicates from recommendations
        impact_assessment["recommendations_summary"] = list(set(impact_assessment["recommendations_summary"]))
        
        # Convert dataclass results to dictionaries (RuleEvaluationResult is a dataclass, not Pydantic)
        results = {
            "diagram_id": diagram_id,
            "rule_results": [asdict(result) for result in rule_results],
            "impact_assessment": impact_assessment,
            "evaluation_timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        if include_mitre:
            # Add MITRE technique mapping
            mitre_techniques = set()
            for result in rule_results:
                mitre_techniques.update(result.mitre_techniques)
            results["mitre_techniques"] = list(mitre_techniques)
        
        return {
            "evaluation_id": str(uuid.uuid4()),
            "triggered_rules": [asdict(result) for result in rule_results],
            "risk_score": impact_assessment["overall_risk_score"],
            "recommendations": impact_assessment["recommendations_summary"],
            "impact_assessment": impact_assessment,
            "mitre_techniques": results.get("mitre_techniques", []),
            "success": True,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error in enhanced rule evaluation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Findings Management API Routes

@api_router.post("/findings", response_model=Finding)
async def create_finding(finding: Finding):
    """Create a new security finding"""
    try:
        created_finding = await findings_manager.create_finding(finding)
        return created_finding
    except Exception as e:
        logger.error(f"Error creating finding: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/findings/{finding_id}", response_model=Finding)
async def get_finding(finding_id: str):
    """Get a specific finding by ID"""
    try:
        finding = await findings_manager.get_finding(finding_id)
        if not finding:
            raise HTTPException(status_code=404, detail="Finding not found")
        return finding
    except Exception as e:
        logger.error(f"Error getting finding: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/findings/{finding_id}", response_model=Finding)
async def update_finding(finding_id: str, updates: dict):
    """Update an existing finding"""
    try:
        updated_finding = await findings_manager.update_finding(finding_id, updates)
        if not updated_finding:
            raise HTTPException(status_code=404, detail="Finding not found")
        return updated_finding
    except Exception as e:
        logger.error(f"Error updating finding: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/findings/{finding_id}")
async def delete_finding(finding_id: str):
    """Delete a finding"""
    try:
        deleted = await findings_manager.delete_finding(finding_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Finding not found")
        return {"success": True, "message": "Finding deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting finding: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/findings", response_model=List[Finding])
async def list_findings(
    diagram_id: Optional[str] = None,
    node_id: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """List findings with optional filtering"""
    try:
        # Build filters
        filters = FindingsFilter()
        if diagram_id:
            filters.diagram_id = diagram_id
        if node_id:
            filters.node_id = node_id
        if severity:
            filters.severity = [FindingSeverity(severity)]
        if status:
            filters.status = [FindingStatus(status)]
        
        findings = await findings_manager.list_findings(
            filters=filters,
            skip=skip,
            limit=limit
        )
        return findings
    except Exception as e:
        logger.error(f"Error listing findings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/findings/summary", response_model=FindingsSummary)
async def get_findings_summary(diagram_id: Optional[str] = None):
    """Get findings summary statistics"""
    try:
        summary = await findings_manager.get_findings_summary(diagram_id)
        return summary
    except Exception as e:
        logger.error(f"Error getting findings summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# SPECIFIC QUESTIONNAIRE ROUTES - MUST BE BEFORE GENERIC ROUTE
# =============================================================================

@api_router.get("/questionnaires/ProductDesignSecurity")
async def get_product_design_security_questionnaire():
    """Get STRIDE-based questionnaire for ProductDesignSecurity nodes"""
    try:
        # Load questionnaire from YAML file
        import yaml
        questionnaire_path = Path(__file__).parent / "questionnaires" / "product_design_security.yaml"
        
        if not questionnaire_path.exists():
            raise HTTPException(status_code=404, detail="ProductDesignSecurity questionnaire not found")
        
        with open(questionnaire_path, 'r', encoding='utf-8') as file:
            questionnaire_data = yaml.safe_load(file)
        
        # Extract basic questionnaire (STRIDE-based)
        basic_questions = questionnaire_data.get("questionnaires", {}).get("basic", [])
        
        # Format questions for API response
        formatted_questions = []
        for question in basic_questions:
            formatted_questions.append({
                "id": question["id"],
                "question": question["question"],
                "type": question["type"],
                "options": question.get("options", []),
                "help_text": question.get("help_text", ""),
                "related_branch": question.get("related_branch", ""),
                "stride_category": question.get("stride_category", "")
            })
        
        return {
            "node_subtype": "ProductDesignSecurity",
            "node_type": questionnaire_data.get("node_type", "Design"),
            "category": questionnaire_data.get("category", "Security Architecture"),
            "description": questionnaire_data.get("description", ""),
            "questionnaire_type": "STRIDE-based Threat Modeling",
            "security_branches": questionnaire_data.get("required_branches", []),
            "prompts": formatted_questions,
            "stride_categories": ["Spoofing", "Tampering", "Repudiation", "Information Disclosure", "Denial of Service", "Elevation of Privilege"],
            "threat_intelligence": questionnaire_data.get("threat_intelligence", {}),
            "dependencies": questionnaire_data.get("dependencies", {})
        }
        
    except Exception as e:
        logger.error(f"Error loading ProductDesignSecurity questionnaire: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load questionnaire: {str(e)}")

@api_router.get("/questionnaires/{node_subtype}")
async def get_phase2_questionnaire(node_subtype: str, level: str = "basic"):
    """Get Phase 2 file-based questionnaire for specific node type and level"""
    try:
        # Validate level parameter
        try:
            questionnaire_level = LoaderQuestionnaireLevel(level.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid questionnaire level. Must be one of: {[l.value for l in LoaderQuestionnaireLevel]}")
        
        # Use the new file-based questionnaire system
        response = questionnaire_loader.create_questionnaire_response(node_subtype, questionnaire_level)
        
        if "error" in response:
            raise HTTPException(status_code=404, detail=response["error"])
        
        # Get metadata for enhanced information
        metadata = questionnaire_loader.get_metadata(node_subtype)
        
        # Add threat intelligence if available
        threat_intelligence = {}
        if metadata and metadata.threat_intelligence:
            threat_intelligence = metadata.threat_intelligence
        
        # Create comprehensive response that matches expected format
        enhanced_response = {
            "success": True,
            "node_subtype": node_subtype,
            "level": level,
            "questions": response["questions"],
            "question_count": len(response["questions"]),
            "estimated_time": response.get("estimated_time", f"{len(response['questions']) * 30} seconds"),
            "metadata": {
                "category": metadata.category if metadata else "Unknown",
                "description": metadata.description if metadata else f"{node_subtype} security questionnaire",
                "required_branches": metadata.required_branches if metadata else [],
                "threat_intelligence": threat_intelligence,
                "risk_factors": metadata.risk_factors if metadata else {}
            },
            # Legacy compatibility fields
            "prompts": response["questions"],  # Alias for backward compatibility
            "security_branches": [{"name": branch, "required": True} for branch in (metadata.required_branches if metadata else [])],
            "total_prompts": len(response["questions"]),
            "threat_intelligence": threat_intelligence,
            "framework_mappings": {
                "MITRE": threat_intelligence.get("mitre_techniques", []),
                "OWASP": ["OWASP Top 10"],
                "NIST": ["NIST Cybersecurity Framework"],
                "ISO27001": ["ISO 27001 Controls"],
                "CIS": ["CIS Controls"],
                "ASVS": ["ASVS Requirements"] if node_subtype == "WebApp" else [],
                "SOC2": ["SOC 2 Type II"],
                "GDPR": ["GDPR Article 32"] if "data" in node_subtype.lower() else []
            },
            "risk_factors": [
                f"{node_subtype} configuration complexity",
                "Integration dependencies", 
                "Exposure to external networks",
                "Data sensitivity level"
            ],
            "dependencies": [],
            # Add security_branches field as expected by testing agent - format as simple objects
            "security_branches": [{"name": branch, "required": True, "completed": False} for branch in (metadata.required_branches if metadata else [])]
        }
        
        return enhanced_response
        
    except Exception as e:
        logger.error(f"Error getting merged questionnaire prompts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions for enhanced simulation

async def get_mitre_analysis_for_diagram(diagram_id: str) -> dict:
    """Get MITRE technique analysis for a diagram"""
    try:
        # Get diagram
        diagram = await db.diagrams.find_one({"id": diagram_id})
        if not diagram:
            return {}
        
        # Use existing MITRE coverage analysis
        nodes = diagram.get("nodes", [])
        edges = diagram.get("edges", [])
        
        # This would use the existing MITRE integration
        coverage_analysis = mitre_db.analyze_coverage(nodes, edges)
        return coverage_analysis
        
    except Exception as e:
        logger.error(f"Error getting MITRE analysis: {e}")
        return {}

async def generate_security_recommendations(nodes: List[dict], edges: List[dict]) -> List[str]:
    """Generate security recommendations based on diagram analysis"""
    try:
        recommendations = []
        
        # Analyze node types and generate recommendations
        node_types = set()
        for node in nodes:
            node_type = node.get("data", {}).get("subtype", node.get("type", "unknown"))
            node_types.add(node_type.lower())
        
        # Generate recommendations based on node types present
        if "webapp" in node_types:
            recommendations.extend([
                "Implement Web Application Firewall (WAF)",
                "Enable HTTPS/TLS encryption",
                "Implement input validation and sanitization",
                "Enable security headers (HSTS, CSP, etc.)"
            ])
        
        if "database" in node_types:
            recommendations.extend([
                "Enable database encryption at rest",
                "Implement database access controls",
                "Enable database audit logging",
                "Use connection encryption (TLS)"
            ])
        
        if "api" in node_types:
            recommendations.extend([
                "Implement API rate limiting",
                "Use OAuth 2.0 or similar authentication",
                "Enable API logging and monitoring",
                "Implement API input validation"
            ])
        
        # Remove duplicates and return top recommendations
        unique_recommendations = list(set(recommendations))
        return unique_recommendations[:10]  # Return top 10
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        return []

# Initialize database indexes on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database indexes and components on startup"""
    try:
        # Create findings collection indexes
        await findings_manager.create_indexes()
        logger.info("Database indexes created successfully")
    except Exception as e:
        logger.error(f"Error creating database indexes: {e}")

# =============================================================================
# VULNERABILITY ANALYSIS API ENDPOINTS
# =============================================================================

class VulnerabilityAnalysisRequest(BaseModel):
    node_id: str
    node_type: str  # WebApp, API, Database
    questionnaire_responses: Dict[str, Any]
    node_position: Optional[Dict[str, float]] = None

class BulkVulnerabilityAnalysisRequest(BaseModel):
    nodes: List[Dict[str, Any]]

class VulnerabilityRemediationRequest(BaseModel):
    vulnerability_id: str

class EnhancedVulnerabilityRequest(BaseModel):
    """Enhanced vulnerability analysis request for specialized endpoints"""
    node_type: str
    security_config: Dict[str, Any]
    endpoints: Optional[List[Dict[str, Any]]] = []
    business_flows: Optional[List[Dict[str, Any]]] = []

# =============================================================================
# OWASP API Security Top 10 2023 Endpoints - MUST BE BEFORE GENERIC ROUTE
# =============================================================================

@api_router.post("/vulnerabilities/analyze/api1-2023")
async def analyze_api1_2023_broken_object_authorization(request: EnhancedVulnerabilityRequest):
    """API1:2023 - Broken Object Level Authorization detection"""
    try:
        vulnerabilities = []
        
        # Check for missing object-level authorization
        security_config = request.security_config
        object_auth = security_config.get("object_level_authorization", "").lower()
        user_context_validation = security_config.get("user_context_validation", False)
        
        if object_auth in ["none", "weak", ""] or not user_context_validation:
            vulnerabilities.append({
                "id": str(uuid.uuid4()),
                "name": "Broken Object Level Authorization",
                "description": "API lacks proper object-level authorization checks, allowing users to access unauthorized objects",
                "severity": "Critical",
                "category": "Broken Access Control",
                "owasp_category": "API1:2023 – Broken Object Level Authorization",
                "mitre_techniques": ["T1078", "T1083"],
                "risk_score": 9.0,
                "remediation_steps": [
                    "Implement object-level authorization checks for every API endpoint",
                    "Validate user permissions for each object access request",
                    "Use user policies and context instead of relying on object IDs",
                    "Add comprehensive authorization testing to your security suite"
                ],
                "trigger_context": {
                    "object_level_authorization": object_auth,
                    "user_context_validation": user_context_validation
                }
            })
        
        # Check endpoint-specific authorization
        for endpoint in request.endpoints:
            if endpoint.get("authorization", "").lower() in ["none", "bearer_only", ""]:
                vulnerabilities.append({
                    "id": str(uuid.uuid4()),
                    "name": f"Weak Authorization - {endpoint.get('path', 'Unknown')}",
                    "description": f"Endpoint {endpoint.get('path')} lacks proper authorization controls",
                    "severity": "High",
                    "category": "Broken Access Control", 
                    "owasp_category": "API1:2023 – Broken Object Level Authorization",
                    "mitre_techniques": ["T1078"],
                    "risk_score": 7.5,
                    "remediation_steps": [
                        f"Add object-level authorization to {endpoint.get('path')}",
                        "Validate user can access specific object IDs",
                        "Implement context-aware authorization logic"
                    ]
                })
        
        return {
            "analysis_type": "API1:2023 - Broken Object Level Authorization",
            "vulnerabilities": vulnerabilities,
            "total_count": len(vulnerabilities),
            "risk_assessment": {
                "overall_risk": "Critical" if any(v["severity"] == "Critical" for v in vulnerabilities) else "High",
                "impact": "Unauthorized access to sensitive objects and data"
            }
        }
        
    except Exception as e:
        logger.error(f"Error in API1:2023 analysis: {e}")
        raise HTTPException(status_code=500, detail=f"API1:2023 analysis failed: {str(e)}")

@api_router.post("/vulnerabilities/analyze/api3-2023")
async def analyze_api3_2023_broken_property_authorization(request: EnhancedVulnerabilityRequest):
    """API3:2023 - Broken Object Property Level Authorization detection"""
    try:
        vulnerabilities = []
        security_config = request.security_config
        
        # Check for excessive data exposure
        data_sanitization = security_config.get("data_sanitization", "").lower()
        field_level_controls = security_config.get("field_level_authorization", False)
        
        if data_sanitization in ["no sanitization", "basic sanitization", ""] or not field_level_controls:
            vulnerabilities.append({
                "id": str(uuid.uuid4()),
                "name": "Excessive Data Exposure",
                "description": "API responses contain more data than necessary, potentially exposing sensitive information",
                "severity": "Medium",
                "category": "Information Disclosure",
                "owasp_category": "API3:2023 – Broken Object Property Level Authorization",
                "mitre_techniques": ["T1213", "T1005"],
                "risk_score": 6.5,
                "remediation_steps": [
                    "Implement response filtering to only return necessary fields",
                    "Use Data Transfer Objects (DTOs) for API responses",
                    "Apply data minimization principles",
                    "Add field-level access controls"
                ],
                "trigger_context": {
                    "data_sanitization": data_sanitization,
                    "field_level_authorization": field_level_controls
                }
            })
        
        # Check for mass assignment vulnerabilities
        input_validation = security_config.get("input_validation", "").lower()
        if "mass assignment" in input_validation or input_validation in ["no validation", ""]:
            vulnerabilities.append({
                "id": str(uuid.uuid4()),
                "name": "Mass Assignment Vulnerability",
                "description": "API allows modification of object properties that should be restricted",
                "severity": "High",
                "category": "Broken Access Control",
                "owasp_category": "API3:2023 – Broken Object Property Level Authorization",
                "mitre_techniques": ["T1078", "T1055"],
                "risk_score": 7.0,
                "remediation_steps": [
                    "Implement allowlists for updatable fields",
                    "Validate input against expected schema",
                    "Use separate DTOs for input and output",
                    "Add property-level authorization checks"
                ]
            })
        
        return {
            "analysis_type": "API3:2023 - Broken Object Property Level Authorization",
            "vulnerabilities": vulnerabilities,
            "total_count": len(vulnerabilities),
            "risk_assessment": {
                "overall_risk": "High" if any(v["severity"] == "High" for v in vulnerabilities) else "Medium",
                "impact": "Unauthorized access to sensitive object properties"
            }
        }
        
    except Exception as e:
        logger.error(f"Error in API3:2023 analysis: {e}")
        raise HTTPException(status_code=500, detail=f"API3:2023 analysis failed: {str(e)}")

@api_router.post("/vulnerabilities/analyze/api4-2023")
async def analyze_api4_2023_resource_consumption(request: EnhancedVulnerabilityRequest):
    """API4:2023 - Unrestricted Resource Consumption detection"""
    try:
        vulnerabilities = []
        security_config = request.security_config
        
        # Check for rate limiting
        rate_limiting = security_config.get("rate_limiting", "").lower()
        if rate_limiting in ["none", "no rate limiting", ""]:
            vulnerabilities.append({
                "id": str(uuid.uuid4()),
                "name": "No Rate Limiting",
                "description": "API lacks rate limiting controls, vulnerable to resource exhaustion attacks",
                "severity": "Medium",
                "category": "Denial of Service",
                "owasp_category": "API4:2023 – Unrestricted Resource Consumption",
                "mitre_techniques": ["T1499", "T1498"],
                "risk_score": 6.0,
                "remediation_steps": [
                    "Implement comprehensive rate limiting per user/IP",
                    "Add request size and payload limits",
                    "Configure timeout controls for long operations",
                    "Monitor resource consumption patterns"
                ]
            })
        
        # Check for pagination limits
        pagination = security_config.get("pagination_security", "").lower()
        if pagination in ["no pagination", "no pagination limits", ""]:
            vulnerabilities.append({
                "id": str(uuid.uuid4()),
                "name": "Unlimited Data Retrieval",
                "description": "API allows unlimited data retrieval without pagination controls",
                "severity": "Medium", 
                "category": "Denial of Service",
                "owasp_category": "API4:2023 – Unrestricted Resource Consumption",
                "mitre_techniques": ["T1499"],
                "risk_score": 5.5,
                "remediation_steps": [
                    "Implement mandatory pagination with reasonable limits",
                    "Add maximum result set size controls",
                    "Use cursor-based pagination for large datasets",
                    "Monitor and alert on excessive data requests"
                ]
            })
        
        return {
            "analysis_type": "API4:2023 - Unrestricted Resource Consumption",
            "vulnerabilities": vulnerabilities,
            "total_count": len(vulnerabilities),
            "risk_assessment": {
                "overall_risk": "Medium",
                "impact": "Resource exhaustion and denial of service"
            }
        }
        
    except Exception as e:
        logger.error(f"Error in API4:2023 analysis: {e}")
        raise HTTPException(status_code=500, detail=f"API4:2023 analysis failed: {str(e)}")

@api_router.post("/vulnerabilities/analyze/api6-2023")
async def analyze_api6_2023_sensitive_business_flows(request: EnhancedVulnerabilityRequest):
    """API6:2023 - Unrestricted Access to Sensitive Business Flows detection"""
    try:
        vulnerabilities = []
        security_config = request.security_config
        
        # Check business flow protection
        business_flow_protection = security_config.get("business_flow_protection", False)
        automated_threat_detection = security_config.get("automated_threat_detection", False)
        
        if not business_flow_protection or not automated_threat_detection:
            vulnerabilities.append({
                "id": str(uuid.uuid4()),
                "name": "Unprotected Sensitive Business Flows",
                "description": "Sensitive business operations lack protection against automation and abuse",
                "severity": "High",
                "category": "Business Logic Vulnerabilities",
                "owasp_category": "API6:2023 – Unrestricted Access to Sensitive Business Flows",
                "mitre_techniques": ["T1499", "T1078"],
                "risk_score": 7.5,
                "remediation_steps": [
                    "Implement business logic rate limiting",
                    "Add CAPTCHA or challenge-response for sensitive operations",
                    "Monitor for automation patterns and bot behavior",
                    "Implement user behavior analytics"
                ]
            })
        
        # Check specific business flows
        for flow in request.business_flows:
            flow_name = flow.get("name", "Unknown")
            protection = flow.get("protection", "").lower()
            rate_limit = flow.get("rate_limit")
            
            if protection in ["none", ""] or rate_limit is None:
                severity = "High" if flow_name in ["password_reset", "account_creation", "payment_processing"] else "Medium"
                vulnerabilities.append({
                    "id": str(uuid.uuid4()),
                    "name": f"Unprotected Business Flow - {flow_name}",
                    "description": f"Business flow '{flow_name}' lacks adequate protection controls",
                    "severity": severity,
                    "category": "Business Logic Vulnerabilities",
                    "owasp_category": "API6:2023 – Unrestricted Access to Sensitive Business Flows",
                    "mitre_techniques": ["T1499", "T1078"],
                    "risk_score": 7.0 if severity == "High" else 5.5,
                    "remediation_steps": [
                        f"Add rate limiting to {flow_name} workflow",
                        "Implement anti-automation controls",
                        "Add behavioral monitoring",
                        "Configure abuse detection alerts"
                    ]
                })
        
        return {
            "analysis_type": "API6:2023 - Unrestricted Access to Sensitive Business Flows",
            "vulnerabilities": vulnerabilities,
            "total_count": len(vulnerabilities),
            "risk_assessment": {
                "overall_risk": "High" if any(v["severity"] == "High" for v in vulnerabilities) else "Medium",
                "impact": "Business process abuse and financial/reputational damage"
            }
        }
        
    except Exception as e:
        logger.error(f"Error in API6:2023 analysis: {e}")
        raise HTTPException(status_code=500, detail=f"API6:2023 analysis failed: {str(e)}")

@api_router.post("/vulnerabilities/analyze/api7-2023")
async def analyze_api7_2023_server_side_request_forgery(request: EnhancedVulnerabilityRequest):
    """API7:2023 - Server-Side Request Forgery detection"""
    try:
        vulnerabilities = []
        security_config = request.security_config
        
        # Check for SSRF protections
        url_validation = security_config.get("url_validation", "").lower()
        allowlist_implementation = security_config.get("external_request_allowlist", False)
        network_segmentation = security_config.get("network_segmentation", False)
        
        if url_validation in ["no validation", "basic validation", ""] or not allowlist_implementation:
            vulnerabilities.append({
                "id": str(uuid.uuid4()),
                "name": "Server-Side Request Forgery",
                "description": "API can be manipulated to make unauthorized requests to internal or external systems",
                "severity": "High",
                "category": "Server-Side Request Forgery",
                "owasp_category": "API7:2023 – Server-Side Request Forgery",
                "mitre_techniques": ["T1190", "T1071"],
                "risk_score": 8.0,
                "remediation_steps": [
                    "Validate and sanitize all user-supplied URLs",
                    "Implement strict allowlist for external requests",
                    "Use network segmentation to limit internal access",
                    "Disable unused URL schemas (file://, ftp://, etc.)"
                ],
                "trigger_context": {
                    "url_validation": url_validation,
                    "allowlist_implementation": allowlist_implementation,
                    "network_segmentation": network_segmentation
                }
            })
        
        # Check input validation for URLs
        input_validation = security_config.get("input_validation", "").lower()
        if input_validation in ["no validation", "client-side only", ""]:
            vulnerabilities.append({
                "id": str(uuid.uuid4()),
                "name": "Insufficient Input Validation for URLs",
                "description": "Inadequate validation of URL inputs enables SSRF attacks",
                "severity": "Medium",
                "category": "Injection",
                "owasp_category": "API7:2023 – Server-Side Request Forgery",
                "mitre_techniques": ["T1190"],
                "risk_score": 6.5,
                "remediation_steps": [
                    "Implement comprehensive URL validation",
                    "Use regular expressions to validate URL patterns",
                    "Check URL schemes and domains against allowlist",
                    "Sanitize URL parameters"
                ]
            })
        
        return {
            "analysis_type": "API7:2023 - Server-Side Request Forgery",
            "vulnerabilities": vulnerabilities,
            "total_count": len(vulnerabilities),
            "risk_assessment": {
                "overall_risk": "High" if any(v["severity"] == "High" for v in vulnerabilities) else "Medium",
                "impact": "Unauthorized access to internal systems and data exfiltration"
            }
        }
        
    except Exception as e:
        logger.error(f"Error in API7:2023 analysis: {e}")
        raise HTTPException(status_code=500, detail=f"API7:2023 analysis failed: {str(e)}")

@api_router.post("/vulnerabilities/analyze/api9-2023")
async def analyze_api9_2023_improper_inventory_management(request: EnhancedVulnerabilityRequest):
    """API9:2023 - Improper Inventory Management detection"""
    try:
        vulnerabilities = []
        security_config = request.security_config
        
        # Check API documentation and inventory
        documentation = security_config.get("documentation_security", "").lower()
        version_management = security_config.get("version_management", "").lower()
        api_discovery = security_config.get("api_discovery_controls", False)
        
        if documentation in ["no documentation", "public detailed docs", ""]:
            severity = "Medium" if documentation == "public detailed docs" else "Low"
            vulnerabilities.append({
                "id": str(uuid.uuid4()),
                "name": "Poor API Documentation Security",
                "description": "API documentation practices create security risks through information disclosure",
                "severity": severity,
                "category": "Information Disclosure",
                "owasp_category": "API9:2023 – Improper Inventory Management",
                "mitre_techniques": ["T1190", "T1213"],
                "risk_score": 5.0 if severity == "Medium" else 3.0,
                "remediation_steps": [
                    "Review and sanitize public API documentation",
                    "Remove sensitive internal details from public docs",
                    "Implement separate documentation for internal/external use",
                    "Regular documentation security reviews"
                ]
            })
        
        if version_management in ["no version management", "poor versioning", ""]:
            vulnerabilities.append({
                "id": str(uuid.uuid4()),
                "name": "Poor API Version Management",
                "description": "Inadequate API version management creates security blind spots",
                "severity": "Low",
                "category": "Security Misconfiguration",
                "owasp_category": "API9:2023 – Improper Inventory Management",
                "mitre_techniques": ["T1190"],
                "risk_score": 4.0,
                "remediation_steps": [
                    "Implement comprehensive API versioning strategy",
                    "Maintain inventory of all API versions",
                    "Plan deprecation timeline for old versions",
                    "Monitor usage of deprecated endpoints"
                ]
            })
        
        if not api_discovery:
            vulnerabilities.append({
                "id": str(uuid.uuid4()),
                "name": "Lack of API Discovery Controls",
                "description": "Missing API discovery and inventory management capabilities",
                "severity": "Low",
                "category": "Security Misconfiguration",
                "owasp_category": "API9:2023 – Improper Inventory Management",
                "mitre_techniques": ["T1190"],
                "risk_score": 4.5,
                "remediation_steps": [
                    "Implement automated API discovery tools",
                    "Maintain real-time API inventory",
                    "Monitor for shadow or undocumented APIs",
                    "Regular API security assessments"
                ]
            })
        
        return {
            "analysis_type": "API9:2023 - Improper Inventory Management",
            "vulnerabilities": vulnerabilities,
            "total_count": len(vulnerabilities),
            "risk_assessment": {
                "overall_risk": "Medium" if any(v["severity"] == "Medium" for v in vulnerabilities) else "Low",
                "impact": "Security blind spots and increased attack surface"
            }
        }
        
    except Exception as e:
        logger.error(f"Error in API9:2023 analysis: {e}")
        raise HTTPException(status_code=500, detail=f"API9:2023 analysis failed: {str(e)}")

# =============================================================================
# ENHANCED DATABASE SECURITY ENDPOINTS - MUST BE BEFORE GENERIC ROUTE
# =============================================================================

@api_router.post("/vulnerabilities/analyze/privilege-escalation")
async def analyze_privilege_escalation(request: EnhancedVulnerabilityRequest):
    """Enhanced Database Security - Privilege Escalation detection"""
    try:
        vulnerabilities = []
        security_config = request.security_config
        
        # Check privilege management
        privilege_mgmt = security_config.get("privilege_management", "").lower()
        if privilege_mgmt in ["static user privileges", "excessive privileges", ""]:
            vulnerabilities.append({
                "id": str(uuid.uuid4()),
                "name": "Database Privilege Escalation Risk",
                "description": "Database configuration allows potential privilege escalation beyond intended access levels",
                "severity": "High",
                "category": "Broken Access Control",
                "owasp_category": "A01:2023 – Broken Access Control",
                "mitre_techniques": ["T1068", "T1078"],
                "risk_score": 7.5,
                "remediation_steps": [
                    "Implement dynamic privilege management system",
                    "Apply principle of least privilege strictly",
                    "Conduct regular privilege audits and reviews",
                    "Monitor and alert on privilege changes"
                ]
            })
        
        # Check for shared accounts
        access_control = security_config.get("access_control", "").lower()
        if "shared accounts" in access_control:
            vulnerabilities.append({
                "id": str(uuid.uuid4()),
                "name": "Shared Database Accounts",
                "description": "Use of shared database accounts increases privilege escalation risk",
                "severity": "Medium",
                "category": "Identification and Authentication Failures",
                "owasp_category": "A07:2023 – Identification and Authentication Failures",
                "mitre_techniques": ["T1078"],
                "risk_score": 6.0,
                "remediation_steps": [
                    "Replace shared accounts with individual user accounts",
                    "Implement proper user authentication and authorization",
                    "Add account activity monitoring",
                    "Establish account lifecycle management"
                ]
            })
        
        return {
            "analysis_type": "Enhanced Database Security - Privilege Escalation",
            "vulnerabilities": vulnerabilities,
            "total_count": len(vulnerabilities),
            "risk_assessment": {
                "overall_risk": "High" if any(v["severity"] == "High" for v in vulnerabilities) else "Medium",
                "impact": "Unauthorized database access and data manipulation"
            }
        }
        
    except Exception as e:
        logger.error(f"Error in privilege escalation analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Privilege escalation analysis failed: {str(e)}")

@api_router.post("/vulnerabilities/analyze/config-drift")
async def analyze_config_drift(request: EnhancedVulnerabilityRequest):
    """Enhanced Database Security - Configuration Drift detection"""
    try:
        vulnerabilities = []
        security_config = request.security_config
        
        # Check change management
        change_mgmt = security_config.get("change_management", "").lower()
        if change_mgmt in ["no change management", "manual change tracking", ""]:
            vulnerabilities.append({
                "id": str(uuid.uuid4()),
                "name": "Database Configuration Drift",
                "description": "Database security configuration may have drifted from established security baseline",
                "severity": "Medium",
                "category": "Security Misconfiguration",
                "owasp_category": "A05:2023 – Security Misconfiguration",
                "mitre_techniques": ["T1190", "T1212"],
                "risk_score": 6.0,
                "remediation_steps": [
                    "Implement automated configuration management",
                    "Establish regular configuration baseline audits",
                    "Deploy automated compliance checking tools",
                    "Set up configuration drift detection and alerts"
                ]
            })
        
        # Check configuration monitoring
        config_monitoring = security_config.get("configuration_monitoring", False)
        if not config_monitoring:
            vulnerabilities.append({
                "id": str(uuid.uuid4()),
                "name": "No Configuration Monitoring",
                "description": "Lack of configuration monitoring prevents detection of security drift",
                "severity": "Medium",
                "category": "Security Logging and Monitoring Failures",
                "owasp_category": "A09:2023 – Security Logging and Monitoring Failures",
                "mitre_techniques": ["T1562", "T1070"],
                "risk_score": 5.5,
                "remediation_steps": [
                    "Implement continuous configuration monitoring",
                    "Set up automated alerts for configuration changes",
                    "Establish configuration change approval workflows",
                    "Regular configuration security assessments"
                ]
            })
        
        return {
            "analysis_type": "Enhanced Database Security - Configuration Drift",
            "vulnerabilities": vulnerabilities,
            "total_count": len(vulnerabilities),
            "risk_assessment": {
                "overall_risk": "Medium",
                "impact": "Security control degradation and compliance violations"
            }
        }
        
    except Exception as e:
        logger.error(f"Error in config drift analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Configuration drift analysis failed: {str(e)}")

@api_router.post("/vulnerabilities/analyze/advanced-injection")
async def analyze_advanced_injection(request: EnhancedVulnerabilityRequest):
    """Enhanced Database Security - Advanced Injection detection"""
    try:
        vulnerabilities = []
        security_config = request.security_config
        
        # Check stored procedure security
        stored_proc_security = security_config.get("stored_procedure_security", "").lower()
        if stored_proc_security in ["no security measures", "basic implementation", ""]:
            vulnerabilities.append({
                "id": str(uuid.uuid4()),
                "name": "Advanced Database Injection Vulnerability",
                "description": "Database vulnerable to NoSQL injection, LDAP injection, or command injection through stored procedures",
                "severity": "Critical",
                "category": "Injection",
                "owasp_category": "A03:2023 – Injection",
                "mitre_techniques": ["T1190", "T1059"],
                "risk_score": 8.5,
                "remediation_steps": [
                    "Implement comprehensive input validation for all database types",
                    "Use parameterized queries for SQL, NoSQL, and LDAP operations",
                    "Apply principle of least privilege for database access",
                    "Conduct regular security code reviews of database procedures"
                ]
            })
        
        # Check query parameterization
        query_parameterization = security_config.get("query_parameterization", "").lower()
        if query_parameterization in ["dynamic queries", "string concatenation", ""]:
            vulnerabilities.append({
                "id": str(uuid.uuid4()),
                "name": "Dynamic Query Construction",
                "description": "Use of dynamic query construction enables advanced injection attacks",
                "severity": "High",
                "category": "Injection",
                "owasp_category": "A03:2023 – Injection",
                "mitre_techniques": ["T1190"],
                "risk_score": 7.0,
                "remediation_steps": [
                    "Replace dynamic queries with parameterized queries",
                    "Implement input validation and sanitization",
                    "Use ORM frameworks with built-in protection",
                    "Regular security testing of database interactions"
                ]
            })
        
        return {
            "analysis_type": "Enhanced Database Security - Advanced Injection",
            "vulnerabilities": vulnerabilities,
            "total_count": len(vulnerabilities),
            "risk_assessment": {
                "overall_risk": "Critical" if any(v["severity"] == "Critical" for v in vulnerabilities) else "High",
                "impact": "Database compromise and data exfiltration"
            }
        }
        
    except Exception as e:
        logger.error(f"Error in advanced injection analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Advanced injection analysis failed: {str(e)}")

@api_router.post("/vulnerabilities/analyze/insider-threat")
async def analyze_insider_threat(request: EnhancedVulnerabilityRequest):
    """Enhanced Database Security - Insider Threat detection"""
    try:
        vulnerabilities = []
        security_config = request.security_config
        
        # Check user activity monitoring
        activity_monitoring = security_config.get("user_activity_monitoring", "").lower()
        if activity_monitoring in ["no activity monitoring", "basic user tracking", ""]:
            vulnerabilities.append({
                "id": str(uuid.uuid4()),
                "name": "Database Insider Threat Risk",
                "description": "Database lacks sufficient monitoring to detect malicious insider activities",
                "severity": "Medium",
                "category": "Security Logging and Monitoring Failures",
                "owasp_category": "A09:2023 – Security Logging and Monitoring Failures",
                "mitre_techniques": ["T1078", "T1213"],
                "risk_score": 6.5,
                "remediation_steps": [
                    "Implement user behavior analytics for database access",
                    "Add comprehensive privileged access monitoring",
                    "Establish regular access reviews and recertification",
                    "Deploy data loss prevention (DLP) solutions"
                ]
            })
        
        # Check privileged access controls
        privileged_access = security_config.get("privileged_access_management", False)
        if not privileged_access:
            vulnerabilities.append({
                "id": str(uuid.uuid4()),
                "name": "Insufficient Privileged Access Controls",
                "description": "Lack of privileged access management increases insider threat risk",
                "severity": "Medium",
                "category": "Broken Access Control",
                "owasp_category": "A01:2023 – Broken Access Control",
                "mitre_techniques": ["T1078"],
                "risk_score": 6.0,
                "remediation_steps": [
                    "Implement privileged access management (PAM) solution",
                    "Add session recording for privileged database access",
                    "Establish approval workflows for sensitive operations",
                    "Monitor and alert on unusual privileged activities"
                ]
            })
        
        return {
            "analysis_type": "Enhanced Database Security - Insider Threat",
            "vulnerabilities": vulnerabilities,
            "total_count": len(vulnerabilities),
            "risk_assessment": {
                "overall_risk": "Medium",
                "impact": "Data theft and unauthorized database modifications by insiders"
            }
        }
        
    except Exception as e:
        logger.error(f"Error in insider threat analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Insider threat analysis failed: {str(e)}")

@api_router.post("/vulnerabilities/analyze/backup-security")
async def analyze_backup_security(request: EnhancedVulnerabilityRequest):
    """Enhanced Database Security - Backup Security detection"""
    try:
        vulnerabilities = []
        security_config = request.security_config
        
        # Check backup encryption
        backup_encryption = security_config.get("backup_encryption", "").lower()
        if backup_encryption in ["unencrypted backups", ""]:
            vulnerabilities.append({
                "id": str(uuid.uuid4()),
                "name": "Unencrypted Database Backups",
                "description": "Database backups are not properly encrypted and could be compromised",
                "severity": "High",
                "category": "Cryptographic Failures",
                "owasp_category": "A02:2023 – Cryptographic Failures",
                "mitre_techniques": ["T1005", "T1213"],
                "risk_score": 7.0,
                "remediation_steps": [
                    "Enable encryption for all database backups",
                    "Implement secure backup storage with access controls",
                    "Regular backup integrity testing and validation",
                    "Establish secure key management for backup encryption"
                ]
            })
        
        # Check backup access controls
        backup_access = security_config.get("backup_access_controls", False)
        if not backup_access:
            vulnerabilities.append({
                "id": str(uuid.uuid4()),
                "name": "Insufficient Backup Access Controls",
                "description": "Database backup files lack adequate access controls",
                "severity": "Medium",
                "category": "Broken Access Control",
                "owasp_category": "A01:2023 – Broken Access Control",
                "mitre_techniques": ["T1005"],
                "risk_score": 6.0,
                "remediation_steps": [
                    "Implement strict access controls for backup files",
                    "Use separate credentials for backup access",
                    "Monitor and log backup file access",
                    "Regular access review for backup systems"
                ]
            })
        
        # Check backup testing
        backup_testing = security_config.get("backup_restoration_testing", "").lower()
        if backup_testing in ["no testing", "irregular testing", ""]:
            vulnerabilities.append({
                "id": str(uuid.uuid4()),
                "name": "Untested Backup Recovery",
                "description": "Database backup recovery procedures are not regularly tested",
                "severity": "Medium",
                "category": "Software and Data Integrity Failures",
                "owasp_category": "A08:2023 – Software and Data Integrity Failures",
                "mitre_techniques": ["T1485"],
                "risk_score": 5.5,
                "remediation_steps": [
                    "Establish regular backup restoration testing schedule",
                    "Validate backup integrity and completeness",
                    "Document and test disaster recovery procedures",
                    "Monitor backup success rates and alert on failures"
                ]
            })
        
        return {
            "analysis_type": "Enhanced Database Security - Backup Security",
            "vulnerabilities": vulnerabilities,
            "total_count": len(vulnerabilities),
            "risk_assessment": {
                "overall_risk": "High" if any(v["severity"] == "High" for v in vulnerabilities) else "Medium",
                "impact": "Data loss and unauthorized access to backup data"
            }
        }
        
    except Exception as e:
        logger.error(f"Error in backup security analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Backup security analysis failed: {str(e)}")

@api_router.post("/vulnerabilities/analyze/{node_id}")
async def analyze_node_vulnerabilities(node_id: str, request: VulnerabilityAnalysisRequest):
    """Analyze security vulnerabilities for a specific node based on questionnaire responses"""
    try:
        logger.info(f"Analyzing vulnerabilities for node {node_id} of type {request.node_type}")
        
        # Analyze vulnerabilities using questionnaire analyzer
        result = questionnaire_analyzer.analyze_questionnaire_responses(
            node_id=request.node_id,
            node_type=request.node_type,
            questionnaire_responses=request.questionnaire_responses,
            node_position=request.node_position
        )
        
        # Convert to dict for JSON response
        return {
            "node_id": result.node_id,
            "node_type": result.node_type,
            "total_vulnerabilities": result.total_vulnerabilities,
            "vulnerabilities_by_severity": {k.value: v for k, v in result.vulnerabilities_by_severity.items()},
            "vulnerability_nodes": [
                {
                    "id": vuln.id,
                    "name": vuln.name,
                    "description": vuln.description,
                    "severity": vuln.severity.value,
                    "category": vuln.category.value,
                    "owasp_category": vuln.owasp_category,
                    "mitre_techniques": vuln.mitre_techniques,
                    "cve_references": vuln.cve_references,
                    "parent_node_id": vuln.parent_node_id,
                    "remediation_steps": vuln.remediation_steps,
                    "risk_score": vuln.risk_score,
                    "position": vuln.position,
                    "color": vuln.color,
                    "icon": vuln.icon,
                    "connection_style": vuln.connection_style,
                    "created_at": vuln.created_at.isoformat(),
                    # Educational context fields
                    "trigger_context": vuln.trigger_context,
                    "triggered_by_rule": vuln.triggered_by_rule,
                    "missing_controls": vuln.missing_controls,
                    "user_selections": vuln.user_selections
                }
                for vuln in result.vulnerability_nodes
            ],
            "overall_risk_score": result.overall_risk_score,
            "recommendations": result.recommendations,
            "analysis_timestamp": result.analysis_timestamp.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error analyzing vulnerabilities for node {node_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Vulnerability analysis failed: {str(e)}")

@api_router.get("/vulnerabilities/rules")
async def get_vulnerability_rules():
    """Get all available vulnerability rules"""
    try:
        from vulnerability_rules import get_vulnerability_rules
        rules = get_vulnerability_rules()
        
        return {
            "total_rules": len(rules),
            "rules_by_node_type": {
                "WebApp": len([r for r in rules if "WebApp" in r.node_types]),
                "API": len([r for r in rules if "API" in r.node_types]),
                "Database": len([r for r in rules if "Database" in r.node_types])
            },
            "rules": [
                {
                    "id": rule.id,
                    "name": rule.name,
                    "description": rule.description,
                    "node_types": rule.node_types,
                    "vulnerability_category": rule.vulnerability_template.get("category", "Unknown"),
                    "severity": rule.vulnerability_template.get("severity", "Medium"),
                    "owasp_category": rule.vulnerability_template.get("owasp_category", "")
                }
                for rule in rules
            ]
        }
        
    except Exception as e:
        logger.error(f"Error retrieving vulnerability rules: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve vulnerability rules: {str(e)}")

@api_router.get("/vulnerabilities/{node_id}")
async def get_node_vulnerabilities(node_id: str):
    """Get existing vulnerability analysis for a node"""
    try:
        # Check if analysis exists in cache
        if node_id in vulnerability_engine.vulnerability_cache:
            result = vulnerability_engine.vulnerability_cache[node_id]
            return {
                "node_id": result.node_id,
                "node_type": result.node_type,
                "total_vulnerabilities": result.total_vulnerabilities,
                "vulnerabilities_by_severity": {k.value: v for k, v in result.vulnerabilities_by_severity.items()},
                "vulnerability_nodes": [
                    {
                        "id": vuln.id,
                        "name": vuln.name,
                        "description": vuln.description,
                        "severity": vuln.severity.value,
                        "category": vuln.category.value,
                        "owasp_category": vuln.owasp_category,
                        "mitre_techniques": vuln.mitre_techniques,
                        "parent_node_id": vuln.parent_node_id,
                        "remediation_steps": vuln.remediation_steps,
                        "risk_score": vuln.risk_score,
                        "position": vuln.position,
                        "color": vuln.color,
                        "icon": vuln.icon,
                        # Educational context fields
                        "trigger_context": vuln.trigger_context,
                        "triggered_by_rule": vuln.triggered_by_rule,
                        "missing_controls": vuln.missing_controls,
                        "user_selections": vuln.user_selections
                    }
                    for vuln in result.vulnerability_nodes
                ],
                "overall_risk_score": result.overall_risk_score,
                "recommendations": result.recommendations,
                "analysis_timestamp": result.analysis_timestamp.isoformat()
            }
        else:
            return {
                "node_id": node_id,
                "total_vulnerabilities": 0,
                "vulnerability_nodes": [],
                "message": "No vulnerability analysis found for this node"
            }
            
    except Exception as e:
        logger.error(f"Error retrieving vulnerabilities for node {node_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve vulnerabilities: {str(e)}")

@api_router.post("/vulnerabilities/remediate/{vulnerability_id}")
async def get_vulnerability_remediation(vulnerability_id: str):
    """Get detailed remediation guidance for a specific vulnerability"""
    try:
        vulnerability = vulnerability_engine.get_vulnerability_by_id(vulnerability_id)
        
        if not vulnerability:
            raise HTTPException(status_code=404, detail="Vulnerability not found")
        
        # Generate enhanced remediation guidance
        remediation_guidance = {
            "vulnerability_id": vulnerability_id,
            "vulnerability_name": vulnerability.name,
            "severity": vulnerability.severity.value,
            "category": vulnerability.category.value,
            "owasp_category": vulnerability.owasp_category,
            "immediate_steps": vulnerability.remediation_steps,
            "implementation_priority": "High" if vulnerability.severity in [VulnerabilitySeverity.CRITICAL, VulnerabilitySeverity.HIGH] else "Medium",
            "estimated_effort": _estimate_remediation_effort(vulnerability),
            "tools_and_resources": _get_remediation_resources(vulnerability),
            "validation_steps": _get_validation_steps(vulnerability),
            "prevention_measures": _get_prevention_measures(vulnerability)
        }
        
        return remediation_guidance
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting remediation for vulnerability {vulnerability_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get remediation guidance: {str(e)}")

@api_router.delete("/vulnerabilities/{vulnerability_id}")
async def mark_vulnerability_fixed(vulnerability_id: str):
    """Mark a vulnerability as fixed/remediated"""
    try:
        success = vulnerability_engine.remove_vulnerability(vulnerability_id)
        
        if success:
            return {"message": "Vulnerability marked as fixed", "vulnerability_id": vulnerability_id}
        else:
            raise HTTPException(status_code=404, detail="Vulnerability not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking vulnerability {vulnerability_id} as fixed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to mark vulnerability as fixed: {str(e)}")

@api_router.post("/vulnerabilities/bulk-analyze")
async def bulk_analyze_vulnerabilities(request: BulkVulnerabilityAnalysisRequest):
    """Analyze vulnerabilities for multiple nodes in bulk"""
    try:
        logger.info(f"Bulk analyzing vulnerabilities for {len(request.nodes)} nodes")
        
        results_list = []  # Change to list instead of dict
        total_vulnerabilities = 0
        total_risk_score = 0.0
        successful_analyses = 0
        
        for node_data in request.nodes:
            try:
                result = questionnaire_analyzer.analyze_questionnaire_responses(
                    node_id=node_data["node_id"],
                    node_type=node_data["node_type"],
                    questionnaire_responses=node_data.get("questionnaire_responses", {}),
                    node_position=node_data.get("position")
                )
                
                node_result = {
                    "node_id": result.node_id,
                    "node_type": result.node_type,
                    "total_vulnerabilities": result.total_vulnerabilities,
                    "vulnerabilities_by_severity": {k.value: v for k, v in result.vulnerabilities_by_severity.items()},
                    "overall_risk_score": result.overall_risk_score,
                    "vulnerability_count": len(result.vulnerability_nodes),
                    "vulnerability_nodes": [
                        {
                            "id": vuln.id,
                            "name": vuln.name,
                            "severity": vuln.severity.value,
                            "category": vuln.category.value,
                            "owasp_category": vuln.owasp_category
                        }
                        for vuln in result.vulnerability_nodes[:5]  # Limit to first 5 for performance
                    ]
                }
                
                results_list.append(node_result)
                total_vulnerabilities += result.total_vulnerabilities
                total_risk_score += result.overall_risk_score
                successful_analyses += 1
                
            except Exception as node_error:
                logger.error(f"Error analyzing node {node_data.get('node_id', 'unknown')}: {node_error}")
                results_list.append({
                    "node_id": node_data.get("node_id", "unknown"),
                    "node_type": node_data.get("node_type", "Unknown"),
                    "error": str(node_error),
                    "total_vulnerabilities": 0,
                    "overall_risk_score": 0.0
                })
        
        # Calculate summary statistics
        avg_risk_score = total_risk_score / successful_analyses if successful_analyses > 0 else 0
        
        # Return as list format as expected by testing agent
        return results_list
        
    except Exception as e:
        logger.error(f"Error in bulk vulnerability analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Bulk analysis failed: {str(e)}")
        
    except Exception as e:
        logger.error(f"Error in bulk vulnerability analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Bulk analysis failed: {str(e)}")

@api_router.get("/questionnaire/responses/{node_id}")
async def get_node_questionnaire_summary(node_id: str):
    """Get questionnaire response summary for a node"""
    try:
        summary = questionnaire_analyzer.get_response_summary(node_id)
        
        if not summary:
            return {
                "node_id": node_id,
                "message": "No questionnaire responses found for this node"
            }
        
        return summary
        
    except Exception as e:
        logger.error(f"Error retrieving questionnaire summary for node {node_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve questionnaire summary: {str(e)}")

def _estimate_remediation_effort(vulnerability: VulnerabilityNode) -> str:
    """Estimate effort required to remediate a vulnerability"""
    effort_map = {
        VulnerabilitySeverity.CRITICAL: "High (1-2 weeks)",
        VulnerabilitySeverity.HIGH: "Medium (3-5 days)",
        VulnerabilitySeverity.MEDIUM: "Low (1-2 days)",
        VulnerabilitySeverity.LOW: "Minimal (< 1 day)"
    }
    return effort_map.get(vulnerability.severity, "Medium")

def _get_remediation_resources(vulnerability: VulnerabilityNode) -> List[str]:
    """Get tools and resources for vulnerability remediation"""
    resources = []
    
    if "injection" in vulnerability.category.value.lower():
        resources.extend([
            "OWASP Input Validation Cheat Sheet",
            "Parameterized query frameworks (SqlAlchemy, Hibernate)",
            "Static Analysis Security Testing (SAST) tools"
        ])
    
    if "access control" in vulnerability.category.value.lower():
        resources.extend([
            "OAuth2 and OpenID Connect implementations",
            "Role-Based Access Control (RBAC) frameworks",
            "Session management libraries"
        ])
    
    if "cryptographic" in vulnerability.category.value.lower():
        resources.extend([
            "TLS/SSL configuration guides",
            "Encryption key management solutions",
            "Cryptographic libraries (libsodium, Bouncy Castle)"
        ])
    
    return resources[:5]  # Limit to top 5

def _get_validation_steps(vulnerability: VulnerabilityNode) -> List[str]:
    """Get steps to validate vulnerability remediation"""
    steps = [
        "Re-run security questionnaire to verify controls are in place",
        "Perform targeted security testing for the specific vulnerability",
        "Validate remediation through automated security scans"
    ]
    
    if vulnerability.severity in [VulnerabilitySeverity.CRITICAL, VulnerabilitySeverity.HIGH]:
        steps.append("Conduct penetration testing to verify fix effectiveness")
    
    return steps

def _get_prevention_measures(vulnerability: VulnerabilityNode) -> List[str]:
    """Get measures to prevent similar vulnerabilities"""
    measures = [
        "Implement security-focused code review processes",
        "Add automated security testing to CI/CD pipelines",
        "Provide security training for development team",
        "Establish security design review procedures"
    ]
    
    return measures

# =============================================================================
# ENHANCED VULNERABILITY DETECTION ENDPOINTS - OWASP API Security Top 10 2023
# =============================================================================

@api_router.post("/vulnerabilities/analyze/api1-2023")
async def analyze_api1_2023_broken_object_authorization(request: EnhancedVulnerabilityRequest):
    """API1:2023 - Broken Object Level Authorization detection"""
    try:
        vulnerabilities = []
        
        # Check for missing object-level authorization
        security_config = request.security_config
        object_auth = security_config.get("object_level_authorization", "").lower()
        user_context_validation = security_config.get("user_context_validation", False)
        
        if object_auth in ["none", "weak", ""] or not user_context_validation:
            vulnerabilities.append({
                "id": str(uuid.uuid4()),
                "name": "Broken Object Level Authorization",
                "description": "API lacks proper object-level authorization checks, allowing users to access unauthorized objects",
                "severity": "Critical",
                "category": "Broken Access Control",
                "owasp_category": "API1:2023 – Broken Object Level Authorization",
                "mitre_techniques": ["T1078", "T1083"],
                "risk_score": 9.0,
                "remediation_steps": [
                    "Implement object-level authorization checks for every API endpoint",
                    "Validate user permissions for each object access request",
                    "Use user policies and context instead of relying on object IDs",
                    "Add comprehensive authorization testing to your security suite"
                ],
                "trigger_context": {
                    "object_level_authorization": object_auth,
                    "user_context_validation": user_context_validation
                }
            })
        
        # Check endpoint-specific authorization
        for endpoint in request.endpoints:
            if endpoint.get("authorization", "").lower() in ["none", "bearer_only", ""]:
                vulnerabilities.append({
                    "id": str(uuid.uuid4()),
                    "name": f"Weak Authorization - {endpoint.get('path', 'Unknown')}",
                    "description": f"Endpoint {endpoint.get('path')} lacks proper authorization controls",
                    "severity": "High",
                    "category": "Broken Access Control", 
                    "owasp_category": "API1:2023 – Broken Object Level Authorization",
                    "mitre_techniques": ["T1078"],
                    "risk_score": 7.5,
                    "remediation_steps": [
                        f"Add object-level authorization to {endpoint.get('path')}",
                        "Validate user can access specific object IDs",
                        "Implement context-aware authorization logic"
                    ]
                })
        
        return {
            "analysis_type": "API1:2023 - Broken Object Level Authorization",
            "vulnerabilities": vulnerabilities,
            "total_count": len(vulnerabilities),
            "risk_assessment": {
                "overall_risk": "Critical" if any(v["severity"] == "Critical" for v in vulnerabilities) else "High",
                "impact": "Unauthorized access to sensitive objects and data"
            }
        }
        
    except Exception as e:
        logger.error(f"Error in API1:2023 analysis: {e}")
        raise HTTPException(status_code=500, detail=f"API1:2023 analysis failed: {str(e)}")

@api_router.post("/vulnerabilities/analyze/api3-2023")
async def analyze_api3_2023_broken_property_authorization(request: EnhancedVulnerabilityRequest):
    """API3:2023 - Broken Object Property Level Authorization detection"""
    try:
        vulnerabilities = []
        security_config = request.security_config
        
        # Check for excessive data exposure
        data_sanitization = security_config.get("data_sanitization", "").lower()
        field_level_controls = security_config.get("field_level_authorization", False)
        
        if data_sanitization in ["no sanitization", "basic sanitization", ""] or not field_level_controls:
            vulnerabilities.append({
                "id": str(uuid.uuid4()),
                "name": "Excessive Data Exposure",
                "description": "API responses contain more data than necessary, potentially exposing sensitive information",
                "severity": "Medium",
                "category": "Information Disclosure",
                "owasp_category": "API3:2023 – Broken Object Property Level Authorization",
                "mitre_techniques": ["T1213", "T1005"],
                "risk_score": 6.5,
                "remediation_steps": [
                    "Implement response filtering to only return necessary fields",
                    "Use Data Transfer Objects (DTOs) for API responses",
                    "Apply data minimization principles",
                    "Add field-level access controls"
                ],
                "trigger_context": {
                    "data_sanitization": data_sanitization,
                    "field_level_authorization": field_level_controls
                }
            })
        
        # Check for mass assignment vulnerabilities
        input_validation = security_config.get("input_validation", "").lower()
        if "mass assignment" in input_validation or input_validation in ["no validation", ""]:
            vulnerabilities.append({
                "id": str(uuid.uuid4()),
                "name": "Mass Assignment Vulnerability",
                "description": "API allows modification of object properties that should be restricted",
                "severity": "High",
                "category": "Broken Access Control",
                "owasp_category": "API3:2023 – Broken Object Property Level Authorization",
                "mitre_techniques": ["T1078", "T1055"],
                "risk_score": 7.0,
                "remediation_steps": [
                    "Implement allowlists for updatable fields",
                    "Validate input against expected schema",
                    "Use separate DTOs for input and output",
                    "Add property-level authorization checks"
                ]
            })
        
        return {
            "analysis_type": "API3:2023 - Broken Object Property Level Authorization",
            "vulnerabilities": vulnerabilities,
            "total_count": len(vulnerabilities),
            "risk_assessment": {
                "overall_risk": "High" if any(v["severity"] == "High" for v in vulnerabilities) else "Medium",
                "impact": "Unauthorized access to sensitive object properties"
            }
        }
        
    except Exception as e:
        logger.error(f"Error in API3:2023 analysis: {e}")
        raise HTTPException(status_code=500, detail=f"API3:2023 analysis failed: {str(e)}")

@api_router.post("/vulnerabilities/analyze/api4-2023")
async def analyze_api4_2023_resource_consumption(request: EnhancedVulnerabilityRequest):
    """API4:2023 - Unrestricted Resource Consumption detection"""
    try:
        vulnerabilities = []
        security_config = request.security_config
        
        # Check for rate limiting
        rate_limiting = security_config.get("rate_limiting", "").lower()
        if rate_limiting in ["none", "no rate limiting", ""]:
            vulnerabilities.append({
                "id": str(uuid.uuid4()),
                "name": "No Rate Limiting",
                "description": "API lacks rate limiting controls, vulnerable to resource exhaustion attacks",
                "severity": "Medium",
                "category": "Denial of Service",
                "owasp_category": "API4:2023 – Unrestricted Resource Consumption",
                "mitre_techniques": ["T1499", "T1498"],
                "risk_score": 6.0,
                "remediation_steps": [
                    "Implement comprehensive rate limiting per user/IP",
                    "Add request size and payload limits",
                    "Configure timeout controls for long operations",
                    "Monitor resource consumption patterns"
                ]
            })
        
        # Check for pagination limits
        pagination = security_config.get("pagination_security", "").lower()
        if pagination in ["no pagination", "no pagination limits", ""]:
            vulnerabilities.append({
                "id": str(uuid.uuid4()),
                "name": "Unlimited Data Retrieval",
                "description": "API allows unlimited data retrieval without pagination controls",
                "severity": "Medium", 
                "category": "Denial of Service",
                "owasp_category": "API4:2023 – Unrestricted Resource Consumption",
                "mitre_techniques": ["T1499"],
                "risk_score": 5.5,
                "remediation_steps": [
                    "Implement mandatory pagination with reasonable limits",
                    "Add maximum result set size controls",
                    "Use cursor-based pagination for large datasets",
                    "Monitor and alert on excessive data requests"
                ]
            })
        
        return {
            "analysis_type": "API4:2023 - Unrestricted Resource Consumption",
            "vulnerabilities": vulnerabilities,
            "total_count": len(vulnerabilities),
            "risk_assessment": {
                "overall_risk": "Medium",
                "impact": "Resource exhaustion and denial of service"
            }
        }
        
    except Exception as e:
        logger.error(f"Error in API4:2023 analysis: {e}")
        raise HTTPException(status_code=500, detail=f"API4:2023 analysis failed: {str(e)}")

@api_router.post("/vulnerabilities/analyze/api6-2023")
async def analyze_api6_2023_sensitive_business_flows(request: EnhancedVulnerabilityRequest):
    """API6:2023 - Unrestricted Access to Sensitive Business Flows detection"""
    try:
        vulnerabilities = []
        security_config = request.security_config
        
        # Check business flow protection
        business_flow_protection = security_config.get("business_flow_protection", False)
        automated_threat_detection = security_config.get("automated_threat_detection", False)
        
        if not business_flow_protection or not automated_threat_detection:
            vulnerabilities.append({
                "id": str(uuid.uuid4()),
                "name": "Unprotected Sensitive Business Flows",
                "description": "Sensitive business operations lack protection against automation and abuse",
                "severity": "High",
                "category": "Business Logic Vulnerabilities",
                "owasp_category": "API6:2023 – Unrestricted Access to Sensitive Business Flows",
                "mitre_techniques": ["T1499", "T1078"],
                "risk_score": 7.5,
                "remediation_steps": [
                    "Implement business logic rate limiting",
                    "Add CAPTCHA or challenge-response for sensitive operations",
                    "Monitor for automation patterns and bot behavior",
                    "Implement user behavior analytics"
                ]
            })
        
        # Check specific business flows
        for flow in request.business_flows:
            flow_name = flow.get("name", "Unknown")
            protection = flow.get("protection", "").lower()
            rate_limit = flow.get("rate_limit")
            
            if protection in ["none", ""] or rate_limit is None:
                severity = "High" if flow_name in ["password_reset", "account_creation", "payment_processing"] else "Medium"
                vulnerabilities.append({
                    "id": str(uuid.uuid4()),
                    "name": f"Unprotected Business Flow - {flow_name}",
                    "description": f"Business flow '{flow_name}' lacks adequate protection controls",
                    "severity": severity,
                    "category": "Business Logic Vulnerabilities",
                    "owasp_category": "API6:2023 – Unrestricted Access to Sensitive Business Flows",
                    "mitre_techniques": ["T1499", "T1078"],
                    "risk_score": 7.0 if severity == "High" else 5.5,
                    "remediation_steps": [
                        f"Add rate limiting to {flow_name} workflow",
                        "Implement anti-automation controls",
                        "Add behavioral monitoring",
                        "Configure abuse detection alerts"
                    ]
                })
        
        return {
            "analysis_type": "API6:2023 - Unrestricted Access to Sensitive Business Flows",
            "vulnerabilities": vulnerabilities,
            "total_count": len(vulnerabilities),
            "risk_assessment": {
                "overall_risk": "High" if any(v["severity"] == "High" for v in vulnerabilities) else "Medium",
                "impact": "Business process abuse and financial/reputational damage"
            }
        }
        
    except Exception as e:
        logger.error(f"Error in API6:2023 analysis: {e}")
        raise HTTPException(status_code=500, detail=f"API6:2023 analysis failed: {str(e)}")

@api_router.post("/vulnerabilities/analyze/api7-2023")
async def analyze_api7_2023_server_side_request_forgery(request: EnhancedVulnerabilityRequest):
    """API7:2023 - Server-Side Request Forgery detection"""
    try:
        vulnerabilities = []
        security_config = request.security_config
        
        # Check for SSRF protections
        url_validation = security_config.get("url_validation", "").lower()
        allowlist_implementation = security_config.get("external_request_allowlist", False)
        network_segmentation = security_config.get("network_segmentation", False)
        
        if url_validation in ["no validation", "basic validation", ""] or not allowlist_implementation:
            vulnerabilities.append({
                "id": str(uuid.uuid4()),
                "name": "Server-Side Request Forgery",
                "description": "API can be manipulated to make unauthorized requests to internal or external systems",
                "severity": "High",
                "category": "Server-Side Request Forgery",
                "owasp_category": "API7:2023 – Server-Side Request Forgery",
                "mitre_techniques": ["T1190", "T1071"],
                "risk_score": 8.0,
                "remediation_steps": [
                    "Validate and sanitize all user-supplied URLs",
                    "Implement strict allowlist for external requests",
                    "Use network segmentation to limit internal access",
                    "Disable unused URL schemas (file://, ftp://, etc.)"
                ],
                "trigger_context": {
                    "url_validation": url_validation,
                    "allowlist_implementation": allowlist_implementation,
                    "network_segmentation": network_segmentation
                }
            })
        
        # Check input validation for URLs
        input_validation = security_config.get("input_validation", "").lower()
        if input_validation in ["no validation", "client-side only", ""]:
            vulnerabilities.append({
                "id": str(uuid.uuid4()),
                "name": "Insufficient Input Validation for URLs",
                "description": "Inadequate validation of URL inputs enables SSRF attacks",
                "severity": "Medium",
                "category": "Injection",
                "owasp_category": "API7:2023 – Server-Side Request Forgery",
                "mitre_techniques": ["T1190"],
                "risk_score": 6.5,
                "remediation_steps": [
                    "Implement comprehensive URL validation",
                    "Use regular expressions to validate URL patterns",
                    "Check URL schemes and domains against allowlist",
                    "Sanitize URL parameters"
                ]
            })
        
        return {
            "analysis_type": "API7:2023 - Server-Side Request Forgery",
            "vulnerabilities": vulnerabilities,
            "total_count": len(vulnerabilities),
            "risk_assessment": {
                "overall_risk": "High" if any(v["severity"] == "High" for v in vulnerabilities) else "Medium",
                "impact": "Unauthorized access to internal systems and data exfiltration"
            }
        }
        
    except Exception as e:
        logger.error(f"Error in API7:2023 analysis: {e}")
        raise HTTPException(status_code=500, detail=f"API7:2023 analysis failed: {str(e)}")

@api_router.post("/vulnerabilities/analyze/api9-2023")
async def analyze_api9_2023_improper_inventory_management(request: EnhancedVulnerabilityRequest):
    """API9:2023 - Improper Inventory Management detection"""
    try:
        vulnerabilities = []
        security_config = request.security_config
        
        # Check API documentation and inventory
        documentation = security_config.get("documentation_security", "").lower()
        version_management = security_config.get("version_management", "").lower()
        api_discovery = security_config.get("api_discovery_controls", False)
        
        if documentation in ["no documentation", "public detailed docs", ""]:
            severity = "Medium" if documentation == "public detailed docs" else "Low"
            vulnerabilities.append({
                "id": str(uuid.uuid4()),
                "name": "Poor API Documentation Security",
                "description": "API documentation practices create security risks through information disclosure",
                "severity": severity,
                "category": "Information Disclosure",
                "owasp_category": "API9:2023 – Improper Inventory Management",
                "mitre_techniques": ["T1190", "T1213"],
                "risk_score": 5.0 if severity == "Medium" else 3.0,
                "remediation_steps": [
                    "Review and sanitize public API documentation",
                    "Remove sensitive internal details from public docs",
                    "Implement separate documentation for internal/external use",
                    "Regular documentation security reviews"
                ]
            })
        
        if version_management in ["no version management", "poor versioning", ""]:
            vulnerabilities.append({
                "id": str(uuid.uuid4()),
                "name": "Poor API Version Management",
                "description": "Inadequate API version management creates security blind spots",
                "severity": "Low",
                "category": "Security Misconfiguration",
                "owasp_category": "API9:2023 – Improper Inventory Management",
                "mitre_techniques": ["T1190"],
                "risk_score": 4.0,
                "remediation_steps": [
                    "Implement comprehensive API versioning strategy",
                    "Maintain inventory of all API versions",
                    "Plan deprecation timeline for old versions",
                    "Monitor usage of deprecated endpoints"
                ]
            })
        
        if not api_discovery:
            vulnerabilities.append({
                "id": str(uuid.uuid4()),
                "name": "Lack of API Discovery Controls",
                "description": "Missing API discovery and inventory management capabilities",
                "severity": "Low",
                "category": "Security Misconfiguration",
                "owasp_category": "API9:2023 – Improper Inventory Management",
                "mitre_techniques": ["T1190"],
                "risk_score": 4.5,
                "remediation_steps": [
                    "Implement automated API discovery tools",
                    "Maintain real-time API inventory",
                    "Monitor for shadow or undocumented APIs",
                    "Regular API security assessments"
                ]
            })
        
        return {
            "analysis_type": "API9:2023 - Improper Inventory Management",
            "vulnerabilities": vulnerabilities,
            "total_count": len(vulnerabilities),
            "risk_assessment": {
                "overall_risk": "Medium" if any(v["severity"] == "Medium" for v in vulnerabilities) else "Low",
                "impact": "Security blind spots and increased attack surface"
            }
        }
        
    except Exception as e:
        logger.error(f"Error in API9:2023 analysis: {e}")
        raise HTTPException(status_code=500, detail=f"API9:2023 analysis failed: {str(e)}")

# =============================================================================
# ENHANCED DATABASE SECURITY ENDPOINTS
# =============================================================================

@api_router.post("/vulnerabilities/analyze/privilege-escalation")
async def analyze_privilege_escalation(request: EnhancedVulnerabilityRequest):
    """Enhanced Database Security - Privilege Escalation detection"""
    try:
        vulnerabilities = []
        security_config = request.security_config
        
        # Check privilege management
        privilege_mgmt = security_config.get("privilege_management", "").lower()
        if privilege_mgmt in ["static user privileges", "excessive privileges", ""]:
            vulnerabilities.append({
                "id": str(uuid.uuid4()),
                "name": "Database Privilege Escalation Risk",
                "description": "Database configuration allows potential privilege escalation beyond intended access levels",
                "severity": "High",
                "category": "Broken Access Control",
                "owasp_category": "A01:2023 – Broken Access Control",
                "mitre_techniques": ["T1068", "T1078"],
                "risk_score": 7.5,
                "remediation_steps": [
                    "Implement dynamic privilege management system",
                    "Apply principle of least privilege strictly",
                    "Conduct regular privilege audits and reviews",
                    "Monitor and alert on privilege changes"
                ]
            })
        
        # Check for shared accounts
        access_control = security_config.get("access_control", "").lower()
        if "shared accounts" in access_control:
            vulnerabilities.append({
                "id": str(uuid.uuid4()),
                "name": "Shared Database Accounts",
                "description": "Use of shared database accounts increases privilege escalation risk",
                "severity": "Medium",
                "category": "Identification and Authentication Failures",
                "owasp_category": "A07:2023 – Identification and Authentication Failures",
                "mitre_techniques": ["T1078"],
                "risk_score": 6.0,
                "remediation_steps": [
                    "Replace shared accounts with individual user accounts",
                    "Implement proper user authentication and authorization",
                    "Add account activity monitoring",
                    "Establish account lifecycle management"
                ]
            })
        
        return {
            "analysis_type": "Enhanced Database Security - Privilege Escalation",
            "vulnerabilities": vulnerabilities,
            "total_count": len(vulnerabilities),
            "risk_assessment": {
                "overall_risk": "High" if any(v["severity"] == "High" for v in vulnerabilities) else "Medium",
                "impact": "Unauthorized database access and data manipulation"
            }
        }
        
    except Exception as e:
        logger.error(f"Error in privilege escalation analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Privilege escalation analysis failed: {str(e)}")

@api_router.post("/vulnerabilities/analyze/config-drift")
async def analyze_config_drift(request: EnhancedVulnerabilityRequest):
    """Enhanced Database Security - Configuration Drift detection"""
    try:
        vulnerabilities = []
        security_config = request.security_config
        
        # Check change management
        change_mgmt = security_config.get("change_management", "").lower()
        if change_mgmt in ["no change management", "manual change tracking", ""]:
            vulnerabilities.append({
                "id": str(uuid.uuid4()),
                "name": "Database Configuration Drift",
                "description": "Database security configuration may have drifted from established security baseline",
                "severity": "Medium",
                "category": "Security Misconfiguration",
                "owasp_category": "A05:2023 – Security Misconfiguration",
                "mitre_techniques": ["T1190", "T1212"],
                "risk_score": 6.0,
                "remediation_steps": [
                    "Implement automated configuration management",
                    "Establish regular configuration baseline audits",
                    "Deploy automated compliance checking tools",
                    "Set up configuration drift detection and alerts"
                ]
            })
        
        # Check configuration monitoring
        config_monitoring = security_config.get("configuration_monitoring", False)
        if not config_monitoring:
            vulnerabilities.append({
                "id": str(uuid.uuid4()),
                "name": "No Configuration Monitoring",
                "description": "Lack of configuration monitoring prevents detection of security drift",
                "severity": "Medium",
                "category": "Security Logging and Monitoring Failures",
                "owasp_category": "A09:2023 – Security Logging and Monitoring Failures",
                "mitre_techniques": ["T1562", "T1070"],
                "risk_score": 5.5,
                "remediation_steps": [
                    "Implement continuous configuration monitoring",
                    "Set up automated alerts for configuration changes",
                    "Establish configuration change approval workflows",
                    "Regular configuration security assessments"
                ]
            })
        
        return {
            "analysis_type": "Enhanced Database Security - Configuration Drift",
            "vulnerabilities": vulnerabilities,
            "total_count": len(vulnerabilities),
            "risk_assessment": {
                "overall_risk": "Medium",
                "impact": "Security control degradation and compliance violations"
            }
        }
        
    except Exception as e:
        logger.error(f"Error in config drift analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Configuration drift analysis failed: {str(e)}")

@api_router.post("/vulnerabilities/analyze/advanced-injection")
async def analyze_advanced_injection(request: EnhancedVulnerabilityRequest):
    """Enhanced Database Security - Advanced Injection detection"""
    try:
        vulnerabilities = []
        security_config = request.security_config
        
        # Check stored procedure security
        stored_proc_security = security_config.get("stored_procedure_security", "").lower()
        if stored_proc_security in ["no security measures", "basic implementation", ""]:
            vulnerabilities.append({
                "id": str(uuid.uuid4()),
                "name": "Advanced Database Injection Vulnerability",
                "description": "Database vulnerable to NoSQL injection, LDAP injection, or command injection through stored procedures",
                "severity": "Critical",
                "category": "Injection",
                "owasp_category": "A03:2023 – Injection",
                "mitre_techniques": ["T1190", "T1059"],
                "risk_score": 8.5,
                "remediation_steps": [
                    "Implement comprehensive input validation for all database types",
                    "Use parameterized queries for SQL, NoSQL, and LDAP operations",
                    "Apply principle of least privilege for database access",
                    "Conduct regular security code reviews of database procedures"
                ]
            })
        
        # Check query parameterization
        query_parameterization = security_config.get("query_parameterization", "").lower()
        if query_parameterization in ["dynamic queries", "string concatenation", ""]:
            vulnerabilities.append({
                "id": str(uuid.uuid4()),
                "name": "Dynamic Query Construction",
                "description": "Use of dynamic query construction enables advanced injection attacks",
                "severity": "High",
                "category": "Injection",
                "owasp_category": "A03:2023 – Injection",
                "mitre_techniques": ["T1190"],
                "risk_score": 7.0,
                "remediation_steps": [
                    "Replace dynamic queries with parameterized queries",
                    "Implement input validation and sanitization",
                    "Use ORM frameworks with built-in protection",
                    "Regular security testing of database interactions"
                ]
            })
        
        return {
            "analysis_type": "Enhanced Database Security - Advanced Injection",
            "vulnerabilities": vulnerabilities,
            "total_count": len(vulnerabilities),
            "risk_assessment": {
                "overall_risk": "Critical" if any(v["severity"] == "Critical" for v in vulnerabilities) else "High",
                "impact": "Database compromise and data exfiltration"
            }
        }
        
    except Exception as e:
        logger.error(f"Error in advanced injection analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Advanced injection analysis failed: {str(e)}")

@api_router.post("/vulnerabilities/analyze/insider-threat")
async def analyze_insider_threat(request: EnhancedVulnerabilityRequest):
    """Enhanced Database Security - Insider Threat detection"""
    try:
        vulnerabilities = []
        security_config = request.security_config
        
        # Check user activity monitoring
        activity_monitoring = security_config.get("user_activity_monitoring", "").lower()
        if activity_monitoring in ["no activity monitoring", "basic user tracking", ""]:
            vulnerabilities.append({
                "id": str(uuid.uuid4()),
                "name": "Database Insider Threat Risk",
                "description": "Database lacks sufficient monitoring to detect malicious insider activities",
                "severity": "Medium",
                "category": "Security Logging and Monitoring Failures",
                "owasp_category": "A09:2023 – Security Logging and Monitoring Failures",
                "mitre_techniques": ["T1078", "T1213"],
                "risk_score": 6.5,
                "remediation_steps": [
                    "Implement user behavior analytics for database access",
                    "Add comprehensive privileged access monitoring",
                    "Establish regular access reviews and recertification",
                    "Deploy data loss prevention (DLP) solutions"
                ]
            })
        
        # Check privileged access controls
        privileged_access = security_config.get("privileged_access_management", False)
        if not privileged_access:
            vulnerabilities.append({
                "id": str(uuid.uuid4()),
                "name": "Insufficient Privileged Access Controls",
                "description": "Lack of privileged access management increases insider threat risk",
                "severity": "Medium",
                "category": "Broken Access Control",
                "owasp_category": "A01:2023 – Broken Access Control",
                "mitre_techniques": ["T1078"],
                "risk_score": 6.0,
                "remediation_steps": [
                    "Implement privileged access management (PAM) solution",
                    "Add session recording for privileged database access",
                    "Establish approval workflows for sensitive operations",
                    "Monitor and alert on unusual privileged activities"
                ]
            })
        
        return {
            "analysis_type": "Enhanced Database Security - Insider Threat",
            "vulnerabilities": vulnerabilities,
            "total_count": len(vulnerabilities),
            "risk_assessment": {
                "overall_risk": "Medium",
                "impact": "Data theft and unauthorized database modifications by insiders"
            }
        }
        
    except Exception as e:
        logger.error(f"Error in insider threat analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Insider threat analysis failed: {str(e)}")

@api_router.post("/vulnerabilities/analyze/backup-security")
async def analyze_backup_security(request: EnhancedVulnerabilityRequest):
    """Enhanced Database Security - Backup Security detection"""
    try:
        vulnerabilities = []
        security_config = request.security_config
        
        # Check backup encryption
        backup_encryption = security_config.get("backup_encryption", "").lower()
        if backup_encryption in ["unencrypted backups", ""]:
            vulnerabilities.append({
                "id": str(uuid.uuid4()),
                "name": "Unencrypted Database Backups",
                "description": "Database backups are not properly encrypted and could be compromised",
                "severity": "High",
                "category": "Cryptographic Failures",
                "owasp_category": "A02:2023 – Cryptographic Failures",
                "mitre_techniques": ["T1005", "T1213"],
                "risk_score": 7.0,
                "remediation_steps": [
                    "Enable encryption for all database backups",
                    "Implement secure backup storage with access controls",
                    "Regular backup integrity testing and validation",
                    "Establish secure key management for backup encryption"
                ]
            })
        
        # Check backup access controls
        backup_access = security_config.get("backup_access_controls", False)
        if not backup_access:
            vulnerabilities.append({
                "id": str(uuid.uuid4()),
                "name": "Insufficient Backup Access Controls",
                "description": "Database backup files lack adequate access controls",
                "severity": "Medium",
                "category": "Broken Access Control",
                "owasp_category": "A01:2023 – Broken Access Control",
                "mitre_techniques": ["T1005"],
                "risk_score": 6.0,
                "remediation_steps": [
                    "Implement strict access controls for backup files",
                    "Use separate credentials for backup access",
                    "Monitor and log backup file access",
                    "Regular access review for backup systems"
                ]
            })
        
        # Check backup testing
        backup_testing = security_config.get("backup_restoration_testing", "").lower()
        if backup_testing in ["no testing", "irregular testing", ""]:
            vulnerabilities.append({
                "id": str(uuid.uuid4()),
                "name": "Untested Backup Recovery",
                "description": "Database backup recovery procedures are not regularly tested",
                "severity": "Medium",
                "category": "Software and Data Integrity Failures",
                "owasp_category": "A08:2023 – Software and Data Integrity Failures",
                "mitre_techniques": ["T1485"],
                "risk_score": 5.5,
                "remediation_steps": [
                    "Establish regular backup restoration testing schedule",
                    "Validate backup integrity and completeness",
                    "Test recovery procedures in isolated environment",
                    "Document and automate recovery processes"
                ]
            })
        
        return {
            "analysis_type": "Enhanced Database Security - Backup Security",
            "vulnerabilities": vulnerabilities,
            "total_count": len(vulnerabilities),
            "risk_assessment": {
                "overall_risk": "High" if any(v["severity"] == "High" for v in vulnerabilities) else "Medium",
                "impact": "Data loss and exposure through compromised backups"
            }
        }
        
    except Exception as e:
        logger.error(f"Error in backup security analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Backup security analysis failed: {str(e)}")

# Duplicate ProductDesignSecurity route removed - now positioned before generic route

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()