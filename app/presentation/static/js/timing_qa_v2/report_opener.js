// Timing QA v2: Report Opener
// Module for opening TMQA Report Excel files

(function(global) {
  'use strict';

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
    if (!project || !subproject || !cell) {
      console.error('[TMQA Report] Missing required parameters');
      return;
    }

    try {
      const [base, access] = await Promise.all([fetchBasePath(), fetchAccessInfo()]);
      const sep = base.includes('\\') ? '\\' : '/';
      const filePath = `${base}${sep}${project}${sep}${subproject}${sep}design${sep}timing${sep}release${sep}process${sep}${cell}${sep}${cell}_TMQA_Report.xlsx`;
      const isSSH = !!(access && access.is_ssh_forwarded);
      console.log('[TMQA Report] Path:', filePath, 'isSSHForwarded=', isSSH);

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
        
        showToast('Download initiated (SSH forward)', 'info');
      } else {
        // Local access: use server-side open (native application)
        const res = await fetch('/api/files/open', { 
          method:'POST', 
          headers:{'Content-Type':'application/json'}, 
          body: JSON.stringify({ file_path: filePath })
        });
        
        if(!res.ok){
          throw new Error(await res.text());
        }
        
        showToast('Report opened successfully', 'success');
      }
    } catch(err){
      console.error('[TMQA Report] Error:', err);
      showToast(`Error opening report: ${err.message}`, 'error');
    }
  }

  function showToast(message, type = 'info') {
    // Simple toast notification
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} fixed bottom-4 right-4 w-auto max-w-sm shadow-lg z-50`;
    toast.innerHTML = `<span>${message}</span>`;
    document.body.appendChild(toast);
    setTimeout(() => {
      toast.remove();
    }, 3000);
  }

  async function openHtmlReport(project, subproject, cell){
    if (!project || !subproject || !cell) {
      console.error('[HTML Report] Missing required parameters');
      return;
    }

    try {
      const base = await fetchBasePath();
      const sep = base.includes('\\') ? '\\' : '/';
      
      // Construct HTML directory path
      const htmlDir = `${base}${sep}${project}${sep}${subproject}${sep}design${sep}timing${sep}release${sep}process${sep}${cell}${sep}html`;
      
      console.log('[HTML Report] Opening for:', project, subproject, cell);
      console.log('[HTML Report] HTML dir:', htmlDir);

      // Use generic HTML viewer endpoint with proper path context
      const url = `/api/html-viewer/summary.html?html_dir=${encodeURIComponent(htmlDir)}`;
      window.open(url, '_blank');
      
      showToast('Opening HTML report in new tab', 'info');
    } catch(err){
      console.error('[HTML Report] Error:', err);
      showToast(`Error opening HTML report: ${err.message}`, 'error');
    }
  }

  // Export to global namespace
  global.QAV2ReportOpener = { 
    open: openTmqaReport,
    openHtml: openHtmlReport
  };
})(window);
