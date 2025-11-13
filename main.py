from importlib import util
from pathlib import Path
import sys


def _load_app_module():
    """
    تلاش برای وارد کردن آبجکت FastAPI با نام app.
    ابتدا سعی می‌کنیم مثل قبل از ماژول «app» ایمپورت کنیم.
    اگر نام «app» به پوشه‌ای اشاره کند و attribute نداشته باشد،
    فایل app.py را به طور مستقیم بارگذاری می‌کنیم.
    """
    try:
        from app import app as fastapi_app  # type: ignore
        return fastapi_app
    except (ImportError, AttributeError):
        current_dir = Path(__file__).resolve().parent
        app_path = current_dir / "app.py"
        spec = util.spec_from_file_location("crypto_monitor_app", app_path)
        if spec is None or spec.loader is None:
            raise ImportError("Could not load app.py module for FastAPI application.")
        module = util.module_from_spec(spec)
        sys.modules["crypto_monitor_app"] = module
        spec.loader.exec_module(module)
        if not hasattr(module, "app"):
            raise ImportError("app.py does not define an 'app' FastAPI instance.")
        return module.app  # type: ignore[attr-defined]


app = _load_app_module()
