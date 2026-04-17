// Project release page logic
// Auto-population and form submission handled by shared/layout_form.js

// Export configuration function that builds full paths for script generation and execution
window.FormConfig = async function() {
    const selection = window.AppSelection ? window.AppSelection.get() : {project: '', subproject: ''};
    const basePath = (await (await fetch('/api/config/base-path')).json()).base_path || '';
    
    const processDir = `${basePath}/${selection.project}/${selection.subproject}/design/timing/release/process`;
    const scriptName = 'run_release.csh';
    
    return {
        output_dir: processDir,                  // Where to generate the script
        script_name: scriptName,                 // Script filename
        executionDir: processDir,                // Working directory for execution
        command: `${processDir}/${scriptName}`,  // FULL PATH to script for execution
        cell_root: processDir                    // Directory where symlinks will be created
    };
};
// Auto-fill the cell list path similar to project_release.js
document.addEventListener('DOMContentLoaded', () => {
  async function autoCreateCellList() {
    const curSel = window.AppSelection ? window.AppSelection.get() : { project: '', subproject: '' };
    if (!curSel.project || !curSel.subproject) return; // still not ready
    try {
      const Dir = (await window.FormConfig()).executionDir;
      const cellInput = document.getElementById('cell_lst');
      if (cellInput && !cellInput.value) {
        const ps = await fetch(`/api/project-status?project=${encodeURIComponent(curSel.project)}&subproject=${encodeURIComponent(curSel.subproject)}&refresh=false`);
        const pdata = await ps.json();
        const cells = Array.isArray(pdata.data) ? pdata.data.map(c => c.ckt_macros).filter(Boolean) : [];
        const content = cells.length ? cells.join('\n') + '\n' : '';
        const r = await fetch('/api/files/create', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({dir: Dir, filename: 'dwc_cells.lst', content})});
        const j = await r.json();
        if (j.path) cellInput.value = j.path;
      }
    } catch (e) {
      console.error('[project_release] Auto-create defaults failed', e);
    }
  }

  // Try immediately (in case selection already set)
  autoCreateCellList();
  // Also listen for selection-ready event
  window.addEventListener('app-selection-ready', autoCreateCellList, { once: true });
});

// Ensure the Release Note value is wrapped in single quotes for CLI safety
// Example: -note 'Example note'
document.addEventListener('DOMContentLoaded', () => {
  function wrapNoteWithQuotes() {
    const noteInput = document.getElementById('note') || document.querySelector('input[name="note"], textarea[name="note"]');
    if (!noteInput) return;
    const v = (noteInput.value || '').trim();
    if (!v) return;
    // If already quoted, leave as-is
    const alreadyQuoted = v.startsWith("'") && v.endsWith("'");
    if (!alreadyQuoted) {
      noteInput.value = `'${v}'`;
    }
  }

  // Run right before layout_form collects FormData
  // layout_form dispatches 'execution:start' at the top of its submit handler
  window.addEventListener('execution:start', wrapNoteWithQuotes);
});