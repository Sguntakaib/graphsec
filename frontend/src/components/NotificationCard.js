import React from 'react';
import { CheckCircle, Info, AlertTriangle, Clock, Users, Target, Lightbulb } from 'lucide-react';

const NotificationCard = ({ 
  title, 
  completion, 
  recommendations, 
  dependentNodes, 
  vulnerabilities, 
  tip, 
  type = 'success' 
}) => {
  const getTypeStyles = () => {
    switch (type) {
      case 'success':
        return {
          bg: 'bg-gray-800 border-green-700',
          headerBg: 'bg-green-900/50',
          headerText: 'text-green-300',
          icon: CheckCircle,
          iconColor: 'text-green-400'
        };
      case 'warning':
        return {
          bg: 'bg-gray-800 border-yellow-700',
          headerBg: 'bg-yellow-900/50',
          headerText: 'text-yellow-300',
          icon: AlertTriangle,
          iconColor: 'text-yellow-400'
        };
      case 'info':
      default:
        return {
          bg: 'bg-gray-800 border-blue-700',
          headerBg: 'bg-blue-900/50',
          headerText: 'text-blue-300',
          icon: Info,
          iconColor: 'text-blue-400'
        };
    }
  };

  const styles = getTypeStyles();
  const Icon = styles.icon;

  return (
    <div className={`${styles.bg} rounded-lg border-2 shadow-lg max-w-md w-full`}>
      {/* Header */}
      <div className={`${styles.headerBg} px-4 py-3 rounded-t-md border-b border-gray-700`}>
        <div className="flex items-center space-x-3">
          <Icon className={`h-5 w-5 ${styles.iconColor}`} />
          <h3 className={`font-semibold ${styles.headerText}`}>{title}</h3>
        </div>
      </div>

      {/* Content */}
      <div className="p-4 space-y-3">
        {/* Completion Status */}
        {completion !== undefined && (
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Target className="h-4 w-4 text-gray-400" />
              <span className="text-sm text-gray-300">Completion</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-16 bg-gray-700 rounded-full h-2">
                <div 
                  className="bg-green-500 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${Math.min(completion, 100)}%` }}
                />
              </div>
              <span className="text-sm font-medium text-white">{completion}%</span>
            </div>
          </div>
        )}

        {/* Recommendations */}
        {recommendations !== undefined && (
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Lightbulb className="h-4 w-4 text-yellow-400" />
              <span className="text-sm text-gray-300">Recommendations</span>
            </div>
            <span className="text-sm font-medium text-white">{recommendations}</span>
          </div>
        )}

        {/* Dependent Nodes */}
        {dependentNodes && dependentNodes > 0 && (
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Users className="h-4 w-4 text-blue-400" />
              <span className="text-sm text-gray-300">Dependent Nodes</span>
            </div>
            <span className="text-sm font-medium text-blue-300">
              {dependentNodes} node{dependentNodes !== 1 ? 's' : ''} will be configured
            </span>
          </div>
        )}

        {/* Vulnerabilities Analysis */}
        {vulnerabilities && (
          <div className="bg-red-900/20 border border-red-800 rounded-md p-3">
            <div className="flex items-center space-x-2 mb-1">
              <AlertTriangle className="h-4 w-4 text-red-400" />
              <span className="text-sm font-medium text-red-300">Security Analysis</span>
            </div>
            <div className="text-xs text-red-200 space-y-1">
              <div>• {vulnerabilities.total} vulnerabilities identified</div>
              <div>• Risk score: {vulnerabilities.riskScore}/10</div>
            </div>
          </div>
        )}

        {/* Tip Section */}
        {tip && (
          <div className="bg-blue-900/20 border border-blue-800 rounded-md p-3">
            <div className="flex items-start space-x-2">
              <Lightbulb className="h-4 w-4 text-blue-400 mt-0.5 flex-shrink-0" />
              <div>
                <span className="text-sm font-medium text-blue-300">Tip: </span>
                <span className="text-xs text-blue-200">{tip}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default NotificationCard;