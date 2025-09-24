#!/usr/bin/env python3
"""
Docker Test Script

This script tests Docker functionality specifically.
"""

import subprocess
import sys
import time


def test_docker_command():
    """Test if docker command is available."""
    print("Testing Docker command availability...")
    
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✓ Docker command found: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Docker command failed: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ Docker command not found in PATH")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Docker command timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing Docker command: {e}")
        return False


def test_docker_daemon():
    """Test Docker daemon connectivity."""
    print("\nTesting Docker daemon connectivity...")
    
    try:
        # Test with different timeouts
        timeouts = [5, 10, 30]
        
        for timeout in timeouts:
            print(f"  Trying with {timeout}s timeout...")
            start_time = time.time()
            
            result = subprocess.run(['docker', 'info'], 
                                  capture_output=True, text=True, timeout=timeout)
            
            elapsed = time.time() - start_time
            print(f"  Command completed in {elapsed:.2f}s")
            
            if result.returncode == 0:
                print("  ✓ Docker daemon is running and accessible")
                return True
            else:
                print(f"  ❌ Docker daemon error (exit code: {result.returncode})")
                print(f"  stderr: {result.stderr.strip()}")
                
                # Check for specific error patterns
                error_lower = result.stderr.lower()
                if "permission denied" in error_lower:
                    print("  → This is a permission issue, not a daemon issue")
                    print("  → Try: sudo docker info")
                    print("  → Or add user to docker group: sudo usermod -aG docker $USER")
                    return True
                elif "cannot connect" in error_lower:
                    print("  → Docker daemon is not running")
                    print("  → Try: sudo systemctl start docker (Linux)")
                    print("  → Or start Docker Desktop (macOS/Windows)")
                    return False
                elif "connection refused" in error_lower:
                    print("  → Docker daemon is not running")
                    return False
        
        print("  ❌ All timeout attempts failed")
        return False
        
    except subprocess.TimeoutExpired:
        print("  ⚠️  Docker command timed out (daemon might be slow)")
        print("  → This usually means Docker is running but slow to respond")
        return True
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        return False


def test_docker_simple():
    """Test Docker with a simple command."""
    print("\nTesting Docker with simple command...")
    
    try:
        result = subprocess.run(['docker', 'run', '--rm', 'hello-world'], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✓ Docker can run containers successfully")
            return True
        else:
            print(f"❌ Docker container test failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Docker container test timed out")
        return False
    except Exception as e:
        print(f"❌ Error running Docker container: {e}")
        return False


def test_docker_permissions():
    """Test Docker permissions."""
    print("\nTesting Docker permissions...")
    
    try:
        # Test without sudo
        result = subprocess.run(['docker', 'ps'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✓ Docker permissions are correct")
            return True
        else:
            print(f"❌ Docker permission error: {result.stderr.strip()}")
            
            # Test with sudo
            print("  Testing with sudo...")
            sudo_result = subprocess.run(['sudo', 'docker', 'ps'], 
                                       capture_output=True, text=True, timeout=10)
            
            if sudo_result.returncode == 0:
                print("  ✓ Docker works with sudo")
                print("  → Add your user to docker group: sudo usermod -aG docker $USER")
                print("  → Then log out and log back in")
                return True
            else:
                print(f"  ❌ Docker doesn't work even with sudo: {sudo_result.stderr}")
                return False
                
    except Exception as e:
        print(f"❌ Error testing Docker permissions: {e}")
        return False


def main():
    """Main test function."""
    print("Docker Test Script")
    print("=" * 40)
    
    tests = [
        ("Docker Command", test_docker_command),
        ("Docker Daemon", test_docker_daemon),
        ("Docker Permissions", test_docker_permissions),
        ("Docker Container", test_docker_simple)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 20)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 40)
    print("Docker Test Summary")
    print("=" * 40)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All Docker tests passed!")
    elif passed > 0:
        print(f"\n⚠️  {total - passed} tests failed. Docker has some issues.")
    else:
        print("\n❌ All Docker tests failed. Docker is not working properly.")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
