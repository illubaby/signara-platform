// Timing QC: Shared HTTP Utilities
// This module provides centralized HTTP utilities, HTML sanitization, and ANSI color conversion
// for the Timing QC page.

(function(global){
  'use strict';

  // ------------------ HTML Escaping ------------------
  /**
   * Basic HTML escaping for XSS prevention
   * @param {string} str - String to escape
   * @returns {string} - Escaped string
   */
  function escapeHTML(str){
    if(!str) return '';
    return String(str).replace(/[&<>]/g, char => {
      const map = {'&': '&amp;', '<': '&lt;', '>': '&gt;'};
      return map[char];
    });
  }

  /**
   * Enhanced HTML escaping including quotes
   * @param {string} str - String to escape
   * @returns {string} - Escaped string
   */
  function escapeForHtml(str){
    if(!str) return '';
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  // ------------------ ANSI Color Conversion ------------------
  const ANSI_COLORS = {
    30: 'ansi-black',
    31: 'text-error',
    32: 'text-success',
    33: 'text-warning',
    34: 'text-info',
    35: 'text-secondary',
    36: 'text-accent',
    37: '',
    90: 'opacity-70',
    91: 'text-error',
    92: 'text-success',
    93: 'text-warning',
    94: 'text-info',
    95: 'text-secondary',
    96: 'text-accent',
    97: ''
  };

  /**
   * Convert ANSI color codes to HTML with DaisyUI classes
   * @param {string} txt - Text with ANSI codes
   * @returns {string} - HTML with color classes
   */
  function ansiToHtml(txt){
    if(!txt) return '';
    const pattern = /\x1b\[(\d+(?:;\d+)*)m/g;
    let lastIndex = 0;
    let html = '';
    let open = false;
    let match;
    
    while((match = pattern.exec(txt)) !== null){
      const chunk = txt.slice(lastIndex, match.index);
      if(chunk){ html += escapeForHtml(chunk); }
      
      const codes = match[1].split(';').filter(Boolean);
      
      // Handle reset code (0)
      if(codes.includes('0')){
        if(open){ html += '</span>'; open = false; }
        codes.splice(codes.indexOf('0'), 1);
      }
      
      // Find color code
      const colorCode = [...codes].reverse().find(c => ANSI_COLORS[c] !== undefined);
      if(colorCode){
        if(open){ html += '</span>'; }
        const cls = ANSI_COLORS[colorCode] || '';
        html += `<span class="${cls}">`;
        open = true;
      }
      
      lastIndex = pattern.lastIndex;
    }
    
    const rest = txt.slice(lastIndex);
    if(rest){ html += escapeForHtml(rest); }
    if(open){ html += '</span>'; }
    
    return html;
  }

  // ------------------ Toast Notification ------------------
  /**
   * Display toast notification to user
   * @param {string} message - Message to display
   * @param {object} options - {duration: 5000, type: 'error'|'success'|'warning'|'info'}
   */
  function showToast(message, options = {}){
    const {
      duration = 5000,
      type = 'error'
    } = options;

    // Get or create toast container
    let toastContainer = document.getElementById('qcToastContainer');
    if(!toastContainer){
      toastContainer = document.createElement('div');
      toastContainer.id = 'qcToastContainer';
      toastContainer.className = 'toast toast-top toast-end z-50';
      document.body.appendChild(toastContainer);
    }

    // Create toast
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
        <span class="text-sm flex-1">${escapeHTML(message)}</span>
        <button class="btn btn-ghost btn-xs btn-circle" onclick="this.parentElement.parentElement.remove()">✕</button>
      </div>
    `;
    
    toastContainer.appendChild(toast);

    // Auto-remove
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
   * Fetch JSON with standardized error handling
   * @param {string} url - URL to fetch
   * @param {object} options - Fetch options
   * @param {object} config - {silent: false, errorPrefix: 'Error'}
   * @returns {Promise<object>} - Parsed JSON response
   */
  async function fetchJSON(url, options = {}, config = {}){
    const {
      silent = false,
      errorPrefix = 'Request Error'
    } = config;

    try {
      const response = await fetch(url, options);
      
      // Try to parse response
      let data;
      const contentType = response.headers.get('content-type');
      if(contentType && contentType.includes('application/json')){
        data = await response.json();
      } else {
        const text = await response.text();
        try {
          data = JSON.parse(text);
        } catch(e){
          // Not JSON, throw as text
          if(!response.ok){
            throw new Error(text || `HTTP ${response.status}`);
          }
          return text;
        }
      }

      if(!response.ok){
        const errorMsg = data && data.detail ? data.detail : `HTTP ${response.status}`;
        throw new Error(errorMsg);
      }

      return data;
    } catch(error){
      if(!silent){
        showToast(`${errorPrefix}: ${error.message}`, {type: 'error'});
      }
      throw error;
    }
  }

  // ------------------ Export to Global Scope ------------------
  global.QCSharedHttp = {
    fetchJSON,
    escapeHTML,
    escapeForHtml,
    ansiToHtml,
    showToast
  };

  console.log('[Timing QC] shared_http.js loaded');

})(window);
