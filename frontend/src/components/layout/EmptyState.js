import React, { useState } from 'react';
import { 
  Shield, 
  BookOpen, 
  Play, 
  ChevronRight,
  Zap,
  Target,
  Network,
  BarChart3,
  Plus
} from 'lucide-react';

const EmptyState = ({ 
  onShowTemplateLibrary,
  onShowThreatModelingWizard,
  onNewDiagram,
  onStartTour
}) => {
  const [currentStep, setCurrentStep] = useState(0);

  const quickStartSteps = [
    {
      title: "Add Your First Asset",
      description: "Start by adding a web application, database, or API that needs protection",
      icon: Target,
      color: "text-blue-400"
    },
    {
      title: "Identify Threat Actors", 
      description: "Add potential attackers like external hackers or malicious insiders",
      icon: Shield,
      color: "text-red-400"
    },
    {
      title: "Connect Attack Paths",
      description: "Draw connections showing how attackers might reach your assets",
      icon: Network,
      color: "text-yellow-400"
    },
    {
      title: "Run Analysis",
      description: "Simulate attack scenarios and get security recommendations",
      icon: BarChart3,
      color: "text-green-400"
    }
  ];

  const templates = [
    {
      name: "Web Application",
      description: "Complete web app security model with common vulnerabilities",
      nodes: 6,
      edges: 8
    },
    {
      name: "Zero Trust Architecture", 
      description: "Modern zero-trust security framework implementation",
      nodes: 12,
      edges: 15
    },
    {
      name: "Cloud Native",
      description: "Kubernetes and containerized application security",
      nodes: 10,
      edges: 12
    }
  ];

  return (
    <div className="flex-1 flex items-center justify-center bg-gray-900 p-8">
      <div className="max-w-4xl w-full">
        {/* Welcome Header */}
        <div className="text-center mb-12">
          <div className="bg-gradient-to-br from-blue-500 to-purple-600 rounded-full w-24 h-24 flex items-center justify-center mx-auto mb-6">
            <Shield className="h-12 w-12 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-white mb-4">
            Start Your Security Model
          </h1>
          <p className="text-xl text-gray-400 mb-8">
            Build comprehensive threat models and analyze attack paths with our advanced platform
          </p>
          
          {/* Quick Actions */}
          <div className="flex items-center justify-center space-x-4">
            <button
              onClick={onNewDiagram}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2 font-medium"
            >
              <Plus className="h-5 w-5" />
              <span>Start from Scratch</span>
            </button>
            
            <button
              onClick={onShowTemplateLibrary}
              className="px-6 py-3 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-colors flex items-center space-x-2 font-medium"
            >
              <BookOpen className="h-5 w-5" />
              <span>Browse Templates</span>
            </button>
            
            <button
              onClick={onShowThreatModelingWizard}
              className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center space-x-2 font-medium"
            >
              <Zap className="h-5 w-5" />
              <span>Guided Wizard</span>
            </button>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Quick Start Guide */}
          <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-white">Quick Start Guide</h3>
              <button
                onClick={onStartTour}
                className="text-blue-400 hover:text-blue-300 text-sm flex items-center space-x-1"
              >
                <span>Interactive Tour</span>
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
            
            <div className="space-y-4">
              {quickStartSteps.map((step, index) => {
                const Icon = step.icon;
                return (
                  <div
                    key={index}
                    className={`flex items-start space-x-4 p-4 rounded-lg transition-colors ${
                      currentStep === index ? 'bg-gray-700' : 'hover:bg-gray-750'
                    }`}
                    onClick={() => setCurrentStep(index)}
                  >
                    <div className={`p-2 rounded-lg bg-gray-600 ${step.color}`}>
                      <Icon className="h-5 w-5" />
                    </div>
                    <div className="flex-1">
                      <h4 className="font-medium text-white mb-1">
                        {index + 1}. {step.title}
                      </h4>
                      <p className="text-sm text-gray-400">
                        {step.description}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
            
            <div className="mt-6 pt-6 border-t border-gray-700">
              <button
                onClick={onStartTour}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
              >
                Start Interactive Tour
              </button>
            </div>
          </div>

          {/* Template Preview */}
          <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-white">Popular Templates</h3>
              <button
                onClick={onShowTemplateLibrary}
                className="text-blue-400 hover:text-blue-300 text-sm flex items-center space-x-1"
              >
                <span>View All</span>
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
            
            <div className="space-y-3">
              {templates.map((template, index) => (
                <div
                  key={index}
                  className="p-4 rounded-lg bg-gray-700 hover:bg-gray-600 transition-colors cursor-pointer group"
                  onClick={onShowTemplateLibrary}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium text-white group-hover:text-blue-400 transition-colors">
                        {template.name}
                      </h4>
                      <p className="text-sm text-gray-400 mt-1">
                        {template.description}
                      </p>
                      <div className="text-xs text-gray-500 mt-2">
                        {template.nodes} nodes • {template.edges} connections
                      </div>
                    </div>
                    <ChevronRight className="h-5 w-5 text-gray-400 group-hover:text-blue-400 transition-colors" />
                  </div>
                </div>
              ))}
            </div>
            
            <div className="mt-6 pt-6 border-t border-gray-700">
              <button
                onClick={onShowTemplateLibrary}
                className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-colors text-sm font-medium"
              >
                Browse All Templates
              </button>
            </div>
          </div>
        </div>

        {/* Feature Highlights */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="bg-blue-600 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-4">
              <Shield className="h-6 w-6 text-white" />
            </div>
            <h4 className="font-semibold text-white mb-2">Advanced Modeling</h4>
            <p className="text-sm text-gray-400">
              Create detailed threat models with our comprehensive library of security components
            </p>
          </div>
          
          <div className="text-center">
            <div className="bg-red-600 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-4">
              <Play className="h-6 w-6 text-white" />
            </div>
            <h4 className="font-semibold text-white mb-2">Attack Simulation</h4>
            <p className="text-sm text-gray-400">
              Simulate realistic attack scenarios and identify critical vulnerabilities
            </p>
          </div>
          
          <div className="text-center">
            <div className="bg-green-600 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-4">
              <BarChart3 className="h-6 w-6 text-white" />
            </div>
            <h4 className="font-semibold text-white mb-2">Risk Analysis</h4>
            <p className="text-sm text-gray-400">
              Get actionable insights and prioritized recommendations for security improvements
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmptyState;