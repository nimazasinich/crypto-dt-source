#!/usr/bin/env python3
"""
Test script for Crypto API Monitor Backend
"""

from database.db import SessionLocal
from database.models import Provider


def test_database():
    """Test database and providers"""
    db = SessionLocal()
    try:
        providers = db.query(Provider).all()
        print(f"\nTotal providers in DB: {len(providers)}")
        print("\nProviders loaded:")
        for p in providers:
            print(f"  - {p.name:20s} ({p.category:25s}) - {p.status.value}")

        # Group by category
        categories = {}
        for p in providers:
            if p.category not in categories:
                categories[p.category] = []
            categories[p.category].append(p.name)

        print(f"\nCategories ({len(categories)}):")
        for cat, provs in categories.items():
            print(f"  - {cat}: {len(provs)} providers")

        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Crypto API Monitor Backend - Database Test")
    print("=" * 60)

    success = test_database()

    print("\n" + "=" * 60)
    print(f"Test {'PASSED' if success else 'FAILED'}")
    print("=" * 60)
