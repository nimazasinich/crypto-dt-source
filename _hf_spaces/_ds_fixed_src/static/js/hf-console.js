const hfFeedback = () => window.UIFeedback || {};
const $ = (id) => document.getElementById(id);

async function loadRegistry() {
  try {
    const [health, registry] = await Promise.all([
      hfFeedback().fetchJSON?.('/api/hf/health', {}, 'HF health'),
      hfFeedback().fetchJSON?.('/api/hf/registry?kind=models', {}, 'HF registry'),
    ]);
    hfFeedback().setBadge?.(
      $('hf-console-health'),
      `HF ${health.status}`,
      health.status === 'healthy' ? 'success' : health.status === 'degraded' ? 'warning' : 'danger',
    );
    $('hf-console-summary').textContent = `Models available: ${registry.items?.length || 0}`;
    $('hf-console-models').innerHTML =
      registry.items
        ?.map((model) => `<li><span>${model}</span><span class="badge info">Model</span></li>`)
        .join('') || '<li class="empty-state">No registry entries yet.</li>';
  } catch {
    $('hf-console-models').innerHTML = '<li class="empty-state">Unable to load registry.</li>';
    hfFeedback().setBadge?.($('hf-console-health'), 'HF unavailable', 'warning');
  }
}

async function runSentiment() {
  const button = $('run-sentiment');
  button.disabled = true;
  const modelName = $('sentiment-model').value;
  const texts = $('sentiment-texts').value
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean);
  hfFeedback().showLoading?.($('sentiment-results'), 'Running sentiment…');
  try {
    const payload = { model: modelName, texts };
    const response = await hfFeedback().fetchJSON?.('/api/hf/models/sentiment', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    $('sentiment-results').innerHTML =
      response.results
        ?.map((entry) => `<div class="stream-item"><strong>${entry.text}</strong><pre>${JSON.stringify(entry.result, null, 2)}</pre></div>`)
        .join('') || '<div class="stream-item empty-state">No sentiment data.</div>';
    hfFeedback().toast?.('success', 'Sentiment complete', `${response.results?.length || 0} text(s)`);
  } catch (err) {
    $('sentiment-results').innerHTML = `<div class="stream-item empty-state">${err.message}</div>`;
  } finally {
    button.disabled = false;
  }
}

async function runForecast() {
  const button = $('run-forecast');
  button.disabled = true;
  const series = $('forecast-series').value
    .split(',')
    .map((val) => val.trim())
    .filter(Boolean);
  const model = $('forecast-model').value;
  const steps = parseInt($('forecast-steps').value, 10) || 3;
  hfFeedback().showLoading?.($('forecast-results'), 'Requesting forecast…');
  try {
    const payload = { model, series, steps };
    const response = await hfFeedback().fetchJSON?.('/api/hf/models/forecast', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    $('forecast-results').innerHTML = `<div class="stream-item"><strong>${response.model}</strong><div>Predictions: ${response.predictions.join(', ')}</div><small style="color:var(--ui-text-muted);">Volatility ${response.volatility}</small></div>`;
    hfFeedback().toast?.('success', 'Forecast ready', `${response.predictions.length} points`);
  } catch (err) {
    $('forecast-results').innerHTML = `<div class="stream-item empty-state">${err.message}</div>`;
  } finally {
    button.disabled = false;
  }
}

const datasetRoutes = {
  'market-ohlcv': '/api/hf/datasets/market/ohlcv?symbol=BTC&interval=1h&limit=50',
  'market-btc': '/api/hf/datasets/market/btc_technical?limit=60',
  'news-semantic': '/api/hf/datasets/news/semantic?limit=10',
};

async function loadDataset(key) {
  const route = datasetRoutes[key];
  if (!route) return;
  hfFeedback().showLoading?.($('dataset-output'), 'Loading dataset…');
  try {
    const data = await hfFeedback().fetchJSON?.(route, {}, 'HF dataset');
    const items = data.items || data.data || [];
    $('dataset-output').innerHTML =
      items
        .slice(0, 6)
        .map((item) => `<div class="stream-item"><pre>${JSON.stringify(item, null, 2)}</pre></div>`)
        .join('') || '<div class="stream-item empty-state">Dataset returned no rows.</div>';
  } catch (err) {
    $('dataset-output').innerHTML = `<div class="stream-item empty-state">${err.message}</div>`;
  }
}

function wireDatasetButtons() {
  document.querySelectorAll('[data-dataset]').forEach((button) => {
    button.addEventListener('click', () => loadDataset(button.dataset.dataset));
  });
}

function initHFConsole() {
  loadRegistry();
  $('run-sentiment').addEventListener('click', runSentiment);
  $('run-forecast').addEventListener('click', runForecast);
  wireDatasetButtons();
}

document.addEventListener('DOMContentLoaded', initHFConsole);
