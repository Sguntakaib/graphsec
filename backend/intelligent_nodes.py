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
    # Deployment-related branches
    DEPLOYMENT = "Deployment"
    CLOUD_SECURITY = "CloudSecurity"
    NETWORK_SECURITY = "NetworkSecurity"
    INFRASTRUCTURE = "Infrastructure"

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
                SecurityBranchType.WAF,
                SecurityBranchType.DEPLOYMENT  # New deployment branch
            ],
            dependencies={
                "webapp_api_endpoints": "API",
                "webapp_database_connection": "Database",
                "webapp_deployment_type": "Deployment"  # This will be handled specially
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
                ),
                SecurityPrompt(
                    id="webapp_deployment_type",
                    question="Where is this web application deployed?",
                    type=PromptType.SINGLE_CHOICE,
                    options=["Cloud", "On-Premises", "Hybrid", "Unknown"],
                    help_text="Deployment type affects security controls and architecture requirements",
                    related_branch=SecurityBranchType.DEPLOYMENT
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
            dependencies={
                # API might depend on authentication services
            },
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
            dependencies={},
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
        
        # Cloud Deployment Node Template
        templates["CloudDeployment"] = IntelligentNodeTemplate(
            node_type="Infrastructure",
            node_subtype="CloudDeployment",
            required_branches=[
                SecurityBranchType.CLOUD_SECURITY,
                SecurityBranchType.ACCESS_CONTROL,
                SecurityBranchType.MONITORING,
                SecurityBranchType.ENCRYPTION
            ],
            dependencies={
                "cloud_provider_aws": "AWSService",
                "cloud_provider_gcp": "GCPService"
            },
            security_prompts=[
                SecurityPrompt(
                    id="cloud_provider",
                    question="Which cloud provider are you using?",
                    type=PromptType.SINGLE_CHOICE,
                    options=["AWS", "Google Cloud Platform (GCP)", "Microsoft Azure", "Other", "Multi-Cloud"],
                    help_text="Different cloud providers have varying security services and configurations",
                    related_branch=SecurityBranchType.CLOUD_SECURITY
                ),
                SecurityPrompt(
                    id="cloud_region",
                    question="Which region(s) is the application deployed in?",
                    type=PromptType.SINGLE_CHOICE,
                    options=["Single Region", "Multiple Regions (Same Country)", "Multiple Regions (Global)", "Edge Locations", "Unknown"],
                    help_text="Regional deployment affects compliance, latency, and disaster recovery",
                    related_branch=SecurityBranchType.CLOUD_SECURITY
                ),
                SecurityPrompt(
                    id="cloud_security_posture",
                    question="What cloud security posture management is in place?",
                    type=PromptType.SINGLE_CHOICE,
                    options=["CSPM Tool (AWS Security Hub/GCP SCC)", "Native Cloud Security", "Third-party CSPM", "Manual Configuration", "None"],
                    help_text="Cloud security posture management ensures proper configuration",
                    related_branch=SecurityBranchType.CLOUD_SECURITY
                ),
                SecurityPrompt(
                    id="cloud_access_management",
                    question="How is cloud access managed?",
                    type=PromptType.SINGLE_CHOICE,
                    options=["IAM with Least Privilege", "Role-Based Access", "Service Accounts Only", "Shared Credentials", "Root Access"],
                    help_text="Proper cloud access management is critical for security",
                    related_branch=SecurityBranchType.ACCESS_CONTROL
                ),
                SecurityPrompt(
                    id="cloud_monitoring",
                    question="What cloud monitoring and logging is configured?",
                    type=PromptType.MULTIPLE_CHOICE,
                    options=["CloudTrail/Activity Logs", "VPC Flow Logs", "Application Logs", "Security Monitoring", "Cost Monitoring", "None"],
                    help_text="Comprehensive monitoring provides visibility into cloud activities",
                    related_branch=SecurityBranchType.MONITORING
                )
            ],
            risk_factors={
                "root_access": 9.0,
                "shared_credentials": 7.0,
                "no_monitoring": 6.0,
                "no_cspm": 4.0,
                "global_deployment": 2.0
            }
        )
        
        # On-Premises Deployment Node Template
        templates["OnPremisesDeployment"] = IntelligentNodeTemplate(
            node_type="Infrastructure",
            node_subtype="OnPremisesDeployment",
            required_branches=[
                SecurityBranchType.NETWORK_SECURITY,
                SecurityBranchType.INFRASTRUCTURE,
                SecurityBranchType.ACCESS_CONTROL,
                SecurityBranchType.MONITORING
            ],
            dependencies={
                "onprem_network_wan": "WANConnection",
                "onprem_network_lan": "LANInfrastructure"
            },
            security_prompts=[
                SecurityPrompt(
                    id="onprem_server_location",
                    question="Where are the servers physically located?",
                    type=PromptType.SINGLE_CHOICE,
                    options=["Corporate Data Center", "Colocation Facility", "On-Site Server Room", "Remote Office", "Unknown"],
                    help_text="Physical location affects security controls and access management",
                    related_branch=SecurityBranchType.INFRASTRUCTURE
                ),
                SecurityPrompt(
                    id="onprem_network_segmentation",
                    question="How is network segmentation implemented?",
                    type=PromptType.SINGLE_CHOICE,
                    options=["VLANs with Firewalls", "Physical Segmentation", "Software-Defined Networking", "Basic Network Separation", "No Segmentation"],
                    help_text="Network segmentation limits attack spread and improves security",
                    related_branch=SecurityBranchType.NETWORK_SECURITY
                ),
                SecurityPrompt(
                    id="onprem_wan_connection",
                    question="How does the application connect to external networks?",
                    type=PromptType.SINGLE_CHOICE,
                    options=["VPN Only", "Direct Internet + Firewall", "MPLS Network", "Dedicated Lines", "Multiple Connections"],
                    help_text="WAN connectivity affects external attack surface",
                    related_branch=SecurityBranchType.NETWORK_SECURITY
                ),
                SecurityPrompt(
                    id="onprem_lan_security",
                    question="What LAN security measures are in place?",
                    type=PromptType.MULTIPLE_CHOICE,
                    options=["Network Access Control (NAC)", "802.1X Authentication", "DHCP Snooping", "Port Security", "IDS/IPS", "None"],
                    help_text="LAN security prevents internal network attacks",
                    related_branch=SecurityBranchType.NETWORK_SECURITY
                ),
                SecurityPrompt(
                    id="onprem_physical_security",
                    question="What physical security controls are implemented?",
                    type=PromptType.MULTIPLE_CHOICE,
                    options=["Keycard Access", "Biometric Access", "Security Cameras", "24/7 Security", "Environmental Controls", "None"],
                    help_text="Physical security protects against unauthorized physical access",
                    related_branch=SecurityBranchType.INFRASTRUCTURE
                )
            ],
            risk_factors={
                "no_segmentation": 8.0,
                "direct_internet": 6.0,
                "no_physical_security": 7.0,
                "no_lan_security": 5.0,
                "remote_office": 4.0
            }
        )
        
        # AWS Service Node Template
        templates["AWSService"] = IntelligentNodeTemplate(
            node_type="Service",
            node_subtype="AWSService",
            required_branches=[
                SecurityBranchType.CLOUD_SECURITY,
                SecurityBranchType.ACCESS_CONTROL,
                SecurityBranchType.MONITORING
            ],
            dependencies={},
            security_prompts=[
                SecurityPrompt(
                    id="aws_services_used",
                    question="Which AWS services are you using for this application?",
                    type=PromptType.MULTIPLE_CHOICE,
                    options=["EC2", "ECS/Fargate", "Lambda", "RDS", "S3", "CloudFront", "Route 53", "ALB/ELB", "API Gateway", "Other"],
                    help_text="Different AWS services have different security configurations",
                    related_branch=SecurityBranchType.CLOUD_SECURITY
                ),
                SecurityPrompt(
                    id="aws_deployment_method",
                    question="How is the application deployed on AWS?",
                    type=PromptType.SINGLE_CHOICE,
                    options=["Infrastructure as Code (Terraform/CloudFormation)", "CI/CD Pipeline", "Manual Deployment", "Third-party Tools", "Container Orchestration"],
                    help_text="Deployment method affects consistency and security",
                    related_branch=SecurityBranchType.CLOUD_SECURITY
                ),
                SecurityPrompt(
                    id="aws_security_services",
                    question="Which AWS security services are enabled?",
                    type=PromptType.MULTIPLE_CHOICE,
                    options=["GuardDuty", "Security Hub", "Config", "CloudTrail", "VPC Flow Logs", "WAF", "Shield", "None"],
                    help_text="AWS security services provide threat detection and compliance",
                    related_branch=SecurityBranchType.MONITORING
                ),
                SecurityPrompt(
                    id="aws_network_configuration",
                    question="How is AWS networking configured?",
                    type=PromptType.SINGLE_CHOICE,
                    options=["Private Subnets + NAT Gateway", "Public + Private Subnets", "Public Subnets Only", "Default VPC", "Custom VPC Design"],
                    help_text="Network configuration affects attack surface and access control",
                    related_branch=SecurityBranchType.NETWORK_SECURITY
                ),
                SecurityPrompt(
                    id="aws_data_encryption",
                    question="How is data encryption configured in AWS?",
                    type=PromptType.MULTIPLE_CHOICE,
                    options=["KMS Customer Managed Keys", "KMS AWS Managed Keys", "CloudHSM", "Client-side Encryption", "No Encryption"],
                    help_text="Data encryption protects sensitive information",
                    related_branch=SecurityBranchType.ENCRYPTION
                )
            ],
            risk_factors={
                "default_vpc": 5.0,
                "public_subnets_only": 7.0,
                "manual_deployment": 4.0,
                "no_security_services": 6.0,
                "no_encryption": 8.0
            }
        )
        
        # GCP Service Node Template
        templates["GCPService"] = IntelligentNodeTemplate(
            node_type="Service",
            node_subtype="GCPService",
            required_branches=[
                SecurityBranchType.CLOUD_SECURITY,
                SecurityBranchType.ACCESS_CONTROL,
                SecurityBranchType.MONITORING
            ],
            dependencies={},
            security_prompts=[
                SecurityPrompt(
                    id="gcp_services_used",
                    question="Which GCP services are you using for this application?",
                    type=PromptType.MULTIPLE_CHOICE,
                    options=["Compute Engine", "App Engine", "Cloud Run", "GKE", "Cloud SQL", "Cloud Storage", "Cloud CDN", "Cloud Load Balancing", "Other"],
                    help_text="Different GCP services have different security configurations",
                    related_branch=SecurityBranchType.CLOUD_SECURITY
                ),
                SecurityPrompt(
                    id="gcp_deployment_method",
                    question="How is the application deployed on GCP?",
                    type=PromptType.SINGLE_CHOICE,
                    options=["Cloud Deployment Manager", "Terraform", "CI/CD Pipeline", "Manual Deployment", "Container Orchestration"],
                    help_text="Deployment method affects consistency and security",
                    related_branch=SecurityBranchType.CLOUD_SECURITY
                ),
                SecurityPrompt(
                    id="gcp_security_services",
                    question="Which GCP security services are enabled?",
                    type=PromptType.MULTIPLE_CHOICE,
                    options=["Security Command Center", "Cloud Security Scanner", "Cloud Audit Logs", "VPC Flow Logs", "Cloud Armor", "Cloud DLP", "None"],
                    help_text="GCP security services provide threat detection and compliance",
                    related_branch=SecurityBranchType.MONITORING
                ),
                SecurityPrompt(
                    id="gcp_network_configuration",
                    question="How is GCP networking configured?",
                    type=PromptType.SINGLE_CHOICE,
                    options=["Private Google Access", "Custom VPC", "Shared VPC", "Default Network", "Private Service Connect"],
                    help_text="Network configuration affects attack surface and access control",
                    related_branch=SecurityBranchType.NETWORK_SECURITY
                ),
                SecurityPrompt(
                    id="gcp_data_encryption",
                    question="How is data encryption configured in GCP?",
                    type=PromptType.MULTIPLE_CHOICE,
                    options=["Cloud KMS Customer Keys", "Google-managed Keys", "Cloud HSM", "Client-side Encryption", "No Encryption"],
                    help_text="Data encryption protects sensitive information",
                    related_branch=SecurityBranchType.ENCRYPTION
                )
            ],
            risk_factors={
                "default_network": 5.0,
                "manual_deployment": 4.0,
                "no_security_services": 6.0,
                "no_encryption": 8.0,
                "shared_vpc": 2.0
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
                "WAF protection status confirmed",
                "Deployment type specified"
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
            ],
            "CloudDeployment": [
                "Cloud provider specified",
                "Cloud region configuration confirmed",
                "Cloud security posture defined",
                "Cloud access management configured",
                "Cloud monitoring configured"
            ],
            "OnPremisesDeployment": [
                "Server location specified",
                "Network segmentation configured",
                "WAN connection defined",
                "LAN security configured",
                "Physical security measures specified"
            ],
            "AWSService": [
                "AWS services specified",
                "Deployment method configured",
                "Security services enabled",
                "Network configuration defined",
                "Data encryption configured"
            ],
            "GCPService": [
                "GCP services specified",
                "Deployment method configured",
                "Security services enabled",
                "Network configuration defined",
                "Data encryption configured"
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
    
    def get_node_dependencies(self, node_subtype: str) -> Dict[str, str]:
        """Get dependency mapping for a node type"""
        template = self.get_node_template(node_subtype)
        return template.dependencies if template else {}
    
    def check_conditional_dependencies(self, node_subtype: str, questionnaire_answers: Dict[str, Any]) -> List[str]:
        """Check which dependent nodes should be created based on questionnaire answers"""
        dependencies = self.get_node_dependencies(node_subtype)
        nodes_to_create = []
        
        for question_id, dependent_node_type in dependencies.items():
            answer = questionnaire_answers.get(question_id)
            
            # Handle deployment dependencies with specific logic
            if question_id == "webapp_deployment_type":
                if isinstance(answer, str):
                    if answer.lower() == "cloud":
                        nodes_to_create.append("CloudDeployment")
                    elif answer.lower() == "on-premises":
                        nodes_to_create.append("OnPremisesDeployment")
            
            # Handle cloud provider dependencies
            elif question_id == "cloud_provider":
                if isinstance(answer, str):
                    if "aws" in answer.lower():
                        nodes_to_create.append("AWSService")
                    elif "gcp" in answer.lower() or "google" in answer.lower():
                        nodes_to_create.append("GCPService")
            
            # Handle standard boolean dependencies
            elif answer is True or (isinstance(answer, str) and answer.lower() in ['yes', 'true']):
                nodes_to_create.append(dependent_node_type)
        
        return nodes_to_create

# Global instance
intelligent_node_engine = IntelligentNodeEngine()