// Bottom console terminal panel
// Depends on xterm.js and xterm-addon-fit loaded in base.html
(function(){
  function qs(id){ return document.getElementById(id); }
  const panel = qs('floatingConsole');
  const resizeHandle = qs('consoleResizeHandle');
  const closeBtn = qs('consoleCloseBtn');
  const termEl = qs('floatingTerminal');
  const statusEl = qs('consoleConnStatus');
  const reconnectBtn = qs('consoleReconnectBtn');
  const clearBtn = qs('consoleClearBtn');
  const insertLsfBtn = qs('consoleInsertLsfBtn');
  if(!panel || !termEl){ return; }

  let socket = null;
  let term = null;
  let fitAddon = null;
  let isOpen = false;
  let pendingInputs = [];

  function status(txt, cls){ if(statusEl){ statusEl.textContent=txt; statusEl.className='badge '+cls; } }

  function initTerminal(){
    if(term){ return; }
    term = new Terminal({cursorBlink:true, scrollback:5000, convertEol:true, fontSize:13, fontFamily:'Menlo,Consolas,monospace'});
    try { if (window.FitAddon && typeof window.FitAddon.FitAddon === 'function') { fitAddon = new window.FitAddon.FitAddon(); term.loadAddon(fitAddon); } } catch(_){}
    term.open(termEl);
    term.onData(data=>{ if(socket && socket.readyState===1){ try{ socket.send(JSON.stringify({type:'input', data})); }catch(_){} } });
    // Clipboard helpers
    term.attachCustomKeyEventHandler((event)=>{
      if((event.ctrlKey||event.metaKey) && event.key==='v' && event.type==='keydown'){ return false; }
      if((event.ctrlKey||event.metaKey) && event.key==='c' && event.type==='keydown'){
        const sel = term.getSelection();
        if(sel){ navigator.clipboard.writeText(sel).catch(()=>{}); return false; }
      }
      return true;
    });
    termEl.addEventListener('paste', (event)=>{
      event.preventDefault();
      const text = event.clipboardData.getData('text');
      if(text && socket && socket.readyState===1){ try{ socket.send(JSON.stringify({type:'input', data:text})); }catch(_){} }
    });
  }

  function sendResize(){
    if(!term) return;
    // Only fit when panel is visible to avoid zero-row resize
    if(isOpen && !panel.classList.contains('hidden')){
      if(fitAddon){ try{ fitAddon.fit(); }catch(_){} }
      if(socket && socket.readyState===1){
        try{ socket.send(JSON.stringify({type:'resize', cols: term.cols, rows: term.rows})); }catch(_){}
      }
    }
  }

  let triedFallback = false;
  function connect(){
    if(!term){ initTerminal(); }
    // Reuse existing healthy connection; don't force close
    if(socket && socket.readyState === 1){
      status('Connected', 'badge-success');
      sendResize();
      // Flush any pending inputs immediately
      while(pendingInputs.length){
        const data = pendingInputs.shift();
        try { socket.send(JSON.stringify({type:'input', data})); } catch(_){}
      }
      return;
    }
    // If already connecting, don't open another
    if(socket && socket.readyState === 0){ status('Connecting...', 'badge-warning'); return; }
    const proto = window.location.protocol === 'https:' ? 'wss':'ws';
    const primary = `${proto}://${window.location.host}/api/terminal/ws/terminal`;
    const fallback = `${proto}://${window.location.host}/api/terminal/ws`;
    const url = triedFallback ? fallback : primary;
    try { socket = new WebSocket(url); } catch(_) { socket = null; }
    status('Connecting...', 'badge-warning');
    const openedAt = Date.now();
    if(!socket){ status('Disconnected', 'badge-error'); return; }
    socket.onopen = ()=>{
      status('Connected', 'badge-success');
      sendResize();
      // Flush queued inputs
      while(pendingInputs.length){
        const data = pendingInputs.shift();
        try { socket.send(JSON.stringify({type:'input', data})); } catch(_){}
      }
    };
    socket.onmessage = ev=>{ if(term){ term.write(ev.data); try{ term.scrollToBottom(); }catch(_){} } };
    socket.onclose = ()=>{
      if(!triedFallback && Date.now()-openedAt < 1000){ triedFallback = true; status('Retrying...', 'badge-warning'); setTimeout(connect, 200); return; }
      status('Disconnected', 'badge-error');
      // Keep inputs queued; user may reopen/connect later
    };
    socket.onerror = ()=>{};
  }

  function openPanel(){
    if(isOpen) return;
    isOpen = true;
    panel.classList.remove('hidden');
    // Ensure heights
    const box = panel.querySelector('.glass-panel-card');
    const savedPx = (function(){ try { return parseFloat(localStorage.getItem('console_height_px')||''); } catch(_) { return NaN; } })();
    if(!isNaN(savedPx) && savedPx > 0){
      box.style.height = `${savedPx}px`;
      termEl.style.height = `calc(${savedPx}px - 42px)`;
    } else {
      const h = box.style.height || '32vh';
      termEl.style.height = `calc(${h} - 42px)`;
    }
    initTerminal();
    setTimeout(()=>{ sendResize(); if(!(socket && socket.readyState===1)){ connect(); } }, 50);
    setTimeout(()=>{ sendResize(); try{ term && term.scrollToBottom(); term && term.focus(); }catch(_){} }, 300);
  }
  function closePanel(){
    if(!isOpen) return;
    isOpen = false;
    panel.classList.add('hidden');
  }

  // Resize dragging
  let dragging = false;
  let startY = 0;
  let startH = 0;
  function setPanelHeight(px){
    const viewportH = window.innerHeight;
    let clamped = Math.max(viewportH*0.2, Math.min(viewportH*0.9, px));
    const box = panel.querySelector('.glass-panel-card');
    box.style.height = `${clamped}px`;
    termEl.style.height = `calc(${clamped}px - 42px)`;
    try { localStorage.setItem('console_height_px', String(Math.round(clamped))); } catch(_) {}
    sendResize();
  }
  resizeHandle.addEventListener('mousedown', (e)=>{
    dragging = true; startY = e.clientY;
    const box = panel.querySelector('.glass-panel-card');
    startH = parseFloat(getComputedStyle(box).height);
    document.body.style.cursor = 'ns-resize';
    e.preventDefault();
  });
  window.addEventListener('mousemove', (e)=>{
    if(!dragging) return;
    const delta = startY - e.clientY; // drag up increases height
    setPanelHeight(startH + delta);
  });
  window.addEventListener('mouseup', ()=>{
    if(!dragging) return; dragging = false; document.body.style.cursor = '';
  });
  window.addEventListener('resize', ()=>{ sendResize(); });

  // Adjust console to avoid overlapping sidebar when open
  function adjustConsoleForSidebar(){
    try {
      const sidebar = document.getElementById('sidebar');
      const isOpen = sidebar && sidebar.classList.contains('open');
      const width = sidebar && sidebar.classList.contains('collapsed') ? 80 : 280;
      panel.style.left = isOpen ? (width + 'px') : '0px';
      // Right remains 0 to shrink width accordingly
    } catch(_) {}
  }
  // Observe sidebar open/close
  (function(){
    const sidebar = document.getElementById('sidebar');
    if(!sidebar) return;
    adjustConsoleForSidebar();
    try {
      const obs = new MutationObserver(()=>{ adjustConsoleForSidebar(); sendResize(); });
      obs.observe(sidebar, { attributes: true, attributeFilter: ['class'] });
    } catch(_) {}
    // Also adjust on toggle button clicks indirectly
    const toggleBtn = document.getElementById('sidebarToggle');
    if(toggleBtn){ toggleBtn.addEventListener('click', ()=>{ setTimeout(()=>{ adjustConsoleForSidebar(); sendResize(); }, 0); }); }
    // Fit after the left-position transition completes
    panel.addEventListener('transitionend', (e)=>{ if(e.propertyName==='left'){ sendResize(); } });
  })();

  // Controls
  if(closeBtn){ closeBtn.addEventListener('click', closePanel); }
  if(reconnectBtn){ reconnectBtn.addEventListener('click', ()=>{ triedFallback=false; connect(); }); }
  if(clearBtn){ clearBtn.addEventListener('click', ()=>{ term && term.clear(); }); }
  if(insertLsfBtn){ insertLsfBtn.addEventListener('click', ()=>{
    const cmd = 'bsub -Is -app normal -n 1 -M 100G -R "span[hosts=1] rusage[mem=10GB,scratch_free=5]" -J custom_job ';
    if(socket && socket.readyState===1){ try{ socket.send(JSON.stringify({type:'input', data: cmd})); }catch(_){} }
    else { pendingInputs.push(cmd); connect(); }
  }); }

  // Expose simple API for other pages
  window.ConsolePanel = {
    open: function(){ openPanel(); },
    close: function(){ closePanel(); },
    toggle: function(){
      if(isOpen){
        closePanel();
      } else {
        openPanel();
      }
    },
    sendInput: function(str){
      initTerminal();
      openPanel();
      const data = typeof str === 'string' ? str : String(str||'');
      if(socket && socket.readyState===1){ try{ socket.send(JSON.stringify({type:'input', data})); }catch(_){} }
      else { pendingInputs.push(data); connect(); }
    },
    isConnected: function(){ return socket && socket.readyState===1; },
    reconnect: function(){ connect(); }
  };
})();
