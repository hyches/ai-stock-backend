# Deployment Guide

This guide provides detailed instructions for deploying the AI Stock Analysis Platform in various environments.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Docker Deployment](#docker-deployment)
4. [Production Deployment](#production-deployment)
5. [Monitoring Setup](#monitoring-setup)
6. [Backup Configuration](#backup-configuration)

## Prerequisites

### System Requirements
- Python 3.13 or higher
- Docker and Docker Compose
- Git
- 2GB RAM minimum (4GB recommended)
- 10GB free disk space

### Required Accounts
- Docker Hub account
- Alpha Vantage API key
- Finnhub API key

## Local Development

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/stock-portfolio.git
cd stock-portfolio
```

### 2. Set Up Python Environment
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env with your configuration
```

### 5. Run Development Server
```bash
uvicorn app.main:app --reload
```

## Docker Deployment

### 1. Build the Image
```bash
docker build -t stock-portfolio .
```

### 2. Run the Container
```bash
docker-compose up -d
```

## Production Deployment

### 1. Server Setup
1. Launch a new server (e.g., AWS EC2 t3.medium)
2. Install Docker and Docker Compose
3. Configure security groups/firewall
4. Set up SSL certificates

### 2. Application Deployment
1. Clone the repository
2. Configure environment variables
3. Build and run the Docker container
4. Set up Nginx reverse proxy

### 3. Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 4. SSL Configuration
```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com
```

## Monitoring Setup

### 1. Prometheus Configuration
1. Install Prometheus
2. Configure scrape targets
3. Set up alerting rules

### 2. Logging Configuration
1. Create logs directory
2. Configure log rotation
3. Set up log aggregation

## Backup Configuration

### 1. Automated Backups
1. Start the backup scheduler:
```bash
python scripts/schedule_backups.py
```

### 2. Manual Backup
1. Use the API endpoint:
```bash
curl -X POST http://localhost:8000/api/v1/backup
```

### 3. Backup Verification
1. List available backups:
```bash
curl http://localhost:8000/api/v1/backup/list
```

## Troubleshooting

### Common Issues
1. **Port Conflicts**
   - Check if port 8000 is in use
   - Change port in Docker run command

2. **Database Issues**
   - Verify database connection string
   - Check database permissions

3. **API Key Problems**
   - Verify API keys in .env file
   - Check API key quotas

### Logs
- Application logs: `logs/app.log`
- Docker logs: `docker logs stock-portfolio`
- Nginx logs: `/var/log/nginx/`

## Security Considerations

1. **Environment Variables**
   - Never commit .env files
   - Use secure secret management

2. **API Security**
   - Enable rate limiting
   - Use HTTPS
   - Implement authentication

3. **Backup Security**
   - Encrypt sensitive data
   - Secure backup storage
   - Regular backup testing

## AWS Deployment

### EC2 Setup

1. Launch EC2 instance:
```bash
aws ec2 run-instances \
    --image-id ami-0c55b159cbfafe1f0 \
    --instance-type t2.micro \
    --key-name your-key-pair \
    --security-group-ids sg-xxxxxxxx
```

2. Configure security groups:
- Allow inbound traffic on port 8000
- Allow inbound traffic on port 22 (SSH)

3. Install Docker:
```bash
sudo yum update -y
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker ec2-user
```

4. Deploy application:
```bash
docker run -d \
    -p 8000:8000 \
    -e DATABASE_URL=postgresql://user:pass@host:5432/db \
    -e REDIS_URL=redis://host:6379 \
    stock-portfolio
```

### RDS Setup

1. Create RDS instance:
```bash
aws rds create-db-instance \
    --db-instance-identifier stock-portfolio-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --master-username admin \
    --master-user-password password \
    --allocated-storage 20
```

2. Configure security group:
- Allow inbound traffic on port 5432 from EC2 security group

### ElastiCache Setup

1. Create Redis cluster:
```bash
aws elasticache create-cache-cluster \
    --cache-cluster-id stock-portfolio-cache \
    --cache-node-type cache.t3.micro \
    --engine redis \
    --num-cache-nodes 1
```

## Monitoring Setup

### 1. Prometheus Configuration
1. Install Prometheus
2. Configure scrape targets
3. Set up alerting rules

### 2. Logging Configuration
1. Create logs directory
2. Configure log rotation
3. Set up log aggregation

## Backup Strategy

1. Database backups:
```bash
# Daily backup
pg_dump -h host -U user -d dbname > backup.sql

# Upload to S3
aws s3 cp backup.sql s3://your-bucket/backups/
```

2. Application logs:
```bash
# Configure log rotation
/var/log/stock-portfolio/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
}
```

## Troubleshooting

### Common Issues

1. Database Connection Issues:
```bash
# Check database connection
psql -h host -U user -d dbname

# Check logs
docker logs stock-portfolio
```

2. Memory Issues:
```bash
# Check memory usage
free -m

# Check container stats
docker stats
```

3. Network Issues:
```bash
# Check network connectivity
netstat -tulpn | grep 8000

# Check firewall rules
sudo iptables -L
```

### Health Checks

1. API Health:
```bash
curl http://localhost:8000/health
```

2. Database Health:
```bash
curl http://localhost:8000/health/db
```

3. Cache Health:
```bash
curl http://localhost:8000/health/cache
```

## Security Checklist

- [ ] Enable HTTPS
- [ ] Configure WAF
- [ ] Set up VPC
- [ ] Enable encryption at rest
- [ ] Enable encryption in transit
- [ ] Configure IAM roles
- [ ] Set up CloudWatch alarms
- [ ] Enable AWS Shield
- [ ] Configure security groups
- [ ] Enable AWS Config 