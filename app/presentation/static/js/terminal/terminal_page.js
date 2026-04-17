// Terminal page logic extracted from template for cleanliness.
// Depends on xterm.js and fit addon loaded via CDN before this script.

(function(){
  const termEl = document.getElementById('terminal');
  if(!termEl){ return; }
  const statusEl = document.getElementById('connStatus');
  const reconnectBtn = document.getElementById('reconnectBtn');
  const clearBtn = document.getElementById('clearBtn');
  const insertLsfBtn = document.getElementById('insertLsfBtn');
  let socket = null;
  const term = new Terminal({cursorBlink:true, scrollback:5000, convertEol:true, fontSize:13, fontFamily:'Menlo,Consolas,monospace'});
  // Gracefully handle cases where FitAddon CDN is blocked
  let fitAddon = null;
  try {
    if (window.FitAddon && typeof window.FitAddon.FitAddon === 'function') {
      fitAddon = new window.FitAddon.FitAddon();
      term.loadAddon(fitAddon);
    }
  } catch(_) { /* ignore addon failure */ }
  term.open(termEl);
  function status(txt, cls){ statusEl.textContent=txt; statusEl.className='badge '+cls; }
  let triedFallback = false;
  function connect(){
    if(socket){ try{ socket.close(); }catch(_){} }
    const proto = window.location.protocol === 'https:' ? 'wss':'ws';
    const primary = `${proto}://${window.location.host}/api/terminal/ws/terminal`;
    const fallback = `${proto}://${window.location.host}/api/terminal/ws`;
    const url = triedFallback ? fallback : primary;
    socket = new WebSocket(url);
    status('Connecting...', 'badge-warning');
    const openedAt = Date.now();
    socket.onopen = ()=>{ status('Connected', 'badge-success'); if (fitAddon) { fitAddon.fit(); } sendResize(); };
    socket.onmessage = ev=>{ term.write(ev.data); };
    socket.onclose = ()=>{
      if(!triedFallback && Date.now()-openedAt < 1000){
        triedFallback = true;
        status('Retrying alternate path...', 'badge-warning');
        setTimeout(connect, 200);
        return;
      }
      status('Disconnected', 'badge-error');
      if(term.buffer.active.length === 0){
        term.writeln('\r\nInteractive terminal unavailable (platform may not support PTY).');
      }
    };
    socket.onerror = ()=>{ /* allow close handler to manage fallback */ };
  }
  function sendResize(){
    if(!socket || socket.readyState!==1) return;
    const cols = term.cols; const rows = term.rows;
    try { socket.send(JSON.stringify({type:'resize', cols, rows})); } catch(_){ }
  }
  term.onData(data=>{ if(socket && socket.readyState===1){ socket.send(JSON.stringify({type:'input', data})); } });
  
  // Enable clipboard support for Ctrl+V paste
  term.attachCustomKeyEventHandler((event) => {
    // Handle Ctrl+V (or Cmd+V on Mac) for paste
    if ((event.ctrlKey || event.metaKey) && event.key === 'v' && event.type === 'keydown') {
      console.log('[Terminal] Paste triggered (Ctrl+V)');
      return false; // Allow default paste behavior to proceed
    }
    // Handle Ctrl+C for copy (when text is selected)
    if ((event.ctrlKey || event.metaKey) && event.key === 'c' && event.type === 'keydown') {
      const selection = term.getSelection();
      if (selection) {
        console.log('[Terminal] Copy triggered (Ctrl+C):', selection);
        navigator.clipboard.writeText(selection).catch(err => {
          console.error('[Terminal] Copy failed:', err);
        });
        return false; // Prevent terminal from receiving Ctrl+C
      }
    }
    return true; // Allow other key events to proceed normally
  });

  // Handle paste event from browser
  termEl.addEventListener('paste', (event) => {
    event.preventDefault();
    const text = event.clipboardData.getData('text');
    console.log('[Terminal] Paste event received:', text);
    if (text && socket && socket.readyState === 1) {
      socket.send(JSON.stringify({type:'input', data: text}));
    }
  });

  window.addEventListener('resize', ()=>{ if (fitAddon) { fitAddon.fit(); } sendResize(); });
  reconnectBtn.addEventListener('click', ()=>{ connect(); });
  clearBtn.addEventListener('click', ()=>{ term.clear(); });
  // Insert predefined LSF interactive job command without executing (no newline)
  if (insertLsfBtn) {
    insertLsfBtn.addEventListener('click', ()=>{
      const cmd = 'bsub -Is -app normal -n 1 -M 100G -R "span[hosts=1] rusage[mem=10GB,scratch_free=5]" -J custom_job ';
      // Avoid double echo: if connected, let PTY echo it; if not, write locally
      if (socket && socket.readyState === 1) {
        try { socket.send(JSON.stringify({type:'input', data: cmd})); } catch(_) {}
      } else {
        term.write(cmd);
      }
    });
  }
  connect();
  // Initial fit with retry to ensure proper sizing
  setTimeout(()=>{ if (fitAddon) { fitAddon.fit(); } sendResize(); }, 100);
  setTimeout(()=>{ if (fitAddon) { fitAddon.fit(); } sendResize(); }, 500);
  if(document.readyState === 'complete') {
    if (fitAddon) { fitAddon.fit(); } sendResize();
  } else {
    window.addEventListener('load', ()=>{ setTimeout(()=>{ if (fitAddon) { fitAddon.fit(); } sendResize(); }, 100); });
  }
})();
