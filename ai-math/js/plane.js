// ---------- Coordinate plane: the picture engine for vectors, functions, slope, derivative ----------
// plane(host, {
//   x:[min,max], y:[min,max], equal, ratio, step:[sx,sy], labels, names:[xName,yName], snap,
//   state:{}, handles:[{get(s)->[x,y], set(s,x,y), color}], sliders:[{key,label,min,max,step}], onSlide(s),
//   buttons:[{label, on(s), active(s)}], draw(g, s), read(s) -> html, tick(s, dt) for animation
// }) -> cleanup
// g: grid() line() fn() arrow() rect() dot() knob() text(), plus X/Y/ctx/css for custom drawing
function plane(host, o) {
  const css = n => getComputedStyle(cv).getPropertyValue('--' + n).trim(); // tokens live on the .aimath wrapper
  const s = o.state || {};
  const cv = document.createElement('canvas');
  host.appendChild(cv);
  const ctx = cv.getContext('2d');
  const [x0, x1] = o.x, [y0, y1] = o.y;
  let W = 0, H = 0;
  const X = x => (x - x0) / (x1 - x0) * W, Y = y => H - (y - y0) / (y1 - y0) * H;
  const iX = px => x0 + px / W * (x1 - x0), iY = py => y0 + (H - py) / H * (y1 - y0);
  const font = (px, w = 500) => `${w} ${px}px Vazirmatn, Tahoma, sans-serif`;
  const stroke = (color, w, dash) => { ctx.strokeStyle = css(color); ctx.lineWidth = w; ctx.setLineDash(dash || []); ctx.lineCap = 'round'; };

  const g = { ctx, X, Y, css,
    grid() {
      const [sx, sy] = o.step || [1, 1];
      stroke('soft', 1); ctx.beginPath();
      for (let x = Math.ceil(x0 / sx) * sx; x <= x1; x += sx) { ctx.moveTo(X(x), 0); ctx.lineTo(X(x), H); }
      for (let y = Math.ceil(y0 / sy) * sy; y <= y1; y += sy) { ctx.moveTo(0, Y(y)); ctx.lineTo(W, Y(y)); }
      ctx.stroke();
      stroke('line', 2); ctx.beginPath();
      if (y0 <= 0 && y1 >= 0) { ctx.moveTo(0, Y(0)); ctx.lineTo(W, Y(0)); }
      if (x0 <= 0 && x1 >= 0) { ctx.moveTo(X(0), 0); ctx.lineTo(X(0), H); }
      ctx.stroke();
      ctx.fillStyle = css('muted');
      if (o.labels) {
        ctx.font = font(12);
        ctx.textAlign = 'center'; ctx.textBaseline = 'top';
        const ly = Math.min(H - 16, Math.max(2, Y(0) + 4));
        for (let x = Math.ceil(x0 / sx) * sx; x <= x1; x += sx) if (x) ctx.fillText(fa(x), X(x), ly);
        ctx.textAlign = 'right'; ctx.textBaseline = 'middle';
        const lx = Math.max(24, X(0) - 5);
        for (let y = Math.ceil(y0 / sy) * sy; y <= y1; y += sy) if (y) ctx.fillText(fa(y), lx, Y(y));
      }
      if (o.names) {
        ctx.font = font(12, 700);
        ctx.textAlign = 'right'; ctx.textBaseline = 'bottom'; ctx.fillText(o.names[0], W - 6, Y(Math.max(y0, 0)) - 4);
        ctx.textAlign = 'left'; ctx.textBaseline = 'top'; ctx.fillText(o.names[1], X(Math.max(x0, 0)) + 8, 6);
      }
    },
    line(a, b, c, d, color = 'ink', w = 2, dash) { stroke(color, w, dash); ctx.beginPath(); ctx.moveTo(X(a), Y(b)); ctx.lineTo(X(c), Y(d)); ctx.stroke(); ctx.setLineDash([]); },
    fn(f, color = 'orange', w = 3, from = x0, to = x1) {
      stroke(color, w); ctx.beginPath();
      let pen = false;
      for (let i = 0; i <= 240; i++) {
        const x = from + (to - from) * i / 240, y = f(x);
        if (!isFinite(y)) { pen = false; continue; }
        pen ? ctx.lineTo(X(x), Y(y)) : ctx.moveTo(X(x), Y(y)); pen = true;
      }
      ctx.stroke();
    },
    arrow(a, b, c, d, color = 'ink', w = 4) {
      const [p, q, r, t] = [X(a), Y(b), X(c), Y(d)];
      const len = Math.hypot(r - p, t - q);
      if (len < 2) return;
      const ang = Math.atan2(t - q, r - p), hd = Math.min(16, len * 0.5);
      stroke(color, w); ctx.fillStyle = css(color);
      ctx.beginPath(); ctx.moveTo(p, q); ctx.lineTo(r - Math.cos(ang) * hd * 0.7, t - Math.sin(ang) * hd * 0.7); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(r, t);
      ctx.lineTo(r - hd * Math.cos(ang - 0.42), t - hd * Math.sin(ang - 0.42));
      ctx.lineTo(r - hd * Math.cos(ang + 0.42), t - hd * Math.sin(ang + 0.42));
      ctx.closePath(); ctx.fill();
    },
    rect(a, b, c, d, color = 'blue', alpha = 1) { ctx.globalAlpha = alpha; ctx.fillStyle = css(color); ctx.fillRect(Math.min(X(a), X(c)), Math.min(Y(b), Y(d)), Math.abs(X(c) - X(a)), Math.abs(Y(d) - Y(b))); ctx.globalAlpha = 1; },
    dot(x, y, color = 'ink', r = 6) { ctx.fillStyle = css(color); ctx.beginPath(); ctx.arc(X(x), Y(y), r, 0, 7); ctx.fill(); },
    knob(x, y, color = 'blue') { ctx.beginPath(); ctx.arc(X(x), Y(y), 11, 0, 7); ctx.fillStyle = css('card'); ctx.fill(); stroke(color, 4); ctx.stroke(); },
    text(x, y, str, color = 'ink', align = 'center', dy = -12) { ctx.font = font(13, 700); ctx.fillStyle = css(color); ctx.textAlign = align; ctx.textBaseline = 'middle'; ctx.fillText(str, X(x), Y(y) + dy); },
  };

  // controls
  const sliders = (o.sliders || []).map(sl => {
    const lab = document.createElement('label');
    lab.className = 'slider';
    lab.innerHTML = `<span>${sl.label}</span><input dir="ltr" type="range" min="${sl.min}" max="${sl.max}" step="${sl.step}" value="${s[sl.key]}"><b></b>`;
    lab.querySelector('input').oninput = e => { s[sl.key] = +e.target.value; o.onSlide && o.onSlide(s); draw(); };
    host.appendChild(lab);
    return [sl, lab.querySelector('b')];
  });
  let btnBox = null;
  if (o.buttons) {
    btnBox = document.createElement('div');
    btnBox.className = 'btns';
    o.buttons.forEach(bt => {
      const b = document.createElement('button');
      b.innerHTML = bt.label;
      b.onclick = () => { bt.on(s); draw(); };
      btnBox.appendChild(b);
    });
    host.appendChild(btnBox);
  }
  const read = document.createElement('div');
  read.className = 'read';
  if (o.read) host.appendChild(read);

  function draw() {
    if (!W) return;
    ctx.clearRect(0, 0, W, H);
    o.draw(g, s);
    (o.handles || []).forEach(h => { const [x, y] = h.get(s); g.knob(x, y, h.color); });
    sliders.forEach(([sl, b]) => { b.textContent = fa(s[sl.key]); });
    if (btnBox) [...btnBox.children].forEach((b, i) => b.classList.toggle('on', !!(o.buttons[i].active && o.buttons[i].active(s))));
    if (o.read) read.innerHTML = o.read(s);
  }
  function size() {
    const dpr = devicePixelRatio || 1;
    W = cv.clientWidth;
    if (!W) return;
    H = Math.round(o.equal ? W * (y1 - y0) / (x1 - x0) : Math.min(380, W * (o.ratio || 0.75)));
    cv.style.height = H + 'px';
    cv.width = W * dpr; cv.height = H * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    draw();
  }

  // dragging handles (36px touch radius)
  let drag = null;
  const pos = e => { const r = cv.getBoundingClientRect(); return [e.clientX - r.left, e.clientY - r.top]; };
  cv.addEventListener('pointerdown', e => {
    const [px, py] = pos(e);
    let best = 36;
    (o.handles || []).forEach(h => { const [x, y] = h.get(s); const d = Math.hypot(X(x) - px, Y(y) - py); if (d < best) { best = d; drag = h; } });
    if (drag) { cv.setPointerCapture(e.pointerId); e.preventDefault(); }
  });
  cv.addEventListener('pointermove', e => {
    if (!drag) return;
    const [px, py] = pos(e);
    let x = iX(px), y = iY(py);
    if (o.snap) { x = Math.round(x / o.snap) * o.snap; y = Math.round(y / o.snap) * o.snap; }
    drag.set(s, x, y);
    draw();
  });
  const end = () => { drag = null; };
  cv.addEventListener('pointerup', end);
  cv.addEventListener('pointercancel', end);

  // optional animation: o.tick(s, dt) runs every frame while the card is open
  let raf = 0, last = 0;
  const loop = t => { o.tick(s, Math.min(0.05, (t - (last || t)) / 1000)); last = t; draw(); raf = requestAnimationFrame(loop); };
  if (o.tick) raf = requestAnimationFrame(loop);

  const ro = new ResizeObserver(size);
  ro.observe(cv);
  size(); // draw at once; the observer handles later resizes
  const mq = matchMedia('(prefers-color-scheme: dark)');
  mq.addEventListener('change', draw);
  addEventListener('themechange', draw);
  const stop = () => { cancelAnimationFrame(raf); ro.disconnect(); mq.removeEventListener('change', draw); removeEventListener('themechange', draw); };
  stop.draw = draw; // lets linked pictures that share one state redraw each other
  return stop;
}
