# 🐳 Docker Deployment Guide - Security Modeling Platform

This guide provides instructions for running the Security Modeling Platform using Docker containers.

## 📋 Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB+ available RAM
- 10GB+ available disk space

## 🚀 Quick Start

### Production Deployment

```bash
# Make scripts executable
chmod +x *.sh

# Build and run in production mode
./run-production.sh
```

### Development Deployment

```bash
# Run in development mode (with hot reload)
./run-development.sh
```

## 📁 Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │    MongoDB      │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (Database)    │
│   Port: 3000    │    │   Port: 8001    │    │   Port: 27017   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Manual Commands

### Build Images

```bash
# Build all images
docker-compose build

# Build specific service
docker-compose build backend
docker-compose build frontend
```

### Run Services

```bash
# Start all services (production)
docker-compose up -d

# Start all services (development with logs)
docker-compose -f docker-compose.dev.yml up

# Start specific service
docker-compose up -d mongodb backend
```

### Manage Services

```bash
# View running containers
docker-compose ps

# View logs
docker-compose logs -f
docker-compose logs -f backend  # specific service

# Stop services
docker-compose down

# Restart services
docker-compose restart

# Remove everything including volumes
docker-compose down -v
```

## 🔧 Configuration

### Environment Variables

**Backend (.env):**
```env
MONGO_URL=mongodb://admin:securepassword123@mongodb:27017/security_modeling_platform?authSource=admin
DB_NAME=security_modeling_platform
CORS_ORIGINS=http://localhost:3000
```

**Frontend (.env):**
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

### MongoDB Configuration

- **Production**: Uses authentication with admin user
- **Development**: No authentication required
- **Data Persistence**: MongoDB data is stored in Docker volumes

## 📊 Service Health Checks

All services include health checks:

```bash
# Check service health
docker-compose ps

# View health check logs
docker inspect security-platform-backend --format='{{.State.Health.Status}}'
```

## 🐛 Troubleshooting

### Common Issues

**1. Port Already in Use**
```bash
# Check what's using the port
sudo lsof -i :3000
sudo lsof -i :8001
sudo lsof -i :27017

# Kill processes if needed
sudo kill -9 <PID>
```

**2. MongoDB Connection Issues**
```bash
# Check MongoDB logs
docker-compose logs mongodb

# Connect to MongoDB shell
docker exec -it security-platform-mongodb mongosh
```

**3. Backend API Issues**
```bash
# Check backend logs
docker-compose logs backend

# Test API endpoint
curl http://localhost:8001/api/

# Enter backend container
docker exec -it security-platform-backend bash
```

**4. Frontend Build Issues**
```bash
# Check frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose build --no-cache frontend

# Check nginx config
docker exec -it security-platform-frontend cat /etc/nginx/conf.d/default.conf
```

### Performance Optimization

**Resource Limits:**
```yaml
# Add to docker-compose.yml under each service
deploy:
  resources:
    limits:
      cpus: '0.5'
      memory: 512M
    reservations:
      cpus: '0.25'
      memory: 256M
```

**Volume Optimization:**
```bash
# Clean up unused volumes
docker volume prune

# View volume usage
docker system df
```

## 🔒 Security Considerations

### Production Security

1. **Change Default Passwords**
   - Update MongoDB admin password in docker-compose.yml
   - Use environment variables for sensitive data

2. **Network Security**
   - Use custom networks (already configured)
   - Expose only necessary ports

3. **User Security**
   - Services run as non-root users
   - Minimal base images used

4. **Data Security**
   - MongoDB data encrypted at rest (configure if needed)
   - Use secrets management in production

### Secure Deployment Example

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  mongodb:
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${MONGO_USER}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_PASSWORD}
    ports:
      - "127.0.0.1:27017:27017"  # Bind to localhost only
```

## 📈 Monitoring

### Container Monitoring

```bash
# Resource usage
docker stats

# System usage
docker system df

# Container processes
docker-compose top
```

### Application Monitoring

```bash
# API health check
curl http://localhost:8001/api/

# Frontend health check
curl http://localhost:3000

# MongoDB status
docker exec security-platform-mongodb mongosh --eval "db.adminCommand('ping')"
```

## 🔄 Updates and Maintenance

### Updating the Application

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Database Backup

```bash
# Create backup
docker exec security-platform-mongodb mongodump --db security_modeling_platform --out /backup

# Copy backup from container
docker cp security-platform-mongodb:/backup ./mongodb-backup
```

### Database Restore

```bash
# Copy backup to container
docker cp ./mongodb-backup security-platform-mongodb:/backup

# Restore database
docker exec security-platform-mongodb mongorestore --db security_modeling_platform /backup/security_modeling_platform
```

## 🎯 URLs and Access

- **Frontend Application**: http://localhost:3000
- **Backend API**: http://localhost:8001/api/
- **API Documentation**: http://localhost:8001/docs
- **MongoDB**: mongodb://localhost:27017

## 📞 Support

For issues with Docker deployment:

1. Check the logs: `docker-compose logs -f`
2. Verify service health: `docker-compose ps`
3. Test individual services
4. Check resource usage: `docker stats`

## 🏷️ Version Information

- **Docker Images**: Based on official images
- **MongoDB**: 7.0 (latest stable)
- **Node.js**: 18 (Alpine Linux)
- **Python**: 3.11 (Slim Debian)
- **Nginx**: Latest Alpine