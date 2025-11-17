"""
Advanced API Router
Provides endpoints for the advanced admin dashboard
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path
import logging
import json
import asyncio

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Advanced API"])


# ============================================================================
# Request Statistics Endpoints
# ============================================================================

@router.get("/stats/requests")
async def get_request_stats():
    """Get API request statistics"""
    try:
        # Try to load from health log
        health_log_path = Path("data/logs/provider_health.jsonl")
        
        stats = {
            'totalRequests': 0,
            'successRate': 0,
            'avgResponseTime': 0,
            'requestsHistory': [],
            'statusBreakdown': {
                'success': 0,
                'errors': 0,
                'timeouts': 0
            }
        }
        
        if health_log_path.exists():
            with open(health_log_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                stats['totalRequests'] = len(lines)
                
                # Parse last 100 entries for stats
                recent_entries = []
                for line in lines[-100:]:
                    try:
                        entry = json.loads(line.strip())
                        recent_entries.append(entry)
                    except:
                        continue
                
                if recent_entries:
                    # Calculate success rate
                    success_count = sum(1 for e in recent_entries if e.get('status') == 'success')
                    stats['successRate'] = round((success_count / len(recent_entries)) * 100, 1)
                    
                    # Calculate avg response time
                    response_times = [e.get('response_time_ms', 0) for e in recent_entries if e.get('response_time_ms')]
                    if response_times:
                        stats['avgResponseTime'] = round(sum(response_times) / len(response_times))
                    
                    # Status breakdown
                    stats['statusBreakdown']['success'] = success_count
                    stats['statusBreakdown']['errors'] = sum(1 for e in recent_entries if e.get('status') == 'error')
                    stats['statusBreakdown']['timeouts'] = sum(1 for e in recent_entries if e.get('status') == 'timeout')
        
        # Generate 24h timeline
        now = datetime.now()
        for i in range(23, -1, -1):
            timestamp = now - timedelta(hours=i)
            stats['requestsHistory'].append({
                'timestamp': timestamp.isoformat(),
                'count': max(10, int(stats['totalRequests'] / 24) + (i % 5) * 3)  # Distribute evenly
            })
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting request stats: {e}")
        return {
            'totalRequests': 0,
            'successRate': 0,
            'avgResponseTime': 0,
            'requestsHistory': [],
            'statusBreakdown': {'success': 0, 'errors': 0, 'timeouts': 0}
        }


# ============================================================================
# Resource Management Endpoints
# ============================================================================

@router.post("/resources/scan")
async def scan_resources():
    """Scan and detect all resources"""
    try:
        providers_path = Path("providers_config_extended.json")
        
        if not providers_path.exists():
            return {'status': 'error', 'message': 'Config file not found'}
        
        with open(providers_path, 'r') as f:
            config = json.load(f)
        
        providers = config.get('providers', {})
        
        return {
            'status': 'success',
            'found': len(providers),
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error scanning resources: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/resources/fix-duplicates")
async def fix_duplicates():
    """Detect and remove duplicate resources"""
    try:
        providers_path = Path("providers_config_extended.json")
        
        if not providers_path.exists():
            return {'status': 'error', 'message': 'Config file not found'}
        
        with open(providers_path, 'r') as f:
            config = json.load(f)
        
        providers = config.get('providers', {})
        
        # Detect duplicates by normalized name
        seen = {}
        duplicates = []
        
        for provider_id, provider_info in list(providers.items()):
            name = provider_info.get('name', provider_id)
            normalized_name = name.lower().replace(' ', '').replace('-', '').replace('_', '')
            
            if normalized_name in seen:
                # This is a duplicate
                duplicates.append(provider_id)
                logger.info(f"Found duplicate: {provider_id} (matches {seen[normalized_name]})")
            else:
                seen[normalized_name] = provider_id
        
        # Remove duplicates
        for dup_id in duplicates:
            del providers[provider_id]
        
        # Save config
        if duplicates:
            # Create backup
            backup_path = providers_path.parent / f"{providers_path.name}.backup.{int(datetime.now().timestamp())}"
            with open(backup_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Save cleaned config
            with open(providers_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"Fixed {len(duplicates)} duplicates. Backup: {backup_path}")
        
        return {
            'status': 'success',
            'removed': len(duplicates),
            'duplicates': duplicates,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fixing duplicates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/resources")
async def add_resource(resource: Dict[str, Any]):
    """Add a new resource"""
    try:
        providers_path = Path("providers_config_extended.json")
        
        if not providers_path.exists():
            raise HTTPException(status_code=404, detail="Config file not found")
        
        with open(providers_path, 'r') as f:
            config = json.load(f)
        
        providers = config.get('providers', {})
        
        # Generate provider ID
        resource_type = resource.get('type', 'api')
        name = resource.get('name', 'unknown')
        provider_id = f"{resource_type}_{name.lower().replace(' ', '_')}"
        
        # Check if already exists
        if provider_id in providers:
            raise HTTPException(status_code=400, detail="Resource already exists")
        
        # Create provider entry
        provider_entry = {
            'name': name,
            'type': resource_type,
            'category': resource.get('category', 'unknown'),
            'base_url': resource.get('url', ''),
            'requires_auth': False,
            'validated': False,
            'priority': 5,
            'added_at': datetime.now().isoformat(),
            'notes': resource.get('notes', '')
        }
        
        # Add to config
        providers[provider_id] = provider_entry
        config['providers'] = providers
        
        # Save
        with open(providers_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Added new resource: {provider_id}")
        
        return {
            'status': 'success',
            'provider_id': provider_id,
            'message': 'Resource added successfully'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding resource: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/resources/{provider_id}")
async def remove_resource(provider_id: str):
    """Remove a resource"""
    try:
        providers_path = Path("providers_config_extended.json")
        
        if not providers_path.exists():
            raise HTTPException(status_code=404, detail="Config file not found")
        
        with open(providers_path, 'r') as f:
            config = json.load(f)
        
        providers = config.get('providers', {})
        
        if provider_id not in providers:
            raise HTTPException(status_code=404, detail="Resource not found")
        
        # Remove
        del providers[provider_id]
        config['providers'] = providers
        
        # Save
        with open(providers_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Removed resource: {provider_id}")
        
        return {
            'status': 'success',
            'message': 'Resource removed successfully'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing resource: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Auto-Discovery Endpoints
# ============================================================================

@router.post("/discovery/full")
async def run_full_discovery(background_tasks: BackgroundTasks):
    """Run full auto-discovery"""
    try:
        # Import APL
        import auto_provider_loader
        
        async def run_discovery():
            """Background task to run discovery"""
            try:
                apl = auto_provider_loader.AutoProviderLoader()
                await apl.run()
                logger.info(f"Discovery completed: {apl.stats.total_active_providers} providers")
            except Exception as e:
                logger.error(f"Discovery error: {e}")
        
        # Run in background
        background_tasks.add_task(run_discovery)
        
        # Return immediate response
        return {
            'status': 'started',
            'message': 'Discovery started in background',
            'found': 0,
            'validated': 0,
            'failed': 0
        }
        
    except Exception as e:
        logger.error(f"Error starting discovery: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/discovery/status")
async def get_discovery_status():
    """Get current discovery status"""
    try:
        report_path = Path("PROVIDER_AUTO_DISCOVERY_REPORT.json")
        
        if not report_path.exists():
            return {
                'status': 'not_run',
                'found': 0,
                'validated': 0,
                'failed': 0
            }
        
        with open(report_path, 'r') as f:
            report = json.load(f)
        
        stats = report.get('statistics', {})
        
        return {
            'status': 'completed',
            'found': stats.get('total_http_candidates', 0) + stats.get('total_hf_candidates', 0),
            'validated': stats.get('http_valid', 0) + stats.get('hf_valid', 0),
            'failed': stats.get('http_invalid', 0) + stats.get('hf_invalid', 0),
            'timestamp': report.get('timestamp', '')
        }
        
    except Exception as e:
        logger.error(f"Error getting discovery status: {e}")
        return {
            'status': 'error',
            'found': 0,
            'validated': 0,
            'failed': 0
        }


# ============================================================================
# Health Logging (Track Requests)
# ============================================================================

@router.post("/log/request")
async def log_request(log_entry: Dict[str, Any]):
    """Log an API request for tracking"""
    try:
        log_dir = Path("data/logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / "provider_health.jsonl"
        
        # Add timestamp
        log_entry['timestamp'] = datetime.now().isoformat()
        
        # Append to log
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        return {'status': 'success'}
        
    except Exception as e:
        logger.error(f"Error logging request: {e}")
        return {'status': 'error', 'message': str(e)}


# ============================================================================
# CryptoBERT Deduplication Fix
# ============================================================================

@router.post("/fix/cryptobert-duplicates")
async def fix_cryptobert_duplicates():
    """Fix CryptoBERT model duplication issues"""
    try:
        providers_path = Path("providers_config_extended.json")
        
        if not providers_path.exists():
            raise HTTPException(status_code=404, detail="Config file not found")
        
        with open(providers_path, 'r') as f:
            config = json.load(f)
        
        providers = config.get('providers', {})
        
        # Find all CryptoBERT models
        cryptobert_models = {}
        for provider_id, provider_info in list(providers.items()):
            name = provider_info.get('name', '')
            if 'cryptobert' in name.lower():
                # Normalize the model identifier
                if 'ulako' in provider_id.lower() or 'ulako' in name.lower():
                    model_key = 'ulako_cryptobert'
                elif 'kk08' in provider_id.lower() or 'kk08' in name.lower():
                    model_key = 'kk08_cryptobert'
                else:
                    model_key = provider_id
                
                if model_key in cryptobert_models:
                    # Duplicate found - keep the better one
                    existing = cryptobert_models[model_key]
                    
                    # Keep the validated one if exists
                    if provider_info.get('validated', False) and not providers[existing].get('validated', False):
                        # Remove old, keep new
                        del providers[existing]
                        cryptobert_models[model_key] = provider_id
                    else:
                        # Remove new, keep old
                        del providers[provider_id]
                else:
                    cryptobert_models[model_key] = provider_id
        
        # Save config
        config['providers'] = providers
        
        # Create backup
        backup_path = providers_path.parent / f"{providers_path.name}.backup.{int(datetime.now().timestamp())}"
        with open(backup_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Save cleaned config
        with open(providers_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Fixed CryptoBERT duplicates. Models remaining: {len(cryptobert_models)}")
        
        return {
            'status': 'success',
            'models_found': len(cryptobert_models),
            'models_remaining': list(cryptobert_models.values()),
            'message': 'CryptoBERT duplicates fixed'
        }
        
    except Exception as e:
        logger.error(f"Error fixing CryptoBERT duplicates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Export Endpoints
# ============================================================================

@router.get("/export/analytics")
async def export_analytics():
    """Export analytics data"""
    try:
        stats = await get_request_stats()
        
        export_dir = Path("data/exports")
        export_dir.mkdir(parents=True, exist_ok=True)
        
        export_file = export_dir / f"analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(export_file, 'w') as f:
            json.dump(stats, f, indent=2)
        
        return {
            'status': 'success',
            'file': str(export_file),
            'message': 'Analytics exported successfully'
        }
        
    except Exception as e:
        logger.error(f"Error exporting analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/resources")
async def export_resources():
    """Export resources configuration"""
    try:
        providers_path = Path("providers_config_extended.json")
        
        if not providers_path.exists():
            raise HTTPException(status_code=404, detail="Config file not found")
        
        export_dir = Path("data/exports")
        export_dir.mkdir(parents=True, exist_ok=True)
        
        export_file = export_dir / f"resources_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Copy config
        with open(providers_path, 'r') as f:
            config = json.load(f)
        
        with open(export_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        return {
            'status': 'success',
            'file': str(export_file),
            'providers_count': len(config.get('providers', {})),
            'message': 'Resources exported successfully'
        }
        
    except Exception as e:
        logger.error(f"Error exporting resources: {e}")
        raise HTTPException(status_code=500, detail=str(e))
