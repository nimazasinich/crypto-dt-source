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
from typing import Optional as _Optional

from .db_manager import DatabaseManager

def _load_legacy_database() -> _Optional[type]:
    """Load the legacy Database class from the root-level ``database.py`` if it exists."""
    legacy_path = _Path(__file__).resolve().parent.parent / "database.py"
    if not legacy_path.exists():
        return None

    spec = _importlib_util.spec_from_file_location("legacy_database", legacy_path)
    if spec is None or spec.loader is None:
        return None

    module = _importlib_util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception:
        # If loading the legacy module fails we silently fall back to DatabaseManager
        return None

    return getattr(module, "Database", None)


_LegacyDatabase = _load_legacy_database()

if _LegacyDatabase is not None:
    Database = _LegacyDatabase
else:
    Database = DatabaseManager

__all__ = ["DatabaseManager", "Database"]
