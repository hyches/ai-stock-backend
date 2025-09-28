# TestSprite Integration Guide for AI Stock Backend

## 🎯 Overview
This guide shows you how to use TestSprite to comprehensively test your AI Stock Backend FastAPI application.

## 🚀 Quick Start with TestSprite

### Method 1: Using TestSprite MCP in Cursor (Recommended)

Since you have TestSprite configured in your MCP setup, you can use it directly:

1. **Open Cursor Chat** and type:
   ```
   Can you test this project with TestSprite?
   ```

2. **TestSprite will automatically:**
   - Analyze your FastAPI application
   - Generate comprehensive test scenarios
   - Test all API endpoints
   - Validate ML services
   - Check trading operations
   - Test portfolio management
   - Verify authentication and security

### Method 2: Using the TestSprite Runner Script

1. **Start your FastAPI server:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Run TestSprite tests:**
   ```bash
   python run_testsprite_tests.py
   ```

3. **Check server status:**
   ```bash
   python run_testsprite_tests.py check
   ```

## 📋 TestSprite Test Scenarios

### 1. Authentication Flow
- User registration
- User login
- Token validation
- Password reset
- User logout
- Role-based access control

### 2. Trading Operations
- Create/update/delete trading strategies
- Execute trades (buy/sell)
- Manage positions
- Portfolio creation and management
- Backtesting functionality
- Risk management

### 3. ML Services
- Single predictions
- Batch predictions
- Model performance metrics
- Feature importance analysis
- Model retraining
- Data preprocessing

### 4. Market Data
- Real-time data fetching
- Historical data retrieval
- Technical indicators calculation
- Market screening
- Data validation and caching

### 5. Portfolio Management
- Portfolio creation and updates
- Position tracking
- Performance analysis
- Risk assessment
- Rebalancing operations

### 6. Alerts and Notifications
- Alert creation and management
- Notification delivery
- Alert history tracking
- Custom alert conditions

### 7. Settings and Configuration
- User preferences
- System configuration
- Backup and restore
- Data export/import

## 🔧 TestSprite Configuration

The `testsprite_config.json` file contains:
- **Project metadata** (name, type, base URL)
- **Test scenarios** with specific endpoints
- **Test data** for realistic testing
- **Authentication** configuration
- **Performance requirements**

## 🎯 What TestSprite Tests

### API Endpoints
- All REST endpoints in your FastAPI application
- Request/response validation
- Error handling
- Status code verification
- Data format validation

### Security
- Authentication bypass attempts
- SQL injection prevention
- XSS prevention
- CSRF protection
- Input validation
- Authorization controls

### Performance
- Response time analysis
- Concurrent user testing
- Load testing
- Memory usage monitoring
- Database query optimization

### Integration
- End-to-end workflows
- Service interactions
- External API mocking
- Data flow validation

## 📊 TestSprite Reports

TestSprite generates comprehensive reports including:
- **Test execution summary** with pass/fail counts
- **Performance metrics** with response times
- **Security findings** with vulnerability details
- **Code coverage analysis** showing tested areas
- **Recommendations** for improvements
- **Automated fix suggestions** for issues found

## 🚀 Running Tests

### Start Your Application
```bash
# Start the FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# In another terminal, run TestSprite
python run_testsprite_tests.py
```

### Test Specific Components
```bash
# Test only authentication
python run_testsprite_tests.py --auth

# Test only trading operations
python run_testsprite_tests.py --trading

# Test only ML services
python run_testsprite_tests.py --ml

# Test only performance
python run_testsprite_tests.py --performance
```

## 🔍 TestSprite Features

### AI-Powered Test Generation
- Automatically generates test cases
- Learns from your API structure
- Creates realistic test data
- Identifies edge cases

### Comprehensive Coverage
- Tests all API endpoints
- Validates data models
- Checks business logic
- Verifies security measures

### Performance Analysis
- Measures response times
- Tests under load
- Identifies bottlenecks
- Suggests optimizations

### Security Testing
- Vulnerability scanning
- Penetration testing
- Input validation testing
- Authentication testing

## 📈 Benefits of Using TestSprite

1. **Automated Testing** - No manual test writing required
2. **Comprehensive Coverage** - Tests all aspects of your application
3. **AI-Powered** - Learns and adapts to your codebase
4. **Real-time Feedback** - Immediate results and suggestions
5. **Continuous Testing** - Integrates with your development workflow
6. **Detailed Reports** - Clear insights into your application's health

## 🛠️ Troubleshooting

### Common Issues

1. **Server Not Running**
   ```bash
   # Check if server is running
   python run_testsprite_tests.py check
   
   # Start server if needed
   python run_testsprite_tests.py server
   ```

2. **Authentication Issues**
   - Ensure your authentication endpoints are working
   - Check token generation and validation
   - Verify user permissions

3. **Database Connection**
   - Ensure database is running
   - Check connection settings
   - Verify migrations are applied

4. **External Dependencies**
   - Check Redis connection
   - Verify external API access
   - Ensure all services are running

### Getting Help

1. **Check TestSprite logs** for detailed error messages
2. **Review test reports** for specific failure details
3. **Verify configuration** in `testsprite_config.json`
4. **Test individual endpoints** manually first

## 🎉 Next Steps

1. **Run TestSprite** on your project
2. **Review the test report** for insights
3. **Fix any issues** identified by TestSprite
4. **Integrate TestSprite** into your CI/CD pipeline
5. **Set up continuous testing** for ongoing quality assurance

## 📚 Additional Resources

- [TestSprite Documentation](https://docs.testsprite.com/)
- [FastAPI Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [API Testing Best Practices](https://docs.testsprite.com/best-practices)

---

**Ready to test your AI Stock Backend with TestSprite?** 

Simply run: `python run_testsprite_tests.py` and let TestSprite do the rest! 🚀
