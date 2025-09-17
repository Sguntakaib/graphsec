import React from 'react';
import { 
  Activity, 
  Users, 
  Network, 
  AlertTriangle, 
  CheckCircle2, 
  Clock,
  Zap
} from 'lucide-react';

const BottomStatusBar = ({ 
  nodes,
  edges,
  simulationResult,
  isLoading,
  performance,
  selectedNode,
  allVulnerabilities = []
}) => {
  const getStatusColor = () => {
    if (isLoading) return 'text-yellow-400';
    if (simulationResult?.overall_risk_level === 'Critical') return 'text-red-400';
    if (simulationResult?.overall_risk_level === 'High') return 'text-orange-400';
    if (simulationResult?.overall_risk_level === 'Medium') return 'text-yellow-400';
    return 'text-green-400';
  };

  const getStatusMessage = () => {
    if (isLoading) return 'Processing analysis...';
    if (simulationResult) {
      return `Risk Level: ${simulationResult.overall_risk_level} (${simulationResult.attack_paths?.length || 0} attack paths)`;
    }
    if (nodes.length === 0) return 'Ready to start modeling';
    return 'Model ready for analysis';
  };

  const vulnerabilityStats = {
    critical: allVulnerabilities.filter(v => v.severity === 'Critical').length,
    high: allVulnerabilities.filter(v => v.severity === 'High').length,
    medium: allVulnerabilities.filter(v => v.severity === 'Medium').length,
    low: allVulnerabilities.filter(v => v.severity === 'Low').length
  };

  const totalVulns = Object.values(vulnerabilityStats).reduce((a, b) => a + b, 0);

  return (
    <div className="bg-gray-800 border-t border-gray-700 px-6 py-3">
      <div className="flex items-center justify-between">
        {/* Left Side - Model Stats */}
        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-2 text-sm">
            <Network className="h-4 w-4 text-blue-400" />
            <span className="text-gray-400">Nodes:</span>
            <span className="text-white font-medium">{nodes.length}</span>
          </div>
          
          <div className="flex items-center space-x-2 text-sm">
            <Activity className="h-4 w-4 text-green-400" />
            <span className="text-gray-400">Connections:</span>
            <span className="text-white font-medium">{edges.length}</span>
          </div>
          
          {selectedNode && (
            <div className="flex items-center space-x-2 text-sm">
              <Users className="h-4 w-4 text-purple-400" />
              <span className="text-gray-400">Selected:</span>
              <span className="text-white font-medium">
                {selectedNode.data?.label || selectedNode.data?.subtype || 'Unknown'}
              </span>
            </div>
          )}
        </div>

        {/* Center - Status Message */}
        <div className="flex items-center space-x-3">
          {isLoading ? (
            <div className="flex items-center space-x-2">
              <div className="animate-spin h-4 w-4 border-2 border-yellow-400 border-t-transparent rounded-full"></div>
              <span className="text-yellow-400 text-sm font-medium">{getStatusMessage()}</span>
            </div>
          ) : (
            <div className="flex items-center space-x-2">
              {simulationResult ? (
                <AlertTriangle className={`h-4 w-4 ${getStatusColor()}`} />
              ) : (
                <CheckCircle2 className="h-4 w-4 text-green-400" />
              )}
              <span className={`text-sm font-medium ${getStatusColor()}`}>
                {getStatusMessage()}
              </span>
            </div>
          )}
        </div>

        {/* Right Side - Performance & Vulnerability Stats */}
        <div className="flex items-center space-x-6">
          {/* Vulnerability Summary */}
          {totalVulns > 0 && (
            <div className="flex items-center space-x-4">
              {vulnerabilityStats.critical > 0 && (
                <div className="flex items-center space-x-1 text-sm">
                  <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                  <span className="text-red-400 font-medium">{vulnerabilityStats.critical}</span>
                </div>
              )}
              {vulnerabilityStats.high > 0 && (
                <div className="flex items-center space-x-1 text-sm">
                  <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
                  <span className="text-orange-400 font-medium">{vulnerabilityStats.high}</span>
                </div>
              )}
              {vulnerabilityStats.medium > 0 && (
                <div className="flex items-center space-x-1 text-sm">
                  <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                  <span className="text-yellow-400 font-medium">{vulnerabilityStats.medium}</span>
                </div>
              )}
              {vulnerabilityStats.low > 0 && (
                <div className="flex items-center space-x-1 text-sm">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-green-400 font-medium">{vulnerabilityStats.low}</span>
                </div>
              )}
            </div>
          )}

          {/* Performance Indicator */}
          <div className="flex items-center space-x-2 text-sm">
            <Zap className={`h-4 w-4 ${
              performance?.renderTime > 1000 ? 'text-red-400' : 
              performance?.renderTime > 500 ? 'text-yellow-400' : 'text-green-400'
            }`} />
            <span className="text-gray-400">Render:</span>
            <span className="text-white font-medium">
              {performance?.renderTime || 0}ms
            </span>
          </div>

          {/* Last Updated */}
          <div className="flex items-center space-x-2 text-sm">
            <Clock className="h-4 w-4 text-gray-400" />
            <span className="text-gray-400">
              {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BottomStatusBar;