import React, { createContext, useContext, useReducer, useCallback } from 'react';

// Questionnaire State Structure
const initialState = {
  // Modal stacking management
  modalStack: [], // Array of questionnaire modals in stacking order
  activeModalId: null, // Currently active modal
  
  // Questionnaire flow tracking
  questionnaireFlow: {
    rootNode: null, // The original node that started the flow
    currentPath: [], // Current questionnaire path
    completedPaths: [], // Completed questionnaire paths
    totalQuestionnaires: 0, // Total questionnaires in the flow
    completedQuestionnaires: 0, // Completed questionnaires count
  },
  
  // Individual questionnaire states
  questionnaires: {}, // Key: nodeId, Value: questionnaire state
  
  // Canvas synchronization
  canvasUpdates: {
    pendingNodeUpdates: [], // Nodes awaiting updates
    pendingEdgeCreations: [], // Edges to create
    highlightedNodes: [], // Nodes to highlight during flow
  },
  
  // Dependency management
  dependencies: {
    pendingDependencies: [], // Dependencies waiting to be resolved
    resolutionQueue: [], // Queue of dependency resolutions
  },
  
  // Flow state
  isFlowActive: false,
  isPaused: false,
  currentPhase: 'idle', // 'idle', 'active', 'paused', 'completing'
};

// Action Types
const ACTIONS = {
  // Flow Management
  START_QUESTIONNAIRE_FLOW: 'START_QUESTIONNAIRE_FLOW',
  END_QUESTIONNAIRE_FLOW: 'END_QUESTIONNAIRE_FLOW',
  PAUSE_FLOW: 'PAUSE_FLOW',
  RESUME_FLOW: 'RESUME_FLOW',
  
  // Modal Stack Management
  PUSH_MODAL: 'PUSH_MODAL',
  POP_MODAL: 'POP_MODAL',
  SET_ACTIVE_MODAL: 'SET_ACTIVE_MODAL',
  CLEAR_MODAL_STACK: 'CLEAR_MODAL_STACK',
  
  // Questionnaire State Management
  CREATE_QUESTIONNAIRE: 'CREATE_QUESTIONNAIRE',
  UPDATE_QUESTIONNAIRE: 'UPDATE_QUESTIONNAIRE',
  COMPLETE_QUESTIONNAIRE: 'COMPLETE_QUESTIONNAIRE',
  PAUSE_QUESTIONNAIRE: 'PAUSE_QUESTIONNAIRE',
  RESUME_QUESTIONNAIRE: 'RESUME_QUESTIONNAIRE',
  
  // Progress Tracking
  UPDATE_PROGRESS: 'UPDATE_PROGRESS',
  ADD_QUESTIONNAIRE_TO_FLOW: 'ADD_QUESTIONNAIRE_TO_FLOW',
  MARK_QUESTIONNAIRE_COMPLETE: 'MARK_QUESTIONNAIRE_COMPLETE',
  
  // Canvas Synchronization
  QUEUE_CANVAS_UPDATE: 'QUEUE_CANVAS_UPDATE',
  APPLY_CANVAS_UPDATES: 'APPLY_CANVAS_UPDATES',
  HIGHLIGHT_NODES: 'HIGHLIGHT_NODES',
  CLEAR_HIGHLIGHTS: 'CLEAR_HIGHLIGHTS',
  
  // Dependency Management
  ADD_PENDING_DEPENDENCY: 'ADD_PENDING_DEPENDENCY',
  RESOLVE_DEPENDENCY: 'RESOLVE_DEPENDENCY',
  QUEUE_DEPENDENCY_RESOLUTION: 'QUEUE_DEPENDENCY_RESOLUTION',
};

// Reducer Function
function questionnaireReducer(state, action) {
  switch (action.type) {
    case ACTIONS.START_QUESTIONNAIRE_FLOW:
      return {
        ...state,
        isFlowActive: true,
        currentPhase: 'active',
        questionnaireFlow: {
          ...state.questionnaireFlow,
          rootNode: action.payload.rootNode,
          currentPath: [action.payload.rootNode.id],
          totalQuestionnaires: action.payload.totalQuestionnaires || 1,
        },
      };
      
    case ACTIONS.END_QUESTIONNAIRE_FLOW:
      return {
        ...initialState,
        questionnaires: state.questionnaires, // Preserve questionnaire data
      };
      
    case ACTIONS.PAUSE_FLOW:
      return {
        ...state,
        isPaused: true,
        currentPhase: 'paused',
      };
      
    case ACTIONS.RESUME_FLOW:
      return {
        ...state,
        isPaused: false,
        currentPhase: 'active',
      };
      
    case ACTIONS.PUSH_MODAL:
      const newModalStack = [...state.modalStack, action.payload];
      return {
        ...state,
        modalStack: newModalStack,
        activeModalId: action.payload.id,
      };
      
    case ACTIONS.POP_MODAL:
      const updatedStack = state.modalStack.slice(0, -1);
      return {
        ...state,
        modalStack: updatedStack,
        activeModalId: updatedStack.length > 0 ? updatedStack[updatedStack.length - 1].id : null,
      };
      
    case ACTIONS.SET_ACTIVE_MODAL:
      return {
        ...state,
        activeModalId: action.payload,
      };
      
    case ACTIONS.CLEAR_MODAL_STACK:
      return {
        ...state,
        modalStack: [],
        activeModalId: null,
      };
      
    case ACTIONS.CREATE_QUESTIONNAIRE:
      return {
        ...state,
        questionnaires: {
          ...state.questionnaires,
          [action.payload.nodeId]: {
            nodeId: action.payload.nodeId,
            nodeSubtype: action.payload.nodeSubtype,
            status: 'active', // 'active', 'paused', 'completed'
            currentPromptIndex: 0,
            answers: action.payload.existingAnswers || {},
            prompts: action.payload.prompts || [],
            parentQuestionnaireId: action.payload.parentQuestionnaireId || null,
            childQuestionnaireIds: [],
            createdAt: new Date().toISOString(),
            completedAt: null,
            progress: {
              totalQuestions: action.payload.prompts?.length || 0,
              answeredQuestions: 0,
              completionPercentage: 0,
            },
          },
        },
      };
      
    case ACTIONS.UPDATE_QUESTIONNAIRE:
      const existingQuestionnaire = state.questionnaires[action.payload.nodeId];
      if (!existingQuestionnaire) return state;
      
      return {
        ...state,
        questionnaires: {
          ...state.questionnaires,
          [action.payload.nodeId]: {
            ...existingQuestionnaire,
            ...action.payload.updates,
            progress: {
              ...existingQuestionnaire.progress,
              ...(action.payload.updates.progress || {}),
            },
          },
        },
      };
      
    case ACTIONS.COMPLETE_QUESTIONNAIRE:
      const completedQuestionnaire = state.questionnaires[action.payload.nodeId];
      if (!completedQuestionnaire) return state;
      
      return {
        ...state,
        questionnaires: {
          ...state.questionnaires,
          [action.payload.nodeId]: {
            ...completedQuestionnaire,
            status: 'completed',
            completedAt: new Date().toISOString(),
            progress: {
              ...completedQuestionnaire.progress,
              completionPercentage: 100,
            },
          },
        },
        questionnaireFlow: {
          ...state.questionnaireFlow,
          completedQuestionnaires: state.questionnaireFlow.completedQuestionnaires + 1,
          completedPaths: [
            ...state.questionnaireFlow.completedPaths,
            action.payload.nodeId,
          ],
        },
      };
      
    case ACTIONS.PAUSE_QUESTIONNAIRE:
      return {
        ...state,
        questionnaires: {
          ...state.questionnaires,
          [action.payload.nodeId]: {
            ...state.questionnaires[action.payload.nodeId],
            status: 'paused',
          },
        },
      };
      
    case ACTIONS.RESUME_QUESTIONNAIRE:
      return {
        ...state,
        questionnaires: {
          ...state.questionnaires,
          [action.payload.nodeId]: {
            ...state.questionnaires[action.payload.nodeId],
            status: 'active',
          },
        },
      };
      
    case ACTIONS.ADD_QUESTIONNAIRE_TO_FLOW:
      return {
        ...state,
        questionnaireFlow: {
          ...state.questionnaireFlow,
          totalQuestionnaires: state.questionnaireFlow.totalQuestionnaires + 1,
          currentPath: [...state.questionnaireFlow.currentPath, action.payload.nodeId],
        },
      };
      
    case ACTIONS.QUEUE_CANVAS_UPDATE:
      return {
        ...state,
        canvasUpdates: {
          ...state.canvasUpdates,
          pendingNodeUpdates: [
            ...state.canvasUpdates.pendingNodeUpdates,
            action.payload.nodeUpdate,
          ],
          pendingEdgeCreations: [
            ...state.canvasUpdates.pendingEdgeCreations,
            ...(action.payload.edgeCreations || []),
          ],
        },
      };
      
    case ACTIONS.APPLY_CANVAS_UPDATES:
      return {
        ...state,
        canvasUpdates: {
          ...state.canvasUpdates,
          pendingNodeUpdates: [],
          pendingEdgeCreations: [],
        },
      };
      
    case ACTIONS.HIGHLIGHT_NODES:
      return {
        ...state,
        canvasUpdates: {
          ...state.canvasUpdates,
          highlightedNodes: action.payload.nodeIds,
        },
      };
      
    case ACTIONS.CLEAR_HIGHLIGHTS:
      return {
        ...state,
        canvasUpdates: {
          ...state.canvasUpdates,
          highlightedNodes: [],
        },
      };
      
    case ACTIONS.ADD_PENDING_DEPENDENCY:
      return {
        ...state,
        dependencies: {
          ...state.dependencies,
          pendingDependencies: [
            ...state.dependencies.pendingDependencies,
            action.payload,
          ],
        },
      };
      
    case ACTIONS.RESOLVE_DEPENDENCY:
      return {
        ...state,
        dependencies: {
          ...state.dependencies,
          pendingDependencies: state.dependencies.pendingDependencies.filter(
            dep => dep.id !== action.payload.dependencyId
          ),
        },
      };
      
    case ACTIONS.QUEUE_DEPENDENCY_RESOLUTION:
      return {
        ...state,
        dependencies: {
          ...state.dependencies,
          resolutionQueue: [
            ...state.dependencies.resolutionQueue,
            action.payload,
          ],
        },
      };
      
    default:
      return state;
  }
}

// Context Creation
const QuestionnaireContext = createContext();

// Custom hook for using the context
export const useQuestionnaire = () => {
  const context = useContext(QuestionnaireContext);
  if (!context) {
    throw new Error('useQuestionnaire must be used within a QuestionnaireProvider');
  }
  return context;
};

// Provider Component
export const QuestionnaireProvider = ({ children }) => {
  const [state, dispatch] = useReducer(questionnaireReducer, initialState);
  
  // Action creators
  const actions = {
    // Flow Management
    startQuestionnaireFlow: useCallback((rootNode, totalQuestionnaires) => {
      dispatch({
        type: ACTIONS.START_QUESTIONNAIRE_FLOW,
        payload: { rootNode, totalQuestionnaires },
      });
    }, []),
    
    endQuestionnaireFlow: useCallback(() => {
      dispatch({ type: ACTIONS.END_QUESTIONNAIRE_FLOW });
    }, []),
    
    pauseFlow: useCallback(() => {
      dispatch({ type: ACTIONS.PAUSE_FLOW });
    }, []),
    
    resumeFlow: useCallback(() => {
      dispatch({ type: ACTIONS.RESUME_FLOW });
    }, []),
    
    // Modal Stack Management
    pushModal: useCallback((modalData) => {
      dispatch({
        type: ACTIONS.PUSH_MODAL,
        payload: modalData,
      });
    }, []),
    
    popModal: useCallback(() => {
      dispatch({ type: ACTIONS.POP_MODAL });
    }, []),
    
    setActiveModal: useCallback((modalId) => {
      dispatch({
        type: ACTIONS.SET_ACTIVE_MODAL,
        payload: modalId,
      });
    }, []),
    
    clearModalStack: useCallback(() => {
      dispatch({ type: ACTIONS.CLEAR_MODAL_STACK });
    }, []),
    
    // Questionnaire Management
    createQuestionnaire: useCallback((nodeId, nodeSubtype, prompts, existingAnswers, parentQuestionnaireId) => {
      dispatch({
        type: ACTIONS.CREATE_QUESTIONNAIRE,
        payload: {
          nodeId,
          nodeSubtype,
          prompts,
          existingAnswers,
          parentQuestionnaireId,
        },
      });
    }, []),
    
    updateQuestionnaire: useCallback((nodeId, updates) => {
      dispatch({
        type: ACTIONS.UPDATE_QUESTIONNAIRE,
        payload: { nodeId, updates },
      });
    }, []),
    
    completeQuestionnaire: useCallback((nodeId) => {
      dispatch({
        type: ACTIONS.COMPLETE_QUESTIONNAIRE,
        payload: { nodeId },
      });
    }, []),
    
    pauseQuestionnaire: useCallback((nodeId) => {
      dispatch({
        type: ACTIONS.PAUSE_QUESTIONNAIRE,
        payload: { nodeId },
      });
    }, []),
    
    resumeQuestionnaire: useCallback((nodeId) => {
      dispatch({
        type: ACTIONS.RESUME_QUESTIONNAIRE,
        payload: { nodeId },
      });
    }, []),
    
    // Progress Tracking
    addQuestionnaireToFlow: useCallback((nodeId) => {
      dispatch({
        type: ACTIONS.ADD_QUESTIONNAIRE_TO_FLOW,
        payload: { nodeId },
      });
    }, []),
    
    // Canvas Synchronization
    queueCanvasUpdate: useCallback((nodeUpdate, edgeCreations) => {
      dispatch({
        type: ACTIONS.QUEUE_CANVAS_UPDATE,
        payload: { nodeUpdate, edgeCreations },
      });
    }, []),
    
    applyCanvasUpdates: useCallback(() => {
      dispatch({ type: ACTIONS.APPLY_CANVAS_UPDATES });
    }, []),
    
    highlightNodes: useCallback((nodeIds) => {
      dispatch({
        type: ACTIONS.HIGHLIGHT_NODES,
        payload: { nodeIds },
      });
    }, []),
    
    clearHighlights: useCallback(() => {
      dispatch({ type: ACTIONS.CLEAR_HIGHLIGHTS });
    }, []),
    
    // Dependency Management
    addPendingDependency: useCallback((dependency) => {
      dispatch({
        type: ACTIONS.ADD_PENDING_DEPENDENCY,
        payload: dependency,
      });
    }, []),
    
    resolveDependency: useCallback((dependencyId) => {
      dispatch({
        type: ACTIONS.RESOLVE_DEPENDENCY,
        payload: { dependencyId },
      });
    }, []),
    
    queueDependencyResolution: useCallback((resolution) => {
      dispatch({
        type: ACTIONS.QUEUE_DEPENDENCY_RESOLUTION,
        payload: resolution,
      });
    }, []),
  };
  
  const value = {
    state,
    actions,
    // Computed values
    computed: {
      isFlowActive: state.isFlowActive,
      currentModal: state.modalStack[state.modalStack.length - 1] || null,
      modalStackDepth: state.modalStack.length,
      flowProgress: state.questionnaireFlow.totalQuestionnaires > 0 
        ? Math.round((state.questionnaireFlow.completedQuestionnaires / state.questionnaireFlow.totalQuestionnaires) * 100)
        : 0,
      activeQuestionnaires: Object.values(state.questionnaires).filter(q => q.status === 'active'),
      completedQuestionnaires: Object.values(state.questionnaires).filter(q => q.status === 'completed'),
      pausedQuestionnaires: Object.values(state.questionnaires).filter(q => q.status === 'paused'),
      hasPendingCanvasUpdates: state.canvasUpdates.pendingNodeUpdates.length > 0 || 
                               state.canvasUpdates.pendingEdgeCreations.length > 0,
      hasPendingDependencies: state.dependencies.pendingDependencies.length > 0,
    },
  };
  
  return (
    <QuestionnaireContext.Provider value={value}>
      {children}
    </QuestionnaireContext.Provider>
  );
};

export default QuestionnaireContext;