/**
 * Sidebar Manager - Handles collapse/expand and mobile behavior
 */

class SidebarManager {
  constructor() {
    this.sidebar = null;
    this.toggleBtn = null;
    this.overlay = null;
    this.isCollapsed = false;
    this.isMobile = window.innerWidth <= 1024;
    
    this.init();
  }

  init() {
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.setup());
    } else {
      this.setup();
    }
  }

  setup() {
    this.sidebar = document.getElementById('sidebar-modern') || document.querySelector('.sidebar-modern');
    this.toggleBtn = document.getElementById('sidebar-collapse-btn');
    this.overlay = document.getElementById('sidebar-overlay-modern') || document.querySelector('.sidebar-overlay-modern');

    if (!this.sidebar) {
      console.warn('Sidebar not found');
      return;
    }

    // Load saved state
    this.loadState();

    // Setup event listeners
    this.setupEventListeners();

    // Handle responsive behavior
    this.handleResize();
  }

  setupEventListeners() {
    // Toggle button
    if (this.toggleBtn) {
      this.toggleBtn.addEventListener('click', () => this.toggle());
    }

    // Overlay click (mobile)
    if (this.overlay) {
      this.overlay.addEventListener('click', () => this.close());
    }

    // Resize handler
    window.addEventListener('resize', () => this.handleResize());

    // ESC key to close on mobile
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.isMobile && this.sidebar.classList.contains('open')) {
        this.close();
      }
    });

    // Close sidebar on nav link click (mobile only)
    const navLinks = this.sidebar.querySelectorAll('.nav-link-modern');
    navLinks.forEach(link => {
      link.addEventListener('click', () => {
        if (this.isMobile) {
          this.close();
        }
      });
    });

    // Set active page
    this.setActivePage();
  }

  toggle() {
    if (this.isMobile) {
      // On mobile, toggle open/close
      this.sidebar.classList.toggle('open');
      this.overlay?.classList.toggle('active');
    } else {
      // On desktop, toggle collapsed state
      this.isCollapsed = !this.isCollapsed;
      this.sidebar.classList.toggle('collapsed');
      this.saveState();
      
      // Dispatch event for other components
      window.dispatchEvent(new CustomEvent('sidebar-toggle', {
        detail: { collapsed: this.isCollapsed }
      }));
    }
  }

  open() {
    if (this.isMobile) {
      this.sidebar.classList.add('open');
      this.overlay?.classList.add('active');
      document.body.style.overflow = 'hidden';
    }
  }

  close() {
    if (this.isMobile) {
      this.sidebar.classList.remove('open');
      this.overlay?.classList.remove('active');
      document.body.style.overflow = '';
    }
  }

  collapse() {
    if (!this.isMobile && !this.isCollapsed) {
      this.isCollapsed = true;
      this.sidebar.classList.add('collapsed');
      this.saveState();
    }
  }

  expand() {
    if (!this.isMobile && this.isCollapsed) {
      this.isCollapsed = false;
      this.sidebar.classList.remove('collapsed');
      this.saveState();
    }
  }

  handleResize() {
    const wasMobile = this.isMobile;
    this.isMobile = window.innerWidth <= 1024;

    // If switching from mobile to desktop or vice versa
    if (wasMobile !== this.isMobile) {
      // Clean up mobile state
      if (!this.isMobile) {
        this.sidebar.classList.remove('open');
        this.overlay?.classList.remove('active');
        document.body.style.overflow = '';
        
        // Restore collapsed state on desktop
        if (this.isCollapsed) {
          this.sidebar.classList.add('collapsed');
        }
      } else {
        // On mobile, remove collapsed state
        this.sidebar.classList.remove('collapsed');
      }
    }
  }

  setActivePage() {
    // Get current page from URL
    const path = window.location.pathname;
    const pageName = this.getPageNameFromPath(path);

    if (!pageName) return;

    // Remove active class from all links
    const navLinks = this.sidebar.querySelectorAll('.nav-link-modern');
    navLinks.forEach(link => {
      link.classList.remove('active');
      link.removeAttribute('aria-current');
    });

    // Add active class to current page link
    const activeLink = this.sidebar.querySelector(`[data-page="${pageName}"]`);
    if (activeLink) {
      activeLink.classList.add('active');
      activeLink.setAttribute('aria-current', 'page');
    }
  }

  getPageNameFromPath(path) {
    // Extract page name from path
    // e.g., /static/pages/dashboard/index.html -> dashboard
    const match = path.match(/\/pages\/([^\/]+)\//);
    return match ? match[1] : null;
  }

  saveState() {
    try {
      localStorage.setItem('sidebar_collapsed', JSON.stringify(this.isCollapsed));
    } catch (error) {
      console.warn('Failed to save sidebar state:', error);
    }
  }

  loadState() {
    try {
      const saved = localStorage.getItem('sidebar_collapsed');
      if (saved !== null) {
        this.isCollapsed = JSON.parse(saved);
        if (this.isCollapsed && !this.isMobile) {
          this.sidebar.classList.add('collapsed');
        }
      }
    } catch (error) {
      console.warn('Failed to load sidebar state:', error);
    }
  }

  // Public API
  getState() {
    return {
      isCollapsed: this.isCollapsed,
      isMobile: this.isMobile,
      isOpen: this.sidebar?.classList.contains('open') || false
    };
  }
}

// Initialize and export
const sidebarManager = new SidebarManager();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = sidebarManager;
}

export default sidebarManager;

