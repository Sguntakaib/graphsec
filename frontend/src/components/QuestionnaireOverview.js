import React, { useState, useEffect } from 'react';
import { 
  Shield, 
  Edit3, 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  Clock,
  FileText,
  X
} from 'lucide-react';

const QuestionnaireOverview = ({ 
  node, 
  diagram, 
  isVisible, 
  onClose, 
  onEdit 
}) => {
  const [questionnaireData, setQuestionnaireData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isVisible && node && diagram) {
      fetchQuestionnaireData();
    }
  }, [isVisible, node, diagram]);

  const fetchQuestionnaireData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/diagrams/${diagram.id}/nodes/${node.id}/questionnaire`
      );
      
      if (!response.ok) {
        throw new Error(`Failed to fetch questionnaire data: ${response.statusText}`);
      }
      
      const data = await response.json();
      setQuestionnaireData(data);
    } catch (err) {
      console.error('Error fetching questionnaire data:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getAnswerDisplay = (prompt, response) => {
    if (response === null || response === undefined) {
      return <span className="text-gray-400 italic">Not answered</span>;
    }

    if (prompt.type === 'boolean') {
      return (
        <div className="flex items-center space-x-2">
          {response ? (
            <>
              <CheckCircle className="h-4 w-4 text-green-400" />
              <span className="text-green-400">Yes</span>
            </>
          ) : (
            <>
              <XCircle className="h-4 w-4 text-red-400" />
              <span className="text-red-400">No</span>
            </>
          )}
        </div>
      );
    }

    if (prompt.type === 'multiple_choice' && Array.isArray(response)) {
      return (
        <div className="space-y-1">
          {response.map((item, index) => (
            <span key={index} className="inline-block bg-blue-900/30 text-blue-300 px-2 py-1 rounded text-sm mr-2">
              {item}
            </span>
          ))}
        </div>
      );
    }

    return <span className="text-white">{String(response)}</span>;
  };

  const getCompletionStatus = () => {
    if (!questionnaireData) return { percentage: 0, color: 'gray' };
    
    const percentage = Math.round((questionnaireData.completed_questions / questionnaireData.total_questions) * 100);
    
    let color = 'gray';
    if (percentage >= 80) color = 'green';
    else if (percentage >= 50) color = 'yellow';
    else if (percentage > 0) color = 'orange';
    else color = 'red';
    
    return { percentage, color };
  };

  if (!isVisible) return null;

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-gray-800 rounded-lg p-6 flex items-center space-x-4">
          <div className="animate-spin h-6 w-6 border-2 border-blue-400 border-t-transparent rounded-full"></div>
          <span className="text-white">Loading questionnaire overview...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-gray-800 rounded-lg p-6 max-w-md">
          <div className="flex items-center space-x-3 mb-4">
            <XCircle className="h-6 w-6 text-red-400" />
            <h3 className="text-lg font-semibold text-white">Error Loading Overview</h3>
          </div>
          <p className="text-gray-300 mb-4">{error}</p>
          <div className="flex space-x-3">
            <button
              onClick={fetchQuestionnaireData}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Retry
            </button>
            <button
              onClick={onClose}
              className="flex-1 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    );
  }

  const completionStatus = getCompletionStatus();

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gray-800 rounded-lg shadow-2xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="border-b border-gray-700 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <Shield className="h-6 w-6 text-blue-400" />
              <h2 className="text-xl font-bold text-white">Security Questionnaire Overview</h2>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-white transition-colors"
            >
              <X className="h-6 w-6" />
            </button>
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm text-gray-300 mb-1">
                Node: <span className="font-semibold text-blue-400">{node.data?.label || node.id}</span>
              </div>
              <div className="text-sm text-gray-300">
                Type: <span className="font-semibold text-green-400">{questionnaireData?.node_subtype}</span>
              </div>
            </div>
            
            <div className="text-right">
              <div className={`text-lg font-bold ${
                completionStatus.color === 'green' ? 'text-green-400' :
                completionStatus.color === 'yellow' ? 'text-yellow-400' :
                completionStatus.color === 'orange' ? 'text-orange-400' :
                'text-red-400'
              }`}>
                {completionStatus.percentage}% Complete
              </div>
              <div className="text-sm text-gray-400">
                {questionnaireData?.completed_questions || 0} of {questionnaireData?.total_questions || 0} answered
              </div>
            </div>
          </div>
          
          {/* Progress Bar */}
          <div className="mt-4">
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div 
                className={`h-2 rounded-full transition-all duration-300 ${
                  completionStatus.color === 'green' ? 'bg-green-600' :
                  completionStatus.color === 'yellow' ? 'bg-yellow-600' :
                  completionStatus.color === 'orange' ? 'bg-orange-600' :
                  'bg-red-600'
                }`}
                style={{ width: `${completionStatus.percentage}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          {questionnaireData?.prompts && questionnaireData.prompts.length > 0 ? (
            <div className="space-y-6">
              {questionnaireData.prompts.map((prompt, index) => {
                const response = questionnaireData.questionnaire_responses?.[prompt.id];
                const isAnswered = response !== null && response !== undefined;
                
                return (
                  <div 
                    key={prompt.id}
                    className={`border rounded-lg p-4 ${
                      isAnswered ? 'border-gray-600 bg-gray-900/50' : 'border-orange-600/50 bg-orange-900/10'
                    }`}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="text-sm font-medium text-gray-400">Q{index + 1}</span>
                          {isAnswered ? (
                            <CheckCircle className="h-4 w-4 text-green-400" />
                          ) : (
                            <AlertTriangle className="h-4 w-4 text-orange-400" />
                          )}
                        </div>
                        <h3 className="text-white font-medium mb-2">
                          {prompt.question}
                        </h3>
                        {prompt.help_text && (
                          <p className="text-sm text-gray-400 mb-3">
                            {prompt.help_text}
                          </p>
                        )}
                      </div>
                    </div>
                    
                    <div className="ml-6">
                      <div className="flex items-center space-x-2">
                        <span className="text-sm font-medium text-gray-300">Answer:</span>
                        {getAnswerDisplay(prompt, response)}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-center py-12">
              <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-white mb-2">No Questionnaire Data</h3>
              <p className="text-gray-400">
                This node doesn't have any questionnaire data yet.
              </p>
            </div>
          )}
          
          {/* Last Updated */}
          {node.data?.lastQuestionnaireUpdate && (
            <div className="mt-6 pt-4 border-t border-gray-700">
              <div className="flex items-center space-x-2 text-sm text-gray-400">
                <Clock className="h-4 w-4" />
                <span>
                  Last updated: {new Date(node.data.lastQuestionnaireUpdate).toLocaleString()}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-gray-700 p-6">
          <div className="flex justify-between items-center">
            <div className="text-sm text-gray-400">
              Double-tap any node to view its questionnaire overview
            </div>
            <div className="flex space-x-3">
              <button
                onClick={onClose}
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
              >
                Close
              </button>
              <button
                onClick={() => onEdit && onEdit(node)}
                className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Edit3 className="h-4 w-4" />
                <span>Edit Questionnaire</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuestionnaireOverview;