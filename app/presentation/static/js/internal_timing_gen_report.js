// Project release page logic
// Auto-population and form submission handled by shared/layout_form.js

// Export configuration function that builds full paths for script generation and execution
window.FormConfig = async function() {
    const selection = window.AppSelection ? window.AppSelection.get() : {project: '', subproject: ''};
    const basePath = (await (await fetch('/api/config/base-path')).json()).base_path || '';
    
    // Get cell name from form input
    const cellInput = document.getElementById('cell');
    const cell = cellInput ? cellInput.value : '';
    
    const processDir = `${basePath}/${selection.project}/${selection.subproject}/design/timing/quality/7_internal/${cell}`;
    const scriptName = 'gen_internal_timing_report.csh';
    
    return {
        output_dir: processDir,                  // Where to generate the script
        script_name: scriptName,                 // Script filename
        executionDir: processDir,                // Working directory for execution
        command: `${processDir}/${scriptName}`,  // FULL PATH to script for execution
        cell_root: processDir                    // Directory where symlinks will be created
    };
};