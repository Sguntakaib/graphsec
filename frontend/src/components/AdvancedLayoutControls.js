import React, { useState, useEffect } from 'react';
import { 
  Zap, 
  Settings, 
  BarChart3, 
  Play, 
  RefreshCw,
  ChevronDown,
  ChevronUp,
  Info,
  Sparkles,
  Target,
  Activity
} from 'lucide-react';
import { 
  autoLayoutDiagram, 
  getLayoutAlgorithms, 
  generateLayoutAnimation, 
  getLayoutMetrics, 
  optimizeLayout 
} from '../services/api';

const AdvancedLayoutControls = ({ 
  currentDiagram, 
  nodes, 
  edges,
  setNodes, 
  setEdges,
  isLoading, 
  setIsLoading,
  fitView 
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [algorithms, setAlgorithms] = useState([]);
  const [selectedAlgorithm, setSelectedAlgorithm] = useState('');
  const [metrics, setMetrics] = useState(null);
  const [showMetrics, setShowMetrics] = useState(false);
  const [animationState, setAnimationState] = useState({
    isAnimating: false,
    fromAlgorithm: '',
    toAlgorithm: '',
    currentFrame: 0,
    totalFrames: 0
  });

  // Load available algorithms on component mount
  useEffect(() => {
    if (currentDiagram) {
      loadLayoutAlgorithms();
    }
  }, [currentDiagram]);

  const loadLayoutAlgorithms = async () => {
    try {
      const response = await getLayoutAlgorithms(currentDiagram.id);
      setAlgorithms(response.algorithms || []);
      if (response.algorithms && response.algorithms.length > 0) {
        setSelectedAlgorithm(response.algorithms[0].id);
      }
    } catch (error) {
      console.error('Failed to load layout algorithms:', error);
    }
  };

  const handleAutoLayout = async (algorithm = null) => {
    if (!currentDiagram) return;
    
    setIsLoading(true);
    try {
      const layoutData = await autoLayoutDiagram(currentDiagram.id, algorithm);
      
      // Apply the new positions with enhanced bounds checking
      setNodes((nds) => {
        const layoutPositions = layoutData.layout_positions || {};
        
        return nds.map((node) => {
          const position = layoutPositions[node.id];
          if (position) {
            return {
              ...node,
              position: {
                x: Math.max(0, position.x),
                y: Math.max(0, position.y)
              }
            };
          }
          return node;
        });
      });

      // Update metrics if available
      if (layoutData.metrics) {
        setMetrics(layoutData.metrics);
      }

      // Auto-fit view after layout
      setTimeout(() => {
        fitView({ 
          padding: 0.1,
          includeHiddenNodes: false,
          minZoom: 0.1,
          maxZoom: 1.5
        });
      }, 100);

    } catch (error) {
      console.error('Failed to auto-layout diagram:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleOptimizeLayout = async () => {
    if (!currentDiagram) return;
    
    setIsLoading(true);
    try {
      const result = await optimizeLayout(currentDiagram.id);
      
      if (result.optimized) {
        // Apply the optimized positions
        setNodes((nds) => {
          const layoutPositions = result.layout_positions || {};
          
          return nds.map((node) => {
            const position = layoutPositions[node.id];
            if (position) {
              return {
                ...node,
                position: {
                  x: Math.max(0, position.x),
                  y: Math.max(0, position.y)
                }
              };
            }
            return node;
          });
        });

        // Update metrics
        if (result.metrics) {
          setMetrics(result.metrics);
        }

        // Show success message
        console.log(`Layout optimized with ${result.best_algorithm} (Score: ${result.quality_score})`);

        // Auto-fit view
        setTimeout(() => {
          fitView({ 
            padding: 0.1,
            includeHiddenNodes: false,
            minZoom: 0.1,
            maxZoom: 1.5
          });
        }, 100);
      }
    } catch (error) {
      console.error('Failed to optimize layout:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGetMetrics = async () => {
    if (!currentDiagram) return;
    
    try {
      const metricsData = await getLayoutMetrics(currentDiagram.id, selectedAlgorithm);
      setMetrics(metricsData.metrics);
      setShowMetrics(true);
    } catch (error) {
      console.error('Failed to get layout metrics:', error);
    }
  };

  const handleAnimateLayout = async () => {
    if (!currentDiagram || !selectedAlgorithm) return;
    
    const fromAlg = 'enhanced_smart_hierarchical';
    const toAlg = selectedAlgorithm;
    
    if (fromAlg === toAlg) return;
    
    setAnimationState({
      isAnimating: true,
      fromAlgorithm: fromAlg,
      toAlgorithm: toAlg,
      currentFrame: 0,
      totalFrames: 0
    });

    try {
      const animationData = await generateLayoutAnimation(currentDiagram.id, fromAlg, toAlg, 2.0, 30);
      
      if (animationData.frames && animationData.frames.length > 0) {
        setAnimationState(prev => ({
          ...prev,
          totalFrames: animationData.frames.length
        }));

        // Play animation frames
        for (let i = 0; i < animationData.frames.length; i++) {
          const frame = animationData.frames[i];
          
          setTimeout(() => {
            setNodes((nds) => {
              return nds.map((node) => {
                const position = frame.positions[node.id];
                if (position) {
                  return {
                    ...node,
                    position: {
                      x: Math.max(0, position.x),
                      y: Math.max(0, position.y)
                    }
                  };
                }
                return node;
              });
            });

            setAnimationState(prev => ({
              ...prev,
              currentFrame: i + 1
            }));

            // Animation complete
            if (i === animationData.frames.length - 1) {
              setTimeout(() => {
                setAnimationState({
                  isAnimating: false,
                  fromAlgorithm: '',
                  toAlgorithm: '',
                  currentFrame: 0,
                  totalFrames: 0
                });
              }, 500);
            }
          }, i * (2000 / 30)); // 30 FPS for 2 seconds
        }
      }
    } catch (error) {
      console.error('Failed to animate layout:', error);
      setAnimationState({
        isAnimating: false,
        fromAlgorithm: '',
        toAlgorithm: '',
        currentFrame: 0,
        totalFrames: 0
      });
    }
  };

  const getQualityColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getMetricBadgeColor = (value, type) => {
    switch (type) {
      case 'overlapping':
        return value === 0 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800';
      case 'utilization':
        return value > 0.7 ? 'bg-green-100 text-green-800' : 
               value > 0.4 ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800';
      case 'crossings':
        return value < 5 ? 'bg-green-100 text-green-800' : 
               value < 15 ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-gray-900 border border-gray-700 rounded-lg shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between p-3 border-b border-gray-700">
        <div className="flex items-center space-x-2">
          <Sparkles className="h-5 w-5 text-purple-400" />
          <span className="font-medium text-gray-100">Advanced Layout</span>
        </div>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="p-1 text-gray-300 hover:bg-gray-800 rounded"
        >
          {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
        </button>
      </div>

      {/* Basic Controls */}
      <div className="p-3 space-y-3">
        <div className="flex flex-col gap-3">
          {/* Dropdown selection */}
          {algorithms.length > 0 && (
            <div className="flex items-center gap-2">
              <select
                value={selectedAlgorithm}
                onChange={(e) => setSelectedAlgorithm(e.target.value)}
                className="flex-1 px-2 py-2 bg-gray-800 text-gray-100 border border-gray-600 rounded text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                title={algorithms.find(a => a.id === selectedAlgorithm)?.description || 'Select a layout algorithm'}
              >
                {algorithms.map((alg) => (
                  <option key={alg.id} value={alg.id}>
                    {alg.name}
                  </option>
                ))}
              </select>

              <button
                onClick={() => handleAutoLayout(selectedAlgorithm)}
                disabled={isLoading || !selectedAlgorithm}
                className="px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 flex items-center space-x-1 text-sm"
                title="Apply selected layout"
              >
                <Settings className="h-4 w-4" />
                <span>Apply Layout</span>
              </button>
            </div>
          )}

          {/* Remove Smart Auto and Optimize per request */}
        </div>

        {/* Advanced Controls (expanded) */}
        {isExpanded && algorithms.length > 0 && (
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                About selected algorithm
              </label>
              {selectedAlgorithm && (
                <p className="text-xs text-gray-500">
                  {algorithms.find(a => a.id === selectedAlgorithm)?.description}
                </p>
              )}
            </div>

            <div className="flex items-center space-x-2">
              <button
                onClick={handleAnimateLayout}
                disabled={isLoading || !selectedAlgorithm || animationState.isAnimating}
                className="px-3 py-1.5 bg-orange-600 text-white rounded hover:bg-orange-700 disabled:opacity-50 flex items-center space-x-1 text-sm"
              >
                <Play className="h-4 w-4" />
                <span>Animate</span>
              </button>

              <button
                onClick={handleGetMetrics}
                disabled={isLoading}
                className="px-3 py-1.5 bg-gray-600 text-white rounded hover:bg-gray-700 disabled:opacity-50 flex items-center space-x-1 text-sm"
              >
                <BarChart3 className="h-4 w-4" />
                <span>Metrics</span>
              </button>
            </div>
          </div>
        )}

        {/* Metrics Display */}
        {showMetrics && metrics && (
          <div className="border-t border-gray-200 pt-3 mt-3">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-medium text-gray-900">Layout Quality</h4>
              <button
                onClick={() => setShowMetrics(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ×
              </button>
            </div>
            
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="bg-gray-50 p-2 rounded">
                <div className="font-medium text-gray-700">Nodes</div>
                <div className="text-gray-600">{metrics.total_nodes} total</div>
                <div className="text-gray-600">{metrics.vulnerability_nodes} vulnerabilities</div>
              </div>
              
              <div className="bg-gray-50 p-2 rounded">
                <div className="font-medium text-gray-700">Spacing</div>
                <div className="text-gray-600">{Math.round(metrics.average_spacing)}px avg</div>
                <div className={`${getMetricBadgeColor(metrics.overlapping_nodes, 'overlapping')} px-1 rounded text-xs`}>
                  {metrics.overlapping_nodes} overlaps
                </div>
              </div>
              
              <div className="bg-gray-50 p-2 rounded">
                <div className="font-medium text-gray-700">Canvas</div>
                <div className="text-gray-600">{Math.round(metrics.canvas_utilization * 100)}% used</div>
                <div className="text-gray-600">{metrics.edge_crossings} crossings</div>
              </div>
              
              <div className="bg-gray-50 p-2 rounded">
                <div className="font-medium text-gray-700">Performance</div>
                <div className="text-gray-600">{Math.round(metrics.layout_time * 1000)}ms</div>
                <div className="text-gray-600">{metrics.algorithm_used}</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdvancedLayoutControls;