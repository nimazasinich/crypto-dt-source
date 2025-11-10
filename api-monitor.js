#!/usr/bin/env node

/**
 * CRYPTOCURRENCY API RESOURCE MONITOR
 * Monitors and manages all API resources from registry
 * Tracks online status, validates endpoints, maintains availability metrics
 */

const fs = require('fs');
const https = require('https');
const http = require('http');

// ═══════════════════════════════════════════════════════════════
// CONFIGURATION
// ═══════════════════════════════════════════════════════════════

const CONFIG = {
  REGISTRY_FILE: './all_apis_merged_2025.json',
  CHECK_INTERVAL: 5 * 60 * 1000, // 5 minutes
  TIMEOUT: 10000, // 10 seconds
  MAX_RETRIES: 3,
  RETRY_DELAY: 2000,

  // Status thresholds
  THRESHOLDS: {
    ONLINE: { responseTime: 2000, successRate: 0.95 },
    DEGRADED: { responseTime: 5000, successRate: 0.80 },
    SLOW: { responseTime: 10000, successRate: 0.70 },
    UNSTABLE: { responseTime: Infinity, successRate: 0.50 }
  }
};

// ═══════════════════════════════════════════════════════════════
// API REGISTRY - Comprehensive resource definitions
// ═══════════════════════════════════════════════════════════════

const API_REGISTRY = {
  blockchainExplorers: {
    etherscan: [
      { name: 'Etherscan-1', url: 'https://api.etherscan.io/api', keyName: 'etherscan', keyIndex: 0, testEndpoint: '?module=stats&action=ethprice&apikey={{KEY}}', tier: 1 },
      { name: 'Etherscan-2', url: 'https://api.etherscan.io/api', keyName: 'etherscan', keyIndex: 1, testEndpoint: '?module=stats&action=ethprice&apikey={{KEY}}', tier: 1 }
    ],
    bscscan: [
      { name: 'BscScan', url: 'https://api.bscscan.com/api', keyName: 'bscscan', keyIndex: 0, testEndpoint: '?module=stats&action=bnbprice&apikey={{KEY}}', tier: 1 }
    ],
    tronscan: [
      { name: 'TronScan', url: 'https://apilist.tronscanapi.com/api', keyName: 'tronscan', keyIndex: 0, testEndpoint: '/system/status', tier: 2 }
    ]
  },

  marketData: {
    coingecko: [
      { name: 'CoinGecko', url: 'https://api.coingecko.com/api/v3', testEndpoint: '/ping', requiresKey: false, tier: 1 },
      { name: 'CoinGecko-Price', url: 'https://api.coingecko.com/api/v3', testEndpoint: '/simple/price?ids=bitcoin&vs_currencies=usd', requiresKey: false, tier: 1 }
    ],
    coinmarketcap: [
      { name: 'CoinMarketCap-1', url: 'https://pro-api.coinmarketcap.com/v1', keyName: 'coinmarketcap', keyIndex: 0, testEndpoint: '/key/info', headerKey: 'X-CMC_PRO_API_KEY', tier: 1 },
      { name: 'CoinMarketCap-2', url: 'https://pro-api.coinmarketcap.com/v1', keyName: 'coinmarketcap', keyIndex: 1, testEndpoint: '/key/info', headerKey: 'X-CMC_PRO_API_KEY', tier: 1 }
    ],
    cryptocompare: [
      { name: 'CryptoCompare', url: 'https://min-api.cryptocompare.com/data', keyName: 'cryptocompare', keyIndex: 0, testEndpoint: '/price?fsym=BTC&tsyms=USD&api_key={{KEY}}', tier: 2 }
    ],
    coinpaprika: [
      { name: 'CoinPaprika', url: 'https://api.coinpaprika.com/v1', testEndpoint: '/ping', requiresKey: false, tier: 2 }
    ],
    coincap: [
      { name: 'CoinCap', url: 'https://api.coincap.io/v2', testEndpoint: '/assets/bitcoin', requiresKey: false, tier: 2 }
    ]
  },

  newsAndSentiment: {
    cryptopanic: [
      { name: 'CryptoPanic', url: 'https://cryptopanic.com/api/v1', testEndpoint: '/posts/?public=true', requiresKey: false, tier: 2 }
    ],
    newsapi: [
      { name: 'NewsAPI', url: 'https://newsapi.org/v2', keyName: 'newsapi', keyIndex: 0, testEndpoint: '/top-headlines?category=business&apiKey={{KEY}}', tier: 2 }
    ],
    alternativeme: [
      { name: 'Fear-Greed-Index', url: 'https://api.alternative.me', testEndpoint: '/fng/?limit=1', requiresKey: false, tier: 2 }
    ],
    reddit: [
      { name: 'Reddit-Crypto', url: 'https://www.reddit.com/r/cryptocurrency', testEndpoint: '/hot.json?limit=1', requiresKey: false, tier: 3 }
    ]
  },

  rpcNodes: {
    ethereum: [
      { name: 'Ankr-ETH', url: 'https://rpc.ankr.com/eth', testEndpoint: '', method: 'POST', rpcTest: true, requiresKey: false, tier: 1 },
      { name: 'PublicNode-ETH', url: 'https://ethereum.publicnode.com', testEndpoint: '', method: 'POST', rpcTest: true, requiresKey: false, tier: 2 },
      { name: 'Cloudflare-ETH', url: 'https://cloudflare-eth.com', testEndpoint: '', method: 'POST', rpcTest: true, requiresKey: false, tier: 2 },
      { name: 'LlamaNodes-ETH', url: 'https://eth.llamarpc.com', testEndpoint: '', method: 'POST', rpcTest: true, requiresKey: false, tier: 3 }
    ],
    bsc: [
      { name: 'BSC-Official', url: 'https://bsc-dataseed.binance.org', testEndpoint: '', method: 'POST', rpcTest: true, requiresKey: false, tier: 2 },
      { name: 'Ankr-BSC', url: 'https://rpc.ankr.com/bsc', testEndpoint: '', method: 'POST', rpcTest: true, requiresKey: false, tier: 2 },
      { name: 'PublicNode-BSC', url: 'https://bsc-rpc.publicnode.com', testEndpoint: '', method: 'POST', rpcTest: true, requiresKey: false, tier: 3 }
    ],
    polygon: [
      { name: 'Polygon-Official', url: 'https://polygon-rpc.com', testEndpoint: '', method: 'POST', rpcTest: true, requiresKey: false, tier: 2 },
      { name: 'Ankr-Polygon', url: 'https://rpc.ankr.com/polygon', testEndpoint: '', method: 'POST', rpcTest: true, requiresKey: false, tier: 2 }
    ],
    tron: [
      { name: 'TronGrid', url: 'https://api.trongrid.io', testEndpoint: '/wallet/getnowblock', method: 'POST', requiresKey: false, tier: 2 },
      { name: 'TronStack', url: 'https://api.tronstack.io', testEndpoint: '/wallet/getnowblock', method: 'POST', requiresKey: false, tier: 3 }
    ]
  },

  onChainAnalytics: [
    { name: 'TheGraph', url: 'https://api.thegraph.com', testEndpoint: '/index-node/graphql', requiresKey: false, tier: 2 },
    { name: 'Blockchair', url: 'https://api.blockchair.com', testEndpoint: '/stats', requiresKey: false, tier: 3 }
  ],

  whaleTracking: [
    { name: 'WhaleAlert-Status', url: 'https://api.whale-alert.io/v1', testEndpoint: '/status', requiresKey: false, tier: 1 }
  ],

  corsProxies: [
    { name: 'AllOrigins', url: 'https://api.allorigins.win', testEndpoint: '/get?url=https://api.coingecko.com/api/v3/ping', requiresKey: false, tier: 3 },
    { name: 'CORS.SH', url: 'https://proxy.cors.sh', testEndpoint: '/https://api.coingecko.com/api/v3/ping', requiresKey: false, tier: 3 },
    { name: 'Corsfix', url: 'https://proxy.corsfix.com', testEndpoint: '/?url=https://api.coingecko.com/api/v3/ping', requiresKey: false, tier: 3 },
    { name: 'ThingProxy', url: 'https://thingproxy.freeboard.io', testEndpoint: '/fetch/https://api.coingecko.com/api/v3/ping', requiresKey: false, tier: 3 }
  ]
};

// ═══════════════════════════════════════════════════════════════
// RESOURCE MONITOR CLASS
// ═══════════════════════════════════════════════════════════════

class CryptoAPIMonitor {
  constructor() {
    this.apiKeys = {};
    this.resourceStatus = {};
    this.metrics = {
      totalChecks: 0,
      successfulChecks: 0,
      failedChecks: 0,
      totalResponseTime: 0
    };
    this.history = {};
    this.alerts = [];
  }

  // Load API keys from registry
  loadRegistry() {
    try {
      const data = fs.readFileSync(CONFIG.REGISTRY_FILE, 'utf8');
      const registry = JSON.parse(data);

      this.apiKeys = registry.discovered_keys || {};
      console.log('✓ Registry loaded successfully');
      console.log(`  Found ${Object.keys(this.apiKeys).length} API key categories`);

      return true;
    } catch (error) {
      console.error('✗ Failed to load registry:', error.message);
      return false;
    }
  }

  // Get API key for resource
  getApiKey(keyName, keyIndex = 0) {
    if (!keyName || !this.apiKeys[keyName]) return null;
    const keys = this.apiKeys[keyName];
    return Array.isArray(keys) ? keys[keyIndex] : keys;
  }

  // Mask API key for display
  maskKey(key) {
    if (!key || key.length < 8) return '****';
    return key.substring(0, 4) + '****' + key.substring(key.length - 4);
  }

  // HTTP request with timeout
  makeRequest(url, options = {}) {
    return new Promise((resolve, reject) => {
      const startTime = Date.now();
      const protocol = url.startsWith('https') ? https : http;

      const req = protocol.request(url, {
        method: options.method || 'GET',
        headers: options.headers || {},
        timeout: CONFIG.TIMEOUT
      }, (res) => {
        let data = '';

        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          const responseTime = Date.now() - startTime;
          resolve({
            statusCode: res.statusCode,
            data: data,
            responseTime: responseTime,
            success: res.statusCode >= 200 && res.statusCode < 300
          });
        });
      });

      req.on('error', (error) => {
        reject({
          error: error.message,
          responseTime: Date.now() - startTime,
          success: false
        });
      });

      req.on('timeout', () => {
        req.destroy();
        reject({
          error: 'Request timeout',
          responseTime: CONFIG.TIMEOUT,
          success: false
        });
      });

      if (options.body) {
        req.write(options.body);
      }

      req.end();
    });
  }

  // Check single API endpoint
  async checkEndpoint(resource) {
    const startTime = Date.now();

    try {
      // Build URL
      let url = resource.url + (resource.testEndpoint || '');

      // Replace API key placeholder
      if (resource.keyName) {
        const apiKey = this.getApiKey(resource.keyName, resource.keyIndex || 0);
        if (apiKey) {
          url = url.replace('{{KEY}}', apiKey);
        }
      }

      // Prepare headers
      const headers = {
        'User-Agent': 'CryptoAPIMonitor/1.0'
      };

      // Add API key to header if needed
      if (resource.headerKey && resource.keyName) {
        const apiKey = this.getApiKey(resource.keyName, resource.keyIndex || 0);
        if (apiKey) {
          headers[resource.headerKey] = apiKey;
        }
      }

      // RPC specific test
      let options = { method: resource.method || 'GET', headers };

      if (resource.rpcTest) {
        options.method = 'POST';
        options.headers['Content-Type'] = 'application/json';
        options.body = JSON.stringify({
          jsonrpc: '2.0',
          method: 'eth_blockNumber',
          params: [],
          id: 1
        });
      }

      // Make request
      const result = await this.makeRequest(url, options);

      return {
        name: resource.name,
        url: resource.url,
        success: result.success,
        statusCode: result.statusCode,
        responseTime: result.responseTime,
        timestamp: new Date().toISOString(),
        tier: resource.tier || 4
      };

    } catch (error) {
      return {
        name: resource.name,
        url: resource.url,
        success: false,
        error: error.error || error.message,
        responseTime: error.responseTime || Date.now() - startTime,
        timestamp: new Date().toISOString(),
        tier: resource.tier || 4
      };
    }
  }

  // Classify status based on metrics
  classifyStatus(resource) {
    if (!this.history[resource.name]) {
      return 'UNKNOWN';
    }

    const hist = this.history[resource.name];
    const recentChecks = hist.slice(-10); // Last 10 checks

    if (recentChecks.length === 0) return 'UNKNOWN';

    const successCount = recentChecks.filter(c => c.success).length;
    const successRate = successCount / recentChecks.length;
    const avgResponseTime = recentChecks
      .filter(c => c.success)
      .reduce((sum, c) => sum + c.responseTime, 0) / (successCount || 1);

    if (successRate >= CONFIG.THRESHOLDS.ONLINE.successRate &&
        avgResponseTime < CONFIG.THRESHOLDS.ONLINE.responseTime) {
      return 'ONLINE';
    } else if (successRate >= CONFIG.THRESHOLDS.DEGRADED.successRate &&
               avgResponseTime < CONFIG.THRESHOLDS.DEGRADED.responseTime) {
      return 'DEGRADED';
    } else if (successRate >= CONFIG.THRESHOLDS.SLOW.successRate &&
               avgResponseTime < CONFIG.THRESHOLDS.SLOW.responseTime) {
      return 'SLOW';
    } else if (successRate >= CONFIG.THRESHOLDS.UNSTABLE.successRate) {
      return 'UNSTABLE';
    } else {
      return 'OFFLINE';
    }
  }

  // Update history for resource
  updateHistory(resource, result) {
    if (!this.history[resource.name]) {
      this.history[resource.name] = [];
    }

    this.history[resource.name].push(result);

    // Keep only last 100 checks
    if (this.history[resource.name].length > 100) {
      this.history[resource.name] = this.history[resource.name].slice(-100);
    }
  }

  // Check all resources in a category
  async checkCategory(categoryName, resources) {
    console.log(`\n  Checking ${categoryName}...`);

    const results = [];

    if (Array.isArray(resources)) {
      for (const resource of resources) {
        const result = await this.checkEndpoint(resource);
        this.updateHistory(resource, result);
        results.push(result);

        // Rate limiting delay
        await new Promise(resolve => setTimeout(resolve, 200));
      }
    } else {
      // Handle nested categories
      for (const [subCategory, subResources] of Object.entries(resources)) {
        for (const resource of subResources) {
          const result = await this.checkEndpoint(resource);
          this.updateHistory(resource, result);
          results.push(result);

          await new Promise(resolve => setTimeout(resolve, 200));
        }
      }
    }

    return results;
  }

  // Run complete monitoring cycle
  async runMonitoringCycle() {
    console.log('\n╔════════════════════════════════════════════════════════╗');
    console.log('║  CRYPTOCURRENCY API RESOURCE MONITOR - Health Check   ║');
    console.log('╚════════════════════════════════════════════════════════╝');
    console.log(`  Timestamp: ${new Date().toISOString()}`);

    const cycleResults = {};

    for (const [category, resources] of Object.entries(API_REGISTRY)) {
      const results = await this.checkCategory(category, resources);
      cycleResults[category] = results;
    }

    this.generateReport(cycleResults);
    this.checkAlertConditions(cycleResults);

    return cycleResults;
  }

  // Generate status report
  generateReport(cycleResults) {
    console.log('\n╔════════════════════════════════════════════════════════╗');
    console.log('║              RESOURCE STATUS REPORT                    ║');
    console.log('╚════════════════════════════════════════════════════════╝\n');

    let totalResources = 0;
    let onlineCount = 0;
    let degradedCount = 0;
    let offlineCount = 0;

    for (const [category, results] of Object.entries(cycleResults)) {
      console.log(`\n📁 ${category.toUpperCase()}`);
      console.log('─'.repeat(60));

      for (const result of results) {
        totalResources++;
        const status = this.classifyStatus(result);

        let statusSymbol = '●';
        let statusColor = '';

        switch (status) {
          case 'ONLINE':
            statusSymbol = '✓';
            onlineCount++;
            break;
          case 'DEGRADED':
          case 'SLOW':
            statusSymbol = '◐';
            degradedCount++;
            break;
          case 'OFFLINE':
          case 'UNSTABLE':
            statusSymbol = '✗';
            offlineCount++;
            break;
        }

        const rt = result.responseTime ? `${result.responseTime}ms` : 'N/A';
        const tierBadge = result.tier === 1 ? '[TIER-1]' : result.tier === 2 ? '[TIER-2]' : '';

        console.log(`  ${statusSymbol} ${result.name.padEnd(25)} ${status.padEnd(10)} ${rt.padStart(8)} ${tierBadge}`);
      }
    }

    // Summary
    console.log('\n╔════════════════════════════════════════════════════════╗');
    console.log('║                    SUMMARY                             ║');
    console.log('╚════════════════════════════════════════════════════════╝');
    console.log(`  Total Resources:    ${totalResources}`);
    console.log(`  Online:             ${onlineCount} (${((onlineCount/totalResources)*100).toFixed(1)}%)`);
    console.log(`  Degraded:           ${degradedCount} (${((degradedCount/totalResources)*100).toFixed(1)}%)`);
    console.log(`  Offline:            ${offlineCount} (${((offlineCount/totalResources)*100).toFixed(1)}%)`);
    console.log(`  Overall Health:     ${((onlineCount/totalResources)*100).toFixed(1)}%`);
  }

  // Check for alert conditions
  checkAlertConditions(cycleResults) {
    const newAlerts = [];

    // Check TIER-1 APIs
    for (const [category, results] of Object.entries(cycleResults)) {
      for (const result of results) {
        if (result.tier === 1 && !result.success) {
          newAlerts.push({
            severity: 'CRITICAL',
            message: `TIER-1 API offline: ${result.name}`,
            timestamp: new Date().toISOString()
          });
        }

        if (result.responseTime > 5000) {
          newAlerts.push({
            severity: 'WARNING',
            message: `Elevated response time: ${result.name} (${result.responseTime}ms)`,
            timestamp: new Date().toISOString()
          });
        }
      }
    }

    if (newAlerts.length > 0) {
      console.log('\n╔════════════════════════════════════════════════════════╗');
      console.log('║                    ⚠️  ALERTS                           ║');
      console.log('╚════════════════════════════════════════════════════════╝');

      for (const alert of newAlerts) {
        console.log(`  [${alert.severity}] ${alert.message}`);
      }

      this.alerts.push(...newAlerts);
    }
  }

  // Generate JSON report
  exportReport(filename = 'api-monitor-report.json') {
    const report = {
      timestamp: new Date().toISOString(),
      summary: {
        totalResources: 0,
        onlineResources: 0,
        degradedResources: 0,
        offlineResources: 0
      },
      categories: {},
      alerts: this.alerts.slice(-50), // Last 50 alerts
      history: this.history
    };

    // Calculate summary
    for (const [category, resources] of Object.entries(API_REGISTRY)) {
      report.categories[category] = [];

      const flatResources = this.flattenResources(resources);

      for (const resource of flatResources) {
        const status = this.classifyStatus(resource);
        const lastCheck = this.history[resource.name] ?
          this.history[resource.name].slice(-1)[0] : null;

        report.summary.totalResources++;

        if (status === 'ONLINE') report.summary.onlineResources++;
        else if (status === 'DEGRADED' || status === 'SLOW') report.summary.degradedResources++;
        else if (status === 'OFFLINE' || status === 'UNSTABLE') report.summary.offlineResources++;

        report.categories[category].push({
          name: resource.name,
          url: resource.url,
          status: status,
          tier: resource.tier,
          lastCheck: lastCheck
        });
      }
    }

    fs.writeFileSync(filename, JSON.stringify(report, null, 2));
    console.log(`\n✓ Report exported to ${filename}`);

    return report;
  }

  // Flatten nested resources
  flattenResources(resources) {
    if (Array.isArray(resources)) {
      return resources;
    }

    const flattened = [];
    for (const subResources of Object.values(resources)) {
      flattened.push(...subResources);
    }
    return flattened;
  }
}

// ═══════════════════════════════════════════════════════════════
// MAIN EXECUTION
// ═══════════════════════════════════════════════════════════════

async function main() {
  const monitor = new CryptoAPIMonitor();

  // Load registry
  if (!monitor.loadRegistry()) {
    console.error('Failed to initialize monitor');
    process.exit(1);
  }

  // Run initial check
  console.log('\n🚀 Starting initial health check...');
  await monitor.runMonitoringCycle();

  // Export report
  monitor.exportReport();

  // Continuous monitoring mode
  if (process.argv.includes('--continuous')) {
    console.log(`\n♾️  Continuous monitoring enabled (interval: ${CONFIG.CHECK_INTERVAL/1000}s)`);

    setInterval(async () => {
      await monitor.runMonitoringCycle();
      monitor.exportReport();
    }, CONFIG.CHECK_INTERVAL);
  } else {
    console.log('\n✓ Monitoring cycle complete');
    console.log('  Use --continuous flag for continuous monitoring');
  }
}

// Run if executed directly
if (require.main === module) {
  main().catch(console.error);
}

module.exports = CryptoAPIMonitor;
