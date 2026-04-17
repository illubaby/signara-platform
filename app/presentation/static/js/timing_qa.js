// Utilities
async function fetchJSON(u,o){const r=await fetch(u,o); if(!r.ok) throw new Error(await r.text()); return r.json();}
function escapeHtml(t){const d=document.createElement('div');d.textContent=t;return d.innerHTML;}

// URL Param Support (cells=, cell=, data_release=, autorun=1, qa_debug=1)
const _qaParams = new URLSearchParams(window.location.search);
const _presetCells = _qaParams.get('cells') ? _qaParams.get('cells').split(/[\s,]+/).filter(Boolean)
                      : (_qaParams.get('cell') ? [_qaParams.get('cell')] : []);
const _presetDataRelease = _qaParams.get('data_release');
// Legacy autorun parameter parsed but intentionally ignored (manual run required)
const _autoRun = false; // _qaParams.get('autorun') === '1';
const _qaDebug = _qaParams.get('qa_debug') === '1';
function _qaLog(){ if(_qaDebug) console.log('[TimingQA]', ...arguments); }

// Detect QA type from URL path (timing-qa-process uses 'process', default is 'quality')
const _qaType = window.location.pathname.includes('timing-qa-process') ? 'process' : 'quality';
_qaLog('QA Type:', _qaType);

const selState=()=> window.AppSelection? window.AppSelection.get(): {project:'', subproject:''};
const cellCheckboxContainer=document.getElementById('cellCheckboxContainer');
const cellSelectorStatus=document.getElementById('cellSelectorStatus');
const selectAllCellsBtn=document.getElementById('selectAllCellsBtn');
const clearCellsBtn=document.getElementById('clearCellsBtn');
const runBtn=document.getElementById('runBtn');
const qaStatusNote=document.getElementById('qaStatusNote');
const runDirInput=document.getElementById('runDirInput');
const dataReleaseInput=document.getElementById('dataReleaseInput');
const headerInput=document.getElementById('headerInput');
const cellListInput=document.getElementById('cellListInput');
const planInput=document.getElementById('planInput');
const outdirInput=document.getElementById('outdirInput');
const queueInput=document.getElementById('queueInput');
const prjInput=document.getElementById('prjInput');
const relInput=document.getElementById('relInput');
const loadMatrixBtn=document.getElementById('loadMatrixBtn');
const matrixMeta=document.getElementById('matrixMeta');
const matrixTable=document.getElementById('matrixTable');
const matrixFilters=document.getElementById('matrixFilters');
const matrixCellFilters=document.getElementById('matrixCellFilters');
const matrixCheckFilters=document.getElementById('matrixCheckFilters');
const selectAllMatrixCellsBtn=document.getElementById('selectAllMatrixCellsBtn');
const clearAllMatrixCellsBtn=document.getElementById('clearAllMatrixCellsBtn');
const selectAllMatrixChecksBtn=document.getElementById('selectAllMatrixChecksBtn');
const clearAllMatrixChecksBtn=document.getElementById('clearAllMatrixChecksBtn');

// Store full matrix data for filtering
let fullMatrixData = null;

// Execution output elements
const execGroup = document.getElementById('executionOutputGroup');
const infoScriptPath = document.getElementById('infoScriptPath');
const infoWorkingDir = document.getElementById('infoWorkingDir');
const infoStatus = document.getElementById('infoStatus');
const infoElapsed = document.getElementById('infoElapsed');
const infoElapsedRow = document.getElementById('infoElapsedRow');
const scriptStream = document.getElementById('scriptStream');
const stopScriptBtn = document.getElementById('stopScriptBtn');
const clearScriptBtn = document.getElementById('clearScriptBtn');
const autoscrollScript = document.getElementById('autoscrollScript');

// Legacy job tracking variables removed (streaming now handled by ExecutionStreamFactory)
// let currentJobId = null;
// let pollInterval = null;
// let jobStartTime = null;
let loadCellsTimeout = null;

async function loadChecks(){
  const sel=selState(); if(!(sel.project&&sel.subproject)) return;
  try{
    const data=await fetchJSON(`/api/qa/${sel.project}/${sel.subproject}/checks`);
    const cont=document.getElementById('checksContainerUnified');
    const flat = data.checks || [];
    cont.innerHTML = flat.map(name=>{
      return `<label class='flex items-start gap-1 cursor-pointer'><input type='checkbox' value='${name}' class='checkbox checkbox-xs qa-check' checked><span class='leading-tight break-all'>${name}</span></label>`;
    }).join('');
  } catch(e){ console.warn('Checks load failed', e); }
}

async function loadAvailableCells() {
  const sel=selState(); 
  if(!(sel.project&&sel.subproject)) return;
  
  const dataReleasePath = dataReleaseInput.value.trim();
  if(!dataReleasePath) {
    cellCheckboxContainer.innerHTML = '<div class="text-center text-[11px] opacity-60 py-4">Enter Data Release path to auto-load cells</div>';
    cellSelectorStatus.textContent = 'No cells loaded';
    selectAllCellsBtn.disabled = true;
    clearCellsBtn.disabled = true;
    validateEnableRun();
    return;
  }
  
  cellSelectorStatus.textContent = 'Loading cells...';
  cellCheckboxContainer.innerHTML = '<div class="text-center text-[11px] opacity-60 py-4"><span class="loading loading-spinner loading-xs"></span> Loading...</div>';
  selectAllCellsBtn.disabled = true;
  clearCellsBtn.disabled = true;
  
  try {
    const data = await fetchJSON(`/api/qa/${sel.project}/${sel.subproject}/available-cells?data_release=${encodeURIComponent(dataReleasePath)}`);
    
    if(!data.cells || data.cells.length === 0) {
      cellCheckboxContainer.innerHTML = '<div class="text-center text-[11px] opacity-60 py-4">No cells found in Data Release path</div>';
      cellSelectorStatus.textContent = data.note || 'No cells found';
      selectAllCellsBtn.disabled = true;
      clearCellsBtn.disabled = true;
    } else {
      cellCheckboxContainer.innerHTML = data.cells.map(cell => 
        `<label class='flex items-center gap-2 cursor-pointer hover:bg-base-300 px-2 py-1 rounded'>
          <input type='checkbox' value='${cell}' class='checkbox checkbox-xs cell-checkbox'>
          <span class='text-[11px]'>${cell}</span>
        </label>`
      ).join('');
      
      // Add change listener to all checkboxes
      document.querySelectorAll('.cell-checkbox').forEach(cb => {
        cb.addEventListener('change', validateEnableRun);
      });
      
      cellSelectorStatus.textContent = data.note || `${data.cells.length} cells available`;
      selectAllCellsBtn.disabled = false;
      clearCellsBtn.disabled = false;
      // Apply preset cell selection from URL if present
      if(_presetCells.length){
        let matched=0; const boxes=document.querySelectorAll('.cell-checkbox');
        _presetCells.forEach(pc=>{ const box=[...boxes].find(b=>b.value===pc); if(box){ box.checked=true; matched++; }});
        if(matched){ _qaLog('Preset cells applied', _presetCells); qaStatusNote.textContent=`Preset selected ${matched}/${_presetCells.length} cell(s).`; }
      }
    }
    validateEnableRun();
  } catch(e) {
    cellCheckboxContainer.innerHTML = `<div class="text-center text-[11px] text-error py-4">Error: ${escapeHtml(e.toString())}</div>`;
    cellSelectorStatus.textContent = `Error loading cells`;
    selectAllCellsBtn.disabled = true;
    clearCellsBtn.disabled = true;
  }
}

function getSelectedCells() {
  return [...document.querySelectorAll('.cell-checkbox:checked')].map(cb => cb.value);
}

function validateEnableRun(){ 
  const selectedCells = getSelectedCells();
  const req=[
    selectedCells.length > 0,
    dataReleaseInput.value.trim(), 
    headerInput.value.trim(), 
    outdirInput.value.trim(), 
    prjInput.value.trim(), 
    relInput.value.trim()
  ]; 
  const ok=req.every(v=>v); 
  // Keep Run button always clickable; only disable while job is running
  runBtn.disabled=false; 
  // Enable load matrix button if run directory is provided
  loadMatrixBtn.disabled = !runDirInput.value.trim();
  qaStatusNote.textContent= ok? 'Ready to run' : 'You can run now; fill recommended fields and select cells for best results.'; 
}

async function loadMatrixSummary() {
  const sel = selState();
  if(!(sel.project && sel.subproject)) {
    matrixMeta.textContent = 'Select project first';
    return;
  }
  
  const runDir = runDirInput.value.trim();
  if(!runDir) {
    matrixMeta.textContent = 'Enter Run Directory first';
    return;
  }
  
  matrixMeta.textContent = 'Loading matrix...';
  const tbody = matrixTable.querySelector('tbody');
  tbody.innerHTML = '<tr><td colspan="100" class="text-center opacity-60"><span class="loading loading-spinner loading-xs"></span> Loading...</td></tr>';
  matrixFilters.classList.add('hidden');
  
  try {
    const data = await fetchJSON(`/api/qa/${sel.project}/${sel.subproject}/matrix-summary?run_dir=${encodeURIComponent(runDir)}`);
    
    if(!data.cell_names || data.cell_names.length === 0) {
      tbody.innerHTML = '<tr><td colspan="100" class="text-center italic opacity-60">No cells with brief.sum found</td></tr>';
      matrixMeta.textContent = data.note || 'No data';
      fullMatrixData = null;
      return;
    }
    
    // Store full matrix data for filtering
    fullMatrixData = data;
    
    // Populate filter checkboxes
    matrixCellFilters.innerHTML = data.cell_names.map((cell, idx) => 
      `<label class='flex items-center gap-1 cursor-pointer hover:bg-base-200 px-1 py-0.5 rounded text-[11px]'>
        <input type='checkbox' value='${idx}' class='checkbox checkbox-xs matrix-cell-filter' checked>
        <span class='truncate' title='${escapeHtml(cell)}'>${escapeHtml(cell)}</span>
      </label>`
    ).join('');
    
    matrixCheckFilters.innerHTML = data.check_items.map((check, idx) => 
      `<label class='flex items-center gap-1 cursor-pointer hover:bg-base-200 px-1 py-0.5 rounded text-[11px]'>
        <input type='checkbox' value='${idx}' class='checkbox checkbox-xs matrix-check-filter' checked>
        <span class='truncate' title='${escapeHtml(check)}'>${escapeHtml(check)}</span>
      </label>`
    ).join('');
    
    // Add change listeners to filters
    document.querySelectorAll('.matrix-cell-filter, .matrix-check-filter').forEach(cb => {
      cb.addEventListener('change', renderFilteredMatrix);
    });
    
    // Show filters
    matrixFilters.classList.remove('hidden');
    
    // Render initial matrix (all selected)
    renderFilteredMatrix();
    
    matrixMeta.textContent = data.note || `${data.cell_names.length} cells × ${data.check_items.length} checks`;
  } catch(e) {
    tbody.innerHTML = `<tr><td colspan='100' class='text-error text-xs text-center'>Error loading matrix: ${escapeHtml(e.toString())}</td></tr>`;
    matrixMeta.textContent = 'Error loading matrix';
    fullMatrixData = null;
  }
}

function renderFilteredMatrix() {
  if(!fullMatrixData) return;

  // For transposed view:
  // Rows = Cells, Columns = Check Items
  const selectedCellIndices = [...document.querySelectorAll('.matrix-cell-filter:checked')].map(cb => parseInt(cb.value)); // rows
  const selectedCheckIndices = [...document.querySelectorAll('.matrix-check-filter:checked')].map(cb => parseInt(cb.value)); // columns

  const thead = matrixTable.querySelector('thead tr');
  const tbody = matrixTable.querySelector('tbody');

  if(selectedCellIndices.length === 0 || selectedCheckIndices.length === 0) {
    thead.innerHTML = '<th class="bg-base-200 sticky left-0 z-10">Cell Name</th>';
    tbody.innerHTML = '<tr><td class="text-center italic opacity-60 py-4">Select at least one cell and one check item to view matrix</td></tr>';
    matrixMeta.textContent = `Filtered: ${selectedCellIndices.length} cells × ${selectedCheckIndices.length} checks`;
    return;
  }

  // Header: first column Cell Name, then each selected check item
  thead.innerHTML = '<th class="bg-base-200 sticky left-0 z-10">Cell Name</th>' +
    selectedCheckIndices.map(checkIdx => {
      const check = fullMatrixData.check_items[checkIdx];
      return `<th class="bg-base-200 text-center text-[10px] max-w-[120px] truncate" title="${escapeHtml(check)}">${escapeHtml(check)}</th>`;
    }).join('');

  // Body: each row per cell
  tbody.innerHTML = selectedCellIndices.map(cellIdx => {
    const cellName = fullMatrixData.cell_names[cellIdx];
    const rowChecks = selectedCheckIndices.map(checkIdx => {
      const status = fullMatrixData.status_matrix[checkIdx][cellIdx];
      const statusLower = (status || '').toLowerCase();
      let badgeClass = 'badge-neutral';
      if (statusLower === 'pass') badgeClass = 'badge-success';
      else if (statusLower === 'fail') badgeClass = 'badge-error';
      else if (statusLower === 'warning') badgeClass = 'badge-warning';
      else if (statusLower === 'waived') badgeClass = 'badge-info';
      else if (statusLower === 'unknown') badgeClass = 'badge-ghost';
      const displayStatus = status || '-';
      return `<td class="text-center text-[10px]"><span class="badge badge-xs ${badgeClass}" title="${escapeHtml(status||'')}">${escapeHtml(displayStatus)}</span></td>`;
    }).join('');
    return `<tr><th class="sticky left-0 bg-base-200 text-[10px] font-normal max-w-[160px] truncate" title="${escapeHtml(cellName)}">${escapeHtml(cellName)}</th>${rowChecks}</tr>`;
  }).join('');

  matrixMeta.textContent = `Filtered: ${selectedCellIndices.length} cells × ${selectedCheckIndices.length} checks (${fullMatrixData.cell_names.length} total cells × ${fullMatrixData.check_items.length} total checks)`;
}

// Removed pollJobStatus/stopPolling (no longer needed with direct streaming)

function applyContext(){
  const sel=selState();
  // If no selection, nothing to apply. Context bar removed; navbar handles selection UX.
  if(!(sel.project && sel.subproject)) return;
  // Prefill project/release if empty
  if(!prjInput.value.trim()) prjInput.value = sel.project;
  if(!relInput.value.trim()) relInput.value = sel.subproject;
  validateEnableRun();
  loadChecks();
  // Auto-load defaults when context becomes available
  const defaultsBtn = document.getElementById('defaultsBtn');
  if(defaultsBtn) defaultsBtn.click();
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  // Remember collapse state
  const qaConfigCollapse = document.getElementById('qaConfigCollapse');
  const qaStorageKey = 'timing_qa_config_collapsed';
  const qaSavedState = localStorage.getItem(qaStorageKey);
  if (qaSavedState === 'open') {
    qaConfigCollapse.checked = true;
  }
  qaConfigCollapse.addEventListener('change', () => {
    localStorage.setItem(qaStorageKey, qaConfigCollapse.checked ? 'open' : 'collapsed');
  });

  // Remember matrix collapse state
  const qaMatrixCollapse = document.getElementById('qaMatrixCollapse');
  if (qaMatrixCollapse) {
    const qaMatrixKey = 'timing_qa_matrix_collapsed';
    const qaMatrixSaved = localStorage.getItem(qaMatrixKey);
    if (qaMatrixSaved === 'open') {
      qaMatrixCollapse.checked = true;
    }
    qaMatrixCollapse.addEventListener('change', () => {
      localStorage.setItem(qaMatrixKey, qaMatrixCollapse.checked ? 'open' : 'collapsed');
    });
  }

  // Auto-load cells when data release path changes (with debounce)
  dataReleaseInput.addEventListener('input', ()=> {
    if(loadCellsTimeout) clearTimeout(loadCellsTimeout);
    loadCellsTimeout = setTimeout(() => {
      loadAvailableCells();
    }, 800);
  });

  // Also trigger on blur (when user leaves the field)
  dataReleaseInput.addEventListener('blur', ()=> {
    if(loadCellsTimeout) clearTimeout(loadCellsTimeout);
    loadAvailableCells();
  });

  // Select all cells button
  selectAllCellsBtn.addEventListener('click', ()=> {
    document.querySelectorAll('.cell-checkbox').forEach(cb => cb.checked = true);
    validateEnableRun();
  });

  // Clear cells button
  clearCellsBtn.addEventListener('click', ()=> {
    document.querySelectorAll('.cell-checkbox').forEach(cb => cb.checked = false);
    validateEnableRun();
  });

  // Input field validation
  ['headerInput','planInput','outdirInput','queueInput','prjInput','relInput','runDirInput'].forEach(id=> {
    document.getElementById(id).addEventListener('input', validateEnableRun);
  });
  
  // Load matrix button
  loadMatrixBtn.addEventListener('click', () => loadMatrixSummary());

  // Defaults button
  document.getElementById('defaultsBtn').addEventListener('click', async ()=>{ 
    const sel=selState(); 
    if(!(sel.project&&sel.subproject)){ alert('Select project first'); return;} 
    try { 
      const cell = prjInput.value.trim() || ''; 
      const cellParam = cell ? `cell=${encodeURIComponent(cell)}` : '';
      const qaTypeParam = `qa_type=${encodeURIComponent(_qaType)}`;
      const queryString = [cellParam, qaTypeParam].filter(Boolean).join('&');
      const defs=await fetchJSON(`/api/qa/${sel.project}/${sel.subproject}/defaults?${queryString}`); 
      if(defs.header_file) headerInput.value=defs.header_file; 
      if(defs.cell_list_file) cellListInput.value=defs.cell_list_file;
      if(defs.data_release) dataReleaseInput.value=defs.data_release; 
      if(defs.plan_file) planInput.value=defs.plan_file; 
      if(defs.outdir) outdirInput.value=defs.outdir; 
      if(defs.queue) queueInput.value=defs.queue; 
      if(defs.run_dir) runDirInput.value=defs.run_dir;
      // Override data release from URL param if provided
      if(_presetDataRelease){ dataReleaseInput.value=_presetDataRelease; _qaLog('Data release overridden via URL param:', _presetDataRelease); }
      
      validateEnableRun(); 
      qaStatusNote.textContent='Defaults applied - Loading cells...'; 
      
      // Auto-load cells after setting defaults
      await loadAvailableCells();
    } catch(e){ 
      qaStatusNote.textContent='Defaults error'; 
    }
  });

  // Clear script output button
  if(clearScriptBtn) clearScriptBtn.addEventListener('click', ()=>{ scriptStream.textContent=''; });

  // Run QA button (streaming execution using ExecutionStreamFactory)
  runBtn.addEventListener('click', async ()=>{
    const sel=selState(); if(runBtn.disabled) return;
    const allChecked=[...document.querySelectorAll('.qa-check:checked')].map(c=>c.value);
    const selectedCells = getSelectedCells();
    const hasCustomCellList = !!((cellListInput.value || '').trim());
    // Allow running without selecting cells when a custom cell list file is provided
    if(selectedCells.length === 0 && !hasCustomCellList) { qaStatusNote.textContent = 'No cells selected. You can still provide a cell list file.'; return; }

    const payload={
      selected_cells: selectedCells,
      data_release: dataReleaseInput.value.trim(),
      header_file: headerInput.value.trim(),
      cell_list_file: (cellListInput.value || '').trim() || null,
      project: prjInput.value.trim(),
      release: relInput.value.trim(),
      plan_file: planInput.value.trim()||null,
      outdir: outdirInput.value.trim(),
      queue: queueInput.value.trim(),
      run_dir: runDirInput.value.trim()||null,
      selected_checks: allChecked
    };

    // Open modal & reset UI
    if(execGroup){
      execGroup.classList.remove('hidden');
    } else {
      console.warn('[TimingQA] Execution output container not found');
    }
    document.getElementById('executionOutputModal').showModal();
    infoStatus.innerHTML = '<span class="loading loading-spinner loading-xs"></span> Preparing script...';
    infoElapsedRow.style.display = 'none';
    scriptStream.textContent = '';
    stopScriptBtn.disabled = true;
    qaStatusNote.innerHTML='<span class="loading loading-spinner loading-xs"></span> Preparing...';
    runBtn.disabled=true;

    try {
      // First call existing run endpoint to generate script (legacy behavior)
      const res=await fetchJSON(`/api/qa/${sel.project}/${sel.subproject}/run`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)});

      // Update info panel
      if(res.script_path) infoScriptPath.textContent = res.script_path;
      if(res.working_dir) infoWorkingDir.textContent = res.working_dir;
      qaStatusNote.textContent = 'Script generated. Starting streaming execution...';

      // Start streaming execution using ExecutionStreamFactory (3 inputs only)
      if(window.ExecutionStreamFactory){
        infoStatus.innerHTML = '<span class="loading loading-spinner loading-xs"></span> Running...';
        const streamController = window.ExecutionStreamFactory.create({
          executionDir: res.working_dir,
          command: res.script_path,
          containerId: 'executionOutputGroup',
          onComplete: (result)=>{
            qaStatusNote.textContent = `Completed (success=${result.success})`;
            // Auto-load matrix summary after completion
            if(runDirInput.value.trim()){
              loadMatrixSummary();
            }
            runBtn.disabled = false;
          },
          onError: (err)=>{
            qaStatusNote.textContent = `Error: ${err}`;
            runBtn.disabled = false;
          }
        });
        if(streamController){ streamController.connect(); }
      } else {
        infoStatus.innerHTML = '<span class="text-error">Streaming module not loaded</span>';
        runBtn.disabled = false;
      }
    } catch(e){
      qaStatusNote.innerHTML=`<span class='text-error text-xs'>Run error: ${e}</span>`;
      infoStatus.innerHTML = `<span class='text-error'>Error: ${escapeHtml(e.toString())}</span>`;
      runBtn.disabled = false;
    }
  });

  // Check all/uncheck all buttons
  document.getElementById('checkAllBtn').addEventListener('click', ()=>{ 
    document.querySelectorAll('#checksContainerUnified .qa-check').forEach(cb=> cb.checked=true); 
  });
  document.getElementById('uncheckAllBtn').addEventListener('click', ()=>{ 
    document.querySelectorAll('#checksContainerUnified .qa-check').forEach(cb=> cb.checked=false); 
  });
  
  // Matrix filter buttons
  selectAllMatrixCellsBtn.addEventListener('click', ()=>{ 
    document.querySelectorAll('.matrix-cell-filter').forEach(cb=> cb.checked=true); 
    renderFilteredMatrix();
  });
  clearAllMatrixCellsBtn.addEventListener('click', ()=>{ 
    document.querySelectorAll('.matrix-cell-filter').forEach(cb=> cb.checked=false); 
    renderFilteredMatrix();
  });
  selectAllMatrixChecksBtn.addEventListener('click', ()=>{ 
    document.querySelectorAll('.matrix-check-filter').forEach(cb=> cb.checked=true); 
    renderFilteredMatrix();
  });
  clearAllMatrixChecksBtn.addEventListener('click', ()=>{ 
    document.querySelectorAll('.matrix-check-filter').forEach(cb=> cb.checked=false); 
    renderFilteredMatrix();
  });

  // Initialize context
  if(window.AppSelection){ 
    applyContext(); 
  } else { 
    window.addEventListener('app-selection-ready', ()=>applyContext(), {once:true}); 
  }
  validateEnableRun();
});
