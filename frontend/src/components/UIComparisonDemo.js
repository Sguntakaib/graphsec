import React from 'react';
import { Shield, Server, Database, AlertTriangle } from 'lucide-react';

const UIComparisonDemo = () => {
  return (
    <div className="ui-comparison-demo p-6 bg-gray-900 text-white">
      <h2 className="text-2xl font-bold mb-6 text-center">UI Simplification: Before vs After</h2>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Old Complex Style */}
        <div className="comparison-section">
          <h3 className="text-lg font-semibold mb-4 text-red-400">❌ Old Complex Style</h3>
          <div className="space-y-4">
            {/* Old Node Style */}
            <div className="old-node-style">
              <div className="flex items-center space-x-3 p-4 rounded-lg border-2 border-green-500 bg-gradient-to-br from-green-600 to-green-800">
                <Server className="h-5 w-5" />
                <div>
                  <div className="font-medium">Web Application</div>
                  <div className="text-xs opacity-75">Asset</div>
                </div>
              </div>
            </div>
            
            {/* Old Library Item */}
            <div className="old-library-style p-4 rounded-lg bg-green-900 bg-opacity-30 border border-green-500 border-opacity-20">
              <div className="flex items-start space-x-3">
                <Server className="h-5 w-5 mt-0.5" />
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-1">
                    <div className="text-white text-sm font-medium">Web Application</div>
                    <span className="px-1.5 py-0.5 bg-black bg-opacity-20 text-xs rounded text-gray-300">
                      Critical Assets
                    </span>
                  </div>
                  <div className="text-gray-300 text-xs mb-2">
                    Customer-facing or internal web application
                  </div>
                  <div className="flex flex-wrap gap-1">
                    <span className="px-2 py-1 bg-red-900 bg-opacity-30 text-red-300 text-xs rounded">
                      High
                    </span>
                    <span className="px-2 py-1 bg-orange-900 bg-opacity-30 text-orange-300 text-xs rounded">
                      Confidential
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* New Simple Style */}
        <div className="comparison-section">
          <h3 className="text-lg font-semibold mb-4 text-green-400">✅ New Simple Style</h3>
          <div className="space-y-4">
            {/* New Node Style */}
            <div className="simple-node" style={{
              borderRadius: '12px',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              color: 'white',
              fontSize: '13px',
              fontWeight: '500',
              padding: '12px 16px',
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',
              minWidth: '140px',
              textAlign: 'center',
              backdropFilter: 'blur(10px)',
              background: 'rgba(34, 197, 94, 0.9)'
            }}>
              <div className="flex flex-col items-center gap-2">
                <Server className="w-5 h-5" />
                <span>Web Application</span>
              </div>
            </div>
            
            {/* New Library Item */}
            <div className="simple-library-node">
              <Server className="simple-library-icon" />
              <span className="simple-library-label">Web Application</span>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-8 text-center">
        <div className="inline-block p-4 bg-blue-900 bg-opacity-30 border border-blue-500 border-opacity-20 rounded-lg">
          <h4 className="font-semibold text-blue-300 mb-2">Key Improvements</h4>
          <ul className="text-sm text-gray-300 space-y-1">
            <li>• Removed visual clutter and complex gradients</li>
            <li>• Simplified to icon + label format</li>
            <li>• Clean, uniform styling throughout</li>
            <li>• Better drag-and-drop experience</li>
            <li>• Matches modern workflow builder aesthetics</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default UIComparisonDemo;