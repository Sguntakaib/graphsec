import React, { useState, useMemo } from 'react';
import { 
  X, 
  Search, 
  Plus, 
  Shield, 
  Database, 
  Cloud, 
  Server, 
  Globe, 
  Lock,
  Filter,
  Star
} from 'lucide-react';

const NodeCreationModal = ({ isVisible, onClose, onCreateNode, recentNodes = [] }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedNode, setSelectedNode] = useState(null);

  // Node categories with enhanced organization
  const nodeCategories = [
    {
      id: 'assets',
      name: 'Assets',
      icon: Database,
      color: 'text-green-400',
      description: 'Protected resources and systems'
    },
    {
      id: 'threats',
      name: 'Threat Actors',
      icon: Shield,
      color: 'text-red-400', 
      description: 'Potential attackers and threat sources'
    },
    {
      id: 'controls',
      name: 'Security Controls',
      icon: Lock,
      color: 'text-blue-400',
      description: 'Protective measures and defenses'
    },
    {
      id: 'infrastructure',
      name: 'Infrastructure',
      icon: Server,
      color: 'text-purple-400',
      description: 'Network and system components'
    },
    {
      id: 'cloud',
      name: 'Cloud Services',
      icon: Cloud,
      color: 'text-cyan-400',
      description: 'Cloud platforms and services'
    }
  ];

  // Enhanced node types with workflow organization
  const nodeTypes = [
    // Assets
    { 
      type: 'Asset', 
      subtype: 'WebApp', 
      category: 'assets',
      name: 'Web Application',
      description: 'Web-based application or service',
      icon: Globe,
      popular: true
    },
    { 
      type: 'Asset', 
      subtype: 'Database', 
      category: 'assets',
      name: 'Database',
      description: 'Data storage system',
      icon: Database,
      popular: true
    },
    { 
      type: 'Asset', 
      subtype: 'API', 
      category: 'assets',
      name: 'API Endpoint',
      description: 'REST or GraphQL API',
      icon: Server,
      popular: true
    },
    
    // Threat Actors
    { 
      type: 'Actor', 
      subtype: 'ExternalAttacker', 
      category: 'threats',
      name: 'External Attacker',
      description: 'Outside malicious actor',
      icon: Shield,
      popular: true
    },
    { 
      type: 'Actor', 
      subtype: 'Insider', 
      category: 'threats',
      name: 'Malicious Insider',
      description: 'Internal threat actor',
      icon: Shield
    },
    
    // Security Controls
    { 
      type: 'Control', 
      subtype: 'WAF', 
      category: 'controls',
      name: 'Web Application Firewall',
      description: 'HTTP/HTTPS traffic filter',
      icon: Lock,
      popular: true
    },
    { 
      type: 'Control', 
      subtype: 'EDR', 
      category: 'controls',
      name: 'Endpoint Detection',
      description: 'Host-based security monitoring',
      icon: Lock
    },
    
    // Infrastructure
    { 
      type: 'Zone', 
      subtype: 'DMZ', 
      category: 'infrastructure',
      name: 'DMZ Network',
      description: 'Demilitarized network zone',
      icon: Server
    },
    { 
      type: 'Zone', 
      subtype: 'Internal', 
      category: 'infrastructure',
      name: 'Internal Network',
      description: 'Private internal network',
      icon: Server
    },
    
    // Cloud Services
    { 
      type: 'Asset', 
      subtype: 'S3Bucket', 
      category: 'cloud',
      name: 'S3 Storage',
      description: 'AWS S3 bucket storage',
      icon: Cloud
    },
    { 
      type: 'Asset', 
      subtype: 'AWSService', 
      category: 'cloud',
      name: 'AWS Service',
      description: 'Generic AWS cloud service',
      icon: Cloud
    }
  ];

  // Filter nodes based on search and category
  const filteredNodes = useMemo(() => {
    let filtered = nodeTypes;
    
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(node => node.category === selectedCategory);
    }
    
    if (searchTerm) {
      filtered = filtered.filter(node => 
        node.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        node.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        node.subtype.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    return filtered;
  }, [searchTerm, selectedCategory]);

  // Get popular nodes for quick access
  const popularNodes = nodeTypes.filter(node => node.popular);

  const handleCreateNode = () => {
    if (selectedNode && onCreateNode) {
      onCreateNode(selectedNode);
      onClose();
      setSelectedNode(null);
      setSearchTerm('');
      setSelectedCategory('all');
    }
  };

  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-800 rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-700">
          <div>
            <h2 className="text-2xl font-semibold text-white">Add Security Component</h2>
            <p className="text-gray-400 text-sm mt-1">
              Choose a component to add to your threat model
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors p-2 hover:bg-gray-700 rounded-lg"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <div className="flex h-[600px]">
          {/* Sidebar - Categories */}
          <div className="w-64 border-r border-gray-700 bg-gray-750">
            {/* Search */}
            <div className="p-4 border-b border-gray-700">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search components..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-gray-700 text-white placeholder-gray-400 rounded-lg border border-gray-600 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                />
              </div>
            </div>

            {/* Categories */}
            <div className="p-4">
              <div className="space-y-2">
                <button
                  onClick={() => setSelectedCategory('all')}
                  className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors text-left ${
                    selectedCategory === 'all'
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                  }`}
                >
                  <Filter className="h-4 w-4" />
                  <span className="font-medium">All Categories</span>
                </button>
                
                {nodeCategories.map((category) => {
                  const Icon = category.icon;
                  return (
                    <button
                      key={category.id}
                      onClick={() => setSelectedCategory(category.id)}
                      className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors text-left ${
                        selectedCategory === category.id
                          ? 'bg-blue-600 text-white'
                          : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                      }`}
                    >
                      <Icon className={`h-4 w-4 ${selectedCategory === category.id ? 'text-white' : category.color}`} />
                      <div>
                        <div className="font-medium">{category.name}</div>
                        <div className="text-xs text-gray-400">{category.description}</div>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="flex-1 flex flex-col">
            {/* Quick Access - Popular Nodes */}
            {searchTerm === '' && selectedCategory === 'all' && (
              <div className="p-6 border-b border-gray-700">
                <div className="flex items-center space-x-2 mb-4">
                  <Star className="h-5 w-5 text-yellow-400" />
                  <h3 className="text-lg font-semibold text-white">Popular Components</h3>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  {popularNodes.map((node, index) => {
                    const Icon = node.icon;
                    return (
                      <button
                        key={`popular-${index}`}
                        onClick={() => setSelectedNode(node)}
                        className={`p-4 rounded-lg border transition-colors text-left ${
                          selectedNode?.subtype === node.subtype
                            ? 'border-blue-500 bg-blue-500 bg-opacity-10'
                            : 'border-gray-600 hover:border-gray-500 hover:bg-gray-700'
                        }`}
                      >
                        <div className="flex items-center space-x-3">
                          <Icon className="h-6 w-6 text-blue-400" />
                          <div>
                            <div className="font-medium text-white">{node.name}</div>
                            <div className="text-sm text-gray-400">{node.description}</div>
                          </div>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Node Grid */}
            <div className="flex-1 overflow-y-auto p-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {filteredNodes.map((node, index) => {
                  const Icon = node.icon;
                  const category = nodeCategories.find(cat => cat.id === node.category);
                  
                  return (
                    <button
                      key={index}
                      onClick={() => setSelectedNode(node)}
                      className={`p-4 rounded-lg border transition-all duration-200 text-left hover:shadow-lg ${
                        selectedNode?.subtype === node.subtype
                          ? 'border-blue-500 bg-blue-500 bg-opacity-10 shadow-lg'
                          : 'border-gray-600 hover:border-gray-500 hover:bg-gray-700'
                      }`}
                    >
                      <div className="flex items-start space-x-4">
                        <div className={`p-2 rounded-lg bg-gray-700 ${category?.color || 'text-gray-400'}`}>
                          <Icon className="h-6 w-6" />
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-1">
                            <h4 className="font-semibold text-white">{node.name}</h4>
                            {node.popular && (
                              <Star className="h-4 w-4 text-yellow-400" />
                            )}
                          </div>
                          <p className="text-sm text-gray-400 mb-2">{node.description}</p>
                          <div className="flex items-center space-x-2">
                            <span className="text-xs px-2 py-1 bg-gray-600 text-gray-300 rounded">
                              {node.type}
                            </span>
                            <span className="text-xs text-gray-500">
                              {category?.name}
                            </span>
                          </div>
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
              
              {filteredNodes.length === 0 && (
                <div className="text-center py-12">
                  <Search className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-white mb-2">No components found</h3>
                  <p className="text-gray-400">
                    Try adjusting your search terms or category filter
                  </p>
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="p-6 border-t border-gray-700 bg-gray-750">
              <div className="flex items-center justify-between">
                <div>
                  {selectedNode && (
                    <div className="text-sm text-gray-400">
                      Selected: <span className="text-white font-medium">{selectedNode.name}</span>
                    </div>
                  )}
                </div>
                <div className="flex items-center space-x-3">
                  <button
                    onClick={onClose}
                    className="px-4 py-2 text-gray-400 hover:text-white transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleCreateNode}
                    disabled={!selectedNode}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
                  >
                    <Plus className="h-4 w-4" />
                    <span>Add Component</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NodeCreationModal;