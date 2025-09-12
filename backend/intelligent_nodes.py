"""
Intelligent Node System for Phase 1
Smart node expansion, security prompting, and guided branching
"""

from typing import Dict, List, Optional, Any, Union
from enum import Enum
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)

class SecurityBranchType(str, Enum):
    LOGIN = "Login"
    API = "API"
    DATABASE = "Database"
    INPUT_VALIDATION = "InputValidation"
    WAF = "WAF"
    ENCRYPTION = "Encryption"
    ACCESS_CONTROL = "AccessControl"
    AUTHENTICATION = "Authentication"
    AUTHORIZATION = "Authorization" 
    RATE_LIMITING = "RateLimiting"
    CORS = "CORS"
    DATA_CLASSIFICATION = "DataClassification"
    BACKUP = "Backup"
    MONITORING = "Monitoring"
    LOGGING = "Logging"

class PromptType(str, Enum):
    SINGLE_CHOICE = "single_choice"
    MULTIPLE_CHOICE = "multiple_choice"
    BOOLEAN = "boolean"
    TEXT = "text"
    NUMBER = "number"

class SecurityBranch(BaseModel):
    id: str
    name: str
    type: SecurityBranchType
    required: bool = True
    completed: bool = False
    value: Optional[Any] = None
    description: str = ""

class SecurityPrompt(BaseModel):
    id: str
    question: str
    type: PromptType
    options: Optional[List[str]] = None
    default_value: Optional[Any] = None
    help_text: str = ""
    validation_rules: Dict[str, Any] = {}
    related_branch: SecurityBranchType

class IntelligentNodeTemplate(BaseModel):
    node_type: str
    node_subtype: str
    required_branches: List[SecurityBranchType]
    security_prompts: List[SecurityPrompt]
    auto_expand_rules: Dict[str, Any] = {}
    risk_factors: Dict[str, float] = {}
    dependencies: Dict[str, str] = {}  # Maps question IDs to dependent node types

class IntelligentNodeEngine:
    """Engine for handling intelligent node expansion and security prompting"""
    
    def __init__(self):
        self.node_templates = self._initialize_node_templates()
        self.completion_rules = self._initialize_completion_rules()
    
    def _initialize_node_templates(self) -> Dict[str, IntelligentNodeTemplate]:
        """Initialize intelligent node templates with security requirements"""
        templates = {}
        
        # Website Node Template
        templates["WebApp"] = IntelligentNodeTemplate(
            node_type="Asset",
            node_subtype="WebApp",
            required_branches=[
                SecurityBranchType.LOGIN,
                SecurityBranchType.API,
                SecurityBranchType.DATABASE,
                SecurityBranchType.INPUT_VALIDATION,
                SecurityBranchType.WAF
            ],
            dependencies={
                "webapp_api_endpoints": "API",
                "webapp_database_connection": "Database"
            },
            security_prompts=[
                SecurityPrompt(
                    id="webapp_login",
                    question="What type of authentication does this web application use?",
                    type=PromptType.SINGLE_CHOICE,
                    options=["Password Only", "Password + MFA", "SSO (SAML/OAuth)", "API Key", "Certificate", "None"],
                    help_text="Choose the primary authentication method. MFA and SSO are more secure options.",
                    related_branch=SecurityBranchType.LOGIN
                ),
                SecurityPrompt(
                    id="webapp_api_endpoints",
                    question="Does this web application expose API endpoints?",
                    type=PromptType.BOOLEAN,
                    help_text="APIs can be attack vectors if not properly secured with authentication and input validation.",
                    related_branch=SecurityBranchType.API
                ),
                SecurityPrompt(
                    id="webapp_database_connection",
                    question="Does this application connect to a database?",
                    type=PromptType.BOOLEAN,
                    help_text="Database connections require input validation to prevent SQL injection attacks.",
                    related_branch=SecurityBranchType.DATABASE
                ),
                SecurityPrompt(
                    id="webapp_input_validation",
                    question="Is input validation implemented for user inputs?",
                    type=PromptType.SINGLE_CHOICE,
                    options=["Comprehensive", "Basic", "Limited", "None", "Unknown"],
                    help_text="Input validation prevents injection attacks (SQLi, XSS, etc.)",
                    related_branch=SecurityBranchType.INPUT_VALIDATION
                ),
                SecurityPrompt(
                    id="webapp_waf_protection",
                    question="Is a Web Application Firewall (WAF) deployed?",
                    type=PromptType.SINGLE_CHOICE,
                    options=["Cloud WAF", "On-Premise WAF", "Basic Protection", "None", "Unknown"],
                    help_text="WAF provides protection against common web attacks",
                    related_branch=SecurityBranchType.WAF
                )
            ],
            risk_factors={
                "login_none": 9.0,
                "login_password_only": 6.0,
                "login_mfa": 3.0,
                "no_input_validation": 8.0,
                "no_waf": 5.0,
                "database_connection": 4.0
            }
        )
        
        # Database Node Template
        templates["Database"] = IntelligentNodeTemplate(
            node_type="Asset",
            node_subtype="Database",
            required_branches=[
                SecurityBranchType.ENCRYPTION,
                SecurityBranchType.ACCESS_CONTROL,
                SecurityBranchType.BACKUP,
                SecurityBranchType.MONITORING,
                SecurityBranchType.DATA_CLASSIFICATION
            ],
            dependencies={
                "db_backup_enabled": "Backup",
                "db_monitoring_enabled": "Monitoring"
            },
            security_prompts=[
                SecurityPrompt(
                    id="db_type",
                    question="What type of database is this?",
                    type=PromptType.SINGLE_CHOICE,
                    options=["MySQL", "PostgreSQL", "MongoDB", "Oracle", "SQL Server", "Redis", "DynamoDB", "Other"],
                    help_text="Different database types have different security considerations.",
                    related_branch=SecurityBranchType.ACCESS_CONTROL
                ),
                SecurityPrompt(
                    id="db_encryption_at_rest",
                    question="Is encryption-at-rest enabled?",
                    type=PromptType.SINGLE_CHOICE,
                    options=["AES-256", "AES-128", "TDE (Transparent Data Encryption)", "None", "Unknown"],
                    help_text="Encryption protects data if storage media is compromised.",
                    related_branch=SecurityBranchType.ENCRYPTION
                ),
                SecurityPrompt(
                    id="db_encryption_in_transit",
                    question="Is encryption-in-transit enabled (TLS/SSL)?",
                    type=PromptType.BOOLEAN,
                    help_text="Encrypts data communications to prevent eavesdropping.",
                    related_branch=SecurityBranchType.ENCRYPTION
                ),
                SecurityPrompt(
                    id="db_access_control",
                    question="What access control mechanisms are in place?",
                    type=PromptType.MULTIPLE_CHOICE,
                    options=["Role-Based Access", "User Authentication", "IP Whitelisting", "VPN Required", "None"],
                    help_text="Multiple layers of access control improve security.",
                    related_branch=SecurityBranchType.ACCESS_CONTROL
                ),
                SecurityPrompt(
                    id="db_data_classification",
                    question="What is the highest data classification level stored?",
                    type=PromptType.SINGLE_CHOICE,
                    options=["Public", "Internal", "Confidential", "Restricted", "Top Secret"],
                    help_text="Higher classification requires stronger security controls.",
                    related_branch=SecurityBranchType.DATA_CLASSIFICATION
                )
            ],
            risk_factors={
                "no_encryption_at_rest": 8.0,
                "no_encryption_in_transit": 6.0,
                "weak_access_control": 7.0,
                "restricted_data": 9.0,
                "no_monitoring": 5.0
            }
        )
        
        # API Node Template  
        templates["API"] = IntelligentNodeTemplate(
            node_type="Asset",
            node_subtype="API",
            required_branches=[
                SecurityBranchType.AUTHENTICATION,
                SecurityBranchType.AUTHORIZATION,
                SecurityBranchType.RATE_LIMITING,
                SecurityBranchType.INPUT_VALIDATION,
                SecurityBranchType.CORS
            ],
            security_prompts=[
                SecurityPrompt(
                    id="api_auth_method",
                    question="What authentication method does this API use?",
                    type=PromptType.SINGLE_CHOICE,
                    options=["JWT", "OAuth 2.0", "API Key", "Basic Auth", "Certificate", "None"],
                    help_text="Strong authentication prevents unauthorized API access.",
                    related_branch=SecurityBranchType.AUTHENTICATION
                ),
                SecurityPrompt(
                    id="api_authorization",
                    question="Is fine-grained authorization implemented?",
                    type=PromptType.SINGLE_CHOICE,
                    options=["RBAC (Role-Based)", "ABAC (Attribute-Based)", "Simple Rules", "None"],
                    help_text="Authorization ensures users can only access permitted resources.",
                    related_branch=SecurityBranchType.AUTHORIZATION
                ),
                SecurityPrompt(
                    id="api_rate_limiting",
                    question="Is rate limiting configured?",
                    type=PromptType.SINGLE_CHOICE,
                    options=["Per User", "Per IP", "Global", "None"],
                    help_text="Rate limiting prevents abuse and DoS attacks.",
                    related_branch=SecurityBranchType.RATE_LIMITING
                ),
                SecurityPrompt(
                    id="api_input_validation",
                    question="How is input validation implemented?",
                    type=PromptType.SINGLE_CHOICE,
                    options=["Schema Validation", "Type Checking", "Basic Sanitization", "None"],
                    help_text="Input validation prevents injection and malformed data attacks.",
                    related_branch=SecurityBranchType.INPUT_VALIDATION
                ),
                SecurityPrompt(
                    id="api_cors_policy",
                    question="Is CORS (Cross-Origin Resource Sharing) properly configured?",
                    type=PromptType.SINGLE_CHOICE,
                    options=["Restrictive (Specific Origins)", "Moderate", "Permissive", "None/Default"],
                    help_text="CORS controls which domains can access your API from browsers.",
                    related_branch=SecurityBranchType.CORS
                )
            ],
            risk_factors={
                "no_authentication": 9.0,
                "weak_authentication": 6.0,
                "no_authorization": 7.0,
                "no_rate_limiting": 5.0,
                "permissive_cors": 4.0
            }
        )
        
        # External Attacker Template
        templates["ExternalAttacker"] = IntelligentNodeTemplate(
            node_type="Actor",
            node_subtype="ExternalAttacker",
            required_branches=[],  # Attackers don't need security controls
            security_prompts=[
                SecurityPrompt(
                    id="attacker_sophistication",
                    question="What is the sophistication level of this threat actor?",
                    type=PromptType.SINGLE_CHOICE,
                    options=["Script Kiddie", "Organized Crime", "Advanced Persistent Threat", "Nation State"],
                    help_text="Higher sophistication means more advanced attack techniques.",
                    related_branch=SecurityBranchType.MONITORING
                ),
                SecurityPrompt(
                    id="attacker_motivation",
                    question="What is the primary motivation of this attacker?",
                    type=PromptType.SINGLE_CHOICE,
                    options=["Financial Gain", "Espionage", "Sabotage", "Reputation", "Activism"],
                    help_text="Motivation influences attack methods and persistence.",
                    related_branch=SecurityBranchType.MONITORING
                ),
                SecurityPrompt(
                    id="attacker_resources",
                    question="What level of resources does this attacker have?",
                    type=PromptType.SINGLE_CHOICE,
                    options=["Limited", "Moderate", "Substantial", "Nation-State Level"],
                    help_text="Resources determine the scale and duration of attacks.",
                    related_branch=SecurityBranchType.MONITORING
                )
            ],
            risk_factors={
                "nation_state": 10.0,
                "apt": 8.0,
                "organized_crime": 6.0,
                "script_kiddie": 3.0
            }
        )
        
        return templates
    
    def _initialize_completion_rules(self) -> Dict[str, List[str]]:
        """Rules for when a node is considered complete"""
        return {
            "WebApp": [
                "Login authentication method specified",
                "API endpoints status confirmed", 
                "Database connection status confirmed",
                "Input validation level specified",
                "WAF protection status confirmed"
            ],
            "Database": [
                "Database type specified",
                "Encryption-at-rest status confirmed",
                "Encryption-in-transit status confirmed", 
                "Access control mechanisms specified",
                "Data classification level specified"
            ],
            "API": [
                "Authentication method specified",
                "Authorization model specified",
                "Rate limiting configuration confirmed",
                "Input validation approach specified",
                "CORS policy configuration confirmed"
            ],
            "ExternalAttacker": [
                "Sophistication level specified",
                "Motivation identified",
                "Resource level estimated"
            ]
        }
    
    def get_node_template(self, node_subtype: str) -> Optional[IntelligentNodeTemplate]:
        """Get the intelligent template for a node subtype"""
        return self.node_templates.get(node_subtype)
    
    def get_security_prompts(self, node_subtype: str) -> List[SecurityPrompt]:
        """Get security prompts for a specific node type"""
        template = self.get_node_template(node_subtype)
        return template.security_prompts if template else []
    
    def get_required_branches(self, node_subtype: str) -> List[SecurityBranchType]:
        """Get required security branches for a node type"""
        template = self.get_node_template(node_subtype)
        return template.required_branches if template else []
    
    def create_security_branches(self, node_subtype: str) -> List[SecurityBranch]:
        """Create security branches for a node based on its template"""
        template = self.get_node_template(node_subtype)
        if not template:
            return []
        
        branches = []
        for branch_type in template.required_branches:
            branch = SecurityBranch(
                id=f"{node_subtype.lower()}_{branch_type.value.lower()}",
                name=branch_type.value,
                type=branch_type,
                required=True,
                completed=False,
                description=self._get_branch_description(branch_type)
            )
            branches.append(branch)
        
        return branches
    
    def _get_branch_description(self, branch_type: SecurityBranchType) -> str:
        """Get description for a security branch type"""
        descriptions = {
            SecurityBranchType.LOGIN: "Authentication mechanism for user login",
            SecurityBranchType.API: "API endpoints and their security configuration",
            SecurityBranchType.DATABASE: "Database connection and query security",
            SecurityBranchType.INPUT_VALIDATION: "Input sanitization and validation controls",
            SecurityBranchType.WAF: "Web Application Firewall protection",
            SecurityBranchType.ENCRYPTION: "Data encryption at rest and in transit",
            SecurityBranchType.ACCESS_CONTROL: "User access management and permissions",
            SecurityBranchType.AUTHENTICATION: "Identity verification mechanisms",
            SecurityBranchType.AUTHORIZATION: "Permission and access control systems",
            SecurityBranchType.RATE_LIMITING: "Request throttling and abuse prevention",
            SecurityBranchType.CORS: "Cross-Origin Resource Sharing policy",
            SecurityBranchType.DATA_CLASSIFICATION: "Data sensitivity and classification levels",
            SecurityBranchType.BACKUP: "Data backup and recovery mechanisms",
            SecurityBranchType.MONITORING: "Security monitoring and alerting",
            SecurityBranchType.LOGGING: "Audit trails and security logging"
        }
        return descriptions.get(branch_type, "Security control or configuration")
    
    def validate_node_completeness(self, node_subtype: str, branches: List[SecurityBranch]) -> Dict[str, Any]:
        """Validate if a node has all required security branches completed"""
        template = self.get_node_template(node_subtype)
        if not template:
            return {"complete": True, "missing_branches": [], "completion_percentage": 100}
        
        required_branches = set(template.required_branches)
        completed_branches = set()
        
        for branch in branches:
            if branch.completed and branch.type in required_branches:
                completed_branches.add(branch.type)
        
        missing_branches = required_branches - completed_branches
        completion_percentage = (len(completed_branches) / len(required_branches) * 100) if required_branches else 100
        
        return {
            "is_complete": len(missing_branches) == 0,
            "missing_branches": [branch.value for branch in missing_branches],
            "completion_percentage": round(completion_percentage, 1),
            "completed_count": len(completed_branches),
            "required_count": len(required_branches)
        }
    
    def calculate_node_risk_score(self, node_subtype: str, branch_values: Dict[str, Any]) -> float:
        """Calculate risk score based on node configuration"""
        template = self.get_node_template(node_subtype)
        if not template:
            return 5.0  # Default medium risk
        
        base_risk = 5.0
        risk_adjustments = 0.0
        
        # Apply risk factors based on configuration
        for key, risk_increase in template.risk_factors.items():
            if key in branch_values:
                value = branch_values[key]
                if value == True or (isinstance(value, str) and value.lower() in ['none', 'unknown', 'basic']):
                    risk_adjustments += risk_increase
        
        # Apply positive security controls
        security_controls = {
            "mfa": -2.0,
            "comprehensive_validation": -2.0,
            "cloud_waf": -1.5,
            "encryption": -1.0,
            "monitoring": -0.5
        }
        
        for control, risk_reduction in security_controls.items():
            if control in branch_values and branch_values[control]:
                risk_adjustments += risk_reduction
        
        final_risk = max(0.0, min(10.0, base_risk + risk_adjustments))
        return round(final_risk, 1)
    
    def generate_security_recommendations(self, node_subtype: str, branches: List[SecurityBranch]) -> List[str]:
        """Generate security recommendations based on node configuration"""
        recommendations = []
        template = self.get_node_template(node_subtype)
        if not template:
            return recommendations
        
        # Check for missing or weak configurations
        for branch in branches:
            if not branch.completed:
                recommendations.append(f"Configure {branch.name}: {branch.description}")
            elif branch.value in ['None', 'Basic', 'Limited', 'Unknown']:
                recommendations.append(f"Strengthen {branch.name}: Consider upgrading from '{branch.value}' to a more secure option")
        
        # Node-specific recommendations
        if node_subtype == "WebApp":
            for branch in branches:
                if branch.type == SecurityBranchType.LOGIN and branch.value == "Password Only":
                    recommendations.append("Implement Multi-Factor Authentication (MFA) to reduce credential-based attacks")
                elif branch.type == SecurityBranchType.INPUT_VALIDATION and branch.value in ["None", "Limited"]:
                    recommendations.append("Implement comprehensive input validation to prevent injection attacks")
        
        elif node_subtype == "Database":
            for branch in branches:
                if branch.type == SecurityBranchType.ENCRYPTION and not branch.value:
                    recommendations.append("Enable encryption-at-rest and encryption-in-transit for data protection")
                elif branch.type == SecurityBranchType.DATA_CLASSIFICATION and branch.value in ["Confidential", "Restricted"]:
                    recommendations.append("Implement additional security controls for high-value data classification")
        
        return recommendations[:5]  # Limit to top 5 recommendations

# Global instance
intelligent_node_engine = IntelligentNodeEngine()