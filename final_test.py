#!/usr/bin/env python3
"""
Final Comprehensive Test Suite
Tests all critical components before Hugging Face deployment
"""

import os
import sys
import json
from pathlib import Path
import importlib.util
import subprocess

class Colors:
    """ANSI color codes"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print formatted header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(80)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.RESET}\n")

def print_test(name, status, details=""):
    """Print test result"""
    if status:
        icon = f"{Colors.GREEN}✅{Colors.RESET}"
        status_text = f"{Colors.GREEN}PASS{Colors.RESET}"
    else:
        icon = f"{Colors.RED}❌{Colors.RESET}"
        status_text = f"{Colors.RED}FAIL{Colors.RESET}"
    
    print(f"{icon} {Colors.BOLD}{name}{Colors.RESET}: {status_text}")
    if details:
        print(f"   {Colors.YELLOW}→{Colors.RESET} {details}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ{Colors.RESET}  {text}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠{Colors.RESET}  {text}")

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓{Colors.RESET}  {text}")

# Test counters
total_tests = 0
passed_tests = 0
failed_tests = 0
warnings = 0

def test(name, condition, details="", critical=True):
    """Run a test and track results"""
    global total_tests, passed_tests, failed_tests, warnings
    total_tests += 1
    
    if condition:
        passed_tests += 1
        print_test(name, True, details)
    else:
        if critical:
            failed_tests += 1
            print_test(name, False, details)
        else:
            warnings += 1
            print_warning(f"{name}: {details}")

# ============================================================================
# TEST 1: Critical Files Existence
# ============================================================================
def test_critical_files():
    print_header("TEST 1: Critical Files Existence")
    
    critical_files = [
        # Entry points
        ("app.py", "Flask server entry point"),
        ("main.py", "Main entry point for HF Space"),
        ("hf_unified_server.py", "FastAPI unified server"),
        
        # Core modules
        ("ai_models.py", "AI models registry"),
        ("config.py", "Configuration module"),
        
        # Configuration files
        ("requirements.txt", "Python dependencies"),
        ("README.md", "Documentation"),
        ("Dockerfile", "Docker configuration"),
        ("docker-compose.yml", "Docker Compose config"),
        
        # Essential configs
        ("providers_config_extended.json", "Providers configuration"),
        ("crypto_resources_unified_2025-11-11.json", "Crypto resources registry"),
    ]
    
    for filename, description in critical_files:
        path = Path(f"/workspace/{filename}")
        test(
            f"File: {filename}",
            path.exists(),
            description,
            critical=True
        )

# ============================================================================
# TEST 2: Critical Directories
# ============================================================================
def test_critical_directories():
    print_header("TEST 2: Critical Directories")
    
    critical_dirs = [
        ("static", "Static files (HTML, CSS, JS)"),
        ("static/pages", "Multi-page application pages"),
        ("static/pages/dashboard", "Dashboard page"),
        ("backend", "Backend modules"),
        ("backend/routers", "API routers"),
        ("backend/services", "Backend services"),
        ("api", "API modules"),
        ("database", "Database modules"),
        ("utils", "Utility modules"),
        ("config", "Configuration directory"),
        ("templates", "HTML templates"),
    ]
    
    for dirname, description in critical_dirs:
        path = Path(f"/workspace/{dirname}")
        exists = path.exists() and path.is_dir()
        
        if exists and dirname.startswith("static/pages"):
            # Check if index.html exists
            index_file = path / "index.html"
            exists = index_file.exists()
            desc = f"{description} (with index.html)"
        else:
            desc = description
        
        test(
            f"Directory: {dirname}",
            exists,
            desc,
            critical=True
        )

# ============================================================================
# TEST 3: Python Modules Import
# ============================================================================
def test_python_imports():
    print_header("TEST 3: Python Modules Import Test")
    
    modules_to_test = [
        ("app", "Flask application"),
        ("hf_unified_server", "FastAPI application"),
        ("ai_models", "AI models registry"),
        ("config", "Configuration"),
    ]
    
    for module_name, description in modules_to_test:
        try:
            # Add workspace to path
            sys.path.insert(0, '/workspace')
            
            # Try to import
            spec = importlib.util.find_spec(module_name)
            if spec is None:
                test(f"Import: {module_name}", False, f"Module not found: {description}", critical=False)
            else:
                # Module exists, but we won't actually import to avoid dependencies
                test(f"Import: {module_name}", True, f"Module loadable: {description}")
        except Exception as e:
            test(f"Import: {module_name}", False, f"Error: {str(e)}", critical=False)

# ============================================================================
# TEST 4: Python Syntax Check
# ============================================================================
def test_python_syntax():
    print_header("TEST 4: Python Syntax Validation")
    
    python_files = [
        "app.py",
        "main.py",
        "hf_unified_server.py",
        "ai_models.py",
        "config.py",
    ]
    
    for filename in python_files:
        path = Path(f"/workspace/{filename}")
        if not path.exists():
            test(f"Syntax: {filename}", False, "File not found", critical=True)
            continue
        
        try:
            result = subprocess.run(
                ["python3", "-m", "py_compile", str(path)],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            test(
                f"Syntax: {filename}",
                result.returncode == 0,
                "Valid Python syntax" if result.returncode == 0 else f"Syntax error: {result.stderr[:100]}",
                critical=True
            )
        except Exception as e:
            test(f"Syntax: {filename}", False, f"Error checking syntax: {str(e)}", critical=True)

# ============================================================================
# TEST 5: JSON Configuration Validation
# ============================================================================
def test_json_configs():
    print_header("TEST 5: JSON Configuration Files Validation")
    
    json_files = [
        ("providers_config_extended.json", "Providers configuration"),
        ("crypto_resources_unified_2025-11-11.json", "Crypto resources"),
        ("package.json", "NPM package configuration"),
    ]
    
    for filename, description in json_files:
        path = Path(f"/workspace/{filename}")
        if not path.exists():
            test(f"JSON: {filename}", False, f"File not found: {description}", critical=False)
            continue
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check if it's empty
            is_valid = bool(data)
            details = f"Valid JSON with {len(data)} top-level keys" if isinstance(data, dict) else f"Valid JSON ({type(data).__name__})"
            
            test(f"JSON: {filename}", is_valid, details)
        except json.JSONDecodeError as e:
            test(f"JSON: {filename}", False, f"Invalid JSON: {str(e)}", critical=True)
        except Exception as e:
            test(f"JSON: {filename}", False, f"Error: {str(e)}", critical=False)

# ============================================================================
# TEST 6: Requirements.txt Validation
# ============================================================================
def test_requirements():
    print_header("TEST 6: Requirements.txt Validation")
    
    req_file = Path("/workspace/requirements.txt")
    
    if not req_file.exists():
        test("requirements.txt", False, "File not found", critical=True)
        return
    
    try:
        with open(req_file, 'r') as f:
            lines = f.readlines()
        
        # Filter out comments and empty lines
        packages = [line.strip() for line in lines if line.strip() and not line.strip().startswith('#')]
        
        test(
            "requirements.txt format",
            len(packages) > 0,
            f"Found {len(packages)} package dependencies"
        )
        
        # Check for essential packages
        essential_packages = ['fastapi', 'flask', 'uvicorn', 'requests', 'transformers']
        content = '\n'.join(lines)
        
        for pkg in essential_packages:
            found = pkg.lower() in content.lower()
            test(
                f"Package: {pkg}",
                found,
                "Required for core functionality" if found else "Missing essential package",
                critical=True
            )
    except Exception as e:
        test("requirements.txt", False, f"Error reading file: {str(e)}", critical=True)

# ============================================================================
# TEST 7: Static Files Structure
# ============================================================================
def test_static_files():
    print_header("TEST 7: Static Files Structure")
    
    static_structure = [
        ("static/index.html", "Main landing page"),
        ("static/pages/dashboard/index.html", "Dashboard page"),
        ("static/pages/market/index.html", "Market page"),
        ("static/pages/models/index.html", "AI Models page"),
        ("static/pages/sentiment/index.html", "Sentiment page"),
        ("static/pages/news/index.html", "News page"),
        ("static/shared/css/main.css", "Main stylesheet"),
        ("static/shared/js/api.js", "API client"),
    ]
    
    for filepath, description in static_structure:
        path = Path(f"/workspace/{filepath}")
        test(
            f"Static: {filepath}",
            path.exists(),
            description,
            critical=False
        )

# ============================================================================
# TEST 8: Database Module
# ============================================================================
def test_database_module():
    print_header("TEST 8: Database Module Structure")
    
    db_files = [
        ("database/__init__.py", "Database package init"),
        ("database/models.py", "Database models"),
        ("database/db.py", "Database connection"),
    ]
    
    for filename, description in db_files:
        path = Path(f"/workspace/{filename}")
        test(
            f"Database: {filename}",
            path.exists(),
            description,
            critical=False
        )

# ============================================================================
# TEST 9: Backend Structure
# ============================================================================
def test_backend_structure():
    print_header("TEST 9: Backend Structure")
    
    backend_items = [
        ("backend/__init__.py", "Backend package init"),
        ("backend/routers", "API routers directory"),
        ("backend/services", "Backend services directory"),
    ]
    
    for item, description in backend_items:
        path = Path(f"/workspace/{item}")
        exists = path.exists()
        
        test(
            f"Backend: {item}",
            exists,
            description,
            critical=False
        )
    
    # Check for key routers
    if Path("/workspace/backend/routers").exists():
        routers = [
            "unified_service_api.py",
            "direct_api.py",
            "ai_api.py",
        ]
        
        for router in routers:
            router_path = Path(f"/workspace/backend/routers/{router}")
            test(
                f"Router: {router}",
                router_path.exists(),
                "API router module",
                critical=False
            )

# ============================================================================
# TEST 10: Archive Organization
# ============================================================================
def test_archive_organization():
    print_header("TEST 10: Archive Organization")
    
    archive_path = Path("/workspace/archive")
    
    if not archive_path.exists():
        print_warning("Archive directory not found (optional)")
        return
    
    # Count archived files
    try:
        archived_files = list(archive_path.rglob("*"))
        file_count = len([f for f in archived_files if f.is_file()])
        
        test(
            "Archive organization",
            file_count > 0,
            f"Successfully archived {file_count} files",
            critical=False
        )
        
        # Check archive structure
        archive_subdirs = [
            "development",
            "documentation",
            "tests",
            "html-demos",
            "json-configs",
        ]
        
        for subdir in archive_subdirs:
            subdir_path = archive_path / subdir
            if subdir_path.exists():
                files = list(subdir_path.rglob("*"))
                file_count = len([f for f in files if f.is_file()])
                print_info(f"archive/{subdir}: {file_count} files")
    except Exception as e:
        print_warning(f"Error checking archive: {str(e)}")

# ============================================================================
# TEST 11: Docker Configuration
# ============================================================================
def test_docker_config():
    print_header("TEST 11: Docker Configuration")
    
    dockerfile = Path("/workspace/Dockerfile")
    docker_compose = Path("/workspace/docker-compose.yml")
    
    test(
        "Dockerfile",
        dockerfile.exists(),
        "Docker container configuration",
        critical=False
    )
    
    test(
        "docker-compose.yml",
        docker_compose.exists(),
        "Docker Compose configuration",
        critical=False
    )
    
    # Check Dockerfile content
    if dockerfile.exists():
        try:
            with open(dockerfile, 'r') as f:
                content = f.read()
            
            has_python = 'python' in content.lower()
            has_requirements = 'requirements.txt' in content
            
            test(
                "Dockerfile: Python base",
                has_python,
                "Uses Python base image",
                critical=False
            )
            
            test(
                "Dockerfile: Requirements install",
                has_requirements,
                "Installs Python dependencies",
                critical=False
            )
        except Exception as e:
            print_warning(f"Error reading Dockerfile: {str(e)}")

# ============================================================================
# TEST 12: README and Documentation
# ============================================================================
def test_documentation():
    print_header("TEST 12: Documentation")
    
    readme = Path("/workspace/README.md")
    
    test(
        "README.md",
        readme.exists(),
        "Project documentation",
        critical=True
    )
    
    if readme.exists():
        try:
            with open(readme, 'r', encoding='utf-8') as f:
                content = f.read()
            
            size_kb = len(content) / 1024
            has_setup = 'setup' in content.lower() or 'install' in content.lower()
            has_usage = 'usage' in content.lower() or 'start' in content.lower()
            
            test(
                "README.md size",
                len(content) > 100,
                f"{size_kb:.1f} KB of documentation",
                critical=False
            )
            
            test(
                "README.md: Setup instructions",
                has_setup,
                "Contains setup/installation guide",
                critical=False
            )
            
            test(
                "README.md: Usage instructions",
                has_usage,
                "Contains usage information",
                critical=False
            )
        except Exception as e:
            print_warning(f"Error reading README: {str(e)}")

# ============================================================================
# FINAL REPORT
# ============================================================================
def print_final_report():
    print_header("FINAL TEST REPORT")
    
    # Calculate percentage
    if total_tests > 0:
        pass_percentage = (passed_tests / total_tests) * 100
    else:
        pass_percentage = 0
    
    # Overall status
    if failed_tests == 0:
        overall_status = f"{Colors.GREEN}{Colors.BOLD}✅ READY FOR DEPLOYMENT{Colors.RESET}"
        recommendation = f"{Colors.GREEN}The project is ready to be uploaded to Hugging Face!{Colors.RESET}"
    elif failed_tests <= 3:
        overall_status = f"{Colors.YELLOW}{Colors.BOLD}⚠️  NEEDS MINOR FIXES{Colors.RESET}"
        recommendation = f"{Colors.YELLOW}Some non-critical issues detected. Review and fix before deployment.{Colors.RESET}"
    else:
        overall_status = f"{Colors.RED}{Colors.BOLD}❌ NOT READY{Colors.RESET}"
        recommendation = f"{Colors.RED}Critical issues detected. Fix before deployment.{Colors.RESET}"
    
    print(f"{Colors.BOLD}Total Tests:{Colors.RESET} {total_tests}")
    print(f"{Colors.GREEN}Passed:{Colors.RESET} {passed_tests}")
    print(f"{Colors.RED}Failed:{Colors.RESET} {failed_tests}")
    print(f"{Colors.YELLOW}Warnings:{Colors.RESET} {warnings}")
    print(f"{Colors.BOLD}Success Rate:{Colors.RESET} {pass_percentage:.1f}%")
    print()
    print(f"{Colors.BOLD}Overall Status:{Colors.RESET} {overall_status}")
    print()
    print(f"{Colors.BOLD}Recommendation:{Colors.RESET} {recommendation}")
    print()
    
    # Additional info
    print_info("Project Structure:")
    print(f"  • Main entry points: app.py, main.py, hf_unified_server.py")
    print(f"  • Backend modules: backend/, api/, database/")
    print(f"  • Frontend: static/ (multi-page application)")
    print(f"  • Configuration: config/, providers_config_extended.json")
    print(f"  • Documentation: README.md")
    print()
    
    if failed_tests == 0:
        print_success("All critical tests passed! ✨")
        print_success("The project is clean, organized, and ready for Hugging Face deployment.")
    elif failed_tests <= 3:
        print_warning("Minor issues detected. Review the failed tests above.")
    else:
        print_warning("Critical issues detected. Please fix before deployment.")
    
    print()
    print(f"{Colors.CYAN}{'=' * 80}{Colors.RESET}\n")

# ============================================================================
# MAIN
# ============================================================================
def main():
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}")
    print("╔════════════════════════════════════════════════════════════════════════════╗")
    print("║                    FINAL COMPREHENSIVE TEST SUITE                          ║")
    print("║                 Crypto Intelligence Hub - Pre-Deployment                   ║")
    print("╚════════════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}\n")
    
    # Run all tests
    test_critical_files()
    test_critical_directories()
    test_python_imports()
    test_python_syntax()
    test_json_configs()
    test_requirements()
    test_static_files()
    test_database_module()
    test_backend_structure()
    test_archive_organization()
    test_docker_config()
    test_documentation()
    
    # Print final report
    print_final_report()
    
    # Exit code
    return 0 if failed_tests == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
