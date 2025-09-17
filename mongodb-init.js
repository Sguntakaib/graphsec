// MongoDB initialization script
print('Starting MongoDB initialization...');

// Switch to the security modeling platform database
db = db.getSiblingDB('security_modeling_platform');

// Create collections with indexes
db.createCollection('diagrams');
db.createCollection('templates');
db.createCollection('simulations');
db.createCollection('vulnerabilities');

// Create indexes for better performance
db.diagrams.createIndex({ "id": 1 }, { unique: true });
db.diagrams.createIndex({ "created_at": 1 });
db.diagrams.createIndex({ "updated_at": 1 });

db.templates.createIndex({ "id": 1 }, { unique: true });
db.templates.createIndex({ "category": 1 });

db.simulations.createIndex({ "diagram_id": 1 });
db.simulations.createIndex({ "created_at": 1 });

db.vulnerabilities.createIndex({ "node_id": 1 });
db.vulnerabilities.createIndex({ "severity": 1 });

// Insert default templates
db.templates.insertMany([
  {
    "id": "web-app-template",
    "name": "Web Application Security",
    "description": "Basic web application threat model with common attack vectors",
    "category": "Web Application",
    "nodes": [
      {
        "id": "web-app-1",
        "type": "custom",
        "subtype": "WebApp",
        "position": { "x": 400, "y": 200 },
        "data": { "label": "Web Application", "subtype": "WebApp" }
      },
      {
        "id": "attacker-1", 
        "type": "custom",
        "subtype": "ExternalAttacker",
        "position": { "x": 100, "y": 200 },
        "data": { "label": "External Attacker", "subtype": "ExternalAttacker" }
      },
      {
        "id": "database-1",
        "type": "custom", 
        "subtype": "Database",
        "position": { "x": 700, "y": 200 },
        "data": { "label": "Database", "subtype": "Database" }
      }
    ],
    "edges": [
      {
        "id": "e1",
        "source": "attacker-1",
        "target": "web-app-1",
        "type": "custom",
        "data": { "label": "HTTP Requests" }
      },
      {
        "id": "e2", 
        "source": "web-app-1",
        "target": "database-1",
        "type": "custom",
        "data": { "label": "Database Queries" }
      }
    ]
  }
]);

print('MongoDB initialization completed successfully!');

// Create user for the application (optional, for production use)
// db.createUser({
//   user: "security_platform_user",
//   pwd: "secure_password_here",
//   roles: [
//     {
//       role: "readWrite",
//       db: "security_modeling_platform"
//     }
//   ]
// });