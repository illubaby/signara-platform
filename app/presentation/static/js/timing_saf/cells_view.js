// Phase 1 extraction: core cell listing + filtering + visibility management for Timing SAF page
// This module owns: fetchJSON wrapper, loadCells, filtering predicates, hidden cell persistence,
// and wiring of filter UI elements.

(function(global){
  'use strict';

  // ------------------ State ------------------
  let tbody;               // <tbody> element
  let allCells = [];        // Raw cell list used for filtering
  let hiddenCells = new Set();
  let cachedBasePath = null;

  // Expose state for debugging (optional) - can be removed later
  global.__TimingSAFState = { getAll: () => allCells, getHidden: () => [...hiddenCells] };

  // ------------------ Utilities (using shared module) ------------------
  function getSelection(){
    return global.SAFSharedHttp ? global.SAFSharedHttp.getSelection() : (global.AppSelection ? global.AppSelection.get() : {project:'', subproject:''});
  }

  async function fetchJSON(url){
    if(global.SAFSharedHttp){
      return global.SAFSharedHttp.fetchJSON(url, {}, {silent: false, errorPrefix: 'Load Cells'});
    }
    // Fallback for backward compatibility
    const res = await fetch(url);
    if(!res.ok){ throw new Error(await res.text()); }
    return res.json();
  }

  async function fetchBasePath(){
    if(cachedBasePath) return cachedBasePath;
    try {
      const res = await fetch('/api/config/base-path');
      if(res.ok){
        const data = await res.json();
        cachedBasePath = data.base_path;
        return cachedBasePath;
      }
    } catch(err){ console.warn('BASE path fetch failed', err); }
    return null;
  }

  async function updateLibraryPaths(project, subproject){
    const rawLibsInput = document.getElementById('rawLibsPathInput');
    const posteditLibsInput = document.getElementById('posteditLibsPathInput');
    const postQaLibsInput = document.getElementById('postQaLibsPathInput');
    if(!(rawLibsInput && posteditLibsInput && postQaLibsInput)) return;

    if(!project || !subproject){
      rawLibsInput.value = posteditLibsInput.value = postQaLibsInput.value = '';
      return;
    }
    const basePath = await fetchBasePath();
    const base = basePath || '{BASE}';
    rawLibsInput.value     = `${base}/${project}/${subproject}/design/timing/release/raw_lib`;
    posteditLibsInput.value= `${base}/${project}/${subproject}/design/timing/release/Postedit_libs`;
    postQaLibsInput.value  = `${base}/${project}/${subproject}/design/timing/release/PostQA_libs`;
  }

  // ------------------ Hidden Cells Persistence ------------------
  function hiddenKey(){
    const sel = getSelection();
    if(sel.project && sel.subproject){
      return `timing_saf_hidden_cells_${sel.project}_${sel.subproject}`;
    }
    return null;
  }

  function loadHiddenCells(){
    const key = hiddenKey();
    if(!key){ hiddenCells = new Set(); return; }
    try {
      const saved = localStorage.getItem(key);
      hiddenCells = saved ? new Set(JSON.parse(saved)) : new Set();
    } catch(err){
      console.warn('Hidden cells load failed', err);
      hiddenCells = new Set();
    }
  }

  function saveHiddenCells(){
    const key = hiddenKey();
    if(!key) return;
    try { localStorage.setItem(key, JSON.stringify([...hiddenCells])); } catch(err){ console.warn('Hidden cells save failed', err); }
  }

  // ------------------ Filtering Logic (Pure Predicate) ------------------
  function cellMatchesFilters(cell, filters){
    // cell: { cell, type, pvt_status_summary }
    const { searchTerm, typeFilter, pvtFilter, hiddenSet } = filters;

    if(hiddenSet.has(cell.cell)) return false;

    if(searchTerm && !cell.cell.toLowerCase().includes(searchTerm)) return false;

    if(typeFilter !== 'all' && cell.type !== typeFilter) return false;

    const summary = cell.pvt_status_summary || {};
    if(pvtFilter !== 'all'){
      switch(pvtFilter){
        case 'passed':      if(!(summary.passed>0)) return false; break;
        case 'failed':      if(!(summary.failed>0)) return false; break;
        case 'in_progress': if(!(summary.in_progress>0)) return false; break;
        case 'not_started': if(!(summary.not_started>0)) return false; break;
      }
    }
    return true;
  }

  // Export predicate for unit tests
  global.applyCellFiltersPredicate = cellMatchesFilters;

  function applyFilters(){
    // Handle missing filter elements gracefully when filters panel is disabled
    const cellSearchInput = document.getElementById('cellSearchInput');
    const cellTypeFilter = document.getElementById('cellTypeFilter');
    const pvtStatusFilter = document.getElementById('pvtStatusFilter');
    
    const searchTerm = cellSearchInput ? cellSearchInput.value.toLowerCase() : '';
    const typeFilter = cellTypeFilter ? cellTypeFilter.value : 'all';
    const pvtFilter = pvtStatusFilter ? pvtStatusFilter.value : 'all';

    const filters = { searchTerm, typeFilter, pvtFilter, hiddenSet: hiddenCells };

    // Iterate table rows and decide visibility using row dataset
    tbody.querySelectorAll('tr.cell-row').forEach(row => {
      const cellName = row.getAttribute('data-cell');
      const type = row.getAttribute('data-type');
      let summary = {};
      try { summary = JSON.parse(row.getAttribute('data-pvt-summary') || '{}'); } catch(_){}
      const show = cellMatchesFilters({ cell: cellName, type, pvt_status_summary: summary }, filters);
      row.classList.toggle('hidden', !show);
    });

    updateCellCounts();
  }

  function updateCellCounts(){
    const totalCount = allCells.length;
    const visibleCount = tbody.querySelectorAll('tr.cell-row:not(.hidden)').length;
    const hiddenCount = hiddenCells.size;
    const badge = document.getElementById('cellCountBadge');
    if(badge) badge.textContent = totalCount;
    const totalEl = document.getElementById('totalCellCount'); if(totalEl) totalEl.textContent = totalCount;
    const visEl = document.getElementById('visibleCellCount'); if(visEl) visEl.textContent = visibleCount;
    const hiddenEl = document.getElementById('hiddenCellCount'); if(hiddenEl) hiddenEl.textContent = hiddenCount>0 ? `(${hiddenCount} manually hidden)` : '';
  }

  // ------------------ Manage Cells Modal ------------------
  function openManageCellsModal(){
    populateManageCellsList();
    document.getElementById('manageCellsModal').showModal();
  }

  function populateManageCellsList(){
    const container = document.getElementById('manageCellsList');
    if(!container) return;
    if(allCells.length === 0){
      container.innerHTML = '<div class="text-center py-4 opacity-70">No cells available</div>';
      return;
    }
    container.innerHTML = allCells.map(c => {
      const isHidden = hiddenCells.has(c.cell);
      const typeLabel = c.type === 'nt' ? 'NT' : 'SiS';
      return `<label class='flex items-center gap-2 p-2 hover:bg-base-300 rounded cursor-pointer'>
        <input type='checkbox' class='checkbox checkbox-xs manage-cell-checkbox' data-cell='${c.cell}' ${isHidden ? '' : 'checked'}>
        <span class='flex-1 font-mono text-sm'>${c.cell}</span>
        <span class='badge badge-xs badge-${c.type === 'nt' ? 'info' : 'primary'}'>${typeLabel}</span>
      </label>`;
    }).join('');
  }

  function filterManageCellsList(searchTerm=''){
    const container = document.getElementById('manageCellsList');
    if(!container) return;
    const q = (searchTerm || '').toLowerCase();
    const labels = container.querySelectorAll('label');
    if(labels.length === 0) return;
    labels.forEach(label => {
      const nameEl = label.querySelector('span.flex-1');
      const name = (nameEl && nameEl.textContent) ? nameEl.textContent.toLowerCase() : '';
      const match = q === '' || name.includes(q);
      label.classList.toggle('hidden', !match);
    });
  }

  function wireFilterControls(){
    // Make filter controls optional - check if elements exist before wiring
    const cellSearchInput = document.getElementById('cellSearchInput');
    const cellTypeFilter = document.getElementById('cellTypeFilter');
    const pvtStatusFilter = document.getElementById('pvtStatusFilter');
    const clearFiltersBtn = document.getElementById('clearFiltersBtn');
    
    if(cellSearchInput) cellSearchInput.addEventListener('input', applyFilters);
    if(cellTypeFilter) cellTypeFilter.addEventListener('change', applyFilters);
    if(pvtStatusFilter) pvtStatusFilter.addEventListener('change', applyFilters);
    if(clearFiltersBtn) clearFiltersBtn.addEventListener('click', () => {
      if(cellSearchInput) cellSearchInput.value='';
      if(cellTypeFilter) cellTypeFilter.value='all';
      if(pvtStatusFilter) pvtStatusFilter.value='all';
      applyFilters();
    });
    
    const manageVisibilityBtn = document.getElementById('manageVisibilityBtn');
    if(manageVisibilityBtn) manageVisibilityBtn.addEventListener('click', openManageCellsModal);
    
    const manageCellsSearch = document.getElementById('manageCellsSearch');
    if(manageCellsSearch) manageCellsSearch.addEventListener('input', e=>filterManageCellsList(e.target.value));
    
    const tickAllBtn = document.getElementById('tickAllBtn');
    if(tickAllBtn) tickAllBtn.addEventListener('click', () => {
      document.querySelectorAll('.manage-cell-checkbox').forEach(cb => cb.checked = true);
    });
    
    const untickAllBtn = document.getElementById('untickAllBtn');
    if(untickAllBtn) untickAllBtn.addEventListener('click', () => {
      document.querySelectorAll('.manage-cell-checkbox').forEach(cb => cb.checked = false);
    });
    
    const manageCellsModal = document.getElementById('manageCellsModal');
    if(manageCellsModal) manageCellsModal.addEventListener('close', () => {
      document.querySelectorAll('.manage-cell-checkbox').forEach(cb => {
        const cell = cb.getAttribute('data-cell');
        if(cb.checked) hiddenCells.delete(cell); else hiddenCells.add(cell);
      });
      saveHiddenCells();
      applyFilters();
    });
  }

  // ------------------ Rendering ------------------
  function renderCells(data, project, subproject){
    allCells = [];
    tbody.innerHTML = data.cells.map(c => {
      allCells.push({
        cell: c.cell,
        type: c.type || 'sis',
        netlist_version: c.netlist_version,
        pvt_status_summary: c.pvt_status_summary,
        final_libs: c.final_libs,
          pvts: c.pvts || [],
          nt_setup_complete: c.nt_setup_complete === true,
          nt_munge_complete: c.nt_munge_complete === true,
          nt_merge_complete: c.nt_merge_complete === true
      });
      const isHidden = hiddenCells.has(c.cell);
      const hiddenClass = isHidden ? ' hidden' : '';
      const summaryStr = JSON.stringify(c.pvt_status_summary || {});
      const typeLabel = c.type || 'sis';
      const netVersion = c.netlist_version || '';
      const netMissing = netVersion.toLowerCase().includes('missing');
      const netMismatch = netVersion.toLowerCase().includes('mismatch');
      const netLabel = netMissing ? 'Missing' : (netVersion.startsWith('#') ? netVersion.substring(1) : netVersion);
      let netlistCell;
      if(netMissing){
        netlistCell = `<span class='text-error cursor-pointer hover:opacity-60 netlist-sync' data-cell='${c.cell}' data-type='${c.type}' title='Click to sync netlist from P4'>${netLabel}</span>`;
      } else {
        const colorClass = netMismatch ? 'text-error' : '';
        netlistCell = `<span class='${colorClass} cursor-pointer hover:opacity-60 netlist-sync' data-cell='${c.cell}' data-type='${c.type}' title='Click to get latest netlist from P4'>${netLabel}</span>`;
      }
      // Use Phase 2 extracted badge renderer
      const pvtStatusHTML = global.PvtStatus ? global.PvtStatus.buildPvtStatusHTML(c.pvt_status_summary) : '<span class="text-xs opacity-50">-</span>';
      // Removed NT setup status badge (success/ghost) per user request
      // Previously showed a green check or placeholder for NT cells; now omitted entirely
      let ntBadge='';
      // Intentionally left blank: no visual badge for NT setup state
      // Run button style via Phase 2 logic
      let rb = global.PvtStatus ? global.PvtStatus.computeRunButton(c.pvt_status_summary) : {class:'btn-ghost hover:btn-primary', text:'Run', icon:'', title:'Run SAF for this cell'};
      // Revised NT run completion logic: use same criterion as Merge button (raw_lib/<cell> has 2x merged PVT libs)
      if(c.type === 'nt' && c.nt_merge_complete){
        rb = {class:'btn-outline btn-success opacity-60', text:'Completed ✓', icon:'', title:'Raw libs complete: 2× merged PVT .lib files present. Click to re-run.'};
      }
      const runBtn = `<button class='btn btn-xs ${rb.class} run-job-btn' data-cell='${c.cell}' data-type='${c.type}' title='${rb.title}'>${rb.icon||''}${rb.text}</button>`;
      const postEditBtn = `<button class='btn btn-xs btn-ghost hover:btn-primary postedit-settings-btn' data-cell='${c.cell}' data-type='${c.type}' data-pvt-count='${c.pvt_count||8}' data-lib-count='0'>Run</button>`;
      const qaBtn = `<button class='btn btn-xs btn-ghost hover:btn-primary timingqa-settings-btn' data-cell='${c.cell}' data-type='${c.type}' data-lib-count='0'>Run</button>`;
      const statusBtn = c.brief_sum_exists ? `<button class='btn btn-xs btn-ghost hover:btn-info view-brief-sum-btn' data-cell='${c.cell}' data-project='${project}' data-subproject='${subproject}' title='Open TMQA Report (.xlsx)'>Report</button>` : '<span class="text-xs opacity-50">-</span>';
  return `<tr data-cell='${c.cell}' data-type='${typeLabel}' data-nt-setup='${c.nt_setup_complete? '1':'0'}' data-nt-munge='${c.nt_munge_complete? '1':'0'}' data-nt-merge='${c.nt_merge_complete? '1':'0'}' data-pvt-count='${c.pvt_count||8}' class='cell-row hover:bg-base-200/60 cursor-pointer transition-colors${hiddenClass}' data-pvt-summary='${summaryStr}' data-project='${project}' data-subproject='${subproject}'>
        <td class='font-mono text-xs'>${c.cell}</td>
  <td class='font-mono text-xs'>${typeLabel}</td>
        <td class='font-mono text-xs'>${netlistCell}</td>
        <td>${pvtStatusHTML}</td>
        <td>${runBtn}</td>
        <td>${postEditBtn}</td>
        <td>${qaBtn}</td>
        <td>${statusBtn}</td>
      </tr>`;
    }).join('');
    updateCellCounts();
    applyFilters();
  }

  // ------------------ Public: loadCells ------------------
  async function loadCells(opts={debug:false, force:false}){
    const sel = getSelection();
    if(!(sel.project && sel.subproject)) return;
    await updateLibraryPaths(sel.project, sel.subproject);
    tbody.innerHTML = '<tr><td colspan="8">Loading...</td></tr>';
    try {
      const q=[]; if(opts.debug) q.push('debug=1'); if(opts.force) q.push('force_refresh=1');
      const url = `/api/saf/${sel.project}/${sel.subproject}/cells` + (q.length?`?${q.join('&')}`:'');
      const data = await fetchJSON(url);
      if(!data.cells.length){
        tbody.innerHTML = '<tr><td colspan="8" class="text-center opacity-70">No cells found.</td></tr>';
        return;
      }
      renderCells(data, sel.project, sel.subproject);
      // Check lib counts for all cells after rendering
      if(global.SAFPostEditQA){
        data.cells.forEach(c => {
          global.SAFPostEditQA.checkPosteditLibCount(c.cell);
          global.SAFPostEditQA.checkPostQALibCount(c.cell);
        });
      }
    } catch(err){
      console.error('loadCells failed', err);
      tbody.innerHTML = `<tr><td colspan='8' class='text-error'>Error loading cells: ${err}</td></tr>`;
    }
  }

  // ------------------ Initialization ------------------
  function initCellsView(){
    tbody = document.querySelector('#cellsTable tbody');
    loadHiddenCells();
    wireFilterControls();

    // Global selection integration
    try {
      if(global.AppSelection){
        applyStoredSelection();
      } else {
        global.addEventListener('app-selection-ready', () => applyStoredSelection(), {once:true});
      }
    } catch(err){
      console.error('Timing SAF cells init failed', err);
      tbody.innerHTML = `<tr><td colspan='8' class='text-error'>Initialization error: ${err}</td></tr>`;
    }
  }

  function applyStoredSelection(){
    const sel = getSelection();
    if(!(sel.project && sel.subproject)){
      tbody.innerHTML = '<tr><td colspan="8" class="text-center opacity-70">No project selected.</td></tr>';
      return;
    }
    loadHiddenCells();
    allCells = []; // reset
    loadCells();
  }

  // Export public API
  global.TimingSafCells = { init: initCellsView, reload: loadCells };

})(window);
