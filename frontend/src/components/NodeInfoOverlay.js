import React, { useEffect } from 'react';
import { Shield, FileText, AlertTriangle, BarChart3, X } from 'lucide-react';

const NodeInfoOverlay = ({ 
  node, 
  position, 
  vulnerabilityCount = 0, 
  strideScore = 0, 
  answeredQuestions = 0, 
  totalQuestions = 0,
  onClose 
}) => {
  // Auto-dismiss after 5 seconds
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, 5000);

    return () => clearTimeout(timer);
  }, [onClose]);

  if (!node || !position) return null;

  const getNodeDescription = (nodeType, nodeSubtype) => {
    const descriptions = {
      WebApp: "A web application that serves users and processes business logic",
      API: "Application Programming Interface that handles data requests and responses", 
      Database: "Data storage system that manages and persists application information",
      Backup: "Backup system that creates and maintains data recovery copies",
      Monitoring: "Monitoring system that tracks application performance and security",
      LoadBalancer: "Load balancer that distributes traffic across multiple servers",
      Cache: "Caching system that improves application performance",
      Queue: "Message queue system for asynchronous processing"
    };
    
    return descriptions[nodeSubtype] || descriptions[nodeType] || "Security component in your architecture";
  };

  const completionPercentage = totalQuestions > 0 ? Math.round((answeredQuestions / totalQuestions) * 100) : 0;

  return (
    <div 
      className="absolute z-50 bg-gray-900 border border-gray-600 rounded-lg shadow-2xl p-4 min-w-[280px] max-w-[320px]"
      style={{
        left: position.x + 10,
        top: position.y - 10,
        transform: 'translateY(-50%)'
      }}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <Shield className="h-4 w-4 text-blue-400" />
          <span className="text-sm font-semibold text-white">
            {node.data?.label || node.id}
          </span>
        </div>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-white transition-colors"
        >
          <X className="h-3 w-3" />
        </button>
      </div>

      {/* Node Description */}
      <div className="mb-3">
        <p className="text-xs text-gray-300 leading-relaxed">
          {getNodeDescription(node.type, node.data?.subtype)}
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-3">
        {/* Questions Answered */}
        <div className="bg-gray-800 rounded-md p-2">
          <div className="flex items-center space-x-1 mb-1">
            <FileText className="h-3 w-3 text-green-400" />
            <span className="text-xs font-medium text-gray-300">Questions</span>
          </div>
          <div className="text-sm text-white font-semibold">
            {answeredQuestions}/{totalQuestions}
          </div>
          <div className="text-xs text-gray-400">
            {completionPercentage}% complete
          </div>
        </div>

        {/* Vulnerabilities */}
        <div className="bg-gray-800 rounded-md p-2">
          <div className="flex items-center space-x-1 mb-1">
            <AlertTriangle className="h-3 w-3 text-red-400" />
            <span className="text-xs font-medium text-gray-300">Vulnerabilities</span>
          </div>
          <div className="text-sm text-white font-semibold">
            {vulnerabilityCount}
          </div>
          <div className="text-xs text-gray-400">
            {vulnerabilityCount === 0 ? 'None found' : 'Issues detected'}
          </div>
        </div>

        {/* STRIDE Score */}
        <div className="bg-gray-800 rounded-md p-2 col-span-2">
          <div className="flex items-center space-x-1 mb-1">
            <BarChart3 className="h-3 w-3 text-purple-400" />
            <span className="text-xs font-medium text-gray-300">STRIDE Risk Score</span>
          </div>
          <div className="flex items-center justify-between">
            <div className="text-sm text-white font-semibold">
              {strideScore.toFixed(1)}/10.0
            </div>
            <div className={`text-xs px-2 py-1 rounded ${
              strideScore >= 7 ? 'bg-red-900 text-red-300' :
              strideScore >= 4 ? 'bg-yellow-900 text-yellow-300' :
              'bg-green-900 text-green-300'
            }`}>
              {strideScore >= 7 ? 'High Risk' :
               strideScore >= 4 ? 'Medium Risk' :
               'Low Risk'}
            </div>
          </div>
        </div>
      </div>

      {/* Auto-dismiss indicator */}
      <div className="mt-3 text-center">
        <div className="text-xs text-gray-500">Auto-dismiss in 5s</div>
        <div className="w-full bg-gray-700 h-1 rounded-full mt-1 overflow-hidden">
          <div 
            className="h-full bg-blue-500 rounded-full"
            style={{
              width: '100%',
              animation: 'shrink-width 5s linear forwards'
            }}
          />
        </div>
      </div>

      <style jsx global>{`
        @keyframes shrink-width {
          from { width: 100%; }
          to { width: 0%; }
        }
      `}</style>
    </div>
  );
};

export default NodeInfoOverlay;