(function(){
  // PCB Circuit: animated traces with flowing signals and blinking vias
  const canvas = document.createElement('canvas');
  canvas.id = 'pcbCircuitCanvas';
  canvas.style.position = 'fixed';
  canvas.style.inset = '0';
  canvas.style.zIndex = '0';
  canvas.style.pointerEvents = 'none';

  const ctx = canvas.getContext('2d');
  let w = 0, h = 0, dpr = Math.max(1, window.devicePixelRatio || 1);
  let rafId = null;
  let t = 0;

  function resize(){
    w = window.innerWidth; h = window.innerHeight;
    canvas.style.width = w + 'px';
    canvas.style.height = h + 'px';
    canvas.width = Math.floor(w * dpr);
    canvas.height = Math.floor(h * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  // Traces grid (angled + straight paths)
  function drawBoard(){
    ctx.save();
    // Fine traces
    ctx.strokeStyle = 'rgba(34,211,238,0.25)';
    ctx.lineWidth = 1;
    for(let x=0; x<=w; x+=64){
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke();
    }
    for(let y=0; y<=h; y+=64){
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke();
    }
    // Angled buses for variety
    ctx.strokeStyle = 'rgba(96,165,250,0.25)';
    ctx.lineWidth = 2;
    for(let i=0;i<6;i++){
      const y0 = (h/6)*i + 20;
      ctx.beginPath(); ctx.moveTo(0, y0); ctx.lineTo(w, y0 + Math.sin(i + t*0.2)*20); ctx.stroke();
    }
    ctx.restore();
  }

  // Vias
  let vias = [];
  function createVias(){
    vias = [];
    for(let x=0; x<=w; x+=128){
      for(let y=0; y<=h; y+=128){
        vias.push({x, y, phase: Math.random()*Math.PI*2});
      }
    }
  }
  function drawVias(){
    for(const v of vias){
      v.phase += 0.03;
      const glow = 0.5 + 0.5*Math.sin(v.phase + t*0.6);
      ctx.save();
      ctx.shadowColor = '#10b981'; ctx.shadowBlur = 12;
      ctx.globalAlpha = glow;
      ctx.fillStyle = '#10b981';
      ctx.beginPath(); ctx.arc(v.x, v.y, 3, 0, Math.PI*2); ctx.fill();
      ctx.restore();
    }
  }

  // Signals flowing along rows/columns
  let signals = [];
  function createSignals(){
    signals = [];
    const count = Math.ceil(Math.min(160, Math.max(50, (w*h)/12000)));
    for(let i=0;i<count;i++){
      const dir = Math.random()<0.5 ? 'h' : 'v';
      const lane = dir==='h' ? Math.floor(Math.random()*Math.floor(h/64))*64 : Math.floor(Math.random()*Math.floor(w/64))*64;
      const speed = 1.0 + Math.random()*2.0;
      const color = Math.random()<0.6 ? '#22d3ee' : '#60a5fa';
      signals.push({ dir, lane, x: Math.random()*w, y: Math.random()*h, speed, color, phase: Math.random()*Math.PI*2 });
    }
  }

  function drawSignals(){
    ctx.lineWidth = 2;
    for(const s of signals){
      s.phase += 0.04;
      const jitter = Math.sin(s.phase)*0.7;
      if(s.dir==='h'){
        s.x += s.speed;
        if(s.x > w+30) s.x = -30;
        const y = s.lane + jitter;
        ctx.strokeStyle = s.color;
        ctx.globalAlpha = 0.6;
        ctx.beginPath(); ctx.moveTo(s.x, y); ctx.lineTo(s.x-16, y); ctx.stroke();
        ctx.save(); ctx.shadowColor = s.color; ctx.shadowBlur = 14; ctx.globalAlpha = 0.85; ctx.fillStyle = s.color; ctx.beginPath(); ctx.arc(s.x, y, 2, 0, Math.PI*2); ctx.fill(); ctx.restore();
      } else {
        s.y += s.speed;
        if(s.y > h+30) s.y = -30;
        const x = s.lane + jitter;
        ctx.strokeStyle = s.color;
        ctx.globalAlpha = 0.6;
        ctx.beginPath(); ctx.moveTo(x, s.y); ctx.lineTo(x, s.y-16); ctx.stroke();
        ctx.save(); ctx.shadowColor = s.color; ctx.shadowBlur = 14; ctx.globalAlpha = 0.85; ctx.fillStyle = s.color; ctx.beginPath(); ctx.arc(x, s.y, 2, 0, Math.PI*2); ctx.fill(); ctx.restore();
      }
    }
    ctx.globalAlpha = 1.0;
  }

  function step(){
    ctx.clearRect(0,0,w,h);
    t += 0.02;
    drawBoard();
    drawVias();
    drawSignals();
    rafId = requestAnimationFrame(step);
  }

  function start(){ cancel(); resize(); createVias(); createSignals(); step(); }
  function cancel(){ if(rafId){ cancelAnimationFrame(rafId); rafId = null; } }

  window.addEventListener('resize', ()=>{ resize(); createVias(); });
  document.addEventListener('visibilitychange', ()=>{ if(document.hidden) cancel(); else start(); });

  window.TimingPcbCircuit = { start, cancel };

  document.body.prepend(canvas);
  start();
})();
