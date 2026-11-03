// ---------- Card types ----------
// Each renderer: (card, el, ctx{L, lock, unlock}) -> optional cleanup function
const tag = t => `<span class="tag">${t}</span>`;

const CARDS = {
  // plain text: { title, body }
  text: (c, el) => { el.innerHTML = `<h2>${c.title}</h2>${c.body}`; },

  // the problem it solved: { title, body, who }
  story: (c, el) => {
    el.innerHTML = `${tag('مشکل: چرا ساخته شد؟')}<h2>${c.title}</h2>${c.body}${c.who ? `<p class="who">${c.who}</p>` : ''}`;
  },

  // everyday examples: { title, items:[{h, d}] }
  life: (c, el) => {
    el.innerHTML = `${tag('در زندگی')}<h2>${c.title}</h2><div class="list">${c.items.map(i => `<div class="box"><b>${i.h}</b><div>${i.d}</div></div>`).join('')}</div>`;
  },

  // interactive picture: { title, body, w: host => cleanup }
  play: (c, el) => {
    el.innerHTML = `${tag('امتحان کنید')}<h2>${c.title}</h2><p>${c.body}</p>`;
    return c.w(el);
  },

  // formula with every symbol named: { title, intro, toks:[{s, c, l}], read, note }
  formula: (c, el) => {
    el.innerHTML = `${tag('فرمول')}<h2>${c.title}</h2>${c.intro || ''}
      <div class="formula">${c.toks.map(k => `<span class="tok" style="${k.c ? `--c:var(--${k.c})` : ''}"><span>${k.s}</span>${k.l ? `<small>${k.l}</small>` : ''}</span>`).join('')}</div>
      ${c.read ? `<p class="muted">${c.read}</p>` : ''}${c.note || ''}`;
  },

  // rules with their reason: { title, items:[{r, why}] }
  rules: (c, el) => {
    el.innerHTML = `${tag('قانون‌ها')}<h2>${c.title}</h2><div class="list">${c.items.map((i, k) =>
      `<div class="box"><div><b>${fa(k + 1)}.</b> ${i.r}</div><div class="muted">${i.why}</div></div>`).join('')}</div>`;
  },

  // yes / no game: { title, yes, no, items:[{q, a, why}] }
  sort: (c, el, x) => {
    x.lock();
    el.innerHTML = `${tag('بازی')}<h2>${c.title}</h2><div class="sort"></div>`;
    const box = el.querySelector('.sort');
    let left = c.items.length;
    c.items.forEach(it => {
      const d = document.createElement('div');
      d.className = 'item';
      d.innerHTML = `<div class="q">${it.q}</div><div class="two"><button>${c.yes}</button><button>${c.no}</button></div>`;
      const [yb, nb] = d.querySelectorAll('button');
      const pick = ans => {
        const right = ans === it.a;
        d.classList.add(right ? 'right' : 'wrong');
        d.querySelector('.two').outerHTML = `<div class="why"><span class="say ${right ? 'ok' : 'no'}">${right ? 'درست!' : 'نه دقیقاً.'}</span> <b>${it.a ? c.yes : c.no}</b>. ${it.why}</div>`;
        if (--left === 0) x.unlock();
      };
      yb.onclick = () => pick(true);
      nb.onclick = () => pick(false);
      box.appendChild(d);
    });
  },

  // multiple choice: { q, options, answer, why }  (review:true when replayed from an earlier lesson)
  quiz: (c, el, x) => {
    x.lock();
    el.innerHTML = `${tag(c.review ? 'مرور درس‌های قبل' : 'سؤال')}<h2>${c.q}</h2><div class="sort"></div><p class="fb"></p>`;
    const box = el.querySelector('.sort');
    const order = c.options.map((o, i) => i).sort(() => Math.random() - 0.5);
    order.forEach(i => {
      const b = document.createElement('button');
      b.className = 'opt';
      b.innerHTML = c.options[i];
      b.onclick = () => {
        box.querySelectorAll('.opt').forEach((o, k) => { o.disabled = true; if (order[k] === c.answer) o.classList.add('right'); });
        if (i !== c.answer) b.classList.add('wrong');
        el.querySelector('.fb').innerHTML = `<span class="say ${i === c.answer ? 'ok' : 'no'}">${i === c.answer ? 'آفرین!' : 'نه دقیقاً.'}</span> ${c.why}`;
        x.unlock();
      };
      box.appendChild(b);
    });
  },

  // link to AI: { title, body }
  ai: (c, el) => {
    el.innerHTML = `<div class="ai">${tag('ارتباط با هوش مصنوعی')}<h2 style="margin:8px 0">${c.title}</h2>${c.body}</div>`;
  },

  // automatic: what this topic is needed for, from the topic graph
  used: (c, el, x) => {
    const node = x.L.node;
    const parents = [...new Set(G_LINKS.filter(([a, b]) => b === node && G_NODES[a] && G_NODES[a][2] !== 'q').map(([a]) => a))];
    const qs = ancestors(node).filter(a => G_NODES[a] && G_NODES[a][2] === 'q');
    el.innerHTML = `${tag('نقشه')}<h2>این را کجا لازم داریم؟</h2>
      <p>«${nodeName(node)}» پله‌ای است برای:</p><div class="aichips">${parents.map(a => `<span class="aichip">${nodeName(a)} <span class="en">(${G_NODES[a][1]})</span></span>`).join('')}</div>
      ${qs.length ? `<p>و برای جواب دادن به این سؤال‌های مصاحبه لازم است:</p><div class="list">${qs.map(a => `<div class="box qbox">${nodeName(a)} <span class="en">(${G_NODES[a][1]})</span></div>`).join('')}</div>` : ''}`;
  },

  // interview mission: the lessons this question stands on, from the topic graph, ticked when started
  ladder: (c, el, x) => {
    const need = new Set([x.L.node]), q = [x.L.node];
    while (q.length) { const a = q.shift(); for (const [p, b] of G_LINKS) if (p === a && !need.has(b)) { need.add(b); q.push(b); } }
    const ids = COURSE_PLAN.flatMap(ch => ch.items.map(([id]) => id)).filter(id => LESSONS[id] && LESSONS[id].node !== x.L.node && need.has(LESSONS[id].node));
    el.innerHTML = `${tag('نردبان')}<h2>${c.title || 'برای جواب دادن، این پله‌ها لازم است'}</h2>
      <div class="list">${ids.map(id => `<div class="box ladder ${started(id) ? 'have' : ''}"><b>${started(id) ? '✓' : '○'}</b> ${LESSONS[id].title} <span class="en">(${LESSONS[id].en})</span></div>`).join('')}</div>
      <p class="muted">${ids.filter(started).length} از ${ids.length} پله را رفته‌اید. پله‌های ○ را می‌توانید بعداً از فهرست درس‌ها بروید.</p>`.replace(/(\d+) از (\d+)/, (m, a, b) => `${fa(+a)} از ${fa(+b)}`);
  },

  // interview mission: the short answer to say out loud: { lines:[...], tip }
  answer: (c, el) => {
    el.innerHTML = `${tag('جواب مصاحبه‌ای')}<h2>${c.title || 'جواب در چند جمله'}</h2>
      <div class="sheet">${c.lines.map(l => `<p>${l}</p>`).join('')}</div>${c.tip ? `<p class="muted">${c.tip}</p>` : ''}`;
  },

  // interview mission: follow-up questions with a reveal: { items:[{q, a}] }
  follow: (c, el) => {
    el.innerHTML = `${tag('سؤال‌های بعدی مصاحبه‌گر')}<h2>${c.title || 'مصاحبه‌گر ممکن است بپرسد…'}</h2>
      <div class="list">${c.items.map(i => `<details class="box"><summary><b>${i.q}</b></summary><div class="muted">${i.a}</div></details>`).join('')}</div>`;
  },

  // automatic: the lesson's cheat sheet
  sheet: (c, el, x) => {
    el.innerHTML = `${tag('خلاصه برای دفترچه')}<h2>این را نگه دارید</h2>${sheetHTML(x.L)}`;
  },
};
