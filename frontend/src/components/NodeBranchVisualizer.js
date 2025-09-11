import React, { useState, useEffect } from 'react';
import { 
  Shield, 
  CheckCircle, 
  XCircle, 
  AlertCircle, 
  Lock, 
  Key, 
  Database, 
  Globe, 
  Filter,
  Monitor,
  FileText,
  Settings,
  ChevronDown,
  ChevronRight,
  Plus,
  Minus
} from 'lucide-react';

const NodeBranchVisualizer = ({ 
  nodeId, 
  nodeSubtype, 
  branches = [], 
  onBranchUpdate,
  isExpanded = false 
}) => {
  const [expanded, setExpanded] = useState(isExpanded);
  const [localBranches, setLocalBranches] = useState(branches);
  const [completionStatus, setCompletionStatus] = useState(null);

  useEffect(() => {
    setLocalBranches(branches);
    calculateCompletionStatus(branches);
  }, [branches]);

  const calculateCompletionStatus = (branchList) => {
    const total = branchList.length;
    const completed = branchList.filter(b => b.completed).length;
    const percentage = total > 0 ? Math.round((completed / total) * 100) : 100;
    
    setCompletionStatus({
      total,
      completed,
      percentage,
      status: percentage === 100 ? 'complete' : percentage >= 50 ? 'partial' : 'incomplete'
    });
  };

  const getBranchIcon = (branchType) => {
    const iconMap = {
      'Login': Key,
      'API': Globe,
      'Database': Database,
      'InputValidation': Filter,
      'WAF': Shield,
      'Encryption': Lock,
      'AccessControl': Key,
      'Authentication': Key,
      'Authorization': Settings,
      'RateLimiting': Monitor,
      'CORS': Globe,
      'DataClassification': FileText,
      'Backup': Database,
      'Monitoring': Monitor,
      'Logging': FileText
    };
    return iconMap[branchType] || Settings;
  };

  const getBranchStatusColor = (branch) => {
    if (branch.completed && branch.value && branch.value !== 'None' && branch.value !== 'Unknown') {
      return 'text-green-400 border-green-500';
    } else if (branch.completed) {
      return 'text-yellow-400 border-yellow-500';
    } else {
      return 'text-red-400 border-red-500';
    }
  };

  const getBranchStatusIcon = (branch) => {
    if (branch.completed && branch.value && branch.value !== 'None' && branch.value !== 'Unknown') {
      return CheckCircle;
    } else if (branch.completed) {
      return AlertCircle;
    } else {
      return XCircle;
    }
  };

  const getCompletionColor = () => {
    if (!completionStatus) return 'text-gray-400';
    
    switch (completionStatus.status) {
      case 'complete': return 'text-green-400';
      case 'partial': return 'text-yellow-400';
      default: return 'text-red-400';
    }
  };

  const handleBranchToggle = (branchId) => {
    const updatedBranches = localBranches.map(branch => {
      if (branch.id === branchId) {
        const updated = { ...branch, completed: !branch.completed };
        if (!updated.completed) {
          updated.value = null;
        }
        return updated;
      }
      return branch;
    });
    
    setLocalBranches(updatedBranches);
    calculateCompletionStatus(updatedBranches);
    
    if (onBranchUpdate) {
      onBranchUpdate(nodeId, updatedBranches);
    }
  };

  const handleBranchValueChange = (branchId, value) => {
    const updatedBranches = localBranches.map(branch => {
      if (branch.id === branchId) {
        return { ...branch, value, completed: true };
      }
      return branch;
    });
    
    setLocalBranches(updatedBranches);
    calculateCompletionStatus(updatedBranches);
    
    if (onBranchUpdate) {
      onBranchUpdate(nodeId, updatedBranches);
    }
  };

  if (localBranches.length === 0) {
    return null;
  }

  return (
    <div className="mt-4 border border-gray-600 rounded-lg bg-gray-800/50">
      {/* Header */}
      <div 
        className="flex items-center justify-between p-3 cursor-pointer hover:bg-gray-700/50 transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center space-x-3">
          {expanded ? (
            <ChevronDown className="h-4 w-4 text-gray-400" />
          ) : (
            <ChevronRight className="h-4 w-4 text-gray-400" />
          )}
          <Shield className="h-5 w-5 text-blue-400" />
          <div>
            <h4 className="text-sm font-semibold text-white">Security Branches</h4>
            <p className="text-xs text-gray-400">
              Required security configurations for {nodeSubtype}
            </p>
          </div>
        </div>
        
        {completionStatus && (
          <div className="flex items-center space-x-2">
            <div className={`text-sm font-medium ${getCompletionColor()}`}>
              {completionStatus.completed}/{completionStatus.total}
            </div>
            <div className="w-8 h-2 bg-gray-700 rounded-full overflow-hidden">
              <div 
                className={`h-full transition-all duration-300 ${
                  completionStatus.status === 'complete' 
                    ? 'bg-green-500' 
                    : completionStatus.status === 'partial' 
                    ? 'bg-yellow-500' 
                    : 'bg-red-500'
                }`}
                style={{ width: `${completionStatus.percentage}%` }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Expanded Content */}
      {expanded && (
        <div className="border-t border-gray-700 p-3 space-y-3">
          {localBranches.map((branch) => {
            const IconComponent = getBranchIcon(branch.type);
            const StatusIcon = getBranchStatusIcon(branch);
            const statusColor = getBranchStatusColor(branch);

            return (
              <div 
                key={branch.id}
                className={`flex items-start space-x-3 p-3 border rounded-lg transition-colors ${statusColor}`}
              >
                <div className="flex items-center space-x-2 min-w-0 flex-1">
                  <IconComponent className="h-4 w-4 flex-shrink-0" />
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center space-x-2">
                      <h5 className="text-sm font-medium text-white truncate">
                        {branch.name}
                      </h5>
                      {branch.required && (
                        <span className="text-xs px-2 py-1 bg-red-900/30 text-red-300 rounded">
                          Required
                        </span>
                      )}
                    </div>
                    {branch.description && (
                      <p className="text-xs text-gray-400 mt-1 line-clamp-2">
                        {branch.description}
                      </p>
                    )}
                    
                    {/* Value Display */}
                    {branch.completed && branch.value && (
                      <div className="mt-2">
                        <span className="text-xs text-gray-300">
                          Current: <span className="font-medium text-white">{branch.value}</span>
                        </span>
                      </div>
                    )}
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <StatusIcon className="h-5 w-5 flex-shrink-0" />
                  <button
                    onClick={() => handleBranchToggle(branch.id)}
                    className={`p-1 rounded transition-colors ${
                      branch.completed 
                        ? 'hover:bg-red-900/30 text-red-400' 
                        : 'hover:bg-green-900/30 text-green-400'
                    }`}
                    title={branch.completed ? 'Mark as incomplete' : 'Mark as complete'}
                  >
                    {branch.completed ? (
                      <Minus className="h-4 w-4" />
                    ) : (
                      <Plus className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </div>
            );
          })}

          {/* Summary */}
          {completionStatus && (
            <div className="mt-4 p-3 bg-gray-900/50 rounded-lg border border-gray-600">
              <div className="flex items-center justify-between">
                <div className="text-sm text-gray-300">
                  <span className="font-medium">Completion Status:</span>
                  <span className={`ml-2 font-bold ${getCompletionColor()}`}>
                    {completionStatus.percentage}%
                  </span>
                </div>
                <div className="text-xs text-gray-400">
                  {completionStatus.completed} of {completionStatus.total} branches configured
                </div>
              </div>
              
              {completionStatus.status !== 'complete' && (
                <div className="mt-2 text-xs text-yellow-300">
                  ⚠️ Incomplete security configuration may increase risk
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default NodeBranchVisualizer;