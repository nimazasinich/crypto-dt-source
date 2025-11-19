#!/usr/bin/env python3
"""
Script to organize and archive extra files in the project root
"""

import os
import shutil
from pathlib import Path

# Define root directory
ROOT = Path(".")

# Files that should stay in root (essential files)
ESSENTIAL_FILES = {
    "app.py",
    "Dockerfile",
    "requirements_hf.txt",
    "requirements.txt",
    "README.md",
    "config.py",
    "ai_models.py",
    "api_server_extended.py",
    "hf_unified_server.py",
    "docker-compose.yml",
    "pyproject.toml",
    "package.json",
    ".gitignore",
    ".dockerignore",
}

# Files to archive by category
ARCHIVE_MAP = {
    "archive/html/": [
        "admin_advanced.html",
        "admin.html",
        "admin.html.optimized",
        "complete_dashboard.html",
        "dashboard.html",
        "hf_console.html",
        "index.html",
        "pool_management.html",
        "simple_overview.html",
        "unified_dashboard.html",
    ],
    "archive/docs/": [
        "ADMIN_DASHBOARD_COMPLETE.md",
        "ADMIN_ROUTING_UPDATE_FA.md",
        "APL_FINAL_SUMMARY.md",
        "APL_USAGE_GUIDE.md",
        "APP_DEPLOYMENT_GUIDE.md",
        "APP_IMPLEMENTATION_SUMMARY.md",
        "APP_PY_UPDATE_SUMMARY_FA.md",
        "AUDIT_COMPLETION_REPORT.md",
        "CHANGELOG.md",
        "CRYPTOBERT_QUICK_REFERENCE.md",
        "DEPENDENCY_FIX_SUMMARY.md",
        "DEPLOYMENT_CHECK_REPORT.md",
        "DEPLOYMENT_MASTER_GUIDE.md",
        "FINAL_SUMMARY.md",
        "FINAL_UI_ROUTING_REPORT.md",
        "FIX_SUMMARY_LOGGING_SETUP.md",
        "HEYSTIVE_README_FA.md",
        "HF_DOCKER_FIX.md",
        "HUGGINGFACE_API_GUIDE.md",
        "HUGGINGFACE_DEPLOYMENT_PROMPT.md",
        "HUGGINGFACE_DIAGNOSTIC_GUIDE.md",
        "IMPLEMENTATION_FIXES.md",
        "IMPLEMENTATION_SUMMARY_FA.md",
        "MODELS_AS_DATA_SOURCES.md",
        "PROFESSIONAL_DASHBOARD_GUIDE.md",
        "PROVIDER_AUTO_DISCOVERY_REPORT.md",
        "PROVIDERS_CONFIG_UPDATE_FA.md",
        "QUICK_REFERENCE_GUIDE.md",
        "QUICK_START.md",
        "QUICK_START_ADMIN.md",
        "QUICK_START_ADVANCED_UI.md",
        "QUICK_START_PROFESSIONAL.md",
        "QUICK_TEST_GUIDE.md",
        "README_HF_INTEGRATION.md",
        "README_HUGGINGFACE_API.md",
        "ROUTING_CONNECTION_SUMMARY_FA.md",
        "UI_ROUTING_SUMMARY_FA.md",
    ],
    "archive/scripts/": [
        "diagnostic.sh",
        "test.sh",
        "TEST_COMMANDS.sh",
        "TEST_ENDPOINTS.sh",
        "verify_deployment.sh",
        "start_crypto_bank.sh",
        "api-monitor.js",
        "failover-manager.js",
    ],
    "archive/servers/": [
        "app_gradio.py",
        "api_dashboard_backend.py",
        "api_loader.py",
        "enhanced_server.py",
        "gradio_ultimate_dashboard.py",
        "production_server.py",
        "real_server.py",
        "simple_server.py",
    ],
    "archive/reports/": [
        "PROVIDER_AUTO_DISCOVERY_REPORT.json",
        "providers_config_extended.backup.json",
        "DASHBOARD_READY.txt",
        "START.txt",
        "VIEW_IMPROVED_DASHBOARD.txt",
    ],
    "archive/": [
        "Dockerfile.zip",
        "requirements_gradio.txt",
        "collectors.py",
        "database.py",
        "monitor.py",
        "scheduler.py",
        "log_manager.py",
        "auto_provider_loader.py",
        "provider_fetch_helper.py",
        "provider_manager.py",
        "provider_validator.py",
        "import_resources.py",
        "test_aggregator.py",
        "test_crypto_bank.py",
        "test_integration.py",
        "test_providers_real.py",
        "test_routing.py",
        "verify_implementation.py",
        "all_apis_merged_2025.json",
        "ultimate_crypto_pipeline_2025_NZasinich.json",
    ],
}

def main():
    """Main function to organize files"""
    moved_count = 0
    skipped_count = 0
    
    print("🚀 Starting file organization...")
    print(f"📁 Root directory: {ROOT.absolute()}\n")
    
    # Create archive directories
    for archive_dir in ARCHIVE_MAP.keys():
        archive_path = ROOT / archive_dir
        archive_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {archive_dir}")
    
    # Move files
    for archive_dir, files in ARCHIVE_MAP.items():
        archive_path = ROOT / archive_dir
        
        for filename in files:
            source = ROOT / filename
            
            if not source.exists():
                print(f"⚠️  File not found: {filename}")
                skipped_count += 1
                continue
            
            # Skip if file is essential
            if filename in ESSENTIAL_FILES:
                print(f"⏭️  Skipping essential file: {filename}")
                skipped_count += 1
                continue
            
            dest = archive_path / filename
            
            try:
                # Create parent directory if needed
                dest.parent.mkdir(parents=True, exist_ok=True)
                
                # Move file
                shutil.move(str(source), str(dest))
                print(f"✅ Moved: {filename} → {archive_dir}")
                moved_count += 1
            except Exception as e:
                print(f"❌ Error moving {filename}: {e}")
                skipped_count += 1
    
    print(f"\n📊 Summary:")
    print(f"   ✅ Files moved: {moved_count}")
    print(f"   ⏭️  Files skipped: {skipped_count}")
    print(f"\n✨ File organization complete!")

if __name__ == "__main__":
    main()

