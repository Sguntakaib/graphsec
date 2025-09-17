import React from 'react';
import { 
  Shield, 
  Save, 
  Play, 
  BookOpen, 
  Zap, 
  AlertTriangle,
  Settings,
  User,
  ChevronDown,
  Plus,
  FolderOpen,
  RotateCcw
} from 'lucide-react';

const TopNavigationBar = ({ 
  currentDiagram,
  isLoading,
  simulationResult,
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
  allVulnerabilities = [],
  viewMode,
  onViewModeChange
}) => {
  return (
    <div className="bg-gray-800 border-b border-gray-700 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Logo and Project Selector */}
        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-3">
            <Shield className="h-8 w-8 text-blue-400" />
            <div>
              <h1 className="text-xl font-bold text-white">Security Modeling Platform</h1>
              <div className="text-xs text-gray-400">
                Advanced Threat Modeling & Attack Path Analysis
              </div>
            </div>
          </div>
          
          {/* Workspace Selector */}
          <div className="flex items-center space-x-2 bg-gray-700 rounded-lg px-3 py-2">
            <FolderOpen className="h-4 w-4 text-gray-400" />
            <span className="text-white text-sm">
              {currentDiagram?.title || 'Untitled Model'}
            </span>
            <ChevronDown className="h-4 w-4 text-gray-400" />
          </div>
        </div>

        {/* View Mode Toggle */}
        <div className="flex items-center space-x-2 bg-gray-700 rounded-lg p-1">
          <button
            onClick={() => onViewModeChange('modeling')}
            className={`px-4 py-2 rounded-md transition-colors text-sm font-medium ${
              viewMode === 'modeling'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-gray-300 hover:text-white hover:bg-gray-600'
            }`}
          >
            <Shield className="h-4 w-4 inline mr-2" />
            Modeling
          </button>
          <button
            onClick={() => onViewModeChange('analysis')}
            className={`px-4 py-2 rounded-md transition-colors text-sm font-medium ${
              viewMode === 'analysis'
                ? 'bg-red-600 text-white shadow-sm'
                : 'text-gray-300 hover:text-white hover:bg-gray-600'
            }`}
            disabled={!simulationResult}
          >
            <AlertTriangle className="h-4 w-4 inline mr-2" />
            Analysis
          </button>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center space-x-3">
          {/* Primary Actions */}
          <div className="flex items-center space-x-2">
            <button
              onClick={onNewDiagram}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2 text-sm font-medium"
              title="New Diagram (Ctrl+N)"
            >
              <Plus className="h-4 w-4" />
              <span>New</span>
            </button>
            
            <button
              onClick={onSave}
              disabled={isLoading}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2 text-sm font-medium"
              title="Save Diagram (Ctrl+S)"
            >
              <Save className="h-4 w-4" />
              <span>{isLoading ? 'Saving...' : 'Save'}</span>
            </button>
            
            <button
              onClick={onSimulate}
              disabled={isLoading}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2 text-sm font-medium"
              title="Run Simulation (Ctrl+R)"
            >
              <Play className="h-4 w-4" />
              <span>{isLoading ? 'Analyzing...' : 'Simulate'}</span>
            </button>
          </div>

          {/* Secondary Actions */}
          <div className="flex items-center space-x-2 pl-3 border-l border-gray-600">
            <button
              onClick={onShowTemplates}
              className="px-3 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-colors flex items-center space-x-2 text-sm"
              title="Template Library"
            >
              <BookOpen className="h-4 w-4" />
              <span>Templates</span>
            </button>
            
            <button
              onClick={onShowWizard}
              className="px-3 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-colors flex items-center space-x-2 text-sm"
              title="Threat Modeling Wizard"
            >
              <Shield className="h-4 w-4" />
              <span>Wizard</span>
            </button>

            <button
              onClick={onAnalyzeVulnerabilities}
              disabled={isLoading}
              className="px-3 py-2 bg-red-700 text-white rounded-lg hover:bg-red-800 disabled:opacity-50 transition-colors flex items-center space-x-2 text-sm"
              title="Analyze Vulnerabilities"
            >
              <AlertTriangle className="h-4 w-4" />
              <span>Vulnerabilities</span>
              {allVulnerabilities.length > 0 && (
                <span className="bg-red-500 text-white text-xs px-2 py-0.5 rounded-full">
                  {allVulnerabilities.length}
                </span>
              )}
            </button>
          </div>

          {/* User Menu */}
          <div className="flex items-center space-x-2 pl-3 border-l border-gray-600">
            <button
              onClick={onShowSettings}
              className="px-3 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-colors flex items-center space-x-2 text-sm"
              title="Settings"
            >
              <Settings className="h-4 w-4" />
            </button>
            
            <button className="px-3 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-colors flex items-center space-x-2 text-sm">
              <User className="h-4 w-4" />
              <ChevronDown className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TopNavigationBar;