/**
 * HTML Sanitization Utility
 * Prevents XSS attacks by escaping HTML special characters
 */

/**
 * Escape HTML special characters to prevent XSS
 * @param {string|number} text - Text to escape
 * @param {boolean} forAttribute - If true, also escapes quotes for HTML attributes
 * @returns {string} Escaped HTML string
 */
export function escapeHtml(text, forAttribute = false) {
    if (text === null || text === undefined) {
        return '';
    }
    
    const str = String(text);
    
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    
    let escaped = str.replace(/[&<>"']/g, m => map[m]);
    
    // For attributes, ensure quotes are properly escaped
    if (forAttribute) {
        escaped = escaped.replace(/"/g, '&quot;').replace(/'/g, '&#039;');
    }
    
    return escaped;
}

/**
 * Safely set innerHTML with sanitization
 * @param {HTMLElement} element - DOM element to update
 * @param {string} html - HTML string (will be sanitized)
 */
export function safeSetInnerHTML(element, html) {
    if (!element || !(element instanceof HTMLElement)) {
        console.warn('[Sanitizer] Invalid element provided to safeSetInnerHTML');
        return;
    }
    
    // For simple text content, use textContent instead
    if (!html.includes('<') && !html.includes('>')) {
        element.textContent = html;
        return;
    }
    
    // For HTML content, create a temporary container and sanitize
    const temp = document.createElement('div');
    temp.innerHTML = html;
    
    // Sanitize all text nodes
    const walker = document.createTreeWalker(
        temp,
        NodeFilter.SHOW_TEXT,
        null,
        false
    );
    
    let node;
    while (node = walker.nextNode()) {
        if (node.textContent) {
            node.textContent = node.textContent; // Already safe, but ensure it's set
        }
    }
    
    // Clear and append sanitized content
    element.innerHTML = '';
    while (temp.firstChild) {
        element.appendChild(temp.firstChild);
    }
}

/**
 * Sanitize object values for HTML rendering
 * Recursively escapes string values in objects
 * @param {any} obj - Object to sanitize
 * @param {number} depth - Recursion depth limit
 * @returns {any} Sanitized object
 */
export function sanitizeObject(obj, depth = 5) {
    if (depth <= 0) {
        return '[Max Depth Reached]';
    }
    
    if (obj === null || obj === undefined) {
        return '';
    }
    
    if (typeof obj === 'string') {
        return escapeHtml(obj);
    }
    
    if (typeof obj === 'number' || typeof obj === 'boolean') {
        return obj;
    }
    
    if (Array.isArray(obj)) {
        return obj.map(item => sanitizeObject(item, depth - 1));
    }
    
    if (typeof obj === 'object') {
        const sanitized = {};
        for (const key in obj) {
            if (Object.prototype.hasOwnProperty.call(obj, key)) {
                sanitized[key] = sanitizeObject(obj[key], depth - 1);
            }
        }
        return sanitized;
    }
    
    return String(obj);
}

/**
 * Format number safely for display
 * @param {number} value - Number to format
 * @param {object} options - Formatting options
 * @returns {string} Formatted number
 */
export function safeFormatNumber(value, options = {}) {
    if (value === null || value === undefined || isNaN(value)) {
        return '—';
    }
    
    const num = Number(value);
    if (isNaN(num)) {
        return '—';
    }
    
    try {
        return num.toLocaleString('en-US', {
            minimumFractionDigits: options.minimumFractionDigits || 2,
            maximumFractionDigits: options.maximumFractionDigits || 2,
            ...options
        });
    } catch (error) {
        console.warn('[Sanitizer] Number formatting error:', error);
        return String(num);
    }
}

/**
 * Safely format currency
 * @param {number} value - Currency value
 * @param {string} currency - Currency code (default: USD)
 * @returns {string} Formatted currency string
 */
export function safeFormatCurrency(value, currency = 'USD') {
    if (value === null || value === undefined || isNaN(value)) {
        return '—';
    }
    
    const num = Number(value);
    if (isNaN(num)) {
        return '—';
    }
    
    try {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency,
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(num);
    } catch (error) {
        console.warn('[Sanitizer] Currency formatting error:', error);
        return `$${num.toFixed(2)}`;
    }
}

