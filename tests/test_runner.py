"""
Comprehensive test runner for the AI Stock Backend project
"""
import pytest
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_all_tests():
    """Run all tests in the project"""
    print("🚀 Starting comprehensive test suite for AI Stock Backend...")
    print("=" * 60)
    
    # Test categories
    test_categories = {
        "API Tests": "tests/test_comprehensive_api.py",
        "ML Services": "tests/test_ml_services.py", 
        "Trading Services": "tests/test_trading_services.py",
        "Core Tests": "tests/core/",
        "Database Tests": "tests/db/",
        "Security Tests": "tests/security/",
        "Integration Tests": "tests/integration/",
        "Performance Tests": "tests/benchmarks/",
        "Load Tests": "tests/load/"
    }
    
    results = {}
    
    for category, test_path in test_categories.items():
        print(f"\n📋 Running {category}...")
        print("-" * 40)
        
        try:
            # Run pytest for this category
            result = pytest.main([
                test_path,
                "-v",
                "--tb=short",
                "--disable-warnings",
                "--color=yes"
            ])
            results[category] = "PASSED" if result == 0 else "FAILED"
        except Exception as e:
            print(f"❌ Error running {category}: {e}")
            results[category] = "ERROR"
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    for category, result in results.items():
        status_icon = "✅" if result == "PASSED" else "❌"
        print(f"{status_icon} {category}: {result}")
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result == "PASSED")
    
    print(f"\n📈 Overall: {passed_tests}/{total_tests} test categories passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Your AI Stock Backend is ready for production.")
    else:
        print("⚠️  Some tests failed. Please review the results above.")
    
    return results

def run_specific_tests(test_pattern: str):
    """Run specific tests matching a pattern"""
    print(f"🔍 Running tests matching: {test_pattern}")
    print("=" * 60)
    
    result = pytest.main([
        test_pattern,
        "-v",
        "--tb=short",
        "--disable-warnings",
        "--color=yes"
    ])
    
    return result == 0

def run_performance_tests():
    """Run performance and benchmark tests"""
    print("⚡ Running performance tests...")
    print("=" * 60)
    
    result = pytest.main([
        "tests/benchmarks/",
        "tests/load/",
        "-v",
        "--tb=short",
        "--disable-warnings",
        "--color=yes"
    ])
    
    return result == 0

def run_security_tests():
    """Run security tests"""
    print("🔒 Running security tests...")
    print("=" * 60)
    
    result = pytest.main([
        "tests/security/",
        "-v",
        "--tb=short",
        "--disable-warnings",
        "--color=yes"
    ])
    
    return result == 0

def run_integration_tests():
    """Run integration tests"""
    print("🔗 Running integration tests...")
    print("=" * 60)
    
    result = pytest.main([
        "tests/integration/",
        "-v",
        "--tb=short",
        "--disable-warnings",
        "--color=yes"
    ])
    
    return result == 0

def generate_test_report():
    """Generate a comprehensive test report"""
    print("📊 Generating test report...")
    print("=" * 60)
    
    # Run tests with coverage
    result = pytest.main([
        "tests/",
        "--cov=app",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-report=xml",
        "-v",
        "--tb=short",
        "--disable-warnings",
        "--color=yes"
    ])
    
    print("\n📁 Test reports generated:")
    print("  - HTML: htmlcov/index.html")
    print("  - XML: coverage.xml")
    print("  - Terminal: Above output")
    
    return result == 0

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Stock Backend Test Runner")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--pattern", type=str, help="Run tests matching pattern")
    parser.add_argument("--performance", action="store_true", help="Run performance tests")
    parser.add_argument("--security", action="store_true", help="Run security tests")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--report", action="store_true", help="Generate test report with coverage")
    
    args = parser.parse_args()
    
    if args.all:
        run_all_tests()
    elif args.pattern:
        run_specific_tests(args.pattern)
    elif args.performance:
        run_performance_tests()
    elif args.security:
        run_security_tests()
    elif args.integration:
        run_integration_tests()
    elif args.report:
        generate_test_report()
    else:
        print("Please specify a test option. Use --help for more information.")
        print("\nAvailable options:")
        print("  --all          Run all tests")
        print("  --pattern      Run tests matching pattern")
        print("  --performance  Run performance tests")
        print("  --security     Run security tests")
        print("  --integration  Run integration tests")
        print("  --report       Generate test report with coverage")
