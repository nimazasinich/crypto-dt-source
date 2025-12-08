"""
Resource Validator for Unified Resources JSON
Validates local_backend_routes and other resources for duplicates and consistency
"""
import json
import logging
from typing import Dict, List, Any, Set, Tuple
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger(__name__)


class ResourceValidator:
    """Validates unified resources and checks for duplicates"""
    
    def __init__(self, json_path: str):
        self.json_path = Path(json_path)
        self.data: Dict[str, Any] = {}
        self.duplicates: Dict[str, List[Dict]] = defaultdict(list)
        self.validation_errors: List[str] = []
        
    def load_json(self) -> bool:
        """Load and parse the JSON file"""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            logger.info(f"✓ Loaded resource JSON: {self.json_path}")
            return True
        except json.JSONDecodeError as e:
            error_msg = f"JSON parse error in {self.json_path}: {e}"
            logger.error(error_msg)
            self.validation_errors.append(error_msg)
            return False
        except Exception as e:
            error_msg = f"Error loading {self.json_path}: {e}"
            logger.error(error_msg)
            self.validation_errors.append(error_msg)
            return False
    
    def validate_local_backend_routes(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate local_backend_routes for duplicates and consistency
        Returns: (is_valid, report)
        """
        registry = self.data.get('registry', {})
        routes = registry.get('local_backend_routes', [])
        
        if not routes:
            logger.warning("No local_backend_routes found in registry")
            return True, {"routes_count": 0, "duplicates": {}}
        
        logger.info(f"Validating {len(routes)} local backend routes...")
        
        # Track seen routes by signature
        seen_routes: Dict[str, List[Dict]] = defaultdict(list)
        route_signatures: Set[str] = set()
        
        for idx, route in enumerate(routes):
            route_id = route.get('id', f'unknown_{idx}')
            base_url = route.get('base_url', '')
            notes = route.get('notes', '')
            
            # Extract HTTP method from notes
            method = 'GET'  # default
            if notes:
                notes_lower = notes.lower()
                if 'post method' in notes_lower or 'post' in notes_lower.split(';')[0]:
                    method = 'POST'
                elif 'websocket' in notes_lower:
                    method = 'WS'
            
            # Create signature: method + normalized_url
            normalized_url = base_url.replace('{API_BASE}/', '').replace('ws://{API_BASE}/', '')
            signature = f"{method}:{normalized_url}"
            
            if signature in route_signatures:
                # Found duplicate
                self.duplicates[signature].append({
                    'id': route_id,
                    'base_url': base_url,
                    'method': method,
                    'index': idx
                })
                seen_routes[signature].append(route)
            else:
                route_signatures.add(signature)
                seen_routes[signature] = [route]
        
        # Log duplicates
        if self.duplicates:
            logger.warning(f"Found {len(self.duplicates)} duplicate route signatures:")
            for sig, dupes in self.duplicates.items():
                logger.warning(f"  - {sig}: {len(dupes)} duplicates")
                for dupe in dupes:
                    logger.warning(f"    → ID: {dupe['id']} (index {dupe['index']})")
        else:
            logger.info("✓ No duplicate routes found")
        
        # Validate required fields
        missing_fields = []
        for idx, route in enumerate(routes):
            route_id = route.get('id', f'unknown_{idx}')
            if not route.get('id'):
                missing_fields.append(f"Route at index {idx} missing 'id'")
            if not route.get('base_url'):
                missing_fields.append(f"Route '{route_id}' missing 'base_url'")
            if not route.get('category'):
                missing_fields.append(f"Route '{route_id}' missing 'category'")
        
        if missing_fields:
            logger.warning(f"Found {len(missing_fields)} routes with missing fields:")
            for msg in missing_fields[:10]:  # Show first 10
                logger.warning(f"  - {msg}")
        
        report = {
            "routes_count": len(routes),
            "unique_routes": len(route_signatures),
            "duplicate_signatures": len(self.duplicates),
            "duplicates": dict(self.duplicates),
            "missing_fields": missing_fields
        }
        
        is_valid = len(self.validation_errors) == 0
        return is_valid, report
    
    def validate_all_categories(self) -> Dict[str, Any]:
        """Validate all resource categories"""
        registry = self.data.get('registry', {})
        summary = {
            "total_categories": 0,
            "total_entries": 0,
            "categories": {}
        }
        
        for category, items in registry.items():
            if category == 'metadata':
                continue
            if isinstance(items, list):
                summary['total_categories'] += 1
                summary['total_entries'] += len(items)
                summary['categories'][category] = {
                    "count": len(items),
                    "has_ids": all(item.get('id') for item in items)
                }
        
        return summary
    
    def get_report(self) -> Dict[str, Any]:
        """Get full validation report"""
        is_valid, route_report = self.validate_local_backend_routes()
        category_summary = self.validate_all_categories()
        
        return {
            "valid": is_valid,
            "file": str(self.json_path),
            "validation_errors": self.validation_errors,
            "local_backend_routes": route_report,
            "categories": category_summary,
            "metadata": self.data.get('registry', {}).get('metadata', {})
        }


def validate_unified_resources(json_path: str) -> Dict[str, Any]:
    """
    Convenience function to validate unified resources
    Usage: validate_unified_resources('api-resources/crypto_resources_unified_2025-11-11.json')
    """
    validator = ResourceValidator(json_path)
    if not validator.load_json():
        return {
            "valid": False,
            "error": "Failed to load JSON",
            "validation_errors": validator.validation_errors
        }
    
    report = validator.get_report()
    
    # Log summary
    logger.info("=" * 60)
    logger.info("VALIDATION SUMMARY")
    logger.info("=" * 60)
    logger.info(f"File: {json_path}")
    logger.info(f"Valid: {report['valid']}")
    logger.info(f"Total Categories: {report['categories']['total_categories']}")
    logger.info(f"Total Entries: {report['categories']['total_entries']}")
    logger.info(f"Local Backend Routes: {report['local_backend_routes']['routes_count']}")
    logger.info(f"Duplicate Routes: {report['local_backend_routes']['duplicate_signatures']}")
    logger.info("=" * 60)
    
    return report


if __name__ == '__main__':
    # Test validation
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    report = validate_unified_resources('api-resources/crypto_resources_unified_2025-11-11.json')
    print(json.dumps(report, indent=2))

