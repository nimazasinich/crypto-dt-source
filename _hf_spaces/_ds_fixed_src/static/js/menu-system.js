/**
 * ═══════════════════════════════════════════════════════════════════
 * COMPLETE MENU SYSTEM
 * All Menus Implementation with Smooth Animations
 * ═══════════════════════════════════════════════════════════════════
 */

class MenuSystem {
    constructor() {
        this.menus = new Map();
        this.activeMenu = null;
        this.init();
    }

    init() {
        this.setupDropdownMenus();
        this.setupContextMenus();
        this.setupMobileMenus();
        this.setupSubmenus();
        this.setupKeyboardNavigation();
    }

    /**
     * Dropdown Menus
     */
    setupDropdownMenus() {
        document.querySelectorAll('[data-menu-trigger]').forEach(trigger => {
            const menuId = trigger.dataset.menuTrigger;
            const menu = document.querySelector(`[data-menu="${menuId}"]`);
            
            if (!menu) return;

            // Show menu initially for positioning
            menu.style.display = 'block';
            menu.style.visibility = 'hidden';

            this.menus.set(menuId, { trigger, menu, type: 'dropdown' });

            trigger.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleMenu(menuId);
            });

            // Handle menu item clicks
            menu.querySelectorAll('.menu-item').forEach(item => {
                item.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const action = item.dataset.action;
                    if (action) {
                        this.handleMenuAction(action);
                    }
                    this.closeMenu(menu);
                });
            });
        });

        // Close on outside click
        document.addEventListener('click', (e) => {
            if (!e.target.closest('[data-menu]') && !e.target.closest('[data-menu-trigger]')) {
                this.closeAllMenus();
            }
        });
    }

    /**
     * Context Menus (Right-click)
     */
    setupContextMenus() {
        document.querySelectorAll('[data-context-menu]').forEach(element => {
            const menuId = element.dataset.contextMenu;
            const menu = document.querySelector(`[data-context-menu-target="${menuId}"]`);
            
            if (!menu) return;

            element.addEventListener('contextmenu', (e) => {
                e.preventDefault();
                this.showContextMenu(menu, e.clientX, e.clientY);
            });
        });

        // Close context menu on click
        document.addEventListener('click', () => {
            document.querySelectorAll('[data-context-menu-target]').forEach(menu => {
                menu.classList.remove('context-menu-open');
            });
        });
    }

    /**
     * Mobile Menu
     */
    setupMobileMenus() {
        const mobileMenuToggle = document.querySelector('[data-mobile-menu-toggle]');
        const mobileMenu = document.querySelector('[data-mobile-menu]');

        if (mobileMenuToggle && mobileMenu) {
            mobileMenuToggle.addEventListener('click', () => {
                mobileMenu.classList.toggle('mobile-menu-open');
                mobileMenuToggle.classList.toggle('mobile-menu-active');
            });
        }
    }

    /**
     * Submenus
     */
    setupSubmenus() {
        document.querySelectorAll('[data-submenu-trigger]').forEach(trigger => {
            const submenu = trigger.nextElementSibling;
            if (!submenu || !submenu.classList.contains('submenu')) return;

            trigger.addEventListener('mouseenter', () => {
                this.showSubmenu(submenu, trigger);
            });

            trigger.addEventListener('mouseleave', () => {
                setTimeout(() => {
                    if (!submenu.matches(':hover')) {
                        this.hideSubmenu(submenu);
                    }
                }, 200);
            });

            submenu.addEventListener('mouseleave', () => {
                this.hideSubmenu(submenu);
            });
        });
    }

    /**
     * Keyboard Navigation
     */
    setupKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            // ESC to close menus
            if (e.key === 'Escape') {
                this.closeAllMenus();
            }

            // Arrow keys for navigation
            if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
                const activeMenu = document.querySelector('.menu-open, .context-menu-open');
                if (activeMenu) {
                    e.preventDefault();
                    this.navigateMenu(activeMenu, e.key === 'ArrowDown' ? 1 : -1);
                }
            }
        });
    }

    toggleMenu(menuId) {
        const menuData = this.menus.get(menuId);
        if (!menuData) return;

        const { menu, trigger } = menuData;

        // Close other menus
        if (this.activeMenu && this.activeMenu !== menu) {
            this.closeMenu(this.activeMenu);
        }

        // Toggle current menu
        if (menu.classList.contains('menu-open')) {
            this.closeMenu(menu);
        } else {
            this.openMenu(menu, trigger);
        }
    }

    openMenu(menu, trigger) {
        menu.style.visibility = 'visible';
        menu.classList.add('menu-open');
        trigger?.classList.add('menu-trigger-active');
        this.activeMenu = menu;

        // Animate in
        this.animateMenuIn(menu, trigger);
    }

    closeMenu(menu) {
        menu.classList.remove('menu-open');
        const trigger = Array.from(this.menus.values()).find(m => m.menu === menu)?.trigger;
        trigger?.classList.remove('menu-trigger-active');
        
        if (this.activeMenu === menu) {
            this.activeMenu = null;
        }

        // Animate out
        this.animateMenuOut(menu);
    }

    closeAllMenus() {
        document.querySelectorAll('.menu-open, .context-menu-open').forEach(menu => {
            this.closeMenu(menu);
        });
    }

    showContextMenu(menu, x, y) {
        // Close other context menus
        document.querySelectorAll('[data-context-menu-target]').forEach(m => {
            m.classList.remove('context-menu-open');
        });

        menu.style.left = `${x}px`;
        menu.style.top = `${y}px`;
        menu.classList.add('context-menu-open');
        this.activeMenu = menu;

        this.animateMenuIn(menu);
    }

    showSubmenu(submenu, trigger) {
        const triggerRect = trigger.getBoundingClientRect();
        submenu.style.top = `${triggerRect.top}px`;
        submenu.style.left = `${triggerRect.right + 8}px`;
        submenu.classList.add('submenu-open');
    }

    hideSubmenu(submenu) {
        submenu.classList.remove('submenu-open');
    }

    navigateMenu(menu, direction) {
        const items = menu.querySelectorAll('.menu-item:not(.disabled)');
        if (items.length === 0) return;

        let currentIndex = Array.from(items).findIndex(item => item.classList.contains('menu-item-active'));
        
        if (currentIndex === -1) {
            currentIndex = direction > 0 ? 0 : items.length - 1;
        } else {
            currentIndex += direction;
            if (currentIndex < 0) currentIndex = items.length - 1;
            if (currentIndex >= items.length) currentIndex = 0;
        }

        items.forEach((item, index) => {
            item.classList.toggle('menu-item-active', index === currentIndex);
        });

        items[currentIndex]?.focus();
    }

    animateMenuIn(menu, trigger) {
        menu.style.opacity = '0';
        menu.style.transform = 'translateY(-10px) scale(0.95)';
        menu.style.pointerEvents = 'none';

        requestAnimationFrame(() => {
            menu.style.transition = 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)';
            menu.style.opacity = '1';
            menu.style.transform = 'translateY(0) scale(1)';
            menu.style.pointerEvents = 'auto';
        });
    }

    animateMenuOut(menu) {
        menu.style.transition = 'all 0.15s cubic-bezier(0.4, 0, 0.2, 1)';
        menu.style.opacity = '0';
        menu.style.transform = 'translateY(-10px) scale(0.95)';
        
        setTimeout(() => {
            menu.style.pointerEvents = 'none';
            menu.style.visibility = 'hidden';
        }, 150);
    }

    handleMenuAction(action) {
        switch(action) {
            case 'theme-light':
                document.body.setAttribute('data-theme', 'light');
                break;
            case 'theme-dark':
                document.body.setAttribute('data-theme', 'dark');
                break;
            case 'settings':
                // Navigate to settings page
                const settingsBtn = document.querySelector('[data-nav="page-settings"]');
                if (settingsBtn) settingsBtn.click();
                break;
            default:
                console.log('Menu action:', action);
        }
    }
}

// Initialize menu system
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.menuSystem = new MenuSystem();
    });
} else {
    window.menuSystem = new MenuSystem();
}

