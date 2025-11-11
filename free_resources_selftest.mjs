#!/usr/bin/env node
/**
 * Free Resources Self-Test
 * Tests connectivity to free crypto APIs and backend endpoints
 * Adapted for port 7860 (default) or env PORT
 */

import https from 'https';
import http from 'http';

const PORT = process.env.PORT || '7860';
const BACKEND_BASE = `http://localhost:${PORT}`;

const TESTS = [
  {
    name: 'CoinGecko Ping',
    url: 'https://api.coingecko.com/api/v3/ping',
    required: true,
    validate: (data) => data.gecko_says === '(V3) To the Moon!'
  },
  {
    name: 'Binance Klines (BTC/USDT)',
    url: 'https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=1',
    required: true,
    validate: (data) => Array.isArray(data) && data.length > 0
  },
  {
    name: 'Alternative.me Fear & Greed',
    url: 'https://api.alternative.me/fng/',
    required: true,
    validate: (data) => data.data && Array.isArray(data.data)
  },
  {
    name: 'Backend Health',
    url: `${BACKEND_BASE}/health`,
    required: true,
    validate: (data) => data.status && data.timestamp
  },
  {
    name: 'Backend API Health (if exists)',
    url: `${BACKEND_BASE}/api/health`,
    required: false,
    validate: (data) => true
  },
  {
    name: 'HF Health',
    url: `${BACKEND_BASE}/api/hf/health`,
    required: false,
    validate: (data) => data.hasOwnProperty('ok')
  },
  {
    name: 'HF Registry Models',
    url: `${BACKEND_BASE}/api/hf/registry?kind=models`,
    required: false,
    validate: (data) => data.items && Array.isArray(data.items)
  }
];

function fetchJson(url) {
  return new Promise((resolve, reject) => {
    const client = url.startsWith('https') ? https : http;
    const req = client.get(url, { timeout: 8000 }, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        try {
          resolve({ status: res.statusCode, data: JSON.parse(body) });
        } catch (e) {
          reject(new Error(`Parse error: ${e.message}`));
        }
      });
    });
    req.on('error', reject);
    req.on('timeout', () => {
      req.destroy();
      reject(new Error('Timeout'));
    });
  });
}

async function runTests() {
  console.log('='.repeat(60));
  console.log('Free Resources Self-Test');
  console.log(`Backend: ${BACKEND_BASE}`);
  console.log('='.repeat(60));

  let passed = 0;
  let failed = 0;
  let skipped = 0;

  for (const test of TESTS) {
    process.stdout.write(`${test.name.padEnd(40)} ... `);
    try {
      const { status, data } = await fetchJson(test.url);
      if (status >= 200 && status < 300 && test.validate(data)) {
        console.log(`\x1b[32mOK\x1b[0m ${test.required ? 'REQ' : 'OPT'}`);
        passed++;
      } else {
        console.log(`\x1b[33mFAIL\x1b[0m (status=${status})`);
        if (test.required) failed++;
        else skipped++;
      }
    } catch (err) {
      console.log(`\x1b[31mERROR\x1b[0m ${err.message}`);
      if (test.required) failed++;
      else skipped++;
    }
  }

  console.log('='.repeat(60));
  console.log(`Results: ${passed} passed, ${failed} failed, ${skipped} skipped`);
  console.log('='.repeat(60));

  if (failed > 0) {
    console.error('\x1b[31mSome required tests failed!\x1b[0m');
    process.exit(1);
  } else {
    console.log('\x1b[32mAll required tests passed!\x1b[0m');
    process.exit(0);
  }
}

runTests().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
