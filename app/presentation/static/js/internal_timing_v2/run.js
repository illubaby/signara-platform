// Internal Timing v2 run modal + execution
(function (global) {
  'use strict';

  const state = {
    currentCell: '',
    onComplete: null,
    pvts: [],
    currentLib2TclCell: ''
  };

  function sanitizeScriptPart(value) {
    return (value || '').replace(/[^A-Za-z0-9_\-.]/g, '_');
  }

  function getSelectedPvts() {
    return Array.from(document.querySelectorAll('#intV2PvtsContainer .int-v2-pvt-checkbox:checked')).map((cb) => cb.value);
  }

  function renderPvts(list) {
    const container = document.getElementById('intV2PvtsContainer');
    if (!container) return;
    if (!list.length) {
      container.innerHTML = '<div class="col-span-2 opacity-70 text-center py-2">Run setupstep to create pvt_corners.lst</div>';
      return;
    }
    container.innerHTML = list.map((pvt) => (
      `<label class="flex items-start gap-1 cursor-pointer"><input type="checkbox" class="checkbox checkbox-xs int-v2-pvt-checkbox" value="${pvt}"><span class="leading-tight break-all">${pvt}</span></label>`
    )).join('');
  }

  async function loadPvtsForCell(cell) {
    const api = global.InternalTimingV2API;
    const sel = api.selection();
    const container = document.getElementById('intV2PvtsContainer');
    if (!container) return;

    if (!sel.project || !sel.subproject || !cell) {
      container.innerHTML = '<div class="col-span-2 opacity-70 text-center py-2">Run setupstep to create pvt_corners.lst</div>';
      state.pvts = [];
      return;
    }

    const cellWithSuffix = cell.endsWith('_int') ? cell : `${cell}_int`;
    container.innerHTML = '<div class="col-span-2 opacity-70 text-center py-2"><span class="loading loading-spinner loading-xs"></span> Loading PVTs...</div>';
    const data = await api.fetchJSON(`/api/saf/${sel.project}/${sel.subproject}/cells/${encodeURIComponent(cellWithSuffix)}/nt-pvts`);
    state.pvts = Array.isArray(data && data.pvts) ? data.pvts : [];
    renderPvts(state.pvts);
    updatePreview();
  }

  function buildEcoArgs() {
    const args = [];
    if (document.getElementById('intV2SetupStep')?.checked) args.push('-setupstep');
    if (document.getElementById('intV2SimStep')?.checked) args.push('-simstep');
    if (document.getElementById('intV2ReportStep')?.checked) args.push('-reportstep');
    if (document.getElementById('intV2SkipJob')?.checked) args.push('--skipjob');
    if (document.getElementById('intV2NoSpice')?.checked) args.push('--nospice');

    const selectedPvts = getSelectedPvts();
    if (selectedPvts.length) {
      args.push(`-pvts "${selectedPvts.join(' ')}"`);
    }

    const ecoName = (document.getElementById('intV2EcoName')?.value || '').trim();
    const ecoNote = (document.getElementById('intV2EcoNote')?.value || '').trim();
    if (ecoName) args.push(`-eco_name ${ecoName}`);
    if (ecoNote) args.push(`-eco_note "${ecoNote.replace(/"/g, '\\"')}"`);
    return args;
  }

  function updatePreview() {
    // Preview is intentionally disabled for now.
    return;

    const cell = state.currentCell || '<cellname>';
    const args = buildEcoArgs().join(' ');
    const preview = [
      'TimingCloseBeta.py -update',
      `./bin/python/EcoInternalTiming.py -block_path ${cell}${args ? ` ${args}` : ''}`
    ].join('\n');
    const pre = document.getElementById('intV2CmdPreview');
    if (pre) pre.textContent = preview;
  }

  async function prepareRuntime(cell, outputDir) {
    const api = global.InternalTimingV2API;
    const sel = api.selection();
    const base = api.cellBase(cell);

    await fetch(`/api/cell/${sel.project}/${sel.subproject}/nt/ensure-share`, { method: 'POST' });
    await fetch(`/api/cell/${sel.project}/${sel.subproject}/int/${base}/prepare`, { method: 'POST' });

    await fetch('/api/files/symlinks', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ cell_root: outputDir })
    });
  }

  async function runCurrentCell() {
    const api = global.InternalTimingV2API;
    const sel = api.selection();
    const cell = state.currentCell;
    if (!sel.project || !sel.subproject || !cell) return;

    const runBtn = document.getElementById('intV2RunNowBtn');
    if (runBtn) {
      runBtn.disabled = true;
      runBtn.innerHTML = '<span class="loading loading-spinner loading-xs"></span> Running';
    }

    try {
      const baseResp = await api.fetchJSON('/api/config/base-path');
      const basePath = (baseResp && baseResp.base_path) || '';
      const outputDir = `${basePath}/${sel.project}/${sel.subproject}/design/timing/nt`;
      const safeCell = cell.replace(/[^A-Za-z0-9_\-.]/g, '_');
      const scriptName = `run_int_v2_${safeCell}.csh`;

      await prepareRuntime(cell, outputDir);

      const scriptCommandParts = [
        `-block_path ${cell}`,
        ...buildEcoArgs()
      ];

      const payload = {
        command: 'TimingCloseBeta.py -update',
        command_line_ending: '',
        options: [
          ['./bin/python/EcoInternalTiming.py', scriptCommandParts.join(' '), null, true]
        ],
        fill_space: ' \\',
        output_dir: outputDir,
        script_name: scriptName
      };

      const genResp = await fetch('/api/script/runall', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (!genResp.ok) {
        const text = await genResp.text();
        throw new Error(`Failed to create script: ${text}`);
      }

      document.getElementById('intV2RunModal')?.close();
      document.getElementById('intV2ExecutionModal')?.showModal();

      const stream = global.ExecutionStreamFactory && global.ExecutionStreamFactory.create({
        executionDir: outputDir,
        command: `${outputDir}/${scriptName}`,
        shell: '/bin/csh',
        containerId: 'intV2ExecutionOutputGroup',
        onComplete: async () => {
          if (typeof state.onComplete === 'function') await state.onComplete();
        }
      });

      if (!stream) {
        throw new Error('Failed to initialize execution stream');
      }
      stream.connect();
    } catch (err) {
      alert(err.message || 'Run failed');
    } finally {
      if (runBtn) {
        runBtn.disabled = false;
        runBtn.textContent = 'Run';
      }
    }
  }

  function getLib2TclFormValues() {
    return {
      database: (document.getElementById('intV2Lib2TclDatabase')?.value || '').trim(),
      rel: (document.getElementById('intV2Lib2TclRel')?.value || '').trim(),
      targetcell: (document.getElementById('intV2Lib2TclTargetCell')?.value || '').trim()
    };
  }

  async function runLib2TclCurrentCell() {
    const api = global.InternalTimingV2API;
    const sel = api.selection();
    const cell = state.currentLib2TclCell;
    if (!sel.project || !sel.subproject || !cell) return;

    const runBtn = document.getElementById('intV2Lib2TclRunBtn');
    if (runBtn) {
      runBtn.disabled = true;
      runBtn.innerHTML = '<span class="loading loading-spinner loading-xs"></span> Running';
    }

    try {
      const form = getLib2TclFormValues();
      if (!form.database || !form.rel || !form.targetcell) {
        throw new Error('database, rel, and targetcell are required');
      }

      const baseResp = await api.fetchJSON('/api/config/base-path');
      const basePath = (baseResp && baseResp.base_path) || '';
      const outputDir = `${basePath}/${sel.project}/${sel.subproject}/design/timing/nt`;
      const safeTarget = sanitizeScriptPart(form.targetcell);
      const scriptName = `run_lib2tcl_${safeTarget}.csh`;

      await prepareRuntime(form.targetcell, outputDir);

      const payload = {
        command: 'TimingCloseBeta.py -update',
        command_line_ending: ' \\',
        options: [
          ['collectdepot', null],
          ['database', form.database],
          ['rel', form.rel],
          ['lib2tcl', null],
          ['targetcell', form.targetcell]
        ],
        fill_space: ' \\',
        output_dir: outputDir,
        script_name: scriptName
      };

      const genResp = await fetch('/api/script/runall', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (!genResp.ok) {
        const text = await genResp.text();
        throw new Error(`Failed to create script: ${text}`);
      }

      document.getElementById('intV2Lib2TclModal')?.close();
      document.getElementById('intV2ExecutionModal')?.showModal();

      const stream = global.ExecutionStreamFactory && global.ExecutionStreamFactory.create({
        executionDir: outputDir,
        command: `${outputDir}/${scriptName}`,
        shell: '/bin/csh',
        containerId: 'intV2ExecutionOutputGroup',
        onComplete: async () => {
          if (typeof state.onComplete === 'function') await state.onComplete();
        }
      });

      if (!stream) {
        throw new Error('Failed to initialize execution stream');
      }
      stream.connect();
    } catch (err) {
      alert(err.message || 'lib2tcl run failed');
    } finally {
      if (runBtn) {
        runBtn.disabled = false;
        runBtn.textContent = 'Run lib2tcl';
      }
    }
  }

  function openRunModal(cell) {
    state.currentCell = cell;
    const label = document.getElementById('intV2RunModalCell');
    if (label) label.textContent = cell;
    loadPvtsForCell(cell);
    updatePreview();
    document.getElementById('intV2RunModal')?.showModal();
  }

  function openLib2TclModal(cell) {
    state.currentLib2TclCell = cell;
    const baseCell = global.InternalTimingV2API.cellBase(cell);
    const label = document.getElementById('intV2Lib2TclModalCell');
    if (label) label.textContent = cell;
    const databaseInput = document.getElementById('intV2Lib2TclDatabase');
    const relInput = document.getElementById('intV2Lib2TclRel');
    const targetCellInput = document.getElementById('intV2Lib2TclTargetCell');
    if (databaseInput) databaseInput.value = '';
    if (relInput) relInput.value = '';
    if (targetCellInput) targetCellInput.value = baseCell;
    document.getElementById('intV2Lib2TclModal')?.showModal();
  }

  function init(opts) {
    state.onComplete = opts && opts.onComplete ? opts.onComplete : null;
    ['intV2SetupStep', 'intV2SimStep', 'intV2ReportStep', 'intV2SkipJob', 'intV2NoSpice', 'intV2EcoName', 'intV2EcoNote'].forEach((id) => {
      document.getElementById(id)?.addEventListener('input', updatePreview);
      document.getElementById(id)?.addEventListener('change', updatePreview);
    });
    document.getElementById('intV2PvtsContainer')?.addEventListener('change', updatePreview);
    document.getElementById('intV2PvtsCheckAll')?.addEventListener('click', () => {
      document.querySelectorAll('#intV2PvtsContainer .int-v2-pvt-checkbox').forEach((cb) => { cb.checked = true; });
      updatePreview();
    });
    document.getElementById('intV2PvtsUncheckAll')?.addEventListener('click', () => {
      document.querySelectorAll('#intV2PvtsContainer .int-v2-pvt-checkbox').forEach((cb) => { cb.checked = false; });
      updatePreview();
    });
    document.getElementById('intV2CancelRunBtn')?.addEventListener('click', () => {
      document.getElementById('intV2RunModal')?.close();
    });
    document.getElementById('intV2RunNowBtn')?.addEventListener('click', runCurrentCell);
    document.getElementById('intV2Lib2TclCancelBtn')?.addEventListener('click', () => {
      document.getElementById('intV2Lib2TclModal')?.close();
    });
    document.getElementById('intV2Lib2TclRunBtn')?.addEventListener('click', runLib2TclCurrentCell);
  }

  global.InternalTimingV2Run = {
    init,
    openRunModal,
    openLib2TclModal
  };
})(window);
