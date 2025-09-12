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

const SecurityQuestionnaire = ({ 
  nodeSubtype, 
  onComplete, 
  onCancel, 
  existingValues = {},
  isVisible = false,
  sourceNode = null,
  currentNodes = [],
  onCreateLinkedNodes = null
}) => {
  const [prompts, setPrompts] = useState([]);
  const [currentPromptIndex, setCurrentPromptIndex] = useState(0);
  const [answers, setAnswers] = useState(existingValues);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [validation, setValidation] = useState(null);

  useEffect(() => {
    if (isVisible && nodeSubtype) {
      // Reset state when opening questionnaire for a new node
      setCurrentPromptIndex(0);
      setAnswers(existingValues);
      setValidation(null);
      setError(null);
      fetchSecurityPrompts();
    }
  }, [isVisible, nodeSubtype]);

  // Additional effect to reset state when the modal is closed and reopened
  useEffect(() => {
    if (isVisible) {
      setCurrentPromptIndex(0);
    }
  }, [isVisible]);

  const fetchSecurityPrompts = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/intelligent-nodes/${nodeSubtype}/prompts`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch prompts: ${response.statusText}`);
      }
      
      const data = await response.json();
      setPrompts(data.prompts || []);
      setError(null);
    } catch (err) {
      console.error('Error fetching security prompts:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const validateAnswers = async () => {
    try {
      const branches = prompts.map(prompt => ({
        id: prompt.id,
        name: prompt.related_branch,
        type: prompt.related_branch,
        required: true,
        completed: answers[prompt.id] !== undefined && answers[prompt.id] !== null,
        value: answers[prompt.id],
        description: prompt.help_text
      }));

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

  const handleNext = () => {
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
          dependentNodes = dependencyData.dependent_nodes || [];
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
        triggerDependentQuestionnaires: dependentNodes.length > 0
      });
    }
  };

  const renderPromptInput = (prompt) => {
    const currentValue = answers[prompt.id];

    switch (prompt.type) {
      case 'single_choice':
        return (
          <div className="space-y-2">
            {prompt.options?.map((option, index) => (
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
                <span className="text-white">{option}</span>
              </label>
            ))}
          </div>
        );

      case 'multiple_choice':
        return (
          <div className="space-y-2">
            {prompt.options?.map((option, index) => {
              const selectedOptions = Array.isArray(currentValue) ? currentValue : [];
              return (
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
                  <span className="text-white">{option}</span>
                </label>
              );
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
  );
};

export default SecurityQuestionnaire;