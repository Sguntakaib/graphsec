import { useEffect, useCallback } from 'react';
import { useQuestionnaire } from '../contexts/QuestionnaireContext';

const CanvasSynchronizer = ({ 
  nodes, 
  setNodes, 
  edges, 
  setEdges, 
  onNodeUpdate,
  onEdgeCreate 
}) => {
  const { state, actions } = useQuestionnaire();
  
  // Apply pending canvas updates
  const applyCanvasUpdates = useCallback(() => {
    const { pendingNodeUpdates, pendingEdgeCreations } = state.canvasUpdates;
    
    if (pendingNodeUpdates.length > 0 || pendingEdgeCreations.length > 0) {
      console.log('🎨 Applying canvas updates:', {
        nodeUpdates: pendingNodeUpdates.length,
        edgeCreations: pendingEdgeCreations.length
      });
      
      // Apply node updates
      pendingNodeUpdates.forEach(update => {
        setNodes(currentNodes => 
          currentNodes.map(node => {
            if (node.id === update.nodeId) {
              const updatedNode = {
                ...node,
                data: {
                  ...node.data,
                  ...update.data,
                  status: update.status,
                  validation: update.validation,
                  lastUpdated: new Date().toISOString(),
                }
              };
              
              // Add visual indicators for completed questionnaires
              if (update.status === 'completed') {
                updatedNode.style = {
                  ...updatedNode.style,
                  border: '2px solid #10B981',
                  boxShadow: '0 0 10px rgba(16, 185, 129, 0.3)',
                };
                
                updatedNode.data.icon = '✅';
              }
              
              // Call external node update handler
              if (onNodeUpdate) {
                onNodeUpdate(updatedNode);
              }
              
              return updatedNode;
            }
            return node;
          })
        );
      });
      
      // Apply edge creations
      pendingEdgeCreations.forEach(edgeCreation => {
        const newEdge = {
          id: `${edgeCreation.from}-${edgeCreation.to}`,
          source: edgeCreation.from,
          target: edgeCreation.to,
          type: 'smoothstep',
          animated: true,
          style: {
            stroke: edgeCreation.type === 'dependency' ? '#3B82F6' : '#6B7280',
            strokeWidth: 2,
          },
          data: {
            type: edgeCreation.type,
            createdBy: 'questionnaire-flow',
            timestamp: new Date().toISOString(),
          },
        };
        
        setEdges(currentEdges => {
          // Check if edge already exists
          const edgeExists = currentEdges.some(edge => edge.id === newEdge.id);
          if (!edgeExists) {
            console.log('🔗 Creating new edge:', newEdge);
            
            // Call external edge creation handler
            if (onEdgeCreate) {
              onEdgeCreate(newEdge);
            }
            
            return [...currentEdges, newEdge];
          }
          return currentEdges;
        });
      });
      
      // Clear pending updates
      actions.applyCanvasUpdates();
    }
  }, [state.canvasUpdates, setNodes, setEdges, onNodeUpdate, onEdgeCreate, actions]);
  
  // Apply canvas highlights
  const applyHighlights = useCallback(() => {
    const { highlightedNodes } = state.canvasUpdates;
    
    if (highlightedNodes.length > 0) {
      setNodes(currentNodes => 
        currentNodes.map(node => {
          const isHighlighted = highlightedNodes.includes(node.id);
          return {
            ...node,
            style: {
              ...node.style,
              opacity: isHighlighted ? 1 : 0.5,
              transform: isHighlighted ? 'scale(1.05)' : 'scale(1)',
              transition: 'all 0.3s ease',
              ...(isHighlighted && {
                border: '2px solid #F59E0B',
                boxShadow: '0 0 20px rgba(245, 158, 11, 0.5)',
              }),
            },
          };
        })
      );
    } else {
      // Clear highlights
      setNodes(currentNodes => 
        currentNodes.map(node => ({
          ...node,
          style: {
            ...node.style,
            opacity: 1,
            transform: 'scale(1)',
            border: node.style?.border?.includes('#F59E0B') ? 'none' : node.style?.border,
            boxShadow: node.style?.boxShadow?.includes('#F59E0B') ? 'none' : node.style?.boxShadow,
          },
        }))
      );
    }
  }, [state.canvasUpdates.highlightedNodes, setNodes]);
  
  // Handle questionnaire flow progress visualization
  const visualizeFlowProgress = useCallback(() => {
    if (!state.isFlowActive) return;
    
    const { rootNode } = state.questionnaireFlow;
    const { questionnaires } = state;
    
    // Highlight nodes based on questionnaire status
    const nodeUpdates = Object.values(questionnaires).map(questionnaire => {
      let highlightColor = '#6B7280'; // Default gray
      let pulseAnimation = false;
      
      switch (questionnaire.status) {
        case 'active':
          highlightColor = '#3B82F6'; // Blue
          pulseAnimation = true;
          break;
        case 'completed':
          highlightColor = '#10B981'; // Green
          break;
        case 'paused':
          highlightColor = '#F59E0B'; // Yellow
          break;
      }
      
      return {
        nodeId: questionnaire.nodeId,
        style: {
          border: `2px solid ${highlightColor}`,
          boxShadow: `0 0 10px ${highlightColor}40`,
          ...(pulseAnimation && {
            animation: 'pulse 2s infinite',
          }),
        },
        data: {
          questionnaireStatus: questionnaire.status,
          progress: questionnaire.progress,
        },
      };
    });
    
    // Apply node updates
    nodeUpdates.forEach(update => {
      setNodes(currentNodes => 
        currentNodes.map(node => {
          if (node.id === update.nodeId) {
            return {
              ...node,
              style: {
                ...node.style,
                ...update.style,
              },
              data: {
                ...node.data,
                ...update.data,
              },
            };
          }
          return node;
        })
      );
    });
  }, [state.isFlowActive, state.questionnaireFlow, state.questionnaires, setNodes]);
  
  // Auto-apply canvas updates when they are queued
  useEffect(() => {
    if (state.canvasUpdates.pendingNodeUpdates.length > 0 || 
        state.canvasUpdates.pendingEdgeCreations.length > 0) {
      const timeout = setTimeout(applyCanvasUpdates, 100);
      return () => clearTimeout(timeout);
    }
  }, [state.canvasUpdates, applyCanvasUpdates]);
  
  // Apply highlights when they change
  useEffect(() => {
    applyHighlights();
  }, [state.canvasUpdates.highlightedNodes, applyHighlights]);
  
  // Visualize flow progress
  useEffect(() => {
    visualizeFlowProgress();
  }, [state.questionnaires, visualizeFlowProgress]);
  
  // Clean up on unmount
  useEffect(() => {
    return () => {
      actions.clearHighlights();
      actions.applyCanvasUpdates();
    };
  }, [actions]);
  
  // This component doesn't render anything - it's just for effects
  return null;
};

export default CanvasSynchronizer;