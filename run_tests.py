#!/usr/bin/env python3
"""
Simple test runner script for AI Stock Backend
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and return success status"""
    print(f"\n🔄 {description}...")
    print(f"Command: {command}")
    print("-" * 50)
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✅ Success!")
        if result.stdout:
            print("Output:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed with exit code {e.returncode}")
        if e.stdout:
            print("Output:", e.stdout)
        if e.stderr:
            print("Error:", e.stderr)
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        "pytest",
        "fastapi",
        "sqlalchemy",
        "pandas",
        "numpy",
        "sklearn"  # scikit-learn imports as sklearn
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Install them with: pip install -r requirements.txt -r requirements-test.txt")
        return False
    
    print("✅ All dependencies found!")
    return True

def run_tests():
    """Run the test suite"""
    print("\n🚀 Starting AI Stock Backend Test Suite")
    print("=" * 60)
    
    # Check dependencies first
    if not check_dependencies():
        print("\n❌ Dependencies check failed. Please install missing packages.")
        return False
    
    # Run tests
    test_commands = [
        ("pytest tests/test_config.py -v", "Configuration tests"),
        ("pytest tests/test_comprehensive_api.py -v", "API tests"),
        ("pytest tests/test_ml_services.py -v", "ML service tests"),
        ("pytest tests/test_trading_services.py -v", "Trading service tests"),
        ("pytest tests/core/ -v", "Core tests"),
        ("pytest tests/db/ -v", "Database tests"),
        ("pytest tests/security/ -v", "Security tests"),
        ("pytest tests/integration/ -v", "Integration tests")
    ]
    
    results = []
    
    for command, description in test_commands:
        success = run_command(command, description)
        results.append((description, success))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for description, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} {description}")
        if success:
            passed += 1
    
    print(f"\n📈 Overall: {passed}/{total} test suites passed")
    
    if passed == total:
        print("🎉 All tests passed! Your AI Stock Backend is ready.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the output above.")
        return False

def run_coverage():
    """Run tests with coverage"""
    print("\n📊 Running tests with coverage...")
    
    command = "pytest tests/ --cov=app --cov-report=html --cov-report=term-missing -v"
    success = run_command(command, "Coverage analysis")
    
    if success:
        print("\n📁 Coverage report generated: htmlcov/index.html")
    
    return success

def main():
    """Main function"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "coverage":
            success = run_coverage()
        elif sys.argv[1] == "deps":
            success = check_dependencies()
        else:
            print("Usage: python run_tests.py [coverage|deps]")
            success = False
    else:
        success = run_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
