"""
API Endpoints for Source Pool Management
Provides endpoints for managing source pools, rotation, and monitoring
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel, Field

from database.db_manager import db_manager
from monitoring.source_pool_manager import SourcePoolManager
from utils.logger import setup_logger

logger = setup_logger("pool_api")

# Create APIRouter instance
router = APIRouter(prefix="/api/pools", tags=["source_pools"])


# ============================================================================
# Pydantic Models for Request/Response Validation
# ============================================================================


class CreatePoolRequest(BaseModel):
    """Request model for creating a pool"""

    name: str = Field(..., description="Pool name")
    category: str = Field(..., description="Pool category")
    description: Optional[str] = Field(None, description="Pool description")
    rotation_strategy: str = Field("round_robin", description="Rotation strategy")


class AddMemberRequest(BaseModel):
    """Request model for adding a member to a pool"""

    provider_id: int = Field(..., description="Provider ID")
    priority: int = Field(1, description="Provider priority")
    weight: int = Field(1, description="Provider weight")


class UpdatePoolRequest(BaseModel):
    """Request model for updating a pool"""

    rotation_strategy: Optional[str] = Field(None, description="Rotation strategy")
    enabled: Optional[bool] = Field(None, description="Pool enabled status")
    description: Optional[str] = Field(None, description="Pool description")


class UpdateMemberRequest(BaseModel):
    """Request model for updating a pool member"""

    priority: Optional[int] = Field(None, description="Provider priority")
    weight: Optional[int] = Field(None, description="Provider weight")
    enabled: Optional[bool] = Field(None, description="Member enabled status")


class TriggerRotationRequest(BaseModel):
    """Request model for triggering manual rotation"""

    reason: str = Field("manual", description="Rotation reason")


class FailoverRequest(BaseModel):
    """Request model for triggering failover"""

    failed_provider_id: int = Field(..., description="Failed provider ID")
    reason: str = Field("manual_failover", description="Failover reason")


# ============================================================================
# GET /api/pools - List All Pools
# ============================================================================


@router.get("")
async def list_pools():
    """
    Get list of all source pools with their status

    Returns:
        List of source pools with status information
    """
    try:
        session = db_manager.get_session()
        pool_manager = SourcePoolManager(session)

        pools_status = pool_manager.get_all_pools_status()

        session.close()

        return {
            "pools": pools_status,
            "total": len(pools_status),
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error listing pools: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list pools: {str(e)}")


# ============================================================================
# POST /api/pools - Create New Pool
# ============================================================================


@router.post("")
async def create_pool(request: CreatePoolRequest):
    """
    Create a new source pool

    Args:
        request: Pool creation request

    Returns:
        Created pool information
    """
    try:
        session = db_manager.get_session()
        pool_manager = SourcePoolManager(session)

        pool = pool_manager.create_pool(
            name=request.name,
            category=request.category,
            description=request.description,
            rotation_strategy=request.rotation_strategy,
        )

        session.close()

        return {
            "pool_id": pool.id,
            "name": pool.name,
            "category": pool.category,
            "rotation_strategy": pool.rotation_strategy,
            "created_at": pool.created_at.isoformat(),
            "message": f"Pool '{pool.name}' created successfully",
        }

    except Exception as e:
        logger.error(f"Error creating pool: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create pool: {str(e)}")


# ============================================================================
# GET /api/pools/{pool_id} - Get Pool Status
# ============================================================================


@router.get("/{pool_id}")
async def get_pool_status(pool_id: int):
    """
    Get detailed status of a specific pool

    Args:
        pool_id: Pool ID

    Returns:
        Detailed pool status
    """
    try:
        session = db_manager.get_session()
        pool_manager = SourcePoolManager(session)

        pool_status = pool_manager.get_pool_status(pool_id)

        session.close()

        if not pool_status:
            raise HTTPException(status_code=404, detail=f"Pool {pool_id} not found")

        return pool_status

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting pool status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get pool status: {str(e)}")


# ============================================================================
# PUT /api/pools/{pool_id} - Update Pool
# ============================================================================


@router.put("/{pool_id}")
async def update_pool(pool_id: int, request: UpdatePoolRequest):
    """
    Update pool configuration

    Args:
        pool_id: Pool ID
        request: Update request

    Returns:
        Updated pool information
    """
    try:
        session = db_manager.get_session()

        # Get pool from database
        from database.models import SourcePool

        pool = session.query(SourcePool).filter_by(id=pool_id).first()

        if not pool:
            session.close()
            raise HTTPException(status_code=404, detail=f"Pool {pool_id} not found")

        # Update fields
        if request.rotation_strategy is not None:
            pool.rotation_strategy = request.rotation_strategy
        if request.enabled is not None:
            pool.enabled = request.enabled
        if request.description is not None:
            pool.description = request.description

        pool.updated_at = datetime.utcnow()

        session.commit()
        session.refresh(pool)

        result = {
            "pool_id": pool.id,
            "name": pool.name,
            "rotation_strategy": pool.rotation_strategy,
            "enabled": pool.enabled,
            "updated_at": pool.updated_at.isoformat(),
            "message": f"Pool '{pool.name}' updated successfully",
        }

        session.close()

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating pool: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to update pool: {str(e)}")


# ============================================================================
# DELETE /api/pools/{pool_id} - Delete Pool
# ============================================================================


@router.delete("/{pool_id}")
async def delete_pool(pool_id: int):
    """
    Delete a source pool

    Args:
        pool_id: Pool ID

    Returns:
        Deletion confirmation
    """
    try:
        session = db_manager.get_session()

        from database.models import SourcePool

        pool = session.query(SourcePool).filter_by(id=pool_id).first()

        if not pool:
            session.close()
            raise HTTPException(status_code=404, detail=f"Pool {pool_id} not found")

        pool_name = pool.name
        session.delete(pool)
        session.commit()
        session.close()

        return {"message": f"Pool '{pool_name}' deleted successfully", "pool_id": pool_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting pool: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to delete pool: {str(e)}")


# ============================================================================
# POST /api/pools/{pool_id}/members - Add Member to Pool
# ============================================================================


@router.post("/{pool_id}/members")
async def add_pool_member(pool_id: int, request: AddMemberRequest):
    """
    Add a provider to a pool

    Args:
        pool_id: Pool ID
        request: Add member request

    Returns:
        Created member information
    """
    try:
        session = db_manager.get_session()
        pool_manager = SourcePoolManager(session)

        member = pool_manager.add_to_pool(
            pool_id=pool_id,
            provider_id=request.provider_id,
            priority=request.priority,
            weight=request.weight,
        )

        # Get provider name
        from database.models import Provider

        provider = session.query(Provider).get(request.provider_id)

        session.close()

        return {
            "member_id": member.id,
            "pool_id": pool_id,
            "provider_id": request.provider_id,
            "provider_name": provider.name if provider else None,
            "priority": member.priority,
            "weight": member.weight,
            "message": f"Provider added to pool successfully",
        }

    except Exception as e:
        logger.error(f"Error adding pool member: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to add pool member: {str(e)}")


# ============================================================================
# PUT /api/pools/{pool_id}/members/{provider_id} - Update Pool Member
# ============================================================================


@router.put("/{pool_id}/members/{provider_id}")
async def update_pool_member(pool_id: int, provider_id: int, request: UpdateMemberRequest):
    """
    Update a pool member configuration

    Args:
        pool_id: Pool ID
        provider_id: Provider ID
        request: Update request

    Returns:
        Updated member information
    """
    try:
        session = db_manager.get_session()

        from database.models import PoolMember

        member = (
            session.query(PoolMember).filter_by(pool_id=pool_id, provider_id=provider_id).first()
        )

        if not member:
            session.close()
            raise HTTPException(status_code=404, detail=f"Member not found in pool {pool_id}")

        # Update fields
        if request.priority is not None:
            member.priority = request.priority
        if request.weight is not None:
            member.weight = request.weight
        if request.enabled is not None:
            member.enabled = request.enabled

        session.commit()
        session.refresh(member)

        result = {
            "pool_id": pool_id,
            "provider_id": provider_id,
            "priority": member.priority,
            "weight": member.weight,
            "enabled": member.enabled,
            "message": "Pool member updated successfully",
        }

        session.close()

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating pool member: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to update pool member: {str(e)}")


# ============================================================================
# DELETE /api/pools/{pool_id}/members/{provider_id} - Remove Member
# ============================================================================


@router.delete("/{pool_id}/members/{provider_id}")
async def remove_pool_member(pool_id: int, provider_id: int):
    """
    Remove a provider from a pool

    Args:
        pool_id: Pool ID
        provider_id: Provider ID

    Returns:
        Deletion confirmation
    """
    try:
        session = db_manager.get_session()

        from database.models import PoolMember

        member = (
            session.query(PoolMember).filter_by(pool_id=pool_id, provider_id=provider_id).first()
        )

        if not member:
            session.close()
            raise HTTPException(status_code=404, detail=f"Member not found in pool {pool_id}")

        session.delete(member)
        session.commit()
        session.close()

        return {
            "message": "Provider removed from pool successfully",
            "pool_id": pool_id,
            "provider_id": provider_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing pool member: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to remove pool member: {str(e)}")


# ============================================================================
# POST /api/pools/{pool_id}/rotate - Trigger Manual Rotation
# ============================================================================


@router.post("/{pool_id}/rotate")
async def trigger_rotation(pool_id: int, request: TriggerRotationRequest):
    """
    Trigger manual rotation to next provider in pool

    Args:
        pool_id: Pool ID
        request: Rotation request

    Returns:
        New provider information
    """
    try:
        session = db_manager.get_session()
        pool_manager = SourcePoolManager(session)

        provider = pool_manager.get_next_provider(pool_id)

        session.close()

        if not provider:
            raise HTTPException(status_code=404, detail=f"No available providers in pool {pool_id}")

        return {
            "pool_id": pool_id,
            "provider_id": provider.id,
            "provider_name": provider.name,
            "timestamp": datetime.utcnow().isoformat(),
            "message": f"Rotated to provider '{provider.name}'",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering rotation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to trigger rotation: {str(e)}")


# ============================================================================
# POST /api/pools/{pool_id}/failover - Trigger Failover
# ============================================================================


@router.post("/{pool_id}/failover")
async def trigger_failover(pool_id: int, request: FailoverRequest):
    """
    Trigger failover from a failed provider

    Args:
        pool_id: Pool ID
        request: Failover request

    Returns:
        New provider information
    """
    try:
        session = db_manager.get_session()
        pool_manager = SourcePoolManager(session)

        provider = pool_manager.failover(
            pool_id=pool_id, failed_provider_id=request.failed_provider_id, reason=request.reason
        )

        session.close()

        if not provider:
            raise HTTPException(
                status_code=404, detail=f"No alternative providers available in pool {pool_id}"
            )

        return {
            "pool_id": pool_id,
            "failed_provider_id": request.failed_provider_id,
            "new_provider_id": provider.id,
            "new_provider_name": provider.name,
            "timestamp": datetime.utcnow().isoformat(),
            "message": f"Failover successful: switched to '{provider.name}'",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering failover: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to trigger failover: {str(e)}")


# ============================================================================
# GET /api/pools/{pool_id}/history - Get Rotation History
# ============================================================================


@router.get("/{pool_id}/history")
async def get_rotation_history(pool_id: int, limit: int = 50):
    """
    Get rotation history for a pool

    Args:
        pool_id: Pool ID
        limit: Maximum number of records to return

    Returns:
        List of rotation history records
    """
    try:
        session = db_manager.get_session()

        from database.models import Provider, RotationHistory

        history = (
            session.query(RotationHistory)
            .filter_by(pool_id=pool_id)
            .order_by(RotationHistory.timestamp.desc())
            .limit(limit)
            .all()
        )

        history_list = []
        for record in history:
            from_provider = None
            if record.from_provider_id:
                from_prov = session.query(Provider).get(record.from_provider_id)
                from_provider = from_prov.name if from_prov else None

            to_prov = session.query(Provider).get(record.to_provider_id)
            to_provider = to_prov.name if to_prov else None

            history_list.append(
                {
                    "id": record.id,
                    "timestamp": record.timestamp.isoformat(),
                    "from_provider": from_provider,
                    "to_provider": to_provider,
                    "reason": record.rotation_reason,
                    "success": record.success,
                    "notes": record.notes,
                }
            )

        session.close()

        return {"pool_id": pool_id, "history": history_list, "total": len(history_list)}

    except Exception as e:
        logger.error(f"Error getting rotation history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get rotation history: {str(e)}")


logger.info("Pool API endpoints module loaded successfully")
