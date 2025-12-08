class SettingsView {
    constructor(section) {
        this.section = section;
        this.themeToggle = section.querySelector('[data-theme-toggle]');
        this.marketIntervalInput = section.querySelector('[data-market-interval]');
        this.newsIntervalInput = section.querySelector('[data-news-interval]');
        this.layoutToggle = section.querySelector('[data-layout-toggle]');
    }

    init() {
        this.loadPreferences();
        this.bindEvents();
    }

    loadPreferences() {
        const theme = localStorage.getItem('dashboard-theme') || 'dark';
        document.body.dataset.theme = theme;
        if (this.themeToggle) {
            this.themeToggle.checked = theme === 'light';
        }
        const marketInterval = localStorage.getItem('market-interval') || 60;
        const newsInterval = localStorage.getItem('news-interval') || 120;
        if (this.marketIntervalInput) this.marketIntervalInput.value = marketInterval;
        if (this.newsIntervalInput) this.newsIntervalInput.value = newsInterval;
        const layout = localStorage.getItem('layout-density') || 'spacious';
        document.body.dataset.layout = layout;
        if (this.layoutToggle) {
            this.layoutToggle.checked = layout === 'compact';
        }
    }

    bindEvents() {
        if (this.themeToggle) {
            this.themeToggle.addEventListener('change', () => {
                const theme = this.themeToggle.checked ? 'light' : 'dark';
                document.body.dataset.theme = theme;
                localStorage.setItem('dashboard-theme', theme);
            });
        }
        if (this.marketIntervalInput) {
            this.marketIntervalInput.addEventListener('change', () => {
                localStorage.setItem('market-interval', this.marketIntervalInput.value);
            });
        }
        if (this.newsIntervalInput) {
            this.newsIntervalInput.addEventListener('change', () => {
                localStorage.setItem('news-interval', this.newsIntervalInput.value);
            });
        }
        if (this.layoutToggle) {
            this.layoutToggle.addEventListener('change', () => {
                const layout = this.layoutToggle.checked ? 'compact' : 'spacious';
                document.body.dataset.layout = layout;
                localStorage.setItem('layout-density', layout);
            });
        }
    }
}

export default SettingsView;
