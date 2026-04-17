// Phase 4 extraction: Netlist sync & debug logic for Timing SAF page
// Responsibilities:
//  - Provide syncNetlist(cell, type, project, subproject, buttonEl)
//  - Attach delegated click handler for .netlist-sync spans if not already handled
//  - Centralize DOM updates for execution output modal
//  - (Future) expose debug fetch if UI adds a button
(function(global){
  'use strict';

  function escapeHtml(s){ 
    return global.SAFSharedHttp ? global.SAFSharedHttp.escapeHtml(s) : ((s||'').replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]))); 
  }

  async function syncNetlist(cell, cellType, project, subproject, btnElement){
    if(!project || !subproject){
      alert('Project or subproject not available');
      return;
    }
    const execGroup = document.getElementById('executionOutputGroup');
    const infoScriptPath = document.getElementById('infoScriptPath');
    const infoWorkingDir = document.getElementById('infoWorkingDir');
    const infoStatus = document.getElementById('infoStatus');
    const infoElapsed = document.getElementById('infoElapsed');
    const infoElapsedRow = document.getElementById('infoElapsedRow');
    const scriptStream = document.getElementById('scriptStream');
    const stopScriptBtn = document.getElementById('stopScriptBtn');
    const autoscrollScript = document.getElementById('autoscrollScript');

    execGroup && execGroup.classList.remove('hidden');
    const modal = document.getElementById('executionOutputModal');
    if(modal) modal.showModal();
    if(infoStatus) infoStatus.innerHTML = '<span class="loading loading-spinner loading-xs"></span> Syncing netlist from P4...';
    if(infoElapsedRow) infoElapsedRow.style.display = 'none';
    if(scriptStream) scriptStream.textContent = '';
    if(stopScriptBtn) stopScriptBtn.disabled = true;

    if(btnElement){ btnElement.disabled = true; btnElement.innerHTML = "<span class='loading loading-spinner loading-xs'></span>"; }
    const startTs = performance.now();

    const depotPath = cellType === 'nt'
      ? `//wwcad/msip/projects/ucie/${project}/${subproject}/design/timing/extr/${cell}/nt/etm/...`
      : `//wwcad/msip/projects/ucie/${project}/${subproject}/design/timing/extr/${cell}/sis/...`;

    if(infoScriptPath) infoScriptPath.textContent = `p4 sync -f ${depotPath}`;
    if(infoWorkingDir) infoWorkingDir.textContent = `${project}/${subproject}/design/timing/extr/${cell}`;

    try {
      const res = await fetch(`/api/saf/${project}/${subproject}/cells/${cell}/sync-netlist?cell_type=${cellType}`, { method: 'POST' });
      const txt = await res.text();
      let data = null; try { data = JSON.parse(txt); } catch(e) {}

      const elapsed = ((performance.now()-startTs)/1000).toFixed(1);
      if(infoElapsed) infoElapsed.textContent = `${elapsed}s`;
      if(infoElapsedRow) infoElapsedRow.style.display = 'flex';

      if(!res.ok){
        if(infoStatus) infoStatus.innerHTML = `<span class='text-error'>Sync failed: ${res.status}</span>`;
        if(scriptStream){
          if(data && data.detail){ scriptStream.innerHTML = escapeHtml(JSON.stringify(data.detail, null, 2)); }
          else { scriptStream.innerHTML = escapeHtml(txt); }
        }
        return;
      }

      const rc = data && data.return_code === null ? '?' : (data? data.return_code : '?');
      const ok = rc === 0;
      if(infoStatus) infoStatus.innerHTML = ok ? `<span class='text-success'>Completed (exit ${rc})</span>` : `<span class='text-error'>Failed (exit ${rc})</span>`;

      if(scriptStream && data){
        if(data.note){ scriptStream.innerHTML += '<span class="opacity-70">[NOTE]</span> ' + escapeHtml(data.note) + '\n'; }
        if(data.depot_path){ scriptStream.innerHTML += '<span class="opacity-70">[DEPOT PATH]</span> ' + escapeHtml(data.depot_path) + '\n'; }
        if(data.stdout){ scriptStream.innerHTML += '<span class="text-success">[STDOUT]</span>\n' + escapeHtml(data.stdout) + '\n'; }
        if(data.stderr){ scriptStream.innerHTML += '<span class="text-error">[STDERR]</span>\n' + escapeHtml(data.stderr) + '\n'; }
        if(autoscrollScript && autoscrollScript.checked){ scriptStream.scrollTop = scriptStream.scrollHeight; }
      }

      if(ok){
        // ask cells module to reload to refresh netlist version
        setTimeout(()=>{ global.TimingSafCells && global.TimingSafCells.reload({force:true}); }, 1000);
      }
    } catch(err){
      if(infoStatus) infoStatus.innerHTML = `<span class='text-error'>${escapeHtml(err.toString())}</span>`;
    } finally {
      if(btnElement){ btnElement.disabled = false; btnElement.textContent = 'Sync'; }
    }
  }

  function attachDelegatedHandler(){
    const tbody = document.querySelector('#cellsTable tbody');
    if(!tbody) return;
    // Avoid double-binding
    if(tbody.__netlistSyncBound) return; tbody.__netlistSyncBound = true;
    tbody.addEventListener('click', (e)=>{
      const el = e.target.closest('.netlist-sync');
      if(!el) return;
      e.stopPropagation();
      const cell = el.getAttribute('data-cell');
      const cellType = el.getAttribute('data-type') || 'sis';
      const row = el.closest('tr');
      const project = row ? row.getAttribute('data-project') : null;
      const subproject = row ? row.getAttribute('data-subproject') : null;
      const netlistText = el.textContent.trim();
      const isMissing = netlistText.toLowerCase() === 'missing';
      if(!isMissing && !confirm(`Sync latest netlist for "${cell}"?`)) return;
      syncNetlist(cell, cellType, project, subproject, el);
    });
  }

  function init(){ attachDelegatedHandler(); }

  global.SAFNetlistSync = { init, syncNetlist };
})(window);
