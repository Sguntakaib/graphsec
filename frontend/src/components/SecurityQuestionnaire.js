import React, { useState, useEffect, useRef } from 'react';
import { 
  Shield, 
  AlertTriangle, 
  CheckCircle, 
  XCircle, 
  HelpCircle, 
  ChevronRight,
  ChevronLeft,
  Save,
  RefreshCw,
  Clock,
  Plus,
  Target,
  Flag,
  ExternalLink,
  BookOpen
} from 'lucide-react';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from './ui/tooltip';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from './ui/alert-dialog';

const SecurityQuestionnaire = ({ 
  nodeSubtype, 
  onComplete, 
  onCancel, 
  existingValues = {},
  isVisible = false,
  sourceNode = null,
  currentNodes = [],
  onCreateLinkedNodes = null,
  resumeFromPromptIndex = null,
  partialAnswers = null,
  getIncompleteDependencies = null
}) => {
  const [prompts, setPrompts] = useState([]);
  const [currentPromptIndex, setCurrentPromptIndex] = useState(0);
  const [answers, setAnswers] = useState(existingValues);
  const [triggeredDependencies, setTriggeredDependencies] = useState(new Set());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [validation, setValidation] = useState(null);
  
  // Phase 2 enhancements
  const [markedForLater, setMarkedForLater] = useState(new Set());
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [showUnsavedDialog, setShowUnsavedDialog] = useState(false);
  const [createdDependencies, setCreatedDependencies] = useState([]);
  const [completionSummary, setCompletionSummary] = useState(null);
  const initialAnswersRef = useRef({});

  useEffect(() => {
    if (isVisible && nodeSubtype) {
      // Check if we're resuming a parent questionnaire
      if (resumeFromPromptIndex !== null && partialAnswers) {
        console.log(`🔄 Resuming parent questionnaire from prompt ${resumeFromPromptIndex}`);
        setCurrentPromptIndex(resumeFromPromptIndex);
        setAnswers(partialAnswers);
        setValidation(null);
        setError(null);
        fetchSecurityPrompts();
      } else {
        // Reset state when opening questionnaire for a new node
        setCurrentPromptIndex(0);
        setAnswers(existingValues);
        setValidation(null);
        setError(null);
        fetchSecurityPrompts();
      }
      
      // Phase 2: Initialize tracking
      initialAnswersRef.current = { ...existingValues };
      setHasUnsavedChanges(false);
      setMarkedForLater(new Set());
      setCreatedDependencies([]);
      setCompletionSummary(null);
    }
  }, [isVisible, nodeSubtype, resumeFromPromptIndex, partialAnswers]);

  // Additional validation for resumption index - only after prompts are properly loaded
  useEffect(() => {
    if (prompts.length > 0 && resumeFromPromptIndex !== null && !loading) {
      // Only clamp if we're sure the prompts are fully loaded and it's still beyond length
      if (resumeFromPromptIndex >= prompts.length) {
        console.log(`⚠️ Resume index ${resumeFromPromptIndex} is beyond questionnaire length ${prompts.length}, clamping to last question`);
        setCurrentPromptIndex(prompts.length - 1);
      } else {
        // If resume index is valid, use it directly
        console.log(`✅ Resume index ${resumeFromPromptIndex} is valid for questionnaire length ${prompts.length}`);
        setCurrentPromptIndex(resumeFromPromptIndex);
      }
    }
  }, [prompts.length, resumeFromPromptIndex, loading]);

  // Additional effect to reset state when the modal is closed and reopened
  useEffect(() => {
    if (isVisible && resumeFromPromptIndex === null) {
      // Only reset to 0 if we're not resuming from a specific index
      setCurrentPromptIndex(0);
      // Reset triggered dependencies for new questionnaire session
      setTriggeredDependencies(new Set());
      console.log('🔄 Reset triggered dependencies for new questionnaire session');
    }
  }, [isVisible, resumeFromPromptIndex]);

  const fetchSecurityPrompts = async () => {
    try {
      setLoading(true);
      
      // Use conditional questionnaires for API and Database to enable enhanced vulnerability rules
      let response;
      if (nodeSubtype === 'WebApp') {
        console.log('🎯 Using comprehensive WebApp questionnaire system');
        response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/questionnaires/WebApp?level=basic`);
      } else if (nodeSubtype === 'API') {
        console.log('🚀 Using CONDITIONAL API questionnaire system to enable enhanced vulnerability rules');
        // Use conditional questionnaire to collect api_type, protocol-specific fields
        const responsesParam = currentQuestionnaireAnswers && Object.keys(currentQuestionnaireAnswers).length > 0 
          ? `&responses=${encodeURIComponent(JSON.stringify(currentQuestionnaireAnswers))}` 
          : '';
        response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/questionnaires/API/conditional?level=basic${responsesParam}`);
      } else if (nodeSubtype === 'Database') {
        console.log('🚀 Using CONDITIONAL Database questionnaire system to enable enhanced vulnerability rules');
        // Use conditional questionnaire to collect database_type, engine-specific fields
        const responsesParam = currentQuestionnaireAnswers && Object.keys(currentQuestionnaireAnswers).length > 0 
          ? `&responses=${encodeURIComponent(JSON.stringify(currentQuestionnaireAnswers))}` 
          : '';
        response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/questionnaires/Database/conditional?level=basic${responsesParam}`);
      } else if (nodeSubtype === 'Backup') {
        console.log('🎯 Using comprehensive Backup questionnaire system');
        response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/questionnaires/Backup?level=basic`);
      } else if (nodeSubtype === 'Monitoring') {
        console.log('🎯 Using comprehensive Monitoring questionnaire system');
        response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/questionnaires/Monitoring?level=basic`);
      } else {
        console.log('🎯 Falling back to intelligent-nodes system for', nodeSubtype);
        response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/intelligent-nodes/${nodeSubtype}/prompts`);
      }
      
      if (!response.ok) {
        throw new Error(`Failed to fetch prompts: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      if (nodeSubtype === 'WebApp' || nodeSubtype === 'API' || nodeSubtype === 'Database' || nodeSubtype === 'Backup' || nodeSubtype === 'Monitoring') {
        // Comprehensive questionnaire response format
        setPrompts(data.prompts || []);
        console.log(`🎯 Loaded ${data.total_questions} comprehensive ${nodeSubtype} questions (${data.level} level)`);
        if (data.completion_required) {
          console.log('⚠️ All questions must be answered before vulnerability analysis');
        }
      } else {
        // Legacy intelligent-nodes response format
        setPrompts(data.prompts || []);
      }
      
      setError(null);
    } catch (err) {
      console.error('Error fetching security prompts:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Map questionnaire prompt types to correct SecurityBranch enum values based on webapp.yaml and api.yaml
  const mapPromptTypeToSecurityBranch = (promptId, relatedBranch) => {
    // Updated mapping to match backend SecurityBranchType enum values exactly
    const branchMappings = {
      // Direct branch mappings (primary)
      'Login': 'Login',
      'API': 'ApiSecurity',  // Map to API_SECURITY enum value
      'Database': 'Database',
      'InputValidation': 'InputValidation',
      'WAF': 'WAF',
      'Encryption': 'Encryption',
      'AccessControl': 'AccessControl',
      'Authentication': 'Authentication',
      'Authorization': 'Authorization',
      'RateLimiting': 'RateLimiting',
      'CORS': 'CORS',
      'DataClassification': 'DataClassification',
      'Backup': 'Backup',
      'Monitoring': 'Monitoring',
      'Logging': 'Logging',
      'Deployment': 'Deployment',
      'CloudSecurity': 'CloudSecurity',
      'NetworkSecurity': 'NetworkSecurity',
      'Infrastructure': 'Infrastructure',
      'ErrorHandling': 'ErrorHandling',
      'Compliance': 'Compliance',
      'SessionManagement': 'SessionManagement',
      'CSP': 'CSP',
      'ExternalService': 'ExternalService',
      
      // Legacy mappings for YAML prompt IDs
      'login': 'Authentication',
      'authentication': 'Authentication',
      'input_validation': 'InputValidation',
      'validation': 'InputValidation',
      'https': 'Encryption',  // Map SSL/TLS to Encryption
      'ssl': 'Encryption',
      'tls': 'Encryption',
      'data_encryption': 'Encryption',
      'database_connection': 'Database',
      'database': 'Database',
      'api_endpoints': 'ApiSecurity',  // Map to correct API_SECURITY value
      'api': 'ApiSecurity',
      'api_security': 'ApiSecurity',
      'session_management': 'SessionManagement',
      'sessionmanagement': 'SessionManagement',
      'error_handling': 'ErrorHandling',
      'errorhandling': 'ErrorHandling',
      'logging': 'Logging',
      'audit_logging': 'AuditLogging',
      'csp': 'CSP',
      'authorization': 'Authorization',
      'rate_limiting': 'RateLimiting',
      'monitoring': 'Monitoring',
      'compliance': 'Compliance',
      'backup': 'Backup',
      'encryption': 'Encryption'
    };

    // First try direct related_branch mapping (most reliable)
    if (relatedBranch && branchMappings[relatedBranch]) {
      return branchMappings[relatedBranch];
    }

    // Then try prompt ID mapping
    if (branchMappings[promptId]) {
      return branchMappings[promptId];
    }

    // Try to extract from prompt ID patterns for YAML questions
    if (promptId.includes('authentication')) return 'Authentication';
    if (promptId.includes('authorization')) return 'Authorization';
    if (promptId.includes('input_validation')) return 'InputValidation';
    if (promptId.includes('https') || promptId.includes('data_encryption') || promptId.includes('ssl') || promptId.includes('tls')) return 'Encryption';
    if (promptId.includes('database')) return 'Database';
    if (promptId.includes('api_endpoints') || promptId.includes('api_security')) return 'ApiSecurity';
    if (promptId.includes('session_management')) return 'SessionManagement';
    if (promptId.includes('error_handling')) return 'ErrorHandling';
    if (promptId.includes('logging')) return 'Logging';
    if (promptId.includes('security_headers')) return 'CSP';
    if (promptId.includes('rate_limiting')) return 'RateLimiting';
    if (promptId.includes('monitoring')) return 'Monitoring';
    if (promptId.includes('backup')) return 'Backup';
    if (promptId.includes('compliance')) return 'Compliance';

    // Default fallback - use related_branch as PascalCase if available
    if (relatedBranch) {
      return relatedBranch;
    }

    // Final fallback
    return 'Authentication';
  };

  const validateAnswers = async () => {
    try {
      const branches = prompts.map(prompt => ({
        id: prompt.id,
        name: prompt.related_branch || prompt.id,
        type: mapPromptTypeToSecurityBranch(prompt.id, prompt.related_branch),
        required: true,
        completed: answers[prompt.id] !== undefined && 
                  answers[prompt.id] !== null && 
                  answers[prompt.id] !== '' &&
                  answers[prompt.id] !== 'Unknown',
        value: answers[prompt.id],
        description: prompt.help_text || prompt.question
      }));

      console.log('🔍 Sending validation data to backend:', {
        nodeSubtype,
        branches: branches.map(b => ({
          id: b.id,
          type: b.type,
          completed: b.completed,
          value: b.value
        })),
        answersProvided: Object.keys(answers).length,
        completedBranchesCount: branches.filter(b => b.completed).length
      });

      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/intelligent-nodes/${nodeSubtype}/validate-completeness`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(branches)
        }
      );

      if (response.ok) {
        const validationData = await response.json();
        console.log('🔍 Backend validation response:', validationData);
        setValidation(validationData.validation);
        return validationData;
      } else {
        console.error('❌ Validation API error:', response.status, await response.text());
      }
    } catch (err) {
      console.error('Validation error:', err);
    }
    return null;
  };

  const handleAnswerChange = (promptId, value) => {
    setAnswers(prev => {
      const newAnswers = { ...prev, [promptId]: value };
      
      // Phase 2: Track unsaved changes
      const hasChanges = JSON.stringify(newAnswers) !== JSON.stringify(initialAnswersRef.current);
      setHasUnsavedChanges(hasChanges);
      
      return newAnswers;
    });
  };

  // Phase 2: Get dependency trigger info for current question
  const getDependencyTriggerInfo = (prompt) => {
    const dependencyTriggers = {
      'webapp_api_endpoints': { nodeType: 'API', condition: 'Yes/True' },
      'webapp_database_connection': { nodeType: 'Database', condition: 'Yes/True' },
      'database_backup_enabled': { nodeType: 'Backup', condition: 'Yes/True' },
      'database_monitoring_integration': { nodeType: 'Monitoring', condition: 'Yes/True' },
      'api_database_access': { nodeType: 'Database', condition: 'Yes/True' },
      'api_external_services': { nodeType: 'ExternalService', condition: 'Yes/True' }
    };
    
    return dependencyTriggers[prompt.id] || null;
  };

  // Phase 2: Mark question for later
  const handleMarkForLater = () => {
    setMarkedForLater(prev => new Set([...prev, currentPromptIndex]));
    if (currentPromptIndex < prompts.length - 1) {
      setCurrentPromptIndex(currentPromptIndex + 1);
    }
  };

  // Phase 2: Enhanced close handler with unsaved changes check
  const handleClose = () => {
    if (hasUnsavedChanges) {
      setShowUnsavedDialog(true);
    } else {
      onCancel();
    }
  };

  const handleNext = async () => {
    // Check if current question is a dependency-triggering question
    const currentPrompt = prompts[currentPromptIndex];
    const currentAnswer = answers[currentPrompt.id];
    
    // Define dependency-triggering questions that should immediately create nodes
    const dependencyTriggers = {
      'webapp_api_endpoints': 'API',
      'webapp_database_connection': 'Database',
      'database_backup_enabled': 'Backup',
      'database_monitoring_integration': 'Monitoring',
      'api_database_access': 'Database',
      'api_external_services': 'ExternalService'
    };
    
    // If current question triggers a dependency and answer is Yes/True
    if (dependencyTriggers[currentPrompt.id] && (currentAnswer === true || currentAnswer === 'Yes')) {
      const specificDependency = dependencyTriggers[currentPrompt.id];
      const dependencyKey = `${currentPrompt.id}-${specificDependency}`;
      
      // Check if this dependency has already been triggered to prevent duplicates
      if (triggeredDependencies.has(dependencyKey)) {
        console.log(`⚠️ Dependency ${currentPrompt.id} → ${specificDependency} already triggered, skipping duplicate`);
        // Continue to next question without triggering dependency again
        if (currentPromptIndex < prompts.length - 1) {
          setCurrentPromptIndex(currentPromptIndex + 1);
        }
        return;
      }
      
      console.log(`🎯 Dependency trigger detected for ${currentPrompt.id} → ${specificDependency}`);
      
      // Mark this dependency as triggered to prevent duplicates
      setTriggeredDependencies(prev => new Set([...prev, dependencyKey]));
      
      // Only trigger the SPECIFIC dependency that was just answered, not all dependencies
      console.log(`🎯 Triggering only specific dependency: ${specificDependency}`);
      
      const allAnswersWithCurrent = {
        ...answers,
        [currentPrompt.id]: currentAnswer
      };
      
      // Trigger dependent node creation immediately for ONLY the specific dependency
      if (onComplete) {
        onComplete({
          answers: allAnswersWithCurrent, // Include current answer with all previous answers
          dependentNodes: [specificDependency], // Only the specific dependency, not all possible ones
          triggerDependentQuestionnaires: true,
          partialCompletion: true, // Flag to indicate this is not final completion
          currentPromptIndex: currentPromptIndex + 1 // Continue questionnaire after dependencies
        });
        return; // Don't proceed to next question yet - let the dependency flow handle it
      }
    }
    
    // Normal next question flow
    if (currentPromptIndex < prompts.length - 1) {
      setCurrentPromptIndex(currentPromptIndex + 1);
    }
  };

  const handlePrevious = () => {
    if (currentPromptIndex > 0) {
      setCurrentPromptIndex(currentPromptIndex - 1);
    }
  };

  const handleComplete = async () => {
    const validationResult = await validateAnswers();
    
    if (validationResult) {
      // Check for conditional dependencies
      let dependentNodes = [];
      try {
        const dependencyResponse = await fetch(
          `${process.env.REACT_APP_BACKEND_URL}/api/intelligent-nodes/${nodeSubtype}/check-dependencies`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({ answers })
          }
        );
        
        if (dependencyResponse.ok) {
          const dependencyData = await dependencyResponse.json();
          const allDependentNodes = dependencyData.dependent_nodes || [];
          
          // Filter out dependencies that are already COMPLETED if filter function is provided
          if (getIncompleteDependencies && sourceNode?.id) {
            dependentNodes = getIncompleteDependencies(sourceNode.id, allDependentNodes);
            console.log('🎯 Dependency check result (filtered):', {
              nodeSubtype,
              answers,
              allDependentNodes,
              incompleteDependentNodes: dependentNodes,
              triggerRequired: dependentNodes.length > 0
            });
          } else {
            dependentNodes = allDependentNodes;
            console.log('🎯 Dependency check result (unfiltered):', {
              nodeSubtype,
              answers,
              dependentNodes,
              triggerRequired: dependentNodes.length > 0
            });
          }
        }
      } catch (error) {
        console.error('Error checking dependencies:', error);
      }

      // Phase 2: Generate completion summary
      const answeredQuestions = Object.keys(answers).length;
      const securityControls = Object.entries(answers)
        .filter(([_, value]) => value === true || value === 'Yes' || (typeof value === 'string' && value !== 'No' && value !== 'False'))
        .map(([key, _]) => prompts.find(p => p.id === key)?.question || key);

      const summary = {
        nodeType: nodeSubtype,
        questionsAnswered: answeredQuestions,
        totalQuestions: prompts.length,
        completionPercentage: validationResult.validation?.completion_percentage || 0,
        dependenciesCreated: dependentNodes,
        securityControlsEnabled: securityControls.slice(0, 5), // Top 5 controls
        markedForLaterCount: markedForLater.size,
        recommendations: validationResult.recommendations?.slice(0, 3) || [] // Top 3 recommendations
      };

      setCompletionSummary(summary);

      // Trigger smart node creation if callback is provided
      let smartNodeResult = null;
      if (onCreateLinkedNodes && sourceNode && currentNodes) {
        try {
          smartNodeResult = await onCreateLinkedNodes(sourceNode.id, nodeSubtype, answers, currentNodes);
        } catch (error) {
          console.error('Error creating linked nodes:', error);
        }
      }

      onComplete({
        answers,
        validation: validationResult.validation,
        recommendations: validationResult.recommendations,
        smartNodeResult,
        dependentNodes,
        triggerDependentQuestionnaires: dependentNodes.length > 0,
        isActualCompletion: true, // Flag to indicate this was a real completion button click
        completionSummary: summary // Phase 2: Include completion summary
      });
    }
  };

  const renderPromptInput = (prompt) => {
    const currentValue = answers[prompt.id];

    switch (prompt.type) {
      case 'single_choice':
        return (
          <div className="space-y-2">
            {prompt.options?.map((option, index) => {
              const optionDescription = prompt.option_descriptions?.[option];
              const optionElement = (
                <label 
                  key={index}
                  className="flex items-center space-x-3 p-3 border border-gray-600 rounded-lg hover:bg-gray-700 cursor-pointer transition-colors"
                >
                  <input
                    type="radio"
                    name={prompt.id}
                    value={option}
                    checked={currentValue === option}
                    onChange={(e) => handleAnswerChange(prompt.id, e.target.value)}
                    className="text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-white flex-grow">{option}</span>
                  {optionDescription && (
                    <HelpCircle className="h-4 w-4 text-gray-400 flex-shrink-0" />
                  )}
                </label>
              );

              if (optionDescription) {
                return (
                  <Tooltip key={index}>
                    <TooltipTrigger asChild>
                      {optionElement}
                    </TooltipTrigger>
                    <TooltipContent side="right" className="z-[60] max-w-xs bg-gray-900 border-gray-700 text-gray-100">
                      <p className="text-sm">{optionDescription}</p>
                    </TooltipContent>
                  </Tooltip>
                );
              }
              
              return optionElement;
            })}
          </div>
        );

      case 'multiple_choice':
        return (
          <div className="space-y-2">
            {prompt.options?.map((option, index) => {
              const selectedOptions = Array.isArray(currentValue) ? currentValue : [];
              const optionDescription = prompt.option_descriptions?.[option];
              const optionElement = (
                <label 
                  key={index}
                  className="flex items-center space-x-3 p-3 border border-gray-600 rounded-lg hover:bg-gray-700 cursor-pointer transition-colors"
                >
                  <input
                    type="checkbox"
                    value={option}
                    checked={selectedOptions.includes(option)}
                    onChange={(e) => {
                      const newSelection = e.target.checked
                        ? [...selectedOptions, option]
                        : selectedOptions.filter(item => item !== option);
                      handleAnswerChange(prompt.id, newSelection);
                    }}
                    className="text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-white flex-grow">{option}</span>
                  {optionDescription && (
                    <HelpCircle className="h-4 w-4 text-gray-400 flex-shrink-0" />
                  )}
                </label>
              );

              if (optionDescription) {
                return (
                  <Tooltip key={index}>
                    <TooltipTrigger asChild>
                      {optionElement}
                    </TooltipTrigger>
                    <TooltipContent side="right" className="z-[60] max-w-xs bg-gray-900 border-gray-700 text-gray-100">
                      <p className="text-sm">{optionDescription}</p>
                    </TooltipContent>
                  </Tooltip>
                );
              }

              return optionElement;
            })}
          </div>
        );

      case 'boolean':
        return (
          <div className="flex space-x-4">
            <label className="flex items-center space-x-2 p-3 border border-gray-600 rounded-lg hover:bg-gray-700 cursor-pointer transition-colors">
              <input
                type="radio"
                name={prompt.id}
                value="true"
                checked={currentValue === true || currentValue === 'true'}
                onChange={() => handleAnswerChange(prompt.id, true)}
                className="text-green-600 focus:ring-green-500"
              />
              <CheckCircle className="h-5 w-5 text-green-400" />
              <span className="text-white">Yes</span>
            </label>
            <label className="flex items-center space-x-2 p-3 border border-gray-600 rounded-lg hover:bg-gray-700 cursor-pointer transition-colors">
              <input
                type="radio"
                name={prompt.id}
                value="false"
                checked={currentValue === false || currentValue === 'false'}
                onChange={() => handleAnswerChange(prompt.id, false)}
                className="text-red-600 focus:ring-red-500"
              />
              <XCircle className="h-5 w-5 text-red-400" />
              <span className="text-white">No</span>
            </label>
          </div>
        );

      case 'text':
        return (
          <input
            type="text"
            value={currentValue || ''}
            onChange={(e) => handleAnswerChange(prompt.id, e.target.value)}
            placeholder="Enter your answer..."
            className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        );

      case 'number':
        return (
          <input
            type="number"
            value={currentValue || ''}
            onChange={(e) => handleAnswerChange(prompt.id, parseFloat(e.target.value))}
            placeholder="Enter a number..."
            className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        );

      default:
        return (
          <div className="text-gray-400 italic">
            Unsupported prompt type: {prompt.type}
          </div>
        );
    }
  };

  if (!isVisible) return null;

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-gray-800 rounded-lg p-6 flex items-center space-x-4">
          <RefreshCw className="h-6 w-6 text-blue-400 animate-spin" />
          <span className="text-white">Loading security questionnaire...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-gray-800 rounded-lg p-6 max-w-md">
          <div className="flex items-center space-x-3 mb-4">
            <XCircle className="h-6 w-6 text-red-400" />
            <h3 className="text-lg font-semibold text-white">Error Loading Questionnaire</h3>
          </div>
          <p className="text-gray-300 mb-4">{error}</p>
          <div className="flex space-x-3">
            <button
              onClick={fetchSecurityPrompts}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Retry
            </button>
            <button
              onClick={onCancel}
              className="flex-1 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (prompts.length === 0) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-gray-800 rounded-lg p-6 max-w-md">
          <div className="flex items-center space-x-3 mb-4">
            <Shield className="h-6 w-6 text-yellow-400" />
            <h3 className="text-lg font-semibold text-white">No Security Prompts</h3>
          </div>
          <p className="text-gray-300 mb-4">
            No security questionnaire is available for {nodeSubtype} nodes yet.
          </p>
          <button
            onClick={onCancel}
            className="w-full px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            Continue
          </button>
        </div>
      </div>
    );
  }

  const currentPrompt = prompts[currentPromptIndex];
  const progressPercentage = ((currentPromptIndex + 1) / prompts.length) * 100;
  const answeredCount = Object.keys(answers).length;

  return (
    <TooltipProvider>
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gray-800 rounded-lg shadow-2xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Enhanced Header with Phase 2 improvements */}
        <div className="border-b border-gray-700 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <Shield className="h-6 w-6 text-blue-400" />
              <div>
                <h2 className="text-xl font-bold text-white">Security Configuration</h2>
                <div className="text-sm text-gray-300">
                  Configuring: <span className="font-semibold text-blue-400">{nodeSubtype}</span>
                </div>
              </div>
            </div>
            <button
              onClick={handleClose}
              className="text-gray-400 hover:text-white transition-colors"
            >
              <XCircle className="h-6 w-6" />
            </button>
          </div>
          
          {/* Enhanced Progress with Pills */}
          <div className="space-y-3">
            {/* Stepper Header */}
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className="bg-blue-900 text-blue-300 px-3 py-1 rounded-full text-sm font-medium">
                  Question {currentPromptIndex + 1} of {prompts.length}
                </div>
                {markedForLater.size > 0 && (
                  <div className="bg-yellow-900 text-yellow-300 px-3 py-1 rounded-full text-sm font-medium flex items-center">
                    <Clock className="h-3 w-3 mr-1" />
                    {markedForLater.size} for later
                  </div>
                )}
                {hasUnsavedChanges && (
                  <div className="bg-orange-900 text-orange-300 px-3 py-1 rounded-full text-sm font-medium">
                    Unsaved changes
                  </div>
                )}
              </div>
              <div className="text-sm text-gray-400">
                {answeredCount} answered
              </div>
            </div>
            
            {/* Progress Bar */}
            <div className="relative">
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${progressPercentage}%` }}
                ></div>
              </div>
              {/* Progress indicators for marked questions */}
              {Array.from(markedForLater).map(index => (
                <div
                  key={index}
                  className="absolute top-0 w-1 h-2 bg-yellow-500 rounded-full"
                  style={{ left: `${((index + 1) / prompts.length) * 100}%` }}
                />
              ))}
            </div>
          </div>
        </div>

        {/* Enhanced Current Question with Dependency Badges */}
        <div className="p-6">
          <div className="mb-6">
            <div className="flex items-start justify-between mb-3">
              <h3 className="text-lg font-semibold text-white flex-1">
                {currentPrompt.question}
              </h3>
              {markedForLater.has(currentPromptIndex) && (
                <div className="bg-yellow-900/30 text-yellow-300 px-2 py-1 rounded text-xs flex items-center ml-3">
                  <Flag className="h-3 w-3 mr-1" />
                  Marked for later
                </div>
              )}
            </div>
            
            {/* Dependency Trigger Badge */}
            {(() => {
              const triggerInfo = getDependencyTriggerInfo(currentPrompt);
              if (triggerInfo) {
                return (
                  <div className="mb-3 p-3 bg-green-900/20 border border-green-700/30 rounded-lg">
                    <div className="flex items-center space-x-2 text-sm">
                      <Plus className="h-4 w-4 text-green-400" />
                      <span className="text-green-300">
                        Answering "{triggerInfo.condition}" will create a <strong>{triggerInfo.nodeType}</strong> node
                      </span>
                    </div>
                  </div>
                );
              }
              return null;
            })()}
            
            {currentPrompt.help_text && (
              <div className="flex items-start space-x-2 p-3 bg-blue-900/20 border border-blue-700/30 rounded-lg mb-4">
                <HelpCircle className="h-5 w-5 text-blue-400 mt-0.5 flex-shrink-0" />
                <p className="text-sm text-blue-200">{currentPrompt.help_text}</p>
              </div>
            )}
          </div>

          {/* Answer Input */}
          <div className="mb-6">
            {renderPromptInput(currentPrompt)}
          </div>

          {/* Validation Status */}
          {validation && (
            <div className="mb-6 p-4 bg-gray-900/50 border border-gray-600 rounded-lg">
              <div className="flex items-center space-x-2 mb-2">
                <CheckCircle className="h-5 w-5 text-green-400" />
                <span className="font-semibold text-white">Completion Status</span>
              </div>
              <div className="text-sm text-gray-300">
                <p>Completed: {validation.completed_count}/{validation.required_count} required fields</p>
                <p>Progress: {validation.completion_percentage}%</p>
              </div>
            </div>
          )}
        </div>

        {/* Enhanced Footer with Phase 2 features */}
        <div className="border-t border-gray-700 p-6">
          <div className="flex justify-between items-center">
            <button
              onClick={handlePrevious}
              disabled={currentPromptIndex === 0}
              className="flex items-center space-x-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronLeft className="h-4 w-4" />
              <span>Previous</span>
            </button>

            <div className="flex space-x-3">
              <button
                onClick={handleMarkForLater}
                className="flex items-center space-x-2 px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors"
              >
                <Clock className="h-4 w-4" />
                <span>Mark for Later</span>
              </button>

              <button
                onClick={validateAnswers}
                className="flex items-center space-x-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
              >
                <AlertTriangle className="h-4 w-4" />
                <span>Validate</span>
              </button>

              {currentPromptIndex < prompts.length - 1 ? (
                <button
                  onClick={handleNext}
                  className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <span>Next</span>
                  <ChevronRight className="h-4 w-4" />
                </button>
              ) : (
                <button
                  onClick={handleComplete}
                  className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                >
                  <Save className="h-4 w-4" />
                  <span>Complete</span>
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Unsaved Changes Dialog */}
        <AlertDialog open={showUnsavedDialog} onOpenChange={setShowUnsavedDialog}>
          <AlertDialogContent className="bg-gray-800 border-gray-700">
            <AlertDialogHeader>
              <AlertDialogTitle className="text-white">Unsaved Changes</AlertDialogTitle>
              <AlertDialogDescription className="text-gray-300">
                You have unsaved changes to your security configuration. Are you sure you want to close without saving?
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel className="bg-gray-600 text-white hover:bg-gray-700">
                Keep Editing
              </AlertDialogCancel>
              <AlertDialogAction 
                onClick={() => {
                  setShowUnsavedDialog(false);
                  onCancel();
                }}
                className="bg-red-600 text-white hover:bg-red-700"
              >
                Discard Changes
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>

        {/* Phase 2: Completion Summary Modal */}
        {completionSummary && (
          <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-60">
            <div className="bg-gray-800 rounded-lg shadow-2xl max-w-2xl w-full mx-4 border border-gray-700">
              <div className="border-b border-gray-700 p-6">
                <div className="flex items-center space-x-3">
                  <CheckCircle className="h-8 w-8 text-green-400" />
                  <div>
                    <h2 className="text-2xl font-bold text-white">Configuration Complete!</h2>
                    <p className="text-gray-300">Your {completionSummary.nodeType} security configuration has been saved.</p>
                  </div>
                </div>
              </div>
              
              <div className="p-6 space-y-6">
                {/* Progress Summary */}
                <div className="grid grid-cols-3 gap-4">
                  <div className="bg-blue-900/30 border border-blue-700 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-blue-400">
                      {completionSummary.questionsAnswered}/{completionSummary.totalQuestions}
                    </div>
                    <div className="text-sm text-gray-300">Questions Answered</div>
                  </div>
                  <div className="bg-green-900/30 border border-green-700 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-green-400">
                      {Math.round(completionSummary.completionPercentage)}%
                    </div>
                    <div className="text-sm text-gray-300">Complete</div>
                  </div>
                  <div className="bg-purple-900/30 border border-purple-700 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-purple-400">
                      {completionSummary.dependenciesCreated.length}
                    </div>
                    <div className="text-sm text-gray-300">Dependencies Created</div>
                  </div>
                </div>

                {/* Dependencies Created */}
                {completionSummary.dependenciesCreated.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold text-white mb-3 flex items-center">
                      <Target className="h-5 w-5 text-green-400 mr-2" />
                      Dependencies Created
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {completionSummary.dependenciesCreated.map((dep, index) => (
                        <div key={index} className="bg-green-900/30 text-green-300 px-3 py-1 rounded-full text-sm border border-green-700">
                          {dep} Node
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Security Controls */}
                {completionSummary.securityControlsEnabled.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold text-white mb-3 flex items-center">
                      <Shield className="h-5 w-5 text-blue-400 mr-2" />
                      Key Security Controls Enabled
                    </h3>
                    <div className="space-y-2">
                      {completionSummary.securityControlsEnabled.map((control, index) => (
                        <div key={index} className="flex items-center space-x-2 text-sm text-gray-300">
                          <CheckCircle className="h-4 w-4 text-green-400" />
                          <span>{control}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Recommendations */}
                {completionSummary.recommendations.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold text-white mb-3 flex items-center">
                      <BookOpen className="h-5 w-5 text-yellow-400 mr-2" />
                      Next Steps & Recommendations
                    </h3>
                    <div className="space-y-2">
                      {completionSummary.recommendations.map((rec, index) => (
                        <div key={index} className="flex items-start space-x-2 text-sm text-gray-300">
                          <ExternalLink className="h-4 w-4 text-yellow-400 mt-0.5" />
                          <span>{rec}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Mark for Later Notice */}
                {completionSummary.markedForLaterCount > 0 && (
                  <div className="bg-yellow-900/20 border border-yellow-700/30 rounded-lg p-4">
                    <div className="flex items-center space-x-2 text-yellow-300">
                      <Clock className="h-5 w-5" />
                      <span className="font-medium">
                        {completionSummary.markedForLaterCount} question{completionSummary.markedForLaterCount !== 1 ? 's' : ''} marked for later
                      </span>
                    </div>
                    <p className="text-sm text-yellow-200 mt-1">
                      You can return to complete these questions anytime by editing this node's security configuration.
                    </p>
                  </div>
                )}
              </div>
              
              <div className="border-t border-gray-700 p-6">
                <button
                  onClick={() => setCompletionSummary(null)}
                  className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors font-medium"
                >
                  Continue to Diagram
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
    </TooltipProvider>
  );
};

export default SecurityQuestionnaire;