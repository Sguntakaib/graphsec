import React, { useState, useRef, useCallback, useEffect } from 'react';
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
  const [isDragging, setIsDragging] = useState(false);
  const [recentlyInteracted, setRecentlyInteracted] = useState(false);
  const dragStartRef = useRef({ x: 0, y: 0, initialLabelPos: null });
  
  // Label editing state
  const [isEditingLabel, setIsEditingLabel] = useState(false);
  const [editingLabelValue, setEditingLabelValue] = useState(label || '');
  const inputRef = useRef(null);
  
  // Refs to track current control point values for use in event handlers
  const controlPoint1Ref = useRef(controlPoint1);
  const controlPoint2Ref = useRef(controlPoint2);

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

  // Mouse event handlers for label-based curve reshaping
  const handleLabelMouseDown = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    e.nativeEvent.stopImmediatePropagation(); // Stop React Flow from handling this
    
    console.log('🎯 Starting label drag for curve reshaping');
    setIsDragging(true);
    setRecentlyInteracted(true);
    
    const labelPos = getLabelPositionOnPath(labelPosition);
    dragStartRef.current = {
      x: e.clientX,
      y: e.clientY,
      initialLabelPos: { ...labelPos }
    };
    
    const handleMouseMove = (e) => {
      e.preventDefault();
      e.stopPropagation();
      
      const currentMouseX = e.clientX;
      const currentMouseY = e.clientY;
      
      // Calculate how much the mouse has moved from the label's initial position
      const dx = currentMouseX - dragStartRef.current.x;
      const dy = currentMouseY - dragStartRef.current.y;
      
      // Calculate new target position for the label (where user is dragging to)
      const newLabelPosX = dragStartRef.current.initialLabelPos.x + dx;
      const newLabelPosY = dragStartRef.current.initialLabelPos.y + dy;
      
      // Calculate control points that would make the curve pass through this point
      // Using simple symmetric control point adjustment
      const curvatureFactor = 0.3;
      const midX = (sourceX + targetX) / 2;
      const midY = (sourceY + targetY) / 2;
      
      // How far is the new label position from the straight line?
      const offsetFromMidX = newLabelPosX - midX;
      const offsetFromMidY = newLabelPosY - midY;
      
      // Adjust control points to create curve that passes through the dragged position
      const newCp1 = {
        x: offsetFromMidX * curvatureFactor,
        y: offsetFromMidY * curvatureFactor
      };
      
      const newCp2 = {
        x: offsetFromMidX * curvatureFactor,
        y: offsetFromMidY * curvatureFactor
      };
      
      setControlPoint1(newCp1);
      setControlPoint2(newCp2);
      
      // Update refs to track current values for use in handleMouseUp
      controlPoint1Ref.current = newCp1;
      controlPoint2Ref.current = newCp2;
    };
    
    const handleMouseUp = (e) => {
      e.preventDefault();
      e.stopPropagation();
      
      console.log('🎯 Completing label drag - curve reshaped');
      setIsDragging(false);
      
      // Trigger edge update event with current ref values (not stale closure values)
      window.dispatchEvent(new CustomEvent('edgeUpdate', {
        detail: {
          edgeId: id,
          updateData: {
            controlPoint1: controlPoint1Ref.current,
            controlPoint2: controlPoint2Ref.current,
            labelPosition: 0.5
          }
        }
      }));
      
      document.removeEventListener('mousemove', handleMouseMove, true);
      document.removeEventListener('mouseup', handleMouseUp, true);
    };
    
    // Use capture phase to intercept events before React Flow can handle them
    document.addEventListener('mousemove', handleMouseMove, true);
    document.addEventListener('mouseup', handleMouseUp, true);
  }, [id, controlPoint1, controlPoint2, sourceX, sourceY, targetX, targetY, labelPosition]);

  // Label editing handlers
  const handleLabelDoubleClick = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    console.log('🏷️ Starting label edit mode');
    setIsEditingLabel(true);
    setEditingLabelValue(label || '');
  }, [label]);

  const handleLabelSave = useCallback(() => {
    console.log('💾 Saving label:', editingLabelValue);
    setIsEditingLabel(false);
    
    // Trigger edge update event with new label
    window.dispatchEvent(new CustomEvent('edgeUpdate', {
      detail: {
        edgeId: id,
        updateData: {
          label: editingLabelValue,
          controlPoint1: controlPoint1Ref.current,
          controlPoint2: controlPoint2Ref.current,
          labelPosition: 0.5
        }
      }
    }));
  }, [id, editingLabelValue]);

  const handleLabelCancel = useCallback(() => {
    console.log('❌ Canceling label edit');
    setIsEditingLabel(false);
    setEditingLabelValue(label || '');
  }, [label]);

  const handleLabelKeyDown = useCallback((e) => {
    if (e.key === 'Enter') {
      handleLabelSave();
    } else if (e.key === 'Escape') {
      handleLabelCancel();
    }
  }, [handleLabelSave, handleLabelCancel]);

  // Effect to manage temporary control point visibility after interaction
  useEffect(() => {
    if (recentlyInteracted) {
      const timer = setTimeout(() => {
        setRecentlyInteracted(false);
      }, 3000); // Keep control points visible for 3 seconds after interaction
      
      return () => clearTimeout(timer);
    }
  }, [recentlyInteracted]);

  // Effect to keep refs in sync with state
  useEffect(() => {
    controlPoint1Ref.current = controlPoint1;
    controlPoint2Ref.current = controlPoint2;
  }, [controlPoint1, controlPoint2]);

  // Effect to focus input when editing starts
  useEffect(() => {
    if (isEditingLabel && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [isEditingLabel]);

  // Styles
  const labelBoxStyle = {
    fill: labelBgStyle.fill || '#374151',
    stroke: '#6B7280',
    strokeWidth: 1,
    rx: labelBgBorderRadius,
    ry: labelBgBorderRadius,
    opacity: labelBgStyle.fillOpacity || 0.9
  };

  const labelTextStyle = {
    fill: labelStyle.fill || '#FFFFFF',
    fontSize: labelStyle.fontSize || '12px',
    fontWeight: labelStyle.fontWeight || 'bold',
    textAnchor: 'middle',
    dominantBaseline: 'central',
    pointerEvents: 'none'
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
          cursor: 'pointer',
          ...style
        }}
        markerEnd={markerEnd}
        className="react-flow__edge-path"
      />
      
      {/* Invisible wider path for easier clicking */}
      <path
        d={customPath}
        style={{
          fill: 'none',
          stroke: 'transparent',
          strokeWidth: Math.max(12, (style.strokeWidth || 2) + 8),
          cursor: 'pointer'
        }}
        className="react-flow__edge-interaction"
      />
      
      {/* Draggable label for curve reshaping */}
      {label && (
        <g 
          transform={`translate(${labelPos.x}, ${labelPos.y})`}
          style={{ cursor: isDragging ? 'grabbing' : 'grab' }}
          onMouseDown={handleLabelMouseDown}
          onMouseMove={(e) => {
            // Prevent event bubbling during mouse move
            if (isDragging) {
              e.preventDefault();
              e.stopPropagation();
            }
          }}
          onContextMenu={(e) => {
            // Prevent context menu when dragging
            e.preventDefault();
            e.stopPropagation();
          }}
        >
          {labelShowBg && (
            <rect
              x={-40}
              y={-12}
              width={80}
              height={24}
              {...labelBoxStyle}
              style={{ 
                ...labelBoxStyle, 
                cursor: isDragging ? 'grabbing' : 'grab',
                stroke: isDragging ? '#3B82F6' : (selected ? '#60A5FA' : '#6B7280'),
                strokeWidth: isDragging || selected ? 2 : 1,
                fill: isDragging ? '#1E3A8A' : labelBgStyle.fill || '#374151',
                pointerEvents: 'all' // Ensure the rect can receive mouse events
              }}
            />
          )}
          <text
            {...labelTextStyle}
            style={{ 
              ...labelTextStyle, 
              cursor: isDragging ? 'grabbing' : 'grab',
              pointerEvents: 'none',
              fill: isDragging ? '#60A5FA' : (labelStyle.fill || '#FFFFFF')
            }}
          >
            {label}
          </text>
          
          {/* Visual hint when selected or recently interacted */}
          {(selected || recentlyInteracted) && (
            <text
              x={0}
              y={30}
              textAnchor="middle"
              style={{
                fill: '#3B82F6',
                fontSize: '10px',
                opacity: 0.7,
                pointerEvents: 'none'
              }}
            >
              ← Drag to reshape →
            </text>
          )}
        </g>
      )}
      
      {/* Visual indicators when dragging */}
      {isDragging && (
        <>
          {/* Show control points when dragging for visual feedback */}
          <circle
            cx={cp1.x}
            cy={cp1.y}
            r={4}
            fill="#3B82F6"
            opacity={0.6}
          />
          <circle
            cx={cp2.x}
            cy={cp2.y}
            r={4}
            fill="#3B82F6"
            opacity={0.6}
          />
          {/* Helper lines */}
          <line
            x1={sourceX}
            y1={sourceY}
            x2={cp1.x}
            y2={cp1.y}
            stroke="#3B82F6"
            strokeWidth={1}
            strokeDasharray="3,3"
            opacity={0.4}
          />
          <line
            x1={cp2.x}
            y1={cp2.y}
            x2={targetX}
            y2={targetY}
            stroke="#3B82F6"
            strokeWidth={1}
            strokeDasharray="3,3"
            opacity={0.4}
          />
        </>
      )}
    </g>
  );
};

export default DraggableEdge;