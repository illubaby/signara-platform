// Project release page logic
// Auto-population and form submission handled by shared/layout_form.js

// Export configuration function that builds full paths for script generation and execution
window.FormConfig = async function() {
    const selection = window.AppSelection ? window.AppSelection.get() : {project: '', subproject: ''};
    const basePath = (await (await fetch('/api/config/base-path')).json()).base_path || '';
    
    const processDir = `${basePath}/${selection.project}/${selection.subproject}/design/timing/quality/seeding`;
    const scriptName = 'run_project_seeding.csh';
    
    return {
        output_dir: processDir,                  // Where to generate the script
        script_name: scriptName,                 // Script filename
        executionDir: processDir,                // Working directory for execution
        command: `${processDir}/${scriptName}`,  // FULL PATH to script for execution
        cell_root: processDir                    // Directory where symlinks will be created
    };
};

// Auto-fill default files for seeding: dwc_cells.lst and updated_files.lst
document.addEventListener('DOMContentLoaded', () => {
    // Handle ref field disable/enable based on mode selection
    const modeField = document.getElementById('mode');
    const refField = document.getElementById('ref');
    
    function updateRefFieldState() {
        if (modeField && refField) {
            const shouldDisableRef = modeField.value === 'pcs' || modeField.value === 'upload';
            refField.disabled = shouldDisableRef;
            if (shouldDisableRef) {
                refField.value = ''; // Clear the value when disabled
            }
        }
    }
    
    // Initialize on page load
    if (modeField) {
        updateRefFieldState();
        modeField.addEventListener('change', updateRefFieldState);
    }
    
    async function autoCreateDefaults() {
        const curSel = window.AppSelection ? window.AppSelection.get() : { project: '', subproject: '' };
        if (!curSel.project || !curSel.subproject) return; // wait until selection ready
        try {
            const Dir = (await window.FormConfig()).executionDir;

            // 1) dwc_cells.lst -> populate from project-status cells
            const cellsInput = document.getElementById('cell_list');
            if (cellsInput && !cellsInput.value) {
                try {
                    const ps = await fetch(`/api/project-status?project=${encodeURIComponent(curSel.project)}&subproject=${encodeURIComponent(curSel.subproject)}&refresh=false`);
                    const pdata = await ps.json();
                    const cells = Array.isArray(pdata.data) ? pdata.data.map(c => c.ckt_macros).filter(Boolean) : [];
                    const content = cells.length ? cells.join('\n') + '\n' : '';
                    const r = await fetch('/api/files/create', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ dir: Dir, filename: 'dwc_cells.lst', content }) });
                    const j = await r.json();
                    if (j.path) cellsInput.value = j.path;
                } catch (e) {
                    console.error('[project_seeding] Failed creating dwc_cells.lst', e);
                }
            }

            // 2) updated_files.lst -> create empty file if not set
            const updatedInput = document.getElementById('updated_files');
            if (updatedInput && !updatedInput.value) {
                try {
                    const r2 = await fetch('/api/files/create', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ dir: Dir, filename: 'updated_files.lst', content: '' }) });
                    const j2 = await r2.json();
                    if (j2.path) updatedInput.value = j2.path;
                } catch (e) {
                    console.error('[project_seeding] Failed creating updated_files.lst', e);
                }
            }
        } catch (e) {
            console.error('[project_seeding] Auto-create defaults failed', e);
        }
    }

    // Try immediately and once when selection is ready
    autoCreateDefaults();
    window.addEventListener('app-selection-ready', autoCreateDefaults, { once: true });
});
