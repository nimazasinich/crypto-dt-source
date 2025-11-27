#!/usr/bin/env python3
"""
GitHub Synchronization Service
Handles GitHub repository synchronization and commit tracking
"""

import os
import logging
import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime
import subprocess
import asyncio

logger = logging.getLogger(__name__)


class GitHubSyncService:
    """
    Service for synchronizing with GitHub repository
    """
    
    def __init__(self):
        self.github_token = os.getenv("GITHUB_TOKEN", "")
        self.github_repo = os.getenv("GITHUB_REPO", "")  # Format: "owner/repo"
        self.base_url = "https://api.github.com"
        self.timeout = 30.0
        
        if not self.github_token:
            logger.warning("⚠️  GITHUB_TOKEN not set. GitHub sync will be limited.")
        
        if not self.github_repo:
            logger.warning("⚠️  GITHUB_REPO not set. Using default repository.")
            self.github_repo = "default-owner/default-repo"
        
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "CryptoDataHub-Sync/1.0"
        }
        
        if self.github_token:
            self.headers["Authorization"] = f"token {self.github_token}"
        
        logger.info(f"🔧 GitHub Sync Service initialized")
        logger.info(f"   Repository: {self.github_repo}")
        logger.info(f"   Auth: {'✅ Token configured' if self.github_token else '❌ No token'}")
    
    async def get_latest_commits(
        self,
        branch: str = "main",
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get latest commits from GitHub repository
        
        Args:
            branch: Branch name (default: main)
            limit: Number of commits to fetch
            
        Returns:
            Dict with commits and metadata
        """
        try:
            url = f"{self.base_url}/repos/{self.github_repo}/commits"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params={
                        "sha": branch,
                        "per_page": limit
                    }
                )
                response.raise_for_status()
                commits = response.json()
            
            # Parse commits
            parsed_commits = []
            for commit in commits:
                parsed_commits.append({
                    "sha": commit["sha"],
                    "message": commit["commit"]["message"],
                    "author": commit["commit"]["author"]["name"],
                    "email": commit["commit"]["author"]["email"],
                    "date": commit["commit"]["author"]["date"],
                    "url": commit["html_url"]
                })
            
            logger.info(f"✅ Fetched {len(parsed_commits)} commits from GitHub")
            
            return {
                "success": True,
                "commits": parsed_commits,
                "count": len(parsed_commits),
                "branch": branch,
                "repository": self.github_repo,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ GitHub API error: {e.response.status_code} - {e.response.text}")
            return {
                "success": False,
                "error": f"GitHub API error: {e.response.status_code}",
                "commits": [],
                "count": 0
            }
        except Exception as e:
            logger.error(f"❌ Failed to fetch commits: {e}")
            return {
                "success": False,
                "error": str(e),
                "commits": [],
                "count": 0
            }
    
    async def get_latest_commit(self, branch: str = "main") -> Optional[Dict[str, Any]]:
        """
        Get the most recent commit
        
        Args:
            branch: Branch name
            
        Returns:
            Latest commit info or None
        """
        result = await self.get_latest_commits(branch=branch, limit=1)
        
        if result["success"] and result["commits"]:
            return result["commits"][0]
        
        return None
    
    async def check_for_new_commits(
        self,
        last_known_sha: str,
        branch: str = "main"
    ) -> Dict[str, Any]:
        """
        Check if there are new commits since the last known commit
        
        Args:
            last_known_sha: SHA of the last known commit
            branch: Branch name
            
        Returns:
            Dict with new commits info
        """
        result = await self.get_latest_commits(branch=branch, limit=50)
        
        if not result["success"]:
            return {
                "has_new_commits": False,
                "new_commits": [],
                "count": 0,
                "error": result.get("error")
            }
        
        # Find new commits
        new_commits = []
        for commit in result["commits"]:
            if commit["sha"] == last_known_sha:
                break
            new_commits.append(commit)
        
        return {
            "has_new_commits": len(new_commits) > 0,
            "new_commits": new_commits,
            "count": len(new_commits),
            "latest_sha": result["commits"][0]["sha"] if result["commits"] else None
        }
    
    def git_pull(self, branch: str = "main") -> Dict[str, Any]:
        """
        Pull latest changes from GitHub repository
        
        Args:
            branch: Branch name
            
        Returns:
            Result of git pull operation
        """
        try:
            # Check if we're in a git repository
            check_result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                capture_output=True,
                text=True,
                cwd="/workspace"
            )
            
            if check_result.returncode != 0:
                return {
                    "success": False,
                    "error": "Not a git repository"
                }
            
            # Git pull
            result = subprocess.run(
                ["git", "pull", "origin", branch],
                capture_output=True,
                text=True,
                cwd="/workspace"
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Git pull successful: {result.stdout}")
                return {
                    "success": True,
                    "output": result.stdout,
                    "branch": branch
                }
            else:
                logger.error(f"❌ Git pull failed: {result.stderr}")
                return {
                    "success": False,
                    "error": result.stderr,
                    "branch": branch
                }
        
        except Exception as e:
            logger.error(f"❌ Git pull exception: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def git_add_all(self) -> Dict[str, Any]:
        """
        Stage all changes for commit
        
        Returns:
            Result of git add operation
        """
        try:
            result = subprocess.run(
                ["git", "add", "."],
                capture_output=True,
                text=True,
                cwd="/workspace"
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Git add successful")
                return {
                    "success": True,
                    "output": result.stdout
                }
            else:
                logger.error(f"❌ Git add failed: {result.stderr}")
                return {
                    "success": False,
                    "error": result.stderr
                }
        
        except Exception as e:
            logger.error(f"❌ Git add exception: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def git_commit(self, message: str) -> Dict[str, Any]:
        """
        Commit staged changes
        
        Args:
            message: Commit message
            
        Returns:
            Result of git commit operation
        """
        try:
            result = subprocess.run(
                ["git", "commit", "-m", message],
                capture_output=True,
                text=True,
                cwd="/workspace"
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Git commit successful: {message}")
                return {
                    "success": True,
                    "output": result.stdout,
                    "message": message
                }
            else:
                # Check if there's nothing to commit
                if "nothing to commit" in result.stdout.lower() or "nothing to commit" in result.stderr.lower():
                    logger.info(f"ℹ️  Nothing to commit")
                    return {
                        "success": True,
                        "output": result.stdout or result.stderr,
                        "message": "Nothing to commit",
                        "nothing_to_commit": True
                    }
                
                logger.error(f"❌ Git commit failed: {result.stderr}")
                return {
                    "success": False,
                    "error": result.stderr
                }
        
        except Exception as e:
            logger.error(f"❌ Git commit exception: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def git_push(self, branch: str = "main") -> Dict[str, Any]:
        """
        Push commits to GitHub repository
        
        Args:
            branch: Branch name
            
        Returns:
            Result of git push operation
        """
        try:
            result = subprocess.run(
                ["git", "push", "origin", branch],
                capture_output=True,
                text=True,
                cwd="/workspace"
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Git push successful: {result.stdout}")
                return {
                    "success": True,
                    "output": result.stdout,
                    "branch": branch
                }
            else:
                logger.error(f"❌ Git push failed: {result.stderr}")
                return {
                    "success": False,
                    "error": result.stderr,
                    "branch": branch
                }
        
        except Exception as e:
            logger.error(f"❌ Git push exception: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def sync_with_github(
        self,
        branch: str = "main",
        commit_message: str = "Sync with Hugging Face models and datasets"
    ) -> Dict[str, Any]:
        """
        Complete synchronization with GitHub
        
        Args:
            branch: Branch name
            commit_message: Commit message
            
        Returns:
            Sync result with all operations
        """
        sync_result = {
            "success": False,
            "operations": [],
            "errors": [],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # 1. Get latest commits
        logger.info(f"📥 Fetching latest commits from GitHub...")
        commits_result = await self.get_latest_commits(branch=branch, limit=5)
        sync_result["operations"].append({
            "operation": "fetch_commits",
            "success": commits_result["success"],
            "commits": commits_result.get("commits", [])
        })
        
        if not commits_result["success"]:
            sync_result["errors"].append(f"Failed to fetch commits: {commits_result.get('error')}")
        
        # 2. Pull latest changes
        logger.info(f"📥 Pulling latest changes from GitHub...")
        pull_result = self.git_pull(branch)
        sync_result["operations"].append({
            "operation": "git_pull",
            "success": pull_result["success"],
            "output": pull_result.get("output", pull_result.get("error"))
        })
        
        if not pull_result["success"]:
            sync_result["errors"].append(f"Git pull failed: {pull_result.get('error')}")
        
        # 3. Add changes
        logger.info(f"📝 Staging changes...")
        add_result = self.git_add_all()
        sync_result["operations"].append({
            "operation": "git_add",
            "success": add_result["success"]
        })
        
        if not add_result["success"]:
            sync_result["errors"].append(f"Git add failed: {add_result.get('error')}")
        
        # 4. Commit changes
        logger.info(f"💾 Committing changes...")
        commit_result = self.git_commit(commit_message)
        sync_result["operations"].append({
            "operation": "git_commit",
            "success": commit_result["success"],
            "message": commit_message,
            "nothing_to_commit": commit_result.get("nothing_to_commit", False)
        })
        
        if not commit_result["success"] and not commit_result.get("nothing_to_commit"):
            sync_result["errors"].append(f"Git commit failed: {commit_result.get('error')}")
        
        # 5. Push changes (only if there was something to commit)
        if commit_result["success"] and not commit_result.get("nothing_to_commit"):
            logger.info(f"📤 Pushing changes to GitHub...")
            push_result = self.git_push(branch)
            sync_result["operations"].append({
                "operation": "git_push",
                "success": push_result["success"],
                "output": push_result.get("output", push_result.get("error"))
            })
            
            if not push_result["success"]:
                sync_result["errors"].append(f"Git push failed: {push_result.get('error')}")
        
        # Determine overall success
        sync_result["success"] = len(sync_result["errors"]) == 0
        
        if sync_result["success"]:
            logger.info(f"✅ GitHub synchronization completed successfully")
        else:
            logger.error(f"❌ GitHub synchronization completed with errors: {sync_result['errors']}")
        
        return sync_result


# Global instance
github_sync_service = GitHubSyncService()


# Export
__all__ = ["GitHubSyncService", "github_sync_service"]
