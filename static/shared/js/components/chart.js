/**
 * Chart Component
 * Wrapper for Chart.js with common configurations
 */

// Chart.js will be loaded from CDN in pages that need it

export class ChartComponent {
  constructor(canvasId, type = 'line', options = {}) {
    this.canvasId = canvasId;
    this.canvas = document.getElementById(canvasId);
    this.type = type;
    this.options = options;
    this.chart = null;

    if (!this.canvas) {
      console.error(`[Chart] Canvas not found: ${canvasId}`);
    }
  }

  /**
   * Create chart with data
   */
  async create(data, customOptions = {}) {
    if (!this.canvas) return;

    // Ensure Chart.js is loaded
    if (typeof Chart === 'undefined') {
      console.error('[Chart] Chart.js not loaded');
      return;
    }

    // Destroy existing chart
    this.destroy();

    const config = {
      type: this.type,
      data: data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        ...this.getDefaultOptions(this.type),
        ...this.options,
        ...customOptions,
      },
    };

    this.chart = new Chart(this.canvas, config);
  }

  /**
   * Update chart data
   */
  update(data) {
    if (!this.chart) {
      console.warn('[Chart] Chart not initialized');
      return;
    }

    this.chart.data = data;
    this.chart.update();
  }

  /**
   * Destroy chart
   */
  destroy() {
    if (this.chart) {
      this.chart.destroy();
      this.chart = null;
    }
  }

  /**
   * Get default options by chart type
   */
  getDefaultOptions(type) {
    const common = {
      plugins: {
        legend: {
          display: true,
          position: 'top',
          labels: {
            color: 'var(--text-normal)',
            font: {
              family: 'var(--font-family-base)',
            },
          },
        },
        tooltip: {
          backgroundColor: 'var(--surface-glass)',
          titleColor: 'var(--text-strong)',
          bodyColor: 'var(--text-normal)',
          borderColor: 'var(--border-default)',
          borderWidth: 1,
        },
      },
    };

    const typeDefaults = {
      line: {
        scales: {
          x: {
            grid: {
              color: 'var(--border-subtle)',
            },
            ticks: {
              color: 'var(--text-soft)',
            },
          },
          y: {
            grid: {
              color: 'var(--border-subtle)',
            },
            ticks: {
              color: 'var(--text-soft)',
            },
          },
        },
      },
      bar: {
        scales: {
          x: {
            grid: {
              display: false,
            },
            ticks: {
              color: 'var(--text-soft)',
            },
          },
          y: {
            grid: {
              color: 'var(--border-subtle)',
            },
            ticks: {
              color: 'var(--text-soft)',
            },
          },
        },
      },
      doughnut: {
        plugins: {
          legend: {
            position: 'right',
          },
        },
      },
    };

    return {
      ...common,
      ...(typeDefaults[type] || {}),
    };
  }
}

/**
 * Load Chart.js from CDN if not already loaded
 */
export async function loadChartJS() {
  if (typeof Chart !== 'undefined') {
    return Promise.resolve();
  }

  return new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js';
    script.onload = () => {
      console.log('[Chart] Chart.js loaded from CDN');
      resolve();
    };
    script.onerror = () => {
      console.error('[Chart] Failed to load Chart.js');
      reject(new Error('Failed to load Chart.js'));
    };
    document.head.appendChild(script);
  });
}

export default ChartComponent;
