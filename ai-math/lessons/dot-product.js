// ---------- Vectors: Dot Product and Cosine Similarity ----------
// uses vecPlane / clampV from lessons/vectors.js
// a negative number inside a sum gets parentheses: 3 + (−2)
const DOT_p = n => (n < 0 ? `(${fa(n)})` : fa(n));
const DOT_SPAN = (c, t) => `<span style="color:var(--${c})">${t}</span>`;

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
    return E(`${DOT_SPAN('blue', V(s.ax, s.ay))} · ${DOT_SPAN('orange', V(s.bx, s.by))}`) + '<br>' +
      E(`= (${DOT_p(s.ax)} × ${DOT_p(s.bx)}) + (${DOT_p(s.ay)} × ${DOT_p(s.by)}) = ${DOT_p(p)} + ${DOT_p(q)} = <b>${fa(d)}</b>`) +
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
    // "=" only when both lengths are whole numbers and the answer needs no rounding
    const ia = Number.isInteger(la), ib = Number.isInteger(lb);
    const exact = ia && ib && Math.abs(c * 100 - Math.round(c * 100)) < 1e-9;
    const word = c > 0.9999 ? 'دقیقاً هم‌جهت' : c < -0.9999 ? 'دقیقاً خلاف جهت' : d > 0 ? 'کم‌وبیش هم‌جهت' : d < 0 ? 'کم‌وبیش خلاف جهت' : 'عمود: بی‌ربط';
    return `ضرب داخلی = ${fa(d)}، طول آبی ${ia ? '=' : '≈'} ${fa(la)}، طول نارنجی ${ib ? '=' : '≈'} ${fa(lb)}<br>` +
      `شباهت ${exact ? '=' : '≈'} ${E(`${fa(d)} ÷ (${fa(la)} × ${fa(lb)}) ${exact ? '=' : '≈'} <b>${fa(c)}</b>`)} : <b>${word}</b>` +
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
               <p class="read">${E('[2, 1] · [3, 4] = 2×3 + 1×4 = 6 + 4 = 10')}</p>
               <p>• <b style="color:var(--green)">مثبت</b>: کم‌وبیش هم‌جهت‌اند (موافق).<br>• <b>صفر</b>: عمود بر هم‌اند (بی‌ربط).<br>• <b style="color:var(--red)">منفی</b>: خلاف جهت‌اند (مخالف).</p>
               <p>نقطه‌ی وسط (·) یعنی «ضرب داخلی».</p>` },
      { t: 'play', w: DOT_W_DOT, title: 'دو پیکان، یک عدد',
        body: 'نوک پیکان <b style="color:var(--blue)">آبی</b> و <b style="color:var(--orange)">نارنجی</b> را بکشید. خط <b style="color:var(--green)">سبز</b> «سایه‌ی» نارنجی روی خط آبی است: چقدر از نارنجی در امتداد آبی می‌رود. ضرب داخلی = طول سایه × طول آبی (سایه‌ی پشت سر = منفی). رنگ گوشه‌ی بین دو پیکان: سبز = مثبت، خاکستری = صفر، قرمز = منفی. پیکان‌ها را عمود و رو در روی هم هم بگذارید.' },
      { t: 'life', title: 'ضرب داخلی در زندگی', items: [
        { h: 'فاکتور خرید', d: `مقدار ${E('[2, 1]')} (۲ کیلو سیب، ۱ کیلو پرتقال) · قیمت هر کیلو ${E('[30, 50]')} هزار تومان = ۶۰ + ۵۰ = <b>۱۱۰ هزار تومان</b>.` },
        { h: 'معدل', d: `نمره‌ها ${E('[18, 15]')} · واحدها ${E('[3, 2]')} = ۵۴ + ۳۰ = ۸۴. تقسیم بر ۵ واحد: معدل ۱۶٫۸.` },
        { h: 'سلیقه و فیلم', d: 'سلیقه‌ی شما · ویژگی‌های فیلم (هیجان، خنده، ترس). عدد بزرگ یعنی احتمالاً از فیلم خوشتان می‌آید.' },
        { h: 'باد و دوچرخه', d: 'باد از پشت: کمک می‌کند (مثبت). باد از پهلو: نه کمک، نه مانع (صفر). باد از روبه‌رو: مانع است (منفی). فقط آن تکه از باد که در امتداد جاده است مهم است.' },
      ] },
      { t: 'sort', title: 'حاصل این ضرب داخلی مثبت است؟', yes: 'مثبت است', no: 'مثبت نیست', items: [
        { q: E('[2, 1] · [3, 1]'), a: true, why: '۶ + ۱ = ۷. هر دو به راست و کمی بالا می‌روند.' },
        { q: E('[1, 0] · [0, 1]'), a: false, why: '۰ + ۰ = <b>صفر</b>. یکی به راست، یکی به بالا: عمود بر هم.' },
        { q: E('[2, 1] · [−2, −1]'), a: false, why: '−۴ + (−۱) = <b>−۵</b>، منفی. دومی همان اولی است، رو به عقب.' },
        { q: E('[3, −1] · [1, 2]'), a: true, why: '۳ + (−۲) = ۱. یک عدد منفی دارد، ولی جمعش هنوز مثبت است.' },
        { q: E('[1, 2] · [−2, 1]'), a: false, why: '−۲ + ۲ = <b>صفر</b>. این دو هم عمودند، با اینکه کج‌اند.' },
      ] },
      { t: 'quiz', q: E('[3, 2] · [1, 4] = ?'),
        options: ['۱۱', '۱۴', '۱۰'], answer: 0,
        why: '۳ × ۱ = ۳ و ۲ × ۴ = ۸. جمع: ۱۱. (۱۴ یعنی ضربدری ضرب کرده‌ایم: ۳ × ۴ + ۲ × ۱؛ باید خانه‌ی اول با اول باشد. ۱۰ جمعِ همه‌ی عددهاست، بدون ضرب.)' },
    ] },
    { name: 'فرمول', cards: [
      { t: 'formula', title: `فرمول ضرب داخلی ${EN('Dot Product')}`,
        intro: `<p>دو بردار ${E('a = [a₁, a₂]')} و ${E('b = [b₁, b₂]')}. عدد کوچکِ پایین می‌گوید خانه‌ی چندم.</p>`,
        toks: [{ s: 'a · b', c: 'green', l: 'ضرب داخلی (یک عدد)' }, { s: '=' }, { s: 'a₁b₁', c: 'blue', l: 'خانه‌ی اول × خانه‌ی اول' },
               { s: '+' }, { s: 'a₂b₂', c: 'orange', l: 'خانه‌ی دوم × خانه‌ی دوم' }, { s: '+ …', c: 'muted', l: 'اگر خانه‌ی بیشتری باشد' }],
        read: 'خوانده می‌شود: «a ضرب داخلی b برابر است با a یک در b یک، به‌علاوه‌ی a دو در b دو».',
        note: `<p>دو حرف کنار هم (مثل a₁b₁) یعنی در هم ضرب‌شان کن. تعداد خانه‌ها باید برابر باشد.</p>
               <p class="read">${E('[2, 3] · [4, 1] = 2×4 + 3×1 = 8 + 3 = 11')}</p>` },
      { t: 'formula', title: `شباهت کسینوسی ${EN('Cosine Similarity')}`,
        intro: '<p>‖a‖ یعنی طول a؛ همان جذرِ جمعِ مربع‌ها (درس قبل). رضا نصفِ علی است، ولی ضرب داخلی‌شان ۵۲ می‌شود؛ بزرگی را باید حذف کرد. پس بر هر دو طول تقسیم می‌کنیم:</p>',
        toks: [{ s: 'cos', c: 'green', l: 'شباهت' }, { s: '=' }, { s: 'a · b', c: 'orange', l: 'ضرب داخلی' },
               { s: '/' }, { s: '(‖a‖ ‖b‖)', c: 'blue', l: 'طول a × طول b' }],
        note: `<p>جواب بین <b>−۱</b> (خلاف جهت) و <b>۱</b> (هم‌جهت) است؛ ۰ یعنی عمود.</p>
               <p class="read">${E('[1, 2], [2, 4]: 10 / (√5 × √20) = 10 / 10 = 1')}</p>
               <p>علی و رضا هم ۱ می‌شوند، علی و سارا حدود ۰٫۸۸. حالا رضا شبیه‌ترین است.</p>` },
      { t: 'play', w: DOT_W_COS, title: 'فقط جهت مهم است',
        body: 'پیکان‌ها را بکشید و عقربه را ببینید. حالا نوک <b style="color:var(--orange)">نارنجی</b> را از [۱، ۱] به [۲، ۲] و [۳، ۳] ببرید: ضرب داخلی بزرگ می‌شود (۳، ۶، ۹)، ولی شباهت ثابت می‌ماند. چون جهت عوض نشده.' },
      { t: 'rules', title: 'سه قانون مهم', items: [
        { r: `ضرب داخلیِ یک بردار در خودش = <b>طول × طول</b>: ${E('a · a = ‖a‖²')}`,
          why: `${E('[3, 4] · [3, 4] = 9 + 16 = 25 = 5²')}. همان جمع مربع‌های فیثاغورس است، فقط بدون جذر.` },
        { r: 'دو پیکان <b>عمود</b> بر هم: ضرب داخلی <b>صفر</b>.',
          why: `هیچ تکه‌ای از یکی در امتداد دیگری نیست؛ سایه‌اش صفر است. مثل ${E('[1, 2] · [−2, 1] = −2 + 2 = 0')}.` },
        { r: `ترتیب مهم نیست: ${E('a · b = b · a')}`,
          why: `چون هر خانه یک ضرب معمولی است و ${E('3 × 2 = 2 × 3')}. جمعِ ضرب‌ها هم همان می‌ماند.` },
      ] },
      { t: 'ai', title: 'ضرب داخلی در هوش مصنوعی',
        body: `<p>• <b>پیشنهاد فیلم و کالا</b> ${EN('Recommender System')}: بردار سلیقه‌ی شما · بردار فیلم = حدسِ اینکه چقدر خوشتان می‌آید.</p>
               <p>• <b>جست‌وجو و چت‌بات‌ها</b>: هر جمله یک بردار معنی است ${EN('Embedding')}، یعنی فهرست عددهایی که معنی را نگه می‌دارد. با شباهت کسینوسی، جمله‌های هم‌معنی را پیدا می‌کنند.</p>
               <p>• <b>توجه</b> ${EN('Attention')} در <b>ترنسفورمرها</b> (نوع مدلی که ChatGPT با آن ساخته شده) با ضرب داخلی می‌سنجد هر کلمه به کدام کلمه‌ها مربوط است.</p>
               <p>• هر <b>نورون</b> (کوچک‌ترین واحد حساب در شبکه‌ی عصبی) حساب می‌کند: ${E('w · x + b')} (وزن‌ها · ورودی‌ها + یک عدد ثابت). شروع شبکه‌های عصبی.</p>` },
      { t: 'quiz', q: `شباهت کسینوسی ${E('[1, 1]')} و ${E('[3, 3]')} چقدر است؟`,
        options: ['۱', '۰٫۳', '۶'], answer: 0,
        why: 'ضرب داخلی: ۳ + ۳ = ۶. طول‌ها: √۲ و √۱۸، و حاصل‌ضربشان √۳۶ = ۶. پس ۶ ÷ ۶ = ۱: هم‌جهت. (۰٫۳ یعنی بر ۲ + ۱۸ = ۲۰ تقسیم کرده‌ایم، نه بر حاصل‌ضرب طول‌ها. ۶ خودِ ضرب داخلی است، بدون تقسیم.)' },
      { t: 'text', title: 'پایان فصل بردارها',
        body: `<p>بردار، جمع، ضرب در عدد، طول، فاصله، و حالا «هم‌جهتی». همه‌ی ابزار فصل در دست شماست.</p>
               <div class="key">اگر بخواهیم یک بردار را با <b>صدها</b> بردار دیگر ضرب داخلی کنیم، چه؟</div>
               <p>بردارها را زیر هم می‌چینیم: <b>ماتریس</b> ${EN('Matrix')}. ضرب ماتریس یعنی صدها ضرب داخلی با هم. فصل بعد!</p>` },
    ] },
  ],
  sheet: {
    one: 'ضرب داخلی = خانه‌های هم‌شماره را در هم ضرب کن و جمع کن؛ جواب یک عدد است. ساخته شد تا بفهمیم دو بردار چقدر به یک سمت می‌روند.',
    f: 'a · b = a₁b₁ + a₂b₂ + …   شباهت = a · b / (‖a‖ ‖b‖)',
    rules: ['مثبت: هم‌جهت، صفر: عمود، منفی: خلاف جهت.', 'a · a = ‖a‖² (طول × طول).', 'a · b = b · a (ترتیب مهم نیست).', 'شباهت کسینوسی فقط جهت را می‌سنجد و بین −۱ و ۱ است.'],
    use: 'پیشنهاد فیلم (سلیقه · فیلم)، جست‌وجوی معنایی با شباهت کسینوسی روی بردار جمله‌ها (Embedding)، توجه (Attention) در ترنسفورمرها، و هر نورون: w · x + b.',
    mistake: 'جواب را بردار بنویسیم ([۳، ۸] به‌جای ۱۱): بعد از ضرب، باید جمع کرد. همچنین برای «شباهت سلیقه» فاصله یا ضرب داخلیِ خام کافی نیست؛ اندازه را با تقسیم بر طول‌ها حذف کنید.',
  },
});
