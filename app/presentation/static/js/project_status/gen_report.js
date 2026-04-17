// Project Status: Gen Report Module
// Handles FTR.py execution with WebSocket streaming in modal

(function(global) {
  'use strict';

  /**
   * Get selected project information from storage
   * @returns {{project: string, subproject: string}}
   */
  function getSelectedProjectInfo() {
    try {
      const project = localStorage.getItem('timing_selected_project') || 
                     sessionStorage.getItem('timing_selected_project') || '';
      const subproject = localStorage.getItem('timing_selected_subproject') || 
                        sessionStorage.getItem('timing_selected_subproject') || '';
      return { project, subproject };
    } catch (_) {
      return { project: '', subproject: '' };
    }
  }

  /**
   * Handle Gen Report button click - Execute FTR.py command with WebSocket streaming
   */
  async function handleGenReport() {
    console.log('[GenReport] Button clicked');
    
    const { project, subproject } = getSelectedProjectInfo();
    console.log('[GenReport] Project:', project);
    console.log('[GenReport] Subproject:', subproject);
    
    if (!project || !subproject) {
      console.warn('[GenReport] Missing project or subproject');
      alert('Please select a project and subproject first');
      return;
    }
    
    const button = document.getElementById('genReportButton');
    const modal = document.getElementById('genReportModal');
    
    if (!modal) {
      console.error('[GenReport] Modal not found');
      alert('Gen Report modal not available');
      return;
    }
    
    // Get working directory from config
    const workingDir = global.projectConfig?.project_root || global.projectConfig?.server_cwd || '';
    
    if (!workingDir) {
      console.error('[GenReport] No working directory available in config');
      alert('Unable to determine working directory. Please refresh the page.');
      return;
    }
    
    // Open modal
    modal.showModal();
    
    try {
      // Disable button during execution
      button.disabled = true;
      button.innerHTML = '<span class="loading loading-spinner loading-xs"></span> Running...';
      console.log('[GenReport] Starting execution with WebSocket streaming');
      
      // Build commands (run both TimingCloseBeta.py -update and FTR.py)
      const commands = [
        'TimingCloseBeta.py -update',
        `./bin/python/FTR.py -project ${project}/${subproject}`
      ];
      const fullCommand = commands.join(' && ');
      
      // Create WebSocket execution stream using ExecutionStreamFactory
      if (!global.ExecutionStreamFactory) {
        throw new Error('ExecutionStreamFactory not available. Please refresh the page.');
      }
      
      // Build WebSocket URL for command execution
      const protocol = location.protocol === 'https:' ? 'wss' : 'ws';
      const encodedCommand = encodeURIComponent(fullCommand);
      const encodedWorkingDir = encodeURIComponent(workingDir);
      const wsUrl = `${protocol}://${location.host}/api/execute/command?command=${encodedCommand}&working_dir=${encodedWorkingDir}`;
      
      console.log('[GenReport] WebSocket URL:', wsUrl);
      
      // Create execution stream
      const streamController = global.ExecutionStreamFactory.create({
        executionDir: workingDir,
        command: fullCommand,
        containerId: 'genReportExecution',
        shell: '/bin/bash',
        wsBaseUrl: wsUrl,
        
        onStart: () => {
          console.log('[GenReport] Execution started');
        },
        
        onComplete: (result) => {
          console.log('[GenReport] Execution completed', result);
          button.disabled = false;
          button.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M6 2a2 2 0 00-2 2v12a2 2 0 002 2h8a2 2 0 002-2V7.414A2 2 0 0015.414 6L12 2.586A2 2 0 0010.586 2H6zm5 6a1 1 0 10-2 0v3.586l-1.293-1.293a1 1 0 10-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 11.586V8z" clip-rule="evenodd" />
            </svg> Gen Report`;
        },
        
        onError: (error) => {
          console.error('[GenReport] Execution error', error);
          button.disabled = false;
          button.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M6 2a2 2 0 00-2 2v12a2 2 0 002 2h8a2 2 0 002-2V7.414A2 2 0 0015.414 6L12 2.586A2 2 0 0010.586 2H6zm5 6a1 1 0 10-2 0v3.586l-1.293-1.293a1 1 0 10-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 11.586V8z" clip-rule="evenodd" />
            </svg> Gen Report`;
        }
      });
      
      // Start execution
      streamController.runCommand();
      
    } catch (error) {
      console.error('[GenReport] Error:', error);
      alert(`Failed to execute Gen Report: ${error.message}`);
      button.disabled = false;
      button.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M6 2a2 2 0 00-2 2v12a2 2 0 002 2h8a2 2 0 002-2V7.414A2 2 0 0015.414 6L12 2.586A2 2 0 0010.586 2H6zm5 6a1 1 0 10-2 0v3.586l-1.293-1.293a1 1 0 10-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 11.586V8z" clip-rule="evenodd" />
        </svg> Gen Report`;
    }
  }

  /**
   * Initialize Gen Report module
   */
  function init() {
    const button = document.getElementById('genReportButton');
    
    if (!button) {
      console.warn('[GenReport] Gen Report button not found');
      return;
    }
    
    console.log('[GenReport] Attaching event listener to Gen Report button');
    button.addEventListener('click', handleGenReport);
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})(window);
