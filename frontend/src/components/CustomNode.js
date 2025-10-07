import React, { useState, useRef } from 'react';
import { Handle, Position } from '@xyflow/react';
import { Shield, Server, AlertTriangle, Lock, Network, Activity } from 'lucide-react';

const CustomNode = ({ data, selected, id }) => {
  const [tapCount, setTapCount] = useState(0);
  const tapTimer = useRef(null);
  const getIcon = (type) => {
    const iconMap = {
      'Actor': Shield,
      'Asset': Server,
      'Surface': AlertTriangle,
      'Control': Lock,
      'Zone': Network,
      'Signal': Activity
    };
    return iconMap[type] || Shield;
  };

  const getNodeClass = (type) => {
    const classMap = {
      'Actor': 'node-actor',
      'Asset': 'node-asset',
      'Surface': 'node-surface',
      'Control': 'node-control',
      'Zone': 'node-zone',
      'Signal': 'node-signal'
    };
    return classMap[type] || 'bg-gray-600';
  };

  const IconComponent = getIcon(data.type);
  const nodeClass = getNodeClass(data.type);

  const handleNodeClick = (event) => {
    event.stopPropagation();
    
    setTapCount(prev => {
      const newCount = prev + 1;
      
      if (tapTimer.current) {
        clearTimeout(tapTimer.current);
      }
      
      tapTimer.current = setTimeout(() => {
        if (newCount === 2) {
          // Double tap detected
          console.log('🎯 Double-tap detected on node:', id, 'with data:', data);
          const customEvent = new CustomEvent('nodeDoubleTap', {
            detail: { nodeId: id, nodeData: data }
          });
          window.dispatchEvent(customEvent);
        }
        setTapCount(0);
      }, 300); // 300ms window for double tap
      
      return newCount;
    });
  };

  const handleNodeHover = (event) => {
    event.stopPropagation();
    const rect = event.currentTarget.getBoundingClientRect();
    
    console.log('🎯 Node hover detected on node:', id, 'with data:', data);
    const customEvent = new CustomEvent('nodeHover', {
      detail: { 
        nodeId: id, 
        nodeData: data,
        position: {
          x: rect.right,
          y: rect.top + rect.height / 2
        }
      }
    });
    window.dispatchEvent(customEvent);
  };

  const handleNodeHoverEnd = (event) => {
    event.stopPropagation();
    const customEvent = new CustomEvent('nodeHoverEnd', {
      detail: { nodeId: id }
    });
    window.dispatchEvent(customEvent);
  };

  return (
    <div 
      className={`simple-node ${nodeClass} ${selected ? 'selected' : ''} cursor-pointer`}
      data-subtype={data.subtype}
      onClick={handleNodeClick}
      onMouseEnter={handleNodeHover}
      onMouseLeave={handleNodeHoverEnd}
    >
      <Handle type="target" position={Position.Top} className="simple-handle" />
      
      <div className="simple-node-content">
        <IconComponent className="simple-node-icon" />
        <span className="simple-node-label">{data.label}</span>
      </div>
      
      <Handle type="source" position={Position.Bottom} className="simple-handle" />
    </div>
  );
};

export { CustomNode };