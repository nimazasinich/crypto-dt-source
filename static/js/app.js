import apiClient from './apiClient.js';
import wsClient from './wsClient.js';
import OverviewView from './overviewView.js';
import MarketView from './marketView.js';
import NewsView from './newsView.js';
import ChartLabView from './chartLabView.js';
import AIAdvisorView from './aiAdvisorView.js';
import DatasetsModelsView from './datasetsModelsView.js';
import DebugConsoleView from './debugConsoleView.js';
import SettingsView from './settingsView.js';
import ProvidersView from './providersView.js';
import ApiExplorerView from './apiExplorerView.js';

const App = {
    init() {
        this.cacheElements();
        this.bindNavigation();
        this.initViews();
        this.initStatusBadges();
        wsClient.connect();
    },

    cacheElements() {
        this.sections = document.querySelectorAll('.page');
        this.navButtons = document.querySelectorAll('[data-nav]');
        this.apiHealthBadge = document.querySelector('[data-api-health]');
        this.wsBadge = document.querySelector('[data-ws-status]');
    },

    bindNavigation() {
        this.navButtons.forEach((button) => {
            button.addEventListener('click', () => {
                const target = button.dataset.nav;
                this.sections.forEach((section) => section.classList.toggle('active', section.id === target));
                this.navButtons.forEach((btn) => btn.classList.toggle('active', btn === button));
            });
        });
    },

    initViews() {
        const overview = new OverviewView(document.getElementById('page-overview'));
        overview.init();

        const market = new MarketView(document.getElementById('page-market'), wsClient);
        market.init();

        const news = new NewsView(document.getElementById('page-news'));
        news.init();

        const chartLab = new ChartLabView(document.getElementById('page-chart'));
        chartLab.init();

        const aiAdvisor = new AIAdvisorView(document.getElementById('page-ai'));
        aiAdvisor.init();

        const datasets = new DatasetsModelsView(document.getElementById('page-datasets'));
        datasets.init();

        const debugView = new DebugConsoleView(document.getElementById('page-debug'), wsClient);
        debugView.init();

        const settings = new SettingsView(document.getElementById('page-settings'));
        settings.init();

        const providersView = new ProvidersView(document.getElementById('page-providers'));
        providersView.init();

        const apiExplorer = new ApiExplorerView(document.getElementById('page-api'));
        apiExplorer.init();
    },

    initStatusBadges() {
        this.refreshHealth();
        wsClient.onStatusChange((status) => {
            if (!this.wsBadge) return;
            const state = status === 'connected' ? 'ok' : status === 'connecting' ? 'warn' : 'error';
            this.wsBadge.dataset.state = state;
            const textNode = this.wsBadge.querySelectorAll('span')[1];
            if (textNode) textNode.textContent = status;
        });
    },

    async refreshHealth() {
        if (!this.apiHealthBadge) return;
        const result = await apiClient.getHealth();
        if (result.ok) {
            this.apiHealthBadge.dataset.state = 'ok';
            const textNode = this.apiHealthBadge.querySelectorAll('span')[1];
            if (textNode) textNode.textContent = result.data?.status || 'healthy';
        } else {
            this.apiHealthBadge.dataset.state = 'error';
            const textNode = this.apiHealthBadge.querySelectorAll('span')[1];
            if (textNode) textNode.textContent = 'error';
        }
    },
};

window.addEventListener('DOMContentLoaded', () => App.init());
