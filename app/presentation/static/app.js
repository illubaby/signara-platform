/* Main application JS extracted from base.html for caching & maintainability */
(function(){
  const KEY_PRJ = 'timing_selected_project';
  const KEY_SUB = 'timing_selected_subproject';
  function readStore(k){ try { return localStorage.getItem(k) || sessionStorage.getItem(k) || ''; } catch(_) { return ''; } }
  function writeStore(k,v){ try { localStorage.setItem(k,v); } catch(_) { try { sessionStorage.setItem(k,v); } catch(__) {} } }
  function getSel(){ return { project: readStore(KEY_PRJ), subproject: readStore(KEY_SUB) }; }
  function setSel(p,s){ 
    const oldProject = readStore(KEY_PRJ);
    const oldSubproject = readStore(KEY_SUB);
    writeStore(KEY_PRJ,p); 
    writeStore(KEY_SUB,s); 
    // Clear layout form localStorage when project changes
    if(oldProject !== p || oldSubproject !== s){
      clearLayoutFormStorage();
    }
  }
  function clearSel(){ try { localStorage.removeItem(KEY_PRJ); localStorage.removeItem(KEY_SUB); sessionStorage.removeItem(KEY_PRJ); sessionStorage.removeItem(KEY_SUB);} catch(_) {} }
  
  /**
   * Clear all layout form state data from localStorage
   * Preserves important app settings (theme, gradient, sidebar)
   */
  function clearLayoutFormStorage(){
    try {
      const keysToPreserve = [
        'theme',
        'gradient_paused',
        'sidebar_open',
        KEY_PRJ,
        KEY_SUB
      ];
      // Also preserve sidebar group expansion states
      const sidebarGroupPattern = /^sidebar_group_/;
      
      const keysToRemove = [];
      for(let i = 0; i < localStorage.length; i++){
        const key = localStorage.key(i);
        if(key && !keysToPreserve.includes(key) && !sidebarGroupPattern.test(key)){
          keysToRemove.push(key);
        }
      }
      
      keysToRemove.forEach(key => {
        try { localStorage.removeItem(key); } catch(_) {}
      });
      
      console.log('[AppSelection] Cleared layout form storage:', keysToRemove.length, 'items');
    } catch(err) {
      console.warn('[AppSelection] Failed to clear layout form storage:', err);
    }
  }
  
  /**
   * Detect app restart and clear layout form states
   * Uses sessionStorage to track if this is a fresh app session
   */
  function clearLayoutFormOnAppRestart(){
    const APP_SESSION_KEY = 'app_session_active';
    const isNewSession = !sessionStorage.getItem(APP_SESSION_KEY);
    
    if(isNewSession){
      console.log('[AppSelection] New app session detected, clearing layout form data');
      clearLayoutFormStorage();
      sessionStorage.setItem(APP_SESSION_KEY, 'true');
    }
  }
  function hydrateQuery(){
    const qs = new URLSearchParams(window.location.search);
    const p = qs.get('project') || qs.get('p');
    const s = qs.get('subproject') || qs.get('s');
    if(p && s){ setSel(p,s); return true; }
    return false;
  }
  function renderBadge(){
    const badge = document.getElementById('currentSelectionBadge');
    if(!badge) return;
    const {project, subproject} = getSel();
    if(project && subproject){
      badge.innerHTML = ` <strong>Project</strong>: ${project}/${subproject} <button class="btn btn-sm " id='changeSelectionBtn' aria-label='Change project selection'>Change</button></span>`;
      badge.classList.remove('hidden');
      const btn = document.getElementById('changeSelectionBtn');
      if(btn) btn.addEventListener('click', ()=>{ clearSel(); window.location.href='/choose-project'; });
    } else {
      badge.classList.add('hidden');
      badge.innerHTML='';
    }
  }

  function highlightActivePage(){
    const path = window.location.pathname;
    document.querySelectorAll('.sidebar-item').forEach(item => {
      const href = item.getAttribute('href');
      if(href && (path === href || (path !== '/' && href !== '/' && path.startsWith(href)))){
        item.classList.add('active');
        item.setAttribute('aria-current','page');
      } else {
        item.classList.remove('active');
        item.removeAttribute('aria-current');
      }
    });
    document.querySelectorAll('.sidebar-subitem').forEach(item => {
      const href = item.getAttribute('href');
      if(href && path === href){
        item.classList.add('active');
        item.setAttribute('aria-current','page');
        const groupContent = item.closest('.sidebar-group-content');
        if(groupContent){
          const groupName = groupContent.getAttribute('data-group-content');
          expandGroup(groupName, true);
        }
      } else {
        item.classList.remove('active');
        item.removeAttribute('aria-current');
      }
    });
  }

  function expandGroup(groupName, expand){
    const header = document.querySelector(`[data-group="${groupName}"]`);
    const content = document.querySelector(`[data-group-content="${groupName}"]`);
    const chevron = header?.querySelector('.chevron-icon');
    if(!header || !content) return;
    if(expand){
      content.classList.add('expanded');
      content.setAttribute('aria-expanded','true');
      header.classList.add('expanded');
      if(chevron) chevron.classList.add('rotated');
      localStorage.setItem(`sidebar_group_${groupName}`, 'expanded');
    } else {
      content.classList.remove('expanded');
      content.setAttribute('aria-expanded','false');
      header.classList.remove('expanded');
      if(chevron) chevron.classList.remove('rotated');
      localStorage.setItem(`sidebar_group_${groupName}`, 'collapsed');
    }
  }
  function toggleGroup(groupName){
    const content = document.querySelector(`[data-group-content="${groupName}"]`);
    const isExpanded = content?.classList.contains('expanded');
    expandGroup(groupName, !isExpanded);
  }
  function restoreExpandedState(){
    document.querySelectorAll('[data-group]').forEach(header => {
      const groupName = header.getAttribute('data-group');
      const savedState = localStorage.getItem(`sidebar_group_${groupName}`);
      if(savedState === 'expanded'){
        expandGroup(groupName, true);
      }
    });
  }
  function gate(){
    hydrateQuery();
    const {project, subproject} = getSel();
    const path = window.location.pathname;
    const choosing = path.startsWith('/choose-project');
    document.querySelectorAll('[data-need-selection]').forEach(item => {
      const links = item.querySelectorAll('a, .sidebar-group-header');
      if(!(project && subproject)){
        item.classList.add('disabled');
        links.forEach(link => {
          link.classList.add('disabled');
          link.setAttribute('title','Select a project first');
          link.setAttribute('aria-disabled','true');
        });
      } else {
        item.classList.remove('disabled');
        links.forEach(link => {
          link.classList.remove('disabled');
          link.removeAttribute('title');
          link.removeAttribute('aria-disabled');
        });
      }
    });
    if(!(project && subproject) && !choosing && path !== '/'){
      if(!sessionStorage.getItem('sel_redirected')){
        sessionStorage.setItem('sel_redirected','1');
        window.location.replace('/choose-project');
      }
    } else {
      sessionStorage.removeItem('sel_redirected');
    }
  }

  function initSidebar(){
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.querySelector('main.main-content');
    const toggleBtn = document.getElementById('sidebarToggle');
    const isAlreadyCollapsed = false; // collapse feature removed
    const SAVED_OPEN = localStorage.getItem('sidebar_open');

    // Restore saved open state (default: closed)
    if(SAVED_OPEN === 'true'){
      sidebar.classList.add('open');
    } else {
      sidebar.classList.remove('open');
    }
    
    // Update main content margin based on initial sidebar state
    // Collapse functionality removed; sidebar only toggles open/closed
    if(toggleBtn){
      toggleBtn.addEventListener('click', () => {
        sidebar.classList.toggle('open');
        const isOpen = sidebar.classList.contains('open');
        try { localStorage.setItem('sidebar_open', isOpen ? 'true' : 'false'); } catch(_) {}
      });
    }
    document.addEventListener('click', (e) => {
      const clickedToggle = toggleBtn && (e.target === toggleBtn || toggleBtn.contains(e.target));
      const clickedInsideSidebar = sidebar.contains(e.target);
      const isMobile = window.innerWidth < 768;
      if(isMobile && !clickedToggle && !clickedInsideSidebar && sidebar.classList.contains('open')){
        sidebar.classList.remove('open');
        try { localStorage.setItem('sidebar_open', 'false'); } catch(_) {}
      }
    });
    document.querySelectorAll('.sidebar-item, .sidebar-subitem').forEach(item => {
      item.addEventListener('click', () => {
        // Close on mobile after navigation; keep state on desktop
        if(window.innerWidth < 768){
          sidebar.classList.remove('open');
          try { localStorage.setItem('sidebar_open', 'false'); } catch(_) {}
        }
      });
    });
    const popupTimeouts = new Map();
    document.querySelectorAll('.sidebar-group-header').forEach(header => {
      const popup = header.querySelector('.sidebar-popup');
      if(!popup) return;
      const groupName = header.getAttribute('data-group');
      const hidePopup = () => { popup.style.display = 'none'; popupTimeouts.delete(groupName); };
      const showPopup = () => {
        if(popupTimeouts.has(groupName)){ clearTimeout(popupTimeouts.get(groupName)); popupTimeouts.delete(groupName); }
        const rect = header.getBoundingClientRect();
        popup.style.top = rect.top + 'px';
        popup.style.display = 'block';
      };
      const scheduleHide = (delay = 300) => {
        if(popupTimeouts.has(groupName)){ clearTimeout(popupTimeouts.get(groupName)); }
        const timeout = setTimeout(hidePopup, delay);
        popupTimeouts.set(groupName, timeout);
      };
      header.addEventListener('click', (e) => {
        if(e.target.closest('.sidebar-popup')){ return; }
        e.preventDefault();
        const isCollapsed = sidebar.classList.contains('collapsed');
        if(!header.classList.contains('disabled')){ if(!isCollapsed){ toggleGroup(groupName); } }
      });
      header.addEventListener('mouseenter', () => { if(sidebar.classList.contains('collapsed')){ showPopup(); } });
      header.addEventListener('mouseleave', (e) => {
        if(sidebar.classList.contains('collapsed')){
          const relatedTarget = e.relatedTarget;
          if(relatedTarget && popup.contains(relatedTarget)){ return; }
          scheduleHide(150);
        }
      });
      popup.addEventListener('mouseenter', () => { if(sidebar.classList.contains('collapsed')){ showPopup(); } });
      popup.addEventListener('mouseleave', (e) => {
        if(sidebar.classList.contains('collapsed')){
          const relatedTarget = e.relatedTarget;
          if(relatedTarget && header.contains(relatedTarget)){ return; }
          scheduleHide(100);
        }
      });
    });
    document.querySelectorAll('.sidebar-popup a').forEach(link => { link.addEventListener('click', (e) => { e.stopPropagation(); }); });
  }

  function initThemeToggle(){
    const themeToggle = document.getElementById('themeToggle');
    const html = document.documentElement;
    const iconLight = document.getElementById('themeIconLight');
    const iconDark = document.getElementById('themeIconDark');
    const savedTheme = localStorage.getItem('theme') || 'corporate';
    html.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
    function updateThemeIcon(theme){
      if(theme === 'dark' || theme === 'night'){ iconLight.classList.add('hidden'); iconDark.classList.remove('hidden'); }
      else { iconLight.classList.remove('hidden'); iconDark.classList.add('hidden'); }
    }
    themeToggle.addEventListener('click', () => {
      const currentTheme = html.getAttribute('data-theme');
      const newTheme = (currentTheme === 'corporate' || currentTheme === 'light') ? 'dark' : 'corporate';
      html.setAttribute('data-theme', newTheme); localStorage.setItem('theme', newTheme); updateThemeIcon(newTheme);
    });
  }

  function initGradientToggle(){
    const gradientToggle = document.getElementById('gradientToggle');
    const html = document.documentElement;
    const iconPlay = document.getElementById('gradientIconPlay');
    const iconPause = document.getElementById('gradientIconPause');
    
    // Exit early if elements don't exist on this page
    if (!gradientToggle || !iconPlay || !iconPause) return;
    
    const savedState = localStorage.getItem('gradient_paused') || 'false';
    if(savedState === 'true'){ html.classList.add('gradient-paused'); iconPlay.classList.remove('hidden'); iconPause.classList.add('hidden'); }
    else { html.classList.remove('gradient-paused'); iconPlay.classList.add('hidden'); iconPause.classList.remove('hidden'); }
    gradientToggle.addEventListener('click', () => {
      const isPaused = html.classList.contains('gradient-paused');
      if(isPaused){ html.classList.remove('gradient-paused'); iconPlay.classList.add('hidden'); iconPause.classList.remove('hidden'); localStorage.setItem('gradient_paused', 'false'); }
      else { html.classList.add('gradient-paused'); iconPlay.classList.remove('hidden'); iconPause.classList.add('hidden'); localStorage.setItem('gradient_paused', 'true'); }
    });
  }

  window.AppSelection = { get:getSel, set:(p,s)=>{ setSel(p,s); renderBadge(); gate(); }, clear:()=>{ clearSel(); renderBadge(); gate(); }, clearLayoutForms:clearLayoutFormStorage };

  document.addEventListener('DOMContentLoaded', ()=>{
    renderBadge(); gate(); restoreExpandedState(); highlightActivePage(); initSidebar(); initThemeToggle(); initGradientToggle(); window.dispatchEvent(new Event('app-selection-ready'));
  });
})();

// LSF Jobs Modal Functions
async function openLSFJobsModal() {
  const modal = document.getElementById('lsfJobsModal');
  modal.showModal();
  await fetchLSFJobs();
}
async function fetchLSFJobs() {
  const contentDiv = document.getElementById('lsfJobsContent');
  const lastUpdateSpan = document.getElementById('jobsLastUpdate');
  const usernameInput = document.getElementById('lsfUsername');
  const username = usernameInput?.value?.trim() || '';
  
  contentDiv.innerHTML = `<div class="flex justify-center items-center py-8"><span class="loading loading-spinner loading-lg" aria-hidden="true"></span><span class="ml-3">Loading jobs...</span></div>`;
  try {
    const payload = username ? {command: 'bjobs', username: username} : {command: 'bjobs'};
    const response = await fetch('/api/lsf/bjobs', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload) });
    if (!response.ok) throw new Error('Failed to fetch jobs');
    const data = await response.json();
    const now = new Date();
    lastUpdateSpan.textContent = `Last updated: ${now.toLocaleTimeString()}`;
    if (data.return_code !== 0) {
      contentDiv.innerHTML = `<div class="alert alert-error" role="alert"><div class="font-bold">Error executing bjobs</div><div class="text-xs">${data.stderr || 'Unknown error'}</div></div>`; return;
    }
    const output = data.stdout.trim();
    if (!output || output.includes('No unfinished job found')) {
      contentDiv.innerHTML = `<div class="alert alert-info" role="status"><span>No running jobs found</span></div>`; return;
    }
    const lines = output.split('\n').filter(line => line.trim());
    if (lines.length === 0) { contentDiv.innerHTML = '<div class="text-center py-4 text-sm opacity-70">No jobs to display</div>'; return; }
    
    // Parse header line to get column positions
    const headerLine = lines[0];
    const dataLines = lines.slice(1); // skip header
    
    // Find column positions from header
    const jobidPos = headerLine.indexOf('JOBID');
    const userPos = headerLine.indexOf('USER');
    const statPos = headerLine.indexOf('STAT');
    const queuePos = headerLine.indexOf('QUEUE');
    const fromHostPos = headerLine.indexOf('FROM_HOST');
    const execHostPos = headerLine.indexOf('EXEC_HOST');
    const jobNamePos = headerLine.indexOf('JOB_NAME');
    const submitTimePos = headerLine.indexOf('SUBMIT_TIME');
    
    let html = `<div class="overflow-x-auto"><table class="table table-xs table-zebra" role="table"><thead><tr><th scope="col">JOBID</th><th scope="col">USER</th><th scope="col">STAT</th><th scope="col">QUEUE</th><th scope="col">FROM_HOST</th><th scope="col">EXEC_HOST</th><th scope="col">JOB_NAME</th><th scope="col">SUBMIT_TIME</th></tr></thead><tbody>`;
    
    for (const line of dataLines) {
      if (line.length < 50) continue; // Skip invalid lines
      
      // Extract fields using column positions
      const jobid = line.substring(jobidPos, userPos).trim();
      const user = line.substring(userPos, statPos).trim();
      const stat = line.substring(statPos, queuePos).trim();
      const queue = line.substring(queuePos, fromHostPos).trim();
      const from_host = line.substring(fromHostPos, execHostPos).trim();
      const exec_host = line.substring(execHostPos, jobNamePos).trim();
      const job_name = line.substring(jobNamePos, submitTimePos > 0 ? submitTimePos : undefined).trim();
      const submit_time = submitTimePos > 0 ? line.substring(submitTimePos).trim() : '';
      
      // Add status badge styling
      let statClass = 'badge badge-sm';
      if (stat === 'RUN') statClass += ' badge-success';
      else if (stat === 'PEND') statClass += ' badge-warning';
      else if (stat === 'DONE') statClass += ' badge-info';
      else if (stat.includes('EXIT')) statClass += ' badge-error';
      else statClass += ' badge-ghost';
      
      const statBadge = `<span class="${statClass}">${stat}</span>`;
      
      html += `<tr><td class="font-mono text-xs">${jobid}</td><td class="text-xs">${user}</td><td>${statBadge}</td><td class="text-xs">${queue}</td><td class="text-xs">${from_host}</td><td class="text-xs">${exec_host}</td><td class="font-mono text-xs max-w-xs truncate" title="${job_name}">${job_name}</td><td class="text-xs">${submit_time}</td></tr>`;
    }
    html += `</tbody></table></div><div class="mt-4 text-xs opacity-60">Total jobs: ${dataLines.length}</div>`;
    contentDiv.innerHTML = html;
  } catch (error) {
    contentDiv.innerHTML = `<div class="alert alert-error" role="alert"><div class="font-bold">Connection Error</div><div class="text-xs">${error.message}</div></div>`;
  }
}

// Start Code Server and open in new tab
async function startCodeServer() {
  try {
    // Show loading state
    const button = event?.target?.closest('button');
    if (button) {
      button.disabled = true;
      button.innerHTML = '<span class="loading loading-spinner loading-sm"></span> <span class="sidebar-item-text">Starting...</span>';
    }

    // Call API to start code-server
    const response = await fetch('/api/code-server/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || 'Failed to start code-server');
    }

    // If already running, open immediately
    if (data.status === 'already_running') {
      const currentHost = window.location.hostname;
      const codeServerUrl = `http://${currentHost}:8080`;
      window.open(codeServerUrl, '_blank');
      
      if (button) {
        button.innerHTML = '<svg class="sidebar-icon w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"></path></svg><span class="sidebar-item-text">Code Server</span>';
        button.disabled = false;
      }
      return;
    }

    // Show waiting message
    if (button) {
      button.innerHTML = '<span class="loading loading-spinner loading-sm"></span> <span class="sidebar-item-text">Waiting for server...</span>';
    }

    // Wait for code-server to be ready (poll until it responds)
    const currentHost = window.location.hostname;
    const codeServerUrl = `http://${currentHost}:8080`;
    const maxAttempts = 30; // 30 seconds max
    let attempts = 0;
    let serverReady = false;

    while (attempts < maxAttempts && !serverReady) {
      try {
        // Try to fetch from code-server (will succeed once it's running)
        const checkResponse = await fetch(`http://${currentHost}:8080/healthz`, { 
          method: 'GET',
          mode: 'no-cors' // Avoid CORS issues
        });
        serverReady = true;
      } catch (e) {
        // Server not ready yet, wait 1 second
        await new Promise(resolve => setTimeout(resolve, 1000));
        attempts++;
      }
    }

    if (serverReady || attempts >= maxAttempts) {
      // Open code-server in new tab
      window.open(codeServerUrl, '_blank');
      
      // Show success message
      if (button) {
        button.innerHTML = '<svg class="sidebar-icon w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"></path></svg><span class="sidebar-item-text">Code Server</span>';
        button.disabled = false;
      }
    }

  } catch (error) {
    console.error('Failed to start code-server:', error);
    alert(`Failed to start code-server: ${error.message}`);
    
    // Reset button
    const button = event?.target?.closest('button');
    if (button) {
      button.innerHTML = '<svg class="sidebar-icon w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"></path></svg><span class="sidebar-item-text">Code Server</span>';
      button.disabled = false;
    }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const refreshBtn = document.getElementById('refreshJobsBtn');
  if (refreshBtn) refreshBtn.addEventListener('click', fetchLSFJobs);
});
