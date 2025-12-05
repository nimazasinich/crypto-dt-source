# Browser Automation Testing Suite

Comprehensive automated browser testing system for the Crypto Monitor application.

## Features

- ✅ **Environment Auto-Detection**: Automatically detects local vs HuggingFace Spaces
- ✅ **Comprehensive Testing**: Tests all 16 pages with buttons, forms, and interactions
- ✅ **API Testing**: Validates all critical API endpoints
- ✅ **WebSocket Testing**: Tests WebSocket connections (local only)
- ✅ **Beautiful Reports**: Generates JSON and HTML reports with detailed results
- ✅ **Error Handling**: Retry logic, screenshots on failure, detailed error messages

## Installation

```bash
# Install required dependencies
pip install httpx
```

## Usage

### Local Testing

```bash
# Run all tests
python browser-testing/test_runner.py

# With custom URL
BASE_URL=http://localhost:7860 python browser-testing/test_runner.py
```

### HuggingFace Spaces Testing

```bash
# Test HuggingFace Spaces deployment
HF_SPACES=true BASE_URL=https://huggingface.co/spaces/Really-amin/Datasourceforcryptocurrency-2 python browser-testing/test_runner.py
```

## Test Structure

```
browser-testing/
├── config.py                  # Environment detection & configuration
├── test_runner.py            # Main test orchestrator
├── utils/
│   ├── browser_utils.py      # Browser automation utilities
│   ├── api_tester.py         # API endpoint testing
│   ├── websocket_tester.py   # WebSocket testing (local only)
│   └── report_generator.py   # Report generation
└── page_testers/
    ├── base_tester.py        # Base class for all page testers
    ├── dashboard_tester.py   # Dashboard page tests
    ├── market_tester.py      # Market page tests
    └── ...                   # 16 page-specific testers
```

## Test Coverage

### Pages Tested (16 total)
1. Dashboard (`/`)
2. Market (`/market`)
3. Models (`/models`)
4. Sentiment (`/sentiment`)
5. AI Analyst (`/ai-analyst`)
6. Trading Assistant (`/trading-assistant`)
7. News (`/news`)
8. Providers (`/providers`)
9. Diagnostics (`/diagnostics`)
10. API Explorer (`/api-explorer`)
11. Crypto API Hub (`/crypto-api-hub`)
12. Technical Analysis (`/technical-analysis`)
13. Data Sources (`/data-sources`)
14. AI Tools (`/ai-tools`)
15. Help (`/help`)
16. Settings (`/settings`)

### Test Types
- **Basic Tests** (all pages):
  - Page navigation
  - Page load completion
  - Essential elements present
  - No console errors
  - Layout components loaded

- **Page-Specific Tests**:
  - Button functionality
  - Form inputs
  - Tab switching
  - Data loading
  - API interactions

- **API Tests**:
  - Health endpoints
  - Status endpoints
  - Data endpoints
  - Response validation

- **WebSocket Tests** (local only):
  - Connection establishment
  - Message send/receive
  - Subscriptions

## Reports

Test reports are generated in `test-results/`:

```
test-results/
├── reports/
│   ├── report_YYYYMMDD_HHMMSS.json    # JSON report
│   ├── report_YYYYMMDD_HHMMSS.html    # HTML report
│   └── latest.json                     # Symlink to latest
├── screenshots/
│   └── *.png                           # Screenshots on errors
└── logs/
    └── *.log                           # Test execution logs
```

## Configuration

Environment variables:
- `BASE_URL`: Override base URL (default: http://localhost:7860)
- `HF_SPACES`: Set to 'true' for HuggingFace Spaces mode
- `SPACE_ID`: HuggingFace Space ID (auto-detected)

## Environment Differences

### Local Development
- WebSocket: **Enabled**
- URL: `http://localhost:7860`
- Full feature testing

### HuggingFace Spaces
- WebSocket: **Disabled** (per `.hf_spaces_config`)
- URL: `https://huggingface.co/spaces/Really-amin/Datasourceforcryptocurrency-2`
- HTTP-only testing

## Success Criteria

- ✅ All pages load successfully
- ✅ All buttons functional
- ✅ All forms work correctly
- ✅ All tabs switch properly
- ✅ All API calls succeed
- ✅ No console errors
- ✅ Proper styling on all pages
- ✅ WebSocket works (local only)
- ✅ Pass rate >= 90%

## Troubleshooting

### Server Not Running
Ensure the server is running before tests:
```bash
python production_server.py
```

### Import Errors
Make sure you're running from the project root:
```bash
cd /path/to/crypto-dt-source-main
python browser-testing/test_runner.py
```

### Permission Errors
Check that test-results directory is writable:
```bash
mkdir -p test-results/{reports,screenshots,logs}
chmod -R 755 test-results
```

## Development

To add new tests:

1. Create page tester in `page_testers/`
2. Inherit from `BasePageTester`
3. Implement `run_specific_tests()` method
4. Add to `test_runner.py` page_testers list

Example:
```python
class MyPageTester(BasePageTester):
    async def run_specific_tests(self) -> List[TestResult]:
        results = []
        results.append(await self.test_my_feature())
        return results
    
    async def test_my_feature(self) -> TestResult:
        # Your test logic here
        pass
```

## License

Part of the Crypto Monitor project.

