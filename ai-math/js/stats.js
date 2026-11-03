// ---------- Statistics helpers + drawing on a plane ----------
const ST = {
  sum: a => a.reduce((s, x) => s + x, 0),
  mean: a => ST.sum(a) / a.length,
  sorted: a => [...a].sort((x, y) => x - y),
  median: a => { const s = ST.sorted(a), n = s.length, h = n >> 1; return n % 2 ? s[h] : (s[h - 1] + s[h]) / 2; },
  // beginner method: Q1 = median of the lower half, Q3 = median of the upper half (middle value left out when n is odd)
  quartiles: a => { const s = ST.sorted(a), n = s.length, h = n >> 1; return [ST.median(s.slice(0, h)), ST.median(s), ST.median(s.slice(n % 2 ? h + 1 : h))]; },
  variance: a => { const m = ST.mean(a); return ST.sum(a.map(x => (x - m) ** 2)) / a.length; }, // population variance (divide by n)
  std: a => Math.sqrt(ST.variance(a)),
  normal: (x, m, sd) => Math.exp(-(((x - m) / sd) ** 2) / 2) / (sd * Math.sqrt(2 * Math.PI)),
  hist: (a, lo, hi, n) => { const c = Array(n).fill(0), w = (hi - lo) / n; a.forEach(x => { const i = Math.floor((x - lo) / w); if (i >= 0 && i < n) c[i]++; else if (x === hi) c[n - 1]++; }); return c; },
  // dot plot: equal values stack upward -> [{x, y}] with y = 1, 2, 3...
  stack: (a, round = 1) => { const seen = {}; return a.map(x => { const k = Math.round(x / round) * round; seen[k] = (seen[k] || 0) + 1; return { x: k, y: seen[k] }; }); },
  // random normal number (Box-Muller)
  randn: (m = 0, sd = 1) => m + sd * Math.sqrt(-2 * Math.log(1 - Math.random())) * Math.cos(2 * Math.PI * Math.random()),
};

// boxplot centred at height y with half-height h
function drawBox(g, a, y, h, color = 'blue') {
  const [q1, q2, q3] = ST.quartiles(a), s = ST.sorted(a);
  g.line(s[0], y, q1, y, color, 2); g.line(q3, y, s[s.length - 1], y, color, 2);
  g.line(s[0], y - h / 2, s[0], y + h / 2, color, 2); g.line(s[s.length - 1], y - h / 2, s[s.length - 1], y + h / 2, color, 2);
  g.rect(q1, y - h, q3, y + h, color, 0.18);
  g.line(q1, y - h, q3, y - h, color, 2); g.line(q1, y + h, q3, y + h, color, 2);
  g.line(q1, y - h, q1, y + h, color, 2); g.line(q3, y - h, q3, y + h, color, 2);
  g.line(q2, y - h, q2, y + h, 'ink', 3);
}
// histogram bars from lo to hi in n bins; scale = height per count
function drawHist(g, a, lo, hi, n, color = 'blue', scale = 1) {
  const c = ST.hist(a, lo, hi, n), w = (hi - lo) / n;
  c.forEach((k, i) => { if (k) { g.rect(lo + i * w, 0, lo + (i + 1) * w, k * scale, color, 0.75); g.line(lo + i * w, k * scale, lo + (i + 1) * w, k * scale, color, 2); } });
  return c;
}
// small triangle under the axis marking a value (e.g. the mean as a balance point)
function drawMarker(g, x, y, color = 'red', label) {
  const c = g.ctx, px = g.X(x), py = g.Y(y);
  c.fillStyle = g.css(color); c.beginPath(); c.moveTo(px, py); c.lineTo(px - 9, py + 14); c.lineTo(px + 9, py + 14); c.closePath(); c.fill();
  if (label) g.text(x, y, label, color, 'center', 26);
}
