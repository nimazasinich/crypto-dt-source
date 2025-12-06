#!/usr/bin/env python3
"""
Installation Verification Script
Checks all components before starting the application
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple

class Colors:
    """ANSI color codes"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class InstallationVerifier:
    def __init__(self):
        self.checks_passed = 0
        self.checks_failed = 0
        self.warnings = 0
        self.workspace = Path(__file__).parent
    
    def check(self, name: str, condition: bool, details: str = "") -> bool:
        """Perform a check and print result"""
        if condition:
            print(f"{Colors.GREEN}✅ {name}{Colors.RESET}")
            if details:
                print(f"   {details}")
            self.checks_passed += 1
            return True
        else:
            print(f"{Colors.RED}❌ {name}{Colors.RESET}")
            if details:
                print(f"   {details}")
            self.checks_failed += 1
            return False
    
    def warn(self, name: str, details: str = ""):
        """Print a warning"""
        print(f"{Colors.YELLOW}⚠️  {name}{Colors.RESET}")
        if details:
            print(f"   {details}")
        self.warnings += 1
    
    def info(self, message: str):
        """Print info message"""
        print(f"{Colors.BLUE}ℹ️  {message}{Colors.RESET}")
    
    def section(self, title: str):
        """Print section header"""
        print()
        print(f"{Colors.BOLD}{'=' * 80}{Colors.RESET}")
        print(f"{Colors.BOLD}{title}{Colors.RESET}")
        print(f"{Colors.BOLD}{'=' * 80}{Colors.RESET}")
    
    def verify_python_version(self) -> bool:
        """Check Python version"""
        version = sys.version_info
        required = (3, 11)
        
        is_valid = version >= required
        version_str = f"{version.major}.{version.minor}.{version.micro}"
        required_str = f"{required[0]}.{required[1]}+"
        
        return self.check(
            "Python Version",
            is_valid,
            f"Found: {version_str}, Required: {required_str}"
        )
    
    def verify_dependencies(self) -> bool:
        """Check if dependencies are installed"""
        required_packages = [
            ('fastapi', 'FastAPI'),
            ('uvicorn', 'Uvicorn'),
            ('sqlalchemy', 'SQLAlchemy'),
            ('httpx', 'HTTPX'),
            ('transformers', 'Transformers'),
            ('torch', 'PyTorch'),
        ]
        
        all_installed = True
        for package, name in required_packages:
            try:
                __import__(package)
                self.check(name, True)
            except ImportError:
                self.check(name, False, f"Install with: pip install {package}")
                all_installed = False
        
        return all_installed
    
    def verify_directories(self) -> bool:
        """Check if required directories exist"""
        required_dirs = [
            ('static', 'Static files'),
            ('static/pages', 'UI pages'),
            ('static/js', 'JavaScript files'),
            ('static/css', 'CSS files'),
            ('api', 'API endpoints'),
            ('core', 'Core modules'),
            ('workers', 'Background workers'),
            ('database', 'Database module'),
            ('hf-data-engine', 'Data engine'),
            ('cursor-instructions', 'Resources config'),
        ]
        
        all_exist = True
        for dir_path, description in required_dirs:
            full_path = self.workspace / dir_path
            exists = full_path.exists() and full_path.is_dir()
            if not self.check(description, exists, f"Path: {dir_path}"):
                all_exist = False
        
        return all_exist
    
    def verify_files(self) -> bool:
        """Check if required files exist"""
        required_files = [
            ('hf_space_api.py', 'Main API file'),
            ('Dockerfile', 'Docker config'),
            ('requirements_hf.txt', 'Requirements'),
            ('static/index.html', 'Main UI'),
            ('static/js/api-config.js', 'API config'),
            ('cursor-instructions/consolidated_crypto_resources.json', 'Resources'),
        ]
        
        all_exist = True
        for file_path, description in required_files:
            full_path = self.workspace / file_path
            exists = full_path.exists() and full_path.is_file()
            if not self.check(description, exists, f"Path: {file_path}"):
                all_exist = False
        
        return all_exist
    
    def verify_environment(self) -> bool:
        """Check environment variables"""
        # Try to load from .env
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except:
            self.warn("python-dotenv not installed", "Install with: pip install python-dotenv")
        
        # Optional but recommended
        optional_vars = [
            ('HF_TOKEN', 'HuggingFace token'),
            ('ALPHA_VANTAGE_API_KEY', 'Alpha Vantage key'),
            ('MASSIVE_API_KEY', 'Massive.com key'),
        ]
        
        for var, description in optional_vars:
            value = os.getenv(var)
            if value:
                masked = value[:4] + '*' * (len(value) - 8) + value[-4:] if len(value) > 8 else '***'
                self.check(description, True, f"{var}={masked}")
            else:
                self.warn(description, f"{var} not set (optional)")
        
        return True
    
    def verify_resources(self) -> bool:
        """Check consolidated resources file"""
        resources_file = self.workspace / 'cursor-instructions' / 'consolidated_crypto_resources.json'
        
        try:
            with open(resources_file, 'r') as f:
                data = json.load(f)
            
            resources = data.get('resources', [])
            count = len(resources)
            
            self.check(
                "Resource file loaded",
                count > 0,
                f"Found {count} resources"
            )
            
            # Count by category
            categories = {}
            for resource in resources:
                category = resource.get('category', 'unknown')
                categories[category] = categories.get(category, 0) + 1
            
            self.info(f"Resource categories: {len(categories)}")
            for category, count in sorted(categories.items()):
                print(f"   • {category}: {count}")
            
            return True
            
        except Exception as e:
            self.check("Resource file loaded", False, str(e))
            return False
    
    def verify_pages_updated(self) -> bool:
        """Check if pages have API config"""
        pages_dir = self.workspace / 'static' / 'pages'
        
        if not pages_dir.exists():
            return self.check("Pages directory", False)
        
        html_files = list(pages_dir.rglob('*.html'))
        updated_count = 0
        
        for html_file in html_files:
            try:
                with open(html_file, 'r') as f:
                    content = f.read()
                    if 'api-config.js' in content:
                        updated_count += 1
            except:
                pass
        
        percentage = (updated_count / len(html_files) * 100) if html_files else 0
        
        return self.check(
            "Pages have API config",
            percentage >= 80,
            f"{updated_count}/{len(html_files)} pages updated ({percentage:.1f}%)"
        )
    
    def verify_database_setup(self) -> bool:
        """Check database configuration"""
        db_dir = self.workspace / 'data' / 'database'
        
        # Check if directory exists
        if not db_dir.exists():
            db_dir.mkdir(parents=True, exist_ok=True)
            self.info("Created database directory")
        
        return self.check("Database directory", db_dir.exists(), str(db_dir))
    
    def verify_import_structure(self) -> bool:
        """Verify Python import structure"""
        try:
            # Add workspace to path
            sys.path.insert(0, str(self.workspace))
            
            # Try importing key modules
            modules = [
                ('database.db_manager', 'Database manager'),
                ('workers.data_collection_agent', 'Data collection agent'),
                ('core.smart_fallback_manager', 'Smart fallback'),
                ('core.smart_proxy_manager', 'Proxy manager'),
            ]
            
            all_imported = True
            for module_name, description in modules:
                try:
                    __import__(module_name)
                    self.check(description, True, f"Import: {module_name}")
                except ImportError as e:
                    self.check(description, False, str(e))
                    all_imported = False
            
            return all_imported
            
        except Exception as e:
            self.check("Import structure", False, str(e))
            return False
    
    def print_summary(self):
        """Print verification summary"""
        print()
        print(f"{Colors.BOLD}{'=' * 80}{Colors.RESET}")
        print(f"{Colors.BOLD}📊 Verification Summary{Colors.RESET}")
        print(f"{Colors.BOLD}{'=' * 80}{Colors.RESET}")
        
        total = self.checks_passed + self.checks_failed
        pass_rate = (self.checks_passed / total * 100) if total > 0 else 0
        
        print(f"\n{Colors.GREEN}✅ Passed: {self.checks_passed}{Colors.RESET}")
        print(f"{Colors.RED}❌ Failed: {self.checks_failed}{Colors.RESET}")
        print(f"{Colors.YELLOW}⚠️  Warnings: {self.warnings}{Colors.RESET}")
        print(f"\nSuccess Rate: {pass_rate:.1f}%")
        
        print()
        if self.checks_failed == 0:
            print(f"{Colors.GREEN}{Colors.BOLD}✅ Installation verified successfully!{Colors.RESET}")
            print(f"{Colors.GREEN}   You can now run: uvicorn hf_space_api:app --reload{Colors.RESET}")
        else:
            print(f"{Colors.RED}{Colors.BOLD}❌ Installation has issues{Colors.RESET}")
            print(f"{Colors.RED}   Please fix the failed checks above{Colors.RESET}")
        
        print(f"{Colors.BOLD}{'=' * 80}{Colors.RESET}")
    
    def run_all_checks(self):
        """Run all verification checks"""
        print(f"{Colors.BOLD}{'=' * 80}{Colors.RESET}")
        print(f"{Colors.BOLD}🔍 Crypto Intelligence Hub - Installation Verification{Colors.RESET}")
        print(f"{Colors.BOLD}{'=' * 80}{Colors.RESET}")
        
        # 1. Python version
        self.section("1️⃣  Python Environment")
        self.verify_python_version()
        
        # 2. Dependencies
        self.section("2️⃣  Dependencies")
        self.verify_dependencies()
        
        # 3. Directories
        self.section("3️⃣  Directory Structure")
        self.verify_directories()
        
        # 4. Files
        self.section("4️⃣  Required Files")
        self.verify_files()
        
        # 5. Environment
        self.section("5️⃣  Environment Variables")
        self.verify_environment()
        
        # 6. Resources
        self.section("6️⃣  Resource Configuration")
        self.verify_resources()
        
        # 7. Pages
        self.section("7️⃣  UI Pages")
        self.verify_pages_updated()
        
        # 8. Database
        self.section("8️⃣  Database Setup")
        self.verify_database_setup()
        
        # 9. Import structure
        self.section("9️⃣  Python Imports")
        self.verify_import_structure()
        
        # Print summary
        self.print_summary()
        
        # Return exit code
        return 0 if self.checks_failed == 0 else 1


def main():
    """Main verification function"""
    verifier = InstallationVerifier()
    exit_code = verifier.run_all_checks()
    sys.exit(exit_code)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Verification interrupted{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Verification failed: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
