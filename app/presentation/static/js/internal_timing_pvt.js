// Internal Timing PVT Selection Module
// Loads PVTs from pvt_corners.lst when cell is selected
// Injects selected PVTs into the sim field in the form

(function() {
  'use strict';

  let currentCell = null;
  let availablePvts = [];

  async function fetchJSON(url) {
    try {
      const resp = await fetch(url);
      if (!resp.ok) return null;
      return await resp.json();
    } catch { return null; }
  }

  function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  /**
   * Create and inject PVT selection panel into the form (above Run button)
   */
  function createPvtPanel() {
    const form = document.querySelector('form[data-page-id]');
    if (!form) return;
    
    // Prefer to place BELOW the Block Path field, ABOVE phase buttons
    const blockPathInput = document.getElementById('block_path') || document.querySelector('select[name="block_path"]');
    let blockPathGroup = null;
    if (blockPathInput) {
      // Field is inside a div.mb-4; place panel right after that container
      blockPathGroup = blockPathInput.closest('.mb-4');
    }
    const phaseContainer = document.getElementById('intSimBtn') ? document.getElementById('intSimBtn').parentElement : null;
    const execContainer = document.getElementById('layoutFormExecution');
    const insertContainer = blockPathGroup || phaseContainer || (execContainer ? execContainer.parentElement : null);
    if (!insertContainer) return;

    // Create the PVT panel
    const panel = document.createElement('div');
    panel.id = 'intPvtSelectionPanel';
    panel.className = 'mt-4 mb-4 border rounded-lg p-4 bg-base-200';
    panel.style.display = 'none';
    panel.innerHTML = `
      <div class="flex items-center justify-between mb-3">
        <h4 class="font-semibold text-sm">Select PVTs to Simulate</h4>
        <div class="flex gap-2">
          <button type="button" id="intPvtCheckAllBtn" class="btn btn-xs btn-outline">Check All</button>
          <button type="button" id="intPvtUncheckAllBtn" class="btn btn-xs btn-outline">Uncheck All</button>
        </div>
      </div>
      <div id="intPvtCheckboxContainer" class="border rounded p-3 bg-base-100 max-h-64 overflow-y-auto grid grid-cols-3 gap-2 text-xs">
        <div class="col-span-3 text-center py-2 opacity-70">
          <span class="loading loading-spinner loading-xs"></span> Loading PVTs...
        </div>
      </div>
      <div class="text-[10px] opacity-70 mt-2">
        Selected PVTs will be added to the script as -sim "pvt1 pvt2 ..."
      </div>
    `;

    // Insert panel AFTER Block Path group if available; otherwise before execution block
    if (blockPathGroup && blockPathGroup.parentNode) {
      blockPathGroup.parentNode.insertBefore(panel, blockPathGroup.nextSibling);
    } else if (phaseContainer) {
      // Place above buttons by inserting before the phase container
      phaseContainer.parentNode.insertBefore(panel, phaseContainer);
    } else if (execContainer) {
      execContainer.parentNode.insertBefore(panel, execContainer);
    }
    
    console.log('[INT PVT] PVT panel created and inserted above Run button');
  }

  /**
   * Load PVTs for the selected cell from pvt_corners.lst
   */
  async function loadPvtsForCell(cellName) {
    const selection = window.AppSelection ? window.AppSelection.get() : { project: '', subproject: '' };
    const { project, subproject } = selection;
    
    if (!project || !subproject || !cellName) {
      hidePvtPanel();
      return;
    }

    currentCell = cellName;
    const panel = document.getElementById('intPvtSelectionPanel');
    const container = document.getElementById('intPvtCheckboxContainer');
    
    if (!panel || !container) {
      console.warn('[INT PVT] Panel or container not found');
      return;
    }

    // Show panel and loading state
    panel.style.display = 'block';
    container.innerHTML = '<div class="col-span-3 text-center py-2 opacity-70"><span class="loading loading-spinner loading-xs"></span> Loading PVTs...</div>';

    // Cell name already has _int suffix, use it directly for the API call
    const cellWithSuffix = cellName.endsWith('_int') ? cellName : `${cellName}_int`;
    
    console.log('[INT PVT] Loading PVTs for cell:', cellWithSuffix);
    
    try {
      // Fetch PVT list from pvt_corners.lst (using cell WITH _int suffix)
      const data = await fetchJSON(`/api/saf/${project}/${subproject}/cells/${cellWithSuffix}/nt-pvts`);
      const pvts = data && data.pvts ? data.pvts : [];
      availablePvts = pvts;

      console.log('[INT PVT] Loaded PVTs:', pvts);

      if (!pvts.length) {
        container.innerHTML = '<div class="col-span-3 text-center py-2 opacity-70">No PVTs found (pvt_corners.lst missing)</div>';
        // CRITICAL: Clear the sim field to avoid using cached values from previous runs
        const simField = document.querySelector('input[name="sim"]');
        if (simField) {
          simField.value = '';
          console.log('[INT PVT] Cleared sim field (no pvt_corners.lst file)');
        }
        return;
      }

      // Fetch PVT statuses (using cell without _int suffix for the status API)
      const cellBase = cellName.endsWith('_int') ? cellName.slice(0, -4) : cellName;
      let pvtStatuses = {};
      try {
        const statusData = await fetchJSON(`/api/cell/${project}/${subproject}/int/${cellBase}/pvt-status`);
        if (statusData && statusData.summary) {
          // Convert summary to per-PVT statuses (simplified - all idle for now)
          pvts.forEach(pvt => { pvtStatuses[pvt] = 'idle'; });
        }
      } catch (err) {
        console.warn('[INT PVT] Failed to load PVT statuses:', err);
      }

      // Render checkboxes with status indicators
      container.innerHTML = pvts.map(pvt => {
        const status = pvtStatuses[pvt] || 'idle';
        let icon = '', cls = '', checked = false;

        if (status === 'success') {
          icon = '✓'; cls = 'text-success';
        } else if (status === 'fail') {
          icon = '✗'; cls = 'text-error'; checked = true;
        } else if (status === 'in_progress') {
          icon = '⟳'; cls = 'text-warning'; checked = true;
        } else {
          icon = '○'; cls = 'opacity-60'; checked = true;
        }

        return `<label class='flex items-start gap-1 cursor-pointer hover:bg-base-200 p-1 rounded'>
          <input type='checkbox' value='${escapeHtml(pvt)}' class='checkbox checkbox-xs int-pvt-checkbox' ${checked ? 'checked' : ''} onchange='window.updateSimField()'>
          <span class='leading-tight break-all flex-1 text-[11px]' title='${escapeHtml(pvt)}'>${escapeHtml(pvt)}</span>
          <span class='${cls} font-semibold text-[10px]' title='Status: ${status}'>${icon}</span>
        </label>`;
      }).join('');

      // Update the sim field immediately
      updateSimField();

    } catch (err) {
      console.error('[INT PVT] Error loading PVTs:', err);
      container.innerHTML = `<div class='col-span-3 text-center py-2 text-error text-xs'>Error: ${escapeHtml(err.message)}</div>`;
    }
  }

  function hidePvtPanel() {
    const panel = document.getElementById('intPvtSelectionPanel');
    if (panel) panel.style.display = 'none';
    currentCell = null;
    availablePvts = [];
    updateSimField(); // Clear sim field
  }

  /**
   * Get selected PVTs as space-separated string wrapped in quotes
   * Returns empty string if no PVTs selected (will exclude --sim from command)
   */
  function getSelectedPvtsString() {
    const checkboxes = document.querySelectorAll('.int-pvt-checkbox:checked');
    const selected = Array.from(checkboxes).map(cb => cb.value);
    // Join with space and wrap in quotes for -sim option
    // Return empty string if nothing selected - optional field will be excluded
    return selected.length > 0 ? `"${selected.join(' ')}"` : '';
  }

  /**
   * Update the hidden sim field with selected PVTs
   * If no PVTs selected, sets field to empty string (will be excluded from command)
   */
  function updateSimField() {
    const simInput = document.querySelector('input[name="sim"]');
    if (simInput) {
      const selectedPvts = getSelectedPvtsString();
      simInput.value = selectedPvts;
      console.log('[INT PVT] Updated sim field:', selectedPvts || '(empty - will exclude --sim option)');
    }
  }

  // Expose updateSimField globally for checkbox onchange
  window.updateSimField = updateSimField;
  // Expose getter for latest selected PVTs to other modules (internal_timing.js)
  window.getSelectedPvtsString = getSelectedPvtsString;

  /**
   * Setup event listeners
   */
  function setup() {
    // Create the PVT panel inside the form
    createPvtPanel();

    // Watch for changes to block_path select
    const blockPathSelect = document.getElementById('block_path') || document.querySelector('select[name="block_path"]');
    if (blockPathSelect) {
      blockPathSelect.addEventListener('change', function() {
        const cellName = this.value;
        console.log('[INT PVT] Block path changed:', cellName);
        if (cellName) {
          loadPvtsForCell(cellName);
        } else {
          hidePvtPanel();
        }
      });

      // Load PVTs for initially selected cell - use longer delay and check multiple times
      const loadInitialPvts = () => {
        const currentValue = blockPathSelect.value;
        if (currentValue && currentValue !== '' && currentValue !== 'dummy') {
          console.log('[INT PVT] Loading PVTs for initial cell:', currentValue);
          loadPvtsForCell(currentValue);
        } else {
          console.log('[INT PVT] No initial cell selected yet, value:', currentValue);
        }
      };

      // Try multiple times with increasing delays to catch when the select is populated
      setTimeout(loadInitialPvts, 300);
      setTimeout(loadInitialPvts, 600);
      setTimeout(loadInitialPvts, 1000);

      // Also listen for any programmatic value changes
      const observer = new MutationObserver(() => {
        if (blockPathSelect.value && blockPathSelect.value !== 'dummy' && blockPathSelect.value !== currentCell) {
          loadPvtsForCell(blockPathSelect.value);
        }
      });
      observer.observe(blockPathSelect, { attributes: true, childList: true, subtree: true });
    }

    // Check All / Uncheck All buttons
    document.addEventListener('click', function(e) {
      if (e.target.id === 'intPvtCheckAllBtn') {
        document.querySelectorAll('.int-pvt-checkbox').forEach(cb => cb.checked = true);
        updateSimField();
      } else if (e.target.id === 'intPvtUncheckAllBtn') {
        document.querySelectorAll('.int-pvt-checkbox').forEach(cb => cb.checked = false);
        updateSimField();
      }
    });
  }

  // Initialize on DOMContentLoaded
  window.addEventListener('DOMContentLoaded', function() {
    // Delay to allow layout_form and internal_timing.js to initialize first
    setTimeout(setup, 300);
  });

})();
