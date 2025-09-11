import React, { useState, useEffect } from 'react';
import { 
  BookOpen, 
  Search, 
  Filter, 
  Clock, 
  Star, 
  Download, 
  Eye, 
  Tag,
  ShieldCheck,
  Globe,
  Cloud,
  Server,
  Zap,
  Lock,
  Users,
  Building,
  ChevronRight,
  CheckCircle,
  Info,
  Layers
} from 'lucide-react';

const TemplateLibrary = ({ onApplyTemplate, onClose }) => {
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedComplexity, setSelectedComplexity] = useState('all');
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [isPreviewMode, setIsPreviewMode] = useState(false);

  const categoryIcons = {
    'Web Application': Globe,
    'Cloud Native': Cloud,
    'Zero Trust': Lock,
    'Enterprise Network': Building,
    'IoT Device': Zap,
    'API Security': Server,
    'DevSecOps': Users,
    'Financial Services': ShieldCheck
  };

  const complexityColors = {
    'Basic': 'bg-green-900 text-green-300',
    'Intermediate': 'bg-yellow-900 text-yellow-300', 
    'Advanced': 'bg-red-900 text-red-300'
  };

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      setLoading(true);
      const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
      const response = await fetch(`${backendUrl}/api/templates`);
      if (response.ok) {
        const data = await response.json();
        setTemplates(data);
      } else {
        console.error('Failed to load templates');
      }
    } catch (error) {
      console.error('Error loading templates:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredTemplates = templates.filter(template => {
    const matchesSearch = searchTerm === '' || 
      template.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      template.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      template.use_case.toLowerCase().includes(searchTerm.toLowerCase()) ||
      template.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesCategory = selectedCategory === 'all' || template.category === selectedCategory;
    const matchesComplexity = selectedComplexity === 'all' || template.complexity === selectedComplexity;
    
    return matchesSearch && matchesCategory && matchesComplexity;
  });

  const handleApplyTemplate = async (template) => {
    try {
      if (onApplyTemplate) {
        await onApplyTemplate(template);
        onClose();
      }
    } catch (error) {
      console.error('Error applying template:', error);
    }
  };

  const renderTemplateCard = (template) => {
    const IconComponent = categoryIcons[template.category] || BookOpen;
    
    return (
      <div
        key={template.id}
        className="bg-gray-800 rounded-lg border border-gray-700 hover:border-gray-600 transition-colors p-4 cursor-pointer"
        onClick={() => setSelectedTemplate(template)}
      >
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center space-x-2">
            <IconComponent className="h-5 w-5 text-blue-400" />
            <h3 className="text-white font-medium text-sm">{template.name}</h3>
          </div>
          <span className={`px-2 py-1 text-xs rounded ${complexityColors[template.complexity]}`}>
            {template.complexity}
          </span>
        </div>
        
        <p className="text-gray-300 text-xs mb-3 line-clamp-2">
          {template.description}
        </p>
        
        <div className="space-y-2">
          <div className="flex items-center text-xs text-gray-400">
            <Clock className="h-3 w-3 mr-1" />
            {template.estimated_time}
          </div>
          
          <div className="flex items-center text-xs text-gray-400">
            <Layers className="h-3 w-3 mr-1" />
            {template.nodes?.length || 0} nodes, {template.edges?.length || 0} edges
          </div>
          
          {template.tags && template.tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {template.tags.slice(0, 3).map((tag) => (
                <span key={tag} className="px-2 py-1 bg-gray-700 text-gray-300 text-xs rounded">
                  {tag}
                </span>
              ))}
              {template.tags.length > 3 && (
                <span className="px-2 py-1 bg-gray-700 text-gray-300 text-xs rounded">
                  +{template.tags.length - 3} more
                </span>
              )}
            </div>
          )}
        </div>
        
        <div className="flex justify-between items-center mt-4 pt-3 border-t border-gray-700">
          <button
            onClick={(e) => {
              e.stopPropagation();
              setSelectedTemplate(template);
              setIsPreviewMode(true);
            }}
            className="flex items-center space-x-1 text-blue-400 hover:text-blue-300 text-xs"
          >
            <Eye className="h-3 w-3" />
            <span>Preview</span>
          </button>
          
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleApplyTemplate(template);
            }}
            className="flex items-center space-x-1 text-green-400 hover:text-green-300 text-xs bg-green-900 bg-opacity-20 px-2 py-1 rounded"
          >
            <Download className="h-3 w-3" />
            <span>Apply</span>
          </button>
        </div>
      </div>
    );
  };

  const renderTemplateDetail = () => {
    if (!selectedTemplate) return null;
    
    const IconComponent = categoryIcons[selectedTemplate.category] || BookOpen;
    
    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <IconComponent className="h-6 w-6 text-blue-400" />
            <div>
              <h2 className="text-white font-semibold text-lg">{selectedTemplate.name}</h2>
              <p className="text-gray-400 text-sm">{selectedTemplate.category}</p>
            </div>
          </div>
          <div className="flex space-x-2">
            <span className={`px-3 py-1 text-sm rounded ${complexityColors[selectedTemplate.complexity]}`}>
              {selectedTemplate.complexity}
            </span>
            <button
              onClick={() => setSelectedTemplate(null)}
              className="text-gray-400 hover:text-white"
            >
              ×
            </button>
          </div>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column - Details */}
          <div className="space-y-4">
            <div>
              <h3 className="text-white font-medium mb-2">Description</h3>
              <p className="text-gray-300 text-sm">{selectedTemplate.description}</p>
            </div>
            
            <div>
              <h3 className="text-white font-medium mb-2">Use Case</h3>
              <p className="text-gray-300 text-sm">{selectedTemplate.use_case}</p>
            </div>
            
            <div>
              <h3 className="text-white font-medium mb-2">Components</h3>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="bg-gray-700 rounded p-3">
                  <div className="text-blue-400 font-medium">{selectedTemplate.nodes?.length || 0}</div>
                  <div className="text-gray-300">Security Nodes</div>
                </div>
                <div className="bg-gray-700 rounded p-3">
                  <div className="text-green-400 font-medium">{selectedTemplate.edges?.length || 0}</div>
                  <div className="text-gray-300">Relationships</div>
                </div>
              </div>
            </div>
            
            <div>
              <h3 className="text-white font-medium mb-2">Setup Time</h3>
              <div className="flex items-center text-gray-300 text-sm">
                <Clock className="h-4 w-4 mr-2" />
                {selectedTemplate.estimated_time}
              </div>
            </div>
          </div>
          
          {/* Right Column - Metadata */}
          <div className="space-y-4">
            {selectedTemplate.tags && selectedTemplate.tags.length > 0 && (
              <div>
                <h3 className="text-white font-medium mb-2">Tags</h3>
                <div className="flex flex-wrap gap-2">
                  {selectedTemplate.tags.map((tag) => (
                    <span key={tag} className="px-2 py-1 bg-gray-700 text-gray-300 text-sm rounded flex items-center">
                      <Tag className="h-3 w-3 mr-1" />
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}
            
            {selectedTemplate.compliance_frameworks && selectedTemplate.compliance_frameworks.length > 0 && (
              <div>
                <h3 className="text-white font-medium mb-2">Compliance Frameworks</h3>
                <div className="space-y-2">
                  {selectedTemplate.compliance_frameworks.map((framework) => (
                    <div key={framework} className="flex items-center text-sm text-gray-300">
                      <CheckCircle className="h-4 w-4 mr-2 text-green-400" />
                      {framework}
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            <div>
              <h3 className="text-white font-medium mb-2">Template Info</h3>
              <div className="text-sm text-gray-300 space-y-1">
                <div>Author: {selectedTemplate.author}</div>
                <div>Version: {selectedTemplate.version}</div>
                <div>Created: {new Date(selectedTemplate.created_at).toLocaleDateString()}</div>
              </div>
            </div>
          </div>
        </div>
        
        <div className="flex justify-end space-x-3 mt-6 pt-4 border-t border-gray-700">
          <button
            onClick={() => setSelectedTemplate(null)}
            className="px-4 py-2 text-gray-300 hover:text-white transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={() => handleApplyTemplate(selectedTemplate)}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors flex items-center space-x-2"
          >
            <Download className="h-4 w-4" />
            <span>Apply Template</span>
          </button>
        </div>
      </div>
    );
  };

  const categories = [...new Set(templates.map(t => t.category))];
  const complexities = ['Basic', 'Intermediate', 'Advanced'];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 rounded-lg max-w-6xl w-full max-h-[90vh] overflow-hidden">
        {selectedTemplate ? (
          <div className="p-6 overflow-y-auto max-h-[90vh]">
            {renderTemplateDetail()}
          </div>
        ) : (
          <>
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-700">
              <div className="flex items-center space-x-3">
                <BookOpen className="h-6 w-6 text-blue-400" />
                <div>
                  <h1 className="text-white font-semibold text-xl">Template Library</h1>
                  <p className="text-gray-400 text-sm">Pre-built security patterns for common architectures</p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-white text-xl"
              >
                ×
              </button>
            </div>
            
            {/* Search and Filters */}
            <div className="p-6 border-b border-gray-700">
              <div className="flex flex-col lg:flex-row gap-4">
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search templates, use cases, tags..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                  />
                </div>
                
                <div className="flex gap-3">
                  <select
                    value={selectedCategory}
                    onChange={(e) => setSelectedCategory(e.target.value)}
                    className="bg-gray-700 border border-gray-600 rounded-lg text-white px-3 py-2 focus:outline-none focus:border-blue-500"
                  >
                    <option value="all">All Categories</option>
                    {categories.map(cat => (
                      <option key={cat} value={cat}>{cat}</option>
                    ))}
                  </select>
                  
                  <select
                    value={selectedComplexity}
                    onChange={(e) => setSelectedComplexity(e.target.value)}
                    className="bg-gray-700 border border-gray-600 rounded-lg text-white px-3 py-2 focus:outline-none focus:border-blue-500"
                  >
                    <option value="all">All Complexity</option>
                    {complexities.map(comp => (
                      <option key={comp} value={comp}>{comp}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
            
            {/* Template Grid */}
            <div className="p-6">
              {loading ? (
                <div className="flex items-center justify-center py-12">
                  <div className="text-gray-400">Loading templates...</div>
                </div>
              ) : filteredTemplates.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {filteredTemplates.map(renderTemplateCard)}
                </div>
              ) : (
                <div className="text-center py-12">
                  <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <div className="text-white font-medium mb-2">No templates found</div>
                  <div className="text-gray-400 text-sm">
                    Try adjusting your search or filter criteria
                  </div>
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export { TemplateLibrary };