import React, { useState, useEffect, useCallback, memo } from 'react';
import { Monitor, Activity, Zap } from 'lucide-react';

/**
 * ReactFlowPerformanceMonitor - Performance monitoring component
 * Receives nodes and edges as props to avoid hook conflicts
 */
const ReactFlowPerformanceMonitor = memo(({ 
  showPerformanceMonitor = false,
  nodes = [],
  edges = [],
  onClose 
}) => {
  const [performanceData, setPerformanceData] = useState({
    nodeCount: 0,
    edgeCount: 0,
    renderTime: 0,
    memoryUsage: 'N/A',
    reRenderCount: 0,
    lastUpdate: new Date().toISOString()
  });

  // Use props instead of hooks to avoid conflicts

  // Performance tracking with React Flow v12 patterns
  const updatePerformanceMetrics = useCallback(() => {
    const startTime = performance.now();
    
    setPerformanceData(prev => {
      const newData = {
        nodeCount: nodes.length,
        edgeCount: edges.length,
        renderTime: Math.round(performance.now() - startTime),
        memoryUsage: performance.memory ? 
          `${Math.round(performance.memory.usedJSHeapSize / 1024 / 1024)}MB` : 
          'Not available',
        reRenderCount: prev.reRenderCount + 1,
        lastUpdate: new Date().toISOString(),
        
        // Advanced metrics
        nodeTypes: [...new Set(nodes.map(n => n.type || 'default'))],
        edgeTypes: [...new Set(edges.map(e => e.type || 'default'))],
        connectionDensity: nodes.length > 0 ? (edges.length / nodes.length).toFixed(2) : 0,
        
        // Performance indicators
        isHighLoad: nodes.length > 100 || edges.length > 200,
        isOptimal: nodes.length <= 50 && edges.length <= 100,
        
        // Recommendations
        recommendations: []
      };
      
      // Generate performance recommendations
      if (newData.nodeCount > 100) {
        newData.recommendations.push('Consider using virtualization for large node counts');
      }
      if (newData.edgeCount > 200) {
        newData.recommendations.push('Consider edge clustering for better performance');
      }
      if (newData.reRenderCount > 10 && prev.reRenderCount > 0) {
        newData.recommendations.push('High re-render count detected - check memoization');
      }
      
      return newData;
    });
  }, [nodes, edges]);

  // Update performance metrics when nodes or edges change
  useEffect(() => {
    updatePerformanceMetrics();
  }, [nodes.length, edges.length, updatePerformanceMetrics]);

  // Auto-update performance metrics every 5 seconds
  useEffect(() => {
    if (!showPerformanceMonitor) return;
    
    const interval = setInterval(updatePerformanceMetrics, 5000);
    return () => clearInterval(interval);
  }, [showPerformanceMonitor, updatePerformanceMetrics]);

  if (!showPerformanceMonitor) return null;

  return (
    <div className="fixed top-4 right-80 bg-gray-800 border border-gray-600 rounded-lg p-4 shadow-lg z-50 min-w-80">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Monitor className="w-5 h-5 text-blue-400" />
          <h3 className="text-sm font-semibold text-white">React Flow Performance</h3>
        </div>
        <button 
          onClick={onClose}
          className="text-gray-400 hover:text-white transition-colors"
        >
          ×
        </button>
      </div>
      
      {/* Core Metrics */}
      <div className="grid grid-cols-2 gap-3 mb-3">
        <div className="bg-gray-700 rounded p-2">
          <div className="text-xs text-gray-300">Nodes</div>
          <div className="text-lg font-bold text-white">{performanceData.nodeCount}</div>
        </div>
        <div className="bg-gray-700 rounded p-2">
          <div className="text-xs text-gray-300">Edges</div>
          <div className="text-lg font-bold text-white">{performanceData.edgeCount}</div>
        </div>
        <div className="bg-gray-700 rounded p-2">
          <div className="text-xs text-gray-300">Render Time</div>
          <div className="text-lg font-bold text-white">{performanceData.renderTime}ms</div>
        </div>
        <div className="bg-gray-700 rounded p-2">
          <div className="text-xs text-gray-300">Memory</div>
          <div className="text-lg font-bold text-white">{performanceData.memoryUsage}</div>
        </div>
      </div>
      
      {/* Performance Status */}
      <div className="mb-3">
        <div className="flex items-center gap-2 mb-1">
          <Activity className="w-4 h-4" />
          <span className="text-xs text-gray-300">Performance Status</span>
        </div>
        <div className={`text-sm font-medium ${
          performanceData.isOptimal ? 'text-green-400' :
          performanceData.isHighLoad ? 'text-red-400' : 'text-yellow-400'
        }`}>
          {performanceData.isOptimal ? '✅ Optimal' :
           performanceData.isHighLoad ? '⚠️ High Load' : '🔶 Moderate'}
        </div>
      </div>
      
      {/* Advanced Metrics */}
      <div className="text-xs text-gray-300 space-y-1 mb-3">
        <div>Connection Density: {performanceData.connectionDensity}</div>
        <div>Re-renders: {performanceData.reRenderCount}</div>
        <div>Node Types: {performanceData.nodeTypes?.length || 0}</div>
        <div>Edge Types: {performanceData.edgeTypes?.length || 0}</div>
      </div>
      
      {/* Recommendations */}
      {performanceData.recommendations && performanceData.recommendations.length > 0 && (
        <div className="border-t border-gray-600 pt-3">
          <div className="flex items-center gap-2 mb-2">
            <Zap className="w-4 h-4 text-yellow-400" />
            <span className="text-xs text-gray-300">Recommendations</span>
          </div>
          <div className="space-y-1">
            {performanceData.recommendations.map((rec, index) => (
              <div key={index} className="text-xs text-yellow-300 leading-tight">
                • {rec}
              </div>
            ))}
          </div>
        </div>
      )}
      
      <div className="text-xs text-gray-500 mt-3">
        Last updated: {new Date(performanceData.lastUpdate).toLocaleTimeString()}
      </div>
    </div>
  );
});

ReactFlowPerformanceMonitor.displayName = 'ReactFlowPerformanceMonitor';

export default ReactFlowPerformanceMonitor;