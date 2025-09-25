import React, { useEffect, useState } from 'react';
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
  const [adjustedPosition, setAdjustedPosition] = useState(position);

  // No auto-dismiss - only close when hover ends

  // Calculate smart positioning to keep overlay within canvas bounds
  useEffect(() => {
    if (!position) return;

    const overlayWidth = 320; // max-w-[320px] from component
    const overlayHeight = 280; // approximate height
    const margin = 20; // minimum margin from edges

    // Get canvas dimensions (ReactFlow container)
    const canvasElement = document.querySelector('.react-flow');
    if (!canvasElement) {
      setAdjustedPosition(position);
      return;
    }

    const canvasRect = canvasElement.getBoundingClientRect();
    const canvasLeft = canvasRect.left;
    const canvasRight = canvasRect.right;
    const canvasTop = canvasRect.top;
    const canvasBottom = canvasRect.bottom;

    let newX = position.x + 15; // Default: to the right of node
    let newY = position.y;

    // Check right boundary - if overlay would go outside canvas, position to the left
    if (newX + overlayWidth + margin > canvasRight) {
      newX = position.x - overlayWidth - 15; // Position to the left of node
    }

    // Check left boundary
    if (newX < canvasLeft + margin) {
      newX = canvasLeft + margin;
    }

    // Check bottom boundary
    if (newY + overlayHeight / 2 + margin > canvasBottom) {
      newY = canvasBottom - overlayHeight / 2 - margin;
    }

    // Check top boundary  
    if (newY - overlayHeight / 2 < canvasTop + margin) {
      newY = canvasTop + overlayHeight / 2 + margin;
    }

    setAdjustedPosition({
      x: newX,
      y: newY
    });
  }, [position]);

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

  const handleOverlayMouseEnter = (event) => {
    event.stopPropagation();
    // Dispatch event to let parent know overlay is being hovered
    const customEvent = new CustomEvent('overlayHover', { detail: { action: 'enter' } });
    window.dispatchEvent(customEvent);
  };

  const handleOverlayMouseLeave = (event) => {
    event.stopPropagation();
    // Dispatch event to let parent know overlay hover ended
    const customEvent = new CustomEvent('overlayHover', { detail: { action: 'leave' } });
    window.dispatchEvent(customEvent);
  };

  return (
    <div 
      className="absolute z-50 bg-gray-900 border border-gray-600 rounded-lg shadow-2xl p-4 min-w-[280px] max-w-[320px]"
      style={{
        left: adjustedPosition.x,
        top: adjustedPosition.y,
        transform: 'translateY(-50%)'
      }}
      onMouseEnter={handleOverlayMouseEnter}
      onMouseLeave={handleOverlayMouseLeave}
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
              {strideScore > 0 ? `${strideScore.toFixed(1)}/10.0` : 'Not analyzed'}
            </div>
            {strideScore > 0 && (
              <div className={`text-xs px-2 py-1 rounded ${
                strideScore >= 7 ? 'bg-red-900 text-red-300' :
                strideScore >= 4 ? 'bg-yellow-900 text-yellow-300' :
                'bg-green-900 text-green-300'
              }`}>
                {strideScore >= 7 ? 'High Risk' :
                 strideScore >= 4 ? 'Medium Risk' :
                 'Low Risk'}
              </div>
            )}
            {strideScore === 0 && (
              <div className="text-xs text-gray-500">
                Run STRIDE analysis
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Hover tip */}
      <div className="mt-3 text-center">
        <div className="text-xs text-gray-500">Hover to view details</div>
      </div>
    </div>
  );
};

export default NodeInfoOverlay;