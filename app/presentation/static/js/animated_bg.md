Quick Controls (no code changes)

Opacity: Run in DevTools Console
TimingAnimatedBg.setOpacity(0.25) for subtle
TimingAnimatedBg.setOpacity(0.35) for bold
Range 0.15–0.45 is generally good.
Shape Density & Size

In animated_bg.js, edit createShapes():

Shapes count:
Lower density: (w*h)/130000, cap at 50
Higher density: (w*h)/70000, cap at 90
Current:
const count = Math.ceil(Math.min(70, Math.max(28, (w*h)/90000)));
Size range:
Smaller: rand(12, 42)
Larger: rand(18, 60)
Current: rand(16, 54)
Per‑shape opacity:

Softer: rand(0.10, 0.22)
Bolder: rand(0.25, 0.40)
Current: rand(0.18, 0.35)
Speed/Drift:

Slower: speed = rand(0.10, 0.30), vx/vy = rand(-0.3, 0.3)
Faster: speed = rand(0.25, 0.55), vx/vy = rand(-0.6, 0.6)
Theme Sensitivity

Colors come from currentPalette(). To make dark themes bolder:
Add brighter dark colors in paletteDark (e.g., #38bdf8, #a78bfa).
Page Background Show‑Through

main.main-content is already transparent. If you want more background visible:
Reduce sidebar/footer opacity via CSS, e.g.:
.sidebar { background-color: rgba(var(--b1), 0.9); }
Or add a slight backdrop-filter: blur(2px); to soften shapes behind panels.
Performance Tips

If animations feel heavy:
Reduce count or maximum size.
Lower alpha range slightly.
Keep requestAnimationFrame as is; it already pauses when tab is hidden.