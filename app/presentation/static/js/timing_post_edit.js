// Utilities
async function fetchJSON(url, opts){ const r = await fetch(url, opts); if(!r.ok) throw new Error(await r.text()); return r.json(); }
function escapeHTML(s){ return s.replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c])); }

const selState = ()=> window.AppSelection ? window.AppSelection.get() : {project:'', subproject:''};
// Dropdown removed; keep reference null and track available cells
const cellSelect = null;
let availableCells = [];
const cellManualInput = document.getElementById('cellManualInput');
const configEditor = document.getElementById('configEditor');
const saveConfigBtn = document.getElementById('saveConfigBtn');
const runBtn = document.getElementById('runBtn');
const runSelectedBtn = document.getElementById('runSelectedBtn');
const metricsBody = document.getElementById('metricsBody');
const cellsOverviewModal = document.getElementById('cellsOverviewModal');
const showCellsOverviewBtn = document.getElementById('showCellsOverviewBtn');
// Cached absolute quality base directory (from defaults endpoint)
let postEditQualityBaseDir = null;

async function loadCells(){
  const sel = selState();
  if(!(sel.project && sel.subproject)) return;
  try {
    const data = await fetchJSON(`/api/post-edit/${sel.project}/${sel.subproject}/cells`);
    const existing = data.cells.filter(c=>c.exists);
    availableCells = existing.map(c=>c.cell);
    if(!availableCells.length){ runBtn.disabled = true; return; }
    // Auto-fill manual input with first cell if empty
    if(cellManualInput && !cellManualInput.value.trim()){
      cellManualInput.value = availableCells[0];
      cellManualInput.dataset.autofill = '1'; // mark as auto-filled so defaults can still load
    }
    runBtn.disabled = false;
    applyDefaultsForCell();
    loadMetrics();
  } catch(e){ console.error(e); }
}

function applyContext(){
  const sel = selState();
  if(!(sel.project && sel.subproject)) return;
  loadCells();
}

function _joinPath(dir, sub){ if(!dir) return ''; if(dir.endsWith('/')||dir.endsWith('\\')) return dir+sub; return dir+"/"+sub; }

function _currentConfigFile(){
  // Now returns the full path to the .cfg file directly
  return document.getElementById('configfileInput').value.trim();
}

async function applyDefaultsForCell(){
  const sel = selState();
  if(!(sel.project && sel.subproject)) return;
  const manualCell = cellManualInput ? cellManualInput.value.trim() : '';
  const cell = manualCell || availableCells[0] || '';
  // Fetch & apply defaults if manual cell is empty OR was auto-filled (autofill flag still '1')
  const shouldFetchDefaults = (!manualCell) || (cellManualInput && cellManualInput.dataset.autofill === '1');
  if(shouldFetchDefaults){
    try {
      const defs = await fetchJSON(`/api/post-edit/${sel.project}/${sel.subproject}/defaults?cell=${encodeURIComponent(cell)}`);
      // Cache full quality base path for execution dir display
      if(defs && defs.base_dir){ postEditQualityBaseDir = defs.base_dir; }
      const configInput = document.getElementById('configfileInput');
      if(!configInput.value || configInput.dataset.autofill==='1'){
        // Now points directly to the .cfg file instead of SiS root
        configInput.value = defs.config_file || defs.config_dir; configInput.dataset.autofill='1';
        configInput.scrollLeft = configInput.scrollWidth;
      }
      const libInput = document.getElementById('libInput');
      if(!libInput.value || libInput.dataset.autofill==='1'){
        libInput.value = defs.lib_path; libInput.dataset.autofill='1';
        libInput.scrollLeft = libInput.scrollWidth;
      }
      const outputInput = document.getElementById('outputInput');
      if(!outputInput.value || outputInput.dataset.autofill==='1'){
        outputInput.value = defs.output_path; outputInput.dataset.autofill='1';
        outputInput.scrollLeft = outputInput.scrollWidth;
      }
    } catch(e){ console.warn('Defaults fetch failed', e); }
  }
  updateComputedCfgPath();
  autoPlanFromCell();
  fetchExistingConfig();
  loadMetrics();
}

function autoPlanFromCell(){
  const manualCell = cellManualInput ? cellManualInput.value.trim() : '';
  const cell = manualCell || availableCells[0] || '';
  const planInput = document.getElementById('planInput');
  if(/ucie2phy/.test(cell)) planInput.value = '//wwcad/msip/projects/ucie/tb/gr_ucie2_v2/design/timing/plan/uciephy_constraint.xlsx';
  else if(/ucie3phy/.test(cell)) planInput.value = '//wwcad/msip/projects/ucie/tb/gr_ucie3_v1/design/timing/plan/uciephy_constraint.xlsx';
  else if(/uciephy/.test(cell)) planInput.value = '//wwcad/msip/projects/ucie/tb/gr_ucie/design/timing/plan/uciephy_constraint.xlsx';
  else planInput.value = '//wwcad/msip/projects/ucie/tb/gr_ucie2_v2/design/timing/plan/uciephy_constraint.xlsx';
}

function updateComputedCfgPath(){
  const p = _currentConfigFile();
  document.getElementById('computedCfgPath').textContent = p || '(none)';
}

async function fetchExistingConfig(){
  const path = _currentConfigFile();
  if(!path){ configEditor.value=''; saveConfigBtn.disabled = true; updateComputedCfgPath(); return; }
  try {
    const cfg = await fetchJSON(`/api/post-edit/config?path=${encodeURIComponent(path)}`);
    configEditor.value = cfg.content;
    saveConfigBtn.disabled = true;
  } catch(e){ /* silent if missing */ }
}

// Removed legacy ansiToHtml + appendLog (streaming handled by WebSocketOutputStream)

function highlightSelectedRow(){
  const manualCell = cellManualInput ? cellManualInput.value.trim() : '';
  const cell = manualCell || availableCells[0] || '';
  metricsBody.querySelectorAll('tr[data-cell]').forEach(r=>{
    const isMatch = r.getAttribute('data-cell')===cell;
    if(isMatch){
      // Use a dim background to indicate selection clearly
      r.classList.add('bg-base-300');
    } else {
      r.classList.remove('bg-base-300');
    }
  });
}

async function loadMetrics(){
  const sel = selState();
  if(!(sel.project && sel.subproject)) return;
  const libFolder = document.getElementById('libInput').value.trim();
  try {
    const data = await fetchJSON(`/api/post-edit/${sel.project}/${sel.subproject}/metrics?lib_path=${encodeURIComponent(libFolder)}`);
    if(!data.cells.length){ metricsBody.innerHTML = '<tr><td colspan="5" class="text-center italic opacity-60">No cells</td></tr>'; return; }
    metricsBody.innerHTML = data.cells.map(m=>{
      const badge = m.complete ? '<span class=\"badge badge-success badge-xs\">Complete</span>' : '<span class=\"badge badge-neutral badge-xs\">Pending</span>';
      return `<tr data-cell='${m.cell}'>
        <td class='text-center'><input type='checkbox' class='checkbox checkbox-xs sel-toggle'></td>
        <td><button type='button' class='link link-primary cell-link' data-cell='${m.cell}'>${m.cell}</button></td>
        <!-- Temporarily disabled metrics columns
        <td class='text-right'>${m.aLibs_count}</td>
        <td class='text-right'>${m.updated_libs_count}</td>
        <td>${badge}</td>
        -->
      </tr>`;
    }).join('');
    metricsBody.querySelectorAll('.cell-link').forEach(el=> el.addEventListener('click', ev=>{
      const cell = ev.currentTarget.getAttribute('data-cell');
      if(cellManualInput){ cellManualInput.value = cell; }
      if(cellManualInput){ cellManualInput.dataset.autofill = '1'; }
      updateComputedCfgPath(); fetchExistingConfig(); applyDefaultsForCell(); highlightSelectedRow();
      // Close modal after selection
      if(cellsOverviewModal) cellsOverviewModal.close();
    }));
    metricsBody.querySelectorAll('.sel-toggle').forEach(cb=> cb.addEventListener('change', updateSelectedRunState));
    highlightSelectedRow();
    updateSelectedRunState();
  } catch(e){ metricsBody.innerHTML = `<tr><td colspan='5' class='text-error text-xs'>Metrics error: ${e}</td></tr>`; }
}

// ================= Streaming Execution (new approach) =================
let postEditQueue = [];
let postEditCurrentStream = null;

function _buildPostEditWsUrl(sel, payload){
  const protocol = location.protocol === 'https:' ? 'wss' : 'ws';
  const qp = new URLSearchParams({
    cell: payload.cell,
    configfile: payload.configfile,
    lib: payload.lib,
    plan: payload.plan,
    reformat: payload.reformat,
    pt: payload.pt,
  });
  if(payload.output) qp.set('output', payload.output);
  if(payload.reference) qp.set('reference', payload.reference);
  if(payload.copyReference) qp.set('copy_reference', 'true');
  if(payload.reorder) qp.set('reorder', 'true');
  if(payload.leakage) qp.set('leakage', 'true');
  if(payload.update) qp.set('update', 'true');
  return `${protocol}://${location.host}/api/post-edit/${sel.project}/${sel.subproject}/run/ws?${qp.toString()}`;
}

function _buildCommandString(payload){
  // Provide a user-visible summary including flags (informational only)
  const parts = ['csh runall.csh', `# cell=${payload.cell}`];
  parts.push(`reformat=${payload.reformat}`);
  if(payload.copyReference && payload.reference) parts.push('copy_reference=1');
  if(payload.reorder) parts.push('reorder=1');
  if(payload.leakage) parts.push('leakage=1');
  if(payload.update) parts.push('update=1');
  return parts.join(' ');
}

function _startStreamingCell(sel, payload, onDone){
  const wsUrl = _buildPostEditWsUrl(sel, payload);
  // Prefer absolute path from defaults cache; fallback to relative if not yet loaded
  const qualityDirDisplay = postEditQualityBaseDir || `${sel.project}/${sel.subproject}/design/timing/quality/1_postedit`;
  // Create stream
  postEditCurrentStream = ExecutionStreamFactory.create({
    executionDir: qualityDirDisplay,
    command: _buildCommandString(payload),
    containerId: 'executionOutputGroup',
    wsBaseUrl: wsUrl,
    shell: '/bin/csh',
    onStart: () => {
      runBtn.disabled = true;
    },
    onComplete: () => {
      runBtn.disabled = false;
      // Refresh metrics after each cell
      loadMetrics();
      if(typeof onDone === 'function') onDone();
    },
    onError: () => {
      runBtn.disabled = false;
      if(typeof onDone === 'function') onDone();
    }
  });
  postEditCurrentStream.runCommand();
}

function _dequeueAndRun(){
  if(!postEditQueue.length){ postEditCurrentStream = null; return; }
  const next = postEditQueue.shift();
  _startStreamingCell(next.sel, next.payload, _dequeueAndRun);
}

async function runCellsSequential(rows){
  const sel = selState();
  postEditQueue = [];
  
  // Fetch config file paths for each cell
  for(const r of rows) {
    const cell = r.getAttribute('data-cell');
    try {
      // Get the config file path for this cell from the API
      const defs = await fetchJSON(`/api/post-edit/${sel.project}/${sel.subproject}/defaults?cell=${encodeURIComponent(cell)}`);
      if(!defs.config_file){
        console.warn(`No config file found for cell: ${cell}`);
        continue;
      }
      
      const payload = {
        cell,
        configfile: defs.config_file,
        lib: document.getElementById('libInput').value.trim(),
        output: document.getElementById('outputInput').value.trim() || undefined,
        reference: document.getElementById('referenceInput').value.trim() || undefined,
        copyReference: document.getElementById('copyReferenceInput').checked,
        plan: document.getElementById('planInput').value.trim(),
        reformat: document.getElementById('reformatSelect').value,
        reorder: document.getElementById('reorderInput').checked,
        leakage: document.getElementById('leakageInput').checked,
        update: document.getElementById('updateInput').checked,
        pt: document.getElementById('ptInput').value.trim()
      };
      postEditQueue.push({sel, payload});
    } catch(e) {
      console.error(`Failed to get config for cell ${cell}:`, e);
    }
  }
  
  if(postEditQueue.length){ _dequeueAndRun(); }
}

function updateSelectedRunState(){
  const anyChecked = metricsBody.querySelector('.sel-toggle:checked');
  runSelectedBtn.disabled = !anyChecked;
}

function initFileBrowserHandlers(){
  document.getElementById('browseConfigBtn').addEventListener('click', ()=>{
    const sel = selState();
    if(!(sel.project && sel.subproject)){ alert('Select project first'); return; }
    window.FileBrowser.open({
      inputId: 'configfileInput',
      type: 'file',  // Changed from 'dir' to 'file' to browse for .cfg files
      project: sel.project,
      subproject: sel.subproject,
      initialPath: 'sis',
      callback: (path) => {
        document.getElementById('configfileInput').dataset.autofill = '0';
        updateComputedCfgPath();
        fetchExistingConfig();
        loadMetrics();
      }
    });
  });

  document.getElementById('browseLibBtn').addEventListener('click', ()=>{
    const sel = selState();
    if(!(sel.project && sel.subproject)){ alert('Select project first'); return; }
    window.FileBrowser.open({
      inputId: 'libInput',
      type: 'dir',
      project: sel.project,
      subproject: sel.subproject,
      initialPath: 'release',
      callback: (path) => {
        document.getElementById('libInput').dataset.autofill = '0';
        loadMetrics();
      }
    });
  });

  document.getElementById('browseRefBtn').addEventListener('click', ()=>{
    const sel = selState();
    if(!(sel.project && sel.subproject)){ alert('Select project first'); return; }
    window.FileBrowser.open({
      inputId: 'referenceInput',
      type: 'dir',
      project: sel.project,
      subproject: sel.subproject,
      initialPath: 'release',
      callback: (path) => {
        document.getElementById('referenceInput').dataset.autofill = '0';
      }
    });
  });

  document.getElementById('browseOutputBtn').addEventListener('click', ()=>{
    const sel = selState();
    if(!(sel.project && sel.subproject)){ alert('Select project first'); return; }
    window.FileBrowser.open({
      inputId: 'outputInput',
      type: 'dir',
      project: sel.project,
      subproject: sel.subproject,
      initialPath: 'release',
      callback: (path) => {
        document.getElementById('outputInput').dataset.autofill = '0';
      }
    });
  });
}

function initFormHandler(){
  document.getElementById('postEditForm').addEventListener('submit', (e)=>{
    e.preventDefault();
    const sel = selState();
    if(!(sel.project && sel.subproject)){ alert('Select project first'); return; }
    const fd = new FormData(e.target);
    const payload = {};
    fd.forEach((v,k)=>{ payload[k]=v; });
    // Override cell with manual input if provided
    const manualCell = cellManualInput ? cellManualInput.value.trim() : '';
    if(manualCell){ payload.cell = manualCell; }
    // Global configuration controls
    payload.copyReference = document.getElementById('copyReferenceInput').checked;
    payload.reorder = document.getElementById('reorderInput').checked;
    payload.leakage = document.getElementById('leakageInput').checked;
    payload.update = document.getElementById('updateInput').checked;
    payload.reformat = document.getElementById('reformatSelect').value || 'pt';
    // configfile now comes directly from the form field
    payload.output = document.getElementById('outputInput').value.trim() || undefined;
    if(!payload.cell){ payload.cell = availableCells[0] || ''; }
    if(!payload.cell){ alert('No cell specified.'); return; }
    if(!payload.configfile){ alert('Missing config file path.'); return; }
    _startStreamingCell(sel, payload, ()=>{});
  });
}

function initEmbeddedMode(){
  try {
    const qs = new URLSearchParams(window.location.search);
    const targetCell = qs.get('cell');
    if(!targetCell) return;
    let attempts = 0;
    const timer = setInterval(()=>{
      attempts++;
      if(availableCells.includes(targetCell)){
        if(cellManualInput){ cellManualInput.value = targetCell; cellManualInput.dataset.autofill='1'; }
        applyDefaultsForCell();
        clearInterval(timer);
        return;
      }
      if(attempts>30){ clearInterval(timer); }
    }, 200);
  } catch(_){}
}

// Initialize
document.addEventListener('DOMContentLoaded', ()=>{
  // Remember collapse state for Configuration
  const configCollapse = document.getElementById('configCollapse');
  const configStorageKey = 'timing_post_edit_config_collapsed';
  const configSavedState = localStorage.getItem(configStorageKey);
  if (configSavedState === 'open') {
    configCollapse.checked = true;
  }
  configCollapse.addEventListener('change', () => {
    localStorage.setItem(configStorageKey, configCollapse.checked ? 'open' : 'collapsed');
  });

  // Show cells overview modal button
  if(showCellsOverviewBtn && cellsOverviewModal){
    showCellsOverviewBtn.addEventListener('click', ()=>{
      cellsOverviewModal.showModal();
      loadMetrics(); // Refresh data when opening modal
    });
  }

  // Manual cell input drives selection (dropdown removed)
  if(cellManualInput){
    cellManualInput.addEventListener('input', ()=>{
      if(!cellManualInput.value.trim()){
        // Revert to first available cell defaults
        cellManualInput.dataset.autofill = '1';
        applyDefaultsForCell();
      } else {
        // User typed -> disable future default overwrites
        cellManualInput.dataset.autofill = '0';
        autoPlanFromCell();
        highlightSelectedRow();
      }
    });
  }
  document.getElementById('configfileInput').addEventListener('input', ()=>{ updateComputedCfgPath(); fetchExistingConfig(); loadMetrics(); });
  
  saveConfigBtn.addEventListener('click', async ()=>{
    const path = _currentConfigFile();
    if(!path){ alert('No config folder or cell selected'); return; }
    try {
      const res = await fetch('/api/post-edit/config', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({path, content: configEditor.value})});
      if(!res.ok){ throw new Error(await res.text()); }
      saveConfigBtn.classList.add('btn-success');
      setTimeout(()=>saveConfigBtn.classList.remove('btn-success'), 1500);
    } catch(e){ alert('Save failed: '+e); }
  });
  
  configEditor.addEventListener('input', ()=>{ saveConfigBtn.disabled = false; });
  
  runSelectedBtn.addEventListener('click', ()=>{
    const rows = Array.from(metricsBody.querySelectorAll('tr[data-cell]')).filter(r=> r.querySelector('.sel-toggle')?.checked);
  if(!rows.length){ console.warn('No cells selected.'); return; }
    runCellsSequential(rows);
  });
  
  initFormHandler();
  initFileBrowserHandlers();
  initEmbeddedMode();
  
  if(window.AppSelection){ applyContext(); } else { window.addEventListener('app-selection-ready', ()=>applyContext(), {once:true}); }
});
