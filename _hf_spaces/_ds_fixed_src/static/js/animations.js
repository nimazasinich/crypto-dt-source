/**
 * ═══════════════════════════════════════════════════════════════════
 * SMOOTH ANIMATIONS & MICRO INTERACTIONS
 * Ultra Smooth, Modern Animations System
 * ═══════════════════════════════════════════════════════════════════
 */

class AnimationController {
    constructor() {
        this.init();
    }

    init() {
        this.setupMicroAnimations();
        this.setupSliderAnimations();
        this.setupButtonAnimations();
        this.setupMenuAnimations();
        this.setupScrollAnimations();
    }

    /**
     * Micro Animations - Subtle feedback
     */
    setupMicroAnimations() {
        // Add micro-bounce to interactive elements
        document.querySelectorAll('button, .nav-button, .stat-card, .glass-card').forEach(el => {
            el.addEventListener('click', (e) => {
                el.classList.add('micro-bounce');
                setTimeout(() => el.classList.remove('micro-bounce'), 600);
            });
        });

        // Add micro-scale on hover for cards
        document.querySelectorAll('.stat-card, .glass-card').forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.style.transition = 'transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
            });
        });
    }

    /**
     * Slider with smooth feedback
     */
    setupSliderAnimations() {
        document.querySelectorAll('.slider-container').forEach(container => {
            const track = container.querySelector('.slider-track');
            const thumb = container.querySelector('.slider-thumb');
            const fill = container.querySelector('.slider-fill');
            const input = container.querySelector('input[type="range"]');

            if (!input) return;

            let isDragging = false;

            const updateSlider = (value) => {
                const min = parseFloat(input.min) || 0;
                const max = parseFloat(input.max) || 100;
                const percentage = ((value - min) / (max - min)) * 100;
                
                if (fill) fill.style.width = `${percentage}%`;
                if (thumb) thumb.style.left = `${percentage}%`;
            };

            input.addEventListener('input', (e) => {
                updateSlider(e.target.value);
                // Add feedback pulse
                container.classList.add('feedback-pulse');
                setTimeout(() => container.classList.remove('feedback-pulse'), 300);
            });

            // Mouse drag
            if (thumb) {
                thumb.addEventListener('mousedown', (e) => {
                    isDragging = true;
                    e.preventDefault();
                });

                document.addEventListener('mousemove', (e) => {
                    if (!isDragging) return;
                    
                    const rect = track.getBoundingClientRect();
                    const x = e.clientX - rect.left;
                    const percentage = Math.max(0, Math.min(100, (x / rect.width) * 100));
                    
                    const min = parseFloat(input.min) || 0;
                    const max = parseFloat(input.max) || 100;
                    const value = min + (percentage / 100) * (max - min);
                    
                    input.value = value;
                    updateSlider(value);
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                });

                document.addEventListener('mouseup', () => {
                    isDragging = false;
                });
            }

            // Initialize
            updateSlider(input.value);
        });
    }

    /**
     * 3D Button animations
     */
    setupButtonAnimations() {
        document.querySelectorAll('.button-3d, button.primary, button.secondary').forEach(button => {
            // Ripple effect
            button.classList.add('feedback-ripple');

            // 3D press effect
            button.addEventListener('mousedown', () => {
                button.style.transform = 'translateY(2px) scale(0.98)';
            });

            button.addEventListener('mouseup', () => {
                button.style.transform = '';
            });

            button.addEventListener('mouseleave', () => {
                button.style.transform = '';
            });
        });
    }

    /**
     * Menu animations
     */
    setupMenuAnimations() {
        // Dropdown menus
        document.querySelectorAll('[data-menu]').forEach(menuTrigger => {
            menuTrigger.addEventListener('click', (e) => {
                e.stopPropagation();
                const menu = document.querySelector(menuTrigger.dataset.menu);
                if (!menu) return;

                const isOpen = menu.classList.contains('menu-open');
                
                // Close all menus
                document.querySelectorAll('.menu-dropdown').forEach(m => {
                    m.classList.remove('menu-open');
                });

                // Toggle current menu
                if (!isOpen) {
                    menu.classList.add('menu-open');
                    this.animateMenuIn(menu);
                }
            });
        });

        // Close menus on outside click
        document.addEventListener('click', (e) => {
            if (!e.target.closest('[data-menu]') && !e.target.closest('.menu-dropdown')) {
                document.querySelectorAll('.menu-dropdown').forEach(menu => {
                    menu.classList.remove('menu-open');
                });
            }
        });
    }

    animateMenuIn(menu) {
        menu.style.opacity = '0';
        menu.style.transform = 'translateY(-10px) scale(0.95)';
        
        // Use setTimeout instead of requestAnimationFrame to avoid performance warnings
        // requestAnimationFrame can trigger warnings if handler takes too long
        setTimeout(() => {
            menu.style.transition = 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)';
            menu.style.opacity = '1';
            menu.style.transform = 'translateY(0) scale(1)';
        }, 0);
    }

    /**
     * Scroll animations
     */
    setupScrollAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, observerOptions);

        document.querySelectorAll('.stat-card, .glass-card, .section').forEach(el => {
            observer.observe(el);
        });
    }

    /**
     * Add smooth transitions to elements
     */
    addSmoothTransition(element, property = 'all') {
        element.style.transition = `${property} 0.3s cubic-bezier(0.4, 0, 0.2, 1)`;
    }
}

// Initialize animations when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.animationController = new AnimationController();
    });
} else {
    window.animationController = new AnimationController();
}

