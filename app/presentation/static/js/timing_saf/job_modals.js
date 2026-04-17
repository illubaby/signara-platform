// Phase 3 extraction: job settings + NT settings + task queue + job execution
// 
// Uses ExecutionStreamFactory for simplified WebSocket streaming.
// Minimal config example (only what's required):
//   ExecutionStreamFactory.presets.saf({
//     project: 'myproject',
//     subproject: 'mysub', 
//     cell: 'mycell',
//     cellType: 'sis'
//   }).connect();
// 
// Callbacks (onStart, onComplete, onError) are optional - factory has smart defaults!
//
(function(global){
  'use strict';

  const state = {
    currentRunButton: null,
    currentRunCell: null,
    currentRunCellType: null,
    availablePVTs: [],
    jobSettings: {}
  };

  function sel(){
    return global.SAFSharedHttp ? global.SAFSharedHttp.getSelection() : (global.AppSelection ? global.AppSelection.get() : {project:'', subproject:''});
  }

  async function fetchJSON(url, opts){
    if(global.SAFSharedHttp){
      return global.SAFSharedHttp.fetchJSON(url, opts, {silent: false, errorPrefix: 'Job Settings'});
    }
    // Fallback
    const res = await fetch(url, opts);
    if(!res.ok){
      const txt = await res.text();
      throw new Error(txt||('HTTP '+res.status));
    }
    return res.json();
  }

  function ensureDialogs(){
    // Settings dialog
    if(!document.getElementById('settingsDialog')){
      const settingsDialog = document.createElement('dialog');
      settingsDialog.id = 'settingsDialog';
      settingsDialog.className = 'modal';
      settingsDialog.innerHTML = `
        <form method="dialog" class="modal-box w-11/12 max-w-4xl max-h-[90vh] overflow-y-auto" id="settingsForm">
          <h3 class="font-bold text-lg mb-2">SAF Settings <span class='font-mono text-sm' id='settingsCellName'></span></h3>
          <div class='flex flex-col gap-4'>
            <div class='border rounded-lg p-4 bg-base-200'>
              <h4 class='font-semibold mb-3'>Job Script Options</h4>
              <div class='grid grid-cols-2 gap-2 text-xs'>
                <label class='form-control'><span class='label-text'>HSPICE</span><input name='hspiceVersion' class='input input-sm input-bordered' value='2023.12-1' required /></label>
                <label class='form-control'><span class='label-text'>FINESIM</span><input name='finesimVersion' class='input input-sm input-bordered' value='2023.12-1' required /></label>
                <label class='form-control'><span class='label-text'>PRIMESIM</span><input name='primesimVersion' class='input input-sm input-bordered' value='2023.12-1' /></label>
                <label class='form-control'><span class='label-text'>SiliconSmart</span><input name='siliconsmartVersion' class='input input-sm input-bordered' value='2024.09-SP4' required /></label>
                <label class='form-control'><span class='label-text'>Queue</span><input name='queue' class='input input-sm input-bordered' value='normal' /></label>
                <label class='form-control'><span class='label-text'>Netlist Type</span><select name='netlistType' class='select select-sm select-bordered'><option value='lpe' selected>lpe</option><option value='nolpe'>nolpe</option></select></label>
              </div>
              <div class='mt-3 flex items-center gap-2'>
                <input type='checkbox' id='internalSafCheckbox' class='checkbox checkbox-sm' />
                <span class='label-text text-sm font-medium'>Internal SAF</span>
              </div>
              <div class='hidden'>
              </div>
              <div class='mt-3'>
                <div class='flex items-center justify-between mb-2'>
                  <span class='label-text font-semibold'>PVT Selection</span>
                  <div class='flex gap-1'>
                    <button type='button' id='pvtCheckAllBtn' class='btn btn-xs btn-outline'>Check All</button>
                    <button type='button' id='pvtUncheckAllBtn' class='btn btn-xs btn-outline'>Uncheck All</button>
                  </div>
                </div>
                <div id='pvtCheckboxContainer' class='border rounded p-2 bg-base-100 max-h-64 overflow-y-auto grid grid-cols-2 gap-1 text-[11px]'>
                  <div class='col-span-2 text-center py-2 opacity-70'>
                    <span class='loading loading-spinner loading-xs'></span> Loading PVTs...
                  </div>
                </div>
                <div class='text-[9px] opacity-70 mt-1'>Select PVTs to run.</div>
              </div>
            </div>
            <div class='collapse collapse-arrow border border-base-300 bg-base-200'>
              <input type='checkbox' id='taskQueueToggle'>
              <div class='collapse-title text-sm font-semibold'>Create Task Queue File (sis_task_queue.tcl)</div>
              <div class='collapse-content'>
                <div class='grid grid-cols-2 gap-2 text-xs mt-2'>
                  <label class='form-control'><span class='label-text'>normal_queue_no_prefix</span><input name='tq_normal_queue_no_prefix' class='input input-sm input-bordered' value='1'></label>
                  <label class='form-control'><span class='label-text'>job_scheduler</span><input name='tq_job_scheduler' class='input input-sm input-bordered' value='lsf'></label>
                  <label class='form-control'><span class='label-text'>run_list_maxsize</span><input name='tq_run_list_maxsize' class='input input-sm input-bordered' value='100'></label>
                  <label class='form-control'><span class='label-text'>simulator</span><select name='tq_simulator' class='select select-sm select-bordered'><option value='primesim' selected>primesim</option><option value='hspice'>hspice</option></select></label>
                  <label class='form-control col-span-2'><span class='label-text'>normal_queue</span><input name='tq_normal_queue' class='input input-sm input-bordered' value='-app normal -n 1 -M 100G -R "span[hosts=1] rusage[mem=10GB,scratch_free=15]"'></label>
                </div>
                <div class='mt-3 flex justify-end gap-2'>
                  <button type='button' class='btn btn-sm btn-primary' id='createTaskQueueBtn'>Create sis_task_queue.tcl</button>
                </div>
                <div id='tqStatusInSettings' class='mt-2 text-[10px] opacity-70'></div>
              </div>
            </div>
            <div class='collapse collapse-arrow border border-base-300 bg-base-200'>
              <input type='checkbox' id='monteCarloToggle'>
              <div class='collapse-title text-sm font-semibold'>Create Monte Carlo Settings (monte_carlo_settings.tcl)</div>
              <div class='collapse-content'>
                <div class='grid grid-cols-2 gap-2 text-xs mt-2'>
                  <label class='form-control'><span class='label-text'>statistical_montecarlo_sample_size</span><input name='tq_statistical_montecarlo_sample_size' class='input input-sm input-bordered' value='250'></label>
                  <label class='form-control'><span class='label-text'>netlist_max_sweeps</span><input name='tq_netlist_max_sweeps' class='input input-sm input-bordered' value='1000'></label>
                  <label class='form-control col-span-2'><span class='label-text'>statistical_simulation_points</span><input name='tq_statistical_simulation_points' class='input input-sm input-bordered' value='{1 3 5 7 9 11 13 15 17 19 21 23 25}'></label>
                </div>
                <div class='mt-3 flex justify-end gap-2'>
                  <button type='button' class='btn btn-sm btn-primary' id='createMonteCarloBtn'>Create monte_carlo_settings.tcl</button>
                </div>
                <div id='mcStatusInSettings' class='mt-2 text-[10px] opacity-70'></div>
              </div>
            </div>
          </div>
          <div class='mt-4 flex gap-2 justify-end'>
            <button type='button' class='btn btn-sm' id='settingsCancelBtn'>Cancel</button>
            <button type='submit' class='btn btn-sm btn-primary'>Run</button>
          </div>
          <div id='settingsResult' class='mt-2 text-[11px]'></div>
          <input type='hidden' name='cell' id='settingsCellHidden'>
        </form>
        <form method="dialog" class="modal-backdrop"><button>close</button></form>`;
      document.body.appendChild(settingsDialog);
    }
  }

  // NT-specific logic moved to SAFNtSettings module.

  async function loadAvailablePVTs(){
    const s = sel(); if(!s.project||!s.subproject) return [];
    const isInternal = document.getElementById('internalSafCheckbox')?.checked || false;
    const url = isInternal ? `/api/saf/${s.project}/${s.subproject}/pvts?internal=true` : `/api/saf/${s.project}/${s.subproject}/pvts`;
    try { const data = await fetchJSON(url); state.availablePVTs = data.pvts||[]; } catch{ state.availablePVTs=[]; }
    return state.availablePVTs;
  }

  function populatePVTCheckboxes(pvtStatuses){
    const pvts = state.availablePVTs; const container = document.getElementById('pvtCheckboxContainer');
    if(!pvts.length){ container.innerHTML = '<div class="col-span-2 text-center py-2 opacity-70">No PVTs found</div>'; return; }
    container.innerHTML = pvts.map(p=>{ const status = (pvtStatuses||{})[p]||'idle';
      let icon='', cls='', checked=false; if(status==='success'){icon='✓';cls='text-success';}
      else if(status==='fail'){icon='✗';cls='text-error';checked=true;} else if(status==='in_progress'){icon='⟳';cls='text-warning';checked=true;} else {icon='○';cls='opacity-60';checked=true;}
      return `<label class='flex items-start gap-1 cursor-pointer'>
        <input type='checkbox' value='${p}' class='checkbox checkbox-xs pvt-checkbox' ${checked?'checked':''}>
        <span class='leading-tight break-all flex-1'>${p}</span>
        <span class='${cls} font-semibold' title='Status: ${status}'>${icon}</span>
      </label>`; }).join('');
  }

  async function openSettingsDialog(cell){
    const s = sel(); if(!s.project||!s.subproject) return;
    document.getElementById('settingsCellName').textContent = cell;
    document.getElementById('settingsCellHidden').value = cell;
    document.getElementById('settingsResult').textContent='';
    document.getElementById('tqStatusInSettings').textContent='';
    document.getElementById('mcStatusInSettings').textContent='';
    const checkbox = document.getElementById('internalSafCheckbox');
    if(checkbox){ checkbox.addEventListener('change', async ()=> { await loadAvailablePVTs(); await openSettingsDialog(cell); }, {once: true}); }
    if(!state.availablePVTs.length){ await loadAvailablePVTs(); }
    let statuses={};
    try{ const d = await fetchJSON(`/api/saf/${s.project}/${s.subproject}/cells/${cell}/pvt-status`, {}, {silent: true}); statuses = d.statuses||{}; }catch{}
    populatePVTCheckboxes(statuses);
    try{
      const tq = await fetchJSON(`/api/saf/${s.project}/${s.subproject}/cells/${cell}/taskqueue`, {}, {silent: true});
      if(tq && tq.values){ 
        const form = document.getElementById('settingsForm');
        for(const [k,v] of Object.entries(tq.values)){ const el=form.querySelector(`[name="tq_${k}"]`); if(el) el.value=v; }
        
        // Update status displays for each file type
        const tqStatus = document.getElementById('tqStatusInSettings');
        const mcStatus = document.getElementById('mcStatusInSettings');
        
        if(tq.exists_task_queue){
          tqStatus.innerHTML = `<span class='text-success'>✓ File exists: sis_task_queue.tcl</span>`;
        }
        if(tq.exists_monte_carlo){
          mcStatus.innerHTML = `<span class='text-success'>✓ File exists: monte_carlo_settings.tcl</span>`;
        }
      }
    }catch{}
    document.getElementById('settingsDialog').showModal();
  }

  async function createTaskQueueFiles(){
    const s=sel(); const cell=document.getElementById('settingsCellHidden').value; if(!cell) return;
    const resultDiv=document.getElementById('tqStatusInSettings'); const btn=document.getElementById('createTaskQueueBtn');
    btn.disabled=true; resultDiv.innerHTML='<span class="loading loading-spinner loading-xs"></span> Creating sis_task_queue.tcl...';
    try{
      const payload={}; 
      ['normal_queue_no_prefix','job_scheduler','run_list_maxsize','normal_queue','simulator'].forEach(k=>{ 
        const el=document.querySelector(`[name="tq_${k}"]`); 
        if(el) payload[k]= el.value; 
      });
      // Set default monte carlo values but don't write the file
      payload.statistical_montecarlo_sample_size = '250';
      payload.netlist_max_sweeps = '1000';
      payload.statistical_simulation_points = '{1 3 5 7 9 11 13 15 17 19 21 23 25}';
      payload.write_monte_carlo = false;
      
      const res = await fetch(`/api/saf/${s.project}/${s.subproject}/cells/${cell}/taskqueue`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)});
      const txt = await res.text(); let data=null; try{data=JSON.parse(txt);}catch{}
      if(!res.ok){ resultDiv.innerHTML = `<div class='text-error'>Error: ${res.status} ${(data&&data.detail)?data.detail:txt}</div>`; return; }
      resultDiv.innerHTML = `<div class='text-success font-semibold'>✓ Created: sis_task_queue.tcl</div>`;
    }catch(err){ resultDiv.innerHTML = `<div class='text-error'>Exception: ${err}</div>`; } finally { btn.disabled=false; }
  }

  async function createMonteCarloFiles(){
    const s=sel(); const cell=document.getElementById('settingsCellHidden').value; if(!cell) return;
    const resultDiv=document.getElementById('mcStatusInSettings'); const btn=document.getElementById('createMonteCarloBtn');
    btn.disabled=true; resultDiv.innerHTML='<span class="loading loading-spinner loading-xs"></span> Creating monte_carlo_settings.tcl...';
    try{
      const payload={}; 
      // Get task queue base values (needed for API)
      ['normal_queue_no_prefix','job_scheduler','run_list_maxsize','normal_queue','simulator'].forEach(k=>{ 
        const el=document.querySelector(`[name="tq_${k}"]`); 
        if(el) payload[k]= el.value; 
      });
      // Get monte carlo specific values
      ['statistical_montecarlo_sample_size','netlist_max_sweeps','statistical_simulation_points'].forEach(k=>{ 
        const el=document.querySelector(`[name="tq_${k}"]`); 
        if(el) payload[k]= el.value; 
      });
      payload.write_monte_carlo = true;
      
      const res = await fetch(`/api/saf/${s.project}/${s.subproject}/cells/${cell}/taskqueue`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)});
      const txt = await res.text(); let data=null; try{data=JSON.parse(txt);}catch{}
      if(!res.ok){ resultDiv.innerHTML = `<div class='text-error'>Error: ${res.status} ${(data&&data.detail)?data.detail:txt}</div>`; return; }
      resultDiv.innerHTML = `<div class='text-success font-semibold'>✓ Created: monte_carlo_settings.tcl</div>`;
    }catch(err){ resultDiv.innerHTML = `<div class='text-error'>Exception: ${err}</div>`; } finally { btn.disabled=false; }
  }

  function onSettingsSubmit(e){
    e.preventDefault(); const fd=new FormData(e.target); const cell=fd.get('cell'); state.jobSettings = Object.fromEntries(fd.entries()); document.getElementById('settingsDialog').close();
    if(state.currentRunButton && state.currentRunCell===cell){ runJobForCell(cell,'sis',state.currentRunButton); }
  }

  // Current WebSocket stream instance
  let currentStream = null;

  async function runJobForCell(cell, cellType, btnElement){
    const s=sel(); 
    if(!s.project||!s.subproject) return;

    // Acquire raw libs input element once (used for both SIS and NT paths).
    // Previously caused ReferenceError because rawLibInput variable was referenced without declaration.
    const rawLibInput = document.getElementById('rawLibsPathInput');
    
    // Get DOM elements
    const execGroup=document.getElementById('executionOutputGroup');
    const infoStatus=document.getElementById('infoStatus');
    const scriptStream=document.getElementById('scriptStream');
    
    // Show modal and prepare UI
    execGroup.classList.remove('hidden');
    document.getElementById('executionOutputModal').showModal();
    infoStatus.innerHTML='<span class="loading loading-spinner loading-xs"></span> Generating script...';
    scriptStream.textContent='';
    
    const origText=btnElement.textContent;
    btnElement.disabled=true;
    btnElement.innerHTML="<span class='loading loading-spinner loading-xs'></span>";
    
    try{
      // Prepare create body based on cell type
      let createBody=null;
      if(cellType==='nt'){
        const nt = global.SAFNtSettings ? global.SAFNtSettings.getCellSettings(cell) : { option:null, selectedPVTs:[] };
        const pvts = global.SAFNtSettings ? global.SAFNtSettings.getAvailablePvts(cell) : [];
        const bsubArgsVal = global.SAFNtSettings ? global.SAFNtSettings.getBsubArgs() : '';
        const rawLibPathsVal = rawLibInput? rawLibInput.value.trim() : '';
        // Conditions for including raw_lib_paths:
        // 1. Merge always appends when path present (existing behavior)
        // 2. Munge appends only if there is at least one PVT AND all PVT names have no underscore
        const allNoUnderscore = pvts.length>0 && pvts.every(p=>!p.includes('_'));
        const includeOutput = (nt.option === '--merge') || (nt.option === '--munge' && allNoUnderscore);
        createBody={
          nt_option: nt.option||'',
            selected_pvts: (nt.selectedPVTs&&nt.selectedPVTs.length)? nt.selectedPVTs : null,
          raw_lib_paths: (includeOutput && rawLibPathsVal.length)? rawLibPathsVal : null,
          bsub_args: bsubArgsVal && bsubArgsVal.length ? bsubArgsVal : undefined
        };
      } else {
        const selectedPVTs=[...document.querySelectorAll('#pvtCheckboxContainer .pvt-checkbox:checked')].map(cb=>cb.value);
        const sjs=state.jobSettings||{};
        const rawLibPathsVal=rawLibInput? rawLibInput.value.trim():'';
        const isInternal = document.getElementById('internalSafCheckbox')?.checked || false;
        createBody={
          hspiceVersion:sjs.hspiceVersion||'2023.12-1',
          finesimVersion:sjs.finesimVersion||'2023.12-1',
          primesimVersion:sjs.primesimVersion||'2023.12-1',
          siliconsmartVersion:sjs.siliconsmartVersion||'2024.09-SP4',
          queue:sjs.queue||'normal',
          netlistType:sjs.netlistType||'lpe',
          raw_lib_paths: rawLibPathsVal.length? rawLibPathsVal : null,
          selected_pvts: selectedPVTs.length? selectedPVTs : null,
          internal_saf: isInternal
        };
      }
      
      // Create script
      const apiUrl=`/api/saf/${s.project}/${s.subproject}/cells/${cell}/job?cell_type=${cellType}`;
      const createRes=await fetch(apiUrl,{method:'POST',headers:{'Content-Type':'application/json'}, body: JSON.stringify(createBody)});
      const createTxt=await createRes.text();
      let createData=null;
      try{createData=JSON.parse(createTxt);}catch{}
      
      if(!createRes.ok){
        infoStatus.innerHTML=`<span class='text-error'>Error creating script: ${createRes.status}</span>`;
        scriptStream.innerHTML = (createData&&createData.detail)? escapeHtml(JSON.stringify(createData.detail)) : escapeHtml(createTxt);
        btnElement.disabled=false;
        btnElement.textContent=origText;
        return;
      }
      
      // Update execution info
      if(createData.script_path){
        infoScriptPath.textContent=createData.script_path;
        const ls=Math.max(createData.script_path.lastIndexOf('/'),createData.script_path.lastIndexOf('\\'));
        infoWorkingDir.textContent= ls>0? createData.script_path.substring(0,ls): createData.script_path;
      }
      
      infoStatus.innerHTML='<span class="loading loading-spinner loading-xs"></span> Script generated. Connecting...';
      
      // Close any existing stream
      if(currentStream){
        currentStream.close();
      }
      
      // Build WebSocket URL for SAF execution
      const protocol = location.protocol === 'https:' ? 'wss' : 'ws';
      const wsUrl = `${protocol}://${location.host}/api/saf/${s.project}/${s.subproject}/cells/${cell}/execute/ws?cell_type=${cellType}`;
      
      // Use ExecutionStreamFactory - handles ALL execution UI automatically!
      const streamController = global.ExecutionStreamFactory.create({
        executionDir: createData.script_path ? createData.script_path.substring(0, Math.max(createData.script_path.lastIndexOf('/'), createData.script_path.lastIndexOf('\\'))) : 'N/A',
        command: createData.script_path || 'N/A',
        containerId: 'executionOutputGroup',
        wsBaseUrl: wsUrl,
        
        // Only custom logic: button state + PVT refresh
        onComplete: () => {
          btnElement.disabled = false;
          btnElement.textContent = origText;
          currentStream = null;
          // Refresh PVT badges
          global.SAFPvtStatus?.refreshStatuses();
          // If NT cell run completed (e.g., Setup just generated pvt_corners.lst), reload cells to update nt_setup flag
          if(cellType === 'nt'){
            global.TimingSafCells?.reload();
          }
        },
        
        onError: () => {
          btnElement.disabled = false;
          btnElement.textContent = origText;
          currentStream = null;
        }
      });
      
      currentStream = streamController.stream;
      streamController.connect();
      
    }catch(err){
      infoStatus.innerHTML=`<span class='text-error'>${escapeHtml(err.toString())}</span>`;
      btnElement.disabled=false;
      btnElement.textContent=origText;
      if(stopBtn) stopBtn.disabled = true;
    }
  }

  function escapeHtml(s){ 
    return global.SAFSharedHttp ? global.SAFSharedHttp.escapeHtml(s) : ((s||'').replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]))); 
  }

  function wireHandlers(){
    document.getElementById('createTaskQueueBtn')?.addEventListener('click', createTaskQueueFiles);
    document.getElementById('createMonteCarloBtn')?.addEventListener('click', createMonteCarloFiles);
    document.getElementById('settingsCancelBtn')?.addEventListener('click', ()=> document.getElementById('settingsDialog').close());
    document.getElementById('settingsForm')?.addEventListener('submit', onSettingsSubmit);
    
    // Listen for NT settings completion events
    window.addEventListener('nt-cell-settings', (e)=>{
      if(e.detail && e.detail.cell === state.currentRunCell && state.currentRunCellType==='nt' && state.currentRunButton){
        // After dialog closes, trigger run
        runJobForCell(state.currentRunCell, 'nt', state.currentRunButton);
      }
    });
    // PVT check/uncheck all
    document.addEventListener('click', (e)=>{ if(e.target.id==='pvtCheckAllBtn'){ document.querySelectorAll('#pvtCheckboxContainer .pvt-checkbox').forEach(cb=>cb.checked=true); } else if(e.target.id==='pvtUncheckAllBtn'){ document.querySelectorAll('#pvtCheckboxContainer .pvt-checkbox').forEach(cb=>cb.checked=false); } });
  }

  function onRunButton(cell, cellType, button){
    state.currentRunButton=button; state.currentRunCell=cell; state.currentRunCellType=cellType;
    const s = sel();
    if(!s.project || !s.subproject){
      alert('Select a project & subproject first (top of page).');
      return;
    }
    if(!cell){ alert('Cell reference missing. Try reloading the page.'); return; }
  if(cellType==='nt'){ global.SAFNtSettings && global.SAFNtSettings.open(cell); } else { openSettingsDialog(cell); }
  }

  function init(){ ensureDialogs(); wireHandlers(); }

  global.SAFJobModals = { init, onRunButton };
})(window);
