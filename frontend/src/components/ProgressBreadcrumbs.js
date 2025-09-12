import React from 'react';
import { useQuestionnaire } from '../contexts/QuestionnaireContext';
import { 
  CheckCircle, 
  Circle, 
  Clock, 
  ChevronRight, 
  Play,
  Pause,
  ArrowRight 
} from 'lucide-react';

const ProgressBreadcrumbs = ({ className = '' }) => {
  const { state, computed } = useQuestionnaire();
  
  const { questionnaireFlow, questionnaires, modalStack } = state;
  const { flowProgress, isFlowActive } = computed;
  
  if (!isFlowActive) {
    return null;
  }
  
  // Build breadcrumb items from questionnaire flow
  const buildBreadcrumbItems = () => {
    const items = [];
    
    // Root questionnaire
    if (questionnaireFlow.rootNode) {
      const rootQuestionnaire = questionnaires[questionnaireFlow.rootNode.id];
      items.push({
        id: questionnaireFlow.rootNode.id,
        nodeId: questionnaireFlow.rootNode.id,
        label: questionnaireFlow.rootNode.data?.subtype || questionnaireFlow.rootNode.subtype || 'Root',
        status: rootQuestionnaire?.status || 'pending',
        progress: rootQuestionnaire?.progress || { completionPercentage: 0 },
        isRoot: true,
        level: 0,
      });
    }
    
    // Add dependent questionnaires from modal stack
    modalStack.forEach((modal, index) => {
      if (modal.type === 'questionnaire' && modal.nodeId !== questionnaireFlow.rootNode?.id) {
        const questionnaire = questionnaires[modal.nodeId];
        items.push({
          id: modal.nodeId,
          nodeId: modal.nodeId,
          label: modal.nodeSubtype || questionnaire?.nodeSubtype || 'Dependent',
          status: questionnaire?.status || 'pending',
          progress: questionnaire?.progress || { completionPercentage: 0 },
          isRoot: false,
          level: index + 1,
          parentId: modal.parentId,
        });
      }
    });
    
    return items;
  };
  
  const breadcrumbItems = buildBreadcrumbItems();
  
  const getStatusIcon = (status, progress) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'active':
        return <Play className="w-5 h-5 text-blue-500 animate-pulse" />;
      case 'paused':
        return <Pause className="w-5 h-5 text-yellow-500" />;
      default:
        return <Circle className="w-5 h-5 text-gray-400" />;
    }
  };
  
  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'active':
        return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'paused':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };
  
  const getLevelIndentation = (level) => {
    return level * 20; // 20px per level
  };
  
  return (
    <div className={`bg-gray-900 border-b border-gray-700 p-4 ${className}`}>
      {/* Flow Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
            <span className="text-white font-medium">Questionnaire Flow</span>
          </div>
          {state.isPaused && (
            <div className="flex items-center space-x-1 text-yellow-400">
              <Pause className="w-4 h-4" />
              <span className="text-sm">Paused</span>
            </div>
          )}
        </div>
        
        {/* Overall Progress */}
        <div className="flex items-center space-x-3">
          <span className="text-gray-300 text-sm">
            {questionnaireFlow.completedQuestionnaires} / {questionnaireFlow.totalQuestionnaires} completed
          </span>
          <div className="w-24 h-2 bg-gray-700 rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-blue-500 to-green-500 transition-all duration-500"
              style={{ width: `${flowProgress}%` }}
            />
          </div>
          <span className="text-white font-medium text-sm">{flowProgress}%</span>
        </div>
      </div>
      
      {/* Breadcrumb Trail */}
      <div className="space-y-2">
        {breadcrumbItems.map((item, index) => (
          <div key={item.id}>
            {/* Connector line for dependent questionnaires */}
            {index > 0 && (
              <div 
                className="flex items-center mb-1"
                style={{ marginLeft: `${getLevelIndentation(item.level - 1) + 12}px` }}
              >
                <div className="w-6 h-px bg-gray-600"></div>
                <ArrowRight className="w-4 h-4 text-gray-500" />
              </div>
            )}
            
            {/* Breadcrumb Item */}
            <div 
              className="flex items-center space-x-3"
              style={{ marginLeft: `${getLevelIndentation(item.level)}px` }}
            >
              {/* Status Icon */}
              <div className="flex-shrink-0">
                {getStatusIcon(item.status, item.progress)}
              </div>
              
              {/* Questionnaire Info */}
              <div className={`flex-1 px-3 py-2 rounded-lg border transition-all duration-200 ${getStatusColor(item.status)}`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="font-medium">{item.label}</span>
                    {item.isRoot && (
                      <span className="text-xs px-2 py-1 bg-purple-100 text-purple-600 rounded-full">
                        Root
                      </span>
                    )}
                    {item.level > 0 && (
                      <span className="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded-full">
                        L{item.level}
                      </span>
                    )}
                  </div>
                  
                  {/* Individual Progress */}
                  <div className="flex items-center space-x-2">
                    {item.status !== 'completed' && (
                      <div className="flex items-center space-x-1">
                        <div className="w-16 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-blue-500 transition-all duration-300"
                            style={{ width: `${item.progress.completionPercentage || 0}%` }}
                          />
                        </div>
                        <span className="text-xs">
                          {Math.round(item.progress.completionPercentage || 0)}%
                        </span>
                      </div>
                    )}
                  </div>
                </div>
                
                {/* Progress Details */}
                {item.progress.totalQuestions > 0 && (
                  <div className="mt-1 text-xs text-gray-500">
                    {item.progress.answeredQuestions || 0} / {item.progress.totalQuestions} questions answered
                  </div>
                )}
              </div>
              
              {/* Active Indicator */}
              {state.activeModalId === item.id && (
                <div className="flex-shrink-0">
                  <div className="w-2 h-8 bg-blue-500 rounded-full animate-pulse"></div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
      
      {/* Current Phase Indicator */}
      <div className="mt-4 pt-3 border-t border-gray-700">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center space-x-2 text-gray-400">
            <Clock className="w-4 h-4" />
            <span>Current Phase: {state.currentPhase}</span>
          </div>
          
          {state.dependencies.pendingDependencies.length > 0 && (
            <div className="text-yellow-400">
              {state.dependencies.pendingDependencies.length} pending dependencies
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProgressBreadcrumbs;