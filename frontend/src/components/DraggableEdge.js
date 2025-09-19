import React, { useState, useRef, useCallback } from 'react';
import { getBezierPath, BaseEdge } from '@xyflow/react';

const DraggableEdge = ({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  data = {},
  label,
  labelStyle = {},
  labelBgStyle = {},
  labelShowBg = true,
  labelBgBorderRadius = 4,
  labelBgPadding = [4, 8],
  markerEnd,
  style = {},
  selected = false
}) => {
  // Control points for bezier curve (stored as offset from default position)
  // Initialize with defaults if data is missing
  const [controlPoint1, setControlPoint1] = useState(() => {
    return data?.controlPoint1 || { x: 0, y: 0 };
  });
  const [controlPoint2, setControlPoint2] = useState(() => {
    return data?.controlPoint2 || { x: 0, y: 0 };
  });
  
  // Label position along the path (always centered at 0.5)
  const labelPosition = 0.5; // Fixed at center, no longer draggable

  // Drag state
  const [isDragging, setIsDragging] = useState(null); // 'cp1', 'cp2', 'label', or null
  const dragStartRef = useRef({ x: 0, y: 0, initialValue: null });

  // Calculate default control points for smooth bezier curve
  const getDefaultControlPoints = () => {
    const dx = targetX - sourceX;
    const dy = targetY - sourceY;
    const distance = Math.sqrt(dx * dx + dy * dy);
    const curvature = 0.25;
    
    const defaultCp1 = {
      x: sourceX + dx * curvature,
      y: sourceY + dy * curvature
    };
    
    const defaultCp2 = {
      x: targetX - dx * curvature,
      y: targetY - dy * curvature
    };
    
    return { defaultCp1, defaultCp2 };
  };

  const { defaultCp1, defaultCp2 } = getDefaultControlPoints();
  
  // Actual control point positions (default + user offset)
  const cp1 = {
    x: defaultCp1.x + controlPoint1.x,
    y: defaultCp1.y + controlPoint1.y
  };
  
  const cp2 = {
    x: defaultCp2.x + controlPoint2.x,
    y: defaultCp2.y + controlPoint2.y
  };

  // Get the bezier path
  const [edgePath, labelPosX, labelPosY] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
    curvature: 0.25
  });

  // Calculate custom bezier path with user control points
  const customPath = `M ${sourceX},${sourceY} C ${cp1.x},${cp1.y} ${cp2.x},${cp2.y} ${targetX},${targetY}`;

  // Calculate label position along the custom bezier curve
  const getLabelPositionOnPath = (t) => {
    // Bezier curve formula: B(t) = (1-t)³P₀ + 3(1-t)²tP₁ + 3(1-t)t²P₂ + t³P₃
    const x = Math.pow(1-t, 3) * sourceX + 
              3 * Math.pow(1-t, 2) * t * cp1.x + 
              3 * (1-t) * Math.pow(t, 2) * cp2.x + 
              Math.pow(t, 3) * targetX;
              
    const y = Math.pow(1-t, 3) * sourceY + 
              3 * Math.pow(1-t, 2) * t * cp1.y + 
              3 * (1-t) * Math.pow(t, 2) * cp2.y + 
              Math.pow(t, 3) * targetY;
              
    return { x, y };
  };

  const labelPos = getLabelPositionOnPath(labelPosition);

  // Mouse event handlers
  const handleMouseDown = useCallback((e, type, initialValue) => {
    e.preventDefault();
    e.stopPropagation();
    
    setIsDragging(type);
    dragStartRef.current = {
      x: e.clientX,
      y: e.clientY,
      initialValue: initialValue || { ...labelPos }
    };
    
    // Add global mouse handlers
    const handleMouseMove = (e) => {
      const dx = e.clientX - dragStartRef.current.x;
      const dy = e.clientY - dragStartRef.current.y;
      
      if (type === 'cp1') {
        const newCp1 = {
          x: controlPoint1.x + dx,
          y: controlPoint1.y + dy
        };
        setControlPoint1(newCp1);
      } else if (type === 'cp2') {
        const newCp2 = {
          x: controlPoint2.x + dx,
          y: controlPoint2.y + dy
        };
        setControlPoint2(newCp2);
      } else if (type === 'label') {
        // Labels are no longer draggable - they stay centered at position 0.5
        // This prevents labels from being positioned awkwardly along edges
        console.log('🚫 Label dragging disabled - labels stay centered');
      }
    };
    
    const handleMouseUp = () => {
      setIsDragging(null);
      
      // Instead of calling onEdgeUpdate, we'll trigger a custom event
      // that the parent App component can listen to
      window.dispatchEvent(new CustomEvent('edgeUpdate', {
        detail: {
          edgeId: id,
          updateData: {
            controlPoint1,
            controlPoint2,
            labelPosition: 0.5  // Always keep labels centered
          }
        }
      }));
      
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
    
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  }, [id, controlPoint1, controlPoint2, labelPosition, labelPos]);

  // Styles
  const controlPointStyle = {
    r: 6,
    fill: '#3B82F6',
    stroke: '#1E40AF',
    strokeWidth: 2,
    cursor: 'grab',
    opacity: selected || isDragging ? 1 : 0  // Only show when selected or dragging
  };

  const controlPointHoverStyle = {
    ...controlPointStyle,
    r: 8,
    fill: '#60A5FA'
  };

  const labelBoxStyle = {
    fill: labelBgStyle.fill || '#374151',
    stroke: isDragging === 'label' ? '#3B82F6' : '#6B7280',
    strokeWidth: isDragging === 'label' ? 2 : 1,
    rx: labelBgBorderRadius,
    ry: labelBgBorderRadius,
    opacity: labelBgStyle.fillOpacity || 0.9,
    cursor: 'grab'
  };

  const labelTextStyle = {
    fill: labelStyle.fill || '#FFFFFF',
    fontSize: labelStyle.fontSize || '12px',
    fontWeight: labelStyle.fontWeight || 'bold',
    textAnchor: 'middle',
    dominantBaseline: 'central',
    pointerEvents: 'none',
    cursor: 'grab'
  };

  return (
    <g>
      {/* Main edge path */}
      <path
        id={id}
        d={customPath}
        style={{
          fill: 'none',
          stroke: style.stroke || '#9CA3AF',
          strokeWidth: style.strokeWidth || 2,
          strokeDasharray: style.strokeDasharray,
          ...style
        }}
        markerEnd={markerEnd}
        className="react-flow__edge-path"
      />
      
      {/* Control point 1 */}
      {(selected || isDragging) && (
        <circle
          cx={cp1.x}
          cy={cp1.y}
          {...controlPointStyle}
          onMouseDown={(e) => handleMouseDown(e, 'cp1')}
          onMouseEnter={(e) => {
            e.target.setAttribute('r', controlPointHoverStyle.r);
            e.target.setAttribute('fill', controlPointHoverStyle.fill);
          }}
          onMouseLeave={(e) => {
            e.target.setAttribute('r', controlPointStyle.r);
            e.target.setAttribute('fill', controlPointStyle.fill);
          }}
        />
      )}
      
      {/* Control point 2 */}
      {(selected || isDragging) && (
        <circle
          cx={cp2.x}
          cy={cp2.y}
          {...controlPointStyle}
          onMouseDown={(e) => handleMouseDown(e, 'cp2')}
          onMouseEnter={(e) => {
            e.target.setAttribute('r', controlPointHoverStyle.r);
            e.target.setAttribute('fill', controlPointHoverStyle.fill);
          }}
          onMouseLeave={(e) => {
            e.target.setAttribute('r', controlPointStyle.r);
            e.target.setAttribute('fill', controlPointStyle.fill);
          }}
        />
      )}
      
      {/* Draggable label */}
      {label && (
        <g 
          transform={`translate(${labelPos.x}, ${labelPos.y})`}
          style={{ cursor: isDragging === 'label' ? 'grabbing' : 'grab' }}
        >
          {labelShowBg && (
            <rect
              x={-40}
              y={-12}
              width={80}
              height={24}
              {...labelBoxStyle}
              onMouseDown={(e) => handleMouseDown(e, 'label')}
              onMouseEnter={(e) => {
                if (isDragging !== 'label') {
                  e.target.setAttribute('stroke', '#3B82F6');
                  e.target.setAttribute('stroke-width', '2');
                }
              }}
              onMouseLeave={(e) => {
                if (isDragging !== 'label') {
                  e.target.setAttribute('stroke', '#6B7280');
                  e.target.setAttribute('stroke-width', '1');
                }
              }}
            />
          )}
          <text
            {...labelTextStyle}
            onMouseDown={(e) => handleMouseDown(e, 'label')}
            style={{ 
              ...labelTextStyle, 
              cursor: isDragging === 'label' ? 'grabbing' : 'grab',
              pointerEvents: 'all'  // Allow text to receive mouse events
            }}
          >
            {label}
          </text>
          
          {/* Visual indicator when dragging */}
          {isDragging === 'label' && (
            <circle
              cx={0}
              cy={0}
              r={50}
              fill="none"
              stroke="#3B82F6"
              strokeWidth={2}
              strokeDasharray="4,4"
              opacity={0.3}
            />
          )}
        </g>
      )}
      
      {/* Helper lines (when control points are visible) */}
      {(selected || isDragging) && (
        <>
          <line
            x1={sourceX}
            y1={sourceY}
            x2={cp1.x}
            y2={cp1.y}
            stroke="#3B82F6"
            strokeWidth={1}
            strokeDasharray="3,3"
            opacity={0.5}
          />
          <line
            x1={cp2.x}
            y1={cp2.y}
            x2={targetX}
            y2={targetY}
            stroke="#3B82F6"
            strokeWidth={1}
            strokeDasharray="3,3"
            opacity={0.5}
          />
        </>
      )}
    </g>
  );
};

export default DraggableEdge;