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

@api_router.post("/diagrams/{diagram_id}/auto-layout")
async def auto_layout_diagram(diagram_id: str):
    """Generate automatic layout for diagram nodes"""
    diagram = await db.diagrams.find_one({"id": diagram_id})
    if not diagram:
        raise HTTPException(status_code=404, detail="Diagram not found")
    
    nodes = diagram.get("nodes", [])
    edges = diagram.get("edges", [])
    
    # Simple hierarchical layout algorithm
    layout_positions = {}
    
    # Group nodes by type
    node_groups = {}
    for node in nodes:
        node_type = node.get("type", "Unknown")
        if node_type not in node_groups:
            node_groups[node_type] = []
        node_groups[node_type].append(node)
    
    # Position groups in layers
    y_offset = 0
    layer_height = 150
    node_spacing = 200
    
    for node_type, type_nodes in node_groups.items():
        x_offset = 0
        for i, node in enumerate(type_nodes):
            layout_positions[node["id"]] = {
                "x": x_offset,
                "y": y_offset
            }
            x_offset += node_spacing
        y_offset += layer_height
    
    return {
        "layout_positions": layout_positions,
        "algorithm": "hierarchical",
        "node_count": len(nodes),
        "group_count": len(node_groups)
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