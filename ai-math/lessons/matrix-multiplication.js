// ---------- Vectors & Matrices: Matrix Multiplication ----------
// uses vecPlane from lessons/vectors.js
// a colored LaTeX piece
const MATMUL_C = (c, tex) => `<span style="color:var(--${c})">${E(tex)}</span>`;

// any matrix (list of rows) as LaTeX
const MATMUL_G = rows => String.raw`\begin{bmatrix} ${rows.map(r => r.join(' & ')).join(String.raw` \\ `)} \end{bmatrix}`;
// a 2×2 matrix kept as [a, b, c, d]
const MATMUL_M = m => MATMUL_G([[m[0], m[1]], [m[2], m[3]]]);
// P · Q for 2×2 matrices [a, b, c, d]: each cell = a row of P · a column of Q
const MATMUL_mul = (P, Q) => [P[0] * Q[0] + P[1] * Q[2], P[0] * Q[1] + P[1] * Q[3], P[2] * Q[0] + P[3] * Q[2], P[2] * Q[1] + P[3] * Q[3]];
const MATMUL_same = (P, Q) => P.every((x, i) => x === Q[i]);
const MATMUL_X = (m, n) => E(String.raw`${m} \times ${n}`);

// preset machines: [name, a, b, c, d]
const MATMUL_PRESETS = [
  ['چرخش ۹۰°', 0, -1, 1, 0],
  ['کش ×۲', 2, 0, 0, 1],
  ['آینه', -1, 0, 0, 1],
  ['کج', 1, 1, 0, 1],
];
const MATMUL_mat = i => MATMUL_PRESETS[i].slice(1);
const MATMUL_sq = m => [[0, 0], [m[0], m[2]], [m[0] + m[1], m[2] + m[3]], [m[1], m[3]]];
const MATMUL_poly = (g, pts, color, alpha, w, dash) => {
  const c = g.ctx;
  c.beginPath(); pts.forEach(([x, y], i) => (i ? c.lineTo(g.X(x), g.Y(y)) : c.moveTo(g.X(x), g.Y(y)))); c.closePath();
  if (alpha) { c.globalAlpha = alpha; c.fillStyle = g.css(color); c.fill(); c.globalAlpha = 1; }
  pts.forEach((p, i) => { const q = pts[(i + 1) % pts.length]; g.line(p[0], p[1], q[0], q[1], color, w, dash); });
};

// picture 1: B first, then A; the green shape is made by the single matrix AB (or BA when swapped)
const MATMUL_W_CHAIN = h => {
  const relabel = s => {
    const bs = h.querySelectorAll('.btns button');
    bs[0].innerHTML = `B: ${MATMUL_PRESETS[s.b][0]}`;
    bs[1].innerHTML = `A: ${MATMUL_PRESETS[s.a][0]}`;
  };
  return vecPlane(h, {
    labels: true,
    state: { a: 1, b: 0, swap: false },
    buttons: [
      { label: `B: ${MATMUL_PRESETS[0][0]}`, on: s => { s.b = (s.b + 1) % 4; relabel(s); } },
      { label: `A: ${MATMUL_PRESETS[1][0]}`, on: s => { s.a = (s.a + 1) % 4; relabel(s); } },
      { label: 'ترتیب برعکس', on: s => { s.swap = !s.swap; }, active: s => s.swap },
    ],
    draw: (g, s) => {
      g.grid();
      const A = MATMUL_mat(s.a), B = MATMUL_mat(s.b);
      const first = s.swap ? A : B, second = s.swap ? B : A;
      MATMUL_poly(g, MATMUL_sq([1, 0, 0, 1]), 'muted', 0, 2, [5, 5]);
      MATMUL_poly(g, MATMUL_sq(first), 'orange', 0.15, 2, [6, 4]);
      MATMUL_poly(g, MATMUL_sq(MATMUL_mul(second, first)), 'green', 0.3, 3);
      g.dot(0, 0, 'ink', 5);
    },
    read: s => {
      const A = MATMUL_mat(s.a), B = MATMUL_mat(s.b), AB = MATMUL_mul(A, B), BA = MATMUL_mul(B, A);
      const nA = MATMUL_PRESETS[s.a][0], nB = MATMUL_PRESETS[s.b][0];
      const [m, other, nm, no] = s.swap ? [BA, AB, 'BA', 'AB'] : [AB, BA, 'AB', 'BA'];
      const [P, Q] = s.swap ? [B, A] : [A, B];
      const steps = s.swap ? `اول A (${nA})، بعد B (${nB})` : `اول B (${nB})، بعد A (${nA})`;
      return `${steps}. ماشینِ تنهایی که هر دو کار را یک‌جا می‌کند (شکل سبز):<br>` +
        N(`${E(`${nm} =`)} ${MATMUL_C('orange', MATMUL_M(P))} ${E(String.raw`\cdot`)} ${MATMUL_C('orange', MATMUL_M(Q))} ${E('=')} ${MATMUL_C('green', MATMUL_M(m))}`) +
        '<br><b>' + (MATMUL_same(AB, BA) ? `این بار ترتیب فرقی نکرد: ${E('AB = BA')}.` : 'ترتیب برعکس، ماشین دیگری است: ') + '</b>' +
        (MATMUL_same(AB, BA) ? '' : E(`${no} = ${MATMUL_M(other)}`));
    },
  });
};

// the shop: how many of (bread, milk, cheese) each customer buys, and the price of each in two cities (thousand toman)
const MATMUL_Q = [[2, 1, 1], [1, 2, 1]];
const MATMUL_P = [[3, 2], [5, 6], [10, 8]];
const MATMUL_WHO = ['علی', 'سارا'], MATMUL_CITY = ['تهران', 'شیراز'];
const MATMUL_R = MATMUL_Q.map(r => [0, 1].map(j => r.reduce((t, x, k) => t + x * MATMUL_P[k][j], 0)));

// picture 2: tap a cell of the answer; its row of S and column of P light up and the dot product is shown
const MATMUL_W_CELL = h => {
  const box = document.createElement('div');
  box.dir = 'ltr';
  box.style.cssText = 'display:grid;grid-template-columns:repeat(5,auto);align-items:center;justify-content:center;gap:4px;margin:10px 0;font-size:15px;max-width:100%';
  const read = document.createElement('div');
  read.className = 'read';
  const cells = [];
  const grid = (rows, kind) => {
    const g = document.createElement('div');
    g.style.cssText = `display:grid;grid-template-columns:repeat(${rows[0].length},28px);gap:2px;padding:2px 3px;` +
      'border-left:2px solid var(--ink);border-right:2px solid var(--ink);border-radius:6px';
    rows.forEach((r, i) => r.forEach((x, j) => {
      const c = document.createElement(kind === 'R' ? 'button' : 'span');
      c.textContent = fa(x);
      c.style.cssText = 'box-sizing:border-box;width:28px;height:28px;padding:0;display:flex;align-items:center;justify-content:center;font:inherit;color:inherit;border-radius:8px;border:2px solid transparent;' +
        (kind === 'R' ? 'background:var(--soft);font-weight:700' : '');
      if (kind === 'R') c.onclick = () => pick(i, j);
      cells.push({ c, kind, i, j });
      g.appendChild(c);
    }));
    return g;
  };
  const sign = t => { const s = document.createElement('span'); s.textContent = t; s.style.fontWeight = '700'; return s; };
  box.append(grid(MATMUL_Q, 'Q'), sign('·'), grid(MATMUL_P, 'P'), sign('='), grid(MATMUL_R, 'R'));
  const pick = (i, j) => {
    cells.forEach(({ c, kind, i: a, j: b }) => {
      const on = kind === 'Q' ? a === i : kind === 'P' ? b === j : a === i && b === j;
      const col = kind === 'Q' ? 'blue' : kind === 'P' ? 'orange' : 'green';
      c.style.background = on ? `color-mix(in srgb, var(--${col}) 22%, var(--card))` : kind === 'R' ? 'var(--soft)' : 'transparent';
      c.style.borderColor = on ? `var(--${col})` : 'transparent';
    });
    const q = MATMUL_Q[i], p = MATMUL_P.map(r => r[j]);
    read.innerHTML = `${MATMUL_WHO[i]} در ${MATMUL_CITY[j]}: <span style="color:var(--blue)">سطر ${fa(i + 1)} از S</span> با<span style="color:var(--orange)">ستون ${fa(j + 1)} از P</span><br>` +
      `تعداد هر کالا × قیمتش در ${MATMUL_CITY[j]}، بعد همه با هم:<br>` +
      E(q.map((x, k) => String.raw`${x} \times ${p[k]}`).join(' + ') + String.raw` = \mathbf{${MATMUL_R[i][j]}}`) +
      ' هزار تومان';
  };
  h.append(box, read);
  pick(0, 0);
  return () => {};
};

const MATMUL_TH = t => `<td style="padding:2px 8px"><b>${t}</b></td>`;
const MATMUL_TD = (c, n) => `<td style="color:var(--${c})">${fa(n)}</td>`;
const MATMUL_TABLE = (cols, rows, data, c) => `<table dir="rtl" style="border-collapse:collapse;margin:6px auto;text-align:center;font-size:15px">` +
  `<tr><td></td>${cols.map(MATMUL_TH).join('')}</tr>` +
  rows.map((r, i) => `<tr>${MATMUL_TH(r)}${data[i].map(n => MATMUL_TD(c, n)).join('')}</tr>`).join('') + '</table>';

lesson({
  id: 'matrix-multiplication', node: 'matrix-multiplication', title: 'ضرب ماتریس', en: 'Matrix Multiplication',
  parts: [
    { name: 'چرا و یعنی چه؟', cards: [
      { t: 'story', title: `ضرب ماتریس ${EN('Matrix Multiplication')}`,
        body: `<p>درس قبل دیدیم هر ماتریس یک ماشین است. حالا دو ماشین پشت سر هم: اول صفحه را ۹۰ درجه <b>بچرخان</b>، بعد دو برابر <b>کش بده</b>. آیا <b>یک</b> ماتریس هست که هر دو کار را یک‌جا بکند؟</p>
               <p>یک مسئله‌ی دیگر: ۲ مشتری، هر کدام چند نان و شیر و پنیر می‌خرند. قیمت‌ها در ۲ شهر فرق دارد. می‌خواهیم فاکتور <b>هر مشتری در هر شهر</b> را با هم داشته باشیم.</p>
               <div class="key">جواب هر دو مسئله یک حساب است: ضرب دو ماتریس.</div>`,
        who: 'کِیلی (Cayley) در ۱۸۵۸ ضرب ماتریس را دقیقاً طوری تعریف کرد که یعنی «دو تغییر، پشت سر هم».' },
      { t: 'text', title: 'معنی ساده',
        body: `<div class="key">ضرب ماتریس یعنی <b>یک کار بعد از کار دیگر</b>. هر خانه‌ی جواب = ضرب داخلیِ <b>یک سطرِ</b> اولی با <b>یک ستونِ</b> دومی.</div>
               <p>${E(String.raw`AB \cdot v`)} یعنی اول B روی v کار می‌کند، بعد A روی جواب: ${E(String.raw`A \cdot (B \cdot v)`)}. ماتریسی که به v نزدیک‌تر است، <b>اول</b> کار می‌کند.</p>
               <p>سطر و ستون باید هم‌اندازه باشند تا ضرب داخلی بشود. و <b>ترتیب مهم است</b>: ${E('AB')} و ${E('BA')} معمولاً فرق دارند.</p>` },
      { t: 'play', w: MATMUL_W_CHAIN, title: 'دو ماشین، یک ماشین',
        body: 'مربع خط‌چین خاکستری اول با B به شکل <b style="color:var(--orange)">نارنجی</b> می‌رود، بعد با A به شکل <b style="color:var(--green)">سبز</b>. دکمه‌های B و A ماشین‌ها را عوض می‌کنند؛ «ترتیب برعکس» جای آن‌ها را عوض می‌کند.',
        look: [
          'اول B = چرخش ۹۰° و A = کش ×۲ است → مربع اول می‌چرخد (نارنجی)، بعد پهن می‌شود: مستطیل سبز ۲ خانه پهن و ۱ خانه بلند است.',
          `«ترتیب برعکس» را بزنید → اول کش، بعد چرخش: مستطیل سبز حالا ۱ خانه پهن و ۲ خانه بلند است، و ${E(String.raw`BA = ${MATMUL_G([[0, -1], [2, 0]])}`)} با ${E(String.raw`AB = ${MATMUL_G([[0, -2], [1, 0]])}`)} فرق دارد.`,
          `«ترتیب برعکس» را خاموش کنید و یک بار دکمه‌ی B را بزنید تا «کش ×۲» شود → هر دو ماشین کش‌اند و ترتیب فرقی نمی‌کند: ${E('AB = BA')}.`,
        ],
        see: 'دو ماشین پشت سر هم همیشه یک ماشینِ تنهاست، و آن ماشین حاصل‌ضرب دو ماتریس است. ولی ترتیب مهم است: «اول بچرخان، بعد کش بده» با برعکسش فرق دارد. شبکه‌ی عصبی هم لایه‌ها را پشت سر هم می‌زند، پس ترتیب لایه‌ها مهم است.' },
      { t: 'life', title: 'ضرب ماتریس در زندگی', items: [
        { h: 'فاکتور مغازه', d: 'جدول «هر مشتری چند تا از هر کالا» × جدول «قیمت هر کالا در هر شهر» = جدول «فاکتور هر مشتری در هر شهر». همه با یک ضرب.' },
        { h: 'آشپزخانه‌ی رستوران', d: 'جدول «هر غذا چقدر از هر مواد لازم دارد» × جدول «قیمت هر مواد در هر فروشگاه» = هزینه‌ی هر غذا در هر فروشگاه.' },
        { h: 'چند فیلتر عکس پشت سر هم', d: 'هر فیلتر رنگ یک ماتریس است. برنامه دو فیلتر را یک بار در هم ضرب می‌کند و بعد فقط <b>یک</b> فیلتر روی میلیون‌ها نقطه‌ی عکس می‌زند.' },
        { h: 'حرکت رقص', d: `اول به راست بچرخید، بعد یک قدم جلو بروید. حالا برعکس: اول قدم، بعد چرخش. جای شما فرق می‌کند. ترتیب مهم است، مثل ${E('AB')} و ${E('BA')}.` },
      ] },
      { t: 'sort', title: 'این دو ماتریس را می‌شود در هم ضرب کرد؟', yes: 'می‌شود', no: 'نمی‌شود', items: [
        { q: E(String.raw`(2 \times 3) \cdot (3 \times 2)`), a: true, why: `هر سطرِ اولی ۳ عدد دارد، هر ستونِ دومی هم ۳ عدد. جواب ${MATMUL_X(2, 2)} است.` },
        { q: E(String.raw`(2 \times 3) \cdot (2 \times 3)`), a: false, why: 'سطرِ اولی ۳ عدد دارد ولی ستونِ دومی فقط ۲ عدد. ضرب داخلی نمی‌شود. (هم‌اندازه بودن دو ماتریس کافی نیست.)' },
        { q: E(String.raw`(3 \times 1) \cdot (1 \times 4)`), a: true, why: `سطرِ اولی ۱ عدد، ستونِ دومی ۱ عدد. جواب ${MATMUL_X(3, 4)} است؛ از دو ماتریس باریک، یک جدول بزرگ.` },
        { q: E(String.raw`(2 \times 2) \cdot (3 \times 2)`), a: false, why: 'سطرِ اولی ۲ عدد دارد، ستونِ دومی ۳ عدد. جور نیست.' },
        { q: E(String.raw`(1 \times 3) \cdot (3 \times 1)`), a: true, why: `یک سطر با یک ستون، هر دو ۳ عددی. جواب ${MATMUL_X(1, 1)} است، یعنی یک عدد: همان ضرب داخلیِ دو بردار.` },
      ] },
      { t: 'quiz', q: `در ${E(String.raw`AB \cdot v`)}، کدام ماتریس اول روی v کار می‌کند؟`,
        options: ['B، بعد A', 'A، بعد B', 'هر دو با هم، ترتیب ندارد'], answer: 0,
        why: `${E(String.raw`AB \cdot v = A \cdot (B \cdot v)`)}: B کنار v است، پس اول کار می‌کند. (ما از چپ به راست می‌خوانیم، ولی ماشین‌ها از راست به چپ کار می‌کنند. ترتیب هم مهم است، چون ${E('AB')} و ${E('BA')} معمولاً فرق دارند.)` },
    ] },
    { name: 'فرمول', cards: [
      { t: 'formula', f: String.raw`\Cg{(AB)_{ij}} = \Ca{\sum_{k=1}^{n}} \Cb{a_{ik}} \, \Co{b_{kj}}`, title: `فرمول ضرب ماتریس ${EN('Matrix Product')}`,
        intro: `<p>${E('a_{ik}')} یعنی خانه‌ی سطر i و ستون k از A. ${E('(AB)_{ij}')} خانه‌ی سطر i و ستون j از جواب است. ${E(String.raw`\sum`)} یعنی همه را جمع کن (درس میانگین). n یعنی هر سطرِ A چند عدد دارد.</p>`,
        toks: [{ s: '(AB)_{ij}', c: 'green', l: 'خانه‌ی سطر i، ستون j از جواب' }, { s: '=' }, { s: String.raw`\sum_{k=1}^{n}`, c: 'accent', l: 'جمع روی k = ۱، ۲، …، n' },
               { s: 'a_{ik}', c: 'blue', l: 'سطر i از A' }, { s: 'b_{kj}', c: 'orange', l: 'ستون j از B' }],
        read: 'خوانده می‌شود: «خانه‌ی i و j از AB برابر است با جمعِ a i k ضرب در b k j، روی همه‌ی kها».',
        note: `<p>یعنی سطر i از A و ستون j از B را خانه به خانه در هم ضرب کن و جمع کن: همان ضرب داخلی.</p>
               <p><b>قانون اندازه:</b> ${E(String.raw`(m \times n) \cdot (n \times p) = m \times p`)}. دو عدد وسط (n) باید برابر باشند؛ دو عدد بیرونی اندازه‌ی جواب‌اند.</p>` },
      { t: 'example', title: 'یک مثال، خانه به خانه',
        intro: `<p class="read">${N(`${MATMUL_C('blue', MATMUL_G([[2, 1], [0, 3]]))} ${E(String.raw`\cdot`)} ${MATMUL_C('orange', MATMUL_G([[1, 4], [2, 1]]))}`)}</p>`,
        steps: [
          `سطر ۱ با ستون ۱: ${E(String.raw`2 \times 1 + 1 \times 2 = 4`)}`,
          `سطر ۱ با ستون ۲: ${E(String.raw`2 \times 4 + 1 \times 1 = 9`)}`,
          `سطر ۲ با ستون ۱: ${E(String.raw`0 \times 1 + 3 \times 2 = 6`)}`,
          `سطر ۲ با ستون ۲: ${E(String.raw`0 \times 4 + 3 \times 1 = 3`)}`,
        ],
        result: `${E(String.raw`= ${MATMUL_G([[4, 9], [6, 3]])}`)}<br>هر خانه یک ضرب داخلی است. چهار خانه، چهار ضرب داخلی.` },
      { t: 'text', title: 'فاکتور مغازه با عدد',
        body: `<p>S: هر مشتری چند تا می‌خرد. P: قیمت هر کالا در هر شهر (هزار تومان).</p>
               ${MATMUL_TABLE(['نان', 'شیر', 'پنیر'], MATMUL_WHO, MATMUL_Q, 'blue')}
               ${MATMUL_TABLE(MATMUL_CITY, ['نان', 'شیر', 'پنیر'], MATMUL_P, 'orange')}
               <p>علی در تهران: ${E(String.raw`2 \times 3 + 1 \times 5 + 1 \times 10 = 21`)}. سه خانه‌ی دیگر هم همین‌طور:</p>
               ${MATMUL_TABLE(MATMUL_CITY, MATMUL_WHO, MATMUL_R, 'green')}
               <p>اندازه‌ها: ${E(String.raw`(2 \times 3) \cdot (3 \times 2) = 2 \times 2`)}؛ ۲ مشتری و ۲ شهر.</p>` },
      { t: 'play', w: MATMUL_W_CELL, title: 'سطر × ستون',
        body: 'همان مغازه. <b style="color:var(--blue)">S</b>: هر مشتری (علی، سارا) چند نان، شیر، پنیر می‌خرد. <b style="color:var(--orange)">P</b>: قیمت هر کالا در تهران و شیراز. سمت راست، <b style="color:var(--green)">جواب</b>: فاکتور هر مشتری در هر شهر. روی خانه‌های جواب بزنید.',
        look: [
          `اول خانه‌ی بالا-چپ روشن است → علی در تهران: ${E(String.raw`2 \times 3 + 1 \times 5 + 1 \times 10 = 21`)}.`,
          `خانه‌ی بالا-راست (۱۸) را بزنید → همان سطر علی، ولی ستون شیراز: ${E(String.raw`2 \times 2 + 1 \times 6 + 1 \times 8 = 18`)}.`,
          `خانه‌ی پایین-چپ (۲۳) را بزنید → سطر سارا با ستون تهران: ${E(String.raw`1 \times 3 + 2 \times 5 + 1 \times 10 = 23`)}.`,
        ],
        see: 'هر خانه‌ی جواب فقط به یک سطر و یک ستون نگاه می‌کند؛ ضرب ماتریس یعنی همه‌ی این ضرب‌های داخلی با هم. چون خانه‌ها به هم کاری ندارند، کامپیوتر می‌تواند همه را هم‌زمان حساب کند؛ راز سرعت هوش مصنوعی همین است.' },
      { t: 'rules', title: 'سه قانون مهم', items: [
        { r: `ترتیب مهم است: معمولاً ${E(String.raw`AB \neq BA`)}.`,
          why: `ضرب ماتریس یعنی کارها پشت سر هم، و «اول بچرخان بعد کش بده» با «اول کش بده بعد بچرخان» فرق دارد. در مثال قبل، با جابه‌جا کردن دو ماتریس، جواب ${E(MATMUL_G([[2, 13], [4, 5]]))} می‌شود، نه ${E(MATMUL_G([[4, 9], [6, 3]]))}.` },
        { r: `اندازه‌های <b>وسط</b> باید برابر باشند: ${E(String.raw`(m \times n) \cdot (n \times p)`)}.`,
          why: 'هر خانه ضرب داخلیِ یک سطر از اولی با یک ستون از دومی است. ضرب داخلی دو فهرستِ هم‌اندازه می‌خواهد: سطر n عدد دارد، پس ستون هم باید n عدد داشته باشد.' },
        { r: `ماتریس همانی هیچ چیز را عوض نمی‌کند: ${E('AI = IA = A')}.`,
          why: 'I هر بردار را همان‌طور پس می‌دهد (درس قبل). پس «هیچ کار، بعد A» همان A است، و «A، بعد هیچ کار» هم همان A. مثل ضرب در عدد ۱.' },
      ] },
      { t: 'ai', title: 'ضرب ماتریس در هوش مصنوعی',
        body: `<p>• یک <b>لایه</b>‌ی شبکه‌ی عصبی ${E(String.raw`W \cdot x`)} است: ماتریس وزن‌ها × یک ورودی. اگر ۱۰۰ ورودی را ستون به ستون کنار هم بچینیم، یک ماتریس X داریم، و ${E(String.raw`W \cdot X`)} جواب هر ۱۰۰ ورودی را با <b>یک</b> ضرب می‌دهد.</p>
               <p>• یادگیری عمیق ${EN('Deep Learning')} یعنی زنجیره‌ای از ضرب ماتریس‌ها، با یک قدم کوچک غیرخطی بین هر دو ضرب (مثلاً صفر کردن عددهای منفی).</p>
               <p>• کارت گرافیک ${EN('GPU')} دقیقاً برای همین ضرب‌های بزرگ ساخته و به کار گرفته می‌شود.</p>
               <p>• در ترنسفورمرها، <b>توجه</b> ${EN('Attention')} با ${E(String.raw`Q \cdot K^{T}`)} حساب می‌شود (${E('K^{T}')} یعنی K با سطر و ستونِ جابه‌جا): ضرب داخلیِ هر کلمه با همه‌ی کلمه‌ها، یک‌جا.</p>` },
      { t: 'quiz', q: E(String.raw`${MATMUL_G([[1, 2], [0, 1]])} \cdot ${MATMUL_G([[3, 0], [1, 2]])} = \,?`),
        options: [E(MATMUL_G([[5, 4], [1, 2]])), E(MATMUL_G([[3, 0], [0, 2]])), E(MATMUL_G([[3, 6], [1, 4]]))], answer: 0,
        why: `سطر ۱ با ستون ۱: ${E(String.raw`1 \times 3 + 2 \times 1 = 5`)}؛ سطر ۱ با ستون ۲: ${E(String.raw`1 \times 0 + 2 \times 2 = 4`)}؛ سطر ۲ با ستون ۱: ${E(String.raw`0 \times 3 + 1 \times 1 = 1`)}؛ سطر ۲ با ستون ۲: ${E(String.raw`0 \times 0 + 1 \times 2 = 2`)}. (جوابِ ۳، ۰، ۰، ۲ یعنی خانه به خانه ضرب کرده‌ایم. جوابِ ۳، ۶، ۱، ۴ یعنی ترتیب را برعکس کرده‌ایم: ${E('BA')}.)` },
      { t: 'text', title: 'یک سؤال برای درس بعد',
        body: `<p>ماتریس «کش ×۲» را دوباره ببینید: پیکان ${V(1, 0)} به ${V(2, 0)} می‌رود. <b>جهتش عوض نشد</b>، فقط دو برابر شد. ولی ${V(1, 1)} به ${V(2, 1)} می‌رود و کج می‌شود.</p>
               <div class="key">هر ماتریس پیکان‌های خاصی دارد که فقط بلند یا کوتاه می‌شوند، نه چرخیده. آن‌ها کدام‌اند و چند برابر می‌شوند؟</div>
               <p>این را <b>مقدار ویژه</b> ${EN('Eigenvalues')} می‌گویند. درس بعد!</p>` },
    ] },
  ],
  sheet: {
    one: 'ضرب ماتریس = دو تغییر پشت سر هم، در قالب یک ماتریس. هر خانه‌ی جواب = ضرب داخلیِ یک سطر از اولی با یک ستون از دومی. ساخته شد تا چند کار یا چند حساب جدولی را یک‌جا انجام دهیم.',
    f: String.raw`(AB)_{ij} = \sum_{k} a_{ik} b_{kj} \qquad (m \times n) \cdot (n \times p) = m \times p`,
    rules: [`${E(String.raw`AB \cdot v = A \cdot (B \cdot v)`)}: اول B، بعد A.`, `معمولاً ${E(String.raw`AB \neq BA`)}؛ ترتیب مهم است.`, 'اندازه‌های وسط باید برابر باشند؛ اندازه‌های بیرونی، اندازه‌ی جواب‌اند.', `${E('AI = IA = A')}.`],
    use: `یک لایه‌ی شبکه‌ی عصبی برای یک دسته ورودی = یک ضرب ماتریس (${E(String.raw`W \cdot X`)}). یادگیری عمیق = زنجیره‌ی ضرب ماتریس با قدم‌های غیرخطی بین آن‌ها؛ GPU برای همین است. توجه در ترنسفورمرها: ${E(String.raw`Q \cdot K^{T}`)}.`,
    mistake: `خانه به خانه ضرب کردن به‌جای «سطر با ستون»، جابه‌جا کردن ترتیب (${E('AB')} به‌جای ${E('BA')})، یا ضرب کردن ماتریس‌هایی که اندازه‌ی وسطشان جور نیست.`,
  },
});
