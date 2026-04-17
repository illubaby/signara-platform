// Internal Timing v2 table rendering + actions
(function (global) {
  'use strict';

  const state = {
    rows: []
  };

  function pvtSummaryHtml(summary) {
    if (!summary || typeof summary !== 'object') return '<span class="text-xs opacity-60">-</span>';
    const parts = [];
    if (summary.passed > 0) parts.push(`<span class="badge badge-xs badge-success">${summary.passed}✓</span>`);
    if (summary.failed > 0) parts.push(`<span class="badge badge-xs badge-error">${summary.failed}✗</span>`);
    if (summary.in_progress > 0) parts.push(`<span class="badge badge-xs badge-warning">${summary.in_progress}⟳</span>`);
    if (summary.not_started > 0) parts.push(`<span class="badge badge-xs badge-ghost">${summary.not_started}○</span>`);
    return parts.length ? `<div class="flex flex-wrap gap-1">${parts.join('')}</div>` : '<span class="text-xs opacity-60">No PVTs</span>';
  }

  function renderRows() {
    const api = global.InternalTimingV2API;
    const tbody = document.getElementById('intV2TableBody');
    if (!tbody) return;

    if (!state.rows.length) {
      tbody.innerHTML = '<tr><td colspan="5" class="text-center opacity-70 py-6">No INT cells found</td></tr>';
      return;
    }

    tbody.innerHTML = state.rows.map((r) => {
      const netlistText = (r.netlist && r.netlist !== 'Unknown') ? r.netlist : 'Missing';
      const reportBtn = r.report_exists
        ? `<button type="button" class="btn btn-xs btn-ghost" data-action="open-report" data-cell="${api.escapeHtml(r.cell)}">Report</button>`
        : '<span class="text-xs opacity-60">-</span>';

      return `
        <tr>
          <td>${api.escapeHtml(r.cell)}</td>
          <td>
            <button type="button" class="link link-primary text-xs" data-action="sync-netlist" data-cell="${api.escapeHtml(r.cell)}">${api.escapeHtml(netlistText)}</button>
          </td>
          <td>${pvtSummaryHtml(r.summary)}</td>
          <td>
            <div class="flex flex-wrap gap-1">
              <button type="button" class="btn btn-xs btn-primary" data-action="run" data-cell="${api.escapeHtml(r.cell)}">Run</button>
              <button type="button" class="btn btn-xs btn-secondary" data-action="lib2tcl" data-cell="${api.escapeHtml(r.cell)}">lib2tcl</button>
            </div>
          </td>
          <td>${reportBtn}</td>
        </tr>
      `;
    }).join('');
  }

  async function reloadRows() {
    const api = global.InternalTimingV2API;
    const sel = api.selection();
    const tbody = document.getElementById('intV2TableBody');
    if (!tbody) return;

    if (!sel.project || !sel.subproject) {
      tbody.innerHTML = '<tr><td colspan="5" class="text-center opacity-70 py-6">Select project/subproject to load data</td></tr>';
      return;
    }

    tbody.innerHTML = '<tr><td colspan="5" class="text-center py-6"><span class="loading loading-spinner loading-sm"></span></td></tr>';
    state.rows = await api.loadRows();
    renderRows();
  }

  async function onSync(cell, btn) {
    const original = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span class="loading loading-spinner loading-xs"></span>';
    try {
      await global.InternalTimingV2API.syncNetlist(cell);
      await reloadRows();
    } finally {
      btn.disabled = false;
      btn.innerHTML = original;
    }
  }

  async function onOpenReport(cell, btn) {
    const original = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span class="loading loading-spinner loading-xs"></span>';
    try {
      await global.InternalTimingV2API.openReport(cell);
    } finally {
      btn.disabled = false;
      btn.innerHTML = original;
    }
  }

  function init() {
    document.getElementById('intV2RefreshBtn')?.addEventListener('click', reloadRows);

    const tableBody = document.getElementById('intV2TableBody');
    if (tableBody) {
      tableBody.addEventListener('click', async (ev) => {
        const btn = ev.target.closest('button[data-action]');
        if (!btn) return;
        const action = btn.getAttribute('data-action');
        const cell = btn.getAttribute('data-cell');
        if (!action || !cell) return;

        if (action === 'sync-netlist') {
          await onSync(cell, btn);
          return;
        }
        if (action === 'run') {
          global.InternalTimingV2Run.openRunModal(cell);
          return;
        }
        if (action === 'lib2tcl') {
          global.InternalTimingV2Run.openLib2TclModal(cell);
          return;
        }
        if (action === 'open-report') {
          await onOpenReport(cell, btn);
        }
      });
    }

    reloadRows();
  }

  global.InternalTimingV2Table = {
    init,
    reloadRows
  };
})(window);
