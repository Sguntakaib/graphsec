"""
Questionnaire Response Analyzer
Processes security questionnaire responses and integrates with vulnerability engine
"""

from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
from vulnerability_engine import vulnerability_engine, VulnerabilityAnalysisResult

logger = logging.getLogger(__name__)

class QuestionnaireAnalyzer:
    """Analyzes questionnaire responses and triggers vulnerability assessment"""
    
    def __init__(self):
        self.response_cache = {}  # Cache questionnaire responses
        
    def analyze_questionnaire_responses(self,
                                      node_id: str,
                                      node_type: str,
                                      questionnaire_responses: Dict[str, Any],
                                      node_position: Optional[Dict[str, float]] = None,
                                      force_refresh: bool = False) -> VulnerabilityAnalysisResult:
        """
        Analyze questionnaire responses and generate vulnerability assessment
        
        Args:
            node_id: ID of the node being analyzed
            node_type: Type of node (WebApp, API, Database)
            questionnaire_responses: Dictionary of question_id -> response mappings
            node_position: Position coordinates for vulnerability node placement
            force_refresh: Force re-analysis even if cached
            
        Returns:
            VulnerabilityAnalysisResult with identified vulnerabilities
        """
        
        # Cache the responses
        self.response_cache[node_id] = {
            "responses": questionnaire_responses,
            "node_type": node_type,
            "timestamp": datetime.now()
        }
        
        # Check if we need to refresh analysis
        if not force_refresh and node_id in vulnerability_engine.vulnerability_cache:
            cached_result = vulnerability_engine.vulnerability_cache[node_id]
            # Return cached result if recent (within 5 minutes)
            if (datetime.now() - cached_result.analysis_timestamp).seconds < 300:
                logger.info(f"Returning cached vulnerability analysis for node {node_id}")
                return cached_result
        
        logger.info(f"Analyzing questionnaire responses for {node_type} node {node_id}")
        logger.debug(f"Responses: {questionnaire_responses}")
        
        # Preprocess responses to standardize format
        processed_responses = self._preprocess_responses(questionnaire_responses, node_type)
        
        # Analyze completeness of responses
        completeness_score = self._calculate_completeness_score(processed_responses, node_type)
        
        # Use vulnerability engine to analyze and generate vulnerabilities
        vulnerability_result = vulnerability_engine.analyze_node_vulnerabilities(
            node_id=node_id,
            node_type=node_type,
            questionnaire_responses=processed_responses,
            node_position=node_position
        )
        
        # Enhance result with questionnaire analysis metadata
        vulnerability_result.recommendations.insert(0, 
            f"Questionnaire completeness: {completeness_score:.1f}% - Consider completing remaining questions for better security assessment"
        )
        
        logger.info(f"Generated {vulnerability_result.total_vulnerabilities} vulnerabilities for node {node_id}")
        return vulnerability_result
    
    def _preprocess_responses(self, responses: Dict[str, Any], node_type: str) -> Dict[str, Any]:
        """
        Preprocess questionnaire responses to standardize format and handle missing data
        
        Args:
            responses: Raw questionnaire responses
            node_type: Type of node for context-specific processing
            
        Returns:
            Processed responses dictionary
        """
        processed = {}
        
        for question_id, response in responses.items():
            # Handle None or empty responses
            if response is None or response == "":
                processed[question_id] = "Unknown"
                continue
            
            # Standardize string responses
            if isinstance(response, str):
                response = response.strip()
                
            # Handle boolean responses
            if isinstance(response, bool):
                response = "Yes" if response else "No"
                
            # Handle list responses (for multiple choice questions)
            if isinstance(response, list):
                if not response:
                    response = "None"
                elif len(response) == 1:
                    response = response[0]
                # Keep as list for multiple selections
                
            processed[question_id] = response
        
        # Add derived responses based on common patterns
        processed.update(self._derive_additional_responses(processed, node_type))
        
        return processed
    
    def _derive_additional_responses(self, responses: Dict[str, Any], node_type: str) -> Dict[str, Any]:
        """
        Derive additional response indicators based on existing responses
        
        Args:
            responses: Processed questionnaire responses
            node_type: Type of node
            
        Returns:
            Dictionary of derived responses
        """
        derived = {}
        
        if node_type == "WebApp":
            # Derive security posture indicators
            auth_method = responses.get("webapp_authentication_method", "Unknown")
            if auth_method in ["OAuth2/OIDC", "SAML", "Username/Password with MFA"]:
                derived["has_strong_auth"] = True
            else:
                derived["has_strong_auth"] = False
                
            https_enforcement = responses.get("webapp_https_enforcement", "Unknown")
            derived["https_secure"] = https_enforcement == "HTTPS only (HSTS enabled)"
            
            input_validation = responses.get("webapp_input_validation", "Unknown")
            derived["input_validation_adequate"] = input_validation == "Comprehensive server-side validation"
            
        elif node_type == "API":
            # Derive API security indicators
            api_auth = responses.get("api_authentication_method", "Unknown")
            derived["api_auth_strong"] = api_auth in ["OAuth2/JWT", "API Keys"]
            
            rate_limiting = responses.get("api_rate_limiting", "Unknown")
            derived["has_rate_limiting"] = rate_limiting != "No rate limiting"
            
        elif node_type == "Database":
            # Derive database security indicators
            db_auth = responses.get("database_authentication", "Unknown")
            derived["db_auth_strong"] = db_auth == "Strong authentication with MFA"
            
            encryption_rest = responses.get("database_encryption_at_rest", "Unknown")
            derived["data_encrypted"] = encryption_rest != "No encryption"
            
        return derived
    
    def _calculate_completeness_score(self, responses: Dict[str, Any], node_type: str) -> float:
        """
        Calculate questionnaire completeness score
        
        Args:
            responses: Questionnaire responses
            node_type: Type of node
            
        Returns:
            Completeness score as percentage (0-100)
        """
        # Get expected questions for node type
        expected_questions = self._get_expected_questions(node_type)
        
        if not expected_questions:
            return 100.0  # If no expected questions defined, assume complete
        
        # Count answered questions (not "Unknown" or empty)
        answered = 0
        for question_id in expected_questions:
            response = responses.get(question_id)
            if response and response != "Unknown" and response != "":
                answered += 1
        
        return (answered / len(expected_questions)) * 100.0
    
    def _get_expected_questions(self, node_type: str) -> List[str]:
        """
        Get list of expected question IDs for a node type
        
        Args:
            node_type: Type of node
            
        Returns:
            List of expected question IDs
        """
        webapp_questions = [
            "webapp_authentication_method",
            "webapp_input_validation", 
            "webapp_https_enforcement",
            "webapp_session_management",
            "webapp_error_handling",
            "webapp_logging_monitoring",
            "webapp_data_encryption",
            "webapp_security_headers"
        ]
        
        api_questions = [
            "api_authentication_method",
            "api_authorization_model",
            "api_rate_limiting",
            "api_input_validation",
            "api_https_enforcement",
            "api_error_handling",
            "api_logging_monitoring"
        ]
        
        database_questions = [
            "database_authentication",
            "database_encryption_at_rest",
            "database_encryption_in_transit",
            "database_access_control",
            "database_backup_strategy",
            "database_patch_management",
            "database_network_security",
            "database_logging"
        ]
        
        question_map = {
            "WebApp": webapp_questions,
            "API": api_questions,
            "Database": database_questions
        }
        
        return question_map.get(node_type, [])
    
    def get_response_summary(self, node_id: str) -> Optional[Dict[str, Any]]:
        """
        Get summary of questionnaire responses for a node
        
        Args:
            node_id: ID of the node
            
        Returns:
            Response summary or None if not found
        """
        if node_id not in self.response_cache:
            return None
            
        cached_data = self.response_cache[node_id]
        responses = cached_data["responses"]
        node_type = cached_data["node_type"]
        
        # Calculate summary statistics
        total_questions = len(self._get_expected_questions(node_type))
        answered_questions = len([r for r in responses.values() if r and r != "Unknown"])
        completeness = (answered_questions / total_questions * 100) if total_questions > 0 else 100
        
        # Categorize responses by security strength
        strong_responses = 0
        weak_responses = 0
        unknown_responses = 0
        
        for response in responses.values():
            if not response or response == "Unknown":
                unknown_responses += 1
            elif self._is_strong_response(response):
                strong_responses += 1
            else:
                weak_responses += 1
        
        return {
            "node_id": node_id,
            "node_type": node_type,
            "total_questions": total_questions,
            "answered_questions": answered_questions,
            "completeness_percentage": completeness,
            "strong_responses": strong_responses,
            "weak_responses": weak_responses,
            "unknown_responses": unknown_responses,
            "last_updated": cached_data["timestamp"]
        }
    
    def _is_strong_response(self, response: Any) -> bool:
        """
        Determine if a response indicates strong security posture
        
        Args:
            response: Questionnaire response
            
        Returns:
            True if response indicates strong security
        """
        if not response:
            return False
            
        response_str = str(response).lower()
        
        # Positive security indicators
        strong_indicators = [
            "oauth2", "saml", "mfa", "comprehensive", "automated", "encrypted",
            "https only", "secure", "strong", "advanced", "role-based",
            "parameterized", "hsts enabled", "fine-grained"
        ]
        
        return any(indicator in response_str for indicator in strong_indicators)
    
    def update_node_responses(self, 
                            node_id: str, 
                            updated_responses: Dict[str, Any],
                            node_position: Optional[Dict[str, float]] = None) -> VulnerabilityAnalysisResult:
        """
        Update questionnaire responses for a node and re-analyze vulnerabilities
        
        Args:
            node_id: ID of the node
            updated_responses: Updated questionnaire responses
            node_position: Position for vulnerability nodes
            
        Returns:
            Updated vulnerability analysis result
        """
        logger.info(f"Updating questionnaire responses for node {node_id}")
        
        # Get existing responses if available
        existing_data = self.response_cache.get(node_id, {})
        existing_responses = existing_data.get("responses", {})
        node_type = existing_data.get("node_type", "WebApp")  # Default to WebApp
        
        # Merge with updated responses
        merged_responses = {**existing_responses, **updated_responses}
        
        # Re-analyze with updated responses
        return self.analyze_questionnaire_responses(
            node_id=node_id,
            node_type=node_type,
            questionnaire_responses=merged_responses,
            node_position=node_position,
            force_refresh=True
        )

# Global questionnaire analyzer instance
questionnaire_analyzer = QuestionnaireAnalyzer()