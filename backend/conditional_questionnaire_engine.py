"""
Conditional Questionnaire Engine
Handles conditional question flow based on user responses
Supports API type and Database type conditional questioning
"""

from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import logging
from questionnaire_loader import QuestionnaireLoader, QuestionnaireLevel

logger = logging.getLogger(__name__)

class ConditionalQuestionnaireEngine:
    """Engine for handling conditional questionnaire logic"""
    
    def __init__(self, questionnaire_loader: QuestionnaireLoader):
        self.questionnaire_loader = questionnaire_loader
        
        # Define conditional question mappings - Enhanced with security focus - Enhanced with security focus
        self.api_type_questions = {
            "REST API": [
                {
                    "id": "rest_api_versioning",
                    "question": "How is REST API versioning implemented?",
                    "type": "single_choice",
                    "options": ["URI versioning (/v1/)", "Header versioning", "Query parameter versioning", "Content negotiation", "No versioning"],
                    "help_text": "REST API versioning strategy affects security and backward compatibility.",
                    "related_branch": "ApiSecurity"
                },
                {
                    "id": "rest_http_methods_security",
                    "question": "How are REST HTTP methods secured against unauthorized operations?",
                    "type": "single_choice",
                    "options": ["Method-specific RBAC with scope validation", "Basic method authorization", "HTTP method filtering only", "No method-level security", "Unknown"],
                    "help_text": "REST method security prevents unauthorized CRUD operations and privilege escalation.",
                    "related_branch": "Authorization"
                },
                {
                    "id": "rest_parameter_pollution",
                    "question": "How does the REST API prevent HTTP Parameter Pollution attacks?",
                    "type": "single_choice",
                    "options": ["Parameter validation with duplicate detection", "Basic parameter parsing", "Framework default handling", "No protection", "Unknown"],
                    "help_text": "Parameter pollution attacks can bypass security controls in REST APIs.",
                    "related_branch": "InputValidation"
                },
                {
                    "id": "rest_bola_protection",
                    "question": "What protection exists against BOLA (Broken Object Level Authorization)?",
                    "type": "single_choice",
                    "options": ["Object-level ACL with ownership validation", "Basic ID validation", "User context checking", "No BOLA protection", "Unknown"],
                    "help_text": "BOLA is a critical REST API vulnerability allowing unauthorized object access.",
                    "related_branch": "Authorization"
                }
            ],
            "GraphQL API": [
                {
                    "id": "graphql_query_depth_limiting",
                    "question": "Is GraphQL query depth limiting implemented?",
                    "type": "single_choice",
                    "options": ["Configurable depth limits with monitoring", "Fixed depth limits", "Basic depth checking", "No depth limiting", "Unknown"],
                    "help_text": "Query depth limiting prevents denial of service attacks on GraphQL APIs.",
                    "related_branch": "ApiSecurity"
                },
                {
                    "id": "graphql_query_complexity_analysis",
                    "question": "How is GraphQL query complexity analysis implemented?",
                    "type": "single_choice", 
                    "options": ["Advanced complexity analysis with cost calculation", "Basic complexity scoring", "Query timeout only", "No complexity analysis", "Unknown"],
                    "help_text": "Query complexity analysis prevents resource exhaustion attacks.",
                    "related_branch": "ApiSecurity"
                },
                {
                    "id": "graphql_batch_query_security",
                    "question": "How are GraphQL batch queries secured?",
                    "type": "single_choice",
                    "options": ["Batch size limits with complexity scoring", "Basic batch limits", "Query count restrictions", "No batch protection", "Unknown"],
                    "help_text": "Batch query attacks can amplify GraphQL resource consumption.",
                    "related_branch": "RateLimiting"
                },
                {
                    "id": "graphql_introspection_security",
                    "question": "How is GraphQL introspection secured in production?",
                    "type": "single_choice",
                    "options": ["Introspection disabled with schema allowlisting", "Authenticated introspection only", "Filtered introspection", "Public introspection enabled", "Unknown"],
                    "help_text": "GraphQL introspection can expose sensitive schema information to attackers.",
                    "related_branch": "InformationDisclosure"
                }
            ],
            "SOAP API": [
                {
                    "id": "soap_wsdl_security",
                    "question": "How is WSDL access controlled to prevent information disclosure?",
                    "type": "single_choice",
                    "options": ["Authenticated WSDL with sanitized schemas", "Role-based WSDL access", "Public WSDL with security filtering", "Public detailed WSDL", "Unknown"],
                    "help_text": "WSDL can expose service structure and should be properly secured against reconnaissance.",
                    "related_branch": "InformationDisclosure"
                },
                {
                    "id": "soap_xml_injection_prevention",
                    "question": "What XML injection prevention measures are implemented?",
                    "type": "multiple_choice",
                    "options": ["XML schema validation", "XML external entity (XXE) prevention", "XML bomb protection", "XSLT injection prevention", "None"],
                    "help_text": "XML-based attacks are common in SOAP services and require comprehensive prevention.",
                    "related_branch": "InputValidation"
                },
                {
                    "id": "soap_ws_security_implementation",
                    "question": "What WS-Security features are implemented?",
                    "type": "multiple_choice",
                    "options": ["Message-level encryption", "Digital signatures", "Timestamp validation", "Username tokens", "None"],
                    "help_text": "WS-Security provides comprehensive message-level security for SOAP.",
                    "related_branch": "Encryption"
                },
                {
                    "id": "soap_fault_information_disclosure",
                    "question": "How are SOAP faults handled to prevent information disclosure?",
                    "type": "single_choice",
                    "options": ["Sanitized SOAP faults with logging", "Generic fault messages", "Detailed fault information", "No fault handling", "Unknown"],
                    "help_text": "SOAP faults can reveal internal system details and should be carefully managed.",
                    "related_branch": "InformationDisclosure"
                }
            ],
            "gRPC API": [
                {
                    "id": "grpc_tls_config",
                    "question": "How is gRPC TLS configured?",
                    "type": "single_choice",
                    "options": ["mTLS (mutual TLS) with certificate validation", "Server-side TLS only", "TLS with custom verification", "Insecure connections", "Unknown"],
                    "help_text": "gRPC TLS configuration secures communication channels against eavesdropping.",
                    "related_branch": "Encryption"
                },
                {
                    "id": "grpc_auth_method",
                    "question": "What gRPC authentication method is used?",
                    "type": "single_choice",
                    "options": ["OAuth2 tokens with scope validation", "JWT tokens with claims verification", "API keys in metadata", "Certificate-based authentication", "No authentication"],
                    "help_text": "gRPC authentication secures service access and prevents unauthorized calls.",
                    "related_branch": "Authentication"
                },
                {
                    "id": "grpc_streaming_security",
                    "question": "How are gRPC streaming connections secured?",
                    "type": "single_choice",
                    "options": ["Per-stream authentication with timeout controls", "Connection-level authentication", "Basic streaming validation", "No stream security", "Unknown"],
                    "help_text": "gRPC streaming requires additional security for long-lived connections.",
                    "related_branch": "ApiSecurity"
                },
                {
                    "id": "grpc_error_handling_security",
                    "question": "How does gRPC error handling prevent information disclosure?",
                    "type": "single_choice",
                    "options": ["Sanitized error responses with logging", "Generic error messages", "Detailed error responses", "No error handling", "Unknown"],
                    "help_text": "gRPC error responses can leak sensitive system information.",
                    "related_branch": "InformationDisclosure"
                }
            ],
            "WebSocket API": [
                {
                    "id": "websocket_origin_validation",
                    "question": "How is WebSocket origin validation implemented?",
                    "type": "single_choice",
                    "options": ["Strict origin validation with allowlist", "Flexible origin checking", "Basic origin validation", "No origin validation", "Unknown"],
                    "help_text": "Origin validation prevents unauthorized cross-origin WebSocket connections.",
                    "related_branch": "ApiSecurity"
                },
                {
                    "id": "websocket_auth_method",
                    "question": "How is WebSocket authentication handled?",
                    "type": "single_choice",
                    "options": ["Token-based with expiration", "Session-based authentication", "Certificate authentication", "Connection-based auth", "No authentication"],
                    "help_text": "WebSocket authentication secures real-time connections against unauthorized access.",
                    "related_branch": "Authentication"
                },
                {
                    "id": "websocket_message_validation",
                    "question": "How are WebSocket messages validated for security?",
                    "type": "single_choice",
                    "options": ["JSON schema validation with sanitization", "Custom message validation", "Basic format checking", "No message validation", "Unknown"],
                    "help_text": "Message validation prevents malicious WebSocket payloads and injection attacks.",
                    "related_branch": "InputValidation"
                },
                {
                    "id": "websocket_rate_limiting",
                    "question": "How is WebSocket message rate limiting implemented?",
                    "type": "single_choice",
                    "options": ["Per-connection rate limiting with burst control", "Global rate limiting", "Basic throttling", "No rate limiting", "Unknown"],
                    "help_text": "Rate limiting prevents WebSocket abuse and denial-of-service attacks.",
                    "related_branch": "RateLimiting"
                }
            ],
            "Other": [
                {
                    "id": "other_api_protocol",
                    "question": "What protocol does this API use?",
                    "type": "single_choice",
                    "options": ["Custom TCP protocol", "UDP-based protocol", "Message queue (AMQP/MQTT)", "Custom HTTP-based", "Binary protocol", "Unknown"],
                    "help_text": "Understanding the protocol helps identify appropriate security measures.",
                    "related_branch": "ApiSecurity"  
                },
                {
                    "id": "other_api_authentication",
                    "question": "How is authentication handled for this custom API?",
                    "type": "single_choice",
                    "options": ["Custom token-based authentication", "Certificate-based authentication", "Pre-shared keys", "IP allowlisting", "No authentication", "Unknown"],
                    "help_text": "Custom APIs require tailored authentication approaches.",
                    "related_branch": "Authentication"
                },
                {
                    "id": "other_api_data_validation",
                    "question": "How is input data validated in this API?",
                    "type": "single_choice",
                    "options": ["Custom schema validation", "Serialization format validation", "Basic type checking", "No validation", "Unknown"],
                    "help_text": "Custom APIs need robust input validation to prevent injection attacks.",
                    "related_branch": "InputValidation"
                },
                {
                    "id": "other_api_error_handling",
                    "question": "How does the API handle errors securely?",
                    "type": "single_choice",
                    "options": ["Structured error responses without details", "Generic error codes", "Detailed error information", "No error handling", "Unknown"],
                    "help_text": "Error handling in custom APIs can reveal implementation details.",
                    "related_branch": "InformationDisclosure"
                }
            ]
        }
        
        # Web interface subset questions for APIs that expose web interfaces
        self.api_web_interface_questions = [
            {
                "id": "api_web_xss_protection",
                "question": "How is Cross-Site Scripting (XSS) prevention implemented in the web interface?",
                "type": "single_choice",
                "options": ["Content Security Policy + output encoding", "Output encoding only", "Input sanitization only", "No XSS protection", "Unknown"],
                "help_text": "XSS protection prevents malicious script injection in web interfaces.",
                "related_branch": "WebSecurity"
            },
            {
                "id": "api_web_csrf_protection", 
                "question": "How is Cross-Site Request Forgery (CSRF) prevented?",
                "type": "single_choice",
                "options": ["CSRF tokens + SameSite cookies", "CSRF tokens only", "Referer validation", "No CSRF protection", "Unknown"],
                "help_text": "CSRF protection prevents unauthorized actions from malicious websites.",
                "related_branch": "WebSecurity"
            },
            {
                "id": "api_web_session_security",
                "question": "How are web sessions secured?",
                "type": "single_choice",
                "options": ["Secure session management with httpOnly/secure flags", "Basic session management", "Cookie-based sessions only", "No session security", "Unknown"],
                "help_text": "Secure session management prevents session hijacking and fixation attacks.",
                "related_branch": "SessionManagement"
            },
            {
                "id": "api_web_input_validation",
                "question": "How is user input validated in web forms?",
                "type": "single_choice",
                "options": ["Server-side validation + client-side enhancement", "Server-side validation only", "Client-side validation only", "No input validation", "Unknown"],
                "help_text": "Web form validation prevents injection attacks and ensures data integrity.",
                "related_branch": "InputValidation"
            },
            {
                "id": "api_web_security_headers",
                "question": "What web security headers are implemented?",
                "type": "multiple_choice",
                "options": ["X-Frame-Options", "X-Content-Type-Options", "Strict-Transport-Security", "Content-Security-Policy", "Referrer-Policy", "None"],
                "help_text": "Security headers provide defense-in-depth against various web attacks.",
                "related_branch": "WebSecurity"
            }
        ]
        
        # Enhanced external services categories based on real-world development
        self.external_services_categories = {
            "Authentication": [
                "OAuth2 providers (Google, Facebook, GitHub)",
                "Identity providers (Auth0, Okta, Azure AD)",
                "SAML providers",
                "LDAP/Active Directory",
                "Social login providers"
            ],
            "Payment": [
                "Payment processors (Stripe, PayPal, Square)",
                "Cryptocurrency payment gateways",
                "Banking APIs",
                "Digital wallet APIs",
                "Billing and subscription services"
            ],
            "Cloud": [
                "Cloud storage (AWS S3, Google Cloud Storage)",
                "Cloud databases (AWS RDS, Azure SQL)",
                "Serverless functions (AWS Lambda, Azure Functions)",
                "CDN services (CloudFlare, AWS CloudFront)",
                "Container registries"
            ],
            "Messaging": [
                "Email services (SendGrid, Mailgun, Amazon SES)",
                "SMS/MMS providers (Twilio, Vonage)",
                "Push notification services",
                "Chat/messaging APIs (Slack, Microsoft Teams)",
                "Communication platforms"
            ],
            "Analytics": [
                "Web analytics (Google Analytics, Adobe Analytics)",
                "Application monitoring (Datadog, New Relic)",
                "Error tracking (Sentry, Rollbar)",
                "Business intelligence platforms",
                "A/B testing services"
            ],
            "Social Media": [
                "Social media APIs (Twitter, LinkedIn, Instagram)",
                "Social sharing services",
                "Social authentication",
                "Social media management platforms",
                "Content syndication services"
            ],
            "File Storage": [
                "File storage services (Dropbox, Box)",
                "Image/video processing (Cloudinary, ImageKit)",
                "Document management systems",
                "Backup services",
                "File sharing platforms"
            ],
            "Notification": [
                "Push notification services (Firebase, OneSignal)",
                "Email notification platforms",
                "SMS notification services",
                "In-app notification systems",
                "Alert management platforms"
            ],
            "Other": [
                "Custom third-party APIs",
                "Legacy system integrations",
                "Industry-specific services",
                "Government APIs",
                "IoT device integrations"
            ]
        }
        
        self.database_type_questions = {
            "MySQL": [
                {
                    "id": "mysql_ssl_mode",
                    "question": "What MySQL SSL mode is configured?",
                    "type": "single_choice",
                    "options": ["REQUIRED", "VERIFY_CA", "VERIFY_IDENTITY", "PREFERRED", "DISABLED"],
                    "help_text": "MySQL SSL mode determines the level of connection encryption and validation.",
                    "related_branch": "Encryption"
                },
                {
                    "id": "mysql_auth_plugin",
                    "question": "Which MySQL authentication plugin is used?",
                    "type": "single_choice",
                    "options": ["caching_sha2_password", "mysql_native_password", "sha256_password", "auth_socket", "Unknown"],
                    "help_text": "MySQL authentication plugin affects password security and compatibility.",
                    "related_branch": "Authentication"
                },
                {
                    "id": "mysql_general_log",
                    "question": "Is MySQL general query logging enabled?",
                    "type": "single_choice",
                    "options": ["Enabled with log rotation", "Enabled without rotation", "Disabled", "Unknown"],
                    "help_text": "MySQL general log captures all database activity for security monitoring.",
                    "related_branch": "AuditLogging"
                }
            ],
            "PostgreSQL": [
                {
                    "id": "postgresql_ssl_config",
                    "question": "How is PostgreSQL SSL configured?",
                    "type": "single_choice",
                    "options": ["SSL required with certificate validation", "SSL required", "SSL preferred", "SSL disabled", "Unknown"],
                    "help_text": "PostgreSQL SSL configuration secures database connections.",
                    "related_branch": "Encryption"
                },
                {
                    "id": "postgresql_row_level_security",
                    "question": "Is PostgreSQL Row Level Security (RLS) enabled?",
                    "type": "single_choice",
                    "options": ["RLS enabled with policies", "RLS enabled without policies", "RLS disabled", "Unknown"],
                    "help_text": "Row Level Security provides fine-grained access control to table rows.",
                    "related_branch": "AccessControl"
                },
                {
                    "id": "postgresql_audit_extension",
                    "question": "Which PostgreSQL audit extension is used?",
                    "type": "single_choice",
                    "options": ["pgAudit", "Custom audit triggers", "Built-in logging only", "No audit extension", "Unknown"],
                    "help_text": "PostgreSQL audit extensions provide comprehensive database activity monitoring.",
                    "related_branch": "AuditLogging"
                }
            ],
            "MongoDB": [
                {
                    "id": "mongodb_auth_mechanism",
                    "question": "What MongoDB authentication mechanism is used?",
                    "type": "single_choice",
                    "options": ["SCRAM-SHA-256", "SCRAM-SHA-1", "X.509 certificates", "LDAP", "No authentication"],
                    "help_text": "MongoDB authentication mechanism affects security strength.",
                    "related_branch": "Authentication"
                },
                {
                    "id": "mongodb_authorization",
                    "question": "How is MongoDB role-based access control configured?",
                    "type": "single_choice",
                    "options": ["Custom roles with least privilege", "Built-in roles only", "Single admin user", "No authorization", "Unknown"],
                    "help_text": "MongoDB RBAC provides granular access control to databases and collections.",
                    "related_branch": "AccessControl"
                },
                {
                    "id": "mongodb_audit_log",
                    "question": "Is MongoDB audit logging enabled?",
                    "type": "single_choice",
                    "options": ["Comprehensive audit logging", "Basic audit logging", "No audit logging", "Unknown"],
                    "help_text": "MongoDB audit logging tracks database access and operations.",
                    "related_branch": "AuditLogging"
                }
            ],
            "Redis": [
                {
                    "id": "redis_auth_config",
                    "question": "How is Redis authentication configured?",
                    "type": "single_choice",
                    "options": ["ACL with multiple users", "Single password (requirepass)", "No authentication", "Unknown"],
                    "help_text": "Redis authentication prevents unauthorized access to data.",
                    "related_branch": "Authentication"
                },
                {
                    "id": "redis_tls_config",
                    "question": "Is Redis TLS encryption enabled?",
                    "type": "single_choice",
                    "options": ["TLS enabled for all connections", "TLS enabled for client connections only", "No TLS encryption", "Unknown"],
                    "help_text": "Redis TLS encryption protects data in transit.",
                    "related_branch": "Encryption"
                },
                {
                    "id": "redis_command_restrictions",
                    "question": "Are dangerous Redis commands disabled?",
                    "type": "multiple_choice",
                    "options": ["FLUSHALL disabled", "CONFIG disabled", "DEBUG disabled", "EVAL disabled", "None disabled"],
                    "help_text": "Disabling dangerous Redis commands reduces attack surface.",
                    "related_branch": "AccessControl"
                }
            ],
            "Elasticsearch": [
                {
                    "id": "elasticsearch_security_enabled",
                    "question": "Is Elasticsearch Security (X-Pack) enabled?",
                    "type": "single_choice",
                    "options": ["X-Pack Security enabled", "Open Distro Security", "Basic authentication only", "No security", "Unknown"],
                    "help_text": "Elasticsearch security features provide authentication and authorization.",
                    "related_branch": "AccessControl"
                },
                {
                    "id": "elasticsearch_tls_config",
                    "question": "How is Elasticsearch TLS configured?",
                    "type": "single_choice",
                    "options": ["TLS for all communications", "TLS for client connections only", "TLS for inter-node only", "No TLS", "Unknown"],
                    "help_text": "Elasticsearch TLS secures all communication channels.",
                    "related_branch": "Encryption"
                },
                {
                    "id": "elasticsearch_audit_logging",
                    "question": "Is Elasticsearch audit logging configured?",
                    "type": "single_choice",
                    "options": ["Comprehensive audit logging", "Basic access logging", "No audit logging", "Unknown"],
                    "help_text": "Elasticsearch audit logging tracks access and operations for security monitoring.",
                    "related_branch": "AuditLogging"
                }
            ]
        }
    
    def get_conditional_questionnaire(self, node_subtype: str, level: QuestionnaireLevel, 
                                    previous_responses: Dict[str, Any] = None) -> Tuple[List[Dict], bool]:
        """
        Get questionnaire with conditional questions based on previous responses
        
        Returns:
            Tuple of (questions_list, has_conditional_questions)
        """
        logger.info(f"Getting conditional questionnaire for {node_subtype} at {level.value} level")
        
        # Get base questionnaire
        base_questions = self.questionnaire_loader.get_questionnaire(node_subtype, level)
        if not base_questions:
            return [], False
        
        # Check if this is a node type that supports conditional questions
        if node_subtype.upper() not in ["API", "DATABASE"]:
            return base_questions, False
            
        # Add type selection question if not already present
        base_questions = self._ensure_type_selection_question(base_questions, node_subtype)
        
        # If we have previous responses, add conditional questions
        conditional_questions = []
        has_conditional = False
        
        if previous_responses:
            conditional_questions = self._get_conditional_questions(node_subtype, previous_responses)
            has_conditional = len(conditional_questions) > 0
        
        # Combine base and conditional questions
        all_questions = base_questions + conditional_questions
        
        return all_questions, has_conditional
    
    def _ensure_type_selection_question(self, questions: List[Dict], node_subtype: str) -> List[Dict]:
        """Ensure type selection question is present and at the beginning"""
        
        type_question_id = f"{node_subtype.lower()}_type"
        
        # Check if type question already exists
        existing_question = None
        for i, question in enumerate(questions):
            if question.get('id') == type_question_id:
                existing_question = questions.pop(i)
                break
        
        # Create or update type selection question
        if node_subtype.upper() == "API":
            type_question = existing_question or {
                "id": "api_type",
                "question": "What type of API is this?",
                "type": "single_choice",
                "options": ["REST API", "GraphQL API", "SOAP API", "gRPC API", "WebSocket API", "Other"],
                "help_text": "API type determines specific security considerations and implementation approaches.",
                "related_branch": "ApiSecurity",
                "is_conditional_trigger": True
            }
        elif node_subtype.upper() == "DATABASE":
            type_question = existing_question or {
                "id": "database_type",
                "question": "What type of database is this?",
                "type": "single_choice",
                "options": ["MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch", "SQL Server", "Oracle", "Other"],
                "help_text": "Database type determines specific security configurations and best practices.",
                "related_branch": "DatabaseSecurity",
                "is_conditional_trigger": True
            }
        else:
            return questions  # No type question needed
        
        # Insert type question at the beginning
        return [type_question] + questions
    
    def _get_conditional_questions(self, node_subtype: str, responses: Dict[str, Any]) -> List[Dict]:
        """Get conditional questions based on previous responses"""
        
        conditional_questions = []
        
        if node_subtype.upper() == "API":
            api_type = responses.get("api_type")
            if api_type and api_type in self.api_type_questions:
                conditional_questions = self.api_type_questions[api_type].copy()
                logger.info(f"Added {len(conditional_questions)} conditional questions for {api_type}")
        
        elif node_subtype.upper() == "DATABASE":
            db_type = responses.get("database_type") 
            if db_type and db_type in self.database_type_questions:
                conditional_questions = self.database_type_questions[db_type].copy()
                logger.info(f"Added {len(conditional_questions)} conditional questions for {db_type}")
        
        # Mark conditional questions
        for question in conditional_questions:
            question["is_conditional"] = True
            question["conditional_trigger"] = responses.get(f"{node_subtype.lower()}_type")
        
        return conditional_questions
    
    def is_conditional_trigger_question(self, question: Dict) -> bool:
        """Check if question triggers conditional questions"""
        return question.get("is_conditional_trigger", False)
    
    def get_next_conditional_questions(self, node_subtype: str, question_id: str, response: str) -> List[Dict]:
        """Get conditional questions triggered by a specific response"""
        
        if question_id == "api_type" and node_subtype.upper() == "API":
            return self.api_type_questions.get(response, [])
        elif question_id == "database_type" and node_subtype.upper() == "DATABASE":
            return self.database_type_questions.get(response, [])
        
        return []
    
    def detect_existing_nodes_on_canvas(self, canvas_nodes: List[Dict], node_type: str) -> List[Dict]:
        """
        Detect existing nodes of a specific type on the canvas
        
        Args:
            canvas_nodes: List of nodes currently on the canvas
            node_type: Type of node to detect (e.g., 'Database', 'API', 'WebApp')
            
        Returns:
            List of existing nodes of the specified type
        """
        existing_nodes = []
        
        for node in canvas_nodes:
            # Check both 'subtype' and 'type' fields for compatibility
            node_subtype = node.get('subtype', '').lower()
            node_type_field = node.get('type', '').lower()
            
            target_type = node_type.lower()
            
            if node_subtype == target_type or node_type_field == target_type:
                existing_nodes.append({
                    'id': node.get('id'),
                    'label': node.get('label', f"{node_type} Node"),
                    'subtype': node.get('subtype'),
                    'position': node.get('position', {}),
                    'data': node.get('data', {})
                })
        
        return existing_nodes
    
    def create_database_reuse_question(self, existing_db_nodes: List[Dict]) -> Dict:
        """
        Create a question for database node reuse when existing databases are detected
        
        Args:
            existing_db_nodes: List of existing database nodes on canvas
            
        Returns:
            Question dictionary for database reuse decision
        """
        if not existing_db_nodes:
            return None
            
        # Create options for each existing database plus "Create new"
        options = []
        option_descriptions = {}
        
        for db_node in existing_db_nodes:
            node_label = db_node.get('label', f"Database {db_node.get('id', '')}")
            node_id = db_node.get('id')
            options.append(f"Use existing: {node_label}")
            option_descriptions[f"Use existing: {node_label}"] = f"Connect to existing database node ({node_id}) - reduces complexity and maintains data consistency."
        
        options.append("Create new dedicated database")
        option_descriptions["Create new dedicated database"] = "Create a separate database node - provides isolation but increases infrastructure complexity."
        
        return {
            "id": "database_reuse_decision",
            "question": f"A Database node already exists on the canvas. Should this API use the same database or create a new one?",
            "type": "single_choice", 
            "options": options,
            "option_descriptions": option_descriptions,
            "help_text": "Database reuse reduces complexity but may create dependencies. New databases provide isolation.",
            "related_branch": "Database",
            "is_reuse_question": True,
            "existing_nodes": existing_db_nodes
        }
    
    def get_enhanced_conditional_questionnaire(self, node_subtype: str, level: QuestionnaireLevel,
                                             previous_responses: Dict[str, Any] = None,
                                             canvas_nodes: List[Dict] = None) -> Tuple[List[Dict], bool]:
        """
        Enhanced version that includes canvas node detection for reuse logic
        
        Args:
            node_subtype: Type of node (API, Database, etc.)
            level: Questionnaire complexity level
            previous_responses: Previous user responses
            canvas_nodes: Current nodes on the canvas for reuse detection
            
        Returns:
            Tuple of (questions_list, has_conditional_questions)
        """
        logger.info(f"Getting enhanced conditional questionnaire for {node_subtype} with canvas detection")
        
        # Get base questionnaire with conditional questions
        base_questions, has_conditional = self.get_conditional_questionnaire(
            node_subtype, level, previous_responses
        )
        
        # Add reuse logic for specific node types
        if canvas_nodes and node_subtype.upper() == "API":
            # Check for database dependency and existing database nodes
            if previous_responses and previous_responses.get('api_database_access') is True:
                existing_db_nodes = self.detect_existing_nodes_on_canvas(canvas_nodes, 'Database')
                
                if existing_db_nodes:
                    db_reuse_question = self.create_database_reuse_question(existing_db_nodes)
                    if db_reuse_question:
                        # Insert reuse question after the database access question
                        db_access_index = -1
                        for i, question in enumerate(base_questions):
                            if question.get('id') == 'api_database_access':
                                db_access_index = i + 1
                                break
                        
                        if db_access_index > 0:
                            base_questions.insert(db_access_index, db_reuse_question)
                            logger.info(f"Added database reuse question with {len(existing_db_nodes)} existing databases")
        
        return base_questions, has_conditional
    
    def process_reuse_decision(self, reuse_response: str, existing_nodes: List[Dict]) -> Dict:
        """
        Process the user's reuse decision and return connection information
        
        Args:
            reuse_response: User's choice from the reuse question
            existing_nodes: List of existing nodes that could be reused
            
        Returns:
            Dictionary with reuse decision details
        """
        if reuse_response.startswith("Use existing:"):
            # Extract node identifier from response
            for node in existing_nodes:
                node_label = node.get('label', f"Database {node.get('id', '')}")
                if node_label in reuse_response:
                    return {
                        "action": "reuse",
                        "target_node_id": node.get('id'),
                        "target_node": node,
                        "create_connection": True,
                        "message": f"Will connect to existing database: {node_label}"
                    }
        
        elif "Create new" in reuse_response:
            return {
                "action": "create_new",
                "target_node_id": None,
                "target_node": None,
                "create_connection": False,
                "message": "Will create a new dedicated database node"
            }
        
        return {
            "action": "unknown",
            "target_node_id": None,
            "target_node": None,
            "create_connection": False,
            "message": "Invalid reuse decision"
        }

# Global instance
conditional_questionnaire_engine = None

def get_conditional_questionnaire_engine() -> ConditionalQuestionnaireEngine:
    """Get the global conditional questionnaire engine instance"""
    global conditional_questionnaire_engine
    if conditional_questionnaire_engine is None:
        from questionnaire_loader import get_questionnaire_loader
        conditional_questionnaire_engine = ConditionalQuestionnaireEngine(get_questionnaire_loader())
    return conditional_questionnaire_engine