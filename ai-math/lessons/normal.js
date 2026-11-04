// ---------- Statistics: Normal Distribution ----------
// (names start with NORM_ because all lesson files share one global scope)

const NORM_clamp = (v, a, b) => Math.max(a, Math.min(b, v));
// share of a normal distribution below z (Abramowitz & Stegun 7.1.26, error < 1e-6)
const NORM_cdf = z => {
  const x = Math.abs(z) / Math.SQRT2, t = 1 / (1 + 0.3275911 * x);
  const erf = 1 - t * (0.254829592 + t * (-0.284496736 + t * (1.421413741 + t * (-1.453152027 + t * 1.061405429)))) * Math.exp(-x * x);
  return z >= 0 ? (1 + erf) / 2 : (1 - erf) / 2;
};

// ---- Galton board: each pin = a coin toss (left or right); bin = number of right turns ----
const NORM_SPEED = 9;      // rows per second
const NORM_GAP = 0.025;    // seconds between balls when dropping many
const NORM_reset = s => { s.counts = Array(s.rows + 1).fill(0); s.balls = []; s.pending = 0; s.clock = 0; s.n = 0; };
const NORM_path = r => Array.from({ length: r }, () => (Math.random() < 0.5 ? -1 : 1));
const NORM_bin = p => p.filter(v => v > 0).length;
const NORM_pinY = (s, i) => 10 - 5 * i / s.rows;

const W_NORM_GALTON = h => {
  const st = { rows: 8 };
  NORM_reset(st);
  return plane(h, {
    x: [-7.2, 7.2], y: [-0.6, 10.8], ratio: 0.95,
    state: st,
    sliders: [{ key: 'rows', label: 'تعداد ردیف میخ:', min: 4, max: 12, step: 1 }],
    onSlide: s => NORM_reset(s),
    buttons: [
      { label: '۱ توپ', on: s => { s.balls.push({ p: NORM_path(s.rows), t: 0 }); } },
      { label: '۱۰۰ توپ', on: s => { s.pending += 100; } },
      { label: '۱۰۰۰ توپ، فوری', on: s => { for (let i = 0; i < 1000; i++) s.counts[NORM_bin(NORM_path(s.rows))]++; s.n += 1000; } },
      { label: 'از اول', on: s => NORM_reset(s) },
    ],
    tick: (s, dt) => {
      if (s.pending > 0) {
        s.clock += dt;
        while (s.clock >= NORM_GAP && s.pending > 0) { s.balls.push({ p: NORM_path(s.rows), t: 0 }); s.pending--; s.clock -= NORM_GAP; }
      } else s.clock = 0;
      s.balls.forEach(b => { b.t += dt * NORM_SPEED; });
      s.balls = s.balls.filter(b => {
        if (b.t < s.rows + 0.4) return true;
        s.counts[NORM_bin(b.p)]++; s.n++;
        return false;
      });
    },
    draw: (g, s) => {
      const R = s.rows, half = R / 2;
      // pins
      for (let i = 0; i < R; i++) for (let j = 0; j <= i; j++) g.dot(j - i / 2, NORM_pinY(s, i), 'muted', 2.5);
      // bins as a histogram
      const top = Math.max(4, ...s.counts), sc = 4.4 / top;
      s.counts.forEach((c, k) => {
        const x = k - half;
        g.line(x - 0.5, 0, x - 0.5, 4.6, 'soft', 1);
        if (c) { g.rect(x - 0.42, 0, x + 0.42, c * sc, 'blue', 0.75); g.line(x - 0.42, c * sc, x + 0.42, c * sc, 'blue', 2); }
      });
      g.line(half + 0.5, 0, half + 0.5, 4.6, 'soft', 1);
      g.line(-half - 0.7, 0, half + 0.7, 0, 'line', 2);
      // the bell that math predicts for this many balls
      if (s.n >= 20) g.fn(x => s.n * ST.normal(x, 0, Math.sqrt(R) / 2) * sc, 'orange', 2.5, -half - 0.6, half + 0.6);
      // falling balls
      const r = Math.max(2.5, Math.min(5, (g.X(1) - g.X(0)) * 0.22));
      s.balls.forEach(b => {
        const i = Math.min(Math.floor(b.t), R), f = Math.min(1, b.t - i);
        let x = 0;
        for (let k = 0; k < i; k++) x += b.p[k] / 2;
        if (i < R) x += f * b.p[i] / 2;
        g.dot(x, 10.35 - 5 * b.t / R, 'blue', r);
      });
    },
    read: s => {
      const R = s.rows, waiting = s.pending + s.balls.length;
      const head = `${fa(R)} ردیف میخ. در هر میخ، شانسِ چپ و راست برابر است (مثل سکه).<br>`;
      if (!s.n) return head + (waiting ? `${fa(waiting)} توپ در راه است...` : 'هنوز توپی نیفتاده. «۱ توپ» یا «۱۰۰ توپ» را بزنید.');
      const top = Math.max(...s.counts), k = s.counts.indexOf(top);
      return head + `<b>${fa(s.n)}</b> توپ رسیده‌اند${waiting ? ` (${fa(waiting)} توپ در راه)` : ''}.<br>` +
        `پرتوپ‌ترین خانه: <b>${fa(k)} بار راست، ${fa(R - k)} بار چپ</b>، با ${fa(top)} توپ.<br>` +
        `برای خانه‌ی آخرِ راست، توپ باید ${fa(R)} بار پشتِ سرِ هم راست برود: شانسش ۱ در ${fa(2 ** R)}.` +
        (s.n >= 20 ? '<br><span class="muted">منحنیِ <b style="color:var(--orange)">نارنجی</b> = زنگوله‌ای که ریاضی برای این تعداد توپ پیش‌بینی می‌کند.</span>' : '');
    },
  });
};

// ---- a bell curve with two knobs (μ, σ), a shaded ±kσ band and a draggable value x ----
const NORM_BAND = ['۶۸', '۹۵', '۹۹٫۷'];
const NORM_pct = z => {
  const p = 100 * NORM_cdf(z);
  return p > 99.5 ? 'بیش از ۹۹٫۵' : p < 0.5 ? 'کمتر از ۰٫۵' : fa(Math.round(p));
};

const W_NORM_BELL = h => plane(h, {
  x: [117, 223], y: [-0.03, 0.115], ratio: 0.75,
  state: { mu: 170, sd: 10, band: 1, x: 180 },
  sliders: [
    { key: 'mu', label: 'μ (مرکز):', min: 150, max: 190, step: 1 },
    { key: 'sd', label: 'σ (پهنا):', min: 4, max: 15, step: 1 },
  ],
  buttons: [1, 2, 3].map(k => ({ label: `±${fa(k)}σ`, on: s => { s.band = k; }, active: s => s.band === k })),
  handles: [{ get: s => [s.x, 0], set: (s, x) => { s.x = NORM_clamp(Math.round(x), 120, 220); }, color: 'red' }],
  draw: (g, s) => {
    const f = x => ST.normal(x, s.mu, s.sd), c = g.ctx;
    // shaded band μ ± kσ
    const a = Math.max(117, s.mu - s.band * s.sd), b = Math.min(223, s.mu + s.band * s.sd);
    c.beginPath(); c.moveTo(g.X(a), g.Y(0));
    for (let i = 0; i <= 120; i++) { const x = a + (b - a) * i / 120; c.lineTo(g.X(x), g.Y(f(x))); }
    c.lineTo(g.X(b), g.Y(0)); c.closePath();
    c.globalAlpha = 0.25; c.fillStyle = g.css('green'); c.fill(); c.globalAlpha = 1;
    g.text(s.mu, f(s.mu) * 0.3, `${NORM_BAND[s.band - 1]}٪`, 'green', 'center', 0);
    // axis with labels
    g.line(117, 0, 223, 0, 'line', 2);
    for (let t = 120; t <= 220; t += 10) { g.line(t, 0, t, -0.004, 'muted', 1); g.text(t, 0, fa(t), 'muted', 'center', 14); }
    // the curve and its center
    g.line(s.mu, 0, s.mu, f(s.mu), 'ink', 1.5, [5, 5]);
    g.fn(f, 'orange', 3);
    // the chosen value x
    g.line(s.x, 0, s.x, f(s.x), 'red', 2);
    g.text(s.x, f(s.x), `z = ${fa((s.x - s.mu) / s.sd)}`, 'red', 'center', -14);
  },
  read: s => {
    const k = s.band, z = (s.x - s.mu) / s.sd;
    const where = Math.abs(z) < 1e-9 ? 'درست روی میانگین'
      : `${fa(Math.abs(z))} برابرِ ${E(String.raw`\sigma`)} ${z > 0 ? 'بالاتر' : 'پایین‌تر'} از میانگین`;
    return `نوار سبز: بینِ <b>${fa(s.mu - k * s.sd)}</b> و <b>${fa(s.mu + k * s.sd)}</b> (یعنی ${E(String.raw`\mu \pm ${k}\sigma`)}): حدود <b style="color:var(--green)">${NORM_BAND[k - 1]}٪</b> داده‌ها.<br>` +
      `خط <b style="color:var(--red)">قرمز</b>: ${E(String.raw`z = \frac{${s.x} - ${s.mu}}{${s.sd}} = ${Math.round(z * 100) / 100}`)}<br>` +
      `یعنی ${fa(s.x)}، ${where}. حدود <b>${NORM_pct(z)}٪</b> داده‌ها کمتر از ${fa(s.x)} هستند.`;
  },
});

lesson({
  id: 'normal', node: 'normal-distribution', title: 'توزیع نرمال', en: 'Normal Distribution',
  parts: [
    { name: 'چرا و یعنی چه؟', cards: [
      { t: 'story', title: `توزیع نرمال ${EN('Normal Distribution')}`,
        body: `<p>قدِ مردانِ بزرگسال، خطای کوچکِ اندازه‌گیری، نمره‌ی امتحانِ یک کلاسِ خیلی بزرگ، وزنِ نان‌های یک نانوایی. این‌ها هیچ ربطی به هم ندارند.</p>
               <p>ولی هیستوگرامِ همه‌شان <b>یک شکل</b> دارد: یک زنگوله. یک قله در وسط، دو طرفِ قرینه، و دو دُمِ کوتاه.</p>
               <div class="key">مشکل: چرا چیزهای این‌قدر مختلف، <b>یک شکل</b> درمی‌آیند؟ و آیا می‌شود این شکل را با چند عدد دقیق گفت؟</div>`,
        who: 'دُموآور (de Moivre) حدود ۱۷۳۰ این شکل را در حسابِ سکه انداختن پیدا کرد. گاوس (Gauss) اوایلِ دهه‌ی ۱۸۰۰ با آن خطای اندازه‌گیریِ ستاره‌ها را بررسی کرد؛ برای همین به آن «توزیع گاوسی» هم می‌گویند.' },
      { t: 'text', title: 'معنی ساده',
        body: `<div class="key">وقتی یک نتیجه، <b>جمعِ خیلی هُلِ کوچک و تصادفی</b> باشد، شکلش زنگوله می‌شود: بیشترِ مقدارها نزدیکِ وسط، هر چه دورتر کمتر، و دو طرف قرینه.</div>
               <p>قد را خیلی چیزِ کوچک بالا یا پایین هُل می‌دهد: ژن‌ها، غذا، خواب... این هُل‌ها <b>مستقل</b>‌اند؛ هر کدام کارِ خودش را می‌کند.</p>
               <p>بیشترشان همدیگر را خنثی می‌کنند. قدِ خیلی بلند یعنی تقریباً <b>همه</b>ی هُل‌ها رو به بالا بوده‌اند؛ این کمیاب است.</p>
               <p class="muted">«نرمال» فقط اسم است، نه به معنیِ «عادی». به آن منحنیِ زنگوله‌ای ${EN('Bell Curve')} هم می‌گویند.</p>` },
      { t: 'play', w: W_NORM_GALTON, title: 'تخته‌ی گالتون',
        body: 'گالتون (Galton) این تخته را در دهه‌ی ۱۸۷۰ ساخت (Galton Board). نقطه‌های خاکستری = میخ‌ها؛ توپ به هر میخ که بخورد، تصادفی به <b>چپ</b> یا <b>راست</b> می‌رود. میله‌های <b style="color:var(--blue)">آبی</b> = چند توپ در هر خانه افتاده. منحنیِ <b style="color:var(--orange)">نارنجی</b> = زنگوله‌ای که ریاضی پیش‌بینی می‌کند.',
        look: [
          '«۱ توپ» را بزنید ← توپ در ۸ ردیف، ۸ بار چپ یا راست می‌رود و در یکی از ۹ خانه می‌افتد.',
          '«۱۰۰ توپ» را بزنید ← خانه‌های وسط زود پر می‌شوند و لبه‌ها تقریباً خالی می‌مانند.',
          '«۱۰۰۰ توپ، فوری» را بزنید ← خانه‌ی وسط (۴ راست، ۴ چپ) حدود ۲۷۰ توپ می‌گیرد، هر لبه فقط حدود ۴ توپ (شانس ۱ در ۲۵۶). منحنیِ نارنجی روی میله‌ها می‌نشیند.',
          'لغزنده را روی ۴ ببرید و باز «۱۰۰۰ توپ، فوری» ← ۱۶ مسیر هست: ۶ تا به وسط می‌رسد (حدود ۳۷۵ توپ)، ۱ تا به هر لبه (حدود ۶۲ توپ).',
        ],
        see: 'هر توپ جمعِ چند هُلِ تصادفیِ چپ و راست است. به خانه‌ی وسط راه‌های زیادی می‌رسد و به لبه فقط یک راه؛ برای همین زنگوله ساخته می‌شود. قد، خطای اندازه‌گیری و نویزِ داده‌ها هم به همین دلیل زنگوله‌ای‌اند.' },
      { t: 'life', title: 'زنگوله در زندگی', items: [
        { h: 'قدِ بزرگسالان', d: 'قدِ زنان یک زنگوله است، قدِ مردان هم. قاطی‌شان کنید، دیگر یک زنگوله‌ی تمیز نیست.' },
        { h: 'خطای اندازه‌گیری', d: 'یک کیسه برنج را ده بار وزن کنید. عددها کمی بالا و پایین‌اند؛ بیشترشان نزدیکِ وزنِ واقعی.' },
        { h: 'وزنِ بسته‌ی غذا', d: 'روی بسته نوشته «۵۰۰ گرم». دستگاه ۴۹۸، ۵۰۳، ۵۰۱ گرم می‌ریزد. هزاران بسته، یک زنگوله دورِ ۵۰۰.' },
        { h: 'آزمونِ هوش (IQ)', d: 'عمداً طوری ساخته می‌شود که نمره‌ها زنگوله‌ای باشند، با میانگینِ ۱۰۰.' },
      ] },
      { t: 'sort', title: 'احتمالاً زنگوله‌ای است؟', yes: 'زنگوله‌ای', no: 'زنگوله‌ای نیست', items: [
        { q: 'قدِ مردانِ بزرگسالِ یک کشور', a: true, why: 'جمعِ خیلی اثرِ کوچک و مستقل است (ژن‌ها، غذا، خواب...).' },
        { q: 'درآمدِ مردمِ یک کشور', a: false, why: 'چوله (Skewed) است، یعنی یک دُمش بلندتر است: درآمد از صفر کمتر نمی‌شود، ولی چند نفرِ خیلی پولدار دُمِ بلندی به راست می‌سازند.' },
        { q: 'عددِ یک تاس', a: false, why: 'هر عدد از ۱ تا ۶ شانسِ برابر دارد. شکلش تخت است، قله‌ای ندارد.' },
        { q: 'جمعِ ۱۰ تاس با هم', a: true, why: 'جمعِ ده چیزِ تصادفی و مستقل است. جمعِ ۳۵ (وسط) راه‌های زیادی دارد؛ ۱۰ یا ۶۰ فقط یک راه.' },
        { q: 'زمانِ انتظار در صفِ بانک', a: false, why: 'از صفر کمتر نمی‌شود ولی گاهی خیلی طول می‌کشد: دُمِ بلند به راست، یعنی چوله.' },
      ] },
      { t: 'quiz', q: 'در تخته‌ی گالتون، چرا خانه‌های وسط از همه پرتوپ‌ترند؟',
        options: ['راه‌های بیشتری به خانه‌ی وسط می‌رسد', 'میخ‌های وسط توپ را کمی به خودشان می‌کشند', 'خانه‌ی وسط از بقیه‌ی خانه‌ها بزرگ‌تر است'], answer: 0,
        why: 'هر میخ مثل سکه است: نصف چپ، نصف راست؛ هیچ میخی توپ را به خودش نمی‌کشد. همه‌ی خانه‌ها هم یک اندازه‌اند. فرق در تعدادِ راه‌هاست: با ۴ ردیف، ۱۶ مسیر هست؛ ۶ تا به وسط می‌رسد (۲ راست و ۲ چپ، به هر ترتیبی)، فقط ۱ تا به لبه‌ی راست (۴ بار راست).' },
    ] },
    { name: 'فرمول', cards: [
      { t: 'text', title: `دو پیچ و قاعده‌ی ۶۸–۹۵–۹۹٫۷ ${EN('68–95–99.7 Rule')}`,
        body: `<p>هر زنگوله را دو عدد می‌سازد: ${E(String.raw`\mu`)} («میو» ${EN('Mu')}) = میانگین، یعنی زنگوله <b>کجاست</b>. ${E(String.raw`\sigma`)} («سیگما»ی کوچک) = انحراف معیار، یعنی <b>چقدر پهن</b> است. (${E(String.raw`\Sigma`)} بزرگ یعنی «جمع کن»؛ چیزِ دیگری است.)</p>
               <p><b>درصد = سهم از مساحتِ زیرِ زنگوله.</b> کلِ مساحت = ۱۰۰٪ داده‌ها.</p>
               <div class="key">حدود <b>۶۸٪</b> مساحت تا ${E(String.raw`1\sigma`)} از ${E(String.raw`\mu`)} است، <b>۹۵٪</b> تا ${E(String.raw`2\sigma`)}، <b>۹۹٫۷٪</b> تا ${E(String.raw`3\sigma`)}.</div>
               <p>قد با ${E(String.raw`\mu = 170`)} و ${E(String.raw`\sigma = 10`)} سانتی‌متر: ۶۸٪ بینِ ۱۶۰ و ۱۸۰، ۹۵٪ بینِ ۱۵۰ و ۱۹۰، ۹۹٫۷٪ بینِ ۱۴۰ و ۲۰۰.</p>` },
      { t: 'formula', f: String.raw`\Cg{f(x)} = \Ci{\frac{1}{\sigma\sqrt{2\pi}}} \, \Cb{e^{-\frac{(x - \mu)^2}{2\sigma^2}}}`, title: 'فرمولِ زنگوله (برای کنجکاوها: لازم نیست حفظ کنید)',
        intro: `<p>${E(String.raw`\pi \approx 3.14`)} همان عددِ دایره است. ${E(String.raw`e \approx 2.72`)} یک عددِ ثابت است؛ هر چه توانش منفی‌تر شود، به صفر نزدیک‌تر می‌شود.</p>`,
        toks: [{ s: 'f(x)', c: 'green', l: 'ارتفاع' }, { s: '=' }, { s: String.raw`\frac{1}{\sigma\sqrt{2\pi}}`, c: 'ink', l: 'مساحت را ۱ می‌کند' }, { s: String.raw`\cdot` },
               { s: String.raw`e^{-\frac{(x - \mu)^2}{2\sigma^2}}`, c: 'blue', l: 'هر چه دورتر از مرکز، کوچک‌تر' }],
        note: `<p>در توان: بالا ${E(String.raw`(x - \mu)^2`)} = فاصله تا مرکز به توان ۲؛ پایین ${E(String.raw`2\sigma^2`)} = پهنا. هر چه ${E('x')} از ${E(String.raw`\mu`)} دورتر، توان منفی‌تر؛ پس زنگوله در دو طرف زود به صفر می‌رسد: در ${E(String.raw`1\sigma`)} ارتفاع حدود ۶۱٪ قله است (${E(String.raw`e^{-0.5} \approx 0.61`)})، در ${E(String.raw`3\sigma`)} حدود ۱٪.</p>` },
      { t: 'formula', f: String.raw`\Cg{z} = \frac{\Cb{x} - \Co{\mu}}{\Co{\sigma}}`, title: `مقدار z ${EN('z-score')}`,
        intro: `<p>«۱۸۰ سانتی‌متر» به‌تنهایی نمی‌گوید بلند است یا نه. باید بدانیم چند ${E(String.raw`\sigma`)} از میانگین دور است:</p>`,
        toks: [{ s: 'z', c: 'green', l: `چند ${E(String.raw`\sigma`)} دور از میانگین` }, { s: '=' }, { s: '(' }, { s: 'x', c: 'blue', l: 'یک داده' }, { s: '-' },
               { s: String.raw`\mu`, c: 'orange', l: 'میانگین' }, { s: ')' }, { s: String.raw`\div` }, { s: String.raw`\sigma`, c: 'orange', l: 'انحراف معیار' }],
        note: `<p>به شکلِ کسری: ${E(String.raw`z = \frac{x - \mu}{\sigma}`)}. ${E('z')} مثبت یعنی بالاتر از میانگین، منفی یعنی پایین‌تر.</p>` },
      { t: 'example', title: 'علی چقدر بلند است؟',
        intro: `<p>قدِ علی ۱۸۰ سانتی‌متر است. در گروهِ او ${E(String.raw`\mu = 170`)} و ${E(String.raw`\sigma = 10`)}.</p>`,
        steps: [
          `فاصله تا میانگین: ${E('180 - 170 = 10')}`,
          `تقسیم بر ${E(String.raw`\sigma`)}: ${E(String.raw`z = \frac{10}{10} = 1`)}؛ یعنی یک ${E(String.raw`\sigma`)} بالاتر از میانگین.`,
          'زنگوله قرینه است، پس ۵۰٪ گروه زیرِ ۱۷۰ هستند.',
          `نصفِ ۶۸٪ بینِ ۱۷۰ و ۱۸۰ است: ${E(String.raw`\frac{68}{2} = 34`)} درصد.`,
          `جمع: ${E('50 + 34 = 84')} درصد.`,
        ],
        result: 'علی از حدودِ <b>۸۴٪</b> گروه بلندتر است. «۱۸۰» به‌تنهایی این را نمی‌گفت؛ z گفت.' },
      { t: 'play', w: W_NORM_BELL, title: 'زنگوله با دو پیچ',
        body: `منحنیِ <b style="color:var(--orange)">نارنجی</b> = زنگوله؛ دو لغزنده ${E(String.raw`\mu`)} (مرکز) و ${E(String.raw`\sigma`)} (پهنا) را عوض می‌کنند. نوارِ <b style="color:var(--green)">سبز</b> = داده‌هایی که تا ۱، ۲ یا ۳ برابرِ ${E(String.raw`\sigma`)} از مرکز دورند. دایره‌ی <b style="color:var(--red)">قرمز</b> روی محور = یک داده که می‌شود کشیدش.`,
        look: [
          `اول ${E(String.raw`\mu = 170`)}، ${E(String.raw`\sigma = 10`)} ← نوار سبز از ۱۶۰ تا ۱۸۰ است: ۶۸٪ داده‌ها. خط قرمز روی ۱۸۰: ${E('z = 1')} و حدود ۸۴٪ کمتر از آن‌اند.`,
          `دکمه‌ی ${E(String.raw`\pm 2\sigma`)} را بزنید ← نوار از ۱۵۰ تا ۱۹۰ پهن می‌شود: ۹۵٪.`,
          `دایره‌ی قرمز را روی ۱۵۰ بکشید ← ${E('z = -2')} و فقط حدود ۲٪ داده‌ها کمتر از ۱۵۰ هستند.`,
          `دایره را به ۱۸۰ برگردانید و ${E(String.raw`\sigma`)} را روی ۵ بگذارید ← زنگوله باریک و بلند می‌شود؛ همان ۱۸۰ حالا ${E('z = 2')} است و حدود ۹۸٪ کمتر از آن‌اند.`,
        ],
        see: `مساحتِ زیرِ زنگوله همیشه ۱ است؛ پس زنگوله‌ی پهن‌تر کوتاه‌تر است. ${E('z')} هر عدد را به زبانِ «چند ${E(String.raw`\sigma`)} دور از میانگین» برمی‌گرداند و با آن می‌شود گفت چند درصد کمتر یا بیشترند. یک قدِ ۱۸۰ در یک گروه معمولی است و در گروهِ دیگر بلند.` },
      { t: 'rules', title: 'سه قانون مهم', items: [
        { r: 'مساحتِ کلِ زیرِ زنگوله <b>۱</b> است (۱۰۰٪).',
          why: 'هر داده یک جایی زیرِ زنگوله است. پس زنگوله‌ی پهن‌تر باید کوتاه‌تر باشد.' },
        { r: `قرینه است، پس <b>میانگین = میانه = نما</b>. نما ${EN('Mode')}: پرتکرارترین مقدار.`,
          why: 'دو طرف آینه‌ی هم‌اند، پس تعادل و نفرِ وسط در وسط‌اند؛ قله هم وسط است.' },
        { r: `جمع یا میانگینِ خیلی چیزِ تصادفی و مستقل، زنگوله‌ای می‌شود، حتی اگر خودشان نباشند: <b>قضیه‌ی حد مرکزی</b> ${EN('Central Limit Theorem')}.`,
          why: 'هر میخِ گالتون فقط چپ یا راست است؛ جمعِ ۱۲ میخ زنگوله شد. یک تاس تخت است؛ جمعِ ۱۰ تاس زنگوله.' },
      ] },
      { t: 'ai', title: 'زنگوله و z در هوش مصنوعی',
        body: `<p><b>استانداردسازی</b> ${EN('Standardization')}: سن ۲۰ تا ۸۰ است، درآمد ۵ تا ۵۰۰ میلیون. مدل درآمد را فقط چون عددش بزرگ‌تر است مهم‌تر می‌بیند. پس هر ستون را به ${E('z')} تبدیل می‌کنیم.</p>
               <p><b>شبکه‌ی عصبی</b> ${EN('Neural Network')}: وزن‌ها اول عددهای کوچکِ تصادفی از یک زنگوله با میانگینِ ۰ هستند.</p>
               <p><b>تشخیصِ ناهنجاری</b> ${EN('Anomaly Detection')}: فقط حدودِ ۳ داده از ۱۰۰۰ بیش از ${E(String.raw`3\sigma`)} دورند؛ خریدی با ${E('z > 3')} یا ${E('z < -3')} مشکوک است.</p>
               <p>خیلی از آزمون‌های آماری (و درسِ بعد) فرض می‌کنند خطاهای کوچکِ تصادفی، یعنی <b>نویز</b> ${EN('Noise')}، زنگوله‌ای‌اند.</p>` },
      { t: 'quiz', q: `میانگینِ یک امتحانِ بزرگ ۱۴ و انحراف معیار ۲ است. کسی که ۱۸ گرفته، ${E('z')} چند است؟`,
        options: ['۲', '۴', '۹', '۰٫۵'], answer: 0,
        why: `${E(String.raw`\frac{18 - 14}{2} = 2`)}؛ یعنی ${E(String.raw`2\sigma`)} بالاتر از میانگین، بالاتر از حدودِ ۹۷٫۵٪ کلاس (۵۰٪ + نصفِ ۹۵٪). ۴ فقط فاصله است؛ تقسیم بر ${E(String.raw`\sigma`)} جا افتاده. ۹ یعنی ${E(String.raw`\frac{18}{2}`)}؛ میانگین کم نشده. ۰٫۵ یعنی ${E(String.raw`\frac{2}{4}`)}؛ تقسیم برعکس شده.` },
      { t: 'text', title: 'یک سؤال برای درس بعد',
        body: `<p>سه نوع کود را امتحان می‌کنیم؛ هر کود روی ۲۰ گلدان. میانگینِ قدِ گیاه‌ها: ۳۰، ۳۲ و ۳۵ سانتی‌متر. قدِ هر گروه هم یک زنگوله است.</p>
               <div class="key">کودها واقعاً فرق دارند، یا این فرق فقط از شانس است؟</div>
               <p>اگر هر زنگوله باریک باشد، سه زنگوله از هم جدا می‌افتند و فرق واقعی است. اگر پهن باشند، روی هم می‌افتند و شاید شانس باشد. باید <b>پخشِ بینِ گروه‌ها</b> را با <b>پخشِ درونِ هر گروه</b> مقایسه کرد: ${EN('ANOVA')}. درس بعد!</p>` },
    ] },
  ],
  sheet: {
    one: 'توزیع نرمال = زنگوله‌ای که از جمعِ خیلی هُلِ کوچک و تصادفیِ مستقل درمی‌آید: بیشتر نزدیکِ وسط، کمتر در دو طرف، قرینه. ساخته شد چون چیزهای خیلی مختلف (قد، خطای اندازه‌گیری، وزنِ بسته‌ها) همین شکل را دارند.',
    f: String.raw`z = \frac{x - \mu}{\sigma}`,
    rules: [`دو پیچ: ${E(String.raw`\mu`)} (مرکز) و ${E(String.raw`\sigma`)} (پهنا).`, `درصد = سهم از مساحتِ زیرِ زنگوله. قاعده‌ی ۶۸–۹۵–۹۹٫۷: تا ${E(String.raw`1\sigma`)} حدود ۶۸٪، تا ${E(String.raw`2\sigma`)} حدود ۹۵٪، تا ${E(String.raw`3\sigma`)} حدود ۹۹٫۷٪.`, 'مساحتِ کل = ۱؛ پس زنگوله‌ی پهن‌تر، کوتاه‌تر است.', 'قرینه است: میانگین = میانه = نما (پرتکرارترین مقدار).', 'قضیه‌ی حد مرکزی (Central Limit Theorem): جمع یا میانگینِ خیلی چیزِ تصادفی و مستقل، زنگوله‌ای می‌شود.'],
    use: `استانداردسازی (Standardization) ستون‌ها با ${E('z')}. وزن‌های اولیه‌ی شبکه‌ی عصبی از زنگوله. تشخیص ناهنجاری (Anomaly Detection): ${E('z > 3')} یا ${E('z < -3')} مشکوک است. خیلی از آزمون‌های آماری (مثل ANOVA) نویزِ زنگوله‌ای فرض می‌کنند.`,
    mistake: `فکر کنیم همه‌چیز زنگوله‌ای است؛ درآمد، قیمت خانه و زمان انتظار چوله‌اند. یا در ${E('z')}، تقسیم بر ${E(String.raw`\sigma`)} را فراموش کنیم.`,
  },
});
