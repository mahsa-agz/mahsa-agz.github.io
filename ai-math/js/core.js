// ---------- Helpers ----------
const fa = n => String(Math.round(n * 100) / 100).replace('-', '−').replace('.', '٫').replace(/\d/g, d => '۰۱۲۳۴۵۶۷۸۹'[d]);
const E = s => `<span class="eq">${s}</span>`;
const V = (x, y) => `<span class="v">[${fa(x)}, ${fa(y)}]</span>`;
const EN = s => `<span class="en">(${s})</span>`;
const $ = s => document.querySelector(s);

// ---------- Lesson registry ----------
// lesson({ id, node, title, en, parts:[{name, cards}] | cards, sheet })
const LESSONS = {};
function lesson(L) {
  if (!L.parts) L.parts = [{ name: '', cards: L.cards }];
  LESSONS[L.id] = L;
}

// ---------- Progress (per device) ----------
const KEY = 'ai-math-v2';
let done = new Set();
try { done = new Set(JSON.parse(localStorage.getItem(KEY)) || []); } catch (e) {}
const saveDone = () => { try { localStorage.setItem(KEY, JSON.stringify([...done])); } catch (e) {} };
const pk = (id, p) => id + '/' + p;
const started = id => LESSONS[id].parts.some((_, p) => done.has(pk(id, p)));
const rows = ch => ch.lessons.flatMap(id => LESSONS[id].parts.map((_, p) => ({ id, p })));

// ---------- Topic graph ----------
function pathUp(node) { // [node, ..., GOAL], shortest
  const prev = { [GOAL]: null }, q = [GOAL];
  while (q.length) {
    const a = q.shift();
    if (a === node) break;
    for (const [x, y] of G_LINKS) if (x === a && !(y in prev)) { prev[y] = a; q.push(y); }
  }
  if (!(node in prev)) return null;
  const chain = [];
  for (let n = node; n; n = prev[n]) chain.push(n);
  return chain;
}
function ancestors(node) {
  const seen = new Set(), q = [node];
  while (q.length) { const b = q.shift(); for (const [x, y] of G_LINKS) if (y === b && !seen.has(x)) { seen.add(x); q.push(x); } }
  return [...seen];
}
const nodeName = id => (G_NODES[id] || [id])[0];
const isMission = L => (G_NODES[L.node] || [])[2] === 'q';

// ---------- Shell ----------
const app = $('#app'), foot = $('#foot'), go = $('#go');
let stopW = null;
const stop = () => { if (stopW) { stopW(); stopW = null; } };

function home() {
  stop(); foot.hidden = true;
  app.innerHTML = `
    <div class="topline"><button class="nb" id="nb">دفترچه‌ی خلاصه</button><button class="theme" id="theme" aria-label="روشن یا تیره">◐</button></div>
    <div class="hello"><h1>ریاضی هوش مصنوعی</h1><p>هر روز یک درس کوتاه. از پایه شروع می‌کنیم.</p></div>
    ${COURSE.map(chapterHTML).join('')}`;
  app.querySelectorAll('[data-id]').forEach(b => b.onclick = () => start(b.dataset.id, +b.dataset.p));
  $('#theme').onclick = toggleTheme;
  $('#nb').onclick = notebook;
  scrollTo(0, 0);
}
function chapterHTML(ch, k) {
  const r = rows(ch), n = r.filter(x => done.has(pk(x.id, x.p))).length, total = r.length + ch.soon.length;
  const items = r.map((x, i) => {
    const L = LESSONS[x.id], isDone = done.has(pk(x.id, x.p));
    const open = i === 0 || done.has(pk(r[i - 1].id, r[i - 1].p));
    const name = L.parts.length > 1 ? `${L.title}: ${L.parts[x.p].name}` : L.title;
    return `<button class="lesson ${isDone ? 'done' : open ? 'open' : 'locked'}" ${open || isDone ? `data-id="${x.id}" data-p="${x.p}"` : 'disabled'}>
      <span class="num">${isDone ? '✓' : fa(i + 1)}</span><span class="txt"><b>${name}</b><span class="en">${L.en}</span></span>
      <span class="state">${isDone ? 'دوباره' : open ? 'شروع' : 'قفل'}</span></button>`;
  }).join('') + ch.soon.map(([f, e], j) => `<div class="lesson locked"><span class="num">${fa(r.length + j + 1)}</span>
      <span class="txt"><b>${f}</b><span class="en">${e}</span></span><span class="state">به‌زودی</span></div>`).join('');
  return `<section class="chapter"><div class="unit"><small>فصل ${fa(k + 1)}</small><h2>${ch.title} <span class="en">(${ch.en})</span></h2>
    <small>${fa(n)} از ${fa(total)} درس</small><div class="bar"><i style="width:${(100 * n) / total}%"></i></div></div>
    <div class="path">${items}</div></section>`;
}

// ---------- Lesson player ----------
function reviewCards(id) {
  const pool = Object.values(LESSONS).filter(L => L.id !== id && started(L.id))
    .flatMap(L => L.parts.flatMap(p => p.cards.filter(c => c.t === 'quiz')));
  return pool.sort(() => Math.random() - 0.5).slice(0, 2).map(c => ({ ...c, review: true }));
}
function start(id, p) {
  const L = LESSONS[id], last = p === L.parts.length - 1;
  const seq = [...(p === 0 ? reviewCards(id) : []), ...L.parts[p].cards,
    ...(last ? [...(isMission(L) ? [] : [{ t: 'used' }]), ...(L.sheet ? [{ t: 'sheet' }] : [])] : [])];
  show(L, p, seq, 0);
}
function goalBar(L) {
  const chain = pathUp(L.node);
  if (!chain) return '';
  return `<div class="goal"><span>تو اینجایی:</span>${chain.map((n, i) =>
    `<span class="g ${i ? '' : 'now'}">${nodeName(n)}</span>`).join('<span>←</span>')}</div>`;
}
function show(L, p, seq, ci) {
  stop();
  if (ci >= seq.length) return finish(L, p);
  const c = seq[ci];
  app.innerHTML = `<div class="top"><button class="close" id="x" aria-label="بستن">✕</button>
    <div class="prog"><i style="width:${(100 * ci) / seq.length}%"></i></div></div>${goalBar(L)}<div class="card" id="card"></div>`;
  $('#x').onclick = home;
  foot.hidden = false;
  go.textContent = ci === seq.length - 1 ? 'تمام' : 'ادامه';
  go.disabled = false;
  go.onclick = () => show(L, p, seq, ci + 1);
  const r = CARDS[c.t](c, $('#card'), { L, lock: () => { go.disabled = true; }, unlock: () => { go.disabled = false; } });
  if (typeof r === 'function') stopW = r;
  scrollTo(0, 0);
}
function finish(L, p) {
  done.add(pk(L.id, p)); saveDone();
  const ch = COURSE.find(c => c.lessons.includes(L.id)), r = rows(ch);
  const next = r[r.findIndex(x => x.id === L.id && x.p === p) + 1];
  const NL = next && LESSONS[next.id];
  const sheetNote = p === L.parts.length - 1 && L.sheet ? '<p>کارت خلاصه‌ی این درس به <b>دفترچه</b> اضافه شد.</p>' : '';
  app.innerHTML = `<div class="end"><div class="big">✓</div><h2>آفرین! «${L.title}» ${L.parts.length > 1 ? `(${L.parts[p].name})` : ''} تمام شد.</h2>${sheetNote}
    <p>${NL ? `بعدی: <b>${NL.title}${NL.parts.length > 1 ? ': ' + NL.parts[next.p].name : ''}</b>` : 'درس‌های بعدیِ این فصل به‌زودی اضافه می‌شوند.'}</p></div>`;
  go.textContent = NL ? 'برو به بعدی' : 'بازگشت به فهرست';
  go.disabled = false;
  go.onclick = () => (NL ? start(next.id, next.p) : home());
}

// ---------- Notebook (cheat sheets) ----------
function notebook() {
  stop(); foot.hidden = true;
  const ls = COURSE.flatMap(c => c.lessons).map(id => LESSONS[id]).filter(L => L.sheet);
  const have = ls.filter(L => started(L.id));
  app.innerHTML = `<div class="top"><button class="close" id="x" aria-label="بستن">✕</button><h2 style="font-size:20px">دفترچه‌ی خلاصه <span class="en">(Cheat Sheet)</span></h2></div>
    <div class="card">${have.length ? have.map(sheetHTML).join('') : '<p class="box">هنوز کارتی نیست. هر درسی را که شروع کنید، خلاصه‌اش اینجا می‌آید.</p>'}
    ${ls.length > have.length ? `<p style="color:var(--muted)">${fa(ls.length - have.length)} کارت دیگر بعد از درس‌های بعدی باز می‌شود.</p>` : ''}</div>`;
  $('#x').onclick = home;
  scrollTo(0, 0);
}
function sheetHTML(L) {
  const s = L.sheet;
  return `<div class="sheet"><div><b>${L.title}</b> <span class="en">(${L.en})</span></div>
    <div class="key">${s.one}</div>
    ${s.f ? `<div class="read">${E(s.f)}</div>` : ''}
    ${s.rules ? `<ul>${s.rules.map(x => `<li>${x}</li>`).join('')}</ul>` : ''}
    ${s.use ? `<p><b>کجا به کار می‌آید:</b> ${s.use}</p>` : ''}
    ${s.mistake ? `<p><b class="bad">اشتباه رایج:</b> ${s.mistake}</p>` : ''}</div>`;
}

function toggleTheme() {
  const r = document.documentElement;
  const dark = r.dataset.theme ? r.dataset.theme === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches;
  r.dataset.theme = dark ? 'light' : 'dark';
  dispatchEvent(new Event('themechange'));
}
