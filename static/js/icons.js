/**
 * ═══════════════════════════════════════════════════════════════════
 * SVG ICON LIBRARY — ULTRA ENTERPRISE EDITION
 * Crypto Monitor HF — 50+ Professional SVG Icons
 * ═══════════════════════════════════════════════════════════════════
 *
 * All icons are:
 * - Pure SVG (NO PNG, NO font-icons)
 * - 24×24 viewBox
 * - stroke-width: 1.75
 * - stroke-linecap: round
 * - stroke-linejoin: round
 * - currentColor support
 * - Fully accessible
 *
 * Icon naming: camelCase (e.g., trendingUp, checkCircle)
 */

class IconLibrary {
    constructor() {
        this.icons = this.initializeIcons();
    }

    /**
     * Initialize all SVG icons
     */
    initializeIcons() {
        const strokeWidth = "1.75";
        const baseProps = `fill="none" stroke="currentColor" stroke-width="${strokeWidth}" stroke-linecap="round" stroke-linejoin="round"`;

        return {
            // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            // 📊 FINANCE & CRYPTO
            // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

            trendingUp: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>`,

            trendingDown: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><polyline points="23 18 13.5 8.5 8.5 13.5 1 6"></polyline><polyline points="17 18 23 18 23 12"></polyline></svg>`,

            dollarSign: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>`,

            bitcoin: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><path d="M11.767 19.089c4.924.868 6.14-6.025 1.216-6.894m-1.216 6.894L5.86 18.047m5.908 1.042-.347 1.97m1.563-8.864c4.924.869 6.14-6.025 1.215-6.893m-1.215 6.893-3.94-.694m5.155-6.2L8.29 4.26m5.908 1.042.348-1.97M7.48 20.364l3.126-17.727"></path></svg>`,

            ethereum: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><path d="M12 2L4 12l8 5 8-5-8-10z"></path><path d="M4 12l8 10 8-10-8 5-8-5z"></path></svg>`,

            pieChart: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><path d="M21.21 15.89A10 10 0 1 1 8 2.83"></path><path d="M22 12A10 10 0 0 0 12 2v10z"></path></svg>`,

            barChart: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><line x1="12" y1="20" x2="12" y2="10"></line><line x1="18" y1="20" x2="18" y2="4"></line><line x1="6" y1="20" x2="6" y2="16"></line></svg>`,

            activity: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>`,

            lineChart: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><polyline points="3 17 9 11 13 15 21 7"></polyline></svg>`,

            candlestickChart: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><line x1="9" y1="5" x2="9" y2="19"></line><line x1="15" y1="9" x2="15" y2="15"></line><rect x="7" y="8" width="4" height="6"></rect><rect x="13" y="5" width="4" height="10"></rect></svg>`,

            // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            // ✅ STATUS & INDICATORS
            // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

            checkCircle: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>`,

            check: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><polyline points="20 6 9 17 4 12"></polyline></svg>`,

            xCircle: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>`,

            alertCircle: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>`,

            alertTriangle: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>`,

            info: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>`,

            helpCircle: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><circle cx="12" cy="12" r="10"></circle><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>`,

            wifi: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><path d="M5 12.55a11 11 0 0 1 14.08 0"></path><path d="M1.42 9a16 16 0 0 1 21.16 0"></path><path d="M8.53 16.11a6 6 0 0 1 6.95 0"></path><line x1="12" y1="20" x2="12.01" y2="20"></line></svg>`,

            wifiOff: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><line x1="1" y1="1" x2="23" y2="23"></line><path d="M16.72 11.06A10.94 10.94 0 0 1 19 12.55"></path><path d="M5 12.55a10.94 10.94 0 0 1 5.17-2.39"></path><path d="M10.71 5.05A16 16 0 0 1 22.58 9"></path><path d="M1.42 9a15.91 15.91 0 0 1 4.7-2.88"></path><path d="M8.53 16.11a6 6 0 0 1 6.95 0"></path><line x1="12" y1="20" x2="12.01" y2="20"></line></svg>`,

            // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            // 🖱️ NAVIGATION & UI
            // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

            menu: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>`,

            close: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>`,

            chevronRight: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><polyline points="9 18 15 12 9 6"></polyline></svg>`,

            chevronLeft: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><polyline points="15 18 9 12 15 6"></polyline></svg>`,

            chevronDown: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><polyline points="6 9 12 15 18 9"></polyline></svg>`,

            chevronUp: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><polyline points="18 15 12 9 6 15"></polyline></svg>`,

            arrowRight: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>`,

            arrowLeft: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><line x1="19" y1="12" x2="5" y2="12"></line><polyline points="12 19 5 12 12 5"></polyline></svg>`,

            arrowUp: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><line x1="12" y1="19" x2="12" y2="5"></line><polyline points="5 12 12 5 19 12"></polyline></svg>`,

            arrowDown: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><line x1="12" y1="5" x2="12" y2="19"></line><polyline points="19 12 12 19 5 12"></polyline></svg>`,

            externalLink: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>`,

            // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            // 🔧 ACTIONS
            // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

            refresh: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>`,

            refreshCw: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>`,

            search: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><circle cx="11" cy="11" r="8"></circle><path d="m21 21-4.35-4.35"></path></svg>`,

            filter: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"></polygon></svg>`,

            download: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>`,

            upload: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>`,

            settings: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><circle cx="12" cy="12" r="3"></circle><path d="M12 1v6m0 6v6m5.2-15.6l-4.2 4.2m-6 6l-4.2 4.2M23 12h-6m-6 0H1m15.6 5.2l-4.2-4.2m-6-6l-4.2-4.2"></path></svg>`,

            sliders: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><line x1="4" y1="21" x2="4" y2="14"></line><line x1="4" y1="10" x2="4" y2="3"></line><line x1="12" y1="21" x2="12" y2="12"></line><line x1="12" y1="8" x2="12" y2="3"></line><line x1="20" y1="21" x2="20" y2="16"></line><line x1="20" y1="12" x2="20" y2="3"></line><line x1="1" y1="14" x2="7" y2="14"></line><line x1="9" y1="8" x2="15" y2="8"></line><line x1="17" y1="16" x2="23" y2="16"></line></svg>`,

            edit: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>`,

            trash: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>`,

            copy: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>`,

            plus: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>`,

            minus: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><line x1="5" y1="12" x2="19" y2="12"></line></svg>`,

            maximize: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"></path></svg>`,

            minimize: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><path d="M8 3v3a2 2 0 0 1-2 2H3m18 0h-3a2 2 0 0 1-2-2V3m0 18v-3a2 2 0 0 1 2-2h3M3 16h3a2 2 0 0 1 2 2v3"></path></svg>`,

            // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            // 💾 DATA & STORAGE
            // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

            database: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path></svg>`,

            server: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><rect x="2" y="2" width="20" height="8" rx="2" ry="2"></rect><rect x="2" y="14" width="20" height="8" rx="2" ry="2"></rect><line x1="6" y1="6" x2="6.01" y2="6"></line><line x1="6" y1="18" x2="6.01" y2="18"></line></svg>`,

            cpu: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><rect x="4" y="4" width="16" height="16" rx="2" ry="2"></rect><rect x="9" y="9" width="6" height="6"></rect><line x1="9" y1="1" x2="9" y2="4"></line><line x1="15" y1="1" x2="15" y2="4"></line><line x1="9" y1="20" x2="9" y2="23"></line><line x1="15" y1="20" x2="15" y2="23"></line><line x1="20" y1="9" x2="23" y2="9"></line><line x1="20" y1="14" x2="23" y2="14"></line><line x1="1" y1="9" x2="4" y2="9"></line><line x1="1" y1="14" x2="4" y2="14"></line></svg>`,

            hardDrive: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><line x1="22" y1="12" x2="2" y2="12"></line><path d="M5.45 5.11L2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"></path><line x1="6" y1="16" x2="6.01" y2="16"></line><line x1="10" y1="16" x2="10.01" y2="16"></line></svg>`,

            // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            // 📁 FILES & DOCUMENTS
            // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

            fileText: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>`,

            file: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>`,

            folder: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>`,

            folderOpen: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><path d="m6 14 1.45-2.9A2 2 0 0 1 9.24 10H20a2 2 0 0 1 1.94 2.5l-1.55 6a2 2 0 0 1-1.94 1.5H4a2 2 0 0 1-2-2V5c0-1.1.9-2 2-2h3.93a2 2 0 0 1 1.66.9l.82 1.2a2 2 0 0 0 1.66.9H18a2 2 0 0 1 2 2v2"></path></svg>`,

            list: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><line x1="8" y1="6" x2="21" y2="6"></line><line x1="8" y1="12" x2="21" y2="12"></line><line x1="8" y1="18" x2="21" y2="18"></line><line x1="3" y1="6" x2="3.01" y2="6"></line><line x1="3" y1="12" x2="3.01" y2="12"></line><line x1="3" y1="18" x2="3.01" y2="18"></line></svg>`,

            newspaper: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2"></path><path d="M18 14h-8"></path><path d="M15 18h-5"></path><path d="M10 6h8v4h-8V6Z"></path></svg>`,

            // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            // 🏠 FEATURES
            // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

            home: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>`,

            bell: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>`,

            bellOff: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><path d="M8.7 3A6 6 0 0 1 18 8a21.3 21.3 0 0 0 .6 5"></path><path d="M17 17H3s3-2 3-9a4.7 4.7 0 0 1 .6-2.3"></path><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"></path><path d="m2 2 20 20"></path></svg>`,

            layers: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>`,

            globe: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>`,

            zap: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>`,

            shield: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>`,

            shieldCheck: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><polyline points="9 12 11 14 15 10"></polyline></svg>`,

            lock: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>`,

            unlock: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 9.9-1"></path></svg>`,

            users: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>`,

            user: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>`,

            userPlus: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="8.5" cy="7" r="4"></circle><line x1="20" y1="8" x2="20" y2="14"></line><line x1="23" y1="11" x2="17" y2="11"></line></svg>`,

            userMinus: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="8.5" cy="7" r="4"></circle><line x1="23" y1="11" x2="17" y2="11"></line></svg>`,

            // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            // 🌙 THEME & APPEARANCE
            // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

            sun: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>`,

            moon: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>`,

            eye: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>`,

            eyeOff: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>`,

            // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            // 🧠 AI & SPECIAL
            // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

            brain: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.98-3A2.5 2.5 0 0 1 9.5 2Z"></path><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.98-3A2.5 2.5 0 0 0 14.5 2Z"></path></svg>`,

            box: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>`,

            package: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><line x1="16.5" y1="9.4" x2="7.5" y2="4.21"></line><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>`,

            terminal: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><polyline points="4 17 10 11 4 5"></polyline><line x1="12" y1="19" x2="20" y2="19"></line></svg>`,

            code: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline></svg>`,

            codesandbox: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="7.5 4.21 12 6.81 16.5 4.21"></polyline><polyline points="7.5 19.79 7.5 14.6 3 12"></polyline><polyline points="21 12 16.5 14.6 16.5 19.79"></polyline><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>`,

            // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            // 📊 DASHBOARD SPECIFIC
            // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

            grid: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>`,

            layout: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="3" y1="9" x2="21" y2="9"></line><line x1="9" y1="21" x2="9" y2="9"></line></svg>`,

            monitor: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line></svg>`,

            smartphone: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><rect x="5" y="2" width="14" height="20" rx="2" ry="2"></rect><line x1="12" y1="18" x2="12.01" y2="18"></line></svg>`,

            tablet: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><rect x="4" y="2" width="16" height="20" rx="2" ry="2"></rect><line x1="12" y1="18" x2="12.01" y2="18"></line></svg>`,

            clock: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>`,

            calendar: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>`,

            target: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg>`,

            anchor: `<svg width="20" height="20" viewBox="0 0 24 24" ${baseProps}><circle cx="12" cy="5" r="3"></circle><line x1="12" y1="22" x2="12" y2="8"></line><path d="M5 12H2a10 10 0 0 0 20 0h-3"></path></svg>`,
        };
    }

    /**
     * Get icon SVG by name
     * @param {string} name - Icon name
     * @param {number} size - Icon size in pixels (default: 20)
     * @param {string} className - Additional CSS class
     * @returns {string} SVG markup
     */
    getIcon(name, size = 20, className = '') {
        const iconSvg = this.icons[name];
        if (!iconSvg) {
            console.warn(`[Icons] Icon "${name}" not found — using fallback`);
            return this.icons.alertCircle;
        }

        let modifiedSvg = iconSvg
            .replace(/width="20"/, `width="${size}"`)
            .replace(/height="20"/, `height="${size}"`);

        if (className) {
            modifiedSvg = modifiedSvg.replace('<svg', `<svg class="${className}"`);
        }

        return modifiedSvg;
    }

    /**
     * Create icon element
     * @param {string} name - Icon name
     * @param {object} options - Configuration options
     * @returns {HTMLElement} Icon element
     */
    createIcon(name, options = {}) {
        const {
            size = 20,
            className = '',
            color = 'currentColor',
            ariaLabel = null
        } = options;

        const wrapper = document.createElement('span');
        wrapper.className = `icon-wrapper ${className}`;
        wrapper.style.display = 'inline-flex';
        wrapper.style.alignItems = 'center';
        wrapper.style.justifyContent = 'center';
        wrapper.style.color = color;
        wrapper.setAttribute('aria-hidden', 'true');

        if (ariaLabel) {
            wrapper.setAttribute('aria-label', ariaLabel);
            wrapper.setAttribute('role', 'img');
            wrapper.removeAttribute('aria-hidden');
        }

        wrapper.innerHTML = this.getIcon(name, size);
        return wrapper;
    }

    /**
     * Inject icon into element
     * @param {HTMLElement} element - Target element
     * @param {string} name - Icon name
     * @param {object} options - Configuration options
     */
    injectIcon(element, name, options = {}) {
        if (!element) return;

        const icon = this.createIcon(name, options);
        element.innerHTML = '';
        element.appendChild(icon);
    }

    /**
     * Get all available icon names
     * @returns {string[]} Array of icon names
     */
    getAvailableIcons() {
        return Object.keys(this.icons);
    }

    /**
     * Check if icon exists
     * @param {string} name - Icon name
     * @returns {boolean}
     */
    hasIcon(name) {
        return this.icons.hasOwnProperty(name);
    }
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// EXPORT & GLOBAL ACCESS
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

window.iconLibrary = new IconLibrary();

// Utility functions for easy icon usage
window.getIcon = (name, size, className) => window.iconLibrary.getIcon(name, size, className);
window.createIcon = (name, options) => window.iconLibrary.createIcon(name, options);

console.log(`[Icons] 🎨 Icon library loaded with ${window.iconLibrary.getAvailableIcons().length} professional SVG icons`);
