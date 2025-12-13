/**
 * Loading States Component
 * Provides loading spinners and skeleton screens
 */

export class Loading {
  /**
   * Show loading spinner in container
   */
  static show(containerId, message = 'Loading...') {
    const container = document.getElementById(containerId);
    if (!container) {
      console.warn(`[Loading] Container not found: ${containerId}`);
      return;
    }

    const spinner = document.createElement('div');
    spinner.className = 'loading-container';
    spinner.innerHTML = `
      <div class="spinner"></div>
      <p class="loading-text">${message}</p>
    `;

    container.innerHTML = '';
    container.appendChild(spinner);
  }

  /**
   * Hide loading spinner
   */
  static hide(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const spinner = container.querySelector('.loading-container');
    if (spinner) {
      spinner.remove();
    }
  }

  /**
   * Generate skeleton rows for tables
   */
  static skeletonRows(count = 5, columns = 5) {
    let html = '';
    for (let i = 0; i < count; i++) {
      html += '<tr class="skeleton-row">';
      for (let j = 0; j < columns; j++) {
        html += '<td><div class="skeleton-box"></div></td>';
      }
      html += '</tr>';
    }
    return html;
  }

  /**
   * Generate skeleton cards
   */
  static skeletonCards(count = 4) {
    let html = '';
    for (let i = 0; i < count; i++) {
      html += `
        <div class="skeleton-card">
          <div class="skeleton-box skeleton-title"></div>
          <div class="skeleton-box skeleton-text"></div>
          <div class="skeleton-box skeleton-text"></div>
        </div>
      `;
    }
    return html;
  }

  /**
   * Add skeleton class to elements
   */
  static addSkeleton(selector) {
    document.querySelectorAll(selector).forEach(el => {
      el.classList.add('skeleton');
    });
  }

  /**
   * Remove skeleton class
   */
  static removeSkeleton(selector) {
    document.querySelectorAll(selector).forEach(el => {
      el.classList.remove('skeleton');
    });
  }
}

export default Loading;
