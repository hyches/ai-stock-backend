# API Documentation

## Authentication

### Login
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "user@example.com", "password": "password123"}'
```

### Register
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
           "email": "user@example.com",
           "password": "password123",
           "full_name": "John Doe"
         }'
```

## Stock Analysis

### Get Stock Sentiment
```bash
curl -X GET "http://localhost:8000/api/stocks/AAPL/sentiment" \
     -H "Authorization: Bearer {your_token}"
```

### Get Competitor Analysis
```bash
curl -X GET "http://localhost:8000/api/stocks/AAPL/competitors" \
     -H "Authorization: Bearer {your_token}"
```

## Portfolio Management

### Create Portfolio
```bash
curl -X POST "http://localhost:8000/api/portfolios" \
     -H "Authorization: Bearer {your_token}" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "Tech Portfolio",
           "stocks": [
             {"symbol": "AAPL", "weight": 0.4},
             {"symbol": "MSFT", "weight": 0.3},
             {"symbol": "GOOGL", "weight": 0.3}
           ]
         }'
```

### Optimize Portfolio
```bash
curl -X POST "http://localhost:8000/api/portfolios/{portfolio_id}/optimize" \
     -H "Authorization: Bearer {your_token}" \
     -H "Content-Type: application/json" \
     -d '{
           "risk_tolerance": "moderate",
           "investment_horizon": "long_term",
           "constraints": {
             "max_weight": 0.4,
             "min_weight": 0.1
           }
         }'
```

## Reports

### Generate Report
```bash
curl -X POST "http://localhost:8000/api/reports" \
     -H "Authorization: Bearer {your_token}" \
     -H "Content-Type: application/json" \
     -d '{
           "portfolio_id": "123",
           "report_type": "full_analysis",
           "format": "pdf"
         }'
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid input data",
  "errors": [
    {
      "loc": ["body", "stocks"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Portfolio not found"
}
```

### 429 Too Many Requests
```json
{
  "detail": "Too many requests",
  "retry_after": 60
}
```

## Rate Limits

- Authentication endpoints: 5 requests per minute
- Stock analysis endpoints: 30 requests per minute
- Portfolio endpoints: 20 requests per minute
- Report generation: 10 requests per minute

## Best Practices

1. Always include the Authorization header
2. Handle rate limiting with exponential backoff
3. Cache responses when possible
4. Use pagination for large datasets
5. Include proper error handling 