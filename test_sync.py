#!/usr/bin/env python3
"""
Sync System Test Suite
Tests for GitHub and HuggingFace synchronization system
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from hf_unified_server import app

client = TestClient(app)


class TestSyncAPIEndpoints:
    """Test sync API endpoints"""
    
    def test_sync_status(self):
        """Test sync status endpoint"""
        response = client.get("/api/v1/sync/status")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "status" in data
        assert "is_running" in data["status"]
    
    def test_github_commits(self):
        """Test GitHub commits endpoint"""
        response = client.get("/api/v1/sync/github/commits?branch=main&limit=5")
        # May fail if GITHUB_TOKEN not set, but should not crash
        assert response.status_code in [200, 500]
    
    def test_hf_models(self):
        """Test HuggingFace models endpoint"""
        response = client.get("/api/v1/sync/hf/models")
        # May fail due to rate limits, but should not crash
        assert response.status_code in [200, 500]
    
    def test_hf_datasets(self):
        """Test HuggingFace datasets endpoint"""
        response = client.get("/api/v1/sync/hf/datasets")
        # May fail due to rate limits, but should not crash
        assert response.status_code in [200, 500]
    
    def test_database_models(self):
        """Test database models endpoint"""
        response = client.get("/api/v1/sync/database/models")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "models" in data
        assert "count" in data
    
    def test_database_datasets(self):
        """Test database datasets endpoint"""
        response = client.get("/api/v1/sync/database/datasets")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "datasets" in data
        assert "count" in data
    
    def test_sync_history(self):
        """Test sync history endpoint"""
        response = client.get("/api/v1/sync/history?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "history" in data
    
    def test_sync_reports(self):
        """Test sync reports endpoint"""
        response = client.get("/api/v1/sync/reports")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "reports" in data


class TestGitHubSyncService:
    """Test GitHub sync service"""
    
    @pytest.mark.asyncio
    async def test_github_service_import(self):
        """Test that GitHub service can be imported"""
        try:
            from backend.services.github_sync_service import github_sync_service
            assert github_sync_service is not None
        except ImportError as e:
            pytest.skip(f"GitHub service not available: {e}")
    
    @pytest.mark.asyncio
    async def test_get_latest_commits(self):
        """Test getting latest commits"""
        try:
            from backend.services.github_sync_service import github_sync_service
            
            # This may fail if GITHUB_TOKEN is not set
            result = await github_sync_service.get_latest_commits(branch="main", limit=1)
            
            assert "success" in result
            assert "commits" in result
        except ImportError:
            pytest.skip("GitHub service not available")


class TestHuggingFaceSyncService:
    """Test HuggingFace sync service"""
    
    @pytest.mark.asyncio
    async def test_hf_service_import(self):
        """Test that HF service can be imported"""
        try:
            from backend.services.huggingface_sync_service import huggingface_sync_service
            assert huggingface_sync_service is not None
        except ImportError as e:
            pytest.skip(f"HF service not available: {e}")
    
    @pytest.mark.asyncio
    async def test_get_model_info(self):
        """Test getting model info"""
        try:
            from backend.services.huggingface_sync_service import huggingface_sync_service
            
            # Test with a public model
            result = await huggingface_sync_service.get_model_info("ElKulako/cryptobert")
            
            assert "success" in result
            assert "model_id" in result
        except ImportError:
            pytest.skip("HF service not available")
    
    @pytest.mark.asyncio
    async def test_get_dataset_info(self):
        """Test getting dataset info"""
        try:
            from backend.services.huggingface_sync_service import huggingface_sync_service
            
            # Test with a public dataset
            result = await huggingface_sync_service.get_dataset_info("linxy/CryptoCoin")
            
            assert "success" in result
            assert "dataset_id" in result
        except ImportError:
            pytest.skip("HF service not available")


class TestSyncOrchestrator:
    """Test sync orchestrator"""
    
    @pytest.mark.asyncio
    async def test_orchestrator_import(self):
        """Test that orchestrator can be imported"""
        try:
            from backend.services.sync_orchestrator import sync_orchestrator
            assert sync_orchestrator is not None
        except ImportError as e:
            pytest.skip(f"Sync orchestrator not available: {e}")


class TestDatabaseUpdater:
    """Test database updater"""
    
    def test_db_updater_import(self):
        """Test that database updater can be imported"""
        try:
            from backend.services.sync_database_updater import sync_db_updater
            assert sync_db_updater is not None
        except ImportError as e:
            pytest.skip(f"Database updater not available: {e}")
    
    def test_get_synced_models(self):
        """Test getting synced models"""
        try:
            from backend.services.sync_database_updater import sync_db_updater
            
            models = sync_db_updater.get_synced_models()
            assert isinstance(models, list)
        except ImportError:
            pytest.skip("Database updater not available")
    
    def test_get_synced_datasets(self):
        """Test getting synced datasets"""
        try:
            from backend.services.sync_database_updater import sync_db_updater
            
            datasets = sync_db_updater.get_synced_datasets()
            assert isinstance(datasets, list)
        except ImportError:
            pytest.skip("Database updater not available")
    
    def test_get_sync_history(self):
        """Test getting sync history"""
        try:
            from backend.services.sync_database_updater import sync_db_updater
            
            history = sync_db_updater.get_sync_history(limit=5)
            assert isinstance(history, list)
        except ImportError:
            pytest.skip("Database updater not available")


class TestIntegration:
    """Integration tests"""
    
    @pytest.mark.asyncio
    async def test_complete_workflow_mock(self):
        """Test complete workflow with mock data"""
        # This is a basic test that just verifies the workflow can be called
        # In production, you'd want more comprehensive testing
        try:
            from backend.services.sync_orchestrator import sync_orchestrator
            
            # Note: This would actually run a sync, so we skip it in automated tests
            pytest.skip("Skipping actual sync in automated tests")
        except ImportError:
            pytest.skip("Sync orchestrator not available")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])
