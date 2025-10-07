import React, { useCallback, useMemo } from 'react';
import { useReactFlow } from '@xyflow/react';

/**
 * ReactFlowCanvasManager - Modern React Flow v12 component for canvas operations
 * Utilizes new hooks and patterns for efficient canvas management
 */
const ReactFlowCanvasManager = ({
  nodes,
  edges,
  setNodes,
  setEdges,
  selectedNode,
  setSelectedNode,
  selectedEdge,
  setSelectedEdge
}) => {
  const { fitView, zoomIn, zoomOut, updateNodeData, updateEdgeData, getNode, getEdge } = useReactFlow();

  // Modern pattern: Memoized edge options for better performance
  const defaultEdgeOptions = useMemo(() => ({
    type: 'draggable',
    markerEnd: {
      type: 'arrowclosed',
      color: '#9CA3AF',
    },
    style: {
      strokeWidth: 2,
      stroke: '#9CA3AF',
    },
  }), []);

  // Modern pattern: Efficient node selection with data dependencies
  const selectNodeWithDependencies = useCallback((nodeId) => {
    const node = getNode(nodeId);
    if (!node) return;
    
    // Get connected edges using passed edges state
    const connectedEdges = edges.filter(edge => 
      edge.source === nodeId || edge.target === nodeId
    );
    
    const enhancedNode = {
      ...node,
      connectedEdges,
      connectionCount: connectedEdges.length,
      hasIncomingConnections: connectedEdges.some(edge => edge.target === nodeId),
      hasOutgoingConnections: connectedEdges.some(edge => edge.source === nodeId)
    };
    
    setSelectedNode(enhancedNode);
    console.log('🎯 Selected node with dependencies:', enhancedNode);
  }, [getNode, edges, setSelectedNode]);

  // Modern pattern: Efficient auto-fit with bounds calculation
  const autoFitNodes = useCallback(() => {
    if (nodes.length === 0) return;
    
    // Calculate bounds using passed nodes state
    const bounds = nodes.reduce((acc, node) => {
      const x = node.position.x;
      const y = node.position.y;
      const width = node.measured?.width || node.width || 200;
      const height = node.measured?.height || node.height || 100;
      
      return {
        minX: Math.min(acc.minX, x),
        minY: Math.min(acc.minY, y),
        maxX: Math.max(acc.maxX, x + width),
        maxY: Math.max(acc.maxY, y + height)
      };
    }, { minX: Infinity, minY: Infinity, maxX: -Infinity, maxY: -Infinity });
    
    // Enhanced fit view with React Flow v12 options
    fitView({ 
      padding: 0.1,
      includeHiddenNodes: false,
      minZoom: 0.2,
      maxZoom: 1.5,
      duration: 600,
      bounds
    });
    
    console.log('🔍 Auto-fit applied to', nodes.length, 'nodes');
  }, [nodes, fitView]);

  // Modern pattern: Batch node updates for better performance
  const batchUpdateNodes = useCallback((updates) => {
    // Use React Flow v12 updateNodeData for efficient updates
    Object.entries(updates).forEach(([nodeId, data]) => {
      updateNodeData(nodeId, data);
    });
    
    console.log('🔄 Batch updated', Object.keys(updates).length, 'nodes');
  }, [updateNodeData]);

  // Modern pattern: Advanced edge management
  const manageEdgeConnections = useCallback((nodeId) => {
    const connectedEdges = edges.filter(edge => 
      edge.source === nodeId || edge.target === nodeId
    );
    
    return {
      incoming: connectedEdges.filter(edge => edge.target === nodeId),
      outgoing: connectedEdges.filter(edge => edge.source === nodeId),
      total: connectedEdges.length,
      edgeTypes: [...new Set(connectedEdges.map(edge => edge.type || 'default'))],
      hasLoops: connectedEdges.some(edge => edge.source === edge.target)
    };
  }, [edges]);

  // Modern pattern: Smart node positioning
  const smartPositionNode = useCallback((newNode, referenceNodeId = null) => {
    let position = { x: 100, y: 100 };
    
    if (referenceNodeId && nodes.length > 0) {
      const refNode = nodes.find(n => n.id === referenceNodeId);
      if (refNode) {
        // Position relative to reference node
        position = {
          x: refNode.position.x + 200,
          y: refNode.position.y
        };
      } else {
        // Smart grid positioning
        const gridSize = 200;
        const cols = Math.ceil(Math.sqrt(nodes.length + 1));
        const row = Math.floor(nodes.length / cols);
        const col = nodes.length % cols;
        
        position = {
          x: col * gridSize + 100,
          y: row * gridSize + 100
        };
      }
    }
    
    return {
      ...newNode,
      position
    };
  }, [nodes]);

  // Modern pattern: Canvas statistics for performance monitoring
  const getCanvasStats = useCallback(() => {
    return {
      nodeCount: nodes.length,
      edgeCount: edges.length,
      nodeTypes: [...new Set(nodes.map(n => n.type || 'default'))],
      edgeTypes: [...new Set(edges.map(e => e.type || 'default'))],
      totalConnections: edges.length,
      isolatedNodes: nodes.filter(node => 
        !edges.some(edge => edge.source === node.id || edge.target === node.id)
      ).length,
      performance: {
        renderTime: performance.now(),
        memoryUsage: performance.memory ? {
          used: Math.round(performance.memory.usedJSHeapSize / 1024 / 1024) + 'MB',
          total: Math.round(performance.memory.totalJSHeapSize / 1024 / 1024) + 'MB'
        } : 'Not available'
      }
    };
  }, [nodes, edges]);

  return {
    // Canvas operations
    autoFitNodes,
    zoomIn,
    zoomOut,
    fitView,
    
    // Node operations
    selectNodeWithDependencies,
    batchUpdateNodes,
    smartPositionNode,
    
    // Edge operations
    manageEdgeConnections,
    defaultEdgeOptions,
    
    // Data and statistics
    getCanvasStats
  };
};

export default ReactFlowCanvasManager;