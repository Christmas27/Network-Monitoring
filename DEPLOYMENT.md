# 🚀 Cloud Deployment Guide

This guide covers multiple deployment options for your Network Monitoring Dashboard.

## 📋 Prerequisites

- Docker installed
- Git repository setup
- Cloud provider account (Heroku, AWS, Azure, or GCP)

## 🎯 Quick Deployment Options

### 1. 🔮 Heroku (Recommended for Portfolio)

**One-click deployment:**
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/Christmas27/Network-Monitoring)

**Manual deployment:**
```bash
# Install Heroku CLI
# Windows: https://devcenter.heroku.com/articles/heroku-cli
# Mac: brew install heroku/brew/heroku
# Linux: snap install --classic heroku

# Login and deploy
heroku login
chmod +x deploy/deploy-heroku.sh
./deploy/deploy-heroku.sh
```

**Environment Variables for Heroku:**
- `SECRET_KEY`: Auto-generated secure key
- `FLASK_ENV`: production
- `CATALYST_CENTER_HOST`: (optional) Your Catalyst Center IP
- `CATALYST_CENTER_USERNAME`: (optional) Your username
- `CATALYST_CENTER_PASSWORD`: (optional) Your password

### 2. 🐳 Docker Hub + Cloud Run

```bash
# Build and push to Docker Hub
docker build -f Dockerfile.production -t yourusername/network-dashboard:latest .
docker push yourusername/network-dashboard:latest

# Deploy to Google Cloud Run
gcloud run deploy network-dashboard \
  --image yourusername/network-dashboard:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 5000
```

### 3. ☁️ AWS ECS Fargate

```bash
# Prerequisites: AWS CLI configured
chmod +x deploy/deploy-aws.sh
./deploy/deploy-aws.sh
```

### 4. 🔵 Azure Container Instances

```bash
# Deploy using Azure CLI
az group create --name NetworkDashboard --location eastus
az deployment group create \
  --resource-group NetworkDashboard \
  --template-file deploy/azure-container-instance.json \
  --parameters secretKey="your-secret-key"
```

## 🔧 Configuration

### Environment Variables

Create `.env.production` with your values:

```env
# Required
SECRET_KEY=your-super-secret-production-key
FLASK_ENV=production
PORT=5000

# Optional - Cisco Integration
CATALYST_CENTER_HOST=your-catalyst-center-ip
CATALYST_CENTER_USERNAME=your-username
CATALYST_CENTER_PASSWORD=your-password

# Optional - External Database
DATABASE_URL=postgresql://user:pass@host:port/dbname
```

### Security Checklist

- ✅ Change default SECRET_KEY
- ✅ Use environment variables for credentials
- ✅ Enable HTTPS in production
- ✅ Configure firewall rules
- ✅ Regular security updates

## 📊 Monitoring & Maintenance

### Health Checks
- Health endpoint: `https://your-app.com/health`
- Status codes: 200 (healthy), 500 (unhealthy)

### Logs
```bash
# Heroku
heroku logs --tail --app your-app-name

# Docker
docker logs container-name

# AWS ECS
aws logs get-log-events --log-group-name /ecs/network-dashboard
```

### Scaling
```bash
# Heroku
heroku ps:scale web=2 --app your-app-name

# AWS ECS
aws ecs update-service --cluster cluster-name --service service-name --desired-count 2
```

## 🚨 Troubleshooting

### Common Issues

1. **Port binding issues**
   ```bash
   # Ensure PORT env var is set
   export PORT=5000
   ```

2. **Database connection**
   ```bash
   # Check database permissions
   # Verify DATABASE_URL format
   ```

3. **Memory issues**
   ```bash
   # Increase container memory limits
   # Optimize worker count
   ```

### Performance Optimization

- Use `gunicorn` with 2-4 workers
- Enable gzip compression
- Implement caching for device data
- Use CDN for static assets

## 🎓 For Your Portfolio

This deployment demonstrates:

### Technical Skills
- **DevOps**: Docker, CI/CD, Infrastructure as Code
- **Cloud Platforms**: Multi-cloud deployment strategies
- **Networking**: Cisco DevNet, SNMP, SSH automation
- **Security**: Secure credential management, HTTPS

### Best Practices
- **12-Factor App**: Environment-based configuration
- **Monitoring**: Health checks, logging, metrics
- **Scalability**: Horizontal scaling capabilities
- **Security**: Non-root containers, secret management

### Resume Highlights
- Built and deployed production-ready network monitoring application
- Implemented CI/CD pipelines with GitHub Actions
- Multi-cloud deployment experience (Heroku, AWS, Azure)
- Cisco networking automation with DevNet APIs
- Docker containerization and orchestration

#### 2. Application Setup
```bash
# Clone repository
git clone https://github.com/your-username/network-automation-dashboard.git
cd network-automation-dashboard

# Setup virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

#### 3. Database Setup
```bash
# PostgreSQL setup
sudo -u postgres createuser netdashboard
sudo -u postgres createdb netdashboard_db
sudo -u postgres psql -c "ALTER USER netdashboard PASSWORD 'secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE netdashboard_db TO netdashboard;"
```

#### 4. Systemd Service
```bash
# Create service file
sudo nano /etc/systemd/system/network-dashboard.service
```

```ini
[Unit]
Description=Network Automation Dashboard
After=network.target

[Service]
User=netdashboard
Group=netdashboard
WorkingDirectory=/home/netdashboard/network-automation-dashboard
Environment=PATH=/home/netdashboard/network-automation-dashboard/.venv/bin
ExecStart=/home/netdashboard/network-automation-dashboard/.venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable network-dashboard
sudo systemctl start network-dashboard
```

#### 5. Nginx Configuration
```bash
# Create Nginx site
sudo nano /etc/nginx/sites-available/network-dashboard
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /home/netdashboard/network-automation-dashboard/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/network-dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 6. SSL Certificate (Let's Encrypt)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Docker Production Deployment

### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:5000", "main:app"]
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/netdashboard
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - ./data:/app/data

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: netdashboard
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6-alpine

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web

volumes:
  postgres_data:
```

## Environment Configuration

### Production Environment Variables
```bash
# Create .env file
cat > .env << EOF
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@localhost/netdashboard_db
REDIS_URL=redis://localhost:6379
DEVNET_USERNAME=your-devnet-username
DEVNET_PASSWORD=your-devnet-password
DEVNET_SANDBOX_URL=https://your-sandbox.devnetcloud.com
EOF
```

### Configuration File
```python
# config/production.py
import os
from datetime import timedelta

class ProductionConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DATABASE_URL = os.environ.get('DATABASE_URL')
    REDIS_URL = os.environ.get('REDIS_URL')
    
    # Security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    
    # Performance settings
    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_POOL_TIMEOUT = 20
    SQLALCHEMY_POOL_RECYCLE = 3600
    
    # DevNet settings
    DEVNET_USERNAME = os.environ.get('DEVNET_USERNAME')
    DEVNET_PASSWORD = os.environ.get('DEVNET_PASSWORD')
    DEVNET_SANDBOX_URL = os.environ.get('DEVNET_SANDBOX_URL')
```

## Monitoring & Maintenance

### Health Checks
```bash
# Application health check
curl -f http://localhost:5000/health

# Database connection check
curl -f http://localhost:5000/api/health/database

# DevNet connectivity check
curl -f http://localhost:5000/api/health/devnet
```

### Log Monitoring
```bash
# Application logs
sudo journalctl -u network-dashboard -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Database logs
sudo tail -f /var/log/postgresql/postgresql-13-main.log
```

### Backup Strategy
```bash
# Database backup
pg_dump netdashboard_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Application backup
tar -czf app_backup_$(date +%Y%m%d_%H%M%S).tar.gz /home/netdashboard/network-automation-dashboard

# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump netdashboard_db > /backups/db_$DATE.sql
tar -czf /backups/app_$DATE.tar.gz /home/netdashboard/network-automation-dashboard
find /backups -name "*.sql" -mtime +7 -delete
find /backups -name "*.tar.gz" -mtime +7 -delete
```

## Performance Optimization

### Application Performance
```python
# Enable caching
from flask_caching import Cache
cache = Cache(app)

# Database connection pooling
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'pool_recycle': 120,
    'pool_pre_ping': True
}

# Redis caching
CACHE_TYPE = 'redis'
CACHE_REDIS_URL = 'redis://localhost:6379'
```

### Nginx Optimization
```nginx
# Gzip compression
gzip on;
gzip_types text/css application/javascript application/json;

# Static file caching
location /static {
    expires 1y;
    add_header Cache-Control "public, immutable";
}

# Rate limiting
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
location /api {
    limit_req zone=api burst=20;
}
```

## Security Hardening

### Firewall Configuration
```bash
# UFW setup
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw deny 5000  # Don't expose Flask directly
```

### SSL/TLS Configuration
```nginx
# Strong SSL configuration
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
ssl_prefer_server_ciphers off;
add_header Strict-Transport-Security "max-age=63072000" always;
```

### Application Security
```python
# Security headers
from flask_talisman import Talisman
Talisman(app, force_https=True)

# Rate limiting
from flask_limiter import Limiter
limiter = Limiter(app, key_func=get_remote_address)
```

## Troubleshooting

### Common Issues
1. **Database connection errors**: Check PostgreSQL service and credentials
2. **DevNet connectivity**: Verify sandbox status and credentials
3. **Permission errors**: Check file permissions and user ownership
4. **Memory issues**: Monitor application memory usage and adjust workers

### Debug Mode
```bash
# Enable debug logging
export FLASK_ENV=development
export FLASK_DEBUG=1

# Check application logs
sudo journalctl -u network-dashboard --since "1 hour ago"
```