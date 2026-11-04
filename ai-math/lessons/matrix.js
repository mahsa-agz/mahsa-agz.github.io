// ---------- Vectors & Matrices: Matrix ----------
// uses vecPlane / clampV from lessons/vectors.js
// a number for LaTeX (Latin digits, 2 decimals); a negative one inside a sum gets parentheses: 3 + (-2)
const MAT_n = n => String(Math.round(n * 100) / 100);
const MAT_p = n => (n < 0 ? `(${MAT_n(n)})` : MAT_n(n));
// a colored LaTeX piece
const MAT_C = (c, tex) => `<span style="color:var(--${c})">${E(tex)}</span>`;
// a 2×2 matrix in LaTeX (numbers or letters)
const MAT_M = (a, b, c, d) => {
  const f = x => (typeof x === 'number' ? MAT_n(x) : x);
  return String.raw`\begin{bmatrix} ${f(a)} & ${f(b)} \\ ${f(c)} & ${f(d)} \end{bmatrix}`;
};
// a vector [x, y] in LaTeX
const MAT_V = (x, y) => `[${MAT_n(x)}, ${MAT_n(y)}]`;
const MAT_DOT = String.raw`\cdot`;

// preset machines: [button label, a, b, c, d, what it does]
const MAT_PRESETS = [
  ['همانی', 1, 0, 0, 1, 'هیچ تغییری: همه‌چیز سر جایش ماند.'],
  ['کش ×۲', 2, 0, 0, 1, 'چپ و راست دو برابر کش آمد؛ بالا و پایین همان ماند.'],
  ['چرخش ۹۰°', 0, -1, 1, 0, 'کل صفحه ۹۰ درجه چرخید (خلاف عقربه‌های ساعت).'],
  ['آینه', -1, 0, 0, 1, 'چپ و راست جابه‌جا شد، مثل آینه.'],
  ['کج', 1, 1, 0, 1, 'هر نقطه به اندازه‌ی ارتفاعش به راست سُر خورد؛ مربع کج شد.'],
];
const MAT_is = (s, p) => s.a === p[1] && s.b === p[2] && s.c === p[3] && s.d === p[4];
const MAT_set = (s, p) => { [s.a, s.b, s.c, s.d] = p.slice(1, 5); };
const MAT_note = s => {
  const p = MAT_PRESETS.find(q => MAT_is(s, q));
  if (p) return p[5];
  const det = s.a * s.d - s.b * s.c;
  return det === 0 ? 'کل صفحه روی یک خط (یا یک نقطه) له شد.'
    : det < 0 ? 'صفحه برعکس شد، مثل آینه (شاید کش هم آمده یا کج شده باشد).'
    : 'صفحه کش آمد، چرخید یا کج شد؛ ولی خط‌ها صاف و موازی ماندند.';
};

// filled polygon in plane coordinates
const MAT_poly = (g, pts, color, alpha) => {
  const c = g.ctx;
  c.beginPath(); pts.forEach(([x, y], i) => (i ? c.lineTo(g.X(x), g.Y(y)) : c.moveTo(g.X(x), g.Y(y)))); c.closePath();
  c.globalAlpha = alpha; c.fillStyle = g.css(color); c.fill(); c.globalAlpha = 1;
};

// the grid after the machine: every grid line goes where the matrix sends it
const MAT_grid = (g, s) => {
  const T = (x, y) => [s.a * x + s.b * y, s.c * x + s.d * y];
  g.ctx.globalAlpha = 0.45;
  for (let t = -5; t <= 5; t++) {
    const [p, q] = T(t, -8), [r, u] = T(t, 8), [p2, q2] = T(-8, t), [r2, u2] = T(8, t);
    g.line(p, q, r, u, 'orange', 1.5); g.line(p2, q2, r2, u2, 'orange', 1.5);
  }
  g.ctx.globalAlpha = 1;
};

// picture 1: four sliders = the machine; the unit square, the grid and the arrow [1, 1] follow it
const MAT_W_MACHINE = h => {
  const sync = s => h.querySelectorAll('input[type=range]').forEach((inp, i) => { inp.value = s['abcd'[i]]; });
  return vecPlane(h, {
    labels: true,
    state: { a: 2, b: 0, c: 0, d: 1 },
    sliders: ['a', 'b', 'c', 'd'].map(k => ({ key: k, label: `${k}:`, min: -2, max: 2, step: 0.5 })),
    buttons: MAT_PRESETS.map(p => ({ label: p[0], on: s => { MAT_set(s, p); sync(s); }, active: s => MAT_is(s, p) })),
    draw: (g, s) => {
      g.grid();
      MAT_grid(g, s);
      [[0, 0, 1, 0], [1, 0, 1, 1], [1, 1, 0, 1], [0, 1, 0, 0]].forEach(([x, y, z, w]) => g.line(x, y, z, w, 'muted', 2, [5, 5]));
      const sq = [[0, 0], [s.a, s.c], [s.a + s.b, s.c + s.d], [s.b, s.d]];
      MAT_poly(g, sq, 'green', 0.25);
      sq.forEach((p, i) => { const q = sq[(i + 1) % 4]; g.line(p[0], p[1], q[0], q[1], 'green', 2); });
      g.arrow(0, 0, s.a + s.b, s.c + s.d, 'green', 7);
      g.arrow(0, 0, 1, 1, 'blue', 4);
      g.dot(0, 0, 'ink', 5);
    },
    read: s => `ماشین ضرب در پیکان آبی = پیکان سبز:<br>` +
      N(`${MAT_C('orange', MAT_M(s.a, s.b, s.c, s.d))} ${E(MAT_DOT)} ${MAT_C('blue', '[1, 1]')} ${E('=')} ${MAT_C('green', MAT_V(s.a + s.b, s.c + s.d))}`) +
      `<br><b>${MAT_note(s)}</b>`,
  });
};

// picture 2: drag v; the chosen machine sends it to Av; the readout does each row · v
const MAT_W_APPLY = h => vecPlane(h, {
  labels: true,
  state: { a: 1, b: 1, c: 0, d: 1, x: 2, y: 1 },
  handles: [{ get: s => [s.x, s.y], set: (s, x, y) => { [s.x, s.y] = clampV(x, y).map(n => Math.max(-2, Math.min(2, n))); }, color: 'blue' }],
  buttons: MAT_PRESETS.map(p => ({ label: p[0], on: s => MAT_set(s, p), active: s => MAT_is(s, p) })),
  draw: (g, s) => {
    g.grid();
    const ox = s.a * s.x + s.b * s.y, oy = s.c * s.x + s.d * s.y;
    g.line(s.x, s.y, ox, oy, 'muted', 2, [6, 6]);
    g.arrow(0, 0, ox, oy, 'green', 7);
    g.arrow(0, 0, s.x, s.y, 'blue', 4);
    g.dot(0, 0, 'ink', 5);
  },
  read: s => {
    const r1 = s.a * s.x + s.b * s.y, r2 = s.c * s.x + s.d * s.y, v = MAT_C('blue', MAT_V(s.x, s.y));
    const row = (p, q, r) => N(`${MAT_C('orange', MAT_V(p, q))} ${E(MAT_DOT)} ${v} ` +
      E(String.raw`= ${MAT_p(p)} \times ${MAT_p(s.x)} + ${MAT_p(q)} \times ${MAT_p(s.y)} = \mathbf{${MAT_n(r)}}`));
    return `سطر ۱ ضرب داخلی v، خانه‌ی اول جواب: ${row(s.a, s.b, r1)}<br>سطر ۲ ضرب داخلی v، خانه‌ی دوم: ${row(s.c, s.d, r2)}<br>` +
      N(`${MAT_C('orange', MAT_M(s.a, s.b, s.c, s.d))} ${E(MAT_DOT)} ${v} ${E('=')} ${MAT_C('green', MAT_V(r1, r2))}`);
  },
});

const MAT_TABLE = `<table dir="rtl" style="border-collapse:collapse;margin:8px auto;text-align:center">
  <tr><td></td><td style="padding:2px 10px"><b>نان</b></td><td style="padding:2px 10px"><b>شیر</b></td><td style="padding:2px 10px"><b>پنیر</b></td></tr>
  <tr><td style="padding:2px 10px"><b>شنبه</b></td><td style="color:var(--blue)">۱۲</td><td style="color:var(--blue)">۸</td><td style="color:var(--blue)">۵</td></tr>
  <tr><td style="padding:2px 10px"><b>یکشنبه</b></td><td style="color:var(--blue)">۱۰</td><td style="color:var(--blue)">۹</td><td style="color:var(--blue)">۳</td></tr></table>`;
const MAT_X = (m, n) => E(String.raw`${m} \times ${n}`);

lesson({
  id: 'matrix', node: 'matrix', title: 'ماتریس', en: 'Matrix',
  parts: [
    { name: 'چرا و یعنی چه؟', cards: [
      { t: 'story', title: `ماتریس ${EN('Matrix')}`,
        body: `<p>یک مغازه فروش ۳ کالا را در ۴ روز می‌نویسد. یک معلم نمره‌ی ۳۰ دانش‌آموز را در ۵ درس. هر دو یک <b>جدول عدد</b> دارند.</p>
               <p>نمی‌خواهیم عدد به عدد حساب کنیم؛ می‌خواهیم با <b>کل جدول</b> یک‌جا کار کنیم.</p>
               <div class="key">و یک معنی عمیق‌تر: همین جدول می‌تواند یک <b>ماشین</b> باشد که بردار می‌گیرد و کل صفحه را کش می‌دهد، می‌چرخاند یا برمی‌گرداند.</div>`,
        who: 'حدود ۲۰۰۰ سال پیش، کتاب چینی «نُه فصل» دستگاه معادله‌ها را با جدول عدد حل می‌کرد. کِیلی (Cayley) در ۱۸۵۸ حساب با ماتریس‌ها را مثل حساب با عدد مرتب کرد.' },
      { t: 'text', title: 'معنی ساده',
        body: `<div class="key">ماتریس یعنی جدولی از عددها، با <b>سطر</b> ${EN('Row')} و <b>ستون</b> ${EN('Column')}.</div>
               ${MAT_TABLE}
               <p>این ماتریس ${MAT_X(2, 3)} است: ۲ سطر، ۳ ستون. همیشه اول سطر، بعد ستون.</p>
               <p>دو نگاه به آن:<br>۱. <b>جدول داده</b>: هر سطر یک نمونه است (یک روز، یعنی یک بردار)، هر ستون یک ویژگی (یک کالا).<br>۲. <b>ماشین</b>: یک بردار به آن بدهید، بردار تازه‌ای می‌گیرید.</p>` },
      { t: 'play', w: MAT_W_MACHINE, title: 'ماتریس، ماشینِ تغییر صفحه',
        body: `چهار عدد a، b، c، d ماتریس ${E(MAT_M('a', 'b', 'c', 'd'))} را می‌سازند. مربع خط‌چین به مربع <b style="color:var(--green)">سبز</b> می‌رود، خط‌های <b style="color:var(--orange)">نارنجی</b> جای تازه‌ی شبکه‌اند، و پیکان <b style="color:var(--blue)">آبی</b> [۱، ۱] به پیکان <b style="color:var(--green)">سبز</b> می‌رود.`,
        look: [
          'اول «کش ×۲» روشن است → مربع دو برابر پهن شده و پیکان [۱، ۱] به [۲، ۱] رفته است.',
          `«چرخش ۹۰°» را بزنید → [۱، ۱] به [−۱، ۱] می‌رود: ${E(String.raw`0 \times 1 + (-1) \times 1 = -1`)} و ${E(String.raw`1 \times 1 + 0 \times 1 = 1`)}. کل شبکه چرخید.`,
          '«کج» را بزنید → مربع سبز کج می‌شود (متوازی‌الاضلاع)، ولی خط‌های نارنجی هنوز صاف و موازی‌اند.',
          'با لغزنده‌ها a = ۱، b = ۲، c = ۰٫۵، d = ۱ بگذارید → کل صفحه روی یک خط له می‌شود و [۱، ۱] به [۳، ۱٫۵] می‌رود.',
        ],
        see: 'فقط چهار عدد، کل صفحه را کش می‌دهند، می‌چرخانند، برمی‌گردانند یا کج می‌کنند. ستون اول ماتریس جای تازه‌ی [۱، ۰] است و ستون دوم جای [۰، ۱]. هر لایه‌ی شبکه‌ی عصبی همین کار را با داده‌ها می‌کند، فقط با فهرست‌های خیلی بلندتر.' },
      { t: 'life', title: 'ماتریس در زندگی', items: [
        { h: 'جدول فروش (اکسل)', d: 'هر سطر یک روز، هر ستون یک کالا. جمع هر ستون = فروش کل آن کالا.' },
        { h: 'عکس سیاه‌وسفید', d: 'هر نقطه یک عدد روشنایی است: ۰ سیاه، ۲۵۵ سفید. عکس یعنی یک ماتریس بزرگ از این عددها.' },
        { h: 'فیلتر اینستاگرام', d: `یک ماتریس ${MAT_X(3, 3)} از عددها، سه رنگ قرمز، سبز و آبی هر نقطه را با هم <b>مخلوط</b> می‌کند و رنگ تازه می‌سازد؛ مثلاً حالت قهوه‌ای قدیمی.` },
        { h: 'چرخاندن نقشه در گوشی', d: 'وقتی نقشه را با دو انگشت می‌چرخانید، یک ماتریس چرخش همه‌ی نقطه‌ها را با هم می‌چرخاند.' },
      ] },
      { t: 'sort', title: 'این یک ماتریس است؟', yes: 'ماتریس است', no: 'ماتریس نیست', items: [
        { q: 'جدول نمره‌های ۳۰ دانش‌آموز در ۵ درس', a: true, why: `۳۰ سطر، ۵ ستون: یک ماتریس ${MAT_X(30, 5)}.` },
        { q: 'قیمت یک کیلو سیب: ۳۰ هزار تومان', a: false, why: `یک عدد تنهاست؛ به آن اسکالر (Scalar) می‌گوییم، نه جدول. (اگر خیلی دقیق باشیم ماتریس ${MAT_X(1, 1)} هم هست، ولی کسی آن را این‌طور صدا نمی‌کند.)` },
        { q: E('[2, 1, 4]'), a: true, why: `هم بردار است، هم ماتریسی با ۱ سطر و ۳ ستون (${MAT_X(1, 3)}). هر دو حرف درست است.` },
        { q: 'یک عکس سیاه‌وسفید', a: true, why: `هر نقطه یک عدد روشنایی است؛ عکسی با ۶۰۰ ردیف و ۸۰۰ ستون نقطه، یک ماتریس ${MAT_X(600, 800)} است.` },
        { q: 'جمله‌ی «امروز هوا خوب است»', a: false, why: 'کلمه است، نه عدد. ولی اگر هر کلمه را به یک بردار تبدیل کنیم (Embedding)، جمله ماتریس می‌شود: هر کلمه یک سطر.' },
      ] },
      { t: 'quiz', q: 'مغازه‌ای فروش ۳ کالا را در ۴ روز می‌نویسد؛ هر روز یک سطر. اندازه‌ی این ماتریس چیست؟',
        options: [MAT_X(4, 3), MAT_X(3, 4), '۱۲'], answer: 0,
        why: `۴ روز = ۴ سطر، ۳ کالا = ۳ ستون؛ و اول سطر می‌آید: ${MAT_X(4, 3)}. (${MAT_X(3, 4)} یعنی سطر و ستون جابه‌جا شده. ۱۲ تعداد خانه‌هاست، نه اندازه.)` },
    ] },
    { name: 'فرمول', cards: [
      { t: 'formula', f: String.raw`\Co{\begin{bmatrix} a & b \ c & d \end{bmatrix}} \Cb{\begin{bmatrix} x \ y \end{bmatrix}} = \Cg{\begin{bmatrix} ax + by \ cx + dy \end{bmatrix}}`, title: `ماتریس × بردار ${EN('Matrix–Vector Product')}`,
        intro: `<p>ماتریس را با حرف بزرگ می‌نویسیم: A. اندازه‌اش ${MAT_X('m', 'n')} یعنی m سطر و n ستون. خانه‌ی سطر i و ستون j را ${E('a_{ij}')} می‌نویسیم؛ مثلاً ${E('a_{12}')} = سطر ۱، ستون ۲.</p>
               <p>برای ${MAT_X(2, 2)} ساده‌تر می‌نویسیم: a، b، c، d.</p>`,
        toks: [{ s: MAT_M('a', 'b', 'c', 'd'), c: 'orange', l: 'ماتریس A (ماشین)' }, { s: MAT_DOT }, { s: '[x, y]', c: 'blue', l: 'بردار v' }, { s: '=' },
               { s: '[ax + by,', c: 'green', l: 'سطر ۱ ضرب داخلی v' }, { s: 'cx + dy]', c: 'green', l: 'سطر ۲ ضرب داخلی v' }],
        read: 'خوانده می‌شود: «A ضرب در v».',
        note: '<p>هر خانه‌ی جواب = <b>ضرب داخلیِ یک سطر</b> با بردار (درس قبل): خانه‌ها را در هم ضرب کن، بعد جمع کن.</p>' },
      { t: 'example', title: 'قیمت یک سبد در دو مغازه',
        intro: `<p>این بار ماتریس را <b>ماشین</b> می‌بینیم. هر سطر، قیمت‌های یک مغازه (هزار تومان) برای (نان، شیر) است. سبد شما: ${E('v = [1, 2]')}، یعنی ۱ نان و ۲ شیر.</p>
                <p class="read">${N(`${MAT_C('orange', MAT_M(2, 1, 1, 3))} ${E(MAT_DOT)} ${MAT_C('blue', '[1, 2]')}`)}</p>`,
        steps: [
          `مغازه‌ی ۱، سطر اول ${E('[2, 1]')}: ${E(String.raw`2 \times 1 + 1 \times 2 = 2 + 2 = 4`)}`,
          `مغازه‌ی ۲، سطر دوم ${E('[1, 3]')}: ${E(String.raw`1 \times 1 + 3 \times 2 = 1 + 6 = 7`)}`,
          `دو جواب کنار هم: ${E(String.raw`${MAT_M(2, 1, 1, 3)} \cdot [1, 2] = [4, 7]`)}`,
        ],
        result: 'با یک ضرب، قیمت سبد را در <b>هر دو مغازه</b> فهمیدیم: ۴ و ۷ هزار تومان.' },
      { t: 'text', title: `ماتریس همانی ${EN('Identity Matrix')}`,
        body: `<p>این ماتریس را با I نشان می‌دهند:</p>
               <p class="read">${E(String.raw`${MAT_M(1, 0, 0, 1)} \cdot [x, y] = [1x + 0y,\ 0x + 1y] = [x, y]`)}</p>
               <div class="key">ماتریس همانی هیچ کاری نمی‌کند؛ هر بردار را همان‌طور پس می‌دهد. مثل ضرب در عدد ۱. مثلاً ${E(String.raw`I \cdot [5, 3] = [5, 3]`)}.</div>
               <p>چرا؟ سطر اول فقط x را برمی‌دارد (ضریب y صفر است) و سطر دوم فقط y را. در تصویر قبل، دکمه‌ی «همانی» همین بود.</p>` },
      { t: 'play', w: MAT_W_APPLY, title: 'سطر به سطر حساب کنید',
        body: 'پیکان <b style="color:var(--blue)">آبی</b> = بردار v (نوکش را بکشید). پیکان <b style="color:var(--green)">سبز</b> = A · v. دکمه‌ها ماشین A را عوض می‌کنند. زیر تصویر، هر <b style="color:var(--orange)">سطر</b> A با v ضرب داخلی می‌شود.',
        look: [
          `اول ماشین «کج» است و v = [۲، ۱] → سطر ۱: ${E(String.raw`1 \times 2 + 1 \times 1 = 3`)}، سطر ۲: ${E(String.raw`0 \times 2 + 1 \times 1 = 1`)}؛ پیکان سبز [۳، ۱] است.`,
          '«همانی» را بزنید → پیکان سبز درست روی آبی می‌افتد: [۲، ۱].',
          '«آینه» را بزنید و v را روی [۲، ۲] بگذارید → جواب [−۲، ۲]: فقط علامت خانه‌ی اول عوض شد.',
          '«کش ×۲» را بزنید و v را روی [۰، ۲] بگذارید → جواب همان [۰، ۲]: کش فقط چپ و راست را دو برابر می‌کند.',
        ],
        see: 'هر خانه‌ی جواب، ضرب داخلیِ یک سطر با v است؛ پس «ماتریس × بردار» یعنی چند ضرب داخلی با هم. یک لایه‌ی شبکه‌ی عصبی دقیقاً همین را حساب می‌کند: هر سطر، وزن‌های یک نورون است.' },
      { t: 'rules', title: 'سه قانون مهم', items: [
        { r: `ماتریس ${MAT_X('m', 'n')} فقط برداری با <b>n</b> خانه می‌گیرد و برداری با <b>m</b> خانه پس می‌دهد.`,
          why: `هر سطر n عدد دارد و با بردار ضرب داخلی می‌شود؛ ضرب داخلی تعداد خانه‌ی برابر می‌خواهد. هر سطر هم یک خانه‌ی جواب می‌سازد. مثلاً ماتریس ${MAT_X(2, 3)} بردار ۳ خانه‌ای می‌گیرد و ۲ خانه پس می‌دهد.` },
        { r: `<b>ستون‌های</b> A نشان می‌دهند ${V(1, 0)} و ${V(0, 1)} کجا می‌روند.`,
          why: `${E(String.raw`A \cdot [1, 0] = [a \times 1 + b \times 0,\ c \times 1 + d \times 0] = [a, c]`)} = ستون اول. هر بردار ${E('[x, y]')} یعنی x تا [۱، ۰] به‌علاوه‌ی y تا [۰، ۱]، پس کل شبکه دنبال همین دو ستون می‌رود.` },
        { r: '<b>جمع</b> دو ماتریس هم‌اندازه، خانه به خانه است. ولی <b>ضرب</b> دو ماتریس خانه به خانه نیست.',
          why: 'هر خانه یک چیز مشخص را نشان می‌دهد (فروش نان در شنبه)؛ فروش دو هفته را خانه به خانه جمع می‌کنیم، مثل جمع بردارها. ضرب، کار ماشین‌هاست: درس بعد.' },
      ] },
      { t: 'ai', title: 'ماتریس در هوش مصنوعی',
        body: `<p>• <b>هر داده‌ای یک ماتریس است</b> ${EN('Dataset')}: هر سطر یک نمونه (یک خانه، یک بیمار)، هر ستون یک ویژگی ${EN('Feature')} مثل متراژ یا سن.</p>
               <p>• یک <b>لایه</b>‌ی شبکه‌ی عصبی = ${E(String.raw`W \cdot x + b`)}. هر سطرِ ${E('W')} وزن‌های یک نورون است، پس <b>وزن‌ها</b> ${EN('Weights')} یک ماتریس‌اند. لایه‌ای با ۳ نورون روی ورودیِ (قد، وزن)، ماتریسی ${MAT_X(3, 2)} دارد.</p>
               <p>• کارت گرافیک ${EN('GPU')} هزاران ضرب را هم‌زمان انجام می‌دهد؛ برای همین ماتریس‌های غول‌پیکر را سریع ضرب می‌کند.</p>` },
      { t: 'quiz', q: E(String.raw`${MAT_M(1, 2, 3, 0)} \cdot [2, 1] = \,?`),
        options: [V(5, 4), V(4, 6), V(2, 6)], answer: 1,
        why: `سطر ۱: ${E(String.raw`1 \times 2 + 2 \times 1 = 4`)}. سطر ۲: ${E(String.raw`3 \times 2 + 0 \times 1 = 6`)}. پس [۴، ۶]. ([۵، ۴] یعنی ستون‌ها را به‌جای سطرها با بردار ضرب کرده‌ایم. [۲، ۶] یعنی فقط x را در هر سطر ضرب کرده‌ایم و y را فراموش کرده‌ایم.)` },
      { t: 'text', title: 'یک سؤال برای درس بعد',
        body: `<p>اول صفحه را ۹۰ درجه بچرخانیم، بعد دو برابر کش بدهیم. دو ماشین، پشت سر هم.</p>
               <div class="key">آیا یک ماشینِ تنها هست که هر دو کار را یک‌جا بکند؟</div>
               <p>بله، و پیدا کردنش یعنی <b>ضرب ماتریس</b> ${EN('Matrix Multiplication')}. درس بعد!</p>` },
    ] },
  ],
  sheet: {
    one: 'ماتریس = جدولی از عددها با سطر و ستون. دو نگاه: جدول داده (هر سطر یک نمونه) یا ماشینی که بردار می‌گیرد و بردار تازه می‌دهد. ساخته شد تا با کل یک جدول یک‌جا حساب کنیم.',
    f: String.raw`${MAT_M('a', 'b', 'c', 'd')} \cdot [x, y] = [ax + by,\ cx + dy]`,
    rules: [`اندازه = سطر × ستون (اول سطر).`, `هر خانه‌ی ${E(String.raw`A \cdot v`)} = ضرب داخلیِ یک سطر با v؛ ماتریس ${MAT_X('m', 'n')} برداری با n خانه می‌گیرد.`, 'ستون‌های A = جای تازه‌ی [۱، ۰] و [۰، ۱].', 'ماتریس همانی I هیچ کاری نمی‌کند. جمع ماتریس‌ها خانه به خانه است.'],
    use: `داده‌ها یک ماتریس‌اند (سطر = نمونه، ستون = ویژگی). هر لایه‌ی شبکه‌ی عصبی ${E(String.raw`W \cdot x + b`)} است و وزن‌ها یک ماتریس‌اند؛ GPU این ضرب‌ها را هم‌زمان انجام می‌دهد.`,
    mistake: `جابه‌جا کردن سطر و ستون (${MAT_X(4, 3)} با ${MAT_X(3, 4)} فرق دارد)، یا ضرب کردن ستون‌ها به‌جای سطرها با بردار.`,
  },
});
