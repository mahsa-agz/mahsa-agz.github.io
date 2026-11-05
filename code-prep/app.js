// Code Prep: TikTok algorithm patterns. Plain JS, no build step.
// Content files call pattern({...}) or mix({...}); start() draws the page.

const P = {};
const pattern = p => { p.kind = 'pattern'; P[p.id] = p; };
const mix = m => { m.kind = 'mix'; P[m.id] = m; };

// the learning path, in order. Ids without content yet show as "soon".
const PATH = [
  'hashmap', 'twopointers', 'window', 'mix1',
  ['prefix', 'Prefix sums', 'Sums of any range in O(1)'],
  ['stack', 'Stack', 'Matching brackets, “next greater”'],
  ['intervals', 'Intervals', 'Sort by start, then merge'],
  ['mix2', 'Mixed 2', 'Patterns 1–6 shuffled', 1],
  ['binary', 'Binary search', 'Halve the search space'],
  ['heap', 'Heap', 'Top-k, scheduling, running median'],
  ['sim', 'Simulation', 'CodeSignal Q3: grids, memory, step-by-step'],
  ['mix3', 'Mixed 3', 'Patterns 1–9 shuffled', 1],
  ['grid', 'Grid DFS / BFS', 'Islands and flood fill'],
  ['graph', 'Graphs & topological sort', 'Course schedule, shortest path'],
  ['design', 'Design', 'LRU Cache and friends'],
  ['dp', 'Dynamic programming', 'Reuse answers to smaller problems'],
  ['mix4', 'Mixed 4', 'Everything shuffled', 1]
];
const NAMES = { hashmap: 'Hash map', twopointers: 'Two pointers', window: 'Sliding window' };
const DIFF = { E: 'Easy', M: 'Medium', H: 'Hard' };

// ---------- small helpers ----------
const $ = s => document.querySelector(s);
const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
// array picture used in the lesson text: A([2,7,11], {0:'l'}, [0,1])
function A(vals, marks = {}, range) {
  return vals.map((v, i) => `<span class="cell${range && i >= range[0] && i <= range[1] ? ' in' : ''}">${v}${marks[i] ? `<i>${marks[i]}</i>` : ''}</span>`).join('');
}
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
  if (!s) return ['', 'new'];
  if (!s.due) return ['ok', 'mastered ✓'];
  if (s.due <= day()) return ['due', 'review today'];
  const n = Math.round((new Date(s.due) - new Date(day())) / 864e5);
  return ['', `review in ${n} day${n > 1 ? 's' : ''}`];
}
const allProblems = () => Object.values(P).flatMap(p => p.problems.map(q => ({ q, p })));
const dueList = () => allProblems().filter(({ q }) => S[q.id] && S[q.id].due && S[q.id].due <= day());

// ---------- pages ----------
function topbar(back) {
  return `<div class="top">${back ? `<a class="back" href="#/">← All patterns</a>` : `<a class="home" href="#/">Code Prep</a>`}
  <div class="end"><button id="theme" aria-label="Light or dark">◐</button>${window.SITE_MENU || ''}</div></div>`;
}

function home() {
  const due = dueList();
  const next = PATH.find(x => typeof x === 'string' && P[x].problems.some(q => !S[q.id]));
  const rows = PATH.map((x, i) => {
    const num = PATH.slice(0, i + 1).filter(y => typeof y === 'string' ? P[y].kind === 'pattern' : !y[3]).length;
    if (typeof x !== 'string') return `<li><div class="soon ${x[3] ? 'mixrow' : ''}"><span class="num">${x[3] ? '★' : num}</span><span class="txt"><b>${x[1]}</b><span>${x[2]} · soon</span></span></div></li>`;
    const p = P[x], tried = p.problems.filter(q => S[q.id]).length, isMix = p.kind === 'mix';
    return `<li><a href="#/p/${x}" class="${isMix ? 'mixrow' : ''} ${tried === p.problems.length ? 'done' : ''}"><span class="num">${isMix ? '★' : num}</span>
      <span class="txt"><b>${p.name}</b><span>${p.sub}</span></span><span class="prog">${tried}/${p.problems.length}</span></a></li>`;
  }).join('');
  return `${topbar()}
  <h1>TikTok coding, by pattern</h1>
  <p class="sub">Learn one pattern, solve real TikTok-tagged LeetCode problems from easy to hard, then mix them.</p>
  <ol class="steps"><li>1. Read the pattern</li><li>2. Try on LeetCode (20 min)</li><li>3. Stuck? Hint → idea → solution</li><li>4. Rewrite it from memory</li><li>5. Mark it</li></ol>
  <div class="card today">
    <h3>Today</h3>
    ${due.length ? `<p>Review first (${due.length}):</p><ul class="due">${due.map(({ q, p }) => `<li><a href="#/p/${p.id}/${q.id}">${q.t}</a> <span class="note">· ${p.name}</span></li>`).join('')}</ul>` : '<p class="note">No reviews due.</p>'}
    <div class="row">${next ? `<a class="btn main" href="#/p/${next}">Continue: ${P[next].name} →</a>` : '<span>All available patterns done 🎉</span>'}</div>
  </div>
  <h2>Path</h2><ol class="path">${rows}</ol>
  <h2>About the TikTok test</h2>
  <div class="card"><ul>
    <li><b>CodeSignal, 4 problems in about 70 min</b>, proctored (camera + screen). Score out of 600; hidden tests decide it.</li>
    <li><b>Shape:</b> Q1–Q2 easy (strings, arrays, counting) · Q3 simulation (grids, memory blocks) · Q4 a data-structure problem (binary search, heap, hash map).</li>
    <li>TikTok uses <b>your first score</b> for the season, so don't take it before you can finish a timed mock.</li>
    <li>Problem lists come from LeetCode's TikTok tag (317 problems; mostly Medium). The number next to each problem is how often TikTok asked it (100 = most).</li>
  </ul></div>`;
}

function problemCard(q, p) {
  const [cls, txt] = status(q.id);
  const isMix = p.kind === 'mix';
  return `<article class="card prob" id="q-${q.id}" data-id="${q.id}">
    <header><span class="tag ${q.d}">${DIFF[q.d]}</span><h3>${q.t}</h3><span class="freq">TikTok ${q.f}</span><span class="st ${cls}">${txt}</span></header>
    <p class="plain">${q.plain}</p>
    ${isMix ? `<div class="guess">Which pattern? ${['hashmap', 'twopointers', 'window'].map(k => `<button data-g="${k}">${NAMES[k]}</button>`).join('')}</div><div class="tell" hidden></div>` : ''}
    <div class="acts">
      <a class="btn main" href="https://leetcode.com/problems/${q.id}/" target="_blank" rel="noopener">Solve on LeetCode ↗</a>
      <button data-r="hint">Hint</button><button data-r="idea">Key idea</button><button data-r="sol">Solution</button>
    </div>
    <div class="rev" data-p="hint" hidden><b class="lbl">Hint</b>${q.hint}</div>
    <div class="rev" data-p="idea" hidden><b class="lbl">Key idea</b><p>${q.idea}</p><b class="lbl">Traps</b><ul>${q.traps.map(t => `<li>${t}</li>`).join('')}</ul></div>
    <div class="rev" data-p="sol" hidden><b class="lbl">Solution · ${q.O}</b>${code(q.code)}<p class="note">Now hide it and write it again on LeetCode from memory.</p></div>
    <div class="mark">Done? <button data-m="1">✓ Solved alone</button><button data-m="0">↻ Needed help</button></div>
  </article>`;
}

function page(id) {
  const p = P[id];
  if (!p) return home();
  if (p.kind === 'mix') return `${topbar(1)}<h1>${p.name}</h1><p class="sub">${p.sub}</p>
    <p class="note">The pattern name is hidden, as in the real test. Read the problem, pick a pattern, then solve.</p>
    <h2>Problems · easy → hard</h2>${p.problems.map(q => problemCard(q, p)).join('')}`;
  const nextId = PATH[PATH.indexOf(id) + 1];
  return `${topbar(1)}
  <h1>${p.n}. ${p.name}</h1><p class="sub">${p.sub}</p>
  <h2>Why it works</h2><div class="card">${p.why}${p.viz || ''}</div>
  <h2>Spot it when you read</h2><div class="card"><ul class="spot">${p.spot.map(s => `<li>${s}</li>`).join('')}</ul></div>
  <h2>Template</h2>${code(p.template)}
  <div class="card tiktok"><b>TikTok note.</b> ${p.tiktok}</div>
  <h2>Problems · easy → hard</h2>${p.problems.map(q => problemCard(q, p)).join('')}
  ${typeof nextId === 'string' ? `<p><a class="btn" href="#/p/${nextId}">Next: ${P[nextId].name} →</a></p>` : ''}`;
}

// ---------- routing + clicks ----------
function render() {
  const [, , id, qid] = location.hash.split('/');
  $('#app').innerHTML = id ? page(id) : home();
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
    tell.innerHTML = `${b.dataset.g === q.p ? '✓ Right.' : `✗ It's <b>${NAMES[q.p]}</b>.`} ${q.tell}`;
  }
});

function start() { addEventListener('hashchange', render); render(); }
