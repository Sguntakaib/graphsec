"""
Findings Management System for Security Modeling Platform

This module handles the creation, persistence, and management of security findings
generated from questionnaire completions, rule evaluations, and simulations.
"""

import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)

class FindingSeverity(str, Enum):
    """Enumeration for finding severity levels"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class FindingStatus(str, Enum):
    """Enumeration for finding status"""
    NEW = "New"
    IN_PROGRESS = "InProgress"
    RESOLVED = "Resolved"
    ACCEPTED = "Accepted"
    FALSE_POSITIVE = "FalsePositive"

class FindingSource(str, Enum):
    """Enumeration for finding sources"""
    QUESTIONNAIRE = "Questionnaire"
    RULE_ENGINE = "RuleEngine"
    SIMULATION = "Simulation"
    MANUAL = "Manual"
    AUTOMATED_SCAN = "AutomatedScan"

class SecurityFramework(str, Enum):
    """Supported security frameworks"""
    MITRE_ATTACK = "MITRE_ATT&CK"
    ASVS = "ASVS"
    OWASP = "OWASP"
    CIS = "CIS"
    NIST_CSF = "NIST_CSF"
    ISO27001 = "ISO27001"
    SOC2 = "SOC2"
    GDPR = "GDPR"

class Finding(BaseModel):
    """Core Finding model representing a security issue or recommendation"""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    diagram_id: str = Field(..., description="ID of the diagram this finding belongs to")
    node_id: Optional[str] = Field(None, description="ID of the specific node related to this finding")
    rule_id: Optional[str] = Field(None, description="ID of the rule that generated this finding")
    
    # Core finding details
    title: str = Field(..., description="Brief title of the finding")
    description: str = Field(..., description="Detailed description of the finding")
    severity: FindingSeverity = Field(..., description="Severity level of the finding")
    risk_score: float = Field(..., ge=0.0, le=10.0, description="Risk score from 0-10")
    
    # Source and categorization
    source: FindingSource = Field(..., description="Source that generated this finding")
    category: str = Field(..., description="Security category (e.g., Authentication, Authorization)")
    subcategory: Optional[str] = Field(None, description="Specific subcategory")
    
    # Evidence and context
    evidence: Dict[str, Any] = Field(default_factory=dict, description="Supporting evidence and data")
    affected_components: List[str] = Field(default_factory=list, description="List of affected system components")
    
    # Framework mappings
    framework_tags: List[str] = Field(default_factory=list, description="Mapping to security frameworks")
    mitre_techniques: List[str] = Field(default_factory=list, description="Related MITRE ATT&CK techniques")
    compliance_standards: List[str] = Field(default_factory=list, description="Related compliance standards")
    
    # Recommendations and remediation
    recommendations: List[str] = Field(default_factory=list, description="Recommended actions to address finding")
    remediation_effort: Optional[str] = Field(None, description="Estimated effort to remediate (Low/Medium/High)")
    remediation_priority: Optional[int] = Field(None, ge=1, le=5, description="Priority ranking 1-5")
    
    # Status and tracking
    status: FindingStatus = Field(default=FindingStatus.NEW, description="Current status of the finding")
    assigned_to: Optional[str] = Field(None, description="Person assigned to address this finding")
    due_date: Optional[datetime] = Field(None, description="Due date for remediation")
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str] = Field(None, description="User who created this finding")
    updated_by: Optional[str] = Field(None, description="User who last updated this finding")
    
    # Additional context
    business_impact: Optional[str] = Field(None, description="Description of business impact")
    technical_impact: Optional[str] = Field(None, description="Description of technical impact")
    exploitability: Optional[float] = Field(None, ge=0.0, le=10.0, description="Exploitability score 0-10")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class FindingsSummary(BaseModel):
    """Summary statistics for findings"""
    total_findings: int = 0
    by_severity: Dict[FindingSeverity, int] = Field(default_factory=dict)
    by_status: Dict[FindingStatus, int] = Field(default_factory=dict)
    by_category: Dict[str, int] = Field(default_factory=dict)
    average_risk_score: float = 0.0
    highest_risk_score: float = 0.0
    critical_findings_count: int = 0
    high_findings_count: int = 0
    overdue_findings_count: int = 0

class FindingsFilter(BaseModel):
    """Filter criteria for finding queries"""
    diagram_id: Optional[str] = None
    node_id: Optional[str] = None
    severity: Optional[List[FindingSeverity]] = None
    status: Optional[List[FindingStatus]] = None
    source: Optional[List[FindingSource]] = None
    category: Optional[List[str]] = None
    assigned_to: Optional[str] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    min_risk_score: Optional[float] = None
    max_risk_score: Optional[float] = None
    framework_tags: Optional[List[str]] = None

class FindingsManager:
    """Manager class for handling all findings operations"""
    
    def __init__(self, db):
        self.db = db
        self.collection_name = "findings"
        self.collection = db[self.collection_name]
        logger.info("FindingsManager initialized")
    
    async def create_finding(self, finding: Finding) -> Finding:
        """Create a new finding in the database"""
        try:
            # Set timestamps
            finding.created_at = datetime.now(timezone.utc)
            finding.updated_at = finding.created_at
            
            # Convert to dict and insert
            finding_dict = finding.dict()
            result = await self.collection.insert_one(finding_dict)
            
            if result.inserted_id:
                logger.info(f"Created finding {finding.id} for diagram {finding.diagram_id}")
                return finding
            else:
                raise Exception("Failed to insert finding into database")
                
        except Exception as e:
            logger.error(f"Error creating finding: {e}")
            raise
    
    async def get_finding(self, finding_id: str) -> Optional[Finding]:
        """Retrieve a single finding by ID"""
        try:
            finding_data = await self.collection.find_one({"id": finding_id})
            if finding_data:
                # Remove MongoDB _id field
                finding_data.pop("_id", None)
                return Finding(**finding_data)
            return None
        except Exception as e:
            logger.error(f"Error retrieving finding {finding_id}: {e}")
            raise
    
    async def update_finding(self, finding_id: str, updates: Dict[str, Any]) -> Optional[Finding]:
        """Update an existing finding"""
        try:
            # Add updated timestamp
            updates["updated_at"] = datetime.now(timezone.utc)
            
            result = await self.collection.update_one(
                {"id": finding_id},
                {"$set": updates}
            )
            
            if result.matched_count > 0:
                logger.info(f"Updated finding {finding_id}")
                return await self.get_finding(finding_id)
            else:
                logger.warning(f"Finding {finding_id} not found for update")
                return None
                
        except Exception as e:
            logger.error(f"Error updating finding {finding_id}: {e}")
            raise
    
    async def delete_finding(self, finding_id: str) -> bool:
        """Delete a finding by ID"""
        try:
            result = await self.collection.delete_one({"id": finding_id})
            if result.deleted_count > 0:
                logger.info(f"Deleted finding {finding_id}")
                return True
            else:
                logger.warning(f"Finding {finding_id} not found for deletion")
                return False
        except Exception as e:
            logger.error(f"Error deleting finding {finding_id}: {e}")
            raise
    
    async def list_findings(
        self, 
        filters: Optional[FindingsFilter] = None,
        skip: int = 0,
        limit: int = 100,
        sort_by: str = "created_at",
        sort_order: int = -1
    ) -> List[Finding]:
        """List findings with optional filtering and pagination"""
        try:
            # Build query from filters
            query = {}
            if filters:
                if filters.diagram_id:
                    query["diagram_id"] = filters.diagram_id
                if filters.node_id:
                    query["node_id"] = filters.node_id
                if filters.severity:
                    query["severity"] = {"$in": [s.value for s in filters.severity]}
                if filters.status:
                    query["status"] = {"$in": [s.value for s in filters.status]}
                if filters.source:
                    query["source"] = {"$in": [s.value for s in filters.source]}
                if filters.category:
                    query["category"] = {"$in": filters.category}
                if filters.assigned_to:
                    query["assigned_to"] = filters.assigned_to
                if filters.created_after:
                    query.setdefault("created_at", {})["$gte"] = filters.created_after
                if filters.created_before:
                    query.setdefault("created_at", {})["$lte"] = filters.created_before
                if filters.min_risk_score is not None:
                    query.setdefault("risk_score", {})["$gte"] = filters.min_risk_score
                if filters.max_risk_score is not None:
                    query.setdefault("risk_score", {})["$lte"] = filters.max_risk_score
                if filters.framework_tags:
                    query["framework_tags"] = {"$in": filters.framework_tags}
            
            # Execute query with pagination and sorting
            cursor = self.collection.find(query).skip(skip).limit(limit).sort(sort_by, sort_order)
            findings_data = await cursor.to_list(length=limit)
            
            # Convert to Finding objects
            findings = []
            for finding_data in findings_data:
                finding_data.pop("_id", None)
                findings.append(Finding(**finding_data))
            
            logger.info(f"Retrieved {len(findings)} findings with filters")
            return findings
            
        except Exception as e:
            logger.error(f"Error listing findings: {e}")
            raise
    
    async def get_findings_summary(self, diagram_id: Optional[str] = None) -> FindingsSummary:
        """Get summary statistics for findings"""
        try:
            # Build base match query
            match_query = {}
            if diagram_id:
                match_query["diagram_id"] = diagram_id
            
            # Aggregation pipeline
            pipeline = []
            if match_query:
                pipeline.append({"$match": match_query})
            
            pipeline.extend([
                {
                    "$group": {
                        "_id": None,
                        "total_findings": {"$sum": 1},
                        "severity_counts": {
                            "$push": "$severity"
                        },
                        "status_counts": {
                            "$push": "$status"
                        },
                        "category_counts": {
                            "$push": "$category"
                        },
                        "risk_scores": {
                            "$push": "$risk_score"
                        },
                        "overdue_count": {
                            "$sum": {
                                "$cond": [
                                    {
                                        "$and": [
                                            {"$ne": ["$due_date", None]},
                                            {"$lt": ["$due_date", datetime.now(timezone.utc)]}
                                        ]
                                    },
                                    1,
                                    0
                                ]
                            }
                        }
                    }
                }
            ])
            
            cursor = self.collection.aggregate(pipeline)
            results = await cursor.to_list(length=1)
            
            summary = FindingsSummary()
            
            if results:
                result = results[0]
                summary.total_findings = result.get("total_findings", 0)
                summary.overdue_findings_count = result.get("overdue_count", 0)
                
                # Process severity counts
                severity_counts = {}
                for severity in result.get("severity_counts", []):
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1
                summary.by_severity = severity_counts
                
                # Process status counts
                status_counts = {}
                for status in result.get("status_counts", []):
                    status_counts[status] = status_counts.get(status, 0) + 1
                summary.by_status = status_counts
                
                # Process category counts
                category_counts = {}
                for category in result.get("category_counts", []):
                    category_counts[category] = category_counts.get(category, 0) + 1
                summary.by_category = category_counts
                
                # Process risk scores
                risk_scores = result.get("risk_scores", [])
                if risk_scores:
                    summary.average_risk_score = sum(risk_scores) / len(risk_scores)
                    summary.highest_risk_score = max(risk_scores)
                
                # Count critical and high findings
                summary.critical_findings_count = severity_counts.get("Critical", 0)
                summary.high_findings_count = severity_counts.get("High", 0)
            
            logger.info(f"Generated findings summary: {summary.total_findings} total findings")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating findings summary: {e}")
            raise
    
    async def create_indexes(self):
        """Create database indexes for optimal query performance"""
        try:
            indexes = [
                ("id", 1),  # Unique index on finding ID
                ("diagram_id", 1),  # Index on diagram ID
                ("node_id", 1),  # Index on node ID
                ("severity", 1),  # Index on severity
                ("status", 1),  # Index on status
                ("created_at", -1),  # Index on creation date (descending)
                ("risk_score", -1),  # Index on risk score (descending)
                ([("diagram_id", 1), ("severity", 1), ("status", 1)]),  # Compound index
                ([("created_at", -1), ("severity", 1)]),  # Compound index for time-based queries
            ]
            
            for index in indexes:
                if isinstance(index, tuple):
                    await self.collection.create_index(index)
                else:
                    await self.collection.create_index(index)
            
            logger.info("Created database indexes for findings collection")
            
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
            raise

# Utility functions for creating findings from different sources

def create_questionnaire_finding(
    diagram_id: str,
    node_id: str,
    question_id: str,
    question_text: str,
    user_response: Any,
    risk_assessment: Dict[str, Any],
    recommendations: List[str]
) -> Finding:
    """Create a finding from questionnaire response analysis"""
    
    severity_map = {
        (8.0, 10.0): FindingSeverity.CRITICAL,
        (6.0, 8.0): FindingSeverity.HIGH,
        (3.0, 6.0): FindingSeverity.MEDIUM,
        (0.0, 3.0): FindingSeverity.LOW
    }
    
    risk_score = risk_assessment.get("risk_score", 0.0)
    severity = FindingSeverity.LOW
    
    for (min_score, max_score), sev in severity_map.items():
        if min_score <= risk_score < max_score:
            severity = sev
            break
    
    return Finding(
        diagram_id=diagram_id,
        node_id=node_id,
        title=f"Security Issue in {question_text}",
        description=risk_assessment.get("description", "Security issue identified through questionnaire analysis"),
        severity=severity,
        risk_score=risk_score,
        source=FindingSource.QUESTIONNAIRE,
        category=risk_assessment.get("category", "General Security"),
        evidence={
            "question_id": question_id,
            "question_text": question_text,
            "user_response": user_response,
            "risk_assessment": risk_assessment
        },
        recommendations=recommendations,
        framework_tags=risk_assessment.get("framework_tags", []),
        mitre_techniques=risk_assessment.get("mitre_techniques", [])
    )

def create_rule_engine_finding(
    diagram_id: str,
    node_id: str,
    rule_id: str,
    rule_result: Dict[str, Any]
) -> Finding:
    """Create a finding from DSL rule engine evaluation"""
    
    return Finding(
        diagram_id=diagram_id,
        node_id=node_id,
        rule_id=rule_id,
        title=rule_result.get("rule_name", "Security Rule Violation"),
        description=rule_result.get("description", "Security rule violation detected"),
        severity=FindingSeverity(rule_result.get("impact_level", "Medium")),
        risk_score=rule_result.get("risk_score", 5.0),
        source=FindingSource.RULE_ENGINE,
        category=rule_result.get("category", "Security Controls"),
        evidence={
            "rule_id": rule_id,
            "rule_result": rule_result
        },
        recommendations=rule_result.get("recommendations", []),
        framework_tags=rule_result.get("framework_tags", []),
        mitre_techniques=rule_result.get("mitre_techniques", [])
    )

def create_simulation_finding(
    diagram_id: str,
    attack_path: Dict[str, Any],
    simulation_result: Dict[str, Any]
) -> Finding:
    """Create a finding from attack path simulation"""
    
    return Finding(
        diagram_id=diagram_id,
        title=f"Attack Path: {attack_path.get('name', 'Potential Security Vulnerability')}",
        description=attack_path.get("description", "Potential attack path identified through simulation"),
        severity=FindingSeverity.HIGH,  # Attack paths are typically high severity
        risk_score=attack_path.get("likelihood", 7.0),
        source=FindingSource.SIMULATION,
        category="Attack Path Analysis",
        evidence={
            "attack_path": attack_path,
            "simulation_result": simulation_result
        },
        affected_components=attack_path.get("steps", []),
        recommendations=attack_path.get("recommendations", []),
        mitre_techniques=attack_path.get("mitre_techniques", [])
    )