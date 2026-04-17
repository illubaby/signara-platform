// Phase 6 extraction: NT-specific settings (dialog, PVT loading, quick actions, selection persistence)
(function(global){
  'use strict';

  const ntState = {
    cellSettings: {}, // cell -> { option, selectedPVTs }
    availablePvts: {}, // cell -> [pvts]
  };

  function sel(){ 
    return global.SAFSharedHttp ? global.SAFSharedHttp.getSelection() : (global.AppSelection ? global.AppSelection.get() : {project:'', subproject:''}); 
  }
  
  function escapeHtml(s){ 
    return global.SAFSharedHttp ? global.SAFSharedHttp.escapeHtml(s) : ((s||'').replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]))); 
  }

  async function fetchJSON(url){ 
    if(global.SAFSharedHttp){
      return global.SAFSharedHttp.fetchJSON(url, {}, {silent: false, errorPrefix: 'NT Settings'});
    }
    // Fallback
    const r=await fetch(url); 
    if(!r.ok) throw new Error(await r.text()); 
    return r.json(); 
  }

  function ensureDialog(){
    if(document.getElementById('ntSettingsDialog')) return;
    const dlg = document.createElement('dialog');
    dlg.id='ntSettingsDialog'; dlg.className='modal';
    // Prevent auto-focus on first input inside dialog
    dlg.setAttribute('tabindex','-1');
    dlg.innerHTML = `
      <form method="dialog" class="modal-box w-11/12 max-w-2xl max-h-[90vh] overflow-y-auto" id="ntSettingsForm">
        <h3 class="font-bold text-lg mb-2">NT Cell Run Options <span class='font-mono text-sm' id='ntCellName'></span></h3>
        <p class="text-sm opacity-70 mb-4">Choose quick actions or select PVTs to simulate.</p>
        <div class='flex flex-col gap-3'>
          <div class='border rounded-lg p-3 bg-base-200'>
            <h4 class='font-semibold mb-2 text-sm'>LSF bsub Arguments</h4>
            <label class='form-control'>
              <span class='label-text text-xs'>--bsub-args</span>
              <input type='text' id='ntBsubArgsInput' class='input input-sm input-bordered font-mono' placeholder="-app quick -n 1 -M 50G -R 'span[hosts=1] rusage[mem=5GB,scratch_free=5]'" value="-app quick -n 1 -M 50G -R 'span[hosts=1] rusage[mem=5GB,scratch_free=5]'" />
            </label>
            <p class='text-[10px] opacity-70 mt-1'>Overrides default LSF options for NT runs. Included in generated runall.csh.</p>
          </div>
          <div class='border rounded-lg p-3 bg-base-200'>
            <h4 class='font-semibold mb-2 text-sm'>Quick Actions</h4>
            <div class='grid grid-cols-2 gap-2'>
              <button type='button' class='btn btn-sm btn-outline justify-start' data-nt-option=''>Setup</button>
              <button type='button' class='btn btn-sm btn-outline justify-start' data-nt-option='--munge'>Munge</button>
              <button type='button' class='btn btn-sm btn-outline justify-start' data-nt-option='--merge'>Merge</button>
              <button type='button' class='btn btn-sm btn-outline justify-start' data-nt-option='--reload'>Reload</button>
            </div>
          </div>
          <div class='border rounded-lg p-3 bg-base-200'>
            <div class='flex items-center justify-between mb-2'>
              <h4 class='font-semibold text-sm'>Select PVTs to Simulate</h4>
              <div class='flex gap-1'>
                <button type='button' id='ntPvtCheckAllBtn' class='btn btn-xs btn-outline'>Check All</button>
                <button type='button' id='ntPvtUncheckAllBtn' class='btn btn-xs btn-outline'>Uncheck All</button>
              </div>
            </div>
            <div id='ntPvtCheckboxContainer' class='border rounded p-2 bg-base-100 max-h-64 overflow-y-auto grid grid-cols-2 gap-1 text-[11px]'>
              <div class='col-span-2 text-center py-2 opacity-70'><span class='loading loading-spinner loading-xs'></span> Loading PVTs...</div>
            </div>
            <div class='text-[9px] opacity-70 mt-1'>Select PVTs and click run to generate --sim list.</div>
            <div class='mt-2'>
              <button type='button' id='ntRunSelectedPvtsBtn' class='btn btn-sm btn-primary btn-block'>Run with Selected PVTs</button>
            </div>
          </div>
        </div>
        <div class='mt-4 flex gap-2 justify-end'>
          <button type='button' class='btn btn-sm btn-ghost' id='ntSettingsCancelBtn'>Cancel</button>
        </div>
        <input type='hidden' name='cell' id='ntCellHidden'>
      </form>
      <form method="dialog" class="modal-backdrop"><button>close</button></form>`;
    document.body.appendChild(dlg);
    wireDialogHandlers();
  }

  async function loadNtPvts(cell){
    const s=sel(); if(!s.project||!s.subproject) return;
    const container=document.getElementById('ntPvtCheckboxContainer');
    container.innerHTML = '<div class="col-span-2 text-center py-2 opacity-70"><span class="loading loading-spinner loading-xs"></span> Loading PVTs...</div>';
    try{
      // Fetch PVT list
      const data = await fetchJSON(`/api/saf/${s.project}/${s.subproject}/cells/${cell}/nt-pvts`);
      const pvts = data.pvts||[]; 
      ntState.availablePvts[cell]=pvts;
      
      if(!pvts.length){ 
        container.innerHTML = '<div class="col-span-2 text-center py-3 bg-info/10 rounded border border-info/30"><div class="text-info font-semibold mb-1">⚠ No PVTs found</div><div class="text-xs opacity-80">Please run <strong>Setup</strong> first to generate pvt_corners.lst</div></div>'; 
        return; 
      }
      
      // Check if any PVT contains underscore to enable/disable merge button
      const hasPvtWithUnderscore = pvts.some(p => p.includes('_'));
      updateMergeButtonState(hasPvtWithUnderscore);
      
      // Fetch PVT statuses
      let pvtStatuses = {};
      try {
        console.log(`[NT Settings] Fetching PVT status for cell: ${cell}`);
        const statusData = await fetchJSON(`/api/saf/${s.project}/${s.subproject}/cells/${cell}/pvt-status?cell_type=nt`);
        pvtStatuses = statusData.statuses || {};
        console.log(`[NT Settings] PVT statuses loaded:`, pvtStatuses);
      } catch(err) {
        console.warn('[NT Settings] Failed to load NT PVT statuses:', err);
      }
      
      // Render checkboxes with status indicators
      container.innerHTML = pvts.map(p=>{
        const status = pvtStatuses[p] || 'idle';
        let icon='', cls='', checked=false;
        
        if(status==='success'){
          icon='✓'; cls='text-success';
        } else if(status==='fail'){
          icon='✗'; cls='text-error'; checked=true;
        } else if(status==='in_progress'){
          icon='⟳'; cls='text-warning'; checked=true;
        } else {
          icon='○'; cls='opacity-60'; checked=true;
        }
        
        return `<label class='flex items-start gap-1 cursor-pointer'>
          <input type='checkbox' value='${p}' class='checkbox checkbox-xs nt-pvt-checkbox' ${checked?'checked':''}>
          <span class='leading-tight break-all flex-1' title='${p}'>${p}</span>
          <span class='${cls} font-semibold' title='Simulation: ${status}'>${icon}</span>
        </label>`;
      }).join('');
    }catch(err){ 
      container.innerHTML = `<div class='col-span-2 text-center py-2 text-error'>Error: ${escapeHtml(err.message)}</div>`; 
    }
  }

  function open(cell){
    ensureDialog();
    document.getElementById('ntCellName').textContent=cell;
    document.getElementById('ntCellHidden').value=cell;
    loadNtPvts(cell);
    const dlg = document.getElementById('ntSettingsDialog');
    dlg.showModal();
    // Move focus away from inputs to avoid blinking cursor
    try { dlg.focus({ preventScroll: true }); } catch(e){}
    try { document.activeElement && document.activeElement.blur && document.activeElement.blur(); } catch(e){}
  }
  
  /**
   * Enable or disable the Merge button based on PVT names.
   * Merge is only available when PVT names contain underscores.
   */
  function updateMergeButtonState(hasPvtWithUnderscore){
    const mergeBtn = document.querySelector('#ntSettingsDialog [data-nt-option="--merge"]');
    if(!mergeBtn) return;
    
    if(!hasPvtWithUnderscore){
      // Disable merge button when PVTs don't have underscores
      mergeBtn.disabled = true;
      mergeBtn.classList.add('btn-disabled', 'opacity-40');
      mergeBtn.setAttribute('title', 'Merge is disabled: PVT names do not contain underscores');
      console.log('[NT Settings] Merge button disabled: No PVTs with underscores found');
    } else {
      // Enable merge button
      mergeBtn.disabled = false;
      mergeBtn.classList.remove('btn-disabled', 'opacity-40');
      mergeBtn.setAttribute('title', 'Merge PVT results');
      console.log('[NT Settings] Merge button enabled: PVTs with underscores found');
    }
  }

  /**
   * Enhance: visually mark Setup quick action as completed (green outline + tick)
   * when pvt_corners.lst already exists for this NT cell (nt_setup_complete flag).
   * The cells table row has data-nt-setup='1' when complete.
   */
  function updateSetupButtonState(cell){
    // Find the corresponding row in cells table
    try {
      const row = document.querySelector(`#cellsTable tr[data-cell="${CSS.escape ? CSS.escape(cell) : cell}"]`);
      const setupComplete = row && row.getAttribute('data-nt-setup') === '1';
      const setupBtn = document.querySelector('#ntSettingsDialog [data-nt-option=""]');
      if(!setupBtn) return;
      if(setupComplete){
        // Apply completed styling similar to run button when all PVTs passed
        setupBtn.classList.add('btn-success','btn-outline','opacity-60');
        setupBtn.classList.remove('btn-ghost');
        if(!setupBtn.textContent.includes('✓')){
          setupBtn.textContent = 'Setup ✓';
        }
        setupBtn.setAttribute('title','Setup already completed (pvt_corners.lst exists). Click to re-run if needed.');
        setupBtn.dataset.setupComplete = '1';
      } else {
        // Revert to default state
        setupBtn.className = 'btn btn-sm btn-outline justify-start';
        setupBtn.textContent = 'Setup';
        setupBtn.removeAttribute('data-setup-complete');
        setupBtn.setAttribute('title','Generate pvt_corners.lst for this NT cell');
      }
    } catch(err){ /* silent */ }
  }

  /**
   * Visually mark Munge quick action as completed (green outline + tick)
   * when setupDir/munged_lib contains expected number of .lib files.
   * Row uses data-nt-munge='1' when complete.
   */
  function updateMungeButtonState(cell){
    try {
      const row = document.querySelector(`#cellsTable tr[data-cell="${CSS.escape ? CSS.escape(cell) : cell}"]`);
      const mungeComplete = row && row.getAttribute('data-nt-munge') === '1';
      const mungeBtn = document.querySelector('#ntSettingsDialog [data-nt-option="--munge"]');
      if(!mungeBtn) return;
      if(mungeComplete){
        mungeBtn.classList.add('btn-success','btn-outline','opacity-60');
        mungeBtn.classList.remove('btn-ghost');
        if(!mungeBtn.textContent.includes('✓')){
          mungeBtn.textContent = 'Munge ✓';
        }
        mungeBtn.setAttribute('title','Munge complete: munged_lib has 2x .lib files vs PVT count. Click to re-run if needed.');
        mungeBtn.dataset.mungeComplete = '1';
      } else {
        mungeBtn.className = 'btn btn-sm btn-outline justify-start';
        mungeBtn.textContent = 'Munge';
        mungeBtn.removeAttribute('data-munge-complete');
        mungeBtn.setAttribute('title','Run Munge to generate munged .lib files');
      }
    } catch(err){ /* silent */ }
  }

  /**
   * Visually mark Merge quick action as completed (green outline + tick)
   * when raw_lib/<cell> contains expected number of .lib files (2x unique PVT count).
   * Row uses data-nt-merge='1' when complete.
   */
  function updateMergeCompleteState(cell){
    try {
      const row = document.querySelector(`#cellsTable tr[data-cell="${CSS.escape ? CSS.escape(cell) : cell}"]`);
      const mergeComplete = row && row.getAttribute('data-nt-merge') === '1';
      const mergeBtn = document.querySelector('#ntSettingsDialog [data-nt-option="--merge"]');
      if(!mergeBtn) return;
      if(mergeComplete){
        mergeBtn.disabled = false; // ensure enabled to show state
        mergeBtn.classList.add('btn-success','btn-outline','opacity-60');
        mergeBtn.classList.remove('btn-ghost','btn-disabled','opacity-40');
        if(!mergeBtn.textContent.includes('✓')){
          mergeBtn.textContent = 'Merge ✓';
        }
        mergeBtn.setAttribute('title','Merge complete: raw_lib has 2x .lib files vs unique PVT count. Click to re-run if needed.');
        mergeBtn.dataset.mergeComplete = '1';
      } else {
        // Only revert visual success styling if previously marked complete
        if(mergeBtn.dataset.mergeComplete === '1'){
          mergeBtn.className = 'btn btn-sm btn-outline justify-start';
          mergeBtn.textContent = 'Merge';
          mergeBtn.removeAttribute('data-merge-complete');
          mergeBtn.removeAttribute('data-mergeComplete');
          mergeBtn.dataset.mergeComplete = '0';
        }
        // Leave enable/disable state managed by updateMergeButtonState(hasPvtWithUnderscore)
      }
    } catch(err){ /* silent */ }
  }

  function ntCheckAll(){ document.querySelectorAll('.nt-pvt-checkbox').forEach(cb=>cb.checked=true); }
  function ntUncheckAll(){ document.querySelectorAll('.nt-pvt-checkbox').forEach(cb=>cb.checked=false); }

  function collectSelected(){ return [...document.querySelectorAll('.nt-pvt-checkbox:checked')].map(cb=>cb.value); }

  function wireDialogHandlers(){
    document.getElementById('ntSettingsDialog').addEventListener('click', (e)=>{
      const btn=e.target.closest('[data-nt-option]'); if(!btn) return; const cell=document.getElementById('ntCellHidden').value; const opt=btn.getAttribute('data-nt-option'); ntState.cellSettings[cell]={ option:opt, selectedPVTs:[] }; document.getElementById('ntSettingsDialog').close(); notifyCellSettingsChanged(cell);
    });
    document.getElementById('ntPvtCheckAllBtn')?.addEventListener('click', ntCheckAll);
    document.getElementById('ntPvtUncheckAllBtn')?.addEventListener('click', ntUncheckAll);
    document.getElementById('ntRunSelectedPvtsBtn')?.addEventListener('click', ()=>{
      const cell=document.getElementById('ntCellHidden').value; const selected=collectSelected(); if(!selected.length){ alert('Select at least one PVT'); return; }
      ntState.cellSettings[cell]={ option:null, selectedPVTs:selected }; document.getElementById('ntSettingsDialog').close(); notifyCellSettingsChanged(cell);
    });
    document.getElementById('ntSettingsCancelBtn')?.addEventListener('click', ()=> document.getElementById('ntSettingsDialog').close());
  }

  // Notification so job_modals can react when user chooses settings.
  function notifyCellSettingsChanged(cell){
    const bsubInput = document.getElementById('ntBsubArgsInput');
    const bsubArgs = bsubInput ? bsubInput.value.trim() : '';
    const ev = new CustomEvent('nt-cell-settings', { detail:{ cell, settings: ntState.cellSettings[cell], bsub_args: bsubArgs }});
    window.dispatchEvent(ev);
  }

  function getCellSettings(cell){ return ntState.cellSettings[cell] || { option:null, selectedPVTs:[] }; }
  function getAvailablePvts(cell){ return ntState.availablePvts[cell] || []; }

  function init(){ ensureDialog(); }

  // Intercept open to update setup button state after dialog creation
  const originalOpen = open;
  open = function(cell){
    originalOpen(cell);
    updateSetupButtonState(cell);
    updateMungeButtonState(cell);
    updateMergeCompleteState(cell);
  };

  function getBsubArgs(){ const el=document.getElementById('ntBsubArgsInput'); return el? el.value.trim() : ''; }
  global.SAFNtSettings = { init, open, getCellSettings, getAvailablePvts, getBsubArgs };
  // Expose completion updater for potential external refresh hooks
  global.__NTMergeRefresh = updateMergeCompleteState;
})(window);
