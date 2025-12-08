/**
 * Layout Manager
 * Handles injection and management of shared layout components
 * Version: 2025-12-02-3 (Fixed syntax error - all methods inside class)
 */

import { PAGE_METADATA } from './config.js';
import logger from '../utils/logger.js';

export class LayoutManager {
  static layoutsInjected = false;
  static featureDetectionLoaded = false;
  static apiStatusInterval = null;
  static consecutiveFailures = 0;
  static maxFailures = 3;
  static isOffline = false;

  /**
   * Load feature detection utility (suppresses browser warnings)
   */
  static async loadFeatureDetection() {
    if (this.featureDetectionLoaded) return;
    
    // Suppress warnings immediately (before loading script)
    if (!window._hfWarningsSuppressed) {
      const originalWarn = console.warn;
      const originalError = console.error;
      
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
      
      console.warn = function(...args) {
        const message = args[0]?.toString() || '';
        if (shouldSuppress(message)) {
          return; // Suppress silently
        }
        originalWarn.apply(console, args);
      };
      
      console.error = function(...args) {
        const message = args[0]?.toString() || '';
        if (shouldSuppress(message)) {
          return; // Suppress silently
        }
        originalError.apply(console, args);
      };
      
      window._hfWarningsSuppressed = true;
    }
    
    try {
      // Try multiple paths for feature detection
      const possiblePaths = [
        '/static/shared/js/feature-detection.js',
        '../shared/js/feature-detection.js',
        './shared/js/feature-detection.js',
        window.location.pathname.includes('/static/') 
          ? window.location.pathname.split('/static/')[0] + '/static/shared/js/feature-detection.js'
          : '/static/shared/js/feature-detection.js'
      ];
      
      // Load feature detection script to suppress console warnings
      const script = document.createElement('script');
      
      // Try first path, fallback to others if needed
      script.src = possiblePaths[0];
      script.async = true;
      script.onerror = () => {
        // Try fallback paths
        for (let i = 1; i < possiblePaths.length; i++) {
          const fallbackScript = document.createElement('script');
          fallbackScript.src = possiblePaths[i];
          fallbackScript.async = true;
          fallbackScript.onerror = () => {
            if (i === possiblePaths.length - 1) {
              logger.warn('LayoutManager', 'Could not load feature detection from any path');
            }
          };
          document.head.appendChild(fallbackScript);
          break;
        }
      };
      
      document.head.appendChild(script);
      this.featureDetectionLoaded = true;
    } catch (e) {
      logger.warn('LayoutManager', 'Could not load feature detection:', e);
      // Continue without feature detection - not critical
    }
  }

  /**
   * Initialize the layout manager - alias for injectLayouts
   * @param {string} pageName - Optional page name to set as active
   */
  static async init(pageName = null) {
    // Load feature detection first to suppress warnings
    await this.loadFeatureDetection();
    await this.injectLayouts();
    if (pageName) {
      this.setActivePage(pageName);
    }
  }

  /**
   * Set active page in sidebar navigation
   * @param {string} pageName - The page identifier
   */
  static setActivePage(pageName) {
    this.setActiveNav(pageName);
  }

  /**
   * Inject all layouts (header, sidebar, footer) into current page
   * Optimized: Lazy load non-critical components after initial render
   */
  static async injectLayouts() {
    if (this.layoutsInjected) {
      logger.debug('LayoutManager', 'Layouts already injected');
      return;
    }

    try {
      // Inject critical header first (needed for initial render)
      await this.injectHeader();

      // Setup event listeners early
      this.setupEventListeners();

      // Check API status immediately (non-blocking)
      this.checkApiStatus();

      // Lazy load sidebar and footer after initial render
      const loadNonCritical = () => {
        // Use requestIdleCallback if available for better performance
        const defer = window.requestIdleCallback || ((fn) => setTimeout(fn, 50));
        defer(async () => {
          try {
            await this.injectSidebar();
            
            // Inject footer (if container exists)
            const footerContainer = document.getElementById('footer-container');
            if (footerContainer) {
              await this.injectFooter();
            }
          } catch (error) {
            logger.warn('LayoutManager', 'Failed to load non-critical layouts:', error);
          }
        }, { timeout: 1000 });
      };

      // Load non-critical components after a short delay
      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', loadNonCritical);
      } else {
        loadNonCritical();
      }

      // Auto-check API status every 30 seconds (only when online)
      this.apiStatusInterval = setInterval(() => {
        // Skip if offline or tab is hidden
        if (!this.isOffline && !document.hidden) {
          this.checkApiStatus();
        }
      }, 30000);

      // Pause when tab is hidden, resume when visible
      document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
          // Tab hidden - pause checks
        } else if (!this.isOffline) {
          // Tab visible and online - resume checks
          this.checkApiStatus();
        }
      });

      // Mark as injected
      this.layoutsInjected = true;

      logger.info('LayoutManager', 'Layouts injection initiated');
    } catch (error) {
      logger.error('LayoutManager', 'Failed to inject layouts:', error);
      throw error;
    }
  }

  /**
   * Check backend API health and update status badge
   */
  static async checkApiStatus() {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      
      const response = await fetch('/api/health', { 
        signal: controller.signal,
        cache: 'no-cache'
      });
      clearTimeout(timeoutId);
      
      if (response.ok) {
        this.consecutiveFailures = 0;
        this.isOffline = false;
        this.updateApiStatus('online', '✓ Online');
      } else {
        this.consecutiveFailures++;
        this.updateApiStatus('degraded', `⚠ HTTP ${response.status}`);
      }
    } catch (error) {
      this.consecutiveFailures++;
      
      if (error.name === 'AbortError') {
        this.updateApiStatus('degraded', '⚠ Timeout');
      } else {
        this.updateApiStatus('offline', '✗ Offline');
      }

      // Stop checking if too many consecutive failures
      if (this.consecutiveFailures >= this.maxFailures) {
        this.isOffline = true;
        if (this.apiStatusInterval) {
          clearInterval(this.apiStatusInterval);
          this.apiStatusInterval = null;
        }
        logger.warn('LayoutManager', 'Too many failures, entering offline mode');
        
        // Retry after 2 minutes
        setTimeout(() => {
          this.consecutiveFailures = 0;
          this.isOffline = false;
          this.checkApiStatus();
          if (!this.apiStatusInterval) {
            this.apiStatusInterval = setInterval(() => {
              if (!this.isOffline && !document.hidden) {
                this.checkApiStatus();
              }
            }, 30000);
          }
        }, 120000);
      }
    }
  }

  /**
   * Inject sidebar HTML
   */
  static async injectSidebar() {
    const container = document.getElementById('sidebar-container');
    if (!container) {
      logger.warn('LayoutManager', 'Sidebar container not found');
      return;
    }

    try {
      // Try primary path
      let response = await fetch('/static/shared/layouts/sidebar.html');
      
      // Fallback to alternative paths if primary fails
      if (!response.ok) {
        const altPaths = [
          '/static/shared/layouts/sidebar.html',
          '../shared/layouts/sidebar.html',
          './shared/layouts/sidebar.html'
        ];
        
        for (const path of altPaths) {
          try {
            response = await fetch(path);
            if (response.ok) break;
          } catch (e) {
            continue;
          }
        }
      }
      
      if (response.ok) {
        const html = await response.text();
        container.innerHTML = html;
      } else {
        throw new Error(`Failed to load sidebar: ${response.status}`);
      }
    } catch (error) {
      logger.error('LayoutManager', 'Failed to load sidebar, using fallback:', error);
      // Fallback: Create minimal sidebar
      container.innerHTML = this._createFallbackSidebar();
    }
  }

  /**
   * Inject header HTML
   */
  static async injectHeader() {
    const container = document.getElementById('header-container');
    if (!container) {
      logger.warn('LayoutManager', 'Header container not found');
      return;
    }

    try {
      // Try primary path
      let response = await fetch('/static/shared/layouts/header.html');
      
      // Fallback to alternative paths if primary fails
      if (!response.ok) {
        const altPaths = [
          '/static/shared/layouts/header.html',
          '../shared/layouts/header.html',
          './shared/layouts/header.html'
        ];
        
        for (const path of altPaths) {
          try {
            response = await fetch(path);
            if (response.ok) break;
          } catch (e) {
            continue;
          }
        }
      }
      
      if (response.ok) {
        const html = await response.text();
        container.innerHTML = html;
        // Update API status
        this.updateApiStatus('checking');
      } else {
        throw new Error(`Failed to load header: ${response.status}`);
      }
    } catch (error) {
      logger.error('LayoutManager', 'Failed to load header, using fallback:', error);
      // Fallback: Create minimal header
      container.innerHTML = this._createFallbackHeader();
      this.updateApiStatus('checking');
    }
  }

  /**
   * Inject footer HTML
   */
  static async injectFooter() {
    const container = document.getElementById('footer-container');
    if (!container) return;

    try {
      // Try primary path
      let response = await fetch('/static/shared/layouts/footer.html');
      
      // Fallback to alternative paths if primary fails
      if (!response.ok) {
        const altPaths = [
          '/static/shared/layouts/footer.html',
          '../shared/layouts/footer.html',
          './shared/layouts/footer.html'
        ];
        
        for (const path of altPaths) {
          try {
            response = await fetch(path);
            if (response.ok) break;
          } catch (e) {
            continue;
          }
        }
      }
      
      if (response.ok) {
        const html = await response.text();
        container.innerHTML = html;
      } else {
        // Footer is optional, just log warning
        logger.warn('LayoutManager', 'Footer not available, skipping');
      }
    } catch (error) {
      // Footer is optional, just log warning
      logger.warn('LayoutManager', 'Failed to load footer:', error);
    }
  }

  /**
   * Set active navigation item based on current page
   */
  static setActiveNav(pageName) {
    // Remove active class from all nav links
    document.querySelectorAll('.nav-link').forEach(link => {
      link.classList.remove('active');
    });

    // Add active class to current page
    const activeLink = document.querySelector(`.nav-link[data-page="${pageName}"]`);
    if (activeLink) {
      activeLink.classList.add('active');
      activeLink.setAttribute('aria-current', 'page');
    }

    // Update page title
    const metadata = PAGE_METADATA.find(p => p.page === pageName);
    if (metadata) {
      document.title = metadata.title;
    }
  }

  /**
   * Update API status badge in header
   */
  static updateApiStatus(status, message = '') {
    const badge = document.getElementById('api-status-badge');
    if (!badge) return;

    badge.setAttribute('data-status', status);

    const statusText = badge.querySelector('.status-text');
    if (statusText) {
      statusText.textContent = message || this.getStatusText(status);
    }
  }

  /**
   * Get status text for badge
   */
  static getStatusText(status) {
    const statusMap = {
      'online': '✅ System Active',
      'offline': '❌ Connection Failed',
      'checking': '⏳ Checking...',
      'degraded': '⚠️ Degraded',
    };
    return statusMap[status] || 'Unknown';
  }

  /**
   * Update last update timestamp in header
   */
  static updateLastUpdate(text) {
    const el = document.getElementById('header-last-update');
    if (!el) return;

    const textEl = el.querySelector('.update-text');
    if (textEl) {
      textEl.textContent = text;
    }
  }

  /**
   * Setup event listeners for layout interactions
   */
  static setupEventListeners() {
    // Mobile sidebar toggle
    const sidebarToggle = document.getElementById('sidebar-toggle');
    if (sidebarToggle) {
      sidebarToggle.addEventListener('click', () => {
        this.toggleSidebar();
      });
    }

    // Theme toggle
    const themeToggle = document.getElementById('theme-toggle-btn');
    if (themeToggle) {
      themeToggle.addEventListener('click', () => {
        this.toggleTheme();
      });
    }

    // Config Helper Modal
    const configHelperBtn = document.getElementById('config-helper-btn');
    if (configHelperBtn) {
      configHelperBtn.addEventListener('click', async () => {
        try {
          const { ConfigHelperModal } = await import('/static/shared/components/config-helper-modal.js');
          if (!window._configHelperModal) {
            window._configHelperModal = new ConfigHelperModal();
          }
          window._configHelperModal.show();
        } catch (error) {
          logger.error('LayoutManager', 'Failed to load config helper:', error);
        }
      });
    }

    // Close sidebar on mobile when clicking a link
    if (window.innerWidth <= 768) {
      document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
          this.closeSidebar();
        });
      });
    }
  }

  /**
   * Toggle sidebar visibility (mobile)
   */
  static toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
      sidebar.classList.toggle('open');
    }
  }

  /**
   * Close sidebar (mobile)
   */
  static closeSidebar() {
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
      sidebar.classList.remove('open');
    }
  }

  /**
   * Toggle theme (dark/light)
   */
  static toggleTheme() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-theme') || 'light';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('crypto_monitor_theme', newTheme);

    // Update visibility of sun/moon icons
    this.updateThemeIcons(newTheme);
    logger.debug('LayoutManager', 'Theme switched to:', newTheme);
  }

  /**
   * Update theme icons visibility
   */
  static updateThemeIcons(theme) {
    const sunIcon = document.querySelector('.icon-sun');
    const moonIcon = document.querySelector('.icon-moon');
    
    if (sunIcon && moonIcon) {
      sunIcon.style.display = theme === 'light' ? 'block' : 'none';
      moonIcon.style.display = theme === 'dark' ? 'block' : 'none';
    }
  }

  /**
   * Initialize theme from localStorage (default: light)
   */
  static initTheme() {
    const savedTheme = localStorage.getItem('crypto_monitor_theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    this.updateThemeIcons(savedTheme);
  }

  /**
   * Create fallback sidebar when file can't be loaded
   * @private
   */
  static _createFallbackSidebar() {
    // Use relative paths that work from any location
    const basePath = window.location.pathname.includes('/static/') 
      ? window.location.pathname.split('/static/')[0] + '/static'
      : '/static';
    
    return `
      <nav class="sidebar" role="navigation">
        <div class="sidebar-header">
          <h2>Crypto Monitor</h2>
        </div>
        <ul class="nav-list">
          <li><a href="${basePath}/pages/dashboard/index.html" class="nav-link" data-page="dashboard">Dashboard</a></li>
          <li><a href="${basePath}/pages/market/index.html" class="nav-link" data-page="market">Market</a></li>
          <li><a href="${basePath}/pages/models/index.html" class="nav-link" data-page="models">AI Models</a></li>
          <li><a href="${basePath}/pages/providers/index.html" class="nav-link" data-page="providers">Providers</a></li>
          <li><a href="${basePath}/pages/sentiment/index.html" class="nav-link" data-page="sentiment">Sentiment</a></li>
          <li><a href="${basePath}/pages/news/index.html" class="nav-link" data-page="news">News</a></li>
          <li><a href="/system-monitor" class="nav-link" data-page="system-monitor">System Monitor</a></li>
        </ul>
      </nav>
    `;
  }

  /**
   * Create fallback header when file can't be loaded
   * @private
   */
  static _createFallbackHeader() {
    return `
      <header class="header">
        <div class="header-content">
          <div class="header-left">
            <button id="sidebar-toggle" class="btn-icon" aria-label="Toggle sidebar">☰</button>
            <h1 class="header-title">Crypto Monitor</h1>
          </div>
          <div class="header-right">
            <span id="api-status-badge" class="status-badge" data-status="checking">
              <span class="status-text">⏳ Checking...</span>
            </span>
          </div>
        </div>
      </header>
    `;
  }
}

// Initialize theme immediately
LayoutManager.initTheme();

export default LayoutManager;
