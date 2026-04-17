// Internal Timing v2 shared API/helpers
(function (global) {
  'use strict';

  function selection() {
    return global.AppSelection ? global.AppSelection.get() : { project: '', subproject: '' };
  }

  async function fetchJSON(url, options) {
    try {
      const res = await fetch(url, options);
      if (!res.ok) return null;
      return await res.json();
    } catch (_) {
      return null;
    }
  }

  function cellBase(cell) {
    return (cell || '').endsWith('_int') ? cell.slice(0, -4) : (cell || '');
  }

  function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str || '';
    return div.innerHTML;
  }

  async function loadRows() {
    const sel = selection();
    if (!sel.project || !sel.subproject) return [];

    const list = await fetchJSON(`/api/saf/${sel.project}/${sel.subproject}/cells-int`);
    const cells = Array.isArray(list && list.cells) ? list.cells : [];

    const rows = [];
    for (const fullCell of cells) {
      const base = cellBase(fullCell);
      const netlistRes = await fetchJSON(`/api/cell/${sel.project}/${sel.subproject}/int/${base}/netlist-version`);
      const pvtRes = await fetchJSON(`/api/cell/${sel.project}/${sel.subproject}/int/${base}/pvt-status`);
      const reportRes = await fetchJSON(`/api/cell/${sel.project}/${sel.subproject}/int/${base}/report-exists`);
      rows.push({
        cell: fullCell,
        netlist: netlistRes && netlistRes.netlist_version ? netlistRes.netlist_version : 'Unknown',
        summary: pvtRes && pvtRes.summary ? pvtRes.summary : null,
        report_exists: !!(reportRes && reportRes.exists)
      });
    }
    return rows;
  }

  async function syncNetlist(cell) {
    const sel = selection();
    if (!sel.project || !sel.subproject) return null;
    const base = cellBase(cell);
    return await fetchJSON(`/api/cell/${sel.project}/${sel.subproject}/int/${base}/sync-netlist`, { method: 'POST' });
  }

  async function openReport(cell) {
    const sel = selection();
    if (!sel.project || !sel.subproject) return;

    const baseResp = await fetchJSON('/api/config/base-path');
    const basePath = (baseResp && baseResp.base_path) || '';
    const sep = basePath.includes('\\') ? '\\' : '/';
    const base = cellBase(cell);
    const filePath = `${basePath}${sep}${sel.project}${sep}${sel.subproject}${sep}design${sep}timing${sep}quality${sep}7_internal${sep}${base}${sep}${base}_InternalTiming_Report.xlsx`;

    const access = await fetchJSON('/api/access/type');
    const isSSH = !!(access && access.is_ssh_forwarded);

    if (isSSH) {
      const a = document.createElement('a');
      a.href = `/api/files/download?file_path=${encodeURIComponent(filePath)}`;
      a.download = '';
      a.style.display = 'none';
      document.body.appendChild(a);
      a.click();
      setTimeout(() => a.remove(), 1000);
      return;
    }

    await fetch('/api/files/open', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ file_path: filePath })
    });
  }

  global.InternalTimingV2API = {
    selection,
    fetchJSON,
    cellBase,
    escapeHtml,
    loadRows,
    syncNetlist,
    openReport
  };
})(window);
