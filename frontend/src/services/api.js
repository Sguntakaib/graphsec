import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
const API = `${BACKEND_URL}/api`;

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Diagram API functions
export const getDiagrams = async () => {
  try {
    const response = await apiClient.get('/diagrams');
    return response.data;
  } catch (error) {
    throw new Error(`Failed to fetch diagrams: ${error.message}`);
  }
};

export const getDiagram = async (diagramId) => {
  try {
    const response = await apiClient.get(`/diagrams/${diagramId}`);
    return response.data;
  } catch (error) {
    throw new Error(`Failed to fetch diagram: ${error.message}`);
  }
};

export const createDiagram = async (diagramData) => {
  try {
    const response = await apiClient.post('/diagrams', diagramData);
    return response.data;
  } catch (error) {
    throw new Error(`Failed to create diagram: ${error.message}`);
  }
};

export const updateDiagram = async (diagramId, diagramData) => {
  try {
    const response = await apiClient.put(`/diagrams/${diagramId}`, diagramData);
    return response.data;
  } catch (error) {
    throw new Error(`Failed to update diagram: ${error.message}`);
  }
};

export const deleteDiagram = async (diagramId) => {
  try {
    const response = await apiClient.delete(`/diagrams/${diagramId}`);
    return response.data;
  } catch (error) {
    throw new Error(`Failed to delete diagram: ${error.message}`);
  }
};

// Simulation API functions
export const simulateAttackPaths = async (diagramId) => {
  try {
    const response = await apiClient.post(`/diagrams/${diagramId}/simulate`);
    return response.data;
  } catch (error) {
    throw new Error(`Failed to run simulation: ${error.message}`);
  }
};

export const getSimulations = async (diagramId) => {
  try {
    const response = await apiClient.get(`/diagrams/${diagramId}/simulations`);
    return response.data;
  } catch (error) {
    throw new Error(`Failed to fetch simulations: ${error.message}`);
  }
};

// Health check
export const healthCheck = async () => {
  try {
    const response = await apiClient.get('/');
    return response.data;
  } catch (error) {
    throw new Error(`Health check failed: ${error.message}`);
  }
};

// Advanced Analysis API functions
export const getMitreTechnique = async (techniqueId) => {
  try {
    const response = await apiClient.get(`/mitre/technique/${techniqueId}`);
    return response.data;
  } catch (error) {
    throw new Error(`Failed to fetch MITRE technique: ${error.message}`);
  }
};

export const getTechniquesByTactic = async (tactic) => {
  try {
    const response = await apiClient.get(`/mitre/techniques/by-tactic/${tactic}`);
    return response.data;
  } catch (error) {
    throw new Error(`Failed to fetch techniques by tactic: ${error.message}`);
  }
};

export const analyzeMitreCoverage = async (diagramId) => {
  try {
    const response = await apiClient.post(`/diagrams/${diagramId}/analyze-coverage`);
    return response.data;
  } catch (error) {
    throw new Error(`Failed to analyze MITRE coverage: ${error.message}`);
  }
};

export const getRiskAnalysis = async (diagramId) => {
  try {
    const response = await apiClient.get(`/diagrams/${diagramId}/risk-analysis`);
    return response.data;
  } catch (error) {
    throw new Error(`Failed to get risk analysis: ${error.message}`);
  }
};

export const autoLayoutDiagram = async (diagramId, algorithm = null) => {
  try {
    const url = algorithm 
      ? `/diagrams/${diagramId}/auto-layout?algorithm=${algorithm}`
      : `/diagrams/${diagramId}/auto-layout`;
    const response = await apiClient.post(url);
    return response.data;
  } catch (error) {
    throw new Error(`Failed to auto-layout diagram: ${error.message}`);
  }
};

export const getLayoutAlgorithms = async (diagramId) => {
  try {
    const response = await apiClient.get(`/diagrams/${diagramId}/layout-algorithms`);
    return response.data;
  } catch (error) {
    throw new Error(`Failed to get layout algorithms: ${error.message}`);
  }
};

export const generateLayoutAnimation = async (diagramId, fromAlgorithm, toAlgorithm, duration = 1.0, fps = 30) => {
  try {
    const response = await apiClient.post(`/diagrams/${diagramId}/layout-animation`, {
      from_algorithm: fromAlgorithm,
      to_algorithm: toAlgorithm,
      duration,
      fps
    });
    return response.data;
  } catch (error) {
    throw new Error(`Failed to generate layout animation: ${error.message}`);
  }
};

export const getLayoutMetrics = async (diagramId, algorithm = null) => {
  try {
    const url = algorithm 
      ? `/diagrams/${diagramId}/layout-metrics?algorithm=${algorithm}`
      : `/diagrams/${diagramId}/layout-metrics`;
    const response = await apiClient.get(url);
    return response.data;
  } catch (error) {
    throw new Error(`Failed to get layout metrics: ${error.message}`);
  }
};

export const optimizeLayout = async (diagramId) => {
  try {
    const response = await apiClient.post(`/diagrams/${diagramId}/optimize-layout`);
    return response.data;
  } catch (error) {
    throw new Error(`Failed to optimize layout: ${error.message}`);
  }
};

// Template API functions
export const getTemplates = async (category, complexity) => {
  try {
    const params = new URLSearchParams();
    if (category && category !== 'all') params.append('category', category);
    if (complexity && complexity !== 'all') params.append('complexity', complexity);
    
    const response = await apiClient.get(`/templates?${params.toString()}`);
    return response.data;
  } catch (error) {
    throw new Error(`Failed to fetch templates: ${error.message}`);
  }
};

export const getTemplate = async (templateId) => {
  try {
    const response = await apiClient.get(`/templates/${templateId}`);
    return response.data;
  } catch (error) {
    throw new Error(`Failed to fetch template: ${error.message}`);
  }
};

export const createTemplate = async (templateData) => {
  try {
    const response = await apiClient.post('/templates', templateData);
    return response.data;
  } catch (error) {
    throw new Error(`Failed to create template: ${error.message}`);
  }
};

export const updateTemplate = async (templateId, templateData) => {
  try {
    const response = await apiClient.put(`/templates/${templateId}`, templateData);
    return response.data;
  } catch (error) {
    throw new Error(`Failed to update template: ${error.message}`);
  }
};

export const deleteTemplate = async (templateId) => {
  try {
    const response = await apiClient.delete(`/templates/${templateId}`);
    return response.data;
  } catch (error) {
    throw new Error(`Failed to delete template: ${error.message}`);
  }
};

export const applyTemplateToCurrentDiagram = async (templateId, diagramId) => {
  try {
    const response = await apiClient.post(`/templates/${templateId}/apply/${diagramId}`);
    return response.data;
  } catch (error) {
    throw new Error(`Failed to apply template: ${error.message}`);
  }
};

export const getTemplateCategories = async () => {
  try {
    const response = await apiClient.get('/templates/categories');
    return response.data;
  } catch (error) {
    throw new Error(`Failed to fetch template categories: ${error.message}`);
  }
};

// Core Loop API functions
export const completeQuestionnaire = async (nodeSubtype, requestData) => {
  try {
    const response = await apiClient.post(`/questionnaires/${nodeSubtype}/complete`, requestData);
    return response.data;
  } catch (error) {
    throw new Error(`Failed to complete questionnaire: ${error.message}`);
  }
};

export const getQuestionnairePrompts = async (nodeSubtype) => {
  try {
    // Use specific endpoints for WebApp, API, and Database to get option_descriptions
    let endpoint;
    if (nodeSubtype === 'WebApp') {
      endpoint = `/questionnaires/WebApp?level=basic`;
    } else if (nodeSubtype === 'API') {
      endpoint = `/questionnaires/API?level=basic`;
    } else if (nodeSubtype === 'Database') {
      endpoint = `/questionnaires/Database?level=basic`;
    } else {
      endpoint = `/questionnaires/${nodeSubtype}`;
    }
    
    const response = await apiClient.get(endpoint);
    return response.data;
  } catch (error) {
    throw new Error(`Failed to get questionnaire prompts: ${error.message}`);
  }
};

export const runStandaloneSimulation = async (simulationData) => {
  try {
    const response = await apiClient.post('/simulate', simulationData);
    return response.data;
  } catch (error) {
    throw new Error(`Failed to run standalone simulation: ${error.message}`);
  }
};

export const evaluateSecurityRules = async (rulesData) => {
  try {
    const response = await apiClient.post('/rules/evaluate', rulesData);
    return response.data;
  } catch (error) {
    throw new Error(`Failed to evaluate security rules: ${error.message}`);
  }
};

export const runCompleteCoreLoop = async (questionnaireData, simulationData, rulesData) => {
  try {
    // Run all 4 Core Loop endpoints
    const [questionnaireResult, promptsResult, simulationResult, rulesResult] = await Promise.all([
      completeQuestionnaire(questionnaireData.node_subtype, {
        responses: questionnaireData.responses,
        business_context: questionnaireData.business_context
      }),
      getQuestionnairePrompts(questionnaireData.node_subtype),
      runStandaloneSimulation(simulationData),
      evaluateSecurityRules(rulesData)
    ]);

    return {
      questionnaire: questionnaireResult,
      prompts: promptsResult,
      simulation: simulationResult,
      rules: rulesResult
    };
  } catch (error) {
    throw new Error(`Failed to run complete Core Loop: ${error.message}`);
  }
};

export default apiClient;