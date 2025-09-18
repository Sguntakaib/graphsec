import React, { useState, useEffect } from 'react';
import { 
  Shield, 
  AlertTriangle, 
  CheckCircle, 
  XCircle, 
  HelpCircle, 
  ChevronRight,
  ChevronLeft,
  Save,
  RefreshCw 
} from 'lucide-react';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from './ui/tooltip';

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
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [validation, setValidation] = useState(null);

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
    }
  }, [isVisible, nodeSubtype, resumeFromPromptIndex, partialAnswers]);

  // Additional validation for resumption index
  useEffect(() => {
    if (prompts.length > 0 && resumeFromPromptIndex !== null && resumeFromPromptIndex >= prompts.length) {
      // If resume index is beyond questionnaire length, clamp it to the last question
      console.log(`⚠️ Resume index ${resumeFromPromptIndex} is beyond questionnaire length ${prompts.length}, clamping to last question`);
      setCurrentPromptIndex(prompts.length - 1);
    }
  }, [prompts.length, resumeFromPromptIndex]);

  // Additional effect to reset state when the modal is closed and reopened
  useEffect(() => {
    if (isVisible && resumeFromPromptIndex === null) {
      // Only reset to 0 if we're not resuming from a specific index
      setCurrentPromptIndex(0);
    }
  }, [isVisible, resumeFromPromptIndex]);

  const fetchSecurityPrompts = async () => {
    try {
      setLoading(true);
      
      // Use comprehensive questionnaire for WebApp, API, and Database - fallback to intelligent-nodes for others
      let response;
      if (nodeSubtype === 'WebApp') {
        console.log('🎯 Using comprehensive WebApp questionnaire system');
        response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/questionnaires/WebApp?level=basic`);
      } else if (nodeSubtype === 'API') {
        console.log('🎯 Using comprehensive API questionnaire system');
        response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/questionnaires/API?level=basic`);
      } else if (nodeSubtype === 'Database') {
        console.log('🎯 Using comprehensive Database questionnaire system');
        response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/questionnaires/Database?level=basic`);
      } else {
        console.log('🎯 Falling back to intelligent-nodes system for', nodeSubtype);
        response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/intelligent-nodes/${nodeSubtype}/prompts`);
      }
      
      if (!response.ok) {
        throw new Error(`Failed to fetch prompts: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      if (nodeSubtype === 'WebApp' || nodeSubtype === 'API' || nodeSubtype === 'Database') {
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
    // Direct mappings based on YAML files' related_branch values
    const branchMappings = {
      // WebApp.yaml branch mappings
      'Authentication': 'Authentication',
      'InputValidation': 'InputValidation', 
      'Encryption': 'SSL/TLS',  // For HTTPS and data encryption questions
      'Database': 'Database',
      'API': 'API',
      'SessionManagement': 'SessionManagement',
      'ErrorHandling': 'ErrorHandling',
      'Logging': 'Logging',
      'CSP': 'CSP',
      
      // API.yaml branch mappings
      'ApiSecurity': 'ApiSecurity',
      'Authorization': 'Authorization',
      'RateLimiting': 'RateLimiting',
      'Monitoring': 'Monitoring',
      'ExternalService': 'ExternalService',
      
      // Legacy mappings
      'login': 'Authentication',
      'authentication': 'Authentication',
      'input_validation': 'InputValidation',
      'validation': 'InputValidation',
      'https': 'SSL/TLS',
      'ssl': 'SSL/TLS',
      'tls': 'SSL/TLS',
      'database_connection': 'Database',
      'database': 'Database',
      'api_endpoints': 'API',
      'api': 'API',
      'session_management': 'SessionManagement',
      'sessionmanagement': 'SessionManagement',
      'error_handling': 'ErrorHandling',
      'errorhandling': 'ErrorHandling',
      'logging': 'Logging',
      'csp': 'CSP',
      'authorization': 'Authorization',
      'rate_limiting': 'RateLimiting',
      'monitoring': 'Monitoring'
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
    if (promptId.includes('https') || promptId.includes('data_encryption')) return 'SSL/TLS';
    if (promptId.includes('database')) return 'Database';
    if (promptId.includes('api_endpoints')) return 'API';
    if (promptId.includes('session_management')) return 'SessionManagement';
    if (promptId.includes('error_handling')) return 'ErrorHandling';
    if (promptId.includes('logging')) return 'Logging';
    if (promptId.includes('security_headers')) return 'CSP';
    if (promptId.includes('rate_limiting')) return 'RateLimiting';
    if (promptId.includes('monitoring')) return 'Monitoring';

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
    setAnswers(prev => ({
      ...prev,
      [promptId]: value
    }));
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
      console.log(`🎯 Dependency trigger detected for ${currentPrompt.id} → ${dependencyTriggers[currentPrompt.id]}`);
      
      // Only trigger the SPECIFIC dependency that was just answered, not all dependencies
      const specificDependency = dependencyTriggers[currentPrompt.id];
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
        isActualCompletion: true // Flag to indicate this was a real completion button click
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
        {/* Header */}
        <div className="border-b border-gray-700 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <Shield className="h-6 w-6 text-blue-400" />
              <h2 className="text-xl font-bold text-white">Security Configuration</h2>
            </div>
            <button
              onClick={onCancel}
              className="text-gray-400 hover:text-white transition-colors"
            >
              <XCircle className="h-6 w-6" />
            </button>
          </div>
          
          <div className="text-sm text-gray-300 mb-3">
            Configuring: <span className="font-semibold text-blue-400">{nodeSubtype}</span>
          </div>
          
          {/* Progress Bar */}
          <div className="relative">
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${progressPercentage}%` }}
              ></div>
            </div>
            <div className="flex justify-between text-xs text-gray-400 mt-1">
              <span>Question {currentPromptIndex + 1} of {prompts.length}</span>
              <span>{answeredCount} answered</span>
            </div>
          </div>
        </div>

        {/* Current Question */}
        <div className="p-6">
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-white mb-2">
              {currentPrompt.question}
            </h3>
            
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

        {/* Footer */}
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
                onClick={validateAnswers}
                className="flex items-center space-x-2 px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors"
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
      </div>
    </div>
    </TooltipProvider>
  );
};

export default SecurityQuestionnaire;