from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, BeforeValidator, PlainSerializer
from typing import List, Dict, Any, Optional, Annotated
import uuid
from datetime import datetime, timezone
from enum import Enum
import asyncio
from concurrent.futures import ThreadPoolExecutor
import networkx as nx
import math
from bson import ObjectId

# Fix ObjectId serialization for Pydantic v2
def check_object_id(value: ObjectId | str | None) -> ObjectId | None:
    if value is None:
        return None
    if isinstance(value, ObjectId):
        return value
    if isinstance(value, str) and ObjectId.is_valid(value):
        return ObjectId(value)
    raise ValueError("Invalid ObjectId format")

PyObjectId = Annotated[
    ObjectId | None,
    BeforeValidator(check_object_id),
    PlainSerializer(func=lambda x: None if x is None else str(x), return_type=str | None),
]

# Import advanced simulation modules
from advanced_simulation import AdvancedSimulationEngine
from mitre_integration import MitreAttackDatabase
from intelligent_nodes import intelligent_node_engine, SecurityBranch, SecurityPrompt, IntelligentNodeTemplate
from dsl_rule_engine import dsl_rule_engine, RuleEvaluationResult, SecurityGap, CompletenessAnalysis
from probabilistic_simulation import probabilistic_engine, ProbabilisticAttackPath, ScenarioAnalysis, DefenseEffectivenessModel

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