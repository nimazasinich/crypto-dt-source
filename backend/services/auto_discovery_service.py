"""
Auto Discovery Service
----------------------
جستجوی خودکار منابع API رایگان با استفاده از موتور جستجوی DuckDuckGo و
تحلیل خروجی توسط مدل‌های Hugging Face.
"""

from __future__ import annotations

import asyncio
import inspect
import json
import logging
import os
import re
from contextlib import AsyncExitStack
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    from duckduckgo_search import AsyncDDGS  # type: ignore
except ImportError:  # pragma: no cover
    AsyncDDGS = None  # type: ignore

try:
    from huggingface_hub import InferenceClient  # type: ignore
except ImportError:  # pragma: no cover
    InferenceClient = None  # type: ignore


logger = logging.getLogger(__name__)


@dataclass
class DiscoveryResult:
    """نتیجهٔ نهایی جستجو و تحلیل"""

    provider_id: str
    name: str
    category: str
    base_url: str
    requires_auth: bool
    description: str
    source_url: str


class AutoDiscoveryService:
    """
    سرویس جستجوی خودکار منابع.

    این سرویس:
      1. با استفاده از DuckDuckGo نتایج مرتبط با APIهای رایگان را جمع‌آوری می‌کند.
      2. متن نتایج را به مدل Hugging Face می‌فرستد تا پیشنهادهای ساختاریافته بازگردد.
      3. پیشنهادهای معتبر را به ResourceManager اضافه می‌کند و در صورت تأیید، ProviderManager را ریفرش می‌کند.
    """

    DEFAULT_QUERIES: List[str] = [
        "free cryptocurrency market data api",
        "open blockchain explorer api free tier",
        "free defi protocol api documentation",
        "open source sentiment analysis crypto api",
        "public nft market data api no api key",
    ]

    def __init__(
        self,
        resource_manager,
        provider_manager,
        enabled: bool = True,
    ):
        self.resource_manager = resource_manager
        self.provider_manager = provider_manager
        self.enabled = enabled and os.getenv("ENABLE_AUTO_DISCOVERY", "true").lower() == "true"
        self.interval_seconds = int(os.getenv("AUTO_DISCOVERY_INTERVAL_SECONDS", "43200"))
        self.hf_model = os.getenv("AUTO_DISCOVERY_HF_MODEL", "HuggingFaceH4/zephyr-7b-beta")
        self.max_candidates_per_query = int(os.getenv("AUTO_DISCOVERY_MAX_RESULTS", "8"))
        self._hf_client: Optional[InferenceClient] = None
        self._running_task: Optional[asyncio.Task] = None
        self._last_run_summary: Optional[Dict[str, Any]] = None

        if not self.enabled:
            logger.info("Auto discovery service disabled via configuration.")
            return

        if AsyncDDGS is None:
            logger.warning("duckduckgo-search package not available. Disabling auto discovery.")
            self.enabled = False
            return

        if InferenceClient is None:
            logger.warning(
                "huggingface-hub package not available. Auto discovery will use fallback heuristics."
            )
        else:
            hf_token = os.getenv("HF_API_TOKEN")
            try:
                self._hf_client = InferenceClient(model=self.hf_model, token=hf_token)
                logger.info(
                    "Auto discovery Hugging Face client initialized with model %s", self.hf_model
                )
            except Exception as exc:  # pragma: no cover - فقط برای شرایط عدم اتصال
                logger.error("Failed to initialize Hugging Face client: %s", exc)
                self._hf_client = None

    async def start(self):
        """شروع سرویس و ساخت حلقهٔ دوره‌ای."""
        if not self.enabled:
            return
        if self._running_task and not self._running_task.done():
            return
        self._running_task = asyncio.create_task(self._run_periodic_loop())
        logger.info(
            "Auto discovery service started with interval %s seconds", self.interval_seconds
        )

    async def stop(self):
        """توقف سرویس."""
        if self._running_task:
            self._running_task.cancel()
            try:
                await self._running_task
            except asyncio.CancelledError:
                pass
            self._running_task = None
            logger.info("Auto discovery service stopped.")

    async def trigger_manual_discovery(self) -> Dict[str, Any]:
        """اجرای دستی یک چرخهٔ کشف."""
        if not self.enabled:
            return {"status": "disabled"}
        summary = await self._run_discovery_cycle()
        return {"status": "completed", "summary": summary}

    def get_status(self) -> Dict[str, Any]:
        """وضعیت آخرین اجرا."""
        return {
            "enabled": self.enabled,
            "model": self.hf_model if self._hf_client else None,
            "interval_seconds": self.interval_seconds,
            "last_run": self._last_run_summary,
        }

    async def _run_periodic_loop(self):
        """حلقهٔ اجرای دوره‌ای."""
        while self.enabled:
            try:
                await self._run_discovery_cycle()
            except Exception as exc:
                logger.exception("Auto discovery cycle failed: %s", exc)
            await asyncio.sleep(self.interval_seconds)

    async def _run_discovery_cycle(self) -> Dict[str, Any]:
        """یک چرخه کامل جستجو، تحلیل و ثبت."""
        started_at = datetime.utcnow().isoformat()
        candidates = await self._gather_candidates()
        structured = await self._infer_candidates(candidates)
        persisted = await self._persist_candidates(structured)

        summary = {
            "started_at": started_at,
            "finished_at": datetime.utcnow().isoformat(),
            "candidates_seen": len(candidates),
            "suggested": len(structured),
            "persisted": len(persisted),
            "persisted_ids": [item.provider_id for item in persisted],
        }
        self._last_run_summary = summary

        logger.info(
            "Auto discovery cycle completed. candidates=%s suggested=%s persisted=%s",
            summary["candidates_seen"],
            summary["suggested"],
            summary["persisted"],
        )
        return summary

    async def _gather_candidates(self) -> List[Dict[str, Any]]:
        """جمع‌آوری نتایج موتور جستجو."""
        if not self.enabled or AsyncDDGS is None:
            return []

        results: List[Dict[str, Any]] = []
        queries = os.getenv("AUTO_DISCOVERY_QUERIES")
        if queries:
            query_list = [q.strip() for q in queries.split(";") if q.strip()]
        else:
            query_list = self.DEFAULT_QUERIES

        try:
            async with AsyncExitStack() as stack:
                ddgs = await stack.enter_async_context(AsyncDDGS())

                for query in query_list:
                    try:
                        text_method = getattr(ddgs, "atext", None)
                        if callable(text_method):
                            async for entry in text_method(
                                query,
                                max_results=self.max_candidates_per_query,
                            ):
                                results.append(
                                    {
                                        "query": query,
                                        "title": entry.get("title", ""),
                                        "url": entry.get("href") or entry.get("url") or "",
                                        "snippet": entry.get("body", ""),
                                    }
                                )
                            continue

                        text_method = getattr(ddgs, "text", None)
                        if not callable(text_method):
                            raise AttributeError("AsyncDDGS has no 'atext' or 'text' method")

                        search_result = text_method(
                            query,
                            max_results=self.max_candidates_per_query,
                        )

                        if inspect.isawaitable(search_result):
                            search_result = await search_result

                        if hasattr(search_result, "__aiter__"):
                            async for entry in search_result:
                                results.append(
                                    {
                                        "query": query,
                                        "title": entry.get("title", ""),
                                        "url": entry.get("href") or entry.get("url") or "",
                                        "snippet": entry.get("body", ""),
                                    }
                                )
                        else:
                            iterable = (
                                search_result
                                if isinstance(search_result, list)
                                else list(search_result or [])
                            )
                            for entry in iterable:
                                results.append(
                                    {
                                        "query": query,
                                        "title": entry.get("title", ""),
                                        "url": entry.get("href") or entry.get("url") or "",
                                        "snippet": entry.get("body", ""),
                                    }
                                )
                    except Exception as exc:  # pragma: no cover - وابسته به اینترنت
                        logger.warning(
                            "Failed to fetch results for query '%s': %s. Skipping remaining queries this cycle.",
                            query,
                            exc,
                        )
                        break
        except Exception as exc:
            logger.warning(
                "DuckDuckGo auto discovery unavailable (%s). Skipping discovery cycle.",
                exc,
            )
        finally:
            close_method = getattr(ddgs, "close", None) if "ddgs" in locals() else None
            if inspect.iscoroutinefunction(close_method):
                try:
                    await close_method()
                except Exception:
                    pass
            elif callable(close_method):
                try:
                    close_method()
                except Exception:
                    pass

        return results

    async def _infer_candidates(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """تحلیل نتایج با مدل Hugging Face یا قواعد ساده."""
        if not candidates:
            return []

        if self._hf_client:
            prompt = self._build_prompt(candidates)
            try:
                response = await asyncio.to_thread(
                    self._hf_client.text_generation,
                    prompt,
                    max_new_tokens=512,
                    temperature=0.1,
                    top_p=0.9,
                    repetition_penalty=1.1,
                )
                return self._parse_model_response(response)
            except Exception as exc:  # pragma: no cover
                logger.warning("Hugging Face inference failed: %s", exc)

        # fallback rule-based
        return self._rule_based_filter(candidates)

    def _build_prompt(self, candidates: List[Dict[str, Any]]) -> str:
        """ساخت پرامپت برای مدل LLM."""
        context_lines = []
        for idx, item in enumerate(candidates, start=1):
            context_lines.append(
                f"{idx}. Title: {item.get('title')}\n"
                f"   URL: {item.get('url')}\n"
                f"   Snippet: {item.get('snippet')}"
            )

        return (
            "You are an expert agent that extracts publicly accessible API providers for cryptocurrency, "
            "blockchain, DeFi, sentiment, NFT or analytics data. From the context entries, select candidates "
            "that represent real API services which are freely accessible (free tier or free plan). "
            "Return ONLY a JSON array. Each entry MUST include keys: "
            "id (lowercase snake_case), name, base_url, category (one of: market_data, blockchain_explorers, "
            "defi, sentiment, nft, analytics, news, rpc, huggingface, whale_tracking, onchain_analytics, custom), "
            "requires_auth (boolean), description (short string), source_url (string). "
            "Do not invent APIs. Ignore SDKs, articles, or paid-only services. "
            "If no valid candidate exists, return an empty JSON array.\n\n"
            "Context:\n" + "\n".join(context_lines)
        )

    def _parse_model_response(self, response: str) -> List[Dict[str, Any]]:
        """تبدیل پاسخ مدل به ساختار داده."""
        try:
            match = re.search(r"\[.*\]", response, re.DOTALL)
            if not match:
                logger.debug("Model response did not contain JSON array.")
                return []
            data = json.loads(match.group(0))
            if isinstance(data, list):
                return [item for item in data if isinstance(item, dict)]
            return []
        except json.JSONDecodeError:
            logger.debug("Failed to decode model JSON response.")
            return []

    def _rule_based_filter(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """فیلتر ساده در صورت در دسترس نبودن مدل."""
        structured: List[Dict[str, Any]] = []
        for item in candidates:
            url = item.get("url", "")
            snippet = (item.get("snippet") or "").lower()
            title = (item.get("title") or "").lower()
            if not url or "github" in url:
                continue
            if "api" not in title and "api" not in snippet:
                continue
            if any(keyword in snippet for keyword in ["pricing", "paid plan", "enterprise only"]):
                continue
            provider_id = self._normalize_id(item.get("title") or url)
            structured.append(
                {
                    "id": provider_id,
                    "name": item.get("title") or provider_id,
                    "base_url": url,
                    "category": "custom",
                    "requires_auth": "token" in snippet or "apikey" in snippet,
                    "description": item.get("snippet", ""),
                    "source_url": url,
                }
            )
        return structured

    async def _persist_candidates(self, structured: List[Dict[str, Any]]) -> List[DiscoveryResult]:
        """ذخیرهٔ پیشنهادهای معتبر."""
        persisted: List[DiscoveryResult] = []
        if not structured:
            return persisted

        for entry in structured:
            provider_id = self._normalize_id(entry.get("id") or entry.get("name"))
            base_url = entry.get("base_url", "")

            if not base_url.startswith(("http://", "https://")):
                continue

            if self.resource_manager.get_provider(provider_id):
                continue

            provider_data = {
                "id": provider_id,
                "name": entry.get("name", provider_id),
                "category": entry.get("category", "custom"),
                "base_url": base_url,
                "requires_auth": bool(entry.get("requires_auth")),
                "priority": 4,
                "weight": 40,
                "notes": entry.get("description", ""),
                "docs_url": entry.get("source_url", base_url),
                "free": True,
                "endpoints": {},
            }

            is_valid, message = self.resource_manager.validate_provider(provider_data)
            if not is_valid:
                logger.debug("Skipping provider %s: %s", provider_id, message)
                continue

            await asyncio.to_thread(self.resource_manager.add_provider, provider_data)
            persisted.append(
                DiscoveryResult(
                    provider_id=provider_id,
                    name=provider_data["name"],
                    category=provider_data["category"],
                    base_url=provider_data["base_url"],
                    requires_auth=provider_data["requires_auth"],
                    description=provider_data["notes"],
                    source_url=provider_data["docs_url"],
                )
            )

        if persisted:
            await asyncio.to_thread(self.resource_manager.save_resources)
            await asyncio.to_thread(self.provider_manager.load_config)
            logger.info("Persisted %s new providers.", len(persisted))

        return persisted

    @staticmethod
    def _normalize_id(raw_value: Optional[str]) -> str:
        """تبدیل نام به شناسهٔ مناسب."""
        if not raw_value:
            return "unknown_provider"
        cleaned = re.sub(r"[^a-zA-Z0-9]+", "_", raw_value).strip("_").lower()
        return cleaned or "unknown_provider"
