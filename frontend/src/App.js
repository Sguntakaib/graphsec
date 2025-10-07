import React, { useState, useCallback, useEffect, useMemo } from 'react';
import {
  ReactFlow,
  ReactFlowProvider,
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Panel,
  useReactFlow,
  useNodes,
  useEdges,
  MarkerType,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import './App.css';
import './styles/vulnerability.css';
import { AdvancedNodeLibrary } from './components/AdvancedNodeLibrary';
import { PropertiesPanel } from './components/PropertiesPanel';
import { EnhancedSimulationPanel } from './components/EnhancedSimulationPanel';
import NodeInfoPanel from './components/NodeInfoPanel';
import { TemplateLibrary } from './components/TemplateLibrary';
import { CustomNode } from './components/CustomNode';
import SecurityQuestionnaire from './components/SecurityQuestionnaire';
import QuestionnaireFlowManager from './components/QuestionnaireFlowManager';
import ReactFlowCanvasManager from './components/ReactFlowCanvasManager';
import ReactFlowPerformanceMonitor from './components/ReactFlowPerformanceMonitor';
import QuestionnaireOverview from './components/QuestionnaireOverview';
import SmartNodeConnector from './components/SmartNodeConnector';
import SimulationDebugger from './components/SimulationDebugger';
import NodeBranchVisualizer from './components/NodeBranchVisualizer';
import UIComparisonDemo from './components/UIComparisonDemo';

import { QuestionnaireProvider, useQuestionnaire } from './contexts/QuestionnaireContext';
import { QuestionnaireConfirmationProvider } from './contexts/QuestionnaireConfirmationContext';
// import QuestionnaireManager from './components/QuestionnaireManager'; // DISABLED: Using legacy system only
// import CanvasSynchronizer from './components/CanvasSynchronizer'; // DISABLED: Causing infinite re-render loops
import VulnerabilityNode from './components/VulnerabilityNode';
import VulnerabilityPanel from './components/VulnerabilityPanel';
import VulnerabilityEdge from './components/VulnerabilityEdge';
import VulnerabilityFilter from './components/VulnerabilityFilter';
import VulnerabilityLegend from './components/VulnerabilityLegend';
import VulnerabilityList from './components/VulnerabilityList';
import VulnerabilityReport from './components/VulnerabilityReport';
import AdvancedLayoutControls from './components/AdvancedLayoutControls';
import DraggableEdge from './components/DraggableEdge';
import StridePanel from './components/StridePanel';
import NodeInfoOverlay from './components/NodeInfoOverlay';
import { Toaster } from './components/ui/toaster';
import { Badge } from './components/ui/badge';
import { Button } from './components/ui/button';
import { useNotification } from './hooks/useNotification';
import { getDiagrams, createDiagram, updateDiagram, simulateAttackPaths, autoLayoutDiagram, applyTemplateToCurrentDiagram } from './services/api';
import { analyzeNodeVulnerabilities, getNodeVulnerabilities, createVulnerabilityNodes, createVulnerabilityEdges } from './services/vulnerabilityApi';
import { 
  Shield, 
  Play, 
  Save, 
  FolderOpen, 
  Maximize2, 
  RotateCcw, 
  Settings,
  Zap,
  BarChart3,
  Download,
  Upload,
  Layers,
  Eye,
  EyeOff,
  Undo,
  Redo,
  Grid,
  ZoomIn,
  ZoomOut,
  Monitor,
  Copy,
  Trash2,
  Edit,
  MoreVertical,
  BookOpen,
  Network,
  AlertTriangle,
  Filter,
  X,
  Menu,
  ChevronUp,
  ChevronDown,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';

const nodeTypes = {
  custom: CustomNode,
  vulnerability: VulnerabilityNode,
};

const edgeTypes = {
  'vulnerability-edge': VulnerabilityEdge,
  'draggable': DraggableEdge,
  'default': DraggableEdge,  // Make all edges draggable by default
};

const initialNodes = [];
const initialEdges = [];

function AppContent() {
  // Add ResizeObserver error handler to prevent console spam
  useEffect(() => {
    const resizeObserverErrHandler = (e) => {
      if (e.message === 'ResizeObserver loop completed with undelivered notifications.' || 
          e.message === 'ResizeObserver loop limit exceeded') {
        e.stopImmediatePropagation();
        return false;
      }
    };
    window.addEventListener('error', resizeObserverErrHandler, true);
    return () => window.removeEventListener('error', resizeObserverErrHandler, true);
  }, []);

  const [nodes, setNodes, defaultOnNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, defaultOnEdgesChange] = useEdgesState(initialEdges);
  // Enhanced questionnaire system disabled - using legacy system only
  const [selectedNode, setSelectedNode] = useState(null);
  const [selectedEdge, setSelectedEdge] = useState(null);  // Add selected edge state
  
  // Notification service
  const notification = useNotification();
  
  // Custom onEdgesChange to maintain selectedEdge state
  const onEdgesChange = useCallback((changes) => {
    // Apply the default edge changes
    defaultOnEdgesChange(changes);
    
    // If the selected edge is being removed, clear the selection
    const removeChanges = changes.filter(change => change.type === 'remove');
    if (selectedEdge && removeChanges.some(change => change.id === selectedEdge.id)) {
      setSelectedEdge(null);
    }
  }, [defaultOnEdgesChange, selectedEdge]);
  
  const [currentDiagram, setCurrentDiagram] = useState(null);
  const [simulationResult, setSimulationResult] = useState(null);
  const [diagrams, setDiagrams] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [viewMode, setViewMode] = useState('modeling'); // 'modeling' or 'analysis'
  const [showUIDemo, setShowUIDemo] = useState(false);
  const [highlightedPaths, setHighlightedPaths] = useState([]);
  const [showAdvancedControls, setShowAdvancedControls] = useState(false);
  const [undoStack, setUndoStack] = useState([]);
  const [redoStack, setRedoStack] = useState([]);
  const [snapToGrid, setSnapToGrid] = useState(true);
  const [gridSize, setGridSize] = useState(20);
  const [zoomLevel, setZoomLevel] = useState(1);
  const [showPerformanceMonitor, setShowPerformanceMonitor] = useState(false);
  const [contextMenu, setContextMenu] = useState(null);
  const [showTemplateLibrary, setShowTemplateLibrary] = useState(false);
  const [showSecurityQuestionnaire, setShowSecurityQuestionnaire] = useState(false);
  const [currentQuestionnaireNode, setCurrentQuestionnaireNode] = useState(null);
  const [currentQuestionnaireAnswers, setCurrentQuestionnaireAnswers] = useState({});
  const [nodeBranches, setNodeBranches] = useState({}); // Store security branches for each node
  const [showQuestionnaireOverview, setShowQuestionnaireOverview] = useState(false);
  const [overviewNode, setOverviewNode] = useState(null);
  const [questionnaireQueue, setQuestionnaireQueue] = useState([]); // Queue for chained questionnaires
  const [currentQueueIndex, setCurrentQueueIndex] = useState(0);
  const [parentQuestionnaireStack, setParentQuestionnaireStack] = useState([]); // Stack for resuming nested parent questionnaires
  const [dependencyStates, setDependencyStates] = useState({}); // Track dependency states per parent node: {parentNodeId: {API: 'COMPLETED', Database: 'CREATED'}}
  const [activeQuestionnaires, setActiveQuestionnaires] = useState(new Set()); // Track which questionnaires are currently active to prevent duplicates
  
  // QW-3: Save status tracking - MOVED BEFORE CALLBACK
  const [lastSavedAt, setLastSavedAt] = useState(null);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  
  // QW-3: Clear All confirmation dialog state
  const [showClearAllConfirm, setShowClearAllConfirm] = useState(false);
  
  // Vulnerability system state
  const [vulnerabilityAnalyses, setVulnerabilityAnalyses] = useState({}); // Store vulnerability analyses by node ID
  const [selectedVulnerability, setSelectedVulnerability] = useState(null);
  const [showVulnerabilityPanel, setShowVulnerabilityPanel] = useState(false);
  const [showVulnerabilityFilter, setShowVulnerabilityFilter] = useState(false);
  const [showVulnerabilityLegend, setShowVulnerabilityLegend] = useState(false);
  const [showVulnerabilityReport, setShowVulnerabilityReport] = useState(false);
  const [showVulnerabilityList, setShowVulnerabilityList] = useState(false); // Phase 2: Enhanced vulnerability list
  const [vulnerabilityNodesVisible, setVulnerabilityNodesVisible] = useState(true); // Global toggle for vulnerability nodes
  
  // Node info overlay state
  const [showNodeInfoOverlay, setShowNodeInfoOverlay] = useState(false);
  const [nodeInfoOverlayData, setNodeInfoOverlayData] = useState(null);
  const [overlayHoverTimer, setOverlayHoverTimer] = useState(null);
  
  // Collapsible sections state
  const [isCanvasNodesCollapsed, setIsCanvasNodesCollapsed] = useState(false);
  const [isStrideCollapsed, setIsStrideCollapsed] = useState(true);
  const [isVulnerabilitiesCollapsed, setIsVulnerabilitiesCollapsed] = useState(true);
  const [isAdvancedLayoutCollapsed, setIsAdvancedLayoutCollapsed] = useState(false);
  
  // STRIDE Analysis count state
  const [strideThreatsCount, setStrideThreatsCount] = useState(0);
  const [vulnerabilityFilter, setVulnerabilityFilter] = useState({
    severity: [],
    category: [],
    nodeTypes: [],
    searchText: '',
    showFixed: false
  });
  const [filteredVulnerabilities, setFilteredVulnerabilities] = useState([]);
  const [autoVulnerabilityAnalysis, setAutoVulnerabilityAnalysis] = useState(false); // Disabled by default - require manual trigger after complete questionnaire
  
  // Vulnerability dropdown menu state
  const [showVulnMenu, setShowVulnMenu] = useState(false);
  const [showClearConfirmation, setShowClearConfirmation] = useState(false);
  
  // Collapsible menu states
  const [isLeftSidebarCollapsed, setIsLeftSidebarCollapsed] = useState(false);
  const [isTopToolbarCollapsed, setIsTopToolbarCollapsed] = useState(false);

  // Custom onNodesChange to track unsaved changes - MOVED AFTER STATE DECLARATIONS
  const onNodesChange = useCallback((changes) => {
    // Apply the default node changes
    defaultOnNodesChange(changes);
    
    // QW-3: Mark as having unsaved changes for non-selection changes
    if (changes.some(change => change.type !== 'select')) {
      setHasUnsavedChanges(true);
    }
  }, [defaultOnNodesChange, setHasUnsavedChanges]);

  // Handle editing questionnaire from node info panel
  const handleEditQuestionnaireFromInfo = useCallback(async (node) => {
    console.log('🎯 Edit questionnaire triggered from info panel for node:', node.id);
    
    // Get existing answers from node data
    let existingAnswers = {};
    
    if (node.data?.questionnaireResponses && Object.keys(node.data.questionnaireResponses).length > 0) {
      existingAnswers = node.data.questionnaireResponses;
      console.log('📝 Found existing questionnaire answers in node data:', existingAnswers);
    } else if (currentDiagram) {
      // Fallback to backend API if no data in node
      try {
        const response = await fetch(
          `${process.env.REACT_APP_BACKEND_URL}/api/diagrams/${currentDiagram.id}/nodes/${node.id}/questionnaire`
        );
        
        if (response.ok) {
          const data = await response.json();
          existingAnswers = data.questionnaire_responses || {};
          console.log('📝 Fetched existing questionnaire answers from backend:', existingAnswers);
        }
      } catch (error) {
        console.error('⚠️ Error fetching existing questionnaire answers from backend:', error);
      }
    }
    
    // Set up questionnaire state
    const nodeSubtype = node.subtype || node.data?.subtype;
    console.log('🚀 Opening Security Questionnaire for editing');
    
    // Clear any existing questionnaire state
    setQuestionnaireQueue([]);
    setCurrentQueueIndex(0);
    setParentQuestionnaireStack([]);
    
    // Set the state to open questionnaire
    const questionnaireNode = {
      id: node.id,
      subtype: nodeSubtype,
      data: { subtype: nodeSubtype }
    };
    
    setCurrentQuestionnaireNode(questionnaireNode);
    setCurrentQuestionnaireAnswers(existingAnswers);
    setShowSecurityQuestionnaire(true);
    
    // Store questionnaire meta on node for accurate progress (e.g., total_questions)
    try {
      let metaUrl = `${process.env.REACT_APP_BACKEND_URL}/api/intelligent-nodes/${nodeSubtype}/prompts`;
      if (['WebApp','API','Database','Backup','Monitoring'].includes(nodeSubtype)) {
        metaUrl = `${process.env.REACT_APP_BACKEND_URL}/api/questionnaires/${nodeSubtype}?level=basic`;
      }
      const metaRes = await fetch(metaUrl);
      if (metaRes.ok) {
        const meta = await metaRes.json();
        const total = meta.total_questions || (meta.prompts ? meta.prompts.length : 0);
        setNodes(nds => nds.map(n => n.id === node.id ? ({
          ...n,
          data: {
            ...n.data,
            questionnaireMeta: { total_questions: total }
          }
        }) : n));
      }
    } catch (e) {
      console.log('ℹ️ Could not fetch questionnaire meta for progress:', e?.message);
    }
  }, [currentDiagram]);

  // Track zoom level changes
  const onMoveEnd = useCallback((event, viewport) => {
    setZoomLevel(Math.round(viewport.zoom * 100) / 100);
  }, []);

  // Double-tap handler for nodes - Direct questionnaire access
  const handleNodeDoubleTap = useCallback(async (event) => {
    console.log('🎯 App.js: Received nodeDoubleTap event:', event.detail);
    
    const { nodeId, nodeData } = event.detail;
    const node = nodes.find(n => n.id === nodeId);
    
    console.log('🔍 Double-tap handler state check:', {
      nodeId,
      nodeFound: !!node,
      currentDiagram: !!currentDiagram,
      nodesLength: nodes.length
    });
    
    if (node) { // Remove currentDiagram requirement for now
      console.log('🎯 Double-tap detected on node:', nodeId);
      
      // Get existing answers - try node data first, then backend API
      let existingAnswers = {};
      
      // First check if questionnaire responses are stored in node data (for auto-created dependent nodes)
      if (node.data?.questionnaireResponses && Object.keys(node.data.questionnaireResponses).length > 0) {
        existingAnswers = node.data.questionnaireResponses;
        console.log('📝 Found existing questionnaire answers in node data:', existingAnswers);
      } else if (node.questionnaireResponses && Object.keys(node.questionnaireResponses).length > 0) {
        existingAnswers = node.questionnaireResponses;
        console.log('📝 Found existing questionnaire answers in node root:', existingAnswers);
      } else if (currentDiagram) {
        // Fallback to backend API if no data in node
        try {
          const response = await fetch(
            `${process.env.REACT_APP_BACKEND_URL}/api/diagrams/${currentDiagram.id}/nodes/${node.id}/questionnaire`
          );
          
          if (response.ok) {
            const data = await response.json();
            existingAnswers = data.questionnaire_responses || {};
            console.log('📝 Fetched existing questionnaire answers from backend:', existingAnswers);
          } else {
            console.log('⚠️ No existing questionnaire data found in backend, starting fresh questionnaire');
          }
        } catch (error) {
          console.error('⚠️ Error fetching existing questionnaire answers from backend:', error);
        }
      } else {
        console.log('⚠️ No currentDiagram available, starting fresh questionnaire');
      }
      
      // Directly set questionnaire state instead of calling startLegacyQuestionnaire
      const nodeSubtype = node.subtype || node.data?.subtype;
      console.log('🚀 Opening Security Questionnaire directly from double-click');
      
      // Clear any existing questionnaire state to prevent completion logic from triggering
      setQuestionnaireQueue([]);
      setCurrentQueueIndex(0);
      setParentQuestionnaireStack([]); // Clear parent stack
      
      // Set the state directly to open questionnaire
      const questionnaireNode = {
        id: node.id,
        subtype: nodeSubtype,
        data: { subtype: nodeSubtype }
      };
      
      console.log('🔧 Setting questionnaire state:', {
        showSecurityQuestionnaire: true,
        currentQuestionnaireNode: questionnaireNode,
        existingAnswers
      });
      
      setCurrentQuestionnaireNode(questionnaireNode);
      setCurrentQuestionnaireAnswers(existingAnswers);
      setShowSecurityQuestionnaire(true);
      
      // Store questionnaire meta on node for accurate progress (e.g., total_questions)
      try {
        let metaUrl = `${process.env.REACT_APP_BACKEND_URL}/api/intelligent-nodes/${nodeSubtype}/prompts`;
        if (['WebApp','API','Database','Backup','Monitoring'].includes(nodeSubtype)) {
          metaUrl = `${process.env.REACT_APP_BACKEND_URL}/api/questionnaires/${nodeSubtype}?level=basic`;
        }
        const metaRes = await fetch(metaUrl);
        if (metaRes.ok) {
          const meta = await metaRes.json();
          const total = meta.total_questions || (meta.prompts ? meta.prompts.length : 0);
          setNodes(nds => nds.map(n => n.id === node.id ? ({
            ...n,
            data: {
              ...n.data,
              questionnaireMeta: { total_questions: total }
            }
          }) : n));
        }
      } catch (e) {
        console.log('ℹ️ Could not fetch questionnaire meta for progress:', e?.message);
      }
      
      // Force a state check after setting
      setTimeout(() => {
        console.log('🔍 State check after 100ms:', {
          showSecurityQuestionnaire: true, // Should be true
          currentQuestionnaireNode: questionnaireNode // Should be set
        });
      }, 100);
    }
  }, [nodes, currentDiagram]); // Proper dependencies for useCallback

  // Edge update handler for draggable edges
  const handleEdgeUpdate = useCallback((event) => {
    const { edgeId, updateData } = event.detail;
    console.log('🔧 Received edge update:', edgeId, updateData);
    
    setEdges((currentEdges) => {
      const updatedEdges = currentEdges.map((edge) => {
        if (edge.id === edgeId) {
          const updatedEdge = {
            ...edge,
            // Update top-level properties like label
            ...(updateData.label !== undefined && { label: updateData.label }),
            data: {
              ...edge.data,
              ...updateData
            }
          };
          return updatedEdge;
        }
        return edge;
      });
      
      // If the updated edge is currently selected, update the selectedEdge state with the new edge object
      // Use a callback-based update to ensure we get the latest edge from the updated edges array
      if (selectedEdge?.id === edgeId) {
        const newSelectedEdge = updatedEdges.find(edge => edge.id === edgeId);
        if (newSelectedEdge) {
          setSelectedEdge(newSelectedEdge);
        }
      }
      
      return updatedEdges;
    });
  }, [selectedEdge]); // Add selectedEdge dependency

  // Node hover handlers for info overlay
  const handleNodeHover = useCallback(async (event) => {
    const { nodeId, nodeData, position } = event.detail;
    const node = nodes.find(n => n.id === nodeId);
    
    if (!node || node.type === 'vulnerability') return; // Skip vulnerability nodes
    
    // Clear any existing hover timer and immediately hide existing overlay
    if (overlayHoverTimer) {
      clearTimeout(overlayHoverTimer);
      setOverlayHoverTimer(null);
    }
    
    // If switching to a different node, immediately switch overlays
    if (showNodeInfoOverlay && nodeInfoOverlayData?.node?.id !== nodeId) {
      // Clear existing timer and immediately switch to new node
      console.log('🎯 Switching from node', nodeInfoOverlayData.node.id, 'to node', nodeId);
    }
    
    // Get node statistics
    const nodeSubtype = node.data?.subtype || node.subtype;
    let answeredQuestions = 0;
    let totalQuestions = 0;
    let vulnerabilityCount = 0;
    let strideScore = 0;
    
    // Calculate answered questions
    const questionnaireResponses = node.data?.questionnaireResponses || node.questionnaireResponses || {};
    answeredQuestions = Object.keys(questionnaireResponses).length;
    
    // Get total questions from node meta or fetch from API
    if (node.data?.questionnaireMeta?.total_questions) {
      totalQuestions = node.data.questionnaireMeta.total_questions;
    } else {
      try {
        let metaUrl = `${process.env.REACT_APP_BACKEND_URL}/api/intelligent-nodes/${nodeSubtype}/prompts`;
        if (['WebApp','API','Database','Backup','Monitoring'].includes(nodeSubtype)) {
          metaUrl = `${process.env.REACT_APP_BACKEND_URL}/api/questionnaires/${nodeSubtype}?level=basic`;
        }
        const metaRes = await fetch(metaUrl);
        if (metaRes.ok) {
          const meta = await metaRes.json();
          totalQuestions = meta.total_questions || (meta.prompts ? meta.prompts.length : 0);
        }
      } catch (e) {
        console.log('Could not fetch question count:', e.message);
      }
    }
    
    // Get vulnerability count for this node
    if (vulnerabilityAnalyses[nodeId]) {
      const analysis = vulnerabilityAnalyses[nodeId];
      // Try different possible data structures
      vulnerabilityCount = analysis.vulnerabilities?.length || 
                          analysis.vulnerability_nodes?.length || 
                          analysis.total_vulnerabilities || 
                          0;
    } else {
      // Try to fetch vulnerability data from API if not in state
      try {
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/vulnerabilities/analyze/${nodeId}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            node_id: nodeId,
            node_type: nodeSubtype,
            questionnaire_responses: questionnaireResponses,
            node_position: node.position
          })
        });
        if (response.ok) {
          const vulnData = await response.json();
          vulnerabilityCount = vulnData.vulnerabilities?.length || vulnData.total_vulnerabilities || 0;
        }
      } catch (e) {
        console.log('Could not fetch vulnerability count:', e.message);
      }
    }
    
    // Get STRIDE score for this node (use diagram-level analysis)
    if (currentDiagram?.id) {
      try {
        console.log('🎯 Fetching STRIDE data for diagram:', currentDiagram.id);
        
        // Get STRIDE coverage data (diagram-level analysis)
        const strideResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/diagrams/${currentDiagram.id}/stride/coverage`);
        
        if (strideResponse.ok) {
          const coverageData = await strideResponse.json();
          console.log('🎯 STRIDE coverage data:', coverageData);
          
          if (coverageData.total_threats > 0) {
            // Use existing analysis data - all nodes show same diagram risk
            strideScore = coverageData.residual_risk_avg || 0;
            console.log('🎯 Using STRIDE coverage average:', strideScore);
          } else {
            // No existing analysis, try to get stored threats
            const threatsResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/diagrams/${currentDiagram.id}/stride/threats`);
            if (threatsResponse.ok) {
              const threatsData = await threatsResponse.json();
              const threats = threatsData.threats || [];
              
              if (threats.length > 0) {
                // Calculate average from stored threats
                const threatScores = threats.map(threat => threat.residual_risk || 0);
                const totalRisk = threatScores.reduce((sum, score) => sum + score, 0);
                strideScore = totalRisk / threats.length;
                console.log('🎯 Calculated STRIDE score from stored threats:', strideScore);
              }
            }
          }
        } else {
          console.log('🎯 STRIDE coverage API returned:', strideResponse.status);
        }
      } catch (e) {
        console.error('🎯 STRIDE API exception:', e.message);
      }
    } else {
      console.log('🎯 No current diagram ID available for STRIDE analysis');
    }
    
    console.log('🎯 Setting overlay data:', {
      nodeId,
      nodeSubtype,
      answeredQuestions,
      totalQuestions,
      vulnerabilityCount,
      strideScore: strideScore.toFixed(1)
    });
    
    setNodeInfoOverlayData({
      node,
      position,
      answeredQuestions,
      totalQuestions,
      vulnerabilityCount,
      strideScore
    });
    setShowNodeInfoOverlay(true);
  }, [nodes, vulnerabilityAnalyses, overlayHoverTimer]);

  const handleNodeHoverEnd = useCallback((event) => {
    // Immediately hide overlay when mouse leaves node (no delay)
    clearTimeout(overlayHoverTimer);
    setOverlayHoverTimer(null);
    setShowNodeInfoOverlay(false);
    setNodeInfoOverlayData(null);
  }, [overlayHoverTimer]);

  const closeNodeInfoOverlay = useCallback(() => {
    setShowNodeInfoOverlay(false);
    setNodeInfoOverlayData(null);
    if (overlayHoverTimer) {
      clearTimeout(overlayHoverTimer);
      setOverlayHoverTimer(null);
    }
  }, [overlayHoverTimer]);

  const handleOverlayHover = useCallback((event) => {
    const action = event.detail?.action;
    
    if (action === 'enter') {
      // Cancel any pending hide timer when hovering over overlay
      if (overlayHoverTimer) {
        clearTimeout(overlayHoverTimer);
        setOverlayHoverTimer(null);
      }
    } else if (action === 'leave') {
      // Hide overlay when leaving overlay area
      setShowNodeInfoOverlay(false);
      setNodeInfoOverlayData(null);
    }
  }, [overlayHoverTimer]);

  useEffect(() => {
    window.addEventListener('nodeDoubleTap', handleNodeDoubleTap);
    window.addEventListener('edgeUpdate', handleEdgeUpdate);
    window.addEventListener('nodeHover', handleNodeHover);
    window.addEventListener('nodeHoverEnd', handleNodeHoverEnd);
    window.addEventListener('overlayHover', handleOverlayHover);
    return () => {
      window.removeEventListener('nodeDoubleTap', handleNodeDoubleTap);
      window.removeEventListener('edgeUpdate', handleEdgeUpdate);
      window.removeEventListener('nodeHover', handleNodeHover);
      window.removeEventListener('nodeHoverEnd', handleNodeHoverEnd);
      window.removeEventListener('overlayHover', handleOverlayHover);
    };
  }, [handleNodeDoubleTap, handleEdgeUpdate, handleNodeHover, handleNodeHoverEnd, handleOverlayHover]); // Use the memoized callbacks

  // Performance monitoring
  const [performance, setPerformance] = useState({
    nodeCount: 0,
    edgeCount: 0,
    renderTime: 0
  });

  useEffect(() => {
    const startTime = performance.now ? performance.now() : Date.now();
    
    setPerformance(prev => ({
      ...prev,
      nodeCount: nodes.length,
      edgeCount: edges.length,
      renderTime: Math.round((performance.now ? performance.now() : Date.now()) - startTime)
    }));
  }, []); // Remove nodes, edges dependencies to prevent infinite loop
  
  const { fitView, zoomIn, zoomOut, updateNodeData, updateEdgeData, getNode, getEdge } = useReactFlow();
  
  // Modern React Flow v12 hooks for reactive state management
  const reactFlowNodes = useNodes();
  const reactFlowEdges = useEdges();

  // Modern React Flow v12 pattern: Efficient node data updates
  const updateNodeDataEfficiently = useCallback((nodeId, newData) => {
    updateNodeData(nodeId, newData);
    console.log('🔄 Updated node data using React Flow v12 updateNodeData:', nodeId, newData);
  }, [updateNodeData]);

  // Modern React Flow v12 pattern: Efficient edge data updates
  const updateEdgeDataEfficiently = useCallback((edgeId, newData) => {
    updateEdgeData(edgeId, newData);
    console.log('🔄 Updated edge data using React Flow v12 updateEdgeData:', edgeId, newData);
  }, [updateEdgeData]);

  // Modern React Flow v12 pattern: Get node with data dependencies
  const getNodeWithDependencies = useCallback((nodeId) => {
    const node = getNode(nodeId);
    if (!node) return null;
    
    // Get connections for this node using modern pattern
    const connectedEdges = reactFlowEdges.filter(edge => 
      edge.source === nodeId || edge.target === nodeId
    );
    
    return {
      ...node,
      connectedEdges,
      connectionCount: connectedEdges.length
    };
  }, [getNode, reactFlowEdges]);

  // Initialize modern React Flow component managers
  const questionnaireFlowManager = QuestionnaireFlowManager({
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
  });

  const canvasManager = ReactFlowCanvasManager({
    nodes,
    edges,
    setNodes,
    setEdges,
    selectedNode,
    setSelectedNode,
    selectedEdge,
    setSelectedEdge
  });

  // Function to automatically fit all nodes within canvas when they go out of bounds
  const handleFitAllNodes = useCallback(() => {
    if (nodes.length === 0) return;
    
    // Get the bounds of all nodes
    const bounds = nodes.reduce((acc, node) => {
      const x = node.position.x;
      const y = node.position.y;
      const width = node.width || 200;
      const height = node.height || 100;
      
      return {
        minX: Math.min(acc.minX, x),
        minY: Math.min(acc.minY, y),
        maxX: Math.max(acc.maxX, x + width),
        maxY: Math.max(acc.maxY, y + height)
      };
    }, { minX: Infinity, minY: Infinity, maxX: -Infinity, maxY: -Infinity });
    
    // Check if any nodes are out of visible bounds
    const canvasWidth = window.innerWidth - 300;
    const canvasHeight = window.innerHeight - 200;
    const padding = 50;
    
    const nodesOutOfBounds = bounds.minX < padding || 
                           bounds.minY < padding || 
                           bounds.maxX > canvasWidth - padding || 
                           bounds.maxY > canvasHeight - padding;
    
    if (nodesOutOfBounds) {
      // Fit view with animation
      fitView({ 
        padding: 0.1,
        includeHiddenNodes: false,
        minZoom: 0.2,
        maxZoom: 1.5,
        duration: 600
      });
    }
  }, [fitView]); // Remove nodes dependency to prevent infinite loop

  // Auto-check for out-of-bounds nodes when nodes change
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      handleFitAllNodes();
    }, 500); // Small delay to avoid constant checking
    
    return () => clearTimeout(timeoutId);
  }, [handleFitAllNodes]); // Remove nodes dependency to prevent infinite loop

  // Save state for undo/redo
  const saveStateToUndoStack = useCallback(() => {
    const currentState = {
      nodes: [...nodes],
      edges: [...edges],
      timestamp: Date.now()
    };
    
    setUndoStack(prev => [...prev.slice(-19), currentState]); // Keep last 20 states
    setRedoStack([]); // Clear redo stack when new action is performed
  }, [nodes, edges]); // Properly include dependencies

  // Smart Node Connector instance (memoized to prevent recreation on every render)
  const smartNodeConnector = useMemo(() => 
    new SmartNodeConnector(setNodes, setEdges, saveStateToUndoStack), 
    [saveStateToUndoStack]
  );

  // Undo functionality
  const handleUndo = useCallback(() => {
    if (undoStack.length === 0) return;
    
    const currentState = {
      nodes: [...nodes],
      edges: [...edges],
      timestamp: Date.now()
    };
    
    const previousState = undoStack[undoStack.length - 1];
    
    setRedoStack(prev => [currentState, ...prev.slice(0, 19)]);
    setUndoStack(prev => prev.slice(0, -1));
    
    setNodes(previousState.nodes);
    setEdges(previousState.edges);
  }, [undoStack]); // Remove nodes, edges dependencies to prevent infinite loop

  // Redo functionality
  const handleRedo = useCallback(() => {
    if (redoStack.length === 0) return;
    
    const currentState = {
      nodes: [...nodes],
      edges: [...edges],
      timestamp: Date.now()
    };
    
    const nextState = redoStack[0];
    
    setUndoStack(prev => [...prev, currentState]);
    setRedoStack(prev => prev.slice(1));
    
    setNodes(nextState.nodes);
    setEdges(nextState.edges);
  }, [redoStack]); // Remove nodes, edges dependencies to prevent infinite loop

  // Enhanced edge styles for attack paths
  const defaultEdgeOptions = useMemo(() => ({
    type: 'draggable',  // Use draggable type for all edges
    markerEnd: {
      type: MarkerType.ArrowClosed,
      color: '#9CA3AF',
    },
    style: {
      strokeWidth: 2,
      stroke: '#9CA3AF',
    },
  }), []);

  const attackPathEdgeOptions = useMemo(() => ({
    type: 'draggable',  // Use draggable type for attack path edges
    markerEnd: {
      type: MarkerType.ArrowClosed,
      color: '#EF4444',
    },
    style: {
      strokeWidth: 3,
      stroke: '#EF4444',
      strokeDasharray: '5,5',
    },
    animated: true,
  }), []);

  useEffect(() => {
    loadDiagrams();
  }, []);

  const loadDiagrams = async () => {
    try {
      const diagramsList = await getDiagrams();
      setDiagrams(diagramsList);
    } catch (error) {
      console.error('Failed to load diagrams:', error);
    }
  };

  // Dependency State Management Functions
  const getDependencyState = (parentNodeId, dependencyType) => {
    return dependencyStates[parentNodeId]?.[dependencyType] || 'PENDING';
  };

  const setDependencyState = (parentNodeId, dependencyType, state) => {
    console.log(`🔄 Setting dependency state: ${parentNodeId} → ${dependencyType} = ${state}`);
    setDependencyStates(prev => ({
      ...prev,
      [parentNodeId]: {
        ...prev[parentNodeId],
        [dependencyType]: state
      }
    }));
  };

  const getIncompleteDependencies = (parentNodeId, allDependencies) => {
    if (!allDependencies || allDependencies.length === 0) return [];
    
    const incompleteDependencies = allDependencies.filter(dep => {
      const state = getDependencyState(parentNodeId, dep);
      return state !== 'COMPLETED';
    });
    
    console.log(`🔍 Incomplete dependencies for ${parentNodeId}:`, incompleteDependencies);
    return incompleteDependencies;
  };

  const onConnect = useCallback(
    (params) => {
      // Find source and target nodes
      const sourceNode = nodes.find(n => n.id === params.source);
      const targetNode = nodes.find(n => n.id === params.target);
      
      // Get connection info with enhanced styling
      const connectionInfo = getConnectionInfo(sourceNode, targetNode);
      
      // Create enhanced edge with connection-specific styling
      const newEdge = {
        ...params,
        id: `edge-${params.source}-${params.target}-${Date.now()}`,
        type: 'draggable',  // Use draggable edge type
        label: connectionInfo.label,
        animated: true,  // Add animation like auto-connected edges
        style: {
          ...connectionInfo.style,
          strokeDasharray: '3,3',  // Add dotted pattern like auto-connected edges
          stroke: '#10B981'  // Use same green color as auto-connected dependency edges
        },
        markerEnd: {
          ...connectionInfo.markerEnd,
          color: '#10B981'  // Use same green color as auto-connected dependency edges
        },
        labelStyle: {
          ...connectionInfo.labelStyle,
          fill: '#ffffff',  // White text like auto-connected edges
          fontWeight: 600,
          fontSize: '12px'
        },
        labelBgStyle: {
          ...connectionInfo.labelBgStyle,
          fill: 'rgba(17, 24, 39, 0.9)',  // Dark background like auto-connected edges
          stroke: '#10B981',  // Green border like auto-connected edges
          strokeWidth: 1,
          fillOpacity: 0.9
        },
        labelShowBg: true,
        labelBgBorderRadius: 4,
        labelBgPadding: [4, 8],
        data: {
          // Store initial control points and label position
          controlPoint1: { x: 0, y: 0 },
          controlPoint2: { x: 0, y: 0 },
          labelPosition: 0.5
        }
      };
      
      setEdges((eds) => addEdge(newEdge, eds));
    },
    [nodes, setEdges],
  );

  const onNodeClick = useCallback(async (event, node) => {
    // Handle vulnerability node clicks
    if (node.type === 'vulnerability') {
      handleVulnerabilityNodeClick(node.data);
      return;
    }
    
    // For custom nodes (WebApp, API, Database, etc.), let the CustomNode component
    // handle the click events including double-tap detection for questionnaires
    if (node.type === 'custom') {
      // Set the selected node immediately to show information in right panel
      setSelectedNode(node);
      
      // Don't handle the click here for double-tap - let CustomNode's handleNodeClick take over
      // This allows the double-tap detection logic in CustomNode.js to work properly
      return;
    }
    
    setSelectedNode(node);
    setContextMenu(null); // Close context menu when clicking node
  }, []);

  const onEdgeClick = (event, edge) => {
    setSelectedNode(null);
    setSelectedEdge(edge);  // Set selected edge for showing control points
    setContextMenu(null);
  };

  const onPaneClick = () => {
    setSelectedNode(null);
    setSelectedEdge(null);  // Clear selected edge when clicking pane
    setContextMenu(null);
  };

  // Context menu handlers
  const handleContextMenu = (event, node = null) => {
    event.preventDefault();
    
    const rect = event.currentTarget.getBoundingClientRect();
    setContextMenu({
      x: event.clientX - rect.left,
      y: event.clientY - rect.top,
      node: node,
      visible: true
    });
  };

  const duplicateNode = (node) => {
    if (!node) return;
    
    saveStateToUndoStack();
    
    const newNode = {
      ...node,
      id: `${node.id}-copy-${Date.now()}`,
      position: {
        x: node.position.x + 50,
        y: node.position.y + 50
      }
    };
    
    setNodes((nds) => [...nds, newNode]);
    setContextMenu(null);
  };

  const deleteNode = (node) => {
    if (!node) return;
    
    saveStateToUndoStack();
    
    setNodes((nds) => nds.filter((n) => n.id !== node.id));
    setEdges((eds) => eds.filter((e) => e.source !== node.id && e.target !== node.id));
    setSelectedNode(null);
    setContextMenu(null);
  };

  const onDrop = useCallback(
    async (event) => {
      event.preventDefault();

      const reactFlowBounds = event.currentTarget.getBoundingClientRect();
      const type = event.dataTransfer.getData('application/reactflow');

      if (typeof type === 'undefined' || !type) {
        return;
      }

      const position = {
        x: event.clientX - reactFlowBounds.left,
        y: event.clientY - reactFlowBounds.top,
      };

      const nodeData = JSON.parse(type);
      const newNode = {
        id: `${nodeData.type.toLowerCase()}-${Date.now()}`,
        type: 'custom',
        position,
        data: {
          ...nodeData,
          label: nodeData.label,
        },
      };

      // Create a diagram automatically if none exists
      let diagramToUse = currentDiagram;
      if (!currentDiagram) {
        console.log('🆕 Creating new diagram automatically for dropped node');
        try {
          const newDiagram = await createDiagram({
            id: `diagram-${Date.now()}`,
            title: 'New Security Model',
            description: 'Security architecture diagram'
          });
          setCurrentDiagram(newDiagram);
          diagramToUse = newDiagram;
          console.log('✅ Auto-created diagram:', newDiagram.id);
        } catch (error) {
          console.error('❌ Error creating auto-diagram:', error);
        }
      }

      // Add the node to React state first
      setNodes((nds) => nds.concat(newNode));

      // Save the node to the database if we have a diagram
      try {
        if (diagramToUse) {
          console.log('💾 Saving new node to database');
          
          // Format the node data to match backend SecurityNode model
          const backendNodeData = {
            id: newNode.id,
            type: newNode.data.type || "Asset", // Map to NodeType enum
            subtype: newNode.data.subtype,
            label: newNode.data.label,
            position: {
              x: parseFloat(newNode.position.x.toString()),
              y: parseFloat(newNode.position.y.toString())
            },
            data: {
              ...newNode.data,
              category: newNode.data.category,
              categoryTitle: newNode.data.categoryTitle,
              description: newNode.data.description,
              criticality: newNode.data.criticality,
              data_classification: newNode.data.data_classification
            },
            mitre_ids: newNode.data.mitre_ids || [],
            cve_ids: newNode.data.cve_ids || []
          };
          
          const updatedDiagram = {
            ...diagramToUse,
            nodes: [...(diagramToUse.nodes || []), backendNodeData],
            edges: diagramToUse.edges || []
          };
          
          await updateDiagram(diagramToUse.id, updatedDiagram);
          setCurrentDiagram(updatedDiagram);
          console.log('✅ Node saved to database');
        }
      } catch (error) {
        console.error('❌ Error saving node to database:', error);
      }

      // Check if this node type supports intelligent expansion
      try {
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/intelligent-nodes/supported-types`);
        if (response.ok) {
          const data = await response.json();
          const supportedType = data.supported_types.find(
            type => type.node_subtype === nodeData.subtype
          );

          if (supportedType) {
            // This node supports intelligent expansion - start legacy questionnaire
            setCurrentQuestionnaireNode({
              id: newNode.id,
              subtype: nodeData.subtype,
              data: { 
                subtype: nodeData.subtype,
                parentNode: nodeData.parentNode
              }
            });
            setShowSecurityQuestionnaire(true);
          }
        }
      } catch (error) {
        console.error('Error checking intelligent node support:', error);
        // Continue without intelligent features if API fails
      }
    },
    [setNodes, currentDiagram],
  );

  const onDragOver = useCallback((event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  // Helper function to start legacy questionnaire
  const startLegacyQuestionnaire = useCallback(async (nodeId, nodeSubtype, parentNodeId = null, existingAnswers = {}) => {
    console.log('🎬 Starting legacy questionnaire:', { nodeId, nodeSubtype, parentNodeId, existingAnswers });
    
    // Use legacy questionnaire system only
    console.log('🎯 Using legacy questionnaire system');
    
    // Find the actual node to get complete data
    const actualNode = nodes.find(n => n.id === nodeId);
    setCurrentQuestionnaireNode({
      id: nodeId,
      subtype: nodeSubtype,
      data: { 
        subtype: nodeSubtype,
        parentNode: actualNode?.data?.parentNode || parentNodeId
      }
    });
    
    // Store existing answers for the questionnaire
    setCurrentQuestionnaireAnswers(existingAnswers);
    setShowSecurityQuestionnaire(true);
  }, []);

  const handleSaveDiagram = async () => {
    setIsLoading(true);
    try {
      const diagramData = {
        title: currentDiagram?.title || 'Untitled Diagram',
        description: currentDiagram?.description || '',
        nodes: nodes.map(node => ({
          id: node.id,
          type: node.data.type,
          subtype: node.data.subtype,
          label: node.data.label,
          position: node.position,
          data: node.data,
          mitre_ids: node.data.mitre_ids || [],
          cve_ids: node.data.cve_ids || []
        })),
        edges: edges.map(edge => ({
          id: edge.id,
          source: edge.source,
          target: edge.target,
          type: edge.type || 'default',
          label: edge.label || '',
          data: edge.data || {}
        }))
      };

      if (currentDiagram) {
        await updateDiagram(currentDiagram.id, { id: currentDiagram.id, ...diagramData });
      } else {
        const newDiagram = await createDiagram({
          title: 'New Security Model',
          description: 'Security architecture diagram'
        });
        setCurrentDiagram(newDiagram);
        await updateDiagram(newDiagram.id, { id: newDiagram.id, ...diagramData });
      }
      
      // QW-3: Update save status tracking
      setLastSavedAt(new Date());
      setHasUnsavedChanges(false);
      
      await loadDiagrams();
    } catch (error) {
      console.error('Failed to save diagram:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLoadDiagram = async (diagram) => {
    try {
      setCurrentDiagram(diagram);
      
      const loadedNodes = diagram.nodes.map(node => ({
        id: node.id,
        type: 'custom',
        position: node.position || { x: 0, y: 0 },
        data: {
          ...node.data,
          subtype: node.subtype,
          label: node.label,
          type: node.type || node.subtype,
          mitre_ids: node.mitre_ids || [],
          cve_ids: node.cve_ids || [],
        },
        subtype: node.subtype,
        mitre_ids: node.mitre_ids || [],
        cve_ids: node.cve_ids || []
      }));

      // Initialize control point data for template edges that don't have it
      const loadedEdges = diagram.edges.map(edge => ({
        id: edge.id,
        source: edge.source,
        target: edge.target,
        type: edge.type === 'default' ? 'draggable' : (edge.type || 'draggable'), // Convert default to draggable
        label: edge.label || '',
        style: edge.style || {},
        markerEnd: edge.markerEnd || {},
        labelStyle: edge.labelStyle || {},
        labelBgStyle: edge.labelBgStyle || {},
        labelShowBg: edge.labelShowBg !== false, // Default to true
        labelBgBorderRadius: edge.labelBgBorderRadius || 4,
        labelBgPadding: edge.labelBgPadding || [4, 8],
        data: {
          // Initialize control point data if missing
          controlPoint1: { x: 0, y: 0 },
          controlPoint2: { x: 0, y: 0 },
          labelPosition: 0.5,
          // Preserve any existing data
          ...edge.data
        }
      }));

      setNodes(loadedNodes);
      setEdges(loadedEdges);
      setSimulationResult(null);
      
      console.log(`✅ Loaded diagram with ${loadedNodes.length} nodes and ${loadedEdges.length} edges`);
      console.log('🔧 Initialized control points for', loadedEdges.length, 'edges');
    } catch (error) {
      console.error('Failed to load diagram:', error);
    }
  };

  const handleRunSimulation = async () => {
    if (!currentDiagram) {
      // Save first if no current diagram
      await handleSaveDiagram();
      return;
    }

    setIsLoading(true);
    try {
      const result = await simulateAttackPaths(currentDiagram.id);
      setSimulationResult(result);
      setViewMode('analysis');
      
      // Highlight attack paths on the canvas
      if (result.attack_paths && result.attack_paths.length > 0) {
        highlightAttackPaths(result.attack_paths);
      }
    } catch (error) {
      console.error('Failed to run simulation:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const highlightAttackPaths = (attackPaths) => {
    if (!attackPaths || attackPaths.length === 0) {
      setHighlightedPaths([]);
      return;
    }

    // Update edges to highlight attack paths
    setEdges((eds) =>
      eds.map((edge) => {
        // Check if this edge is part of any attack path
        const isInAttackPath = attackPaths.some(path => 
          path.steps?.some(step => 
            step.source_node === edge.source && step.target_node === edge.target
          )
        );

        if (isInAttackPath) {
          return {
            ...edge,
            style: {
              ...edge.style,
              stroke: '#ef4444', // Red color for attack paths
              strokeWidth: 3,
              strokeDasharray: '5,5',
            },
            animated: true,
            markerEnd: {
              type: MarkerType.ArrowClosed,
              width: 20,
              height: 20,
              color: '#ef4444',
            },
            data: {
              ...edge.data,
              isHighlighted: true
            }
          };
        }

        return {
          ...edge,
          style: {
            ...edge.style,
            stroke: edge.data?.isHighlighted ? '#6b7280' : (edge.style?.stroke || '#6b7280'),
            strokeWidth: edge.data?.isHighlighted ? 1 : (edge.style?.strokeWidth || 1),
            strokeDasharray: edge.data?.isHighlighted ? 'none' : (edge.style?.strokeDasharray || 'none'),
          },
          animated: false,
          data: {
            ...edge.data,
            isHighlighted: false
          }
        };
      })
    );

    // Update nodes to highlight those involved in attack paths
    setNodes((nds) =>
      nds.map((node) => {
        const isInAttackPath = attackPaths.some(path =>
          path.steps?.some(step =>
            step.source_node === node.id || step.target_node === node.id
          )
        );

        if (isInAttackPath) {
          return {
            ...node,
            style: {
              ...node.style,
              border: '2px solid #ef4444',
              boxShadow: '0 0 10px rgba(239, 68, 68, 0.5)',
            },
            data: {
              ...node.data,
              isHighlighted: true
            }
          };
        }

        return {
          ...node,
          style: {
            ...node.style,
            border: node.data?.isHighlighted ? 'none' : (node.style?.border || 'none'),
            boxShadow: node.data?.isHighlighted ? 'none' : (node.style?.boxShadow || 'none'),
          },
          data: {
            ...node.data,
            isHighlighted: false
          }
        };
      })
    );

    setHighlightedPaths(attackPaths);
  };

  const clearAttackPathHighlighting = () => {
    // Reset all edge styles
    setEdges((eds) =>
      eds.map((edge) => ({
        ...edge,
        style: {
          ...edge.style,
          stroke: '#6b7280',
          strokeWidth: 1,
          strokeDasharray: 'none',
        },
        animated: false,
        markerEnd: {
          type: MarkerType.ArrowClosed,
          width: 20,
          height: 20,
          color: '#6b7280',
        },
        data: {
          ...edge.data,
          isHighlighted: false
        }
      }))
    );

    // Reset all node styles
    setNodes((nds) =>
      nds.map((node) => ({
        ...node,
        style: {
          ...node.style,
          border: 'none',
          boxShadow: 'none',
        },
        data: {
          ...node.data,
          isHighlighted: false
        }
      }))
    );

    setHighlightedPaths([]);
  };
  
  // QW-3: Clear All with confirmation
  const handleClearAllConfirm = () => {
    setShowClearAllConfirm(true);
  };
  
  const executeClearAll = () => {
    setNodes([]);
    setEdges([]);
    setSelectedNode(null);
    setSimulationResult(null);
    setHighlightedPaths([]);
    setUndoStack([]);
    setRedoStack([]);
    clearAttackPathHighlighting();
    setHasUnsavedChanges(false); // Reset unsaved changes after clearing
    setShowClearAllConfirm(false);
  };
  
  const cancelClearAll = () => {
    setShowClearAllConfirm(false);
  };

  // Enhanced function to determine edge label and styling based on connection type
  const getConnectionInfo = (sourceNode, targetNode, questionnaire_answers = {}) => {
    const sourceType = sourceNode?.data?.subtype || sourceNode?.type;
    const targetType = targetNode?.data?.subtype || targetNode?.type;
    
    // API connections (WebApp to API, API to API)
    if ((sourceType === 'WebApp' && targetType === 'API') || 
        (sourceType === 'API' && targetType === 'API')) {
      const apiType = questionnaire_answers?.api_type || 'REST';
      const protocol = questionnaire_answers?.api_protocol || 'HTTPS';
      return {
        label: `${protocol} ${apiType}`,
        style: { stroke: '#3B82F6', strokeWidth: 2 },
        markerEnd: { type: 'arrowclosed', color: '#3B82F6' },
        labelStyle: { fill: '#3B82F6', fontWeight: 'bold', fontSize: '12px' },
        labelBgStyle: { fill: '#1E3A8A', fillOpacity: 0.8 }
      };
    }
    
    // Database connections
    if ((sourceType === 'WebApp' || sourceType === 'API') && targetType === 'Database') {
      const dbType = questionnaire_answers?.database_type || 'SQL';
      return {
        label: `${dbType} DB`,
        style: { stroke: '#8B5CF6', strokeWidth: 2 },
        markerEnd: { type: 'arrowclosed', color: '#8B5CF6' },
        labelStyle: { fill: '#8B5CF6', fontWeight: 'bold', fontSize: '12px' },
        labelBgStyle: { fill: '#581C87', fillOpacity: 0.8 }
      };
    }
    
    // Storage connections (to S3Bucket, file systems, etc.)
    if ((sourceType === 'WebApp' || sourceType === 'API') && 
        (targetType === 'S3Bucket' || targetType === 'FileSystem')) {
      return {
        label: 'File I/O',
        style: { stroke: '#10B981', strokeWidth: 2, strokeDasharray: '4,2' },
        markerEnd: { type: 'arrowclosed', color: '#10B981' },
        labelStyle: { fill: '#10B981', fontWeight: 'bold', fontSize: '12px' },
        labelBgStyle: { fill: '#047857', fillOpacity: 0.8 }
      };
    }
    
    // Message Queue connections
    if ((sourceType === 'WebApp' || sourceType === 'API') && 
        (targetType === 'MessageQueue' || targetType === 'ServiceBus')) {
      return {
        label: 'Message',
        style: { stroke: '#F59E0B', strokeWidth: 2, strokeDasharray: '6,3' },
        markerEnd: { type: 'arrowclosed', color: '#F59E0B' },
        labelStyle: { fill: '#F59E0B', fontWeight: 'bold', fontSize: '12px' },
        labelBgStyle: { fill: '#92400E', fillOpacity: 0.8 }
      };
    }
    
    // Network zone transitions (crossing trust boundaries)
    if (sourceType === 'Internet' || targetType === 'Internet') {
      return {
        label: 'Public Network',
        style: { stroke: '#EF4444', strokeWidth: 3, strokeDasharray: '8,4' },
        markerEnd: { type: 'arrowclosed', color: '#EF4444' },
        labelStyle: { fill: '#EF4444', fontWeight: 'bold', fontSize: '12px' },
        labelBgStyle: { fill: '#7F1D1D', fillOpacity: 0.8 }
      };
    }
    
    if ((sourceType === 'DMZ' && targetType === 'Internal') || 
        (sourceType === 'Internal' && targetType === 'DMZ')) {
      return {
        label: 'Network Transit',
        style: { stroke: '#F97316', strokeWidth: 2, strokeDasharray: '5,3' },
        markerEnd: { type: 'arrowclosed', color: '#F97316' },
        labelStyle: { fill: '#F97316', fontWeight: 'bold', fontSize: '12px' },
        labelBgStyle: { fill: '#9A3412', fillOpacity: 0.8 }
      };
    }
    
    // Cloud service connections
    if (targetType === 'AWSService' || targetType === 'GCPService' || targetType === 'AzureService') {
      return {
        label: 'Cloud API',
        style: { stroke: '#06B6D4', strokeWidth: 2, strokeDasharray: '3,3' },
        markerEnd: { type: 'arrowclosed', color: '#06B6D4' },
        labelStyle: { fill: '#06B6D4', fontWeight: 'bold', fontSize: '12px' },
        labelBgStyle: { fill: '#0E7490', fillOpacity: 0.8 }
      };
    }
    
    // Authentication flows
    if ((sourceType === 'WebApp' || sourceType === 'API') && 
        (targetType === 'ActiveDirectory' || targetType === 'OAuth' || targetType === 'SAML')) {
      return {
        label: 'Auth Flow',
        style: { stroke: '#8B5CF6', strokeWidth: 2, strokeDasharray: '4,4' },
        markerEnd: { type: 'arrowclosed', color: '#8B5CF6' },
        labelStyle: { fill: '#8B5CF6', fontWeight: 'bold', fontSize: '12px' },
        labelBgStyle: { fill: '#581C87', fillOpacity: 0.8 }
      };
    }
    
    // Load balancer connections
    if (sourceType === 'LoadBalancer' || targetType === 'LoadBalancer') {
      return {
        label: 'Load Balance',
        style: { stroke: '#14B8A6', strokeWidth: 2 },
        markerEnd: { type: 'arrowclosed', color: '#14B8A6' },
        labelStyle: { fill: '#14B8A6', fontWeight: 'bold', fontSize: '12px' },
        labelBgStyle: { fill: '#0F766E', fillOpacity: 0.8 }
      };
    }
    
    // Attack surface connections (vulnerabilities)
    if (targetType === 'SSRF' || targetType === 'SQLi' || targetType === 'RCE' || 
        targetType === 'IDOR' || targetType === 'WeakIAM' || targetType === 'Deserialization') {
      return {
        label: 'Exploits',
        style: { stroke: '#DC2626', strokeWidth: 3, strokeDasharray: '7,3' },
        markerEnd: { type: 'arrowclosed', color: '#DC2626' },
        labelStyle: { fill: '#DC2626', fontWeight: 'bold', fontSize: '12px' },
        labelBgStyle: { fill: '#7F1D1D', fillOpacity: 0.8 }
      };
    }
    
    // Security control connections (protective)
    if (sourceType === 'WAF' || sourceType === 'EDR' || sourceType === 'SIEM' || 
        sourceType === 'EgressProxy' || sourceType === 'IAMPolicy' || sourceType === 'NetworkACL') {
      return {
        label: 'Protects',
        style: { stroke: '#059669', strokeWidth: 2, strokeDasharray: '6,2' },
        markerEnd: { type: 'arrowclosed', color: '#059669' },
        labelStyle: { fill: '#059669', fontWeight: 'bold', fontSize: '12px' },
        labelBgStyle: { fill: '#064E3B', fillOpacity: 0.8 }
      };
    }
    
    // Actor attack paths
    if (sourceType === 'ExternalAttacker' || sourceType === 'Insider' || 
        sourceType === 'ServiceAccount' || sourceType === 'NationState') {
      return {
        label: 'Attack Vector',
        style: { stroke: '#EF4444', strokeWidth: 3, strokeDasharray: '7,3' },
        markerEnd: { type: 'arrowclosed', color: '#EF4444' },
        labelStyle: { fill: '#EF4444', fontWeight: 'bold', fontSize: '12px' },
        labelBgStyle: { fill: '#7F1D1D', fillOpacity: 0.8 }
      };
    }
    
    // VM/Container connections
    if ((sourceType === 'VM' || sourceType === 'Container') && 
        (targetType === 'WebApp' || targetType === 'API' || targetType === 'Database')) {
      return {
        label: 'Hosts',
        style: { stroke: '#7C3AED', strokeWidth: 2, strokeDasharray: '5,2' },
        markerEnd: { type: 'arrowclosed', color: '#7C3AED' },
        labelStyle: { fill: '#7C3AED', fontWeight: 'bold', fontSize: '12px' },
        labelBgStyle: { fill: '#4C1D95', fillOpacity: 0.8 }
      };
    }
    
    // Default connection with improved styling
    return {
      label: 'Data Flow',
      style: { stroke: '#9CA3AF', strokeWidth: 2 },
      markerEnd: { type: 'arrowclosed', color: '#9CA3AF' },
      labelStyle: { fill: '#9CA3AF', fontWeight: 'bold', fontSize: '12px' },
      labelBgStyle: { fill: '#374151', fillOpacity: 0.8 }
    };
  };

  const handleAutoLayout = async () => {
    if (!currentDiagram) {
      // If no diagram, perform local layout
      performLocalAutoLayout();
      return;
    }
    
    setIsLoading(true);
    try {
      const layoutData = await autoLayoutDiagram(currentDiagram.id);
      
      // Apply the new positions with enhanced bounds checking
      setNodes((nds) => {
        const updatedNodes = nds.map((node) => {
          const layoutPosition = layoutData.layout_positions[node.id];
          if (layoutPosition) {
            // Dynamic canvas bounds based on viewport
            const canvasWidth = window.innerWidth - 300; // Account for sidebars
            const canvasHeight = window.innerHeight - 200; // Account for header/footer
            
            // Ensure nodes stay within dynamic canvas bounds with padding
            const padding = 100;
            const x = Math.max(padding, Math.min(layoutPosition.x, canvasWidth - padding));
            const y = Math.max(padding, Math.min(layoutPosition.y, canvasHeight - padding));
            
            return {
              ...node,
              position: { x, y },
            };
          }
          return node;
        });
        
        return updatedNodes;
      });
      
      // Fit view to show all nodes with padding
      setTimeout(() => {
        fitView({ 
          padding: 0.15,
          includeHiddenNodes: false,
          minZoom: 0.3,
          maxZoom: 1.5,
          duration: 800
        });
      }, 100);
    } catch (error) {
      console.error('Failed to auto-layout diagram:', error);
      performLocalAutoLayout();
    } finally {
      setIsLoading(false);
    }
  };

  // Enhanced local auto-layout function
  const performLocalAutoLayout = () => {
    if (nodes.length === 0) return;
    
    setIsLoading(true);
    
    // Get canvas dimensions
    const canvasWidth = window.innerWidth - 300;
    const canvasHeight = window.innerHeight - 200;
    
    // Intelligent grid-based layout with categorization
    const nodesByType = nodes.reduce((acc, node) => {
      const type = node.data?.type || 'default';
      if (!acc[type]) acc[type] = [];
      acc[type].push(node);
      return acc;
    }, {});
    
    const typePositions = {
      'Actor': { x: 50, y: 50 },      // Top-left for threat actors
      'Asset': { x: canvasWidth * 0.4, y: canvasHeight * 0.3 }, // Center for assets
      'Surface': { x: canvasWidth * 0.7, y: canvasHeight * 0.2 }, // Right for attack surfaces
      'Control': { x: canvasWidth * 0.2, y: canvasHeight * 0.7 }, // Bottom-left for controls
      'Zone': { x: canvasWidth * 0.8, y: canvasHeight * 0.8 }, // Bottom-right for zones
      'default': { x: canvasWidth * 0.5, y: canvasHeight * 0.5 }
    };
    
    const spacing = {
      x: Math.min(250, canvasWidth / 6),
      y: Math.min(200, canvasHeight / 6)
    };
    
    setNodes((nds) => {
      const updatedNodes = nds.map((node) => {
        const nodeType = node.data?.type || 'default';
        const typeNodes = nodesByType[nodeType];
        const nodeIndex = typeNodes.findIndex(n => n.id === node.id);
        
        // Calculate position within type group
        const basePos = typePositions[nodeType] || typePositions.default;
        const nodesPerRow = Math.ceil(Math.sqrt(typeNodes.length));
        const row = Math.floor(nodeIndex / nodesPerRow);
        const col = nodeIndex % nodesPerRow;
        
        const x = basePos.x + (col * spacing.x);
        const y = basePos.y + (row * spacing.y);
        
        // Ensure nodes stay within bounds
        const boundedX = Math.max(50, Math.min(x, canvasWidth - 50));
        const boundedY = Math.max(50, Math.min(y, canvasHeight - 50));
        
        return {
          ...node,
          position: { x: boundedX, y: boundedY },
        };
      });
      
      return updatedNodes;
    });
    
    // Auto-fit view after layout
    setTimeout(() => {
      fitView({ 
        padding: 0.1,
        includeHiddenNodes: false,
        minZoom: 0.3,
        maxZoom: 1.5,
        duration: 800
      });
      setIsLoading(false);
    }, 100);
  };

  const handleExportDiagram = () => {
    if (!currentDiagram) return;
    
    const exportData = {
      diagram: currentDiagram,
      nodes: nodes,
      edges: edges,
      simulation: simulationResult,
      exportedAt: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: 'application/json'
    });
    
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${currentDiagram.title || 'diagram'}-export.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleImportDiagram = (event) => {
    const file = event.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const importData = JSON.parse(e.target.result);
        
        if (importData.diagram && importData.nodes && importData.edges) {
          setCurrentDiagram(importData.diagram);
          setNodes(importData.nodes);
          setEdges(importData.edges);
          if (importData.simulation) {
            setSimulationResult(importData.simulation);
          }
        } else {
          notification.showError('Invalid File Format', 'Invalid diagram file format');
        }
      } catch (error) {
        console.error('Failed to import diagram:', error);
        notification.showError('Import Failed', 'Failed to import diagram');
      }
    };
    reader.readAsText(file);
  };

  const handleNewDiagram = () => {
    setNodes([]);
    setEdges([]);
    setCurrentDiagram(null);
    setSimulationResult(null);
    setSelectedNode(null);
    setHighlightedPaths([]);
    setViewMode('modeling');
    clearAttackPathHighlighting();
  };

  const handleApplyTemplate = async (template) => {
    try {
      setIsLoading(true);
      
      // Ensure we have a current diagram to apply template to
      let diagramId = currentDiagram?.id;
      
      if (!diagramId) {
        // Create a new diagram if none exists
        const newDiagram = await createDiagram({
          title: `${template.name} - Applied Template`,
          description: `Created from template: ${template.description}`
        });
        diagramId = newDiagram.id;
        setCurrentDiagram(newDiagram);
      }
      
      // Apply template to diagram
      const result = await applyTemplateToCurrentDiagram(template.id, diagramId);
      
      // Reload the updated diagram
      const updatedDiagram = await updateDiagram(diagramId, {
        title: currentDiagram?.title || `${template.name} - Applied Template`,
        description: currentDiagram?.description || template.description
      });
      
      // Update the canvas with new nodes and edges
      const templateNodes = template.nodes.map(node => ({
        id: `template-${node.id}-${Date.now()}`,
        type: 'custom',
        position: node.position || { x: Math.random() * 500, y: Math.random() * 500 },
        data: {
          ...node,
          label: node.label
        }
      }));
      
      const templateEdges = template.edges.map(edge => ({
        id: `template-edge-${edge.id}-${Date.now()}`,
        source: `template-${edge.source}-${Date.now()}`,
        target: `template-${edge.target}-${Date.now()}`,
        type: 'draggable',  // Use draggable type for all template edges
        label: edge.label || '',
        style: edge.style || {
          strokeWidth: 2,
          stroke: '#9CA3AF',
        },
        markerEnd: edge.markerEnd || {
          type: 'arrowclosed',
          color: '#9CA3AF',
        },
        labelStyle: edge.labelStyle || {},
        labelBgStyle: edge.labelBgStyle || {},
        labelShowBg: edge.labelShowBg !== false, // Default to true
        labelBgBorderRadius: edge.labelBgBorderRadius || 4,
        labelBgPadding: edge.labelBgPadding || [4, 8],
        data: {
          // Initialize control point data for draggable functionality
          controlPoint1: { x: 0, y: 0 },
          controlPoint2: { x: 0, y: 0 },
          labelPosition: 0.5,
          // Preserve any existing data from template
          ...edge.data
        }
      }));
      
      // Add template nodes and edges to existing ones
      setNodes(prevNodes => [...prevNodes, ...templateNodes]);
      setEdges(prevEdges => [...prevEdges, ...templateEdges]);
      
      // Save state for undo functionality
      saveStateToUndoStack();
      
      notification.showInfo('Template Applied', `Template "${template.name}" applied successfully! Added ${result.nodes_added} nodes and ${result.edges_added} edges.`);
      
    } catch (error) {
      console.error('Error applying template:', error);
      notification.showError('Template Failed', 'Failed to apply template. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Questionnaire Completeness Check
  const checkQuestionnaireCompleteness = async (nodeId, nodeSubtype) => {
    try {
      if (nodeSubtype === 'WebApp') {
        // For comprehensive WebApp questionnaire, check against the full set
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/questionnaires/WebApp?level=basic`);
        if (response.ok) {
          const data = await response.json();
          const totalQuestions = data.total_questions;
          
          // Get current node answers
          const node = nodes.find(n => n.id === nodeId);
          const currentAnswers = node?.data?.questionnaireResponses || {};
          const answeredCount = Object.keys(currentAnswers).filter(key => currentAnswers[key] !== null && currentAnswers[key] !== undefined).length;
          
          console.log(`🎯 WebApp questionnaire completeness: ${answeredCount}/${totalQuestions} questions answered`);
          return answeredCount >= totalQuestions;
        }
      } else {
        // For other node types, use existing intelligent-nodes system
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/intelligent-nodes/${nodeSubtype}/prompts`);
        if (response.ok) {
          const data = await response.json();
          const totalQuestions = data.prompts?.length || 0;
          
          // Get current node answers
          const node = nodes.find(n => n.id === nodeId);
          const currentAnswers = node?.data?.questionnaireResponses || {};
          const answeredCount = Object.keys(currentAnswers).filter(key => currentAnswers[key] !== null && currentAnswers[key] !== undefined).length;
          
          console.log(`🎯 ${nodeSubtype} questionnaire completeness: ${answeredCount}/${totalQuestions} questions answered`);
          return answeredCount >= totalQuestions;
        }
      }
      
      return false; // Default to incomplete if unable to check
    } catch (error) {
      console.error('Error checking questionnaire completeness:', error);
      return false;
    }
  };

  // Security Questionnaire Handlers
  const handleSecurityQuestionnaireComplete = async (result) => {
    try {
      if (!currentQuestionnaireNode) return;

      // Save questionnaire responses to the diagram
      await saveQuestionnaireResponses(currentQuestionnaireNode.id, result.answers);

      // Create security branches for the node
      const branchResponse = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/intelligent-nodes/${currentQuestionnaireNode.subtype}/create-branches`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );

      if (branchResponse.ok) {
        const branchData = await branchResponse.json();
        
        // Update branches with user answers
        const updatedBranches = branchData.branches.map(branch => {
          const answer = result.answers[branch.id] || result.answers[Object.keys(result.answers).find(key => key.includes(branch.type.toLowerCase()))];
          return {
            ...branch,
            completed: answer !== undefined && answer !== null,
            value: answer
          };
        });

        // Store branches for this node
        setNodeBranches(prev => ({
          ...prev,
          [currentQuestionnaireNode.id]: updatedBranches
        }));

        // Modern React Flow v12 pattern: Update node data efficiently
        const nodeUpdateData = {
          securityBranches: updatedBranches,
          completionStatus: result.validation,
          recommendations: result.recommendations,
          intelligentNode: true,
          questionnaireResponses: result.answers,
          lastQuestionnaireUpdate: new Date().toISOString()
        };
        
        // Use React Flow v12's updateNodeData for better performance
        updateNodeDataEfficiently(currentQuestionnaireNode.id, nodeUpdateData);
        
        // Fallback: Also update via setNodes for compatibility
        setNodes(nds => nds.map(node => {
          if (node.id === currentQuestionnaireNode.id) {
            return {
              ...node,
              data: {
                ...node.data,
                ...nodeUpdateData
              }
            };
          }
          return node;
        }));

        // Mark dependency as COMPLETED if this node is a dependency of another node
        const completedNode = currentQuestionnaireNode;
        const dependencyType = completedNode.subtype || completedNode.data?.subtype;
        
        // Find the actual React Flow node to get the complete data including parentNode
        const actualNode = nodes.find(n => n.id === completedNode.id);
        let parentNodeId = actualNode?.data?.parentNode;
        
        // If parentNodeId is not found, check if this is a dependent questionnaire scenario
        if (!parentNodeId && questionnaireQueue.length > 0) {
          // This might be a dependent questionnaire - try to find parent from queue context
          const parentFromQueue = nodes.find(n => 
            questionnaireQueue.some(qn => qn.data?.parentNode === n.id)
          );
          if (parentFromQueue) {
            parentNodeId = parentFromQueue.id;
          }
        }
        
        if (parentNodeId && dependencyType) {
          console.log(`✅ Marking dependency as COMPLETED: ${parentNodeId} → ${dependencyType}`);
          setDependencyState(parentNodeId, dependencyType, 'COMPLETED');
          
          // Remove from active questionnaires
          setActiveQuestionnaires(prev => {
            const newSet = new Set(prev);
            newSet.delete(completedNode.id);
            return newSet;
          });
        } else {
          console.log(`⚠️ Could not mark dependency as completed - missing parentNodeId: ${parentNodeId} or dependencyType: ${dependencyType}`);
          console.log('🔍 Current node data:', completedNode);
          console.log('🔍 Questionnaire queue:', questionnaireQueue);
        }

        // Handle dependent node questionnaires
        console.log('🔍 Checking for dependent questionnaires:', {
          nodeSubtype: currentQuestionnaireNode.subtype,
          triggerDependentQuestionnaires: result.triggerDependentQuestionnaires,
          dependentNodesLength: result.dependentNodes?.length,
          dependentNodes: result.dependentNodes,
          resultAnswers: result.answers
        });
        
        if (result.triggerDependentQuestionnaires && result.dependentNodes?.length > 0) {
          // Filter out dependencies that are already COMPLETED
          const incompleteDependencies = getIncompleteDependencies(currentQuestionnaireNode.id, result.dependentNodes);
          
          if (incompleteDependencies.length > 0) {
            console.log('🚀 Triggering dependent node creation for incomplete dependencies:', incompleteDependencies);
            await handleDependentNodeCreation(incompleteDependencies, result.answers);
          } else {
            console.log('✅ All dependencies already completed, skipping dependent node creation');
          }
        }

        // Show completion status with smart node creation info
        let statusMessage = `Security configuration completed!\n\nCompletion: ${result.validation?.completion_percentage || 0}%\nRecommendations: ${result.recommendations?.length || 0}`;
        
        if (result.smartNodeResult) {
          statusMessage += `\n\nSmart Links Created:\n• ${result.smartNodeResult.nodesCreated} new nodes\n• ${result.smartNodeResult.edgesCreated} connections`;
        }

        if (result.dependentNodes?.length > 0) {
          statusMessage += `\n\nDependent Nodes:\n• ${result.dependentNodes.length} nodes will be configured`;
        }

        // Check if questionnaire is complete before triggering vulnerability analysis
        const isQuestionnaireComplete = await checkQuestionnaireCompleteness(currentQuestionnaireNode.id, currentQuestionnaireNode.subtype);
        
        // Only trigger vulnerability analysis if enabled AND questionnaire is complete
        if (autoVulnerabilityAnalysis && ['WebApp', 'API', 'Database', 'Backup', 'Monitoring'].includes(currentQuestionnaireNode.subtype)) {
          if (isQuestionnaireComplete) {
            console.log('🔍 Auto-triggering vulnerability analysis for COMPLETE questionnaire');
            
            const nodePosition = nodes.find(n => n.id === currentQuestionnaireNode.id)?.position;
            const analysisResult = await analyzeNodeVulnerabilitiesHandler(
              currentQuestionnaireNode.id,
              currentQuestionnaireNode.subtype,
              result.answers,
              nodePosition
            );
            
            if (analysisResult && analysisResult.total_vulnerabilities > 0) {
              statusMessage += `\n\n🚨 Security Analysis:\n• ${analysisResult.total_vulnerabilities} vulnerabilities identified\n• Overall risk score: ${analysisResult.overall_risk_score.toFixed(1)}/10`;
            }
          } else {
            console.log('⚠️ Questionnaire incomplete - skipping auto-vulnerability analysis');
            statusMessage += `\n\n⚠️ Security Analysis:\n• Questionnaire incomplete - please answer all questions before vulnerability analysis\n• Use "Vulnerabilities" button after completing all security questions`;
          }
        } else if (!autoVulnerabilityAnalysis) {
          statusMessage += `\n\n💡 Tip: Use "Vulnerabilities" button to analyze security risks after completing all questions`;
        }
        
        // Parse vulnerability analysis results
        let vulnerabilityData = null;
        if (result.vulnerabilityAnalysis && result.vulnerabilityAnalysis.total_vulnerabilities > 0) {
          vulnerabilityData = {
            total: result.vulnerabilityAnalysis.total_vulnerabilities,
            riskScore: result.vulnerabilityAnalysis.overall_risk_score.toFixed(1)
          };
        }

        // Show enhanced notification instead of alert
        notification.showSecurityConfigurationComplete({
          completion: result.validation?.completion_percentage || 0,
          recommendations: result.recommendations?.length || 0,
          dependentNodes: result.dependentNodes?.length || 0,
          vulnerabilities: vulnerabilityData,
          smartNodeResult: result.smartNodeResult,
          autoVulnerabilityAnalysis: autoVulnerabilityAnalysis
        });
      }

    } catch (error) {
      console.error('Error completing security questionnaire:', error);
    } finally {
      // Handle dependent questionnaires first
      if (result?.triggerDependentQuestionnaires && result?.dependentNodes?.length > 0) {
        console.log('🔄 Dependent questionnaires triggered, storing parent state for resumption');
        
        // Store parent questionnaire state in stack for resumption after dependencies complete
        if (result.partialCompletion) {
          // Check if this questionnaire is already at the top of the stack to prevent duplicates
          const isAlreadyOnTop = parentQuestionnaireStack.length > 0 && 
            parentQuestionnaireStack[parentQuestionnaireStack.length - 1]?.nodeId === currentQuestionnaireNode.id;
          
          if (!isAlreadyOnTop) {
            // Push current questionnaire to the parent stack
            const parentState = {
              nodeId: currentQuestionnaireNode.id,
              nodeSubtype: currentQuestionnaireNode.subtype,
              resumeFromPromptIndex: result.currentPromptIndex, // Resume from the current question index
              partialAnswers: result.answers
            };
            setParentQuestionnaireStack(prev => [...prev, parentState]);
            console.log(`🔄 Pushed parent questionnaire to stack at prompt ${result.currentPromptIndex}. Stack depth: ${parentQuestionnaireStack.length + 1}`);
          } else {
            // Update the existing entry with the latest state instead of pushing duplicate
            setParentQuestionnaireStack(prev => {
              const updated = [...prev];
              updated[updated.length - 1] = {
                nodeId: currentQuestionnaireNode.id,
                nodeSubtype: currentQuestionnaireNode.subtype,
                resumeFromPromptIndex: result.currentPromptIndex, // Resume from the current question index
                partialAnswers: result.answers
              };
              return updated;
            });
            console.log(`🔄 Updated existing parent questionnaire in stack at prompt ${result.currentPromptIndex}. Stack depth: ${parentQuestionnaireStack.length}`);
          }
        }
        return; // Don't close the questionnaire, let handleDependentNodeCreation manage it
      }

      // Check if this is a dependency questionnaire completion and we need to resume parent
      if (questionnaireQueue.length > currentQueueIndex + 1) {
        // Move to next questionnaire in queue (next dependency)
        setCurrentQueueIndex(prev => prev + 1);
        const nextNode = questionnaireQueue[currentQueueIndex + 1];
        setCurrentQuestionnaireNode(nextNode);
        console.log(`🔄 Moving to next dependency questionnaire: ${nextNode?.data?.subtype}`);
      } else if (questionnaireQueue.length > 0 && parentQuestionnaireStack.length > 0) {
        // All dependencies complete, resume parent questionnaire from stack
        const parentState = parentQuestionnaireStack[parentQuestionnaireStack.length - 1];
        console.log('🔄 All dependencies completed, resuming parent questionnaire from stack:', parentState);
        
        // Ensure parentState exists and has required properties
        if (parentState && parentState.nodeId && parentState.nodeSubtype) {
          // Find the actual parent node to get complete data
          const actualParentNode = nodes.find(n => n.id === parentState.nodeId);
          setCurrentQuestionnaireNode({
            id: parentState.nodeId,
            subtype: parentState.nodeSubtype,
            data: { 
              subtype: parentState.nodeSubtype,
              parentNode: actualParentNode?.data?.parentNode
            }
          });
        } else {
          console.error('⚠️ Invalid parent state found in stack:', parentState);
          // Fallback: close questionnaire if parent state is invalid
          setShowSecurityQuestionnaire(false);
          setCurrentQuestionnaireNode(null);
          setParentQuestionnaireStack([]);
          return;
        }
        
        // Clear the queue but keep parent stack for the SecurityQuestionnaire component
        setQuestionnaireQueue([]);
        setCurrentQueueIndex(0);
        
        // The SecurityQuestionnaire component will use the parent state from stack for resumption
        // Don't pop from stack here - it will be popped when parent completes
      } else {
        // No more dependencies in queue - check if this questionnaire completed and has parent to resume
        const isCompletingCurrentFromStack = parentQuestionnaireStack.length > 0 && 
          parentQuestionnaireStack[parentQuestionnaireStack.length - 1]?.nodeId === currentQuestionnaireNode.id && 
          !result?.partialCompletion && result?.isActualCompletion;
        
        if (isCompletingCurrentFromStack && parentQuestionnaireStack.length > 1) {
          // This questionnaire is completed and there's a parent to resume
          console.log('✅ Current questionnaire completed, popping from stack and resuming parent');
          
          // Pop the completed questionnaire from stack first
          setParentQuestionnaireStack(prev => {
            const newStack = prev.slice(0, -1);
            // Get the parent (now the last item after popping)
            const parentState = newStack[newStack.length - 1];
            console.log('🔄 Resuming parent questionnaire:', parentState);
            
            // Only resume if parentState exists and has required properties
            if (parentState && parentState.nodeId && parentState.nodeSubtype) {
              // Resume the parent questionnaire
              const actualParentNode = nodes.find(n => n.id === parentState.nodeId);
              setCurrentQuestionnaireNode({
                id: parentState.nodeId,
                subtype: parentState.nodeSubtype,
                data: { 
                  subtype: parentState.nodeSubtype,
                  parentNode: actualParentNode?.data?.parentNode
                }
              });
            } else {
              console.log('✅ No more parent questionnaires to resume - closing modal');
              // No valid parent state, close questionnaire
              setShowSecurityQuestionnaire(false);
              setCurrentQuestionnaireNode(null);
            }
            
            return newStack;
          });
          
          // Clear the queue
          setQuestionnaireQueue([]);
          setCurrentQueueIndex(0);
        } else if (isCompletingCurrentFromStack && parentQuestionnaireStack.length === 1) {
          // This is the last questionnaire in the stack - close everything
          console.log('✅ Last parent questionnaire completed, closing modal');
          setShowSecurityQuestionnaire(false);
          setCurrentQuestionnaireNode(null);
          setCurrentQuestionnaireAnswers({});
          setQuestionnaireQueue([]);
          setCurrentQueueIndex(0);
          setParentQuestionnaireStack([]);
        } else {
          // All questionnaires completed - close everything
          console.log('✅ All questionnaires completed, closing modal');
          setShowSecurityQuestionnaire(false);
          setCurrentQuestionnaireNode(null);
          setCurrentQuestionnaireAnswers({}); // Clear existing answers
          setQuestionnaireQueue([]);
          setCurrentQueueIndex(0);
          setParentQuestionnaireStack([]); // Clear the stack
        }
      }
    }
  };

  // =============================================================================
  // VULNERABILITY ANALYSIS FUNCTIONS
  // =============================================================================

  // =============================================================================
  // VULNERABILITY SYSTEM FUNCTIONS
  // =============================================================================

  // Get all vulnerabilities from analyses
  const getAllVulnerabilities = () => {
    const allVulns = [];
    Object.values(vulnerabilityAnalyses).forEach(analysis => {
      if (analysis.vulnerability_nodes) {
        analysis.vulnerability_nodes.forEach(vuln => {
          allVulns.push({
            ...vuln,
            parent_node_type: analysis.node_type || 'Unknown'
          });
        });
      }
    });
    return allVulns;
  };

  const allVulnerabilities = useMemo(() => getAllVulnerabilities(), [vulnerabilityAnalyses]);

  // Handle vulnerability filter changes
  const handleVulnerabilityFilterChange = useCallback((filtered, filters) => {
    setFilteredVulnerabilities(filtered);
    
    // Update node visibility based on filters
    setNodes(nds => nds.map(node => {
      if (node.type === 'vulnerability') {
        const isVisible = filtered.some(v => v.id === node.id);
        return {
          ...node,
          hidden: !isVisible
        };
      }
      return node;
    }));
  }, []); // Empty dependency array to prevent recreation

  // Handle export filtered vulnerabilities
  const handleExportFilteredVulnerabilities = (filteredVulns) => {
    setShowVulnerabilityReport(true);
  };

  // Handle vulnerability severity filter from legend
  const handleVulnerabilityLegendFilter = (severity) => {
    setVulnerabilityFilter(prev => ({
      ...prev,
      severity: prev.severity.includes(severity)
        ? prev.severity.filter(s => s !== severity)
        : [...prev.severity, severity]
    }));
  };

  // Map frontend questionnaire field names to backend vulnerability rule field names
  const mapQuestionnaireResponsesToVulnRules = (responses, nodeType) => {
    const mapped = {};
    
    if (nodeType === 'WebApp') {
      // Map WebApp fields
      if (responses.webapp_login !== undefined) {
        // Map webapp_login to webapp_authentication_method
        const authMapping = {
          'None': 'No Authentication',
          'Password Only': 'Username/Password only',
          'OAuth2': 'OAuth2/OIDC',
          'SAML': 'SAML',
          'MFA': 'Username/Password with MFA'
        };
        mapped.webapp_authentication_method = authMapping[responses.webapp_login] || responses.webapp_login;
      }
      if (responses.webapp_input_validation !== undefined) {
        // Map input validation
        const validationMapping = {
          'None': 'No validation',
          'Client-side only': 'Client-side only',
          'Server-side': 'Comprehensive server-side validation',
          'Basic': 'Basic validation'
        };
        mapped.webapp_input_validation = validationMapping[responses.webapp_input_validation] || responses.webapp_input_validation;
      }
      if (responses.webapp_waf_protection !== undefined) {
        mapped.webapp_https_enforcement = responses.webapp_waf_protection === 'None' ? 'HTTP only' : 'HTTPS only (HSTS enabled)';
      }
      if (responses.webapp_deployment_type !== undefined) {
        mapped.webapp_session_management = responses.webapp_deployment_type === 'Cloud' ? 'Secure session management' : 'Basic sessions';
      }
      // Add default insecure values to trigger vulnerabilities for testing
      mapped.webapp_data_encryption = mapped.webapp_data_encryption || 'No encryption';
      mapped.webapp_https_enforcement = mapped.webapp_https_enforcement || 'HTTP only';
      mapped.webapp_session_management = mapped.webapp_session_management || 'Basic sessions';
    }
    
    if (nodeType === 'API') {
      // Map API fields
      if (responses.api_auth_method !== undefined) {
        const authMapping = {
          'None': 'No Authentication',
          'API Key': 'API Key',
          'OAuth 2.0': 'OAuth2',
          'JWT': 'JWT'
        };
        mapped.api_authentication_method = authMapping[responses.api_auth_method] || responses.api_auth_method;
      }
      if (responses.api_rate_limiting !== undefined) {
        mapped.api_rate_limiting = responses.api_rate_limiting;
      }
      if (responses.api_input_validation !== undefined) {
        mapped.api_input_validation = responses.api_input_validation === 'None' ? 'No validation' : 'Schema validation';
      }
      // Add default insecure values
      mapped.api_cors_policy = mapped.api_cors_policy || 'Permissive';
      mapped.api_https_enforcement = mapped.api_https_enforcement || 'HTTP allowed';
    }
    
    if (nodeType === 'Database') {
      // Map Database fields
      if (responses.db_encryption_at_rest !== undefined) {
        mapped.database_encryption_at_rest = responses.db_encryption_at_rest === 'None' ? 'No encryption' : 'Full encryption';
      }
      if (responses.db_encryption_in_transit !== undefined) {
        mapped.database_encryption_in_transit = responses.db_encryption_in_transit ? 'TLS enabled' : 'No TLS';
      }
      if (responses.db_access_control !== undefined) {
        mapped.database_access_control = Array.isArray(responses.db_access_control) ? 
          responses.db_access_control.join(',') : responses.db_access_control;
      }
      // Add default insecure values
      mapped.database_authentication = mapped.database_authentication || 'Weak passwords';
      mapped.database_patch_management = mapped.database_patch_management || 'Manual updates';
    }
    
    // Copy any existing properly named fields
    Object.keys(responses).forEach(key => {
      if (key.startsWith('webapp_') || key.startsWith('api_') || key.startsWith('database_') || key.startsWith('backup_') || key.startsWith('monitoring_')) {
        mapped[key] = responses[key];
      }
    });
    
    console.log(`🔄 Mapped questionnaire responses for ${nodeType}:`, { original: responses, mapped });
    return mapped;
  };

  const analyzeNodeVulnerabilitiesHandler = async (nodeId, nodeType, questionnaireResponses, nodePosition = null) => {
    try {
      console.log(`🔍 Analyzing vulnerabilities for ${nodeType} node ${nodeId}`);
      
      // Map frontend field names to backend vulnerability rule field names
      const mappedResponses = mapQuestionnaireResponsesToVulnRules(questionnaireResponses, nodeType);
      
      const analysisResult = await analyzeNodeVulnerabilities(
        nodeId,
        nodeType,
        mappedResponses,
        nodePosition
      );
      
      // Store the analysis result
      setVulnerabilityAnalyses(prev => ({
        ...prev,
        [nodeId]: analysisResult
      }));
      
      // Create vulnerability nodes for visualization
      const vulnerabilityNodes = createVulnerabilityNodes(analysisResult, nodeId);
      const vulnerabilityEdges = createVulnerabilityEdges(analysisResult, nodeId);
      
      // Remove existing vulnerability nodes and edges for this parent node first to prevent duplicates
      if (vulnerabilityNodes.length > 0) {
        setNodes(nds => {
          // Filter out existing vulnerability nodes for this parent node
          const filteredNodes = nds.filter(node => {
            if (node.type !== 'vulnerability') return true;
            // Check if this vulnerability node belongs to the current parent node
            return !node.data?.parent_node_id || node.data.parent_node_id !== nodeId;
          });
          // Add new vulnerability nodes with unique keys
          const uniqueVulnNodes = vulnerabilityNodes.map(vuln => ({
            ...vuln,
            id: `${nodeId}-${vuln.id}` // Ensure unique IDs by prefixing with parent node ID
          }));
          return [...filteredNodes, ...uniqueVulnNodes];
        });
        
        setEdges(eds => {
          // Filter out existing vulnerability edges for this parent node
          const filteredEdges = eds.filter(edge => {
            return !edge.id?.includes(`${nodeId}-vulnerability-`);
          });
          // Add new vulnerability edges with updated IDs
          const uniqueVulnEdges = vulnerabilityEdges.map(edge => ({
            ...edge,
            id: `${nodeId}-vulnerability-${edge.target}`,
            target: `${nodeId}-${edge.target}` // Update target to match new vulnerability node ID
          }));
          return [...filteredEdges, ...uniqueVulnEdges];
        });
        
        console.log(`✅ Created ${vulnerabilityNodes.length} vulnerability nodes for node ${nodeId}`);
      }
      
      return analysisResult;
      
    } catch (error) {
      console.error('Error analyzing vulnerabilities:', error);
      return null;
    }
  };

  const handleVulnerabilityNodeClick = (vulnerabilityNode) => {
    setSelectedVulnerability(vulnerabilityNode);
    setShowVulnerabilityPanel(true);
  };

  const handleVulnerabilityFixed = async (vulnerabilityId) => {
    try {
      // Remove vulnerability node from graph
      setNodes(nds => nds.filter(node => node.id !== vulnerabilityId));
      setEdges(eds => eds.filter(edge => edge.target !== vulnerabilityId));
      
      // Update vulnerability analyses
      setVulnerabilityAnalyses(prev => {
        const updated = { ...prev };
        Object.keys(updated).forEach(nodeId => {
          if (updated[nodeId].vulnerability_nodes) {
            updated[nodeId].vulnerability_nodes = updated[nodeId].vulnerability_nodes.filter(
              vuln => vuln.id !== vulnerabilityId
            );
            updated[nodeId].total_vulnerabilities = updated[nodeId].vulnerability_nodes.length;
          }
        });
        return updated;
      });
      
      console.log(`✅ Vulnerability ${vulnerabilityId} marked as fixed and removed from graph`);
      
    } catch (error) {
      console.error('Error handling vulnerability fix:', error);
    }
  };

  const analyzeAllNodeVulnerabilities = async () => {
    const securityNodes = nodes.filter(node => 
      node.data?.subtype && 
      ['WebApp', 'API', 'Database', 'Backup', 'Monitoring'].includes(node.data.subtype) &&
      node.data?.questionnaireResponses
    );
    
    if (securityNodes.length === 0) {
      notification.showInfo('No Nodes Found', 'No nodes with questionnaire responses found for vulnerability analysis.');
      return;
    }

    // Check completeness for all nodes before analysis
    setIsLoading(true);
    const incompleteNodes = [];
    const completeNodes = [];
    
    try {
      for (const node of securityNodes) {
        const isComplete = await checkQuestionnaireCompleteness(node.id, node.data.subtype);
        if (isComplete) {
          completeNodes.push(node);
        } else {
          incompleteNodes.push(node);
        }
      }
      
      let message = '';
      
      if (incompleteNodes.length > 0) {
        const incompleteNames = incompleteNodes.map(n => `${n.data.subtype} (${n.data.label || n.id})`).join(', ');
        message += `⚠️ ${incompleteNodes.length} nodes have incomplete questionnaires:\n• ${incompleteNames}\n\nPlease complete all security questions before vulnerability analysis.\n\n`;
      }
      
      if (completeNodes.length === 0) {
        notification.showInfo('No Ready Nodes', message + 'No nodes are ready for vulnerability analysis. Complete questionnaires first.');
        return;
      }
      
      // Ask user whether to proceed with only complete nodes
      if (incompleteNodes.length > 0) {
        const proceed = confirm(message + `Proceed with vulnerability analysis for ${completeNodes.length} complete nodes only?`);
        if (!proceed) {
          return;
        }
      }
      
      // Analyze only complete nodes
      for (const node of completeNodes) {
        await analyzeNodeVulnerabilitiesHandler(
          node.id,
          node.data.subtype,
          node.data.questionnaireResponses,
          node.position
        );
      }
      
      let resultMessage = `✅ Vulnerability analysis completed for ${completeNodes.length} nodes.`;
      if (incompleteNodes.length > 0) {
        resultMessage += `\n\n⚠️ ${incompleteNodes.length} nodes skipped due to incomplete questionnaires.`;
      }
      notification.showInfo('Vulnerability Analysis Complete', resultMessage);
      
    } catch (error) {
      console.error('Error in bulk vulnerability analysis:', error);
      notification.showError('Analysis Error', 'Error occurred during bulk vulnerability analysis.');
    } finally {
      setIsLoading(false);
    }
  };

  const clearAllVulnerabilities = () => {
    // Remove all vulnerability nodes and edges
    setNodes(nds => nds.filter(node => node.type !== 'vulnerability'));
    setEdges(eds => eds.filter(edge => !edge.data?.vulnerability));
    
    // Clear vulnerability analyses
    setVulnerabilityAnalyses({});
    
    console.log('✅ All vulnerabilities cleared from graph');
  };

  const handleClearVulnerabilities = () => {
    setShowClearConfirmation(true);
  };

  const confirmClearVulnerabilities = () => {
    clearAllVulnerabilities();
    setShowClearConfirmation(false);
  };

  // Toggle vulnerability nodes visibility
  const toggleVulnerabilityNodesVisibility = useCallback(() => {
    const newVisibility = !vulnerabilityNodesVisible;
    setVulnerabilityNodesVisible(newVisibility);
    
    // Update all vulnerability nodes visibility
    setNodes(currentNodes => 
      currentNodes.map(node => {
        if (node.type === 'vulnerability') {
          return {
            ...node,
            hidden: !newVisibility,
            style: {
              ...node.style,
              display: newVisibility ? 'block' : 'none'
            }
          };
        }
        return node;
      })
    );
    
    // Update all vulnerability edges visibility
    setEdges(currentEdges =>
      currentEdges.map(edge => {
        if (edge.data?.vulnerability || edge.type === 'vulnerability-edge') {
          return {
            ...edge,
            hidden: !newVisibility,
            style: {
              ...edge.style,
              display: newVisibility ? 'block' : 'none'
            }
          };
        }
        return edge;
      })
    );
    
    console.log(`${newVisibility ? '👁️ Showing' : '👁️‍🗨️ Hiding'} vulnerability nodes and edges`);
  }, [vulnerabilityNodesVisible]);

  const saveQuestionnaireResponses = async (nodeId, responses) => {
    if (!currentDiagram) return;
    
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/diagrams/${currentDiagram.id}/nodes/${nodeId}/questionnaire`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ responses })
        }
      );
      
      if (response.ok) {
        // Update local node data with questionnaire responses for immediate UI refresh
        setNodes(nds => nds.map(node => {
          if (node.id === nodeId) {
            return {
              ...node,
              data: {
                ...node.data,
                questionnaireResponses: responses,
                lastQuestionnaireUpdate: new Date().toISOString()
              }
            };
          }
          return node;
        }));
        
        console.log('✅ Questionnaire responses saved and node data updated:', { nodeId, responses });
      } else if (response.status === 404) {
        console.warn('⚠️ Diagram or node not found in database - continuing with local state only');
        // Still update local node data even if backend save fails
        setNodes(nds => nds.map(node => {
          if (node.id === nodeId) {
            return {
              ...node,
              data: {
                ...node.data,
                questionnaireResponses: responses,
                lastQuestionnaireUpdate: new Date().toISOString()
              }
            };
          }
          return node;
        }));
      } else {
        console.error('Failed to save questionnaire responses:', response.status, response.statusText);
      }
    } catch (error) {
      console.error('Error saving questionnaire responses:', error);
    }
  };

  const handleDependentNodeCreation = async (dependentNodeTypes, parentAnswers) => {
    console.log('🎯 handleDependentNodeCreation called with:', {
      dependentNodeTypes,
      sourceNodeId: currentQuestionnaireNode?.id,
      sourceNodeSubtype: currentQuestionnaireNode?.data?.subtype
    });
    
    // Find the actual React Flow node with position data
    const sourceNode = nodes.find(node => node.id === currentQuestionnaireNode?.id);
    
    if (!sourceNode) {
      console.error('❌ Source node not found in nodes array:', currentQuestionnaireNode?.id);
      return;
    }
    
    if (!sourceNode.position) {
      console.error('❌ Source node missing position property:', sourceNode);
      return;
    }
    const allDependentNodes = [];
    const newNodes = [];
    const newEdges = [];
    
    // For each dependent node type, check for existing nodes with enhanced canvas detection
    for (const [index, nodeType] of dependentNodeTypes.entries()) {
      // Check if this dependency has already been processed to prevent duplicates
      const dependencyKey = `${sourceNode.id}-${nodeType}`;
      const currentState = getDependencyState(sourceNode.id, nodeType);
      
      if (currentState === 'CREATED' || currentState === 'COMPLETED') {
        console.log(`⚠️ Dependency ${sourceNode.id} → ${nodeType} already processed (${currentState}), skipping duplicate creation`);
        continue;
      }
      
      // First, check if SmartNodeConnector already created a node of this type linked to the source
      const autoGeneratedNode = nodes.find(node => 
        node.data?.subtype === nodeType && 
        node.data?.autoGenerated === true &&
        edges.some(edge => edge.source === sourceNode.id && edge.target === node.id)
      );

      if (autoGeneratedNode) {
        // Auto-generated node already exists, just add it to the questionnaire queue
        console.log(`✅ Found existing auto-generated ${nodeType} node:`, autoGeneratedNode.id);
        allDependentNodes.push(autoGeneratedNode);
        setDependencyState(sourceNode.id, nodeType, 'CREATED');
        continue;
      }

      // Enhanced Canvas Detection: Check for ANY existing nodes of this type on the canvas
      const existingNodesOfType = nodes.filter(node => 
        (node.data?.subtype === nodeType || node.subtype === nodeType) &&
        node.id !== sourceNode.id // Don't include the source node itself
      );
      
      console.log(`🔍 Enhanced Canvas Detection for ${nodeType}:`, {
        sourceNodeType: sourceNode.data?.subtype,
        lookingForNodeType: nodeType,
        existingNodesFound: existingNodesOfType.length,
        existingNodeIds: existingNodesOfType.map(n => ({ id: n.id, subtype: n.data?.subtype || n.subtype })),
        allNodesOnCanvas: nodes.map(n => ({ id: n.id, subtype: n.data?.subtype || n.subtype }))
      });

      if (existingNodesOfType.length > 0) {
        console.log(`🔍 Found ${existingNodesOfType.length} existing ${nodeType} node(s) on canvas:`, existingNodesOfType.map(n => n.id));
        
        // Ask user whether to reuse existing node or create new one
        const userChoice = await new Promise((resolve) => {
          const handleUserChoice = (choice) => {
            resolve(choice);
          };

          // Create a confirmation dialog
          const dialog = document.createElement('div');
          dialog.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
          dialog.innerHTML = `
            <div class="bg-gray-800 border border-gray-600 rounded-lg p-6 max-w-md mx-4 shadow-xl">
              <div class="flex items-center mb-4">
                <div class="w-10 h-10 bg-blue-900 rounded-full flex items-center justify-center mr-3">
                  <svg class="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                </div>
                <h3 class="text-lg font-semibold text-white">Existing ${nodeType} Node Found</h3>
              </div>
              <p class="text-gray-300 mb-6">
                A ${nodeType} node already exists on the canvas. Should this ${sourceNode.data?.subtype || 'node'} use the existing ${nodeType} or create a new one?
              </p>
              <div class="flex flex-col space-y-3">
                <button id="reuse-btn" class="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 focus:ring-2 focus:ring-green-400 focus:ring-offset-2 focus:ring-offset-gray-800 transition-colors">
                  ✅ Reuse Existing ${nodeType}
                </button>
                <button id="create-btn" class="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-400 focus:ring-offset-2 focus:ring-offset-gray-800 transition-colors">
                  ➕ Create New ${nodeType}
                </button>
              </div>
            </div>
          `;

          document.body.appendChild(dialog);

          // Add event listeners
          dialog.querySelector('#reuse-btn').addEventListener('click', () => {
            document.body.removeChild(dialog);
            handleUserChoice('reuse');
          });

          dialog.querySelector('#create-btn').addEventListener('click', () => {
            document.body.removeChild(dialog);
            handleUserChoice('create');
          });

          // Allow clicking outside to close (default to create new)
          dialog.addEventListener('click', (e) => {
            if (e.target === dialog) {
              document.body.removeChild(dialog);
              handleUserChoice('create');
            }
          });
        });

        if (userChoice === 'reuse') {
          // User chose to reuse existing node
          const selectedNode = existingNodesOfType[0]; // Use the first existing node
          console.log(`✅ User chose to reuse existing ${nodeType} node:`, selectedNode.id);
          allDependentNodes.push(selectedNode);
          setDependencyState(sourceNode.id, nodeType, 'CREATED');

          // Create edge connecting parent to the reused node if it doesn't exist
          const edgeId = `edge-${sourceNode.id}-${selectedNode.id}`;
          const edgeExists = edges.some(edge => edge.id === edgeId) || 
                            newEdges.some(edge => edge.id === edgeId);

          if (!edgeExists) {
            const reuseEdge = {
              id: edgeId,
              source: sourceNode.id,
              target: selectedNode.id,
              label: 'reuses',
              type: 'draggable',
              animated: true,
              style: {
                strokeWidth: 2,
                stroke: '#3B82F6',
                strokeDasharray: '5,5'
              },
              labelStyle: {
                fill: '#ffffff',
                fontWeight: 600,
                fontSize: '12px',
                backgroundColor: 'rgba(59, 130, 246, 0.9)',
                padding: '2px 6px',
                borderRadius: '4px',
                border: '1px solid #3B82F6'
              },
              labelBgStyle: {
                fill: 'rgba(59, 130, 246, 0.9)',
                stroke: '#3B82F6',
                strokeWidth: 1,
                fillOpacity: 0.9
              },
              markerEnd: {
                type: 'arrowclosed',
                color: '#3B82F6',
              }
            };
            newEdges.push(reuseEdge);
          }
          continue;
        }
      }

      // Create new node (either no existing nodes found or user chose to create new)
      console.log(`🔄 Creating new ${nodeType} node via conditional dependency`);
      const newNode = {
        id: `${nodeType.toLowerCase()}-${sourceNode.id}-${Date.now()}-${index}`,
        type: 'custom',
        subtype: nodeType,
        position: {
          x: sourceNode.position.x + 200 + (index * 100),
          y: sourceNode.position.y + (index % 2 === 0 ? -100 : 100)
        },
        data: {
          type: 'Asset',
          subtype: nodeType,
          label: `${nodeType} (Auto-created)`,
          intelligentNode: true,
          autoGenerated: true,
          parentNode: sourceNode.id
        }
      };
      
      newNodes.push(newNode);
      allDependentNodes.push(newNode);
      setDependencyState(sourceNode.id, nodeType, 'CREATED');

      // Create edge connecting parent to dependent node
      const edgeId = `edge-${sourceNode.id}-${newNode.id}`;
      
      // Check if edge already exists to prevent duplicates
      const edgeExists = edges.some(edge => edge.id === edgeId) || 
                        newEdges.some(edge => edge.id === edgeId);
      
      if (!edgeExists) {
        const newEdge = {
          id: edgeId,
          source: sourceNode.id,
          target: newNode.id,
          label: 'has_dependency',
          type: 'draggable',
          animated: true,
          style: {
            strokeWidth: 2,
            stroke: '#10B981',
            strokeDasharray: '3,3'
          },
          labelStyle: {
            fill: '#ffffff',
            fontWeight: 600,
            fontSize: '12px',
            backgroundColor: 'rgba(17, 24, 39, 0.9)',
            padding: '2px 6px',
            borderRadius: '4px',
            border: '1px solid #10B981'
          },
          labelBgStyle: {
            fill: 'rgba(17, 24, 39, 0.9)',
            stroke: '#10B981',
            strokeWidth: 1,
            fillOpacity: 0.9
          },
          markerEnd: {
            type: 'arrowclosed',
            color: '#10B981',
          }
        };
        newEdges.push(newEdge);
      }
    }

    // Add new nodes and edges to canvas if any were created
    if (newNodes.length > 0) {
      setNodes(prevNodes => [...prevNodes, ...newNodes]);
    }
    if (newEdges.length > 0) {
      setEdges(prevEdges => [...prevEdges, ...newEdges]);
    }

    // CRITICAL FIX: Save newly created nodes to database
    if (newNodes.length > 0 && currentDiagram) {
      try {
        console.log('💾 Saving newly created dependent nodes to database:', newNodes.map(n => n.id));
        
        // Format nodes for backend
        const backendNodes = newNodes.map(node => ({
          id: node.id,
          type: node.data.type || "Asset",
          subtype: node.data.subtype || node.subtype,
          label: node.data.label || `${node.data.subtype} (Auto-created)`,
          position: node.position,
          data: node.data,
          mitre_ids: [],
          cve_ids: [],
          created_at: new Date().toISOString()
        }));

        // Format edges for backend
        const backendEdges = newEdges.map(edge => ({
          id: edge.id,
          source: edge.source,
          target: edge.target,
          label: edge.label || "",
          type: edge.type,
          data: edge.data || {}
        }));

        // Update diagram with new nodes and edges
        const updatedDiagram = {
          ...currentDiagram,
          nodes: [...(currentDiagram.nodes || []), ...backendNodes],
          edges: [...(currentDiagram.edges || []), ...backendEdges]
        };

        await updateDiagram(currentDiagram.id, updatedDiagram);
        setCurrentDiagram(updatedDiagram);
        console.log('✅ Dependent nodes saved to database successfully');
      } catch (error) {
        console.error('❌ Error saving dependent nodes to database:', error);
      }
    }

    // Queue questionnaires ONLY for newly created nodes (not reused ones)
    if (newNodes.length > 0) {
      console.log(`🎯 Queueing questionnaires for ${newNodes.length} newly created dependent nodes:`, newNodes.map(n => n.data.subtype));
      setQuestionnaireQueue(newNodes);
      setCurrentQueueIndex(0);
      
      // Start questionnaire for the first newly created dependent node
      console.log(`🚀 Starting legacy questionnaire for newly created dependent node:`, {
        nodeId: newNodes[0].id,
        nodeSubtype: newNodes[0].subtype || newNodes[0].data?.subtype,
        parentId: currentQuestionnaireNode?.id
      });
      
      const firstNode = newNodes[0];
      const nodeSubtype = firstNode.subtype || firstNode.data?.subtype;
      
      // Set the first questionnaire in the queue as current
      setCurrentQuestionnaireNode({
        id: firstNode.id,
        subtype: nodeSubtype,
        data: { 
          subtype: nodeSubtype,
          parentNode: firstNode.data?.parentNode 
        }
      });
      
      // Keep the modal open for the first dependent questionnaire
      setShowSecurityQuestionnaire(true);
    } else {
      console.log('✅ All dependencies resolved by reusing existing nodes - no new questionnaires needed');
      // All dependencies were satisfied by reusing existing nodes, so we can continue with parent questionnaire
      // The parent questionnaire should continue automatically
    }
  };

  // Handler for smart node creation
  const handleCreateLinkedNodes = (sourceNodeId, nodeSubtype, answers, currentNodes) => {
    return smartNodeConnector.processQuestionnaireAnswers(sourceNodeId, nodeSubtype, answers, currentNodes);
  };

  const handleSecurityQuestionnaireCancel = () => {
    if (currentQuestionnaireNode) {
      setActiveQuestionnaires(prev => {
        const newSet = new Set(prev);
        newSet.delete(currentQuestionnaireNode.id);
        return newSet;
      });
    }
    setShowSecurityQuestionnaire(false);
    setCurrentQuestionnaireNode(null);
    setCurrentQuestionnaireAnswers({}); // Clear existing answers
    setQuestionnaireQueue([]);
    setCurrentQueueIndex(0);
    setParentQuestionnaireStack([]); // Clear parent stack on cancel
  };

  const handleQuestionnaireOverviewEdit = async (node) => {
    setShowQuestionnaireOverview(false);
    
    // Get existing answers from the backend
    let existingAnswers = {};
    try {
      if (currentDiagram) {
        const response = await fetch(
          `${process.env.REACT_APP_BACKEND_URL}/api/diagrams/${currentDiagram.id}/nodes/${node.id}/questionnaire`
        );
        
        if (response.ok) {
          const data = await response.json();
          existingAnswers = data.questionnaire_responses || {};
          console.log('📝 Fetched existing questionnaire answers:', existingAnswers);
        }
      }
    } catch (error) {
      console.error('⚠️ Error fetching existing questionnaire answers:', error);
    }
    
    // Use legacy questionnaire system
    const nodeSubtype = node.subtype || node.data?.subtype;
    startLegacyQuestionnaire(node.id, nodeSubtype, null, existingAnswers);
  };

  const handleNodeBranchUpdate = (nodeId, updatedBranches) => {
    setNodeBranches(prev => ({
      ...prev,
      [nodeId]: updatedBranches
    }));

    // Update node data
    setNodes(nds => nds.map(node => {
      if (node.id === nodeId) {
        return {
          ...node,
          data: {
            ...node.data,
            securityBranches: updatedBranches
          }
        };
      }
      return node;
    }));
  };

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.ctrlKey || event.metaKey) {
        switch (event.key) {
          case 's':
            event.preventDefault();
            handleSaveDiagram();
            break;
          case 'n':
            event.preventDefault();
            handleNewDiagram();
            break;
          case 'r':
            event.preventDefault();
            handleRunSimulation();
            break;
          case 'z':
            event.preventDefault();
            if (event.shiftKey) {
              handleRedo();
            } else {
              handleUndo();
            }
            break;
          case 'y':
            event.preventDefault();
            handleRedo();
            break;
          case 'd':
            if (selectedNode) {
              event.preventDefault();
              duplicateNode(selectedNode);
            }
            break;
          default:
            break;
        }
      } else if (event.key === 'Escape') {
        // Close vulnerability dropdown menu
        if (showVulnMenu) {
          setShowVulnMenu(false);
        }
        // Clear attack path highlighting or close context menu
        else if (contextMenu) {
          setContextMenu(null);
        } else if (highlightedPaths.length > 0) {
          event.preventDefault();
          clearAttackPathHighlighting();
        }
      } else if (event.key === 'Delete' && selectedNode) {
        event.preventDefault();
        deleteNode(selectedNode);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentDiagram]);

  // Handle click outside vulnerability dropdown menu
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (showVulnMenu && !event.target.closest('.vulnerability-dropdown')) {
        setShowVulnMenu(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showVulnMenu]);

  return (
    <div className="h-screen flex flex-col bg-gray-900">
      {/* Enhanced Header */}
      <div className={`bg-gray-800 border-b border-gray-700 transition-all duration-300 ease-in-out ${
        isTopToolbarCollapsed ? 'h-0 overflow-hidden' : 'p-4'
      }`}>
        <div className="flex items-center justify-between overflow-x-auto no-scrollbar">
          <div className="flex items-center space-x-4">
            <Shield className="h-8 w-8 text-blue-400" />
            <div>
              <h1 className="text-xl font-bold text-white">Security Modeling Platform</h1>
              <div className="text-xs text-gray-400">
                Advanced Threat Modeling & Attack Path Analysis
              </div>
            </div>
          </div>
          
          {/* View Mode Toggle */}
          <div className="flex items-center space-x-2 bg-gray-700 rounded-lg p-1">
            <button
              onClick={() => setViewMode('modeling')}
              className={`px-3 py-1 rounded-md transition-colors text-sm ${
                viewMode === 'modeling'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:text-white'
              }`}
            >
              <Layers className="h-4 w-4 inline mr-2" />
              Modeling
            </button>
            <button
              onClick={() => setViewMode('analysis')}
              className={`px-3 py-1 rounded-md transition-colors text-sm ${
                viewMode === 'analysis'
                  ? 'bg-red-600 text-white'
                  : 'text-gray-300 hover:text-white'
              }`}
              disabled={!simulationResult}
            >
              <BarChart3 className="h-4 w-4 inline mr-2" />
              Analysis
            </button>
          </div>
          
          {/* 🎯 PRIMARY ACTIONS - Most Important Functions */}
          <div className="flex items-center space-x-3">
            {/* File Operations Group */}
            <div className="flex items-center space-x-1">
              <button
                onClick={handleNewDiagram}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center space-x-2 text-sm font-medium shadow-sm"
                title="New Diagram (Ctrl+N)"
              >
                <span>New</span>
              </button>
              
              <button
                onClick={handleSaveDiagram}
                disabled={isLoading}
                className={`px-4 py-2 rounded-lg flex items-center space-x-2 text-sm font-medium shadow-sm ${
                  hasUnsavedChanges
                    ? 'bg-blue-600 text-white hover:bg-blue-700'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                } disabled:opacity-50`}
                title="Save Diagram (Ctrl+S)"
              >
                <Save className="h-4 w-4" />
                <span>{isLoading ? 'Saving...' : 'Save'}</span>
                {hasUnsavedChanges && (
                  <div className="w-2 h-2 bg-yellow-400 rounded-full"></div>
                )}
              </button>
            </div>

            {/* Divider */}
            <div className="h-6 w-px bg-gray-600"></div>

            {/* Analysis Actions - Primary Functions */}
            <div className="flex items-center space-x-1">
              <button
                onClick={handleRunSimulation}
                disabled={isLoading || nodes.length === 0}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 text-sm font-medium shadow-sm"
                title="Run Attack Path Simulation (Ctrl+R)"
              >
                <Play className="h-4 w-4" />
                <span>{isLoading ? 'Analyzing...' : 'Simulate'}</span>
              </button>
              
              <button
                onClick={analyzeAllNodeVulnerabilities}
                disabled={isLoading || nodes.filter(n => n.data?.questionnaireResponses).length === 0}
                className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 text-sm font-medium shadow-sm"
                title="Analyze Security Vulnerabilities"
              >
                <AlertTriangle className="h-4 w-4" />
                <span>Analyze</span>
              </button>
              
              {/* UI Demo Button - Commented out after demonstration
              <button
                onClick={() => setShowUIDemo(!showUIDemo)}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 flex items-center space-x-2 text-sm font-medium shadow-sm"
                title="Show UI Improvements Demo"
              >
                <span>UI Demo</span>
              </button>
              */}
              
              {/* Vulnerability Toggle Button - Shows when vulnerability nodes exist */}
              {nodes.some(n => n.type === 'vulnerability') && (
                <button
                  onClick={toggleVulnerabilityNodesVisibility}
                  className={`px-4 py-2 rounded-lg flex items-center space-x-2 text-sm font-medium shadow-sm transition-colors ${
                    vulnerabilityNodesVisible
                      ? 'bg-purple-600 text-white hover:bg-purple-700'
                      : 'bg-gray-600 text-gray-300 hover:bg-gray-700'
                  }`}
                  title={`${vulnerabilityNodesVisible ? 'Hide' : 'Show'} Vulnerability Nodes`}
                >
                  {vulnerabilityNodesVisible ? <Eye className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}
                  <span>{vulnerabilityNodesVisible ? 'Hide' : 'Show'}</span>
                </button>
              )}
            </div>

            {/* Divider */}
            <div className="h-6 w-px bg-gray-600"></div>

            {/* 🛡️ VULNERABILITY MANAGEMENT - Enhanced Dropdown */}
            <div className="relative vulnerability-dropdown">
              {allVulnerabilities.length > 0 ? (
                <div className="flex items-center bg-gray-700 rounded-lg border border-gray-600">
                  <button
                    onClick={() => {
                      setIsVulnerabilitiesCollapsed(false);
                    }}
                    className={`px-4 py-2 rounded-l-lg flex items-center space-x-2 text-sm font-medium transition-colors ${
                      !isVulnerabilitiesCollapsed || showVulnerabilityFilter || showVulnerabilityLegend
                        ? 'bg-purple-600 text-white'
                        : 'text-white hover:bg-gray-600'
                    }`}
                    title="Manage Vulnerabilities"
                  >
                    <Shield className="h-4 w-4" />
                    <span>Vulnerabilities</span>
                    <span className="ml-2 px-2 py-0.5 bg-purple-600 text-white text-xs rounded-full font-semibold">
                      {allVulnerabilities.length}
                    </span>
                  </button>
                  
                  <button
                    onClick={() => setShowVulnMenu(!showVulnMenu)}
                    className={`px-3 py-2 rounded-r-lg border-l border-gray-600 flex items-center transition-colors ${
                      showVulnMenu
                        ? 'bg-gray-600 text-white'
                        : 'text-gray-300 hover:bg-gray-600 hover:text-white'
                    }`}
                    aria-haspopup="menu"
                    aria-expanded={showVulnMenu}
                    title="Vulnerability Actions"
                  >
                    <ChevronDown className={`h-4 w-4 transition-transform ${showVulnMenu ? 'rotate-180' : ''}`} />
                  </button>
                  
                  {/* Enhanced Dropdown Menu */}
                  {showVulnMenu && (
                    <div className="absolute top-full right-0 mt-2 w-56 bg-gray-800 rounded-lg border border-gray-600 shadow-xl z-50 py-2">
                      <div className="px-3 py-2 text-xs font-semibold text-gray-400 uppercase tracking-wide border-b border-gray-700">
                        Vulnerability Actions
                      </div>
                      <div role="menu" className="py-1">
                        <button
                          role="menuitem"
                          onClick={() => {
                            setIsVulnerabilitiesCollapsed(false);
                            setShowVulnMenu(false);
                          }}
                          className="w-full px-4 py-3 text-left text-sm text-white hover:bg-gray-700 flex items-center space-x-3 transition-colors"
                        >
                          <Shield className="h-4 w-4 text-blue-400" />
                          <div>
                            <div className="font-medium">Manage</div>
                            <div className="text-xs text-gray-400">View and organize vulnerabilities</div>
                          </div>
                        </button>
                        
                        <button
                          role="menuitem"
                          onClick={() => {
                            setShowVulnerabilityFilter(!showVulnerabilityFilter);
                            setShowVulnMenu(false);
                          }}
                          className="w-full px-4 py-3 text-left text-sm text-white hover:bg-gray-700 flex items-center space-x-3 transition-colors"
                        >
                          <Filter className="h-4 w-4 text-green-400" />
                          <div>
                            <div className="font-medium">Filter</div>
                            <div className="text-xs text-gray-400">Filter by severity and type</div>
                          </div>
                        </button>
                        
                        <button
                          role="menuitem"
                          onClick={() => {
                            setShowVulnerabilityLegend(!showVulnerabilityLegend);
                            setShowVulnMenu(false);
                          }}
                          className="w-full px-4 py-3 text-left text-sm text-white hover:bg-gray-700 flex items-center space-x-3 transition-colors"
                        >
                          <BarChart3 className="h-4 w-4 text-purple-400" />
                          <div>
                            <div className="font-medium">Dashboard</div>
                            <div className="text-xs text-gray-400">Security metrics overview</div>
                          </div>
                        </button>
                        
                        <div className="h-px bg-gray-700 my-2 mx-2" />
                        
                        <button
                          role="menuitem"
                          onClick={() => {
                            setShowVulnerabilityReport(true);
                            setShowVulnMenu(false);
                          }}
                          className="w-full px-4 py-3 text-left text-sm text-white hover:bg-gray-700 flex items-center space-x-3 transition-colors"
                        >
                          <Download className="h-4 w-4 text-emerald-400" />
                          <div>
                            <div className="font-medium">Export Report</div>
                            <div className="text-xs text-gray-400">Generate security report</div>
                          </div>
                        </button>
                        
                        <button
                          role="menuitem"
                          onClick={() => {
                            handleClearVulnerabilities();
                            setShowVulnMenu(false);
                          }}
                          className="w-full px-4 py-3 text-left text-sm text-red-300 hover:bg-red-900 hover:text-red-100 flex items-center space-x-3 transition-colors"
                        >
                          <X className="h-4 w-4" />
                          <div>
                            <div className="font-medium">Clear All</div>
                            <div className="text-xs text-red-400">Remove all vulnerabilities</div>
                          </div>
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <button
                  className="px-4 py-2 bg-gray-700 text-gray-400 rounded-lg cursor-not-allowed flex items-center space-x-2 text-sm"
                  title="No vulnerabilities found. Run analysis first."
                  disabled
                >
                  <Shield className="h-4 w-4" />
                  <span>Vulnerabilities</span>
                  <span className="text-xs">(0)</span>
                </button>
              )}
            </div>
          </div>

          {/* 🔧 SECONDARY ACTIONS - Organized Dropdown */}
          <div className="flex items-center space-x-2">
            {/* Quick Actions */}
            <button
              onClick={clearAttackPathHighlighting}
              disabled={highlightedPaths.length === 0}
              className="px-3 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 text-sm"
              title="Clear Attack Path Highlights (Esc)"
            >
              <EyeOff className="h-4 w-4" />
            </button>

            {/* Tools & Options Dropdown */}
            <div className="relative">
              <button
                onClick={() => setShowAdvancedControls(!showAdvancedControls)}
                className="px-3 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 hover:text-white flex items-center space-x-2 text-sm"
                title="More Tools & Options"
              >
                <Menu className="h-4 w-4" />
                <ChevronDown className={`h-3 w-3 transition-transform ${showAdvancedControls ? 'rotate-180' : ''}`} />
              </button>
              
              {showAdvancedControls && (
                <div className="absolute top-full right-0 mt-2 w-48 bg-gray-800 rounded-lg border border-gray-600 shadow-xl z-50 py-2">
                  <div className="px-3 py-2 text-xs font-semibold text-gray-400 uppercase tracking-wide border-b border-gray-700">
                    Tools & Options
                  </div>
                  <div className="py-1">
                    <button
                      onClick={() => {
                        setShowTemplateLibrary(true);
                        setShowAdvancedControls(false);
                      }}
                      className="w-full px-4 py-2 text-left text-sm text-white hover:bg-gray-700 flex items-center space-x-3"
                    >
                      <BookOpen className="h-4 w-4 text-blue-400" />
                      <span>Templates</span>
                    </button>
                    
                    <div className="h-px bg-gray-700 my-1 mx-2" />
                    
                    <div className="relative">
                      <input
                        type="file"
                        accept=".json"
                        onChange={(e) => {
                          handleImportDiagram(e);
                          setShowAdvancedControls(false);
                        }}
                        className="absolute inset-0 opacity-0 cursor-pointer"
                        id="import-file-menu"
                      />
                      <label
                        htmlFor="import-file-menu"
                        className="w-full px-4 py-2 text-left text-sm text-white hover:bg-gray-700 flex items-center space-x-3 cursor-pointer"
                      >
                        <Upload className="h-4 w-4 text-gray-400" />
                        <span>Import</span>
                      </label>
                    </div>
                    
                    <button
                      onClick={() => {
                        handleExportDiagram();
                        setShowAdvancedControls(false);
                      }}
                      disabled={!currentDiagram}
                      className="w-full px-4 py-2 text-left text-sm text-white hover:bg-gray-700 disabled:text-gray-500 disabled:cursor-not-allowed flex items-center space-x-3"
                    >
                      <Download className="h-4 w-4 text-gray-400" />
                      <span>Export</span>
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Save Status Indicator */}
            <div className="text-xs text-gray-400 ml-4">
              {hasUnsavedChanges ? (
                <span className="text-yellow-400 flex items-center space-x-1">
                  <div className="w-1.5 h-1.5 bg-yellow-400 rounded-full"></div>
                  <span>Unsaved</span>
                </span>
              ) : lastSavedAt ? (
                <span className="text-green-400 flex items-center space-x-1">
                  <div className="w-1.5 h-1.5 bg-green-400 rounded-full"></div>
                  <span>Saved {lastSavedAt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                </span>
              ) : (
                <span className="text-gray-500">Not saved</span>
              )}
            </div>
          </div>
        </div>
        
        {/* Advanced Layout Controls - Simplified */}
        {showAdvancedControls && (
          <div className="mt-3 pt-3 border-t border-gray-700">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <button
                  onClick={handleAutoLayout}
                  disabled={isLoading || nodes.length === 0}
                  className="px-3 py-1.5 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 flex items-center space-x-2 text-sm"
                  title="Automatically arrange nodes"
                >
                  <Zap className="h-4 w-4" />
                  <span>Auto-Layout</span>
                </button>
              
                <button
                  onClick={handleFitAllNodes}
                  disabled={nodes.length === 0}
                  className="px-3 py-1.5 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center space-x-2 text-sm"
                  title="Fit All Nodes to Canvas"
                >
                  <Maximize2 className="h-4 w-4" />
                  <span>Fit All</span>
                </button>
                
                <button
                  onClick={handleUndo}
                  disabled={undoStack.length === 0}
                  className="px-3 py-1.5 bg-gray-600 text-white rounded-lg hover:bg-gray-500 disabled:opacity-50 flex items-center space-x-2 text-sm"
                  title="Undo (Ctrl+Z)"
                >
                  <Undo className="h-4 w-4" />
                  <span>Undo</span>
                </button>

                <button
                  onClick={handleRedo}
                  disabled={redoStack.length === 0}
                  className="px-3 py-1.5 bg-gray-600 text-white rounded-lg hover:bg-gray-500 disabled:opacity-50 flex items-center space-x-2 text-sm"
                  title="Redo (Ctrl+Y)"
                >
                  <Redo className="h-4 w-4" />
                  <span>Redo</span>
                </button>
              </div>
              
              <div className="flex items-center space-x-3">
                <button
                  onClick={() => setSnapToGrid(!snapToGrid)}
                  className={`px-3 py-1.5 rounded-lg flex items-center space-x-2 text-sm ${
                    snapToGrid 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-gray-600 text-white hover:bg-gray-500'
                  }`}
                  title="Toggle snap to grid"
                >
                  <Grid className="h-4 w-4" />
                  <span>Grid {snapToGrid ? 'On' : 'Off'}</span>
                </button>

                <button
                  onClick={handleClearAllConfirm}
                  className="px-3 py-1.5 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center space-x-2 text-sm"
                  title="Clear All Nodes and Edges"
                >
                  <Trash2 className="h-4 w-4" />
                  <span>Clear All</span>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
      

      <div className="flex flex-1 overflow-hidden relative">
        {/* Left Sidebar Toggle Button */}
        <div className="absolute top-1/2 left-0 transform -translate-y-1/2 z-50">
          <button
            onClick={() => setIsLeftSidebarCollapsed(!isLeftSidebarCollapsed)}
            className="px-1 py-3 bg-gray-700 text-white rounded-r hover:bg-gray-600 transition-colors flex items-center justify-center shadow-lg"
            title={isLeftSidebarCollapsed ? "Show Security Nodes Menu" : "Hide Security Nodes Menu"}
          >
            {isLeftSidebarCollapsed ? (
              <ChevronRight className="h-4 w-4" />
            ) : (
              <ChevronLeft className="h-4 w-4" />
            )}
          </button>
        </div>

        {/* Left Sidebar - Advanced Node Library */}
        <div className={`bg-gray-800 border-r border-gray-700 overflow-y-auto transition-all duration-300 ease-in-out ${
          isLeftSidebarCollapsed ? 'w-0 overflow-hidden' : 'w-80'
        }`}>
          <AdvancedNodeLibrary />
          
          {/* Diagram List */}
          <div className="p-4 border-t border-gray-700">
            <div className="flex items-center space-x-2 mb-4">
              <FolderOpen className="h-5 w-5 text-gray-400" />
              <h3 className="text-white font-medium">Saved Models</h3>
            </div>
            <div className="space-y-2">
              {diagrams.map((diagram) => (
                <button
                  key={diagram.id}
                  onClick={() => handleLoadDiagram(diagram)}
                  className={`w-full text-left p-3 rounded text-white text-sm transition-colors ${
                    currentDiagram?.id === diagram.id
                      ? 'bg-blue-700 border border-blue-500'
                      : 'bg-gray-700 hover:bg-gray-600'
                  }`}
                >
                  <div className="font-medium">{diagram.title}</div>
                  <div className="text-gray-400 text-xs">
                    {diagram.nodes?.length || 0} nodes, {diagram.edges?.length || 0} edges
                  </div>
                  <div className="text-gray-500 text-xs">
                    {new Date(diagram.updated_at || diagram.created_at).toLocaleDateString()}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Main Canvas Area */}
        <div className="flex-1 relative">
          <ReactFlow
            nodes={nodes}
            edges={edges.map(edge => ({
              ...edge,
              selected: selectedEdge?.id === edge.id
            }))}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={onNodeClick}
            onEdgeClick={onEdgeClick}
            onPaneClick={onPaneClick}
            onDrop={onDrop}
            onDragOver={onDragOver}
            nodeTypes={nodeTypes}
            edgeTypes={edgeTypes}
            defaultEdgeOptions={defaultEdgeOptions}
            className="bg-gray-900"
            fitView
            snapToGrid
            snapGrid={[15, 15]}
            nodesDraggable={true}
            nodesConnectable={true}
            elementsSelectable={true}
            selectNodesOnDrag={false}
          >
            <Controls 
              className="bg-gray-800 border-gray-700"
              showZoom={true}
              showFitView={true}
              showInteractive={true}
            />
            <MiniMap 
              className="bg-gray-800 border-gray-700" 
              nodeColor={(node) => {
                const colorMap = {
                  'Actor': '#DC2626',
                  'Asset': '#059669', 
                  'Surface': '#D97706',
                  'Control': '#2563EB',
                  'Zone': '#7C3AED',
                  'Signal': '#0891B2'
                };
                return colorMap[node.data?.type] || '#6B7280';
              }}
              maskColor="rgba(0, 0, 0, 0.6)"
              pannable
              zoomable
            />
            <Background 
              variant="dots" 
              gap={20} 
              size={1} 
              color="#374151" 
            />
            
            {/* Connection Types Legend */}
            <Panel position="bottom-left" className="bg-gray-800 border border-gray-700 rounded-lg p-3 m-4 max-w-sm">
              <div className="text-white text-sm font-semibold mb-2 flex items-center">
                <Network className="h-4 w-4 mr-2" />
                Connection Types
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-0.5 bg-blue-500"></div>
                  <span className="text-blue-300">HTTPS REST</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-0.5 bg-purple-500"></div>
                  <span className="text-purple-300">SQL DB</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-0.5 bg-green-500" style={{clipPath: 'polygon(0 50%, 25% 0, 75% 0, 100% 50%, 75% 100%, 25% 100%)'}}></div>
                  <span className="text-green-300">File I/O</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-0.5 bg-amber-500" style={{borderStyle: 'dashed', borderWidth: '1px 0'}}></div>
                  <span className="text-amber-300">Message</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-0.5 bg-red-500" style={{borderStyle: 'dashed', borderWidth: '2px 0'}}></div>
                  <span className="text-red-300">Attack Vector</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-0.5 bg-emerald-600" style={{borderStyle: 'dashed', borderWidth: '1px 0'}}></div>
                  <span className="text-emerald-200 font-medium">Protects</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-0.5 bg-cyan-500"></div>
                  <span className="text-cyan-200 font-medium">Cloud API</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-0.5 bg-gray-500"></div>
                  <span className="text-gray-200 font-medium">Data Flow</span>
                </div>
              </div>
            </Panel>
            
            {/* Canvas Info Panels */}
            {currentDiagram && (
              <Panel position="top-left" className="bg-gray-800 border border-gray-700 rounded p-3">
                <div className="text-white text-sm font-medium">{currentDiagram.title}</div>
                <div className="text-gray-400 text-xs mt-1">
                  {viewMode === 'analysis' ? 'Analysis Mode' : 'Modeling Mode'}
                </div>
              </Panel>
            )}
            
            {simulationResult && viewMode === 'analysis' && (
              <Panel position="top-right" className="bg-gray-800 border border-gray-700 rounded p-3">
                <div className="text-white text-sm font-medium">
                  Risk Level: <span className={`${
                    simulationResult.overall_risk_level === 'Critical' ? 'text-red-400' :
                    simulationResult.overall_risk_level === 'High' ? 'text-orange-400' :
                    simulationResult.overall_risk_level === 'Medium' ? 'text-yellow-400' :
                    'text-green-400'
                  }`}>{simulationResult.overall_risk_level}</span>
                </div>
                <div className="text-gray-400 text-xs">
                  {simulationResult.attack_paths?.length || 0} attack paths found
                </div>
              </Panel>
            )}
            
            {isLoading && (
              <Panel position="bottom-center" className="bg-gray-800 border border-gray-700 rounded p-3">
                <div className="text-white text-sm flex items-center space-x-2">
                  <div className="animate-spin h-4 w-4 border-2 border-blue-400 border-t-transparent rounded-full"></div>
                  <span>Processing advanced simulation...</span>
                </div>
              </Panel>
            )}
          </ReactFlow>
          
          {/* Node Info Overlay */}
          {showNodeInfoOverlay && nodeInfoOverlayData && (
            <NodeInfoOverlay
              node={nodeInfoOverlayData.node}
              position={nodeInfoOverlayData.position}
              vulnerabilityCount={nodeInfoOverlayData.vulnerabilityCount}
              strideScore={nodeInfoOverlayData.strideScore}
              answeredQuestions={nodeInfoOverlayData.answeredQuestions}
              totalQuestions={nodeInfoOverlayData.totalQuestions}
              onClose={closeNodeInfoOverlay}
            />
          )}
        </div>

        {/* Right Sidebar - Properties and Analysis */}
        <div className="w-80 bg-gray-800 border-l border-gray-700 overflow-y-auto">
          {viewMode === 'modeling' && (
            <>
              {/* Node Information Panel - Collapsible */}
              <div className="border-b border-gray-700">
                <div className="p-3 bg-gradient-to-r from-gray-800 to-gray-700 border-b border-gray-600">
                  <button
                    onClick={() => setIsCanvasNodesCollapsed(!isCanvasNodesCollapsed)}
                    className="w-full flex items-center justify-between text-white hover:bg-gray-700 rounded p-2 transition-colors"
                  >
                    <div className="flex items-center space-x-2">
                      <Layers className="h-4 w-4 text-blue-400" />
                      <h3 className="font-medium text-sm">Canvas Nodes</h3>
                      <Badge variant="secondary" className="bg-blue-900 text-blue-300 text-xs h-5 px-2">
                        {nodes.length}
                      </Badge>
                    </div>
                    {isCanvasNodesCollapsed ? (
                      <ChevronDown className="h-4 w-4 text-gray-400" />
                    ) : (
                      <ChevronUp className="h-4 w-4 text-gray-400" />
                    )}
                  </button>
                </div>
                {!isCanvasNodesCollapsed && (
                  <NodeInfoPanel 
                    nodes={nodes}
                    selectedNode={selectedNode}
                    onEditQuestionnaire={handleEditQuestionnaireFromInfo}
                  />
                )}
              </div>

              {/* STRIDE Threat Analysis Panel - Collapsible */}
              <div className="border-b border-gray-700">
                <div className="p-3 bg-gradient-to-r from-gray-800 to-gray-700 border-b border-gray-600">
                  <button
                    onClick={() => setIsStrideCollapsed(!isStrideCollapsed)}
                    className="w-full flex items-center justify-between text-white hover:bg-gray-700 rounded p-2 transition-colors"
                  >
                    <div className="flex items-center space-x-2">
                      <Shield className="h-4 w-4 text-green-400" />
                      <h3 className="font-medium text-sm">STRIDE Analysis</h3>
                      {strideThreatsCount > 0 && (
                        <Badge variant="secondary" className="bg-green-900 text-green-300 text-xs h-5 px-2">
                          {strideThreatsCount}
                        </Badge>
                      )}
                    </div>
                    {isStrideCollapsed ? (
                      <ChevronDown className="h-4 w-4 text-gray-400" />
                    ) : (
                      <ChevronUp className="h-4 w-4 text-gray-400" />
                    )}
                  </button>
                </div>
                {!isStrideCollapsed && (
                  <StridePanel 
                    diagramId={currentDiagram?.id}
                    onAnalyzeStride={(result) => {
                      console.log('STRIDE Analysis completed:', result);
                    }}
                    onStrideDataUpdate={setStrideThreatsCount}
                  />
                )}
              </div>

              {/* Vulnerability Management Section - Collapsible in Right Sidebar */}
              {allVulnerabilities.length > 0 && (
                <div className="border-b border-gray-700">
                  <div className="p-3 bg-gradient-to-r from-gray-800 to-gray-700 border-b border-gray-600">
                    <button
                      onClick={() => setIsVulnerabilitiesCollapsed(!isVulnerabilitiesCollapsed)}
                      className="w-full flex items-center justify-between text-white hover:bg-gray-700 rounded p-2 transition-colors"
                    >
                      <div className="flex items-center space-x-2">
                        <AlertTriangle className="h-4 w-4 text-red-400" />
                        <h3 className="font-medium text-sm">Vulnerabilities</h3>
                        <Badge variant="secondary" className="bg-red-900 text-red-300 text-xs h-5 px-2">
                          {allVulnerabilities.length}
                        </Badge>
                      </div>
                      {isVulnerabilitiesCollapsed ? (
                        <ChevronDown className="h-4 w-4 text-gray-400" />
                      ) : (
                        <ChevronUp className="h-4 w-4 text-gray-400" />
                      )}
                    </button>
                  </div>
                  {!isVulnerabilitiesCollapsed && (
                    <div className="max-h-64 overflow-y-auto">
                      <VulnerabilityList
                        vulnerabilities={allVulnerabilities}
                        nodes={nodes}
                        onVulnerabilityClick={(vulnerability) => {
                          setSelectedVulnerability(vulnerability);
                          setShowVulnerabilityPanel(true);
                        }}
                        onCreateFindings={(selectedVulns) => {
                          setFilteredVulnerabilities(selectedVulns);
                          setShowVulnerabilityReport(true);
                        }}
                        className="p-0"
                      />
                    </div>
                  )}
                </div>
              )}

              {/* Advanced Layout Controls - Collapsible */}
              <div className="border-b border-gray-700">
                <div className="p-3 bg-gradient-to-r from-gray-800 to-gray-700 border-b border-gray-600">
                  <button
                    onClick={() => setIsAdvancedLayoutCollapsed(!isAdvancedLayoutCollapsed)}
                    className="w-full flex items-center justify-between text-white hover:bg-gray-700 rounded p-2 transition-colors"
                  >
                    <div className="flex items-center space-x-2">
                      <Settings className="h-4 w-4 text-purple-400" />
                      <h3 className="font-medium text-sm">Advanced Layout</h3>
                    </div>
                    {isAdvancedLayoutCollapsed ? (
                      <ChevronDown className="h-4 w-4 text-gray-400" />
                    ) : (
                      <ChevronUp className="h-4 w-4 text-gray-400" />
                    )}
                  </button>
                </div>
                {!isAdvancedLayoutCollapsed && (
                  <div className="p-4">
                    <AdvancedLayoutControls 
                      currentDiagram={currentDiagram}
                      nodes={nodes}
                      edges={edges}
                      setNodes={setNodes}
                      setEdges={setEdges}
                      isLoading={isLoading}
                      setIsLoading={setIsLoading}
                      fitView={fitView}
                    />
                  </div>
                )}
              </div>
              
              {/* Simulation Debugger */}
              <SimulationDebugger
                nodes={nodes}
                edges={edges}
                onRunSimulation={handleRunSimulation}
                simulationResult={simulationResult}
                isLoading={isLoading}
              />
              
              {/* Security Branches Visualizer - Only show if node has intelligent features */}
              {selectedNode?.data?.intelligentNode && (
                <div className="border-t border-gray-700">
                  <NodeBranchVisualizer
                    nodeId={selectedNode.id}
                    nodeSubtype={selectedNode.data.subtype}
                    branches={nodeBranches[selectedNode.id] || []}
                    onBranchUpdate={handleNodeBranchUpdate}
                    isExpanded={true}
                  />
                </div>
              )}
            </>
          )}
          {viewMode === 'analysis' && simulationResult && (
            <EnhancedSimulationPanel 
              result={simulationResult} 
              onHighlightPath={highlightAttackPaths}
              onClearHighlights={clearAttackPathHighlighting}
            />
          )}
          {viewMode === 'analysis' && !simulationResult && (
            <div className="p-4 text-center">
              <div className="text-gray-400 text-sm">
                Run a simulation to see analysis results
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Legacy Security Questionnaire - ENABLED: Main questionnaire system */}
      {showSecurityQuestionnaire && currentQuestionnaireNode && (
        <SecurityQuestionnaire 
          nodeSubtype={currentQuestionnaireNode.subtype || currentQuestionnaireNode.data?.subtype} 
          onComplete={handleSecurityQuestionnaireComplete}
          onCancel={handleSecurityQuestionnaireCancel}
          existingValues={currentQuestionnaireAnswers}
          isVisible={showSecurityQuestionnaire}
          sourceNode={currentQuestionnaireNode}
          currentNodes={nodes}
          onCreateLinkedNodes={handleCreateLinkedNodes}
          getIncompleteDependencies={getIncompleteDependencies}
          resumeFromPromptIndex={
            parentQuestionnaireStack.length > 0 && 
            parentQuestionnaireStack[parentQuestionnaireStack.length - 1]?.nodeId === currentQuestionnaireNode.id 
              ? parentQuestionnaireStack[parentQuestionnaireStack.length - 1].resumeFromPromptIndex 
              : null
          }
          partialAnswers={
            parentQuestionnaireStack.length > 0 && 
            parentQuestionnaireStack[parentQuestionnaireStack.length - 1]?.nodeId === currentQuestionnaireNode.id 
              ? parentQuestionnaireStack[parentQuestionnaireStack.length - 1].partialAnswers 
              : null
          }
        />
      )}

      {/* Template Library Modal */}
      {showTemplateLibrary && (
        <TemplateLibrary
          onApplyTemplate={handleApplyTemplate}
          onClose={() => setShowTemplateLibrary(false)}
        />
      )}

      {/* Questionnaire Overview Modal */}
      {showQuestionnaireOverview && overviewNode && (
        <QuestionnaireOverview
          node={overviewNode}
          diagram={currentDiagram}
          isVisible={showQuestionnaireOverview}
          onClose={() => {
            setShowQuestionnaireOverview(false);
            setOverviewNode(null);
          }}
          onEdit={handleQuestionnaireOverviewEdit}
        />
      )}

      {/* Vulnerability Analysis Panel */}
      {showVulnerabilityPanel && selectedVulnerability && (
        <VulnerabilityPanel
          vulnerability={selectedVulnerability}
          onClose={() => {
            setShowVulnerabilityPanel(false);
            setSelectedVulnerability(null);
          }}
          onMarkFixed={handleVulnerabilityFixed}
          userAnswers={(() => {
            // Get user answers from the parent node
            const parentNode = nodes.find(n => n.id === selectedVulnerability.parent_node_id);
            return parentNode?.data?.questionnaireResponses || {};
          })()}
          nodeSubtype={(() => {
            // Get node subtype from the parent node
            const parentNode = nodes.find(n => n.id === selectedVulnerability.parent_node_id);
            return parentNode?.data?.subtype || '';
          })()}
        />
      )}

      {/* Phase 2: Enhanced Vulnerability List - Now integrated into right panel */}

      {/* Vulnerability Filter Panel */}
      {showVulnerabilityFilter && (
        <div className="fixed top-20 left-4 z-40 w-80">
          <VulnerabilityFilter
            vulnerabilities={allVulnerabilities}
            onFilterChange={handleVulnerabilityFilterChange}
            onExportFiltered={handleExportFilteredVulnerabilities}
          />
        </div>
      )}

      {/* Vulnerability Legend Panel */}
      {showVulnerabilityLegend && (
        <div className="fixed top-20 right-4 z-40 w-80">
          <VulnerabilityLegend
            vulnerabilities={allVulnerabilities}
            onSeverityFilter={handleVulnerabilityLegendFilter}
          />
        </div>
      )}

      {/* Vulnerability Report Modal */}
      {showVulnerabilityReport && (
        <VulnerabilityReport
          vulnerabilities={filteredVulnerabilities.length > 0 ? filteredVulnerabilities : allVulnerabilities}
          onClose={() => setShowVulnerabilityReport(false)}
          diagramInfo={currentDiagram}
        />
      )}

      {/* Clear Vulnerabilities Confirmation Dialog */}
      {showClearConfirmation && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 max-w-md mx-4">
            <h3 className="text-lg font-semibold text-white mb-4">Clear All Vulnerabilities</h3>
            <p className="text-gray-300 mb-6">
              Are you sure you want to clear all {allVulnerabilities.length} vulnerabilities? This will remove all vulnerability nodes and analyses from the diagram.
            </p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowClearConfirmation(false)}
                className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 text-sm"
              >
                Cancel
              </button>
              <button
                onClick={confirmClearVulnerabilities}
                className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 text-sm"
              >
                Clear All
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Enhanced Questionnaire System - DISABLED: Using legacy system only */}
      {/*
      <QuestionnaireManager
        nodes={nodes}
        setNodes={setNodes}
        onNodeCreate={(newNode) => {
          setNodes(currentNodes => [...currentNodes, newNode]);
        }}
        onNodeUpdate={(updatedNode) => {
          setNodes(currentNodes => 
            currentNodes.map(node => 
              node.id === updatedNode.id ? updatedNode : node
            )
          );
        }}
        currentDiagram={currentDiagram}
        setDependencyState={setDependencyState}
        getDependencyState={getDependencyState}
        getIncompleteDependencies={getIncompleteDependencies}
      />
      */}

      {/* Canvas Synchronizer - Temporarily disabled to fix infinite loop */}
      {/* <CanvasSynchronizer
        nodes={nodes}
        setNodes={setNodes}
        edges={edges}
        setEdges={setEdges}
        onNodeUpdate={(updatedNode) => {
          console.log('Canvas sync: Node updated', updatedNode);
        }}
        onEdgeCreate={(newEdge) => {
          console.log('Canvas sync: Edge created', newEdge);
        }}
      /> */}
      
      {/* QW-3: Clear All Confirmation Modal */}
      {showClearAllConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 max-w-md">
            <h3 className="text-lg font-semibold text-white mb-4">Clear All Nodes and Edges?</h3>
            <p className="text-gray-300 mb-6">
              This will remove all nodes and edges from the canvas. This action cannot be undone.
            </p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={cancelClearAll}
                className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
              >
                Cancel
              </button>
              <button
                onClick={executeClearAll}
                className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
              >
                Clear All
              </button>
            </div>
          </div>
        </div>
      )}

      {/* UI Improvements Demo */}
      {showUIDemo && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-900 rounded-lg border border-gray-700 max-w-6xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-4 border-b border-gray-700">
              <h2 className="text-xl font-bold text-white">UI Simplification Demo</h2>
              <button
                onClick={() => setShowUIDemo(false)}
                className="text-gray-400 hover:text-white"
              >
                <X className="h-6 w-6" />
              </button>
            </div>
            <UIComparisonDemo />
          </div>
        </div>
      )}
    </div>
  );
}

function App() {
  return (
    <QuestionnaireProvider>
      <QuestionnaireConfirmationProvider>
        <ReactFlowProvider>
          <AppContent />
          <Toaster />
        </ReactFlowProvider>
      </QuestionnaireConfirmationProvider>
    </QuestionnaireProvider>
  );
}

export default App;