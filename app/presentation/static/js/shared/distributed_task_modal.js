/**
 * Distributed Task Modal - Reusable component for generating distributed task scripts
 * Can be used across multiple pages (Timing QC, Post-Edit, etc.)
 * 
 * Usage:
 *   DistributedTaskModal.open({
 *     folder_run_dir: '/path/to/testbench',
 *     remote_dir: '/u/username/p4_ws/projects/...',
 *     sim_command: './runall.csh'  // optional, defaults to './runall.csh'
 *   });
 */

window.DistributedTaskModal = (function() {
  'use strict';

  let modalElement = null;
  let currentConfig = null;
  let remoteHosts = [];

  /**
   * Initialize modal HTML if not already in DOM
   */
  function initModal() {
    if (modalElement) return;

    const modalHTML = `
      <dialog id="distributedTaskModal" class="modal">
        <div class="modal-box w-11/12 max-w-7xl">
          <h3 class="font-bold text-lg mb-4">Task Redirect - Distributed Execution</h3>
          
          <!-- Remote Host Selection -->
          <div class="form-control mb-4">
            <label class="label">
              <span class="label-text font-semibold">Remote Host</span>
            </label>
            <select id="remoteHostSelect" class="select select-bordered select-sm w-full">
              <option value="">Loading...</option>
            </select>
          </div>

          <!-- Remote Directory Input -->
          <div class="form-control mb-4">
            <label class="label">
              <span class="label-text font-semibold">Remote Directory</span>
            </label>
            <input type="text" id="remoteDirInput" class="input input-sm input-bordered font-mono text-xs w-full" style="text-align: left; direction: rtl;" 
                   placeholder="/u/username/p4_ws/projects/...">
          </div>

          <!-- Sim Command Input -->
          <div class="form-control mb-4">
            <label class="label">
              <span class="label-text font-semibold">Simulation Command</span>
            </label>
            <input type="text" id="simCommandInput" class="input input-sm input-bordered font-mono text-xs w-full" 
                   placeholder="./runall.csh">
          </div>

          <!-- Status Message -->
          <div id="distributedTaskStatus" class="mb-4"></div>

          <!-- Execution Output Container (matching execution_output.html structure) -->
          <div id="distributedTaskExecution" class="hidden mt-3">
            <div class="flex flex-col gap-3">
              <!-- Execution Details -->
              <div class="p-3 bg-base-200 rounded border border-base-300">
                <div class="flex items-center justify-between mb-2">
                  <div class="text-xs font-semibold">Execution Details</div>
                  <button id="distributedTaskExecution_StopBtn" type="button" class="btn btn-xs btn-error" disabled>Stop</button>
                </div>
                <div class="space-y-1 text-[11px]">
                  <div class="flex gap-2">
                    <span class="font-semibold min-w-[100px]">Execution Dir:</span>
                    <code id="distributedTaskExecution_WorkingDir" class="text-[10px] flex-1"></code>
                  </div>
                  <div class="flex gap-2">
                    <span class="font-semibold min-w-[100px]">Command:</span>
                    <code id="distributedTaskExecution_ScriptPath" class="text-[10px] flex-1"></code>
                  </div>
                  <div class="flex gap-2">
                    <span class="font-semibold min-w-[100px]">Status:</span>
                    <span id="distributedTaskExecution_Status" class="text-[10px]"></span>
                  </div>
                  <div class="flex gap-2" id="distributedTaskExecution_ElapsedRow" style="display: none;">
                    <span class="font-semibold min-w-[100px]">Elapsed:</span>
                    <span id="distributedTaskExecution_Elapsed" class="text-[10px]"></span>
                  </div>
                </div>
              </div>
              <!-- Script Output -->
              <div class="bg-base-200 rounded border border-base-300">
                <div class="flex items-center justify-between px-2 py-1 text-xs font-semibold">
                  <span>Script Output</span>
                  <div class="flex gap-1">
                    <button id="distributedTaskExecution_ClearBtn" type="button" class="btn btn-ghost btn-xs">Clear</button>
                    <label class="flex items-center gap-1 cursor-pointer text-[10px]">
                      <input type="checkbox" id="distributedTaskExecution_Autoscroll" class="checkbox checkbox-xs" checked>
                      <span>Autoscroll</span>
                    </label>
                  </div>
                </div>
                <pre id="distributedTaskExecution_Stream" class="p-2 bg-base-300 text-[10px] overflow-auto whitespace-pre-wrap font-mono resize-y" style="min-height: 160px; height: 256px; max-height: 800px;"></pre>
              </div>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="modal-action">
            <button id="btnSendTask" class="btn btn-primary">
              <span class="loading loading-spinner loading-xs hidden"></span>
              Send Data
            </button>
            <button id="btnSimTask" class="btn btn-warning">
              <span class="loading loading-spinner loading-xs hidden"></span>
              Run Simulation
            </button>
            <button id="btnGetBackTask" class="btn btn-success">
              <span class="loading loading-spinner loading-xs hidden"></span>
              Retrieve Data
            </button>
            <button id="btnCloseModal" class="btn">Close</button>
          </div>
        </div>
        <form method="dialog" class="modal-backdrop">
          <button>close</button>
        </form>
      </dialog>
    `;

    document.body.insertAdjacentHTML('beforeend', modalHTML);
    modalElement = document.getElementById('distributedTaskModal');

    // Attach event listeners
    document.getElementById('btnSendTask').addEventListener('click', () => handleTaskAction('send'));
    document.getElementById('btnSimTask').addEventListener('click', () => handleTaskAction('sim'));
    document.getElementById('btnGetBackTask').addEventListener('click', () => handleTaskAction('get_back'));
    document.getElementById('btnCloseModal').addEventListener('click', closeModal);
  }

  /**
   * Check which script files exist and update button colors
   */
  async function updateButtonColors(folderRunDir) {
    try {
      const response = await fetch('/api/distributed-task/check-scripts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ folder_run_dir: folderRunDir })
      });

      if (!response.ok) return;

      const result = await response.json();
      
      // Modal buttons keep their original colors, don't change based on file existence
      // (User wants the table "Task Redirect" button to change color, not modal buttons)
    } catch (error) {
      console.error('[DistributedTaskModal] Error checking scripts:', error);
    }
  }

  /**
   * Load remote hosts from API
   */
  async function loadRemoteHosts() {
    try {
      const response = await fetch('/api/distributed-task/remote-hosts');
      if (!response.ok) {
        throw new Error('Failed to load remote hosts');
      }
      remoteHosts = await response.json();
      
      const select = document.getElementById('remoteHostSelect');
      select.innerHTML = '';
      
      if (remoteHosts.length === 0) {
        select.innerHTML = '<option value="">No hosts configured (add to ~/.remote_host.lst)</option>';
      } else {
        remoteHosts.forEach(host => {
          const option = document.createElement('option');
          option.value = host.connection_string;
          option.textContent = `${host.connection_string} (${host.hostname})`;
          select.appendChild(option);
        });
      }
    } catch (error) {
      console.error('[DistributedTaskModal] Error loading remote hosts:', error);
      const select = document.getElementById('remoteHostSelect');
      select.innerHTML = '<option value="">Error loading hosts</option>';
      showStatus('error', 'Failed to load remote hosts. Check ~/.remote_host.lst');
    }
  }

  /**
   * Handle task action (send/sim/get_back)
   */
  async function handleTaskAction(taskType) {
    const remoteHost = document.getElementById('remoteHostSelect').value;
    const remoteDir = document.getElementById('remoteDirInput').value.trim();
    const simCommand = document.getElementById('simCommandInput').value.trim() || './runall.csh';

    // Validate inputs
    if (!remoteHost) {
      showStatus('error', 'Please select a remote host');
      return;
    }
    if (!remoteDir) {
      showStatus('error', 'Please enter remote directory');
      return;
    }
    if (!currentConfig || !currentConfig.folder_run_dir) {
      showStatus('error', 'Configuration error: folder_run_dir not set');
      return;
    }

    const taskLabels = {
      'send': 'Send Data',
      'sim': 'Run Simulation',
      'get_back': 'Retrieve Data'
    };

    // Show loading state
    const button = document.getElementById(`btn${capitalize(taskType)}Task`);
    const spinner = button.querySelector('.loading');
    button.disabled = true;
    if (spinner) spinner.classList.remove('hidden');
    showStatus('info', `Generating script for ${taskLabels[taskType] || taskType}...`);

    try {
      const response = await fetch('/api/distributed-task/generate-script', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          task_type: taskType,
          folder_run_dir: currentConfig.folder_run_dir,
          remote_dir: remoteDir,
          remote_host: remoteHost,
          sim_command: simCommand
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to generate script');
      }

      const result = await response.json();
      const taskLabels = {
        'send': 'Send Data',
        'sim': 'Run Simulation',
        'get_back': 'Retrieve Data'
      };
      showStatus('success', `✓ ${taskLabels[taskType] || result.note}: ${result.script_path}`);
      
      // Notify to update table colors (if QCApiClient is available)
      if (window.QCApiClient && window.QCApiClient.updateTaskScriptColors) {
        const cellSelect = document.getElementById('cellSelect');
        if (cellSelect && cellSelect.value) {
          await window.QCApiClient.updateTaskScriptColors(cellSelect.value);
          // Re-render table if QCTableRenderer is available
          if (window.QCTableRenderer && window.QCTableRenderer.renderTables) {
            window.QCTableRenderer.renderTables();
          }
        }
      }
      
      // Create symlinks (TimingCloseBeta.py and bin/) in parent directory (execution dir)
      try {
        // Extract parent directory from testbench folder path
        const testbenchPath = currentConfig.folder_run_dir;
        const parentDir = testbenchPath.substring(0, testbenchPath.lastIndexOf('/'));
        
        console.log('[DistributedTaskModal] Starting symlink creation...');
        console.log('[DistributedTaskModal] testbench path:', testbenchPath);
        console.log('[DistributedTaskModal] parent dir (cell_root):', parentDir);
        
        showStatus('info', 'Creating tool symlinks...');
        const symlinkResponse = await fetch('/api/files/symlinks', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ cell_root: parentDir })
        });
        
        console.log('[DistributedTaskModal] Symlink API response status:', symlinkResponse.status);
        
        if (!symlinkResponse.ok) {
          const errorText = await symlinkResponse.text();
          console.error('[DistributedTaskModal] Symlink API error:', errorText);
          showStatus('warning', `⚠ Symlink creation warning: ${symlinkResponse.status}`);
        } else {
          const symlinkResult = await symlinkResponse.json();
          console.log('[DistributedTaskModal] Symlink result:', symlinkResult);
          if (symlinkResult.note) {
            console.log('[DistributedTaskModal] Symlink note:', symlinkResult.note);
          }
          if (symlinkResult.warnings && symlinkResult.warnings.length > 0) {
            console.warn('[DistributedTaskModal] Symlink warnings:', symlinkResult.warnings);
          }
        }
      } catch (symlinkError) {
        console.error('[DistributedTaskModal] Symlink creation exception:', symlinkError);
        console.error('[DistributedTaskModal] Error stack:', symlinkError.stack);
        showStatus('warning', '⚠ Symlink creation failed (continuing anyway)');
        // Continue anyway - symlinks might already exist
      }
      
      // Execute the generated script from parent directory (where script was created)
      // Extract parent directory from testbench folder path
      const testbenchPath = currentConfig.folder_run_dir;
      const parentDir = testbenchPath.substring(0, testbenchPath.lastIndexOf('/'));
      executeScript(result.script_path, parentDir);

    } catch (error) {
      console.error('[DistributedTaskModal] Error generating script:', error);
      showStatus('error', `✗ Error: ${error.message}`);
    } finally {
      button.disabled = false;
      if (spinner) spinner.classList.add('hidden');
    }
  }

  /**
   * Execute the generated script using ExecutionStreamFactory (same pattern as layout_form.js)
   */
  function executeScript(scriptPath, executionDir) {
    // Show execution output section
    const executionDiv = document.getElementById('distributedTaskExecution');
    if (executionDiv) executionDiv.classList.remove('hidden');

    // Check if ExecutionStreamFactory is available
    if (!window.ExecutionStreamFactory) {
      showStatus('error', 'ExecutionStreamFactory not available');
      console.error('[DistributedTaskModal] ExecutionStreamFactory not found');
      return;
    }

    showStatus('info', 'Starting execution...');

    // Create execution stream (same pattern as layout_form.js lines 334-375)
    const streamController = window.ExecutionStreamFactory.create({
      executionDir: executionDir,
      command: scriptPath,
      containerId: 'distributedTaskExecution',  // Use container ID, not output div ID
      shell: '/bin/csh',
      onComplete: (result) => {
        if (result.success) {
          showStatus('success', `✓ Execution completed successfully (exit code: ${result.returnCode})`);
        } else {
          showStatus('error', `✗ Execution failed (exit code: ${result.returnCode})`);
        }
      },
      onError: (error) => {
        showStatus('error', `✗ Execution error: ${error.detail || 'Unknown error'}`);
        console.error('[DistributedTaskModal] Execution error:', error);
      }
    });

    if (streamController) {
      streamController.connect();
    } else {
      showStatus('error', '✗ Failed to create execution stream');
      console.error('[DistributedTaskModal] streamController is null');
    }
  }

  /**
   * Show status message
   */
  function showStatus(type, message) {
    const statusDiv = document.getElementById('distributedTaskStatus');
    const classMap = {
      'info': 'alert-info',
      'success': 'alert-success',
      'error': 'alert-error'
    };
    statusDiv.innerHTML = `<div class="alert ${classMap[type] || 'alert-info'}">${message}</div>`;
  }

  /**
   * Capitalize and convert underscores to camelCase
   * 'get_back' -> 'GetBack', 'send' -> 'Send', 'sim' -> 'Sim'
   */
  function capitalize(str) {
    return str.split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join('');
  }

  /**
   * Open modal with configuration
   */
  function open(config) {
    if (!config || !config.folder_run_dir) {
      console.error('[DistributedTaskModal] Missing required config: folder_run_dir');
      alert('Configuration error: folder_run_dir is required');
      return;
    }

    initModal();
    currentConfig = config;

    // Set default values
    document.getElementById('remoteDirInput').value = config.remote_dir || '';
    document.getElementById('simCommandInput').value = config.sim_command || './runall.csh';
    document.getElementById('distributedTaskStatus').innerHTML = '';
    
    // Reset execution output section
    const executionDiv = document.getElementById('distributedTaskExecution');
    if (executionDiv) executionDiv.classList.add('hidden');
    const streamOutput = document.getElementById('distributedTaskExecution_Stream');
    if (streamOutput) streamOutput.textContent = '';

    // Load remote hosts and check existing scripts
    loadRemoteHosts();
    updateButtonColors(config.folder_run_dir);
    modalElement.showModal();
  }

  /**
   * Close modal
   */
  function closeModal() {
    if (modalElement) {
      modalElement.close();
    }
  }

  // Public API
  return {
    open: open,
    close: closeModal
  };
})();
