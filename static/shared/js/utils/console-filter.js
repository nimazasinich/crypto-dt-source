/**
 * Console Filter - Suppress HuggingFace Space Permissions-Policy Warnings
 * 
 * This script MUST run as early as possible to catch browser warnings
 * that occur during page load from the HF Space container.
 * 
 * Version: 1.0.0
 */

(function () {
    'use strict';

    // Prevent multiple initializations
    if (window._hfWarningsSuppressed) return;

    // List of unrecognized features that cause warnings (from HF Space container)
    const unrecognizedFeatures = [
        'ambient-light-sensor',
        'battery',
        'document-domain',
        'layout-animations',
        'legacy-image-formats',
        'oversized-images',
        'vr',
        'wake-lock',
        'screen-wake-lock',
        'virtual-reality',
        'cross-origin-isolated',
        'execution-while-not-rendered',
        'execution-while-out-of-viewport',
        'keyboard-map',
        'navigation-override',
        'publickey-credentials-get',
        'xr-spatial-tracking'
    ];

    const shouldSuppress = (message) => {
        if (!message) return false;
        const msg = message.toString().toLowerCase();

        // Check for "Unrecognized feature:" pattern
        if (msg.includes('unrecognized feature:')) {
            return unrecognizedFeatures.some(feature => msg.includes(feature));
        }

        // Also check for Permissions-Policy warnings
        if (msg.includes('permissions-policy') || msg.includes('feature-policy')) {
            return unrecognizedFeatures.some(feature => msg.includes(feature));
        }

        // Check for HF Space domain in warning
        if (msg.includes('datasourceforcryptocurrency') &&
            unrecognizedFeatures.some(feature => msg.includes(feature))) {
            return true;
        }

        return false;
    };

    // Store original console methods
    const originalWarn = console.warn;
    const originalError = console.error;
    const originalLog = console.log;

    // Override console.warn
    console.warn = function (...args) {
        const message = args[0]?.toString() || '';
        if (shouldSuppress(message)) {
            return; // Suppress silently
        }
        originalWarn.apply(console, args);
    };

    // Override console.error (some browsers log these as errors)
    console.error = function (...args) {
        const message = args[0]?.toString() || '';
        if (shouldSuppress(message)) {
            return; // Suppress silently
        }
        originalError.apply(console, args);
    };

    // Also filter console.log (just in case)
    console.log = function (...args) {
        const message = args[0]?.toString() || '';
        if (shouldSuppress(message)) {
            return; // Suppress silently
        }
        originalLog.apply(console, args);
    };

    // Mark as suppressed
    window._hfWarningsSuppressed = true;

    // Export for other scripts
    window.suppressHFWarnings = shouldSuppress;
})();

