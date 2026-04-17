// Post Edit V2 page logic
// Auto-population and form submission handled by shared/layout_form.js

window.FormConfig = async function() {
    const selection = window.AppSelection ? window.AppSelection.get() : {project: '', subproject: ''};
    const basePath = (await (await fetch('/api/config/base-path')).json()).base_path || '';

    const processDir = `${basePath}/${selection.project}/${selection.subproject}/design/timing/quality/1_postedit`;
    const scriptName = 'run_post_edit.csh';

    return {
        output_dir: processDir,
        script_name: scriptName,
        executionDir: processDir,
        command: `${processDir}/${scriptName}`,
        cell_root: processDir
    };
};

// Hide/show fields by name based on tab selection
function setFieldVisibility(fieldNames, visible) {
    fieldNames.forEach(name => {
        // Find wrapper by data-field-name (single field)
        const wrapper = document.querySelector(`[data-field-name="${name}"]`);
        if (wrapper) {
            wrapper.style.display = visible ? '' : 'none';
            return;
        }
        // Find wrapper by data-field-names (comma-separated for divide groups)
        const allWrappers = document.querySelectorAll('[data-field-names]');
        allWrappers.forEach(w => {
            const names = w.getAttribute('data-field-names').split(',');
            if (names.includes(name)) {
                w.style.display = visible ? '' : 'none';
            }
        });
    });
}

function setButtonVisibility(runSingle, runMulti) {
    const runBtn = document.getElementById('layoutFormRunBtn');
    const runMultiBtn = document.getElementById('layoutFormRunMultiBtn');
    if (runBtn) runBtn.style.display = runSingle ? '' : 'none';
    if (runMultiBtn) runMultiBtn.style.display = runMulti ? '' : 'none';
}

function setupPostEditTabs() {
    const tabs = document.querySelectorAll('input[name="postedit_tabs"]');
    const singleCellFields = ['cell', 'configfile'];
    const multipleCellsFields = ['cell_lst', 'configfile_multiple_cells'];

    function updateFieldsForTab(tabIndex) {
        if (tabIndex === 0) {
            // Single Cell tab - show single fields, hide multiple, show Run, hide Run multiple
            setFieldVisibility(singleCellFields, true);
            setFieldVisibility(multipleCellsFields, false);
            setButtonVisibility(true, false);
        } else {
            // Multiple Cells tab - show multiple fields, hide single, hide Run, show Run multiple
            setFieldVisibility(singleCellFields, false);
            setFieldVisibility(multipleCellsFields, true);
            setButtonVisibility(false, true);
        }
    }

    tabs.forEach((tab, index) => {
        tab.addEventListener('change', () => {
            if (tab.checked) updateFieldsForTab(index);
        });
    });

    // Initialize based on default checked tab
    tabs.forEach((tab, index) => {
        if (tab.checked) updateFieldsForTab(index);
    });
}

// Auto-fill the cell list path similar to project_release.js
document.addEventListener('DOMContentLoaded', () => {
    // Setup tab switching
    setupPostEditTabs();

    async function autoCreateCellList() {
        const curSel = window.AppSelection ? window.AppSelection.get() : { project: '', subproject: '' };
        if (!curSel.project || !curSel.subproject) return;
        try {
            const Dir = (await window.FormConfig()).executionDir;
            const cellInput = document.getElementById('cell_lst');
            if (cellInput && !cellInput.value) {
                const ps = await fetch(`/api/project-status?project=${encodeURIComponent(curSel.project)}&subproject=${encodeURIComponent(curSel.subproject)}&refresh=false`);
                const pdata = await ps.json();
                const cells = Array.isArray(pdata.data) ? pdata.data.map(c => c.ckt_macros).filter(Boolean) : [];
                const content = cells.length ? cells.join('\n') + '\n' : '';
                const r = await fetch('/api/files/create', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ dir: Dir, filename: 'dwc_cells.lst', content })
                });
                const j = await r.json();
                if (j.path) {
                    cellInput.value = j.path;
                    console.log('Cell list created:', j.path);
                }
            }
        } catch (e) {
            console.log('Cell list creation failed');
        }
    }

    autoCreateCellList();
    window.addEventListener('app-selection-ready', autoCreateCellList, { once: true });

    // Add an extra "Run multiple cells" button next to default Run
    try {
        const runBtn = document.getElementById('layoutFormRunBtn');
        if (runBtn && runBtn.parentElement) {
            const multiBtn = document.createElement('button');
            multiBtn.type = 'button';
            multiBtn.id = 'layoutFormRunMultiBtn';
            multiBtn.className = 'btn btn-secondary ml-2';
            multiBtn.textContent = 'Run multiple cells';

            runBtn.parentElement.appendChild(multiBtn);

            // Ensure initial button visibility is correct
            if (typeof setButtonVisibility === 'function') {
                // Default: Single tab is checked at load
                setButtonVisibility(true, false);
            }

            multiBtn.addEventListener('click', async () => {
                const cellListInput = document.getElementById('cell_lst');
                const cellListPath = cellListInput ? cellListInput.value : '';
                console.log('[post_edit_v2] Run multiple cells clicked; cell_lst=', cellListPath);
                                const statusEl = document.getElementById('layoutFormStatus');
                                if (!cellListPath) {
                                    if (statusEl) statusEl.textContent = '✗ Provide cell list path first';
                                    return;
                                }

                                // Read cell list file from backend
                                let cells = [];
                                try {
                                    const resp = await fetch('/api/files/read', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ path: cellListPath })});
                                    const data = await resp.json();
                                    const lines = (data.content || '').split(/\r?\n/).map(s => s.trim()).filter(Boolean);
                                    cells = lines;
                                } catch (e) {
                                    console.error('[post_edit_v2] Failed to read cell list:', e);
                                    if (statusEl) statusEl.textContent = '✗ Failed to read cell list';
                                    return;
                                }

                                if (cells.length === 0) {
                                    if (statusEl) statusEl.textContent = '✗ Cell list is empty';
                                    return;
                                }

                                // Gather shared form values
                                const getVal = (id) => { const el = document.getElementById(id); return el ? (el.type === 'checkbox' ? el.checked : el.value) : ''; };
                                // Check if optional field is enabled (via its _enabled checkbox)
                                const isFieldEnabled = (id) => {
                                    const enabledCb = document.getElementById(id + '_enabled');
                                    return enabledCb ? enabledCb.checked : true;
                                };
                                const selection = window.AppSelection ? window.AppSelection.get() : { project: '', subproject: '' };
                                const lib = getVal('lib');
                                // Respect optional toggles for plan/reference
                                const plan = isFieldEnabled('plan') ? getVal('plan') : '';
                                // reformat_mode values are "reformat pt" or "reformat sis", extract just "pt" or "sis"
                                // If the optional checkbox is unchecked, reformat should be empty (not sent)
                                let reformat = '';
                                if (isFieldEnabled('reformat_mode')) {
                                    const rawReformat = getVal('reformat_mode') || '';
                                    // Extract the actual mode: "reformat pt" -> "pt", "reformat sis" -> "sis"
                                    const match = rawReformat.match(/reformat\s+(\w+)/i);
                                    reformat = match ? match[1] : (rawReformat || 'pt');
                                }
                                console.log('[post_edit_v2] reformat_mode enabled:', isFieldEnabled('reformat_mode'), 'raw:', getVal('reformat_mode'), 'parsed:', reformat);
                                const ptver = getVal('pt');
                                const output = getVal('output') || '';
                                const reference = isFieldEnabled('reference') ? (getVal('reference') || '') : '';
                                const reorder = !!getVal('reorder');
                                const leakage = !!getVal('leakage');
                                const update = !!getVal('update');
                                console.log('[post_edit_v2] Checkboxes - reorder:', reorder, 'leakage:', leakage, 'update:', update);
                                const configRoot = getVal('configfile_multiple_cells') || getVal('configfile');

                                if (!selection.project || !selection.subproject) {
                                    if (statusEl) statusEl.textContent = '✗ Select project/subproject first';
                                    return;
                                }
                                // lib/plan may be optional depending on config/script; do not block

                                // Wire up Stop button
                                const stopBtnId = 'layoutFormExecution_StopBtn';
                                const stopBtn = document.getElementById(stopBtnId) || document.getElementById('stopScriptBtn'); // legacy fallback
                                let stopRequested = false;
                                let currentWS = null;
                                const onStopClick = () => {
                                    stopRequested = true;
                                    try { if (currentWS && currentWS.readyState === WebSocket.OPEN) currentWS.send(JSON.stringify({ action: 'stop' })); } catch (_) {}
                                };
                                if (stopBtn) {
                                    stopBtn.disabled = false;
                                    stopBtn.addEventListener('click', onStopClick, { once: false });
                                }

                                // Helper: run a single cell via WebSocket stream endpoint
                                const runOneCell = (cellName) => new Promise(async (resolve) => {
                                    if (stopRequested) { resolve({ success: false, stopped: true }); return; }
                                    const cfg = `${configRoot}/${cellName}/${cellName}.cfg`;
                                    const qs = new URLSearchParams({
                                        cell: cellName,
                                        configfile: cfg,
                                        pt: ptver,
                                    });
                                    // Only add reformat if enabled (checkbox checked)
                                    if (reformat) qs.append('reformat', reformat);
                                    if (lib) qs.append('lib', lib);
                                    if (isFieldEnabled('plan') && plan) qs.append('plan', plan);
                                    if (output) qs.append('output', output);
                                    if (isFieldEnabled('reference') && reference) qs.append('reference', reference);
                                    if (reorder) qs.append('reorder', 'true');
                                    if (leakage) qs.append('leakage', 'true');
                                    if (update) qs.append('update', 'true');

                                    const url = `${location.origin}/api/post-edit/${encodeURIComponent(selection.project)}/${encodeURIComponent(selection.subproject)}/run/ws?${qs.toString()}`;
                                    const ws = new WebSocket(url.replace('http', 'ws'));
                                    currentWS = ws;
                                    if (statusEl) statusEl.textContent = `Running ${cellName}...`;
                                    ws.onmessage = (ev) => {
                                        try {
                                            const msg = JSON.parse(ev.data);
                                            if (msg.stream === 'stdout') {
                                                // Append to console container if available
                                                const cont = document.getElementById('layoutFormExecution');
                                                if (cont) {
                                                    const pre = cont.querySelector('pre');
                                                    if (pre) pre.textContent += msg.data + '\n';
                                                }
                                            } else if (msg.event === 'end') {
                                                ws.close();
                                                resolve({ success: msg.return_code === 0 });
                                            } else if (msg.event === 'error') {
                                                ws.close();
                                                resolve({ success: false });
                                            }
                                        } catch (_) {}
                                    };
                                    ws.onerror = () => {
                                        resolve({ success: false });
                                    };
                                });

                                // Sequentially run all cells
                                let okCount = 0;
                                for (const c of cells) {
                                    if (stopRequested) break;
                                    const res = await runOneCell(c);
                                    okCount += res.success ? 1 : 0;
                                    if (stopRequested) break;
                                }
                                if (stopBtn) stopBtn.disabled = true;
                                if (statusEl) statusEl.textContent = stopRequested ? `⛔ Stopped. Completed: ${okCount}/${cells.length}` : `✓ Completed: ${okCount}/${cells.length} cells`;
            });
        }
    } catch (e) {
        console.warn('[post_edit_v2] Failed to add Run multiple cells button', e);
    }
});