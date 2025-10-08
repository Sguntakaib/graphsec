import React, { useState, useRef, useMemo, useCallback, memo } from 'react';
import { Handle, Position } from '@xyflow/react';
import { 
  Shield, 
  Server, 
  AlertTriangle, 
  Lock, 
  Network, 
  Activity,
  Globe,
  Database,
  HardDrive,
  Cloud,
  Monitor,
  Container,
  Zap,
  Users,
  Settings,
  Eye,
  FileText,
  Cpu,
  Wifi,
  Router,
  Bug
} from 'lucide-react';

// Icon mapping - moved outside component to prevent recreation
const ICON_MAP = {
  'Actor': Shield,
  'Asset': Server,
  'Surface': AlertTriangle,
  'Control': Lock,
  'Zone': Network,
  'Signal': Activity
};

// Class mapping - moved outside component to prevent recreation
const CLASS_MAP = {
  'Actor': 'node-actor',
  'Asset': 'node-asset',
  'Surface': 'node-surface',
  'Control': 'node-control',
  'Zone': 'node-zone',
  'Signal': 'node-signal'
};

const CustomNode = memo(({ data, selected, id }) => {
  const [tapCount, setTapCount] = useState(0);
  const tapTimer = useRef(null);
  
  // Memoized icon component to prevent recreation
  const IconComponent = useMemo(() => {
    return ICON_MAP[data.type] || Shield;
  }, [data.type]);

  // Memoized node class to prevent string concatenation on every render
  const nodeClassName = useMemo(() => {
    const baseClass = CLASS_MAP[data.type] || 'bg-gray-600';
    return `simple-node ${baseClass} ${selected ? 'selected' : ''} cursor-pointer`;
  }, [data.type, selected]);

  // Memoized click handler to prevent recreation
  const handleNodeClick = useCallback((event) => {
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
  }, [id, data]);

  // Memoized hover handler to prevent recreation
  const handleNodeHover = useCallback((event) => {
    event.stopPropagation();
    const rect = event.currentTarget.getBoundingClientRect();
    
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
  }, [id, data]);

  // Memoized hover end handler to prevent recreation
  const handleNodeHoverEnd = useCallback((event) => {
    event.stopPropagation();
    const customEvent = new CustomEvent('nodeHoverEnd', {
      detail: { nodeId: id }
    });
    window.dispatchEvent(customEvent);
  }, [id]);

  return (
    <div 
      className={nodeClassName}
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
});

// Add display name for better debugging
CustomNode.displayName = 'CustomNode';

export { CustomNode };