// Shared WebSocket Output Stream Module
// Reusable real-time output streaming for any feature requiring script execution feedback

(function(global) {
  'use strict';

  /**
   * WebSocketOutputStream - Manages WebSocket connection for streaming command output
   * 
   * Features:
   * - Real-time output streaming with ANSI color support
   * - Bidirectional communication (send stop signals)
   * - Auto-scroll capability
   * - Status tracking (running, completed, failed)
   * - Elapsed time tracking
   * - Event callbacks for lifecycle hooks
   */
  class WebSocketOutputStream {
    constructor(config) {
      // Required configuration
      this.outputElement = config.outputElement; // DOM element for output
      this.wsUrl = config.wsUrl; // WebSocket URL
      
      // Optional configuration
      this.autoScrollElement = config.autoScrollElement || null; // Checkbox for auto-scroll
      this.statusElement = config.statusElement || null; // Element to show status
      this.elapsedElement = config.elapsedElement || null; // Element to show elapsed time
      this.onOpen = config.onOpen || null; // Callback when WS opens
      this.onMessage = config.onMessage || null; // Callback on each message
      this.onComplete = config.onComplete || null; // Callback when execution completes
      this.onError = config.onError || null; // Callback on error
      this.onClose = config.onClose || null; // Callback when WS closes
      
      // Internal state
      this.ws = null;
      this.startTime = null;
      this.closed = false;
    }

    /**
     * Connect and start streaming
     */
    connect() {
      if (this.ws) {
        console.warn('[WebSocketOutputStream] Already connected');
        return;
      }

      this.startTime = performance.now();
      this.closed = false;

      try {
        this.ws = new WebSocket(this.wsUrl);
      } catch (e) {
        this._handleError('WebSocket initialization failed', e);
        return;
      }

      this.ws.onopen = () => this._handleOpen();
      this.ws.onmessage = (event) => this._handleMessage(event);
      this.ws.onclose = () => this._handleClose();
      this.ws.onerror = () => this._handleWSError();
    }

    /**
     * Send stop signal to server
     */
    stop() {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        try {
          this.ws.send(JSON.stringify({ action: 'stop' }));
          this.appendOutput('\n[Stopped by user]\n');
          this._updateStatus('Stopped', 'warning');
        } catch (e) {
          console.error('[WebSocketOutputStream] Error sending stop signal:', e);
        }
      }
    }

    /**
     * Close WebSocket connection
     */
    close() {
      if (this.ws) {
        this.closed = true;
        try {
          this.ws.close();
        } catch (e) {
          console.error('[WebSocketOutputStream] Error closing WebSocket:', e);
        }
        this.ws = null;
      }
    }

    /**
     * Clear output display
     */
    clearOutput() {
      if (this.outputElement) {
        this.outputElement.innerHTML = '';
      }
    }

    /**
     * Append text to output (with ANSI color support)
     * @param {string} text - Text to append
     */
    appendOutput(text) {
      if (!this.outputElement) return;

      const html = this._ansiToHtml(text);
      this.outputElement.innerHTML += html;

      // Auto-scroll if enabled
      if (this.autoScrollElement && this.autoScrollElement.checked) {
        this.outputElement.scrollTop = this.outputElement.scrollHeight;
      }
    }

    /**
     * Get elapsed time in seconds
     * @returns {number} Elapsed time
     */
    getElapsedTime() {
      if (!this.startTime) return 0;
      return ((performance.now() - this.startTime) / 1000).toFixed(1);
    }

    // ==================== Private Methods ====================

    _handleOpen() {
      console.log('[WebSocketOutputStream] Connected');
      this._updateStatus('Running...', 'warning');
      if (this.onOpen) this.onOpen();
    }

    _handleMessage(event) {
      try {
        const msg = JSON.parse(event.data);

        // Stream output
        if (msg.stream) {
          this.appendOutput(msg.data);
          if (this.onMessage) this.onMessage(msg);
        }
        // Error event
        else if (msg.event === 'error') {
          this.appendOutput(`\nERROR: ${msg.detail}\n`);
          this._updateStatus('Error occurred', 'error');
          if (this.elapsedElement) {
            this.elapsedElement.textContent = `${this.getElapsedTime()}s`;
          }
          if (this.onError) this.onError(msg);
        }
        // Completion event
        else if (msg.event === 'end') {
          const elapsed = this.getElapsedTime();
          const success = msg.return_code === 0;
          const statusText = success ? 'Completed' : 'Failed';
          const statusClass = success ? 'success' : 'error';
          
          this._updateStatus(`${statusText} (exit code: ${msg.return_code})`, statusClass);
          
          if (this.elapsedElement) {
            this.elapsedElement.textContent = `${elapsed}s`;
          }

          if (this.onComplete) {
            this.onComplete({
              success,
              returnCode: msg.return_code,
              elapsed
            });
          }
        }
      } catch (e) {
        // Not JSON, treat as raw text
        this.appendOutput(event.data + '\n');
      }
    }

    _handleClose() {
      if (!this.closed) {
        console.log('[WebSocketOutputStream] Connection closed');
        this.closed = true;
        this.ws = null;
        if (this.onClose) this.onClose();
      }
    }

    _handleWSError() {
      this.appendOutput('\n[WebSocket connection error]\n');
      this._updateStatus('Connection error', 'error');
      if (this.onError) this.onError({ detail: 'WebSocket connection error' });
    }

    _handleError(message, error) {
      console.error(`[WebSocketOutputStream] ${message}:`, error);
      this._updateStatus(message, 'error');
      if (this.onError) this.onError({ detail: message, error });
    }

    _updateStatus(text, type = 'info') {
      if (!this.statusElement) return;

      const classMap = {
        info: 'text-info',
        warning: 'text-warning',
        success: 'text-success',
        error: 'text-error'
      };

      const className = classMap[type] || 'text-base-content';
      this.statusElement.innerHTML = `<span class="${className}">${text}</span>`;
    }

    /**
     * Convert ANSI escape codes to HTML
     * @param {string} text - Text with ANSI codes
     * @returns {string} HTML string
     */
    _ansiToHtml(text) {
      // Basic ANSI color code mapping
      const ansiColorMap = {
        '0': 'reset',
        '1': 'bold',
        '30': 'black',
        '31': 'red',
        '32': 'green',
        '33': 'yellow',
        '34': 'blue',
        '35': 'magenta',
        '36': 'cyan',
        '37': 'white',
        '90': 'gray'
      };

      const colorClasses = {
        'reset': '',
        'bold': 'font-bold',
        'black': 'text-gray-900',
        'red': 'text-red-500',
        'green': 'text-green-500',
        'yellow': 'text-yellow-500',
        'blue': 'text-blue-500',
        'magenta': 'text-purple-500',
        'cyan': 'text-cyan-500',
        'white': 'text-white',
        'gray': 'text-gray-500'
      };

      // Escape HTML
      let html = text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');

      // Replace ANSI codes with spans
      html = html.replace(/\x1b\[([0-9;]+)m/g, (match, codes) => {
        const codeList = codes.split(';');
        const color = ansiColorMap[codeList[codeList.length - 1]] || 'reset';
        const className = colorClasses[color];
        
        if (!className || color === 'reset') {
          return '</span>';
        }
        return `<span class="${className}">`;
      });

      return html;
    }
  }

  // ==================== Factory Function ====================

  /**
   * Create a WebSocket output stream with simplified configuration
   * @param {object} config - Configuration object
   * @returns {WebSocketOutputStream} Stream instance
   */
  function createOutputStream(config) {
    return new WebSocketOutputStream(config);
  }

  // ==================== Export to Global Scope ====================

  global.WebSocketOutputStream = WebSocketOutputStream;
  global.createOutputStream = createOutputStream;

  console.log('[Shared] websocket_output_stream.js loaded');

})(window);
