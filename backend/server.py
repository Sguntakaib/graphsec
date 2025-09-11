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