// ---------- Interview mission: Bagging vs Boosting ----------
// (names start with MBB_ because all lesson files share one global scope)

// fixed pseudo-random numbers (mulberry32), so every learner sees the same picture
const MBB_rng = seed => () => {
  seed |= 0; seed = seed + 0x6D2B79F5 | 0;
  let t = Math.imul(seed ^ seed >>> 15, 1 | seed);
  t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
  return ((t ^ t >>> 14) >>> 0) / 4294967296;
};

// 1D toy: true curve 3 + 1.5 sin(0.7x), noise std 0.6 (σ² = 0.36), rounded to 0.1.
// Two training samples (A seed 3, B seed 5) of 20 points at x = 0.25, 0.75, …, 9.75; 60 new points (seed 7).
// Checked in node (sample A · sample B · "jump" = mean (f_A − f_B)² on x = 0, 0.1, …, 10):
//   deep tree:          train 0 / 0       new 0.59 / 0.51   jump 0.60
//   bagging, 100 trees: train 0.10 / 0.05 new 0.46 / 0.40   jump 0.24
//   one stump:          train 0.52 / 0.52 new 0.78 / 0.78   jump 0.03
//   boosting, 30 stumps η 0.3: train 0.17 / 0.10 new 0.45 / 0.46 jump 0.11
//   the true curve itself on the new points: 0.36 (pure noise)
const MBB_true = x => 3 + 1.5 * Math.sin(0.7 * x);
const MBB_noisy = (xs, seed) => {
  const r = MBB_rng(seed);
  return xs.map(x => Math.round((MBB_true(x) + 0.6 * Math.sqrt(-2 * Math.log(1 - r())) * Math.cos(2 * Math.PI * r())) * 10) / 10);
};
const MBB_X = Array.from({ length: 20 }, (_, i) => 0.25 + 0.5 * i);
const MBB_XN = Array.from({ length: 60 }, (_, i) => (i + 0.5) / 6);
const MBB_Y = [MBB_noisy(MBB_X, 3), MBB_noisy(MBB_X, 5)];
const MBB_YN = MBB_noisy(MBB_XN, 7);

// regression tree: best least-squares split at midpoints, down to `depth` levels (99 = until one x per leaf)
const MBB_tree = (xs, ys, depth) => {
  const avg = a => a.reduce((p, q) => p + q, 0) / a.length;
  const sse = a => { const m = avg(a); return a.reduce((p, q) => p + (q - m) ** 2, 0); };
  const mean = avg(ys), ux = [...new Set(xs)].sort((a, b) => a - b);
  if (depth === 0 || ux.length < 2) return () => mean;
  let best = null;
  for (let i = 0; i < ux.length - 1; i++) {
    const t = (ux[i] + ux[i + 1]) / 2, L = [], R = [];
    ys.forEach((y, k) => (xs[k] < t ? L : R).push(y));
    const e = sse(L) + sse(R);
    if (!best || e < best.e - 1e-12) best = { t, e };
  }
  const li = [], ri = [];
  xs.forEach((x, k) => (x < best.t ? li : ri).push(k));
  const l = MBB_tree(li.map(k => xs[k]), li.map(k => ys[k]), depth - 1);
  const r = MBB_tree(ri.map(k => xs[k]), ri.map(k => ys[k]), depth - 1);
  return x => (x < best.t ? l(x) : r(x));
};
// bagging: 100 deep trees, each on a bootstrap sample (20 rows drawn with replacement)
const MBB_bag = s => {
  const r = MBB_rng(100 + s), T = [];
  for (let b = 0; b < 100; b++) {
    const idx = MBB_X.map(() => Math.floor(r() * MBB_X.length));
    T.push(MBB_tree(idx.map(k => MBB_X[k]), idx.map(k => MBB_Y[s][k]), 99));
  }
  return x => T.reduce((a, t) => a + t(x), 0) / T.length;
};
// boosting: start from the mean, then M stumps on the residuals, each added × η
const MBB_boost = (s, M, eta) => {
  const Y = MBB_Y[s], F0 = Y.reduce((a, b) => a + b, 0) / Y.length, T = [];
  const F = x => T.reduce((a, t) => a + eta * t(x), F0);
  for (let m = 0; m < M; m++) T.push(MBB_tree(MBB_X, MBB_X.map((x, k) => Y[k] - F(x)), 1));
  return F;
};
const MBB_MODELS = {
  deep: ['یک درختِ عمیق', s => MBB_tree(MBB_X, MBB_Y[s], 99),
    '<b style="color:var(--red)">واریانسِ زیاد</b>: از همه‌ی نقطه‌ها رد می‌شود، ولی با نمونه‌ی دیگر منحنی خیلی عوض می‌شود.'],
  bag: ['میانگینِ ۱۰۰ درخت (Bagging)', MBB_bag,
    'همان درخت‌های عمیق، ولی <b>میانگینِ</b> ۱۰۰ تا روی نمونه‌های Bootstrap: جابه‌جایی کمتر از نصف شد؛ <b style="color:var(--green)">واریانس کم شد</b>.'],
  stump: ['یک کُنده', s => MBB_tree(MBB_X, MBB_Y[s], 1),
    '<b style="color:var(--red)">سوگیریِ زیاد</b>: آرام و پایدار، ولی با یک سؤال نمی‌تواند شکلِ موج را بگیرد.'],
  boost: ['جمعِ ۳۰ کُنده (Boosting)', s => MBB_boost(s, 30, 0.3),
    '۳۰ کُنده‌ی پشت‌سرهم با η = ۰٫۳، هر کدام روی باقی‌مانده‌ها: شکلِ موج را گرفت؛ <b style="color:var(--green)">سوگیری کم شد</b>.'],
};
const MBB_CACHE = {};
const MBB_get = (m, s) => MBB_CACHE[m + s] || (MBB_CACHE[m + s] = MBB_MODELS[m][1](s));
const MBB_mse = (f, X, Y) => X.reduce((a, x, k) => a + (Y[k] - f(x)) ** 2, 0) / X.length;
const MBB_GRID = Array.from({ length: 101 }, (_, i) => i / 10);
const MBB_jump = m => { const a = MBB_get(m, 0), b = MBB_get(m, 1); return MBB_GRID.reduce((t, x) => t + (a(x) - b(x)) ** 2, 0) / MBB_GRID.length; };

// ---- Picture: one deep tree vs bagged average vs boosted sum, on two samples of the same curve ----
const MBB_W_COMPARE = h => plane(h, {
  x: [0, 10], y: [0, 6], labels: true, ratio: 0.7,
  state: { m: 'deep', s: 0 },
  buttons: [
    ...Object.keys(MBB_MODELS).map(m => ({ label: MBB_MODELS[m][0], on: s => { s.m = m; }, active: s => s.m === m })),
    { label: 'نمونه‌ی دیگر از داده', on: s => { s.s = 1 - s.s; }, active: s => s.s === 1 },
  ],
  draw: (g, s) => {
    g.grid();
    g.fn(MBB_true, 'muted', 2);
    g.fn(MBB_get(s.m, 1 - s.s), 'accent', 2);
    g.fn(MBB_get(s.m, s.s), 'orange', 3);
    MBB_X.forEach((x, k) => g.dot(x, MBB_Y[s.s][k], 'blue', 5));
  },
  read: s => {
    const f = MBB_get(s.m, s.s);
    return `نمونه‌ی ${s.s ? 'دوم' : 'اول'} · <b>${MBB_MODELS[s.m][0]}</b><br>` +
      `خطای آموزش (MSE): <b style="color:var(--blue)">${fa(MBB_mse(f, MBB_X, MBB_Y[s.s]))}</b> · ` +
      `خطای داده‌ی تازه: <b style="color:var(--red)">${fa(MBB_mse(f, MBB_XN, MBB_YN))}</b><br>` +
      `جابه‌جایی با نمونه‌ی دیگر: <b style="color:var(--accent)">${fa(MBB_jump(s.m))}</b><br>${MBB_MODELS[s.m][2]}<br>` +
      `<span class="muted">حتی خودِ منحنیِ درست روی داده‌ی تازه خطای ${fa(MBB_mse(MBB_true, MBB_XN, MBB_YN))} دارد: این سروصداست و هیچ مدلی کمش نمی‌کند.</span>`;
  },
});

lesson({
  id: 'm-bagging-boosting', node: 'bagging-vs-boosting', title: 'فرق Bagging و Boosting؟', en: 'Bagging vs Boosting',
  parts: [
    { name: 'سؤال و نردبان', cards: [
      { t: 'text', title: 'سؤالِ مصاحبه',
        body: `<p>مصاحبه‌گر می‌پرسد:</p>
               <div class="key" dir="ltr" style="text-align:left">"What's the difference between bagging and boosting? When would you use each?"</div>
               <p>یعنی: «فرقِ Bagging و Boosting چیست؟ هر کدام را کِی به کار می‌برید؟»</p>
               <p>اگر الان جوابش را بلد نیستید، اشکالی ندارد. همه‌ی تکه‌هایش را در درس‌های قبل دیده‌اید. قدم به قدم کنارِ هم می‌گذاریم.</p>` },
      { t: 'ladder' },
      { t: 'text', title: 'پله‌ی ۱: خطا دو جور است',
        body: `<p>از درسِ <b>سوگیری و واریانس</b>: ${E('Error = Bias² + Variance + σ²')}.</p>
               <p><b>سوگیری</b> ${EN('Bias')} یعنی مدل به‌طور میانگین کج می‌زند (زیادی ساده است). <b>واریانس</b> ${EN('Variance')} یعنی با نمونه‌ی دیگری از داده، جوابش خیلی می‌پرد. σ² سروصداست و دستِ ما نیست.</p>
               <p>از درسِ <b>درخت تصمیم</b>: درختِ <b>عمیق</b> همه‌ی پیچ‌ها را می‌گیرد ولی لرزان است (واریانسِ زیاد). <b>کُنده</b> ${EN('Stump')}، درختی با یک سؤال، آرام است ولی ساده (سوگیریِ زیاد).</p>
               <div class="key">Bagging و Boosting هر کدام یکی از این دو خطا را نشانه می‌گیرند.</div>` },
      { t: 'text', title: 'پله‌ی ۲: Bagging، کنارِ هم',
        body: `<p>از درسِ <b>جنگل تصادفی</b>: صدها درختِ <b>عمیق</b> را <b>هم‌زمان و جدا</b> ${EN('Parallel')} می‌سازیم. هر درخت یک نمونه‌ی دوباره ${EN('Bootstrap')} می‌بیند: ردیف‌ها را تصادفی و با برگرداندن برمی‌داریم. آخر <b>میانگین</b> (یا رأیِ اکثریت) می‌گیریم.</p>
               <p>فرض کنید جوابِ یک درخت واریانسِ ${E('τ²')} دارد و میانگینِ ${E('M')} درخت را می‌گیریم. اگر درخت‌ها مستقل بودند: ${E('Var = τ²/M')}. ولی شبیه‌اند (همبستگی ${E('ρ')}): ${E('Var = ρτ² + (1 − ρ)τ²/M')}. با ${E('τ² = 1, ρ = 0.5, M = 100')}: ${E('0.5 + 0.005 = 0.505')}؛ هرگز زیرِ ۰٫۵ نمی‌رود.</p>
               <div class="key">برای همین جنگل تصادفی در هر سؤالِ درخت (split) فقط چند <b>ستونِ تصادفی</b> را امتحان می‌کند تا درخت‌ها کمتر شبیه شوند (ρ کمتر). نتیجه: <b>واریانسِ کمتر</b>.</div>` },
      { t: 'text', title: 'پله‌ی ۳: Boosting، پشتِ سرِ هم',
        body: `<p>از همان درس: درخت‌های <b>کوچک</b>، <b>یکی پس از دیگری</b> ${EN('Sequential')}. هر درختِ تازه روی <b>باقی‌مانده‌ها</b> ${EN('Residuals')} ساخته می‌شود، یعنی اشتباهی که قبلی‌ها هنوز دارند:</p>
               <p class="read">${E('F_new(x) = F_old(x) + η · h(x)')}</p>
               <p>هر کُنده ساده است، ولی جمعِ ده‌ها کُنده شکل‌های پیچیده را می‌گیرد. نتیجه: <b>سوگیریِ کمتر</b>.</p>
               <div class="key">خطرش: اگر زیاد ادامه بدهیم، بعد از گرفتنِ شکلِ اصلی، سروصدا را دنبال می‌کند (بیش‌برازش). پس نرخ یادگیریِ کوچک (η) و <b>توقفِ زودهنگام</b> ${EN('Early Stopping')} لازم است.</div>` },
      { t: 'quiz', q: 'جنگلی از ۱۰۰ درخت داریم. واریانسِ جوابِ هر درخت ۱ است و همبستگیِ دو درخت ρ = ۰٫۲ است. واریانسِ میانگینِ جنگل چقدر است؟',
        options: ['۰٫۰۱', '۰٫۲۰۸', '۰٫۸۰۲'], answer: 1,
        why: 'ρτ² + (1 − ρ)τ²/M = ۰٫۲ + ۰٫۸ ÷ ۱۰۰ = ۰٫۲۰۸. «۰٫۰۱» یعنی τ²/M؛ درخت‌ها را مستقل فرض کرده‌اید، ولی همبسته‌اند و تکه‌ی ρτ² با درختِ بیشتر کم نمی‌شود. «۰٫۸۰۲» یعنی ρ و (1 − ρ) را جابه‌جا گذاشته‌اید.' },
    ] },
    { name: 'جواب مصاحبه‌ای', cards: [
      { t: 'answer', lines: [
          'هر دو <b>ensemble</b> از درخت‌ها هستند، ولی خطای متفاوتی را کم می‌کنند: Bagging <b>variance</b> را، Boosting <b>bias</b> را.',
          'Bagging مدل‌های قوی ولی لرزان، مثلِ deep trees، را <b>parallel</b> روی <b>bootstrap samples</b> می‌سازد و average یا majority vote می‌گیرد؛ Random Forest با random feature subsets درخت‌ها را <b>decorrelate</b> می‌کند.',
          'Boosting مدل‌های ضعیف، مثلِ shallow trees، را <b>sequential</b> می‌سازد و هر کدام روی residuals یا خطاهای قبلی‌ها کار می‌کند؛ برای همین learning rate کوچک و <b>early stopping</b> لازم دارد و به <b>label noise</b> حساس است، چون ممکن است noise را overfit کند.',
          'وقتی مدل overfit می‌کند یا داده noisy است و یک baseline محکم با tuning کم می‌خواهم، <b>Random Forest</b>؛ وقتی بیشترین دقت روی داده‌ی جدولی را می‌خواهم و وقتِ tuning دارم، <b>Gradient Boosting</b> مثلِ XGBoost یا LightGBM.',
        ],
        tip: 'نکته: با جمله‌ی اول شروع کنید (variance در برابرِ bias). مصاحبه‌گر همین را می‌خواهد بشنود؛ بقیه توضیحِ «چطور» است.' },
      { t: 'follow', items: [
          { q: 'Why does Random Forest pick random features? (چرا جنگل تصادفی ستون‌های تصادفی برمی‌دارد؟)',
            a: 'اگر یک ستونِ خیلی قوی باشد، همه‌ی درخت‌ها اول همان سؤال را می‌پرسند و شبیهِ هم می‌شوند؛ خطاهایشان همبسته است. در Var = ρτ² + (1 − ρ)τ²/M، تکه‌ی ρτ² با درختِ بیشتر کم نمی‌شود. با امتحان کردنِ چند ستونِ تصادفی در هر سؤال (برای دسته‌بندی معمولاً حدودِ √p از p ستون)، ρ پایین می‌آید و میانگین واقعاً کمک می‌کند.' },
          { q: 'Which is more sensitive to noisy labels? (کدام به برچسب‌های اشتباه حساس‌تر است؟)',
            a: 'Boosting. نقطه‌ای که برچسبش غلط است همیشه «اشتباه» به نظر می‌رسد، و Boosting هر دور دقیقاً روی اشتباه‌ها تمرکز می‌کند (AdaBoost وزنشان را مدام بالا می‌برد). در Bagging آن نقطه فقط در بخشی از درخت‌ها هست و در میانگین گم می‌شود. چاره در Boosting: η کوچک، early stopping، subsampling و loss مقاوم مثلِ Huber.' },
          { q: 'What is a bootstrap sample? (نمونه‌ی Bootstrap چیست؟)',
            a: 'از n ردیف، n بار <b>با برگرداندن</b> برمی‌داریم. احتمالِ این‌که یک ردیف هیچ‌وقت انتخاب نشود (1 − 1/n)ⁿ ≈ 1/e ≈ ۳۶٫۸٪ است؛ پس هر درخت حدودِ ۶۳٪ ردیف‌های متفاوت را می‌بیند. ردیف‌های جامانده (Out-of-Bag) را می‌شود برای سنجیدنِ همان درخت به کار برد؛ یک validation مجانی.' },
        ] },
      { t: 'play', w: MBB_W_COMPARE, title: 'پله‌ی ۴: هر سه را روی یک موج ببینید',
        body: 'نقطه‌های <b style="color:var(--blue)">آبی</b> ۲۰ نقطه از یک موجِ پرسروصدا هستند. منحنیِ خاکستری موجِ درست است. منحنیِ <b style="color:var(--orange)">نارنجی</b> مدل است و منحنیِ کم‌رنگِ <b style="color:var(--accent)">دیگر</b> همان نوع مدل روی <b>نمونه‌ی دیگری</b> از همان موج. هر چه این دو بیشتر از هم دور باشند، واریانس بیشتر است. چهار مدل را امتحان کنید و دکمه‌ی «نمونه‌ی دیگر» را بزنید.' },
      { t: 'quiz', q: 'در تصویر، «جابه‌جایی با نمونه‌ی دیگر» برای یک درختِ عمیق ۰٫۶ بود و برای Bagging حدودِ ۰٫۲۴. Bagging کدام بخشِ خطا را کم کرد؟',
        options: ['واریانس', 'سوگیری', 'سروصدا (σ²)'], answer: 0,
        why: 'جابه‌جایی یعنی «با داده‌ی دیگر، جواب چقدر می‌پرد»؛ این خودِ واریانس است، و میانگین گرفتن آن را کم می‌کند. سوگیری نه: درختِ عمیق از اول همه‌ی پیچ‌ها را می‌گرفت و میانگینِ درخت‌های کج هم کج می‌ماند. سروصدا را هیچ مدلی کم نمی‌کند؛ حتی منحنیِ درست روی داده‌ی تازه خطای ۰٫۳۶ داشت.' },
      { t: 'quiz', q: 'مصاحبه‌گر: «حدودِ ۱۰٪ برچسب‌های داده‌ی ما اشتباه است و فرصتِ تنظیمِ زیادی هم نداریم. اول کدام را امتحان می‌کنید؟»',
        options: ['Random Forest، چون میانگین اثرِ نقطه‌های اشتباه را کم می‌کند', 'Boosting با ۱۰۰۰ دور و η = ۱، چون سوگیری را بیشتر کم می‌کند', 'یک درختِ عمیقِ تنها، چون همه‌ی داده را دقیق یاد می‌گیرد', 'Boosting، چون همیشه از Bagging دقیق‌تر است'], answer: 0,
        why: 'با برچسب‌های اشتباه، خطرِ اصلی دنبال کردنِ سروصداست. Random Forest میانگین می‌گیرد و تنظیمِ کمی می‌خواهد. Boosting با η بزرگ و دورِ زیاد دقیقاً همان نقطه‌های غلط را دنبال می‌کند. درختِ عمیقِ تنها برچسب‌های غلط را هم حفظ می‌کند (واریانسِ زیاد). Boosting «همیشه» بهتر نیست؛ معمولاً با تنظیمِ دقیق و داده‌ی تمیز جلو می‌افتد.' },
    ] },
  ],
  sheet: {
    one: 'هر دو ensemble از درخت‌اند: Bagging (و Random Forest) درخت‌های عمیق را جدا و هم‌زمان روی نمونه‌های Bootstrap می‌سازد و میانگین می‌گیرد ← واریانسِ کمتر؛ Boosting درخت‌های کوچک را پشت‌سرهم روی باقی‌مانده‌ها می‌سازد ← سوگیریِ کمتر.',
    f: 'Bagging: f̄(x) = (1/M) Σ fₘ(x),  Var = ρτ² + (1 − ρ)τ²/M  ·  Boosting: F_new(x) = F_old(x) + η · h(x)',
    rules: ['Bagging: parallel، deep trees، bootstrap، average ← variance کم. درختِ بیشتر ضرر ندارد.', 'Random Forest: ستون‌های تصادفی در هر سؤال تا ρ کم شود.', 'Boosting: sequential، shallow trees، residuals ← bias کم؛ η کوچک و early stopping، و حساس به برچسبِ اشتباه.'],
    use: 'داده‌ی جدولی: Random Forest به‌عنوانِ baseline محکم؛ XGBoost و LightGBM برای بیشترین دقت.',
    mistake: 'گفتنِ این‌که «Boosting سوگیری و واریانس هر دو را کم می‌کند و همیشه بهتر است»، یا جابه‌جا گفتنِ این دو: Bagging = موازی و واریانس، Boosting = پشت‌سرهم و سوگیری.',
  },
});
