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
  User,
  Cloud,
  Container,
  Zap,
  Users,
  Settings,
  Eye,
  FileText,
  Cpu,
  Wifi,
  Router,
  Bug,
  Lock,
  Network,
  Activity
} from 'lucide-react';

const NodeInfoPanel = ({ nodes, selectedNode, onEditQuestionnaire }) => {
  const [questionsData, setQuestionsData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeNode, setActiveNode] = useState(null);
  const [typeFilter, setTypeFilter] = useState('All');
  const [completionFilter, setCompletionFilter] = useState('All'); // All | Complete | Partial | Not Started
  const [searchText, setSearchText] = useState('');
  const [sortBy, setSortBy] = useState('Type'); // Type | Completion | Recently Updated

  const getCompletionPercent = (node) => {
    const answers = node.data?.questionnaireResponses || {};
    const answered = Object.keys(answers).filter(k => answers[k] !== null && answers[k] !== undefined && answers[k] !== '').length;
    const subtype = node.data?.subtype;
    const comprehensiveTypes = ['WebApp','API','Database','Backup','Monitoring'];
    let total = 0;
    if (comprehensiveTypes.includes(subtype) && node.data?.questionnaireMeta?.total_questions) {
      total = node.data.questionnaireMeta.total_questions;
    } else {
      // heuristic fallbacks
      if (subtype === 'WebApp') total = 10;
      else if (subtype === 'API') total = 7;
      else if (subtype === 'Database') total = 10;
      else if (subtype === 'Backup') total = 5;
      else if (subtype === 'Monitoring') total = 5;
      else total = Math.max(5, Object.keys(answers).length || 5);
    }
    if (total === 0) return 0;
    return Math.min(100, Math.round((answered / total) * 100));
  };

  useEffect(() => {
    if (activeNode && (activeNode.data?.subtype || activeNode.subtype)) {
      fetchNodeQuestionsAndAnswers();
    } else {
      setQuestionsData(null);
    }
  }, [activeNode, activeNode?.data?.questionnaireResponses, activeNode?.questionnaireResponses, activeNode?.data?.lastQuestionnaireUpdate]);

  const fetchNodeQuestionsAndAnswers = async () => {
    if (!activeNode?.data?.subtype) return;
    
    setLoading(true);
    try {
      // First, try to get questions for this node type
      let questionsResponse;
      const nodeSubtype = activeNode.data.subtype;
      
      if (['WebApp','API','Database','Backup','Monitoring'].includes(nodeSubtype)) {
        questionsResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/questionnaires/${nodeSubtype}?level=basic`);
      } else {
        questionsResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/intelligent-nodes/${nodeSubtype}/prompts`);
      }
      
      if (!questionsResponse.ok && ['WebApp','API','Database','Backup','Monitoring'].includes(nodeSubtype)) {
        // Fallback to intelligent-nodes prompts if comprehensive endpoint is unavailable
        try {
          const fallback = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/intelligent-nodes/${nodeSubtype}/prompts`);
          questionsResponse = fallback;
        } catch (e) {
          console.warn('Fallback fetch failed:', e);
        }
      }

      if (questionsResponse.ok) {
        const questionsDataJson = await questionsResponse.json();
        const questions = questionsDataJson.prompts || [];
        
        // Get user answers from node data - try multiple possible sources
        // Merge possible locations for stored answers (root and data)
        let userAnswers = {
          ...(activeNode.questionnaireResponses || {}),
          ...(activeNode.data?.questionnaireResponses || {})
        };
        
        // If no questionnaire responses in node data, try to fetch from backend
        if (Object.keys(userAnswers).length === 0 && (activeNode.data?.subtype || activeNode.subtype)) {
          try {
            const diagramId = window.location.pathname.includes('/diagram/') ? 
              window.location.pathname.split('/diagram/')[1] : null;
            
            if (diagramId) {
              const answersResponse = await fetch(
                `${process.env.REACT_APP_BACKEND_URL}/api/diagrams/${diagramId}/nodes/${activeNode.id}/questionnaire`
              );
              
              if (answersResponse.ok) {
                const answersData = await answersResponse.json();
                userAnswers = answersData.questionnaire_responses || {};
                console.log('📊 Fetched questionnaire responses from backend:', userAnswers);
              }
            }
          } catch (error) {
            console.log('ℹ️ Could not fetch backend questionnaire responses:', error.message);
          }
        }
        
        // Combine questions with answers
        const combinedData = questions.map(question => ({
          ...question,
          userAnswer: userAnswers[question.id] || null
        }));
        
        // Calculate answered questions based on actual questions, not all userAnswers keys
        const answeredCount = combinedData.filter(q => {
          const answer = userAnswers[q.id];
          return answer !== null && answer !== undefined && answer !== '';
        }).length;
        
        setQuestionsData({
          questions: combinedData,
          totalQuestions: questions.length,
          answeredQuestions: answeredCount,
          completionPercentage: questions.length > 0 ? Math.round((answeredCount / questions.length) * 100) : 0
        });
      }
    } catch (error) {
      console.error('Error fetching node questions:', error);
    } finally {
      setLoading(false);
    }
  };

  const getNodeIcon = (subtype) => {
    // Enhanced subtype-specific icon mapping matching CustomNode
    const iconMap = {
      // Actor subtypes
      'ExternalAttacker': Shield,
      'Insider': Users,
      'ServiceAccount': Settings,
      
      // Infrastructure subtypes  
      'CloudDeployment': Cloud,
      'OnPremisesDeployment': Server,
      
      // Service subtypes
      'AWSService': Cloud,
      'GCPService': Cloud,
      
      // Asset subtypes
      'WebApp': Globe,
      'API': Zap,
      'Database': Database,
      'S3Bucket': HardDrive,
      'VM': Monitor,
      'IMDS': FileText,
      
      // Surface subtypes (Attack Surfaces)
      'SSRF': Bug,
      'SQLi': Database,
      'IDOR': Lock,
      'RCE': Cpu,
      'WeakIAM': Users,
      
      // Control subtypes (Security Controls)
      'WAF': Shield,
      'EDR': Eye,
      'EgressProxy': Router,
      'IAMPolicy': Users,
      'NetworkACL': Network,
      
      // Zone subtypes
      'Internet': Globe,
      'DMZ': Network,
      'Internal': Lock,
      'CloudVPC': Cloud,
      
      // Signal subtypes
      'WAFAlert': Shield,
      'EDRAlert': Eye,
      'NetworkLog': Activity,
      
      // Additional subtypes for dynamic nodes
      'Backup': HardDrive,
      'Monitoring': Monitor,
      'Container': Container,
      'LoadBalancer': Router,
      'CDN': Wifi
    };
    return iconMap[subtype] || Server;
  };

  const isGoodSecurityPractice = (answer, question) => {
    // Define good security practices based on question context and answers
    const questionId = question.id?.toLowerCase() || '';
    const questionText = question.question?.toLowerCase() || '';
    
    // Boolean questions - determine if true/false represents good security
    if (typeof answer === 'boolean') {
      // These questions are good when answered 'true'
      if (questionId.includes('encryption') || 
          questionId.includes('mfa') || 
          questionId.includes('backup') ||
          questionId.includes('monitoring') ||
          questionId.includes('logging') ||
          questionId.includes('validation') ||
          questionText.includes('encryption') ||
          questionText.includes('multi-factor') ||
          questionText.includes('backup') ||
          questionText.includes('monitor')) {
        return answer === true;
      }
      
      // These questions are good when answered 'false' 
      if (questionId.includes('anonymous') || 
          questionId.includes('public') ||
          questionText.includes('anonymous') ||
          questionText.includes('public access')) {
        return answer === false;
      }
      
      // Default: true is generally better for security questions
      return answer === true;
    }
    
    // Single choice questions - evaluate based on answer content
    if (question.type === 'single_choice' && typeof answer === 'string') {
      const answerLower = answer.toLowerCase();
      
      // Good security practices
      if (answerLower.includes('oauth') || 
          answerLower.includes('saml') ||
          answerLower.includes('mfa') ||
          answerLower.includes('aes') ||
          answerLower.includes('encrypted') ||
          answerLower.includes('comprehensive') ||
          answerLower.includes('strict') ||
          answerLower.includes('https') ||
          answerLower.includes('tls') ||
          answerLower.includes('regular')) {
        return true;
      }
      
      // Bad security practices
      if (answerLower.includes('none') ||
          answerLower.includes('basic') ||
          answerLower.includes('no encryption') ||
          answerLower.includes('never') ||
          answerLower.includes('minimal') ||
          answerLower.includes('http') ||
          answerLower.includes('plain')) {
        return false;
      }
    }
    
    // Default to neutral if we can't determine
    return null;
  };

  const formatAnswer = (answer, question) => {
    if (answer === null || answer === undefined) {
      return <span className="text-gray-400 italic">Not answered</span>;
    }
    
    const isGoodPractice = isGoodSecurityPractice(answer, question);
    
    if (typeof answer === 'boolean') {
      const bgColor = isGoodPractice === true ? 'bg-green-900 text-green-300 border border-green-700' : 
                     isGoodPractice === false ? 'bg-red-900 text-red-300 border border-red-700' : 
                     'bg-gray-700 text-gray-300 border border-gray-600';
      
      return (
        <span className={`px-2 py-1 rounded text-xs font-medium ${bgColor}`}>
          {answer ? 'Yes' : 'No'}
        </span>
      );
    }
    
    if (question.type === 'single_choice' && question.options) {
      const option = question.options.find(opt => opt.value === answer);
      const displayText = option ? option.label : answer;
      
      const bgColor = isGoodPractice === true ? 'bg-green-900 text-green-300 border border-green-700' : 
                     isGoodPractice === false ? 'bg-red-900 text-red-300 border border-red-700' : 
                     'bg-blue-900 text-blue-300 border border-blue-700';
      
      return (
        <span className={`px-2 py-1 rounded text-xs font-medium ${bgColor}`}>
          {displayText}
        </span>
      );
    }
    
    return <span className="text-gray-300">{String(answer)}</span>;
  };

  const getCompletionStatus = (node) => {
    if (!node.data?.questionnaireResponses) {
      return { icon: XCircle, color: 'text-gray-400', bg: 'bg-gray-800', text: 'Not Started' };
    }
    
    const userAnswers = node.data.questionnaireResponses;
    const answeredCount = Object.keys(userAnswers).filter(key => 
      userAnswers[key] !== null && userAnswers[key] !== undefined && userAnswers[key] !== ''
    ).length;

    // For comprehensive node types, compute against actual question count from backend if available on node
    const subtype = node.data?.subtype;
    const comprehensiveTypes = ['WebApp','API','Database','Backup','Monitoring'];
    if (comprehensiveTypes.includes(subtype) && node.data?.questionnaireMeta?.total_questions) {
      const total = node.data.questionnaireMeta.total_questions;
      if (total > 0) {
        const pct = Math.round((answeredCount / total) * 100);
        if (answeredCount === 0) {
          return { icon: XCircle, color: 'text-gray-400', bg: 'bg-gray-800', text: 'Not Started' };
        }
        if (pct >= 80) return { icon: CheckCircle, color: 'text-green-400', bg: 'bg-green-900', text: 'Complete' };
        if (pct >= 30) return { icon: AlertCircle, color: 'text-yellow-400', bg: 'bg-yellow-900', text: 'Partial' };
        return { icon: XCircle, color: 'text-gray-400', bg: 'bg-gray-800', text: 'Not Started' };
      }
    }
    
    if (answeredCount === 0) {
      return { icon: XCircle, color: 'text-gray-400', bg: 'bg-gray-800', text: 'Not Started' };
    }
    
    // Check if node has completionStatus from intelligent questionnaire system
    if (node.data?.completionStatus?.is_complete) {
      return { icon: CheckCircle, color: 'text-green-400', bg: 'bg-green-900', text: 'Complete' };
    }
    
    // Use a more intelligent threshold based on node type or reasonable defaults
    const nodeSubtype = node.data?.subtype;
    let expectedQuestions = 5; // default
    
    // Set expected question counts based on node type
    if (nodeSubtype === 'WebApp') expectedQuestions = 10;
    else if (nodeSubtype === 'API') expectedQuestions = 7;
    else if (nodeSubtype === 'Database') expectedQuestions = 5;
    else if (nodeSubtype === 'Backup') expectedQuestions = 5;
    else if (nodeSubtype === 'Monitoring') expectedQuestions = 5;
    
    const completionPercentage = (answeredCount / expectedQuestions) * 100;
    
    if (completionPercentage >= 80) { // 80% or more is considered complete
      return { icon: CheckCircle, color: 'text-green-400', bg: 'bg-green-900', text: 'Complete' };
    } else if (completionPercentage >= 30) { // 30% or more is partial
      return { icon: AlertCircle, color: 'text-yellow-400', bg: 'bg-yellow-900', text: 'Partial' };
    } else {
      return { icon: XCircle, color: 'text-gray-400', bg: 'bg-gray-800', text: 'Not Started' };
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
  let availableNodes = (nodes || []).filter(node => 
    node.type !== 'vulnerability' && node.data?.subtype
  );

  // Apply filters
  availableNodes = availableNodes.filter(node => {
    const subtype = node.data?.subtype;
    const label = (node.data?.label || node.id || '').toLowerCase();
    const pct = getCompletionPercent(node);
    const status = pct >= 80 ? 'Complete' : pct >= 30 ? 'Partial' : 'Not Started';

    const typeOk = typeFilter === 'All' || subtype === typeFilter || node.data?.type === typeFilter;
    const completionOk = completionFilter === 'All' || status === completionFilter;
    const searchOk = searchText.trim() === '' || label.includes(searchText.toLowerCase().trim());
    return typeOk && completionOk && searchOk;
  });

  // Sorting
  if (sortBy === 'Type') {
    availableNodes.sort((a, b) => (a.data?.subtype || '').localeCompare(b.data?.subtype || ''));
  } else if (sortBy === 'Completion') {
    availableNodes.sort((a, b) => getCompletionPercent(b) - getCompletionPercent(a));
  } else if (sortBy === 'Recently Updated') {
    availableNodes.sort((a, b) => {
      const aTime = new Date(a.data?.lastQuestionnaireUpdate || a.data?.updated_at || 0).getTime();
      const bTime = new Date(b.data?.lastQuestionnaireUpdate || b.data?.updated_at || 0).getTime();
      return bTime - aTime;
    });
  }

  // Show node details view if activeNode is selected
  if (activeNode) {
    const NodeIcon = getNodeIcon(activeNode.data?.subtype);
    const status = getCompletionStatus(activeNode);

    return (
      <div className="bg-gray-900 h-full">
        {/* Header with Back Button */}
        <div className="p-4 bg-gradient-to-r from-gray-800 to-gray-700 border-b border-gray-600">
          <div className="flex items-center space-x-3">
            <button
              onClick={handleBackToList}
              className="p-2 hover:bg-gray-600 rounded-lg transition-colors"
            >
              <ArrowLeft className="h-4 w-4 text-blue-400" />
            </button>
            <div className="p-2 bg-gray-800 rounded-lg shadow-sm border border-gray-600">
              <NodeIcon className="h-5 w-5 text-blue-400" />
            </div>
            <div className="flex-1">
              <h3 className="font-medium text-white">{activeNode.data?.label || activeNode.id}</h3>
              <p className="text-sm text-gray-300">{activeNode.data?.subtype}</p>
            </div>
            {status && (
              <div className={`flex items-center space-x-1 px-2 py-1 rounded-full ${status.bg}`}>
                <status.icon className={`h-4 w-4 ${status.color}`} />
                <span className={`text-xs font-medium ${status.color}`}>{status.text}</span>
              </div>
            )}
          </div>
        </div>

        {/* Questions and Answers Section */}
        <div className="flex-1 overflow-y-auto">
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin h-6 w-6 border-2 border-blue-400 border-t-transparent rounded-full"></div>
              <span className="ml-3 text-gray-300">Loading questions...</span>
            </div>
          ) : questionsData ? (
            <div className="p-4">
              {/* Progress Info */}
              <div className="mb-6 bg-gray-800 rounded-lg p-4 border border-gray-700">
                <div className="flex items-center justify-between text-sm mb-2">
                  <span className="font-medium text-gray-300">Progress</span>
                  <span className="font-bold text-white">{questionsData.completionPercentage}%</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div 
                    className="bg-blue-500 h-2 rounded-full transition-all duration-300" 
                    style={{ width: `${Math.min(questionsData.completionPercentage, 100)}%` }}
                  ></div>
                </div>
                <div className="mt-2 text-xs text-gray-400">
                  {questionsData.answeredQuestions} of {questionsData.totalQuestions} questions answered
                </div>
              </div>

              {/* Edit Button */}
              <button
                onClick={() => onEditQuestionnaire && onEditQuestionnaire(activeNode)}
                className="w-full mb-6 px-4 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
              >
                Edit Security Configuration
              </button>

              {/* Questions List */}
              <div className="space-y-4">
                <h4 className="font-medium text-white mb-3">Questions & Answers</h4>
                {questionsData.questions.map((question, index) => (
                  <div key={`question-${activeNode.id}-${question.id || index}-${index}`} className="bg-gray-800 border border-gray-700 rounded-lg p-4 shadow-sm">
                    <div className="text-sm font-medium text-white mb-3">
                      {index + 1}. {question.question}
                    </div>
                    <div className="text-sm mb-2">
                      <span className="text-gray-300 font-medium">Answer: </span>
                      {formatAnswer(question.userAnswer, question)}
                    </div>
                    {question.help_text && (
                      <div className="mt-3 p-3 bg-green-900 rounded-md border border-green-700">
                        <div className="flex items-start space-x-2">
                          <Info className="h-4 w-4 text-green-400 mt-0.5 flex-shrink-0" />
                          <span className="text-xs text-green-300">{question.help_text}</span>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
                
                {questionsData.questions.length === 0 && (
                  <div className="text-center py-8 text-gray-400">
                    <Info className="h-8 w-8 mx-auto mb-3 text-gray-500" />
                    <p>No configuration questions available for this node type.</p>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-400">
              <Info className="h-8 w-8 mx-auto mb-3 text-gray-500" />
              <p>Unable to load questions for this node.</p>
            </div>
          )}
        </div>
      </div>
    );
  }

  // Show nodes list view by default
  return (
    <div className="bg-gray-900 h-full">
      {/* Header */}
      <div className="p-4 bg-gradient-to-r from-gray-800 to-gray-700 border-b border-gray-600">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-gray-800 rounded-lg shadow-sm border border-gray-600">
            <User className="h-5 w-5 text-blue-400" />
          </div>
          <div>
            <h3 className="font-medium text-white">Canvas Nodes</h3>
            <p className="text-sm text-gray-300">{availableNodes.length} nodes available</p>
          </div>
        </div>
      </div>

      {/* Filters/Search/Sort */}
      <div className="p-3 border-b border-gray-700 bg-gray-900">
        <div className="grid grid-cols-2 gap-2">
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="px-2 py-2 bg-gray-800 text-gray-100 border border-gray-600 rounded text-sm"
          >
            {['All','WebApp','API','Database','Backup','Monitoring','Surface','Control','Asset'].map(t => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>

          <select
            value={completionFilter}
            onChange={(e) => setCompletionFilter(e.target.value)}
            className="px-2 py-2 bg-gray-800 text-gray-100 border border-gray-600 rounded text-sm"
          >
            {['All','Complete','Partial','Not Started'].map(t => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>

        <div className="mt-2 grid grid-cols-2 gap-2">
          <input
            type="text"
            placeholder="Search by label..."
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            className="px-2 py-2 bg-gray-800 text-gray-100 border border-gray-600 rounded text-sm"
          />

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-2 py-2 bg-gray-800 text-gray-100 border border-gray-600 rounded text-sm"
          >
            {['Type','Completion','Recently Updated'].map(t => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Nodes List */}
      <div className="flex-1 overflow-y-auto">
        {availableNodes.length === 0 ? (
          <div className="text-center py-8 text-gray-400">
            <User className="h-8 w-8 mx-auto mb-3 text-gray-500" />
            <p className="text-sm">No nodes on canvas</p>
            <p className="text-xs text-gray-500 mt-1">Add nodes to see their details here</p>
          </div>
        ) : (
          <div className="p-4 space-y-3">
            {availableNodes.map((node) => {
              const NodeIcon = getNodeIcon(node.data?.subtype);
              const status = getCompletionStatus(node);
              
              return (
                <div
                  key={node.id}
                  onClick={() => handleNodeClick(node)}
                  className="p-4 bg-gray-800 border border-gray-700 rounded-lg hover:border-blue-500 hover:shadow-lg transition-all cursor-pointer group"
                >
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-gray-700 group-hover:bg-blue-900 rounded-lg transition-colors">
                      <NodeIcon className="h-5 w-5 text-gray-300 group-hover:text-blue-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="font-medium text-white truncate">
                        {node.data?.label || node.id}
                      </h4>
                      <p className="text-sm text-gray-300">{node.data?.subtype}</p>
                    </div>
                    {status && (
                      <div className={`flex items-center space-x-1 px-2 py-1 rounded-full ${status.bg}`}>
                        <status.icon className={`h-3 w-3 ${status.color}`} />
                        <span className={`text-xs font-medium ${status.color}`}>{status.text}</span>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default NodeInfoPanel;