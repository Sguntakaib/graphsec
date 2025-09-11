import React, { useState } from 'react';
import { Play, Bug, AlertTriangle, CheckCircle, RefreshCw } from 'lucide-react';

const SimulationDebugger = ({ nodes, edges, onRunSimulation, simulationResult, isLoading }) => {
  const [debugInfo, setDebugInfo] = useState({});
  const [showDetails, setShowDetails] = useState(false);

  const analyzeGraphForSimulation = () => {
    const actors = nodes.filter(n => n.data?.type === 'Actor');
    const assets = nodes.filter(n => n.data?.type === 'Asset');
    const surfaces = nodes.filter(n => n.data?.type === 'Surface');
    const controls = nodes.filter(n => n.data?.type === 'Control');
    
    const hasConnections = edges.length > 0;
    const hasActorToAssetPath = actors.some(actor => 
      assets.some(asset => 
        edges.some(edge => 
          (edge.source === actor.id && edge.target === asset.id) ||
          edges.some(edge2 => 
            edge.source === actor.id && edge2.target === asset.id
          )
        )
      )
    );

    return {
      nodeStats: {
        total: nodes.length,
        actors: actors.length,
        assets: assets.length,
        surfaces: surfaces.length,
        controls: controls.length
      },
      edgeStats: {
        total: edges.length,
        hasConnections
      },
      simulationReady: {
        hasNodes: nodes.length > 0,
        hasEdges: edges.length > 0,
        hasActors: actors.length > 0,
        hasAssets: assets.length > 0,
        hasPaths: hasConnections && hasActorToAssetPath
      },
      actors,
      assets,
      surfaces,
      controls
    };
  };

  const analysis = analyzeGraphForSimulation();

  const getReadinessStatus = () => {
    const ready = analysis.simulationReady;
    if (!ready.hasNodes) return { status: 'error', message: 'No nodes in diagram' };
    if (!ready.hasActors) return { status: 'warning', message: 'No threat actors defined' };
    if (!ready.hasAssets) return { status: 'warning', message: 'No assets to protect' };
    if (!ready.hasEdges) return { status: 'warning', message: 'No connections between nodes' };
    if (!ready.hasPaths) return { status: 'info', message: 'Limited attack paths possible' };
    return { status: 'success', message: 'Ready for simulation' };
  };

  const status = getReadinessStatus();

  const handleTestSimulation = async () => {
    setDebugInfo({ testing: true });
    try {
      await onRunSimulation();
      setDebugInfo({ success: true, timestamp: new Date().toISOString() });
    } catch (error) {
      setDebugInfo({ 
        error: true, 
        errorMessage: error.message,
        timestamp: new Date().toISOString()
      });
    }
  };

  const StatusIcon = () => {
    switch (status.status) {
      case 'success': return <CheckCircle className="h-5 w-5 text-green-400" />;
      case 'warning': return <AlertTriangle className="h-5 w-5 text-yellow-400" />;
      case 'error': return <Bug className="h-5 w-5 text-red-400" />;
      default: return <AlertTriangle className="h-5 w-5 text-gray-400" />;
    }
  };

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg p-4 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Bug className="h-5 w-5 text-blue-400" />
          <span className="font-medium text-white">Simulation Diagnostics</span>
        </div>
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="text-gray-400 hover:text-white text-sm"
        >
          {showDetails ? 'Hide' : 'Show'} Details
        </button>
      </div>

      {/* Quick Status */}
      <div className="flex items-center space-x-3 p-3 bg-gray-700 rounded-lg">
        <StatusIcon />
        <div className="flex-1">
          <div className="text-white font-medium">{status.message}</div>
          <div className="text-gray-400 text-sm">
            {analysis.nodeStats.total} nodes, {analysis.edgeStats.total} connections
          </div>
        </div>
        {status.status === 'success' && (
          <button
            onClick={handleTestSimulation}
            disabled={isLoading}
            className="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50 flex items-center space-x-2"
          >
            {isLoading ? (
              <RefreshCw className="h-4 w-4 animate-spin" />
            ) : (
              <Play className="h-4 w-4" />
            )}
            <span>Test</span>
          </button>
        )}
      </div>

      {showDetails && (
        <div className="space-y-3">
          {/* Node Breakdown */}
          <div className="bg-gray-700 rounded-lg p-3">
            <h4 className="text-white font-medium mb-2">Node Distribution</h4>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div className="flex justify-between">
                <span className="text-red-400">Actors:</span>
                <span className="text-white">{analysis.nodeStats.actors}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-green-400">Assets:</span>
                <span className="text-white">{analysis.nodeStats.assets}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-orange-400">Surfaces:</span>
                <span className="text-white">{analysis.nodeStats.surfaces}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-blue-400">Controls:</span>
                <span className="text-white">{analysis.nodeStats.controls}</span>
              </div>
            </div>
          </div>

          {/* Simulation Requirements */}
          <div className="bg-gray-700 rounded-lg p-3">
            <h4 className="text-white font-medium mb-2">Simulation Requirements</h4>
            <div className="space-y-1 text-sm">
              {Object.entries(analysis.simulationReady).map(([key, value]) => (
                <div key={key} className="flex items-center space-x-2">
                  {value ? (
                    <CheckCircle className="h-3 w-3 text-green-400" />
                  ) : (
                    <AlertTriangle className="h-3 w-3 text-red-400" />
                  )}
                  <span className="text-gray-300 capitalize">
                    {key.replace(/([A-Z])/g, ' $1').toLowerCase()}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Current Result Status */}
          {simulationResult && (
            <div className="bg-gray-700 rounded-lg p-3">
              <h4 className="text-white font-medium mb-2">Last Simulation Result</h4>
              <div className="text-sm space-y-1">
                <div className="flex justify-between">
                  <span className="text-gray-400">Risk Level:</span>
                  <span className={`font-medium ${
                    simulationResult.overall_risk_level === 'Critical' ? 'text-red-400' :
                    simulationResult.overall_risk_level === 'High' ? 'text-orange-400' :
                    simulationResult.overall_risk_level === 'Medium' ? 'text-yellow-400' :
                    'text-green-400'
                  }`}>
                    {simulationResult.overall_risk_level} ({simulationResult.risk_score}/10)
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Attack Paths:</span>
                  <span className="text-white">{simulationResult.attack_paths?.length || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">MITRE Techniques:</span>
                  <span className="text-white">{simulationResult.mitre_techniques?.length || 0}</span>
                </div>
              </div>
            </div>
          )}

          {/* Debug Info */}
          {debugInfo.error && (
            <div className="bg-red-900 border border-red-600 rounded-lg p-3">
              <div className="text-red-400 font-medium">Simulation Error</div>
              <div className="text-red-300 text-sm mt-1">{debugInfo.errorMessage}</div>
              <div className="text-red-400 text-xs mt-1">{debugInfo.timestamp}</div>
            </div>
          )}

          {debugInfo.success && (
            <div className="bg-green-900 border border-green-600 rounded-lg p-3">
              <div className="text-green-400 font-medium">Simulation Successful</div>
              <div className="text-green-300 text-sm">Check the Analysis tab for results</div>
              <div className="text-green-400 text-xs mt-1">{debugInfo.timestamp}</div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SimulationDebugger;