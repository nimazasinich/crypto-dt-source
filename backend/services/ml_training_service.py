#!/usr/bin/env python3
"""
ML Training Service
===================
سرویس آموزش مدل‌های یادگیری ماشین با قابلیت پیگیری پیشرفت و ذخیره checkpoint
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
import uuid
import logging
import json

from database.models import (
    Base, MLTrainingJob, TrainingStep, TrainingStatus
)

logger = logging.getLogger(__name__)


class MLTrainingService:
    """سرویس اصلی آموزش مدل‌های ML"""

    def __init__(self, db_session: Session):
        """
        Initialize the ML training service.
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session

    def start_training(
        self,
        model_name: str,
        training_data_start: datetime,
        training_data_end: datetime,
        batch_size: int = 32,
        learning_rate: Optional[float] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Start training a model.
        
        Args:
            model_name: Name of the model to train
            training_data_start: Start date for training data
            training_data_end: End date for training data
            batch_size: Training batch size
            learning_rate: Learning rate (optional)
            config: Additional training configuration
        
        Returns:
            Dict containing training job details
        """
        try:
            # Generate job ID
            job_id = f"TR-{uuid.uuid4().hex[:12].upper()}"

            # Create training job
            job = MLTrainingJob(
                job_id=job_id,
                model_name=model_name,
                model_version="1.0.0",
                status=TrainingStatus.PENDING,
                training_data_start=training_data_start,
                training_data_end=training_data_end,
                batch_size=batch_size,
                learning_rate=learning_rate or 0.001,
                config=json.dumps(config) if config else None
            )

            self.db.add(job)
            self.db.commit()
            self.db.refresh(job)

            logger.info(f"Created training job {job_id} for model {model_name}")

            # In production, this would start training in background
            # For now, we just return the job details
            return self._job_to_dict(job)

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error starting training: {e}", exc_info=True)
            raise

    def execute_training_step(
        self,
        job_id: str,
        step_number: int,
        loss: Optional[float] = None,
        accuracy: Optional[float] = None,
        learning_rate: Optional[float] = None,
        metrics: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a single training step.
        
        Args:
            job_id: Training job ID
            step_number: Step number
            loss: Training loss
            accuracy: Training accuracy
            learning_rate: Current learning rate
            metrics: Additional metrics
        
        Returns:
            Dict containing step details
        """
        try:
            # Get training job
            job = self.db.query(MLTrainingJob).filter(
                MLTrainingJob.job_id == job_id
            ).first()

            if not job:
                raise ValueError(f"Training job {job_id} not found")

            if job.status != TrainingStatus.RUNNING:
                raise ValueError(f"Training job {job_id} is not in RUNNING status")

            # Create training step
            step = TrainingStep(
                job_id=job_id,
                step_number=step_number,
                loss=loss,
                accuracy=accuracy,
                learning_rate=learning_rate,
                metrics=json.dumps(metrics) if metrics else None
            )

            self.db.add(step)

            # Update job
            job.current_step = step_number
            if loss is not None:
                job.loss = loss
            if accuracy is not None:
                job.accuracy = accuracy
            if learning_rate is not None:
                job.learning_rate = learning_rate

            self.db.commit()
            self.db.refresh(step)

            logger.info(f"Training step {step_number} executed for job {job_id}")

            return self._step_to_dict(step)

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error executing training step: {e}", exc_info=True)
            raise

    def get_training_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get the current training status.
        
        Args:
            job_id: Training job ID
        
        Returns:
            Dict containing training status
        """
        try:
            job = self.db.query(MLTrainingJob).filter(
                MLTrainingJob.job_id == job_id
            ).first()

            if not job:
                raise ValueError(f"Training job {job_id} not found")

            return self._job_to_dict(job)

        except Exception as e:
            logger.error(f"Error getting training status: {e}", exc_info=True)
            raise

    def get_training_history(
        self,
        model_name: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get training history.
        
        Args:
            model_name: Filter by model name (optional)
            limit: Maximum number of jobs to return
        
        Returns:
            List of training job dictionaries
        """
        try:
            query = self.db.query(MLTrainingJob)

            if model_name:
                query = query.filter(MLTrainingJob.model_name == model_name)

            jobs = query.order_by(desc(MLTrainingJob.created_at)).limit(limit).all()

            return [self._job_to_dict(job) for job in jobs]

        except Exception as e:
            logger.error(f"Error retrieving training history: {e}", exc_info=True)
            raise

    def update_training_status(
        self,
        job_id: str,
        status: str,
        checkpoint_path: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update training job status.
        
        Args:
            job_id: Training job ID
            status: New status
            checkpoint_path: Path to checkpoint (optional)
            error_message: Error message if failed (optional)
        
        Returns:
            Dict containing updated job details
        """
        try:
            job = self.db.query(MLTrainingJob).filter(
                MLTrainingJob.job_id == job_id
            ).first()

            if not job:
                raise ValueError(f"Training job {job_id} not found")

            job.status = TrainingStatus[status.upper()]

            if status.upper() == "RUNNING" and not job.started_at:
                job.started_at = datetime.utcnow()
            
            if status.upper() in ["COMPLETED", "FAILED", "CANCELLED"]:
                job.completed_at = datetime.utcnow()

            if checkpoint_path:
                job.checkpoint_path = checkpoint_path

            if error_message:
                job.error_message = error_message

            self.db.commit()
            self.db.refresh(job)

            return self._job_to_dict(job)

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating training status: {e}", exc_info=True)
            raise

    def _job_to_dict(self, job: MLTrainingJob) -> Dict[str, Any]:
        """Convert job model to dictionary."""
        config = json.loads(job.config) if job.config else {}
        
        return {
            "job_id": job.job_id,
            "model_name": job.model_name,
            "model_version": job.model_version,
            "status": job.status.value if job.status else None,
            "training_data_start": job.training_data_start.isoformat() if job.training_data_start else None,
            "training_data_end": job.training_data_end.isoformat() if job.training_data_end else None,
            "total_steps": job.total_steps,
            "current_step": job.current_step,
            "batch_size": job.batch_size,
            "learning_rate": job.learning_rate,
            "loss": job.loss,
            "accuracy": job.accuracy,
            "checkpoint_path": job.checkpoint_path,
            "config": config,
            "error_message": job.error_message,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "updated_at": job.updated_at.isoformat() if job.updated_at else None
        }

    def _step_to_dict(self, step: TrainingStep) -> Dict[str, Any]:
        """Convert step model to dictionary."""
        metrics = json.loads(step.metrics) if step.metrics else {}
        
        return {
            "id": step.id,
            "job_id": step.job_id,
            "step_number": step.step_number,
            "loss": step.loss,
            "accuracy": step.accuracy,
            "learning_rate": step.learning_rate,
            "metrics": metrics,
            "timestamp": step.timestamp.isoformat() if step.timestamp else None
        }

