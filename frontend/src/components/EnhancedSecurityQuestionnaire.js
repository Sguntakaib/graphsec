import React, { useState, useEffect, useCallback } from 'react';
import { Shield, CheckCircle, AlertCircle, Info, ChevronLeft, ChevronRight, X } from 'lucide-react';

const EnhancedSecurityQuestionnaire = ({ 
  nodeId, 
  nodeSubtype, 
  isOpen, 
  onClose, 
  onComplete,
  getIncompleteDependencies,
  resumeFromPromptIndex = 0,
  partialAnswers = {}
}) => {
  const [prompts, setPrompts] = useState([]);
  const [answers, setAnswers] = useState(partialAnswers);
  const [currentPromptIndex, setCurrentPromptIndex] = useState(resumeFromPromptIndex);
  const [loading, setLoading] = useState(false);
  const [validation, setValidation] = useState(null);
  const [showValidation, setShowValidation] = useState(false);
  const [error, setError] = useState(null);

  // Map questionnaire prompt types to correct SecurityBranch enum values
  const mapPromptTypeToSecurityBranch = (promptId, relatedBranch) => {
    // Common mappings based on prompt IDs and related branches
    const mappings = {
      // Authentication related
      'authentication_method': 'Login',
      'auth_method': 'Login',
      'login': 'Login',
      'authentication': 'Login',
      
      // Database related
      'database_connection': 'Database',
      'database': 'Database',
      'db_connection': 'Database',
      
      // API related
      'api_endpoints': 'API',
      'api': 'API',
      'rest_api': 'API',
      
      // Input validation
      'input_validation': 'InputValidation',
      'validation': 'InputValidation',
      
      // WAF
      'waf': 'WAF',
      'firewall': 'WAF',
      'web_firewall': 'WAF',
      
      // HTTPS/Encryption
      'https': 'Encryption',
      'encryption': 'Encryption',
      'ssl': 'Encryption',
      'tls': 'Encryption',
      
      // Deployment
      'deployment': 'Deployment',
      'deploy': 'Deployment',
      'deployment_security': 'Deployment',
      
      // Default fallbacks based on related_branch
      'encryption': 'Encryption',
      'access_control': 'AccessControl',
      'monitoring': 'Monitoring',
      'logging': 'Logging'
    };

    // First try direct prompt ID mapping
    if (mappings[promptId]) {
      return mappings[promptId];
    }

    // Then try related_branch mapping
    if (relatedBranch && mappings[relatedBranch.toLowerCase()]) {
      return mappings[relatedBranch.toLowerCase()];
    }

    // Try to extract from prompt ID patterns
    if (promptId.includes('auth') || promptId.includes('login')) return 'Login';
    if (promptId.includes('database') || promptId.includes('db')) return 'Database';
    if (promptId.includes('api')) return 'API';
    if (promptId.includes('validation') || promptId.includes('input')) return 'InputValidation';
    if (promptId.includes('waf') || promptId.includes('firewall')) return 'WAF';
    if (promptId.includes('deploy')) return 'Deployment';

    // Default fallback - use related_branch as PascalCase if available
    if (relatedBranch) {
      return relatedBranch.charAt(0).toUpperCase() + relatedBranch.slice(1).toLowerCase();
    }

    // Final fallback
    return 'Login';
  };

  useEffect(() => {
    if (isOpen && nodeSubtype) {
      fetchPrompts();
    }
  }, [isOpen, nodeSubtype]);

  const fetchPrompts = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Use specific endpoints for WebApp, API, and Database to get option_descriptions
      let endpoint;
      if (nodeSubtype === 'WebApp') {
        endpoint = `${process.env.REACT_APP_BACKEND_URL}/api/questionnaires/WebApp?level=basic`;
      } else if (nodeSubtype === 'API') {
        endpoint = `${process.env.REACT_APP_BACKEND_URL}/api/questionnaires/API?level=basic`;
      } else if (nodeSubtype === 'Database') {
        endpoint = `${process.env.REACT_APP_BACKEND_URL}/api/questionnaires/Database?level=basic`;
      } else {
        endpoint = `${process.env.REACT_APP_BACKEND_URL}/api/questionnaires/${nodeSubtype}`;
      }
      
      const response = await fetch(endpoint);
      
      if (response.ok) {
        const data = await response.json();
        setPrompts(data.prompts || []);
      } else {
        setError('Failed to load questionnaire prompts');
      }
    } catch (err) {
      setError('Network error loading prompts');
      console.error('Error fetching prompts:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (promptId, value) => {
    setAnswers(prev => ({
      ...prev,
      [promptId]: value
    }));
  };

  const validateAnswers = async () => {
    try {
      const branches = prompts.map(prompt => ({
        id: prompt.id,
        name: prompt.related_branch || prompt.id,
        type: mapPromptTypeToSecurityBranch(prompt.id, prompt.related_branch),
        required: true,
        completed: answers[prompt.id] !== undefined && answers[prompt.id] !== null,
        value: answers[prompt.id],
        description: prompt.help_text || prompt.question
      }));

      console.log('Validating with branches:', branches.map(b => ({ id: b.id, type: b.type, completed: b.completed })));

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
        setValidation(validationData.validation);
        return validationData;
      } else {
        const errorData = await response.json();
        console.error('Validation failed:', errorData);
        setError('Validation failed: ' + (errorData.detail || 'Unknown error'));
      }
    } catch (err) {
      console.error('Validation error:', err);
      setError('Network error during validation');
    }
    return null;
  };

  const nextPrompt = () => {
    if (currentPromptIndex < prompts.length - 1) {
      setCurrentPromptIndex(currentPromptIndex + 1);
    }
  };

  const previousPrompt = () => {
    if (currentPromptIndex > 0) {
      setCurrentPromptIndex(currentPromptIndex - 1);
    }
  };

  const completeQuestionnaire = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // First validate the answers
      const validationResult = await validateAnswers();
      
      if (validationResult) {
        // Check for dependencies that need to be handled
        let dependenciesToCreate = [];
        
        if (getIncompleteDependencies) {
          dependenciesToCreate = await getIncompleteDependencies(nodeSubtype, answers);
          console.log('Dependencies to create:', dependenciesToCreate);
        }
        
        // Complete the questionnaire
        if (onComplete) {
          await onComplete({
            nodeId,
            nodeSubtype,
            answers,
            validation: validationResult.validation,
            dependencies: dependenciesToCreate
          });
        }
        
        // Close the modal
        onClose();
      }
    } catch (err) {
      console.error('Error completing questionnaire:', err);
      setError('Failed to complete questionnaire');
    } finally {
      setLoading(false);
    }
  };

  const currentPrompt = prompts[currentPromptIndex];
  const progress = prompts.length > 0 ? ((currentPromptIndex + 1) / prompts.length) * 100 : 0;
  const isLastPrompt = currentPromptIndex === prompts.length - 1;
  const hasAnswer = currentPrompt && answers[currentPrompt.id] !== undefined && answers[currentPrompt.id] !== null;

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" data-testid="questionnaire-modal">
      <div className="bg-gray-900 rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-gray-800 px-6 py-4 border-b border-gray-700">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Shield className="h-6 w-6 text-blue-400" />
              <div>
                <h2 className="text-xl font-semibold text-white">Security Configuration</h2>
                <p className="text-sm text-gray-400">
                  {nodeSubtype} - Question {currentPromptIndex + 1} of {prompts.length}
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
              data-testid="questionnaire-close-button"
            >
              <X className="h-5 w-5 text-gray-400" />
            </button>
          </div>
          
          {/* Progress Bar */}
          <div className="mt-4">
            <div className="flex justify-between text-sm text-gray-400 mb-1">
              <span>Progress</span>
              <span>{Math.round(progress)}%</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div 
                className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 flex-1 overflow-y-auto">
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
              <p className="text-gray-400">Loading questionnaire...</p>
            </div>
          ) : error ? (
            <div className="text-center py-8">
              <AlertCircle className="h-8 w-8 text-red-400 mx-auto mb-4" />
              <p className="text-red-400 mb-2">Error</p>
              <p className="text-gray-400">{error}</p>
              <button
                onClick={fetchPrompts}
                className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Retry
              </button>
            </div>
          ) : currentPrompt ? (
            <div className="space-y-6">
              {/* Question */}
              <div>
                <h3 className="text-lg font-medium text-white mb-2">
                  {currentPrompt.question}
                </h3>
                {currentPrompt.help_text && (
                  <div className="flex items-start space-x-2 p-3 bg-blue-900 bg-opacity-20 border border-blue-500 border-opacity-30 rounded-lg">
                    <Info className="h-4 w-4 text-blue-400 mt-0.5 flex-shrink-0" />
                    <p className="text-sm text-blue-200">{currentPrompt.help_text}</p>
                  </div>
                )}
              </div>

              {/* Answer Input */}
              <div>
                {currentPrompt.type === 'boolean' ? (
                  <div className="space-y-2">
                    <label className="flex items-center space-x-3 p-3 border border-gray-600 rounded-lg hover:bg-gray-800 transition-colors cursor-pointer">
                      <input
                        type="radio"
                        name={currentPrompt.id}
                        value={true}
                        checked={answers[currentPrompt.id] === true}
                        onChange={() => handleAnswerChange(currentPrompt.id, true)}
                        className="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 focus:ring-blue-500"
                        data-testid={`answer-yes-${currentPrompt.id}`}
                      />
                      <span className="text-white">Yes</span>
                    </label>
                    <label className="flex items-center space-x-3 p-3 border border-gray-600 rounded-lg hover:bg-gray-800 transition-colors cursor-pointer">
                      <input
                        type="radio"
                        name={currentPrompt.id}
                        value={false}
                        checked={answers[currentPrompt.id] === false}
                        onChange={() => handleAnswerChange(currentPrompt.id, false)}
                        className="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 focus:ring-blue-500"
                        data-testid={`answer-no-${currentPrompt.id}`}
                      />
                      <span className="text-white">No</span>
                    </label>
                  </div>
                ) : currentPrompt.type === 'single_choice' ? (
                  <div className="space-y-2">
                    {currentPrompt.options?.map((option, index) => (
                      <label key={index} className="flex items-center space-x-3 p-3 border border-gray-600 rounded-lg hover:bg-gray-800 transition-colors cursor-pointer">
                        <input
                          type="radio"
                          name={currentPrompt.id}
                          value={option}
                          checked={answers[currentPrompt.id] === option}
                          onChange={() => handleAnswerChange(currentPrompt.id, option)}
                          className="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 focus:ring-blue-500"
                          data-testid={`answer-option-${index}-${currentPrompt.id}`}
                        />
                        <span className="text-white">{option}</span>
                      </label>
                    ))}
                  </div>
                ) : (
                  <input
                    type="text"
                    value={answers[currentPrompt.id] || ''}
                    onChange={(e) => handleAnswerChange(currentPrompt.id, e.target.value)}
                    placeholder="Enter your answer..."
                    className="w-full px-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    data-testid={`answer-text-${currentPrompt.id}`}
                  />
                )}
              </div>

              {/* Validation Results */}
              {showValidation && validation && (
                <div className="p-4 bg-gray-800 rounded-lg border border-gray-600">
                  <div className="flex items-center space-x-2 mb-2">
                    <CheckCircle className="h-5 w-5 text-green-400" />
                    <span className="text-white font-medium">Validation Results</span>
                  </div>
                  <div className="text-sm text-gray-300">
                    <p>Completion: {Math.round(validation.completion_percentage)}%</p>
                    <p>Status: {validation.is_complete ? 'Complete' : 'Incomplete'}</p>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-gray-400">No questions available</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="bg-gray-800 px-6 py-4 border-t border-gray-700">
          <div className="flex items-center justify-between">
            <button
              onClick={previousPrompt}
              disabled={currentPromptIndex === 0}
              className="flex items-center space-x-2 px-4 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              data-testid="questionnaire-previous-button"
            >
              <ChevronLeft className="h-4 w-4" />
              <span>Previous</span>
            </button>

            <div className="flex items-center space-x-3">
              {isLastPrompt ? (
                <>
                  <button
                    onClick={() => {
                      validateAnswers();
                      setShowValidation(true);
                    }}
                    className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors"
                    disabled={loading}
                    data-testid="questionnaire-validate-button"
                  >
                    Validate
                  </button>
                  <button
                    onClick={completeQuestionnaire}
                    disabled={!hasAnswer || loading}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    data-testid="questionnaire-complete-button"
                  >
                    {loading ? 'Completing...' : 'Complete'}
                  </button>
                </>
              ) : (
                <button
                  onClick={nextPrompt}
                  disabled={!hasAnswer}
                  className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  data-testid="questionnaire-next-button"
                >
                  <span>Next</span>
                  <ChevronRight className="h-4 w-4" />
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnhancedSecurityQuestionnaire;