(function () {
  const stack = document.createElement('div');
  stack.className = 'toast-stack';
  const mountStack = () => document.body.appendChild(stack);
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mountStack, { once: true });
  } else {
    mountStack();
  }

  const createToast = (type, title, message) => {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<div><strong>${title}</strong>${message ? `<small>${message}</small>` : ''}</div>`;
    stack.appendChild(toast);
    setTimeout(() => toast.remove(), 4500);
  };

  const setBadge = (element, text, tone = 'info') => {
    if (!element) return;
    element.textContent = text;
    element.className = `badge ${tone}`;
  };

  const showLoading = (container, message = 'Loading data...') => {
    if (!container) return;
    container.innerHTML = `<div class="loading-indicator">${message}</div>`;
  };

  const fadeReplace = (container, html) => {
    if (!container) return;
    container.innerHTML = html;
    container.classList.add('fade-in');
    setTimeout(() => container.classList.remove('fade-in'), 200);
  };

  const fetchJSON = async (url, options = {}, context = '') => {
    try {
      const response = await fetch(url, options);
      if (!response.ok) {
        const text = await response.text();
        createToast('error', context || 'Request failed', text || response.statusText);
        throw new Error(text || response.statusText);
      }
      return await response.json();
    } catch (err) {
      createToast('error', context || 'Network error', err.message || String(err));
      throw err;
    }
  };

  window.UIFeedback = {
    toast: createToast,
    setBadge,
    showLoading,
    fadeReplace,
    fetchJSON,
  };
})();
