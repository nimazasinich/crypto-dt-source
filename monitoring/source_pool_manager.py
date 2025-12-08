"""
Intelligent Source Pool Manager
Manages source pools, rotation, and automatic failover
"""

import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from threading import Lock
from sqlalchemy.orm import Session

from database.models import (
    SourcePool, PoolMember, RotationHistory, RotationState,
    Provider, RateLimitUsage
)
from monitoring.rate_limiter import rate_limiter
from utils.logger import setup_logger

logger = setup_logger("source_pool_manager")


class SourcePoolManager:
    """
    Manages source pools and intelligent rotation
    """

    def __init__(self, db_session: Session):
        """
        Initialize source pool manager

        Args:
            db_session: Database session
        """
        self.db = db_session
        self.lock = Lock()
        logger.info("Source Pool Manager initialized")

    def create_pool(
        self,
        name: str,
        category: str,
        description: Optional[str] = None,
        rotation_strategy: str = "round_robin"
    ) -> SourcePool:
        """
        Create a new source pool

        Args:
            name: Pool name
            category: Pool category
            description: Pool description
            rotation_strategy: Rotation strategy (round_robin, least_used, priority)

        Returns:
            Created SourcePool
        """
        with self.lock:
            pool = SourcePool(
                name=name,
                category=category,
                description=description,
                rotation_strategy=rotation_strategy,
                enabled=True
            )
            self.db.add(pool)
            self.db.commit()
            self.db.refresh(pool)

            # Create rotation state
            state = RotationState(
                pool_id=pool.id,
                current_provider_id=None,
                rotation_count=0
            )
            self.db.add(state)
            self.db.commit()

            logger.info(f"Created source pool: {name} (strategy: {rotation_strategy})")
            return pool

    def add_to_pool(
        self,
        pool_id: int,
        provider_id: int,
        priority: int = 1,
        weight: int = 1
    ) -> PoolMember:
        """
        Add a provider to a pool

        Args:
            pool_id: Pool ID
            provider_id: Provider ID
            priority: Provider priority (higher = better)
            weight: Provider weight for weighted rotation

        Returns:
            Created PoolMember
        """
        with self.lock:
            member = PoolMember(
                pool_id=pool_id,
                provider_id=provider_id,
                priority=priority,
                weight=weight,
                enabled=True,
                use_count=0,
                success_count=0,
                failure_count=0
            )
            self.db.add(member)
            self.db.commit()
            self.db.refresh(member)

            logger.info(f"Added provider {provider_id} to pool {pool_id}")
            return member

    def get_next_provider(
        self,
        pool_id: int,
        exclude_rate_limited: bool = True
    ) -> Optional[Provider]:
        """
        Get next provider from pool based on rotation strategy

        Args:
            pool_id: Pool ID
            exclude_rate_limited: Exclude rate-limited providers

        Returns:
            Next Provider or None if none available
        """
        with self.lock:
            # Get pool and its members
            pool = self.db.query(SourcePool).filter_by(id=pool_id).first()
            if not pool or not pool.enabled:
                logger.warning(f"Pool {pool_id} not found or disabled")
                return None

            # Get enabled members with their providers
            members = (
                self.db.query(PoolMember)
                .filter_by(pool_id=pool_id, enabled=True)
                .join(Provider)
                .filter(Provider.id == PoolMember.provider_id)
                .all()
            )

            if not members:
                logger.warning(f"No enabled members in pool {pool_id}")
                return None

            # Filter out rate-limited providers
            if exclude_rate_limited:
                available_members = []
                for member in members:
                    provider = self.db.query(Provider).get(member.provider_id)
                    can_use, _ = rate_limiter.can_make_request(provider.name)
                    if can_use:
                        available_members.append(member)

                if not available_members:
                    logger.warning(f"All providers in pool {pool_id} are rate-limited")
                    # Return highest priority member anyway
                    available_members = members
            else:
                available_members = members

            # Select provider based on strategy
            selected_member = self._select_by_strategy(
                pool.rotation_strategy,
                available_members
            )

            if not selected_member:
                return None

            # Get rotation state
            state = self.db.query(RotationState).filter_by(pool_id=pool_id).first()
            if not state:
                state = RotationState(pool_id=pool_id)
                self.db.add(state)

            # Record rotation if provider changed
            old_provider_id = state.current_provider_id
            if old_provider_id != selected_member.provider_id:
                self._record_rotation(
                    pool_id=pool_id,
                    from_provider_id=old_provider_id,
                    to_provider_id=selected_member.provider_id,
                    reason="rotation"
                )

            # Update state
            state.current_provider_id = selected_member.provider_id
            state.last_rotation = datetime.utcnow()
            state.rotation_count += 1

            # Update member stats
            selected_member.last_used = datetime.utcnow()
            selected_member.use_count += 1

            self.db.commit()

            provider = self.db.query(Provider).get(selected_member.provider_id)
            logger.info(
                f"Selected provider {provider.name} from pool {pool.name} "
                f"(strategy: {pool.rotation_strategy})"
            )
            return provider

    def _select_by_strategy(
        self,
        strategy: str,
        members: List[PoolMember]
    ) -> Optional[PoolMember]:
        """
        Select a pool member based on rotation strategy

        Args:
            strategy: Rotation strategy
            members: Available pool members

        Returns:
            Selected PoolMember
        """
        if not members:
            return None

        if strategy == "priority":
            # Select highest priority member
            return max(members, key=lambda m: m.priority)

        elif strategy == "least_used":
            # Select least used member
            return min(members, key=lambda m: m.use_count)

        elif strategy == "weighted":
            # Weighted random selection (simple implementation)
            # In production, use proper weighted random
            return max(members, key=lambda m: m.weight * (1.0 / (m.use_count + 1)))

        else:  # round_robin (default)
            # Select least recently used
            never_used = [m for m in members if m.last_used is None]
            if never_used:
                return never_used[0]
            return min(members, key=lambda m: m.last_used)

    def _record_rotation(
        self,
        pool_id: int,
        from_provider_id: Optional[int],
        to_provider_id: int,
        reason: str,
        notes: Optional[str] = None
    ):
        """
        Record a rotation event

        Args:
            pool_id: Pool ID
            from_provider_id: Previous provider ID
            to_provider_id: New provider ID
            reason: Rotation reason
            notes: Additional notes
        """
        rotation = RotationHistory(
            pool_id=pool_id,
            from_provider_id=from_provider_id,
            to_provider_id=to_provider_id,
            rotation_reason=reason,
            success=True,
            notes=notes
        )
        self.db.add(rotation)
        self.db.commit()

    def failover(
        self,
        pool_id: int,
        failed_provider_id: int,
        reason: str = "failure"
    ) -> Optional[Provider]:
        """
        Perform failover from a failed provider

        Args:
            pool_id: Pool ID
            failed_provider_id: Failed provider ID
            reason: Failure reason

        Returns:
            Next available provider
        """
        with self.lock:
            logger.warning(
                f"Failover triggered for provider {failed_provider_id} "
                f"in pool {pool_id}. Reason: {reason}"
            )

            # Update failure count for the failed provider
            member = (
                self.db.query(PoolMember)
                .filter_by(pool_id=pool_id, provider_id=failed_provider_id)
                .first()
            )
            if member:
                member.failure_count += 1
                self.db.commit()

            # Get next provider (excluding the failed one)
            pool = self.db.query(SourcePool).filter_by(id=pool_id).first()
            if not pool:
                return None

            members = (
                self.db.query(PoolMember)
                .filter_by(pool_id=pool_id, enabled=True)
                .filter(PoolMember.provider_id != failed_provider_id)
                .all()
            )

            if not members:
                logger.error(f"No alternative providers available in pool {pool_id}")
                return None

            # Select next provider
            selected_member = self._select_by_strategy(
                pool.rotation_strategy,
                members
            )

            if not selected_member:
                return None

            # Record failover
            self._record_rotation(
                pool_id=pool_id,
                from_provider_id=failed_provider_id,
                to_provider_id=selected_member.provider_id,
                reason=reason,
                notes=f"Automatic failover from provider {failed_provider_id}"
            )

            # Update rotation state
            state = self.db.query(RotationState).filter_by(pool_id=pool_id).first()
            if state:
                state.current_provider_id = selected_member.provider_id
                state.last_rotation = datetime.utcnow()
                state.rotation_count += 1

            # Update member stats
            selected_member.last_used = datetime.utcnow()
            selected_member.use_count += 1

            self.db.commit()

            provider = self.db.query(Provider).get(selected_member.provider_id)
            logger.info(f"Failover successful: switched to provider {provider.name}")
            return provider

    def record_success(self, pool_id: int, provider_id: int):
        """
        Record successful use of a provider

        Args:
            pool_id: Pool ID
            provider_id: Provider ID
        """
        with self.lock:
            member = (
                self.db.query(PoolMember)
                .filter_by(pool_id=pool_id, provider_id=provider_id)
                .first()
            )
            if member:
                member.success_count += 1
                self.db.commit()

    def record_failure(self, pool_id: int, provider_id: int):
        """
        Record failed use of a provider

        Args:
            pool_id: Pool ID
            provider_id: Provider ID
        """
        with self.lock:
            member = (
                self.db.query(PoolMember)
                .filter_by(pool_id=pool_id, provider_id=provider_id)
                .first()
            )
            if member:
                member.failure_count += 1
                self.db.commit()

    def get_pool_status(self, pool_id: int) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive pool status

        Args:
            pool_id: Pool ID

        Returns:
            Pool status dictionary
        """
        with self.lock:
            pool = self.db.query(SourcePool).filter_by(id=pool_id).first()
            if not pool:
                return None

            # Get rotation state
            state = self.db.query(RotationState).filter_by(pool_id=pool_id).first()

            # Get current provider
            current_provider = None
            if state and state.current_provider_id:
                provider = self.db.query(Provider).get(state.current_provider_id)
                if provider:
                    current_provider = {
                        "id": provider.id,
                        "name": provider.name,
                        "status": "active"
                    }

            # Get all members with stats
            members = []
            pool_members = self.db.query(PoolMember).filter_by(pool_id=pool_id).all()

            for member in pool_members:
                provider = self.db.query(Provider).get(member.provider_id)
                if not provider:
                    continue

                # Check rate limit status
                rate_status = rate_limiter.get_status(provider.name)
                rate_limit_info = None
                if rate_status:
                    rate_limit_info = {
                        "usage": rate_status['current_usage'],
                        "limit": rate_status['limit_value'],
                        "percentage": rate_status['percentage'],
                        "status": rate_status['status']
                    }

                success_rate = 0
                if member.use_count > 0:
                    success_rate = (member.success_count / member.use_count) * 100

                members.append({
                    "provider_id": provider.id,
                    "provider_name": provider.name,
                    "priority": member.priority,
                    "weight": member.weight,
                    "enabled": member.enabled,
                    "use_count": member.use_count,
                    "success_count": member.success_count,
                    "failure_count": member.failure_count,
                    "success_rate": round(success_rate, 2),
                    "last_used": member.last_used.isoformat() if member.last_used else None,
                    "rate_limit": rate_limit_info
                })

            # Get recent rotations
            recent_rotations = (
                self.db.query(RotationHistory)
                .filter_by(pool_id=pool_id)
                .order_by(RotationHistory.timestamp.desc())
                .limit(10)
                .all()
            )

            rotation_list = []
            for rotation in recent_rotations:
                from_provider = None
                if rotation.from_provider_id:
                    from_prov = self.db.query(Provider).get(rotation.from_provider_id)
                    from_provider = from_prov.name if from_prov else None

                to_prov = self.db.query(Provider).get(rotation.to_provider_id)
                to_provider = to_prov.name if to_prov else None

                rotation_list.append({
                    "timestamp": rotation.timestamp.isoformat(),
                    "from_provider": from_provider,
                    "to_provider": to_provider,
                    "reason": rotation.rotation_reason,
                    "success": rotation.success
                })

            return {
                "pool_id": pool.id,
                "pool_name": pool.name,
                "category": pool.category,
                "description": pool.description,
                "rotation_strategy": pool.rotation_strategy,
                "enabled": pool.enabled,
                "current_provider": current_provider,
                "total_rotations": state.rotation_count if state else 0,
                "last_rotation": state.last_rotation.isoformat() if state and state.last_rotation else None,
                "members": members,
                "recent_rotations": rotation_list
            }

    def get_all_pools_status(self) -> List[Dict[str, Any]]:
        """
        Get status of all pools

        Returns:
            List of pool status dictionaries
        """
        pools = self.db.query(SourcePool).all()
        return [
            self.get_pool_status(pool.id)
            for pool in pools
            if self.get_pool_status(pool.id)
        ]
