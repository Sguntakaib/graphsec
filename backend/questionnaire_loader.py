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
        if node_subtype not in self._cache:
            logger.warning(f"Node type {node_subtype} not found")
            return []
        
        questionnaires = self._cache[node_subtype]
        
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
    
    def get_metadata(self, node_subtype: str) -> Optional[QuestionnaireMetadata]:
        """Get metadata for a specific node type"""
        return self._metadata_cache.get(node_subtype)
    
    def get_all_levels_count(self, node_subtype: str) -> Dict[str, int]:
        """Get question count for all levels of a node type"""
        if node_subtype not in self._cache:
            return {}
        
        questionnaires = self._cache[node_subtype]
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