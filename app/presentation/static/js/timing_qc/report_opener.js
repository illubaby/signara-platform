// Timing QC: Report Opener
// Module for opening TMQC Report Excel files (similar to SAF brief_sum_modal)

(function(global) {
  'use strict';

  async function fetchJSON(url, opts={}) {
    if (global.QCSharedHttp) {
      return global.QCSharedHttp.fetchJSON(url, opts.body?{method:opts.method||'GET', body:JSON.stringify(opts.body), headers:{'Content-Type':'application/json'}}:{}, { silent: false, errorPrefix: 'TMQC Report' });
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

  async function openTmqcReport(project, subproject, cell){
    if (!project || !subproject || !cell) {
      console.error('[TMQC Report] Missing required parameters');
      return;
    }

    try {
      const [base, access] = await Promise.all([fetchBasePath(), fetchAccessInfo()]);
      const sep = base.includes('\\') ? '\\' : '/';
      const filePath = `${base}${sep}${project}${sep}${subproject}${sep}design${sep}timing${sep}quality${sep}4_qc${sep}${cell}${sep}${cell}_TMQC_Report.xlsx`;
      const isSSH = !!(access && access.is_ssh_forwarded);
      console.log('[TMQC Report] Path:', filePath, 'isSSHForwarded=', isSSH);

      if(isSSH){
        // Remote / port-forwarded: trigger download instead of server-side open
        const downloadUrl = `/api/files/download?file_path=${encodeURIComponent(filePath)}`;
        // Create temporary anchor to start download without navigation side-effects
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.style.display = 'none';
        a.download = '';
        document.body.appendChild(a);
        a.click();
        setTimeout(()=>a.remove(), 2000);
        
        // Show toast notification
        if (global.QCSharedHttp && global.QCSharedHttp.showToast) {
          global.QCSharedHttp.showToast('Download initiated (SSH forward)', {type: 'info'});
        }
      } else {
        // Local access: use server-side open (native application)
        await fetchJSON('/api/files/open', { method:'POST', body:{ file_path: filePath } });
        
        // Show toast notification
        if (global.QCSharedHttp && global.QCSharedHttp.showToast) {
          global.QCSharedHttp.showToast('Report opened successfully', {type: 'success'});
        }
      }
    } catch(err){
      console.error('[TMQC Report] Error:', err);
      // Show error toast
      if (global.QCSharedHttp && global.QCSharedHttp.showToast) {
        global.QCSharedHttp.showToast(`Error opening report: ${err.message}`, {type: 'error'});
      }
    }
  }

  // Export to global namespace
  global.QCReportOpener = { open: openTmqcReport };
})(window);
