import React from 'react';
import { Settings, Tag, Shield, ExternalLink } from 'lucide-react';

const PropertiesPanel = ({ node }) => {
  if (!node) return null;

  const { data } = node;

  const getMitreUrl = (id) => `https://attack.mitre.org/techniques/${id.replace('.', '/')}/`;

  return (
    <div className="p-4 border-b border-gray-700">
      <div className="flex items-center space-x-2 mb-4">
        <Settings className="h-5 w-5 text-gray-400" />
        <h3 className="text-white font-medium">Properties</h3>
      </div>

      <div className="space-y-4">
        {/* Basic Information */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Node Type
          </label>
          <div className="flex items-center space-x-2">
            <span className="px-3 py-1 bg-gray-700 rounded text-sm text-white">
              {data.type}
            </span>
            <span className="px-3 py-1 bg-gray-600 rounded text-sm text-gray-300">
              {data.subtype}
            </span>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Label
          </label>
          <input
            type="text"
            value={data.label || ''}
            readOnly
            className="w-full p-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
          />
        </div>

        {/* Description */}
        {data.description && (
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Description
            </label>
            <div className="p-3 bg-gray-700 rounded text-sm text-gray-300">
              {data.description}
            </div>
          </div>
        )}

        {/* MITRE ATT&CK Techniques */}
        {data.mitre_ids && data.mitre_ids.length > 0 && (
          <div>
            <div className="flex items-center space-x-2 mb-2">
              <Shield className="h-4 w-4 text-red-400" />
              <label className="text-sm font-medium text-gray-300">
                MITRE ATT&CK Techniques
              </label>
            </div>
            <div className="space-y-2">
              {data.mitre_ids.map((id) => (
                <div key={id} className="flex items-center justify-between p-2 bg-gray-700 rounded">
                  <span className="text-sm text-white font-mono">{id}</span>
                  <a
                    href={getMitreUrl(id)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-400 hover:text-blue-300"
                  >
                    <ExternalLink className="h-4 w-4" />
                  </a>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Position Information */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Position
          </label>
          <div className="grid grid-cols-2 gap-2">
            <div>
              <span className="text-xs text-gray-400">X</span>
              <div className="text-sm text-white bg-gray-700 p-2 rounded">
                {Math.round(node.position.x)}
              </div>
            </div>
            <div>
              <span className="text-xs text-gray-400">Y</span>
              <div className="text-sm text-white bg-gray-700 p-2 rounded">
                {Math.round(node.position.y)}
              </div>
            </div>
          </div>
        </div>

        {/* Node ID */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Node ID
          </label>
          <div className="p-2 bg-gray-700 rounded text-xs text-gray-400 font-mono break-all">
            {node.id}
          </div>
        </div>

        {/* Security Context */}
        {(data.type === 'Surface' || data.type === 'Asset') && (
          <div className="p-3 bg-red-900 bg-opacity-20 border border-red-500 border-opacity-30 rounded">
            <div className="flex items-center space-x-2 mb-2">
              <Shield className="h-4 w-4 text-red-400" />
              <span className="text-sm font-medium text-red-300">Security Context</span>
            </div>
            <div className="text-xs text-red-200">
              {data.type === 'Surface' 
                ? 'This represents a potential attack vector that could be exploited by threat actors.'
                : 'This asset may contain sensitive data and should be protected with appropriate controls.'
              }
            </div>
          </div>
        )}

        {data.type === 'Control' && (
          <div className="p-3 bg-blue-900 bg-opacity-20 border border-blue-500 border-opacity-30 rounded">
            <div className="flex items-center space-x-2 mb-2">
              <Lock className="h-4 w-4 text-blue-400" />
              <span className="text-sm font-medium text-blue-300">Control Function</span>
            </div>
            <div className="text-xs text-blue-200">
              This security control helps prevent, detect, or respond to threats targeting your assets.
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export { PropertiesPanel };