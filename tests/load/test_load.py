import pytest
import asyncio
import aiohttp
import time
from typing import List, Dict
import statistics
from app.config import Settings

# Test configuration
BASE_URL = "http://localhost:8000"
CONCURRENT_USERS = 50
REQUESTS_PER_USER = 20
THINK_TIME = 1  # seconds between requests

settings = Settings()

class LoadTest:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.results: List[Dict] = []
    
    async def make_request(self, session: aiohttp.ClientSession, endpoint: str, method: str = "GET", 
                          data: Dict = None, headers: Dict = None) -> Dict:
        """Make a single request and record metrics"""
        start_time = time.time()
        try:
            if method == "GET":
                async with session.get(f"{self.base_url}{endpoint}", headers=headers) as response:
                    status = response.status
                    await response.text()
            else:
                async with session.post(f"{self.base_url}{endpoint}", json=data, headers=headers) as response:
                    status = response.status
                    await response.text()
            
            duration = time.time() - start_time
            return {
                "endpoint": endpoint,
                "status": status,
                "duration": duration,
                "success": 200 <= status < 300
            }
        except Exception as e:
            duration = time.time() - start_time
            return {
                "endpoint": endpoint,
                "status": 0,
                "duration": duration,
                "success": False,
                "error": str(e)
            }
    
    async def user_session(self, user_id: int, auth_token: str):
        """Simulate a user session"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        async with aiohttp.ClientSession() as session:
            for _ in range(REQUESTS_PER_USER):
                # Simulate user behavior
                endpoints = [
                    ("/api/stocks/AAPL/sentiment", "GET"),
                    ("/api/stocks/MSFT/sentiment", "GET"),
                    ("/api/portfolios", "POST", {
                        "name": f"Test Portfolio {user_id}",
                        "stocks": [
                            {"symbol": "AAPL", "weight": 0.4},
                            {"symbol": "MSFT", "weight": 0.3},
                            {"symbol": "GOOGL", "weight": 0.3}
                        ]
                    })
                ]
                
                for endpoint in endpoints:
                    if len(endpoint) == 2:
                        result = await self.make_request(session, endpoint[0], endpoint[1], headers=headers)
                    else:
                        result = await self.make_request(session, endpoint[0], endpoint[1], endpoint[2], headers=headers)
                    
                    self.results.append(result)
                    await asyncio.sleep(THINK_TIME)
    
    def analyze_results(self) -> Dict:
        """Analyze test results"""
        if not self.results:
            return {}
        
        # Calculate metrics
        durations = [r["duration"] for r in self.results]
        success_rate = sum(1 for r in self.results if r["success"]) / len(self.results)
        
        return {
            "total_requests": len(self.results),
            "success_rate": success_rate,
            "avg_response_time": statistics.mean(durations),
            "min_response_time": min(durations),
            "max_response_time": max(durations),
            "p95_response_time": statistics.quantiles(durations, n=20)[18],
            "p99_response_time": statistics.quantiles(durations, n=100)[98],
            "errors": [r for r in self.results if not r["success"]]
        }

@pytest.mark.asyncio
async def test_concurrent_users():
    """Test system under concurrent user load"""
    load_test = LoadTest(BASE_URL)
    
    # Create test users and get auth tokens
    auth_tokens = []
    async with aiohttp.ClientSession() as session:
        for i in range(CONCURRENT_USERS):
            # Register user
            user_data = {
                "email": f"test{i}@example.com",
                "password": "password123",
                "full_name": f"Test User {i}"
            }
            async with session.post(f"{BASE_URL}/api/auth/register", json=user_data) as response:
                if response.status == 200:
                    # Login to get token
                    login_data = {
                        "username": user_data["email"],
                        "password": user_data["password"]
                    }
                    async with session.post(f"{BASE_URL}/api/auth/login", json=login_data) as login_response:
                        if login_response.status == 200:
                            token_data = await login_response.json()
                            auth_tokens.append(token_data["access_token"])
    
    # Run concurrent user sessions
    tasks = []
    for i, token in enumerate(auth_tokens):
        tasks.append(load_test.user_session(i, token))
    
    await asyncio.gather(*tasks)
    
    # Analyze results
    results = load_test.analyze_results()
    
    # Assertions
    assert results["success_rate"] >= 0.95, f"Success rate {results['success_rate']} below 95%"
    assert results["avg_response_time"] < 1.0, f"Average response time {results['avg_response_time']}s above 1s"
    assert results["p95_response_time"] < 2.0, f"95th percentile response time {results['p95_response_time']}s above 2s"
    assert results["p99_response_time"] < 3.0, f"99th percentile response time {results['p99_response_time']}s above 3s"

@pytest.mark.asyncio
async def test_sustained_load():
    """Test system under sustained load"""
    load_test = LoadTest(BASE_URL)
    duration = 300  # 5 minutes
    end_time = time.time() + duration
    
    # Get auth token
    async with aiohttp.ClientSession() as session:
        login_data = {
            "username": "test@example.com",
            "password": "password123"
        }
        async with session.post(f"{BASE_URL}/api/auth/login", json=login_data) as response:
            if response.status == 200:
                token_data = await response.json()
                auth_token = token_data["access_token"]
    
    # Run sustained load
    while time.time() < end_time:
        async with aiohttp.ClientSession() as session:
            # Make a batch of requests
            endpoints = [
                "/api/stocks/AAPL/sentiment",
                "/api/stocks/MSFT/sentiment",
                "/api/stocks/GOOGL/sentiment"
            ]
            
            tasks = []
            for endpoint in endpoints:
                tasks.append(load_test.make_request(
                    session,
                    endpoint,
                    headers={"Authorization": f"Bearer {auth_token}"}
                ))
            
            await asyncio.gather(*tasks)
            await asyncio.sleep(1)  # 1 second between batches
    
    # Analyze results
    results = load_test.analyze_results()
    
    # Assertions
    assert results["success_rate"] >= 0.98, f"Success rate {results['success_rate']} below 98%"
    assert results["avg_response_time"] < 0.5, f"Average response time {results['avg_response_time']}s above 0.5s"
    assert results["p95_response_time"] < 1.0, f"95th percentile response time {results['p95_response_time']}s above 1s"

@pytest.mark.asyncio
async def test_error_handling():
    """Test system error handling under load"""
    load_test = LoadTest(BASE_URL)
    
    # Get auth token
    async with aiohttp.ClientSession() as session:
        login_data = {
            "username": "test@example.com",
            "password": "password123"
        }
        async with session.post(f"{BASE_URL}/api/auth/login", json=login_data) as response:
            if response.status == 200:
                token_data = await response.json()
                auth_token = token_data["access_token"]
    
    # Make requests with invalid data
    async with aiohttp.ClientSession() as session:
        invalid_requests = [
            ("/api/stocks/INVALID/sentiment", "GET"),
            ("/api/portfolios", "POST", {"invalid": "data"}),
            ("/api/reports", "POST", {"invalid": "data"})
        ]
        
        tasks = []
        for endpoint in invalid_requests:
            if len(endpoint) == 2:
                tasks.append(load_test.make_request(
                    session,
                    endpoint[0],
                    endpoint[1],
                    headers={"Authorization": f"Bearer {auth_token}"}
                ))
            else:
                tasks.append(load_test.make_request(
                    session,
                    endpoint[0],
                    endpoint[1],
                    endpoint[2],
                    headers={"Authorization": f"Bearer {auth_token}"}
                ))
        
        await asyncio.gather(*tasks)
    
    # Analyze results
    results = load_test.analyze_results()
    
    # Assertions
    assert all(r["status"] in [400, 404, 422] for r in results["errors"]), "Invalid error status codes"
    assert results["avg_response_time"] < 0.5, f"Average response time {results['avg_response_time']}s above 0.5s" 