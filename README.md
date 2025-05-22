# AI Stock Analysis Platform

A comprehensive stock analysis platform that provides AI-powered insights, automated research, and detailed reports.

## Features

- Real-time stock screening and analysis
- AI-powered stock recommendations
- Automated research report generation
- PDF report generation
- Backup and recovery system
- Monitoring and logging
- RESTful API

## API Documentation

The API documentation is available at `/docs` when running the server. Here are the main endpoints:

### Stock Analysis
- `GET /api/v1/stocks/screen` - Screen stocks based on criteria
- `GET /api/v1/stocks/{symbol}/analyze` - Analyze a specific stock
- `GET /api/v1/stocks/{symbol}/research` - Generate research report

### Reports
- `GET /api/v1/reports/{report_id}` - Get a specific report
- `POST /api/v1/reports/generate` - Generate a new report

### Backup Management
- `POST /api/v1/backup` - Create a new backup
- `POST /api/v1/backup/restore/{backup_path}` - Restore from backup
- `GET /api/v1/backup/list` - List available backups
- `DELETE /api/v1/backup/cleanup` - Clean up old backups

## Deployment Guide

### Prerequisites
- Python 3.13+
- Docker (for containerized deployment)
- Git

### Local Development Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-stock-analysis
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp app/.env.template app/.env
# Edit app/.env with your configuration
```

5. Run the development server:
```bash
uvicorn app.main:app --reload
```

### Docker Deployment

1. Build the Docker image:
```bash
docker build -t ai-stock-backend .
```

2. Run the container:
```bash
docker run -d -p 8000:8000 --name ai-stock-backend ai-stock-backend
```

### Production Deployment

1. Set up a production server (e.g., AWS EC2, DigitalOcean)
2. Install Docker and Docker Compose
3. Clone the repository
4. Configure environment variables
5. Build and run the Docker container
6. Set up a reverse proxy (e.g., Nginx)
7. Configure SSL certificates

## Backup and Recovery

### Automated Backups
- Daily backups are scheduled at 2 AM
- Last 5 backups are retained
- Backups include database and reports

### Manual Backup
```python
from app.core.backup import BackupManager
backup_manager = BackupManager()
backup_path = backup_manager.create_backup()
```

### Restore from Backup
```python
backup_manager.restore_backup("backups/backup_20240315_020000")
```

### Backup Management
- Use the API endpoints for backup management
- Monitor backup status in logs
- Verify backup integrity regularly

## Monitoring

- Prometheus metrics available at `/metrics`
- Log files in `logs/app.log`
- Rotating log files (10MB max, 5 backups)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Testing

The project includes a comprehensive test suite covering unit tests, integration tests, load tests, and security tests. To run the tests:

1. Install test dependencies:
```bash
pip install -r requirements-test.txt
```

2. Create a `.env.test` file in the project root with the following settings (values can be customized):
```bash
# Database
DATABASE_URL=sqlite:///./test.db

# Security
SECRET_KEY=test_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15

# API Keys
NEWS_API_KEY=test_news_api_key
ALPHA_VANTAGE_API_KEY=test_alpha_vantage_api_key

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60

# File Upload
MAX_UPLOAD_SIZE=5242880
ALLOWED_EXTENSIONS=pdf,doc,docx

# Cache
REDIS_URL=redis://localhost:6379/1
CACHE_TTL=300

# Logging
LOG_LEVEL=DEBUG
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# Testing
TEST_USER_EMAIL=test@example.com
TEST_USER_PASSWORD=password123
TEST_USER_FULL_NAME=Test User
```

3. Run the test suite:
```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit
pytest tests/integration
pytest tests/load
pytest tests/security

# Run with coverage report
pytest --cov=app tests/
```

4. View test coverage report:
```bash
coverage report
coverage html  # Generates HTML report in htmlcov/
```

### Test Categories

- **Unit Tests**: Test individual components in isolation
  - API endpoints
  - Database models
  - Service functions
  - Utility functions

- **Integration Tests**: Test component interactions
  - User workflows
  - Portfolio management
  - Stock analysis
  - Report generation

- **Load Tests**: Test system performance
  - Concurrent user sessions
  - Sustained load
  - Error handling under load

- **Security Tests**: Test security measures
  - Authentication
  - Authorization
  - Input validation
  - Rate limiting
  - File upload security

### Test Configuration

The test configuration is managed through:
- `app/config/test.py`: Test settings
- `tests/conftest.py`: Test fixtures and configuration
- `.env.test`: Test environment variables (create from template)

### Best Practices

1. Write tests before implementing features (TDD)
2. Keep tests focused and atomic
3. Use meaningful test names
4. Clean up test data after each test
5. Mock external dependencies
6. Test both success and failure cases
7. Maintain test coverage above 80% 