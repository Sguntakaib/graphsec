import React from 'react';

/**
 * Smart Node Connector - Handles automatic node creation and linking
 * based on questionnaire responses
 */
class SmartNodeConnector {
  constructor(setNodes, setEdges, saveStateToUndoStack) {
    this.setNodes = setNodes;
    this.setEdges = setEdges;
    this.saveStateToUndoStack = saveStateToUndoStack;
  }

  /**
   * Process questionnaire answers and create linked nodes automatically
   */
  processQuestionnaireAnswers(sourceNodeId, sourceNodeType, answers, currentNodes) {
    const nodesToCreate = [];
    const edgesToCreate = [];

    // Process different node types
    switch (sourceNodeType) {
      case 'WebApp':
        this.processWebAppAnswers(sourceNodeId, answers, nodesToCreate, edgesToCreate, currentNodes);
        break;
      case 'API':
        this.processAPIAnswers(sourceNodeId, answers, nodesToCreate, edgesToCreate, currentNodes);
        break;
      case 'Database':
        this.processDatabaseAnswers(sourceNodeId, answers, nodesToCreate, edgesToCreate, currentNodes);
        break;
    }

    // Create nodes and edges if any were generated
    if (nodesToCreate.length > 0 || edgesToCreate.length > 0) {
      this.saveStateToUndoStack();
      
      if (nodesToCreate.length > 0) {
        this.setNodes(prevNodes => [...prevNodes, ...nodesToCreate]);
      }
      
      if (edgesToCreate.length > 0) {
        this.setEdges(prevEdges => [...prevEdges, ...edgesToCreate]);
      }
    }

    return { nodesCreated: nodesToCreate.length, edgesCreated: edgesToCreate.length };
  }

  processWebAppAnswers(sourceNodeId, answers, nodesToCreate, edgesToCreate, currentNodes) {
    const sourceNode = currentNodes.find(n => n.id === sourceNodeId);
    if (!sourceNode) return;

    const baseX = sourceNode.position.x;
    const baseY = sourceNode.position.y;

    // NOTE: API and Database node creation is now handled by the conditional dependency system
    // This prevents duplicate node creation and ensures proper questionnaire chaining
    // The conditional dependency system will check 'webapp_api_endpoints' and 'webapp_database_connection'
    // and create nodes accordingly with proper questionnaire flow

    // Check WAF protection
    const wafProtection = answers['webapp_waf_protection'];
    if (wafProtection && wafProtection !== 'None' && wafProtection !== 'Unknown') {
      const wafNodeId = `waf-${sourceNodeId}-${Date.now()}`;
      const wafNode = this.createWAFNode(wafNodeId, baseX - 200, baseY);
      nodesToCreate.push(wafNode);
      
      // Create edge from WAF to WebApp
      const wafEdge = this.createEdge(wafNodeId, sourceNodeId, 'Protects');
      edgesToCreate.push(wafEdge);
    }

    // Create attacker node if security is weak
    const authType = answers['webapp_login'];
    if (authType === 'None' || authType === 'Password Only') {
      const attackerNodeId = `attacker-${sourceNodeId}-${Date.now()}`;
      const attackerNode = this.createAttackerNode(attackerNodeId, baseX - 300, baseY - 150);
      nodesToCreate.push(attackerNode);
      
      // Create attack edge
      const attackEdge = this.createEdge(attackerNodeId, sourceNodeId, 'Targets');
      edgesToCreate.push(attackEdge);
    }
  }

  processAPIAnswers(sourceNodeId, answers, nodesToCreate, edgesToCreate, currentNodes) {
    const sourceNode = currentNodes.find(n => n.id === sourceNodeId);
    if (!sourceNode) return;

    const baseX = sourceNode.position.x;
    const baseY = sourceNode.position.y;

    // Create API Gateway if sophisticated auth is used
    const authMethod = answers['api_auth_method'];
    if (['OAuth 2.0', 'JWT'].includes(authMethod)) {
      const gatewayNodeId = `gateway-${sourceNodeId}-${Date.now()}`;
      const gatewayNode = this.createAPIGatewayNode(gatewayNodeId, baseX - 200, baseY);
      nodesToCreate.push(gatewayNode);
      
      const gatewayEdge = this.createEdge(gatewayNodeId, sourceNodeId, 'Routes to');
      edgesToCreate.push(gatewayEdge);
    }

    // Create rate limiter if configured
    const rateLimit = answers['api_rate_limiting'];
    if (rateLimit && rateLimit !== 'None') {
      const limiterNodeId = `ratelimit-${sourceNodeId}-${Date.now()}`;
      const limiterNode = this.createRateLimiterNode(limiterNodeId, baseX, baseY - 150);
      nodesToCreate.push(limiterNode);
      
      const limiterEdge = this.createEdge(limiterNodeId, sourceNodeId, 'Protects');
      edgesToCreate.push(limiterEdge);
    }
  }

  processDatabaseAnswers(sourceNodeId, answers, nodesToCreate, edgesToCreate, currentNodes) {
    const sourceNode = currentNodes.find(n => n.id === sourceNodeId);
    if (!sourceNode) return;

    const baseX = sourceNode.position.x;
    const baseY = sourceNode.position.y;

    // NOTE: Backup and Monitoring node creation is now handled by the conditional dependency system
    // This prevents duplicate node creation and ensures proper questionnaire chaining
    // The conditional dependency system will check 'db_backup_enabled' and 'db_monitoring_enabled'
    // and create nodes accordingly with proper questionnaire flow
  }

  // Node creation helper methods
  createAPINode(id, x, y) {
    return {
      id,
      type: 'custom',
      position: { x, y },
      data: {
        type: 'Asset',
        subtype: 'API',
        label: 'API Endpoint',
        description: 'Auto-generated API node',
        criticality: 'Medium',
        intelligentNode: true,
        autoGenerated: true
      }
    };
  }

  createDatabaseNode(id, x, y) {
    return {
      id,
      type: 'custom',
      position: { x, y },
      data: {
        type: 'Asset',
        subtype: 'Database',
        label: 'Database',
        description: 'Auto-generated database node',
        criticality: 'High',
        intelligentNode: true,
        autoGenerated: true
      }
    };
  }

  createWAFNode(id, x, y) {
    return {
      id,
      type: 'custom',
      position: { x, y },
      data: {
        type: 'Control',
        subtype: 'WAF',
        label: 'Web Application Firewall',
        description: 'Auto-generated WAF control',
        effectiveness: 80,
        autoGenerated: true
      }
    };
  }

  createAttackerNode(id, x, y) {
    return {
      id,
      type: 'custom',
      position: { x, y },
      data: {
        type: 'Actor',
        subtype: 'ExternalAttacker',
        label: 'External Attacker',
        description: 'Potential threat actor',
        sophistication: 'Medium',
        autoGenerated: true
      }
    };
  }

  createAPIGatewayNode(id, x, y) {
    return {
      id,
      type: 'custom',
      position: { x, y },
      data: {
        type: 'Control',
        subtype: 'APIGateway',
        label: 'API Gateway',
        description: 'API Gateway with authentication',
        effectiveness: 85,
        autoGenerated: true
      }
    };
  }

  createRateLimiterNode(id, x, y) {
    return {
      id,
      type: 'custom',
      position: { x, y },
      data: {
        type: 'Control',
        subtype: 'RateLimit',
        label: 'Rate Limiter',
        description: 'API rate limiting control',
        effectiveness: 70,
        autoGenerated: true
      }
    };
  }

  createBackupNode(id, x, y) {
    return {
      id,
      type: 'custom',
      position: { x, y },
      data: {
        type: 'Asset',
        subtype: 'Backup',
        label: 'Backup System',
        description: 'Database backup storage',
        criticality: 'Medium',
        autoGenerated: true
      }
    };
  }

  createMonitoringNode(id, x, y) {
    return {
      id,
      type: 'custom',
      position: { x, y },
      data: {
        type: 'Signal',
        subtype: 'Monitor',
        label: 'DB Monitor',
        description: 'Database monitoring system',
        autoGenerated: true
      }
    };
  }

  createEdge(sourceId, targetId, label) {
    return {
      id: `edge-${sourceId}-${targetId}-${Date.now()}`,
      source: sourceId,
      target: targetId,
      label: label,
      type: 'draggable',  // Use draggable type for label positioning
      animated: true,
      style: {
        strokeWidth: 2,
        stroke: '#10B981', // Green for auto-generated connections
        strokeDasharray: '3,3'
      },
      markerEnd: {
        type: 'arrowclosed',
        color: '#10B981',
      },
      data: {
        autoGenerated: true
      }
    };
  }
}

export default SmartNodeConnector;