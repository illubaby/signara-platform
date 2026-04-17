// Timing SAF: Simulation Multiple Cells
(function(global){
  const openBtn = document.getElementById('multiSimBtn');
  const modal = document.getElementById('multiSimModal');
  const cellsList = document.getElementById('multiSimCellsList');
  const searchInput = document.getElementById('multiSimSearch');
  const runBtn = document.getElementById('multiSimRunBtn');
  const sisDirInput = document.getElementById('multiSimSisDir');
  if(!openBtn || !modal){ return; }

  let allCells = [];

  function getSelection(){
    return global.SAFSharedHttp ? global.SAFSharedHttp.getSelection() : (global.AppSelection ? global.AppSelection.get() : {project:'', subproject:''});
  }

  async function fetchBasePath(){
    try {
      const res = await fetch('/api/config/base-path');
      if(res.ok){ const data = await res.json(); return data.base_path; }
    } catch(_){}
    return '';
  }

  async function prefillSisDir(){
    const sel = getSelection();
    const base = await fetchBasePath();
    if(sel.project && sel.subproject && base){
      // Heuristic default; user can edit
      sisDirInput.value = `${base}/${sel.project}/${sel.subproject}/design/timing/sis`;
    }
  }

  function populateCells(){
    try {
      const state = global.__TimingSAFState && global.__TimingSAFState.getAll ? global.__TimingSAFState.getAll() : [];
      allCells = state.map(c => c.cell);
    } catch(_) { allCells = []; }
    if(allCells.length === 0){
      cellsList.innerHTML = '<div class="text-center py-4 opacity-70">No cells available</div>';
      return;
    }
    cellsList.innerHTML = allCells.map(name => (
      `<label class='flex items-center gap-2 p-2 hover:bg-base-300 rounded cursor-pointer'>
        <input type='checkbox' class='checkbox checkbox-xs multi-sim-cell' data-cell='${name}'>
        <span class='flex-1 font-mono text-sm'>${name}</span>
      </label>`
    )).join('');
  }

  function filterCells(q){
    const labels = cellsList.querySelectorAll('label');
    const needle = (q||'').toLowerCase();
    labels.forEach(label => {
      const nameEl = label.querySelector('span.flex-1');
      const name = (nameEl && nameEl.textContent) ? nameEl.textContent.toLowerCase() : '';
      const match = name.includes(needle);
      label.classList.toggle('hidden', !match);
    });
  }

  function openModal(){
    populateCells();
    prefillSisDir();
    modal.showModal();
  }

  function buildCommand(sisDir, selected){
    const scripts = selected.map(c => `${c}.csh`).join(' ');
    // Wrap in parentheses per user: ( cd <sis_dir> && bin/python/runningman.py -y -s <cells...> )
    return `( cd ${sisDir} && bin/python/runningman.py -y -s ${scripts} )`;
  }

  function run(){
    const sisDir = (sisDirInput.value||'').trim();
    if(!sisDir){ alert('Please set SiS directory.'); return; }
    const boxes = Array.from(cellsList.querySelectorAll('.multi-sim-cell'));
    const selected = boxes.filter(cb => cb.checked).map(cb => cb.getAttribute('data-cell'));
    if(selected.length === 0){ alert('Please select at least one cell.'); return; }
    const cmd = buildCommand(sisDir, selected) + "\n";
    if(global.ConsolePanel){
      global.ConsolePanel.open();
      global.ConsolePanel.sendInput(cmd);
    } else {
      alert('Console panel not available.');
    }
    modal.close();
  }

  openBtn.addEventListener('click', openModal);
  if(searchInput) searchInput.addEventListener('input', (e)=>filterCells(e.target.value));
  if(runBtn) runBtn.addEventListener('click', run);
})(window);
