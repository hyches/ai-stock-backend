#!/usr/bin/env python3
"""
Test script for the stock search functionality
"""
import requests
import json
import time

def test_stock_search():
    """Test the stock search API"""
    base_url = "http://127.0.0.1:8000/api/v1"
    
    print("🔍 Testing Stock Search API...")
    
    # Test search functionality
    try:
        response = requests.get(f"{base_url}/market/search?q=AAPL")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search API working: Found {len(data)} results for AAPL")
            for stock in data[:3]:  # Show first 3 results
                print(f"   - {stock['symbol']}: {stock['name']}")
        else:
            print(f"❌ Search API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Search API error: {e}")
    
    # Test stock details
    try:
        response = requests.get(f"{base_url}/market/data/AAPL")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Stock Details API working: {data['symbol']} - ${data['price']:.2f}")
        else:
            print(f"❌ Stock Details API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Stock Details API error: {e}")
    
    # Test market overview
    try:
        response = requests.get(f"{base_url}/market/overview")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Market Overview API working: {data['gainers']} gainers, {data['losers']} losers")
        else:
            print(f"❌ Market Overview API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Market Overview API error: {e}")
    
    # Test popular stocks
    try:
        response = requests.get(f"{base_url}/market/popular")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Popular Stocks API working: Found {len(data)} popular stocks")
        else:
            print(f"❌ Popular Stocks API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Popular Stocks API error: {e}")

def test_frontend():
    """Test if frontend is accessible"""
    print("\n🌐 Testing Frontend...")
    
    try:
        response = requests.get("http://127.0.0.1:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is accessible")
        else:
            print(f"❌ Frontend returned status: {response.status_code}")
    except Exception as e:
        print(f"❌ Frontend not accessible: {e}")

def main():
    """Main test function"""
    print("🚀 AI Stock Trading Platform - Test Suite")
    print("=" * 50)
    
    # Wait a moment for servers to start
    print("⏳ Waiting for servers to start...")
    time.sleep(2)
    
    # Test backend APIs
    test_stock_search()
    
    # Test frontend
    test_frontend()
    
    print("\n" + "=" * 50)
    print("🎯 Test Summary:")
    print("1. Backend APIs should be working")
    print("2. Frontend should be accessible")
    print("3. Visit http://127.0.0.1:3000 to see the home page")
    print("4. Search for stocks like 'AAPL', 'MSFT', 'GOOGL'")
    print("5. Click on any stock to see detailed information")
    
    print("\n🔧 If tests fail:")
    print("- Make sure backend is running: python run_server.py")
    print("- Make sure frontend is running: cd frontend && npm run dev")
    print("- Check if all dependencies are installed")

if __name__ == "__main__":
    main()
