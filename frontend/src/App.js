import React, { useState, useCallback, useEffect, useMemo } from 'react';
import {
  ReactFlow,
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
import { CustomNode } from './components/CustomNode';
import { getDiagrams, createDiagram, updateDiagram, simulateAttackPaths, autoLayoutDiagram } from './services/api';
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
  Layers
} from 'lucide-react';

const nodeTypes = {
  custom: CustomNode,
};

const initialNodes = [];
const initialEdges = [];

function App() {
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
  
  const { fitView, zoomIn, zoomOut } = useReactFlow();

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
  }, []);

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
    } catch (error) {
      console.error('Failed to run simulation:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewDiagram = () => {
    setNodes([]);
    setEdges([]);
    setCurrentDiagram(null);
    setSimulationResult(null);
    setSelectedNode(null);
  };

  return (
    <div className="h-screen flex flex-col bg-gray-900">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Shield className="h-8 w-8 text-blue-400" />
            <h1 className="text-xl font-bold text-white">Security Modeling Platform</h1>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={handleNewDiagram}
              className="px-4 py-2 bg-gray-700 text-white rounded hover:bg-gray-600 flex items-center space-x-2"
            >
              <span>New</span>
            </button>
            <button
              onClick={handleSaveDiagram}
              disabled={isLoading}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 flex items-center space-x-2"
            >
              <Save className="h-4 w-4" />
              <span>{isLoading ? 'Saving...' : 'Save'}</span>
            </button>
            <button
              onClick={handleRunSimulation}
              disabled={isLoading || nodes.length === 0}
              className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50 flex items-center space-x-2"
            >
              <Play className="h-4 w-4" />
              <span>{isLoading ? 'Running...' : 'Simulate'}</span>
            </button>
          </div>
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Left Sidebar - Node Library */}
        <div className="w-80 bg-gray-800 border-r border-gray-700 overflow-y-auto">
          <SecurityNodeLibrary />
          
          {/* Diagram List */}
          <div className="p-4 border-t border-gray-700">
            <div className="flex items-center space-x-2 mb-4">
              <FolderOpen className="h-5 w-5 text-gray-400" />
              <h3 className="text-white font-medium">Saved Diagrams</h3>
            </div>
            <div className="space-y-2">
              {diagrams.map((diagram) => (
                <button
                  key={diagram.id}
                  onClick={() => handleLoadDiagram(diagram)}
                  className="w-full text-left p-3 bg-gray-700 rounded hover:bg-gray-600 text-white text-sm"
                >
                  <div className="font-medium">{diagram.title}</div>
                  <div className="text-gray-400 text-xs">
                    {diagram.nodes?.length || 0} nodes, {diagram.edges?.length || 0} edges
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
            className="bg-gray-900"
            fitView
          >
            <Controls className="bg-gray-800 border-gray-700" />
            <MiniMap 
              className="bg-gray-800 border-gray-700" 
              nodeColor="#4F46E5"
              maskColor="rgba(0, 0, 0, 0.6)"
            />
            <Background variant="dots" gap={20} size={1} color="#374151" />
            
            {currentDiagram && (
              <Panel position="top-left" className="bg-gray-800 border border-gray-700 rounded p-2">
                <div className="text-white text-sm font-medium">{currentDiagram.title}</div>
              </Panel>
            )}
          </ReactFlow>
        </div>

        {/* Right Sidebar - Properties and Simulation */}
        <div className="w-80 bg-gray-800 border-l border-gray-700 overflow-y-auto">
          {selectedNode && <PropertiesPanel node={selectedNode} />}
          {simulationResult && <SimulationPanel result={simulationResult} />}
        </div>
      </div>
    </div>
  );
}

export default App;