import React, { useState } from 'react';
import { Shield, Server, AlertTriangle, Lock, Network, Activity, Search, Filter, Star } from 'lucide-react';

const AdvancedNodeLibrary = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [favorites, setFavorites] = useState(new Set());

  const nodeCategories = [
    {
      id: 'actors',
      title: 'Threat Actors',
      icon: Shield,
      color: 'text-red-400',
      nodes: [
        {
          type: 'Actor',
          subtype: 'ExternalAttacker',
          label: 'External Attacker',
          description: 'Advanced persistent threat or opportunistic external attacker',
          mitre_ids: ['T1190', 'T1566'],
          sophistication: 'High',
          motivation: 'Financial, Espionage'
        },
        {
          type: 'Actor',
          subtype: 'Insider',
          label: 'Malicious Insider',
          description: 'Employee or contractor with authorized access acting maliciously',
          mitre_ids: ['T1078'],
          sophistication: 'Medium',
          motivation: 'Financial, Revenge'
        },
        {
          type: 'Actor',
          subtype: 'ServiceAccount',
          label: 'Compromised Service',
          description: 'Automated service or application account under attacker control',
          mitre_ids: ['T1078'],
          sophistication: 'Low',
          motivation: 'Lateral Movement'
        },
        {
          type: 'Actor',
          subtype: 'NationState',
          label: 'Nation State Actor',
          description: 'State-sponsored advanced persistent threat group',
          mitre_ids: ['T1190', 'T1566', 'T1078'],
          sophistication: 'Very High',
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
          subtype: 'IMDS',
          label: 'Instance Metadata',
          description: 'Cloud instance metadata service with IAM credentials',
          mitre_ids: ['T1552.001'],
          criticality: 'High',
          data_classification: 'Restricted'
        },
        {
          type: 'Asset',
          subtype: 'ActiveDirectory',
          label: 'Active Directory',
          description: 'Domain controller and identity management system',
          mitre_ids: [],
          criticality: 'Critical',
          data_classification: 'Restricted'
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
          subtype: 'SSRF',
          label: 'SSRF Vulnerability',
          description: 'Server-Side Request Forgery allowing internal network access',
          mitre_ids: ['T1190'],
          cvss_score: 8.6,
          exploitability: 'High'
        },
        {
          type: 'Surface',
          subtype: 'SQLi',
          label: 'SQL Injection',
          description: 'SQL injection vulnerability enabling database compromise',
          mitre_ids: ['T1190', 'T1213'],
          cvss_score: 9.8,
          exploitability: 'High'
        },
        {
          type: 'Surface',
          subtype: 'IDOR',
          label: 'Broken Access Control',
          description: 'Insecure Direct Object Reference bypassing authorization',
          mitre_ids: ['T1190'],
          cvss_score: 6.5,
          exploitability: 'Medium'
        },
        {
          type: 'Surface',
          subtype: 'RCE',
          label: 'Remote Code Execution',
          description: 'Code execution vulnerability allowing system compromise',
          mitre_ids: ['T1190', 'T1059'],
          cvss_score: 9.9,
          exploitability: 'Critical'
        },
        {
          type: 'Surface',
          subtype: 'WeakIAM',
          label: 'IAM Misconfiguration',
          description: 'Overprivileged roles or weak authentication mechanisms',
          mitre_ids: ['T1078', 'T1484'],
          cvss_score: 7.5,
          exploitability: 'Medium'
        },
        {
          type: 'Surface',  
          subtype: 'Deserialization',
          label: 'Unsafe Deserialization',
          description: 'Insecure deserialization leading to code execution',
          mitre_ids: ['T1190', 'T1059'],
          cvss_score: 9.1,
          exploitability: 'High'
        }
      ]
    },
    {
      id: 'controls',
      title: 'Security Controls',
      icon: Lock,
      color: 'text-blue-400',
      nodes: [
        {
          type: 'Control',
          subtype: 'WAF',
          label: 'Web Application Firewall',
          description: 'Advanced WAF with machine learning threat detection',
          mitre_ids: [],
          effectiveness: 85,
          control_type: 'Preventive'
        },
        {
          type: 'Control',
          subtype: 'EDR',
          label: 'Endpoint Detection & Response',
          description: 'Behavioral analysis and threat hunting on endpoints',
          mitre_ids: [],
          effectiveness: 90,
          control_type: 'Detective'
        },
        {
          type: 'Control',
          subtype: 'EgressProxy',
          label: 'Egress Filtering',
          description: 'Outbound traffic inspection and data loss prevention',
          mitre_ids: [],
          effectiveness: 75,
          control_type: 'Preventive'
        },
        {
          type: 'Control',
          subtype: 'IAMPolicy',
          label: 'Zero Trust IAM',
          description: 'Principle of least privilege with continuous verification',
          mitre_ids: [],
          effectiveness: 95,
          control_type: 'Preventive'
        },
        {
          type: 'Control',
          subtype: 'NetworkACL',
          label: 'Network Segmentation',
          description: 'Micro-segmentation with software-defined perimeters',
          mitre_ids: [],
          effectiveness: 80,
          control_type: 'Preventive'
        },
        {
          type: 'Control',
          subtype: 'SIEM',
          label: 'Security Orchestration',
          description: 'SIEM/SOAR with automated incident response',
          mitre_ids: [],
          effectiveness: 85,
          control_type: 'Detective'
        }
      ]
    },
    {
      id: 'zones',
      title: 'Network Zones',
      icon: Network,
      color: 'text-purple-400',
      nodes: [
        {
          type: 'Zone',
          subtype: 'Internet',
          label: 'Internet Zone',
          description: 'Untrusted public internet space',
          mitre_ids: [],
          trust_level: 'Untrusted',
          security_level: 'None'
        },
        {
          type: 'Zone',
          subtype: 'DMZ',
          label: 'Demilitarized Zone',
          description: 'Semi-trusted zone for public-facing services',
          mitre_ids: [],
          trust_level: 'Low',
          security_level: 'Basic'
        },
        {
          type: 'Zone',
          subtype: 'Internal',
          label: 'Corporate Network',
          description: 'Internal trusted network for business operations',
          mitre_ids: [],
          trust_level: 'Medium',
          security_level: 'Standard'
        },
        {
          type: 'Zone',
          subtype: 'CloudVPC',
          label: 'Cloud VPC',
          description: 'Virtual private cloud with cloud-native security',
          mitre_ids: [],
          trust_level: 'Medium',
          security_level: 'Enhanced'
        },
        {
          type: 'Zone',
          subtype: 'SecureEnclave',
          label: 'Secure Enclave',
          description: 'High-security zone for critical assets and operations',
          mitre_ids: [],
          trust_level: 'High',
          security_level: 'Maximum'
        }
      ]
    },
    {
      id: 'signals',
      title: 'Detection Signals',
      icon: Activity,
      color: 'text-cyan-400',
      nodes: [
        {
          type: 'Signal',
          subtype: 'WAFAlert',
          label: 'WAF Detection',
          description: 'Web application firewall triggered on malicious request',
          mitre_ids: [],
          confidence: 85,
          alert_volume: 'Medium'
        },
        {
          type: 'Signal',
          subtype: 'EDRAlert',
          label: 'Endpoint Alert',
          description: 'Suspicious process or behavior detected on endpoint',
          mitre_ids: [],
          confidence: 90,
          alert_volume: 'Low'
        },
        {
          type: 'Signal',
          subtype: 'NetworkAnomaly',
          label: 'Network Anomaly',
          description: 'Unusual network traffic pattern or connection',
          mitre_ids: [],
          confidence: 70,
          alert_volume: 'High'
        },
        {
          type: 'Signal',
          subtype: 'DataExfiltration',
          label: 'Data Loss Alert',
          description: 'Large data transfer or sensitive data movement detected',
          mitre_ids: [],
          confidence: 95,
          alert_volume: 'Low'
        }
      ]
    },
    {
      id: 'infrastructure',
      title: 'Infrastructure',
      icon: Server,
      color: 'text-blue-400',
      nodes: [
        {
          type: 'Infrastructure',
          subtype: 'CloudDeployment',
          label: 'Cloud Deployment',
          description: 'Cloud-based deployment infrastructure with automatic scaling',
          mitre_ids: [],
          deployment_model: 'IaaS/PaaS',
          security_level: 'Shared Responsibility'
        },
        {
          type: 'Infrastructure',
          subtype: 'OnPremisesDeployment',
          label: 'On-Premises Deployment',
          description: 'On-premises deployment infrastructure with full control',
          mitre_ids: [],
          deployment_model: 'Self-Managed',
          security_level: 'Full Responsibility'
        }
      ]
    },
    {
      id: 'cloud-services',
      title: 'Cloud Services',
      icon: Network,
      color: 'text-cyan-400',
      nodes: [
        {
          type: 'Service',
          subtype: 'AWSService',
          label: 'AWS Service',
          description: 'Amazon Web Services cloud platform components',
          mitre_ids: [],
          provider: 'Amazon',
          service_model: 'Multi-Service'
        },
        {
          type: 'Service',
          subtype: 'GCPService',
          label: 'GCP Service',
          description: 'Google Cloud Platform components and services',
          mitre_ids: [],
          provider: 'Google',
          service_model: 'Multi-Service'
        }
      ]
    }
  ];

  const allNodes = nodeCategories.flatMap(cat => 
    cat.nodes.map(node => ({ ...node, category: cat.id, categoryTitle: cat.title }))
  );

  const filteredNodes = allNodes.filter(node => {
    const matchesSearch = searchTerm === '' || 
      node.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
      node.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      node.mitre_ids.some(id => id.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesCategory = selectedCategory === 'all' || node.category === selectedCategory;
    
    return matchesSearch && matchesCategory;
  });

  const toggleFavorite = (nodeKey) => {
    setFavorites(prev => {
      const newFavorites = new Set(prev);
      if (newFavorites.has(nodeKey)) {
        newFavorites.delete(nodeKey);
      } else {
        newFavorites.add(nodeKey);
      }
      return newFavorites;
    });
  };

  const onDragStart = (event, nodeData) => {
    event.dataTransfer.setData('application/reactflow', JSON.stringify(nodeData));
    event.dataTransfer.effectAllowed = 'move';
  };

  const getNodeColorClass = (type) => {
    const colorMap = {
      'Actor': 'node-actor',
      'Asset': 'node-asset',
      'Surface': 'node-surface',
      'Control': 'node-control',
      'Zone': 'node-zone',
      'Signal': 'node-signal'
    };
    return colorMap[type] || 'bg-gray-600';
  };

  const getCategoryIcon = (categoryId) => {
    const category = nodeCategories.find(cat => cat.id === categoryId);
    return category ? category.icon : Shield;
  };

  return (
    <div className="p-4">
      <h2 className="text-lg font-semibold text-white mb-4 flex items-center">
        <Shield className="h-5 w-5 mr-2 text-blue-400" />
        Security Elements
      </h2>
      
      {/* Search and Filter Controls */}
      <div className="space-y-3 mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search elements, techniques..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
          />
        </div>
        
        <div className="flex items-center space-x-2">
          <Filter className="h-4 w-4 text-gray-400" />
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="bg-gray-700 border border-gray-600 rounded text-white text-sm px-3 py-1 focus:outline-none focus:border-blue-500"
          >
            <option value="all">All Categories</option>
            {nodeCategories.map(cat => (
              <option key={cat.id} value={cat.id}>{cat.title}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Filtered Nodes Display */}
      <div className="space-y-3">
        {filteredNodes.length > 0 ? (
          filteredNodes.map((node) => {
            const nodeKey = `${node.type}-${node.subtype}`;
            const isFavorite = favorites.has(nodeKey);
            const IconComponent = getCategoryIcon(node.category);
            
            return (
              <div
                key={nodeKey}
                draggable
                onDragStart={(event) => onDragStart(event, node)}
                className={`security-node-item p-3 rounded-lg cursor-grab border border-opacity-20 ${getNodeColorClass(node.type)} relative group`}
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
                            'bg-yellow-900 bg-opacity-30 text-yellow-300'
                          }`}>
                            {node.criticality}
                          </span>
                        )}
                        {node.cvss_score && (
                          <span className="px-2 py-1 bg-red-900 bg-opacity-30 text-red-300 text-xs rounded">
                            CVSS: {node.cvss_score}
                          </span>
                        )}
                        {node.effectiveness && (
                          <span className="px-2 py-1 bg-green-900 bg-opacity-30 text-green-300 text-xs rounded">
                            {node.effectiveness}% effective
                          </span>
                        )}
                      </div>
                      
                      {node.mitre_ids.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {node.mitre_ids.map((id) => (
                            <span
                              key={id}
                              className="px-2 py-1 bg-gray-700 text-gray-300 text-xs rounded font-mono"
                            >
                              {id}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <button
                    onClick={() => toggleFavorite(nodeKey)}
                    className={`ml-2 p-1 rounded transition-colors ${
                      isFavorite 
                        ? 'text-yellow-400 hover:text-yellow-300' 
                        : 'text-gray-500 hover:text-yellow-400'
                    }`}
                  >
                    <Star className={`h-4 w-4 ${isFavorite ? 'fill-current' : ''}`} />
                  </button>
                </div>
              </div>
            );
          })
        ) : (
          <div className="text-center py-8">
            <Search className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <div className="text-white font-medium mb-2">No elements found</div>
            <div className="text-gray-400 text-sm">
              Try adjusting your search or filter criteria
            </div>
          </div>
        )}
      </div>
      
      {/* Usage Instructions */}
      <div className="mt-6 p-3 bg-gray-700 rounded-lg">
        <div className="text-xs text-gray-300">
          <strong>Advanced Features:</strong>
          <br />
          • Search by name, description, or MITRE technique
          <br />
          • Filter by category or mark favorites with ⭐
          <br />
          • Drag elements to canvas for threat modeling
          <br />
          • Enhanced metadata shows risk levels and effectiveness
        </div>
      </div>
    </div>
  );
};

export { AdvancedNodeLibrary };