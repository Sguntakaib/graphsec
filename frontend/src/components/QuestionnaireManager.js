import React, { useCallback, useEffect } from 'react';
import { useQuestionnaire } from '../contexts/QuestionnaireContext';
import EnhancedSecurityQuestionnaire from './EnhancedSecurityQuestionnaire';
import ProgressBreadcrumbs from './ProgressBreadcrumbs';

const QuestionnaireManager = ({ 
  nodes,
  setNodes,
  onNodeCreate,
  onNodeUpdate,
  currentDiagram
}) => {
  const { state, actions } = useQuestionnaire();
  
  // Handle questionnaire completion
  const handleQuestionnaireComplete = useCallback(async (result) => {
    const { 
      nodeId, 
      answers, 
      validation, 
      recommendations, 
      dependentNodes = [], 
      triggerDependentQuestionnaires = false,
      partialCompletion = false,
      shouldPause = false,
      isCompleted = false 
    } = result;
    
    console.log('🎯 QuestionnaireManager: Handling completion', {
      nodeId,
      dependentNodes,
      triggerDependentQuestionnaires,
      partialCompletion,
      isCompleted
    });
    
    try {
      // Save questionnaire responses
      if (currentDiagram) {
        await saveQuestionnaireResponses(nodeId, answers);
      }
      
      // Handle different completion scenarios
      if (isCompleted) {
        // Final completion - questionnaire is fully done
        console.log('✅ Questionnaire completed:', nodeId);
        
        // Remove from modal stack
        actions.popModal();
        
        // Update node on canvas
        actions.queueCanvasUpdate({
          nodeId,
          status: 'completed',
          validation,
          data: { answers, validation, recommendations }
        });
        
        // Check if we need to resume parent questionnaire
        const currentModal = state.modalStack[state.modalStack.length - 2]; // Parent modal
        if (currentModal && currentModal.type === 'questionnaire') {
          console.log('🔄 Resuming parent questionnaire:', currentModal.nodeId);
          actions.resumeQuestionnaire(currentModal.nodeId);
        }
        
      } else if (partialCompletion && triggerDependentQuestionnaires) {
        // Partial completion with dependencies - pause current and create dependents
        console.log('⏸️ Pausing questionnaire for dependencies:', nodeId);
        
        if (shouldPause) {
          actions.pauseQuestionnaire(nodeId);
        }
        
        // Create dependent nodes and their questionnaires
        await handleDependentNodeCreation(dependentNodes, nodeId, answers);
        
      } else {
        // Regular completion - continue with flow
        actions.completeQuestionnaire(nodeId);
        actions.popModal();
        
        // Check for next questionnaire in stack
        if (state.modalStack.length > 1) {
          const nextModal = state.modalStack[state.modalStack.length - 2];
          if (nextModal.type === 'questionnaire') {
            actions.resumeQuestionnaire(nextModal.nodeId);
          }
        }
      }
      
    } catch (error) {
      console.error('Error handling questionnaire completion:', error);
    }
  }, [currentDiagram, state.modalStack, actions]);
  
  // Handle dependent node creation
  const handleDependentNodeCreation = useCallback(async (dependentNodeTypes, parentNodeId, parentAnswers) => {
    console.log('🚀 Creating dependent nodes:', {
      dependentNodeTypes,
      parentNodeId,
      parentAnswers
    });
    
    const createdNodes = [];
    
    for (const nodeType of dependentNodeTypes) {
      // Check if node already exists
      const existingNode = nodes.find(node => 
        node.data?.subtype === nodeType && 
        node.data?.parentId === parentNodeId
      );
      
      if (existingNode) {
        console.log(`📝 Using existing ${nodeType} node:`, existingNode.id);
        createdNodes.push(existingNode);
      } else {
        // Create new dependent node
        const newNodeId = `${parentNodeId}_${nodeType}_${Date.now()}`;
        const parentNode = nodes.find(n => n.id === parentNodeId);
        
        if (parentNode) {
          const newNode = {
            id: newNodeId,
            type: 'custom',
            position: {
              x: parentNode.position.x + 200,
              y: parentNode.position.y + (createdNodes.length * 100),
            },
            data: {
              label: nodeType,
              subtype: nodeType,
              parentId: parentNodeId,
              category: getNodeCategory(nodeType),
              createdBy: 'questionnaire-dependency',
              createdAt: new Date().toISOString(),
            },
          };
          
          console.log(`➕ Creating new ${nodeType} node:`, newNode);
          createdNodes.push(newNode);
          
          // Add to canvas
          if (onNodeCreate) {
            onNodeCreate(newNode);
          }
        }
      }
    }
    
    // Create questionnaires for all dependent nodes
    for (const node of createdNodes) {
      console.log(`📋 Starting questionnaire for ${node.data.subtype}:`, node.id);
      
      // Start questionnaire flow for this dependent node
      await startQuestionnaireForNode(
        node.id,
        node.data.subtype,
        parentNodeId,
        {} // Start with empty answers
      );
    }
    
    return createdNodes;
  }, [nodes, onNodeCreate]);
  
  // Start questionnaire for a specific node
  const startQuestionnaireForNode = useCallback(async (nodeId, nodeSubtype, parentNodeId = null, existingAnswers = {}) => {
    console.log('🎬 QuestionnaireManager: Starting questionnaire for node:', {
      nodeId,
      nodeSubtype,
      parentNodeId
    });
    
    try {
      // If this is the first questionnaire, start the flow
      if (!state.isFlowActive && !parentNodeId) {
        console.log('🚀 Starting new questionnaire flow');
        const rootNode = nodes.find(n => n.id === nodeId);
        actions.startQuestionnaireFlow(rootNode, 1);
      }
      
      // Fetch the prompts for this node type
      console.log('📋 Fetching prompts for', nodeSubtype);
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/intelligent-nodes/${nodeSubtype}/prompts`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch prompts: ${response.statusText}`);
      }
      
      const data = await response.json();
      const prompts = data.prompts || [];
      
      console.log('✅ Prompts fetched:', prompts.length, 'questions');
      
      // Create questionnaire in context
      actions.createQuestionnaire(nodeId, nodeSubtype, prompts, existingAnswers, parentNodeId);
      
      // Check if modal already exists in stack to prevent duplicates
      const existingModal = state.modalStack.find(modal => modal.nodeId === nodeId);
      if (!existingModal) {
        // Add to modal stack to trigger the modal display
        actions.pushModal({
          id: nodeId,
          type: 'questionnaire',
          nodeId,
          nodeSubtype,
          parentId: parentNodeId,
          zIndex: 1000 + state.modalStack.length * 10,
        });
      } else {
        console.log('⚠️ Modal already exists for node:', nodeId, '- skipping duplicate');
      }
      
      console.log('🎉 Questionnaire modal should now be visible!');
      
      return { 
        nodeId, 
        nodeSubtype, 
        parentNodeId, 
        existingAnswers,
        success: true 
      };
      
    } catch (error) {
      console.error('❌ Failed to start questionnaire:', error);
      return { 
        nodeId, 
        nodeSubtype, 
        parentNodeId, 
        existingAnswers,
        success: false,
        error: error.message 
      };
    }
  }, [state.isFlowActive, state.modalStack.length, nodes, actions]);
  
  // Save questionnaire responses to backend
  const saveQuestionnaireResponses = useCallback(async (nodeId, answers) => {
    if (!currentDiagram) return;
    
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/diagrams/${currentDiagram.id}/nodes/${nodeId}/questionnaire`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ responses: answers })
        }
      );
      
      if (response.ok) {
        console.log('✅ Questionnaire responses saved:', nodeId);
      } else {
        console.error('❌ Failed to save questionnaire responses:', response.statusText);
      }
    } catch (error) {
      console.error('Error saving questionnaire responses:', error);
    }
  }, [currentDiagram]);
  
  // Helper function to get node category
  const getNodeCategory = (nodeSubtype) => {
    const categoryMap = {
      'API': 'surface',
      'Database': 'asset',
      'Backup': 'control',
      'Monitoring': 'control',
      'WebApp': 'asset',
      'ExternalAttacker': 'actor',
    };
    return categoryMap[nodeSubtype] || 'asset';
  };
  
  // Handle questionnaire cancellation
  const handleQuestionnaireCancel = useCallback((nodeId) => {
    console.log('❌ Questionnaire cancelled:', nodeId);
    
    // Remove from modal stack
    actions.popModal();
    
    // If there are no more modals, end the flow
    if (state.modalStack.length <= 1) {
      actions.endQuestionnaireFlow();
    }
  }, [actions, state.modalStack.length]);
  
  // Expose methods for external use
  const publicMethods = {
    startQuestionnaireForNode,
    handleDependentNodeCreation,
  };
  
  // Store public methods in a ref or context for external access
  useEffect(() => {
    // This could be exposed via a ref or context if needed
    window.questionnaireManager = publicMethods;
    
    return () => {
      delete window.questionnaireManager;
    };
  }, [publicMethods]);
  
  return (
    <>
      {/* Progress Breadcrumbs */}
      {state.isFlowActive && (
        <ProgressBreadcrumbs className="fixed top-0 left-0 right-0 z-40" />
      )}
      
      {/* Render all questionnaire modals in stack order */}
      {state.modalStack.map((modal, index) => {
        if (modal.type !== 'questionnaire') return null;
        
        const zIndex = 1000 + index * 10; // Ensure proper stacking
        
        return (
          <EnhancedSecurityQuestionnaire
            key={modal.id}
            nodeId={modal.nodeId}
            nodeSubtype={modal.nodeSubtype}
            parentNodeId={modal.parentId}
            existingValues={{}}
            zIndex={zIndex}
            onComplete={handleQuestionnaireComplete}
            onCancel={() => handleQuestionnaireCancel(modal.nodeId)}
          />
        );
      })}
    </>
  );
};

export default QuestionnaireManager;