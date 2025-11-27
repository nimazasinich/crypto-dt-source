// Crypto API Hub Dashboard JavaScript

const svgIcons = {
    chain: '<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>',
    chart: '<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><line x1="12" y1="20" x2="12" y2="10"></line><line x1="18" y1="20" x2="18" y2="4"></line><line x1="6" y1="20" x2="6" y2="16"></line></svg>',
    news: '<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2"></path><path d="M18 14h-8"></path><path d="M15 18h-5"></path><path d="M10 6h8v4h-8V6Z"></path></svg>',
    brain: '<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.98-3A2.5 2.5 0 0 1 9.5 2Z"></path><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.98-3A2.5 2.5 0 0 0 14.5 2Z"></path></svg>',
    analytics: '<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><path d="M3 3v18h18"></path><path d="m19 9-5 5-4-4-3 3"></path></svg>'
};

let SERVICES = {};
let currentMethod = 'GET';
let currentFilter = 'all';
let isLoading = false;

// Load services from backend
async function loadServices() {
    isLoading = true;
    const loadingEl = document.getElementById('loadingIndicator');
    const gridEl = document.getElementById('servicesGrid');

    loadingEl.style.display = 'block';
    gridEl.style.display = 'none';

    try {
        const response = await fetch('/api/crypto-hub/services');
        const data = await response.json();

        if (data.services) {
            SERVICES = data.services;

            // Update stats
            const totalServices = Object.values(SERVICES).flat().length;
            const totalEndpoints = Object.values(SERVICES)
                .flat()
                .reduce((sum, service) => sum + service.endpoints.length, 0);
            const totalKeys = Object.values(SERVICES)
                .flat()
                .filter(service => service.key && service.key.length > 0)
                .length;

            document.getElementById('stat-services').textContent = totalServices;
            document.getElementById('stat-endpoints').textContent = totalEndpoints + '+';
            document.getElementById('stat-keys').textContent = totalKeys;

            renderServices();
        }
    } catch (error) {
        console.error('Error loading services:', error);
        showToast('❌', 'Failed to load services');

        // Load from local file as fallback
        loadServicesFromLocal();
    } finally {
        isLoading = false;
        loadingEl.style.display = 'none';
        gridEl.style.display = 'grid';
    }
}

// Load services from local JSON file
async function loadServicesFromLocal() {
    try {
        const response = await fetch('/crypto_api_hub_services.json');
        const data = await response.json();

        if (data.services) {
            SERVICES = data.services;
            renderServices();
        }
    } catch (error) {
        console.error('Error loading local services:', error);
        showToast('❌', 'Failed to load services from local file');
    }
}

function getIcon(category) {
    const icons = {
        explorer: svgIcons.chain,
        market: svgIcons.chart,
        news: svgIcons.news,
        sentiment: svgIcons.brain,
        analytics: svgIcons.analytics
    };
    return icons[category] || svgIcons.chain;
}

function renderServices() {
    const grid = document.getElementById('servicesGrid');
    let html = '';

    Object.entries(SERVICES).forEach(([category, services]) => {
        services.forEach(service => {
            if (currentFilter !== 'all' && category !== currentFilter) return;

            const hasKey = service.key ? `<span class="badge badge-key">🔑 Has Key</span>` : '';
            const endpoints = service.endpoints.length;

            html += `
                <div class="service-card" data-category="${category}" data-name="${service.name.toLowerCase()}">
                    <div class="service-header">
                        <div class="service-icon">${getIcon(category)}</div>
                        <div class="service-info">
                            <div class="service-name">${service.name}</div>
                            <div class="service-url">${service.url}</div>
                        </div>
                    </div>
                    <div class="service-badges">
                        <span class="badge badge-category">${category}</span>
                        ${endpoints > 0 ? `<span class="badge badge-endpoints">${endpoints} endpoints</span>` : ''}
                        ${hasKey}
                    </div>
                    ${endpoints > 0 ? `
                        <div class="endpoints-list">
                            ${service.endpoints.slice(0, 2).map(ep => `
                                <div class="endpoint-item">
                                    <div class="endpoint-path">${escapeHtml(ep)}</div>
                                    <div class="endpoint-actions">
                                        <button class="btn-sm" onclick='copyText("${escapeQuotes(service.url + ep)}")'>
                                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                                                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                                            </svg>
                                            Copy
                                        </button>
                                        <button class="btn-sm" onclick='testEndpoint("${escapeQuotes(service.url + ep)}", "${escapeQuotes(service.key)}")'>
                                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
                                            </svg>
                                            Test
                                        </button>
                                    </div>
                                </div>
                            `).join('')}
                            ${endpoints > 2 ? `<div style="text-align: center; color: var(--text-secondary); margin-top: 0.75rem; font-size: 0.875rem;">+${endpoints - 2} more endpoints</div>` : ''}
                        </div>
                    ` : '<div style="color: var(--text-secondary); font-size: 0.875rem;">Base endpoint available</div>'}
                </div>
            `;
        });
    });

    grid.innerHTML = html || '<div style="grid-column: 1/-1; text-align: center; padding: 4rem; color: var(--text-secondary);">No services found</div>';
}

function setFilter(filter) {
    currentFilter = filter;
    document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
    event.target.classList.add('active');
    renderServices();
}

function filterServices() {
    const search = document.getElementById('searchInput').value.toLowerCase();
    document.querySelectorAll('.service-card').forEach(card => {
        const text = card.textContent.toLowerCase();
        card.style.display = text.includes(search) ? 'block' : 'none';
    });
}

function testEndpoint(url, key) {
    openTester();
    let finalUrl = url;
    if (key) {
        finalUrl = url.replace(/{KEY}/g, key).replace(/{key}/g, key);
    }
    document.getElementById('testUrl').value = finalUrl;
}

function openTester() {
    document.getElementById('testerModal').classList.add('active');
}

function closeTester() {
    document.getElementById('testerModal').classList.remove('active');
}

function setMethod(method, btn) {
    currentMethod = method;
    document.querySelectorAll('.method-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('bodyGroup').style.display = (method === 'POST' || method === 'PUT') ? 'block' : 'none';
}

async function sendRequest() {
    const url = document.getElementById('testUrl').value;
    const headersText = document.getElementById('testHeaders').value;
    const bodyText = document.getElementById('testBody').value;
    const responseBox = document.getElementById('responseBox');
    const responseJson = document.getElementById('responseJson');

    if (!url) {
        showToast('⚠️', 'Please enter a URL');
        return;
    }

    responseBox.style.display = 'block';
    responseJson.textContent = '⏳ Sending request...';

    try {
        // Use proxy endpoint to avoid CORS issues
        const proxyResponse = await fetch('/api/crypto-hub/proxy', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                url: url,
                method: currentMethod,
                headers: headersText ? JSON.parse(headersText) : {},
                body: (currentMethod === 'POST' || currentMethod === 'PUT') && bodyText ? bodyText : null
            })
        });

        const data = await proxyResponse.json();

        if (data.error) {
            responseJson.textContent = `❌ Error: ${data.error}\n\n${data.details || ''}`;
            showToast('❌', 'Request failed');
        } else {
            responseJson.textContent = JSON.stringify(data, null, 2);
            showToast('✅', 'Request successful!');
        }
    } catch (error) {
        responseJson.textContent = `❌ Error: ${error.message}\n\nThis might be due to CORS policy or network issues.`;
        showToast('❌', 'Request failed');
    }
}

function copyText(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('✅', 'Copied to clipboard!');
    }).catch(() => {
        showToast('❌', 'Failed to copy');
    });
}

function exportJSON() {
    const data = {
        metadata: {
            exported_at: new Date().toISOString(),
            total_services: Object.values(SERVICES).flat().length
        },
        services: SERVICES
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `crypto-api-hub-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);

    showToast('✅', 'JSON exported!');
}

function showToast(icon, message) {
    const toast = document.getElementById('toast');
    document.getElementById('toastIcon').textContent = icon;
    document.getElementById('toastMessage').textContent = message;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 3000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function escapeQuotes(text) {
    return text.replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadServices();
});
