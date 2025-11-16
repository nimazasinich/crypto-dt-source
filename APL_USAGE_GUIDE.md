# Auto Provider Loader (APL) - Usage Guide

## Overview

The Auto Provider Loader (APL) is a fully automated system that discovers, validates, and integrates crypto API providers into your application. It scans designated folders for provider definitions, validates them with real HTTP calls, and only adds providers that are actually functional.

## Components

### 1. `provider_validator.py`
- **Purpose**: Validates providers with real HTTP calls
- **Features**:
  - Async HTTP requests with configurable timeout
  - Rate limiting with concurrency control
  - Automatic endpoint selection
  - JSON and XML/RSS validation
  - Detailed error reporting

### 2. `auto_provider_loader.py`
- **Purpose**: Main APL system
- **Features**:
  - Multi-format JSON parsing (crypto_resources_unified, ultimate_crypto_pipeline, providers_config)
  - Duplicate detection
  - Category normalization
  - Pool management
  - Config backup before update
  - Comprehensive reporting

## How It Works

### Phase 1: Provider Discovery
1. Scans `api-resources/` and root directory for JSON files
2. Parses multiple JSON formats
3. Extracts provider metadata (base_url, endpoints, auth, rate limits)
4. Skips duplicates from existing config

### Phase 2: Provider Validation
1. Selects best endpoint for each provider
2. Makes real HTTP calls with proper headers
3. Validates response status and content
4. Records response time and errors
5. Uses concurrency control to avoid overwhelming APIs

### Phase 3: Integration
1. Loads existing config (with backup)
2. Adds only VALID providers
3. Updates existing pools or creates new ones
4. Saves updated config
5. Maintains existing providers

### Phase 4: Report Generation
1. Creates `PROVIDER_AUTO_DISCOVERY_REPORT.md`
2. Lists valid and invalid providers
3. Provides detailed validation results
4. Documents integration notes

## Usage

### Basic Usage

```bash
cd /workspace
python3 auto_provider_loader.py
```

### Output Files

1. **Updated Config**: `providers_config_extended.json`
   - Contains all providers (existing + new valid ones)
   - Backup created automatically

2. **Report**: `PROVIDER_AUTO_DISCOVERY_REPORT.md`
   - Complete validation results
   - Error details for failed providers
   - Integration statistics

3. **Backup**: `providers_config_extended.json.backup_TIMESTAMP`
   - Original config before APL run

### Customization

You can modify the APL behavior by editing `auto_provider_loader.py`:

```python
apl = AutoProviderLoader(
    scan_directories=["api-resources", "custom-folder"],  # Add more folders
    config_path="providers_config_extended.json",         # Target config
    validator_timeout=10,                                  # HTTP timeout (seconds)
    validator_concurrency=5                                # Max concurrent requests
)
```

## Validation Rules

A provider is considered VALID if:
1. ✅ HTTP status is 200
2. ✅ Response is valid JSON or XML/RSS
3. ✅ Response contains data (not empty)
4. ✅ No authentication errors (unless auth is provided)
5. ✅ Request completes within timeout

A provider is INVALID if:
- ❌ HTTP status is 4xx/5xx (except 401/403 which are marked as requires_auth)
- ❌ Request timeout
- ❌ Invalid or empty response
- ❌ No testable endpoints found
- ❌ Connection errors

## Integration with ProviderManager

After APL runs, the ProviderManager automatically uses the new providers:

```python
from provider_manager import ProviderManager

manager = ProviderManager("providers_config_extended.json")

# Providers are loaded automatically
print(f"Total providers: {len(manager.providers)}")

# Get next provider from pool
provider = manager.get_next_from_pool("blockchain_explorer_pool")
print(f"Using: {provider.name}")
```

## API Endpoints to Test New Providers

### Check Total Providers
```bash
curl http://localhost:PORT/api/providers | jq '.total'
```

### Check Specific Pool
```bash
curl http://localhost:PORT/api/pools | jq '.blockchain_explorers'
```

### Test Provider Rotation
```bash
# Call multiple times to see rotation
curl http://localhost:PORT/api/market
curl http://localhost:PORT/api/market
curl http://localhost:PORT/api/market
```

## Current Status (Latest Run)

```
================================================================================
STATUS: APL PROVIDER INTEGRATION COMPLETE ✅
================================================================================

📊 Statistics:
- Files Scanned: 7
- Candidates Discovered: 49
- Valid Providers: 5
- Invalid Providers: 44
- Providers Added: 5

🎯 Valid Providers Added:
1. etherscan_primary (blockchain_explorers) - 42.48ms
2. etherscan_secondary (blockchain_explorers) - 177.30ms
3. bscscan_primary (blockchain_explorers) - 187.79ms
4. blockscout (blockchain_explorers) - 143.81ms
5. blockscout_ethereum (blockchain_explorers) - 137.02ms

📋 Pool Updates:
- Blockchain Explorer Pool: +5 providers (now 10 total)

✅ Config File: providers_config_extended.json (68 providers total)
✅ Report Generated: PROVIDER_AUTO_DISCOVERY_REPORT.md
✅ Backup Created: providers_config_extended.json.backup_20251116_142600
```

## Troubleshooting

### Issue: Many providers marked as invalid

**Reason**: Strict validation - providers must actually respond successfully
**Solution**: This is expected behavior. APL only adds proven-working providers.

### Issue: RPC endpoints marked as invalid

**Reason**: RPC endpoints often have no simple GET endpoints to test
**Solution**: RPC endpoints need JSON-RPC POST requests which APL currently doesn't test

### Issue: Providers marked as "requires_auth"

**Reason**: Provider returned 401/403 (needs API key)
**Solution**: Add API keys to the provider definition in source JSON files

### Issue: No new providers discovered

**Reason**: All candidates were duplicates of existing providers
**Solution**: This is expected if you've already run APL before

## Safety Features

1. **Backup System**: Original config is always backed up before modification
2. **Duplicate Prevention**: Existing providers are never overwritten
3. **Strict Validation**: Only proven-working providers are added
4. **Graceful Failure**: Individual provider failures don't stop the process
5. **Rate Limiting**: Concurrent requests are controlled to avoid overwhelming APIs

## Performance

- **Validation Speed**: ~0.6 seconds for 49 providers (with concurrency=5)
- **Success Rate**: Typically 5-20% (depends on provider quality in source files)
- **Memory Usage**: Minimal (async HTTP with connection pooling)

## Extending APL

### Add New JSON Format Support

Edit `auto_provider_loader.py` and add a new parsing method:

```python
def _parse_custom_format(self, data: Dict, source_file: str):
    # Your custom parsing logic
    for item in data.get('custom_providers', []):
        provider_id = item['id']
        # ... extract data ...
        candidate = ProviderCandidate(...)
        self.discovered_providers[provider_id] = candidate
```

Then call it in `parse_provider_file()`:

```python
elif 'custom_format_marker' in data:
    self._parse_custom_format(data, str(file_path))
```

### Add Custom Validation Logic

Edit `provider_validator.py` and modify `validate_provider()`:

```python
# Add custom validation after HTTP request
if response.status == 200:
    # Your custom checks
    if not custom_validation_check(data):
        return ValidationResult(
            provider_id=provider_id,
            status=ValidationStatus.INVALID,
            error_message="Failed custom validation"
        )
```

## Best Practices

1. **Run APL periodically** to discover new providers as they're added to source files
2. **Review the report** after each run to understand what failed and why
3. **Keep backups** of your config files
4. **Test new providers** manually before relying on them in production
5. **Update source JSON files** with correct endpoints and auth info for better validation rates

## Support

For issues or questions:
1. Check `PROVIDER_AUTO_DISCOVERY_REPORT.md` for detailed error messages
2. Review provider definitions in source JSON files
3. Test providers manually with curl to verify they work
4. Ensure API keys are correctly embedded in source files

---

**Last Updated**: 2025-11-16  
**Version**: 1.0  
**Author**: Crypto Data Aggregator Team
