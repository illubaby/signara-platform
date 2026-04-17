(function(){
  const canvas = document.getElementById('animatedBg');
  if(!canvas) return;
  const ctx = canvas.getContext('2d');

  let w = 0, h = 0, dpr = Math.max(1, window.devicePixelRatio || 1);
  let shapes = [];
  let rafId = null;

  function resize(){
    w = window.innerWidth;
    h = window.innerHeight;
    canvas.style.width = w + 'px';
    canvas.style.height = h + 'px';
    canvas.width = Math.floor(w * dpr);
    canvas.height = Math.floor(h * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  function rand(min, max){ return Math.random() * (max - min) + min; }
  function pick(arr){ return arr[Math.floor(Math.random()*arr.length)]; }

  const paletteLight = ['#2563eb','#7c3aed','#db2777','#f59e0b','#10b981','#14b8a6'];
  const paletteDark = ['#1e40af','#6b21a8','#be185d','#d97706','#0ea5e9','#22c55e'];

  function currentPalette(){
    const theme = document.documentElement.getAttribute('data-theme') || 'corporate';
    return (theme === 'dark' || theme === 'night') ? paletteDark : paletteLight;
  }

  function createShapes(){
    // Increase density for bolder visuals
    const count = Math.ceil(Math.min(70, Math.max(28, (w*h)/40000)));
    shapes = new Array(count).fill(0).map(() => {
      const type = pick(['circle','triangle','square']);
      const speed = rand(0.15, 0.45);
      // Slightly larger average size
      const size = rand(16, 70);
      const x = rand(0, w);
      const y = rand(0, h);
      const angle = rand(0, Math.PI*2);
      const spin = rand(-0.01, 0.01);
      // Make shapes more visible
      const alpha = rand(0.5, 0.9);
      return { type, speed, size, x, y, angle, spin, alpha, vx: rand(-0.4,0.4), vy: rand(-0.4,0.4), color: pick(currentPalette()) };
    });
  }

  function step(){
    ctx.clearRect(0,0,w,h);
    const pal = currentPalette();
    for(const s of shapes){
      // gentle drift
      s.x += s.vx * s.speed;
      s.y += s.vy * s.speed;
      s.angle += s.spin;
      // wrap around edges
      if(s.x < -50) s.x = w+50; if(s.x > w+50) s.x = -50;
      if(s.y < -50) s.y = h+50; if(s.y > h+50) s.y = -50;
      // slight color cycling
      if(Math.random() < 0.002) s.color = pick(pal);

      ctx.save();
      ctx.globalAlpha = s.alpha;
      ctx.translate(s.x, s.y);
      ctx.rotate(s.angle);
      ctx.fillStyle = s.color;
      ctx.strokeStyle = s.color;
      ctx.lineWidth = 1.2;

      switch(s.type){
        case 'circle':
          ctx.beginPath();
          ctx.arc(0,0,s.size,0,Math.PI*2);
          ctx.fill();
          // outline for extra boldness
          ctx.stroke();
          break;
        case 'square':
          ctx.beginPath();
          const ss = s.size;
          ctx.rect(-ss/2,-ss/2,ss,ss);
          ctx.fill();
          ctx.stroke();
          break;
        case 'triangle':
          ctx.beginPath();
          const t = s.size;
          ctx.moveTo(0,-t/1.2);
          ctx.lineTo(-t/1.2, t/1.2);
          ctx.lineTo(t/1.2, t/1.2);
          ctx.closePath();
          ctx.fill();
          ctx.stroke();
          break;
      }
      ctx.restore();
    }
    rafId = requestAnimationFrame(step);
  }

  function start(){
    cancel();
    resize();
    createShapes();
    rafId = requestAnimationFrame(step);
  }

  function cancel(){
    if(rafId){
      cancelAnimationFrame(rafId);
      rafId = null;
    }
  }

  // react to theme changes
  const obs = new MutationObserver(() => {
    // update colors gradually
    for(const s of shapes){ s.color = pick(currentPalette()); }
  });
  obs.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });

  window.addEventListener('resize', () => { resize(); });

  // pause when tab hidden to save CPU
  document.addEventListener('visibilitychange', () => {
    if(document.hidden) cancel(); else start();
  });

  // expose minimal API for future toggles
  window.TimingAnimatedBg = { start, cancel, setOpacity(v){ canvas.style.opacity = String(v); } };

  // ensure main content sits above canvas
  // by default z-index of canvas is 0, DaisyUI components have higher z-index

  start();
})();
