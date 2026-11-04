// ---------- Interview mission: Why is L1 sparse? ----------
// (names start with ML1_ because all lesson files share one global scope)

// ---- Picture: two weights. Data loss f(w) = (w − C)ᵀ A (w − C), ellipse contours around C = (2, 1).
// Budget form: minimize f with |w₁| + |w₂| ≤ t (diamond, L1) or w₁² + w₂² ≤ t² (circle, L2).
// Diamond: best point on each of the 4 edges (1-D quadratic, clamped) → pick the lowest. Circle: w = (A + μI)⁻¹ A C, μ by bisection.
// Checked in node (w₁, w₂):
//   diamond t 0.25…1.75 → (t, 0) exactly: a corner · t 2 → (1.875, 0.125) · t 2.5 → (1.938, 0.563) · t 3 → (2, 1) = C
//   circle  t 1 → (0.913, 0.407) · t 1.5 → (1.365, 0.623) · t 2 → (1.804, 0.863) · t ≥ 2.25 → C (|C| ≈ 2.236)
const ML1_C = [2, 1], ML1_A = [[1, 0.3], [0.3, 0.4]];
const ML1_f = w => { const a = w[0] - ML1_C[0], b = w[1] - ML1_C[1]; return ML1_A[0][0] * a * a + 2 * ML1_A[0][1] * a * b + ML1_A[1][1] * b * b; };
const ML1_Av = v => [ML1_A[0][0] * v[0] + ML1_A[0][1] * v[1], ML1_A[1][0] * v[0] + ML1_A[1][1] * v[1]];
const ML1_diamond = t => {
  if (Math.abs(ML1_C[0]) + Math.abs(ML1_C[1]) <= t) return ML1_C.slice();
  const P = [[t, 0], [0, t], [-t, 0], [0, -t]];
  let best = null, bf = Infinity;
  for (let i = 0; i < 4; i++) {
    const p = P[i], q = P[(i + 1) % 4], d = [q[0] - p[0], q[1] - p[1]], r = [ML1_C[0] - p[0], ML1_C[1] - p[1]], Ad = ML1_Av(d);
    const u = Math.max(0, Math.min(1, (Ad[0] * r[0] + Ad[1] * r[1]) / (Ad[0] * d[0] + Ad[1] * d[1])));
    const w = [p[0] + u * d[0], p[1] + u * d[1]], v = ML1_f(w);
    if (v < bf - 1e-12) { bf = v; best = w; }
  }
  return best;
};
const ML1_circle = t => {
  if (Math.hypot(...ML1_C) <= t) return ML1_C.slice();
  const sol = mu => { const a = ML1_A[0][0] + mu, b = ML1_A[0][1], d = ML1_A[1][1] + mu, det = a * d - b * b, r = ML1_Av(ML1_C); return [(d * r[0] - b * r[1]) / det, (-b * r[0] + a * r[1]) / det]; };
  let lo = 0, hi = 1e4;
  for (let k = 0; k < 200; k++) { const m = (lo + hi) / 2; Math.hypot(...sol(m)) > t ? lo = m : hi = m; }
  return sol(hi);
};
const ML1_zero = v => Math.abs(v) < 1e-9;

const ML1_W_SHAPES = h => plane(h, {
  x: [-1.2, 3.2], y: [-1.2, 2.2], equal: true, step: [1, 1], labels: true, names: ['w₁', 'w₂'],
  state: { t: 1, m: 1 },
  sliders: [{ key: 't', label: 'بودجه‌ی t (اندازه‌ی شکل):', min: 0.25, max: 3, step: 0.25 }],
  buttons: [
    { label: 'L1: لوزی', on: s => { s.m = 1; }, active: s => s.m === 1 },
    { label: 'L2: دایره', on: s => { s.m = 2; }, active: s => s.m === 2 },
  ],
  draw: (g, s) => {
    const { ctx, X, Y, css } = g;
    g.grid();
    // the allowed region
    ctx.beginPath();
    if (s.m === 1) { ctx.moveTo(X(s.t), Y(0)); ctx.lineTo(X(0), Y(s.t)); ctx.lineTo(X(-s.t), Y(0)); ctx.lineTo(X(0), Y(-s.t)); ctx.closePath(); }
    else ctx.arc(X(0), Y(0), X(s.t) - X(0), 0, 7);
    ctx.globalAlpha = 0.18; ctx.fillStyle = css('blue'); ctx.fill(); ctx.globalAlpha = 1;
    ctx.setLineDash([]); ctx.lineWidth = 2.5; ctx.strokeStyle = css('blue'); ctx.stroke();
    // ellipse contours of the data loss: f = k
    const ring = (k, color, wd) => {
      ctx.beginPath();
      for (let i = 0; i <= 120; i++) {
        const a = i / 120 * 2 * Math.PI, u = [Math.cos(a), Math.sin(a)], Au = ML1_Av(u), r = Math.sqrt(k / (u[0] * Au[0] + u[1] * Au[1]));
        const px = X(ML1_C[0] + r * u[0]), py = Y(ML1_C[1] + r * u[1]);
        i ? ctx.lineTo(px, py) : ctx.moveTo(px, py);
      }
      ctx.setLineDash([]); ctx.lineWidth = wd; ctx.strokeStyle = css(color); ctx.stroke();
    };
    [0.15, 0.6, 1.4, 2.5].forEach(k => ring(k, 'soft', 1.5));
    const w = s.m === 1 ? ML1_diamond(s.t) : ML1_circle(s.t), fw = ML1_f(w);
    if (fw > 1e-9) ring(fw, 'orange', 3);
    g.dot(ML1_C[0], ML1_C[1], 'red', 6);
    g.text(ML1_C[0], ML1_C[1], 'بهترین بی‌جریمه', 'red', 'center', -14);
    g.dot(w[0], w[1], 'green', 8);
  },
  read: s => {
    const w = s.m === 1 ? ML1_diamond(s.t) : ML1_circle(s.t);
    const v = x => ML1_zero(x) ? '<b style="color:var(--red)">دقیقاً ۰</b>' : `<b>${fa(x)}</b>`;
    const head = `نقطه‌ی تماس (<b style="color:var(--green)">سبز</b>): w₁ = ${v(w[0])} · w₂ = ${v(w[1])}<br>`;
    if (ML1_f(w) < 1e-9) return head + 'بودجه آن‌قدر بزرگ است که بهترین نقطه‌ی بی‌جریمه خودش داخلِ شکل است؛ جریمه کاری نمی‌کند. بودجه را کم کنید.';
    if (s.m === 2) return head + 'دایره گوشه ندارد؛ بیضی هر جای لبه‌اش ممکن است بخورد. هر دو وزن کوچک شدند، ولی هیچ‌کدام صفر نشد.';
    if (ML1_zero(w[1])) return head + 'اولین تماسِ بیضی با لوزی روی <b>گوشه</b>‌ی آن است، روی محورِ w₁. یعنی وزنِ w₂ کنار گذاشته شد.';
    return head + 'این بار بیضی به یک <b>ضلع</b> خورد و هر دو وزن ماندند. بودجه بزرگ است و جریمه کم‌اثر؛ بودجه را کمتر کنید.';
  },
});

lesson({
  id: 'm-l1-sparse', node: 'why-is-l1-sparse', title: 'چرا L1 وزن‌ها را صفر می‌کند؟', en: 'Why is L1 sparse?',
  parts: [
    { name: 'سؤال و نردبان', cards: [
      { t: 'text', title: 'سؤالِ مصاحبه',
        body: `<p>مصاحبه‌گر می‌پرسد:</p>
               <div class="key" dir="ltr" style="text-align:left">"Why does L1 regularization produce sparse weights, while L2 doesn't?"</div>
               <p>یعنی: «چرا منظم‌سازیِ L1 بعضی وزن‌ها را دقیقاً صفر می‌کند (تُنُک ${EN('Sparse')})، ولی L2 نه؟»</p>
               <p>اگر الان جوابش را بلد نیستید، اشکالی ندارد. همه‌ی تکه‌هایش را در درس‌های قبل دیده‌اید. قدم به قدم کنارِ هم می‌گذاریم.</p>` },
      { t: 'ladder' },
      { t: 'text', title: 'پله‌ی ۱: دو جور مالیات',
        body: `<p>از درسِ <b>منظم‌سازی</b>: به خطای داده، مالیاتی برای بزرگیِ وزن‌ها اضافه می‌کنیم.</p>
               <p class="read">L2 (Ridge): ${E(String.raw`\text{Loss} = \text{MSE} + \lambda \sum_i w_i^2`)}<br>L1 (Lasso): ${E(String.raw`\text{Loss} = \text{MSE} + \lambda \sum_i |w_i|`)}</p>
               <p><b>تُنُک</b> یعنی بیشترِ وزن‌ها <b>دقیقاً</b> صفرند، نه فقط کوچک. وزنِ صفر یعنی آن ورودی کلاً کنار رفته ${EN('Feature Selection')}.</p>
               <div class="key">مصاحبه‌گر معمولاً دو توضیح می‌خواهد: یکی با <b>مشتق</b>، یکی با <b>شکل</b>.</div>` },
      { t: 'text', title: 'پله‌ی ۲: توضیحِ مشتق',
        body: `<p>از درسِ <b>مشتق</b>: شیبِ جریمه یعنی «کششِ» آن به سمتِ صفر.</p>
               <p class="read">L2: ${E(String.raw`(\lambda w^2)' = 2\lambda w`)} &nbsp;·&nbsp; L1: ${E(String.raw`(\lambda |w|)' = \lambda \cdot \text{sign}(w)`)}</p>
               <p>sign یعنی علامت: ۱+ برای w مثبت، ۱− برای w منفی. با ${E(String.raw`\lambda = 0.5`)}:</p>
               <p class="read">${E(String.raw`w = 1:\quad \text{L2} \to 1,\quad \text{L1} \to 0.5`)}<br>${E(String.raw`w = 0.1:\quad \text{L2} \to 0.1,\quad \text{L1} \to 0.5`)}<br>${E(String.raw`w = 0.01:\quad \text{L2} \to 0.01,\quad \text{L1} \to 0.5`)}</p>
               <div class="key">کششِ L2 (${E(String.raw`2\lambda w`)}) نزدیکِ صفر جان ندارد؛ وزن به صفر نمی‌رسد. کششِ L1 <b>ثابت</b> است (همیشه ${E(String.raw`\lambda`)})؛ اگر زورِ داده از ${E(String.raw`\lambda`)} کمتر باشد، وزن تا خودِ صفر می‌رود و می‌ماند.</div>` },
      { t: 'play', w: ML1_W_SHAPES, title: 'بیضی به کجا می‌خورد؟',
        body: '<b style="color:var(--red)">قرمز</b> = بهترین وزن‌ها بدونِ جریمه (۲، ۱). بیضی‌ها = وزن‌هایی با خطای داده‌ی یکسان. <b style="color:var(--blue)">آبی</b> = بودجه، وزن‌ها فقط داخلِ آن مجازند (L1 لوزی، L2 دایره). <b style="color:var(--orange)">نارنجی</b> = اولین بیضی که به شکل می‌خورد؛ <b style="color:var(--green)">سبز</b> = جای تماس، یعنی جوابِ جریمه‌دار.',
        look: [
          'با لوزی و بودجه‌ی ۱ ← نقطه‌ی سبز روی گوشه‌ی (۱، ۰) است: w₂ دقیقاً صفر شد.',
          'بودجه را تا ۱٫۷۵ ببرید ← سبز هنوز روی گوشه است، (۱٫۷۵، ۰)؛ w₂ هنوز صفر.',
          'بودجه را روی ۲٫۵ بگذارید ← تماس روی ضلع می‌افتد، (۱٫۹۴، ۰٫۵۶): هیچ وزنی صفر نیست.',
          'بودجه را به ۱ برگردانید و «L2: دایره» را بزنید ← (۰٫۹۱، ۰٫۴۱): هر دو کوچک، هیچ‌کدام صفر نه.',
        ],
        see: 'لوزی گوشه‌های تیز روی محورها دارد و بیضیِ در حالِ بزرگ شدن معمولاً اول به همان گوشه می‌خورد؛ روی گوشه یکی از وزن‌ها صفر است. دایره گوشه ندارد، پس تماس تقریباً هیچ‌وقت دقیقاً روی محور نیست. این همان توضیحِ «شکل» برای مصاحبه است.' },
      { t: 'quiz', q: `${E(String.raw`\lambda = 0.5`)} و وزنِ ${E('w = 0.1')}. کششِ هر جریمه به سمتِ صفر چقدر است؟`,
        options: ['L1: ۰٫۰۵ و L2: ۰٫۱', 'هر دو ۰٫۱', 'L1: ۰٫۵ و L2: ۰٫۱', 'L1: ۰٫۵ و L2: ۰٫۰۰۵'], answer: 2,
        why: `کششِ L1 همیشه ${E(String.raw`\lambda = 0.5`)} است؛ کششِ L2 برابرِ ${E(String.raw`2\lambda w = 2 \times 0.5 \times 0.1 = 0.1`)}. «۰٫۰۵» خودِ جریمه‌ی L1 است (${E(String.raw`\lambda |w|`)})، نه شیبش. «۰٫۰۰۵» خودِ جریمه‌ی L2 است (${E(String.raw`\lambda w^2`)})، نه شیبش. هم‌اندازه هم نیستند: در ${E('w = 0.1')} کششِ L1 پنج برابرِ L2 است.` },
    ] },
    { name: 'جواب مصاحبه‌ای', cards: [
      { t: 'answer', lines: [
          `دو توضیح دارد. <b>Gradient</b>: مشتقِ L1، یعنی ${E(String.raw`\lambda \cdot \text{sign}(w)`)}، اندازه‌اش ثابت است؛ پس وزن را با همان زور تا خودِ صفر هل می‌دهد. مشتقِ L2، یعنی ${E(String.raw`2\lambda w`)}، نزدیکِ صفر خودش صفر می‌شود؛ وزن کوچک می‌شود ولی صفر نه.`,
          `اگر اندازه‌ی gradientِ داده در صفر از ${E(String.raw`\lambda`)} بیشتر نباشد، با L1 آن وزن دقیقاً روی صفر می‌ماند.`,
          '<b>Geometry</b>: در فرمِ constraint، ناحیه‌ی L1 یک diamond است با گوشه‌هایی روی محورها و ناحیه‌ی L2 یک circle. contourهای loss معمولاً اول به یک <b>گوشه</b> می‌خورند، و آن‌جا یکی از وزن‌ها صفر است.',
          'پس L1 هم‌زمان feature selection می‌کند؛ L2 فقط وزن‌ها را کوچک و پخش می‌کند.',
        ],
        tip: 'نکته: هر دو توضیح را بگویید؛ اول یک جمله‌ی gradient، بعد تصویرِ لوزی. اگر اجازه دارید، لوزی و بیضی را روی تخته بکشید.' },
      { t: 'follow', items: [
          { q: 'When would you use L1 vs L2? (کِی L1 و کِی L2؟)',
            a: 'L1 وقتی ورودی‌ها خیلی زیادند و فقط چند تا مهم‌اند، یا مدلِ قابلِ توضیح می‌خواهیم. L2 وقتی اثرها کوچک و پخش‌اند، یا ورودی‌ها با هم همبسته‌اند (L1 از چند ورودیِ همبسته تقریباً دلبخواهی یکی را نگه می‌دارد). در شبکه‌های عصبی معمولاً L2 (Weight Decay) پیش‌فرض است.' },
          { q: 'What is Elastic Net? (الاستیک‌نت چیست؟)',
            a: `هر دو جریمه با هم: ${E(String.raw`\text{Loss} = \text{MSE} + \lambda_1 \sum_i |w_i| + \lambda_2 \sum_i w_i^2`)}. از L1 تُنُکی را می‌گیرد، از L2 پایداری را؛ ورودی‌های همبسته را با هم نگه می‌دارد یا با هم کنار می‌گذارد.` },
          { q: 'Is L1 differentiable at 0? (آیا L1 در صفر مشتق دارد؟)',
            a: `نه؛ ${E('|w|')} در صفر یک گوشه‌ی تیز دارد. به‌جایش از زیرگرادیان (Subgradient) استفاده می‌کنیم: در صفر هر شیبی بینِ ${E(String.raw`-\lambda`)} و ${E(String.raw`+\lambda`)} برای جریمه قبول است؛ پس اگر زورِ داده کمتر از ${E(String.raw`\lambda`)} باشد، w روی صفر می‌ماند.` },
        ] },
      { t: 'example', title: 'پله‌ی ۳: یک وزن، با عدد',
        intro: `<p>یک وزنِ تنها، با خطای داده‌ی ${E('(w - 1)^2')}؛ یعنی بهترین وزنِ بی‌جریمه ۱ است. با گذاشتنِ مشتق برابرِ صفر، کمینه با جریمه این می‌شود:</p>
               <p class="read">L1: ${E(String.raw`w = 1 - \frac{\lambda}{2}`)} (و اگر ${E(String.raw`\lambda \ge 2`)}، ${E('w = 0')}) &nbsp;·&nbsp; L2: ${E(String.raw`w = \frac{1}{1 + \lambda}`)}</p>`,
        steps: [
          `${E(String.raw`\lambda = 1`)}: L1 ← ${E(String.raw`1 - \frac{1}{2} = 0.5`)}؛ L2 ← ${E(String.raw`\frac{1}{1 + 1} = 0.5`)}. هنوز هم‌اندازه‌اند.`,
          `${E(String.raw`\lambda = 2`)}: L1 ← ${E(String.raw`1 - \frac{2}{2} = 0`)}؛ L2 ← ${E(String.raw`\frac{1}{3} \approx 0.33`)}.`,
          `${E(String.raw`\lambda = 4`)}: L1 ← چون ${E(String.raw`4 \ge 2`)}، باز ${E('w = 0')}؛ L2 ← ${E(String.raw`\frac{1}{5} = 0.2`)}.`,
        ],
        result: `L1 از یک ${E(String.raw`\lambda`)} به بعد وزن را دقیقاً صفر می‌کند و همان‌جا نگه می‌دارد. L2 هر قدر ${E(String.raw`\lambda`)} بزرگ شود، فقط کوچک‌ترش می‌کند.` },
      { t: 'text', title: 'پله‌ی ۴: توضیحِ شکل',
        body: `<p>تصویر را با کلام بگوییم: «کمترین خطای داده، به شرطِ بودجه»، یعنی ${E(String.raw`|w_1| + |w_2| \le t`)} برای L1 و ${E(String.raw`w_1^2 + w_2^2 \le t^2`)} برای L2. ${E(String.raw`\lambda`)} بزرگ‌تر یعنی t کوچک‌تر.</p>
               <p>لوزی گوشه‌های تیز روی محورها دارد. بیضیِ در حالِ بزرگ شدن بیشتر اول به یکی از گوشه‌ها می‌خورد، و روی گوشه یکی از وزن‌ها صفر است. دایره گوشه ندارد.</p>
               <div class="key">«معمولاً»؛ اگر بودجه بزرگ باشد، تماس روی ضلع می‌افتد و هیچ وزنی صفر نیست. در تصویر t = ۲٫۵ را ببینید.</div>` },
      { t: 'quiz', q: 'مصاحبه‌گر: «چرا L2 وزن‌ها را دقیقاً صفر نمی‌کند؟» بهترین جواب کدام است؟',
        options: ['چون جریمه‌ی L2 برای همه‌ی وزن‌ها از جریمه‌ی L1 کوچک‌تر است', 'چون L2 در صفر مشتق ندارد و گرادیان کاهشی آن‌جا گیر می‌کند', `چون ${E(String.raw`\lambda`)} ی L2 همیشه کوچک انتخاب می‌شود`, `کششِ L2 یعنی ${E(String.raw`2\lambda w`)} نزدیکِ صفر محو می‌شود، پس وزن به صفر نمی‌رسد`], answer: 3,
        why: `دلیل کششِ کم‌جانِ ${E(String.raw`2\lambda w`)} نزدیکِ صفر است. جریمه‌ی L2 همیشه کوچک‌تر نیست: برای ${E('w = 3')}، ${E(String.raw`\lambda w^2 = 9\lambda`)} ولی ${E(String.raw`\lambda |w| = 3\lambda`)}. مشتق نداشتن در صفر ویژگیِ L1 است، نه L2. با ${E(String.raw`\lambda`)} ی بزرگ هم L2 وزن را فقط کوچک‌تر می‌کند، صفر نه.` },
    ] },
  ],
  sheet: {
    one: `کششِ L1 به سمتِ صفر ثابت است (${E(String.raw`\lambda`)}) و وزن‌های کم‌اهمیت را تا خودِ صفر می‌برد؛ کششِ L2 (${E(String.raw`2\lambda w`)}) نزدیکِ صفر جان ندارد. در شکل: لوزیِ L1 گوشه روی محورها دارد و بیضیِ خطا معمولاً به گوشه می‌خورد.`,
    f: String.raw`(\lambda |w|)' = \lambda\,\text{sign}(w) \qquad (\lambda w^2)' = 2\lambda w \qquad |w_1| + |w_2| \le t \ \ (\text{L1}) \qquad w_1^2 + w_2^2 \le t^2 \ \ (\text{L2})`,
    rules: [`با یک وزن و خطای داده‌ی ${E('(w - c)^2')}: L1 ← اگر ${E(String.raw`\lambda \ge 2|c|`)}، w دقیقاً ۰ است؛ L2 ← ${E(String.raw`w = \frac{c}{1 + \lambda}`)}، هیچ‌وقت صفر نیست.`,
      `${E(String.raw`\lambda`)} بزرگ‌تر = بودجه‌ی t کوچک‌تر = وزن‌های صفرِ بیشتر.`,
      'L1 در صفر مشتق ندارد؛ از زیرگرادیان (Subgradient) استفاده می‌شود. Elastic Net = L1 + L2.'],
    use: 'Lasso برای انتخابِ ورودی (Feature Selection) وقتی ورودی‌ها هزاران‌اند؛ مدل‌های ساده و قابلِ توضیح.',
    mistake: 'گفتنِ «چون جریمه‌ی L1 بزرگ‌تر است»؛ برای وزن‌های بزرگ جریمه‌ی L2 بزرگ‌تر است. مهم <b>شیبِ</b> جریمه نزدیکِ صفر است (یا گوشه‌های لوزی)، نه اندازه‌ی خودِ جریمه.',
  },
});
