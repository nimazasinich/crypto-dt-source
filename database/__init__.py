"""Database package exports.

This package exposes both the new SQLAlchemy-based ``DatabaseManager`` and the
legacy SQLite-backed ``Database`` class that the existing application modules
still import via ``from database import Database``. During the transition phase
we dynamically load the legacy implementation from the root ``database.py``
module (renamed here as ``legacy_database`` when importing) and fall back to the
new manager if that module is unavailable.
"""

from importlib import util as _importlib_util
from pathlib import Path as _Path
from typing import Optional as _Optional, Any as _Any

from .db_manager import DatabaseManager


def _load_legacy_module():
    """Load the legacy root-level ``database.py`` module if it exists.

    This is used to support older entry points like ``get_database`` and the
    ``Database`` class that live in the legacy file.
    """

    legacy_path = _Path(__file__).resolve().parent.parent / "database.py"
    if not legacy_path.exists():
        return None

    spec = _importlib_util.spec_from_file_location("legacy_database", legacy_path)
    if spec is None or spec.loader is None:
        return None

    module = _importlib_util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)  # type: ignore[union-attr]
    except Exception:
        # If loading the legacy module fails we silently fall back to DatabaseManager
        return None

    return module


def _load_legacy_database_class() -> _Optional[type]:
    """Load the legacy ``Database`` class from ``database.py`` if available."""

    module = _load_legacy_module()
    if module is None:
        return None
    return getattr(module, "Database", None)


def _load_legacy_get_database() -> _Optional[callable]:
    """Load the legacy ``get_database`` function from ``database.py`` if available."""

    module = _load_legacy_module()
    if module is None:
        return None
    return getattr(module, "get_database", None)


_LegacyDatabase = _load_legacy_database_class()
_LegacyGetDatabase = _load_legacy_get_database()
_db_manager_instance: _Optional[DatabaseManager] = None


if _LegacyDatabase is not None:
    Database = _LegacyDatabase
else:
    Database = DatabaseManager


def get_database(*args: _Any, **kwargs: _Any) -> _Any:
    """Return a database instance compatible with legacy callers.

    The resolution order is:

    1. If the legacy ``database.py`` file exists and exposes ``get_database``,
       use that function (this returns the legacy singleton used by the
       Gradio crypto dashboard and other older modules).
    2. Otherwise, return a singleton instance of ``DatabaseManager`` from the
       new SQLAlchemy-backed implementation.
    """

    if _LegacyGetDatabase is not None:
        return _LegacyGetDatabase(*args, **kwargs)

    global _db_manager_instance
    if _db_manager_instance is None:
        _db_manager_instance = DatabaseManager()
        # Ensure tables are created for the monitoring schema
        _db_manager_instance.init_database()
    return _db_manager_instance


__all__ = ["DatabaseManager", "Database", "get_database"]
