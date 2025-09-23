# Security Modeling Platform - Deployment Guide

A comprehensive guide to deploy the Security Modeling Platform with React frontend, FastAPI backend, and MongoDB database.

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Dependencies Installation](#dependencies-installation)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [Services Deployment](#services-deployment)
- [Production Deployment](#production-deployment)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Monitoring & Health Checks](#monitoring--health-checks)
- [Troubleshooting](#troubleshooting)
- [Maintenance](#maintenance)

## Overview

The Security Modeling Platform is a full-stack application consisting of:

- **Frontend**: React application with Vite build system
- **Backend**: FastAPI Python application  
- **Database**: MongoDB for data persistence
- **Process Management**: Supervisor for service management
- **Architecture**: Microservices with API-first approach

## Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+ recommended) or Docker environment
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Storage**: Minimum 10GB free space
- **CPU**: 2+ cores recommended

### Software Dependencies
- **Node.js**: v18.0.0 or higher
- **Python**: 3.9 or higher
- **MongoDB**: 5.0 or higher
- **Yarn**: Package manager for frontend
- **pip**: Python package manager
- **Supervisor**: Process control system

## Environment Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd security-modeling-platform
```

### 2. Create Environment Structure
```bash
# Create necessary directories
mkdir -p logs
mkdir -p data/mongodb
mkdir -p backup
```

### 3. Set File Permissions
```bash
chmod +x scripts/*.sh  # If any shell scripts exist
```

## Dependencies Installation

### Backend Dependencies
```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Install additional dependencies if needed
pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/
```

### Frontend Dependencies
```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies using Yarn
yarn install

# Build production assets
yarn build
```

## Configuration

### 1. Backend Environment Variables
Create `/app/backend/.env`:
```env
# Database Configuration
MONGO_URL=mongodb://localhost:27017/security_modeling_platform

# API Configuration
API_HOST=0.0.0.0
API_PORT=8001

# Security Keys (Generate secure random strings)
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here

# External API Keys (Optional)
EMERGENT_LLM_KEY=your-emergent-llm-key-here

# Environment
ENVIRONMENT=production
DEBUG=False

# CORS Settings
ALLOWED_ORIGINS=https://yourdomain.com

# Logging
LOG_LEVEL=INFO
```

### 2. Frontend Environment Variables  
Create `/app/frontend/.env`:
```env
# Backend API URL - Critical: Must match your deployment URL
REACT_APP_BACKEND_URL=https://yourdomain.com/api

# Build Configuration
GENERATE_SOURCEMAP=false
REACT_APP_ENV=production
```

### 3. Supervisor Configuration
Create `/etc/supervisor/conf.d/security-platform.conf`:
```ini
[group:security-platform]
programs=backend,frontend,mongodb

[program:backend]
directory=/app/backend
command=uvicorn server:app --host 0.0.0.0 --port 8001 --workers 4
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/backend.err.log
stdout_logfile=/var/log/supervisor/backend.out.log
environment=PYTHONPATH="/app/backend"

[program:frontend]
directory=/app/frontend
command=yarn preview --host 0.0.0.0 --port 3000
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/frontend.err.log
stdout_logfile=/var/log/supervisor/frontend.out.log

[program:mongodb]
command=mongod --dbpath /var/lib/mongodb --logpath /var/log/mongodb/mongod.log --fork
user=mongodb
autostart=true
autorestart=true
```

## Database Setup

### 1. Install MongoDB
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y mongodb

# Or install MongoDB Community Edition
wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/5.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-5.0.list
sudo apt update
sudo apt install -y mongodb-org
```

### 2. Configure MongoDB
Create `/etc/mongod.conf`:
```yaml
storage:
  dbPath: /var/lib/mongodb
  journal:
    enabled: true

systemLog:
  destination: file
  logAppend: true
  path: /var/log/mongodb/mongod.log

net:
  port: 27017
  bindIp: 127.0.0.1

security:
  authorization: enabled

setParameter:
  enableLocalhostAuthBypass: false
```

### 3. Create Database User
```bash
# Start MongoDB
sudo systemctl start mongod

# Create admin user
mongosh
use admin
db.createUser({
  user: "admin",
  pwd: "secure-password",
  roles: ["userAdminAnyDatabase", "dbAdminAnyDatabase", "readWriteAnyDatabase"]
})

# Create application database
use security_modeling_platform
db.createUser({
  user: "app_user", 
  pwd: "app-password",
  roles: ["readWrite"]
})
```

### 4. Update Connection String
Update `MONGO_URL` in backend `.env`:
```env
MONGO_URL=mongodb://app_user:app-password@localhost:27017/security_modeling_platform
```

## Services Deployment

### 1. Using Supervisor (Recommended)
```bash
# Install Supervisor
sudo apt install supervisor

# Copy configuration
sudo cp supervisor.conf /etc/supervisor/conf.d/security-platform.conf

# Reload Supervisor
sudo supervisorctl reread
sudo supervisorctl update

# Start services
sudo supervisorctl start security-platform:*

# Check status
sudo supervisorctl status
```

### 2. Manual Service Start
```bash
# Start MongoDB
sudo systemctl start mongod

# Start Backend
cd /app/backend
nohup uvicorn server:app --host 0.0.0.0 --port 8001 &

# Start Frontend  
cd /app/frontend
nohup yarn preview --host 0.0.0.0 --port 3000 &
```

## Production Deployment

### 1. Web Server Configuration (Nginx)
Install and configure Nginx as reverse proxy:

```nginx
# /etc/nginx/sites-available/security-platform
server {
    listen 80;
    server_name yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    # SSL Configuration
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    
    # Backend API Routes
    location /api/ {
        proxy_pass http://127.0.0.1:8001/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Frontend Static Files
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Static Assets Caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        proxy_pass http://127.0.0.1:3000;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/security-platform /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 2. SSL Certificate (Let's Encrypt)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 3. Firewall Configuration
```bash
# Configure UFW firewall
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw --force enable
```

## Docker Deployment

### 1. Create Dockerfile for Backend
Create `/app/backend/Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/

# Copy application code
COPY . .

# Expose port
EXPOSE 8001

# Run application
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001"]
```

### 2. Create Dockerfile for Frontend  
Create `/app/frontend/Dockerfile`:
```dockerfile
FROM node:18-alpine as build

WORKDIR /app

# Copy package files
COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile

# Copy source code and build
COPY . .
RUN yarn build

# Production stage
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 3. Docker Compose
Create `/app/docker-compose.yml`:
```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:5.0
    container_name: security-platform-mongo
    restart: unless-stopped
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: secure-password
      MONGO_INITDB_DATABASE: security_modeling_platform
    volumes:
      - mongodb_data:/data/db
      - ./scripts/mongo-init.js:/docker-entrypoint-initdb.d/mongo-init.js:ro
    ports:
      - "27017:27017"
    networks:
      - security-platform

  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile
    container_name: security-platform-backend
    restart: unless-stopped
    environment:
      - MONGO_URL=mongodb://app_user:app-password@mongodb:27017/security_modeling_platform
      - SECRET_KEY=your-secret-key
      - ENVIRONMENT=production
    depends_on:
      - mongodb
    ports:
      - "8001:8001"
    networks:
      - security-platform
    volumes:
      - ./logs:/app/logs

  frontend:
    build:
      context: ./frontend  
      dockerfile: Dockerfile
    container_name: security-platform-frontend
    restart: unless-stopped
    environment:
      - REACT_APP_BACKEND_URL=http://localhost:8001/api
    depends_on:
      - backend
    ports:
      - "3000:80"
    networks:
      - security-platform

volumes:
  mongodb_data:

networks:
  security-platform:
    driver: bridge
```

### 4. Deploy with Docker Compose
```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Scale services
docker-compose up -d --scale backend=3

# Stop services
docker-compose down
```

## Kubernetes Deployment

### 1. MongoDB Deployment
Create `k8s/mongodb.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mongodb
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mongodb
  template:
    metadata:
      labels:
        app: mongodb
    spec:
      containers:
      - name: mongodb
        image: mongo:5.0
        ports:
        - containerPort: 27017
        env:
        - name: MONGO_INITDB_ROOT_USERNAME
          value: "admin"
        - name: MONGO_INITDB_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mongodb-secret
              key: password
        volumeMounts:
        - name: mongodb-storage
          mountPath: /data/db
      volumes:
      - name: mongodb-storage
        persistentVolumeClaim:
          claimName: mongodb-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: mongodb-service
spec:
  ports:
  - port: 27017
  selector:
    app: mongodb
```

### 2. Backend Deployment
Create `k8s/backend.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: security-platform/backend:latest
        ports:
        - containerPort: 8001
        env:
        - name: MONGO_URL
          value: "mongodb://mongodb-service:27017/security_modeling_platform"
        livenessProbe:
          httpGet:
            path: /api/
            port: 8001
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/
            port: 8001
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service  
metadata:
  name: backend-service
spec:
  ports:
  - port: 8001
  selector:
    app: backend
```

### 3. Frontend Deployment
Create `k8s/frontend.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: security-platform/frontend:latest
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
spec:
  ports:
  - port: 80
  selector:
    app: frontend
```

### 4. Ingress Configuration
Create `k8s/ingress.yaml`:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: security-platform-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /$1
    nginx.ingress.kubernetes.io/use-regex: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - yourdomain.com
    secretName: security-platform-tls
  rules:
  - host: yourdomain.com
    http:
      paths:
      - path: /api/(.*)
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 8001
      - path: /(.*)
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
```

## Monitoring & Health Checks

### 1. Health Check Endpoints
The application provides these health check endpoints:

- **Backend Health**: `GET /api/` - Returns API status
- **Database Health**: Check MongoDB connection status
- **Frontend Health**: HTTP 200 response from static files

### 2. Monitoring Script
Create `/app/scripts/health-check.sh`:
```bash
#!/bin/bash

# Health check script for Security Modeling Platform

# Check backend health
echo "Checking backend health..."
backend_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/api/)
if [ $backend_status -eq 200 ]; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend is unhealthy (HTTP $backend_status)"
    exit 1
fi

# Check frontend health  
echo "Checking frontend health..."
frontend_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/)
if [ $frontend_status -eq 200 ]; then
    echo "✅ Frontend is healthy"
else
    echo "❌ Frontend is unhealthy (HTTP $frontend_status)"
    exit 1
fi

# Check MongoDB health
echo "Checking MongoDB health..."
mongo_status=$(mongosh --quiet --eval "db.adminCommand('ping').ok" 2>/dev/null)
if [ "$mongo_status" = "1" ]; then
    echo "✅ MongoDB is healthy"
else
    echo "❌ MongoDB is unhealthy"
    exit 1
fi

echo "✅ All services are healthy"
```

### 3. Systemd Service for Health Checks
Create `/etc/systemd/system/security-platform-healthcheck.service`:
```ini
[Unit]
Description=Security Platform Health Check
After=network.target

[Service]
Type=oneshot
ExecStart=/app/scripts/health-check.sh
User=www-data

[Install]
WantedBy=multi-user.target
```

Create timer `/etc/systemd/system/security-platform-healthcheck.timer`:
```ini
[Unit]
Description=Run Security Platform Health Check every 5 minutes
Requires=security-platform-healthcheck.service

[Timer]
OnCalendar=*:0/5
Persistent=true

[Install]
WantedBy=timers.target
```

Enable monitoring:
```bash
sudo systemctl enable security-platform-healthcheck.timer
sudo systemctl start security-platform-healthcheck.timer
```

## Troubleshooting

### Common Issues

#### 1. Backend Service Won't Start
```bash
# Check logs
sudo tail -f /var/log/supervisor/backend.err.log

# Common fixes:
# - Check Python dependencies: pip install -r requirements.txt
# - Verify MongoDB connection: check MONGO_URL in .env
# - Check port availability: netstat -tulpn | grep 8001
```

#### 2. Frontend Build Fails
```bash
# Check Node.js version
node --version  # Should be v18+

# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json yarn.lock
yarn install
yarn build
```

#### 3. Database Connection Issues
```bash
# Check MongoDB status
sudo systemctl status mongod

# Test connection
mongosh "mongodb://localhost:27017/security_modeling_platform"

# Check logs
sudo tail -f /var/log/mongodb/mongod.log
```

#### 4. CORS Issues
Update backend CORS settings in `server.py`:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Service Management Commands

```bash
# Supervisor commands
sudo supervisorctl status                    # Check status
sudo supervisorctl restart security-platform:*  # Restart all
sudo supervisorctl stop backend              # Stop backend
sudo supervisorctl start frontend           # Start frontend
sudo supervisorctl tail -f backend          # Follow logs

# Systemd commands (if using systemd)
sudo systemctl status security-platform
sudo systemctl restart security-platform
sudo journalctl -u security-platform -f    # Follow logs

# Docker commands
docker-compose logs -f backend              # Follow backend logs
docker-compose restart backend              # Restart backend
docker-compose ps                           # Check container status
```

## Maintenance

### 1. Backup Strategy
Create `/app/scripts/backup.sh`:
```bash
#!/bin/bash

BACKUP_DIR="/app/backup"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup MongoDB
echo "Backing up MongoDB..."
mongodump --out $BACKUP_DIR/mongodb_$DATE

# Backup application code
echo "Backing up application..."
tar -czf $BACKUP_DIR/app_$DATE.tar.gz /app --exclude=/app/backup --exclude=/app/logs --exclude=/app/node_modules

# Remove backups older than 7 days
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $DATE"
```

### 2. Log Rotation
Configure log rotation in `/etc/logrotate.d/security-platform`:
```
/var/log/supervisor/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        supervisorctl restart security-platform:*
    endscript
}
```

### 3. Updates and Patches
```bash
# Update system packages
sudo apt update && sudo apt upgrade

# Update Python dependencies
cd /app/backend
pip install -r requirements.txt --upgrade

# Update Node.js dependencies
cd /app/frontend
yarn upgrade

# Rebuild frontend
yarn build

# Restart services
sudo supervisorctl restart security-platform:*
```

### 4. Performance Monitoring
Install and configure monitoring tools:
```bash
# Install htop for system monitoring
sudo apt install htop

# Install MongoDB monitoring
sudo apt install mongodb-tools

# Monitor processes
htop
sudo supervisorctl status
docker stats  # If using Docker
```

## Security Considerations

1. **Environment Variables**: Never commit `.env` files to version control
2. **Database Security**: Use strong passwords and enable authentication
3. **SSL/TLS**: Always use HTTPS in production
4. **Firewall**: Configure appropriate firewall rules
5. **Updates**: Keep all dependencies and system packages updated
6. **Backup**: Implement regular backup strategy
7. **Monitoring**: Set up monitoring and alerting
8. **Access Control**: Implement proper user authentication and authorization

## Support

For issues and questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review service logs
3. Verify configuration files
4. Check system resources (CPU, RAM, Disk)
5. Ensure all dependencies are properly installed

---

**Last Updated**: December 2024
**Version**: 1.0
**Platform**: Security Modeling Platform