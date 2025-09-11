import React, { useState } from 'react';
import { 
  Activity, 
  AlertTriangle, 
  CheckCircle, 
  ExternalLink, 
  TrendingUp, 
  Shield,
  Target,
  Eye,
  BarChart3,
  ChevronDown,
  ChevronRight,
  Info
} from 'lucide-react';

const EnhancedSimulationPanel = ({ result, onHighlightPath }) => {
  const [expandedPaths, setExpandedPaths] = useState({});
  const [selectedTab, setSelectedTab] = useState('overview');

  if (!result) return null;

  const togglePathExpansion = (index) => {
    setExpandedPaths(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  const getRiskScoreClass = (score) => {
    if (score <= 3) return 'risk-score low';
    if (score <= 6) return 'risk-score medium';
    return 'risk-score high';
  };

  const getRiskScoreLabel = (score) => {
    if (score <= 3) return 'Low';
    if (score <= 6) return 'Medium';
    return 'High';
  };

  const getMitreUrl = (id) => `https://attack.mitre.org/techniques/${id.replace('.', '/')}/`;

  const renderOverviewTab = () => (
    <div className="space-y-4">
      {/* Risk Score Section */}
      <div className="bg-gray-800 rounded-lg p-4">
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm text-gray-300 flex items-center">
            <BarChart3 className="h-4 w-4 mr-2" />
            Overall Risk Assessment
          </span>
          <span className={getRiskScoreClass(result.risk_score)}>
            {result.overall_risk_level} ({result.risk_score}/10)
          </span>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-3 mb-2">
          <div
            className={`h-3 rounded-full transition-all duration-500 ${
              result.risk_score <= 3 ? 'bg-green-500' :
              result.risk_score <= 6 ? 'bg-yellow-500' : 'bg-red-500'
            }`}
            style={{ width: `${(result.risk_score / 10) * 100}%` }}
          />
        </div>
        <div className="text-xs text-gray-400">
          Detection Coverage: {result.detection_coverage}%
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-gray-800 rounded-lg p-3">
          <div className="text-red-400 text-xl font-bold">{result.attack_paths?.length || 0}</div>
          <div className="text-xs text-gray-400">Attack Paths</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-3">
          <div className="text-orange-400 text-xl font-bold">{result.mitre_techniques?.length || 0}</div>
          <div className="text-xs text-gray-400">MITRE Techniques</div>
        </div>
      </div>

      {/* MITRE Coverage */}
      {result.mitre_coverage && (
        <div className="bg-gray-800 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-3">
            <Shield className="h-4 w-4 text-blue-400" />
            <span className="text-sm font-medium text-white">MITRE ATT&CK Coverage</span>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-xs text-gray-400">Tactics Covered</span>
              <span className="text-xs text-white">{result.mitre_coverage.tactics_covered?.length || 0}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-xs text-gray-400">Detection Difficulty</span>
              <span className="text-xs text-white">
                {Math.round((result.mitre_coverage.detection_difficulty || 0) * 100)}%
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderAttackPathsTab = () => (
    <div className="space-y-3">
      {result.attack_paths && result.attack_paths.length > 0 ? (
        result.attack_paths.map((path, index) => (
          <div key={index} className="attack-path">
            <div 
              className="flex items-center justify-between cursor-pointer"
              onClick={() => togglePathExpansion(index)}
            >
              <div className="flex items-center space-x-2">
                {expandedPaths[index] ? 
                  <ChevronDown className="h-4 w-4 text-gray-400" /> : 
                  <ChevronRight className="h-4 w-4 text-gray-400" />
                }
                <span className="text-sm font-medium text-white">Attack Path {index + 1}</span>
              </div>
              <div className="flex space-x-2">
                <span className={`px-2 py-1 text-xs rounded ${
                  path.likelihood === 'High' ? 'bg-red-900 text-red-300' :
                  path.likelihood === 'Medium' ? 'bg-yellow-900 text-yellow-300' :
                  'bg-green-900 text-green-300'
                }`}>
                  {path.likelihood}
                </span>
                <span className="px-2 py-1 text-xs rounded bg-gray-700 text-gray-300">
                  Risk: {path.risk_score}/10
                </span>
              </div>
            </div>
            
            {expandedPaths[index] && (
              <div className="mt-3 space-y-2">
                {path.steps?.map((step, stepIndex) => (
                  <div key={stepIndex} className="attack-path-step">
                    <div className="flex items-start space-x-3">
                      <span className="text-xs bg-gray-600 text-gray-300 px-2 py-1 rounded min-w-max">
                        Step {stepIndex + 1}
                      </span>
                      <div className="flex-1">
                        <div className="text-sm text-white font-medium">{step.action}</div>
                        {step.mitre_id && (
                          <div className="flex items-center space-x-2 mt-1">
                            <span className="text-xs bg-orange-900 text-orange-300 px-2 py-1 rounded font-mono">
                              {step.mitre_id}
                            </span>
                            <span className="text-xs text-gray-400">
                              Detection: {step.detection_likelihood}%
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
                
                {path.mitre_techniques && path.mitre_techniques.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-700">
                    <div className="text-xs text-gray-400 mb-2">MITRE Techniques Used:</div>
                    <div className="flex flex-wrap gap-1">
                      {path.mitre_techniques.map((tech) => (
                        <a
                          key={tech}
                          href={getMitreUrl(tech)}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="px-2 py-1 bg-orange-900 bg-opacity-30 border border-orange-500 border-opacity-30 rounded text-orange-300 hover:bg-opacity-50 transition-colors text-xs"
                        >
                          {tech}
                        </a>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        ))
      ) : (
        <div className="text-center py-8">
          <Target className="h-12 w-12 text-green-400 mx-auto mb-4" />
          <div className="text-white font-medium mb-2">No Attack Paths Detected</div>
          <div className="text-gray-400 text-sm">
            Your current security posture shows no viable attack paths.
          </div>
        </div>
      )}
    </div>
  );

  const renderTechniquesTab = () => (
    <div className="space-y-3">
      {result.technique_details && Object.keys(result.technique_details).length > 0 ? (
        Object.entries(result.technique_details).map(([techId, details]) => (
          <div key={techId} className="bg-gray-800 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <span className="text-sm font-mono text-orange-300">{techId}</span>
                <span className={`px-2 py-1 text-xs rounded ${
                  details.impact_level === 'HIGH' ? 'bg-red-900 text-red-300' :
                  details.impact_level === 'MEDIUM' ? 'bg-yellow-900 text-yellow-300' :
                  'bg-blue-900 text-blue-300'
                }`}>
                  {details.impact_level}
                </span>
              </div>
              <a
                href={getMitreUrl(techId)}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-400 hover:text-blue-300"
              >
                <ExternalLink className="h-4 w-4" />
              </a>
            </div>
            
            <div className="text-sm font-medium text-white mb-2">{details.name}</div>
            <div className="text-xs text-gray-300 mb-3 line-clamp-2">{details.description}</div>
            
            {details.tactics && details.tactics.length > 0 && (
              <div className="mb-3">
                <div className="text-xs text-gray-400 mb-1">Tactics:</div>
                <div className="flex flex-wrap gap-1">
                  {details.tactics.map((tactic) => (
                    <span key={tactic} className="px-2 py-1 bg-purple-900 bg-opacity-30 text-purple-300 text-xs rounded">
                      {tactic}
                    </span>
                  ))}
                </div>
              </div>
            )}
            
            {details.detection_methods && details.detection_methods.length > 0 && (
              <div className="mb-3">
                <div className="text-xs text-gray-400 mb-1">Detection Methods:</div>
                <ul className="text-xs text-gray-300 space-y-1">
                  {details.detection_methods.map((method, index) => (
                    <li key={index} className="flex items-start space-x-2">
                      <Eye className="h-3 w-3 text-blue-400 mt-0.5 flex-shrink-0" />
                      <span>{method}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {details.mitigations && details.mitigations.length > 0 && (
              <div>
                <div className="text-xs text-gray-400 mb-1">Mitigations:</div>
                <ul className="text-xs text-gray-300 space-y-1">
                  {details.mitigations.map((mitigation, index) => (
                    <li key={index} className="flex items-start space-x-2">
                      <Shield className="h-3 w-3 text-green-400 mt-0.5 flex-shrink-0" />
                      <span>{mitigation}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))
      ) : (
        <div className="text-center py-8">
          <Info className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <div className="text-white font-medium mb-2">No Technique Details</div>
          <div className="text-gray-400 text-sm">
            Run a simulation to see detailed MITRE ATT&CK technique analysis.
          </div>
        </div>
      )}
    </div>
  );

  const renderRecommendationsTab = () => (
    <div className="space-y-3">
      {result.recommendations && result.recommendations.length > 0 ? (
        result.recommendations.map((recommendation, index) => (
          <div key={index} className="recommendation">
            <div className="flex items-start space-x-3">
              <CheckCircle className="h-4 w-4 text-green-400 mt-0.5 flex-shrink-0" />
              <div className="text-sm text-green-100">{recommendation}</div>
            </div>
          </div>
        ))
      ) : (
        <div className="text-center py-8">
          <CheckCircle className="h-12 w-12 text-green-400 mx-auto mb-4" />
          <div className="text-white font-medium mb-2">No Recommendations</div>
          <div className="text-gray-400 text-sm">
            Your security posture looks good! No immediate recommendations.
          </div>
        </div>
      )}
      
      {result.suggested_controls && result.suggested_controls.length > 0 && (
        <div className="mt-6">
          <div className="text-sm font-medium text-white mb-3 flex items-center">
            <Shield className="h-4 w-4 text-blue-400 mr-2" />
            Suggested Additional Controls
          </div>
          <div className="space-y-2">
            {result.suggested_controls.map((control, index) => (
              <div key={index} className="bg-blue-900 bg-opacity-20 border border-blue-500 border-opacity-30 rounded p-3">
                <div className="text-sm text-blue-100">{control}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  const tabs = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'paths', label: 'Attack Paths', icon: TrendingUp },
    { id: 'techniques', label: 'MITRE Details', icon: AlertTriangle },
    { id: 'recommendations', label: 'Recommendations', icon: CheckCircle }
  ];

  return (
    <div className="p-4">
      <div className="flex items-center space-x-2 mb-4">
        <Activity className="h-5 w-5 text-red-400" />
        <h3 className="text-white font-medium">Advanced Analysis Results</h3>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 mb-4 bg-gray-800 rounded-lg p-1">
        {tabs.map((tab) => {
          const IconComponent = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setSelectedTab(tab.id)}
              className={`flex items-center space-x-2 px-3 py-2 rounded-md transition-colors text-sm ${
                selectedTab === tab.id
                  ? 'bg-gray-700 text-white'
                  : 'text-gray-400 hover:text-white hover:bg-gray-700'
              }`}
            >
              <IconComponent className="h-4 w-4" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {selectedTab === 'overview' && renderOverviewTab()}
        {selectedTab === 'paths' && renderAttackPathsTab()}
        {selectedTab === 'techniques' && renderTechniquesTab()}
        {selectedTab === 'recommendations' && renderRecommendationsTab()}
      </div>

      {/* Simulation Metadata */}
      <div className="mt-6 pt-4 border-t border-gray-700">
        <div className="text-xs text-gray-400">
          <div className="flex justify-between">
            <span>Analysis ID: {result.id}</span>
            <span>Generated: {new Date(result.created_at).toLocaleString()}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export { EnhancedSimulationPanel };