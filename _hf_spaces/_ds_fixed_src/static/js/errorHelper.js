/**
 * Error Helper & Auto-Fix Utility
 * ابزار خطایابی و تصحیح خودکار
 */

class ErrorHelper {
    constructor() {
        this.errorHistory = [];
        this.autoFixEnabled = true;
    }

    /**
     * Analyze error and suggest fixes
     */
    analyzeError(error, context = {}) {
        const analysis = {
            error: error.message || String(error),
            type: this.detectErrorType(error),
            suggestions: [],
            autoFix: null,
            severity: 'medium'
        };

        // Common error patterns
        if (error.message?.includes('500') || error.message?.includes('Internal Server Error')) {
            analysis.suggestions.push('Server error - check backend logs');
            analysis.suggestions.push('Try refreshing the page');
            analysis.severity = 'high';
        }

        if (error.message?.includes('404') || error.message?.includes('Not Found')) {
            analysis.suggestions.push('Endpoint not found - check API URL');
            analysis.suggestions.push('Verify backend is running');
            analysis.severity = 'medium';
        }

        if (error.message?.includes('CORS') || error.message?.includes('cross-origin')) {
            analysis.suggestions.push('CORS error - check backend CORS settings');
            analysis.severity = 'high';
        }

        if (error.message?.includes('WebSocket')) {
            analysis.suggestions.push('WebSocket connection failed');
            analysis.suggestions.push('Check if WebSocket endpoint is available');
            analysis.autoFix = () => this.reconnectWebSocket();
            analysis.severity = 'medium';
        }

        if (error.message?.includes('symbol') || error.message?.includes('BTC')) {
            analysis.suggestions.push('Invalid symbol - try BTC, ETH, SOL, etc.');
            analysis.autoFix = () => this.fixSymbol(context.symbol);
            analysis.severity = 'low';
        }

        this.errorHistory.push({
            ...analysis,
            timestamp: new Date().toISOString(),
            context
        });

        return analysis;
    }

    detectErrorType(error) {
        const msg = String(error.message || error).toLowerCase();
        if (msg.includes('network') || msg.includes('fetch')) return 'network';
        if (msg.includes('500') || msg.includes('server')) return 'server';
        if (msg.includes('404') || msg.includes('not found')) return 'not_found';
        if (msg.includes('cors')) return 'cors';
        if (msg.includes('websocket')) return 'websocket';
        if (msg.includes('timeout')) return 'timeout';
        return 'unknown';
    }

    /**
     * Auto-fix common issues
     */
    async autoFix(error, context = {}) {
        if (!this.autoFixEnabled) return false;

        const analysis = this.analyzeError(error, context);

        if (analysis.autoFix) {
            try {
                await analysis.autoFix();
                return true;
            } catch (e) {
                console.error('Auto-fix failed:', e);
                return false;
            }
        }

        // Generic fixes
        if (analysis.type === 'network') {
            // Retry after delay
            await new Promise(resolve => setTimeout(resolve, 1000));
            return true;
        }

        return false;
    }

    fixSymbol(symbol) {
        if (!symbol) return 'BTC';
        // Remove spaces, convert to uppercase
        return symbol.trim().toUpperCase().replace(/\s+/g, '');
    }

    async reconnectWebSocket() {
        // Access wsClient from window or import
        if (typeof window !== 'undefined' && window.wsClient) {
            window.wsClient.disconnect();
            await new Promise(resolve => setTimeout(resolve, 1000));
            window.wsClient.connect();
            return true;
        }
        return false;
    }

    /**
     * Get error statistics
     */
    getStats() {
        const types = {};
        this.errorHistory.forEach(err => {
            types[err.type] = (types[err.type] || 0) + 1;
        });
        return {
            total: this.errorHistory.length,
            byType: types,
            recent: this.errorHistory.slice(-10)
        };
    }

    /**
     * Clear error history
     */
    clear() {
        this.errorHistory = [];
    }
}

// Global error helper instance
const errorHelper = new ErrorHelper();

// Auto-catch unhandled errors
window.addEventListener('error', (event) => {
    errorHelper.analyzeError(event.error || event.message, {
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno
    });
});

window.addEventListener('unhandledrejection', (event) => {
    errorHelper.analyzeError(event.reason, {
        type: 'unhandled_promise_rejection'
    });
});

export default errorHelper;

