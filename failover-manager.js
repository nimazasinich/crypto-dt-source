#!/usr/bin/env node

/**
 * FAILOVER CHAIN MANAGER
 * Builds redundancy chains and manages automatic failover for API resources
 */

const fs = require('fs');

class FailoverManager {
  constructor(reportPath = './api-monitor-report.json') {
    this.reportPath = reportPath;
    this.report = null;
    this.failoverChains = {};
  }

  // Load monitoring report
  loadReport() {
    try {
      const data = fs.readFileSync(this.reportPath, 'utf8');
      this.report = JSON.parse(data);
      return true;
    } catch (error) {
      console.error('Failed to load report:', error.message);
      return false;
    }
  }

  // Build failover chains for each data type
  buildFailoverChains() {
    console.log('\n╔════════════════════════════════════════════════════════╗');
    console.log('║         FAILOVER CHAIN BUILDER                         ║');
    console.log('╚════════════════════════════════════════════════════════╝\n');

    const chains = {
      ethereumPrice: this.buildPriceChain('ethereum'),
      bitcoinPrice: this.buildPriceChain('bitcoin'),
      ethereumExplorer: this.buildExplorerChain('ethereum'),
      bscExplorer: this.buildExplorerChain('bsc'),
      tronExplorer: this.buildExplorerChain('tron'),
      rpcEthereum: this.buildRPCChain('ethereum'),
      rpcBSC: this.buildRPCChain('bsc'),
      newsFeeds: this.buildNewsChain(),
      sentiment: this.buildSentimentChain()
    };

    this.failoverChains = chains;

    // Display chains
    for (const [chainName, chain] of Object.entries(chains)) {
      this.displayChain(chainName, chain);
    }

    return chains;
  }

  // Build price data failover chain
  buildPriceChain(coin) {
    const chain = [];

    // Get market data resources
    const marketResources = this.report?.categories?.marketData || [];

    // Sort by status and tier
    const sorted = marketResources
      .filter(r => ['ONLINE', 'DEGRADED'].includes(r.status))
      .sort((a, b) => {
        // Prioritize by tier first
        if (a.tier !== b.tier) return a.tier - b.tier;

        // Then by status
        const statusPriority = { ONLINE: 1, DEGRADED: 2, SLOW: 3 };
        return statusPriority[a.status] - statusPriority[b.status];
      });

    for (const resource of sorted) {
      chain.push({
        name: resource.name,
        url: resource.url,
        status: resource.status,
        tier: resource.tier,
        responseTime: resource.lastCheck?.responseTime
      });
    }

    return chain;
  }

  // Build explorer failover chain
  buildExplorerChain(blockchain) {
    const chain = [];
    const explorerResources = this.report?.categories?.blockchainExplorers || [];

    const filtered = explorerResources
      .filter(r => {
        const name = r.name.toLowerCase();
        return (blockchain === 'ethereum' && name.includes('eth')) ||
               (blockchain === 'bsc' && name.includes('bsc')) ||
               (blockchain === 'tron' && name.includes('tron'));
      })
      .filter(r => ['ONLINE', 'DEGRADED'].includes(r.status))
      .sort((a, b) => a.tier - b.tier);

    for (const resource of filtered) {
      chain.push({
        name: resource.name,
        url: resource.url,
        status: resource.status,
        tier: resource.tier,
        responseTime: resource.lastCheck?.responseTime
      });
    }

    return chain;
  }

  // Build RPC node failover chain
  buildRPCChain(network) {
    const chain = [];
    const rpcResources = this.report?.categories?.rpcNodes || [];

    const filtered = rpcResources
      .filter(r => {
        const name = r.name.toLowerCase();
        return name.includes(network.toLowerCase());
      })
      .filter(r => ['ONLINE', 'DEGRADED'].includes(r.status))
      .sort((a, b) => {
        if (a.tier !== b.tier) return a.tier - b.tier;
        return (a.lastCheck?.responseTime || 999999) - (b.lastCheck?.responseTime || 999999);
      });

    for (const resource of filtered) {
      chain.push({
        name: resource.name,
        url: resource.url,
        status: resource.status,
        tier: resource.tier,
        responseTime: resource.lastCheck?.responseTime
      });
    }

    return chain;
  }

  // Build news feed failover chain
  buildNewsChain() {
    const chain = [];
    const newsResources = this.report?.categories?.newsAndSentiment || [];

    const filtered = newsResources
      .filter(r => ['ONLINE', 'DEGRADED'].includes(r.status))
      .sort((a, b) => a.tier - b.tier);

    for (const resource of filtered) {
      chain.push({
        name: resource.name,
        url: resource.url,
        status: resource.status,
        tier: resource.tier,
        responseTime: resource.lastCheck?.responseTime
      });
    }

    return chain;
  }

  // Build sentiment data failover chain
  buildSentimentChain() {
    const chain = [];
    const newsResources = this.report?.categories?.newsAndSentiment || [];

    const filtered = newsResources
      .filter(r => r.name.toLowerCase().includes('fear') ||
                   r.name.toLowerCase().includes('greed') ||
                   r.name.toLowerCase().includes('sentiment'))
      .filter(r => ['ONLINE', 'DEGRADED'].includes(r.status));

    for (const resource of filtered) {
      chain.push({
        name: resource.name,
        url: resource.url,
        status: resource.status,
        tier: resource.tier,
        responseTime: resource.lastCheck?.responseTime
      });
    }

    return chain;
  }

  // Display failover chain
  displayChain(chainName, chain) {
    console.log(`\n📊 ${chainName.toUpperCase()} Failover Chain:`);
    console.log('─'.repeat(60));

    if (chain.length === 0) {
      console.log('  ⚠️  No available resources');
      return;
    }

    chain.forEach((resource, index) => {
      const arrow = index === 0 ? '🎯' : '  ↓';
      const priority = index === 0 ? '[PRIMARY]' : index === 1 ? '[BACKUP]' : `[BACKUP-${index}]`;
      const tierBadge = `[TIER-${resource.tier}]`;
      const rt = resource.responseTime ? `${resource.responseTime}ms` : 'N/A';

      console.log(`  ${arrow} ${priority.padEnd(12)} ${resource.name.padEnd(25)} ${resource.status.padEnd(10)} ${rt.padStart(8)} ${tierBadge}`);
    });
  }

  // Generate failover configuration file
  exportFailoverConfig(filename = 'failover-config.json') {
    const config = {
      generatedAt: new Date().toISOString(),
      chains: this.failoverChains,
      usage: {
        description: 'Automatic failover configuration for API resources',
        example: `
// Example usage in your application:
const failoverConfig = require('./failover-config.json');

async function fetchWithFailover(chainName, fetchFunction) {
  const chain = failoverConfig.chains[chainName];

  for (const resource of chain) {
    try {
      const result = await fetchFunction(resource.url);
      return result;
    } catch (error) {
      console.log(\`Failed \${resource.name}, trying next...\`);
      continue;
    }
  }

  throw new Error('All resources in chain failed');
}

// Use it:
const data = await fetchWithFailover('ethereumPrice', async (url) => {
  const response = await fetch(url + '/api/v3/simple/price?ids=ethereum&vs_currencies=usd');
  return response.json();
});
`
      }
    };

    fs.writeFileSync(filename, JSON.stringify(config, null, 2));
    console.log(`\n✓ Failover configuration exported to ${filename}`);
  }

  // Identify categories with single point of failure
  identifySinglePointsOfFailure() {
    console.log('\n╔════════════════════════════════════════════════════════╗');
    console.log('║       SINGLE POINT OF FAILURE ANALYSIS                ║');
    console.log('╚════════════════════════════════════════════════════════╝\n');

    const spofs = [];

    for (const [chainName, chain] of Object.entries(this.failoverChains)) {
      const onlineCount = chain.filter(r => r.status === 'ONLINE').length;

      if (onlineCount === 0) {
        spofs.push({
          chain: chainName,
          severity: 'CRITICAL',
          message: 'Zero available resources'
        });
      } else if (onlineCount === 1) {
        spofs.push({
          chain: chainName,
          severity: 'HIGH',
          message: 'Only one resource available (SPOF)'
        });
      } else if (onlineCount === 2) {
        spofs.push({
          chain: chainName,
          severity: 'MEDIUM',
          message: 'Only two resources available'
        });
      }
    }

    if (spofs.length === 0) {
      console.log('  ✓ No single points of failure detected\n');
    } else {
      for (const spof of spofs) {
        const icon = spof.severity === 'CRITICAL' ? '🔴' :
                     spof.severity === 'HIGH' ? '🟠' : '🟡';
        console.log(`  ${icon} [${spof.severity}] ${spof.chain}: ${spof.message}`);
      }
      console.log();
    }

    return spofs;
  }

  // Generate redundancy report
  generateRedundancyReport() {
    console.log('\n╔════════════════════════════════════════════════════════╗');
    console.log('║            REDUNDANCY ANALYSIS REPORT                  ║');
    console.log('╚════════════════════════════════════════════════════════╝\n');

    const categories = this.report?.categories || {};

    for (const [category, resources] of Object.entries(categories)) {
      const total = resources.length;
      const online = resources.filter(r => r.status === 'ONLINE').length;
      const degraded = resources.filter(r => r.status === 'DEGRADED').length;
      const offline = resources.filter(r => r.status === 'OFFLINE').length;

      let indicator = '✓';
      if (online === 0) indicator = '✗';
      else if (online === 1) indicator = '⚠';
      else if (online >= 3) indicator = '✓✓';

      console.log(`  ${indicator} ${category.padEnd(25)} Online: ${online}/${total}  Degraded: ${degraded}  Offline: ${offline}`);
    }
  }
}

// ═══════════════════════════════════════════════════════════════
// MAIN EXECUTION
// ═══════════════════════════════════════════════════════════════

async function main() {
  const manager = new FailoverManager();

  if (!manager.loadReport()) {
    console.error('\n✗ Please run the monitor first: node api-monitor.js');
    process.exit(1);
  }

  // Build failover chains
  manager.buildFailoverChains();

  // Export configuration
  manager.exportFailoverConfig();

  // Identify SPOFs
  manager.identifySinglePointsOfFailure();

  // Generate redundancy report
  manager.generateRedundancyReport();

  console.log('\n✓ Failover analysis complete\n');
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = FailoverManager;
