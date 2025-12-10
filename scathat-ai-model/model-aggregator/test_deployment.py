#!/usr/bin/env python3
"""
Test script to verify deployment configuration
"""

import os
import sys
import subprocess

def test_docker_build():
    """Test that Docker build works"""
    print("🧪 Testing Docker build...")
    
    try:
        # Test Dockerfile syntax
        result = subprocess.run([
            'docker', 'build', '-q', '-f', 'Dockerfile', '.'
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Docker build test passed")
            return True
        else:
            print(f"❌ Docker build failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Docker build timed out")
        return False
    except Exception as e:
        print(f"❌ Docker build error: {e}")
        return False

def test_requirements():
    """Test that requirements.txt is valid"""
    print("🧪 Testing requirements.txt...")
    
    if not os.path.exists('requirements.txt'):
        print("❌ requirements.txt not found")
        return False
    
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read().strip()
        
        if requirements:
            print("✅ requirements.txt is valid")
            return True
        else:
            print("❌ requirements.txt is empty")
            return False
            
    except Exception as e:
        print(f"❌ Error reading requirements.txt: {e}")
        return False

def test_api_server():
    """Test that api_server.py exists and is importable"""
    print("🧪 Testing API server...")
    
    if not os.path.exists('api_server.py'):
        print("❌ api_server.py not found")
        return False
    
    try:
        # Try to import the main components
        import sys
        sys.path.insert(0, '.')
        
        from api_server import app
        from model_aggregator import ResultAggregator
        from bytecode_client import BytecodeDetectorClient
        
        print("✅ API server components import successfully")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Other error: {e}")
        return False

def test_deploy_script():
    """Test that deploy script exists and is executable"""
    print("🧪 Testing deploy script...")
    
    if not os.path.exists('deploy.sh'):
        print("❌ deploy.sh not found")
        return False
    
    if not os.access('deploy.sh', os.X_OK):
        print("❌ deploy.sh is not executable")
        return False
    
    # Check script syntax
    try:
        result = subprocess.run(['bash', '-n', 'deploy.sh'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ deploy.sh syntax is valid")
            return True
        else:
            print(f"❌ deploy.sh syntax error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error testing deploy.sh: {e}")
        return False

def main():
    """Run all deployment tests"""
    print("🚀 Running deployment configuration tests\n")
    
    tests = [
        test_requirements,
        test_api_server,
        test_deploy_script,
        test_docker_build
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All deployment tests passed! Ready for deployment.")
        return 0
    else:
        print("❌ Some tests failed. Please fix the issues before deployment.")
        return 1

if __name__ == "__main__":
    sys.exit(main())