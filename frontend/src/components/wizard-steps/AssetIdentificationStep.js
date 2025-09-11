import React, { useState, useEffect } from 'react';
import { 
  Database, 
  Server, 
  Globe, 
  Files, 
  Key, 
  Users, 
  Building2, 
  Smartphone,
  Plus, 
  Edit, 
  Trash2, 
  AlertCircle,
  CheckCircle2,
  DollarSign,
  Shield,
  Clock,
  Target
} from 'lucide-react';

const AssetIdentificationStep = ({ data, onUpdate, wizardData, existingNodes, existingEdges }) => {
  const [assets, setAssets] = useState(data.assets || []);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingAsset, setEditingAsset] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    type: '',
    category: '',
    description: '',
    criticality: '',
    confidentiality: 'medium',
    integrity: 'medium',
    availability: 'medium',
    businessValue: 'medium',
    dataClassification: '',
    owner: '',
    location: '',
    dependencies: [],
    regulations: [],
    customAttributes: {}
  });

  // Update parent when assets change
  useEffect(() => {
    onUpdate({ assets });
  }, [assets, onUpdate]);

  const assetTypes = [
    { value: 'data', label: 'Data Asset', icon: Files, color: 'text-blue-400' },
    { value: 'application', label: 'Application', icon: Globe, color: 'text-green-400' },
    { value: 'system', label: 'System/Server', icon: Server, color: 'text-purple-400' },
    { value: 'device', label: 'Device', icon: Smartphone, color: 'text-orange-400' },
    { value: 'network', label: 'Network Component', icon: Target, color: 'text-cyan-400' },
    { value: 'service', label: 'Service', icon: Building2, color: 'text-pink-400' },
    { value: 'people', label: 'Personnel', icon: Users, color: 'text-yellow-400' },
    { value: 'process', label: 'Business Process', icon: Clock, color: 'text-indigo-400' }
  ];

  const assetCategories = {
    data: ['Database', 'File System', 'API Data', 'Configuration Data', 'Backup Data', 'Log Data'],
    application: ['Web Application', 'Mobile App', 'Desktop Application', 'API Service', 'Microservice'],
    system: ['Web Server', 'Database Server', 'Application Server', 'Load Balancer', 'Virtual Machine'],
    device: ['Laptop', 'Mobile Device', 'IoT Device', 'Network Device', 'Security Appliance'],
    network: ['Router', 'Switch', 'Firewall', 'VPN Gateway', 'DNS Server', 'Load Balancer'],
    service: ['Authentication Service', 'Payment Service', 'Notification Service', 'Monitoring Service'],
    people: ['Administrators', 'Developers', 'End Users', 'Contractors', 'Support Staff'],
    process: ['Deployment Process', 'Backup Process', 'Incident Response', 'User Onboarding']
  };

  const criticalityLevels = [
    { value: 'critical', label: 'Critical', color: 'bg-red-600', description: 'Mission critical, immediate impact if compromised' },
    { value: 'high', label: 'High', color: 'bg-orange-600', description: 'Important to business operations' },
    { value: 'medium', label: 'Medium', color: 'bg-yellow-600', description: 'Standard business importance' },
    { value: 'low', label: 'Low', color: 'bg-green-600', description: 'Low business impact' }
  ];

  const dataClassifications = [
    'Public', 'Internal', 'Confidential', 'Restricted', 'Top Secret'
  ];

  const commonRegulations = [
    'GDPR', 'HIPAA', 'PCI DSS', 'SOX', 'FERPA', 'CCPA', 'SOC 2', 'ISO 27001'
  ];

  const resetForm = () => {
    setFormData({
      name: '',
      type: '',
      category: '',
      description: '',
      criticality: '',
      confidentiality: 'medium',
      integrity: 'medium',
      availability: 'medium',
      businessValue: 'medium',
      dataClassification: '',
      owner: '',
      location: '',
      dependencies: [],
      regulations: [],
      customAttributes: {}
    });
  };

  const handleAddAsset = () => {
    if (!formData.name.trim() || !formData.type || !formData.criticality) {
      return;
    }

    const newAsset = {
      id: Date.now().toString(),
      ...formData,
      createdAt: new Date().toISOString()
    };

    setAssets(prev => [...prev, newAsset]);
    resetForm();
    setShowAddForm(false);
  };

  const handleEditAsset = (asset) => {
    setFormData({ ...asset });
    setEditingAsset(asset.id);
    setShowAddForm(true);
  };

  const handleUpdateAsset = () => {
    if (!formData.name.trim() || !formData.type || !formData.criticality) {
      return;
    }

    setAssets(prev => prev.map(asset => 
      asset.id === editingAsset 
        ? { ...formData, id: editingAsset, updatedAt: new Date().toISOString() }
        : asset
    ));
    
    resetForm();
    setShowAddForm(false);
    setEditingAsset(null);
  };

  const handleDeleteAsset = (assetId) => {
    setAssets(prev => prev.filter(asset => asset.id !== assetId));
  };

  const addDependency = (dependency) => {
    if (dependency.trim() && !formData.dependencies.includes(dependency.trim())) {
      setFormData(prev => ({
        ...prev,
        dependencies: [...prev.dependencies, dependency.trim()]
      }));
    }
  };

  const removeDependency = (index) => {
    setFormData(prev => ({
      ...prev,
      dependencies: prev.dependencies.filter((_, i) => i !== index)
    }));
  };

  const addRegulation = (regulation) => {
    if (regulation && !formData.regulations.includes(regulation)) {
      setFormData(prev => ({
        ...prev,
        regulations: [...prev.regulations, regulation]
      }));
    }
  };

  const removeRegulation = (index) => {
    setFormData(prev => ({
      ...prev,
      regulations: prev.regulations.filter((_, i) => i !== index)
    }));
  };

  const getCriticalityStats = () => {
    const stats = { critical: 0, high: 0, medium: 0, low: 0 };
    assets.forEach(asset => {
      stats[asset.criticality] = (stats[asset.criticality] || 0) + 1;
    });
    return stats;
  };

  const criticalityStats = getCriticalityStats();
  const isFormValid = formData.name.trim() && formData.type && formData.criticality;

  return (
    <div className="space-y-6">
      {/* Header with Stats */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <Database className="h-6 w-6 text-blue-400" />
            <h3 className="text-lg font-semibold text-white">Asset Inventory</h3>
          </div>
          <button
            onClick={() => setShowAddForm(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 flex items-center space-x-2"
          >
            <Plus className="h-4 w-4" />
            <span>Add Asset</span>
          </button>
        </div>

        {/* Asset Statistics */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
          {criticalityLevels.map(level => (
            <div key={level.value} className="bg-gray-700 rounded p-3 text-center">
              <div className={`w-4 h-4 rounded-full ${level.color} mx-auto mb-2`}></div>
              <div className="text-white font-bold text-lg">{criticalityStats[level.value] || 0}</div>
              <div className="text-gray-400 text-sm capitalize">{level.label}</div>
            </div>
          ))}
        </div>

        <div className="text-gray-400 text-sm">
          Total Assets: {assets.length} | 
          {assets.length > 0 ? ' Click on an asset to edit or delete' : ' Start by adding your first asset'}
        </div>
      </div>

      {/* Add/Edit Asset Form */}
      {showAddForm && (
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white">
              {editingAsset ? 'Edit Asset' : 'Add New Asset'}
            </h3>
            <button
              onClick={() => {
                setShowAddForm(false);
                setEditingAsset(null);
                resetForm();
              }}
              className="text-gray-400 hover:text-white"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Basic Information */}
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Asset Name *
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400"
                  placeholder="e.g., Customer Database, Payment API"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Asset Type *
                </label>
                <select
                  value={formData.type}
                  onChange={(e) => {
                    setFormData(prev => ({ 
                      ...prev, 
                      type: e.target.value,
                      category: '' // Reset category when type changes
                    }));
                  }}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                >
                  <option value="">Select asset type</option>
                  {assetTypes.map(type => (
                    <option key={type.value} value={type.value}>{type.label}</option>
                  ))}
                </select>
              </div>

              {formData.type && (
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Category
                  </label>
                  <select
                    value={formData.category}
                    onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                  >
                    <option value="">Select category</option>
                    {(assetCategories[formData.type] || []).map(category => (
                      <option key={category} value={category}>{category}</option>
                    ))}
                  </select>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                  rows={3}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400"
                  placeholder="Describe the asset's purpose, functionality, and importance..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Asset Owner
                </label>
                <input
                  type="text"
                  value={formData.owner}
                  onChange={(e) => setFormData(prev => ({ ...prev, owner: e.target.value }))}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400"
                  placeholder="e.g., IT Team, Security Team, John Doe"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Location
                </label>
                <input
                  type="text"
                  value={formData.location}
                  onChange={(e) => setFormData(prev => ({ ...prev, location: e.target.value }))}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400"
                  placeholder="e.g., AWS us-east-1, On-premises DC1"
                />
              </div>
            </div>

            {/* Security Classification */}
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Business Criticality *
                </label>
                <div className="space-y-2">
                  {criticalityLevels.map(level => (
                    <label key={level.value} className="flex items-center space-x-3">
                      <input
                        type="radio"
                        name="criticality"
                        value={level.value}
                        checked={formData.criticality === level.value}
                        onChange={(e) => setFormData(prev => ({ ...prev, criticality: e.target.value }))}
                        className="text-blue-600"
                      />
                      <div className={`w-3 h-3 rounded-full ${level.color}`}></div>
                      <div>
                        <span className="text-white font-medium">{level.label}</span>
                        <span className="text-gray-400 text-sm ml-2">{level.description}</span>
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Data Classification
                </label>
                <select
                  value={formData.dataClassification}
                  onChange={(e) => setFormData(prev => ({ ...prev, dataClassification: e.target.value }))}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                >
                  <option value="">Select classification</option>
                  {dataClassifications.map(classification => (
                    <option key={classification} value={classification}>{classification}</option>
                  ))}
                </select>
              </div>

              {/* CIA Triad */}
              <div className="space-y-3">
                <h4 className="text-sm font-medium text-gray-300">Security Requirements</h4>
                {['confidentiality', 'integrity', 'availability'].map(requirement => (
                  <div key={requirement}>
                    <label className="block text-xs text-gray-400 mb-1 capitalize">
                      {requirement}
                    </label>
                    <select
                      value={formData[requirement]}
                      onChange={(e) => setFormData(prev => ({ ...prev, [requirement]: e.target.value }))}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white text-sm"
                    >
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                      <option value="critical">Critical</option>
                    </select>
                  </div>
                ))}
              </div>

              {/* Compliance Requirements */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Regulatory Requirements
                </label>
                <div className="flex flex-wrap gap-2 mb-2">
                  {formData.regulations.map((regulation, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center px-2 py-1 rounded text-xs bg-yellow-600 text-white"
                    >
                      {regulation}
                      <button
                        onClick={() => removeRegulation(index)}
                        className="ml-1 text-yellow-200 hover:text-white"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
                <select
                  onChange={(e) => {
                    if (e.target.value) {
                      addRegulation(e.target.value);
                      e.target.value = '';
                    }
                  }}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white text-sm"
                >
                  <option value="">Add regulation</option>
                  {commonRegulations.map(regulation => (
                    <option 
                      key={regulation} 
                      value={regulation}
                      disabled={formData.regulations.includes(regulation)}
                    >
                      {regulation}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Form Actions */}
          <div className="flex justify-end space-x-3 mt-6 pt-4 border-t border-gray-700">
            <button
              onClick={() => {
                setShowAddForm(false);
                setEditingAsset(null);
                resetForm();
              }}
              className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
            >
              Cancel
            </button>
            <button
              onClick={editingAsset ? handleUpdateAsset : handleAddAsset}
              disabled={!isFormValid}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {editingAsset ? 'Update Asset' : 'Add Asset'}
            </button>
          </div>
        </div>
      )}

      {/* Assets List */}
      <div className="space-y-4">
        {assets.map(asset => {
          const AssetIcon = assetTypes.find(t => t.value === asset.type)?.icon || Database;
          const criticalityLevel = criticalityLevels.find(l => l.value === asset.criticality);
          
          return (
            <div key={asset.id} className="bg-gray-800 rounded-lg p-4 border border-gray-700 hover:border-gray-600 transition-colors">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-4 flex-1">
                  <div className={`p-2 rounded ${criticalityLevel?.color || 'bg-gray-600'}`}>
                    <AssetIcon className="h-5 w-5 text-white" />
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h4 className="text-white font-medium">{asset.name}</h4>
                      <span className="text-xs px-2 py-1 bg-gray-700 text-gray-300 rounded">
                        {asset.type}
                      </span>
                      {asset.category && (
                        <span className="text-xs px-2 py-1 bg-blue-700 text-blue-200 rounded">
                          {asset.category}
                        </span>
                      )}
                    </div>
                    
                    {asset.description && (
                      <p className="text-gray-400 text-sm mb-2">{asset.description}</p>
                    )}
                    
                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
                      <div>
                        <span className="text-gray-500">Criticality: </span>
                        <span className={`font-medium ${criticalityLevel?.color.replace('bg-', 'text-')}`}>
                          {asset.criticality}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-500">C/I/A: </span>
                        <span className="text-gray-300">
                          {asset.confidentiality[0]?.toUpperCase()}/
                          {asset.integrity[0]?.toUpperCase()}/
                          {asset.availability[0]?.toUpperCase()}
                        </span>
                      </div>
                      {asset.owner && (
                        <div>
                          <span className="text-gray-500">Owner: </span>
                          <span className="text-gray-300">{asset.owner}</span>
                        </div>
                      )}
                      {asset.dataClassification && (
                        <div>
                          <span className="text-gray-500">Classification: </span>
                          <span className="text-gray-300">{asset.dataClassification}</span>
                        </div>
                      )}
                    </div>
                    
                    {asset.regulations.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {asset.regulations.map((regulation, index) => (
                          <span key={index} className="text-xs px-2 py-1 bg-yellow-700 text-yellow-200 rounded">
                            {regulation}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
                
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleEditAsset(asset)}
                    className="p-2 text-blue-400 hover:text-blue-300 hover:bg-gray-700 rounded"
                  >
                    <Edit className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleDeleteAsset(asset.id)}
                    className="p-2 text-red-400 hover:text-red-300 hover:bg-gray-700 rounded"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Completion Status */}
      <div className="bg-gray-900 rounded-lg p-4 border border-gray-600">
        <div className="flex items-center space-x-2">
          {assets.length > 0 ? (
            <>
              <CheckCircle2 className="h-5 w-5 text-green-400" />
              <span className="text-green-400 font-medium">
                Asset Inventory Complete - {assets.length} assets identified
              </span>
            </>
          ) : (
            <>
              <AlertCircle className="h-5 w-5 text-yellow-400" />
              <span className="text-yellow-400 font-medium">
                No assets added yet - Add at least one asset to continue
              </span>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default AssetIdentificationStep;