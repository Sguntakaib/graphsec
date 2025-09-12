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
    
    setTapCount(prev => prev + 1);
    
    if (tapTimer.current) {
      clearTimeout(tapTimer.current);
    }
    
    tapTimer.current = setTimeout(() => {
      if (tapCount + 1 === 2) {
        // Double tap detected
        const customEvent = new CustomEvent('nodeDoubleTap', {
          detail: { nodeId: id, nodeData: data }
        });
        window.dispatchEvent(customEvent);
      }
      setTapCount(0);
    }, 300); // 300ms window for double tap
  };

  return (
    <div 
      className={`react-flow__node-custom ${nodeClass} ${selected ? 'selected' : ''} cursor-pointer`}
      onClick={handleNodeClick}
    >
      <Handle type="target" position={Position.Top} />
      
      <div className="flex items-center justify-center space-x-2">
        <IconComponent className="h-4 w-4" />
        <div className="text-center">
          <div className="font-medium">{data.label}</div>
          {data.subtype && (
            <div className="text-xs opacity-75">{data.subtype}</div>
          )}
        </div>
      </div>
      
      {data.mitre_ids && data.mitre_ids.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-1 justify-center">
          {data.mitre_ids.slice(0, 2).map((id) => (
            <span
              key={id}
              className="px-1 py-0.5 bg-black bg-opacity-20 text-xs rounded"
            >
              {id}
            </span>
          ))}
          {data.mitre_ids.length > 2 && (
            <span className="px-1 py-0.5 bg-black bg-opacity-20 text-xs rounded">
              +{data.mitre_ids.length - 2}
            </span>
          )}
        </div>
      )}
      
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
};

export { CustomNode };