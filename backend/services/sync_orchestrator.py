#!/usr/bin/env python3
"""
Sync Orchestrator - Complete Synchronization Service
Coordinates GitHub and Hugging Face synchronization with reporting
"""

import os
import logging
from typing import Dict, Any
from datetime import datetime
from pathlib import Path

from backend.services.github_sync_service import github_sync_service
from backend.services.huggingface_sync_service import huggingface_sync_service

logger = logging.getLogger(__name__)


class SyncOrchestrator:
    """
    Orchestrates complete synchronization between GitHub and Hugging Face
    """
    
    def __init__(self):
        self.github_service = github_sync_service
        self.hf_service = huggingface_sync_service
        self.report_dir = "/workspace/sync_reports"
        
        # Create report directory
        Path(self.report_dir).mkdir(parents=True, exist_ok=True)
        
        logger.info(f"🎯 Sync Orchestrator initialized")
        logger.info(f"   Report directory: {self.report_dir}")
    
    async def run_complete_sync(
        self,
        branch: str = "main",
        commit_message: str = "Sync with Hugging Face models and datasets"
    ) -> Dict[str, Any]:
        """
        Run complete synchronization workflow
        
        Args:
            branch: Git branch to sync
            commit_message: Commit message for changes
            
        Returns:
            Complete sync result with all operations
        """
        logger.info(f"🚀 Starting complete synchronization workflow...")
        
        start_time = datetime.utcnow()
        
        sync_result = {
            "success": False,
            "start_time": start_time.isoformat(),
            "operations": [],
            "errors": [],
            "warnings": []
        }
        
        # 1. Fetch GitHub commits
        logger.info(f"📥 Step 1: Fetching GitHub commits...")
        github_commits = await self.github_service.get_latest_commits(branch=branch, limit=10)
        sync_result["github_commits"] = github_commits
        
        if not github_commits["success"]:
            sync_result["errors"].append(f"Failed to fetch GitHub commits: {github_commits.get('error')}")
            sync_result["warnings"].append("Continuing with Hugging Face sync despite GitHub error")
        else:
            logger.info(f"✅ Fetched {github_commits['count']} commits from GitHub")
        
        # 2. Sync Hugging Face models
        logger.info(f"🤗 Step 2: Syncing Hugging Face models...")
        hf_models_result = await self.hf_service.sync_models()
        sync_result["hf_models"] = hf_models_result
        
        if not hf_models_result["success"]:
            sync_result["errors"].append(f"Failed to sync all HF models: {hf_models_result['failed']} failed")
        else:
            logger.info(f"✅ Synced {hf_models_result['successful']}/{hf_models_result['total']} HF models")
        
        # 3. Sync Hugging Face datasets
        logger.info(f"📊 Step 3: Syncing Hugging Face datasets...")
        hf_datasets_result = await self.hf_service.sync_datasets()
        sync_result["hf_datasets"] = hf_datasets_result
        
        if not hf_datasets_result["success"]:
            sync_result["errors"].append(f"Failed to sync all HF datasets: {hf_datasets_result['failed']} failed")
        else:
            logger.info(f"✅ Synced {hf_datasets_result['successful']}/{hf_datasets_result['total']} HF datasets")
        
        # 4. Git operations (pull, add, commit, push)
        logger.info(f"📝 Step 4: Performing Git operations...")
        git_result = await self.github_service.sync_with_github(
            branch=branch,
            commit_message=commit_message
        )
        sync_result["git_operations"] = git_result
        
        if not git_result["success"]:
            sync_result["errors"].extend(git_result.get("errors", []))
        else:
            logger.info(f"✅ Git operations completed successfully")
        
        # Calculate duration
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        sync_result["end_time"] = end_time.isoformat()
        sync_result["duration_seconds"] = duration
        sync_result["success"] = len(sync_result["errors"]) == 0
        
        # Summary
        sync_result["summary"] = {
            "github_commits_fetched": github_commits.get("count", 0),
            "hf_models_synced": hf_models_result.get("successful", 0),
            "hf_models_total": hf_models_result.get("total", 0),
            "hf_datasets_synced": hf_datasets_result.get("successful", 0),
            "hf_datasets_total": hf_datasets_result.get("total", 0),
            "git_operations_completed": len(git_result.get("operations", [])),
            "total_errors": len(sync_result["errors"]),
            "total_warnings": len(sync_result["warnings"])
        }
        
        # Generate report
        report_path = self.generate_report(sync_result)
        sync_result["report_path"] = report_path
        
        if sync_result["success"]:
            logger.info(f"✅ Complete synchronization finished successfully in {duration:.2f}s")
        else:
            logger.error(f"❌ Complete synchronization finished with {len(sync_result['errors'])} errors in {duration:.2f}s")
        
        return sync_result
    
    def generate_report(self, sync_result: Dict[str, Any]) -> str:
        """
        Generate detailed synchronization report
        
        Args:
            sync_result: Sync result data
            
        Returns:
            Path to report file
        """
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            report_filename = f"sync_report_{timestamp}.txt"
            report_path = os.path.join(self.report_dir, report_filename)
            
            with open(report_path, 'w') as f:
                f.write("=" * 80 + "\n")
                f.write("SYNCHRONIZATION REPORT\n")
                f.write("=" * 80 + "\n\n")
                
                # Header
                f.write(f"Report Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
                f.write(f"Status: {'✅ SUCCESS' if sync_result['success'] else '❌ FAILED'}\n")
                f.write(f"Duration: {sync_result['duration_seconds']:.2f} seconds\n")
                f.write("\n")
                
                # Summary
                f.write("-" * 80 + "\n")
                f.write("SUMMARY\n")
                f.write("-" * 80 + "\n")
                summary = sync_result.get("summary", {})
                f.write(f"GitHub Commits Fetched: {summary.get('github_commits_fetched', 0)}\n")
                f.write(f"HF Models Synced: {summary.get('hf_models_synced', 0)}/{summary.get('hf_models_total', 0)}\n")
                f.write(f"HF Datasets Synced: {summary.get('hf_datasets_synced', 0)}/{summary.get('hf_datasets_total', 0)}\n")
                f.write(f"Git Operations: {summary.get('git_operations_completed', 0)}\n")
                f.write(f"Total Errors: {summary.get('total_errors', 0)}\n")
                f.write(f"Total Warnings: {summary.get('total_warnings', 0)}\n")
                f.write("\n")
                
                # GitHub Commits
                f.write("-" * 80 + "\n")
                f.write("GITHUB COMMITS\n")
                f.write("-" * 80 + "\n")
                github_commits = sync_result.get("github_commits", {})
                if github_commits.get("success"):
                    commits = github_commits.get("commits", [])
                    if commits:
                        for i, commit in enumerate(commits, 1):
                            f.write(f"\n{i}. Commit: {commit['sha'][:8]}\n")
                            f.write(f"   Author: {commit['author']} <{commit['email']}>\n")
                            f.write(f"   Date: {commit['date']}\n")
                            f.write(f"   Message: {commit['message']}\n")
                    else:
                        f.write("No commits found.\n")
                else:
                    f.write(f"❌ Error: {github_commits.get('error', 'Unknown error')}\n")
                f.write("\n")
                
                # HuggingFace Models
                f.write("-" * 80 + "\n")
                f.write("HUGGINGFACE MODELS\n")
                f.write("-" * 80 + "\n")
                hf_models = sync_result.get("hf_models", {})
                models = hf_models.get("models", [])
                for i, model_result in enumerate(models, 1):
                    status = "✅" if model_result["success"] else "❌"
                    f.write(f"\n{i}. {status} {model_result['model_id']}\n")
                    if model_result["success"]:
                        model = model_result["model"]
                        f.write(f"   Author: {model.get('author', 'N/A')}\n")
                        f.write(f"   Downloads: {model.get('downloads', 0):,}\n")
                        f.write(f"   Likes: {model.get('likes', 0)}\n")
                        f.write(f"   Last Modified: {model.get('last_modified', 'N/A')}\n")
                    else:
                        f.write(f"   Error: {model_result.get('error', 'Unknown error')}\n")
                f.write("\n")
                
                # HuggingFace Datasets
                f.write("-" * 80 + "\n")
                f.write("HUGGINGFACE DATASETS\n")
                f.write("-" * 80 + "\n")
                hf_datasets = sync_result.get("hf_datasets", {})
                datasets = hf_datasets.get("datasets", [])
                for i, dataset_result in enumerate(datasets, 1):
                    status = "✅" if dataset_result["success"] else "❌"
                    f.write(f"\n{i}. {status} {dataset_result['dataset_id']}\n")
                    if dataset_result["success"]:
                        dataset = dataset_result["dataset"]
                        f.write(f"   Author: {dataset.get('author', 'N/A')}\n")
                        f.write(f"   Downloads: {dataset.get('downloads', 0):,}\n")
                        f.write(f"   Likes: {dataset.get('likes', 0)}\n")
                        f.write(f"   Last Modified: {dataset.get('last_modified', 'N/A')}\n")
                    else:
                        f.write(f"   Error: {dataset_result.get('error', 'Unknown error')}\n")
                f.write("\n")
                
                # Git Operations
                f.write("-" * 80 + "\n")
                f.write("GIT OPERATIONS\n")
                f.write("-" * 80 + "\n")
                git_ops = sync_result.get("git_operations", {})
                operations = git_ops.get("operations", [])
                for i, op in enumerate(operations, 1):
                    status = "✅" if op["success"] else "❌"
                    f.write(f"\n{i}. {status} {op['operation']}\n")
                    if "output" in op and op["output"]:
                        f.write(f"   Output: {op['output'][:200]}\n")
                    if op.get("nothing_to_commit"):
                        f.write(f"   Note: Nothing to commit (clean working directory)\n")
                f.write("\n")
                
                # Errors
                if sync_result["errors"]:
                    f.write("-" * 80 + "\n")
                    f.write("ERRORS\n")
                    f.write("-" * 80 + "\n")
                    for i, error in enumerate(sync_result["errors"], 1):
                        f.write(f"{i}. {error}\n")
                    f.write("\n")
                
                # Warnings
                if sync_result["warnings"]:
                    f.write("-" * 80 + "\n")
                    f.write("WARNINGS\n")
                    f.write("-" * 80 + "\n")
                    for i, warning in enumerate(sync_result["warnings"], 1):
                        f.write(f"{i}. {warning}\n")
                    f.write("\n")
                
                # Footer
                f.write("=" * 80 + "\n")
                f.write("END OF REPORT\n")
                f.write("=" * 80 + "\n")
            
            logger.info(f"✅ Generated sync report: {report_path}")
            return report_path
        
        except Exception as e:
            logger.error(f"❌ Failed to generate report: {e}")
            return ""


# Global instance
sync_orchestrator = SyncOrchestrator()


# Export
__all__ = ["SyncOrchestrator", "sync_orchestrator"]
