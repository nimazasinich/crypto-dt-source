import apiClient from './apiClient.js';

class DebugConsoleView {
    constructor(section, wsClient) {
        this.section = section;
        this.wsClient = wsClient;
        this.healthStatus = section.querySelector('[data-health-status]');
        this.providersContainer = section.querySelector('[data-providers]');
        this.requestLogBody = section.querySelector('[data-request-log]');
        this.errorLogBody = section.querySelector('[data-error-log]');
        this.wsLogBody = section.querySelector('[data-ws-log]');
        this.refreshButton = section.querySelector('[data-refresh-health]');
    }

    init() {
        this.refresh();
        if (this.refreshButton) {
            this.refreshButton.addEventListener('click', () => this.refresh());
        }
        apiClient.onLog(() => this.renderRequestLogs());
        apiClient.onError(() => this.renderErrorLogs());
        this.wsClient.onStatusChange(() => this.renderWsLogs());
        this.wsClient.onMessage(() => this.renderWsLogs());
    }

    async refresh() {
        const [health, providers] = await Promise.all([apiClient.getHealth(), apiClient.getProviders()]);
        if (health.ok) {
            this.healthStatus.textContent = health.data?.status || 'OK';
        } else {
            this.healthStatus.textContent = 'Unavailable';
        }
        if (providers.ok) {
            const list = providers.data || [];
            this.providersContainer.innerHTML = list
                .map(
                    (provider) => `
                    <div class="glass-card">
                        <h4>${provider.name}</h4>
                        <p>Status: <span class="${provider.status === 'healthy' ? 'text-success' : 'text-danger'}">${
                            provider.status || 'unknown'
                        }</span></p>
                        <p>Latency: ${provider.latency || '—'}ms</p>
                    </div>
                `,
                )
                .join('');
        } else {
            this.providersContainer.innerHTML = `<div class="inline-message inline-error">${providers.error}</div>`;
        }
        this.renderRequestLogs();
        this.renderErrorLogs();
        this.renderWsLogs();
    }

    renderRequestLogs() {
        if (!this.requestLogBody) return;
        const logs = apiClient.getLogs();
        this.requestLogBody.innerHTML = logs
            .slice(-12)
            .reverse()
            .map(
                (log) => `
                <tr>
                    <td>${log.time}</td>
                    <td>${log.method}</td>
                    <td>${log.endpoint}</td>
                    <td>${log.status}</td>
                    <td>${log.duration}ms</td>
                </tr>
            `,
            )
            .join('');
    }

    renderErrorLogs() {
        if (!this.errorLogBody) return;
        const logs = apiClient.getErrors();
        if (!logs.length) {
            this.errorLogBody.innerHTML = '<tr><td colspan="3">No recent errors.</td></tr>';
            return;
        }
        this.errorLogBody.innerHTML = logs
            .slice(-8)
            .reverse()
            .map(
                (log) => `
                <tr>
                    <td>${log.time}</td>
                    <td>${log.endpoint}</td>
                    <td>${log.message}</td>
                </tr>
            `,
            )
            .join('');
    }

    renderWsLogs() {
        if (!this.wsLogBody) return;
        const events = this.wsClient.getEvents();
        if (!events.length) {
            this.wsLogBody.innerHTML = '<tr><td colspan="3">No WebSocket events yet.</td></tr>';
            return;
        }
        this.wsLogBody.innerHTML = events
            .slice(-12)
            .reverse()
            .map(
                (event) => `
                <tr>
                    <td>${event.time}</td>
                    <td>${event.type}</td>
                    <td>${event.messageType || event.status || event.details || ''}</td>
                </tr>
            `,
            )
            .join('');
    }
}

export default DebugConsoleView;
