// Timing QC: Equalizer Tab Handler
// This module handles loading, displaying, and editing EqualizeMap.csv

(function(global){
  'use strict';

  // Verify dependencies
  if(!global.QCSharedHttp || !global.QCState){
    console.error('[Timing QC] equalizer.js requires shared_http.js and state.js');
    return;
  }

  const { fetchJSON, escapeHTML } = global.QCSharedHttp;
  const { getSelectionState, getLoadedCell } = global.QCState;

  // State
  let equalizerData = [];
  let isDirty = false;
  let selectedRowIndex = null;

  // ------------------ API Functions ------------------
  /**
   * Load EqualizeMap.csv data from backend
   */
  async function loadEqualizerData(){
    const sel = getSelectionState();
    // Get cell from dropdown or loaded cell state
    const cellSelect = document.getElementById('cellSelect');
    const cell = cellSelect?.value || getLoadedCell();
    
    if(!(sel.project && sel.subproject && cell)){
      console.log('[Equalizer] Missing project/subproject/cell', {project: sel.project, subproject: sel.subproject, cell: cell});
      updateStatus('Select a cell to load EqualizeMap.csv');
      return;
    }

    updateStatus('Loading...');
    
    try {
      const url = `/api/qc/${sel.project}/${sel.subproject}/equalizer?cell=${encodeURIComponent(cell)}`;
      const data = await fetchJSON(url);
      
      equalizerData = data.rows || [];
      isDirty = false;
      selectedRowIndex = null;
      
      renderEqualizerTable();
      updateSaveButton();
      
      if(data.exists){
        updateStatus(`Loaded ${equalizerData.length} rows from EqualizeMap.csv`);
      } else {
        updateStatus('EqualizeMap.csv not found - file will be created on first save');
      }
    } catch(error){
      console.error('[Equalizer] Load error:', error);
      updateStatus('Error loading EqualizeMap.csv');
      equalizerData = [];
      selectedRowIndex = null;
      renderEqualizerTable();
    }
  }

  /**
   * Save EqualizeMap.csv data to backend
   */
  async function saveEqualizerData(){
    const sel = getSelectionState();
    const cellSelect = document.getElementById('cellSelect');
    const cell = cellSelect?.value || getLoadedCell();
    
    if(!(sel.project && sel.subproject && cell)){
      alert('Missing project/subproject/cell selection');
      return;
    }

    updateStatus('Saving...');
    
    try {
      const url = `/api/qc/${sel.project}/${sel.subproject}/equalizer?cell=${encodeURIComponent(cell)}`;
      const response = await fetch(url, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rows: equalizerData })
      });

      if(!response.ok){
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || `HTTP ${response.status}`);
      }

      const data = await response.json();
      isDirty = false;
      updateSaveButton();
      updateStatus(`Saved ${data.rows.length} rows to EqualizeMap.csv`);
    } catch(error){
      console.error('[Equalizer] Save error:', error);
      alert('Error saving: ' + error.message);
      updateStatus('Error saving file');
    }
  }

  /**
   * Run 3.RunallEqual.csh in the Equalizer directory
   */
  async function runEqualizer(){
    const sel = getSelectionState();
    const cellSelect = document.getElementById('cellSelect');
    const cell = cellSelect?.value || getLoadedCell();
    
    if(!(sel.project && sel.subproject && cell)){
      alert('Please select project, subproject, and cell first');
      return;
    }

    try {
      // Fetch base path
      const res = await fetch('/api/config/base-path');
      if(!res.ok) throw new Error('Failed to fetch base path');
      const { base_path } = await res.json();
      
      // Build the path to Equalizer directory
      const equalizerDir = `${base_path}/${sel.project}/${sel.subproject}/design/timing/quality/4_qc/${cell}/Equalizer`;
      
      // Build command: cd to directory and run script
      const cmd = `cd ${equalizerDir} && ./3.RunallEqual.csh\n`;
      
      // Send to terminal console
      if(global.ConsolePanel){
        global.ConsolePanel.open();
        global.ConsolePanel.sendInput(cmd);
        updateStatus('Command sent to terminal');
      } else {
        alert('Console panel not available. Please ensure terminal is initialized.');
      }
    } catch(error){
      console.error('[Equalizer] Run error:', error);
      alert('Error running Equalizer: ' + error.message);
    }
  }

  // ------------------ Rendering ------------------
  /**
   * Render the equalizer table
   */
  function renderEqualizerTable(){
    const tbody = document.querySelector('#equalizerTable tbody');
    if(!tbody) return;

    if(equalizerData.length === 0){
      tbody.innerHTML = '<tr><td colspan="12" class="text-center italic opacity-60">No data</td></tr>';
      return;
    }

    const rows = equalizerData.map((row, idx) => {
      // Determine status background color - use inline style for better compatibility
      const statusUpper = row.status.toUpperCase();
      const statusStyle = statusUpper === 'PASSED' ? 'background-color: #36d399; color: #000;' : '';
      const rowClass = selectedRowIndex === idx ? 'active' : '';
      
      return `
        <tr data-index="${idx}" class="cell-row hover:bg-base-200/60 transition-colors ${rowClass}">
          <td>${idx + 1}</td>
          <td>
            <select class="select select-xs select-bordered w-20" data-field="action" data-index="${idx}">
              <option value="EQ" ${row.action === 'EQ' ? 'selected' : ''}>EQ</option>
              <option value="NOEQ" ${row.action === 'NOEQ' ? 'selected' : ''}>NOEQ</option>
            </select>
          </td>
          <td><input type="text" class="input input-xs input-bordered w-20" value="${escapeHTML(row.type)}" data-field="type" data-index="${idx}"></td>
          <td><input type="text" class="input input-xs input-bordered w-32" value="${escapeHTML(row.pin)}" data-field="pin" data-index="${idx}"></td>
          <td><input type="text" class="input input-xs input-bordered w-32" value="${escapeHTML(row.related_pin)}" data-field="related_pin" data-index="${idx}"></td>
          <td><input type="text" class="input input-xs input-bordered w-24" value="${escapeHTML(row.when)}" data-field="when" data-index="${idx}"></td>
          <td><input type="text" class="input input-xs input-bordered w-32" value="${escapeHTML(row.ff_max_min)}" data-field="ff_max_min" data-index="${idx}"></td>
          <td><input type="text" class="input input-xs input-bordered w-32" value="${escapeHTML(row.tt_max_min)}" data-field="tt_max_min" data-index="${idx}"></td>
          <td><input type="text" class="input input-xs input-bordered w-32" value="${escapeHTML(row.ss_max_min)}" data-field="ss_max_min" data-index="${idx}"></td>
          <td><input type="text" class="input input-xs input-bordered w-32" value="${escapeHTML(row.sf_max_min)}" data-field="sf_max_min" data-index="${idx}"></td>
          <td><input type="text" class="input input-xs input-bordered w-24" value="${escapeHTML(row.status)}" data-field="status" data-index="${idx}" style="${statusStyle}"></td>
          <td><input type="text" class="input input-xs input-bordered w-32" value="${escapeHTML(row.extra_margin || 'NA')}" data-field="extra_margin" data-index="${idx}"></td>
        </tr>
      `;
    }).join('');

    tbody.innerHTML = rows;
    attachInputListeners();
    updateSelectedRowClass();
  }

  function updateSelectedRowClass(){
    const rows = document.querySelectorAll('#equalizerTable tbody tr[data-index]');
    rows.forEach((rowEl) => {
      const idx = Number(rowEl.getAttribute('data-index'));
      if(idx === selectedRowIndex){
        rowEl.classList.add('active');
      } else {
        rowEl.classList.remove('active');
      }
    });
  }

  function wireRowSelection(){
    const tbody = document.querySelector('#equalizerTable tbody');
    if(!tbody || tbody.dataset.rowSelectionWired === '1') return;

    tbody.addEventListener('click', (event) => {
      const tr = event.target.closest('tr[data-index]');
      if(!tr) return;

      const idx = Number(tr.getAttribute('data-index'));
      if(Number.isNaN(idx)) return;

      selectedRowIndex = idx;
      updateSelectedRowClass();
    });

    tbody.dataset.rowSelectionWired = '1';
  }

  /**
   * Attach input change listeners to detect edits
   */
  function attachInputListeners(){
    const inputs = document.querySelectorAll('#equalizerTable input, #equalizerTable select');
    inputs.forEach(input => {
      input.addEventListener('change', handleCellEdit);
      input.addEventListener('input', handleCellEdit);
    });
  }

  /**
   * Handle cell edit
   */
  function handleCellEdit(event){
    const target = event.target;
    const field = target.dataset.field;
    const index = parseInt(target.dataset.index);

    if(field && index >= 0 && index < equalizerData.length){
      equalizerData[index][field] = target.value;
      
      // Re-render if status changed to update background color
      if(field === 'status'){
        renderEqualizerTable();
      }
      
      markDirty();
    }
  }

  /**
   * Mark data as dirty (unsaved changes)
   */
  function markDirty(){
    isDirty = true;
    updateSaveButton();
    updateStatus('Unsaved changes');
  }

  /**
   * Update save button state
   */
  function updateSaveButton(){
    const saveBtn = document.getElementById('equalizerSaveBtn');
    if(saveBtn){
      saveBtn.disabled = !isDirty;
    }
  }

  /**
   * Update status text
   */
  function updateStatus(text){
    const statusEl = document.getElementById('equalizerStatus');
    if(statusEl) statusEl.textContent = text;
  }

  // ------------------ Event Handlers ------------------
  function initEventHandlers(){
    const saveBtn = document.getElementById('equalizerSaveBtn');
    const runBtn = document.getElementById('equalizerRunBtn');

    if(saveBtn){
      saveBtn.addEventListener('click', saveEqualizerData);
    }
    
    if(runBtn){
      runBtn.addEventListener('click', runEqualizer);
    }
  }

  // ------------------ Initialization ------------------
  function init(){
    console.log('[Equalizer] Initializing...');
    initEventHandlers();
    wireRowSelection();
  }

  // Auto-initialize when DOM is ready
  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Export public API
  global.QCEqualizer = {
    load: loadEqualizerData,
    save: saveEqualizerData,
    run: runEqualizer
  };

})(window);
