/**
 * AttendAI — Javascript Utilities
 */

const Utils = {
  /**
   * Helper to perform AJAX requests with JSON parsing
   */
  async fetchJSON(url, options = {}) {
    const defaultHeaders = {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    };

    options.headers = {
      ...defaultHeaders,
      ...options.headers
    };

    if (options.body && typeof options.body === 'object') {
      options.body = JSON.stringify(options.body);
    }

    try {
      const response = await fetch(url, options);
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || `HTTP error! status: ${response.status}`);
      }
      return data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  },

  /**
   * Format numbers (e.g., 1000 -> 1,000)
   */
  formatNumber(num) {
    return new Intl.NumberFormat().format(num);
  },

  /**
   * Show element loading spinner
   */
  showLoading(element) {
    if (!element) return;
    element.classList.add('position-relative');
    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.innerHTML = '<div class="spinner-border spinner-border-sm text-primary" role="status"><span class="visually-hidden">Loading...</span></div>';
    element.appendChild(overlay);
  },

  /**
   * Hide element loading spinner
   */
  hideLoading(element) {
    if (!element) return;
    const overlay = element.querySelector('.loading-overlay');
    if (overlay) {
      overlay.remove();
    }
  }
};
