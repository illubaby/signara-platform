// Timing QA v2 page logic (mirrors wrap_up.js pattern)
// Auto-population and form submission handled by shared/layout_form.js
// Toggle functionality for check_groups is provided by shared/layout_form.js

window.FormConfig = async function() {
    const selection = window.AppSelection ? window.AppSelection.get() : {project: '', subproject: ''};
    const basePath = (await (await fetch('/api/config/base-path')).json()).base_path || '';

    // Directory structure analogous to wrapup but for qa_v2
    const processDir = `${basePath}/${selection.project}/${selection.subproject}/design/timing/release/process`;
    const scriptName = 'run_timing_qa.csh';

    return {
        output_dir: processDir,
        script_name: scriptName,
        executionDir: processDir,
        command: `${processDir}/${scriptName}`,
        cell_root: processDir
    };
};

// Set default value for -outdir using Release_<prj>_<rel>_<Mon>_<YYYY>
document.addEventListener('DOMContentLoaded', () => {
  const sel = window.AppSelection ? window.AppSelection.get() : { project: '', subproject: '' };
  // Set outdir default
  const outdir = document.getElementById('outdir');
  if (outdir && sel.project && sel.subproject) {
    const now = new Date();
    const month = now.toLocaleString('en-US', { month: 'short' });
    outdir.value = `Release_${sel.project}_${sel.subproject}_${month}_${now.getFullYear()}`;
  }

  // Apply query-string overrides (used by SAF page to pre-fill paths)
  const params = new URLSearchParams(window.location.search);
  const presetData = params.get('data');
  if (presetData) {
    const dataInput = document.getElementById('data');
    if (dataInput && !dataInput.value) {
      dataInput.value = presetData;
    }
  }

  // Auto-create celllist/header if empty
  (async () => {
    if (!sel.project || !sel.subproject) return;
    try {
      const cfg = await window.FormConfig();
      const runDir = cfg.executionDir;
      const qaDir = runDir;
      const cellInput = document.getElementById('celllist');
      const headerInput = document.getElementById('header');
      // Only create if input exists and currently empty
      if (cellInput && !cellInput.value) {
        // Get cells from project status
        const ps = await fetch(`/api/project-status?project=${encodeURIComponent(sel.project)}&subproject=${encodeURIComponent(sel.subproject)}&refresh=false`);
        const pdata = await ps.json();
        const cells = Array.isArray(pdata.data) ? pdata.data.map(c => c.ckt_macros).filter(Boolean) : [];
        const content = cells.length ? cells.join('\n') + '\n' : '';
        const r = await fetch('/api/files/create', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({dir: qaDir, filename: 'dwc_cells.lst', content})});
        const j = await r.json();
        if (j.path) cellInput.value = j.path;
      }
      if (headerInput && !headerInput.value) {
        const r2 = await fetch('/api/files/create', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({dir: qaDir, filename: 'header_dummy.txt'})});
        const j2 = await r2.json();
        if (j2.path) headerInput.value = j2.path;
      }
    } catch (e) {
      console.error('Auto-create defaults failed', e);
    }
  })();
});

// Minimal matrix loader using existing QA matrix-summary API
let qaV2Data = null; // cache last-loaded matrix for filtering
async function qaV2LoadMatrix() {
  const meta = document.getElementById('qaV2MatrixMeta');
  const table = document.getElementById('qaV2MatrixTable');
  const filters = document.getElementById('qaV2MatrixFilters');
  const cellFilters = document.getElementById('qaV2CellFilters');
  const checkFiltersLeft = document.getElementById('qaV2CheckFiltersLeft');
  const checkFiltersRight = document.getElementById('qaV2CheckFiltersRight');
  const sel = window.AppSelection ? window.AppSelection.get() : {project:'', subproject:''};
  if(!(sel.project && sel.subproject)) { meta.textContent = 'Select project/subproject first'; return; }
  try {
    const cfg = await window.FormConfig();
    const runDir = cfg.executionDir;
    meta.textContent = 'Loading...';
    const tbody = table.querySelector('tbody');
    tbody.innerHTML = '<tr><td class="text-center opacity-60"><span class="loading loading-spinner loading-xs"></span> Loading...</td></tr>';
    const res = await fetch(`/api/qa/${encodeURIComponent(sel.project)}/${encodeURIComponent(sel.subproject)}/matrix-summary?run_dir=${encodeURIComponent(runDir)}`);
    if(!res.ok){ throw new Error(await res.text()); }
    const data = await res.json();
    if(!data.cell_names || !data.cell_names.length) {
      tbody.innerHTML = '<tr><td class="text-center italic opacity-60">No cells with brief.sum</td></tr>';
      meta.textContent = data.note || 'No data';
      return;
    }
    // cache dataset for filter operations
    qaV2Data = data;
    // Populate filters (button will be added later by qaV2UpdateCellCountsDisplay)
    cellFilters.innerHTML = data.cell_names.map((cell, idx) => 
      `<label class='flex items-center gap-1 cursor-pointer hover:bg-base-200 px-1 py-0.5 rounded text-sm'>
        <input type='checkbox' value='${idx}' class='checkbox checkbox-sm qaV2-cell-filter' checked>
        <span class='truncate' title='${cell}'>${cell}</span>
      </label>`
    ).join('');
    // Split check filters into two columns for readability
    const half = Math.ceil((data.check_items || []).length / 2);
    const leftHtml = data.check_items.slice(0, half).map((check, idx) => 
      `<label class='flex items-center gap-1 cursor-pointer hover:bg-base-200 px-1 py-0.5 rounded text-sm'>
        <input type='checkbox' value='${idx}' class='checkbox checkbox-sm qaV2-check-filter' checked>
        <span class='truncate' title='${check}'>${check}</span>
      </label>`
    ).join('');
    const rightHtml = data.check_items.slice(half).map((check, i2) => {
      const idx = half + i2;
      return `<label class='flex items-center gap-1 cursor-pointer hover:bg-base-200 px-1 py-0.5 rounded text-sm'>
        <input type='checkbox' value='${idx}' class='checkbox checkbox-sm qaV2-check-filter' checked>
        <span class='truncate' title='${check}'>${check}</span>
      </label>`;
    }).join('');
    checkFiltersLeft.innerHTML = leftHtml;
    checkFiltersRight.innerHTML = rightHtml;
    document.querySelectorAll('.qaV2-cell-filter, .qaV2-check-filter').forEach(cb => {
      cb.addEventListener('change', ()=> {
        qaV2RenderFilteredMatrix(qaV2Data);
        qaV2UpdateCellCountsDisplay(qaV2Data);
      });
    });
    filters.classList.remove('hidden');
    // Render simple transposed view: rows=cells, cols=checks
    qaV2RenderFilteredMatrix(qaV2Data);
    qaV2UpdateCellCountsDisplay(qaV2Data);
    meta.textContent = data.note || `${data.cell_names.length} cells × ${data.check_items.length} checks`;
  } catch(e) {
    const tbody = document.getElementById('qaV2MatrixTable').querySelector('tbody');
    tbody.innerHTML = `<tr><td class='text-error text-xs text-center'>Error: ${String(e)}</td></tr>`;
    document.getElementById('qaV2MatrixMeta').textContent = 'Error loading matrix';
  }
}

function qaV2RenderFilteredMatrix(data){
  const table = document.getElementById('qaV2MatrixTable');
  const thead = table.querySelector('thead tr');
  const tbody = table.querySelector('tbody');
  const selectedCellIdx = [...document.querySelectorAll('.qaV2-cell-filter:checked')].map(cb=>parseInt(cb.value));
  const selectedCheckIdx = [...document.querySelectorAll('.qaV2-check-filter:checked')].map(cb=>parseInt(cb.value));
  if(selectedCellIdx.length===0 || selectedCheckIdx.length===0){
    thead.innerHTML = '<th>Cell</th>';
    tbody.innerHTML = '<tr><td class="text-center italic opacity-60 py-4">Select at least one cell and one check item</td></tr>';
    return;
  }
  thead.innerHTML = '<th>Cell</th>' + selectedCheckIdx.map(i=>`<th class="text-sm">${data.check_items[i]}</th>`).join('');
  tbody.innerHTML = selectedCellIdx.map(cIdx=>{
    const cellName = data.cell_names[cIdx];
    const cols = selectedCheckIdx.map(kIdx=>{
      const status = (data.status_matrix?.[kIdx]?.[cIdx]) || '';
      const s = (status||'').toLowerCase();
      let cls = 'badge-ghost';
      if(s==='pass') cls='badge-success';
      else if(s==='fail') cls='badge-error';
      else if(s==='warning') cls='badge-warning';
      else if(s==='waived') cls='badge-info';
      return `<td class="text-center text-sm"><span class="badge badge-sm ${cls}">${status||'-'}</span></td>`;
    }).join('');
    return `<tr><th class="text-sm font-normal">${cellName}</th>${cols}</tr>`;
  }).join('');
}

// Compute and display per-cell counts (Pass/Warning/Fail) under current check filters
function qaV2UpdateCellCountsDisplay(data){
  const cellFilters = document.querySelectorAll('#qaV2CellFilters label');
  if(!data || !cellFilters || cellFilters.length===0) return;
  const selectedCheckIdx = [...document.querySelectorAll('.qaV2-check-filter:checked')].map(cb=>parseInt(cb.value));
  // For each cell, count statuses across selected checks
  cellFilters.forEach(label => {
    const cb = label.querySelector('input.qaV2-cell-filter');
    const nameSpan = label.querySelector('span');
    if(!cb || !nameSpan) return;
    const cIdx = parseInt(cb.value);
    let p=0,w=0,f=0,u=0;
    selectedCheckIdx.forEach(kIdx=>{
      const status = (data.status_matrix?.[kIdx]?.[cIdx]) || '';
      const s = (status||'').toLowerCase();
      if(s==='pass') p++;
      else if(s==='warning') w++;
      else if(s==='fail') f++;
      else if(s==='unknown' || s==='' || s==='-') u++;
      else u++;
    });
    const cellName = data.cell_names[cIdx] || '';
    // Build badges aligned to right inside label
    // Ensure label has a flex layout: name on left, badges on right
    nameSpan.textContent = cellName;
    let badges = label.querySelector('.qaV2-count-badges');
    if(!badges){
      badges = document.createElement('span');
      badges.className = 'qaV2-count-badges ml-auto flex items-center gap-1';
      label.appendChild(badges);
    }
    // Colorize only when count > 0; otherwise use ghost (no color)
    const passCls = p > 0 ? 'badge-success' : 'badge-ghost';
    const warnCls = w > 0 ? 'badge-warning' : 'badge-ghost';
    const failCls = f > 0 ? 'badge-error' : 'badge-ghost';
    const unkCls  = u > 0 ? 'badge-info' : 'badge-ghost';
    badges.innerHTML = `
      <span class="badge ${passCls} badge-xs">P:${p}</span>
      <span class="badge ${warnCls} badge-xs">W:${w}</span>
      <span class="badge ${failCls} badge-xs">F:${f}</span>
      <span class="badge ${unkCls} badge-xs">U:${u}</span>
    `;
    // Add Open Report buttons after badges
    let reportBtn = label.querySelector('.qaV2-open-report-btn');
    if(!reportBtn){
      reportBtn = document.createElement('button');
      reportBtn.className = 'btn btn-ghost btn-xs qaV2-open-report-btn';
      reportBtn.setAttribute('data-cell', cellName);
      reportBtn.title = 'Open TMQA Report (.xlsx)';
      reportBtn.innerHTML = `
        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
        </svg>
      `;
      reportBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        const cell = reportBtn.getAttribute('data-cell');
        const sel = window.AppSelection ? window.AppSelection.get() : {project:'', subproject:''};
        if(cell && window.QAV2ReportOpener && window.QAV2ReportOpener.open){
          window.QAV2ReportOpener.open(sel.project, sel.subproject, cell);
        } else {
          console.error('[TMQA v2] QAV2ReportOpener module not loaded or cell missing');
        }
      });
      label.appendChild(reportBtn);
    }
    // Add HTML Report button
    let htmlBtn = label.querySelector('.qaV2-open-html-btn');
    if(!htmlBtn){
      htmlBtn = document.createElement('button');
      htmlBtn.className = 'btn btn-ghost btn-xs qaV2-open-html-btn';
      htmlBtn.setAttribute('data-cell', cellName);
      htmlBtn.title = 'Open HTML Summary Report';
      htmlBtn.innerHTML = `
        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
        </svg>
      `;
      htmlBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        const cell = htmlBtn.getAttribute('data-cell');
        const sel = window.AppSelection ? window.AppSelection.get() : {project:'', subproject:''};
        if(cell && window.QAV2ReportOpener && window.QAV2ReportOpener.openHtml){
          window.QAV2ReportOpener.openHtml(sel.project, sel.subproject, cell);
        } else {
          console.error('[TMQA v2] QAV2ReportOpener.openHtml not loaded or cell missing');
        }
      });
      label.appendChild(htmlBtn);
    }
  });
}

// Filter control buttons
document.addEventListener('DOMContentLoaded', ()=>{
  const allCellsBtn = document.getElementById('qaV2SelectAllCellsBtn');
  const clrCellsBtn = document.getElementById('qaV2ClearAllCellsBtn');
  const allChecksBtn = document.getElementById('qaV2SelectAllChecksBtn');
  const clrChecksBtn = document.getElementById('qaV2ClearAllChecksBtn');
  if(allCellsBtn) allCellsBtn.addEventListener('click', ()=>{ 
      document.querySelectorAll('.qaV2-cell-filter').forEach(cb=> cb.checked=true);
      if(qaV2Data){
        qaV2RenderFilteredMatrix(qaV2Data);
        qaV2UpdateCellCountsDisplay(qaV2Data);
      }
  });
  if(clrCellsBtn) clrCellsBtn.addEventListener('click', ()=>{ 
      document.querySelectorAll('.qaV2-cell-filter').forEach(cb=> cb.checked=false);
      if(qaV2Data){
        qaV2RenderFilteredMatrix(qaV2Data);
        qaV2UpdateCellCountsDisplay(qaV2Data);
      }
  });
  if(allChecksBtn) allChecksBtn.addEventListener('click', ()=>{ 
    document.querySelectorAll('.qaV2-check-filter').forEach(cb=> cb.checked=true);
    if(qaV2Data){
      qaV2RenderFilteredMatrix(qaV2Data);
      qaV2UpdateCellCountsDisplay(qaV2Data);
    }
  });
  if(clrChecksBtn) clrChecksBtn.addEventListener('click', ()=>{ 
    document.querySelectorAll('.qaV2-check-filter').forEach(cb=> cb.checked=false);
    if(qaV2Data){
      qaV2RenderFilteredMatrix(qaV2Data);
      qaV2UpdateCellCountsDisplay(qaV2Data);
    }
  });
});

// Wire button
document.addEventListener('DOMContentLoaded', ()=>{
  const btn = document.getElementById('qaV2LoadMatrixBtn');
  if(btn) btn.addEventListener('click', qaV2LoadMatrix);
});