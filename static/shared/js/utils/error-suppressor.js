/**
 * Error Suppressor - Suppress external service errors (Hugging Face Spaces, SSE, etc.)
 * This prevents console pollution from external services that we don't control
 */

(function() {
  'use strict';

  // Store original console methods
  const originalError = console.error;
  const originalWarn = console.warn;

  // Patterns to suppress
  const suppressedPatterns = [
    // SSE errors from Hugging Face Spaces
    /Failed to fetch.*via SSE/i,
    /SSE Stream ended with error/i,
    /BodyStreamBuffer was aborted/i,
    /SpaceHeader.*\.js/i,
    /AbortError.*BodyStreamBuffer/i,
    
    // Permissions-Policy warnings (harmless browser warnings)
    /Unrecognized feature.*permissions-policy/i,
    /Unrecognized feature: 'ambient-light-sensor'/i,
    /Unrecognized feature: 'battery'/i,
    /Unrecognized feature: 'document-domain'/i,
    /Unrecognized feature: 'layout-animations'/i,
    /Unrecognized feature: 'legacy-image-formats'/i,
    /Unrecognized feature: 'oversized-images'/i,
    /Unrecognized feature: 'vr'/i,
    /Unrecognized feature: 'wake-lock'/i,
    
    // Other harmless external service errors
    /index\.js.*SSE/i,
    /onStateChange.*SSE/i
  ];

  /**
   * Check if a message should be suppressed
   */
  function shouldSuppress(message) {
    if (!message) return false;
    
    const messageStr = typeof message === 'string' ? message : String(message);
    
    return suppressedPatterns.some(pattern => {
      try {
        return pattern.test(messageStr);
      } catch (e) {
        return false;
      }
    });
  }

  /**
   * Filter console.error
   */
  console.error = function(...args) {
    const message = args[0];
    
    // Suppress external service errors
    if (shouldSuppress(message)) {
      return; // Silently ignore
    }
    
    // Call original error handler
    originalError.apply(console, args);
  };

  /**
   * Filter console.warn
   */
  console.warn = function(...args) {
    const message = args[0];
    
    // Suppress Permissions-Policy warnings
    if (shouldSuppress(message)) {
      return; // Silently ignore
    }
    
    // Call original warn handler
    originalWarn.apply(console, args);
  };

  // Also catch unhandled errors from external scripts
  window.addEventListener('error', function(event) {
    if (shouldSuppress(event.message)) {
      event.preventDefault();
      event.stopPropagation();
      return false;
    }
  }, true);

  // Suppress unhandled promise rejections from external services
  window.addEventListener('unhandledrejection', function(event) {
    const reason = event.reason;
    const message = reason?.message || reason?.toString() || '';
    
    if (shouldSuppress(message)) {
      event.preventDefault();
      return false;
    }
  });

  console.log('[Error Suppressor] External service error filtering enabled');
})();

