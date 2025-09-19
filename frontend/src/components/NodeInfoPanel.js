import React, { useState, useEffect } from 'react';
import { 
  Shield, 
  Database, 
  Globe, 
  Server, 
  Monitor,
  HardDrive,
  CheckCircle,
  XCircle,
  AlertCircle,
  Info,
  ArrowLeft,
  User
} from 'lucide-react';

const NodeInfoPanel = ({ nodes, selectedNode, onEditQuestionnaire }) => {
  const [questionsData, setQuestionsData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeNode, setActiveNode] = useState(null);

  useEffect(() => {
    if (activeNode && activeNode.data?.subtype) {
      fetchNodeQuestionsAndAnswers();
    } else {
      setQuestionsData(null);
    }
  }, [activeNode]);

  const fetchNodeQuestionsAndAnswers = async () => {
    if (!activeNode?.data?.subtype) return;
    
    setLoading(true);
    try {
      // First, try to get questions for this node type
      let questionsResponse;
      const nodeSubtype = activeNode.data.subtype;
      
      if (nodeSubtype === 'WebApp') {
        questionsResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/questionnaires/WebApp?level=basic`);
      } else {
        questionsResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/intelligent-nodes/${nodeSubtype}/prompts`);
      }
      
      if (questionsResponse.ok) {
        const questionsData = await questionsResponse.json();
        const questions = questionsData.prompts || [];
        
        // Get user answers from node data
        const userAnswers = activeNode.data?.questionnaireResponses || {};
        
        // Combine questions with answers
        const combinedData = questions.map(question => ({
          ...question,
          userAnswer: userAnswers[question.id] || null
        }));
        
        setQuestionsData({
          questions: combinedData,
          totalQuestions: questions.length,
          answeredQuestions: Object.keys(userAnswers).filter(key => userAnswers[key] !== null && userAnswers[key] !== undefined).length,
          completionPercentage: questions.length > 0 ? Math.round((Object.keys(userAnswers).filter(key => userAnswers[key] !== null && userAnswers[key] !== undefined).length / questions.length) * 100) : 0
        });
      }
    } catch (error) {
      console.error('Error fetching node questions:', error);
    } finally {
      setLoading(false);
    }
  };

  const getNodeIcon = (subtype) => {
    const iconMap = {
      'WebApp': Globe,
      'API': Server,
      'Database': Database,
      'Backup': HardDrive,
      'Monitoring': Monitor,
      'ExternalAttacker': Shield
    };
    return iconMap[subtype] || Server;
  };

  const formatAnswer = (answer, question) => {
    if (answer === null || answer === undefined) {
      return <span className="text-gray-500 italic">Not answered</span>;
    }
    
    if (typeof answer === 'boolean') {
      return (
        <span className={`px-2 py-1 rounded text-xs font-medium ${
          answer ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        }`}>
          {answer ? 'Yes' : 'No'}
        </span>
      );
    }
    
    if (question.type === 'single_choice' && question.options) {
      const option = question.options.find(opt => opt.value === answer);
      return (
        <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-medium">
          {option ? option.label : answer}
        </span>
      );
    }
    
    return <span className="text-gray-700">{String(answer)}</span>;
  };

  const getCompletionStatus = (node) => {
    if (!node.data?.questionnaireResponses) return null;
    
    const userAnswers = node.data.questionnaireResponses;
    const answeredCount = Object.keys(userAnswers).filter(key => 
      userAnswers[key] !== null && userAnswers[key] !== undefined
    ).length;
    
    if (answeredCount === 0) {
      return { icon: XCircle, color: 'text-gray-500', bg: 'bg-gray-50', text: 'Not Started' };
    } else if (answeredCount >= 5) { // Assuming most questionnaires have around 5-10 questions
      return { icon: CheckCircle, color: 'text-green-600', bg: 'bg-green-50', text: 'Complete' };
    } else {
      return { icon: AlertCircle, color: 'text-yellow-600', bg: 'bg-yellow-50', text: 'Partial' };
    }
  };

  const handleNodeClick = (node) => {
    setActiveNode(node);
  };

  const handleBackToList = () => {
    setActiveNode(null);
    setQuestionsData(null);
  };

  // Filter nodes to only show non-vulnerability nodes with subtypes
  const availableNodes = (nodes || []).filter(node => 
    node.type !== 'vulnerability' && node.data?.subtype
  );

  return (
    <div className="bg-white border-b border-gray-200">
      {/* Header */}
      <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-white rounded-lg shadow-sm">
            <NodeIcon className="h-5 w-5 text-blue-600" />
          </div>
          <div className="flex-1">
            <h3 className="font-medium text-gray-900">{node.data?.label || node.id}</h3>
            <p className="text-sm text-gray-600">{node.data?.subtype}</p>
          </div>
          {status && (
            <div className={`flex items-center space-x-1 px-2 py-1 rounded-full ${status.bg}`}>
              <status.icon className={`h-4 w-4 ${status.color}`} />
              <span className={`text-xs font-medium ${status.color}`}>{status.text}</span>
            </div>
          )}
        </div>
      </div>

      {/* Basic Information */}
      <div className="border-b border-gray-200">
        <button
          onClick={() => toggleSection('basic')}
          className="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-gray-50 transition-colors"
        >
          <span className="font-medium text-gray-900">Basic Information</span>
          {expandedSections.basic ? 
            <ChevronDown className="h-4 w-4 text-gray-500" /> : 
            <ChevronRight className="h-4 w-4 text-gray-500" />
          }
        </button>
        
        {expandedSections.basic && (
          <div className="px-4 pb-4 space-y-2">
            <div className="grid grid-cols-1 gap-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Type:</span>
                <span className="font-medium text-gray-900">{node.data?.type}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Subtype:</span>
                <span className="font-medium text-gray-900">{node.data?.subtype}</span>
              </div>
              {node.data?.category && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Category:</span>
                  <span className="font-medium text-gray-900">{node.data.category}</span>
                </div>
              )}
              {node.data?.description && (
                <div className="mt-2">
                  <span className="text-gray-600 block mb-1">Description:</span>
                  <p className="text-gray-900 text-xs bg-gray-50 p-2 rounded">{node.data.description}</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Questionnaire Information */}
      {questionsData && (
        <div className="border-b border-gray-200">
          <button
            onClick={() => toggleSection('questionnaire')}
            className="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-center space-x-2">
              <span className="font-medium text-gray-900">Security Configuration</span>
              {questionsData.completionPercentage > 0 && (
                <span className="text-xs text-gray-500">
                  ({questionsData.answeredQuestions}/{questionsData.totalQuestions})
                </span>
              )}
            </div>
            {expandedSections.questionnaire ? 
              <ChevronDown className="h-4 w-4 text-gray-500" /> : 
              <ChevronRight className="h-4 w-4 text-gray-500" />
            }
          </button>
          
          {expandedSections.questionnaire && (
            <div className="px-4 pb-4">
              {loading ? (
                <div className="flex items-center justify-center py-4">
                  <div className="animate-spin h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>
                  <span className="ml-2 text-sm text-gray-600">Loading...</span>
                </div>
              ) : (
                <>
                  {/* Progress Bar */}
                  <div className="mb-4">
                    <div className="flex items-center justify-between text-sm mb-1">
                      <span className="text-gray-600">Completion Progress</span>
                      <span className="font-medium text-gray-900">{questionsData.completionPercentage}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                        style={{ width: `${questionsData.completionPercentage}%` }}
                      ></div>
                    </div>
                  </div>

                  {/* Edit Button */}
                  <button
                    onClick={() => onEditQuestionnaire && onEditQuestionnaire(node)}
                    className="w-full mb-4 px-3 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors"
                  >
                    Edit Security Configuration
                  </button>

                  {/* Questions and Answers */}
                  <div className="space-y-3 max-h-64 overflow-y-auto">
                    {questionsData.questions.map((question, index) => (
                      <div key={question.id || index} className="bg-gray-50 rounded p-3">
                        <div className="text-sm font-medium text-gray-900 mb-2">
                          {question.question}
                        </div>
                        <div className="text-sm">
                          {formatAnswer(question.userAnswer, question)}
                        </div>
                        {question.help_text && (
                          <div className="mt-2 text-xs text-gray-600 flex items-start space-x-1">
                            <Info className="h-3 w-3 mt-0.5 flex-shrink-0" />
                            <span>{question.help_text}</span>
                          </div>
                        )}
                      </div>
                    ))}
                    
                    {questionsData.questions.length === 0 && (
                      <div className="text-center py-4 text-gray-500 text-sm">
                        No configuration questions available for this node type.
                      </div>
                    )}
                  </div>
                </>
              )}
            </div>
          )}
        </div>
      )}

      {/* Security Information */}
      {node.data?.securityBranches && (
        <div className="border-b border-gray-200">
          <button
            onClick={() => toggleSection('security')}
            className="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-gray-50 transition-colors"
          >
            <span className="font-medium text-gray-900">Security Branches</span>
            {expandedSections.security ? 
              <ChevronDown className="h-4 w-4 text-gray-500" /> : 
              <ChevronRight className="h-4 w-4 text-gray-500" />
            }
          </button>
          
          {expandedSections.security && (
            <div className="px-4 pb-4">
              <div className="space-y-2">
                {node.data.securityBranches.map((branch, index) => (
                  <div key={index} className="flex items-center justify-between text-sm">
                    <span className="text-gray-700">{branch.type}</span>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      branch.completed ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
                    }`}>
                      {branch.completed ? 'Complete' : 'Pending'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default NodeInfoPanel;