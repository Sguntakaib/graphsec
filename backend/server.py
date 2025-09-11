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

# Import advanced simulation modules
from advanced_simulation import AdvancedSimulationEngine
from mitre_integration import MitreAttackDatabase
from intelligent_nodes import intelligent_node_engine, SecurityBranch, SecurityPrompt, IntelligentNodeTemplate
from dsl_rule_engine import dsl_rule_engine, RuleEvaluationResult, SecurityGap, CompletenessAnalysis

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