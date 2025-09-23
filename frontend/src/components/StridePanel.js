import React, { useState, useEffect } from 'react';
import { Shield, AlertTriangle, Eye, EyeOff, Filter, Play, CheckCircle, Circle, Clock, RefreshCw } from 'lucide-react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';

const StridePanel = ({ diagramId, onAnalyzeStride }) => {
  const [threats, setThreats] = useState([]);
  const [coverage, setCoverage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [hasAnalysis, setHasAnalysis] = useState(false);

  const strideCategories = [
    'Spoofing',
    'Tampering',
    'Repudiation', 
    'Information Disclosure',
    'Denial of Service',
    'Elevation of Privilege'
  ];

  const categoryColors = {
    'Spoofing': 'bg-red-900 text-red-300 border-red-700',
    'Tampering': 'bg-orange-900 text-orange-300 border-orange-700',
    'Repudiation': 'bg-yellow-900 text-yellow-300 border-yellow-700',
    'Information Disclosure': 'bg-blue-900 text-blue-300 border-blue-700',
    'Denial of Service': 'bg-purple-900 text-purple-300 border-purple-700',
    'Elevation of Privilege': 'bg-pink-900 text-pink-300 border-pink-700'
  };

  const statusIcons = {
    open: <Circle className="h-3 w-3 text-red-400" />,
    mitigated: <CheckCircle className="h-3 w-3 text-green-400" />,
    partial: <Clock className="h-3 w-3 text-yellow-400" />
  };

  // Load existing analysis on mount
  useEffect(() => {
    if (diagramId) {
      loadStrideCoverage();
    }
  }, [diagramId]);

  const loadStrideCoverage = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/diagrams/${diagramId}/stride/coverage`);
      
      if (response.ok) {
        const coverageData = await response.json();
        setCoverage(coverageData);
        
        // If there are threats, load them too
        if (coverageData.total_threats > 0) {
          setHasAnalysis(true);
          // Load the actual threats
          const threatsResponse = await fetch(`${backendUrl}/api/diagrams/${diagramId}/stride/threats`);
          if (threatsResponse.ok) {
            const threatsData = await threatsResponse.json();
            setThreats(threatsData.threats || []);
          }
        }
      }
    } catch (error) {
      console.error('Error loading STRIDE coverage:', error);
    }
  };

  const runStrideAnalysis = async () => {
    if (!diagramId) return;
    
    setLoading(true);
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/diagrams/${diagramId}/stride/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setThreats(data.threats || []);
        setHasAnalysis(true);
        
        // Reload coverage
        await loadStrideCoverage();
        
        if (onAnalyzeStride) {
          onAnalyzeStride(data);
        }
      } else {
        console.error('STRIDE analysis failed');
      }
    } catch (error) {
      console.error('Error running STRIDE analysis:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateThreatStatus = async (threatId, status) => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/diagrams/${diagramId}/stride/threats/${threatId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status })
      });
      
      if (response.ok) {
        // Update local state
        setThreats(prev => prev.map(t => 
          t.id === threatId ? { ...t, status } : t
        ));
        // Reload coverage to update metrics
        await loadStrideCoverage();
      }
    } catch (error) {
      console.error('Error updating threat status:', error);
    }
  };

  const filteredThreats = threats.filter(threat => {
    if (selectedCategory !== 'all' && threat.stride_category !== selectedCategory) {
      return false;
    }
    if (selectedStatus !== 'all' && threat.status !== selectedStatus) {
      return false;
    }
    return true;
  });

  const getRiskColor = (risk) => {
    if (risk >= 8) return 'text-red-400';
    if (risk >= 6) return 'text-orange-400';
    if (risk >= 4) return 'text-yellow-400';
    return 'text-green-400';
  };

  // Empty state when no analysis has been run
  if (!hasAnalysis) {
    return (
      <div className="p-4 bg-gray-800">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Shield className="h-4 w-4 text-blue-400" />
            <h3 className="font-medium text-white text-sm">STRIDE Analysis</h3>
          </div>
        </div>

        <div className="text-center py-8">
          <Shield className="h-16 w-16 text-gray-600 mx-auto mb-4" />
          <h4 className="text-gray-300 font-medium mb-2">No STRIDE Analysis</h4>
          <p className="text-gray-500 text-sm mb-6">
            Run STRIDE threat analysis to identify security threats across all categories
          </p>
          <Button
            onClick={runStrideAnalysis}
            disabled={loading || !diagramId}
            className="bg-blue-600 hover:bg-blue-700 text-white"
          >
            {loading ? (
              <>
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Play className="h-4 w-4 mr-2" />
                Analyze STRIDE Now
              </>
            )}
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800">
      {/* Header */}
      <div className="p-3 bg-gradient-to-r from-gray-800 to-gray-700 border-b border-gray-600">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <Shield className="h-4 w-4 text-blue-400" />
            <h3 className="font-medium text-white text-sm">STRIDE Analysis</h3>
            <Badge variant="secondary" className="bg-blue-900 text-blue-300 text-xs h-5 px-2">
              {threats.length}
            </Badge>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={runStrideAnalysis}
            disabled={loading}
            className="text-gray-400 hover:text-white h-6 px-2"
          >
            {loading ? (
              <RefreshCw className="h-3 w-3 animate-spin" />
            ) : (
              <RefreshCw className="h-3 w-3" />
            )}
          </Button>
        </div>

        {/* STRIDE Categories Overview */}
        {coverage && (
          <div className="grid grid-cols-3 gap-1 text-xs">
            {strideCategories.map(category => (
              <div key={category} className="text-center">
                <div className={`px-1 py-1 rounded text-xs ${categoryColors[category]}`}>
                  {coverage.totals[category] || 0}
                </div>
                <div className="text-gray-400 text-xs mt-1 truncate" title={category}>
                  {category.split(' ')[0]}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Coverage Summary */}
        {coverage && (
          <div className="mt-3 text-xs text-gray-300">
            <div className="flex justify-between">
              <span>Risk Avg:</span>
              <span className={getRiskColor(coverage.residual_risk_avg)}>
                {coverage.residual_risk_avg}/10
              </span>
            </div>
            <div className="flex justify-between">
              <span>Mitigated:</span>
              <span className="text-green-400">{coverage.mitigation_percentage}%</span>
            </div>
          </div>
        )}
      </div>

      {/* Filters */}
      <div className="p-2 bg-gray-800 border-b border-gray-700">
        <div className="flex space-x-2 mb-2">
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="flex-1 bg-gray-700 border border-gray-600 rounded px-2 py-1 text-xs text-white"
          >
            <option value="all">All Categories</option>
            {strideCategories.map(category => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>
        </div>
        <div className="flex space-x-2">
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="flex-1 bg-gray-700 border border-gray-600 rounded px-2 py-1 text-xs text-white"
          >
            <option value="all">All Status</option>
            <option value="open">Open</option>
            <option value="partial">Partial</option>
            <option value="mitigated">Mitigated</option>
          </select>
        </div>
      </div>

      {/* Threats List */}
      <div className="max-h-64 overflow-y-auto">
        {filteredThreats.length === 0 ? (
          <div className="p-4 text-center">
            <p className="text-gray-500 text-sm">No threats match current filters</p>
          </div>
        ) : (
          filteredThreats.map(threat => (
            <div key={threat.id} className="p-3 border-b border-gray-700 hover:bg-gray-750">
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-1">
                    {statusIcons[threat.status]}
                    <span className="text-white text-xs font-medium truncate">
                      {threat.title}
                    </span>
                  </div>
                  <Badge 
                    className={`text-xs ${categoryColors[threat.stride_category]} mb-1`}
                  >
                    {threat.stride_category}
                  </Badge>
                </div>
                <div className="flex flex-col items-end space-y-1">
                  <span className={`text-xs font-medium ${getRiskColor(threat.residual_risk)}`}>
                    {threat.residual_risk}/10
                  </span>
                  <select
                    value={threat.status}
                    onChange={(e) => updateThreatStatus(threat.id, e.target.value)}
                    className="bg-gray-700 border border-gray-600 rounded px-1 py-0 text-xs text-white"
                  >
                    <option value="open">Open</option>
                    <option value="partial">Partial</option>
                    <option value="mitigated">Mitigated</option>
                  </select>
                </div>
              </div>
              
              <p className="text-gray-400 text-xs mb-2 leading-relaxed">
                {threat.description}
                {threat.references && Array.isArray(threat.references.derived_from) && threat.references.derived_from.length > 0 && (
                  <div className="mt-2 text-xs text-gray-400">
                    <span className="text-gray-500">Derived from:</span>
                    <ul className="list-disc ml-4 mt-1">
                      {threat.references.derived_from.slice(0, 3).map((line, i) => (
                        <li key={i}>{line}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </p>
              
              {threat.mitigations && threat.mitigations.length > 0 && (
                <div className="text-xs">
                  <span className="text-gray-500">Mitigations:</span>
                  <ul className="text-gray-400 mt-1">
                    {threat.mitigations.slice(0, 2).map((mitigation, index) => (
                      <li key={index} className="truncate">• {mitigation}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default StridePanel;