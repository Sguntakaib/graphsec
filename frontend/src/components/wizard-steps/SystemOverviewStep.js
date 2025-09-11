import React, { useState, useEffect } from 'react';
import { 
  Building2, 
  Users, 
  Globe, 
  Database, 
  Shield, 
  AlertCircle,
  CheckCircle2,
  Info,
  Target,
  Layers,
  Clock,
  DollarSign
} from 'lucide-react';

const SystemOverviewStep = ({ data, onUpdate, wizardData, existingNodes, existingEdges }) => {
  const [formData, setFormData] = useState({
    systemName: data.systemName || '',
    systemDescription: data.systemDescription || '',
    businessContext: data.businessContext || '',
    systemType: data.systemType || '',
    deploymentModel: data.deploymentModel || '',
    userTypes: data.userTypes || [],
    dataTypes: data.dataTypes || [],
    complianceRequirements: data.complianceRequirements || [],
    businessCriticality: data.businessCriticality || '',
    securityObjectives: data.securityObjectives || {
      confidentiality: 'medium',
      integrity: 'medium',
      availability: 'medium'
    },
    stakeholders: data.stakeholders || [],
    assumptions: data.assumptions || [],
    constraints: data.constraints || []
  });

  const [validationErrors, setValidationErrors] = useState({});

  // Update parent component when form data changes
  useEffect(() => {
    const errors = validateFormData(formData);
    setValidationErrors(errors);
    onUpdate(formData);
  }, [formData, onUpdate]);

  const validateFormData = (data) => {
    const errors = {};
    
    if (!data.systemName?.trim()) errors.systemName = 'System name is required';
    if (!data.systemDescription?.trim()) errors.systemDescription = 'System description is required';
    if (!data.businessContext?.trim()) errors.businessContext = 'Business context is required';
    if (!data.systemType) errors.systemType = 'System type is required';
    if (!data.deploymentModel) errors.deploymentModel = 'Deployment model is required';
    if (!data.businessCriticality) errors.businessCriticality = 'Business criticality is required';
    if (data.userTypes.length === 0) errors.userTypes = 'At least one user type is required';
    if (data.dataTypes.length === 0) errors.dataTypes = 'At least one data type is required';
    
    return errors;
  };

  const updateField = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const updateSecurityObjective = (objective, value) => {
    setFormData(prev => ({
      ...prev,
      securityObjectives: {
        ...prev.securityObjectives,
        [objective]: value
      }
    }));
  };

  const addArrayItem = (field, item) => {
    if (item?.trim()) {
      setFormData(prev => ({
        ...prev,
        [field]: [...prev[field], item.trim()]
      }));
    }
  };

  const removeArrayItem = (field, index) => {
    setFormData(prev => ({
      ...prev,
      [field]: prev[field].filter((_, i) => i !== index)
    }));
  };

  const systemTypes = [
    { value: 'web_application', label: 'Web Application', icon: Globe },
    { value: 'mobile_application', label: 'Mobile Application', icon: Users },
    { value: 'api_service', label: 'API Service', icon: Database },
    { value: 'desktop_application', label: 'Desktop Application', icon: Building2 },
    { value: 'cloud_infrastructure', label: 'Cloud Infrastructure', icon: Layers },
    { value: 'iot_system', label: 'IoT System', icon: Target },
    { value: 'enterprise_system', label: 'Enterprise System', icon: Building2 },
    { value: 'other', label: 'Other', icon: AlertCircle }
  ];

  const deploymentModels = [
    { value: 'cloud_public', label: 'Public Cloud', description: 'AWS, Azure, GCP' },
    { value: 'cloud_private', label: 'Private Cloud', description: 'Dedicated cloud environment' },
    { value: 'cloud_hybrid', label: 'Hybrid Cloud', description: 'Mix of public and private' },
    { value: 'on_premises', label: 'On-Premises', description: 'Internal data centers' },
    { value: 'saas', label: 'Software as a Service', description: 'Third-party hosted' },
    { value: 'container', label: 'Containerized', description: 'Docker, Kubernetes' }
  ];

  const businessCriticalityLevels = [
    { value: 'critical', label: 'Critical', color: 'text-red-400', description: 'Mission critical, high business impact' },
    { value: 'high', label: 'High', color: 'text-orange-400', description: 'Important business function' },
    { value: 'medium', label: 'Medium', color: 'text-yellow-400', description: 'Standard business operation' },
    { value: 'low', label: 'Low', color: 'text-green-400', description: 'Supporting function' }
  ];

  const commonUserTypes = [
    'End Users', 'Administrators', 'API Clients', 'External Partners', 
    'Customers', 'Employees', 'Contractors', 'Anonymous Users', 'Service Accounts'
  ];

  const commonDataTypes = [
    'Personal Data (PII)', 'Financial Data', 'Health Records (PHI)', 'Intellectual Property',
    'Authentication Credentials', 'Business Confidential', 'Public Information', 
    'System Configuration', 'Audit Logs', 'Encrypted Data'
  ];

  const commonComplianceFrameworks = [
    'SOC 2', 'ISO 27001', 'NIST Cybersecurity Framework', 'GDPR', 'HIPAA', 
    'PCI DSS', 'FedRAMP', 'FISMA', 'CIS Controls', 'OWASP'
  ];

  return (
    <div className="space-y-8">
      {/* System Identification */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div className="flex items-center space-x-3 mb-4">
          <Building2 className="h-6 w-6 text-blue-400" />
          <h3 className="text-lg font-semibold text-white">System Identification</h3>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              System Name *
            </label>
            <input
              type="text"
              value={formData.systemName}
              onChange={(e) => updateField('systemName', e.target.value)}
              className={`w-full px-3 py-2 bg-gray-700 border rounded-md text-white placeholder-gray-400 ${
                validationErrors.systemName ? 'border-red-500' : 'border-gray-600'
              }`}
              placeholder="e.g., Customer Portal, Payment API, Mobile App"
            />
            {validationErrors.systemName && (
              <p className="mt-1 text-sm text-red-400">{validationErrors.systemName}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              System Type *
            </label>
            <select
              value={formData.systemType}
              onChange={(e) => updateField('systemType', e.target.value)}
              className={`w-full px-3 py-2 bg-gray-700 border rounded-md text-white ${
                validationErrors.systemType ? 'border-red-500' : 'border-gray-600'
              }`}
            >
              <option value="">Select system type</option>
              {systemTypes.map(type => (
                <option key={type.value} value={type.value}>{type.label}</option>
              ))}
            </select>
            {validationErrors.systemType && (
              <p className="mt-1 text-sm text-red-400">{validationErrors.systemType}</p>
            )}
          </div>

          <div className="lg:col-span-2">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              System Description *
            </label>
            <textarea
              value={formData.systemDescription}
              onChange={(e) => updateField('systemDescription', e.target.value)}
              rows={3}
              className={`w-full px-3 py-2 bg-gray-700 border rounded-md text-white placeholder-gray-400 ${
                validationErrors.systemDescription ? 'border-red-500' : 'border-gray-600'
              }`}
              placeholder="Describe the system's primary functions, key features, and technical architecture..."
            />
            {validationErrors.systemDescription && (
              <p className="mt-1 text-sm text-red-400">{validationErrors.systemDescription}</p>
            )}
          </div>

          <div className="lg:col-span-2">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Business Context *
            </label>
            <textarea
              value={formData.businessContext}
              onChange={(e) => updateField('businessContext', e.target.value)}
              rows={2}
              className={`w-full px-3 py-2 bg-gray-700 border rounded-md text-white placeholder-gray-400 ${
                validationErrors.businessContext ? 'border-red-500' : 'border-gray-600'
              }`}
              placeholder="Explain the business purpose, value proposition, and organizational context..."
            />
            {validationErrors.businessContext && (
              <p className="mt-1 text-sm text-red-400">{validationErrors.businessContext}</p>
            )}
          </div>
        </div>
      </div>

      {/* Deployment & Environment */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div className="flex items-center space-x-3 mb-4">
          <Layers className="h-6 w-6 text-green-400" />
          <h3 className="text-lg font-semibold text-white">Deployment & Environment</h3>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Deployment Model *
            </label>
            <div className="space-y-2">
              {deploymentModels.map(model => (
                <label key={model.value} className="flex items-center space-x-3">
                  <input
                    type="radio"
                    name="deploymentModel"
                    value={model.value}
                    checked={formData.deploymentModel === model.value}
                    onChange={(e) => updateField('deploymentModel', e.target.value)}
                    className="text-blue-600"
                  />
                  <div>
                    <span className="text-white font-medium">{model.label}</span>
                    <span className="text-gray-400 text-sm ml-2">{model.description}</span>
                  </div>
                </label>
              ))}
            </div>
            {validationErrors.deploymentModel && (
              <p className="mt-1 text-sm text-red-400">{validationErrors.deploymentModel}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Business Criticality *
            </label>
            <div className="space-y-2">
              {businessCriticalityLevels.map(level => (
                <label key={level.value} className="flex items-center space-x-3">
                  <input
                    type="radio"
                    name="businessCriticality"
                    value={level.value}
                    checked={formData.businessCriticality === level.value}
                    onChange={(e) => updateField('businessCriticality', e.target.value)}
                    className="text-blue-600"
                  />
                  <div>
                    <span className={`font-medium ${level.color}`}>{level.label}</span>
                    <span className="text-gray-400 text-sm ml-2">{level.description}</span>
                  </div>
                </label>
              ))}
            </div>
            {validationErrors.businessCriticality && (
              <p className="mt-1 text-sm text-red-400">{validationErrors.businessCriticality}</p>
            )}
          </div>
        </div>
      </div>

      {/* Security Objectives */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div className="flex items-center space-x-3 mb-4">
          <Shield className="h-6 w-6 text-purple-400" />
          <h3 className="text-lg font-semibold text-white">Security Objectives (CIA Triad)</h3>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {Object.entries(formData.securityObjectives).map(([objective, level]) => (
            <div key={objective}>
              <label className="block text-sm font-medium text-gray-300 mb-2 capitalize">
                {objective} Requirements
              </label>
              <select
                value={level}
                onChange={(e) => updateSecurityObjective(objective, e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
              >
                <option value="low">Low - Basic protection needed</option>
                <option value="medium">Medium - Standard protection</option>
                <option value="high">High - Strong protection required</option>
                <option value="critical">Critical - Maximum protection</option>
              </select>
            </div>
          ))}
        </div>
      </div>

      {/* Users and Data */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* User Types */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center space-x-3 mb-4">
            <Users className="h-6 w-6 text-blue-400" />
            <h3 className="text-lg font-semibold text-white">User Types *</h3>
          </div>
          
          <div className="space-y-3">
            <div className="flex flex-wrap gap-2">
              {formData.userTypes.map((userType, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-600 text-white"
                >
                  {userType}
                  <button
                    onClick={() => removeArrayItem('userTypes', index)}
                    className="ml-2 text-blue-200 hover:text-white"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
            
            <div className="grid grid-cols-2 gap-2">
              {commonUserTypes.map(userType => (
                <button
                  key={userType}
                  onClick={() => addArrayItem('userTypes', userType)}
                  disabled={formData.userTypes.includes(userType)}
                  className="text-left p-2 text-sm border border-gray-600 rounded hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed text-gray-300"
                >
                  {userType}
                </button>
              ))}
            </div>
            
            {validationErrors.userTypes && (
              <p className="text-sm text-red-400">{validationErrors.userTypes}</p>
            )}
          </div>
        </div>

        {/* Data Types */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center space-x-3 mb-4">
            <Database className="h-6 w-6 text-green-400" />
            <h3 className="text-lg font-semibold text-white">Data Types *</h3>
          </div>
          
          <div className="space-y-3">
            <div className="flex flex-wrap gap-2">
              {formData.dataTypes.map((dataType, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-green-600 text-white"
                >
                  {dataType}
                  <button
                    onClick={() => removeArrayItem('dataTypes', index)}
                    className="ml-2 text-green-200 hover:text-white"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
            
            <div className="grid grid-cols-1 gap-2">
              {commonDataTypes.map(dataType => (
                <button
                  key={dataType}
                  onClick={() => addArrayItem('dataTypes', dataType)}
                  disabled={formData.dataTypes.includes(dataType)}
                  className="text-left p-2 text-sm border border-gray-600 rounded hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed text-gray-300"
                >
                  {dataType}
                </button>
              ))}
            </div>
            
            {validationErrors.dataTypes && (
              <p className="text-sm text-red-400">{validationErrors.dataTypes}</p>
            )}
          </div>
        </div>
      </div>

      {/* Compliance Requirements */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div className="flex items-center space-x-3 mb-4">
          <Shield className="h-6 w-6 text-yellow-400" />
          <h3 className="text-lg font-semibold text-white">Compliance Requirements</h3>
        </div>
        
        <div className="space-y-3">
          <div className="flex flex-wrap gap-2">
            {formData.complianceRequirements.map((framework, index) => (
              <span
                key={index}
                className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-yellow-600 text-white"
              >
                {framework}
                <button
                  onClick={() => removeArrayItem('complianceRequirements', index)}
                  className="ml-2 text-yellow-200 hover:text-white"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
          
          <div className="grid grid-cols-2 lg:grid-cols-3 gap-2">
            {commonComplianceFrameworks.map(framework => (
              <button
                key={framework}
                onClick={() => addArrayItem('complianceRequirements', framework)}
                disabled={formData.complianceRequirements.includes(framework)}
                className="text-left p-2 text-sm border border-gray-600 rounded hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed text-gray-300"
              >
                {framework}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Completion Status */}
      <div className="bg-gray-900 rounded-lg p-4 border border-gray-600">
        <div className="flex items-center space-x-2">
          {Object.keys(validationErrors).length === 0 ? (
            <>
              <CheckCircle2 className="h-5 w-5 text-green-400" />
              <span className="text-green-400 font-medium">System Overview Complete</span>
            </>
          ) : (
            <>
              <AlertCircle className="h-5 w-5 text-yellow-400" />
              <span className="text-yellow-400 font-medium">
                {Object.keys(validationErrors).length} required fields missing
              </span>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default SystemOverviewStep;