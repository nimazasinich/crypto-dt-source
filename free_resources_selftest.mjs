#!/usr/bin/env node
/**
 * Free Resources Self-Test for Crypto DT Source
 * Tests all free API endpoints and HuggingFace connectivity
 * Adapted for port 7860 with /api/health and /api/market/prices
 */

const BACKEND_PORT = process.env.BACKEND_PORT || '7860';
const BACKEND_HOST = process.env.BACKEND_HOST || 'localhost';
const API_BASE = `http://${BACKEND_HOST}:${BACKEND_PORT}`;

// Test configuration
const TESTS = {
  // Required backend endpoints
  'Backend Health': {
    url: `${API_BASE}/api/health`,
    method: 'GET',
    required: true,
    validate: (data) => data && (data.status === 'healthy' || data.online !== undefined)
  },

  // HuggingFace endpoints
  'HF Health': {
    url: `${API_BASE}/api/hf/health`,
    method: 'GET',
    required: true,
    validate: (data) => data && typeof data.ok === 'boolean' && data.counts
  },
  'HF Registry Models': {
    url: `${API_BASE}/api/hf/registry?kind=models`,
    method: 'GET',
    required: true,
    validate: (data) => data && Array.isArray(data.items) && data.items.length >= 2
  },
  'HF Registry Datasets': {
    url: `${API_BASE}/api/hf/registry?kind=datasets`,
    method: 'GET',
    required: true,
    validate: (data) => data && Array.isArray(data.items) && data.items.length >= 4
  },
  'HF Search': {
    url: `${API_BASE}/api/hf/search?q=crypto&kind=models`,
    method: 'GET',
    required: true,
    validate: (data) => data && data.count >= 0 && Array.isArray(data.items)
  },

  // External free APIs
  'CoinGecko Simple Price': {
    url: 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd',
    method: 'GET',
    required: true,
    validate: (data) => data && data.bitcoin && data.bitcoin.usd
  },
  'Binance Klines': {
    url: 'https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=10',
    method: 'GET',
    required: true,
    validate: (data) => Array.isArray(data) && data.length > 0
  },
  'Alternative.me Fear & Greed': {
    url: 'https://api.alternative.me/fng/?limit=1',
    method: 'GET',
    required: true,
    validate: (data) => data && data.data && Array.isArray(data.data)
  },
  'CoinCap Assets': {
    url: 'https://api.coincap.io/v2/assets?limit=5',
    method: 'GET',
    required: false,
    validate: (data) => data && Array.isArray(data.data)
  },
  'CryptoCompare Price': {
    url: 'https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=USD',
    method: 'GET',
    required: false,
    validate: (data) => data && data.USD
  }
};

// Optional: test POST endpoint for sentiment (may be slow due to model loading)
const POST_TESTS = {
  'HF Sentiment Analysis': {
    url: `${API_BASE}/api/hf/run-sentiment`,
    method: 'POST',
    body: { texts: ['BTC strong breakout', 'ETH looks weak'] },
    required: false,
    validate: (data) => data && typeof data.enabled === 'boolean'
  }
};

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  cyan: '\x1b[36m',
  gray: '\x1b[90m'
};

async function testEndpoint(name, config) {
  const start = Date.now();

  try {
    const options = {
      method: config.method,
      headers: { 'Content-Type': 'application/json' },
      signal: AbortSignal.timeout(10000) // 10s timeout
    };

    if (config.body) {
      options.body = JSON.stringify(config.body);
    }

    const response = await fetch(config.url, options);
    const elapsed = Date.now() - start;

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();

    // Validate response data if validator exists
    const isValid = config.validate ? config.validate(data) : true;

    if (!isValid) {
      throw new Error('Validation failed');
    }

    const status = config.required ? 'OK | REQ' : 'OK | OPT';
    const color = config.required ? colors.green : colors.cyan;

    console.log(
      `${color}✓${colors.reset} ${status.padEnd(10)} ${name.padEnd(30)} ${colors.gray}${elapsed}ms${colors.reset}`
    );

    return { success: true, elapsed, required: config.required };

  } catch (error) {
    const elapsed = Date.now() - start;
    const status = config.required ? 'FAIL | REQ' : 'SKIP | OPT';
    const color = config.required ? colors.red : colors.yellow;

    console.log(
      `${color}✗${colors.reset} ${status.padEnd(10)} ${name.padEnd(30)} ${colors.gray}${elapsed}ms${colors.reset} ${colors.gray}${error.message}${colors.reset}`
    );

    return { success: false, elapsed, required: config.required, error: error.message };
  }
}

async function runTests() {
  console.log(`\n${colors.bright}${colors.cyan}═══════════════════════════════════════════════════════════════${colors.reset}`);
  console.log(`${colors.bright}Free Resources Self-Test${colors.reset}`);
  console.log(`${colors.gray}Backend: ${API_BASE}${colors.reset}`);
  console.log(`${colors.cyan}═══════════════════════════════════════════════════════════════${colors.reset}\n`);

  const results = [];

  // Run GET tests
  console.log(`${colors.bright}Testing Endpoints:${colors.reset}\n`);
  for (const [name, config] of Object.entries(TESTS)) {
    const result = await testEndpoint(name, config);
    results.push(result);
    await new Promise(resolve => setTimeout(resolve, 100)); // Small delay between tests
  }

  // Run POST tests if enabled
  if (process.env.TEST_POST === 'true' || process.argv.includes('--post')) {
    console.log(`\n${colors.bright}Testing POST Endpoints:${colors.reset}\n`);
    for (const [name, config] of Object.entries(POST_TESTS)) {
      const result = await testEndpoint(name, config);
      results.push(result);
      await new Promise(resolve => setTimeout(resolve, 100));
    }
  }

  // Summary
  console.log(`\n${colors.cyan}═══════════════════════════════════════════════════════════════${colors.reset}`);
  console.log(`${colors.bright}Summary:${colors.reset}\n`);

  const total = results.length;
  const passed = results.filter(r => r.success).length;
  const failed = results.filter(r => !r.success).length;
  const requiredTests = results.filter(r => r.required);
  const requiredPassed = requiredTests.filter(r => r.success).length;
  const requiredFailed = requiredTests.filter(r => !r.success).length;

  console.log(`  Total Tests:     ${total}`);
  console.log(`  ${colors.green}✓ Passed:${colors.reset}        ${passed}`);
  console.log(`  ${colors.red}✗ Failed:${colors.reset}        ${failed}`);
  console.log(`  ${colors.bright}Required Tests:${colors.reset}  ${requiredTests.length}`);
  console.log(`    ${colors.green}✓ Passed:${colors.reset}      ${requiredPassed}`);
  console.log(`    ${colors.red}✗ Failed:${colors.reset}      ${requiredFailed}`);

  console.log(`${colors.cyan}═══════════════════════════════════════════════════════════════${colors.reset}\n`);

  // Exit code
  if (requiredFailed > 0) {
    console.log(`${colors.red}${colors.bright}FAILED:${colors.reset} ${requiredFailed} required test(s) failed\n`);
    process.exit(1);
  } else {
    console.log(`${colors.green}${colors.bright}SUCCESS:${colors.reset} All required tests passed\n`);
    process.exit(0);
  }
}

// Help text
if (process.argv.includes('--help') || process.argv.includes('-h')) {
  console.log(`
Free Resources Self-Test

Usage:
  node free_resources_selftest.mjs [options]

Options:
  --help, -h          Show this help message
  --post              Include POST endpoint tests (slower, requires model loading)

Environment Variables:
  BACKEND_PORT        Backend server port (default: 7860)
  BACKEND_HOST        Backend server host (default: localhost)
  TEST_POST           Set to 'true' to test POST endpoints

Examples:
  node free_resources_selftest.mjs
  node free_resources_selftest.mjs --post
  BACKEND_PORT=8000 node free_resources_selftest.mjs
  TEST_POST=true node free_resources_selftest.mjs
  `);
  process.exit(0);
}

// Run tests
runTests().catch(error => {
  console.error(`\n${colors.red}${colors.bright}Fatal Error:${colors.reset} ${error.message}\n`);
  process.exit(1);
});
