import React, { useState, useEffect, useCallback } from 'react';
import { useQuestionnaire } from '../contexts/QuestionnaireContext';
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
  X,
  Layers,
  ArrowUp,
  ArrowDown
} from 'lucide-react';

const EnhancedSecurityQuestionnaire = ({ 
  nodeId,
  nodeSubtype, 
  onComplete, 
  onCancel,
  parentNodeId = null,
  existingValues = {},
  zIndex = 1000,
  getIncompleteDependencies = null,
}) => {
  const { state, actions } = useQuestionnaire();
  const [prompts, setPrompts] = useState([]);
  const [currentPromptIndex, setCurrentPromptIndex] = useState(0);
  const [answers, setAnswers] = useState(existingValues);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [validation, setValidation] = useState(null);
  
  // Get questionnaire state from context
  const questionnaire = state.questionnaires[nodeId];
  const isActive = state.activeModalId === nodeId;
  const modalDepth = state.modalStack.findIndex(modal => modal.id === nodeId);
  const isTopModal = state.modalStack[state.modalStack.length - 1]?.id === nodeId;
  
  // Initialize questionnaire on mount
  useEffect(() => {
    if (nodeId && nodeSubtype) {
      initializeQuestionnaire();
    }
    
    // Cleanup function
    return () => {
      // Clean up any pending request for this component
      if (window.pendingPromptRequests) {
        window.pendingPromptRequests.delete(`${nodeSubtype}-prompts`);
      }
    };
  }, [nodeId, nodeSubtype]);
  
  const initializeQuestionnaire = async () => {
    try {
      setLoading(true);
      
      // Check if questionnaire already exists in context (prevents duplicate API calls)
      if (questionnaire && questionnaire.prompts && questionnaire.prompts.length > 0) {
        console.log('📋 Using existing prompts from context:', questionnaire.prompts.length);
        setPrompts(questionnaire.prompts);
        setError(null);
        setLoading(false);
        return;
      }
      
      // Add a small delay to prevent rapid duplicate requests
      const requestKey = `${nodeSubtype}-prompts`;
      if (window.pendingPromptRequests && window.pendingPromptRequests.has(requestKey)) {
        console.log('⏳ Prompt request already in progress, waiting...');
        await new Promise(resolve => setTimeout(resolve, 100));
        
        // Check again if prompts are now available
        const updatedQuestionnaire = state.questionnaires[nodeId];
        if (updatedQuestionnaire && updatedQuestionnaire.prompts && updatedQuestionnaire.prompts.length > 0) {
          setPrompts(updatedQuestionnaire.prompts);
          setError(null);
          setLoading(false);
          return;
        }
      }
      
      // Mark request as pending
      if (!window.pendingPromptRequests) {
        window.pendingPromptRequests = new Set();
      }
      window.pendingPromptRequests.add(requestKey);
      
      // Fetch security prompts
      console.log('🔄 Fetching prompts for', nodeSubtype);
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/intelligent-nodes/${nodeSubtype}/prompts`);
      
      // Remove from pending requests
      window.pendingPromptRequests.delete(requestKey);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch prompts: ${response.statusText}`);
      }
      
      const data = await response.json();
      const fetchedPrompts = data.prompts || [];
      setPrompts(fetchedPrompts);
      
      // Create questionnaire in context
      actions.createQuestionnaire(
        nodeId, 
        nodeSubtype, 
        fetchedPrompts, 
        existingValues, 
        parentNodeId
      );
      
      // Add to modal stack (prevent duplicates)
      const existingModal = state.modalStack.find(modal => modal.id === nodeId);
      if (!existingModal) {
        actions.pushModal({
          id: nodeId,
          type: 'questionnaire',
          nodeId,
          nodeSubtype,
          parentId: parentNodeId,
          zIndex: zIndex + modalDepth,
        });
      }
      
      // Update progress tracking
      actions.addQuestionnaireToFlow(nodeId);
      
      setError(null);
    } catch (err) {
      console.error('Error initializing questionnaire:', err);
      setError(err.message);
      
      // Remove from pending requests on error
      if (window.pendingPromptRequests) {
        window.pendingPromptRequests.delete(`${nodeSubtype}-prompts`);
      }
    } finally {
      setLoading(false);
    }
  };
  
  const handleAnswerChange = useCallback((promptId, value) => {
    const newAnswers = {
      ...answers,
      [promptId]: value
    };
    setAnswers(newAnswers);
    
    // Update questionnaire in context
    const answeredQuestions = Object.keys(newAnswers).filter(key => 
      newAnswers[key] !== undefined && newAnswers[key] !== null
    ).length;
    
    actions.updateQuestionnaire(nodeId, {
      answers: newAnswers,
      progress: {
        answeredQuestions,
        completionPercentage: Math.round((answeredQuestions / prompts.length) * 100),
      },
    });
  }, [answers, nodeId, prompts.length, actions]);
  
  const handleNext = async () => {
    // Check if current question is a dependency-triggering question
    const currentPrompt = prompts[currentPromptIndex];
    const currentAnswer = answers[currentPrompt.id];
    
    // Define dependency-triggering questions
    const dependencyTriggers = {
      'webapp_api_endpoints': 'API',
      'webapp_database_connection': 'Database',
      'db_backup_enabled': 'Backup',
      'db_monitoring_enabled': 'Monitoring'
    };
    
    // If current question triggers a dependency and answer is Yes/True
    if (dependencyTriggers[currentPrompt.id] && (currentAnswer === true || currentAnswer === 'Yes')) {
      console.log(`🎯 Dependency trigger detected for ${currentPrompt.id} → ${dependencyTriggers[currentPrompt.id]}`);
      
      try {
        // Check dependencies for this specific answer
        const dependencyResponse = await fetch(
          `${process.env.REACT_APP_BACKEND_URL}/api/intelligent-nodes/${nodeSubtype}/check-dependencies`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({ answers: { [currentPrompt.id]: currentAnswer } })
          }
        );
        
        if (dependencyResponse.ok) {
          const dependencyData = await dependencyResponse.json();
          const dependentNodes = dependencyData.dependent_nodes || [];
          
          if (dependentNodes.length > 0) {
            console.log(`🚀 Triggering immediate dependent nodes:`, dependentNodes);
            
            // Pause current questionnaire
            actions.pauseQuestionnaire(nodeId);
            
            // Trigger dependent node creation
            if (onComplete) {
              onComplete({
                nodeId,
                answers,
                dependentNodes,
                triggerDependentQuestionnaires: true,
                partialCompletion: true,
                currentPromptIndex: currentPromptIndex + 1,
                shouldPause: true, // Flag to pause current questionnaire
              });
              return;
            }
          }
        }
      } catch (error) {
        console.error('Error checking immediate dependencies:', error);
      }
    }
    
    // Normal next question flow
    if (currentPromptIndex < prompts.length - 1) {
      const newIndex = currentPromptIndex + 1;
      setCurrentPromptIndex(newIndex);
      
      // Update questionnaire progress
      actions.updateQuestionnaire(nodeId, {
        currentPromptIndex: newIndex,
      });
    }
  };
  
  const handlePrevious = () => {
    if (currentPromptIndex > 0) {
      const newIndex = currentPromptIndex - 1;
      setCurrentPromptIndex(newIndex);
      
      // Update questionnaire progress
      actions.updateQuestionnaire(nodeId, {
        currentPromptIndex: newIndex,
      });
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
          // Use nodeId as the parent when checking dependencies (since this node is creating dependencies)
          if (getIncompleteDependencies) {
            dependentNodes = getIncompleteDependencies(nodeId, allDependentNodes);
            console.log('🎯 Enhanced dependency check result (filtered):', {
              nodeSubtype,
              answers,
              allDependentNodes,
              incompleteDependentNodes: dependentNodes,
              triggerRequired: dependentNodes.length > 0
            });
          } else {
            dependentNodes = allDependentNodes;
            console.log('🎯 Enhanced dependency check result (unfiltered):', {
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

      // Mark questionnaire as completed in context
      actions.completeQuestionnaire(nodeId);
      
      // Queue canvas updates
      actions.queueCanvasUpdate(
        { nodeId, status: 'completed', validation: validationResult.validation },
        dependentNodes.map(depType => ({ 
          from: nodeId, 
          to: `${nodeId}_${depType}`, 
          type: 'dependency' 
        }))
      );

      // Call completion handler
      if (onComplete) {
        onComplete({
          nodeId,
          answers,
          validation: validationResult.validation,
          recommendations: validationResult.recommendations,
          dependentNodes,
          triggerDependentQuestionnaires: dependentNodes.length > 0,
          isCompleted: true,
        });
      }
    }
  };
  
  const handleCancel = () => {
    // Remove from modal stack
    actions.popModal();
    
    if (onCancel) {
      onCancel();
    }
  };
  
  const handleBringToFront = () => {
    actions.setActiveModal(nodeId);
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
        
      case 'boolean':
        return (
          <div className="space-y-2">
            {['Yes', 'No'].map((option) => (
              <label 
                key={option}
                className="flex items-center space-x-3 p-3 border border-gray-600 rounded-lg hover:bg-gray-700 cursor-pointer transition-colors"
              >
                <input
                  type="radio"
                  name={prompt.id}
                  value={option === 'Yes'}
                  checked={currentValue === (option === 'Yes')}
                  onChange={(e) => handleAnswerChange(prompt.id, option === 'Yes')}
                  className="text-blue-600 focus:ring-blue-500"
                />
                <span className="text-white">{option}</span>
              </label>
            ))}
          </div>
        );
        
      case 'text':
      default:
        return (
          <textarea
            value={currentValue || ''}
            onChange={(e) => handleAnswerChange(prompt.id, e.target.value)}
            className="w-full p-3 border border-gray-600 rounded-lg bg-gray-800 text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 resize-none"
            rows="3"
            placeholder="Enter your answer..."
          />
        );
    }
  };
  
  if (loading) {
    return (
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center"
        style={{ zIndex }}
      >
        <div className="bg-gray-900 p-6 rounded-lg">
          <div className="flex items-center space-x-3">
            <RefreshCw className="w-5 h-5 animate-spin text-blue-500" />
            <span className="text-white">Loading questionnaire...</span>
          </div>
        </div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center"
        style={{ zIndex }}
      >
        <div className="bg-gray-900 p-6 rounded-lg">
          <div className="flex items-center space-x-3">
            <XCircle className="w-5 h-5 text-red-500" />
            <span className="text-white">Error loading questionnaire: {error}</span>
          </div>
          <button
            onClick={handleCancel}
            className="mt-4 px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600"
          >
            Close
          </button>
        </div>
      </div>
    );
  }
  
  const currentPrompt = prompts[currentPromptIndex];
  
  return (
    <div 
      className={`fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 ${
        !isTopModal ? 'pointer-events-none' : ''
      }`}
      style={{ zIndex }}
    >
      <div 
        className={`bg-gray-900 rounded-lg shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto transition-all duration-200 ${
          isTopModal ? 'pointer-events-auto scale-100' : 'pointer-events-auto scale-95 opacity-90'
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-700">
          <div className="flex items-center space-x-3">
            <Shield className="w-6 h-6 text-blue-500" />
            <div>
              <h2 className="text-xl font-bold text-white">
                Security Questionnaire
              </h2>
              <p className="text-gray-400 text-sm">
                {nodeSubtype} Configuration
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            {/* Modal Stack Indicator */}
            {state.modalStack.length > 1 && (
              <div className="flex items-center space-x-1 px-2 py-1 bg-gray-800 rounded-lg">
                <Layers className="w-4 h-4 text-gray-400" />
                <span className="text-gray-400 text-sm">
                  {modalDepth + 1}/{state.modalStack.length}
                </span>
              </div>
            )}
            
            {/* Bring to Front Button */}
            {!isTopModal && (
              <button
                onClick={handleBringToFront}
                className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
                title="Bring to front"
              >
                <ArrowUp className="w-4 h-4" />
              </button>
            )}
            
            {/* Close Button */}
            <button
              onClick={handleCancel}
              className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>
        
        {/* Progress */}
        <div className="px-6 py-4 bg-gray-800">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-300 text-sm">
              Question {currentPromptIndex + 1} of {prompts.length}
            </span>
            <span className="text-gray-300 text-sm">
              {Math.round(((currentPromptIndex + 1) / prompts.length) * 100)}% Complete
            </span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div 
              className="bg-gradient-to-r from-blue-500 to-green-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${((currentPromptIndex + 1) / prompts.length) * 100}%` }}
            />
          </div>
        </div>
        
        {/* Content */}
        <div className="p-6">
          {currentPrompt && (
            <div className="space-y-6">
              {/* Question */}
              <div>
                <h3 className="text-lg font-semibold text-white mb-2">
                  {currentPrompt.question}
                </h3>
                {currentPrompt.help_text && (
                  <div className="flex items-start space-x-2 p-3 bg-blue-900/20 border border-blue-500/30 rounded-lg">
                    <HelpCircle className="w-5 h-5 text-blue-400 mt-0.5 flex-shrink-0" />
                    <p className="text-blue-300 text-sm">
                      {currentPrompt.help_text}
                    </p>
                  </div>
                )}
              </div>
              
              {/* Answer Input */}
              <div>
                {renderPromptInput(currentPrompt)}
              </div>
              
              {/* Validation */}
              {validation && (
                <div className="p-4 bg-red-900/20 border border-red-500/30 rounded-lg">
                  <div className="flex items-start space-x-2">
                    <AlertTriangle className="w-5 h-5 text-red-400 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="text-red-300 font-medium">Validation Issues</p>
                      <p className="text-red-300 text-sm mt-1">
                        {validation.message}
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
        
        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-gray-700 bg-gray-800">
          <button
            onClick={handlePrevious}
            disabled={currentPromptIndex === 0}
            className="flex items-center space-x-2 px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <ChevronLeft className="w-4 h-4" />
            <span>Previous</span>
          </button>
          
          <div className="flex items-center space-x-3">
            {currentPromptIndex < prompts.length - 1 ? (
              <button
                onClick={handleNext}
                className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <span>Next</span>
                <ChevronRight className="w-4 h-4" />
              </button>
            ) : (
              <button
                onClick={handleComplete}
                className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                <CheckCircle className="w-4 h-4" />
                <span>Complete</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnhancedSecurityQuestionnaire;