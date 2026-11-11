// Builds a sticky table of contents from every <h2> on the page.
// Wide screens: a fixed column beside the text. Phones: a «فهرست» button that opens it.
(() => {
  const hs = [...document.querySelectorAll('main h2')];
  if (!hs.length) return;
  const nav = document.createElement('nav');
  nav.className = 'toc';
  nav.innerHTML = '<b>فهرست</b>' + hs.map((h, i) => {
    if (!h.id) h.id = 's' + (i + 1);
    return `<a href="#${h.id}">${h.textContent.replace(/\s*\(.*?\)\s*/g, ' ').trim()}</a>`;
  }).join('');
  const btn = document.createElement('button');
  btn.className = 'toc-btn'; btn.textContent = '☰ فهرست';
  btn.onclick = () => nav.classList.toggle('open');
  nav.addEventListener('click', e => { if (e.target.tagName === 'A') nav.classList.remove('open'); });
  document.body.append(nav, btn);
  const links = [...nav.querySelectorAll('a')];
  const io = new IntersectionObserver(es => es.forEach(e => {
    if (e.isIntersecting) links.forEach(a => a.classList.toggle('on', a.getAttribute('href') === '#' + e.target.id));
  }), { rootMargin: '0px 0px -75% 0px' });
  hs.forEach(h => io.observe(h));
  const css = document.createElement('style');
  css.textContent = `
.toc { position: fixed; top: 16px; left: 16px; width: 230px; max-height: calc(100vh - 32px); overflow-y: auto; background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: 10px 12px; font-size: 13px; line-height: 1.6; z-index: 20; }
.toc b { display: block; margin-bottom: 6px; color: var(--muted); }
.toc a { display: block; padding: 3px 8px; border-radius: 6px; color: var(--ink); text-decoration: none; }
.toc a:hover { background: var(--soft); }
.toc a.on { background: var(--soft); color: var(--accent); font-weight: 700; }
.toc-btn { display: none; position: fixed; bottom: 16px; left: 16px; z-index: 21; background: var(--card); color: var(--ink); border: 1px solid var(--line); border-radius: 999px; padding: 8px 14px; font: inherit; font-size: 14px; margin: 0; }
@media (max-width: 1300px) { .toc { display: none; bottom: 64px; top: auto; } .toc.open { display: block; } .toc-btn { display: block; } }
html { scroll-behavior: smooth; } h2 { scroll-margin-top: 12px; }`;
  document.head.appendChild(css);
})();
// MathJax sometimes fails on one formula during the first pass; draw those again once it is ready
if (window.MathJax && MathJax.startup && MathJax.startup.promise) MathJax.startup.promise.then(() => {
  const bad = [...MathJax.startup.document.math].filter(m => m.typesetRoot && m.typesetRoot.querySelector('mjx-merror'));
  if (!bad.length) return;
  const hosts = bad.map(m => { const h = m.typesetRoot.parentElement; m.typesetRoot.replaceWith(document.createTextNode(m.display ? '\\[' + m.math + '\\]' : '\\(' + m.math + '\\)')); return h; });
  MathJax.typesetClear(hosts); MathJax.typesetPromise(hosts);
});
