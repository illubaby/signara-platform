// Special check page logic
// Auto-population and form submission handled by shared/layout_form.js

// Export configuration function that builds full paths for script generation and execution
window.FormConfig = async function() {
    const selection = window.AppSelection ? window.AppSelection.get() : {project: '', subproject: ''};
    const basePath = (await (await fetch('/api/config/base-path')).json()).base_path || '';
    
    const processDir = `${basePath}/${selection.project}/${selection.subproject}/design/timing/quality/6_specialcheck`;
    const scriptName = 'run_special_check.csh';
    
    return {
        output_dir: processDir,                  // Where to generate the script
        script_name: scriptName,                 // Script filename
        executionDir: processDir,                // Working directory for execution
        command: `${processDir}/${scriptName}`,  // FULL PATH to script for execution
        cell_root: processDir                    // Directory where symlinks will be created
    };
};

// Validate database path matches selected project and subproject
function setupDatabaseValidation() {
    const databaseInput = document.getElementById('database');
    if (!databaseInput) return;

    const selection = window.AppSelection ? window.AppSelection.get() : {project: '', subproject: ''};
    const selectedProject = (selection.project || '').toLowerCase().trim();
    const selectedSubproject = (selection.subproject || '').toLowerCase().trim();

    function validateDatabase() {
        const dbPath = databaseInput.value.trim();
        if (!dbPath || !selectedProject) return;

        // Extract project and subproject from path like: .../projects/ucie/h301-ucie3-s32-tsmc2p-075-ew/rel1.00/...
        const match = dbPath.match(/\/projects\/ucie\/([^\/]+)\/([^\/]+)/);
        if (match && match[1]) {
            const pathProject = match[1].toLowerCase();
            const pathSubproject = match[2] ? match[2].toLowerCase() : '';
            
            const projectMismatch = pathProject !== selectedProject;
            const subprojectMismatch = selectedSubproject && pathSubproject && pathSubproject !== selectedSubproject;
            
            if (projectMismatch || subprojectMismatch) {
                // Show warning - project or subproject don't match
                databaseInput.classList.add('input-error');
                let warningDiv = databaseInput.parentElement.querySelector('.database-warning');
                if (!warningDiv) {
                    warningDiv = document.createElement('div');
                    warningDiv.className = 'database-warning text-error text-sm mt-1';
                    databaseInput.parentElement.appendChild(warningDiv);
                }
                
                let warningMsg = '';
                if (projectMismatch && subprojectMismatch) {
                    warningMsg = `⚠️ Warning: Database path has project "${pathProject}" / subproject "${pathSubproject}" but selected is "${selectedProject}" / "${selectedSubproject}"`;
                } else if (projectMismatch) {
                    warningMsg = `⚠️ Warning: Database path contains project "${pathProject}" but selected project is "${selectedProject}"`;
                } else if (subprojectMismatch) {
                    warningMsg = `⚠️ Warning: Database path contains subproject "${pathSubproject}" but selected subproject is "${selectedSubproject}"`;
                }
                warningDiv.textContent = warningMsg;
            } else {
                // Remove warning - both match
                databaseInput.classList.remove('input-error');
                const warningDiv = databaseInput.parentElement.querySelector('.database-warning');
                if (warningDiv) warningDiv.remove();
            }
        }
    }

    // Validate on input change
    databaseInput.addEventListener('input', validateDatabase);
    databaseInput.addEventListener('blur', validateDatabase);
    
    // Initial validation if field already has value
    validateDatabase();
}


// Initialize validation on page load
(function() {
    function init() {
        setupDatabaseValidation();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();

// Render Summary.csv using the reusable TableView module with real-time polling
(function() {
    async function initSummaryPolling() {
        // Wait for TableView to be available (with retry mechanism)
        let retries = 0;
        while (!window.TableView && retries < 50) {
            console.debug(`[SpecialCheck] Waiting for TableView... (attempt ${retries + 1})`);
            await new Promise(resolve => setTimeout(resolve, 100));
            retries++;
        }

        if (!window.TableView) {
            console.error('[SpecialCheck] TableView module not loaded after 5 seconds. Please check if table.js is loaded correctly.');
            console.error('[SpecialCheck] Available on window:', Object.keys(window).filter(k => k.includes('Table')));
            return;
        }
        
        console.log('[SpecialCheck] TableView loaded successfully');

        // Use the reusable polling method with custom column filter
        const pollingControl = window.TableView.renderWithPolling(
            async () => {
                const cfg = await window.FormConfig();
                return `${cfg.output_dir}/Summary.csv`;
            },
            {
                containerId: 'special-check',
                title: 'Special Check Summary',
                maxWidth: '80vw',
                startLine: 6,
                pollIntervalMs: 3000,
                columnFilter: (headers, rows) => {
                    // Remove columns 12 and 13 (0-based indices: 11 and 12)
                    const removeIdx = [];
                    return {
                        headers: headers.filter((_, idx) => !removeIdx.includes(idx)),
                        rows: rows.map(cols => cols.filter((_, idx) => !removeIdx.includes(idx)))
                    };
                },
                logPrefix: '[SpecialCheck]'
            }
        );

        // Expose refresh function for external trigger (e.g., after script execution)
        window.refreshSpecialCheckSummary = pollingControl.refresh;
        window.stopSpecialCheckPolling = pollingControl.stop;
    }

    // Initialize on page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initSummaryPolling);
    } else {
        initSummaryPolling();
    }
})();