import React, { useState, useCallback, useMemo } from 'react';
import { 
  Shield, 
  Server, 
  Database, 
  Cloud, 
  Settings,
  AlertTriangle,
  Users,
  FileText,
  Info,
  ChevronDown,
  ChevronRight,
  Search,
  Filter
} from 'lucide-react';

const AdvancedNodeLibrary = ({ onAddNode }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [collapsedCategories, setCollapsedCategories] = useState(new Set());
  const [detailView, setDetailView] = useState(false);

  const nodeCategories = [
    {
      id: 'actors',
      title: 'Threat Actors',
      icon: Users,
      color: 'text-red-400',
      nodes: [
        {
          type: 'Actor',
          subtype: 'ExternalAttacker',
          label: 'External Attacker',
          description: 'External threat actor attempting to breach systems',
          mitre_ids: ['T1078', 'T1190', 'T1566'],
          sophistication: 'Advanced',
          motivation: 'Financial Gain, Espionage'
        },
        {
          type: 'Actor',
          subtype: 'MaliciousInsider',
          label: 'Malicious Insider',
          description: 'Internal threat actor with legitimate access',
          mitre_ids: ['T1078', 'T1098', 'T1484'],
          sophistication: 'Medium',
          motivation: 'Revenge, Financial Gain'
        },
        {
          type: 'Actor',
          subtype: 'CompromisedAccount',
          label: 'Compromised Account',
          description: 'Legitimate account under attacker control',
          mitre_ids: ['T1078', 'T1136', 'T1484'],
          sophistication: 'High',
          motivation: 'Espionage, Sabotage'
        }
      ]
    },
    {
      id: 'assets',
      title: 'Critical Assets',
      icon: Server,
      color: 'text-green-400',
      nodes: [
        {
          type: 'Asset',
          subtype: 'WebApp',
          label: 'Web Application',
          description: 'Customer-facing or internal web application',
          mitre_ids: [],
          criticality: 'High',
          data_classification: 'Confidential'
        },
        {
          type: 'Asset',
          subtype: 'API',
          label: 'API Gateway',
          description: 'REST/GraphQL API endpoint handling sensitive operations',
          mitre_ids: [],
          criticality: 'High',
          data_classification: 'Confidential'
        },
        {
          type: 'Asset',
          subtype: 'Database',
          label: 'Production Database',
          description: 'Primary data store containing customer and business data',
          mitre_ids: [],
          criticality: 'Critical',
          data_classification: 'Restricted'
        },
        {
          type: 'Asset',
          subtype: 'S3Bucket',
          label: 'Cloud Storage',
          description: 'Object storage containing backups, logs, or sensitive files',
          mitre_ids: [],
          criticality: 'Medium',
          data_classification: 'Internal'
        },
        {
          type: 'Asset',
          subtype: 'VM',
          label: 'Virtual Machine',
          description: 'Compute instance hosting applications or services',
          mitre_ids: [],
          criticality: 'Medium',
          data_classification: 'Internal'
        },
        {
          type: 'Asset',
          subtype: 'Container',
          label: 'Container Service',
          description: 'Containerized application or microservice',
          mitre_ids: [],
          criticality: 'Medium',
          data_classification: 'Internal'
        },
        {
          type: 'Asset',
          subtype: 'LoadBalancer',
          label: 'Load Balancer',
          description: 'Traffic distribution and routing component',
          mitre_ids: [],
          criticality: 'Medium',
          data_classification: 'Internal'
        },
        {
          type: 'Asset',
          subtype: 'CDN',
          label: 'Content Delivery Network',
          description: 'Distributed content caching and delivery system',
          mitre_ids: [],
          criticality: 'Low',
          data_classification: 'Public'
        }
      ]
    },
    {
      id: 'surfaces',
      title: 'Attack Surfaces',
      icon: AlertTriangle,
      color: 'text-orange-400',
      nodes: [
        {
          type: 'Surface',
          subtype: 'SQLi',
          label: 'SQL Injection',
          description: 'Database query manipulation vulnerability',
          mitre_ids: ['T1190'],
          cve_references: ['CWE-89'],
          risk_level: 'High'
        },
        {
          type: 'Surface',
          subtype: 'WeakIAM',
          label: 'Weak Identity & Access Management',
          description: 'Authentication and authorization weaknesses',
          mitre_ids: ['T1078', 'T1110'],
          cve_references: ['CWE-287', 'CWE-306'],
          risk_level: 'Critical'
        },
        {
          type: 'Surface',
          subtype: 'UnencryptedData',
          label: 'Unencrypted Data',
          description: 'Data transmission or storage without encryption',
          mitre_ids: ['T1040', 'T1552'],
          cve_references: ['CWE-311'],
          risk_level: 'High'
        },
        {
          type: 'Surface',
          subtype: 'APIVuln',
          label: 'API Vulnerability',
          description: 'REST/GraphQL API security weaknesses',
          mitre_ids: ['T1190'],
          cve_references: ['CWE-200', 'CWE-285'],
          risk_level: 'High'
        },
        {
          type: 'Surface',
          subtype: 'XSS',
          label: 'Cross-Site Scripting',
          description: 'Client-side code injection vulnerability',
          mitre_ids: ['T1189'],
          cve_references: ['CWE-79'],
          risk_level: 'Medium'
        },
        {
          type: 'Surface',
          subtype: 'CSRF',
          label: 'Cross-Site Request Forgery',
          description: 'Unauthorized command transmission vulnerability',
          mitre_ids: ['T1189'],
          cve_references: ['CWE-352'],
          risk_level: 'Medium'
        },
        {
          type: 'Surface',
          subtype: 'InsecureDeserialization',
          label: 'Insecure Deserialization',
          description: 'Untrusted data deserialization vulnerability',
          mitre_ids: ['T1190'],
          cve_references: ['CWE-502'],
          risk_level: 'High'
        },
        {
          type: 'Surface',
          subtype: 'SecurityMisconfiguration',
          label: 'Security Misconfiguration',
          description: 'Improper security settings and configurations',
          mitre_ids: ['T1190', 'T1068'],
          cve_references: ['CWE-16'],
          risk_level: 'Medium'
        }
      ]
    },
    {
      id: 'controls',
      title: 'Security Controls',
      icon: Shield,
      color: 'text-blue-400',
      nodes: [
        {
          type: 'Control',
          subtype: 'WAF',
          label: 'Web Application Firewall',
          description: 'Application-layer firewall filtering HTTP/HTTPS traffic',
          mitre_ids: [],
          effectiveness: 'High',
          control_type: 'Preventive'
        },
        {
          type: 'Control',
          subtype: 'EDR',
          label: 'Endpoint Detection & Response',
          description: 'Advanced endpoint monitoring and threat response',
          mitre_ids: [],
          effectiveness: 'High',
          control_type: 'Detective'
        },
        {
          type: 'Control',
          subtype: 'SIEM',
          label: 'Security Information & Event Management',
          description: 'Centralized security event monitoring and analysis',
          mitre_ids: [],
          effectiveness: 'Medium',
          control_type: 'Detective'
        },
        {
          type: 'Control',
          subtype: 'DLP',
          label: 'Data Loss Prevention',
          description: 'Data exfiltration detection and prevention system',
          mitre_ids: [],
          effectiveness: 'Medium',
          control_type: 'Preventive'
        },
        {
          type: 'Control',
          subtype: 'MFA',
          label: 'Multi-Factor Authentication',
          description: 'Additional authentication factors beyond passwords',
          mitre_ids: [],
          effectiveness: 'High',
          control_type: 'Preventive'
        },
        {
          type: 'Control',
          subtype: 'NetworkSegmentation',
          label: 'Network Segmentation',
          description: 'Isolated network zones with controlled access',
          mitre_ids: [],
          effectiveness: 'High',
          control_type: 'Preventive'
        },
        {
          type: 'Control',
          subtype: 'Encryption',
          label: 'Data Encryption',
          description: 'Data protection through cryptographic means',
          mitre_ids: [],
          effectiveness: 'High',
          control_type: 'Preventive'
        },
        {
          type: 'Control',
          subtype: 'VulnerabilityScanning',
          label: 'Vulnerability Scanning',
          description: 'Automated security vulnerability assessment',
          mitre_ids: [],
          effectiveness: 'Medium',
          control_type: 'Detective'
        }
      ]
    },
    {
      id: 'zones',
      title: 'Trust Zones',
      icon: Cloud,
      color: 'text-purple-400',
      nodes: [
        {
          type: 'Zone',
          subtype: 'PublicCloud',
          label: 'Public Cloud',
          description: 'Public cloud infrastructure and services',
          mitre_ids: [],
          trust_level: 'Low',
          security_level: 'Standard'
        },
        {
          type: 'Zone',
          subtype: 'PrivateCloud',
          label: 'Private Cloud',
          description: 'Private cloud infrastructure with enhanced controls',
          mitre_ids: [],
          trust_level: 'Medium',
          security_level: 'Enhanced'
        },
        {
          type: 'Zone',
          subtype: 'DMZ',
          label: 'Demilitarized Zone',
          description: 'Network buffer zone between internal and external networks',
          mitre_ids: [],
          trust_level: 'Low',
          security_level: 'Enhanced'
        },
        {
          type: 'Zone',
          subtype: 'InternalNetwork',
          label: 'Internal Network',
          description: 'Protected internal corporate network',
          mitre_ids: [],
          trust_level: 'High',
          security_level: 'Standard'
        },
        {
          type: 'Zone',
          subtype: 'SecureEnclave',
          label: 'Secure Enclave',
          description: 'High-security zone for critical assets and operations',
          mitre_ids: [],
          trust_level: 'High',
          security_level: 'Maximum'
        },
        {
          type: 'Zone',
          subtype: 'Internet',
          label: 'Internet',
          description: 'Untrusted external network environment',
          mitre_ids: [],
          trust_level: 'None',
          security_level: 'None'
        }
      ]
    },
    {
      id: 'infrastructure',
      title: 'Infrastructure',
      icon: Settings,
      color: 'text-gray-400',
      nodes: [
        {
          type: 'Infrastructure',
          subtype: 'Router',
          label: 'Network Router',
          description: 'Network traffic routing and forwarding device',
          mitre_ids: [],
          category: 'Network',
          management_protocol: 'SNMP'
        },
        {
          type: 'Infrastructure',
          subtype: 'Switch',
          label: 'Network Switch',
          description: 'Layer 2 network switching device',
          mitre_ids: [],
          category: 'Network',
          management_protocol: 'SNMP'
        },
        {
          type: 'Infrastructure',
          subtype: 'Firewall',
          label: 'Network Firewall',
          description: 'Network-layer traffic filtering and inspection',
          mitre_ids: [],
          category: 'Security',
          management_protocol: 'HTTPS'
        },
        {
          type: 'Infrastructure',
          subtype: 'DNS',
          label: 'DNS Server',
          description: 'Domain name resolution service',
          mitre_ids: [],
          category: 'Service',
          management_protocol: 'DNS'
        },
        {
          type: 'Infrastructure',
          subtype: 'DHCP',
          label: 'DHCP Server',
          description: 'Dynamic host configuration service',
          mitre_ids: [],
          category: 'Service',
          management_protocol: 'DHCP'
        },
        {
          type: 'Infrastructure',
          subtype: 'ActiveDirectory',
          label: 'Active Directory',
          description: 'Directory service for Windows domain networks',
          mitre_ids: [],
          category: 'Identity',
          management_protocol: 'LDAP'
        }
      ]
    }
  ];

  const enrichedCategories = useMemo(() => {
    return nodeCategories.map(category => ({
      ...category,
      categoryTitle: category.title,
      nodes: category.nodes.map(node => ({
        ...node,
        category: category.id,
        categoryTitle: category.title
      }))
    }));
  }, []);

  const getCategoryIcon = (categoryId) => {
    const category = enrichedCategories.find(cat => cat.id === categoryId);
    return category ? category.icon : FileText;
  };

  const getNodeColorClass = (nodeType) => {
    const colorMap = {
      'Actor': 'bg-red-900 bg-opacity-30 border-red-500 hover:bg-red-800',
      'Asset': 'bg-green-900 bg-opacity-30 border-green-500 hover:bg-green-800',
      'Surface': 'bg-orange-900 bg-opacity-30 border-orange-500 hover:bg-orange-800',
      'Control': 'bg-blue-900 bg-opacity-30 border-blue-500 hover:bg-blue-800',
      'Zone': 'bg-purple-900 bg-opacity-30 border-purple-500 hover:bg-purple-800',
      'Infrastructure': 'bg-gray-900 bg-opacity-30 border-gray-500 hover:bg-gray-800'
    };
    return colorMap[nodeType] || 'bg-gray-900 bg-opacity-30 border-gray-500 hover:bg-gray-800';
  };

  const filterNodes = useCallback((categories) => {
    return categories.map(category => ({
      ...category,
      nodes: category.nodes.filter(node => {
        const matchesSearch = searchTerm === '' || 
          node.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
          node.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
          (node.mitre_ids && node.mitre_ids.some(id => id.toLowerCase().includes(searchTerm.toLowerCase())));
        
        const matchesCategory = selectedCategory === 'all' || category.id === selectedCategory;
        
        return matchesSearch && matchesCategory;
      })
    })).filter(category => category.nodes.length > 0);
  }, [searchTerm, selectedCategory]);

  const filteredCategories = useMemo(() => {
    return filterNodes(enrichedCategories);
  }, [enrichedCategories, filterNodes]);

  const toggleCategory = (categoryId) => {
    setCollapsedCategories(prev => {
      const newSet = new Set(prev);
      if (newSet.has(categoryId)) {
        newSet.delete(categoryId);
      } else {
        newSet.add(categoryId);
      }
      return newSet;
    });
  };

  const onDragStart = (event, nodeData) => {
    event.dataTransfer.setData('application/reactflow', JSON.stringify(nodeData));
    event.dataTransfer.effectAllowed = 'move';
  };

  const totalVisibleNodes = filteredCategories.reduce((sum, cat) => sum + cat.nodes.length, 0);

  return (
    <div className="advanced-node-library h-full flex flex-col bg-gray-900 border-r border-gray-700">
      {/* Header */}
      <div className="p-4 border-b border-gray-700" data-testid="node-library-header">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Shield className="h-5 w-5 text-blue-400" />
            <h2 className="text-lg font-semibold text-white">Security Nodes</h2>
          </div>
          <button
            onClick={() => setDetailView(!detailView)}
            className="p-1 rounded hover:bg-gray-800 text-gray-400 hover:text-white transition-colors"
            title={detailView ? "Simple View" : "Detailed View"}
          >
            <Info className="h-4 w-4" />
          </button>
        </div>
        
        {/* Search */}
        <div className="relative mb-3">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search nodes..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            data-testid="node-search-input"
          />
        </div>
        
        {/* Filter */}
        <div className="relative">
          <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="w-full pl-9 pr-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none cursor-pointer"
            data-testid="category-filter-select"
          >
            <option value="all">All Categories ({totalVisibleNodes})</option>
            {nodeCategories.map(category => (
              <option key={category.id} value={category.id}>
                {category.title}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Node Categories */}
      <div className="flex-1 overflow-y-auto p-3 space-y-3" data-testid="node-categories-container">
        {filteredCategories.map((category) => {
          const isCollapsed = collapsedCategories.has(category.id);
          const IconComponent = category.icon;
          
          return (
            <div key={category.id} className="node-category">
              {/* Category Header */}
              <button
                onClick={() => toggleCategory(category.id)}
                className={`w-full flex items-center justify-between p-3 rounded-lg border border-opacity-20 transition-all ${category.color} bg-opacity-10 hover:bg-opacity-20 border-current`}
                data-testid={`category-${category.id}-header`}
              >
                <div className="flex items-center space-x-3">
                  <IconComponent className={`h-5 w-5 ${category.color}`} />
                  <span className="text-white font-medium">{category.title}</span>
                  <span className="px-2 py-1 bg-black bg-opacity-20 text-xs rounded text-gray-300">
                    {category.nodes.length}
                  </span>
                </div>
                {isCollapsed ? 
                  <ChevronRight className="h-4 w-4 text-gray-400" /> : 
                  <ChevronDown className="h-4 w-4 text-gray-400" />
                }
              </button>
              
              {/* Category Nodes */}
              {!isCollapsed && (
                <div className="mt-2 space-y-2 ml-4" data-testid={`category-${category.id}-nodes`}>
                  {category.nodes.map((node) => {
                    const nodeKey = `${node.type}-${node.subtype}`;
                    const IconComponent = getCategoryIcon(node.category);
                    
                    return (
                      <div
                        key={nodeKey}
                        draggable
                        onDragStart={(event) => onDragStart(event, node)}
                        className={`security-node-item p-3 rounded-lg cursor-grab border border-opacity-20 ${getNodeColorClass(node.type)} relative group`}
                        data-testid={`node-${node.subtype.toLowerCase()}`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex items-start space-x-3 flex-1">
                            <IconComponent className="h-5 w-5 mt-0.5 flex-shrink-0" />
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center space-x-2 mb-1">
                                <div className="text-white text-sm font-medium">{node.label}</div>
                                <span className="px-1.5 py-0.5 bg-black bg-opacity-20 text-xs rounded text-gray-300">
                                  {node.categoryTitle}
                                </span>
                              </div>
                              <div className="text-gray-300 text-xs mb-2 line-clamp-2">
                                {node.description}
                              </div>
                              
                              {/* Node-specific metadata */}
                              <div className="flex flex-wrap gap-1 mb-2">
                                {node.sophistication && (
                                  <span className="px-2 py-1 bg-purple-900 bg-opacity-30 text-purple-300 text-xs rounded">
                                    {node.sophistication}
                                  </span>
                                )}
                                {node.criticality && (
                                  <span className={`px-2 py-1 text-xs rounded ${
                                    node.criticality === 'Critical' ? 'bg-red-900 bg-opacity-30 text-red-300' :
                                    node.criticality === 'High' ? 'bg-orange-900 bg-opacity-30 text-orange-300' :
                                    node.criticality === 'Medium' ? 'bg-yellow-900 bg-opacity-30 text-yellow-300' :
                                    'bg-green-900 bg-opacity-30 text-green-300'
                                  }`}>
                                    {node.criticality}
                                  </span>
                                )}
                                {node.effectiveness && (
                                  <span className={`px-2 py-1 text-xs rounded ${
                                    node.effectiveness === 'High' ? 'bg-green-900 bg-opacity-30 text-green-300' :
                                    node.effectiveness === 'Medium' ? 'bg-yellow-900 bg-opacity-30 text-yellow-300' :
                                    'bg-red-900 bg-opacity-30 text-red-300'
                                  }`}>
                                    {node.effectiveness}
                                  </span>
                                )}
                                {node.risk_level && (
                                  <span className={`px-2 py-1 text-xs rounded ${
                                    node.risk_level === 'Critical' ? 'bg-red-900 bg-opacity-30 text-red-300' :
                                    node.risk_level === 'High' ? 'bg-orange-900 bg-opacity-30 text-orange-300' :
                                    node.risk_level === 'Medium' ? 'bg-yellow-900 bg-opacity-30 text-yellow-300' :
                                    'bg-green-900 bg-opacity-30 text-green-300'
                                  }`}>
                                    {node.risk_level}
                                  </span>
                                )}
                                {node.trust_level && (
                                  <span className={`px-2 py-1 text-xs rounded ${
                                    node.trust_level === 'High' ? 'bg-green-900 bg-opacity-30 text-green-300' :
                                    node.trust_level === 'Medium' ? 'bg-yellow-900 bg-opacity-30 text-yellow-300' :
                                    node.trust_level === 'Low' ? 'bg-orange-900 bg-opacity-30 text-orange-300' :
                                    'bg-red-900 bg-opacity-30 text-red-300'
                                  }`}>
                                    Trust: {node.trust_level}
                                  </span>
                                )}
                              </div>
                              
                              {/* MITRE ATT&CK IDs */}
                              {detailView && node.mitre_ids && node.mitre_ids.length > 0 && (
                                <div className="flex flex-wrap gap-1 mb-2">
                                  {node.mitre_ids.map(mitreId => (
                                    <span key={mitreId} className="px-1.5 py-0.5 bg-gray-800 text-gray-300 text-xs rounded font-mono">
                                      {mitreId}
                                    </span>
                                  ))}
                                </div>
                              )}
                              
                              {/* CVE References */}
                              {detailView && node.cve_references && node.cve_references.length > 0 && (
                                <div className="flex flex-wrap gap-1">
                                  {node.cve_references.map(cve => (
                                    <span key={cve} className="px-1.5 py-0.5 bg-red-900 bg-opacity-20 text-red-300 text-xs rounded font-mono">
                                      {cve}
                                    </span>
                                  ))}
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                        
                        {/* Drag indicator */}
                        <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                          <div className="flex flex-col space-y-1">
                            <div className="w-1 h-1 bg-gray-400 rounded-full"></div>
                            <div className="w-1 h-1 bg-gray-400 rounded-full"></div>
                            <div className="w-1 h-1 bg-gray-400 rounded-full"></div>
                            <div className="w-1 h-1 bg-gray-400 rounded-full"></div>
                            <div className="w-1 h-1 bg-gray-400 rounded-full"></div>
                            <div className="w-1 h-1 bg-gray-400 rounded-full"></div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
        
        {filteredCategories.length === 0 && (
          <div className="text-center text-gray-400 py-8">
            <Search className="h-8 w-8 mx-auto mb-2 opacity-50" />
            <p>No nodes found matching your criteria</p>
            <p className="text-xs mt-1">Try adjusting your search or filter</p>
          </div>
        )}
      </div>
    </div>
  );
};

export { AdvancedNodeLibrary };