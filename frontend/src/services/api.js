import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
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

export const autoLayoutDiagram = async (diagramId) => {
  try {
    const response = await apiClient.post(`/diagrams/${diagramId}/auto-layout`);
    return response.data;
  } catch (error) {
    throw new Error(`Failed to auto-layout diagram: ${error.message}`);
  }
};

export default apiClient;