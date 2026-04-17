// Internal Timing NT cells info: cell, netlist snaphier, PVT status, actions
// Lightweight module to avoid overcomplicating internal_timing.js

(function(){
  async function fetchJSON(url) {
    try {
      const resp = await fetch(url);
      if (!resp.ok) return null;
      return await resp.json();
    } catch { return null; }
  }

  async function openInternalTimingReport(project, subproject, cell, btnElement) {
    const originalHtml = btnElement.innerHTML;
    btnElement.disabled = true;
    btnElement.innerHTML = '<span class="loading loading-spinner loading-xs"></span>';
    
    try {
      // Get base path
      const baseResp = await fetch('/api/config/base-path');
      const baseData = await baseResp.json();
      const base = baseData.base_path || '';
      const sep = base.includes('\\') ? '\\' : '/';
      
      // Remove _int suffix for path construction
      const cellBase = cell.endsWith('_int') ? cell.slice(0, -4) : cell;
      
      // Construct file path: <Base>/<project>/<subproject>/design/timing/quality/7_internal/<cell>/<cell>_InternalTiming_Report.xlsx
      const filePath = `${base}${sep}${project}${sep}${subproject}${sep}design${sep}timing${sep}quality${sep}7_internal${sep}${cellBase}${sep}${cellBase}_InternalTiming_Report.xlsx`;
      
      console.log('[IntCells] Opening Internal Timing Report:', filePath);
      
      // Check if SSH forwarded (remote access)
      const accessResp = await fetch('/api/access/type');
      const accessData = await accessResp.json();
      const isSSH = !!(accessData && accessData.is_ssh_forwarded);
      
      if (isSSH) {
        // Remote: trigger download
        const downloadUrl = `/api/files/download?file_path=${encodeURIComponent(filePath)}`;
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.style.display = 'none';
        a.download = '';
        document.body.appendChild(a);
        a.click();
        setTimeout(() => a.remove(), 2000);
        console.log('[IntCells] Download initiated (SSH forward)');
      } else {
        // Local: open with native application
        await fetch('/api/files/open', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ file_path: filePath })
        });
        console.log('[IntCells] Opened locally');
      }
    } catch (err) {
      console.error('[IntCells] Error opening report:', err);
      alert(`Error opening report: ${err.message}`);
    } finally {
      btnElement.disabled = false;
      btnElement.innerHTML = originalHtml;
    }
  }

  function buildPvtStatusHTML(summary) {
    if (!summary || typeof summary !== 'object') {
      return `<span class='text-xs opacity-50'>-</span>`;
    }
    const s = summary;
    const badges = [];
    if (s.passed && s.passed > 0) badges.push(`<span class='badge badge-xs badge-success' title='${s.passed} Passed'>${s.passed}✓</span>`);
    if (s.failed && s.failed > 0) badges.push(`<span class='badge badge-xs badge-error' title='${s.failed} Failed'>${s.failed}✗</span>`);
    if (s.in_progress && s.in_progress > 0) badges.push(`<span class='badge badge-xs badge-warning' title='${s.in_progress} In Progress'>${s.in_progress}⟳</span>`);
    if (s.not_started && s.not_started > 0) badges.push(`<span class='badge badge-xs badge-ghost' title='${s.not_started} Not Started'>${s.not_started}○</span>`);
    if (!badges.length) {
      return `<span class='text-xs opacity-50'>No PVTs</span>`;
    }
    return `<div class='flex flex-wrap gap-1'>${badges.join('')}</div>`;
  }

  function renderTable(container, rows) {
    const html = [
      '<div class="int-cells-table w-full overflow-x-auto bg-base-100 rounded-box shadow-md">',
      '<table class="table table-zebra w-full rounded-box overflow-hidden">',
      '<thead><tr><th>Cell</th><th>Netlist</th><th>PVT Status</th><th>Action</th><th>Report</th></tr></thead>',
      '<tbody>',
      ...rows.map(r => `
        <tr>
          <td>${r.cell}</td>
          <td>${r.netlist}</td>
          <td>${buildPvtStatusHTML(r.summary)}</td>
          <td>
            <button class="btn btn-xs" data-action="sync" data-cell="${r.cell}">Sync Netlist</button>
          </td>
          <td>${r.report_exists ? `<button class='btn btn-xs btn-ghost hover:btn-info' data-action='open-report' data-cell='${r.cell}' title='Open InternalTiming Report (.xlsx)'>Report</button>` : '<span class="text-xs opacity-50">-</span>'}</td>
        </tr>`),
      '</tbody></table>',
      '</div>'
    ].join('');
    container.innerHTML = html;
  }

  async function loadData(project, subproject, cells) {
    const rows = [];
    for (const full of cells) {
      // API expects base name (no _int) for extr/<cell>/nt/etm
      const base = full.endsWith('_int') ? full.slice(0, -4) : full;
      const nl = await fetchJSON(`/api/cell/${project}/${subproject}/int/${base}/netlist-version`);
      const netlist = nl && nl.netlist_version ? nl.netlist_version : 'Unknown';
      
      // Fetch PVT status summary for this cell
      const pvtData = await fetchJSON(`/api/cell/${project}/${subproject}/int/${base}/pvt-status`);
      const summary = pvtData && pvtData.summary ? pvtData.summary : null;
      
      // Check if Internal Timing Report exists
      const reportData = await fetchJSON(`/api/cell/${project}/${subproject}/int/${base}/report-exists`);
      const report_exists = reportData && reportData.exists ? true : false;
      
      rows.push({ cell: full, netlist, summary, report_exists });
    }
    return rows;
  }

  async function setup() {
    const container = document.getElementById('intCellsInfo');
    if (!container) return;
    const selection = window.AppSelection ? window.AppSelection.get() : { project: '', subproject: '' };
    const { project, subproject } = selection;
    if (!project || !subproject) return;

    // Source INT cells
    const list = await fetchJSON(`/api/saf/${project}/${subproject}/cells-int`);
    let cells = Array.isArray(list && list.cells) ? list.cells : [];

    const rows = await loadData(project, subproject, cells);
    renderTable(container, rows);

    // Wire actions
    container.addEventListener('click', async (ev) => {
      const btn = ev.target.closest('button[data-action]');
      if (!btn) return;
      const cell = btn.getAttribute('data-cell');
      const action = btn.getAttribute('data-action');
      if (action === 'sync') {
        const originalHtml = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = '<span class="loading loading-spinner loading-xs"></span> Syncing...';
        try {
          const resp = await fetch(`/api/cell/${project}/${subproject}/int/${cell}/sync-netlist`, { method: 'POST' });
          const data = await resp.json().catch(() => ({}));
          console.log('[IntCells] Sync netlist', { status: resp.status, cell, data });
        } catch (e) {
          console.error('[IntCells] Sync error', e);
        } finally {
          btn.disabled = false;
          btn.innerHTML = originalHtml;
        }
      } else if (action === 'open-report') {
        // Open Internal Timing Report Excel file
        openInternalTimingReport(project, subproject, cell, btn);
      }
    });
  }

  window.addEventListener('DOMContentLoaded', setup);
})();
