import React, { useState, useCallback } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Switch } from './ui/switch';
import { AlertCircle, CheckCircle, Loader2, Play, Shield, Target, Zap } from 'lucide-react';
import { Alert, AlertDescription } from './ui/alert';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const CoreLoopDashboard = () => {
  const [activeTab, setActiveTab] = useState('questionnaire');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState({});
  const [error, setError] = useState(null);

  // Questionnaire state
  const [questionnaireData, setQuestionnaireData] = useState({
    node_subtype: 'WebApp',
    responses: {
      authentication_method: 'oauth2',
      encryption_enabled: true,
      input_validation: 'comprehensive'
    },
    business_context: {
      criticality: 'high',
      data_classification: 'confidential'
    }
  });

  // Simulation state
  const [simulationData, setSimulationData] = useState({
    nodes: [
      {
        id: 'attacker-1',
        type: 'Actor',
        subtype: 'ExternalAttacker',
        label: 'External Attacker',
        position: { x: 100, y: 100 }
      },
      {
        id: 'webapp-1',
        type: 'Asset',
        subtype: 'WebApp',
        label: 'Web Application',
        position: { x: 300, y: 100 }
      },
      {
        id: 'database-1',
        type: 'Asset',
        subtype: 'Database',
        label: 'Database',
        position: { x: 500, y: 100 }
      }
    ],
    edges: [
      {
        id: 'edge-1',
        source: 'attacker-1',
        target: 'webapp-1',
        label: 'Attack'
      },
      {
        id: 'edge-2',
        source: 'webapp-1',
        target: 'database-1',
        label: 'Access'
      }
    ]
  });

  // Rules evaluation state
  const [rulesData, setRulesData] = useState({
    nodes: [
      {
        id: 'webapp-1',
        type: 'Asset',
        subtype: 'WebApp',
        label: 'Web Application',
        data: { encryption_enabled: false, authentication: 'basic' }
      },
      {
        id: 'database-1',
        type: 'Asset',
        subtype: 'Database',
        label: 'Database',
        data: { encryption_at_rest: false, access_control: 'weak' }
      }
    ],
    edges: [
      {
        id: 'edge-1',
        source: 'webapp-1',
        target: 'database-1',
        label: 'Connection'
      }
    ]
  });

  const callAPI = useCallback(async (endpoint, data, method = 'POST') => {
    const response = await fetch(`${BACKEND_URL}/api${endpoint}`, {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
      body: method !== 'GET' ? JSON.stringify(data) : undefined,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }

    return await response.json();
  }, []);

  const runQuestionnaireCompletion = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await callAPI(
        `/questionnaires/${questionnaireData.node_subtype}/complete`,
        {
          responses: questionnaireData.responses,
          business_context: questionnaireData.business_context
        }
      );
      setResults(prev => ({ ...prev, questionnaire: result }));
      setActiveTab('results');
    } catch (err) {
      setError(`Questionnaire Completion Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const getQuestionnairePrompts = async () => {
    setLoading(true);
    setError(null);
    try {
      // Use specific endpoints for WebApp, API, Database, Backup, and Monitoring to get option_descriptions
      let endpoint;
      if (questionnaireData.node_subtype === 'WebApp') {
        endpoint = `/questionnaires/WebApp?level=basic`;
      } else if (questionnaireData.node_subtype === 'API') {
        endpoint = `/questionnaires/API?level=basic`;
      } else if (questionnaireData.node_subtype === 'Database') {
        endpoint = `/questionnaires/Database?level=basic`;
      } else if (questionnaireData.node_subtype === 'Backup') {
        endpoint = `/questionnaires/Backup?level=basic`;
      } else if (questionnaireData.node_subtype === 'Monitoring') {
        endpoint = `/questionnaires/Monitoring?level=basic`;
      } else {
        endpoint = `/questionnaires/${questionnaireData.node_subtype}`;
      }
      
      const result = await callAPI(endpoint, null, 'GET');
      setResults(prev => ({ ...prev, prompts: result }));
    } catch (err) {
      setError(`Questionnaire Prompts Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const runSimulation = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await callAPI('/simulate', simulationData);
      setResults(prev => ({ ...prev, simulation: result }));
      setActiveTab('results');
    } catch (err) {
      setError(`Simulation Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const runRulesEvaluation = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await callAPI('/rules/evaluate', rulesData);
      setResults(prev => ({ ...prev, rules: result }));
      setActiveTab('results');
    } catch (err) {
      setError(`Rules Evaluation Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const runAllCoreLoop = async () => {
    setLoading(true);
    setError(null);
    try {
      // Run all 4 endpoints in sequence
      const questionnaireResult = await callAPI(
        `/questionnaires/${questionnaireData.node_subtype}/complete`,
        {
          responses: questionnaireData.responses,
          business_context: questionnaireData.business_context
        }
      );

      // Use specific endpoints for WebApp, API, and Database to get option_descriptions
      let promptsEndpoint;
      if (questionnaireData.node_subtype === 'WebApp') {
        promptsEndpoint = `/questionnaires/WebApp?level=basic`;
      } else if (questionnaireData.node_subtype === 'API') {
        promptsEndpoint = `/questionnaires/API?level=basic`;
      } else if (questionnaireData.node_subtype === 'Database') {
        promptsEndpoint = `/questionnaires/Database?level=basic`;
      } else {
        promptsEndpoint = `/questionnaires/${questionnaireData.node_subtype}`;
      }

      const promptsResult = await callAPI(
        promptsEndpoint,
        null,
        'GET'
      );

      const simulationResult = await callAPI('/simulate', simulationData);
      const rulesResult = await callAPI('/rules/evaluate', rulesData);

      setResults({
        questionnaire: questionnaireResult,
        prompts: promptsResult,
        simulation: simulationResult,
        rules: rulesResult
      });
      setActiveTab('results');
    } catch (err) {
      setError(`Core Loop Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-6xl mx-auto p-6 space-y-6">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold text-gray-900">Phase 1 Core Loop Dashboard</h1>
        <p className="text-gray-600">
          Test and interact with the 4 critical Core Loop endpoints
        </p>
        <div className="flex justify-center gap-2">
          <Badge variant="secondary">POST /api/questionnaires/{'{node_subtype}'}/complete</Badge>
          <Badge variant="secondary">GET /api/questionnaires/{'{node_subtype}'}</Badge>
          <Badge variant="secondary">POST /api/simulate</Badge>
          <Badge variant="secondary">POST /api/rules/evaluate</Badge>
        </div>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="flex justify-center mb-4">
        <Button 
          onClick={runAllCoreLoop} 
          disabled={loading}
          className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-3 text-lg"
        >
          {loading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Running Core Loop...
            </>
          ) : (
            <>
              <Zap className="mr-2 h-4 w-4" />
              Run Complete Core Loop
            </>
          )}
        </Button>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid grid-cols-5 w-full">
          <TabsTrigger value="questionnaire" className="flex items-center gap-2">
            <Shield className="h-4 w-4" />
            Questionnaire
          </TabsTrigger>
          <TabsTrigger value="simulation" className="flex items-center gap-2">
            <Target className="h-4 w-4" />
            Simulation
          </TabsTrigger>
          <TabsTrigger value="rules" className="flex items-center gap-2">
            <CheckCircle className="h-4 w-4" />
            Rules
          </TabsTrigger>
          <TabsTrigger value="results" className="flex items-center gap-2">
            <Play className="h-4 w-4" />
            Results
          </TabsTrigger>
          <TabsTrigger value="docs" className="flex items-center gap-2">
            📖 Docs
          </TabsTrigger>
        </TabsList>

        <TabsContent value="questionnaire" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Questionnaire Completion</CardTitle>
              <CardDescription>
                Test POST /api/questionnaires/{'{node_subtype}'}/complete and GET /api/questionnaires/{'{node_subtype}'}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="node-subtype">Node Subtype</Label>
                  <Select
                    value={questionnaireData.node_subtype}
                    onValueChange={(value) => setQuestionnaireData(prev => ({ ...prev, node_subtype: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="WebApp">WebApp</SelectItem>
                      <SelectItem value="Database">Database</SelectItem>
                      <SelectItem value="API">API</SelectItem>
                      <SelectItem value="ExternalAttacker">ExternalAttacker</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="auth-method">Authentication Method</Label>
                  <Select
                    value={questionnaireData.responses.authentication_method}
                    onValueChange={(value) => setQuestionnaireData(prev => ({
                      ...prev,
                      responses: { ...prev.responses, authentication_method: value }
                    }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="oauth2">OAuth2</SelectItem>
                      <SelectItem value="basic">Basic Auth</SelectItem>
                      <SelectItem value="jwt">JWT</SelectItem>
                      <SelectItem value="none">None</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center space-x-2">
                  <Switch
                    id="encryption"
                    checked={questionnaireData.responses.encryption_enabled}
                    onCheckedChange={(checked) => setQuestionnaireData(prev => ({
                      ...prev,
                      responses: { ...prev.responses, encryption_enabled: checked }
                    }))}
                  />
                  <Label htmlFor="encryption">Encryption Enabled</Label>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="validation">Input Validation</Label>
                  <Select
                    value={questionnaireData.responses.input_validation}
                    onValueChange={(value) => setQuestionnaireData(prev => ({
                      ...prev,
                      responses: { ...prev.responses, input_validation: value }
                    }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="comprehensive">Comprehensive</SelectItem>
                      <SelectItem value="basic">Basic</SelectItem>
                      <SelectItem value="minimal">Minimal</SelectItem>
                      <SelectItem value="none">None</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="criticality">Business Criticality</Label>
                  <Select
                    value={questionnaireData.business_context.criticality}
                    onValueChange={(value) => setQuestionnaireData(prev => ({
                      ...prev,
                      business_context: { ...prev.business_context, criticality: value }
                    }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="critical">Critical</SelectItem>
                      <SelectItem value="high">High</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="low">Low</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="classification">Data Classification</Label>
                  <Select
                    value={questionnaireData.business_context.data_classification}
                    onValueChange={(value) => setQuestionnaireData(prev => ({
                      ...prev,
                      business_context: { ...prev.business_context, data_classification: value }
                    }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="confidential">Confidential</SelectItem>
                      <SelectItem value="internal">Internal</SelectItem>
                      <SelectItem value="public">Public</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="flex gap-2">
                <Button onClick={runQuestionnaireCompletion} disabled={loading}>
                  {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Shield className="mr-2 h-4 w-4" />}
                  Complete Questionnaire
                </Button>
                <Button onClick={getQuestionnairePrompts} disabled={loading} variant="outline">
                  Get Prompts
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="simulation" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Attack Path Simulation</CardTitle>
              <CardDescription>
                Test POST /api/simulate with standalone simulation data
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="sim-data">Simulation Data (JSON)</Label>
                <Textarea
                  id="sim-data"
                  rows={10}
                  value={JSON.stringify(simulationData, null, 2)}
                  onChange={(e) => {
                    try {
                      setSimulationData(JSON.parse(e.target.value));
                    } catch (err) {
                      // Ignore parse errors while typing
                    }
                  }}
                  className="font-mono text-sm"
                />
              </div>
              <Button onClick={runSimulation} disabled={loading}>
                {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Target className="mr-2 h-4 w-4" />}
                Run Simulation
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="rules" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Rules Evaluation</CardTitle>
              <CardDescription>
                Test POST /api/rules/evaluate with security rules
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="rules-data">Rules Data (JSON)</Label>
                <Textarea
                  id="rules-data"
                  rows={10}
                  value={JSON.stringify(rulesData, null, 2)}
                  onChange={(e) => {
                    try {
                      setRulesData(JSON.parse(e.target.value));
                    } catch (err) {
                      // Ignore parse errors while typing
                    }
                  }}
                  className="font-mono text-sm"
                />
              </div>
              <Button onClick={runRulesEvaluation} disabled={loading}>
                {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <CheckCircle className="mr-2 h-4 w-4" />}
                Evaluate Rules
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="results" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {results.questionnaire && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Shield className="h-4 w-4" />
                    Questionnaire Results
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 text-sm">
                    <div><strong>Completion ID:</strong> {results.questionnaire.completion_id}</div>
                    <div><strong>Findings:</strong> {Array.isArray(results.questionnaire.findings) ? results.questionnaire.findings.length : 'N/A'}</div>
                    <div><strong>Recommendations:</strong> {Array.isArray(results.questionnaire.recommendations) ? results.questionnaire.recommendations.length : 'N/A'}</div>
                    <div><strong>Success:</strong> {results.questionnaire.success ? '✅' : '❌'}</div>
                  </div>
                </CardContent>
              </Card>
            )}

            {results.prompts && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Shield className="h-4 w-4" />
                    Questionnaire Prompts
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 text-sm">
                    <div><strong>Security Branches:</strong> {results.prompts.security_branches?.length || 0}</div>
                    <div><strong>Prompts:</strong> {results.prompts.prompts?.length || 0}</div>
                  </div>
                </CardContent>
              </Card>
            )}

            {results.simulation && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Target className="h-4 w-4" />
                    Simulation Results
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 text-sm">
                    <div><strong>Simulation ID:</strong> {results.simulation.simulation_id}</div>
                    <div><strong>Attack Paths:</strong> {results.simulation.attack_paths?.length || 0}</div>
                    <div><strong>MITRE Techniques:</strong> {results.simulation.mitre_techniques?.length || 0}</div>
                    <div><strong>Recommendations:</strong> {results.simulation.recommendations?.length || 0}</div>
                  </div>
                </CardContent>
              </Card>
            )}

            {results.rules && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4" />
                    Rules Evaluation Results
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 text-sm">
                    <div><strong>Evaluation ID:</strong> {results.rules.evaluation_id}</div>
                    <div><strong>Triggered Rules:</strong> {results.rules.triggered_rules?.length || 0}</div>
                    <div><strong>Risk Score:</strong> {results.rules.risk_score?.toFixed(2) || 'N/A'}</div>
                    <div><strong>Recommendations:</strong> {results.rules.recommendations?.length || 0}</div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        <TabsContent value="docs" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Core Loop API Documentation</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold mb-2">1. POST /api/questionnaires/{'{node_subtype}'}/complete</h3>
                  <p className="text-sm text-gray-600 mb-2">Complete questionnaire processing with end-to-end flow</p>
                  <Badge>Standalone Mode ✅</Badge>
                </div>

                <div>
                  <h3 className="text-lg font-semibold mb-2">2. GET /api/questionnaires/{'{node_subtype}'}</h3>
                  <p className="text-sm text-gray-600 mb-2">Get questionnaire prompts and security branches</p>
                  <Badge>Security Branches ✅</Badge>
                </div>

                <div>
                  <h3 className="text-lg font-semibold mb-2">3. POST /api/simulate</h3>
                  <p className="text-sm text-gray-600 mb-2">Run standalone attack path simulation</p>
                  <Badge>Standalone Simulation ✅</Badge>
                </div>

                <div>
                  <h3 className="text-lg font-semibold mb-2">4. POST /api/rules/evaluate</h3>
                  <p className="text-sm text-gray-600 mb-2">Evaluate security rules with impact assessment</p>
                  <Badge>Standalone Rules ✅</Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default CoreLoopDashboard;