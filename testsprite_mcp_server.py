#!/usr/bin/env python3
"""
TestSprite MCP Server Implementation
A Python-based MCP server that provides TestSprite functionality
"""
import json
import sys
import asyncio
import subprocess
from typing import Dict, Any, List
from pathlib import Path

class TestSpriteMCPServer:
    def __init__(self):
        self.project_root = Path.cwd()
        self.test_results = {}
        
    async def test_project(self, project_root: str, test_name: str, test_description: str) -> Dict[str, Any]:
        """Test a project with comprehensive analysis"""
        print(f"🎯 TestSprite: Testing project at {project_root}")
        print(f"📋 Test Name: {test_name}")
        print(f"📝 Description: {test_description}")
        
        # Change to project directory
        project_path = Path(project_root)
        if not project_path.exists():
            return {"error": f"Project path {project_root} does not exist"}
        
        # Run comprehensive tests
        results = await self._run_comprehensive_tests(project_path)
        
        return {
            "status": "completed",
            "test_name": test_name,
            "project_root": project_root,
            "results": results,
            "summary": self._generate_summary(results)
        }
    
    async def _run_comprehensive_tests(self, project_path: Path) -> Dict[str, Any]:
        """Run comprehensive tests on the project"""
        results = {
            "api_tests": await self._test_api_endpoints(project_path),
            "ml_tests": await self._test_ml_services(project_path),
            "trading_tests": await self._test_trading_services(project_path),
            "security_tests": await self._test_security(project_path),
            "performance_tests": await self._test_performance(project_path),
            "integration_tests": await self._test_integration(project_path)
        }
        return results
    
    async def _test_api_endpoints(self, project_path: Path) -> Dict[str, Any]:
        """Test API endpoints"""
        print("🔍 Testing API endpoints...")
        
        # Run pytest on API tests
        try:
            result = subprocess.run([
                "python", "-m", "pytest", 
                str(project_path / "tests" / "test_comprehensive_api.py"),
                "-v", "--tb=short"
            ], capture_output=True, text=True, cwd=project_path)
            
            return {
                "status": "completed",
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "passed": "PASSED" in result.stdout,
                "failed": "FAILED" in result.stdout
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _test_ml_services(self, project_path: Path) -> Dict[str, Any]:
        """Test ML services"""
        print("🤖 Testing ML services...")
        
        try:
            result = subprocess.run([
                "python", "-m", "pytest",
                str(project_path / "tests" / "test_ml_services.py"),
                "-v", "--tb=short"
            ], capture_output=True, text=True, cwd=project_path)
            
            return {
                "status": "completed",
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "passed": "PASSED" in result.stdout,
                "failed": "FAILED" in result.stdout
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _test_trading_services(self, project_path: Path) -> Dict[str, Any]:
        """Test trading services"""
        print("📈 Testing trading services...")
        
        try:
            result = subprocess.run([
                "python", "-m", "pytest",
                str(project_path / "tests" / "test_trading_services.py"),
                "-v", "--tb=short"
            ], capture_output=True, text=True, cwd=project_path)
            
            return {
                "status": "completed",
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "passed": "PASSED" in result.stdout,
                "failed": "FAILED" in result.stdout
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _test_security(self, project_path: Path) -> Dict[str, Any]:
        """Test security aspects"""
        print("🔒 Testing security...")
        
        # Check for common security issues
        security_issues = []
        
        # Check for hardcoded secrets
        for py_file in project_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "password" in content.lower() and "=" in content:
                        security_issues.append(f"Potential hardcoded password in {py_file}")
            except:
                pass
        
        return {
            "status": "completed",
            "security_issues": security_issues,
            "issues_count": len(security_issues)
        }
    
    async def _test_performance(self, project_path: Path) -> Dict[str, Any]:
        """Test performance aspects"""
        print("⚡ Testing performance...")
        
        # Check for performance issues
        performance_issues = []
        
        # Check for potential N+1 queries
        for py_file in project_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "for" in content and "query" in content.lower():
                        performance_issues.append(f"Potential N+1 query in {py_file}")
            except:
                pass
        
        return {
            "status": "completed",
            "performance_issues": performance_issues,
            "issues_count": len(performance_issues)
        }
    
    async def _test_integration(self, project_path: Path) -> Dict[str, Any]:
        """Test integration aspects"""
        print("🔗 Testing integration...")
        
        # Check if all required files exist
        required_files = [
            "app/main.py",
            "requirements.txt",
            "tests/conftest.py"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not (project_path / file_path).exists():
                missing_files.append(file_path)
        
        return {
            "status": "completed",
            "missing_files": missing_files,
            "all_files_present": len(missing_files) == 0
        }
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate test summary"""
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        for test_type, result in results.items():
            if isinstance(result, dict) and "passed" in result:
                if result.get("passed"):
                    passed_tests += 1
                if result.get("failed"):
                    failed_tests += 1
                total_tests += 1
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0
        }

async def main():
    """Main function for MCP server"""
    server = TestSpriteMCPServer()
    
    # Test the current project
    result = await server.test_project(
        project_root=str(Path.cwd()),
        test_name="AI Stock Backend Comprehensive Test",
        test_description="Comprehensive testing of the AI Stock Backend FastAPI application"
    )
    
    print("\n" + "="*60)
    print("🎯 TESTSPRITE TEST RESULTS")
    print("="*60)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
