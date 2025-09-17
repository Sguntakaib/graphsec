import React, { useState, useEffect, useMemo } from 'react';
import TopNavigationBar from './TopNavigationBar';
import LeftPanel from './LeftPanel';
import RightPanel from './RightPanel';
import EmptyState from './EmptyState';
import BottomStatusBar from './BottomStatusBar';

const MainLayout = ({
  // Navigation props
  currentDiagram,
  isLoading,
  simulationResult,
  viewMode,
  onViewModeChange,
  
  // Action handlers
  onNewDiagram,
  onSave,
  onSimulate,
  onShowTemplates,
  onShowWizard,
  onShowCoreLoop,
  onShowSettings,
  onImport,
  onExport,
  onAnalyzeVulnerabilities,
  
  // Canvas and data
  children, // This will be the ReactFlow component
  nodes,
  edges,
  setNodes,
  setEdges,
  selectedNode,
  diagrams,
  onLoadDiagram,
  
  // Right panel props
  fitView,
  onRunSimulation,
  onHighlightPath,
  onClearHighlights,
  nodeBranches,
  onNodeBranchUpdate,
  
  // Vulnerability data
  allVulnerabilities,
  
  // Performance data
  performance,
  
  // Tour/onboarding
  onStartTour
}) => {
  // Layout state
  const [leftPanelCollapsed, setLeftPanelCollapsed] = useState(false);
  const [rightPanelVisible, setRightPanelVisible] = useState(true);
  const [rightPanelCollapsed, setRightPanelCollapsed] = useState(false);
  
  // Left panel state
  const [searchTerm, setSearchTerm] = useState('');
  const [activeLeftTab, setActiveLeftTab] = useState('nodes');
  
  // Auto-show right panel when node is selected or analysis is available
  useEffect(() => {
    if (selectedNode || (viewMode === 'analysis' && simulationResult)) {
      setRightPanelVisible(true);
      setRightPanelCollapsed(false);
    }
  }, [selectedNode, viewMode, simulationResult]);

  // Determine if we should show empty state
  const showEmptyState = useMemo(() => {
    return nodes.length === 0 && !isLoading;
  }, [nodes.length, isLoading]);

  // Auto-hide right panel in empty state
  useEffect(() => {
    if (showEmptyState) {
      setRightPanelVisible(false);
    }
  }, [showEmptyState]);

  const handleStartTour = () => {
    // Implementation for interactive tour
    if (onStartTour) {
      onStartTour();
    } else {
      // Fallback - show template library
      onShowTemplates();
    }
  };

  return (
    <div className="h-screen flex flex-col bg-gray-900">
      {/* Top Navigation Bar */}
      <TopNavigationBar
        currentDiagram={currentDiagram}
        isLoading={isLoading}
        simulationResult={simulationResult}
        viewMode={viewMode}
        onViewModeChange={onViewModeChange}
        onNewDiagram={onNewDiagram}
        onSave={onSave}
        onSimulate={onSimulate}
        onShowTemplates={onShowTemplates}
        onShowWizard={onShowWizard}
        onShowCoreLoop={onShowCoreLoop}
        onShowSettings={onShowSettings}
        onImport={onImport}
        onExport={onExport}
        onAnalyzeVulnerabilities={onAnalyzeVulnerabilities}
        allVulnerabilities={allVulnerabilities}
      />

      {/* Main Content Area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Panel */}
        <LeftPanel
          isCollapsed={leftPanelCollapsed}
          onToggleCollapse={() => setLeftPanelCollapsed(!leftPanelCollapsed)}
          diagrams={diagrams}
          currentDiagram={currentDiagram}
          onLoadDiagram={onLoadDiagram}
          searchTerm={searchTerm}
          onSearchChange={setSearchTerm}
          activeTab={activeLeftTab}
          onTabChange={setActiveLeftTab}
        />

        {/* Main Canvas Area */}
        <div className="flex-1 flex flex-col relative">
          {showEmptyState ? (
            <EmptyState
              onShowTemplateLibrary={onShowTemplates}
              onShowThreatModelingWizard={onShowWizard}
              onNewDiagram={onNewDiagram}
              onStartTour={handleStartTour}
            />
          ) : (
            <>
              {/* Canvas Content */}
              <div className="flex-1 relative">
                {children}
              </div>
            </>
          )}
        </div>

        {/* Right Panel */}
        {rightPanelVisible && (
          <RightPanel
            isVisible={rightPanelVisible}
            isCollapsed={rightPanelCollapsed}
            onToggleCollapse={() => setRightPanelCollapsed(!rightPanelCollapsed)}
            onClose={() => setRightPanelVisible(false)}
            viewMode={viewMode}
            selectedNode={selectedNode}
            simulationResult={simulationResult}
            currentDiagram={currentDiagram}
            nodes={nodes}
            edges={edges}
            setNodes={setNodes}
            setEdges={setEdges}
            isLoading={isLoading}
            setIsLoading={() => {}} // This should be passed from parent
            fitView={fitView}
            onRunSimulation={onRunSimulation}
            onHighlightPath={onHighlightPath}
            onClearHighlights={onClearHighlights}
            nodeBranches={nodeBranches}
            onNodeBranchUpdate={onNodeBranchUpdate}
          />
        )}
      </div>

      {/* Bottom Status Bar */}
      {!showEmptyState && (
        <BottomStatusBar
          nodes={nodes}
          edges={edges}
          simulationResult={simulationResult}
          isLoading={isLoading}
          performance={performance}
          selectedNode={selectedNode}
          allVulnerabilities={allVulnerabilities}
        />
      )}
    </div>
  );
};

export default MainLayout;