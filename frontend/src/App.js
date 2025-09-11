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
import { AdvancedNodeLibrary } from './components/AdvancedNodeLibrary';
import { PropertiesPanel } from './components/PropertiesPanel';
import { EnhancedSimulationPanel } from './components/EnhancedSimulationPanel';
import { TemplateLibrary } from './components/TemplateLibrary';
import { CustomNode } from './components/CustomNode';
import { getDiagrams, createDiagram, updateDiagram, simulateAttackPaths, autoLayoutDiagram, applyTemplateToCurrentDiagram } from './services/api';
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
  MoreVertical
} from 'lucide-react';

const nodeTypes = {
  custom: CustomNode,
};

const initialNodes = [];
const initialEdges = [];

function AppContent() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
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

  // Track zoom level changes
  const onMoveEnd = useCallback((event, viewport) => {
    setZoomLevel(Math.round(viewport.zoom * 100) / 100);
  }, []);

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

  const onConnect = useCallback(
    (params) => setEdges((eds) => addEdge(params, eds)),
    [setEdges],
  );

  const onNodeClick = useCallback((event, node) => {
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
    (event) => {
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

      setNodes((nds) => nds.concat(newNode));
    },
    [setNodes],
  );

  const onDragOver = useCallback((event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
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

  const handleAutoLayout = async () => {
    if (!currentDiagram) return;
    
    setIsLoading(true);
    try {
      const layoutData = await autoLayoutDiagram(currentDiagram.id);
      
      // Apply the new positions
      setNodes((nds) =>
        nds.map((node) => {
          const newPosition = layoutData.layout_positions[node.id];
          return newPosition
            ? { ...node, position: newPosition }
            : node;
        })
      );
      
      // Fit view to show all nodes
      setTimeout(() => fitView(), 100);
    } catch (error) {
      console.error('Failed to auto-layout diagram:', error);
    } finally {
      setIsLoading(false);
    }
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
                onClick={() => fitView({ padding: 0.1 })}
                className="px-3 py-1 bg-gray-600 text-white rounded hover:bg-gray-500 flex items-center space-x-2 text-sm"
              >
                <Maximize2 className="h-4 w-4" />
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
            defaultEdgeOptions={defaultEdgeOptions}
            className="bg-gray-900"
            fitView
            snapToGrid
            snapGrid={[20, 20]}
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
          {viewMode === 'modeling' && selectedNode && (
            <PropertiesPanel node={selectedNode} />
          )}
          {viewMode === 'analysis' && simulationResult && (
            <EnhancedSimulationPanel 
              result={simulationResult} 
              onHighlightPath={highlightAttackPaths}
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
    </div>
  );
}

function App() {
  return (
    <ReactFlowProvider>
      <AppContent />
    </ReactFlowProvider>
  );
}

export default App;