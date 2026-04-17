// Package compare page logic
// Auto-population and form submission handled by shared/layout_form.js

// Export configuration function that builds full paths for script generation and execution
window.FormConfig = async function() {
    const selection = window.AppSelection ? window.AppSelection.get() : {project: '', subproject: ''};
    const basePath = (await (await fetch('/api/config/base-path')).json()).base_path || '';
    
    const processDir = `${basePath}/${selection.project}/${selection.subproject}/design/timing/quality/5_compare`;
    const scriptName = 'run_package_compare.csh';
    
    return {
        output_dir: processDir,                  // Where to generate the script
        script_name: scriptName,                 // Script filename
        executionDir: processDir,                // Working directory for execution
        command: `${processDir}/${scriptName}`,  // FULL PATH to script for execution
        cell_root: processDir                    // Directory where symlinks will be created
    };
};

// Render SUMMARY.txt using the reusable TableView module with real-time polling
(function() {
    async function initSummaryPolling() {
        // Wait for TableView to be available (with retry mechanism)
        let retries = 0;
        while (!window.TableView && retries < 50) {
            console.debug(`[PackageCompare] Waiting for TableView... (attempt ${retries + 1})`);
            await new Promise(resolve => setTimeout(resolve, 100));
            retries++;
        }

        if (!window.TableView) {
            console.error('[PackageCompare] TableView module not loaded after 5 seconds. Please check if table.js is loaded correctly.');
            console.error('[PackageCompare] Available on window:', Object.keys(window).filter(k => k.includes('Table')));
            return;
        }
        
        console.log('[PackageCompare] TableView loaded successfully');

        // Use the reusable polling method with custom column filter
        const pollingControl = window.TableView.renderWithPolling(
            async () => {
                const cfg = await window.FormConfig();
                return `${cfg.output_dir}/draftreport/SUMMARY.txt`;
            },
            {
                containerId: 'package-summary',
                title: 'Package Compare Summary',
                maxWidth: '80vw',
                startLine: 1,
                pollIntervalMs: 3000,
                columnFilter: (headers, rows) => {
                    // Remove columns 12 and 13 (0-based indices: 11 and 12)
                    const removeIdx = [11, 12];
                    return {
                        headers: headers.filter((_, idx) => !removeIdx.includes(idx)),
                        rows: rows.map(cols => cols.filter((_, idx) => !removeIdx.includes(idx)))
                    };
                },
                logPrefix: '[PackageCompare]'
            }
        );

        // Expose refresh function for external trigger (e.g., after script execution)
        window.refreshPackageCompareSummary = pollingControl.refresh;
        window.stopPackageComparePolling = pollingControl.stop;
    }

    // Initialize on page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initSummaryPolling);
    } else {
        initSummaryPolling();
    }
})();
