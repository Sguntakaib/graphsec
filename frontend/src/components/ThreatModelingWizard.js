import React, { useState, useEffect } from 'react';
import { 
  Shield, 
  CheckCircle2, 
  AlertTriangle, 
  Info, 
  ArrowRight, 
  ArrowLeft, 
  Save, 
  Play,
  BookOpen,
  Target,
  Database,
  Network,
  Users,
  Lock,
  BarChart3,
  FileCheck,
  Zap,
  X
} from 'lucide-react';

// Import wizard step components
import SystemOverviewStep from './wizard-steps/SystemOverviewStep';
import AssetIdentificationStep from './wizard-steps/AssetIdentificationStep';

const ThreatModelingWizard = ({ 
  isVisible, 
  onClose, 
  onComplete, 
  currentDiagram,
  existingNodes = [],
  existingEdges = []
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [wizardData, setWizardData] = useState({
    systemOverview: {},
    assetInventory: [],
    trustBoundaries: [],
    dataFlows: [],
    threatActors: [],
    attackSurfaces: [],
    securityControls: [],
    riskAssessment: {},
    complianceFrameworks: [],
    implementationPlan: {}
  });
  const [stepProgress, setStepProgress] = useState({});
  const [recommendations, setRecommendations] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);

  const wizardSteps = [
    {
      id: 'overview',
      title: 'System Overview',
      description: 'Define your system context and objectives',
      icon: Target,
      component: SystemOverviewStep
    },
    {
      id: 'assets',
      title: 'Asset Identification',
      description: 'Identify and classify critical assets',
      icon: Database,
      component: AssetIdentificationStep
    },
    {
      id: 'boundaries',
      title: 'Trust Boundaries',
      description: 'Define security zones and boundaries',
      icon: Shield,
      component: TrustBoundariesStep
    },
    {
      id: 'dataflows',
      title: 'Data Flow Analysis',
      description: 'Map data flows and communication paths',
      icon: Network,
      component: DataFlowStep
    },
    {
      id: 'threats',
      title: 'Threat Identification',
      description: 'Identify potential threat actors',
      icon: Users,
      component: ThreatIdentificationStep
    },
    {
      id: 'surfaces',
      title: 'Attack Surface Analysis',
      description: 'Analyze potential attack vectors',
      icon: Target,
      component: AttackSurfaceStep
    },
    {
      id: 'controls',
      title: 'Security Controls',
      description: 'Assess existing and required controls',
      icon: Lock,
      component: SecurityControlsStep
    },
    {
      id: 'risk',
      title: 'Risk Assessment',
      description: 'Analyze and prioritize risks',
      icon: BarChart3,
      component: RiskAssessmentStep
    },
    {
      id: 'compliance',
      title: 'Compliance Mapping',
      description: 'Map to compliance frameworks',
      icon: FileCheck,
      component: ComplianceStep
    },
    {
      id: 'implementation',
      title: 'Implementation Plan',
      description: 'Generate actionable recommendations',
      icon: Zap,
      component: ImplementationStep
    }
  ];

  const currentStepData = wizardSteps[currentStep];
  const CurrentStepComponent = currentStepData?.component;

  // Load recommendations based on current step and data
  useEffect(() => {
    if (currentStep > 0) {
      loadStepRecommendations();
    }
  }, [currentStep, wizardData]);

  const loadStepRecommendations = async () => {
    try {
      setIsProcessing(true);
      
      // Call backend for contextual recommendations based on current step
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/wizard/recommendations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          step: currentStepData.id,
          wizardData: wizardData,
          existingNodes: existingNodes,
          existingEdges: existingEdges
        })
      });

      if (response.ok) {
        const data = await response.json();
        setRecommendations(data.recommendations || []);
      }
    } catch (error) {
      console.error('Error loading recommendations:', error);
      // Provide fallback recommendations
      setRecommendations(getFallbackRecommendations(currentStepData.id));
    } finally {
      setIsProcessing(false);
    }
  };

  const getFallbackRecommendations = (stepId) => {
    const fallbackRecommendations = {
      overview: [
        'Define clear system boundaries and scope',
        'Identify primary business objectives',
        'Document key stakeholders and users'
      ],
      assets: [
        'Classify assets by criticality (Critical, High, Medium, Low)',
        'Include both technical and business assets',
        'Consider data assets, system components, and processes'
      ],
      boundaries: [
        'Define trust zones based on security requirements',
        'Identify boundaries between internal and external systems',
        'Consider network segmentation and access controls'
      ],
      dataflows: [
        'Map all data inputs and outputs',
        'Identify sensitive data paths',
        'Document authentication and authorization flows'
      ],
      threats: [
        'Consider internal and external threat actors',
        'Analyze threat motivations and capabilities',
        'Reference MITRE ATT&CK framework for threat intelligence'
      ],
      surfaces: [
        'Identify all system entry points',
        'Analyze network-accessible services',
        'Consider physical and social attack vectors'
      ],
      controls: [
        'Map existing security controls to assets',
        'Identify control gaps and redundancies',
        'Consider preventive, detective, and corrective controls'
      ],
      risk: [
        'Calculate risk using impact and likelihood',
        'Prioritize risks by business impact',
        'Consider risk appetite and tolerance'
      ],
      compliance: [
        'Map to relevant frameworks (SOC2, ISO 27001, NIST)',
        'Identify compliance requirements',
        'Document control mappings'
      ],
      implementation: [
        'Prioritize recommendations by risk reduction',
        'Consider implementation complexity and cost',
        'Create actionable timeline and ownership'
      ]
    };

    return fallbackRecommendations[stepId] || [];
  };

  const updateWizardData = (stepId, data) => {
    setWizardData(prev => ({
      ...prev,
      [stepId]: data
    }));
    
    // Update step progress
    setStepProgress(prev => ({
      ...prev,
      [stepId]: calculateStepCompleteness(stepId, data)
    }));
  };

  const calculateStepCompleteness = (stepId, data) => {
    // Simple completeness calculation - can be made more sophisticated
    if (!data || (Array.isArray(data) && data.length === 0)) return 0;
    if (typeof data === 'object') {
      const fields = Object.keys(data);
      const completedFields = fields.filter(field => data[field] && data[field] !== '');
      return Math.round((completedFields.length / Math.max(fields.length, 1)) * 100);
    }
    return Array.isArray(data) && data.length > 0 ? 100 : 0;
  };

  const handleNext = () => {
    if (currentStep < wizardSteps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleComplete = async () => {
    try {
      setIsProcessing(true);
      
      // Generate final threat model based on wizard data
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/wizard/generate-model`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          wizardData: wizardData,
          diagramId: currentDiagram?.id
        })
      });

      if (response.ok) {
        const result = await response.json();
        onComplete(result);
      } else {
        // Fallback: provide summary of wizard data
        onComplete({
          summary: wizardData,
          recommendations: recommendations,
          implementationPlan: wizardData.implementationPlan
        });
      }
    } catch (error) {
      console.error('Error completing wizard:', error);
      // Provide fallback completion
      onComplete({
        summary: wizardData,
        recommendations: recommendations,
        implementationPlan: wizardData.implementationPlan
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const jumpToStep = (stepIndex) => {
    setCurrentStep(stepIndex);
  };

  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-800 rounded-lg shadow-2xl w-full max-w-6xl h-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-700">
          <div className="flex items-center space-x-3">
            <Shield className="h-8 w-8 text-blue-400" />
            <div>
              <h2 className="text-2xl font-bold text-white">Guided Threat Modeling</h2>
              <p className="text-gray-400">Step-by-step security assessment wizard</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <div className="flex flex-1 overflow-hidden">
          {/* Progress Sidebar */}
          <div className="w-80 bg-gray-900 border-r border-gray-700 overflow-y-auto">
            <div className="p-4">
              <h3 className="text-white font-medium mb-4">Progress Overview</h3>
              <div className="space-y-2">
                {wizardSteps.map((step, index) => {
                  const Icon = step.icon;
                  const isActive = index === currentStep;
                  const isCompleted = stepProgress[step.id] === 100;
                  const isPartiallyCompleted = stepProgress[step.id] > 0 && stepProgress[step.id] < 100;
                  
                  return (
                    <button
                      key={step.id}
                      onClick={() => jumpToStep(index)}
                      className={`w-full text-left p-3 rounded-lg transition-colors ${
                        isActive 
                          ? 'bg-blue-700 border border-blue-500' 
                          : isCompleted
                          ? 'bg-green-700 hover:bg-green-600'
                          : isPartiallyCompleted
                          ? 'bg-yellow-700 hover:bg-yellow-600'
                          : 'bg-gray-700 hover:bg-gray-600'
                      }`}
                    >
                      <div className="flex items-center space-x-3">
                        <div className={`p-2 rounded ${
                          isActive ? 'bg-blue-600' : 
                          isCompleted ? 'bg-green-600' : 
                          isPartiallyCompleted ? 'bg-yellow-600' : 'bg-gray-600'
                        }`}>
                          {isCompleted ? (
                            <CheckCircle2 className="h-4 w-4 text-white" />
                          ) : (
                            <Icon className="h-4 w-4 text-white" />
                          )}
                        </div>
                        <div className="flex-1">
                          <div className={`font-medium ${isActive ? 'text-white' : isCompleted ? 'text-green-100' : 'text-gray-300'}`}>
                            {step.title}
                          </div>
                          <div className={`text-xs ${isActive ? 'text-blue-200' : 'text-gray-400'}`}>
                            {step.description}
                          </div>
                          {stepProgress[step.id] > 0 && (
                            <div className="mt-1">
                              <div className="w-full bg-gray-600 rounded-full h-1">
                                <div 
                                  className={`h-1 rounded-full ${
                                    isCompleted ? 'bg-green-400' : isPartiallyCompleted ? 'bg-yellow-400' : 'bg-blue-400'
                                  }`}
                                  style={{ width: `${stepProgress[step.id]}%` }}
                                ></div>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="flex-1 flex flex-col overflow-hidden">
            {/* Step Header */}
            <div className="p-6 border-b border-gray-700">
              <div className="flex items-center space-x-3">
                <currentStepData.icon className="h-6 w-6 text-blue-400" />
                <div>
                  <h3 className="text-xl font-bold text-white">{currentStepData.title}</h3>
                  <p className="text-gray-400">{currentStepData.description}</p>
                </div>
              </div>
            </div>

            {/* Step Content */}
            <div className="flex-1 flex overflow-hidden">
              <div className="flex-1 p-6 overflow-y-auto">
                {CurrentStepComponent && (
                  <CurrentStepComponent
                    data={wizardData[currentStepData.id] || {}}
                    onUpdate={(data) => updateWizardData(currentStepData.id, data)}
                    wizardData={wizardData}
                    existingNodes={existingNodes}
                    existingEdges={existingEdges}
                  />
                )}
              </div>

              {/* Recommendations Sidebar */}
              <div className="w-80 bg-gray-900 border-l border-gray-700 p-4 overflow-y-auto">
                <div className="flex items-center space-x-2 mb-4">
                  <Info className="h-5 w-5 text-blue-400" />
                  <h4 className="text-white font-medium">Recommendations</h4>
                </div>
                
                {isProcessing ? (
                  <div className="text-center py-4">
                    <div className="animate-spin h-6 w-6 border-2 border-blue-400 border-t-transparent rounded-full mx-auto mb-2"></div>
                    <p className="text-gray-400 text-sm">Loading recommendations...</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {recommendations.map((rec, index) => (
                      <div key={index} className="bg-gray-800 rounded p-3">
                        <div className="flex items-start space-x-2">
                          <AlertTriangle className="h-4 w-4 text-yellow-400 mt-0.5 flex-shrink-0" />
                          <p className="text-gray-300 text-sm">{rec}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Navigation Footer */}
            <div className="p-6 border-t border-gray-700">
              <div className="flex items-center justify-between">
                <button
                  onClick={handlePrevious}
                  disabled={currentStep === 0}
                  className="px-4 py-2 bg-gray-700 text-white rounded hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                >
                  <ArrowLeft className="h-4 w-4" />
                  <span>Previous</span>
                </button>

                <div className="text-gray-400 text-sm">
                  Step {currentStep + 1} of {wizardSteps.length}
                </div>

                {currentStep === wizardSteps.length - 1 ? (
                  <button
                    onClick={handleComplete}
                    disabled={isProcessing}
                    className="px-6 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50 flex items-center space-x-2"
                  >
                    <Play className="h-4 w-4" />
                    <span>{isProcessing ? 'Generating...' : 'Complete & Generate'}</span>
                  </button>
                ) : (
                  <button
                    onClick={handleNext}
                    className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 flex items-center space-x-2"
                  >
                    <span>Next</span>
                    <ArrowRight className="h-4 w-4" />
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Placeholder step components - will be implemented individually

const TrustBoundariesStep = ({ data, onUpdate }) => (
  <div className="text-white">Trust Boundaries Step - Coming next...</div>
);

const DataFlowStep = ({ data, onUpdate }) => (
  <div className="text-white">Data Flow Step - Coming next...</div>
);

const ThreatIdentificationStep = ({ data, onUpdate }) => (
  <div className="text-white">Threat Identification Step - Coming next...</div>
);

const AttackSurfaceStep = ({ data, onUpdate }) => (
  <div className="text-white">Attack Surface Step - Coming next...</div>
);

const SecurityControlsStep = ({ data, onUpdate }) => (
  <div className="text-white">Security Controls Step - Coming next...</div>
);

const RiskAssessmentStep = ({ data, onUpdate }) => (
  <div className="text-white">Risk Assessment Step - Coming next...</div>
);

const ComplianceStep = ({ data, onUpdate }) => (
  <div className="text-white">Compliance Step - Coming next...</div>
);

const ImplementationStep = ({ data, onUpdate }) => (
  <div className="text-white">Implementation Step - Coming next...</div>
);

export default ThreatModelingWizard;