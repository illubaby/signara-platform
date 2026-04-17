// Timing QC: Script Runner
// This module handles script execution using ExecutionStreamFactory

(function(global){
  'use strict';

  // Verify dependencies
  if(!global.QCSharedHttp || !global.QCState || !global.QCApiClient || !global.ExecutionStreamFactory){
    console.error('[Timing QC] script_runner.js requires shared_http.js, state.js, api_client.js, and execution_stream_factory.js');
    return;
  }

  const { showToast } = global.QCSharedHttp;
  const { getSelectionState, getRunningWS, setRunningWS, setDelays, setSelectedIndex } = global.QCState;
  const { generateScript } = global.QCApiClient;

  // DOM elements
  let runScriptBtn, stopScriptBtn, statusNote, executionOutputGroup;
  
  // Execution stream instance (using factory)
  let currentStream = null;

  /**
   * Initialize DOM element references
   */
  function initElements(){
    runScriptBtn = document.getElementById('runScriptBtn');
    stopScriptBtn = document.getElementById('stopScriptBtn');
    statusNote = document.getElementById('statusNote');
    executionOutputGroup = document.getElementById('executionOutputGroup');
  }

  // ------------------ Script Execution (using ExecutionStreamFactory) ------------------
  /**
   * Create and start execution stream
   * @param {string} cell - Cell name
   * @param {string} scriptPath - Path to the generated script
   * @param {string} workingDir - Working directory
   * @param {Function} onComplete - Callback object {startPolling, refreshStatuses}
   */
  function startExecution(cell, scriptPath, workingDir, onComplete){
    const sel = getSelectionState();
    
    // Close any existing stream
    if(currentStream && currentStream.close){
      currentStream.close();
    }
    
    // Build custom WebSocket URL for QC endpoint
    const protocol = location.protocol === 'https:' ? 'wss' : 'ws';
    const wsUrl = `${protocol}://${location.host}/api/qc/${sel.project}/${sel.subproject}/run-script/ws?cell=${encodeURIComponent(cell)}`;
    
    // Create execution stream using factory
    currentStream = global.ExecutionStreamFactory.create({
      executionDir: workingDir,
      command: scriptPath,
      shell: '/bin/csh',
      containerId: 'executionOutputGroup', // Uses legacy IDs for backward compatibility
      wsBaseUrl: wsUrl, // Custom QC endpoint instead of generic
      
      onStart: () => {
        console.log('[QC] Script execution started');
        if(stopScriptBtn) stopScriptBtn.disabled = false;
        
        // Start status polling
        if(onComplete && onComplete.startPolling){
          onComplete.startPolling();
        }
      },
      
      onComplete: (result) => {
        console.log('[QC] Script execution completed', result);
        
        // Refresh statuses
        if(onComplete && onComplete.refreshStatuses){
          onComplete.refreshStatuses();
        }
        
        // Update button states
        if(runScriptBtn) runScriptBtn.disabled = false;
        if(stopScriptBtn) stopScriptBtn.disabled = true;
        setRunningWS(null);
        currentStream = null;
      },
      
      onError: (error) => {
        console.error('[QC] Script execution error', error);
        if(runScriptBtn) runScriptBtn.disabled = false;
        if(stopScriptBtn) stopScriptBtn.disabled = true;
        setRunningWS(null);
        currentStream = null;
      }
    });
    
    // Show execution output container
    if(executionOutputGroup) {
      executionOutputGroup.classList.remove('hidden');
    }
    
    // Store reference for state management
    setRunningWS(currentStream.stream);
    
    // Start execution
    currentStream.runCommand();
    
    return currentStream;
  }

  // ------------------ Script Execution ------------------
  /**
   * Run script with given payload
   * @param {string} cell - Cell name
   * @param {object} payload - Script configuration
   * @param {Function} onComplete - Callback object {startPolling, refreshStatuses}
   */
  async function runScript(cell, payload, onComplete){
    const sel = getSelectionState();
    
    if(!cell){
      showToast('Please select a cell first', {type: 'warning'});
      return;
    }
    
    if(!(sel.project && sel.subproject)){
      showToast('Select project first', {type: 'warning'});
      return;
    }
    
    // Disable buttons
    if(statusNote) statusNote.innerHTML = '<span class="loading loading-spinner loading-xs"></span> Generating script...';
    if(runScriptBtn) runScriptBtn.disabled = true;
    if(stopScriptBtn) stopScriptBtn.disabled = true;
    
    try {
      // Generate script
      const res = await generateScript(payload);
      setDelays(res.delay);
      setSelectedIndex(null);
      
      // Clear previous output
      if(currentStream) currentStream.clearOutput();
      
      // Update execution info
      if(res.script_path){
        const lastSlash = Math.max(res.script_path.lastIndexOf('/'), res.script_path.lastIndexOf('\\'));
        const workingDir = lastSlash > 0 ? res.script_path.substring(0, lastSlash) : '.';
        
        if(statusNote) statusNote.innerHTML = `<span class='text-success'>Script generated successfully</span>`;
      } else {
        if(statusNote) statusNote.textContent = 'Script generated, launching...';
      }
      
      // Render tables if available
      if(global.QCTableRenderer && global.QCTableRenderer.renderTables){
        global.QCTableRenderer.renderTables();
      }
      
      // Start execution
      const lastSlash = Math.max(res.script_path.lastIndexOf('/'), res.script_path.lastIndexOf('\\'));
      const workingDir = lastSlash > 0 ? res.script_path.substring(0, lastSlash) : '.';
      startExecution(cell, res.script_path, workingDir, onComplete);
      
    } catch(error){
      if(statusNote) statusNote.innerHTML = `<span class='text-error text-xs'>Error: ${error.message}</span>`;
      if(runScriptBtn) runScriptBtn.disabled = false;
      if(stopScriptBtn) stopScriptBtn.disabled = true;
      setRunningWS(null);
      currentStream = null;
    }
  }

  /**
   * Stop running script
   */
  function stopScript(){
    if(currentStream) {
      currentStream.stopCommand();
      currentStream.close();
      currentStream = null;
      setRunningWS(null);
    }
  }

  // ------------------ Export to Global Scope ------------------
  global.QCScriptRunner = {
    initElements,
    runScript,
    stopScript
  };

  console.log('[Timing QC] script_runner.js loaded - Using ExecutionStreamFactory');

})(window);
