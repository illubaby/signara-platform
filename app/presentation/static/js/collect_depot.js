// Project release page logic
// Auto-population and form submission handled by shared/layout_form.js

// Cache-busting sanity check:
// Change this value, refresh the page (no hard refresh), and confirm the new value prints in DevTools.
// const COLLECT_DEPOT_JS_VERSION = "2026-02-02-1";
// console.log("[collect_depot] loaded", { version: COLLECT_DEPOT_JS_VERSION, ts: new Date().toISOString() });

// Export configuration function that builds full paths for script generation and execution
window.FormConfig = async function() {
    const selection = window.AppSelection ? window.AppSelection.get() : {project: '', subproject: ''};
    const basePath = (await (await fetch('/api/config/base-path')).json()).base_path || '';
    
    const processDir = `${basePath}/${selection.project}/${selection.subproject}/design/timing/release/process`;
    const scriptName = 'run_collect_depot.csh';
    
    return {
        output_dir: processDir,                  // Where to generate the script
        script_name: scriptName,                 // Script filename
        executionDir: processDir,                // Working directory for execution
        command: `${processDir}/${scriptName}`,  // FULL PATH to script for execution
        cell_root: processDir                    // Directory where symlinks will be created
    };
};

document.addEventListener('DOMContentLoaded', () => {
  const sel = window.AppSelection ? window.AppSelection.get() : { project: '', subproject: '' };

  // Auto-create celllist/header if empty
  (async () => {
    if (!sel.project || !sel.subproject) return;
    try {
      const Dir = (await window.FormConfig()).executionDir;
      const cellInput = document.getElementById('cell');
      // Only create if input exists and currently empty
      if (cellInput && !cellInput.value) {
        // Get cells from project status
        const ps = await fetch(`/api/project-status?project=${encodeURIComponent(sel.project)}&subproject=${encodeURIComponent(sel.subproject)}&refresh=false`);
        const pdata = await ps.json();
        const cells = Array.isArray(pdata.data) ? pdata.data.map(c => c.ckt_macros).filter(Boolean) : [];
        const content = cells.length ? cells.join('\n') + '\n' : '';
        const r = await fetch('/api/files/create', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({dir: Dir, filename: 'dwc_cells.lst', content})});
        const j = await r.json();
        if (j.path) cellInput.value = j.path;
      }
    } catch (e) {
      console.error('Auto-create defaults failed', e);
    }
  })();
});