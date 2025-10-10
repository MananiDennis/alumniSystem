#!/usr/bin/env python3
"""
Unified Alumni System Launcher
Starts both backend API and React frontend with dependency management
"""
import subprocess
import sys
import time
import os
import webbrowser
from pathlib import Path


def check_python_deps():
    """Install Python dependencies if needed"""
    try:
        import uvicorn, fastapi
        print("✅ Python dependencies OK")
    except ImportError:
        print("📦 Installing Python dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)


def check_node_deps():
    """Install Node.js dependencies if needed"""
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    if not (frontend_dir / "node_modules").exists():
        print("📦 Installing frontend dependencies...")
        try:
            subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ npm install failed. Please install Node.js")
            return False
    
    print("✅ Frontend dependencies OK")
    return True


def start_backend():
    """Start FastAPI backend"""
    print("🚀 Starting Alumni API...")
    return subprocess.Popen([
        sys.executable, "-m", "uvicorn", 
        "src.api.main:app", 
        "--host", "0.0.0.0", 
        "--port", "8000",
        "--reload"
    ])


def start_frontend():
    """Start React frontend"""
    print("🌐 Starting React frontend...")
    try:
        return subprocess.Popen(
            ["npm", "start"], 
            cwd="frontend",
            env={**os.environ, "BROWSER": "none"}
        )
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return None


def main():
    """Main launcher function"""
    print("🎓 ECU Alumni Tracking System")
    print("=" * 40)
    
    # Check dependencies
    check_python_deps()
    if not check_node_deps():
        print("\n💡 You can still use the API at http://localhost:8000")
        print("   Install Node.js to use the full web interface")
    
    # Start services
    backend = start_backend()
    time.sleep(3)  # Wait for backend
    
    frontend = start_frontend()
    
    if frontend:
        print("\n✅ System started successfully!")
        print("🌐 Frontend: http://localhost:3000")
        print("🔧 API: http://localhost:8000")
        print("📚 API Docs: http://localhost:8000/docs")
        print("\n🛑 Press Ctrl+C to stop")
        
        # Open browser after delay
        time.sleep(5)
        try:
            webbrowser.open("http://localhost:3000")
        except:
            pass
        
        try:
            backend.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping services...")
            backend.terminate()
            if frontend:
                frontend.terminate()
            print("✅ Services stopped")
    else:
        print("\n⚠️  Frontend failed, but API is running at:")
        print("   http://localhost:8000")
        print("   http://localhost:8000/docs")
        print("\n🛑 Press Ctrl+C to stop")
        
        try:
            backend.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping API...")
            backend.terminate()


if __name__ == "__main__":
    main()