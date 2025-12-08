/**
 * UI Animations & Interactions
 * Smooth animations, transitions, and micro-interactions
 */

export class UIAnimations {
  /**
   * Animate number counting up
   * @param {HTMLElement} element - Target element
   * @param {number} target - Target number
   * @param {number} duration - Animation duration in ms
   * @param {string} suffix - Optional suffix (e.g., '%', 'K')
   */
  static animateNumber(element, target, duration = 1000, suffix = '') {
    if (!element) return;
    
    const start = parseFloat(element.textContent) || 0;
    const increment = (target - start) / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
      current += increment;
      
      if ((increment > 0 && current >= target) || (increment < 0 && current <= target)) {
        current = target;
        clearInterval(timer);
      }
      
      element.textContent = Math.round(current) + suffix;
    }, 16);
  }

  /**
   * Animate element entrance with fade and slide
   * @param {HTMLElement} element - Target element
   * @param {string} direction - 'up', 'down', 'left', 'right'
   * @param {number} delay - Delay in ms
   */
  static animateEntrance(element, direction = 'up', delay = 0) {
    if (!element) return;
    
    const directions = {
      up: { x: 0, y: 20 },
      down: { x: 0, y: -20 },
      left: { x: 20, y: 0 },
      right: { x: -20, y: 0 }
    };
    
    const { x, y } = directions[direction] || directions.up;
    
    element.style.opacity = '0';
    element.style.transform = `translate(${x}px, ${y}px)`;
    element.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    
    setTimeout(() => {
      element.style.opacity = '1';
      element.style.transform = 'translate(0, 0)';
    }, delay);
  }

  /**
   * Stagger animation for multiple elements
   * @param {NodeList|Array} elements - Elements to animate
   * @param {number} staggerDelay - Delay between each element in ms
   */
  static staggerAnimation(elements, staggerDelay = 100) {
    if (!elements || elements.length === 0) return;
    
    elements.forEach((element, index) => {
      this.animateEntrance(element, 'up', index * staggerDelay);
    });
  }

  /**
   * Create ripple effect on click
   * @param {Event} event - Click event
   * @param {HTMLElement} element - Target element
   */
  static createRipple(event, element) {
    if (!element) return;
    
    const ripple = document.createElement('span');
    const rect = element.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;
    
    ripple.style.cssText = `
      position: absolute;
      width: ${size}px;
      height: ${size}px;
      left: ${x}px;
      top: ${y}px;
      background: rgba(255, 255, 255, 0.5);
      border-radius: 50%;
      transform: scale(0);
      animation: ripple 0.6s ease-out;
      pointer-events: none;
    `;
    
    element.style.position = 'relative';
    element.style.overflow = 'hidden';
    element.appendChild(ripple);
    
    setTimeout(() => ripple.remove(), 600);
  }

  /**
   * Smooth scroll to element
   * @param {string|HTMLElement} target - Target element or selector
   * @param {number} offset - Offset from top in px
   */
  static smoothScrollTo(target, offset = 0) {
    const element = typeof target === 'string' 
      ? document.querySelector(target) 
      : target;
    
    if (!element) return;
    
    const targetPosition = element.getBoundingClientRect().top + window.pageYOffset - offset;
    
    window.scrollTo({
      top: targetPosition,
      behavior: 'smooth'
    });
  }

  /**
   * Parallax effect on scroll
   * @param {HTMLElement} element - Target element
   * @param {number} speed - Parallax speed (0.1 - 1)
   */
  static initParallax(element, speed = 0.5) {
    if (!element) return;
    
    const handleScroll = () => {
      const scrolled = window.pageYOffset;
      const rate = scrolled * speed;
      element.style.transform = `translateY(${rate}px)`;
    };
    
    window.addEventListener('scroll', handleScroll, { passive: true });
    
    return () => window.removeEventListener('scroll', handleScroll);
  }

  /**
   * Intersection Observer for lazy animations
   * @param {string} selector - CSS selector for elements
   * @param {Function} callback - Callback when element is visible
   * @param {Object} options - Intersection Observer options
   */
  static observeElements(selector, callback, options = {}) {
    const defaultOptions = {
      threshold: 0.1,
      rootMargin: '0px',
      ...options
    };
    
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          callback(entry.target);
          observer.unobserve(entry.target);
        }
      });
    }, defaultOptions);
    
    document.querySelectorAll(selector).forEach(el => observer.observe(el));
    
    return observer;
  }

  /**
   * Create sparkline SVG
   * @param {Array} data - Array of numbers
   * @param {number} width - SVG width
   * @param {number} height - SVG height
   * @returns {string} SVG string
   */
  static createSparkline(data, width = 60, height = 24) {
    if (!data || data.length === 0) return '';
    
    const max = Math.max(...data);
    const min = Math.min(...data);
    const range = max - min || 1;
    
    const points = data.map((value, index) => {
      const x = (index / (data.length - 1)) * width;
      const y = height - ((value - min) / range) * height;
      return `${x},${y}`;
    }).join(' ');
    
    return `
      <svg class="sparkline" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">
        <polyline points="${points}" fill="none" stroke="currentColor" stroke-width="2" />
      </svg>
    `;
  }

  /**
   * Progress bar animation
   * @param {HTMLElement} element - Progress bar element
   * @param {number} percentage - Target percentage (0-100)
   * @param {number} duration - Animation duration in ms
   */
  static animateProgress(element, percentage, duration = 1000) {
    if (!element) return;
    
    const start = parseFloat(element.style.width) || 0;
    const target = Math.min(Math.max(percentage, 0), 100);
    const increment = (target - start) / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
      current += increment;
      
      if ((increment > 0 && current >= target) || (increment < 0 && current <= target)) {
        current = target;
        clearInterval(timer);
      }
      
      element.style.width = `${current}%`;
    }, 16);
  }

  /**
   * Shake animation for errors
   * @param {HTMLElement} element - Target element
   */
  static shake(element) {
    if (!element) return;
    
    element.style.animation = 'shake 0.5s ease';
    
    setTimeout(() => {
      element.style.animation = '';
    }, 500);
  }

  /**
   * Pulse animation
   * @param {HTMLElement} element - Target element
   * @param {number} duration - Duration in ms
   */
  static pulse(element, duration = 1000) {
    if (!element) return;
    
    element.style.animation = `pulse ${duration}ms ease`;
    
    setTimeout(() => {
      element.style.animation = '';
    }, duration);
  }

  /**
   * Typewriter effect
   * @param {HTMLElement} element - Target element
   * @param {string} text - Text to type
   * @param {number} speed - Typing speed in ms per character
   */
  static typewriter(element, text, speed = 50) {
    if (!element) return;
    
    element.textContent = '';
    let index = 0;
    
    const timer = setInterval(() => {
      if (index < text.length) {
        element.textContent += text.charAt(index);
        index++;
      } else {
        clearInterval(timer);
      }
    }, speed);
    
    return timer;
  }

  /**
   * Confetti effect (lightweight)
   * @param {Object} options - Confetti options
   */
  static confetti(options = {}) {
    const defaults = {
      particleCount: 50,
      spread: 70,
      origin: { y: 0.6 },
      colors: ['#2dd4bf', '#22d3ee', '#3b82f6']
    };
    
    const config = { ...defaults, ...options };
    const container = document.createElement('div');
    container.style.cssText = `
      position: fixed;
      inset: 0;
      pointer-events: none;
      z-index: 9999;
    `;
    document.body.appendChild(container);
    
    for (let i = 0; i < config.particleCount; i++) {
      const particle = document.createElement('div');
      const color = config.colors[Math.floor(Math.random() * config.colors.length)];
      const angle = Math.random() * config.spread - config.spread / 2;
      const velocity = Math.random() * 10 + 5;
      
      particle.style.cssText = `
        position: absolute;
        width: 8px;
        height: 8px;
        background: ${color};
        left: 50%;
        top: ${config.origin.y * 100}%;
        border-radius: 50%;
        animation: confetti 2s ease-out forwards;
        transform: rotate(${angle}deg) translateY(-${velocity}px);
      `;
      
      container.appendChild(particle);
    }
    
    setTimeout(() => container.remove(), 2000);
  }

  /**
   * Initialize all animations on page load
   */
  static init() {
    // Add ripple effect to buttons
    document.querySelectorAll('.btn-primary, .btn-gradient').forEach(button => {
      button.addEventListener('click', (e) => this.createRipple(e, button));
    });
    
    // Animate elements on scroll
    this.observeElements('.stat-card-enhanced, .glass-card', (element) => {
      this.animateEntrance(element, 'up');
    });
    
    // Add shake animation keyframes if not exists
    if (!document.querySelector('#ui-animations-styles')) {
      const style = document.createElement('style');
      style.id = 'ui-animations-styles';
      style.textContent = `
        @keyframes ripple {
          to {
            transform: scale(4);
            opacity: 0;
          }
        }
        
        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
          20%, 40%, 60%, 80% { transform: translateX(5px); }
        }
        
        @keyframes confetti {
          0% {
            transform: translateY(0) rotate(0deg);
            opacity: 1;
          }
          100% {
            transform: translateY(100vh) rotate(720deg);
            opacity: 0;
          }
        }
      `;
      document.head.appendChild(style);
    }
  }
}

// Auto-initialize on DOM ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => UIAnimations.init());
} else {
  UIAnimations.init();
}

export default UIAnimations;
