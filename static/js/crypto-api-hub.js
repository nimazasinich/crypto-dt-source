/**
 * Crypto API Hub Dashboard - Main JavaScript
 * Handles service loading, filtering, search, and API testing
 */

// ============================================================================
// State Management
// ============================================================================

let servicesData = null;
let currentFilter = 'all';
let currentMethod = 'GET';

// SVG Icons
const svgIcons = {
    chain: '<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>',
    chart: '<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><line x1="12" y1="20" x2="12" y2="10"></line><line x1="18" y1="20" x2="18" y2="4"></line><line x1="6" y1="20" x2="6" y2="16"></line></svg>',
    news: '<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2"></path><path d="M18 14h-8"></path><path d="M15 18h-5"></path><path d="M10 6h8v4h-8V6Z"></path></svg>',
    brain: '<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.98-3A2.5 2.5 0 0 1 9.5 2Z"></path><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.98-3A2.5 2.5 0 0 0 14.5 2Z"></path></svg>',
    analytics: '<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><path d="M3 3v18h18"></path><path d="m19 9-5 5-4-4-3 3"></path></svg>'
};

// ============================================================================
// API Functions
// ============================================================================

async function fetchServices() {
    // Fetch services data from backend API
    try {
        const response = await fetch('/api/crypto-hub/services');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        servicesData = await response.json();
        return servicesData;
    } catch (error) {
        console.error('Error fetching services:', error);
        showToast('❌', 'Failed to load services');
        return null;
    }
}

async function fetchStatistics() {
    // Fetch hub statistics from backend
    try {
        const response = await fetch('/api/crypto-hub/stats');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching statistics:', error);
        return null;
    }
}

async function testAPIEndpoint(url, method = 'GET', headers = null, body = null) {
    // Test an API endpoint via backend proxy
    try {
        const response = await fetch('/api/crypto-hub/test', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                url: url,
                method: method,
                headers: headers,
                body: body
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Error testing API:', error);
        return {
            success: false,
            status_code: 0,
            data: null,
            error: error.message
        };
    }
}

// ============================================================================
// UI Rendering Functions
// ============================================================================

function getIcon(category) {
    // Get SVG icon for category
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
    // Render all service cards in the grid
    if (!servicesData) {
        console.error('No services data available');
        return;
    }

    const grid = document.getElementById('servicesGrid');
    if (!grid) {
        console.error('Services grid element not found');
        return;
    }

    let html = '';
    const categories = servicesData.categories || {};

    Object.entries(categories).forEach(([categoryId, categoryData]) => {
        const services = categoryData.services || [];

        services.forEach(service => {
            // Filter by category
            if (currentFilter !== 'all' && categoryId !== currentFilter) return;

            const hasKey = service.key ? `<span class="badge badge-key">🔑 Has Key</span>` : '';
            const endpoints = service.endpoints || [];
            const endpointsCount = endpoints.length;

            html += `
                <div class="service-card" data-category="${categoryId}" data-name="${service.name.toLowerCase()}">
                    <div class="service-header">
                        <div class="service-icon">${getIcon(categoryId)}</div>
                        <div class="service-info">
                            <div class="service-name">${escapeHtml(service.name)}</div>
                            <div class="service-url">${escapeHtml(service.url)}</div>
                        </div>
                    </div>
                    <div class="service-badges">
                        <span class="badge badge-category">${categoryId}</span>
                        ${endpointsCount > 0 ? `<span class="badge badge-endpoints">${endpointsCount} endpoints</span>` : ''}
                        ${hasKey}
                    </div>
                    ${endpointsCount > 0 ? renderEndpoints(service, endpoints) : renderBaseEndpoint()}
                </div>
            `;
        });
    });

    grid.innerHTML = html || '<div style="grid-column: 1/-1; text-align: center; padding: 4rem; color: var(--text-secondary);">No services found</div>';
}

function renderEndpoints(service, endpoints) {
    // Render endpoint list for a service
    const displayEndpoints = endpoints.slice(0, 2);
    const remaining = endpoints.length - 2;

    let html = '<div class="endpoints-list">';

    displayEndpoints.forEach(endpoint => {
        const endpointPath = endpoint.path || endpoint;
        const fullUrl = service.url + endpointPath;
        const description = endpoint.description || '';

        html += `
            <div class="endpoint-item">
                <div class="endpoint-path" title="${escapeHtml(description)}">
                    ${escapeHtml(endpointPath)}
                </div>
                <div class="endpoint-actions">
                    <button class="btn-sm" onclick='copyText("${escapeHtml(fullUrl, true)}")'>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                        </svg>
                        Copy
                    </button>
                    <button class="btn-sm" onclick='testEndpoint("${escapeHtml(fullUrl, true)}", "${escapeHtml(service.key || '', true)}")'>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
                        </svg>
                        Test
                    </button>
                </div>
            </div>
        `;
    });

    if (remaining > 0) {
        html += `<div style="text-align: center; color: var(--text-secondary); margin-top: 0.75rem; font-size: 0.875rem;">+${remaining} more endpoints</div>`;
    }

    html += '</div>';
    return html;
}

function renderBaseEndpoint() {
    // Render placeholder for services without specific endpoints
    return '<div style="color: var(--text-secondary); font-size: 0.875rem;">Base endpoint available</div>';
}

async function updateStatistics() {
    // Update statistics in the header
    const stats = await fetchStatistics();
    if (!stats) return;

    // Update stat values
    const statsElements = {
        services: document.querySelector('.stat-value:nth-child(1)'),
        endpoints: document.querySelector('.stat-value:nth-child(2)'),
        keys: document.querySelector('.stat-value:nth-child(3)')
    };

    if (statsElements.services) {
        document.querySelectorAll('.stat-value')[0].textContent = stats.total_services || 0;
    }
    if (statsElements.endpoints) {
        document.querySelectorAll('.stat-value')[1].textContent = (stats.total_endpoints || 0) + '+';
    }
    if (statsElements.keys) {
        document.querySelectorAll('.stat-value')[2].textContent = stats.api_keys_count || 0;
    }
}

// ============================================================================
// Filter and Search Functions
// ============================================================================

function setFilter(filter) {
    // Set current category filter
    currentFilter = filter;

    // Update active filter tab
    document.querySelectorAll('.filter-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    event.target.classList.add('active');

    // Re-render services
    renderServices();
}

function filterServices() {
    // Filter services based on search input
    const search = document.getElementById('searchInput');
    if (!search) return;

    const searchTerm = search.value.toLowerCase();
    const cards = document.querySelectorAll('.service-card');

    cards.forEach(card => {
        const text = card.textContent.toLowerCase();
        card.style.display = text.includes(searchTerm) ? 'block' : 'none';
    });
}

// ============================================================================
// API Testing Functions
// ============================================================================

function testEndpoint(url, key) {
    // Open tester modal with pre-filled URL
    openTester();

    // Replace key placeholder if key exists
    let finalUrl = url;
    if (key) {
        finalUrl = url.replace(/{KEY}/gi, key).replace(/{key}/gi, key);
    }

    const urlInput = document.getElementById('testUrl');
    if (urlInput) {
        urlInput.value = finalUrl;
    }
}

function openTester() {
    // Open API tester modal
    const modal = document.getElementById('testerModal');
    if (modal) {
        modal.classList.add('active');
        // Focus on first input
        setTimeout(() => {
            const urlInput = document.getElementById('testUrl');
            if (urlInput) urlInput.focus();
        }, 100);
    }
}

function closeTester() {
    // Close API tester modal
    const modal = document.getElementById('testerModal');
    if (modal) {
        modal.classList.remove('active');
    }
}

function setMethod(method, btn) {
    // Set HTTP method for API test
    currentMethod = method;

    // Update active button
    document.querySelectorAll('.method-btn').forEach(b => {
        b.classList.remove('active');
    });
    btn.classList.add('active');

    // Show/hide body input for POST/PUT
    const bodyGroup = document.getElementById('bodyGroup');
    if (bodyGroup) {
        bodyGroup.style.display = (method === 'POST' || method === 'PUT') ? 'block' : 'none';
    }
}

async function sendRequest() {
    // Send API test request
    const urlInput = document.getElementById('testUrl');
    const headersInput = document.getElementById('testHeaders');
    const bodyInput = document.getElementById('testBody');
    const responseBox = document.getElementById('responseBox');
    const responseJson = document.getElementById('responseJson');

    if (!urlInput || !responseBox || !responseJson) {
        console.error('Required elements not found');
        return;
    }

    const url = urlInput.value.trim();
    if (!url) {
        showToast('⚠️', 'Please enter a URL');
        return;
    }

    // Show loading state
    responseBox.style.display = 'block';
    responseJson.textContent = '⏳ Sending request...';

    try {
        // Parse headers
        let headers = null;
        if (headersInput && headersInput.value.trim()) {
            try {
                headers = JSON.parse(headersInput.value);
            } catch (e) {
                showToast('⚠️', 'Invalid JSON in headers');
                responseJson.textContent = '❌ Error: Invalid headers JSON format';
                return;
            }
        }

        // Get body if applicable
        let body = null;
        if ((currentMethod === 'POST' || currentMethod === 'PUT') && bodyInput) {
            body = bodyInput.value.trim();
        }

        // Send request via backend proxy
        const result = await testAPIEndpoint(url, currentMethod, headers, body);

        if (result.success) {
            responseJson.textContent = JSON.stringify(result.data, null, 2);
            showToast('✅', `Success! Status: ${result.status_code}`);
        } else {
            responseJson.textContent = `❌ Error: ${result.error || 'Request failed'}\n\nStatus Code: ${result.status_code || 'N/A'}\n\nThis might be due to CORS policy, invalid API key, or network issues.`;
            showToast('❌', 'Request failed');
        }
    } catch (error) {
        responseJson.textContent = `❌ Error: ${error.message}`;
        showToast('❌', 'Request failed');
    }
}

// ============================================================================
// Utility Functions
// ============================================================================

function copyText(text) {
    // Copy text to clipboard
    navigator.clipboard.writeText(text).then(() => {
        showToast('✅', 'Copied to clipboard!');
    }).catch(() => {
        showToast('❌', 'Failed to copy');
    });
}

function exportJSON() {
    // Export all services data as JSON file
    if (!servicesData) {
        showToast('⚠️', 'No data to export');
        return;
    }

    const data = {
        exported_at: new Date().toISOString(),
        ...servicesData
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `crypto-api-hub-export-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    showToast('✅', 'JSON exported successfully!');
}

function showToast(icon, message) {
    // Show toast notification
    const toast = document.getElementById('toast');
    const toastIcon = document.getElementById('toastIcon');
    const toastMessage = document.getElementById('toastMessage');

    if (toast && toastIcon && toastMessage) {
        toastIcon.textContent = icon;
        toastMessage.textContent = message;
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 3000);
    }
}

function escapeHtml(text, forAttribute = false) {
    // Escape HTML to prevent XSS
    if (!text) return '';

    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };

    const escaped = String(text).replace(/[&<>"']/g, m => map[m]);

    // For attributes, also escape quotes properly
    if (forAttribute) {
        return escaped.replace(/"/g, '&quot;');
    }

    return escaped;
}

// ============================================================================
// Initialization
// ============================================================================

async function initializeDashboard() {
    // Initialize the dashboard on page load
    console.log('Initializing Crypto API Hub Dashboard...');

    // Fetch services data
    const data = await fetchServices();
    if (!data) {
        console.error('Failed to load services data');
        showErrorState();
        return;
    }

    // Render services
    renderServices();

    // Update statistics
    await updateStatistics();

    console.log('Dashboard initialized successfully!');
}

function showErrorState() {
    // Show error state when services fail to load
    const grid = document.getElementById('servicesGrid');
    if (!grid) return;

    grid.innerHTML = `
        <div class="error-state" style="grid-column: 1/-1;">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
            <h3>Failed to Load Services</h3>
            <p>We couldn't load the API services. Please check your connection and try again.</p>
            <button class="retry-btn" onclick="location.reload()">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display: inline; margin-right: 8px;">
                    <polyline points="23 4 23 10 17 10"></polyline>
                    <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
                </svg>
                Retry
            </button>
        </div>
    `;
}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeDashboard);
} else {
    initializeDashboard();
}

// ============================================================================
// Event Listeners for Enhanced UX
// ============================================================================

// Close modal on ESC key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        const modal = document.getElementById('testerModal');
        if (modal && modal.classList.contains('active')) {
            closeTester();
        }
    }
});

// Close modal when clicking outside
document.addEventListener('click', (e) => {
    const modal = document.getElementById('testerModal');
    if (modal && e.target === modal) {
        closeTester();
    }
});
