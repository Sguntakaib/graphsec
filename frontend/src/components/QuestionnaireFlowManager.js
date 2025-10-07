import React, { useState, useCallback, useEffect } from 'react';
import { useReactFlow } from '@xyflow/react';

/**
 * QuestionnaireFlowManager - Modern React Flow component for managing questionnaire workflow
 * Utilizes React Flow v12 patterns for efficient data management
 */
const QuestionnaireFlowManager = ({
  currentQuestionnaireNode,
  setCurrentQuestionnaireNode,
  currentQuestionnaireAnswers,
  setCurrentQuestionnaireAnswers,
  showSecurityQuestionnaire,
  setShowSecurityQuestionnaire,
  questionnaireQueue,
  setQuestionnaireQueue,
  currentQueueIndex,
  setCurrentQueueIndex,
  parentQuestionnaireStack,
  setParentQuestionnaireStack,
  activeQuestionnaires,
  setActiveQuestionnaires,
  nodes,
  setNodes,
  currentDiagram
}) => {
  const { updateNodeData, getNode } = useReactFlow();

  // Modern React Flow v12 pattern: Efficient questionnaire data propagation
  const updateQuestionnaireProgress = useCallback(async (nodeId, answers = {}) => {
    const node = getNode(nodeId);
    if (!node) return;

    const nodeSubtype = node.data?.subtype || node.subtype;
    
    try {
      // Get questionnaire metadata for progress calculation
      let metaUrl = `${process.env.REACT_APP_BACKEND_URL}/api/intelligent-nodes/${nodeSubtype}/prompts`;
      if (['WebApp','API','Database','Backup','Monitoring'].includes(nodeSubtype)) {
        metaUrl = `${process.env.REACT_APP_BACKEND_URL}/api/questionnaires/${nodeSubtype}?level=basic`;
      }
      
      const metaRes = await fetch(metaUrl);
      if (metaRes.ok) {
        const meta = await metaRes.json();
        const totalQuestions = meta.total_questions || (meta.prompts ? meta.prompts.length : 0);
        const answeredQuestions = Object.keys(answers).length;
        const completionPercentage = totalQuestions > 0 ? (answeredQuestions / totalQuestions) * 100 : 0;
        
        // Use React Flow v12 updateNodeData for efficient updates
        updateNodeData(nodeId, {
          questionnaireMeta: { 
            total_questions: totalQuestions,
            answered_questions: answeredQuestions,
            completion_percentage: completionPercentage
          },
          questionnaireResponses: answers,
          lastProgressUpdate: new Date().toISOString()
        });
        
        console.log(`📊 Updated questionnaire progress for node ${nodeId}: ${completionPercentage.toFixed(1)}%`);
      }
    } catch (error) {
      console.warn('⚠️ Could not update questionnaire progress:', error.message);
    }
  }, [getNode, updateNodeData]);

  // Modern pattern: Handle questionnaire initialization with dependencies
  const initializeQuestionnaire = useCallback(async (node, existingAnswers = {}) => {
    if (!node) return;

    // Clear any existing questionnaire state
    setQuestionnaireQueue([]);
    setCurrentQueueIndex(0);
    setParentQuestionnaireStack([]);
    
    const nodeSubtype = node.subtype || node.data?.subtype;
    const questionnaireNode = {
      id: node.id,
      subtype: nodeSubtype,
      data: { subtype: nodeSubtype }
    };
    
    // Set questionnaire state
    setCurrentQuestionnaireNode(questionnaireNode);
    setCurrentQuestionnaireAnswers(existingAnswers);
    setShowSecurityQuestionnaire(true);
    
    // Update progress tracking
    await updateQuestionnaireProgress(node.id, existingAnswers);
    
    console.log('🚀 Initialized questionnaire for node:', node.id, 'with subtype:', nodeSubtype);
  }, [
    setQuestionnaireQueue,
    setCurrentQueueIndex,
    setParentQuestionnaireStack,
    setCurrentQuestionnaireNode,
    setCurrentQuestionnaireAnswers,
    setShowSecurityQuestionnaire,
    updateQuestionnaireProgress
  ]);

  // Modern pattern: Handle questionnaire completion with data propagation
  const completeQuestionnaire = useCallback(async (nodeId, answers, validationResult) => {
    try {
      // Update node data with completion info
      const completionData = {
        questionnaireResponses: answers,
        completionStatus: validationResult,
        intelligentNode: true,
        lastQuestionnaireUpdate: new Date().toISOString(),
        isCompleted: true
      };
      
      // Use React Flow v12 updateNodeData for efficient updates
      updateNodeData(nodeId, completionData);
      
      // Update progress to 100%
      await updateQuestionnaireProgress(nodeId, answers);
      
      // Remove from active questionnaires
      setActiveQuestionnaires(prev => {
        const newSet = new Set(prev);
        newSet.delete(nodeId);
        return newSet;
      });
      
      console.log('✅ Completed questionnaire for node:', nodeId);
      
    } catch (error) {
      console.error('❌ Error completing questionnaire:', error);
    }
  }, [updateNodeData, updateQuestionnaireProgress, setActiveQuestionnaires]);

  // Fetch existing questionnaire answers for a node
  const fetchExistingAnswers = useCallback(async (node) => {
    let existingAnswers = {};
    
    // Check node data first
    if (node.data?.questionnaireResponses && Object.keys(node.data.questionnaireResponses).length > 0) {
      existingAnswers = node.data.questionnaireResponses;
      console.log('📝 Found existing answers in node data');
    } else if (currentDiagram) {
      // Fallback to API
      try {
        const response = await fetch(
          `${process.env.REACT_APP_BACKEND_URL}/api/diagrams/${currentDiagram.id}/nodes/${node.id}/questionnaire`
        );
        
        if (response.ok) {
          const data = await response.json();
          existingAnswers = data.questionnaire_responses || {};
          console.log('📝 Fetched existing answers from API');
        }
      } catch (error) {
        console.error('⚠️ Error fetching existing answers:', error);
      }
    }
    
    return existingAnswers;
  }, [currentDiagram]);

  return {
    initializeQuestionnaire,
    completeQuestionnaire,
    fetchExistingAnswers,
    updateQuestionnaireProgress
  };
};

export default QuestionnaireFlowManager;