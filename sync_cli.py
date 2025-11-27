#!/usr/bin/env python3
"""
Synchronization CLI Tool
Command-line interface for running GitHub and HuggingFace synchronization
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.services.sync_orchestrator import sync_orchestrator
from backend.services.sync_database_updater import sync_db_updater
from backend.services.github_sync_service import github_sync_service
from backend.services.huggingface_sync_service import huggingface_sync_service
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def run_complete_sync(args):
    """Run complete synchronization"""
    logger.info(f"🚀 Starting complete synchronization...")
    logger.info(f"   Branch: {args.branch}")
    logger.info(f"   Commit message: {args.message}")
    
    result = await sync_orchestrator.run_complete_sync(
        branch=args.branch,
        commit_message=args.message
    )
    
    # Update database if requested
    if args.update_db:
        logger.info(f"💾 Updating database...")
        
        if result.get("hf_models"):
            models_data = result["hf_models"].get("models", [])
            models_result = sync_db_updater.update_models(models_data)
            logger.info(f"   Models: {models_result}")
        
        if result.get("hf_datasets"):
            datasets_data = result["hf_datasets"].get("datasets", [])
            datasets_result = sync_db_updater.update_datasets(datasets_data)
            logger.info(f"   Datasets: {datasets_result}")
        
        # Record history
        sync_db_updater.record_sync_history(result)
    
    # Print summary
    print("\n" + "=" * 80)
    print("SYNCHRONIZATION SUMMARY")
    print("=" * 80)
    print(f"Status: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
    print(f"Duration: {result['duration_seconds']:.2f} seconds")
    
    summary = result.get("summary", {})
    print(f"\nGitHub Commits: {summary.get('github_commits_fetched', 0)}")
    print(f"HF Models: {summary.get('hf_models_synced', 0)}/{summary.get('hf_models_total', 0)}")
    print(f"HF Datasets: {summary.get('hf_datasets_synced', 0)}/{summary.get('hf_datasets_total', 0)}")
    print(f"Errors: {summary.get('total_errors', 0)}")
    print(f"Warnings: {summary.get('total_warnings', 0)}")
    
    if result.get("report_path"):
        print(f"\nReport: {result['report_path']}")
    
    print("=" * 80 + "\n")
    
    return 0 if result["success"] else 1


async def sync_github_only(args):
    """Sync GitHub only"""
    logger.info(f"📥 Syncing GitHub repository...")
    
    result = await github_sync_service.sync_with_github(
        branch=args.branch,
        commit_message=args.message
    )
    
    print(f"\nGitHub Sync: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
    print(f"Operations: {len(result.get('operations', []))}")
    print(f"Errors: {len(result.get('errors', []))}")
    
    return 0 if result["success"] else 1


async def sync_hf_only(args):
    """Sync HuggingFace only"""
    logger.info(f"🤗 Syncing Hugging Face models and datasets...")
    
    result = await huggingface_sync_service.sync_all()
    
    print(f"\nHuggingFace Sync: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
    print(f"Models: {result['models']['successful']}/{result['models']['total']}")
    print(f"Datasets: {result['datasets']['successful']}/{result['datasets']['total']}")
    
    # Update database if requested
    if args.update_db:
        logger.info(f"💾 Updating database...")
        
        models_data = result["models"].get("models", [])
        models_result = sync_db_updater.update_models(models_data)
        logger.info(f"   Models: {models_result}")
        
        datasets_data = result["datasets"].get("datasets", [])
        datasets_result = sync_db_updater.update_datasets(datasets_data)
        logger.info(f"   Datasets: {datasets_result}")
    
    return 0 if result["success"] else 1


async def get_github_commits(args):
    """Get GitHub commits"""
    logger.info(f"📥 Fetching GitHub commits...")
    
    result = await github_sync_service.get_latest_commits(
        branch=args.branch,
        limit=args.limit
    )
    
    if result["success"]:
        print(f"\n✅ Fetched {result['count']} commits:\n")
        for i, commit in enumerate(result["commits"], 1):
            print(f"{i}. {commit['sha'][:8]} - {commit['message']}")
            print(f"   Author: {commit['author']} <{commit['email']}>")
            print(f"   Date: {commit['date']}\n")
    else:
        print(f"\n❌ Failed to fetch commits: {result.get('error')}")
        return 1
    
    return 0


async def get_hf_models(args):
    """Get HuggingFace models"""
    logger.info(f"🤗 Fetching HuggingFace models...")
    
    result = await huggingface_sync_service.sync_models()
    
    if result["success"]:
        print(f"\n✅ Fetched {result['successful']}/{result['total']} models:\n")
        for model_result in result["models"]:
            if model_result["success"]:
                model = model_result["model"]
                print(f"• {model['id']}")
                print(f"  Downloads: {model.get('downloads', 0):,}")
                print(f"  Likes: {model.get('likes', 0)}")
                print(f"  Author: {model.get('author', 'N/A')}\n")
            else:
                print(f"• {model_result['model_id']} - ❌ Error: {model_result.get('error')}\n")
    else:
        print(f"\n❌ Failed to fetch models")
        return 1
    
    return 0


async def get_sync_history(args):
    """Get sync history"""
    logger.info(f"📜 Fetching sync history...")
    
    history = sync_db_updater.get_sync_history(limit=args.limit)
    
    if history:
        print(f"\n✅ Last {len(history)} sync operations:\n")
        for i, entry in enumerate(history, 1):
            status = "✅" if entry["success"] else "❌"
            print(f"{i}. {status} {entry['timestamp']}")
            print(f"   Duration: {entry['duration_seconds']}s")
            print(f"   Models: {entry['models_synced']}, Datasets: {entry['datasets_synced']}")
            print(f"   Errors: {entry['errors_count']}\n")
    else:
        print(f"\nNo sync history found")
    
    return 0


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="GitHub and HuggingFace Synchronization CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run complete sync
  python sync_cli.py sync --branch main --message "Update models"
  
  # Sync GitHub only
  python sync_cli.py github --branch main
  
  # Sync HuggingFace only
  python sync_cli.py hf --update-db
  
  # Get GitHub commits
  python sync_cli.py commits --branch main --limit 5
  
  # Get HuggingFace models
  python sync_cli.py models
  
  # Get sync history
  python sync_cli.py history --limit 10
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Complete sync command
    sync_parser = subparsers.add_parser("sync", help="Run complete synchronization")
    sync_parser.add_argument("--branch", default="main", help="Git branch (default: main)")
    sync_parser.add_argument("--message", default="Sync with Hugging Face models and datasets", 
                           help="Commit message")
    sync_parser.add_argument("--update-db", action="store_true", help="Update database")
    
    # GitHub only sync
    github_parser = subparsers.add_parser("github", help="Sync GitHub only")
    github_parser.add_argument("--branch", default="main", help="Git branch")
    github_parser.add_argument("--message", default="Sync update", help="Commit message")
    
    # HuggingFace only sync
    hf_parser = subparsers.add_parser("hf", help="Sync HuggingFace only")
    hf_parser.add_argument("--update-db", action="store_true", help="Update database")
    
    # Get GitHub commits
    commits_parser = subparsers.add_parser("commits", help="Get GitHub commits")
    commits_parser.add_argument("--branch", default="main", help="Git branch")
    commits_parser.add_argument("--limit", type=int, default=10, help="Number of commits")
    
    # Get HuggingFace models
    models_parser = subparsers.add_parser("models", help="Get HuggingFace models")
    
    # Get sync history
    history_parser = subparsers.add_parser("history", help="Get sync history")
    history_parser.add_argument("--limit", type=int, default=10, help="Number of entries")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute command
    if args.command == "sync":
        return asyncio.run(run_complete_sync(args))
    elif args.command == "github":
        return asyncio.run(sync_github_only(args))
    elif args.command == "hf":
        return asyncio.run(sync_hf_only(args))
    elif args.command == "commits":
        return asyncio.run(get_github_commits(args))
    elif args.command == "models":
        return asyncio.run(get_hf_models(args))
    elif args.command == "history":
        return asyncio.run(get_sync_history(args))
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
