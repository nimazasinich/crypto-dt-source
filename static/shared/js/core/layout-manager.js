/**
 * Layout Manager
 * Handles injection and management of shared layout components
 */

import { PAGE_METADATA } from './config.js';

export class LayoutManager {
  static layoutsInjected = false;

  /**
   * Inject all layouts (header, sidebar, footer) into current page
   */
  static async injectLayouts() {
    if (this.layoutsInjected) {
      console.log('[LayoutManager] Layouts already injected');
      return;
    }

    try {
      // Inject sidebar
      await this.injectSidebar();

      // Inject header
      await this.injectHeader();

      // Inject footer (if container exists)
      const footerContainer = document.getElementById('footer-container');
      if (footerContainer) {
        await this.injectFooter();
      }

      // Setup event listeners
      this.setupEventListeners();

      // Mark as injected
      this.layoutsInjected = true;

      console.log('[LayoutManager] All layouts injected successfully');
    } catch (error) {
      console.error('[LayoutManager] Failed to inject layouts:', error);
      throw error;
    }
  }

  /**
   * Inject sidebar HTML
   */
  static async injectSidebar() {
    const container = document.getElementById('sidebar-container');
    if (!container) {
      console.warn('[LayoutManager] Sidebar container not found');
      return;
    }

    const response = await fetch('/static/shared/layouts/sidebar.html');
    const html = await response.text();
    container.innerHTML = html;
  }

  /**
   * Inject header HTML
   */
  static async injectHeader() {
    const container = document.getElementById('header-container');
    if (!container) {
      console.warn('[LayoutManager] Header container not found');
      return;
    }

    const response = await fetch('/static/shared/layouts/header.html');
    const html = await response.text();
    container.innerHTML = html;

    // Update API status
    this.updateApiStatus('checking');
  }

  /**
   * Inject footer HTML
   */
  static async injectFooter() {
    const container = document.getElementById('footer-container');
    if (!container) return;

    const response = await fetch('/static/shared/layouts/footer.html');
    const html = await response.text();
    container.innerHTML = html;
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
    const currentTheme = html.getAttribute('data-theme') || 'dark';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('crypto_monitor_theme', newTheme);

    // Update icon
    const themeIcon = document.querySelector('.theme-icon');
    if (themeIcon) {
      themeIcon.textContent = newTheme === 'dark' ? '🌙' : '☀️';
    }

    console.log('[LayoutManager] Theme switched to:', newTheme);
  }

  /**
   * Initialize theme from localStorage
   */
  static initTheme() {
    const savedTheme = localStorage.getItem('crypto_monitor_theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);

    // Update icon if header is loaded
    const themeIcon = document.querySelector('.theme-icon');
    if (themeIcon) {
      themeIcon.textContent = savedTheme === 'dark' ? '🌙' : '☀️';
    }
  }
}

// Initialize theme immediately
LayoutManager.initTheme();

export default LayoutManager;
