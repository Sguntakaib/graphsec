import React from 'react';
import { 
  X, 
  ChevronLeft, 
  ChevronRight,
  Settings,
  BarChart3,
  FileText,
  Shield
} from 'lucide-react';
import { PropertiesPanel } from '../PropertiesPanel';
import { EnhancedSimulationPanel } from '../EnhancedSimulationPanel';
import AdvancedLayoutControls from '../AdvancedLayoutControls';
import SimulationDebugger from '../SimulationDebugger';
import NodeBranchVisualizer from '../NodeBranchVisualizer';

const RightPanel = ({ 
  isVisible,
  isCollapsed,
  onToggleCollapse,
  onClose,
  viewMode,
  selectedNode,
  simulationResult,
  currentDiagram,
  nodes,
  edges,
  setNodes,
  setEdges,
  isLoading,
  setIsLoading,
  fitView,
  onRunSimulation,
  onHighlightPath,
  onClearHighlights,
  nodeBranches,
  onNodeBranchUpdate
}) => {
  if (!isVisible) return null;

  const getPanelTitle = () => {
    if (viewMode === 'analysis' && simulationResult) return 'Analysis Results';
    if (selectedNode) return 'Node Properties';
    return 'Workspace Tools';
  };

  const getPanelIcon = () => {
    if (viewMode === 'analysis' && simulationResult) return BarChart3;
    if (selectedNode) return FileText;
    return Settings;
  };

  const PanelIcon = getPanelIcon();

  return (
    <div className={`bg-gray-800 border-l border-gray-700 flex flex-col transition-all duration-300 ${
      isCollapsed ? 'w-16' : 'w-96'
    }`}>
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center justify-between">
          {!isCollapsed && (
            <div className="flex items-center space-x-2">
              <PanelIcon className="h-5 w-5 text-blue-400" />
              <h2 className="text-white font-semibold">{getPanelTitle()}</h2>
            </div>
          )}
          <div className="flex items-center space-x-2">
            <button
              onClick={onToggleCollapse}
              className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-colors"
              title={isCollapsed ? 'Expand Panel' : 'Collapse Panel'}
            >
              {isCollapsed ? (
                <ChevronLeft className="h-4 w-4" />
              ) : (
                <ChevronRight className="h-4 w-4" />
              )}
            </button>
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-colors"
              title="Close Panel"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto">
        {!isCollapsed ? (
          <>
            {viewMode === 'modeling' && (
              <>
                {/* Advanced Layout Controls */}
                <div className="border-b border-gray-700">
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
                
                {/* Simulation Debugger */}
                <div className="border-b border-gray-700">
                  <SimulationDebugger
                    nodes={nodes}
                    edges={edges}
                    onRunSimulation={onRunSimulation}
                    simulationResult={simulationResult}
                    isLoading={isLoading}
                  />
                </div>
                
                {/* Node Properties */}
                {selectedNode && (
                  <>
                    <div className="border-b border-gray-700">
                      <PropertiesPanel node={selectedNode} />
                    </div>
                    
                    {/* Security Branches Visualizer */}
                    {selectedNode.data?.intelligentNode && (
                      <div className="border-b border-gray-700">
                        <NodeBranchVisualizer
                          nodeId={selectedNode.id}
                          nodeSubtype={selectedNode.data.subtype}
                          branches={nodeBranches[selectedNode.id] || []}
                          onBranchUpdate={onNodeBranchUpdate}
                          isExpanded={true}
                        />
                      </div>
                    )}
                  </>
                )}
                
                {/* Empty State */}
                {!selectedNode && (
                  <div className="p-6 text-center">
                    <div className="bg-gray-700 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                      <FileText className="h-8 w-8 text-gray-400" />
                    </div>
                    <h3 className="text-white font-medium mb-2">No Selection</h3>
                    <p className="text-gray-400 text-sm mb-4">
                      Select a node to view its properties and configuration options.
                    </p>
                    <div className="text-xs text-gray-500">
                      Tip: Double-click nodes to open questionnaires
                    </div>
                  </div>
                )}
              </>
            )}

            {viewMode === 'analysis' && simulationResult && (
              <EnhancedSimulationPanel 
                result={simulationResult} 
                onHighlightPath={onHighlightPath}
                onClearHighlights={onClearHighlights}
              />
            )}

            {viewMode === 'analysis' && !simulationResult && (
              <div className="p-6 text-center">
                <div className="bg-gray-700 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                  <BarChart3 className="h-8 w-8 text-gray-400" />
                </div>
                <h3 className="text-white font-medium mb-2">No Analysis Results</h3>
                <p className="text-gray-400 text-sm mb-4">
                  Run a simulation to see detailed analysis results and attack paths.
                </p>
                <button
                  onClick={onRunSimulation}
                  disabled={isLoading || nodes.length === 0}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 transition-colors text-sm"
                >
                  Run Analysis
                </button>
              </div>
            )}
          </>
        ) : (
          <div className="flex flex-col items-center pt-6">
            <button
              onClick={onToggleCollapse}
              className="p-3 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-colors"
              title="Expand Panel"
            >
              <PanelIcon className="h-5 w-5" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default RightPanel;