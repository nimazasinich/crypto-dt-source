#!/usr/bin/env python3
"""
Sync Database Updater
Updates database with synchronized models and datasets information
"""

import logging
from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

logger = logging.getLogger(__name__)

Base = declarative_base()


class SyncedModel(Base):
    """Model for storing synced HuggingFace models"""
    __tablename__ = "synced_models"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    model_id = Column(String(255), unique=True, nullable=False, index=True)
    author = Column(String(255))
    pipeline_tag = Column(String(100))
    downloads = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    library_name = Column(String(100))
    created_at = Column(DateTime)
    last_modified = Column(DateTime)
    last_synced = Column(DateTime, default=datetime.utcnow)
    sha = Column(String(100))
    url = Column(Text)
    is_active = Column(Boolean, default=True)


class SyncedDataset(Base):
    """Model for storing synced HuggingFace datasets"""
    __tablename__ = "synced_datasets"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(String(255), unique=True, nullable=False, index=True)
    author = Column(String(255))
    downloads = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    created_at = Column(DateTime)
    last_modified = Column(DateTime)
    last_synced = Column(DateTime, default=datetime.utcnow)
    sha = Column(String(100))
    url = Column(Text)
    is_active = Column(Boolean, default=True)


class SyncHistory(Base):
    """Model for storing sync history"""
    __tablename__ = "sync_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sync_timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    success = Column(Boolean, default=False)
    duration_seconds = Column(Integer)
    models_synced = Column(Integer, default=0)
    datasets_synced = Column(Integer, default=0)
    github_commits_fetched = Column(Integer, default=0)
    errors_count = Column(Integer, default=0)
    report_path = Column(Text)


class SyncDatabaseUpdater:
    """
    Updates database with synchronized data
    """
    
    def __init__(self, database_url: str = None):
        if database_url is None:
            database_url = os.getenv("DATABASE_URL", "sqlite:///./sync_database.db")
        
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        logger.info(f"💾 Sync Database Updater initialized")
        logger.info(f"   Database: {database_url}")
    
    def update_models(self, models_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Update or insert models in database
        
        Args:
            models_data: List of model sync results
            
        Returns:
            Update result
        """
        session = self.SessionLocal()
        updated = 0
        inserted = 0
        errors = 0
        
        try:
            for model_result in models_data:
                if not model_result.get("success"):
                    errors += 1
                    continue
                
                model_data = model_result.get("model", {})
                model_id = model_data.get("id") or model_result.get("model_id")
                
                # Check if model exists
                existing_model = session.query(SyncedModel).filter_by(model_id=model_id).first()
                
                if existing_model:
                    # Update existing model
                    existing_model.author = model_data.get("author", "")
                    existing_model.pipeline_tag = model_data.get("pipeline_tag", "")
                    existing_model.downloads = model_data.get("downloads", 0)
                    existing_model.likes = model_data.get("likes", 0)
                    existing_model.library_name = model_data.get("library_name", "")
                    existing_model.last_modified = self._parse_datetime(model_data.get("last_modified"))
                    existing_model.last_synced = datetime.utcnow()
                    existing_model.sha = model_data.get("sha", "")
                    existing_model.url = model_data.get("url", "")
                    updated += 1
                else:
                    # Insert new model
                    new_model = SyncedModel(
                        model_id=model_id,
                        author=model_data.get("author", ""),
                        pipeline_tag=model_data.get("pipeline_tag", ""),
                        downloads=model_data.get("downloads", 0),
                        likes=model_data.get("likes", 0),
                        library_name=model_data.get("library_name", ""),
                        created_at=self._parse_datetime(model_data.get("created_at")),
                        last_modified=self._parse_datetime(model_data.get("last_modified")),
                        sha=model_data.get("sha", ""),
                        url=model_data.get("url", "")
                    )
                    session.add(new_model)
                    inserted += 1
            
            session.commit()
            logger.info(f"✅ Models updated: {updated}, inserted: {inserted}, errors: {errors}")
            
            return {
                "success": True,
                "updated": updated,
                "inserted": inserted,
                "errors": errors
            }
        
        except Exception as e:
            session.rollback()
            logger.error(f"❌ Failed to update models: {e}")
            return {
                "success": False,
                "error": str(e),
                "updated": 0,
                "inserted": 0,
                "errors": len(models_data)
            }
        finally:
            session.close()
    
    def update_datasets(self, datasets_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Update or insert datasets in database
        
        Args:
            datasets_data: List of dataset sync results
            
        Returns:
            Update result
        """
        session = self.SessionLocal()
        updated = 0
        inserted = 0
        errors = 0
        
        try:
            for dataset_result in datasets_data:
                if not dataset_result.get("success"):
                    errors += 1
                    continue
                
                dataset_data = dataset_result.get("dataset", {})
                dataset_id = dataset_data.get("id") or dataset_result.get("dataset_id")
                
                # Check if dataset exists
                existing_dataset = session.query(SyncedDataset).filter_by(dataset_id=dataset_id).first()
                
                if existing_dataset:
                    # Update existing dataset
                    existing_dataset.author = dataset_data.get("author", "")
                    existing_dataset.downloads = dataset_data.get("downloads", 0)
                    existing_dataset.likes = dataset_data.get("likes", 0)
                    existing_dataset.last_modified = self._parse_datetime(dataset_data.get("last_modified"))
                    existing_dataset.last_synced = datetime.utcnow()
                    existing_dataset.sha = dataset_data.get("sha", "")
                    existing_dataset.url = dataset_data.get("url", "")
                    updated += 1
                else:
                    # Insert new dataset
                    new_dataset = SyncedDataset(
                        dataset_id=dataset_id,
                        author=dataset_data.get("author", ""),
                        downloads=dataset_data.get("downloads", 0),
                        likes=dataset_data.get("likes", 0),
                        created_at=self._parse_datetime(dataset_data.get("created_at")),
                        last_modified=self._parse_datetime(dataset_data.get("last_modified")),
                        sha=dataset_data.get("sha", ""),
                        url=dataset_data.get("url", "")
                    )
                    session.add(new_dataset)
                    inserted += 1
            
            session.commit()
            logger.info(f"✅ Datasets updated: {updated}, inserted: {inserted}, errors: {errors}")
            
            return {
                "success": True,
                "updated": updated,
                "inserted": inserted,
                "errors": errors
            }
        
        except Exception as e:
            session.rollback()
            logger.error(f"❌ Failed to update datasets: {e}")
            return {
                "success": False,
                "error": str(e),
                "updated": 0,
                "inserted": 0,
                "errors": len(datasets_data)
            }
        finally:
            session.close()
    
    def record_sync_history(self, sync_result: Dict[str, Any]) -> bool:
        """
        Record sync operation in history
        
        Args:
            sync_result: Sync result data
            
        Returns:
            Success status
        """
        session = self.SessionLocal()
        
        try:
            summary = sync_result.get("summary", {})
            
            history_entry = SyncHistory(
                success=sync_result.get("success", False),
                duration_seconds=int(sync_result.get("duration_seconds", 0)),
                models_synced=summary.get("hf_models_synced", 0),
                datasets_synced=summary.get("hf_datasets_synced", 0),
                github_commits_fetched=summary.get("github_commits_fetched", 0),
                errors_count=summary.get("total_errors", 0),
                report_path=sync_result.get("report_path", "")
            )
            
            session.add(history_entry)
            session.commit()
            
            logger.info(f"✅ Recorded sync history")
            return True
        
        except Exception as e:
            session.rollback()
            logger.error(f"❌ Failed to record sync history: {e}")
            return False
        finally:
            session.close()
    
    def get_synced_models(self) -> List[Dict[str, Any]]:
        """Get all synced models from database"""
        session = self.SessionLocal()
        
        try:
            models = session.query(SyncedModel).filter_by(is_active=True).all()
            
            return [
                {
                    "model_id": model.model_id,
                    "author": model.author,
                    "pipeline_tag": model.pipeline_tag,
                    "downloads": model.downloads,
                    "likes": model.likes,
                    "last_synced": model.last_synced.isoformat() if model.last_synced else None,
                    "url": model.url
                }
                for model in models
            ]
        finally:
            session.close()
    
    def get_synced_datasets(self) -> List[Dict[str, Any]]:
        """Get all synced datasets from database"""
        session = self.SessionLocal()
        
        try:
            datasets = session.query(SyncedDataset).filter_by(is_active=True).all()
            
            return [
                {
                    "dataset_id": dataset.dataset_id,
                    "author": dataset.author,
                    "downloads": dataset.downloads,
                    "likes": dataset.likes,
                    "last_synced": dataset.last_synced.isoformat() if dataset.last_synced else None,
                    "url": dataset.url
                }
                for dataset in datasets
            ]
        finally:
            session.close()
    
    def get_sync_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get sync history"""
        session = self.SessionLocal()
        
        try:
            history = session.query(SyncHistory).order_by(SyncHistory.sync_timestamp.desc()).limit(limit).all()
            
            return [
                {
                    "timestamp": entry.sync_timestamp.isoformat() if entry.sync_timestamp else None,
                    "success": entry.success,
                    "duration_seconds": entry.duration_seconds,
                    "models_synced": entry.models_synced,
                    "datasets_synced": entry.datasets_synced,
                    "errors_count": entry.errors_count
                }
                for entry in history
            ]
        finally:
            session.close()
    
    def _parse_datetime(self, date_str: str) -> datetime:
        """Parse datetime string"""
        if not date_str:
            return None
        
        try:
            # Try ISO format
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return None


# Global instance
sync_db_updater = SyncDatabaseUpdater()


# Export
__all__ = ["SyncDatabaseUpdater", "sync_db_updater", "SyncedModel", "SyncedDataset", "SyncHistory"]
