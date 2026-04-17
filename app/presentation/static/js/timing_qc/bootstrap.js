// Timing QC: Bootstrap
// This module coordinates initialization of all Timing QC modules

(function(global){
  'use strict';

  console.log('[Timing QC] Bootstrap starting...');

  // ------------------ Module Verification ------------------
  /**
   * Verify all required modules are loaded
   * @returns {Array} - Array of missing module names
   */
  function verifyModules(){
    const requiredModules = {
      'QCSharedHttp': 'shared_http.js',
      'QCState': 'state.js',
      'QCApiClient': 'api_client.js',
      'QCTableRenderer': 'table_renderer.js',
      'QCScriptRunner': 'script_runner.js',
      'QCTaskQueue': 'task_queue.js',
      'QCPvtRunner': 'pvt_runner.js',
      'QCDatastoreHandler': 'datastore_handler.js',
      'QCEventHandlers': 'event_handlers.js'
    };

    const missing = [];
    for(const [moduleName, fileName] of Object.entries(requiredModules)){
      if(!global[moduleName]){
        missing.push(`${moduleName} (${fileName})`);
      }
    }

    return missing;
  }

  // ------------------ Initialization ------------------
  /**
   * Initialize all modules in dependency order
   */
  function initializeModules(){
    console.log('[Timing QC] Initializing modules...');

    // Verify modules
    const missing = verifyModules();
    if(missing.length > 0){
      console.error('[Timing QC] Missing modules:', missing.join(', '));
      const tbody = document.querySelector('#qcTable tbody');
      if(tbody){
        tbody.innerHTML = `<tr><td colspan='5' class='text-error text-center'>Module initialization error: Missing ${missing.join(', ')}</td></tr>`;
      }
      return false;
    }

    try {
      // Create modals
      console.log('[Timing QC] Creating modals...');
      if(global.QCTaskQueue && global.QCTaskQueue.createModal){
        global.QCTaskQueue.createModal();
      }
      if(global.QCPvtRunner && global.QCPvtRunner.createModal){
        global.QCPvtRunner.createModal();
      }

      // Initialize datastore handler
      console.log('[Timing QC] Initializing datastore handler...');
      if(global.QCDatastoreHandler && global.QCDatastoreHandler.init){
        global.QCDatastoreHandler.init();
      }

      // Initialize event handlers (this wires everything up)
      console.log('[Timing QC] Initializing event handlers...');
      if(global.QCEventHandlers && global.QCEventHandlers.init){
        global.QCEventHandlers.init();
      }

      console.log('[Timing QC] All modules initialized successfully');
      return true;
    } catch(error){
      console.error('[Timing QC] Initialization error:', error);
      const tbody = document.querySelector('#qcTable tbody');
      if(tbody){
        tbody.innerHTML = `<tr><td colspan='5' class='text-error text-center'>Initialization error: ${error.message}</td></tr>`;
      }
      return false;
    }
  }

  // ------------------ Context Application ------------------
  /**
   * Apply context when project/subproject selection is ready
   */
  function applyContext(){
    const sel = global.QCState ? global.QCState.getSelectionState() : {project: '', subproject: ''};
    
    if(sel.project && sel.subproject){
      console.log('[Timing QC] Applying context:', sel.project, '/', sel.subproject);
      
      // Load cells
      if(global.QCApiClient && global.QCApiClient.loadCells){
        const cellSelect = document.getElementById('cellSelect');
        if(cellSelect){
          cellSelect.innerHTML = '<option value="">Loading...</option>';
          
          global.QCApiClient.loadCells().then(cells => {
            if(cells.length === 0){
              cellSelect.innerHTML = '<option value="">(no cells)</option>';
              return;
            }
            
            // Store cells data globally for report button access
            global._qcCellsData = cells;
            
            cellSelect.innerHTML = '<option value="">-- choose --</option>' + 
              cells.map(c => `<option value='${c.cell}'>${c.cell}</option>`).join('');
            
            // Auto-restore last selected cell if it matches current project/subproject
            const lastSel = global.QCState.getLastSelection();
            if(lastSel.project === sel.project && lastSel.subproject === sel.subproject && lastSel.cell){
              // Check if the last cell still exists
              const cellExists = cells.some(c => c.cell === lastSel.cell);
              if(cellExists){
                cellSelect.value = lastSel.cell;
                // Trigger change event to load defaults and testbenches
                cellSelect.dispatchEvent(new Event('change'));
              }
            }
          }).catch(error => {
            console.error('[Timing QC] Error loading cells:', error);
            cellSelect.innerHTML = '<option value="">(error)</option>';
          });
        }
      }
    } else {
      console.log('[Timing QC] No context available, waiting for selection...');
    }
  }

  // ------------------ Page Load Handler ------------------
  /**
   * Handle page load and initialization
   */
  function onPageLoad(){
    console.log('[Timing QC] Page loaded, starting initialization...');

    // Initialize modules
    const success = initializeModules();
    if(!success){
      console.error('[Timing QC] Module initialization failed');
      return;
    }

    // Apply context
    if(global.AppSelection){
      // AppSelection is already available
      applyContext();
    } else {
      // Wait for AppSelection to be ready
      console.log('[Timing QC] Waiting for AppSelection...');
      global.addEventListener('app-selection-ready', () => {
        console.log('[Timing QC] AppSelection ready, applying context');
        applyContext();
      }, {once: true});
    }
  }

  // ------------------ Auto-Execute on DOM Ready ------------------
  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', onPageLoad);
  } else {
    // DOM already loaded
    onPageLoad();
  }

  console.log('[Timing QC] bootstrap.js loaded');

})(window);
