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
import CanvasSynchronizer from './components/CanvasSynchronizer';
import VulnerabilityNode from './components/VulnerabilityNode';
import VulnerabilityPanel from './components/VulnerabilityPanel';
import VulnerabilityEdge from './components/VulnerabilityEdge';
import VulnerabilityFilter from './components/VulnerabilityFilter';
import VulnerabilityLegend from './components/VulnerabilityLegend';
import VulnerabilityReport from './components/VulnerabilityReport';
import AdvancedLayoutControls from './components/AdvancedLayoutControls';
import NodeCreationModal from './components/NodeCreationModal';
import MainLayout from './components/layout/MainLayout';
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
  Plus
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
  const [selectedNode, setSelectedNode] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [diagrams, setDiagrams] = useState([]);
  const [currentDiagram, setCurrentDiagram] = useState(null);
  const [simulationResult, setSimulationResult] = useState(null);
  const [highlightedPaths, setHighlightedPaths] = useState([]);
  const [viewMode, setViewMode] = useState('modeling');
  
  // UI State
  const [showTemplateLibrary, setShowTemplateLibrary] = useState(false);
  const [showThreatModelingWizard, setShowThreatModelingWizard] = useState(false);
  const [showCoreLoopDashboard, setShowCoreLoopDashboard] = useState(false);
  const [showAdvancedControls, setShowAdvancedControls] = useState(false);
  const [showNodeCreationModal, setShowNodeCreationModal] = useState(false);
  const [showConnectionLegend, setShowConnectionLegend] = useState(true);
  const [showPerformancePanel, setShowPerformancePanel] = useState(false);
  const [showMiniMap, setShowMiniMap] = useState(true);
  
  // Vulnerability state
  const [showVulnerabilityFilter, setShowVulnerabilityFilter] = useState(false);
  const [showVulnerabilityLegend, setShowVulnerabilityLegend] = useState(false);
  const [showVulnerabilityReport, setShowVulnerabilityReport] = useState(false);
  const [selectedVulnerability, setSelectedVulnerability] = useState(null);
  const [vulnerabilityAnalyses, setVulnerabilityAnalyses] = useState({});
  const [allVulnerabilities, setAllVulnerabilities] = useState([]);
  const [autoVulnerabilityAnalysis, setAutoVulnerabilityAnalysis] = useState(false);

  // Questionnaire state
  const [showSecurityQuestionnaire, setShowSecurityQuestionnaire] = useState(false);
  const [currentQuestionnaireNode, setCurrentQuestionnaireNode] = useState(null);
  const [showQuestionnaireOverview, setShowQuestionnaireOverview] = useState(false);
  const [nodeBranches, setNodeBranches] = useState({});
  const [parentQuestionnaireState, setParentQuestionnaireState] = useState(null);
  const [dependencyStates, setDependencyStates] = useState({});

  // Undo/Redo state
  const [undoStack, setUndoStack] = useState([]);
  const [redoStack, setRedoStack] = useState([]);

  // Performance monitoring
  const [performance, setPerformance] = useState({
    nodeCount: 0,
    renderTime: 0,
    edgeCount: 0
  });

  const { fitView, zoomIn, zoomOut, getZoom } = useReactFlow();

  // Load diagrams on mount
  useEffect(() => {
    loadDiagrams();
  }, []);

  const loadDiagrams = async () => {
    try {
      const diagramsData = await getDiagrams();
      setDiagrams(diagramsData);
    } catch (error) {
      console.error('Failed to load diagrams:', error);
    }
  };

  // Performance monitoring
  useEffect(() => {
    const startTime = performance.now();
    const timeoutId = setTimeout(() => {
      const endTime = performance.now();
      setPerformance({
        nodeCount: nodes.length,
        edgeCount: edges.length,
        renderTime: Math.round(endTime - startTime)
      });
    }, 100);
    
    return () => clearTimeout(timeoutId);
  }, [nodes, edges]);

  // Save state for undo/redo
  const saveStateToUndoStack = useCallback(() => {
    const currentState = {
      nodes: nodes,
      edges: edges,
      timestamp: Date.now()
    };
    
    setUndoStack(prev => [...prev.slice(-9), currentState]); // Keep last 10 states
    setRedoStack([]); // Clear redo stack when new action is performed
  }, [nodes, edges]);

  // Undo/Redo handlers
  const handleUndo = useCallback(() => {
    if (undoStack.length === 0) return;
    
    const previousState = undoStack[undoStack.length - 1];
    const currentState = { nodes, edges, timestamp: Date.now() };
    
    setRedoStack(prev => [...prev, currentState]);
    setUndoStack(prev => prev.slice(0, -1));
    
    setNodes(previousState.nodes);
    setEdges(previousState.edges);
  }, [undoStack, nodes, edges, setNodes, setEdges]);

  const handleRedo = useCallback(() => {
    if (redoStack.length === 0) return;
    
    const nextState = redoStack[redoStack.length - 1];
    const currentState = { nodes, edges, timestamp: Date.now() };
    
    setUndoStack(prev => [...prev, currentState]);
    setRedoStack(prev => prev.slice(0, -1));
    
    setNodes(nextState.nodes);
    setEdges(nextState.edges);
  }, [redoStack, nodes, edges, setNodes, setEdges]);

  // Node creation from modal
  const handleCreateNodeFromModal = useCallback((nodeType) => {
    const newNodeId = `node_${Date.now()}`;
    const newNode = {
      id: newNodeId,
      type: 'custom',
      position: { x: 300 + Math.random() * 200, y: 200 + Math.random() * 200 },
      data: {
        ...nodeType,
        label: nodeType.name,
        id: newNodeId,
        intelligentNode: true,
        questionnaire_responses: {}
      }
    };
    
    setNodes((nds) => [...nds, newNode]);
    saveStateToUndoStack();
    setShowNodeCreationModal(false);
  }, [setNodes, saveStateToUndoStack]);

  // Handle node selection
  const onNodeClick = useCallback((event, node) => {
    setSelectedNode(node);
  }, []);

  // Handle connections
  const onConnect = useCallback((params) => {
    const newEdge = {
      ...params,
      id: `edge_${Date.now()}`,
      type: 'default',
      markerEnd: {
        type: MarkerType.ArrowClosed,
        width: 20,
        height: 20,
        color: '#6b7280',
      },
      style: { stroke: '#6b7280', strokeWidth: 2 }
    };
    
    setEdges((eds) => addEdge(newEdge, eds));
    saveStateToUndoStack();
  }, [setEdges, saveStateToUndoStack]);

  // Drag and drop handlers
  const onDragOver = useCallback((event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback((event) => {
    event.preventDefault();
    const reactFlowBounds = event.currentTarget.getBoundingClientRect();
    const nodeData = JSON.parse(event.dataTransfer.getData('application/reactflow'));
    
    const position = {
      x: event.clientX - reactFlowBounds.left - nodeData.offsetX,
      y: event.clientY - reactFlowBounds.top - nodeData.offsetY,
    };

    const newNode = {
      id: `node_${Date.now()}`,
      type: 'custom',
      position,
      data: {
        ...nodeData,
        id: `node_${Date.now()}`,
        intelligentNode: true,
        questionnaire_responses: {}
      }
    };

    setNodes((nds) => [...nds, newNode]);
    saveStateToUndoStack();
  }, [setNodes, saveStateToUndoStack]);

  // Diagram management
  const handleNewDiagram = useCallback(() => {
    setNodes([]);
    setEdges([]);
    setCurrentDiagram(null);
    setSelectedNode(null);
    setSimulationResult(null);
    setHighlightedPaths([]);
    setUndoStack([]);
    setRedoStack([]);
    setAllVulnerabilities([]);
    setVulnerabilityAnalyses({});
  }, [setNodes, setEdges]);

  const handleSaveDiagram = useCallback(async () => {
    if (isLoading) return;
    
    setIsLoading(true);
    try {
      const diagramData = {
        title: currentDiagram?.title || `Security Model ${new Date().toLocaleDateString()}`,
        nodes: nodes,
        edges: edges,
        metadata: {
          viewMode,
          performance,
          vulnerabilityCount: allVulnerabilities.length
        }
      };

      let savedDiagram;
      if (currentDiagram?.id) {
        savedDiagram = await updateDiagram(currentDiagram.id, diagramData);
      } else {
        savedDiagram = await createDiagram(diagramData);
      }

      setCurrentDiagram(savedDiagram);
      await loadDiagrams();
    } catch (error) {
      console.error('Failed to save diagram:', error);
    } finally {
      setIsLoading(false);
    }
  }, [currentDiagram, nodes, edges, viewMode, performance, allVulnerabilities, isLoading]);

  const handleLoadDiagram = useCallback(async (diagram) => {
    setCurrentDiagram(diagram);
    setNodes(diagram.nodes || []);
    setEdges(diagram.edges || []);
    setSelectedNode(null);
    setSimulationResult(null);
    setHighlightedPaths([]);
    setUndoStack([]);
    setRedoStack([]);
    
    // Restore view mode if available
    if (diagram.metadata?.viewMode) {
      setViewMode(diagram.metadata.viewMode);
    }
  }, [setNodes, setEdges]);

  // Simulation
  const handleRunSimulation = useCallback(async () => {
    if (isLoading || nodes.length === 0) return;

    setIsLoading(true);
    try {
      const simulationData = {
        nodes: nodes,
        edges: edges
      };

      const result = await simulateAttackPaths(simulationData);
      setSimulationResult(result);
      setViewMode('analysis');
      
      // Highlight attack paths
      if (result.attack_paths && result.attack_paths.length > 0) {
        highlightAttackPaths(result.attack_paths);
      }
    } catch (error) {
      console.error('Simulation failed:', error);
    } finally {
      setIsLoading(false);
    }
  }, [nodes, edges, isLoading]);

  // Attack path highlighting
  const highlightAttackPaths = useCallback((attackPaths) => {
    // Highlight edges in attack paths
    setEdges((eds) =>
      eds.map((edge) => {
        const isInAttackPath = attackPaths.some(path =>
          path.some(step => step.connection_id === edge.id)
        );

        return {
          ...edge,
          style: {
            ...edge.style,
            stroke: isInAttackPath ? '#ef4444' : '#6b7280',
            strokeWidth: isInAttackPath ? 3 : 1,
            strokeDasharray: isInAttackPath ? '8,4' : 'none',
          },
          animated: isInAttackPath,
          markerEnd: {
            type: MarkerType.ArrowClosed,
            width: 20,
            height: 20,
            color: isInAttackPath ? '#ef4444' : '#6b7280',
          },
          data: {
            ...edge.data,
            isHighlighted: isInAttackPath
          }
        };
      })
    );

    // Highlight nodes in attack paths
    setNodes((nds) =>
      nds.map((node) => {
        const isInAttackPath = attackPaths.some(path =>
          path.some(step => step.node_id === node.id)
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
  }, [setEdges, setNodes]);

  const clearAttackPathHighlighting = useCallback(() => {
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
  }, [setEdges, setNodes]);

  // Vulnerability analysis
  const analyzeAllNodeVulnerabilities = useCallback(async () => {
    if (isLoading) return;

    const nodesToAnalyze = nodes.filter(n => n.data?.questionnaireResponses && Object.keys(n.data.questionnaireResponses).length > 0);
    
    if (nodesToAnalyze.length === 0) {
      console.warn('No nodes with questionnaire responses found for vulnerability analysis');
      return;
    }

    setIsLoading(true);
    try {
      const vulnerabilities = [];
      const analyses = {};

      for (const node of nodesToAnalyze) {
        try {
          const analysis = await analyzeNodeVulnerabilities(node.id, {
            node_type: node.data.subtype,
            questionnaire_responses: node.data.questionnaireResponses,
            business_context: node.data.businessContext || {}
          });

          analyses[node.id] = analysis;
          
          if (analysis.vulnerabilities && analysis.vulnerabilities.length > 0) {
            vulnerabilities.push(...analysis.vulnerabilities);
          }
        } catch (error) {
          console.error(`Failed to analyze vulnerabilities for node ${node.id}:`, error);
        }
      }

      setVulnerabilityAnalyses(analyses);
      setAllVulnerabilities(vulnerabilities);

      // Create vulnerability nodes and edges
      if (vulnerabilities.length > 0) {
        const { vulnerabilityNodes, vulnerabilityEdges } = createVulnerabilityNodes(vulnerabilities, nodes);
        
        setNodes(prevNodes => [...prevNodes, ...vulnerabilityNodes]);
        setEdges(prevEdges => [...prevEdges, ...vulnerabilityEdges]);
      }

    } catch (error) {
      console.error('Vulnerability analysis failed:', error);
    } finally {
      setIsLoading(false);
    }
  }, [nodes, isLoading, setNodes, setEdges]);

  const clearAllVulnerabilities = useCallback(() => {
    // Remove vulnerability nodes and edges
    setNodes(prevNodes => prevNodes.filter(node => node.type !== 'vulnerability'));
    setEdges(prevEdges => prevEdges.filter(edge => edge.type !== 'vulnerability-edge'));
    
    // Clear vulnerability data
    setAllVulnerabilities([]);
    setVulnerabilityAnalyses({});
    setSelectedVulnerability(null);
  }, [setNodes, setEdges]);

  // Template and wizard handlers
  const handleApplyTemplate = useCallback(async (template) => {
    try {
      const result = await applyTemplateToCurrentDiagram(template.id, currentDiagram?.id);
      
      setNodes(result.nodes || []);
      setEdges(result.edges || []);
      setCurrentDiagram(result);
      
      setShowTemplateLibrary(false);
      await loadDiagrams();
      
      // Auto-fit view after template application
      setTimeout(() => {
        fitView({ padding: 0.1, duration: 600 });
      }, 100);
      
    } catch (error) {
      console.error('Failed to apply template:', error);
    }
  }, [currentDiagram, setNodes, setEdges, fitView]);

  // Auto-layout handler
  const handleAutoLayout = useCallback(async () => {
    if (isLoading || nodes.length === 0 || !currentDiagram?.id) return;

    setIsLoading(true);
    try {
      const result = await autoLayoutDiagram(currentDiagram.id);
      
      if (result.layout_positions) {
        setNodes(prevNodes => 
          prevNodes.map(node => ({
            ...node,
            position: result.layout_positions[node.id] || node.position
          }))
        );
      }
    } catch (error) {
      console.error('Auto-layout failed:', error);
    } finally {
      setIsLoading(false);
    }
  }, [currentDiagram, nodes, isLoading, setNodes]);

  // Questionnaire handlers
  const handleNodeBranchUpdate = useCallback((nodeId, branches) => {
    setNodeBranches(prev => ({
      ...prev,
      [nodeId]: branches
    }));
  }, []);

  const handleSecurityQuestionnaireComplete = useCallback((responses, businessContext) => {
    if (currentQuestionnaireNode) {
      setNodes(prevNodes =>
        prevNodes.map(node =>
          node.id === currentQuestionnaireNode.id
            ? {
                ...node,
                data: {
                  ...node.data,
                  questionnaireResponses: responses,
                  businessContext: businessContext,
                  isComplete: true
                }
              }
            : node
        )
      );

      // Auto-analyze vulnerabilities if enabled
      if (autoVulnerabilityAnalysis) {
        setTimeout(() => {
          analyzeAllNodeVulnerabilities();
        }, 500);
      }
    }

    setShowSecurityQuestionnaire(false);
    setCurrentQuestionnaireNode(null);
    setParentQuestionnaireState(null);
  }, [currentQuestionnaireNode, setNodes, autoVulnerabilityAnalysis, analyzeAllNodeVulnerabilities]);

  const handleSecurityQuestionnaireCancel = useCallback(() => {
    setShowSecurityQuestionnaire(false);
    setCurrentQuestionnaireNode(null);
    setParentQuestionnaireState(null);
  }, []);

  // Import/Export handlers
  const handleImportDiagram = useCallback((event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const diagramData = JSON.parse(e.target.result);
          setNodes(diagramData.nodes || []);
          setEdges(diagramData.edges || []);
          setCurrentDiagram(null);
          setSelectedNode(null);
          setSimulationResult(null);
          setHighlightedPaths([]);
        } catch (error) {
          console.error('Failed to import diagram:', error);
        }
      };
      reader.readAsText(file);
    }
  }, [setNodes, setEdges]);

  const handleExportDiagram = useCallback(() => {
    const diagramData = {
      title: currentDiagram?.title || 'Security Model Export',
      nodes: nodes,
      edges: edges,
      metadata: {
        exportDate: new Date().toISOString(),
        nodeCount: nodes.length,
        edgeCount: edges.length
      }
    };

    const dataStr = JSON.stringify(diagramData, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `security-model-${new Date().toISOString().split('T')[0]}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  }, [currentDiagram, nodes, edges]);

  // Double-tap handler for opening questionnaires
  useEffect(() => {
    const handleNodeDoubleTap = (event) => {
      const nodeId = event.detail.nodeId;
      const node = nodes.find(n => n.id === nodeId);
      
      if (node && node.data?.intelligentNode) {
        setCurrentQuestionnaireNode(node);
        setShowSecurityQuestionnaire(true);
      } else if (node) {
        setShowQuestionnaireOverview(true);
      }
    };

    window.addEventListener('nodeDoubleTap', handleNodeDoubleTap);
    return () => window.removeEventListener('nodeDoubleTap', handleNodeDoubleTap);
  }, [nodes, currentDiagram]);

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
            if (!event.shiftKey) {
              event.preventDefault();
              handleUndo();
            }
            break;
          case 'y':
            event.preventDefault();
            handleRedo();
            break;
        }
      } else if (event.key === 'Escape') {
        clearAttackPathHighlighting();
      } else if (event.key === 'Delete' || event.key === 'Backspace') {
        if (selectedNode) {
          setNodes(prevNodes => prevNodes.filter(node => node.id !== selectedNode.id));
          setEdges(prevEdges => prevEdges.filter(edge => 
            edge.source !== selectedNode.id && edge.target !== selectedNode.id
          ));
          setSelectedNode(null);
          saveStateToUndoStack();
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleSaveDiagram, handleNewDiagram, handleRunSimulation, handleUndo, handleRedo, clearAttackPathHighlighting, selectedNode, setNodes, setEdges, saveStateToUndoStack]);

  return (
    <MainLayout
      // Navigation props
      currentDiagram={currentDiagram}
      isLoading={isLoading}
      simulationResult={simulationResult}
      viewMode={viewMode}
      onViewModeChange={setViewMode}
      
      // Action handlers
      onNewDiagram={handleNewDiagram}
      onSave={handleSaveDiagram}
      onSimulate={handleRunSimulation}
      onShowTemplates={() => setShowTemplateLibrary(true)}
      onShowWizard={() => setShowThreatModelingWizard(true)}
      onShowCoreLoop={() => setShowCoreLoopDashboard(true)}
      onShowSettings={() => setShowAdvancedControls(!showAdvancedControls)}
      onImport={handleImportDiagram}
      onExport={handleExportDiagram}
      onAnalyzeVulnerabilities={analyzeAllNodeVulnerabilities}
      
      // Canvas and data
      nodes={nodes}
      edges={edges}
      setNodes={setNodes}
      setEdges={setEdges}
      selectedNode={selectedNode}
      diagrams={diagrams}
      onLoadDiagram={handleLoadDiagram}
      
      // Right panel props
      fitView={fitView}
      onRunSimulation={handleRunSimulation}
      onHighlightPath={highlightAttackPaths}
      onClearHighlights={clearAttackPathHighlighting}
      nodeBranches={nodeBranches}
      onNodeBranchUpdate={handleNodeBranchUpdate}
      
      // Vulnerability data
      allVulnerabilities={allVulnerabilities}
      
      // Performance data
      performance={performance}
      
      // Tour/onboarding
      onStartTour={() => setShowTemplateLibrary(true)}
    >
      {/* ReactFlow Canvas */}
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
        {showMiniMap && (
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
        )}
        <Background 
          variant="dots" 
          gap={20} 
          size={1} 
          color="#374151" 
        />
        
        {/* Floating Action Button for Adding Nodes */}
        <Panel position="bottom-right" className="m-4">
          <button
            onClick={() => setShowNodeCreationModal(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-full shadow-lg transition-colors flex items-center justify-center"
            title="Add Security Component"
          >
            <Plus className="h-6 w-6" />
          </button>
        </Panel>
        
        {/* Connection Types Legend */}
        {showConnectionLegend && (
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
                <div className="w-4 h-0.5 bg-green-500 border-dashed border-green-500"></div>
                <span className="text-green-300">File I/O</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-4 h-0.5 bg-yellow-500 border-dashed border-yellow-500"></div>
                <span className="text-yellow-300">Message</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-4 h-0.5 bg-red-500 border-dashed border-red-500"></div>
                <span className="text-red-300">Public Net</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-4 h-0.5 bg-cyan-500"></div>
                <span className="text-cyan-300">Cloud API</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-4 h-0.5 bg-red-600 border-dashed border-red-600"></div>
                <span className="text-red-400">Exploits</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-4 h-0.5 bg-green-600"></div>
                <span className="text-green-400">Controls</span>
              </div>
            </div>
          </Panel>
        )}
        
        {/* Risk Analysis Panel */}
        {simulationResult && (
          <Panel position="top-right" className="bg-gray-800 border border-gray-700 rounded-lg p-3 m-4 max-w-xs">
            <div className="text-white text-sm font-semibold mb-2 flex items-center">
              <AlertTriangle className="h-4 w-4 mr-2 text-orange-400" />
              Risk Assessment
            </div>
            <div className="text-xs space-y-1">
              <div className="flex justify-between">
                <span className="text-gray-400">Overall Risk:</span>
                <span className={`font-medium ${
                  simulationResult.overall_risk_level === 'Critical' ? 'text-red-400' :
                  simulationResult.overall_risk_level === 'High' ? 'text-orange-400' :
                  simulationResult.overall_risk_level === 'Medium' ? 'text-yellow-400' :
                  'text-green-400'
                }`}>{simulationResult.overall_risk_level}</span>
              </div>
              <div className="text-gray-400 text-xs">
                {simulationResult.attack_paths?.length || 0} attack paths found
              </div>
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
    </MainLayout>

    {/* Modals */}
    <>
      {/* Node Creation Modal */}
      <NodeCreationModal
        isVisible={showNodeCreationModal}
        onClose={() => setShowNodeCreationModal(false)}
        onCreateNode={handleCreateNodeFromModal}
      />

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
          onClose={() => setShowThreatModelingWizard(false)}
          onComplete={(result) => {
            setNodes(result.nodes || []);
            setEdges(result.edges || []);
            setShowThreatModelingWizard(false);
          }}
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
                <X className="w-6 h-6" />
              </button>
            </div>
            <div className="overflow-y-auto max-h-[calc(90vh-80px)]">
              <CoreLoopDashboard />
            </div>
          </div>
        </div>
      )}

      {/* Security Questionnaire */}
      {showSecurityQuestionnaire && currentQuestionnaireNode && (
        <SecurityQuestionnaire 
          nodeSubtype={currentQuestionnaireNode.subtype || currentQuestionnaireNode.data?.subtype} 
          onComplete={handleSecurityQuestionnaireComplete}
          onCancel={handleSecurityQuestionnaireCancel}
          existingValues={currentQuestionnaireNode.data?.questionnaireResponses || {}}
          isVisible={showSecurityQuestionnaire}
          sourceNode={currentQuestionnaireNode}
          currentNodes={nodes}
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

      {/* Vulnerability Components */}
      {showVulnerabilityFilter && (
        <VulnerabilityFilter
          vulnerabilities={allVulnerabilities}
          onFilterChange={(filtered) => {
            // Handle vulnerability filtering
          }}
          onClose={() => setShowVulnerabilityFilter(false)}
        />
      )}

      {showVulnerabilityLegend && (
        <VulnerabilityLegend
          vulnerabilities={allVulnerabilities}
          onClose={() => setShowVulnerabilityLegend(false)}
        />
      )}

      {showVulnerabilityReport && (
        <VulnerabilityReport
          vulnerabilities={allVulnerabilities}
          onClose={() => setShowVulnerabilityReport(false)}
        />
      )}

      {selectedVulnerability && (
        <VulnerabilityPanel
          vulnerability={selectedVulnerability}
          onClose={() => setSelectedVulnerability(null)}
          onRemediate={(vulnId, action) => {
            // Handle vulnerability remediation
          }}
        />
      )}
    </>
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