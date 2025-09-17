import React, { useState } from 'react';
import { 
  ChevronLeft, 
  ChevronRight, 
  Search, 
  Layers, 
  BookOpen, 
  History,
  Plus,
  Grid3X3,
  FolderOpen
} from 'lucide-react';
import { AdvancedNodeLibrary } from '../AdvancedNodeLibrary';

const LeftPanel = ({ 
  isCollapsed, 
  onToggleCollapse,
  diagrams,
  currentDiagram,
  onLoadDiagram,
  searchTerm,
  onSearchChange,
  activeTab,
  onTabChange
}) => {
  const tabs = [
    { id: 'nodes', label: 'Nodes', icon: Grid3X3 },
    { id: 'templates', label: 'Templates', icon: BookOpen },
    { id: 'history', label: 'History', icon: History }
  ];

  return (
    <div className={`bg-gray-800 border-r border-gray-700 flex flex-col transition-all duration-300 ${
      isCollapsed ? 'w-16' : 'w-80'
    }`}>
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center justify-between">
          {!isCollapsed && (
            <div className="flex items-center space-x-2">
              <Layers className="h-5 w-5 text-blue-400" />
              <h2 className="text-white font-semibold">Workspace</h2>
            </div>
          )}
          <button
            onClick={onToggleCollapse}
            className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-colors"
            title={isCollapsed ? 'Expand Panel' : 'Collapse Panel'}
          >
            {isCollapsed ? (
              <ChevronRight className="h-4 w-4" />
            ) : (
              <ChevronLeft className="h-4 w-4" />
            )}
          </button>
        </div>
      </div>

      {/* Search Bar */}
      {!isCollapsed && (
        <div className="p-4 border-b border-gray-700">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search components..."
              value={searchTerm}
              onChange={(e) => onSearchChange(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-gray-700 text-white placeholder-gray-400 rounded-lg border border-gray-600 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors"
            />
          </div>
        </div>
      )}

      {/* Navigation Tabs */}
      {!isCollapsed && (
        <div className="flex border-b border-gray-700">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => onTabChange(tab.id)}
                className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'text-blue-400 border-b-2 border-blue-400 bg-gray-750'
                    : 'text-gray-400 hover:text-white hover:bg-gray-750'
                }`}
              >
                <Icon className="h-4 w-4 inline mr-2" />
                {tab.label}
              </button>
            );
          })}
        </div>
      )}

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto">
        {!isCollapsed ? (
          <>
            {activeTab === 'nodes' && (
              <div className="p-4">
                <AdvancedNodeLibrary searchTerm={searchTerm} />
              </div>
            )}
            
            {activeTab === 'templates' && (
              <div className="p-4">
                <div className="text-center text-gray-400 py-8">
                  <BookOpen className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p className="text-sm">Template browser coming soon</p>
                  <button className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm">
                    Browse Templates
                  </button>
                </div>
              </div>
            )}
            
            {activeTab === 'history' && (
              <div className="p-4">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-white font-medium">Recent Models</h3>
                  <Plus className="h-4 w-4 text-gray-400 hover:text-white cursor-pointer" />
                </div>
                <div className="space-y-2">
                  {diagrams.map((diagram) => (
                    <button
                      key={diagram.id}
                      onClick={() => onLoadDiagram(diagram)}
                      className={`w-full text-left p-3 rounded-lg text-white text-sm transition-colors ${
                        currentDiagram?.id === diagram.id
                          ? 'bg-blue-700 border border-blue-500'
                          : 'bg-gray-700 hover:bg-gray-600'
                      }`}
                    >
                      <div className="font-medium truncate">{diagram.title}</div>
                      <div className="text-gray-400 text-xs mt-1">
                        {diagram.nodes?.length || 0} nodes • {diagram.edges?.length || 0} edges
                      </div>
                      <div className="text-gray-500 text-xs">
                        {new Date(diagram.updated_at || diagram.created_at).toLocaleDateString()}
                      </div>
                    </button>
                  ))}
                  {diagrams.length === 0 && (
                    <div className="text-center text-gray-400 py-8">
                      <History className="h-8 w-8 mx-auto mb-2 opacity-50" />
                      <p className="text-sm">No saved models yet</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="flex flex-col items-center pt-6 space-y-4">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => onTabChange(tab.id)}
                  className={`p-3 rounded-lg transition-colors ${
                    activeTab === tab.id
                      ? 'text-blue-400 bg-gray-700'
                      : 'text-gray-400 hover:text-white hover:bg-gray-700'
                  }`}
                  title={tab.label}
                >
                  <Icon className="h-5 w-5" />
                </button>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default LeftPanel;