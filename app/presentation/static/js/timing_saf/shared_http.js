// Phase 7: Shared HTTP utilities and helpers for Timing SAF page
// This module consolidates duplicated fetchJSON, escapeHtml, and error handling
// across all timing_saf modules to ensure DRY principles and consistent UX.

(function(global){
  'use strict';

  // ------------------ HTML Escaping ------------------
  /**
   * Escape HTML special characters to prevent XSS and ensure safe rendering.
   * @param {string} str - The string to escape
   * @returns {string} - Escaped string safe for innerHTML
   */
  function escapeHtml(str){
    if(str === null || str === undefined) return '';
    return String(str).replace(/[&<>"']/g, char => {
      const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
      };
      return map[char];
    });
  }

  // ------------------ Error Toast Notification ------------------
  /**
   * Display a user-friendly error toast notification.
   * Uses DaisyUI alert or fallback to alert() if toast not available.
   * @param {string} message - Error message to display
   * @param {object} options - Optional configuration {duration: 5000, type: 'error'}
   */
  function showToast(message, options = {}){
    const {
      duration = 5000,
      type = 'error'
    } = options;

    // Check if toast container exists, create if not
    let toastContainer = document.getElementById('safToastContainer');
    if(!toastContainer){
      toastContainer = document.createElement('div');
      toastContainer.id = 'safToastContainer';
      toastContainer.className = 'toast toast-top toast-end z-50';
      document.body.appendChild(toastContainer);
    }

    // Create toast alert
    const toast = document.createElement('div');
    const alertClass = type === 'error' ? 'alert-error' 
                     : type === 'success' ? 'alert-success'
                     : type === 'warning' ? 'alert-warning'
                     : 'alert-info';
    
    toast.className = `alert ${alertClass} shadow-lg max-w-md`;
    toast.innerHTML = `
      <div class="flex items-start gap-2 w-full">
        <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          ${type === 'error' ? '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>' : ''}
          ${type === 'success' ? '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>' : ''}
          ${type === 'warning' ? '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>' : ''}
        </svg>
        <span class="text-sm flex-1">${escapeHtml(message)}</span>
        <button class="btn btn-ghost btn-xs btn-circle" onclick="this.parentElement.parentElement.remove()">✕</button>
      </div>
    `;
    
    toastContainer.appendChild(toast);

    // Auto-remove after duration
    if(duration > 0){
      setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.3s ease-out';
        setTimeout(() => toast.remove(), 300);
      }, duration);
    }
  }

  // ------------------ Fetch JSON Wrapper ------------------
  /**
   * Fetch JSON from URL with standardized error handling and user feedback.
   * Automatically displays error toasts on failure.
   * @param {string} url - URL to fetch
   * @param {object} options - Fetch options (method, headers, body, etc.)
   * @param {object} config - Additional configuration {silent: false, errorPrefix: 'Error'}
   * @returns {Promise<object>} - Parsed JSON response
   * @throws {Error} - Throws on network or HTTP errors
   */
  async function fetchJSON(url, options = {}, config = {}){
    const {
      silent = false,
      errorPrefix = 'Request Error'
    } = config;

    try {
      const response = await fetch(url, options);
      
      // Try to parse response as JSON
      let data = null;
      const contentType = response.headers.get('content-type');
      const isJson = contentType && contentType.includes('application/json');
      
      if(isJson){
        try {
          data = await response.json();
        } catch(parseErr){
          // JSON parse failed, fall back to text
          const text = await response.text();
          throw new Error(`Invalid JSON response: ${text.substring(0, 200)}`);
        }
      } else {
        // Not JSON, get as text
        const text = await response.text();
        if(!response.ok){
          throw new Error(text || `HTTP ${response.status}: ${response.statusText}`);
        }
        // Try parsing anyway in case content-type is wrong
        try {
          data = JSON.parse(text);
        } catch(e){
          throw new Error(`Expected JSON response but got: ${text.substring(0, 200)}`);
        }
      }

      // Check HTTP status
      if(!response.ok){
        const errorMsg = (data && data.detail) 
          ? (typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail))
          : `HTTP ${response.status}: ${response.statusText}`;
        
        if(!silent){
          showToast(`${errorPrefix}: ${errorMsg}`, {type: 'error'});
        }
        
        const error = new Error(errorMsg);
        error.status = response.status;
        error.data = data;
        throw error;
      }

      return data;
    } catch(err){
      // Network error or other exception
      if(!silent){
        showToast(`${errorPrefix}: ${err.message}`, {type: 'error'});
      }
      throw err;
    }
  }

  // ------------------ Selection Helper ------------------
  /**
   * Get current project/subproject selection from global AppSelection.
   * @returns {object} - {project: string, subproject: string}
   */
  function getSelection(){
    return global.AppSelection ? global.AppSelection.get() : {project:'', subproject:''};
  }

  // ------------------ Export Public API ------------------
  global.SAFSharedHttp = {
    escapeHtml,
    showToast,
    fetchJSON,
    getSelection
  };

})(window);
