/**
 * Fear & Greed Index Fix for Dashboard
 * Add this to fix the loading issue
 */

export async function loadFearGreedIndex() {
  try {
    console.log('[Fear & Greed] Loading index...');
    
    // Try primary API
    let response = await fetch('https://api.alternative.me/fng/?limit=1');
    
    if (!response.ok) {
      console.warn('[Fear & Greed] Primary API failed, trying fallback...');
      // Try our backend API
      response = await fetch('/api/sentiment/global');
    }
    
    if (!response.ok) {
      throw new Error('All APIs failed');
    }
    
    const data = await response.json();
    
    // Parse response
    let value = 50;
    let timestamp = new Date().toISOString();
    
    if (data.data && data.data[0]) {
      // Alternative.me format
      value = parseInt(data.data[0].value);
      timestamp = data.data[0].timestamp;
    } else if (data.fear_greed_index) {
      // Our backend format
      value = data.fear_greed_index;
    }
    
    console.log('[Fear & Greed] Loaded value:', value);
    
    // Render the gauge
    renderFearGreedGauge(value);
    
    // Update text elements
    updateFearGreedText(value, timestamp);
    
    return { value, timestamp };
  } catch (error) {
    console.error('[Fear & Greed] Load error:', error);
    
    // Use fallback value
    const fallbackValue = 50;
    renderFearGreedGauge(fallbackValue);
    updateFearGreedText(fallbackValue, new Date().toISOString());
    
    return { value: fallbackValue, timestamp: new Date().toISOString() };
  }
}

function renderFearGreedGauge(value) {
  const gauge = document.getElementById('sentiment-gauge');
  if (!gauge) {
    console.warn('[Fear & Greed] Gauge element not found');
    return;
  }

  let label = 'Neutral', color = '#eab308';
  if (value < 25) { label = 'Extreme Fear'; color = '#ef4444'; }
  else if (value < 45) { label = 'Fear'; color = '#f97316'; }
  else if (value < 55) { label = 'Neutral'; color = '#eab308'; }
  else if (value < 75) { label = 'Greed'; color = '#22c55e'; }
  else { label = 'Extreme Greed'; color = '#10b981'; }

  gauge.innerHTML = `
    <div class="gauge-container">
      <div class="gauge-bar">
        <div class="gauge-fill" style="width: ${value}%; background: ${color}; transition: width 0.5s ease;"></div>
        <div class="gauge-indicator" style="left: ${value}%; transition: left 0.5s ease;">
          <span class="gauge-value">${value}</span>
        </div>
      </div>
      <div class="gauge-labels">
        <span style="color: #ef4444;">Extreme Fear</span>
        <span style="color: #eab308;">Neutral</span>
        <span style="color: #10b981;">Extreme Greed</span>
      </div>
      <div class="gauge-result" style="color: ${color}; font-size: 1.25rem; font-weight: 700; margin-top: 1rem;">
        ${label}
      </div>
    </div>
  `;
}

function updateFearGreedText(value, timestamp) {
  // Update value display
  const valueEl = document.getElementById('fng-value');
  if (valueEl) {
    valueEl.textContent = value;
    valueEl.style.fontSize = '2rem';
    valueEl.style.fontWeight = '700';
  }
  
  // Update sentiment text
  const sentimentEl = document.getElementById('fng-sentiment');
  if (sentimentEl) {
    let label = 'Neutral';
    if (value < 25) label = 'Extreme Fear';
    else if (value < 45) label = 'Fear';
    else if (value < 55) label = 'Neutral';
    else if (value < 75) label = 'Greed';
    else label = 'Extreme Greed';
    
    sentimentEl.textContent = label;
  }
  
  // Update timestamp
  const timeEl = document.getElementById('fng-timestamp');
  if (timeEl) {
    const date = new Date(timestamp);
    timeEl.textContent = `Updated: ${date.toLocaleTimeString()}`;
  }
}

// Auto-refresh every 5 minutes
export function startFearGreedAutoRefresh() {
  loadFearGreedIndex();
  setInterval(() => {
    loadFearGreedIndex();
  }, 5 * 60 * 1000); // 5 minutes
}

// Export for use in dashboard
window.loadFearGreedIndex = loadFearGreedIndex;
window.startFearGreedAutoRefresh = startFearGreedAutoRefresh;
