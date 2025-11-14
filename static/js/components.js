/**
 * Reusable UI Components Library
 * Enterprise-grade components for Crypto Monitor Ultimate
 */

class UIComponents {
    /**
     * Create a modal dialog
     */
    static createModal(title, content, footer = '') {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <h2 class="modal-title">${title}</h2>
                    <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="18" y1="6" x2="6" y2="18"></line>
                            <line x1="6" y1="6" x2="18" y2="18"></line>
                        </svg>
                    </button>
                </div>
                <div class="modal-body">
                    ${content}
                </div>
                ${footer ? `<div class="modal-footer">${footer}</div>` : ''}
            </div>
        `;

        document.body.appendChild(modal);
        setTimeout(() => modal.classList.add('active'), 10);

        // Close on backdrop click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('active');
                setTimeout(() => modal.remove(), 300);
            }
        });

        // Close on Escape key
        const escHandler = (e) => {
            if (e.key === 'Escape') {
                modal.classList.remove('active');
                setTimeout(() => modal.remove(), 300);
                document.removeEventListener('keydown', escHandler);
            }
        };
        document.addEventListener('keydown', escHandler);

        return modal;
    }

    /**
     * Create a sparkline chart using Chart.js
     */
    static createSparkline(canvasId, data, color = '#667eea') {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        return new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map((_, i) => i),
                datasets: [{
                    data: data,
                    borderColor: color,
                    borderWidth: 2,
                    fill: false,
                    pointRadius: 0,
                    tension: 0.4
                }]
            },
            options: {
                responsive: false,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false }
                },
                scales: {
                    x: { display: false },
                    y: { display: false }
                }
            }
        });
    }

    /**
     * Create a donut/gauge chart
     */
    static createGaugeChart(canvasId, value, max = 100, label = '') {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        const percentage = (value / max) * 100;
        let color = '#10b981'; // Green
        if (percentage < 50) color = '#ef4444'; // Red
        else if (percentage < 75) color = '#f59e0b'; // Orange

        return new Chart(ctx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [value, max - value],
                    backgroundColor: [color, '#e5e7eb'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                cutout: '70%',
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false }
                }
            }
        });
    }

    /**
     * Create a line chart for time series data
     */
    static createLineChart(canvasId, labels, datasets, options = {}) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        const defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    enabled: true,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    borderRadius: 8
                }
            },
            scales: {
                x: {
                    grid: { display: false }
                },
                y: {
                    grid: { color: 'rgba(0, 0, 0, 0.05)' },
                    beginAtZero: true
                }
            }
        };

        return new Chart(ctx, {
            type: 'line',
            data: { labels, datasets },
            options: { ...defaultOptions, ...options }
        });
    }

    /**
     * Create a bar chart
     */
    static createBarChart(canvasId, labels, data, label = 'Data', color = '#667eea') {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        return new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: label,
                    data: data,
                    backgroundColor: color,
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: { grid: { display: false } },
                    y: { grid: { color: 'rgba(0, 0, 0, 0.05)' }, beginAtZero: true }
                }
            }
        });
    }

    /**
     * Create an advanced data table with sorting, filtering, pagination
     */
    static createDataTable(containerId, columns, data, options = {}) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const {
            sortable = true,
            searchable = true,
            pageSize = 20,
            onRowClick = null
        } = options;

        let currentPage = 1;
        let sortColumn = null;
        let sortDirection = 'asc';
        let searchQuery = '';
        let filteredData = [...data];

        const render = () => {
            // Filter data
            if (searchQuery) {
                filteredData = data.filter(row =>
                    Object.values(row).some(val =>
                        String(val).toLowerCase().includes(searchQuery.toLowerCase())
                    )
                );
            } else {
                filteredData = [...data];
            }

            // Sort data
            if (sortColumn) {
                filteredData.sort((a, b) => {
                    const aVal = a[sortColumn];
                    const bVal = b[sortColumn];
                    const direction = sortDirection === 'asc' ? 1 : -1;

                    if (typeof aVal === 'number' && typeof bVal === 'number') {
                        return (aVal - bVal) * direction;
                    }
                    return String(aVal).localeCompare(String(bVal)) * direction;
                });
            }

            // Pagination
            const totalPages = Math.ceil(filteredData.length / pageSize);
            const startIndex = (currentPage - 1) * pageSize;
            const endIndex = startIndex + pageSize;
            const pageData = filteredData.slice(startIndex, endIndex);

            // Render HTML
            let html = '';

            if (searchable) {
                html += `
                    <div style="margin-bottom: var(--space-lg);">
                        <input type="text" class="form-input" placeholder="Search..." id="${containerId}-search" value="${searchQuery}">
                    </div>
                `;
            }

            html += `
                <table class="data-table">
                    <thead>
                        <tr>
                            ${columns.map(col => `
                                <th class="${sortable && col.sortable !== false ? 'sortable-header' : ''}"
                                    data-column="${col.key}"
                                    style="cursor: ${sortable && col.sortable !== false ? 'pointer' : 'default'};">
                                    ${col.label}
                                    ${sortColumn === col.key ? (sortDirection === 'asc' ? ' ↑' : ' ↓') : ''}
                                </th>
                            `).join('')}
                        </tr>
                    </thead>
                    <tbody>
                        ${pageData.map((row, rowIndex) => `
                            <tr class="${onRowClick ? 'clickable-row' : ''}" data-row-index="${startIndex + rowIndex}">
                                ${columns.map(col => `
                                    <td>${col.render ? col.render(row[col.key], row) : row[col.key]}</td>
                                `).join('')}
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;

            if (totalPages > 1) {
                html += `
                    <div class="pagination">
                        <button class="pagination-btn" id="${containerId}-prev" ${currentPage === 1 ? 'disabled' : ''}>
                            Previous
                        </button>
                        <span style="padding: 0 var(--space-md);">
                            Page ${currentPage} of ${totalPages}
                        </span>
                        <button class="pagination-btn" id="${containerId}-next" ${currentPage === totalPages ? 'disabled' : ''}>
                            Next
                        </button>
                    </div>
                `;
            }

            container.innerHTML = html;

            // Attach event listeners
            if (searchable) {
                const searchInput = document.getElementById(`${containerId}-search`);
                if (searchInput) {
                    searchInput.addEventListener('input', (e) => {
                        searchQuery = e.target.value;
                        currentPage = 1;
                        render();
                    });
                }
            }

            if (sortable) {
                container.querySelectorAll('.sortable-header').forEach(header => {
                    header.addEventListener('click', () => {
                        const column = header.dataset.column;
                        if (sortColumn === column) {
                            sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
                        } else {
                            sortColumn = column;
                            sortDirection = 'asc';
                        }
                        render();
                    });
                });
            }

            if (onRowClick) {
                container.querySelectorAll('.clickable-row').forEach(row => {
                    row.addEventListener('click', () => {
                        const rowIndex = parseInt(row.dataset.rowIndex);
                        onRowClick(data[rowIndex]);
                    });
                    row.style.cursor = 'pointer';
                });
            }

            const prevBtn = document.getElementById(`${containerId}-prev`);
            if (prevBtn) {
                prevBtn.addEventListener('click', () => {
                    if (currentPage > 1) {
                        currentPage--;
                        render();
                    }
                });
            }

            const nextBtn = document.getElementById(`${containerId}-next`);
            if (nextBtn) {
                nextBtn.addEventListener('click', () => {
                    if (currentPage < totalPages) {
                        currentPage++;
                        render();
                    }
                });
            }
        };

        render();
        return { render, update: (newData) => { data = newData; render(); } };
    }

    /**
     * Create a progress bar
     */
    static createProgressBar(value, max = 100, showLabel = true) {
        const percentage = (value / max) * 100;
        let colorClass = 'success';
        if (percentage < 50) colorClass = 'danger';
        else if (percentage < 75) colorClass = 'warning';

        return `
            <div style="width: 100%;">
                ${showLabel ? `
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px; font-size: 12px;">
                        <span>${percentage.toFixed(0)}%</span>
                    </div>
                ` : ''}
                <div class="progress-bar">
                    <div class="progress-fill ${colorClass}" style="width: ${percentage}%;"></div>
                </div>
            </div>
        `;
    }

    /**
     * Create a badge
     */
    static createBadge(text, type = 'info') {
        const validTypes = ['success', 'warning', 'danger', 'info'];
        const badgeType = validTypes.includes(type) ? type : 'info';
        return `<span class="badge-pill badge-${badgeType}">${text}</span>`;
    }

    /**
     * Create an alert box
     */
    static createAlert(title, message, type = 'info') {
        const icons = {
            success: '<path d="M20 6L9 17l-5-5"></path>',
            warning: '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line>',
            danger: '<circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line>',
            info: '<circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line>'
        };

        return `
            <div class="alert alert-${type}">
                <svg class="alert-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    ${icons[type] || icons.info}
                </svg>
                <div class="alert-content">
                    ${title ? `<div class="alert-title">${title}</div>` : ''}
                    <div class="alert-description">${message}</div>
                </div>
            </div>
        `;
    }

    /**
     * Create empty state
     */
    static createEmptyState(title, description, actionButton = null) {
        return `
            <div class="empty-state">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="11" cy="11" r="8"></circle>
                    <path d="m21 21-4.35-4.35"></path>
                </svg>
                <div class="empty-state-title">${title}</div>
                <div class="empty-state-description">${description}</div>
                ${actionButton ? actionButton : ''}
            </div>
        `;
    }

    /**
     * Create loading skeleton
     */
    static createSkeleton(type = 'text', count = 3) {
        if (type === 'card') {
            return `
                <div class="card">
                    <div class="skeleton skeleton-title"></div>
                    <div class="skeleton skeleton-text"></div>
                    <div class="skeleton skeleton-text" style="width: 80%;"></div>
                </div>
            `;
        }

        return Array(count).fill('<div class="skeleton skeleton-text"></div>').join('');
    }

    /**
     * Create accordion
     */
    static createAccordion(items) {
        return items.map((item, index) => `
            <div class="accordion-item" id="accordion-${index}">
                <div class="accordion-header" onclick="UIComponents.toggleAccordion('accordion-${index}')">
                    <div class="accordion-title">${item.title}</div>
                    <svg class="accordion-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="6 9 12 15 18 9"></polyline>
                    </svg>
                </div>
                <div class="accordion-content">
                    <div class="accordion-body">
                        ${item.content}
                    </div>
                </div>
            </div>
        `).join('');
    }

    static toggleAccordion(id) {
        const item = document.getElementById(id);
        if (item) {
            item.classList.toggle('active');
        }
    }

    /**
     * Format currency
     */
    static formatCurrency(value, compact = false) {
        if (value === null || value === undefined) return '-';

        if (compact) {
            if (value >= 1e12) return `$${(value / 1e12).toFixed(2)}T`;
            if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
            if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
            if (value >= 1e3) return `$${(value / 1e3).toFixed(2)}K`;
        }

        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: value < 1 ? 4 : 2,
            maximumFractionDigits: value < 1 ? 4 : 2
        }).format(value);
    }

    /**
     * Format number
     */
    static formatNumber(value, decimals = 0) {
        if (value === null || value === undefined) return '-';
        return new Intl.NumberFormat('en-US', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }).format(value);
    }

    /**
     * Format date/time
     */
    static formatDateTime(date, format = 'full') {
        if (!date) return '-';
        const d = new Date(date);

        if (format === 'relative') {
            const now = new Date();
            const diff = now - d;
            const seconds = Math.floor(diff / 1000);
            const minutes = Math.floor(seconds / 60);
            const hours = Math.floor(minutes / 60);
            const days = Math.floor(hours / 24);

            if (seconds < 60) return 'Just now';
            if (minutes < 60) return `${minutes}m ago`;
            if (hours < 24) return `${hours}h ago`;
            if (days < 7) return `${days}d ago`;
            return d.toLocaleDateString();
        }

        if (format === 'time') {
            return d.toLocaleTimeString();
        }

        if (format === 'date') {
            return d.toLocaleDateString();
        }

        return d.toLocaleString();
    }

    /**
     * Copy text to clipboard
     */
    static async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            return true;
        } catch (err) {
            console.error('Failed to copy:', err);
            return false;
        }
    }

    /**
     * Download data as file
     */
    static downloadFile(data, filename, type = 'text/plain') {
        const blob = new Blob([data], { type });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    }

    /**
     * Convert data to CSV
     */
    static toCSV(data, headers) {
        const rows = data.map(row =>
            headers.map(h => row[h] || '').join(',')
        );
        return [headers.join(','), ...rows].join('\n');
    }
}

// Make available globally
window.UIComponents = UIComponents;
