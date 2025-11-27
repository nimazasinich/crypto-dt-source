"""
Diagnostics & Auto-Repair Service
----------------------------------
سرویس اشکال‌یابی خودکار و تعمیر مشکلات سیستم
"""

import asyncio
import logging
import os
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import json
import importlib.util

logger = logging.getLogger(__name__)


@dataclass
class DiagnosticIssue:
    """یک مشکل شناسایی شده"""

    severity: str  # critical, warning, info
    category: str  # dependency, config, network, service, model
    title: str
    description: str
    fixable: bool
    fix_action: Optional[str] = None
    auto_fixed: bool = False
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class DiagnosticReport:
    """گزارش کامل اشکال‌یابی"""

    timestamp: str
    total_issues: int
    critical_issues: int
    warnings: int
    info_issues: int
    issues: List[DiagnosticIssue]
    fixed_issues: List[DiagnosticIssue]
    system_info: Dict[str, Any]
    duration_ms: float


class DiagnosticsService:
    """سرویس اشکال‌یابی و تعمیر خودکار"""

    def __init__(self, resource_manager=None, provider_manager=None, auto_discovery_service=None):
        self.resource_manager = resource_manager
        self.provider_manager = provider_manager
        self.auto_discovery_service = auto_discovery_service
        self.last_report: Optional[DiagnosticReport] = None

    async def run_full_diagnostics(self, auto_fix: bool = False) -> DiagnosticReport:
        """اجرای کامل اشکال‌یابی"""
        start_time = datetime.now()
        issues: List[DiagnosticIssue] = []
        fixed_issues: List[DiagnosticIssue] = []

        # بررسی وابستگی‌ها
        issues.extend(await self._check_dependencies())

        # بررسی تنظیمات
        issues.extend(await self._check_configuration())

        # بررسی شبکه
        issues.extend(await self._check_network())

        # بررسی سرویس‌ها
        issues.extend(await self._check_services())

        # بررسی مدل‌ها
        issues.extend(await self._check_models())

        # بررسی فایل‌ها و دایرکتوری‌ها
        issues.extend(await self._check_filesystem())

        # اجرای تعمیر خودکار
        if auto_fix:
            for issue in issues:
                if issue.fixable and issue.fix_action:
                    fixed = await self._apply_fix(issue)
                    if fixed:
                        issue.auto_fixed = True
                        fixed_issues.append(issue)

        # محاسبه آمار
        critical = sum(1 for i in issues if i.severity == "critical")
        warnings = sum(1 for i in issues if i.severity == "warning")
        info_count = sum(1 for i in issues if i.severity == "info")

        duration_ms = (datetime.now() - start_time).total_seconds() * 1000

        report = DiagnosticReport(
            timestamp=datetime.now().isoformat(),
            total_issues=len(issues),
            critical_issues=critical,
            warnings=warnings,
            info_issues=info_count,
            issues=issues,
            fixed_issues=fixed_issues,
            system_info=await self._get_system_info(),
            duration_ms=duration_ms,
        )

        self.last_report = report
        return report

    async def _check_dependencies(self) -> List[DiagnosticIssue]:
        """بررسی وابستگی‌های Python"""
        issues = []
        required_packages = {
            "fastapi": "FastAPI",
            "uvicorn": "Uvicorn",
            "httpx": "HTTPX",
            "pydantic": "Pydantic",
            "duckduckgo_search": "DuckDuckGo Search",
            "huggingface_hub": "HuggingFace Hub",
            "transformers": "Transformers",
        }

        for package, name in required_packages.items():
            try:
                spec = importlib.util.find_spec(package)
                if spec is None:
                    issues.append(
                        DiagnosticIssue(
                            severity="critical" if package in ["fastapi", "uvicorn"] else "warning",
                            category="dependency",
                            title=f"بسته {name} نصب نشده است",
                            description=f"بسته {package} مورد نیاز است اما نصب نشده است.",
                            fixable=True,
                            fix_action=f"pip install {package}",
                        )
                    )
            except Exception as e:
                issues.append(
                    DiagnosticIssue(
                        severity="warning",
                        category="dependency",
                        title=f"خطا در بررسی {name}",
                        description=f"خطا در بررسی بسته {package}: {str(e)}",
                        fixable=False,
                    )
                )

        return issues

    async def _check_configuration(self) -> List[DiagnosticIssue]:
        """بررسی تنظیمات"""
        issues = []

        # بررسی متغیرهای محیطی مهم
        important_env_vars = {
            "HF_API_TOKEN": ("warning", "توکن HuggingFace برای استفاده از مدل‌ها"),
        }

        for var, (severity, desc) in important_env_vars.items():
            if not os.getenv(var):
                issues.append(
                    DiagnosticIssue(
                        severity=severity,
                        category="config",
                        title=f"متغیر محیطی {var} تنظیم نشده",
                        description=desc,
                        fixable=False,
                    )
                )

        # بررسی فایل‌های پیکربندی
        config_files = ["resources.json", "config.json"]
        for config_file in config_files:
            if not os.path.exists(config_file):
                issues.append(
                    DiagnosticIssue(
                        severity="info",
                        category="config",
                        title=f"فایل پیکربندی {config_file} وجود ندارد",
                        description=f"فایل {config_file} یافت نشد. ممکن است به صورت خودکار ساخته شود.",
                        fixable=False,
                    )
                )

        return issues

    async def _check_network(self) -> List[DiagnosticIssue]:
        """بررسی اتصال شبکه"""
        issues = []
        import httpx

        test_urls = [
            ("https://api.coingecko.com/api/v3/ping", "CoinGecko API"),
            ("https://api.huggingface.co", "HuggingFace API"),
        ]

        for url, name in test_urls:
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(url)
                    if response.status_code >= 400:
                        issues.append(
                            DiagnosticIssue(
                                severity="warning",
                                category="network",
                                title=f"مشکل در اتصال به {name}",
                                description=f"درخواست به {url} با کد {response.status_code} پاسخ داد.",
                                fixable=False,
                            )
                        )
            except Exception as e:
                issues.append(
                    DiagnosticIssue(
                        severity="warning",
                        category="network",
                        title=f"عدم دسترسی به {name}",
                        description=f"خطا در اتصال به {url}: {str(e)}",
                        fixable=False,
                    )
                )

        return issues

    async def _check_services(self) -> List[DiagnosticIssue]:
        """بررسی سرویس‌ها"""
        issues = []

        # بررسی Auto-Discovery Service
        if self.auto_discovery_service:
            status = self.auto_discovery_service.get_status()
            if not status.get("enabled"):
                issues.append(
                    DiagnosticIssue(
                        severity="info",
                        category="service",
                        title="سرویس Auto-Discovery غیرفعال است",
                        description="سرویس جستجوی خودکار منابع غیرفعال است.",
                        fixable=False,
                    )
                )
            elif not status.get("model"):
                issues.append(
                    DiagnosticIssue(
                        severity="warning",
                        category="service",
                        title="مدل HuggingFace برای Auto-Discovery تنظیم نشده",
                        description="سرویس Auto-Discovery بدون مدل HuggingFace کار می‌کند.",
                        fixable=False,
                    )
                )

        # بررسی Provider Manager
        if self.provider_manager:
            stats = self.provider_manager.get_all_stats()
            summary = stats.get("summary", {})
            if summary.get("online", 0) == 0 and summary.get("total_providers", 0) > 0:
                issues.append(
                    DiagnosticIssue(
                        severity="critical",
                        category="service",
                        title="هیچ Provider آنلاینی وجود ندارد",
                        description="تمام Provider‌ها آفلاین هستند.",
                        fixable=False,
                    )
                )

        return issues

    async def _check_models(self) -> List[DiagnosticIssue]:
        """بررسی وضعیت مدل‌های HuggingFace"""
        issues = []

        try:
            from huggingface_hub import InferenceClient, HfApi

            api = HfApi()

            # بررسی مدل‌های استفاده شده
            models_to_check = [
                "HuggingFaceH4/zephyr-7b-beta",
                "cardiffnlp/twitter-roberta-base-sentiment-latest",
            ]

            for model_id in models_to_check:
                try:
                    model_info = api.model_info(model_id, timeout=5.0)
                    if not model_info:
                        issues.append(
                            DiagnosticIssue(
                                severity="warning",
                                category="model",
                                title=f"مدل {model_id} در دسترس نیست",
                                description=f"نمی‌توان به اطلاعات مدل {model_id} دسترسی پیدا کرد.",
                                fixable=False,
                            )
                        )
                except Exception as e:
                    issues.append(
                        DiagnosticIssue(
                            severity="warning",
                            category="model",
                            title=f"خطا در بررسی مدل {model_id}",
                            description=f"خطا: {str(e)}",
                            fixable=False,
                        )
                    )
        except ImportError:
            issues.append(
                DiagnosticIssue(
                    severity="info",
                    category="model",
                    title="بسته huggingface_hub نصب نشده",
                    description="برای بررسی مدل‌ها نیاز به نصب huggingface_hub است.",
                    fixable=True,
                    fix_action="pip install huggingface_hub",
                )
            )

        return issues

    async def _check_filesystem(self) -> List[DiagnosticIssue]:
        """بررسی فایل سیستم"""
        issues = []

        # بررسی دایرکتوری‌های مهم
        important_dirs = ["static", "static/css", "static/js", "backend", "backend/services"]
        for dir_path in important_dirs:
            if not os.path.exists(dir_path):
                issues.append(
                    DiagnosticIssue(
                        severity="warning",
                        category="filesystem",
                        title=f"دایرکتوری {dir_path} وجود ندارد",
                        description=f"دایرکتوری {dir_path} یافت نشد.",
                        fixable=True,
                        fix_action=f"mkdir -p {dir_path}",
                    )
                )

        # بررسی فایل‌های مهم
        important_files = [
            "api_server_extended.py",
            "unified_dashboard.html",
            "static/js/websocket-client.js",
            "static/css/connection-status.css",
        ]
        for file_path in important_files:
            if not os.path.exists(file_path):
                issues.append(
                    DiagnosticIssue(
                        severity="critical" if "api_server" in file_path else "warning",
                        category="filesystem",
                        title=f"فایل {file_path} وجود ندارد",
                        description=f"فایل {file_path} یافت نشد.",
                        fixable=False,
                    )
                )

        return issues

    async def _apply_fix(self, issue: DiagnosticIssue) -> bool:
        """اعمال تعمیر خودکار"""
        if not issue.fixable or not issue.fix_action:
            return False

        try:
            if issue.fix_action.startswith("pip install"):
                # نصب بسته
                package = issue.fix_action.replace("pip install", "").strip()
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", package],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                if result.returncode == 0:
                    logger.info(f"✅ بسته {package} با موفقیت نصب شد")
                    return True
                else:
                    logger.error(f"❌ خطا در نصب {package}: {result.stderr}")
                    return False

            elif issue.fix_action.startswith("mkdir"):
                # ساخت دایرکتوری
                dir_path = issue.fix_action.replace("mkdir -p", "").strip()
                os.makedirs(dir_path, exist_ok=True)
                logger.info(f"✅ دایرکتوری {dir_path} ساخته شد")
                return True

            else:
                logger.warning(f"⚠️ عمل تعمیر ناشناخته: {issue.fix_action}")
                return False

        except Exception as e:
            logger.error(f"❌ خطا در اعمال تعمیر: {e}")
            return False

    async def _get_system_info(self) -> Dict[str, Any]:
        """دریافت اطلاعات سیستم"""
        import platform

        return {
            "python_version": sys.version,
            "platform": platform.platform(),
            "architecture": platform.architecture(),
            "processor": platform.processor(),
            "cwd": os.getcwd(),
        }

    def get_last_report(self) -> Optional[Dict[str, Any]]:
        """دریافت آخرین گزارش"""
        if self.last_report:
            return asdict(self.last_report)
        return None
