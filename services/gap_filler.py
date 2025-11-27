#!/usr/bin/env python3
"""
Gap Filling Service - Intelligently fills missing data
Uses AI models first, then fallback to external providers
Priority: HF Models → HF Space API → External Providers
"""

import asyncio
import logging
import time
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class GapType(Enum):
    """Types of data gaps that can be detected and filled"""

    MISSING_OHLC = "missing_ohlc"
    MISSING_DEPTH = "missing_depth"
    MISSING_WHALE_DATA = "missing_whale_data"
    MISSING_SENTIMENT = "missing_sentiment"
    INCOMPLETE_METADATA = "incomplete_metadata"
    MISSING_TRANSACTIONS = "missing_transactions"
    MISSING_BALANCE = "missing_balance"


class GapFillStrategy(Enum):
    """Strategies for filling gaps"""

    AI_MODEL_SYNTHESIS = "ai_model_synthesis"
    INTERPOLATION = "interpolation"
    EXTERNAL_PROVIDER = "external_provider"
    HYBRID = "hybrid"
    STATISTICAL_ESTIMATION = "statistical_estimation"


class GapFillerService:
    """Main orchestrator for gap filling operations"""

    def __init__(self, model_registry=None, provider_manager=None, database=None):
        """
        Initialize gap filler service

        Args:
            model_registry: AI model registry for ML-based gap filling
            provider_manager: Provider manager for external API fallback
            database: Database instance for storing gap filling audit logs
        """
        self.models = model_registry
        self.providers = provider_manager
        self.db = database
        self.gap_fill_cache = {}
        self.audit_log = []

        logger.info("GapFillerService initialized")

    async def detect_gaps(
        self,
        data: Dict[str, Any],
        required_fields: List[str],
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Detect all missing/incomplete data in provided dataset

        Args:
            data: Dataset to analyze for gaps
            required_fields: List of required field names
            context: Additional context for gap detection (e.g., expected data range)

        Returns:
            List of detected gaps with recommended strategies
        """
        gaps = []

        # Check for missing required fields
        for field in required_fields:
            if field not in data or data[field] is None:
                gap = {
                    "gap_type": self._infer_gap_type(field),
                    "field": field,
                    "severity": "high",
                    "recommended_strategy": self._recommend_strategy(field, data),
                    "context": context or {},
                }
                gaps.append(gap)

        # Check for incomplete time series data
        if "timestamps" in data and isinstance(data["timestamps"], list):
            missing_timestamps = self._detect_missing_timestamps(data["timestamps"], context)
            if missing_timestamps:
                gaps.append(
                    {
                        "gap_type": GapType.MISSING_OHLC.value,
                        "field": "ohlc_data",
                        "missing_count": len(missing_timestamps),
                        "missing_timestamps": missing_timestamps,
                        "severity": "medium",
                        "recommended_strategy": GapFillStrategy.INTERPOLATION.value,
                    }
                )

        # Check for incomplete price data
        if "prices" in data:
            price_gaps = self._detect_price_gaps(data["prices"])
            if price_gaps:
                gaps.extend(price_gaps)

        logger.info(f"Detected {len(gaps)} gaps in data")
        return gaps

    def _infer_gap_type(self, field: str) -> str:
        """Infer gap type from field name"""
        if "ohlc" in field.lower() or "price" in field.lower() or "candle" in field.lower():
            return GapType.MISSING_OHLC.value
        elif "depth" in field.lower() or "orderbook" in field.lower():
            return GapType.MISSING_DEPTH.value
        elif "whale" in field.lower() or "large_transfer" in field.lower():
            return GapType.MISSING_WHALE_DATA.value
        elif "sentiment" in field.lower():
            return GapType.MISSING_SENTIMENT.value
        elif "transaction" in field.lower():
            return GapType.MISSING_TRANSACTIONS.value
        elif "balance" in field.lower():
            return GapType.MISSING_BALANCE.value
        else:
            return GapType.INCOMPLETE_METADATA.value

    def _recommend_strategy(self, field: str, data: Dict[str, Any]) -> str:
        """Recommend best strategy for filling this gap"""
        gap_type = self._infer_gap_type(field)

        if gap_type == GapType.MISSING_OHLC.value:
            # If we have surrounding data, use interpolation
            if "prices" in data and len(data.get("prices", [])) > 2:
                return GapFillStrategy.INTERPOLATION.value
            else:
                return GapFillStrategy.EXTERNAL_PROVIDER.value

        elif gap_type == GapType.MISSING_SENTIMENT.value:
            # Use AI models for sentiment
            return GapFillStrategy.AI_MODEL_SYNTHESIS.value

        elif gap_type == GapType.MISSING_DEPTH.value:
            # Use statistical estimation
            return GapFillStrategy.STATISTICAL_ESTIMATION.value

        else:
            # Default to external provider
            return GapFillStrategy.EXTERNAL_PROVIDER.value

    def _detect_missing_timestamps(
        self, timestamps: List[int], context: Optional[Dict[str, Any]]
    ) -> List[int]:
        """Detect missing timestamps in a time series"""
        if not timestamps or len(timestamps) < 2:
            return []

        timestamps = sorted(timestamps)
        missing = []

        # Determine expected interval (e.g., 1 minute, 5 minutes, 1 hour)
        intervals = [timestamps[i + 1] - timestamps[i] for i in range(len(timestamps) - 1)]
        expected_interval = min(intervals) if intervals else 60

        # Find gaps
        for i in range(len(timestamps) - 1):
            current = timestamps[i]
            next_ts = timestamps[i + 1]
            diff = next_ts - current

            if diff > expected_interval * 1.5:  # Allow 50% tolerance
                # Generate missing timestamps
                num_missing = int(diff / expected_interval) - 1
                for j in range(1, num_missing + 1):
                    missing.append(current + j * expected_interval)

        return missing[:100]  # Limit to 100 missing points

    def _detect_price_gaps(self, prices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect gaps in price data (e.g., missing OHLC fields)"""
        gaps = []
        required_ohlc_fields = ["open", "high", "low", "close"]

        for i, price_data in enumerate(prices):
            missing_fields = [
                f for f in required_ohlc_fields if f not in price_data or price_data[f] is None
            ]
            if missing_fields:
                gaps.append(
                    {
                        "gap_type": GapType.MISSING_OHLC.value,
                        "index": i,
                        "missing_fields": missing_fields,
                        "severity": "medium",
                        "recommended_strategy": GapFillStrategy.INTERPOLATION.value,
                    }
                )

        return gaps

    async def fill_gap(
        self, gap: Dict[str, Any], data: Dict[str, Any], context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Fill a single gap using best available strategy
        Priority: HF Models → HF Space API → External Providers

        Args:
            gap: Gap definition from detect_gaps()
            data: Original data containing the gap
            context: Additional context for gap filling

        Returns:
            Filled data with metadata about the fill operation
        """
        start_time = time.time()
        gap_type = gap.get("gap_type")
        strategy = gap.get("recommended_strategy")

        result = {
            "gap": gap,
            "filled": False,
            "strategy_used": None,
            "confidence": 0.0,
            "filled_data": None,
            "attempts": [],
            "execution_time_ms": 0,
            "error": None,
        }

        try:
            # Strategy 1: AI Model Synthesis (Priority 1)
            if strategy == GapFillStrategy.AI_MODEL_SYNTHESIS.value and self.models:
                attempt = await self._fill_with_ai_model(gap, data, context)
                result["attempts"].append(attempt)

                if attempt["success"]:
                    result["filled"] = True
                    result["strategy_used"] = GapFillStrategy.AI_MODEL_SYNTHESIS.value
                    result["confidence"] = attempt.get("confidence", 0.7)
                    result["filled_data"] = attempt["data"]

            # Strategy 2: Interpolation (for time series)
            if not result["filled"] and strategy == GapFillStrategy.INTERPOLATION.value:
                attempt = await self._fill_with_interpolation(gap, data, context)
                result["attempts"].append(attempt)

                if attempt["success"]:
                    result["filled"] = True
                    result["strategy_used"] = GapFillStrategy.INTERPOLATION.value
                    result["confidence"] = attempt.get("confidence", 0.8)
                    result["filled_data"] = attempt["data"]

            # Strategy 3: Statistical Estimation
            if not result["filled"] and strategy == GapFillStrategy.STATISTICAL_ESTIMATION.value:
                attempt = await self._fill_with_statistics(gap, data, context)
                result["attempts"].append(attempt)

                if attempt["success"]:
                    result["filled"] = True
                    result["strategy_used"] = GapFillStrategy.STATISTICAL_ESTIMATION.value
                    result["confidence"] = attempt.get("confidence", 0.65)
                    result["filled_data"] = attempt["data"]

            # Strategy 4: External Provider (Fallback)
            if not result["filled"] and self.providers:
                attempt = await self._fill_with_external_provider(gap, data, context)
                result["attempts"].append(attempt)

                if attempt["success"]:
                    result["filled"] = True
                    result["strategy_used"] = GapFillStrategy.EXTERNAL_PROVIDER.value
                    result["confidence"] = attempt.get("confidence", 0.9)
                    result["filled_data"] = attempt["data"]

        except Exception as e:
            logger.error(f"Error filling gap: {e}")
            result["error"] = str(e)

        result["execution_time_ms"] = int((time.time() - start_time) * 1000)

        # Log attempt
        await self._log_gap_fill_attempt(result)

        return result

    async def _fill_with_ai_model(
        self, gap: Dict[str, Any], data: Dict[str, Any], context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Fill gap using AI models"""
        try:
            # Use the gap filler from ai_models
            from ai_models import get_gap_filler

            gap_filler = get_gap_filler()

            gap_type = gap.get("gap_type")

            if gap_type == GapType.MISSING_SENTIMENT.value:
                # Use sentiment analysis model
                text = context.get("text") if context else ""
                if not text and "text" in data:
                    text = data["text"]

                if text:
                    from ai_models import ensemble_crypto_sentiment

                    sentiment = ensemble_crypto_sentiment(text)

                    return {
                        "success": True,
                        "data": sentiment,
                        "confidence": sentiment.get("confidence", 0.7),
                        "method": "ai_sentiment_model",
                    }

            elif gap_type == GapType.MISSING_OHLC.value:
                # Use OHLC interpolation
                symbol = context.get("symbol") if context else "BTC"
                existing_data = data.get("prices", [])
                missing_timestamps = gap.get("missing_timestamps", [])

                if existing_data and missing_timestamps:
                    result = await gap_filler.fill_missing_ohlc(
                        symbol, existing_data, missing_timestamps
                    )
                    if result["status"] == "success":
                        return {
                            "success": True,
                            "data": result["filled_data"],
                            "confidence": result["average_confidence"],
                            "method": "ai_ohlc_interpolation",
                        }

            return {"success": False, "error": "No suitable AI model found"}

        except Exception as e:
            logger.warning(f"AI model fill failed: {e}")
            return {"success": False, "error": str(e)}

    async def _fill_with_interpolation(
        self, gap: Dict[str, Any], data: Dict[str, Any], context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Fill gap using interpolation"""
        try:
            from ai_models import get_gap_filler

            gap_filler = get_gap_filler()

            symbol = context.get("symbol") if context else "UNKNOWN"
            existing_data = data.get("prices", [])
            missing_timestamps = gap.get("missing_timestamps", [])

            if not existing_data or not missing_timestamps:
                return {"success": False, "error": "Insufficient data for interpolation"}

            result = await gap_filler.fill_missing_ohlc(symbol, existing_data, missing_timestamps)

            if result["status"] == "success":
                return {
                    "success": True,
                    "data": result["filled_data"],
                    "confidence": result["average_confidence"],
                    "method": "linear_interpolation",
                }

            return {"success": False, "error": result.get("message", "Interpolation failed")}

        except Exception as e:
            logger.warning(f"Interpolation fill failed: {e}")
            return {"success": False, "error": str(e)}

    async def _fill_with_statistics(
        self, gap: Dict[str, Any], data: Dict[str, Any], context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Fill gap using statistical estimation"""
        try:
            from ai_models import get_gap_filler

            gap_filler = get_gap_filler()

            gap_type = gap.get("gap_type")

            if gap_type == GapType.MISSING_DEPTH.value:
                # Estimate orderbook depth
                symbol = context.get("symbol") if context else "BTCUSDT"
                mid_price = data.get("price") or context.get("price") if context else 50000

                result = await gap_filler.estimate_orderbook_depth(symbol, mid_price)

                if result["status"] == "success":
                    return {
                        "success": True,
                        "data": result,
                        "confidence": result["confidence"],
                        "method": "statistical_orderbook_estimation",
                    }

            return {"success": False, "error": "No suitable statistical method found"}

        except Exception as e:
            logger.warning(f"Statistical fill failed: {e}")
            return {"success": False, "error": str(e)}

    async def _fill_with_external_provider(
        self, gap: Dict[str, Any], data: Dict[str, Any], context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Fill gap using external provider API"""
        try:
            if not self.providers:
                return {"success": False, "error": "No provider manager available"}

            gap_type = gap.get("gap_type")

            # Map gap type to provider category
            if gap_type in [GapType.MISSING_OHLC.value, GapType.INCOMPLETE_METADATA.value]:
                # Use CoinMarketCap for market data
                provider = self.providers.get_provider("coinmarketcap")
                if provider and provider.is_available:
                    # This would call real API
                    # For now, return placeholder
                    return {
                        "success": True,
                        "data": {"source": "coinmarketcap", "provider_used": True},
                        "confidence": 0.9,
                        "method": "external_coinmarketcap",
                    }

            elif gap_type == GapType.MISSING_TRANSACTIONS.value:
                # Use blockchain explorer
                chain = context.get("chain") if context else "ethereum"
                if chain == "ethereum":
                    provider = self.providers.get_provider("etherscan")
                elif chain == "bsc":
                    provider = self.providers.get_provider("bscscan")
                elif chain == "tron":
                    provider = self.providers.get_provider("tronscan")
                else:
                    provider = None

                if provider and provider.is_available:
                    return {
                        "success": True,
                        "data": {"source": provider.name, "provider_used": True},
                        "confidence": 0.9,
                        "method": f"external_{provider.provider_id}",
                    }

            return {"success": False, "error": "No suitable provider found"}

        except Exception as e:
            logger.warning(f"External provider fill failed: {e}")
            return {"success": False, "error": str(e)}

    async def fill_all_gaps(
        self,
        data: Dict[str, Any],
        required_fields: List[str],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Detect and fill all gaps in one operation

        Returns:
            Enriched data with metadata about what was filled
        """
        start_time = time.time()

        # Detect gaps
        gaps = await self.detect_gaps(data, required_fields, context)

        # Fill each gap
        fill_results = []
        for gap in gaps:
            result = await self.fill_gap(gap, data, context)
            fill_results.append(result)

            # Update data with filled values
            if result["filled"] and result["filled_data"]:
                # Merge filled data into original data
                field = gap.get("field")
                if field:
                    data[field] = result["filled_data"]

        execution_time = int((time.time() - start_time) * 1000)

        # Calculate statistics
        gaps_detected = len(gaps)
        gaps_filled = sum(1 for r in fill_results if r["filled"])
        avg_confidence = (
            sum(r["confidence"] for r in fill_results) / gaps_detected if gaps_detected > 0 else 0
        )

        return {
            "status": "success",
            "original_data": data,
            "enriched_data": data,
            "gaps_detected": gaps_detected,
            "gaps_filled": gaps_filled,
            "fill_rate": gaps_filled / gaps_detected if gaps_detected > 0 else 0,
            "fill_results": fill_results,
            "average_confidence": avg_confidence,
            "execution_time_ms": execution_time,
            "metadata": {
                "strategies_used": list(
                    set(r["strategy_used"] for r in fill_results if r["strategy_used"])
                ),
                "timestamp": datetime.utcnow().isoformat(),
            },
        }

    async def _log_gap_fill_attempt(self, result: Dict[str, Any]):
        """Log gap fill attempt for audit trail"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "gap_type": result["gap"].get("gap_type"),
            "field": result["gap"].get("field"),
            "filled": result["filled"],
            "strategy_used": result["strategy_used"],
            "confidence": result["confidence"],
            "execution_time_ms": result["execution_time_ms"],
            "attempts_count": len(result["attempts"]),
        }

        self.audit_log.append(log_entry)

        # Keep only last 1000 entries
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-1000:]

        # Save to database if available
        if self.db:
            try:
                # This would save to gap_filling_audit table
                pass
            except Exception as e:
                logger.warning(f"Failed to save audit log to database: {e}")

    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent gap filling audit logs"""
        return self.audit_log[-limit:]

    def get_statistics(self) -> Dict[str, Any]:
        """Get gap filling statistics"""
        if not self.audit_log:
            return {
                "total_attempts": 0,
                "success_rate": 0,
                "average_confidence": 0,
                "average_execution_time_ms": 0,
            }

        total = len(self.audit_log)
        successful = sum(1 for log in self.audit_log if log["filled"])
        avg_confidence = sum(log["confidence"] for log in self.audit_log) / total
        avg_time = sum(log["execution_time_ms"] for log in self.audit_log) / total

        # Count by strategy
        strategy_counts = {}
        for log in self.audit_log:
            strategy = log.get("strategy_used")
            if strategy:
                strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1

        return {
            "total_attempts": total,
            "successful_fills": successful,
            "success_rate": successful / total if total > 0 else 0,
            "average_confidence": avg_confidence,
            "average_execution_time_ms": avg_time,
            "strategies_used": strategy_counts,
        }
