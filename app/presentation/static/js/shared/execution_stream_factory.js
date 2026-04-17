// Execution Stream Factory - Simplified API for WebSocket Output Streaming
// Provides convenient factory functions to create execution streams with minimal configuration

(function(global) {
  'use strict';

  // Verify dependencies
  if (!global.WebSocketOutputStream) {
    console.error('[ExecutionStreamFactory] Requires websocket_output_stream.js to be loaded first');
    return;
  }

  /**
   * Create an execution stream with simplified configuration
   * 
   * MINIMAL USAGE (only required fields):
   *   ExecutionStreamFactory.create({
   *     executionDir: '/project/build',
   *     command: '/project/build/compile.sh',
   *     containerId: 'buildExecution'
   *   }).connect();
   * 
   * @param {object} config - Configuration object
   * @param {string} config.executionDir - Working directory where command executes
   * @param {string} config.command - Script path or command to execute
   * @param {string} [config.containerId] - Container ID prefix (default: 'executionOutputGroup')
   * @param {string} [config.shell] - Shell to use (default: '/bin/bash')
   * @param {Function} [config.onStart] - Optional callback when execution starts
   * @param {Function} [config.onComplete] - Optional callback when execution completes
   * @param {Function} [config.onError] - Optional callback on error
   * @param {string} [config.wsBaseUrl] - Custom WebSocket base URL (default: auto-detect)
   * 
   * @returns {object} - Object with {stream, elements, connect, stop, clear}
   */
  function createExecutionStream(config) {
    const containerId = config.containerId || 'executionOutputGroup';
    
    // Detect if using legacy IDs (for backward compatibility with QC page)
    const useLegacyIds = containerId === 'executionOutputGroup' && document.getElementById('scriptStream');
    
    // Get DOM elements - try legacy IDs first, then new format
    const elements = {
      container: document.getElementById(containerId),
      output: useLegacyIds ? document.getElementById('scriptStream') : document.getElementById(`${containerId}_Stream`),
      autoscroll: useLegacyIds ? document.getElementById('autoscrollScript') : document.getElementById(`${containerId}_Autoscroll`),
      status: useLegacyIds ? document.getElementById('infoStatus') : document.getElementById(`${containerId}_Status`),
      elapsed: useLegacyIds ? document.getElementById('infoElapsed') : document.getElementById(`${containerId}_Elapsed`),
      elapsedRow: useLegacyIds ? document.getElementById('infoElapsedRow') : document.getElementById(`${containerId}_ElapsedRow`),
      scriptPath: useLegacyIds ? document.getElementById('infoScriptPath') : document.getElementById(`${containerId}_ScriptPath`),
      workingDir: useLegacyIds ? document.getElementById('infoWorkingDir') : document.getElementById(`${containerId}_WorkingDir`),
      stopBtn: useLegacyIds ? document.getElementById('stopScriptBtn') : document.getElementById(`${containerId}_StopBtn`),
      clearBtn: useLegacyIds ? document.getElementById('clearScriptBtn') : document.getElementById(`${containerId}_ClearBtn`)
    };

    // Validate required elements
    if (!elements.output) {
      const expectedId = useLegacyIds ? 'scriptStream' : `${containerId}_Stream`;
      console.error(`[ExecutionStreamFactory] Output element not found: ${expectedId}`);
      return null;
    }

    // Build WebSocket URL
    const wsUrl = buildWebSocketUrl({
      scriptPath: config.command,
      workingDir: config.executionDir,
      shell: config.shell || '/bin/bash',
      baseUrl: config.wsBaseUrl
    });

    // Update execution info in UI
    if (elements.scriptPath) {
      elements.scriptPath.textContent = config.command || 'N/A';
    }
    if (elements.workingDir) {
      elements.workingDir.textContent = config.executionDir || 'N/A';
    }

    // Show container
    if (elements.container) {
      elements.container.classList.remove('hidden');
    }

    // Create WebSocketOutputStream instance with smart defaults
    const stream = new global.WebSocketOutputStream({
      outputElement: elements.output,
      autoScrollElement: elements.autoscroll,
      statusElement: elements.status,
      elapsedElement: elements.elapsed,
      wsUrl: wsUrl,
      
      onOpen: () => {
        console.log('[ExecutionStream] Started');
        if (elements.stopBtn) elements.stopBtn.disabled = false;
        if (elements.elapsedRow) elements.elapsedRow.style.display = 'flex';
        // Only call user callback if provided
        if (config.onStart) config.onStart();
      },
      
      onComplete: (result) => {
        console.log('[ExecutionStream] Completed', result);
        if (elements.stopBtn) elements.stopBtn.disabled = true;
        // Only call user callback if provided
        if (config.onComplete) config.onComplete(result);
      },
      
      onError: (error) => {
        console.error('[ExecutionStream] Error', error);
        if (elements.stopBtn) elements.stopBtn.disabled = true;
        // Only call user callback if provided
        if (config.onError) config.onError(error);
      },
      
      onClose: () => {
        console.log('[ExecutionStream] Connection closed');
        if (elements.stopBtn) elements.stopBtn.disabled = true;
      }
    });

    // Wire up UI controls
    if (elements.stopBtn) {
      elements.stopBtn.onclick = () => stream.stop();
    }
    
    if (elements.clearBtn) {
      elements.clearBtn.onclick = () => stream.clearOutput();
    }

    // Return stream controller with convenient methods
    return {
      // Raw stream instance (for advanced usage)
      stream: stream,
      
      // DOM elements (for custom manipulation if needed)
      elements: elements,
      
      // ==================== Core Methods ====================
      
      /**
       * Start command execution (connect WebSocket)
       * Alias: runCommand
       */
      connect: () => {
        stream.connect();
        return stream;
      },
      
      /**
       * Start command execution (same as connect)
       */
      runCommand: function() {
        return this.connect();
      },
      
      /**
       * Stop running command (sends stop signal)
       * Alias: stopCommand
       */
      stop: () => {
        stream.stop();
      },
      
      /**
       * Stop running command (same as stop)
       */
      stopCommand: function() {
        this.stop();
      },
      
      /**
       * Close WebSocket connection
       */
      close: () => {
        stream.close();
      },
      
      /**
       * Clear output display
       * Alias: clearOutput
       */
      clear: () => {
        stream.clearOutput();
      },
      
      /**
       * Clear output display (same as clear)
       */
      clearOutput: function() {
        this.clear();
      },
      
      /**
       * Update execution info in UI
       * @param {object} info - {scriptPath: '', workingDir: '', status: ''}
       */
      updateInfo: (info) => {
        if (info.scriptPath && elements.scriptPath) {
          elements.scriptPath.textContent = info.scriptPath;
        }
        if (info.workingDir && elements.workingDir) {
          elements.workingDir.textContent = info.workingDir;
        }
        if (info.status && elements.status) {
          elements.status.innerHTML = info.status;
        }
      },
      
      /**
       * Check if command is currently running
       */
      isRunning: () => {
        return stream && stream.ws && stream.ws.readyState === WebSocket.OPEN;
      },
      
      /**
       * Get elapsed time in seconds
       */
      getElapsedTime: () => {
        return stream ? stream.getElapsedTime() : 0;
      }
    };
  }

  /**
   * Build WebSocket URL for execution endpoint
   * 
   * @param {object} params
   * @param {string} params.scriptPath - Path to script
   * @param {string} params.workingDir - Working directory
   * @param {string} params.shell - Shell to use
   * @param {string} [params.baseUrl] - Custom base URL (if provided, returned as-is)
   * @returns {string} WebSocket URL
   */
  function buildWebSocketUrl(params) {
    // If custom base URL provided, use it directly (for feature-specific endpoints like QC)
    if (params.baseUrl) {
      return params.baseUrl;
    }
    
    // Otherwise, build generic endpoint URL
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const host = window.location.host;
    const baseUrl = `${protocol}://${host}/api/execute/stream`;
    
    const queryParams = new URLSearchParams({
      script_path: params.scriptPath,
      working_dir: params.workingDir,
      shell: params.shell
    });
    
    return `${baseUrl}?${queryParams.toString()}`;
  }

  /**
   * Create multiple execution streams for parallel execution
   * 
   * @param {Array} configs - Array of configuration objects
   * @returns {Array} Array of stream controllers
   */
  function createMultipleStreams(configs) {
    return configs.map(config => createExecutionStream(config));
  }

  // ==================== Export to Global Scope ====================

  global.ExecutionStreamFactory = {
    create: createExecutionStream,
    createMultiple: createMultipleStreams,
    buildWebSocketUrl: buildWebSocketUrl
  };

  console.log('[Shared] execution_stream_factory.js loaded');

})(window);
