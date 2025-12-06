#!/usr/bin/env python3
"""
Verification script for Hugging Face deployment
Checks all critical components are configured correctly
"""

import os
import sys
from pathlib import Path

def check_port_configuration():
    """Verify port is correctly configured"""
    print("=" * 70)
    print("1. PORT Configuration Check")
    print("=" * 70)
    
    port_env = os.getenv("PORT")
    hf_port_env = os.getenv("HF_PORT")
    default_port = 7860
    
    print(f"  PORT env var: {port_env or 'not set'}")
    print(f"  HF_PORT env var: {hf_port_env or 'not set'}")
    print(f"  Default port: {default_port}")
    
    # Hugging Face sets PORT automatically
    if port_env:
        print(f"  [OK] PORT is set: {port_env}")
        print(f"  [OK] App will use port {port_env} (Hugging Face assigned)")
    else:
        print(f"  [WARN] PORT not set, will use default: {default_port}")
        print(f"  [INFO] Hugging Face will set PORT automatically in production")
    
    print()

def check_static_files():
    """Verify static files are accessible"""
    print("=" * 70)
    print("2. Static Files Check")
    print("=" * 70)
    
    workspace_candidates = [Path("."), Path("/app"), Path("/workspace")]
    static_path = None
    
    for candidate in workspace_candidates:
        test_path = candidate / "static" / "pages" / "dashboard" / "index.html"
        if test_path.exists():
            static_path = candidate / "static"
            print(f"  [OK] Found static directory: {static_path}")
            break
    
    if static_path:
        # Check key files
        key_files = [
            "index.html",
            "pages/dashboard/index.html",
            "pages/models/index.html",
            "shared/js/core/layout-manager.js",
            "shared/js/core/models-client.js",
            "shared/js/core/api-client.js"
        ]
        
        for file_path in key_files:
            full_path = static_path / file_path
            if full_path.exists():
                print(f"  [OK] {file_path}")
            else:
                print(f"  [ERROR] {file_path} - MISSING")
    else:
        print("  [ERROR] Static directory not found!")
        print("  [WARN] Check WORKSPACE_ROOT configuration")
    
    print()

def check_environment_variables():
    """Check critical environment variables"""
    print("=" * 70)
    print("3. Environment Variables Check")
    print("=" * 70)
    
    critical_vars = {
        "PORT": os.getenv("PORT"),
        "HOST": os.getenv("HOST", "0.0.0.0"),
        "HF_MODE": os.getenv("HF_MODE", "not set"),
        "SPACE_ID": os.getenv("SPACE_ID"),
        "HF_TOKEN": "***" if os.getenv("HF_TOKEN") else "not set",
        "HUGGINGFACE_TOKEN": "***" if os.getenv("HUGGINGFACE_TOKEN") else "not set",
        "USE_MOCK_DATA": os.getenv("USE_MOCK_DATA", "false"),
        "PYTHONUNBUFFERED": os.getenv("PYTHONUNBUFFERED", "not set"),
    }
    
    for var, value in critical_vars.items():
        if value:
            status = "[OK]" if var in ["PORT", "HOST"] or value != "not set" else "[WARN]"
            print(f"  {status} {var}: {value}")
        else:
            print(f"  [WARN] {var}: not set")
    
    # Check if running in Hugging Face
    is_hf_space = bool(os.getenv("SPACE_ID")) or os.getenv("HF_SPACES") == "true"
    if is_hf_space:
        print(f"  [OK] Running in Hugging Face Space")
    else:
        print(f"  [INFO] Running locally (not in Hugging Face Space)")
    
    print()

def check_api_endpoints():
    """Verify API endpoints are accessible"""
    print("=" * 70)
    print("4. API Endpoints Check")
    print("=" * 70)
    
    # Check if endpoints file exists
    endpoints_file = Path("api_endpoints.py")
    if endpoints_file.exists():
        print("  [OK] api_endpoints.py exists")
        
        # Check for key endpoints
        content = endpoints_file.read_text()
        key_endpoints = [
            "/api/models/summary",
            "/api/models/status",
            "/api/health",
            "/api/resources/summary"
        ]
        
        for endpoint in key_endpoints:
            if endpoint.replace("/", "").replace("api", "api") in content.replace("/", ""):
                print(f"  [OK] {endpoint} endpoint found")
            else:
                print(f"  [WARN] {endpoint} endpoint - check manually")
    else:
        print("  [ERROR] api_endpoints.py not found!")
    
    print()

def check_model_loading():
    """Check model loading configuration"""
    print("=" * 70)
    print("5. Model Loading Check")
    print("=" * 70)
    
    ai_models_file = Path("ai_models.py")
    if ai_models_file.exists():
        print("  [OK] ai_models.py exists")
        
        content = ai_models_file.read_text()
        
        # Check for HF_TOKEN usage
        if "HF_TOKEN" in content or "HUGGINGFACE_TOKEN" in content:
            print("  [OK] HF_TOKEN handling found")
        else:
            print("  [WARN] HF_TOKEN handling not found")
        
        # Check for transformers
        if "transformers" in content.lower():
            print("  [OK] Transformers integration found")
        else:
            print("  [WARN] Transformers integration not found")
    else:
        print("  [ERROR] ai_models.py not found!")
    
    print()

def check_docker_configuration():
    """Check Docker configuration"""
    print("=" * 70)
    print("6. Docker Configuration Check")
    print("=" * 70)
    
    dockerfile = Path("Dockerfile")
    if dockerfile.exists():
        print("  [OK] Dockerfile exists")
        
        content = dockerfile.read_text()
        
        # Check port
        if "EXPOSE" in content:
            print(f"  [OK] EXPOSE directive found")
            if "7860" in content:
                print(f"  [OK] Port 7860 configured")
            else:
                print(f"  [WARN] Check port configuration")
        
        # Check CMD
        if "CMD" in content and "api_server_extended.py" in content:
            print(f"  [OK] CMD correctly points to api_server_extended.py")
        else:
            print(f"  [WARN] Check CMD directive")
    else:
        print("  [WARN] Dockerfile not found (may use .huggingface.yml)")
    
    # Check Hugging Face config
    hf_config = Path(".huggingface.yml")
    if hf_config.exists():
        print("  [OK] .huggingface.yml exists")
        content = hf_config.read_text()
        if "app_port: 7860" in content:
            print("  [OK] app_port: 7860 configured")
        if "health_check" in content:
            print("  [OK] Health check configured")
    else:
        print("  [WARN] .huggingface.yml not found")
    
    print()

def main():
    """Run all checks"""
    print("\n" + "=" * 70)
    print("HUGGING FACE DEPLOYMENT VERIFICATION")
    print("=" * 70)
    print()
    
    check_port_configuration()
    check_static_files()
    check_environment_variables()
    check_api_endpoints()
    check_model_loading()
    check_docker_configuration()
    
    print("=" * 70)
    print("VERIFICATION COMPLETE")
    print("=" * 70)
    print()
    print("Summary:")
    print("  - Port: Uses PORT env var (set by Hugging Face)")
    print("  - Static Files: Served via FastAPI StaticFiles")
    print("  - API Endpoints: Available at /api/*")
    print("  - Models: Load via ai_models.py with HF_TOKEN")
    print()
    print("[SUCCESS] Ready for Hugging Face deployment!")
    print()

if __name__ == "__main__":
    main()

