// Phase 7: Bootstrap module for Timing SAF page
// Coordinates initialization of all SAF modules in correct dependency order
// This file is the single entry point for the timing_saf.html page

(function(global){
  'use strict';

  /**
   * Initialize all Timing SAF modules in dependency order.
   * Dependencies:
   *   1. SAFSharedHttp (utilities) - must be loaded first
   *   2. PvtStatus (rendering logic) - needed by cells_view
   *   3. TimingSafCells (listing/filtering) - core data
   *   4. SAFPostEditQA (iframe helpers)
   *   5. SAFJobModals (job execution)
   *   6. SAFNetlistSync (netlist operations)
   *   7. SAFNtSettings (NT cell dialogs)
   */
  function initializeModules(){
    console.log('[SAF Bootstrap] Initializing modules...');

    // Verify all required modules are loaded
    const requiredModules = {
      'SAFSharedHttp': 'shared_http.js',
      'PvtStatus': 'pvt_status.js',
      'TimingSafCells': 'cells_view.js',
      'SAFPostEditQA': 'postedit_qa.js',
      'SAFJobModals': 'job_modals.js',
      'SAFNetlistSync': 'netlist_sync.js',
      'SAFNtSettings': 'nt_settings.js',
      'BriefSumModal': 'brief_sum_modal.js'
    };

    const missing = [];
    for(const [moduleName, fileName] of Object.entries(requiredModules)){
      if(!global[moduleName]){
        missing.push(`${moduleName} (${fileName})`);
      }
    }

    if(missing.length > 0){
      console.error('[SAF Bootstrap] Missing modules:', missing.join(', '));
      const tbody = document.querySelector('#cellsTable tbody');
      if(tbody){
        tbody.innerHTML = `<tr><td colspan='8' class='text-error'>Module initialization error: Missing ${missing.join(', ')}</td></tr>`;
      }
      return;
    }

    // Initialize modules in dependency order
    try {
      // 1. Cells view (core listing and filtering)
      if(global.TimingSafCells && global.TimingSafCells.init){
        console.log('[SAF Bootstrap] Initializing TimingSafCells...');
        global.TimingSafCells.init();
      }

      // 2. Post-Edit / Timing QA iframe handlers
      if(global.SAFPostEditQA && global.SAFPostEditQA.init){
        console.log('[SAF Bootstrap] Initializing SAFPostEditQA...');
        global.SAFPostEditQA.init();
      }

      // 3. Job modals (settings + execution)
      if(global.SAFJobModals && global.SAFJobModals.init){
        console.log('[SAF Bootstrap] Initializing SAFJobModals...');
        global.SAFJobModals.init();
      }

      // 4. Netlist sync handlers
      if(global.SAFNetlistSync && global.SAFNetlistSync.init){
        console.log('[SAF Bootstrap] Initializing SAFNetlistSync...');
        global.SAFNetlistSync.init();
      }

      // 5. NT settings (depends on job modals for event communication)
      if(global.SAFNtSettings && global.SAFNtSettings.init){
        console.log('[SAF Bootstrap] Initializing SAFNtSettings...');
        global.SAFNtSettings.init();
      }

      // 6. Brief Sum modal
      if(global.BriefSumModal && global.BriefSumModal.init){
        console.log('[SAF Bootstrap] Initializing BriefSumModal...');
        global.BriefSumModal.init();
      }

      console.log('[SAF Bootstrap] All modules initialized successfully');
    } catch(err){
      console.error('[SAF Bootstrap] Initialization error:', err);
      const tbody = document.querySelector('#cellsTable tbody');
      if(tbody){
        tbody.innerHTML = `<tr><td colspan='8' class='text-error'>Initialization error: ${err.message}</td></tr>`;
      }
    }
  }

  /**
   * Wire minimal page-level event handlers that aren't owned by any specific module.
   * Most handlers are now delegated within modules; this only handles truly global events.
   */
  function wireGlobalHandlers(){
    // Open Explorer button (requires selected cell)
    const openExplorerBtn = document.getElementById('openExplorerBtn');
    if(openExplorerBtn){
      openExplorerBtn.addEventListener('click', () => {
        const selectedCellName = document.getElementById('selectedCellName');
        if(!selectedCellName || !selectedCellName.textContent){
          alert('Please select a cell first');
          return;
        }
        
        // Parse cell name and type from indicator (format: "cellname (SIS)" or "cellname (NT)")
        const match = selectedCellName.textContent.match(/^(.+?)\s+\((\w+)\)$/);
        if(!match){
          alert('Could not parse selected cell');
          return;
        }
        
        const cell = match[1];
        const typeStr = match[2].toLowerCase();
        
        const sel = global.SAFSharedHttp ? global.SAFSharedHttp.getSelection() : (global.AppSelection ? global.AppSelection.get() : {project:'', subproject:''});
        if(sel.project && sel.subproject && cell){
          const typeFolder = typeStr || 'sis';
          const relativePath = `${typeFolder}/${cell}`;
          const url = `/explorer?project=${encodeURIComponent(sel.project)}&subproject=${encodeURIComponent(sel.subproject)}&path=${encodeURIComponent(relativePath)}`;
          window.open(url, '_blank');
        }
      });
    }

    // Clear script output button
    const clearScriptBtn = document.getElementById('clearScriptBtn');
    if(clearScriptBtn){
      clearScriptBtn.addEventListener('click', () => {
        const scriptStream = document.getElementById('scriptStream');
        if(scriptStream) scriptStream.textContent = '';
      });
    }
  }

  /**
   * Setup row click handler for cell selection and action button delegation.
   * This handler is shared across all action types.
   */
  function setupCellRowHandlers(){
    const tbody = document.querySelector('#cellsTable tbody');
    if(!tbody) return;

    let selectedCell = null;
    let selectedType = null;

    tbody.addEventListener('click', (e) => {
      // Check for action buttons (handled by their respective modules)
      const runBtn = e.target.closest('.run-job-btn');
      if(runBtn){
        e.stopPropagation();
        const cell = runBtn.getAttribute('data-cell');
        const cellType = runBtn.getAttribute('data-type') || 'sis';
        global.SAFJobModals && global.SAFJobModals.onRunButton(cell, cellType, runBtn);
        return;
      }

      const peBtn = e.target.closest('.postedit-settings-btn');
      if(peBtn){
        e.stopPropagation();
        const cell = peBtn.getAttribute('data-cell');
        global.SAFPostEditQA && global.SAFPostEditQA.openPostEdit(cell);
        return;
      }

      const qaBtn = e.target.closest('.timingqa-settings-btn');
      if(qaBtn){
        e.stopPropagation();
        const cell = qaBtn.getAttribute('data-cell');
        global.SAFPostEditQA && global.SAFPostEditQA.openTimingQA(cell);
        return;
      }

      // Netlist sync handled by SAFNetlistSync module's delegated handler
      // Row selection
      const row = e.target.closest('tr.cell-row');
      if(!row) return;

      const cell = row.getAttribute('data-cell');
      const type = row.getAttribute('data-type');
      if(!cell) return;

      // Update selection state
      document.querySelectorAll('tr.cell-row').forEach(r => r.classList.remove('active'));
      row.classList.add('active');
      selectedCell = cell;
      selectedType = type || 'sis';

      // Update UI indicators
      const openExplorerBtn = document.getElementById('openExplorerBtn');
      const selectedCellIndicator = document.getElementById('selectedCellIndicator');
      const selectedCellName = document.getElementById('selectedCellName');

      if(openExplorerBtn) openExplorerBtn.disabled = false;
      if(selectedCellIndicator) selectedCellIndicator.classList.remove('hidden');
      if(selectedCellName) selectedCellName.textContent = `${cell} (${(type||'sis').toUpperCase()})`;

      // Trigger lib count checks
      global.SAFPostEditQA && global.SAFPostEditQA.checkPosteditLibCount(cell);
      global.SAFPostEditQA && global.SAFPostEditQA.checkPostQALibCount(cell);
    });
  }

  /**
   * Main bootstrap entry point.
   * Called when DOM is ready.
   */
  function init(){
    console.log('[SAF Bootstrap] Starting initialization...');
    
    // Wait for DOM to be fully loaded
    if(document.readyState === 'loading'){
      document.addEventListener('DOMContentLoaded', () => {
        initializeModules();
        wireGlobalHandlers();
        setupCellRowHandlers();
      });
    } else {
      initializeModules();
      wireGlobalHandlers();
      setupCellRowHandlers();
    }
  }

  // Export bootstrap API
  global.SAFBootstrap = { init };

  // Auto-initialize
  init();

})(window);
