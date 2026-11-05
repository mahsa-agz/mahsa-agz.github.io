// Code Prep: TikTok algorithm patterns. Plain JS, no build step.
// Content files call pattern({...}) or mix({...}); start() draws the page.

const P = {};
const pattern = p => { p.kind = 'pattern'; P[p.id] = p; };
const mix = m => { m.kind = 'mix'; P[m.id] = m; };

// the learning path, in order. Ids without content yet show as "soon".
const PATH = [
  'hashmap', 'twopointers', 'window', 'mix1',
  ['prefix', 'جمع پیشوندی (Prefix sum)', 'جمع هر بازه در O(1)'],
  ['stack', 'پشته (Stack)', 'پرانتزها، «بزرگ‌ترِ بعدی»'],
  ['intervals', 'بازه‌ها (Intervals)', 'مرتب کن، بعد ادغام کن'],
  ['mix2', 'ترکیبی ۲', 'الگوهای ۱ تا ۶ قاطی', 1],
  ['binary', 'جست‌وجوی دودویی (Binary search)', 'هر بار نصفِ فضا را دور بریز'],
  ['heap', 'هیپ (Heap)', 'k تای برتر، زمان‌بندی، میانه'],
  ['sim', 'شبیه‌سازی (Simulation)', 'سؤال ۳ کدسیگنال: جدول، حافظه، قدم‌به‌قدم'],
  ['mix3', 'ترکیبی ۳', 'الگوهای ۱ تا ۹ قاطی', 1],
  ['grid', 'جست‌وجو در جدول (DFS / BFS)', 'جزیره‌ها و پر کردن ناحیه'],
  ['graph', 'گراف و ترتیب توپولوژیک', 'برنامه‌ی درس‌ها، کوتاه‌ترین مسیر'],
  ['design', 'طراحی (Design)', 'LRU Cache و مشابه‌ها'],
  ['dp', 'برنامه‌ریزی پویا (DP)', 'جوابِ مسئله‌های کوچک‌تر را دوباره استفاده کن'],
  ['mix4', 'ترکیبی ۴', 'همه‌چیز قاطی', 1]
];
const NAMES = { hashmap: 'هش‌مپ (Hash map)', twopointers: 'دو اشاره‌گر (Two pointers)', window: 'پنجره‌ی لغزان (Sliding window)' };
const DIFF = { E: 'آسان', M: 'متوسط', H: 'سخت' };

// ---------- small helpers ----------
const $ = s => document.querySelector(s);
const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
// array picture used in the lesson text: A([2,7,11], {0:'l'}, [0,1])
// A(values, {index: label}, [from, to] highlighted, Set of greyed-out indexes)
function A(vals, marks = {}, range, dim) {
  return vals.map((v, i) => `<span class="cell${range && i >= range[0] && i <= range[1] ? ' in' : ''}${dim && dim.has(i) ? ' out' : ''}">${esc(v)}${marks[i] ? `<i>${marks[i]}</i>` : ''}</span>`).join('');
}
const L = s => `<span dir="ltr">${s}</span>`; // keep math left-to-right inside Persian text
const nums = s => String(s).split(/[,\s]+/).filter(Boolean).map(Number).filter(x => !isNaN(x)).slice(0, 14);
// tiny Python highlighter: comments, strings, numbers, keywords, function names
const KW = /^(def|class|return|if|elif|else|for|while|in|not|and|or|is|None|True|False|import|from|as|break|continue|pass|lambda|self|yield|with|del)$/;
function py(src) {
  return src.replace(/(#[^\n]*)|("[^"\n]*"|'[^'\n]*')|\b(\d+)\b|\b([A-Za-z_]\w*)(\s*\()?|([&<>])/g, (m, com, str, num, word, call, ch) => {
    if (com) return `<span class="c">${esc(com)}</span>`;
    if (str) return `<span class="s">${esc(str)}</span>`;
    if (num) return `<span class="n">${num}</span>`;
    if (ch) return esc(ch);
    if (KW.test(word)) return `<span class="k">${word}</span>${call || ''}`;
    if (call) return `<span class="f">${word}</span>${call}`;
    return word;
  });
}
const code = s => `<pre><code>${py(s)}</code></pre>`;

// ---------- progress: spaced review, saved in this browser ----------
// solved alone -> back in 3, then 7, then 21 days, then mastered. needed help -> back tomorrow.
const KEY = 'codeprep.v1';
let S = {};
try { S = JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) { S = {}; }
const save = () => { try { localStorage.setItem(KEY, JSON.stringify(S)); } catch (e) {} };
const day = (d = 0) => { const t = new Date(); t.setDate(t.getDate() + d); return t.toLocaleDateString('en-CA'); };
const GAPS = [3, 7, 21];
function markProblem(id, alone) {
  const s = S[id] || { lv: 0 };
  if (alone) { s.due = s.lv < GAPS.length ? day(GAPS[s.lv]) : null; s.lv++; }
  else { s.lv = 0; s.due = day(1); }
  S[id] = s; save();
}
function status(id) {
  const s = S[id];
  if (!s) return ['', 'جدید'];
  if (!s.due) return ['ok', 'مسلط شدی ✓'];
  if (s.due <= day()) return ['due', 'مرور امروز'];
  const n = Math.round((new Date(s.due) - new Date(day())) / 864e5);
  return ['', `مرور ${n} روز دیگر`];
}
const allProblems = () => Object.values(P).flatMap(p => p.problems.map(q => ({ q, p })));
const dueList = () => allProblems().filter(({ q }) => S[q.id] && S[q.id].due && S[q.id].due <= day());

// ---------- pages ----------
function topbar(back) {
  return `<div class="top">${back ? `<a class="back" href="#/">→ همه‌ی الگوها</a>` : `<a class="home" href="#/">Code Prep</a>`}
  <div class="end"><button id="theme" aria-label="روشن یا تیره">◐</button>${window.SITE_MENU || ''}</div></div>`;
}

function home() {
  const due = dueList();
  const next = PATH.find(x => typeof x === 'string' && P[x].problems.some(q => !S[q.id]));
  const rows = PATH.map((x, i) => {
    const num = PATH.slice(0, i + 1).filter(y => typeof y === 'string' ? P[y].kind === 'pattern' : !y[3]).length;
    if (typeof x !== 'string') return `<li><div class="soon ${x[3] ? 'mixrow' : ''}"><span class="num">${x[3] ? '★' : num}</span><span class="txt"><b>${x[1]}</b><span>${x[2]} · به‌زودی</span></span></div></li>`;
    const p = P[x], tried = p.problems.filter(q => S[q.id]).length, isMix = p.kind === 'mix';
    return `<li><a href="#/p/${x}" class="${isMix ? 'mixrow' : ''} ${tried === p.problems.length ? 'done' : ''}"><span class="num">${isMix ? '★' : num}</span>
      <span class="txt"><b>${p.name}</b><span>${p.sub}</span></span><span class="prog">${tried}/${p.problems.length}</span></a></li>`;
  }).join('');
  return `${topbar()}
  <h1>کدنویسیِ تیک‌تاک، الگو به الگو</h1>
  <p class="sub">هر بار یک الگو را یاد بگیر، سؤال‌های واقعیِ تیک‌تاک در لیت‌کد را از آسان تا سخت حل کن، بعد آن‌ها را قاطی تمرین کن.</p>
  <ol class="steps"><li>۱. الگو را بخوان</li><li>۲. در لیت‌کد امتحان کن (۲۰ دقیقه)</li><li>۳. گیر کردی؟ راهنما ← ایده ← جواب</li><li>۴. از حفظ دوباره بنویس</li><li>۵. علامت بزن</li></ol>
  <div class="card today">
    <h3>امروز</h3>
    ${due.length ? `<p>اول مرور (${due.length}):</p><ul class="due">${due.map(({ q, p }) => `<li><a href="#/p/${p.id}/${q.id}" dir="ltr">${q.t}</a> <span class="note">· ${p.name}</span></li>`).join('')}</ul>` : '<p class="note">امروز مروری نداری.</p>'}
    <div class="row">${next ? `<a class="btn main" href="#/p/${next}">ادامه: ${P[next].name} ←</a>` : '<span>همه‌ی الگوهای موجود تمام شد 🎉</span>'}</div>
  </div>
  <h2>مسیر</h2><ol class="path">${rows}</ol>
  <h2>درباره‌ی آزمون تیک‌تاک</h2>
  <div class="card"><ul>
    <li><b>کدسیگنال (CodeSignal)، ۴ سؤال در حدود ۷۰ دقیقه</b>، با نظارت (دوربین و صفحه). نمره از ۶۰۰ است و تست‌های پنهان (hidden tests) تعیینش می‌کنند.</li>
    <li><b>شکل آزمون:</b> سؤال ۱ و ۲ آسان (رشته، آرایه، شمارش) · سؤال ۳ شبیه‌سازی (جدول، بلوک‌های حافظه) · سؤال ۴ یک ساختار داده (جست‌وجوی دودویی، هیپ، هش‌مپ).</li>
    <li>تیک‌تاک فقط <b>اولین نمره‌ات</b> را برای آن فصل استخدام حساب می‌کند. پس تا وقتی یک آزمون آزمایشیِ زمان‌دار را تمام نکرده‌ای، شرکت نکن.</li>
    <li>سؤال‌ها از برچسب تیک‌تاک در لیت‌کد آمده‌اند (۳۱۷ سؤال، بیشترشان متوسط). عدد کنار هر سؤال نشان می‌دهد تیک‌تاک چقدر آن را پرسیده (۱۰۰ = بیشترین).</li>
  </ul></div>`;
}

function problemCard(q, p) {
  const [cls, txt] = status(q.id);
  const isMix = p.kind === 'mix';
  return `<article class="card prob" id="q-${q.id}" data-id="${q.id}">
    <header><span class="tag ${q.d}">${DIFF[q.d]}</span><h3 dir="ltr">${q.t}</h3><span class="freq">تیک‌تاک ${q.f}</span><span class="st ${cls}">${txt}</span></header>
    <p class="plain">${q.plain}</p>
    ${isMix ? `<div class="guess">کدام الگو؟ ${['hashmap', 'twopointers', 'window'].map(k => `<button data-g="${k}">${NAMES[k]}</button>`).join('')}</div><div class="tell" hidden></div>` : ''}
    <div class="acts">
      <a class="btn main" href="https://leetcode.com/problems/${q.id}/" target="_blank" rel="noopener">حل در لیت‌کد ↗</a>
      <button data-r="hint">راهنما</button><button data-r="idea">ایده‌ی اصلی</button><button data-r="sol">جواب</button>
    </div>
    <div class="rev" data-p="hint" hidden><b class="lbl">راهنما</b>${q.hint}</div>
    <div class="rev" data-p="idea" hidden><b class="lbl">ایده‌ی اصلی</b><p>${q.idea}</p><b class="lbl">دام‌ها</b><ul>${q.traps.map(t => `<li>${t}</li>`).join('')}</ul></div>
    <div class="rev" data-p="sol" hidden><b class="lbl">جواب · <span dir="ltr">${q.O}</span></b>${code(q.code)}<p class="note">حالا ببندش و در لیت‌کد از حفظ دوباره بنویس.</p></div>
    <div class="mark">تمام شد؟ <button data-m="1">✓ خودم حل کردم</button><button data-m="0">↻ کمک لازم شد</button></div>
  </article>`;
}

function page(id) {
  const p = P[id];
  if (!p) return home();
  if (p.kind === 'mix') return `${topbar(1)}<h1>${p.name}</h1><p class="sub">${p.sub}</p>
    <p class="note">مثل آزمون واقعی، اسم الگو پنهان است. سؤال را بخوان، الگو را انتخاب کن، بعد حل کن.</p>
    <h2>سؤال‌ها · آسان ← سخت</h2>${p.problems.map(q => problemCard(q, p)).join('')}`;
  const nextId = PATH[PATH.indexOf(id) + 1];
  return `${topbar(1)}
  <h1>${p.n}. ${p.name}</h1><p class="sub">${p.sub}</p>
  ${p.story ? `<h2>داستانش: چرا اختراع شد؟</h2><div class="card">${p.story}</div>` : ''}
  <h2>چرا کار می‌کند؟</h2><div class="card">${p.why}${p.viz || ''}</div>
  ${p.uses ? `<h2>به درد چه سؤال‌هایی می‌خورد؟</h2><div class="card">${p.uses}</div>` : ''}
  ${p.demo ? demoBox(p) : ''}
  <h2>از کجا بفهمی همین الگوست؟</h2><div class="card"><ul class="spot">${p.spot.map(s => `<li>${s}</li>`).join('')}</ul></div>
  <h2>قالب کد (Template)</h2>${code(p.template)}
  <div class="card tiktok"><b>نکته‌ی تیک‌تاک.</b> ${p.tiktok}</div>
  <h2>سؤال‌ها · آسان ← سخت</h2>${p.problems.map(q => problemCard(q, p)).join('')}
  ${typeof nextId === 'string' ? `<p><a class="btn" href="#/p/${nextId}">بعدی: ${P[nextId].name} ←</a></p>` : ''}`;
}

// ---------- interactive step-through ----------
let D = null; // { p, steps, i }
function demoBox(p) {
  return `<h2>خودت امتحان کن</h2><div class="card demo">
    <h3>${p.demo.title}</h3>
    <div class="fields">${p.demo.fields.map(([k, v]) => `<label>${k}<input data-k="${k}" value="${esc(v)}" dir="ltr" spellcheck="false"></label>`).join('')}</div>
    <div class="stage"></div>
    <div class="acts"><button data-d="prev">→ قبلی</button><button data-d="next" class="btn main">بعدی ←</button><button data-d="reset">از اول</button><span class="note" id="dstep"></span></div>
  </div>`;
}
function demoRun() {
  const box = $('.demo');
  if (!box) { D = null; return; }
  const p = P[location.hash.split('/')[2]], f = {};
  box.querySelectorAll('input').forEach(x => { f[x.dataset.k] = x.value; });
  let steps;
  try { steps = p.demo.run(f); } catch (e) { steps = [{ cells: '', note: 'ورودی را بررسی کن.' }]; }
  D = { steps, i: 0 }; demoDraw();
}
function demoDraw() {
  const s = D.steps[D.i];
  $('.demo .stage').innerHTML = `<div class="vrow">${s.cells}</div><div class="vnote">${s.note}</div>${s.state ? `<div class="vrow">${s.state}</div>` : ''}`;
  $('#dstep').textContent = `قدم ${D.i + 1} از ${D.steps.length}`;
}
document.addEventListener('input', e => { if (e.target.closest('.demo')) demoRun(); });

// ---------- routing + clicks ----------
function render() {
  const [, , id, qid] = location.hash.split('/');
  $('#app').innerHTML = id ? page(id) : home();
  demoRun();
  const el = qid && document.getElementById('q-' + qid);
  if (el) { el.scrollIntoView({ block: 'start' }); el.classList.add('flash'); } else scrollTo(0, 0);
}

document.addEventListener('click', e => {
  const b = e.target.closest('button');
  if (!b) return;
  if (b.id === 'theme') {
    const dark = document.documentElement.getAttribute('data-theme') === 'dark' ||
      (!document.documentElement.getAttribute('data-theme') && matchMedia('(prefers-color-scheme: dark)').matches);
    const t = dark ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', t);
    try { localStorage.setItem('theme', t); } catch (err) {}
    return;
  }
  if (b.dataset.d && D) {
    D.i = b.dataset.d === 'reset' ? 0 : Math.max(0, Math.min(D.steps.length - 1, D.i + (b.dataset.d === 'next' ? 1 : -1)));
    demoDraw(); return;
  }
  const card = b.closest('.prob');
  if (!card) return;
  const id = card.dataset.id;
  if (b.dataset.r) { // show / hide hint, idea, solution
    const box = card.querySelector(`[data-p="${b.dataset.r}"]`);
    box.hidden = !box.hidden; b.classList.toggle('on', !box.hidden);
  } else if (b.dataset.m) { // mark result
    markProblem(id, b.dataset.m === '1');
    const [cls, txt] = status(id), st = card.querySelector('.st');
    st.className = 'st ' + cls; st.textContent = txt;
    card.querySelectorAll('[data-m]').forEach(x => x.classList.toggle('on', x === b));
  } else if (b.dataset.g) { // mixed: guess the pattern
    const q = allProblems().find(x => x.q.id === id).q;
    card.querySelectorAll('[data-g]').forEach(x => { x.classList.remove('right', 'wrong'); if (x.dataset.g === q.p) x.classList.add('right'); });
    if (b.dataset.g !== q.p) b.classList.add('wrong');
    const tell = card.querySelector('.tell');
    tell.hidden = false;
    tell.innerHTML = `${b.dataset.g === q.p ? '✓ درست است.' : `✗ این <b>${NAMES[q.p]}</b> است.`} ${q.tell}`;
  }
});

function start() { addEventListener('hashchange', render); render(); }
