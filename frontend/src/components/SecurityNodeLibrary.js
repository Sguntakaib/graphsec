import React from 'react';
import { Shield, Server, AlertTriangle, Lock, Network, Activity } from 'lucide-react';

const SecurityNodeLibrary = () => {
  const nodeCategories = [
    {
      title: 'Actors',
      icon: Shield,
      color: 'text-red-400',
      nodes: [
        {
          type: 'Actor',
          subtype: 'ExternalAttacker',
          label: 'External Attacker',
          description: 'External threat actor attempting to compromise systems',
          mitre_ids: []
        },
        {
          type: 'Actor',
          subtype: 'Insider',
          label: 'Insider Threat',
          description: 'Malicious or compromised internal user',
          mitre_ids: ['T1078']
        },
        {
          type: 'Actor',
          subtype: 'ServiceAccount',
          label: 'Service Account',
          description: 'Automated service or application account',
          mitre_ids: []
        }
      ]
    },
    {
      title: 'Assets',
      icon: Server,
      color: 'text-green-400',
      nodes: [
        {
          type: 'Asset',
          subtype: 'WebApp',
          label: 'Web Application',
          description: 'Web-based application or service',
          mitre_ids: []
        },
        {
          type: 'Asset',
          subtype: 'API',
          label: 'API Endpoint',
          description: 'REST/GraphQL API endpoint',
          mitre_ids: []
        },
        {
          type: 'Asset',
          subtype: 'Database',
          label: 'Database',
          description: 'Data storage system',
          mitre_ids: []
        },
        {
          type: 'Asset',
          subtype: 'S3Bucket',
          label: 'S3 Bucket',
          description: 'Cloud storage bucket',
          mitre_ids: []
        },
        {
          type: 'Asset',
          subtype: 'VM',
          label: 'Virtual Machine',
          description: 'Compute instance or server',
          mitre_ids: []
        },
        {
          type: 'Asset',
          subtype: 'IMDS',
          label: 'Instance Metadata',
          description: 'Cloud instance metadata service',
          mitre_ids: ['T1552.001']
        }
      ]
    },
    {
      title: 'Attack Surfaces',
      icon: AlertTriangle,
      color: 'text-orange-400',
      nodes: [
        {
          type: 'Surface',
          subtype: 'SSRF',
          label: 'SSRF Vulnerability',
          description: 'Server-Side Request Forgery weakness',
          mitre_ids: ['T1190']
        },
        {
          type: 'Surface',
          subtype: 'SQLi',
          label: 'SQL Injection',
          description: 'SQL injection vulnerability',
          mitre_ids: ['T1190', 'T1213']
        },
        {
          type: 'Surface',
          subtype: 'IDOR',
          label: 'IDOR',
          description: 'Insecure Direct Object Reference',
          mitre_ids: ['T1190']
        },
        {
          type: 'Surface',
          subtype: 'RCE',
          label: 'Remote Code Execution',
          description: 'Code execution vulnerability',
          mitre_ids: ['T1190', 'T1059']
        },
        {
          type: 'Surface',
          subtype: 'WeakIAM',
          label: 'Weak IAM Policy',
          description: 'Overprivileged or misconfigured access',
          mitre_ids: ['T1078', 'T1484']
        }
      ]
    },
    {
      title: 'Security Controls',
      icon: Lock,
      color: 'text-blue-400',
      nodes: [
        {
          type: 'Control',
          subtype: 'WAF',
          label: 'Web Application Firewall',
          description: 'Filters malicious web traffic',
          mitre_ids: []
        },
        {
          type: 'Control',
          subtype: 'EDR',
          label: 'Endpoint Detection',
          description: 'Monitors endpoint activity',
          mitre_ids: []
        },
        {
          type: 'Control',
          subtype: 'EgressProxy',
          label: 'Egress Proxy',
          description: 'Controls outbound connections',
          mitre_ids: []
        },
        {
          type: 'Control',
          subtype: 'IAMPolicy',
          label: 'IAM Policy',
          description: 'Access control policy',
          mitre_ids: []
        },
        {
          type: 'Control',
          subtype: 'NetworkACL',
          label: 'Network ACL',
          description: 'Network-level access control',
          mitre_ids: []
        }
      ]
    },
    {
      title: 'Network Zones',
      icon: Network,
      color: 'text-purple-400',
      nodes: [
        {
          type: 'Zone',
          subtype: 'Internet',
          label: 'Internet Zone',
          description: 'Public internet space',
          mitre_ids: []
        },
        {
          type: 'Zone',
          subtype: 'DMZ',
          label: 'DMZ',
          description: 'Demilitarized zone',
          mitre_ids: []
        },
        {
          type: 'Zone',
          subtype: 'Internal',
          label: 'Internal Network',
          description: 'Internal corporate network',
          mitre_ids: []
        },
        {
          type: 'Zone',
          subtype: 'CloudVPC',
          label: 'Cloud VPC',
          description: 'Virtual private cloud',
          mitre_ids: []
        }
      ]
    },
    {
      title: 'Detection Signals',
      icon: Activity,
      color: 'text-cyan-400',
      nodes: [
        {
          type: 'Signal',
          subtype: 'WAFAlert',
          label: 'WAF Alert',
          description: 'Web application firewall detection',
          mitre_ids: []
        },
        {
          type: 'Signal',
          subtype: 'EDRAlert',
          label: 'EDR Alert',
          description: 'Endpoint detection alert',
          mitre_ids: []
        },
        {
          type: 'Signal',
          subtype: 'NetworkLog',
          label: 'Network Log',
          description: 'Network traffic observation',
          mitre_ids: []
        }
      ]
    }
  ];

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

  return (
    <div className="p-4">
      <h2 className="text-lg font-semibold text-white mb-4 flex items-center">
        <Shield className="h-5 w-5 mr-2 text-blue-400" />
        Security Elements
      </h2>
      
      <div className="space-y-6">
        {nodeCategories.map((category) => {
          const IconComponent = category.icon;
          return (
            <div key={category.title}>
              <h3 className={`text-sm font-medium mb-3 flex items-center ${category.color}`}>
                <IconComponent className="h-4 w-4 mr-2" />
                {category.title}
              </h3>
              
              <div className="space-y-2">
                {category.nodes.map((node) => (
                  <div
                    key={`${node.type}-${node.subtype}`}
                    draggable
                    onDragStart={(event) => onDragStart(event, node)}
                    className={`security-node-item p-3 rounded-lg cursor-grab border border-opacity-20 ${getNodeColorClass(node.type)}`}
                  >
                    <div className="text-white text-sm font-medium">
                      {node.label}
                    </div>
                    <div className="text-gray-300 text-xs mt-1">
                      {node.description}
                    </div>
                    {node.mitre_ids.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {node.mitre_ids.map((id) => (
                          <span
                            key={id}
                            className="px-2 py-1 bg-gray-700 text-gray-300 text-xs rounded"
                          >
                            {id}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
      
      <div className="mt-6 p-3 bg-gray-700 rounded-lg">
        <div className="text-xs text-gray-300">
          <strong>How to use:</strong>
          <br />
          • Drag elements from library to canvas
          <br />
          • Connect elements to show relationships
          <br />
          • Click "Simulate" to analyze attack paths
        </div>
      </div>
    </div>
  );
};

export { SecurityNodeLibrary };