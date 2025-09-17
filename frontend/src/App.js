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
  MarkerType,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import './App.css';
import './styles/vulnerability.css';
import { AdvancedNodeLibrary } from './components/AdvancedNodeLibrary';
import { PropertiesPanel } from './components/PropertiesPanel';
import { EnhancedSimulationPanel } from './components/EnhancedSimulationPanel';
import { TemplateLibrary } from './components/TemplateLibrary';
import { CustomNode } from './components/CustomNode';
import SecurityQuestionnaire from './components/SecurityQuestionnaire';
import QuestionnaireOverview from './components/QuestionnaireOverview';
import SmartNodeConnector from './components/SmartNodeConnector';
import SimulationDebugger from './components/SimulationDebugger';
import NodeBranchVisualizer from './components/NodeBranchVisualizer';
import ThreatModelingWizard from './components/ThreatModelingWizard';
import CoreLoopDashboard from './components/CoreLoopDashboard';
import { QuestionnaireProvider, useQuestionnaire } from './contexts/QuestionnaireContext';
// import QuestionnaireManager from './components/QuestionnaireManager'; // DISABLED: Using legacy system only
import CanvasSynchronizer from './components/CanvasSynchronizer';
import VulnerabilityNode from './components/VulnerabilityNode';
import VulnerabilityPanel from './components/VulnerabilityPanel';
import VulnerabilityEdge from './components/VulnerabilityEdge';
import VulnerabilityFilter from './components/VulnerabilityFilter';
import VulnerabilityLegend from './components/VulnerabilityLegend';
import VulnerabilityReport from './components/VulnerabilityReport';
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
  X
} from 'lucide-react';

const nodeTypes = {
  custom: CustomNode,
  vulnerability: VulnerabilityNode,
};

const edgeTypes = {
  'vulnerability-edge': VulnerabilityEdge,
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

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  // Enhanced questionnaire system disabled - using legacy system only
  const [selectedNode, setSelectedNode] = useState(null);
  const [currentDiagram, setCurrentDiagram] = useState(null);
  const [simulationResult, setSimulationResult] = useState(null);
  const [diagrams, setDiagrams] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [viewMode, setViewMode] = useState('modeling'); // 'modeling' or 'analysis'
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
  const [showThreatModelingWizard, setShowThreatModelingWizard] = useState(false);
  const [showCoreLoopDashboard, setShowCoreLoopDashboard] = useState(false);
  const [currentQuestionnaireNode, setCurrentQuestionnaireNode] = useState(null);
  const [nodeBranches, setNodeBranches] = useState({}); // Store security branches for each node
  const [showQuestionnaireOverview, setShowQuestionnaireOverview] = useState(false);
  const [overviewNode, setOverviewNode] = useState(null);
  const [questionnaireQueue, setQuestionnaireQueue] = useState([]); // Queue for chained questionnaires
  const [currentQueueIndex, setCurrentQueueIndex] = useState(0);
  const [parentQuestionnaireState, setParentQuestionnaireState] = useState(null); // For resuming parent questionnaires
  const [dependencyStates, setDependencyStates] = useState({}); // Track dependency states per parent node: {parentNodeId: {API: 'COMPLETED', Database: 'CREATED'}}
  const [activeQuestionnaires, setActiveQuestionnaires] = useState(new Set()); // Track which questionnaires are currently active to prevent duplicates
  
  // Vulnerability system state
  const [vulnerabilityAnalyses, setVulnerabilityAnalyses] = useState({}); // Store vulnerability analyses by node ID
  const [selectedVulnerability, setSelectedVulnerability] = useState(null);
  const [showVulnerabilityPanel, setShowVulnerabilityPanel] = useState(false);
  const [showVulnerabilityFilter, setShowVulnerabilityFilter] = useState(false);
  const [showVulnerabilityLegend, setShowVulnerabilityLegend] = useState(false);
  const [showVulnerabilityReport, setShowVulnerabilityReport] = useState(false);
  const [vulnerabilityFilter, setVulnerabilityFilter] = useState({
    severity: [],
    category: [],
    nodeTypes: [],
    searchText: '',
    showFixed: false
  });
  const [filteredVulnerabilities, setFilteredVulnerabilities] = useState([]);
  const [autoVulnerabilityAnalysis, setAutoVulnerabilityAnalysis] = useState(false); // Disabled by default - require manual trigger after complete questionnaire

  // Track zoom level changes
  const onMoveEnd = useCallback((event, viewport) => {
    setZoomLevel(Math.round(viewport.zoom * 100) / 100);
  }, []);

  // Double-tap handler for nodes
  useEffect(() => {
    const handleNodeDoubleTap = (event) => {
      const { nodeId, nodeData } = event.detail;
      const node = nodes.find(n => n.id === nodeId);
      if (node && currentDiagram) {
        setOverviewNode(node);
        setShowQuestionnaireOverview(true);
      }
    };

    window.addEventListener('nodeDoubleTap', handleNodeDoubleTap);
    return () => window.removeEventListener('nodeDoubleTap', handleNodeDoubleTap);
  }, [nodes, currentDiagram]);

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
  }, [nodes, edges]);
  
  const { fitView, zoomIn, zoomOut } = useReactFlow();

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
  }, [nodes, fitView]);

  // Auto-check for out-of-bounds nodes when nodes change
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      handleFitAllNodes();
    }, 500); // Small delay to avoid constant checking
    
    return () => clearTimeout(timeoutId);
  }, [nodes, handleFitAllNodes]);

  // Save state for undo/redo
  const saveStateToUndoStack = useCallback(() => {
    const currentState = {
      nodes: [...nodes],
      edges: [...edges],
      timestamp: Date.now()
    };
    
    setUndoStack(prev => [...prev.slice(-19), currentState]); // Keep last 20 states
    setRedoStack([]); // Clear redo stack when new action is performed
  }, [nodes, edges]);

  // Smart Node Connector instance (initialized after saveStateToUndoStack)
  const smartNodeConnector = new SmartNodeConnector(setNodes, setEdges, saveStateToUndoStack);

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
  }, [undoStack, nodes, edges, setNodes, setEdges]);

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
  }, [redoStack, nodes, edges, setNodes, setEdges]);

  // Enhanced edge styles for attack paths
  const defaultEdgeOptions = useMemo(() => ({
    type: 'smoothstep',
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
    type: 'smoothstep',
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
        type: 'smoothstep',
        label: connectionInfo.label,
        style: connectionInfo.style,
        markerEnd: connectionInfo.markerEnd,
        labelStyle: connectionInfo.labelStyle,
        labelBgStyle: connectionInfo.labelBgStyle,
        labelShowBg: true,
        labelBgBorderRadius: 4,
        labelBgPadding: [4, 8],
      };
      
      setEdges((eds) => addEdge(newEdge, eds));
    },
    [nodes, setEdges],
  );

  const onNodeClick = useCallback((event, node) => {
    // Handle vulnerability node clicks
    if (node.type === 'vulnerability') {
      handleVulnerabilityNodeClick(node.data);
      return;
    }
    
    setSelectedNode(node);
    setContextMenu(null); // Close context menu when clicking node
  }, []);

  const onEdgeClick = (event, edge) => {
    setSelectedNode(null);
    setContextMenu(null);
  };

  const onPaneClick = () => {
    setSelectedNode(null);
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

      // Add the node first
      setNodes((nds) => nds.concat(newNode));

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
              data: { subtype: nodeData.subtype }
            });
            setShowSecurityQuestionnaire(true);
          }
        }
      } catch (error) {
        console.error('Error checking intelligent node support:', error);
        // Continue without intelligent features if API fails
      }
    },
    [setNodes],
  );

  const onDragOver = useCallback((event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  // Helper function to start legacy questionnaire
  const startLegacyQuestionnaire = useCallback(async (nodeId, nodeSubtype, parentNodeId = null) => {
    console.log('🎬 Starting legacy questionnaire:', { nodeId, nodeSubtype, parentNodeId });
    
    // Use legacy questionnaire system only
    console.log('🎯 Using legacy questionnaire system');
    
    setCurrentQuestionnaireNode({
      id: nodeId,
      subtype: nodeSubtype,
      data: { subtype: nodeSubtype }
    });
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
        position: node.position,
        data: {
          type: node.type,
          subtype: node.subtype,
          label: node.label,
          mitre_ids: node.mitre_ids || [],
          cve_ids: node.cve_ids || [],
          ...node.data
        }
      }));

      const loadedEdges = diagram.edges.map(edge => ({
        id: edge.id,
        source: edge.source,
        target: edge.target,
        type: edge.type || 'default',
        label: edge.label || '',
        data: edge.data || {}
      }));

      setNodes(loadedNodes);
      setEdges(loadedEdges);
      setSimulationResult(null);
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
          alert('Invalid diagram file format');
        }
      } catch (error) {
        console.error('Failed to import diagram:', error);
        alert('Failed to import diagram');
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
        label: edge.label || '',
        type: 'smoothstep',
        markerEnd: {
          type: 'arrowclosed',
          color: '#9CA3AF',
        },
        style: {
          strokeWidth: 2,
          stroke: '#9CA3AF',
        }
      }));
      
      // Add template nodes and edges to existing ones
      setNodes(prevNodes => [...prevNodes, ...templateNodes]);
      setEdges(prevEdges => [...prevEdges, ...templateEdges]);
      
      // Save state for undo functionality
      saveStateToUndoStack();
      
      alert(`Template "${template.name}" applied successfully! Added ${result.nodes_added} nodes and ${result.edges_added} edges.`);
      
    } catch (error) {
      console.error('Error applying template:', error);
      alert('Failed to apply template. Please try again.');
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

        // Update node data with security information
        setNodes(nds => nds.map(node => {
          if (node.id === currentQuestionnaireNode.id) {
            return {
              ...node,
              data: {
                ...node.data,
                securityBranches: updatedBranches,
                completionStatus: result.validation,
                recommendations: result.recommendations,
                intelligentNode: true,
                questionnaireResponses: result.answers,
                lastQuestionnaireUpdate: new Date().toISOString()
              }
            };
          }
          return node;
        }));

        // Mark dependency as COMPLETED if this node is a dependency of another node
        const completedNode = currentQuestionnaireNode;
        let parentNodeId = completedNode.data?.parentNode;
        const dependencyType = completedNode.subtype || completedNode.data?.subtype;
        
        // If parentNodeId is not in data, check if this is a dependent questionnaire scenario
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
          triggerDependentQuestionnaires: result.triggerDependentQuestionnaires,
          dependentNodesLength: result.dependentNodes?.length,
          dependentNodes: result.dependentNodes
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
        if (autoVulnerabilityAnalysis && ['WebApp', 'API', 'Database'].includes(currentQuestionnaireNode.subtype)) {
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
        
        alert(statusMessage);
      }

    } catch (error) {
      console.error('Error completing security questionnaire:', error);
    } finally {
      // Handle dependent questionnaires first
      if (result?.triggerDependentQuestionnaires && result?.dependentNodes?.length > 0) {
        console.log('🔄 Dependent questionnaires triggered, storing parent state for resumption');
        
        // Store parent questionnaire state for resumption after dependencies complete
        if (result.partialCompletion) {
          // This is a partial completion from dependency trigger - store parent state
          setParentQuestionnaireState({
            nodeId: currentQuestionnaireNode.id,
            nodeSubtype: currentQuestionnaireNode.subtype,
            resumeFromPromptIndex: result.currentPromptIndex, // Resume from the next question after dependency trigger
            partialAnswers: result.answers
          });
          console.log(`🔄 Stored parent questionnaire state for resumption at prompt ${result.currentPromptIndex}`);
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
      } else if (questionnaireQueue.length > 0 && parentQuestionnaireState) {
        // All dependencies complete, resume parent questionnaire
        console.log('🔄 All dependencies completed, resuming parent questionnaire:', parentQuestionnaireState);
        
        setCurrentQuestionnaireNode({
          id: parentQuestionnaireState.nodeId,
          subtype: parentQuestionnaireState.nodeSubtype,
          data: { subtype: parentQuestionnaireState.nodeSubtype }
        });
        
        // Clear the queue but keep parent state for the SecurityQuestionnaire component
        setQuestionnaireQueue([]);
        setCurrentQueueIndex(0);
        
        // The SecurityQuestionnaire component will use parentQuestionnaireState for resumption
        // Don't clear parentQuestionnaireState here - let it be cleared when parent completes
      } else {
        // All questionnaires completed - close everything
        console.log('✅ All questionnaires completed, closing modal');
        setShowSecurityQuestionnaire(false);
        setCurrentQuestionnaireNode(null);
        setQuestionnaireQueue([]);
        setCurrentQueueIndex(0);
        setParentQuestionnaireState(null);
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

  const allVulnerabilities = getAllVulnerabilities();

  // Handle vulnerability filter changes
  const handleVulnerabilityFilterChange = (filtered, filters) => {
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
  };

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
      if (key.startsWith('webapp_') || key.startsWith('api_') || key.startsWith('database_')) {
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
      const vulnerabilityNodes = createVulnerabilityNodes(analysisResult);
      const vulnerabilityEdges = createVulnerabilityEdges(analysisResult, nodeId);
      
      // Add vulnerability nodes and edges to the graph
      if (vulnerabilityNodes.length > 0) {
        setNodes(nds => [...nds, ...vulnerabilityNodes]);
        setEdges(eds => [...eds, ...vulnerabilityEdges]);
        
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
      ['WebApp', 'API', 'Database'].includes(node.data.subtype) &&
      node.data?.questionnaireResponses
    );
    
    if (securityNodes.length === 0) {
      alert('No nodes with questionnaire responses found for vulnerability analysis.');
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
        alert(message + 'No nodes are ready for vulnerability analysis. Complete questionnaires first.');
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
      alert(resultMessage);
      
    } catch (error) {
      console.error('Error in bulk vulnerability analysis:', error);
      alert('Error occurred during bulk vulnerability analysis.');
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

  const saveQuestionnaireResponses = async (nodeId, responses) => {
    if (!currentDiagram) return;
    
    try {
      await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/diagrams/${currentDiagram.id}/nodes/${nodeId}/questionnaire`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ responses })
        }
      );
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
    
    // For each dependent node type, check if it already exists (created by SmartNodeConnector)
    dependentNodeTypes.forEach((nodeType, index) => {
      // Check if SmartNodeConnector already created a node of this type linked to the source
      const existingNode = nodes.find(node => 
        node.data?.subtype === nodeType && 
        node.data?.autoGenerated === true &&
        edges.some(edge => edge.source === sourceNode.id && edge.target === node.id)
      );

      if (existingNode) {
        // Node already exists, just add it to the questionnaire queue
        console.log(`✅ Found existing ${nodeType} node created by SmartNodeConnector:`, existingNode.id);
        allDependentNodes.push(existingNode);
        // Set dependency state to CREATED since node exists but questionnaire not necessarily completed
        setDependencyState(sourceNode.id, nodeType, 'CREATED');
      } else {
        // Node doesn't exist, create it
        console.log(`🔄 Creating new ${nodeType} node via conditional dependency`);
        const newNode = {
          id: `${nodeType.toLowerCase()}-${sourceNode.id}-${Date.now()}-${index}`,
          type: 'custom',
          subtype: nodeType,  // Add subtype at top level for consistency
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
        // Set dependency state to CREATED since we're creating the node
        setDependencyState(sourceNode.id, nodeType, 'CREATED');

        // Create edge connecting parent to dependent node
        const newEdge = {
          id: `edge-${sourceNode.id}-${newNode.id}`,
          source: sourceNode.id,
          target: newNode.id,
          label: 'has_dependency',
          type: 'smoothstep',
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
    });

    // Add new nodes and edges to canvas if any were created
    if (newNodes.length > 0) {
      setNodes(prevNodes => [...prevNodes, ...newNodes]);
    }
    if (newEdges.length > 0) {
      setEdges(prevEdges => [...prevEdges, ...newEdges]);
    }

    // Queue questionnaires for ALL dependent nodes (existing + new)
    if (allDependentNodes.length > 0) {
      console.log(`🎯 Queueing questionnaires for ${allDependentNodes.length} dependent nodes:`, allDependentNodes.map(n => n.data.subtype));
      setQuestionnaireQueue(allDependentNodes);
      setCurrentQueueIndex(0);
      
      // Start questionnaire for the first dependent node using legacy system
      console.log(`🚀 Starting legacy questionnaire for dependent node:`, {
        nodeId: allDependentNodes[0].id,
        nodeSubtype: allDependentNodes[0].subtype || allDependentNodes[0].data?.subtype,
        parentId: currentQuestionnaireNode?.id
      });
      
      const firstNode = allDependentNodes[0];
      const nodeSubtype = firstNode.subtype || firstNode.data?.subtype;
      
      // Set the first questionnaire in the queue as current
      setCurrentQuestionnaireNode({
        id: firstNode.id,
        subtype: nodeSubtype,
        data: { subtype: nodeSubtype }
      });
      
      // Keep the modal open for the first dependent questionnaire
      setShowSecurityQuestionnaire(true);
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
    setQuestionnaireQueue([]);
    setCurrentQueueIndex(0);
    setParentQuestionnaireState(null); // Clear parent state on cancel
  };

  const handleQuestionnaireOverviewEdit = (node) => {
    setShowQuestionnaireOverview(false);
    
    // Use legacy questionnaire system
    const nodeSubtype = node.subtype || node.data?.subtype;
    startLegacyQuestionnaire(node.id, nodeSubtype);
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

  // Threat Modeling Wizard Handlers
  const handleThreatModelingWizardComplete = async (result) => {
    try {
      // Process wizard results and generate threat model
      console.log('Threat Modeling Wizard completed:', result);
      
      // Generate nodes and edges based on wizard results
      if (result.generatedNodes && result.generatedEdges) {
        setNodes(prevNodes => [...prevNodes, ...result.generatedNodes]);
        setEdges(prevEdges => [...prevEdges, ...result.generatedEdges]);
      }
      
      // If we have a current diagram, save the updates
      if (currentDiagram) {
        await handleSaveDiagram();
      }
      
      alert('Threat model generated successfully!');
    } catch (error) {
      console.error('Error processing wizard results:', error);
      alert('Threat model completed, but some features may need manual configuration.');
    } finally {
      setShowThreatModelingWizard(false);
    }
  };

  const handleThreatModelingWizardCancel = () => {
    setShowThreatModelingWizard(false);
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
        // Clear attack path highlighting or close context menu
        if (contextMenu) {
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

  return (
    <div className="h-screen flex flex-col bg-gray-900">
      {/* Enhanced Header */}
      <div className="bg-gray-800 border-b border-gray-700 p-4">
        <div className="flex items-center justify-between">
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
          
          {/* Action Buttons */}
          <div className="flex items-center space-x-2">
            <button
              onClick={handleNewDiagram}
              className="px-3 py-2 bg-gray-700 text-white rounded hover:bg-gray-600 flex items-center space-x-2 text-sm"
              title="New Diagram (Ctrl+N)"
            >
              <span>New</span>
            </button>
            
            <button
              onClick={() => setShowTemplateLibrary(true)}
              className="px-3 py-2 bg-blue-700 text-white rounded hover:bg-blue-600 flex items-center space-x-2 text-sm"
              title="Template Library - Apply pre-built security patterns"
            >
              <BookOpen className="h-4 w-4" />
              <span>Templates</span>
            </button>
            
            <button
              onClick={() => setShowThreatModelingWizard(true)}
              className="px-3 py-2 bg-purple-700 text-white rounded hover:bg-purple-600 flex items-center space-x-2 text-sm"
              title="Guided Threat Modeling - Step-by-step security assessment wizard"
            >
              <Shield className="h-4 w-4" />
              <span>Wizard</span>
            </button>
            
            <button
              onClick={() => setShowCoreLoopDashboard(true)}
              className="px-3 py-2 bg-gradient-to-r from-green-600 to-blue-600 text-white rounded hover:from-green-700 hover:to-blue-700 flex items-center space-x-2 text-sm"
              title="Core Loop Dashboard - Test Phase 1 Critical Endpoints"
            >
              <Zap className="h-4 w-4" />
              <span>Core Loop</span>
            </button>
            
            <button
              onClick={analyzeAllNodeVulnerabilities}
              disabled={isLoading || nodes.filter(n => n.data?.questionnaireResponses).length === 0}
              className="px-3 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50 flex items-center space-x-2 text-sm"
              title="Analyze Vulnerabilities - Requires COMPLETE questionnaires for all security questions (headers, logging, authentication, etc.)"
            >
              <AlertTriangle className="h-4 w-4" />
              <span>Vulnerabilities</span>
            </button>

            {/* Vulnerability System Controls */}
            {allVulnerabilities.length > 0 && (
              <>
                <button
                  onClick={() => setShowVulnerabilityFilter(!showVulnerabilityFilter)}
                  className={`px-3 py-2 rounded flex items-center space-x-2 text-sm transition-colors ${
                    showVulnerabilityFilter
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-600 text-white hover:bg-gray-700'
                  }`}
                  title="Filter Vulnerabilities"
                >
                  <Filter className="h-4 w-4" />
                  <span>Filter</span>
                </button>

                <button
                  onClick={() => setShowVulnerabilityLegend(!showVulnerabilityLegend)}
                  className={`px-3 py-2 rounded flex items-center space-x-2 text-sm transition-colors ${
                    showVulnerabilityLegend
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-600 text-white hover:bg-gray-700'
                  }`}
                  title="Security Dashboard"
                >
                  <BarChart3 className="h-4 w-4" />
                  <span>Dashboard</span>
                </button>

                <button
                  onClick={() => setShowVulnerabilityReport(true)}
                  className="px-3 py-2 bg-green-600 text-white rounded hover:bg-green-700 flex items-center space-x-2 text-sm"
                  title="Generate Vulnerability Report"
                >
                  <Download className="h-4 w-4" />
                  <span>Report</span>
                </button>

                <button
                  onClick={clearAllVulnerabilities}
                  className="px-3 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 flex items-center space-x-2 text-sm"
                  title="Clear All Vulnerabilities"
                >
                  <X className="h-4 w-4" />
                  <span>Clear</span>
                </button>
              </>
            )}
            
            <div className="relative">
              <input
                type="file"
                accept=".json"
                onChange={handleImportDiagram}
                className="absolute inset-0 opacity-0 cursor-pointer"
                id="import-file"
              />
              <label
                htmlFor="import-file"
                className="px-3 py-2 bg-gray-700 text-white rounded hover:bg-gray-600 flex items-center space-x-2 text-sm cursor-pointer"
                title="Import Diagram"
              >
                <Upload className="h-4 w-4" />
                <span>Import</span>
              </label>
            </div>
            
            <button
              onClick={handleExportDiagram}
              disabled={!currentDiagram}
              className="px-3 py-2 bg-gray-700 text-white rounded hover:bg-gray-600 disabled:opacity-50 flex items-center space-x-2 text-sm"
              title="Export Diagram"
            >
              <Download className="h-4 w-4" />
              <span>Export</span>
            </button>
            
            <button
              onClick={handleSaveDiagram}
              disabled={isLoading}
              className="px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 flex items-center space-x-2 text-sm"
              title="Save Diagram (Ctrl+S)"
            >
              <Save className="h-4 w-4" />
              <span>{isLoading ? 'Saving...' : 'Save'}</span>
            </button>
            
            <button
              onClick={handleRunSimulation}
              disabled={isLoading || nodes.length === 0}
              className="px-3 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50 flex items-center space-x-2 text-sm"
              title="Run Simulation (Ctrl+R)"
            >
              <Play className="h-4 w-4" />
              <span>{isLoading ? 'Analyzing...' : 'Simulate'}</span>
            </button>
            
            <button
              onClick={clearAttackPathHighlighting}
              disabled={highlightedPaths.length === 0}
              className="px-3 py-1 bg-orange-600 text-white rounded hover:bg-orange-700 disabled:opacity-50 flex items-center space-x-2 text-sm"
              title="Clear Attack Path Highlights (Esc)"
            >
              <EyeOff className="h-4 w-4" />
              <span>Clear Highlights</span>
            </button>
            
            <button
              onClick={() => setShowAdvancedControls(!showAdvancedControls)}
              className="px-3 py-2 bg-gray-700 text-white rounded hover:bg-gray-600 flex items-center space-x-2 text-sm"
              title="Advanced Controls"
            >
              <Settings className="h-4 w-4" />
            </button>
          </div>
        </div>
        
        {/* Advanced Controls Bar */}
        {showAdvancedControls && (
          <div className="mt-3 pt-3 border-t border-gray-700 space-y-3">
            {/* First Row - Layout & Navigation */}
            <div className="flex items-center space-x-3">
              <button
                onClick={handleAutoLayout}
                disabled={isLoading || nodes.length === 0}
                className="px-3 py-1 bg-purple-600 text-white rounded hover:bg-purple-700 disabled:opacity-50 flex items-center space-x-2 text-sm"
              >
                <Zap className="h-4 w-4" />
                <span>Auto-Layout</span>
              </button>
              
              <button
                onClick={handleFitAllNodes}
                disabled={nodes.length === 0}
                className="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50 flex items-center space-x-2 text-sm"
                title="Fit All Nodes to Canvas"
              >
                <Maximize2 className="h-4 w-4" />
                <span>Fit All</span>
              </button>
              
              <button
                onClick={() => fitView({ padding: 0.1, duration: 600 })}
                className="px-3 py-1 bg-gray-600 text-white rounded hover:bg-gray-500 flex items-center space-x-2 text-sm"
                title="Fit Current View"
              >
                <Eye className="h-4 w-4" />
                <span>Fit View</span>
              </button>

              <button
                onClick={handleUndo}
                disabled={undoStack.length === 0}
                className="px-3 py-1 bg-gray-600 text-white rounded hover:bg-gray-500 disabled:opacity-50 flex items-center space-x-2 text-sm"
                title="Undo (Ctrl+Z)"
              >
                <Undo className="h-4 w-4" />
                <span>Undo</span>
              </button>

              <button
                onClick={handleRedo}
                disabled={redoStack.length === 0}
                className="px-3 py-1 bg-gray-600 text-white rounded hover:bg-gray-500 disabled:opacity-50 flex items-center space-x-2 text-sm"
                title="Redo (Ctrl+Y)"
              >
                <Redo className="h-4 w-4" />
                <span>Redo</span>
              </button>

              <div className="flex items-center space-x-2 px-3 py-1 bg-gray-700 rounded text-sm text-gray-300">
                <ZoomIn className="h-4 w-4" />
                <span>{Math.round(zoomLevel * 100)}%</span>
              </div>
            </div>

            {/* Second Row - Grid & View Options */}
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setSnapToGrid(!snapToGrid)}
                className={`px-3 py-1 rounded flex items-center space-x-2 text-sm ${
                  snapToGrid 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-600 text-white hover:bg-gray-500'
                }`}
              >
                <Grid className="h-4 w-4" />
                <span>Snap {snapToGrid ? 'On' : 'Off'}</span>
              </button>

              <div className="flex items-center space-x-2">
                <span className="text-xs text-gray-400">Grid:</span>
                <select
                  value={gridSize}
                  onChange={(e) => setGridSize(Number(e.target.value))}
                  className="bg-gray-700 border border-gray-600 rounded text-white text-xs px-2 py-1"
                >
                  <option value={10}>10px</option>
                  <option value={20}>20px</option>
                  <option value={30}>30px</option>
                  <option value={50}>50px</option>
                </select>
              </div>

              <button
                onClick={() => setShowPerformanceMonitor(!showPerformanceMonitor)}
                className={`px-3 py-1 rounded flex items-center space-x-2 text-sm ${
                  showPerformanceMonitor
                    ? 'bg-green-600 text-white'
                    : 'bg-gray-600 text-white hover:bg-gray-500'
                }`}
              >
                <Monitor className="h-4 w-4" />
                <span>Performance</span>
              </button>

              <button
                onClick={() => setAutoVulnerabilityAnalysis(!autoVulnerabilityAnalysis)}
                className={`px-3 py-1 rounded flex items-center space-x-2 text-sm ${
                  autoVulnerabilityAnalysis
                    ? 'bg-red-600 text-white'
                    : 'bg-gray-600 text-white hover:bg-gray-500'
                }`}
                title={autoVulnerabilityAnalysis 
                  ? "Auto-vulnerability analysis enabled - will analyze after COMPLETE questionnaires only"
                  : "Auto-vulnerability analysis disabled - use 'Vulnerabilities' button after completing all security questions"
                }
              >
                <Shield className="h-4 w-4" />
                <span>Auto-Vuln {autoVulnerabilityAnalysis ? 'On' : 'Off'}</span>
              </button>

              <button
                onClick={clearAllVulnerabilities}
                disabled={Object.keys(vulnerabilityAnalyses).length === 0}
                className="px-3 py-1 bg-orange-600 text-white rounded hover:bg-orange-700 disabled:opacity-50 flex items-center space-x-2 text-sm"
                title="Clear all vulnerability nodes from the canvas"
              >
                <EyeOff className="h-4 w-4" />
                <span>Clear Vulns</span>
              </button>

              <button
                onClick={() => {
                  setNodes([]);
                  setEdges([]);
                  setSelectedNode(null);
                  setSimulationResult(null);
                  setHighlightedPaths([]);
                  setUndoStack([]);
                  setRedoStack([]);
                  clearAttackPathHighlighting();
                }}
                className="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 flex items-center space-x-2 text-sm"
              >
                <Trash2 className="h-4 w-4" />
                <span>Clear All</span>
              </button>
            </div>
          </div>
        )}
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Left Sidebar - Advanced Node Library */}
        <div className="w-80 bg-gray-800 border-r border-gray-700 overflow-y-auto">
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
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={onNodeClick}
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
        </div>

        {/* Right Sidebar - Properties and Analysis */}
        <div className="w-80 bg-gray-800 border-l border-gray-700 overflow-y-auto">
          {viewMode === 'modeling' && (
            <>
              {/* Simulation Debugger */}
              <SimulationDebugger
                nodes={nodes}
                edges={edges}
                onRunSimulation={handleRunSimulation}
                simulationResult={simulationResult}
                isLoading={isLoading}
              />
              
              {selectedNode && (
                <>
                  <PropertiesPanel node={selectedNode} />
                  
                  {/* Security Branches Visualizer */}
                  {selectedNode.data?.intelligentNode && (
                    <NodeBranchVisualizer
                      nodeId={selectedNode.id}
                      nodeSubtype={selectedNode.data.subtype}
                      branches={nodeBranches[selectedNode.id] || []}
                      onBranchUpdate={handleNodeBranchUpdate}
                      isExpanded={true}
                    />
                  )}
                </>
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
          {!selectedNode && !simulationResult && (
            <div className="p-4 text-center">
              <div className="text-gray-400 text-sm">
                {viewMode === 'modeling' 
                  ? 'Select a node to view properties'
                  : 'Run a simulation to see analysis results'
                }
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
          existingValues={{}}
          isVisible={showSecurityQuestionnaire}
          sourceNode={currentQuestionnaireNode}
          currentNodes={nodes}
          onCreateLinkedNodes={handleCreateLinkedNodes}
          getIncompleteDependencies={getIncompleteDependencies}
          resumeFromPromptIndex={
            parentQuestionnaireState?.nodeId === currentQuestionnaireNode.id 
              ? parentQuestionnaireState.resumeFromPromptIndex 
              : null
          }
          partialAnswers={
            parentQuestionnaireState?.nodeId === currentQuestionnaireNode.id 
              ? parentQuestionnaireState.partialAnswers 
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

      {/* Threat Modeling Wizard Modal */}
      {showThreatModelingWizard && (
        <ThreatModelingWizard
          isVisible={showThreatModelingWizard}
          onClose={handleThreatModelingWizardCancel}
          onComplete={handleThreatModelingWizardComplete}
          currentDiagram={currentDiagram}
          existingNodes={nodes}
          existingEdges={edges}
        />
      )}

      {/* Core Loop Dashboard Modal */}
      {showCoreLoopDashboard && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-7xl w-full max-h-[90vh] overflow-hidden">
            <div className="flex items-center justify-between p-4 border-b">
              <h2 className="text-xl font-semibold text-gray-900">Phase 1 Core Loop Dashboard</h2>
              <button
                onClick={() => setShowCoreLoopDashboard(false)}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="overflow-y-auto max-h-[calc(90vh-80px)]">
              <CoreLoopDashboard />
            </div>
          </div>
        </div>
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
    </div>
  );
}

function App() {
  return (
    <QuestionnaireProvider>
      <ReactFlowProvider>
        <AppContent />
      </ReactFlowProvider>
    </QuestionnaireProvider>
  );
}

export default App;