/* DS Handbook: tabs, three languages, search, intra links, 30-day plan with Colab links, daily theory flashcards. */
(() => {
  "use strict";
  const TABS = ["plan", "algo", "sql", "stats", "ai", "cheat", "qa", "resources"];
  const CONTENT_TABS = ["algo", "sql", "stats", "ai", "cheat", "resources"];
  const LANGS = ["en", "fa", "ko"];
  const AREAS = ["algorithms", "sql", "stats", "ai", "qa"];
  const state = {
    lang: "en", tab: "plan", qaDay: 1, showPatterns: false,
    content: {}, ui: {}, plan: null, days: null,
  };
  const $ = (s, el = document) => el.querySelector(s);
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  // ------------------------------------------------------------------ browser storage (language choice only)
  const local = {
    get(k, d) { try { const v = localStorage.getItem("dsh_" + k); return v ? JSON.parse(v) : d; } catch { return d; } },
    set(k, v) { try { localStorage.setItem("dsh_" + k, JSON.stringify(v)); } catch { /* storage blocked */ } },
  };

  // ------------------------------------------------------------------ loading content
  async function getJSON(path) {
    const r = await fetch(path);
    if (!r.ok) throw new Error(path + " " + r.status);
    return r.json();
  }
  async function loadLang(lang) {
    if (state.content[lang]) return;
    const out = {};
    const files = CONTENT_TABS.concat(["days", "ui"]);
    await Promise.all(files.map(async (f) => {
      try { out[f] = await getJSON(`content/${lang}/${f}.json`); }
      catch { out[f] = null; }
    }));
    state.content[lang] = out;
  }
  const C = (tab) => (state.content[state.lang] && state.content[state.lang][tab]) || (state.content.en && state.content.en[tab]) || null;
  const T = (key, fallback) => {
    const ui = C("ui") || {};
    const en = (state.content.en && state.content.en.ui) || {};
    return ui[key] || en[key] || fallback || key;
  };
  const isFallback = (tab) => state.lang !== "en" && !(state.content[state.lang] && state.content[state.lang][tab]);

  // all sections across tabs for the current language: id -> {tab, section}
  function sectionIndex() {
    const idx = {};
    for (const tab of CONTENT_TABS) {
      const c = C(tab);
      if (!c) continue;
      for (const s of c.sections || []) idx[s.id] = { tab, s };
    }
    return idx;
  }
  const titleOf = (id) => { const hit = sectionIndex()[id]; return hit ? hit.s.title : id; };

  // ------------------------------------------------------------------ markdown
  function md(text) {
    const html = window.marked ? window.marked.parse(String(text || ""), { gfm: true, breaks: false }) : "<p>" + esc(text) + "</p>";
    return html;
  }
  function decorate(root) {
    root.querySelectorAll("table").forEach((t) => {
      if (t.parentElement && t.parentElement.classList.contains("table-wrap")) return;
      const w = document.createElement("div"); w.className = "table-wrap";
      t.parentNode.insertBefore(w, t); w.appendChild(t);
    });
    root.querySelectorAll("pre code").forEach((c) => {
      if (window.hljs) { try { window.hljs.highlightElement(c); } catch { /* plain */ } }
      const pre = c.parentElement;
      if (pre.querySelector(".copy")) return;
      const b = document.createElement("button");
      b.className = "copy"; b.type = "button"; b.textContent = T("copy", "Copy");
      b.addEventListener("click", () => {
        const done = () => { b.textContent = T("copied", "Copied"); setTimeout(() => (b.textContent = T("copy", "Copy")), 1200); };
        try { navigator.clipboard.writeText(c.innerText).then(done, () => selectText(c)); } catch { selectText(c); }
      });
      pre.appendChild(b);
    });
    root.querySelectorAll("a[href]").forEach((a) => {
      const href = a.getAttribute("href");
      if (href.startsWith("#")) a.addEventListener("click", (e) => { e.preventDefault(); go(href.slice(1)); });
      else { a.target = "_blank"; a.rel = "noopener"; }
    });
  }
  function selectText(el) { const r = document.createRange(); r.selectNodeContents(el); const s = getSelection(); s.removeAllRanges(); s.addRange(r); }

  // ------------------------------------------------------------------ routing
  function go(id) {
    if (!id) return;
    if (TABS.includes(id)) { state.tab = id; render(); scrollTo(0, 0); setHash(id); return; }
    const m = /^day-(\d+)$/.exec(id);
    if (m) { state.tab = "qa"; state.qaDay = +m[1]; render(); scrollTo(0, 0); setHash(id); return; }
    const hit = sectionIndex()[id];
    if (hit) {
      state.tab = hit.tab; render(); setHash(id);
      const jump = () => { const el = document.getElementById(id); if (el) el.scrollIntoView({ block: "start" }); };
      requestAnimationFrame(jump);
      setTimeout(jump, 150);                                   // after code highlighting and late layout
      if (document.fonts && document.fonts.ready) document.fonts.ready.then(jump);
    }
  }
  function setHash(id) { try { history.replaceState(null, "", "#" + id); } catch { /* sandbox */ } }

  // ------------------------------------------------------------------ render shell
  function renderTabs() {
    const nav = $("#tabs");
    nav.innerHTML = TABS.map((t) => `<button role="tab" id="tab-${t}" aria-selected="${t === state.tab}" data-tab="${t}">${esc(T("tab_" + t, t))}</button>`).join("");
    nav.querySelectorAll("button").forEach((b) => b.addEventListener("click", () => go(b.dataset.tab)));
    document.querySelectorAll(".lang button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.lang === state.lang)));
    $("#brand").firstChild.textContent = T("brand", "DS Handbook") + " ";
    $("#brand-sub").textContent = T("brand_sub", "30 days");
    $("#search").placeholder = T("search", "Search");
    document.documentElement.lang = state.lang;
    document.body.classList.toggle("fa", state.lang === "fa");
    document.body.classList.toggle("ko", state.lang === "ko");
    $("#main").dir = state.lang === "fa" ? "rtl" : "ltr";
    document.querySelector(".top").dir = state.lang === "fa" ? "rtl" : "ltr";
  }
  function render() {
    renderTabs();
    const main = $("#main");
    const q = $("#search").value.trim();
    let html = q ? renderSearch(q) : "";
    if (state.tab === "plan") html += renderPlan();
    else if (state.tab === "qa") html += renderQA();
    else html += renderContentTab(state.tab);
    main.innerHTML = html;
    decorate(main);
    bindPlan(main);
    bindQA(main);
  }

  // ------------------------------------------------------------------ content tabs
  function renderContentTab(tab) {
    const c = C(tab);
    if (!c) return `<p class="status">${esc(T("missing", "This part is still being written."))}</p>`;
    const toc = (c.sections || []).map((s) => `<a href="#${esc(s.id)}">${esc(s.title)}</a>`).join("");
    const fb = isFallback(tab) ? `<p class="note">${esc(T("fallback", "Not translated yet: showing English."))}</p>` : "";
    const secs = (c.sections || []).map((s) => `
      <section class="section" id="${esc(s.id)}">
        <h2>${esc(s.title)} <span class="sid">#${esc(s.id)}</span></h2>
        ${s.summary ? `<p class="summary">${esc(s.summary)}</p>` : ""}
        <div class="prose">${md(s.body)}</div>
      </section>`).join("");
    return `<div class="layout">
      <aside class="toc"><details open><summary class="toc-title">${esc(T("contents", "Contents"))}</summary>${toc}</details></aside>
      <div class="reading"><h1>${esc(c.title)}</h1>${fb}<div class="tab-intro prose">${md(c.intro || "")}</div>${secs}</div>
    </div>`;
  }

  // ------------------------------------------------------------------ search
  function renderSearch(q) {
    const words = q.toLowerCase().split(/\s+/).filter(Boolean);
    const hits = [];
    for (const [id, { tab, s }] of Object.entries(sectionIndex())) {
      const hay = (s.title + " " + (s.summary || "") + " " + (s.body || "") + " " + id).toLowerCase();
      if (words.every((w) => hay.includes(w))) {
        const score = words.reduce((a, w) => a + (s.title.toLowerCase().includes(w) ? 5 : 0) + (id.includes(w) ? 3 : 0), 0);
        hits.push({ id, tab, s, score });
      }
    }
    hits.sort((a, b) => b.score - a.score);
    const list = hits.slice(0, 12).map((h) => `<a href="#${esc(h.id)}"><b>${esc(h.s.title)}</b> <small>${esc(T("tab_" + h.tab, h.tab))} · ${esc(h.s.summary || "")}</small></a>`).join("");
    return `<div class="results" aria-live="polite">${list || `<p class="status">${esc(T("no_results", "Nothing found."))}</p>`}</div>`;
  }

  // ------------------------------------------------------------------ plan tab (static: no accounts, no tracking)
  const COLAB = "https://colab.research.google.com/github/mahsa-agz/mahsa-agz.github.io/blob/main/ds-handbook/exam_prep/";
  const NOTEBOOKS = [["algorithms", "1_algorithms"], ["sql", "2_sql"], ["stats", "3_stats"], ["ai", "4_ai"]];
  function renderPlan() {
    const p = state.plan;
    if (!p) return `<p class="status">${esc(T("missing", "This part is still being written."))}</p>`;
    const intro = C("ui") && C("ui").plan_intro ? md(C("ui").plan_intro) : "";
    const days = p.days.map((d) => {
      const dd = String(d.day).padStart(2, "0");
      const lv = `<span class="pill ${d.level}">${esc(T("level_" + d.level, d.level))}</span>` + (d.mock ? ` <span class="pill mock">${esc(T("mock", "mock"))}</span>` : "");
      const algo = d.algo.map((a) => `<li>${a.url ? `<a href="${esc(a.url)}">${esc(a.title)}</a>` : esc(a.title)} <small>(${esc(T("level_" + a.level, a.level))}${state.showPatterns ? ", " + esc(titleOf("algo-" + a.pattern)) : ""})</small></li>`).join("");
      const topics = (area, key) => {
        const v = d[key]; if (!v) return "";
        const f = v.focus.map((id) => sectionIndex()[key + "-" + id] ? `<a href="#${key}-${id}">${esc(titleOf(key + "-" + id))}</a>` : esc(T("t_" + id, id))).join(", ");
        const r = v.review.length ? ` <small>· ${esc(T("review", "review"))}: ${v.review.map((id) => sectionIndex()[key + "-" + id] ? esc(titleOf(key + "-" + id)) : esc(T("t_" + id, id))).join(", ")}</small>` : "";
        return `<div class="area">${esc(area)}</div><div>${f}${r}</div>`;
      };
      const nbs = NOTEBOOKS.map(([a, f]) => `<a href="${COLAB}day_${dd}/${f}.ipynb">${esc(T("area_" + a, a))}</a>`).join(" · ");
      return `<article class="day" id="plan-day-${d.day}">
        <header><h3>${esc(T("day", "Day"))} ${d.day}</h3><span>${lv}</span></header>
        <div class="area">${esc(T("area_algorithms", "Algorithms"))}</div><ul>${algo}</ul>
        ${topics(T("area_sql", "SQL"), "sql")}${topics(T("area_stats", "Statistics"), "stats")}${topics(T("area_ai", "AI"), "ai")}
        <div class="checks"><span>${esc(T("open_colab", "Open in Colab"))}: ${nbs}</span><span><a href="#day-${d.day}">${esc(T("theory_qa", "Theory flashcards"))}</a></span></div>
      </article>`;
    }).join("");
    return `<div class="plan-head">
        <div><h1>${esc(T("plan_title", "30-day plan"))}</h1><div class="tab-intro prose">${intro}</div></div>
      </div>
      <div class="panel"><div class="form-row">
        <label><span><input type="checkbox" id="show-patterns" ${state.showPatterns ? "checked" : ""}> ${esc(T("show_patterns", "Show algorithm patterns (spoiler)"))}</span></label>
        <a class="btn ghost" href="${COLAB}00_start_here.ipynb">${esc(T("start_here", "Start here (Colab)"))}</a>
      </div></div>
      <div class="days">${days}</div>`;
  }
  function bindPlan(root) {
    if (state.tab !== "plan") return;
    const sp = $("#show-patterns", root);
    if (sp) sp.addEventListener("change", () => { state.showPatterns = sp.checked; render(); });
  }

  // ------------------------------------------------------------------ theory Q&A tab
  function renderQA() {
    const days = C("days");
    if (!days) return `<p class="status">${esc(T("missing", "This part is still being written."))}</p>`;
    const d = (days.days || []).find((x) => x.day === state.qaDay) || { qa: [] };
    const pick = Array.from({ length: 30 }, (_, i) => i + 1).map((n) => `<button type="button" data-qa="${n}" aria-pressed="${n === state.qaDay}">${n}</button>`).join("");
    const fb = isFallback("days") ? `<p class="note">${esc(T("fallback", "Not translated yet: showing English."))}</p>` : "";
    const cards = d.qa.map((c, i) => `<div class="card">
        <div class="meta">${esc(T("area_" + (c.area === "algo" ? "algorithms" : c.area), c.area))}${c.ref ? ` · <a href="#${esc(c.ref)}">${esc(titleOf(c.ref))}</a>` : ""}</div>
        <div class="q prose">${md(c.q)}</div>
        <details id="qa-${state.qaDay}-${i}"><summary>${esc(T("show_answer", "Show answer"))}</summary><div class="a prose">${md(c.a)}</div></details>
      </div>`).join("");
    return `<h1>${esc(T("qa_title", "Theory flashcards"))}</h1>
      <p class="tab-intro">${esc(T("qa_help", "Answer each question out loud in under a minute, then open the answer. Missed ones go on your redo list."))}</p>
      ${fb}<div class="daypick" role="group" aria-label="${esc(T("day", "Day"))}">${pick}</div>
      <h2>${esc(T("day", "Day"))} ${state.qaDay}</h2><div class="cards">${cards || `<p class="status">${esc(T("missing", "This part is still being written."))}</p>`}</div>`;
  }
  function bindQA(root) {
    root.querySelectorAll("button[data-qa]").forEach((b) => b.addEventListener("click", () => { state.qaDay = +b.dataset.qa; setHash("day-" + state.qaDay); render(); }));
  }

  // ------------------------------------------------------------------ boot
  async function setLang(lang) {
    if (!LANGS.includes(lang)) lang = "en";
    await loadLang(lang);
    state.lang = lang; local.set("lang", lang);
    render();
  }
  async function boot() {
    try { if ("scrollRestoration" in history) history.scrollRestoration = "manual"; } catch { /* sandbox */ }
    try { state.plan = await getJSON("plan.json"); } catch { state.plan = null; }
    await loadLang("en");
    state.lang = local.get("lang", "en");
    if (state.lang !== "en") await loadLang(state.lang);
    const h = (location.hash || "").slice(1);
    if (h) { render(); go(h); } else render();
    document.querySelectorAll(".lang button").forEach((b) => b.addEventListener("click", () => setLang(b.dataset.lang)));
    window.addEventListener("hashchange", () => { const id = (location.hash || "").slice(1); if (id) go(id); });
    let timer = null;
    $("#search").addEventListener("input", () => { clearTimeout(timer); timer = setTimeout(render, 150); });
  }
  boot();
})();
