const adminFeedback = () => window.UIFeedback || {};
const $ = (id) => document.getElementById(id);

function renderProviders(providers = []) {
  const table = $('providers-table');
  if (!table) return;
  if (!providers.length) {
    table.innerHTML = '<tr><td colspan="4" class="empty-state">No providers configured.</td></tr>';
    return;
  }
  table.innerHTML = providers
    .map((provider) => `
      <tr data-provider-id="${provider.provider_id || provider.name}">
        <td>${provider.name || provider.provider_id}</td>
        <td><span class="badge ${provider.status || 'info'}">${provider.status || 'unknown'}</span></td>
        <td>${provider.response_time_ms ?? '-'}</td>
        <td>${provider.category || provider.provider_category || 'n/a'}</td>
      </tr>`)
    .join('');
}

function renderDetail(detail) {
  if (!detail) return;
  $('selected-provider').textContent = detail.provider_id || detail.name;
  $('provider-detail-list').innerHTML = `
    <li><span>Status</span><span><span class="badge ${detail.status || 'info'}">${
    detail.status || 'unknown'
  }</span></span></li>
    <li><span>Response</span><span>${detail.response_time_ms ?? 0} ms</span></li>
    <li><span>Priority</span><span>${detail.priority ?? 'n/a'}</span></li>
    <li><span>Auth</span><span>${detail.requires_auth ? 'Yes' : 'No'}</span></li>
    <li><span>Base URL</span><span style="font-size:0.78rem;color:var(--ui-text-muted);">${
      detail.base_url || '-'
    }</span></li>`;
}

function renderConfig(config) {
  $('config-summary').textContent = `${config.total || 0} providers`;
  $('config-list').innerHTML =
    Object.entries(config.providers || {})
      .slice(0, 8)
      .map(([key, value]) => `<li><span>${value.name || key}</span><span>${value.category || value.chain || 'n/a'}</span></li>`)
      .join('') || '<li class="empty-state"><span>No config loaded.</span></li>';
}

function renderLogs(logs = []) {
  $('logs-list').innerHTML =
    logs
      .map((log) => `<div class="stream-item"><strong>${log.timestamp || ''}</strong><div>${log.endpoint || ''} Â| ${log.status || ''}</div></div>`)
      .join('') || '<div class="stream-item empty-state">No logs yet.</div>';
}

function renderAlerts(alerts = []) {
  $('alerts-list').innerHTML =
    alerts
      .map((alert) => `<div class="alert ${alert.severity || 'info'}"><span>${alert.message || ''}</span><span>${alert.timestamp || ''}</span></div>`)
      .join('') || '<div class="alert info">No alerts at the moment.</div>';
}

async function bootstrapAdmin() {
  adminFeedback().showLoading?.($('providers-table'), 'Loading providersâ€¦');
  try {
    const payload = await adminFeedback().fetchJSON?.('/api/providers', {}, 'Providers');
    renderProviders(payload.providers);
    $('providers-count').textContent = `${payload.total || payload.providers?.length || 0} providers`;
    $('providers-table').addEventListener('click', async (event) => {
      const row = event.target.closest('tr[data-provider-id]');
      if (!row) return;
      const providerId = row.dataset.providerId;
      adminFeedback().showLoading?.($('provider-detail-list'), 'Fetching detailsâ€¦');
      try {
        const detail = await adminFeedback().fetchJSON?.(
          `/api/providers/${encodeURIComponent(providerId)}/health`,
          {},
          'Provider health',
        );
        renderDetail({ provider_id: providerId, ...detail });
      } catch {}
    });
  } catch {}

  try {
    const config = await adminFeedback().fetchJSON?.('/api/providers/config', {}, 'Providers config');
    renderConfig(config);
  } catch {}

  try {
    const logs = await adminFeedback().fetchJSON?.('/api/logs?limit=20', {}, 'Logs');
    renderLogs(logs.logs || logs);
  } catch {
    renderLogs([]);
  }

  try {
    const alerts = await adminFeedback().fetchJSON?.('/api/alerts', {}, 'Alerts');
    renderAlerts(alerts.alerts || []);
  } catch {
    renderAlerts([]);
  }
}

document.addEventListener('DOMContentLoaded', bootstrapAdmin);
