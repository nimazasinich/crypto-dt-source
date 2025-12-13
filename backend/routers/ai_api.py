#!/usr/bin/env python3
"""
AI & ML API Router
==================
API endpoints for AI predictions, backtesting, and ML training
"""

from fastapi import APIRouter, HTTPException, Depends, Body, Query, Path
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from sqlalchemy.orm import Session
import logging

from backend.services.backtesting_service import BacktestingService
from backend.services.ml_training_service import MLTrainingService
from database.db_manager import db_manager

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/ai",
    tags=["AI & ML"]
)


# ============================================================================
# Pydantic Models
# ============================================================================

class BacktestRequest(BaseModel):
    """Request model for starting a backtest."""
    strategy: str = Field(..., description="Strategy name (e.g., 'simple_moving_average', 'rsi_strategy', 'macd_strategy')")
    symbol: str = Field(..., description="Trading pair (e.g., 'BTC/USDT')")
    start_date: datetime = Field(..., description="Backtest start date")
    end_date: datetime = Field(..., description="Backtest end date")
    initial_capital: float = Field(..., gt=0, description="Starting capital for backtest")


class TrainingRequest(BaseModel):
    """Request model for starting ML training."""
    model_name: str = Field(..., description="Name of the model to train")
    training_data_start: datetime = Field(..., description="Start date for training data")
    training_data_end: datetime = Field(..., description="End date for training data")
    batch_size: int = Field(32, gt=0, description="Training batch size")
    learning_rate: Optional[float] = Field(None, gt=0, description="Learning rate")
    config: Optional[Dict[str, Any]] = Field(None, description="Additional training configuration")


class TrainingStepRequest(BaseModel):
    """Request model for executing a training step."""
    step_number: int = Field(..., ge=1, description="Step number")
    loss: Optional[float] = Field(None, description="Training loss")
    accuracy: Optional[float] = Field(None, ge=0, le=1, description="Training accuracy")
    learning_rate: Optional[float] = Field(None, gt=0, description="Current learning rate")
    metrics: Optional[Dict[str, Any]] = Field(None, description="Additional metrics")


# ============================================================================
# Dependency Injection
# ============================================================================

def get_db() -> Session:
    """Get database session."""
    db = db_manager.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_backtesting_service(db: Session = Depends(get_db)) -> BacktestingService:
    """Get backtesting service instance."""
    return BacktestingService(db)


def get_ml_training_service(db: Session = Depends(get_db)) -> MLTrainingService:
    """Get ML training service instance."""
    return MLTrainingService(db)


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/backtest")
async def start_backtest(
    backtest_request: BacktestRequest,
    service: BacktestingService = Depends(get_backtesting_service)
) -> JSONResponse:
    """
    Start a backtest for a specific strategy.
    
    Runs a backtest simulation using historical data and returns comprehensive
    performance metrics including total return, Sharpe ratio, max drawdown, and win rate.
    
    Args:
        backtest_request: Backtest configuration
        service: Backtesting service instance
    
    Returns:
        JSON response with backtest results
    """
    try:
        # Validate dates
        if backtest_request.end_date <= backtest_request.start_date:
            raise ValueError("end_date must be after start_date")

        # Run backtest
        results = service.start_backtest(
            strategy=backtest_request.strategy,
            symbol=backtest_request.symbol,
            start_date=backtest_request.start_date,
            end_date=backtest_request.end_date,
            initial_capital=backtest_request.initial_capital
        )

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Backtest completed successfully",
                "data": results
            }
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error running backtest: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/train")
async def start_training(
    training_request: TrainingRequest,
    service: MLTrainingService = Depends(get_ml_training_service)
) -> JSONResponse:
    """
    Start training a model.
    
    Initiates the model training process with specified configuration.
    
    Args:
        training_request: Training configuration
        service: ML training service instance
    
    Returns:
        JSON response with training job details
    """
    try:
        job = service.start_training(
            model_name=training_request.model_name,
            training_data_start=training_request.training_data_start,
            training_data_end=training_request.training_data_end,
            batch_size=training_request.batch_size,
            learning_rate=training_request.learning_rate,
            config=training_request.config
        )

        return JSONResponse(
            status_code=201,
            content={
                "success": True,
                "message": "Training job created successfully",
                "data": job
            }
        )

    except Exception as e:
        logger.error(f"Error starting training: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/train-step")
async def execute_training_step(
    job_id: str = Query(..., description="Training job ID"),
    step_request: TrainingStepRequest = Body(...),
    service: MLTrainingService = Depends(get_ml_training_service)
) -> JSONResponse:
    """
    Execute a training step.
    
    Records a single training step with metrics.
    
    Args:
        job_id: Training job ID
        step_request: Training step data
        service: ML training service instance
    
    Returns:
        JSON response with step details
    """
    try:
        step = service.execute_training_step(
            job_id=job_id,
            step_number=step_request.step_number,
            loss=step_request.loss,
            accuracy=step_request.accuracy,
            learning_rate=step_request.learning_rate,
            metrics=step_request.metrics
        )

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Training step executed successfully",
                "data": step
            }
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error executing training step: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/train/status")
async def get_training_status(
    job_id: str = Query(..., description="Training job ID"),
    service: MLTrainingService = Depends(get_ml_training_service)
) -> JSONResponse:
    """
    Get the current training status.
    
    Retrieves the current status and metrics for a training job.
    
    Args:
        job_id: Training job ID
        service: ML training service instance
    
    Returns:
        JSON response with training status
    """
    try:
        status = service.get_training_status(job_id)

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": status
            }
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting training status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/train/history")
async def get_training_history(
    model_name: Optional[str] = Query(None, description="Filter by model name"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of jobs to return"),
    service: MLTrainingService = Depends(get_ml_training_service)
) -> JSONResponse:
    """
    Get training history.
    
    Retrieves the training history for all models or a specific model.
    
    Args:
        model_name: Optional model name filter
        limit: Maximum number of jobs to return
        service: ML training service instance
    
    Returns:
        JSON response with training history
    """
    try:
        history = service.get_training_history(
            model_name=model_name,
            limit=limit
        )

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "count": len(history),
                "data": history
            }
        )

    except Exception as e:
        logger.error(f"Error retrieving training history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

