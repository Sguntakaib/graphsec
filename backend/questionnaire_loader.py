"""
QUESTIONNAIRE LOADER SYSTEM
File-based questionnaire management for security modeling platform

This module provides:
1. YAML-based questionnaire loading
2. Automatic questionnaire validation
3. Dynamic questionnaire discovery
4. Caching for performance
"""

import os
import yaml
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class QuestionnaireLevel(str, Enum):
    BASIC = "basic"
    ADVANCED = "advanced"
    EXPERT = "expert"

@dataclass
class QuestionnaireMetadata:
    node_type: str
    node_subtype: str
    category: str
    description: str
    required_branches: List[str]
    dependencies: Dict[str, str]
    threat_intelligence: Dict[str, Any]
    risk_factors: Dict[str, float]

class QuestionnaireLoader:
    """Loads and manages questionnaires from YAML files"""
    
    def __init__(self, questionnaires_dir: str = None):
        if questionnaires_dir is None:
            self.questionnaires_dir = Path(__file__).parent / "questionnaires"
        else:
            self.questionnaires_dir = Path(questionnaires_dir)
        
        self._cache = {}
        self._metadata_cache = {}
        self._load_all_questionnaires()
    
    def _load_all_questionnaires(self):
        """Load all questionnaire files from the directory"""
        if not self.questionnaires_dir.exists():
            logger.error(f"Questionnaires directory does not exist: {self.questionnaires_dir}")
            return
        
        yaml_files = list(self.questionnaires_dir.glob("*.yaml"))
        logger.info(f"Loading {len(yaml_files)} questionnaire files")
        
        for yaml_file in yaml_files:
            try:
                node_subtype = yaml_file.stem.upper()
                self._load_questionnaire_file(yaml_file, node_subtype)
                logger.info(f"Loaded questionnaire for {node_subtype}")
            except Exception as e:
                logger.error(f"Failed to load questionnaire file {yaml_file}: {e}")
    
    def _load_questionnaire_file(self, file_path: Path, node_subtype: str):
        """Load a single questionnaire file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # Store questionnaires
        self._cache[node_subtype] = data.get('questionnaires', {})
        
        # Store metadata
        self._metadata_cache[node_subtype] = QuestionnaireMetadata(
            node_type=data.get('node_type', 'Asset'),
            node_subtype=data.get('node_subtype', node_subtype),
            category=data.get('category', 'Unknown'),
            description=data.get('description', f'{node_subtype} component'),
            required_branches=data.get('required_branches', []),
            dependencies=data.get('dependencies', {}),
            threat_intelligence=data.get('threat_intelligence', {}),
            risk_factors=data.get('risk_factors', {})
        )
        
        # Validate questionnaire structure
        self._validate_questionnaire(node_subtype, data.get('questionnaires', {}))
    
    def _validate_questionnaire(self, node_subtype: str, questionnaires: Dict):
        """Validate questionnaire structure"""
        required_fields = ['id', 'question', 'type', 'help_text', 'related_branch']
        valid_types = ['single_choice', 'multiple_choice', 'text', 'boolean', 'number']
        
        for level, questions in questionnaires.items():
            if not isinstance(questions, list):
                raise ValueError(f"Questions for {node_subtype}.{level} must be a list")
            
            for i, question in enumerate(questions):
                # Check required fields
                missing_fields = [field for field in required_fields if field not in question]
                if missing_fields:
                    raise ValueError(f"Question {i+1} in {node_subtype}.{level} missing fields: {missing_fields}")
                
                # Check question type
                if question.get('type') not in valid_types:
                    raise ValueError(f"Invalid question type '{question.get('type')}' in {node_subtype}.{level}")
                
                # Check options for choice questions
                if question.get('type') in ['single_choice', 'multiple_choice'] and not question.get('options'):
                    raise ValueError(f"Choice question without options in {node_subtype}.{level}")
    
    def get_supported_node_types(self) -> List[str]:
        """Get list of all supported node types"""
        return list(self._cache.keys())
    
    def get_questionnaire(self, node_subtype: str, level: QuestionnaireLevel) -> List[Dict]:
        """Get questionnaire for specific level with proper scaling"""
        # Handle case-insensitive lookup
        actual_key = None
        for key in self._cache.keys():
            if key.upper() == node_subtype.upper():
                actual_key = key
                break
        
        if actual_key is None:
            logger.warning(f"Node type {node_subtype} not found in cache. Available keys: {list(self._cache.keys())}")
            return []
        
        questionnaires = self._cache[actual_key]
        
        # If level exists in YAML, return it
        if level.value in questionnaires:
            return questionnaires[level.value]
        
        # If level doesn't exist, scale from basic level
        basic_questions = questionnaires.get('basic', [])
        if not basic_questions:
            return []
        
        return self._scale_questionnaire_for_level(basic_questions, level, node_subtype)
    
    def _scale_questionnaire_for_level(self, basic_questions: List[Dict], level: QuestionnaireLevel, node_subtype: str) -> List[Dict]:
        """Scale basic questionnaire to match the requested level"""
        if level == QuestionnaireLevel.BASIC:
            # Basic level should have 5-8 questions
            target_count = max(5, min(8, len(basic_questions)))
            return basic_questions[:target_count]
        
        scaled_questions = []
        
        # Start with enhanced versions of basic questions
        for question in basic_questions:
            scaled_question = question.copy()
            
            if level == QuestionnaireLevel.ADVANCED:
                # For advanced level, add more detailed help text and validation
                scaled_question['help_text'] = f"Advanced: {question.get('help_text', '')}"
                if question.get('type') == 'text':
                    scaled_question['validation'] = {'min_length': 50}
                elif question.get('type') in ['single_choice', 'multiple_choice']:
                    # Add more nuanced options if available
                    options = question.get('options', [])
                    if len(options) >= 3:
                        scaled_question['options'] = options + [{'value': 'other', 'label': 'Other (please specify)'}]
            
            elif level == QuestionnaireLevel.EXPERT:
                # For expert level, add comprehensive help and advanced validation
                scaled_question['help_text'] = f"Expert: {question.get('help_text', '')} Consider regulatory compliance, threat modeling, and risk assessment implications."
                if question.get('type') == 'text':
                    scaled_question['validation'] = {'min_length': 100, 'requires_justification': True}
                elif question.get('type') in ['single_choice', 'multiple_choice']:
                    # Add comprehensive options
                    options = question.get('options', [])
                    expert_options = options + [
                        {'value': 'custom_implementation', 'label': 'Custom implementation (requires detailed explanation)'},
                        {'value': 'regulatory_exception', 'label': 'Regulatory exception applies'},
                        {'value': 'risk_accepted', 'label': 'Risk formally accepted by management'}
                    ]
                    scaled_question['options'] = expert_options
                
                # Add expert-level metadata
                scaled_question['expert_considerations'] = [
                    'Regulatory compliance requirements',
                    'Threat landscape analysis',
                    'Business impact assessment',
                    'Technical debt implications'
                ]
            
            scaled_questions.append(scaled_question)
        
        # Generate additional questions to meet level requirements
        if level == QuestionnaireLevel.ADVANCED:
            # Advanced level should have 15-20 questions
            target_count = 18  # Aim for middle of range
            additional_needed = max(0, target_count - len(scaled_questions))
            scaled_questions.extend(self._generate_additional_questions(node_subtype, additional_needed, level))
        
        elif level == QuestionnaireLevel.EXPERT:
            # Expert level should have 25-30 questions  
            target_count = 28  # Aim for middle of range
            additional_needed = max(0, target_count - len(scaled_questions))
            scaled_questions.extend(self._generate_additional_questions(node_subtype, additional_needed, level))
        
        logger.info(f"Scaled {len(basic_questions)} questions to {len(scaled_questions)} questions from basic to {level.value} level for {node_subtype}")
        return scaled_questions
    
    def _generate_additional_questions(self, node_subtype: str, count: int, level: QuestionnaireLevel) -> List[Dict]:
        """Generate additional questions for advanced/expert levels"""
        if count <= 0:
            return []
        
        # Get metadata to understand the node type
        metadata = self.get_metadata(node_subtype)
        category = metadata.category if metadata else "Unknown"
        
        additional_questions = []
        
        # Generate questions based on common security patterns
        question_templates = self._get_question_templates_for_category(category, level)
        
        for i, template in enumerate(question_templates[:count]):
            question_id = f"{node_subtype.lower()}_{level.value}_gen_{i+1}"
            
            additional_question = {
                "id": question_id,
                "question": template["question"].format(node_type=node_subtype),
                "type": template["type"],
                "options": template.get("options", []),
                "help_text": template["help_text"].format(node_type=node_subtype),
                "related_branch": template["related_branch"],
                "generated": True,  # Mark as auto-generated
                "level": level.value
            }
            
            if level == QuestionnaireLevel.EXPERT:
                additional_question["expert_considerations"] = template.get("expert_considerations", [])
                additional_question["compliance_relevance"] = template.get("compliance_relevance", [])
            
            additional_questions.append(additional_question)
        
        return additional_questions
    
    def _get_question_templates_for_category(self, category: str, level: QuestionnaireLevel) -> List[Dict]:
        """Get question templates based on category and level"""
        
        # Common security question templates
        common_templates = [
            {
                "question": "What incident response procedures are in place for {node_type} security events?",
                "type": "single_choice",
                "options": ["Automated Response", "Manual Procedures", "Hybrid Approach", "No Procedures", "Unknown"],
                "help_text": "Proper incident response procedures are critical for {node_type} security.",
                "related_branch": "IncidentResponse",
                "expert_considerations": ["Response time requirements", "Escalation procedures", "Communication protocols"],
                "compliance_relevance": ["SOC2", "ISO27001", "GDPR"]
            },
            {
                "question": "How is access to {node_type} logged and monitored?",
                "type": "single_choice", 
                "options": ["Comprehensive Logging", "Basic Logging", "Minimal Logging", "No Logging", "Unknown"],
                "help_text": "Access logging is essential for {node_type} security monitoring.",
                "related_branch": "AuditLogging",
                "expert_considerations": ["Log retention policies", "SIEM integration", "Real-time alerting"],
                "compliance_relevance": ["PCI-DSS", "SOX", "HIPAA"]
            },
            {
                "question": "What backup and recovery procedures exist for {node_type}?",
                "type": "single_choice",
                "options": ["Automated Regular Backups", "Scheduled Backups", "Manual Backups", "No Backup", "Unknown"],
                "help_text": "Backup procedures ensure {node_type} data integrity and availability.",
                "related_branch": "Backup",
                "expert_considerations": ["RTO/RPO requirements", "Cross-region replication", "Backup encryption"],
                "compliance_relevance": ["SOC2", "ISO27001"]
            },
            {
                "question": "How is {node_type} configuration managed and validated?",
                "type": "single_choice",
                "options": ["Infrastructure as Code", "Configuration Management Tools", "Manual Configuration", "Ad-hoc Changes", "Unknown"],
                "help_text": "Proper configuration management reduces {node_type} security risks.",
                "related_branch": "ConfigurationManagement",
                "expert_considerations": ["Configuration drift detection", "Change approval process", "Version control"],
                "compliance_relevance": ["SOC2", "ISO27001", "CIS Controls"]
            },
            {
                "question": "What vulnerability management processes are applied to {node_type}?",
                "type": "single_choice",
                "options": ["Automated Scanning & Patching", "Regular Scanning", "Periodic Assessment", "No Process", "Unknown"],
                "help_text": "Vulnerability management is crucial for {node_type} security posture.",
                "related_branch": "VulnerabilityManagement",
                "expert_considerations": ["Patch testing procedures", "Emergency patching", "Risk-based prioritization"],
                "compliance_relevance": ["PCI-DSS", "SOC2", "ISO27001"]
            }
        ]
        
        # Category-specific templates
        category_templates = {
            "Cloud Infrastructure": [
                {
                    "question": "How is {node_type} integrated with cloud security services?",
                    "type": "multiple_choice",
                    "options": ["AWS Security Hub", "Azure Security Center", "GCP Security Command Center", "Third-party CSPM", "None"],
                    "help_text": "Cloud security integration enhances {node_type} threat detection.",
                    "related_branch": "CloudSecurity",
                    "expert_considerations": ["Multi-cloud security", "Compliance automation", "Cost optimization"],
                    "compliance_relevance": ["SOC2", "ISO27001", "CSA CCM"]
                },
                {
                    "question": "What cloud governance policies apply to {node_type}?",
                    "type": "text",
                    "help_text": "Cloud governance ensures {node_type} compliance and security standards.",
                    "related_branch": "CloudGovernance",
                    "expert_considerations": ["Policy automation", "Exception handling", "Audit trails"],
                    "compliance_relevance": ["SOC2", "ISO27001", "GDPR"]
                }
            ],
            "Data Storage": [
                {
                    "question": "What data classification scheme is applied to {node_type}?",
                    "type": "single_choice",
                    "options": ["Automated Classification", "Manual Classification", "Basic Labels", "No Classification", "Unknown"],
                    "help_text": "Data classification drives {node_type} security controls.",
                    "related_branch": "DataClassification",
                    "expert_considerations": ["Sensitive data identification", "Retention policies", "Cross-border transfers"],
                    "compliance_relevance": ["GDPR", "CCPA", "HIPAA"]
                },
                {
                    "question": "How is data integrity verified for {node_type}?",
                    "type": "single_choice",
                    "options": ["Cryptographic Hashing", "Digital Signatures", "Checksums", "No Verification", "Unknown"],
                    "help_text": "Data integrity verification protects {node_type} from tampering.",
                    "related_branch": "DataIntegrity",
                    "expert_considerations": ["Hash algorithm selection", "Key management", "Verification frequency"],
                    "compliance_relevance": ["PCI-DSS", "SOX", "FDA 21 CFR Part 11"]
                }
            ],
            "Security Services": [
                {
                    "question": "How is {node_type} threat intelligence integrated?",
                    "type": "single_choice",
                    "options": ["Real-time Feeds", "Daily Updates", "Weekly Updates", "No Integration", "Unknown"],
                    "help_text": "Threat intelligence enhances {node_type} detection capabilities.",
                    "related_branch": "ThreatIntelligence",
                    "expert_considerations": ["Feed quality assessment", "False positive management", "Attribution analysis"],
                    "compliance_relevance": ["NIST Cybersecurity Framework", "ISO27001"]
                }
            ]
        }
        
        # Combine common and category-specific templates
        templates = common_templates.copy()
        if category in category_templates:
            templates.extend(category_templates[category])
        
        # Add level-specific complexity
        if level == QuestionnaireLevel.EXPERT:
            expert_templates = [
                {
                    "question": "What threat modeling methodologies have been applied to {node_type}?",
                    "type": "multiple_choice",
                    "options": ["STRIDE", "PASTA", "TRIKE", "OCTAVE", "Custom Methodology", "None"],
                    "help_text": "Threat modeling provides systematic {node_type} security analysis.",
                    "related_branch": "ThreatModeling",
                    "expert_considerations": ["Model maintenance", "Threat landscape evolution", "Risk quantification"],
                    "compliance_relevance": ["ISO27001", "NIST Cybersecurity Framework"]
                },
                {
                    "question": "How is {node_type} security measured and reported to stakeholders?",
                    "type": "text",
                    "help_text": "Security metrics enable {node_type} risk management and decision making.",
                    "related_branch": "SecurityMetrics",
                    "expert_considerations": ["KPI selection", "Dashboard design", "Executive reporting"],
                    "compliance_relevance": ["SOC2", "ISO27001", "Board oversight requirements"]
                }
            ]
            templates.extend(expert_templates)
        
        return templates
    
    def get_metadata(self, node_subtype: str) -> Optional[QuestionnaireMetadata]:
        """Get metadata for a specific node type"""
        # Handle case-insensitive lookup
        for key in self._metadata_cache.keys():
            if key.upper() == node_subtype.upper():
                return self._metadata_cache[key]
        return None
    
    def get_all_levels_count(self, node_subtype: str) -> Dict[str, int]:
        """Get question count for all levels of a node type"""
        # Handle case-insensitive lookup
        actual_key = None
        for key in self._cache.keys():
            if key.upper() == node_subtype.upper():
                actual_key = key
                break
        
        if actual_key is None:
            return {}
        
        questionnaires = self._cache[actual_key]
        return {
            level: len(questions) 
            for level, questions in questionnaires.items()
        }
    
    def reload(self):
        """Reload all questionnaires from files"""
        self._cache.clear()
        self._metadata_cache.clear()
        self._load_all_questionnaires()
    
    def create_questionnaire_response(self, node_subtype: str, level: QuestionnaireLevel) -> Dict:
        """Create a formatted questionnaire response"""
        questions = self.get_questionnaire(node_subtype, level)
        metadata = self.get_metadata(node_subtype)
        
        if not questions:
            return {
                "error": f"Questionnaire not found for {node_subtype} at {level.value} level",
                "available_levels": list(self._cache.get(node_subtype, {}).keys()) if node_subtype in self._cache else [],
                "supported_types": self.get_supported_node_types()
            }
        
        # Calculate estimated time (assuming 30 seconds per question on average)
        estimated_time = len(questions) * 30
        
        return {
            "node_subtype": node_subtype,
            "questionnaire_level": level.value,
            "questions": questions,
            "question_count": len(questions),
            "estimated_time": f"{estimated_time // 60} minutes" if estimated_time >= 60 else f"{estimated_time} seconds",
            "metadata": {
                "category": metadata.category if metadata else "Unknown",
                "description": metadata.description if metadata else f"{node_subtype} security questionnaire",
                "required_branches": metadata.required_branches if metadata else []
            }
        }

# Global instance
questionnaire_loader = QuestionnaireLoader()

def get_questionnaire_loader() -> QuestionnaireLoader:
    """Get the global questionnaire loader instance"""
    return questionnaire_loader