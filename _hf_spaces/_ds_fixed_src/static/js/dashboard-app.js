const numberFormatter = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  maximumFractionDigits: 0,
});
const compactNumber = new Intl.NumberFormat('en-US', {
  notation: 'compact',
  maximumFractionDigits: 1,
});
const $ = (id) => document.getElementById(id);
const feedback = () => window.UIFeedback || {};

function renderTopPrices(data = [], source = 'live') {
  const tbody = $('top-prices-table');
  if (!tbody) return;
  if (!data.length) {
    feedback().fadeReplace?.(
      tbody,
      '<tr><td colspan="4" class="empty-state">No price data available.</td></tr>',
    );
    return;
  }
  const rows = data
    .map((item) => {
      const change = Number(item.price_change_percentage_24h ?? 0);
      const tone = change >= 0 ? 'success' : 'danger';
      return `<tr>
        <td><strong>${item.symbol}</strong></td>
        <td>${numberFormatter.format(item.current_price || item.price || 0)}</td>
        <td><span class="badge ${tone}">${change.toFixed(2)}%</span></td>
        <td>${compactNumber.format(item.total_volume || item.volume_24h || 0)}</td>
      </tr>`;
    })
    .join('');
  feedback().fadeReplace?.(tbody, rows);
  feedback().setBadge?.(
    $('top-prices-source'),
    `Source: ${source}`,
    source === 'local-fallback' ? 'warning' : 'success',
  );
}

function renderMarketOverview(payload) {
  if (!payload) return;
  $('metric-market-cap').textContent = numberFormatter.format(payload.total_market_cap || 0);
  $('metric-volume').textContent = numberFormatter.format(payload.total_volume_24h || 0);
  $('metric-btc-dom').textContent = `${(payload.btc_dominance || 0).toFixed(2)}%`;
  $('metric-cap-source').textContent = `Assets: ${payload.top_by_volume?.length || 0}`;
  $('metric-volume-source').textContent = `Markets: ${payload.markets || 0}`;
  const gainers = payload.top_gainers?.slice(0, 3) || [];
  const losers = payload.top_losers?.slice(0, 3) || [];
  $('market-overview-list').innerHTML = `
    <li><span>Top Gainers</span><span>${gainers
      .map((g) => `${g.symbol} ${g.price_change_percentage_24h?.toFixed(1) ?? 0}%`)
      .join(', ')}</span></li>
    <li><span>Top Losers</span><span>${losers
      .map((g) => `${g.symbol} ${g.price_change_percentage_24h?.toFixed(1) ?? 0}%`)
      .join(', ')}</span></li>
    <li><span>Liquidity Leaders</span><span>${payload.top_by_volume
      ?.slice(0, 3)
      .map((p) => p.symbol)
      .join(', ')}</span></li>
  `;
  $('intro-source').textContent = payload.source === 'local-fallback' ? 'Source: Local Fallback JSON' : 'Source: Live Providers';
  feedback().setBadge?.(
    $('market-overview-source'),
    `Source: ${payload.source || 'live'}`,
    payload.source === 'local-fallback' ? 'warning' : 'info',
  );
}

function renderSystemStatus(health, status, rateLimits, config) {
  if (health) {
    const tone =
      health.status === 'healthy' ? 'success' : health.status === 'degraded' ? 'warning' : 'danger';
    $('metric-health').textContent = health.status.toUpperCase();
    $('metric-health-details').textContent = `${(health.services?.market_data?.status || 'n/a').toUpperCase()} MARKET | ${(health.services?.news?.status || 'n/a').toUpperCase()} NEWS`;
    $('system-health-status').textContent = `Providers loaded: ${
      health.providers_loaded || health.services?.providers?.count || 0
    }`;
    feedback().setBadge?.($('system-status-source'), `/health: ${health.status}`, tone);
  }
  if (status) {
    $('system-status-list').innerHTML = `
      <li><span>Providers online</span><span>${status.providers_online || 0}</span></li>
      <li><span>Cache size</span><span>${status.cache_size || 0}</span></li>
      <li><span>Uptime</span><span>${Math.round(status.uptime_seconds || 0)}s</span></li>
    `;
  }
  if (config) {
    const configEntries = [
      ['Version', config.version || '--'],
      ['API Version', config.api_version || '--'],
      ['Symbols', (config.supported_symbols || []).slice(0, 5).join(', ') || '--'],
      ['Intervals', (config.supported_intervals || []).join(', ') || '--'],
    ];
    $('system-config-list').innerHTML = configEntries
      .map(([label, value]) => `<li><span>${label}</span><span>${value}</span></li>`)
      .join('');
  } else {
    $('system-config-list').innerHTML = '<li class="empty-state"><span>No configuration loaded.</span></li>';
  }
  if (rateLimits) {
    $('rate-limits-list').innerHTML =
      rateLimits.rate_limits
        ?.map((rule) => `<li><span>${rule.endpoint}</span><span>${rule.limit}/${rule.window}</span></li>`)
        .join('') || '<li><span>No limits configured</span><span></span></li>';
  }
}

function renderHFWidget(health, registry) {
  if (health) {
    const tone =
      health.status === 'healthy' ? 'success' : health.status === 'degraded' ? 'warning' : 'danger';
    feedback().setBadge?.($('hf-health-status'), `HF ${health.status}`, tone);
    $('hf-widget-summary').textContent = `Config ready: ${
      health.services?.config ? 'Yes' : 'No'
    } | Models: ${registry?.items?.length || 0}`;
  }
  const items = registry?.items?.slice(0, 4) || [];
  $('hf-registry-list').innerHTML =
    items
      .map((item) => `<li><span>${item}</span><span class="badge info">Model</span></li>`)
      .join('') || '<li class="empty-state"><span>No registry data.</span></li>';
}

function pushStream(payload) {
  const stream = $('ws-stream');
  if (!stream) return;
  const node = document.createElement('div');
  node.className = 'stream-item fade-in';
  const topCoin = payload.market_data?.[0]?.symbol || 'n/a';
  const sentiment = payload.sentiment
    ? `${payload.sentiment.label || payload.sentiment.result || ''} (${(
        payload.sentiment.confidence || 0
      ).toFixed?.(2) || payload.sentiment.confidence || ''})`
    : 'n/a';
  node.innerHTML = `<strong>${new Date().toLocaleTimeString()}</strong>
    <div style="color:var(--ui-text-muted);margin-top:6px;">${topCoin} | Sentiment: ${sentiment}</div>
    <div style="margin-top:8px;display:flex;gap:8px;flex-wrap:wrap;">${
      (payload.market_data || [])
        .slice(0, 3)
        .map(
          (coin) => `<span class="badge ${
            coin.price_change_percentage_24h >= 0 ? 'success' : 'danger'
          }">${coin.symbol} ${coin.price_change_percentage_24h?.toFixed(1) || 0}%</span>`,
        )
        .join('') || '<span class="badge info">Awaiting data</span>'
    }</div>`;
  stream.prepend(node);
  while (stream.children.length > 6) stream.removeChild(stream.lastChild);
}

function connectWebSocket() {
  const badge = $('ws-status');
  const url = `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/ws`;
  try {
    const socket = new WebSocket(url);
    socket.addEventListener('open', () => feedback().setBadge?.(badge, 'Connected', 'success'));
    socket.addEventListener('message', (event) => {
      try {
        const message = JSON.parse(event.data);
        if (message.type === 'connected') {
          feedback().setBadge?.(badge, `Client ${message.client_id.slice(0, 6)}...`, 'info');
        }
        if (message.type === 'update') pushStream(message.payload);
      } catch (err) {
        feedback().toast?.('error', 'WS parse error', err.message);
      }
    });
    socket.addEventListener('close', () => feedback().setBadge?.(badge, 'Disconnected', 'warning'));
  } catch (err) {
    feedback().toast?.('error', 'WebSocket failed', err.message);
    feedback().setBadge?.(badge, 'Unavailable', 'danger');
  }
}

async function initDashboard() {
  feedback().showLoading?.($('top-prices-table'), 'Loading market data...');
  feedback().showLoading?.($('market-overview-list'), 'Loading overview...');
  try {
    const [{ data: topData, source }, overview] = await Promise.all([
      feedback().fetchJSON?.('/api/crypto/prices/top?limit=8', {}, 'Top prices'),
      feedback().fetchJSON?.('/api/crypto/market-overview', {}, 'Market overview'),
    ]);
    renderTopPrices(topData, source);
    renderMarketOverview(overview);
  } catch {
    renderTopPrices([], 'local-fallback');
  }

  try {
    const [health, status, rateLimits, config] = await Promise.all([
      feedback().fetchJSON?.('/health', {}, 'Health'),
      feedback().fetchJSON?.('/api/system/status', {}, 'System status'),
      feedback().fetchJSON?.('/api/rate-limits', {}, 'Rate limits'),
      feedback().fetchJSON?.('/api/system/config', {}, 'System config'),
    ]);
    renderSystemStatus(health, status, rateLimits, config);
  } catch {}

  try {
    const [hfHealth, hfRegistry] = await Promise.all([
      feedback().fetchJSON?.('/api/hf/health', {}, 'HF health'),
      feedback().fetchJSON?.('/api/hf/registry?kind=models', {}, 'HF registry'),
    ]);
    renderHFWidget(hfHealth, hfRegistry);
  } catch {
    feedback().setBadge?.($('hf-health-status'), 'HF unavailable', 'warning');
  }

  connectWebSocket();
}

document.addEventListener('DOMContentLoaded', initDashboard);
