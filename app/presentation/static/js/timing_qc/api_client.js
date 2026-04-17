// Timing QC: API Client
// This module handles all backend API communication

(function(global){
  'use strict';

  // Verify dependencies
  if(!global.QCSharedHttp || !global.QCState){
    console.error('[Timing QC] api_client.js requires shared_http.js and state.js');
    return;
  }

  const { fetchJSON } = global.QCSharedHttp;
  const { getSelectionState, getDelays, setDelays, addTestbench, updateTestbenchStatus,
          setImportantNumbers, getStatusPoll, setStatusPoll, clearStatusPoll } = global.QCState;

  // ------------------ Cell Operations ------------------
  /**
   * Load available cells for current project/subproject
   * @returns {Promise<Array>} - Array of cell objects
   */
  async function loadCells(){
    const sel = getSelectionState();
    if(!(sel.project && sel.subproject)) return [];

    try {
      const data = await fetchJSON(`/api/qc/${sel.project}/${sel.subproject}/cells`);
      return data.cells || [];
    } catch(error){
      console.error('[Timing QC] Error loading cells:', error);
      return [];
    }
  }

  /**
   * Load default configuration for a cell
   * @param {string} cell - Cell name
   * @param {boolean} forceDefaults - Force system defaults (ignore runall.csh)
   * @returns {Promise<object>} - Configuration object
   */
  async function loadDefaults(cell, forceDefaults = false){
    const sel = getSelectionState();
    if(!cell) return null;

    try {
      const params = forceDefaults ? '&force_defaults=true' : '';
      const data = await fetchJSON(
        `/api/qc/${sel.project}/${sel.subproject}/defaults?cell=${encodeURIComponent(cell)}${params}`
      );
      return data;
    } catch(error){
      console.error('[Timing QC] Error loading defaults:', error);
      return null;
    }
  }

  // ------------------ Testbench Operations ------------------
  /**
   * Load important arc numbers for a cell
   * @param {string} cell - Cell name
   * @returns {Promise<Set>} - Set of important arc numbers
   */
  async function loadImportantNumbers(cell){
    const sel = getSelectionState();
    if(!(sel.project && sel.subproject && cell)) return new Set();

    try {
      const data = await fetchJSON(
        `/api/qc/${sel.project}/${sel.subproject}/important-arcs?cell=${encodeURIComponent(cell)}`
      );
      const numbers = new Set(data.important_numbers || []);
      setImportantNumbers(numbers);
      return numbers;
    } catch(error){
      console.error('[Timing QC] Error loading important numbers:', error);
      setImportantNumbers(new Set());
      return new Set();
    }
  }

  /**
   * Load testbenches for a cell
   * @param {string} cell - Cell name
   * @returns {Promise<object>} - {added: number, total: number}
   */
  async function loadTestbenches(cell){
    const sel = getSelectionState();
    if(!(sel.project && sel.subproject && cell)) return {added: 0, total: 0};

    try {
      // Load important numbers first
      await loadImportantNumbers(cell);

      const data = await fetchJSON(
        `/api/qc/${sel.project}/${sel.subproject}/testbenches?cell=${encodeURIComponent(cell)}`
      );

      const serverList = Array.isArray(data.testbenches) ? data.testbenches : [];
      const serverSet = new Set(serverList);

      // Prune rows that no longer exist on disk (important for Reload behavior)
      const prevRows = getDelays();
      const removedRows = prevRows.filter(r => !serverSet.has(r.testbench));
      if(removedRows.length > 0){
        const keptRows = prevRows.filter(r => serverSet.has(r.testbench));
        setDelays(keptRows);
      }

      // Add any new rows discovered by server scan
      const existing = new Set(getDelays().map(r => r.testbench));
      let added = 0;
      serverList.forEach(tb => {
        if(!existing.has(tb)){
          addTestbench({
            testbench: tb,
            pvt: '',
            status: 'Pending',
            slack: null,
            factorx: null,
            program_time: '',
            notes: '(auto)'
          });
          existing.add(tb);
          added++;
        }
      });

      return {added, removed: removedRows.length, total: serverList.length};
    } catch(error){
      console.error('[Timing QC] Error loading testbenches:', error);
      return {added: 0, total: 0};
    }
  }

  /**
   * Fetch status for a single testbench
   * @param {string} cell - Cell name
   * @param {string} testbench - Testbench name
   * @returns {Promise<object>} - Status data with PVT details
   */
  async function fetchTestbenchStatus(cell, testbench){
    const sel = getSelectionState();
    if(!(sel.project && sel.subproject && cell && testbench)) return null;

    try {
      const data = await fetchJSON(
        `/api/qc/${sel.project}/${sel.subproject}/status?cell=${encodeURIComponent(cell)}&testbench=${encodeURIComponent(testbench)}`,
        {},
        {silent: true}  // Don't show toast for status polling
      );
      
      // Update state
      updateTestbenchStatus(testbench, data.status, data.pvts);
      
      return data;
    } catch(error){
      // Silent fail for polling
      return null;
    }
  }

  /**
   * Refresh status for all testbenches
   * @param {string} cell - Cell name
   * @returns {Promise<void>}
   */
  async function refreshAllStatuses(cell){
    const testbenches = getDelays().map(r => r.testbench);
    await Promise.all(testbenches.map(tb => fetchTestbenchStatus(cell, tb)));
  }

  /**
   * Start status polling (every 5 seconds)
   * @param {string} cell - Cell name
   * @param {Function} renderCallback - Function to call after refresh
   */
  function startStatusPolling(cell, renderCallback){
    clearStatusPoll();

    const poll = async () => {
      await refreshAllStatuses(cell);
      if(renderCallback) renderCallback();

      // Continue polling if not all done
      const delays = getDelays();
      const allDone = delays.every(r => r.status === 'Passed' || r.status === 'Fail');
      if(!allDone && delays.length > 0){
        setStatusPoll(setTimeout(poll, 5000));
      }
    };

    // Start first poll
    poll();
  }

  /**
   * Stop status polling
   */
  function stopStatusPolling(){
    clearStatusPoll();
  }

  // ------------------ Script Operations ------------------
  /**
   * Generate and get script path
   * @param {object} payload - Script configuration payload
   * @returns {Promise<object>} - {script_path: '', delay: [], ...}
   */
  async function generateScript(payload){
    const sel = getSelectionState();
    
    try {
      const data = await fetchJSON(
        `/api/qc/${sel.project}/${sel.subproject}/generate`,
        {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(payload)
        }
      );
      
      // Update delay data
      if(data.delay){
        setDelays(data.delay);
      }
      
      return data;
    } catch(error){
      console.error('[Timing QC] Error generating script:', error);
      throw error;
    }
  }

  // ------------------ Task Queue Operations ------------------
  /**
   * Get existing task queue settings
   * @param {string} cell - Cell name
   * @param {string} testbench - Testbench name
   * @returns {Promise<object>} - Settings object
   */
  async function getTaskQueueSettings(cell, testbench){
    const sel = getSelectionState();
    
    try {
      const data = await fetchJSON(
        `/api/qc/${sel.project}/${sel.subproject}/cells/${cell}/taskqueue?testbench=${encodeURIComponent(testbench)}`,
        {},
        {silent: true}
      );
      return data;
    } catch(error){
      return null;
    }
  }

  /**
   * Create task queue files
   * @param {string} cell - Cell name
   * @param {string} testbench - Testbench name
   * @param {object} payload - Task queue configuration
   * @returns {Promise<object>} - Result with file paths
   */
  async function createTaskQueue(cell, testbench, payload){
    const sel = getSelectionState();
    
    try {
      const data = await fetchJSON(
        `/api/qc/${sel.project}/${sel.subproject}/cells/${cell}/taskqueue?testbench=${encodeURIComponent(testbench)}`,
        {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(payload)
        }
      );
      return data;
    } catch(error){
      console.error('[Timing QC] Error creating task queue:', error);
      throw error;
    }
  }

  // ------------------ PVT Operations ------------------
  /**
   * Get PVT list and status for testbench
   * @param {string} cell - Cell name
   * @param {string} testbench - Testbench name
   * @returns {Promise<object>} - {status: '', pvts: []}
   */
  async function getPvtList(cell, testbench){
    const sel = getSelectionState();
    
    try {
      const data = await fetchJSON(
        `/api/qc/${sel.project}/${sel.subproject}/status?cell=${encodeURIComponent(cell)}&testbench=${encodeURIComponent(testbench)}`
      );
      return data;
    } catch(error){
      console.error('[Timing QC] Error getting PVT list:', error);
      throw error;
    }
  }

  /**
   * Submit PVT jobs
   * @param {string} cell - Cell name
   * @param {object} payload - {testbench: '', pvts: [], queue_opts: '', impostor: ''}
   * @returns {Promise<object>} - Job submission results
   */
  async function submitPvtJobs(cell, payload){
    const sel = getSelectionState();
    
    try {
      const data = await fetchJSON(
        `/api/qc/${sel.project}/${sel.subproject}/cells/${cell}/run-pvts`,
        {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(payload)
        }
      );
      return data;
    } catch(error){
      console.error('[Timing QC] Error submitting PVT jobs:', error);
      throw error;
    }
  }

  // ------------------ Distributed Task Script Check ------------------
  /**
   * Check which distributed task scripts exist for a testbench
   * @param {string} testbenchPath - Full path to testbench directory
   * @returns {Promise<object>} - {send_exists, sim_exists, get_back_exists}
   */
  async function checkTaskScripts(testbenchPath){
    try {
      const data = await fetchJSON(
        '/api/distributed-task/check-scripts',
        {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ folder_run_dir: testbenchPath })
        }
      );
      return data;
    } catch(error){
      console.error('[Timing QC] Error checking task scripts:', error);
      return { send_exists: false, sim_exists: false, get_back_exists: false };
    }
  }

  /**
   * Update task script status colors for all testbenches
   * Priority: get_back (green) > sim (yellow) > send (blue)
   */
  async function updateTaskScriptColors(cell){
    const sel = getSelectionState();
    if(!(sel.project && sel.subproject && cell)) return;

    // Get base path
    let basePath = '';
    try {
      const configData = await fetchJSON('/api/config/base-path');
      basePath = configData.base_path;
    } catch(error){
      console.error('[Timing QC] Error getting base path:', error);
      return;
    }

    // Check scripts for each testbench
    const delays = getDelays();
    for(const row of delays){
      const testbenchPath = `${basePath}/${sel.project}/${sel.subproject}/design/timing/quality/4_qc/${cell}/simulations_${cell}/${row.testbench}`;
      const scriptStatus = await checkTaskScripts(testbenchPath);
      
      // Determine color based on priority: get_back > sim > send
      let colorClass = 'btn-ghost'; // default
      if(scriptStatus.send_exists) colorClass = 'btn-primary'; // blue
      if(scriptStatus.sim_exists) colorClass = 'btn-warning'; // yellow
      if(scriptStatus.get_back_exists) colorClass = 'btn-success'; // green
      
      // Store in row data
      row._taskScriptStatus = colorClass;
    }
  }

  // ------------------ Export to Global Scope ------------------
  global.QCApiClient = {
    // Cell operations
    loadCells,
    loadDefaults,
    
    // Testbench operations
    loadImportantNumbers,
    loadTestbenches,
    fetchTestbenchStatus,
    refreshAllStatuses,
    
    // Polling
    startStatusPolling,
    stopStatusPolling,
    
    // Script operations
    generateScript,
    
    // Task queue
    getTaskQueueSettings,
    createTaskQueue,
    
    // PVT operations
    getPvtList,
    submitPvtJobs,
    
    // Distributed task
    checkTaskScripts,
    updateTaskScriptColors
  };

  console.log('[Timing QC] api_client.js loaded');

})(window);
