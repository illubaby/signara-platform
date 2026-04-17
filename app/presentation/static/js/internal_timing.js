// Internal Timing page logic
// Auto-population and form submission handled by shared/layout_form.js

// Export configuration function that builds full paths for script generation and execution
window.FormConfig = async function() {
    const selection = window.AppSelection ? window.AppSelection.get() : {project: '', subproject: ''};
    const basePath = (await (await fetch('/api/config/base-path')).json()).base_path || '';
    
    const processDir = `${basePath}/${selection.project}/${selection.subproject}/design/timing/nt`;
    const scriptName = 'run_int.csh';
    
    return {
        output_dir: processDir,                  // Where to generate the script
        script_name: scriptName,                 // Script filename
        executionDir: processDir,                // Working directory for execution
        command: `${processDir}/${scriptName}`,  // FULL PATH to script for execution
        cell_root: processDir                    // Directory where symlinks will be created
    };
};

// Populate block_path literal dropdown with INT cells
async function populateBlockPathFromIntCells() {
    try {
        const selection = window.AppSelection ? window.AppSelection.get() : {project: '', subproject: ''};
        const { project, subproject } = selection;
        if (!project || !subproject) {
            console.log('[InternalTiming] Skipped INT cells: missing project/subproject');
            return;
        }
        const url = `/api/saf/${project}/${subproject}/cells-int`;
        const resp = await fetch(url);
        if (!resp.ok) {
            console.log('[InternalTiming] INT cells fetch failed', resp.status, url);
            return;
        }
        const data = await resp.json();
        const cells = Array.isArray(data.cells) ? data.cells : [];

        // Find the block_path select rendered as a literal field
        const select = document.getElementById('block_path') || document.querySelector('select[name="block_path"]');
        if (!select) {
            console.log('[InternalTiming] block_path select not found');
            return;
        }

        // Try to read saved state directly to be robust to timing
        let savedValue = null;
        try {
            const form = document.querySelector('form[data-page-id]');
            const pageId = form ? form.getAttribute('data-page-id') || 'unknown' : 'unknown';
            const path = (window.location && window.location.pathname) ? window.location.pathname : 'unknown-path';
            const key = `layoutFormState:${pageId}:${path}`;
            const raw = localStorage.getItem(key);
            if (raw) {
                const state = JSON.parse(raw);
                if (state && typeof state === 'object') {
                    savedValue = state.block_path || null;
                }
            }
        } catch (_) {
            // ignore
        }
        const prevValue = savedValue || select.value;

        // Replace options with cells list
        select.innerHTML = cells.map(c => `<option value="${c}">${c}</option>`).join('');

        // Restore selection if possible; otherwise pick first
        if (prevValue && cells.includes(prevValue)) {
            select.value = prevValue;
        } else if (prevValue && !cells.includes(prevValue)) {
            // Add a fallback option for the saved value so it persists
            const opt = document.createElement('option');
            opt.value = prevValue;
            opt.textContent = prevValue;
            select.insertBefore(opt, select.firstChild);
            select.value = prevValue;
        } else if (cells.length > 0) {
            select.value = cells[0];
        }
    } catch (e) {
        console.log('[InternalTiming] INT cells error:', e);
    }
}

window.addEventListener('DOMContentLoaded', () => {
    // Delay to allow layout_form.js to restore saved form state first
    setTimeout(populateBlockPathFromIntCells, 100);
    setupIntCellPreparation();
    setupPhaseButtons();
});

// Ensure INT cell directory exists and is synced before running
function setupIntCellPreparation() {
    const attachPrepAndSubmit = async function(ev, form) {
        if (window.__intPrepBusy) return; // debounce concurrent clicks
        if (!form) return;
        const select = document.getElementById('block_path') || document.querySelector('select[name="block_path"]');
        const selection = window.AppSelection ? window.AppSelection.get() : {project: '', subproject: ''};
        const { project, subproject } = selection;
        if (!project || !subproject || !select || !select.value) {
            // Nothing to prepare; let default submit happen
            form && form.requestSubmit();
            return;
        }
        if (ev) ev.preventDefault(); // intercept click to run prep each time
        window.__intPrepBusy = true;
        const cellName = select.value.trim();
        const cellBase = cellName.endsWith('_int') ? cellName.slice(0, -4) : cellName;
        const statusEl = document.getElementById('layoutFormStatus');
        if (statusEl) statusEl.innerHTML = '<span class="loading loading-spinner loading-xs"></span> Preparing INT cell...';
        // Try: sync INT netlist via cell API before preparing
        // try {
        //     console.log('[InternalTiming] Sync INT netlist start', { project, subproject, cellBase });
        //     const nlResp = await fetch(`/api/cell/${project}/${subproject}/int/${cellBase}/sync-netlist`, { method: 'POST' });
        //     console.log('[InternalTiming] Sync INT netlist response', { status: nlResp.status });
        //     if (nlResp.ok) {
        //         const nl = await nlResp.json();
        //         console.log('[InternalTiming] Sync INT netlist result', nl);
        //         if (statusEl) statusEl.innerHTML = `<span class="text-info">Netlist: ${nl.synced ? 'synced' : 'not synced'}; </span>` + (statusEl.innerHTML || '');
        //     } else {
        //         const text = await nlResp.text().catch(() => '');
        //         console.warn('[InternalTiming] Netlist sync failed', { status: nlResp.status, body: text });
        //         if (statusEl) statusEl.innerHTML = '<span class="text-warning">Netlist sync failed; </span>' + (statusEl.innerHTML || '');
        //     }
        // } catch (err) {
        //     console.error('[InternalTiming] Netlist sync error', err);
        //     if (statusEl) statusEl.innerHTML = '<span class="text-warning">Netlist sync error; </span>' + (statusEl.innerHTML || '');
        // }
        // ensure NT share symlink exists (for tools expecting nt/share)
        try {
            const shareResp = await fetch(`/api/cell/${project}/${subproject}/nt/ensure-share`, { method: 'POST' });
            if (shareResp.ok) {
                const s = await shareResp.json();
                if (statusEl) statusEl.innerHTML = `<span class="text-info">Share: ${s.created ? 'linked' : 'exists'}; </span>` + (statusEl.innerHTML || '');
            } else {
                if (statusEl) statusEl.innerHTML = '<span class="text-warning">Share link failed; </span>' + (statusEl.innerHTML || '');
            }
        } catch (_) {
            if (statusEl) statusEl.innerHTML = '<span class="text-warning">Share link error; </span>' + (statusEl.innerHTML || '');
        }
        // Next: prepare/sync setup of the INT cell
        try {
            const resp = await fetch(`/api/cell/${project}/${subproject}/int/${cellBase}/prepare`, { method: 'POST' });
            if (resp.ok) {
                const data = await resp.json();
                if (statusEl) statusEl.innerHTML = `<span class="text-success">INT prep: ${data.created ? 'created' : 'exists'}, ${data.synced ? 'synced' : 'sync failed'}</span>`;
            } else {
                if (statusEl) statusEl.innerHTML = '<span class="text-error">INT prep failed</span>';
            }
        } catch (e) {
            if (statusEl) statusEl.innerHTML = '<span class="text-error">INT prep error</span>';
        }
        window.__intPrepBusy = false;
        // Trigger actual form submission now
        form.requestSubmit();
    };

    // Attach to Run button if present (legacy)
    const runBtn = document.getElementById('layoutFormRunBtn');
    if (runBtn) {
        const form = runBtn.closest('form');
        runBtn.addEventListener('click', function(ev) { attachPrepAndSubmit(ev, form); }, { capture: true });
    }

    // Expose for phase buttons
    window.__intAttachPrepAndSubmit = attachPrepAndSubmit;
}

// Replace Run with three phase buttons (Sim, Reload, Setup) and wire behavior
function setupPhaseButtons() {
    const runBtn = document.getElementById('layoutFormRunBtn');
    const form = document.querySelector('form[data-page-id]');
    const execContainer = document.getElementById('layoutFormExecution');
    if (!form || !execContainer) return;

    // Hide legacy Run button if present
    if (runBtn) {
        runBtn.style.display = 'none';
        runBtn.id = 'layoutFormRunBtnHidden';
    }

    // Insert phase button group above execution details
    const wrapper = document.createElement('div');
    wrapper.className = 'mt-6 flex justify-center gap-2';

    const mkBtn = (id, text, style) => {
        const b = document.createElement('button');
        b.type = 'button';
        b.id = id;
        b.className = `btn ${style}`;
        b.textContent = text;
        return b;
    };

    const setupBtn = mkBtn('intSetupBtn', 'Setup', 'btn-outline');
    const simBtn = mkBtn('intSimBtn', 'Sim', 'btn-outline');
    const reloadBtn = mkBtn('intReloadBtn', 'Reload', 'btn-outline');

    // Order: Setup, Sim, Reload
    wrapper.appendChild(setupBtn);
    wrapper.appendChild(simBtn);
    wrapper.appendChild(reloadBtn);

    // Place before execution output container
    execContainer.parentNode.insertBefore(wrapper, execContainer);

    // Helpers to set mutually exclusive phase fields
    const setPhase = (phase) => {
        const setupEl = form.querySelector('#setup');
        const reloadEl = form.querySelector('#reload');
        const simEl = form.querySelector('#sim');
        // Toggle checked states
        if (setupEl) setupEl.checked = (phase === 'setup'); else console.debug('[InternalTiming] setup field missing');
        if (reloadEl) reloadEl.checked = (phase === 'reload'); else console.debug('[InternalTiming] reload field missing');
        // sim is an optional string. Only include when phase === 'sim'. Otherwise leave its value intact.
        if (simEl) {
            if (phase === 'sim') {
                // If PVT panel is available, use its selected list
                if (typeof window.getSelectedPvtsString === 'function') {
                    const pvts = window.getSelectedPvtsString();
                    simEl.value = pvts || '';
                } else {
                    // fallback: keep current value or clear
                    simEl.value = simEl.value || '';
                }
                // If still empty, do not submit 'sim'
                if (!simEl.value || simEl.value.trim() === '') {
                    simEl.removeAttribute('name');
                }
            }
        }

        // Exclude non-selected phase fields from submission by removing name
        const ensureName = (el, name) => { if (el && !el.getAttribute('name')) el.setAttribute('name', name); };
        const removeName = (el) => { if (el && el.getAttribute('name')) el.removeAttribute('name'); };

        if (phase === 'setup') {
            ensureName(setupEl, 'setup');
            if (setupEl) setupEl.value = 'True';
            removeName(reloadEl);
            // keep sim included only if has value (handled below in submit)
            removeName(simEl); // prevent accidental -sim when not chosen
        } else if (phase === 'reload') {
            ensureName(reloadEl, 'reload');
            if (reloadEl) reloadEl.value = 'True';
            removeName(setupEl);
            removeName(simEl);
        } else if (phase === 'sim') {
            // sim only
            ensureName(simEl, 'sim');
            // Name already set above; value assigned once from getSelectedPvtsString()
            if (simEl && (!simEl.value || simEl.value.trim() === '')) removeName(simEl);
            removeName(setupEl);
            removeName(reloadEl);
        }
    };

    const handlePhaseClick = async (phase, ev) => {
        setPhase(phase);
        // run preparation + submit
        if (typeof window.__intAttachPrepAndSubmit === 'function') {
            await window.__intAttachPrepAndSubmit(ev, form);
        } else {
            form.requestSubmit();
        }
    };

    setupBtn.addEventListener('click', (ev) => handlePhaseClick('setup', ev));
    simBtn.addEventListener('click', (ev) => handlePhaseClick('sim', ev));
    reloadBtn.addEventListener('click', (ev) => handlePhaseClick('reload', ev));
}


