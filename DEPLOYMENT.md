# DevEx Ambient Agent - Production Deployment Guide

## 🚀 Overview

This guide covers deploying the DevEx Ambient Agent in production using Docker containers with comprehensive monitoring, logging, and security features.

## 📋 Prerequisites

### System Requirements
- **CPU**: 4+ cores (8+ recommended)
- **RAM**: 8GB minimum (16GB+ recommended)
- **Storage**: 50GB+ SSD storage
- **OS**: Linux (Ubuntu 20.04+, CentOS 8+, or similar)

### Software Requirements
- Docker 24.0+
- Docker Compose 2.0+
- Git 2.30+
- `uv` package manager (for local development)

### Network Requirements
- Ports 80, 443 (HTTP/HTTPS)
- Port 8000 (DevEx Agent API)
- Ports 3000, 5601, 9090 (Monitoring dashboards)
- Ports 7474, 7687 (Neo4j)

## 🔧 Quick Deployment

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/your-org/devex-agent.git
cd devex-agent

# Create environment file
cp env.production.example .env

# Edit environment variables
nano .env
```

### 2. Configure Environment Variables

Edit `.env` with your production settings:

```bash
# Required API Keys
OPENAI_API_KEY=your_openai_api_key_here
CONFLUENCE_API_TOKEN=your_confluence_token_here
GITHUB_ACCESS_TOKEN=your_github_token_here

# Security (generate strong passwords)
NEO4J_PASSWORD=your_secure_neo4j_password
REDIS_PASSWORD=your_secure_redis_password
GRAFANA_PASSWORD=your_secure_grafana_password

# Domain configuration
CONFLUENCE_BASE_URL=https://yourcompany.atlassian.net
CONFLUENCE_USERNAME=your-email@company.com
```

### 3. Deploy with Docker Compose

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f devex-agent
```

### 4. Verify Deployment

```bash
# Check DevEx Agent health
curl http://localhost:8000/

# Access monitoring dashboards
# Grafana: http://localhost:3000 (admin/your_grafana_password)
# Prometheus: http://localhost:9090
# Kibana: http://localhost:5601
```

## 🏗 Architecture Overview

### Services Deployed

| Service | Purpose | Port | Health Check |
|---------|---------|------|--------------|
| **devex-agent** | Main application | 8000 | `/` |
| **neo4j** | Graph database | 7474, 7687 | Cypher query |
| **chroma** | Vector database | 8001 | `/api/v1/heartbeat` |
| **redis** | Cache layer | 6379 | Redis ping |
| **prometheus** | Metrics collection | 9090 | Web UI |
| **grafana** | Dashboards | 3000 | Web UI |
| **elasticsearch** | Log aggregation | 9200 | `/_cluster/health` |
| **kibana** | Log visualization | 5601 | Web UI |
| **nginx** | Reverse proxy | 80, 443 | `/nginx_status` |

### Data Persistence

All data is persisted using Docker volumes:

```yaml
volumes:
  neo4j_data:          # Graph database
  chroma_data:         # Vector embeddings
  redis_data:          # Cache data
  prometheus_data:     # Metrics
  grafana_data:        # Dashboards
  elasticsearch_data:  # Logs
```

## 📊 Monitoring Setup

### Grafana Dashboards

1. **Access Grafana**: http://localhost:3000
2. **Login**: admin / your_grafana_password
3. **Import Dashboard**: Use the pre-configured DevEx Agent dashboard

Key metrics monitored:
- API request rate and response times
- Knowledge Graph operations
- Memory and CPU usage
- Cache performance
- Error rates
- Active connections

### Prometheus Metrics

Custom metrics exposed by DevEx Agent:
- `knowledge_graph_operations_total`
- `relationship_discovery_operations_total`
- `cache_hits_total` / `cache_misses_total`
- `knowledge_graph_entities_total`
- `ingestion_jobs_active`

### Log Aggregation

Logs are collected from:
- DevEx Agent application logs
- All Docker container logs
- Nginx access and error logs
- System metrics via Filebeat

Access logs in Kibana: http://localhost:5601

## 🔒 Security Configuration

### SSL/TLS Setup

1. **Generate certificates**:
```bash
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem
```

2. **Update nginx configuration**:
```bash
# Uncomment SSL section in nginx/nginx.conf
# Update server_name to your domain
```

3. **Enable HTTPS in docker-compose.yml**:
```yaml
nginx:
  ports:
    - "443:443"
```

### Authentication

#### Basic Authentication (Nginx)
```bash
# Create password file
htpasswd -c nginx/.htpasswd admin

# Update nginx.conf to enable auth_basic
```

#### OAuth Integration (Optional)
Configure OAuth providers in Grafana for enterprise authentication.

### Firewall Configuration

```bash
# Allow only necessary ports
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 22/tcp  # SSH only from specific IPs
ufw enable

# Block direct access to service ports
ufw deny 3000  # Grafana (access via nginx)
ufw deny 9090  # Prometheus (access via nginx)
```

## 📈 Scaling Configuration

### Horizontal Scaling

1. **Multiple Agent Instances**:
```yaml
devex-agent:
  deploy:
    replicas: 3
  # Add load balancer configuration
```

2. **Database Clustering**:
- Neo4j Cluster (Enterprise)
- Chroma distributed setup
- Redis Cluster

### Resource Limits

```yaml
devex-agent:
  deploy:
    resources:
      limits:
        cpus: '2.0'
        memory: 4G
      reservations:
        cpus: '1.0'
        memory: 2G
```

## 🔄 Backup and Recovery

### Automated Backups

1. **Database Backups**:
```bash
# Neo4j backup script
#!/bin/bash
docker exec devex-neo4j neo4j-admin dump \
  --database=neo4j \
  --to=/backups/neo4j-$(date +%Y%m%d).dump

# Chroma backup
docker exec devex-chroma tar -czf \
  /backups/chroma-$(date +%Y%m%d).tar.gz /chroma/chroma
```

2. **Application Data**:
```bash
# Backup volumes
docker run --rm -v devex-agent_neo4j_data:/data \
  -v $(pwd)/backups:/backup alpine \
  tar -czf /backup/neo4j-data-$(date +%Y%m%d).tar.gz /data
```

3. **Automated Schedule**:
```bash
# Add to crontab
0 2 * * * /path/to/backup-script.sh
```

### Recovery Process

1. **Stop services**:
```bash
docker-compose down
```

2. **Restore data**:
```bash
# Restore from backup
docker run --rm -v devex-agent_neo4j_data:/data \
  -v $(pwd)/backups:/backup alpine \
  tar -xzf /backup/neo4j-data-20240101.tar.gz -C /
```

3. **Restart services**:
```bash
docker-compose up -d
```

## 🚨 Alerting Setup

### Prometheus Alerts

Create `monitoring/alerts.yml`:
```yaml
groups:
  - name: devex-agent
    rules:
      - alert: AgentDown
        expr: up{job="devex-agent"} == 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "DevEx Agent is down"

      - alert: HighErrorRate
        expr: rate(http_requests_total{code=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
```

### Notification Channels

1. **Slack Integration**:
```bash
# Add to .env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
```

2. **Email Alerts**:
```bash
# SMTP configuration
SMTP_HOST=smtp.yourcompany.com
SMTP_USER=alerts@yourcompany.com
SMTP_PASSWORD=your_smtp_password
```

## 🔧 Maintenance

### Updates and Upgrades

1. **Application Updates**:
```bash
# Pull latest code
git pull origin main

# Rebuild and deploy
docker-compose build devex-agent
docker-compose up -d devex-agent
```

2. **Database Migrations**:
```bash
# Run migration scripts
docker exec devex-agent python -m devex_agent.migrations.run
```

3. **Health Checks**:
```bash
# Check all services
docker-compose ps
docker-compose logs --tail=50
```

### Performance Tuning

1. **Memory optimization**:
```yaml
# Adjust in docker-compose.yml
NEO4J_dbms_memory_heap_max__size=4g
NEO4J_dbms_memory_pagecache_size=2g
```

2. **Connection pooling**:
```bash
# In .env
MAX_WORKERS=8
REDIS_MAX_CONNECTIONS=100
```

## 🐛 Troubleshooting

### Common Issues

1. **Service won't start**:
```bash
# Check logs
docker-compose logs service-name

# Check resource usage
docker stats

# Verify environment variables
docker-compose config
```

2. **Database connection issues**:
```bash
# Test Neo4j connection
docker exec devex-neo4j cypher-shell -u neo4j -p your_password "RETURN 1"

# Test Chroma
curl http://localhost:8001/api/v1/heartbeat
```

3. **Performance issues**:
```bash
# Monitor resource usage
docker stats

# Check cache hit rates
curl http://localhost:8000/api/v1/performance/cache

# Review slow queries in logs
docker-compose logs devex-agent | grep "slow"
```

### Log Analysis

```bash
# Application errors
docker-compose logs devex-agent | grep ERROR

# Database slow queries
docker-compose logs neo4j | grep "slow"

# Nginx access patterns
docker-compose logs nginx | tail -100
```

## 📞 Support

### Health Endpoints

- **Agent Health**: `GET /` - Basic health check
- **Detailed Status**: `GET /status/{developer_id}` - Detailed status
- **Performance Stats**: `GET /api/v1/performance/stats` - Performance metrics
- **Cache Stats**: `GET /api/v1/performance/cache` - Cache statistics

### Monitoring URLs

- **Application**: http://localhost:8000
- **Grafana**: http://localhost:3000
- **Prometheus**: http://localhost:9090
- **Kibana**: http://localhost:5601
- **Neo4j Browser**: http://localhost:7474

### Support Contacts

- **Technical Issues**: tech-support@yourcompany.com
- **Emergency**: +1-XXX-XXX-XXXX
- **Documentation**: https://docs.devex-agent.com

---

## 🎯 Next Steps

After successful deployment:

1. **Configure Knowledge Sources**: Add GitHub repos and Confluence spaces
2. **Set up Integrations**: Connect with your IDE and development tools
3. **Train the Model**: Let the agent learn from your codebase
4. **Monitor Performance**: Use dashboards to optimize performance
5. **Scale as Needed**: Add more resources based on usage patterns

For additional configuration options and advanced features, see the main [README.md](README.md). 