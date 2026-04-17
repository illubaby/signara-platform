// Brief Sum Modal Handler for Timing SAF
(function(global) {
  'use strict';

  async function fetchJSON(url, opts={}) {
    if (global.SAFSharedHttp) {
      return global.SAFSharedHttp.fetchJSON(url, opts.body?{method:opts.method||'GET', body:JSON.stringify(opts.body), headers:{'Content-Type':'application/json'}}:{}, { silent: false, errorPrefix: 'TMQA Report' });
    }
    const fetchOpts = { method: opts.method||'GET', headers:{}, body: undefined };
    if (opts.body) { fetchOpts.headers['Content-Type'] = 'application/json'; fetchOpts.body = JSON.stringify(opts.body); }
    const res = await fetch(url, fetchOpts);
    if (!res.ok) {
      throw new Error(await res.text());
    }
    return res.json().catch(()=>({}));
  }

  async function fetchBasePath(){
    try {
      const res = await fetch('/api/config/base-path');
      if(res.ok){ const data = await res.json(); return data.base_path; }
    } catch(_) {}
    return '';
  }

  // Cache access info so we don't re-fetch repeatedly
  let cachedAccessInfo = null;
  async function fetchAccessInfo(){
    if(cachedAccessInfo) return cachedAccessInfo;
    try {
      const res = await fetch('/api/access/type');
      if(res.ok){
        cachedAccessInfo = await res.json();
        return cachedAccessInfo;
      }
    } catch(err){ console.warn('[AccessInfo] fetch failed', err); }
    return { is_local: true, is_ssh_forwarded: false }; // safe default: treat as local
  }

  async function openTmqaReport(project, subproject, cell){
    const modal = document.getElementById('briefSumModal');
    const titleEl = document.getElementById('briefSumTitle');
    const pathEl = document.getElementById('briefSumPath');
    const tbody = document.getElementById('briefSumTableBody');
    const statsEl = document.getElementById('briefSumStats');

    if(modal){ modal.showModal(); }
    if(titleEl) titleEl.textContent = `TMQA Report - ${cell}`;
    if(pathEl) pathEl.textContent = 'Preparing to open report...';
    if(tbody) tbody.innerHTML = '<tr><td colspan="2" class="text-center">Opening...</td></tr>';
    if(statsEl) statsEl.innerHTML = '';

    try {
      const [base, access] = await Promise.all([fetchBasePath(), fetchAccessInfo()]);
      const sep = base.includes('\\') ? '\\' : '/';
      const filePath = `${base}${sep}${project}${sep}${subproject}${sep}design${sep}timing${sep}quality${sep}3_qa${sep}${cell}${sep}${cell}_TMQA_Report.xlsx`;
      const isSSH = !!(access && access.is_ssh_forwarded);
      console.log('[TMQA Report] Path:', filePath, 'isSSHForwarded=', isSSH);

      if(isSSH){
        // Remote / port-forwarded: trigger download instead of server-side open
        const downloadUrl = `/api/files/download?file_path=${encodeURIComponent(filePath)}`;
        if(pathEl) pathEl.textContent = `Downloading: ${filePath}`;
        // Create temporary anchor to start download without navigation side-effects
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.style.display = 'none';
        a.download = '';
        document.body.appendChild(a);
        a.click();
        setTimeout(()=>a.remove(), 2000);
        if(tbody) tbody.innerHTML = '<tr><td colspan="2" class="text-center text-info">Download initiated (SSH forward).</td></tr>';
      } else {
        // Local access: use server-side open (native application)
        await fetchJSON('/api/files/open', { method:'POST', body:{ file_path: filePath } });
        if(pathEl) pathEl.textContent = `Opened locally: ${filePath}`;
        if(tbody) tbody.innerHTML = '<tr><td colspan="2" class="text-center text-success">Report open request sent.</td></tr>';
      }
    } catch(err){
      console.error('[TMQA Report] Error:', err);
      if(tbody) tbody.innerHTML = `<tr><td colspan="2" class="text-error text-center">Error: ${err.message}</td></tr>`;
      if(pathEl) pathEl.textContent = '';
    }
  }

  function wireEventListeners(){
    const tbody = document.querySelector('#cellsTable tbody');
    if(!tbody) return;
    tbody.addEventListener('click', e => {
      const btn = e.target.closest('.view-brief-sum-btn');
      if(!btn) return;
      e.stopPropagation();
      const cell = btn.getAttribute('data-cell');
      const project = btn.getAttribute('data-project');
      const subproject = btn.getAttribute('data-subproject');
      if(cell && project && subproject){
        openTmqaReport(project, subproject, cell);
      }
    });
  }

  function init(){ wireEventListeners(); }

  global.BriefSumModal = { init, open: openTmqaReport };
})(window);
