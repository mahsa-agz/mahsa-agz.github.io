// ---------- Vectors: Dot Product and Cosine Similarity ----------
// uses vecPlane / clampV from lessons/vectors.js
// a number for LaTeX (Latin digits, 2 decimals); a negative one inside a sum gets parentheses: 3 + (-2)
const DOT_n = n => String(Math.round(n * 100) / 100);
const DOT_p = n => (n < 0 ? `(${DOT_n(n)})` : DOT_n(n));
// a colored LaTeX piece
const DOT_C = (c, tex) => `<span style="color:var(--${c})">${E(tex)}</span>`;

// shade the angle between the two arrows: green if a·b > 0, grey if 0, red if < 0
const DOT_angle = (g, ax, ay, bx, by) => {
  if (!(ax || ay) || !(bx || by)) return;
  const A = Math.atan2(ay, ax);
  let d = Math.atan2(by, bx) - A;
  if (d > Math.PI) d -= 2 * Math.PI;
  if (d < -Math.PI) d += 2 * Math.PI;
  const dot = ax * bx + ay * by, c = g.ctx, x = g.X(0), y = g.Y(0);
  c.globalAlpha = 0.25;
  c.fillStyle = g.css(dot > 0 ? 'green' : dot < 0 ? 'red' : 'muted');
  c.beginPath(); c.moveTo(x, y); c.arc(x, y, 34, -A, -(A + d), d > 0); c.closePath(); c.fill();
  c.globalAlpha = 1;
};

const DOT_handles = () => [
  { get: s => [s.ax, s.ay], set: (s, x, y) => { [s.ax, s.ay] = clampV(x, y); }, color: 'blue' },
  { get: s => [s.bx, s.by], set: (s, x, y) => { [s.bx, s.by] = clampV(x, y); }, color: 'orange' },
];

// two arrows; the readout multiplies matching cells and adds them
const DOT_W_DOT = h => vecPlane(h, {
  labels: true,
  state: { ax: 3, ay: 1, bx: 1, by: 3 },
  handles: DOT_handles(),
  draw: (g, s) => {
    g.grid();
    DOT_angle(g, s.ax, s.ay, s.bx, s.by);
    const A2 = s.ax * s.ax + s.ay * s.ay;
    if (A2 && (s.bx || s.by)) {
      // shadow of the orange arrow on the line of the blue arrow
      const t = (s.ax * s.bx + s.ay * s.by) / A2, fx = t * s.ax, fy = t * s.ay;
      g.line(s.bx, s.by, fx, fy, 'muted', 2, [6, 6]);
      g.line(0, 0, fx, fy, 'green', 10);
    }
    g.arrow(0, 0, s.ax, s.ay, 'blue', 5);
    g.arrow(0, 0, s.bx, s.by, 'orange', 5);
    g.dot(0, 0, 'ink', 5);
  },
  read: s => {
    const p = s.ax * s.bx, q = s.ay * s.by, d = p + q;
    const zero = !(s.ax || s.ay) || !(s.bx || s.by);
    const note = zero ? 'یکی از پیکان‌ها صفر است، پس حاصل هم صفر است.'
      : d > 0 ? '<b style="color:var(--green)">مثبت</b>: کم‌وبیش به یک سمت می‌روند (هم‌جهت).'
      : d < 0 ? '<b style="color:var(--red)">منفی</b>: کم‌وبیش رو در روی هم‌اند (خلاف جهت).'
      : '<b>صفر</b>: درست عمود بر هم‌اند (به هم ربطی ندارند).';
    return 'خانه‌ی اول × خانه‌ی اول، به‌علاوه‌ی خانه‌ی دوم × خانه‌ی دوم:<br>' +
      N(`${DOT_C('blue', `[${DOT_n(s.ax)}, ${DOT_n(s.ay)}]`)} ${E(String.raw`\cdot`)} ${DOT_C('orange', `[${DOT_n(s.bx)}, ${DOT_n(s.by)}]`)}`) + '<br>' +
      E(String.raw`= ${DOT_p(s.ax)} \times ${DOT_p(s.bx)} + ${DOT_p(s.ay)} \times ${DOT_p(s.by)} = ${DOT_p(p)} + ${DOT_p(q)} = \mathbf{${DOT_n(d)}}`) +
      `<br>${note}`;
  },
});

// cosine similarity with a meter from −1 to 1
const DOT_meter = c => {
  const p = (c + 1) / 2 * 100;
  return `<div dir="ltr" style="position:relative;height:12px;border-radius:6px;margin:12px 6px 4px;background:linear-gradient(90deg,var(--red),var(--line),var(--green))">` +
    `<div style="position:absolute;top:-5px;left:calc(${p}% - 3px);width:6px;height:22px;border-radius:3px;background:var(--ink)"></div></div>` +
    `<div dir="ltr" style="display:flex;justify-content:space-between;font-size:12px;color:var(--muted);margin:0 2px"><span>−۱</span><span>۰</span><span>۱</span></div>`;
};

const DOT_W_COS = h => vecPlane(h, {
  labels: true,
  state: { ax: 2, ay: 1, bx: 1, by: 1 },
  handles: DOT_handles(),
  draw: (g, s) => {
    g.grid();
    DOT_angle(g, s.ax, s.ay, s.bx, s.by);
    g.arrow(0, 0, s.ax, s.ay, 'blue', 5);
    g.arrow(0, 0, s.bx, s.by, 'orange', 5);
    g.dot(0, 0, 'ink', 5);
  },
  read: s => {
    const A2 = s.ax * s.ax + s.ay * s.ay, B2 = s.bx * s.bx + s.by * s.by, d = s.ax * s.bx + s.ay * s.by;
    if (!A2 || !B2) return 'یکی از پیکان‌ها صفر است. پیکان صفر جهت ندارد، پس شباهتِ جهت هم معنی ندارد.';
    const la = Math.sqrt(A2), lb = Math.sqrt(B2), c = d / (la * lb);
    // a length is shown as a whole number or as a square root; "=" only when the answer needs no rounding
    const len = (n2, l) => (Number.isInteger(l) ? `${l}` : String.raw`\sqrt{${n2}}`);
    const eq = Math.abs(c * 100 - Math.round(c * 100)) < 1e-9 ? '=' : String.raw`\approx`;
    const word = c > 0.9999 ? 'دقیقاً هم‌جهت' : c < -0.9999 ? 'دقیقاً خلاف جهت' : d > 0 ? 'کم‌وبیش هم‌جهت' : d < 0 ? 'کم‌وبیش خلاف جهت' : 'عمود: بی‌ربط';
    return `بالای کسر: ضرب داخلی (${fa(d)}). پایین: طول آبی × طول نارنجی.<br>` +
      `شباهت: ${E(String.raw`\frac{${d}}{${len(A2, la)} \times ${len(B2, lb)}} ${eq} \mathbf{${DOT_n(c)}}`)}، یعنی <b>${word}</b>` +
      DOT_meter(c);
  },
});

lesson({
  id: 'dot-product', node: 'dot-product', title: 'ضرب داخلی و شباهت', en: 'Dot Product',
  parts: [
    { name: 'چرا و یعنی چه؟', cards: [
      { t: 'story', title: `ضرب داخلی ${EN('Dot Product')}`,
        body: `<p>سه نفر به فیلم‌ها نمره می‌دهند (هیجان، خنده، ترس): علی ${E('[8, 6, 2]')}، رضا ${E('[4, 3, 1]')}، سارا ${E('[5, 6, 6]')}.</p>
               <p>رضا <b>دقیقاً</b> سلیقه‌ی علی را دارد، فقط به همه‌چیز نصفِ نمره می‌دهد. سارا ولی فیلم ترسناک دوست دارد و علی نه.</p>
               <p>ولی فاصله می‌گوید سارا (۵) از رضا (حدود ۵٫۱) به علی نزدیک‌تر است!</p>
               <div class="key">مشکل: فاصله «چقدر بزرگ» را هم می‌سنجد. ما فقط می‌خواهیم بدانیم دو پیکان <b>به یک سمت</b> می‌روند یا نه.</div>`,
        who: 'حسابش قدیمی است: فاکتور خرید (مقدار × قیمت، همه با هم جمع) همین است. اسم و نقطه‌ی وسطش را گیبز (Gibbs) و هویساید (Heaviside) در دهه‌ی ۱۸۸۰ رایج کردند.' },
      { t: 'text', title: 'معنی ساده',
        body: `<div class="key">ضرب داخلی = خانه‌های هم‌شماره را <b>در هم ضرب کن</b>، بعد همه را <b>جمع کن</b>. جواب یک <b>عدد</b> است، نه بردار.</div>
               <p class="read">${E(String.raw`[2, 1] \cdot [3, 4] = 2 \times 3 + 1 \times 4 = 6 + 4 = 10`)}</p>
               <p>• <b style="color:var(--green)">مثبت</b>: کم‌وبیش هم‌جهت‌اند (موافق).<br>• <b>صفر</b>: عمود بر هم‌اند (بی‌ربط).<br>• <b style="color:var(--red)">منفی</b>: خلاف جهت‌اند (مخالف).</p>
               <p>نقطه‌ی وسط (${E(String.raw`\cdot`)}) یعنی «ضرب داخلی».</p>` },
      { t: 'play', w: DOT_W_DOT, title: 'دو پیکان، یک عدد',
        body: 'پیکان <b style="color:var(--blue)">آبی</b> و <b style="color:var(--orange)">نارنجی</b> را با نوکشان بکشید. خط <b style="color:var(--green)">سبز</b> «سایه‌ی» نارنجی روی خط آبی است. رنگ گوشه‌ی بین دو پیکان: سبز = مثبت، خاکستری = صفر، قرمز = منفی.',
        look: [
          `همان‌طور که هست ببینید: آبی [۳، ۱]، نارنجی [۱، ۳] → ${E(String.raw`3 \times 1 + 1 \times 3 = 6`)}؛ مثبت و گوشه سبز.`,
          `نوک نارنجی را روی [−۱، ۳] بگذارید → ${E(String.raw`3 \times (-1) + 1 \times 3 = 0`)}؛ دو پیکان عمودند، گوشه خاکستری و سایه ناپدید می‌شود.`,
          `نارنجی را روی [−۳، −۱] بگذارید → ${E(String.raw`-9 + (-1) = -10`)}؛ منفی، گوشه قرمز و سایه پشتِ سرِ آبی می‌افتد.`,
          'آبی را روی [۱، ۰] و نارنجی را روی [۲، ۳] بگذارید → جواب ۲، درست برابر طول سایه، چون طول آبی ۱ است.',
        ],
        see: 'ضرب داخلی یک عدد است که می‌گوید دو پیکان چقدر به یک سمت می‌روند: مثبت یعنی هم‌جهت، صفر یعنی عمود، منفی یعنی خلاف جهت. این عدد همان «طول سایه × طول آبی» است. هوش مصنوعی با همین عدد می‌سنجد دو چیز چقدر به هم ربط دارند.' },
      { t: 'life', title: 'ضرب داخلی در زندگی', items: [
        { h: 'فاکتور خرید', d: `مقدار ${E('[2, 1]')} (۲ کیلو سیب، ۱ کیلو پرتقال) ${E(String.raw`\cdot`)} قیمت هر کیلو ${E('[30, 50]')} هزار تومان: ${E(String.raw`2 \times 30 + 1 \times 50 = 110`)}، یعنی <b>۱۱۰ هزار تومان</b>.` },
        { h: 'معدل', d: `نمره‌ها ${E('[18, 15]')} ${E(String.raw`\cdot`)} واحدها ${E('[3, 2]')} = ${E(String.raw`54 + 30 = 84`)}. تقسیم بر ۵ واحد: معدل ۱۶٫۸.` },
        { h: 'سلیقه و فیلم', d: 'سلیقه‌ی شما (هیجان، خنده، ترس) ضرب داخلی در ویژگی‌های فیلم. عدد بزرگ یعنی احتمالاً از فیلم خوشتان می‌آید.' },
        { h: 'باد و دوچرخه', d: 'باد از پشت: کمک می‌کند (مثبت). باد از پهلو: نه کمک، نه مانع (صفر). باد از روبه‌رو: مانع است (منفی). فقط آن تکه از باد که در امتداد جاده است مهم است.' },
      ] },
      { t: 'sort', title: 'حاصل این ضرب داخلی مثبت است؟', yes: 'مثبت است', no: 'مثبت نیست', items: [
        { q: E(String.raw`[2, 1] \cdot [3, 1]`), a: true, why: `${E('6 + 1 = 7')}. هر دو به راست و کمی بالا می‌روند.` },
        { q: E(String.raw`[1, 0] \cdot [0, 1]`), a: false, why: `${E('0 + 0 = 0')}، <b>صفر</b>. یکی به راست، یکی به بالا: عمود بر هم.` },
        { q: E(String.raw`[2, 1] \cdot [-2, -1]`), a: false, why: `${E('-4 + (-1) = -5')}، <b>منفی</b>. دومی همان اولی است، رو به عقب.` },
        { q: E(String.raw`[3, -1] \cdot [1, 2]`), a: true, why: `${E('3 + (-2) = 1')}. یک عدد منفی دارد، ولی جمعش هنوز مثبت است.` },
        { q: E(String.raw`[1, 2] \cdot [-2, 1]`), a: false, why: `${E('-2 + 2 = 0')}، <b>صفر</b>. این دو هم عمودند، با اینکه کج‌اند.` },
      ] },
      { t: 'quiz', q: E(String.raw`[3, 2] \cdot [1, 4] = \,?`),
        options: ['۱۱', '۱۴', '۱۰'], answer: 0,
        why: `${E(String.raw`3 \times 1 + 2 \times 4 = 3 + 8 = 11`)}. (۱۴ یعنی ضربدری ضرب کرده‌ایم: ${E(String.raw`3 \times 4 + 2 \times 1`)}؛ باید خانه‌ی اول با اول باشد. ۱۰ جمعِ همه‌ی عددهاست، بدون ضرب.)` },
    ] },
    { name: 'فرمول', cards: [
      { t: 'formula', f: String.raw`\Cg{a \cdot b} = \Cb{a_1 b_1} + \Co{a_2 b_2} \Cm{+ \dots}`, title: `فرمول ضرب داخلی ${EN('Dot Product')}`,
        intro: `<p>دو بردار ${E('a = [a_1, a_2]')} و ${E('b = [b_1, b_2]')}. عدد کوچکِ پایین می‌گوید خانه‌ی چندم.</p>`,
        toks: [{ s: String.raw`a \cdot b`, c: 'green', l: 'ضرب داخلی (یک عدد)' }, { s: '=' }, { s: 'a_1 b_1', c: 'blue', l: 'خانه‌ی اول × خانه‌ی اول' },
               { s: '+' }, { s: 'a_2 b_2', c: 'orange', l: 'خانه‌ی دوم × خانه‌ی دوم' }, { s: String.raw`+ \dots`, c: 'muted', l: 'اگر خانه‌ی بیشتری باشد' }],
        read: 'خوانده می‌شود: «a ضرب داخلی b برابر است با a یک در b یک، به‌علاوه‌ی a دو در b دو».',
        note: `<p>دو حرف کنار هم (مثل ${E('a_1 b_1')}) یعنی در هم ضرب‌شان کن. تعداد خانه‌ها باید برابر باشد.</p>` },
      { t: 'example', title: 'فاکتور سوپرمارکت',
        intro: `<p>سبد شما: ۳ نان، ۲ شیر، ۱ پنیر، یعنی ${E('[3, 2, 1]')}. قیمت هر کدام (هزار تومان): ${E('[5, 15, 40]')}.</p>`,
        steps: [
          `نان: ${E(String.raw`3 \times 5 = 15`)}`,
          `شیر: ${E(String.raw`2 \times 15 = 30`)}`,
          `پنیر: ${E(String.raw`1 \times 40 = 40`)}`,
          `جمع: ${E('15 + 30 + 40 = 85')}`,
        ],
        result: `${E(String.raw`[3, 2, 1] \cdot [5, 15, 40] = 85`)}: کل فاکتور ۸۵ هزار تومان است. صندوق‌دار هر روز ضرب داخلی حساب می‌کند!` },
      { t: 'formula', f: String.raw`\Cg{\cos(a, b)} = \Co{\frac{a \cdot b}{\|a\| \, \|b\|}}`, title: `شباهت کسینوسی ${EN('Cosine Similarity')}`,
        intro: `<p>${E(String.raw`\|a\|`)} یعنی طول a؛ همان جذرِ جمعِ مربع‌ها (درس قبل). رضا نصفِ علی است، ولی ضرب داخلی‌شان ۵۲ می‌شود؛ بزرگی را باید حذف کرد. پس بر هر دو طول تقسیم می‌کنیم:</p>`,
        toks: [{ s: String.raw`\cos(a, b)`, c: 'green', l: 'شباهت' }, { s: '=' },
               { s: String.raw`\frac{a \cdot b}{\|a\| \, \|b\|}`, c: 'orange', l: 'بالا: ضرب داخلی. پایین: طول a × طول b' }],
        note: `<p>جواب بین <b>−۱</b> (خلاف جهت) و <b>۱</b> (هم‌جهت) است؛ ۰ یعنی عمود.</p>
               <p class="read">${E(String.raw`[1, 2], [2, 4]: \ \frac{10}{\sqrt{5} \times \sqrt{20}} = \frac{10}{10} = 1`)}</p>` },
      { t: 'example', title: 'علی شبیه سارا است یا رضا؟',
        intro: `<p>علی ${E('[8, 6, 2]')}، سارا ${E('[5, 6, 6]')}. شباهت را قدم به قدم حساب کنیم:</p>`,
        steps: [
          `ضرب داخلی: ${E(String.raw`8 \times 5 + 6 \times 6 + 2 \times 6 = 40 + 36 + 12 = 88`)}`,
          `طول علی: ${E(String.raw`\sqrt{64 + 36 + 4} = \sqrt{104}`)}`,
          `طول سارا: ${E(String.raw`\sqrt{25 + 36 + 36} = \sqrt{97}`)}`,
          `حاصل‌ضرب طول‌ها: ${E(String.raw`\sqrt{104} \times \sqrt{97} = \sqrt{10088} \approx 100.4`)}`,
          `شباهت: ${E(String.raw`\frac{88}{100.4} \approx 0.88`)}`,
        ],
        result: `علی و رضا: ${E(String.raw`\frac{52}{\sqrt{104} \times \sqrt{26}} = \frac{52}{52} = 1`)}. پس رضا شبیه‌ترین است، با اینکه فاصله‌اش بیشتر بود.` },
      { t: 'play', w: DOT_W_COS, title: 'فقط جهت مهم است',
        body: 'پیکان <b style="color:var(--blue)">آبی</b> و <b style="color:var(--orange)">نارنجی</b> را بکشید. زیر تصویر، عقربه شباهت را بین −۱ (قرمز) و ۱ (سبز) نشان می‌دهد.',
        look: [
          'نوک نارنجی را از [۱، ۱] به [۲، ۲] و بعد [۳، ۳] ببرید → ضرب داخلی ۳، ۶، ۹ می‌شود، ولی شباهت همیشه حدود ۰٫۹۵ می‌ماند.',
          'نارنجی را روی [۴، ۲] بگذارید → شباهت دقیقاً ۱ می‌شود: هم‌جهتِ آبی است، فقط دو برابر بلندتر.',
          'نارنجی را روی [−۲، −۱] بگذارید → شباهت −۱: درست خلاف جهت.',
          'نارنجی را روی [−۱، ۲] بگذارید → شباهت ۰: عمود بر آبی.',
        ],
        see: 'شباهت کسینوسی طول را کنار می‌گذارد و فقط جهت را می‌سنجد؛ برای همین همیشه بین −۱ و ۱ است. این همان چیزی است که برای «سلیقه‌ی شبیه» لازم داشتیم. جست‌وجوی معنایی هم با همین عدد جمله‌های هم‌معنی را پیدا می‌کند.' },
      { t: 'rules', title: 'سه قانون مهم', items: [
        { r: `ضرب داخلیِ یک بردار در خودش = <b>طول × طول</b>: ${E(String.raw`a \cdot a = \|a\|^2`)}`,
          why: `${E(String.raw`[3, 4] \cdot [3, 4] = 9 + 16 = 25 = 5^2`)}. همان جمع مربع‌های فیثاغورس است، فقط بدون جذر.` },
        { r: 'دو پیکان <b>عمود</b> بر هم: ضرب داخلی <b>صفر</b>.',
          why: `هیچ تکه‌ای از یکی در امتداد دیگری نیست؛ سایه‌اش صفر است. مثل ${E(String.raw`[1, 2] \cdot [-2, 1] = -2 + 2 = 0`)}.` },
        { r: `ترتیب مهم نیست: ${E(String.raw`a \cdot b = b \cdot a`)}`,
          why: `چون هر خانه یک ضرب معمولی است و ${E(String.raw`3 \times 2 = 2 \times 3`)}. جمعِ ضرب‌ها هم همان می‌ماند.` },
      ] },
      { t: 'ai', title: 'ضرب داخلی در هوش مصنوعی',
        body: `<p>• <b>پیشنهاد فیلم و کالا</b> ${EN('Recommender System')}: بردار سلیقه‌ی شما ${E(String.raw`\cdot`)} بردار فیلم = حدسِ اینکه چقدر خوشتان می‌آید.</p>
               <p>• <b>جست‌وجو و چت‌بات‌ها</b>: هر جمله یک بردار معنی است ${EN('Embedding')}، یعنی فهرست عددهایی که معنی را نگه می‌دارد. با شباهت کسینوسی، جمله‌های هم‌معنی را پیدا می‌کنند.</p>
               <p>• <b>توجه</b> ${EN('Attention')} در <b>ترنسفورمرها</b> (نوع مدلی که ChatGPT با آن ساخته شده) با ضرب داخلی می‌سنجد هر کلمه به کدام کلمه‌ها مربوط است.</p>
               <p>• هر <b>نورون</b> (کوچک‌ترین واحد حساب در شبکه‌ی عصبی) حساب می‌کند: ${E(String.raw`w \cdot x + b`)} (وزن‌ها ضرب داخلی در ورودی‌ها، به‌علاوه‌ی یک عدد ثابت).</p>` },
      { t: 'quiz', q: `شباهت کسینوسی ${E('[1, 1]')} و ${E('[3, 3]')} چقدر است؟`,
        options: ['۱', '۰٫۳', '۶'], answer: 0,
        why: `ضرب داخلی: ${E('3 + 3 = 6')}. طول‌ها: ${E(String.raw`\sqrt{2}`)} و ${E(String.raw`\sqrt{18}`)}، و حاصل‌ضربشان ${E(String.raw`\sqrt{36} = 6`)}. پس ${E(String.raw`\frac{6}{6} = 1`)}: هم‌جهت. (۰٫۳ یعنی بر ${E('2 + 18 = 20')} تقسیم کرده‌ایم، نه بر حاصل‌ضرب طول‌ها. ۶ خودِ ضرب داخلی است، بدون تقسیم.)` },
      { t: 'text', title: 'پایان فصل بردارها',
        body: `<p>بردار، جمع، ضرب در عدد، طول، فاصله، و حالا «هم‌جهتی». همه‌ی ابزار فصل در دست شماست.</p>
               <div class="key">اگر بخواهیم یک بردار را با <b>صدها</b> بردار دیگر ضرب داخلی کنیم، چه؟</div>
               <p>بردارها را زیر هم می‌چینیم: <b>ماتریس</b> ${EN('Matrix')}. ضرب ماتریس یعنی صدها ضرب داخلی با هم. فصل بعد!</p>` },
    ] },
  ],
  sheet: {
    one: 'ضرب داخلی = خانه‌های هم‌شماره را در هم ضرب کن و جمع کن؛ جواب یک عدد است. ساخته شد تا بفهمیم دو بردار چقدر به یک سمت می‌روند.',
    f: String.raw`a \cdot b = a_1 b_1 + a_2 b_2 + \dots \qquad \cos(a, b) = \frac{a \cdot b}{\|a\| \, \|b\|}`,
    rules: ['مثبت: هم‌جهت، صفر: عمود، منفی: خلاف جهت.', `${E(String.raw`a \cdot a = \|a\|^2`)} (طول × طول).`, `${E(String.raw`a \cdot b = b \cdot a`)} (ترتیب مهم نیست).`, 'شباهت کسینوسی فقط جهت را می‌سنجد و بین −۱ و ۱ است.'],
    use: `پیشنهاد فیلم (سلیقه ${E(String.raw`\cdot`)} فیلم)، جست‌وجوی معنایی با شباهت کسینوسی روی بردار جمله‌ها (Embedding)، توجه (Attention) در ترنسفورمرها، و هر نورون: ${E(String.raw`w \cdot x + b`)}.`,
    mistake: 'جواب را بردار بنویسیم ([۳، ۸] به‌جای ۱۱): بعد از ضرب، باید جمع کرد. همچنین برای «شباهت سلیقه» فاصله یا ضرب داخلیِ خام کافی نیست؛ اندازه را با تقسیم بر طول‌ها حذف کنید.',
  },
});
