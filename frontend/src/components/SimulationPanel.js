import React from 'react';
import { Activity, AlertTriangle, CheckCircle, ExternalLink, TrendingUp } from 'lucide-react';

const SimulationPanel = ({ result }) => {
  if (!result) return null;

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

  return (
    <div className="p-4 bg-gray-900 border-b border-gray-700">
      <div className="flex items-center space-x-2 mb-4">
        <Activity className="h-5 w-5 text-red-400" />
        <h3 className="text-white font-medium">Simulation Results</h3>
      </div>

      {/* Risk Score */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-300">Overall Risk Score</span>
          <span className={getRiskScoreClass(result.risk_score)}>
            {getRiskScoreLabel(result.risk_score)} ({result.risk_score.toFixed(1)}/10)
          </span>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-2">
          <div
            className={`h-2 rounded-full ${
              result.risk_score <= 3 ? 'bg-green-500' :
              result.risk_score <= 6 ? 'bg-yellow-500' : 'bg-red-500'
            }`}
            style={{ width: `${(result.risk_score / 10) * 100}%` }}
          />
        </div>
      </div>

      {/* Attack Paths */}
      {result.attack_paths && result.attack_paths.length > 0 && (
        <div className="mb-6">
          <div className="flex items-center space-x-2 mb-3">
            <TrendingUp className="h-4 w-4 text-red-400" />
            <h4 className="text-sm font-medium text-white">Attack Paths Identified</h4>
            <span className="px-2 py-1 bg-red-900 bg-opacity-50 text-red-300 text-xs rounded">
              {result.attack_paths.length}
            </span>
          </div>
          
          <div className="space-y-3">
            {result.attack_paths.map((path, index) => (
              <div key={index} className="bg-gray-800 border border-gray-600 rounded-lg p-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-white">Path {index + 1}</span>
                  <div className="flex space-x-2">
                    <span className={`px-2 py-1 text-xs rounded ${
                      path.likelihood === 'High' ? 'bg-red-900 text-red-300' :
                      path.likelihood === 'Medium' ? 'bg-yellow-900 text-yellow-300' :
                      'bg-green-900 text-green-300'
                    }`}>
                      {path.likelihood} Likelihood
                    </span>
                    <span className={`px-2 py-1 text-xs rounded ${
                      path.impact === 'High' ? 'bg-red-900 text-red-300' :
                      path.impact === 'Medium' ? 'bg-yellow-900 text-yellow-300' :
                      'bg-green-900 text-green-300'
                    }`}>
                      {path.impact} Impact
                    </span>
                  </div>
                </div>
                
                <div className="space-y-2">
                  {path.steps.map((step, stepIndex) => (
                    <div key={stepIndex} className="bg-gray-700 rounded p-2">
                      <div className="flex items-center space-x-2">
                        <span className="text-xs bg-gray-600 text-gray-300 px-2 py-1 rounded">
                          {stepIndex + 1}
                        </span>
                        <div>
                          <div className="text-sm text-white font-medium">{step.node}</div>
                          <div className="text-xs text-gray-300">{step.action}</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* MITRE ATT&CK Techniques */}
      {result.mitre_techniques && result.mitre_techniques.length > 0 && (
        <div className="mb-6">
          <div className="flex items-center space-x-2 mb-3">
            <AlertTriangle className="h-4 w-4 text-orange-400" />
            <h4 className="text-sm font-medium text-white">MITRE ATT&CK Techniques</h4>
          </div>
          
          <div className="flex flex-wrap gap-2">
            {result.mitre_techniques.map((technique) => (
              <a
                key={technique}
                href={getMitreUrl(technique)}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center space-x-1 px-3 py-1 bg-orange-900 bg-opacity-30 border border-orange-500 border-opacity-30 rounded text-orange-300 hover:bg-opacity-50 transition-colors"
              >
                <span className="text-xs font-mono">{technique}</span>
                <ExternalLink className="h-3 w-3" />
              </a>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {result.recommendations && result.recommendations.length > 0 && (
        <div className="mb-6">
          <div className="flex items-center space-x-2 mb-3">
            <CheckCircle className="h-4 w-4 text-green-400" />
            <h4 className="text-sm font-medium text-white">Security Recommendations</h4>
          </div>
          
          <div className="space-y-2">
            {result.recommendations.map((recommendation, index) => (
              <div key={index} className="bg-gray-800 border border-gray-600 rounded-lg p-3">
                <div className="text-sm text-green-100">{recommendation}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* No Results Message */}
      {(!result.attack_paths || result.attack_paths.length === 0) && (
        <div className="text-center py-8">
          <CheckCircle className="h-12 w-12 text-green-400 mx-auto mb-4" />
          <div className="text-white font-medium mb-2">No Attack Paths Found</div>
          <div className="text-gray-400 text-sm">
            The current security model shows no direct attack paths. Consider adding more elements to create a more comprehensive model.
          </div>
        </div>
      )}

      {/* Simulation Metadata */}
      <div className="mt-6 pt-4 border-t border-gray-700">
        <div className="text-xs text-gray-400">
          <div>Simulation ID: {result.id}</div>
          <div>Generated: {new Date(result.created_at).toLocaleString()}</div>
        </div>
      </div>
    </div>
  );
};

export { SimulationPanel };