// ---------- Interview mission: What does PCA do? ----------
// (names start with MPCA_ because all lesson files share one global scope)

const MPCA_rad = d => d * Math.PI / 180;
const MPCA_mean = a => a.reduce((p, q) => p + q, 0) / a.length;

// ---- the cloud: 40 fixed points, centred at (0, 0), covariance (divide by n) exactly
// C = [[3.25, 1.299], [1.299, 1.75]] = eigenvalue 4 along 30° and eigenvalue 1 along 120°.
// a and b come from a fixed seed, are centred, made uncorrelated and scaled to σ = 1;
// point = 2·a·u1 + b·u2 with u1 = [cos 30°, sin 30°], u2 = [−sin 30°, cos 30°].
// Checked in node: shadow variance 0° → 3.25, 30° → 4 (max), 90° → 1.75, 120° → 1 (min).
// With x doubled (unit change): C = [[13, 2.6], [2.6, 1.75]], λ = 13.57 and 1.18, PC1 at 12.4°, 92%.
const MPCA_PTS = (() => {
  let t = 77;
  const u = () => { t = (t * 1103515245 + 12345) % 2147483648; return (t + 0.5) / 2147483648; };
  const n = () => Math.sqrt(-2 * Math.log(u())) * Math.cos(2 * Math.PI * u());
  const centre = a => { const m = MPCA_mean(a); return a.map(v => v - m); };
  const unit = a => { const s = Math.sqrt(MPCA_mean(a.map(v => v * v))); return a.map(v => v / s); };
  const a = unit(centre(Array.from({ length: 40 }, n)));
  let b = centre(Array.from({ length: 40 }, n));
  const k = MPCA_mean(b.map((v, i) => v * a[i]));
  b = unit(b.map((v, i) => v - k * a[i]));
  const c = Math.cos(Math.PI / 6), s = 0.5;
  return a.map((v, i) => [2 * v * c - b[i] * s, 2 * v * s + b[i] * c]);
})();
const MPCA_pts = big => (big ? MPCA_PTS.map(([x, y]) => [2 * x, y]) : MPCA_PTS);
// shadow length of p on the line through (0, 0) at angle deg, and the variance of all shadows
const MPCA_proj = (p, deg) => p[0] * Math.cos(MPCA_rad(deg)) + p[1] * Math.sin(MPCA_rad(deg));
const MPCA_spread = (pts, deg) => { const sh = pts.map(p => MPCA_proj(p, deg)), m = MPCA_mean(sh); return MPCA_mean(sh.map(v => (v - m) ** 2)); };
// covariance matrix of a centred 2D cloud, its eigenvalues and the angle of PC1
const MPCA_eig = pts => {
  const a = MPCA_mean(pts.map(p => p[0] * p[0])), b = MPCA_mean(pts.map(p => p[0] * p[1])), d = MPCA_mean(pts.map(p => p[1] * p[1]));
  const r = Math.sqrt(((a - d) / 2) ** 2 + b * b);
  return { a, b, d, l1: (a + d) / 2 + r, l2: (a + d) / 2 - r, deg: Math.atan2(2 * b, a - d) / 2 * 180 / Math.PI };
};

// ---- Picture: turn a line through the centre; every point drops a shadow on it; read the shadow variance.
// withScale = true adds a button that doubles the x column (a unit change) to show why scaling matters.
const MPCA_W = withScale => h => plane(h, {
  x: withScale ? [-8.5, 8.5] : [-5, 5], y: withScale ? [-4.5, 4.5] : [-4, 4], equal: true,
  state: { deg: 0, big: false, show: false, best: 0, bestV: MPCA_spread(MPCA_PTS, 0) },
  sliders: [{ key: 'deg', label: 'زاویه‌ی خط:', min: 0, max: 175, step: 5 }],
  onSlide: s => { const v = MPCA_spread(MPCA_pts(s.big), s.deg); if (v > s.bestV + 1e-9) { s.bestV = v; s.best = s.deg; } },
  buttons: [
    { label: 'PC1 و PC2 را نشان بده', on: s => { s.show = !s.show; }, active: s => s.show },
    ...(withScale ? [{ label: 'ستونِ x را ۲ برابر کن (واحدِ دیگر)', active: s => s.big,
      on: s => { s.big = !s.big; s.bestV = MPCA_spread(MPCA_pts(s.big), s.deg); s.best = s.deg; } }] : []),
  ],
  draw: (g, s) => {
    g.grid();
    const pts = MPCA_pts(s.big), c = Math.cos(MPCA_rad(s.deg)), sn = Math.sin(MPCA_rad(s.deg));
    g.line(-12 * c, -12 * sn, 12 * c, 12 * sn, 'orange', 3);
    pts.forEach(p => { const t = MPCA_proj(p, s.deg); g.line(p[0], p[1], t * c, t * sn, 'muted', 1, [3, 4]); });
    pts.forEach(([x, y]) => g.dot(x, y, 'blue', 4));
    pts.forEach(p => { const t = MPCA_proj(p, s.deg); g.dot(t * c, t * sn, 'green', 3.5); });
    if (s.show) {
      const e = MPCA_eig(pts), r1 = MPCA_rad(e.deg), L1 = 1.3 * Math.sqrt(e.l1), L2 = 1.3 * Math.sqrt(e.l2);
      g.arrow(0, 0, L1 * Math.cos(r1), L1 * Math.sin(r1), 'green', 6); g.text(L1 * Math.cos(r1), L1 * Math.sin(r1), 'PC1', 'green', 'left', -10);
      g.arrow(0, 0, -L2 * Math.sin(r1), L2 * Math.cos(r1), 'red', 5); g.text(-L2 * Math.sin(r1), L2 * Math.cos(r1), 'PC2', 'red', 'right', -10);
    }
    g.dot(0, 0, 'red', 6);
  },
  read: s => {
    const pts = MPCA_pts(s.big), v = MPCA_spread(pts, s.deg), e = MPCA_eig(pts);
    const bar = `<div style="height:8px;border-radius:4px;background:var(--soft);margin:4px 0"><div style="height:8px;border-radius:4px;background:var(--green);width:${Math.round(v / e.l1 * 100)}%"></div></div>`;
    const head = `واریانسِ سایه‌ها: <b style="color:var(--green)">${fa(v)}</b> &nbsp;|&nbsp; بیشترین تا حالا: <b>${fa(s.bestV)}</b> در ${fa(s.best)}°${bar}`;
    if (s.big) return head + `حالا PC1 در حدودِ <b>${fa(Math.round(e.deg))}°</b> است، نه ۳۰°، و <b>${fa(Math.round(e.l1 / (e.l1 + e.l2) * 100))}٪</b> پخش را دارد. داده همان است؛ فقط واحدِ x عوض شد و ستونِ x «مهم‌تر» به نظر آمد.`;
    if (s.deg === 30) return head + `<b style="color:var(--green)">بیشترین واریانس: ${E(String.raw`\lambda_1 = 4`)}.</b> این جهت PC1 است و ۴ از ۵، یعنی ۸۰٪ پخش را دارد.`;
    if (s.deg === 120) return head + `<b style="color:var(--red)">کمترین واریانس: ${E(String.raw`\lambda_2 = 1`)}.</b> این جهت PC2 است، عمود بر PC1.`;
    if (s.deg === 0) return head + 'خط روی محورِ x است؛ این همان واریانسِ ستونِ x است (خانه‌ی بالا-چپِ ماتریس کوواریانس).';
    if (s.deg === 90) return head + 'خط روی محورِ y است؛ این همان واریانسِ ستونِ y است (خانه‌ی پایین-راست).';
    return head + 'خط را بچرخانید تا سایه‌های سبز بیشترین پخش را داشته باشند.';
  },
});
const MPCA_W_TURN = MPCA_W(false);
const MPCA_W_SCALE = MPCA_W(true);

lesson({
  id: 'm-pca', node: 'what-does-pca-do', title: 'PCA دقیقاً چه می‌کند؟', en: 'What does PCA do?',
  parts: [
    { name: 'سؤال و نردبان', cards: [
      { t: 'text', title: 'سؤالِ مصاحبه',
        body: `<p>مصاحبه‌گر می‌پرسد:</p>
               <div class="key" dir="ltr" style="text-align:left">"Explain PCA. What are the principal components mathematically?"</div>
               <p>یعنی: «PCA را توضیح دهید. مؤلفه‌های اصلی، از نظرِ ریاضی، دقیقاً چه هستند؟»</p>
               <p>اگر الان جوابش را بلد نیستید، اشکالی ندارد. همه‌ی تکه‌هایش را در درس‌های قبل دیده‌اید. قدم به قدم کنارِ هم می‌گذاریم.</p>` },
      { t: 'ladder' },
      { t: 'text', title: 'پله‌ی ۱: اول مرکز کن، بعد هم‌اندازه',
        body: `<p>از درسِ <b>پراکندگی</b>: واریانس = میانگینِ مربعِ فاصله از میانگین. PCA پخش را دورِ نقطه‌ی (۰، ۰) می‌سنجد.</p>
               <p><b>مرکز کردن</b> ${EN('Centering')}: از هر ستون میانگینش را کم کن؛ وسطِ ابر می‌رود روی (۰، ۰).</p>
               <p><b>هم‌اندازه کردن</b> ${EN('Standardizing')}: هر ستون را بر انحراف معیارش (${E(String.raw`\sigma`)}) تقسیم کن؛ وقتی واحدها فرق دارند (تومان و سال)، لازم است.</p>
               <div class="key">بدونِ این دو قدم، PCA به‌جای «جهتِ پخش»، جای ابر یا بزرگ‌ترین واحد را پیدا می‌کند.</div>` },
      { t: 'play', w: MPCA_W_TURN, title: 'پله‌ی ۲: جهتِ بیشترین واریانس',
        body: '۴۰ نقطه‌ی <b style="color:var(--blue)">آبی</b>، مرکزشده. هر نقطه سایه‌ای <b style="color:var(--green)">سبز</b> روی خطِ <b style="color:var(--orange)">نارنجی</b> می‌اندازد (Projection). نوارِ سبزِ زیرِ تصویر واریانسِ این سایه‌هاست.',
        look: [
          'زاویه ۰° (خط روی محورِ x) ← واریانسِ سایه‌ها ۳٫۲۵؛ همان واریانسِ ستونِ x.',
          'خط را تا ۳۰° بچرخانید ← ۴: بیشترین ممکن. سایه‌ها بیشترین پخش را دارند.',
          'روی ۹۰° ← ۱٫۷۵ (واریانسِ ستونِ y). روی ۱۲۰° ← ۱: کمترینِ ممکن، عمود بر ۳۰°.',
          'دکمه‌ی «PC1 و PC2» را بزنید ← فلشِ سبز روی ۳۰° و فلشِ قرمز روی ۱۲۰° می‌نشیند.',
        ],
        see: 'PC1 همان جهتی است که سایه‌ها در آن بیشترین پخش را دارند (اینجا ۴ از ۵، یعنی ۸۰٪). PC2 عمود بر آن است و باقیِ پخش را دارد. اگر فقط PC1 را نگه داریم، هر نقطه با یک عدد نوشته می‌شود و ۸۰٪ پخش می‌ماند.' },
      { t: 'text', title: 'پله‌ی ۳: ماتریس کوواریانس و بردارهای ویژه',
        body: `<p>از درسِ <b>کاهش بُعد</b>: ماتریس کوواریانسِ این ابر (تقریباً):</p>
               ${ED(String.raw`C = \begin{bmatrix} 3.25 & 1.3 \\ 1.3 & 1.75 \end{bmatrix}`)}
               <p>قطر = واریانسِ هر ستون (همان عددهای ۰° و ۹۰° در تصویر). برای جهتِ واحدِ u، واریانسِ سایه‌ها = ${E(String.raw`u \cdot (C u)`)}.</p>
               <p>از درسِ <b>مقدار ویژه</b>: جهتی که ${E(String.raw`C u`)} فقط کشیده‌ی خودِ u باشد (${E(String.raw`C u = \lambda u`)})، بردار ویژه است.</p>
               <div class="key">جهتی که این واریانس را بیشترین می‌کند، <b>بردار ویژه‌ی اول</b> ${EN('Eigenvector')} است و آن بیشترین مقدار، خودِ ${E(String.raw`\lambda_1`)}.</div>` },
      { t: 'example', title: 'مثال: جهتِ ۳۰° را امتحان کنیم',
        intro: `<p>جهتِ ۳۰° یعنی ${E(String.raw`u = \begin{bmatrix} 0.866 \\ 0.5 \end{bmatrix}`)}. ضربِ C در u را سطر به سطر حساب می‌کنیم:</p>`,
        steps: [
          `سطرِ اول: ${E(String.raw`3.25 \times 0.866 + 1.3 \times 0.5 = 2.81 + 0.65 \approx 3.46`)}`,
          `سطرِ دوم: ${E(String.raw`1.3 \times 0.866 + 1.75 \times 0.5 = 1.13 + 0.875 \approx 2`)}`,
          `مقایسه با u: ${E(String.raw`4 \times 0.866 \approx 3.46`)} و ${E(String.raw`4 \times 0.5 = 2`)}؛ پس ${E(String.raw`C u \approx 4u`)}`,
          `واریانسِ سایه‌ها: ${E(String.raw`0.866 \times 3.46 + 0.5 \times 2 \approx 3 + 1 = 4`)}`,
        ],
        result: `u بردارِ ویژه است با ${E(String.raw`\lambda_1 = 4`)}؛ همان ۴ که در تصویر روی ۳۰° دیدیم.` },
      { t: 'quiz', q: `در تصویر، برای جهتِ ۱۲۰° یعنی ${E(String.raw`u = [-0.5,\ 0.866]`)}، ضربِ ${E('C u')} برابرِ ${E(String.raw`[-0.5,\ 0.866]`)} شد (خودِ u). این یعنی چه؟`,
        options: [`u بردارِ ویژه است با ${E(String.raw`\lambda = 1`)}؛ کمترین پخش، یعنی PC2`, `u بردارِ ویژه است با ${E(String.raw`\lambda = 0.866`)}؛ چون آخرین عددِ u این است`, `u بردارِ ویژه است با ${E(String.raw`\lambda = 4`)}؛ یعنی PC1`], answer: 0,
        why: `${E(String.raw`C u = \lambda u`)}: وقتی ${E('C u')} دقیقاً خودِ u می‌شود، ضریب ۱ است؛ پس ${E(String.raw`\lambda = 1`)} و این همان کمترین پخشِ تصویر (PC2) است. «۰٫۸۶۶» فقط یکی از درایه‌های u است، نه ضریب. ${E(String.raw`\lambda = 4`)} برای جهتِ ۳۰° بود، با ${E('C u = 4 u')}.` },
    ] },
    { name: 'جواب مصاحبه‌ای', cards: [
      { t: 'answer', lines: [
          'PCA یک روشِ <b>unsupervised</b> برای <b>dimensionality reduction</b> است: داده را <b>center</b> (و معمولاً <b>standardize</b>) می‌کند و محورهای تازه‌ای پیدا می‌کند که داده در آن‌ها بیشترین <b>variance</b> را دارد.',
          'از نظرِ ریاضی، principal components همان <b>eigenvectors</b>ِ <b>covariance matrix</b> هستند و <b>eigenvalue</b>ِ هر کدام، variance داده در آن جهت است؛ چون covariance matrix قرینه (symmetric) است، componentها بر هم <b>orthogonal</b>اند.',
          `داده را روی k component اول <b>project</b> می‌کنیم و k را از <b>explained variance ratio</b>، یعنی ${E(String.raw`\frac{\lambda_i}{\sum_j \lambda_j}`)}، انتخاب می‌کنیم؛ مثلاً تا ۹۰ یا ۹۵ درصد.`,
          'کاربردش visualization، فشرده کردنِ featureها و حذفِ noise است؛ ولی فقط ساختارِ <b>linear</b> را می‌بیند.',
        ],
        tip: 'نکته: کلمه‌ی کلیدی جمله‌ی دوم است: «eigenvectors of the covariance matrix». بعد بگویید eigenvalue یعنی variance در آن جهت؛ این نشان می‌دهد معنی‌اش را هم می‌دانید.' },
      { t: 'follow', items: [
          { q: 'Why must you scale features first? (چرا اول باید هم‌اندازه کرد؟)',
            a: `چون واریانس به واحد بستگی دارد: اگر متر را سانتی‌متر کنیم، عددها ۱۰۰ برابر و واریانس ${E(String.raw`100^2 = 10{,}000`)} برابر می‌شود. PCA بیشترین واریانس را دنبال می‌کند، پس PC1 فقط «ستونِ با بزرگ‌ترین واحد» می‌شود. در تصویرِ آخرِ همین درس، فقط ۲ برابر کردنِ x، PC1 را از ۳۰° به حدودِ ۱۲° برد. با standardize (کم کردنِ میانگین، تقسیم بر ${E(String.raw`\sigma`)}) واریانسِ هر ستون ۱ می‌شود.` },
          { q: 'Is PCA supervised? (آیا PCA با برچسب کار می‌کند؟)',
            a: 'نه، unsupervised است: فقط ستون‌های X را می‌بیند و هیچ‌وقت به جوابِ درست (y) نگاه نمی‌کند. برای همین جهتِ بیشترین پخش لزوماً جهتی نیست که دو دسته را از هم جدا می‌کند؛ گاهی فرقِ دو دسته در یک جهتِ کم‌پخش است و PCA همان را دور می‌ریزد. روشِ با برچسب برای کاهش بُعد: LDA.' },
          { q: 'What are the limits of PCA? (محدودیت‌های PCA چیست؟)',
            a: '(۱) فقط linear: داده‌ای که روی یک حلقه یا منحنی است با هیچ سایه‌ی صافی باز نمی‌شود (برای آن t-SNE، UMAP یا kernel PCA). (۲) تفسیرش سخت است: هر component ترکیبی از همه‌ی ستون‌هاست. (۳) به نقطه‌های پرت (outlier) حساس است، چون واریانس با مربعِ فاصله‌ها کار می‌کند. (۴) پخشِ بیشتر همیشه یعنی اطلاعاتِ مفیدتر برای پیش‌بینی نیست.' },
        ] },
      { t: 'text', title: 'پله‌ی ۴: سایه انداختن و انتخابِ k',
        body: `<p><b>تصویر کردن</b> ${EN('Projection')}: هر نقطه را با طولِ سایه‌اش روی k جهتِ اول می‌نویسیم (ضربِ داخلی با هر جهت). ۲ عدد می‌شود ۱ عدد، یا ۱۰۰ ستون می‌شود ۱۰.</p>
               <p><b>چند مؤلفه نگه داریم؟</b> سهمِ هر مؤلفه ${EN('Explained Variance Ratio')} = ${E(String.raw`\frac{\lambda_i}{\sum_j \lambda_j}`)}. مثال، ۵ ستون با ${E(String.raw`\lambda = 5,\ 3,\ 1,\ 0.5,\ 0.5`)} (جمع ۱۰): سهمِ جمع‌شونده ${E(String.raw`\frac{5}{10} = 50\%`)}، ${E(String.raw`\frac{8}{10} = 80\%`)}، ${E(String.raw`\frac{9}{10} = 90\%`)}، ۹۵٪، ۱۰۰٪.</p>
               <div class="key">برای نگه داشتنِ ۹۰٪ پخش، <b>k = ۳</b> کافی است. در تصویر: ${E(String.raw`\frac{4}{4 + 1} = 80\%`)} فقط با PC1.</div>` },
      { t: 'quiz', q: 'مصاحبه‌گر: «روی ستون‌های قد (سانتی‌متر)، وزن (کیلو) و درآمد (تومان) PCA زدیم، بدونِ هم‌اندازه کردن. PC1 تنها ۹۹٪ پخش را دارد و تقریباً همان ستونِ درآمد است. چرا؟»',
        options: ['چون عددهای درآمد خیلی بزرگ‌ترند و واریانسشان بقیه را می‌پوشاند', 'چون درآمد مهم‌ترین ستون برای پیش‌بینی است', 'چون قد و وزن کاملاً به هم وابسته‌اند', 'چون PCA همیشه ستونِ آخر را PC1 می‌کند'], answer: 0,
        why: 'واریانسِ درآمد به تومان میلیون‌ها برابرِ واریانسِ قد است، و PCA فقط بزرگیِ پخش را می‌بیند. «مهم‌ترین برای پیش‌بینی» نه: PCA اصلاً برچسب را نمی‌بیند (unsupervised). وابستگیِ قد و وزن یک مؤلفه‌ی مشترک می‌سازد، ولی ۹۹٪ را توضیح نمی‌دهد. ترتیبِ ستون‌ها هم هیچ نقشی ندارد. چاره: اول standardize.' },
      { t: 'play', w: MPCA_W_SCALE, title: 'واحد را عوض کنید، PC1 جابه‌جا می‌شود',
        body: 'همان ابر و همان خطِ چرخان. دکمه‌ی «۲ برابر کن» فقط واحدِ ستونِ x را عوض می‌کند، مثلِ این‌که به‌جای متر با نیم‌متر بشماریم؛ خودِ داده همان است.',
        look: [
          'خط را روی ۳۰° بگذارید ← بیشترین واریانس، ۴، همان‌جاست.',
          'دکمه‌ی «ستونِ x را ۲ برابر کن» را بزنید ← ابر پهن‌تر می‌شود؛ روی ۳۰° حالا ۱۲٫۴۴.',
          'خط را روی ۱۰° یا ۱۵° ببرید ← ۱۳٫۵۵، بیشتر از ۳۰°. «PC1 و PC2» را بزنید ← PC1 حدودِ ۱۲° است و ۹۲٪ پخش را دارد.',
        ],
        see: 'فقط عوض کردنِ واحد، PC1 را از ۳۰° به ۱۲° برد و سهمش را از ۸۰٪ به ۹۲٪. PCA بزرگیِ عددها را دنبال می‌کند، نه معنایشان؛ برای همین وقتی واحدها فرق دارند، اول standardize می‌کنیم.' },
    ] },
  ],
  sheet: {
    one: 'PCA داده را مرکز (و هم‌اندازه) می‌کند و محورهای عمود بر همی پیدا می‌کند که داده در آن‌ها بیشترین واریانس را دارد: بردارهای ویژه‌ی ماتریس کوواریانس، با مقدارِ ویژه = واریانس در آن جهت؛ بعد روی k تای اول سایه می‌اندازد.',
    f: String.raw`C v = \lambda v \qquad \text{Var}_u = u \cdot (C u) \qquad \text{ratio}_i = \frac{\lambda_i}{\sum_j \lambda_j}`,
    rules: ['اول center، و وقتی واحدها فرق دارند standardize؛ وگرنه PC1 = بزرگ‌ترین واحد.', 'componentها eigenvectorهای covariance matrix و بر هم عمودند؛ eigenvalue = variance در آن جهت.', 'unsupervised و فقط linear؛ componentها ترکیبِ همه‌ی ستون‌ها و سخت‌تفسیرند.'],
    use: 'نمایشِ دوبُعدیِ داده‌ی پرستون و Embeddingها، فشرده کردنِ featureها پیش از مدل، حذفِ noise.',
    mistake: 'گفتنِ این‌که PCA «مهم‌ترین ستون‌ها را انتخاب می‌کند» (ستون‌های تازه می‌سازد که ترکیبِ همه‌اند)، یا جا انداختنِ center و scale، یا این‌که با برچسب کار می‌کند.',
  },
});
