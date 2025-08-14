# 🚀 Deployment Guide

## Quick Deployment Options

### 1. Local Development
```bash
# Clone and setup
git clone https://github.com/your-username/network-automation-dashboard.git
cd network-automation-dashboard
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### 2. Docker Deployment
```bash
# Build and run
docker build -t network-dashboard .
docker run -p 5000:5000 network-dashboard

# Or use docker-compose
docker-compose up -d
```

### 3. Cloud Deployment (Heroku)
```bash
# Deploy to Heroku
heroku create your-dashboard-name
git push heroku main
heroku open
```

## Production Deployment

### Ubuntu/CentOS Server Setup

#### 1. System Prerequisites
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3 python3-pip python3-venv nginx postgresql redis-server -y

# Create application user
sudo useradd -m -s /bin/bash netdashboard
sudo su - netdashboard
```

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