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
@api_router.post("/diagrams/{diagram_id}/simulate", response_model=SimulationResult)
async def simulate_attack_paths(diagram_id: str):
    diagram = await db.diagrams.find_one({"id": diagram_id})
    if not diagram:
        raise HTTPException(status_code=404, detail="Diagram not found")
    
    # Basic simulation logic
    nodes = diagram.get("nodes", [])
    edges = diagram.get("edges", [])
    
    # Find attack paths (simplified)
    attack_paths = []
    recommendations = []
    mitre_techniques = []
    
    # Look for common attack patterns
    actors = [n for n in nodes if n.get("type") == "Actor"]
    surfaces = [n for n in nodes if n.get("type") == "Surface"]
    assets = [n for n in nodes if n.get("type") == "Asset"]
    controls = [n for n in nodes if n.get("type") == "Control"]
    
    # Generate attack paths from actors through surfaces to assets
    for actor in actors:
        for surface in surfaces:
            for asset in assets:
                # Check if there's a path from actor -> surface -> asset
                actor_to_surface = any(e.get("source") == actor["id"] and e.get("target") == surface["id"] for e in edges)
                surface_to_asset = any(e.get("source") == surface["id"] and e.get("target") == asset["id"] for e in edges)
                
                if actor_to_surface and surface_to_asset:
                    path = {
                        "steps": [
                            {"node": actor["label"], "action": "initiates attack"},
                            {"node": surface["label"], "action": f"exploits {surface['subtype']}"},
                            {"node": asset["label"], "action": "compromises asset"}
                        ],
                        "likelihood": "Medium",
                        "impact": "High" if asset["subtype"] in ["Database", "S3Bucket"] else "Medium"
                    }
                    attack_paths.append(path)
                    
                    # Add MITRE techniques based on surface type
                    if surface["subtype"] == "SSRF":
                        mitre_techniques.extend(["T1190", "T1552.001"])
                    elif surface["subtype"] == "SQLi":
                        mitre_techniques.extend(["T1190", "T1213"])
                    elif surface["subtype"] == "WeakIAM":
                        mitre_techniques.extend(["T1078", "T1484"])
    
    # Generate recommendations based on missing controls
    control_types = {c["subtype"] for c in controls}
    if not any("WAF" in ct for ct in control_types) and surfaces:
        recommendations.append("Deploy Web Application Firewall (WAF) to protect against common web attacks")
    if not any("EDR" in ct for ct in control_types) and assets:
        recommendations.append("Implement Endpoint Detection and Response (EDR) for asset monitoring")
    if not any("EgressProxy" in ct for ct in control_types):
        recommendations.append("Configure egress proxy to control outbound connections")
    
    # Calculate risk score
    risk_score = min(len(attack_paths) * 2.5, 10.0)
    
    simulation = SimulationResult(
        diagram_id=diagram_id,
        attack_paths=attack_paths,
        recommendations=recommendations,
        mitre_techniques=list(set(mitre_techniques)),
        risk_score=risk_score
    )
    
    # Save simulation result
    simulation_dict = prepare_for_mongo(simulation.dict())
    await db.simulations.insert_one(simulation_dict)
    
    return simulation

@api_router.get("/diagrams/{diagram_id}/simulations", response_model=List[SimulationResult])
async def get_simulations(diagram_id: str):
    simulations = await db.simulations.find({"diagram_id": diagram_id}).to_list(1000)
    return [SimulationResult(**parse_from_mongo(sim)) for sim in simulations]

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