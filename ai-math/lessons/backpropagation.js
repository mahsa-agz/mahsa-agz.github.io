// ---------- Deep Learning: Backpropagation ----------
// (names start with BP_ because all lesson files share one global scope)

// whole numbers with Persian digits and thousands separators: 1048576 -> ۱٬۰۴۸٬۵۷۶
// like fa() but keeps up to 4 decimals, so the shrinking error stays visible
const BP_fa4 = n => String(+n.toFixed(4)).replace('-', '−').replace('.', '٫').replace(/\d/g, d => '۰۱۲۳۴۵۶۷۸۹'[d]);
const BP_int = n => String(n).replace(/\B(?=(\d{3})+(?!\d))/g, '٬').replace(/\d/g, d => '۰۱۲۳۴۵۶۷۸۹'[d]);
// the same 4-decimal number with Latin digits, for inside LaTeX
const BP_t4 = n => String(+n.toFixed(4));
// LaTeX for a partial slope ∂a/∂b
const BP_d = (a, b) => String.raw`\frac{\partial ${a}}{\partial ${b}}`;

// picture 1: a tiny network  x -> h = ReLU(w1·x) -> ŷ = w2·h -> E = (ŷ − y)²
// fixed start x = 2, y = 10, w1 = 1, w2 = 3:  h = 2, ŷ = 6, E = 16
// backward: dE/dŷ = 2(ŷ − y) = −8, dE/dw2 = −8·h = −16, dE/dh = −8·w2 = −24, dE/dw1 = −24·1·x = −48
// one step with η = 0.01: w1 = 1.48, w2 = 3.16 -> h = 2.96, ŷ = 9.3536, E ≈ 0.418; then ≈ 0.0001
const BP_X = 2, BP_Y = 10, BP_ETA = 0.01;
const BP_fwd = s => {
  s.z = s.w1 * BP_X;
  s.h = Math.max(0, s.z);
  s.yh = s.w2 * s.h;
  s.E = (s.yh - BP_Y) ** 2;
};
const BP_bwd = s => {
  s.gy = 2 * (s.yh - BP_Y);          // dE/dŷ
  s.g2 = s.gy * s.h;                 // dE/dw2 = dE/dŷ · ŷ/w2-slope (h)
  s.gh = s.gy * s.w2;                // dE/dh  = dE/dŷ · w2
  s.g1 = s.gh * (s.z > 0 ? 1 : 0) * BP_X; // dE/dw1 = dE/dh · ReLU slope · x
};
const BP_reset = s => { s.w1 = 1; s.w2 = 3; s.stage = 0; s.n = 0; s.hist = []; BP_fwd(s); };
const BP_step = s => {
  if (s.stage < 1) { BP_fwd(s); s.hist = [s.E]; }
  BP_bwd(s);
  s.w1 -= BP_ETA * s.g1;
  s.w2 -= BP_ETA * s.g2;
  BP_fwd(s);
  s.n++;
  s.hist.push(s.E);
  if (s.hist.length > 6) s.hist.shift();
  s.stage = 1; // new weights: the old blame no longer fits, run backward again
};

const BP_W_NET = h => plane(h, {
  x: [0, 10], y: [0, 5], ratio: 0.62,
  state: (() => { const s = {}; BP_reset(s); return s; })(),
  buttons: [
    { label: 'رو به جلو', on: s => { BP_fwd(s); if (s.stage < 1) { s.stage = 1; s.hist = [s.E]; } }, active: s => s.stage === 1 },
    { label: 'رو به عقب', on: s => { if (s.stage < 1) { BP_fwd(s); s.hist = [s.E]; } BP_bwd(s); s.stage = 2; }, active: s => s.stage === 2 },
    { label: 'یک قدم', on: BP_step },
    { label: 'از نو', on: BP_reset },
  ],
  draw: (g, s) => {
    const xs = [1, 3.7, 6.3, 9], Ly = 3, R = 20, ctx = g.ctx;
    const names = ['x', 'h', 'ŷ', 'E'];
    const vals = [BP_X, s.h, s.yh, s.E];
    const show = (v, i) => (i === 3 ? BP_fa4(v) : fa(v));
    const blame = [null, s.gh, s.gy, 1];
    const cols = ['blue', 'orange', 'orange', 'red'];
    // arrows between the circles, with what each link does
    const links = ['×w₁، ReLU', '×w₂', '(ŷ − y)²'];
    for (let i = 0; i < 3; i++) {
      g.arrow(xs[i] + 0.62, Ly, xs[i + 1] - 0.62, Ly, 'muted', 2);
      g.text((xs[i] + xs[i + 1]) / 2, Ly, links[i], i < 2 ? 'orange' : 'muted', 'center', -14);
    }
    // backward arrows (red) once the backward pass ran
    if (s.stage === 2) for (let i = 2; i >= 0; i--) g.arrow(xs[i + 1] - 0.5, Ly - 0.75, xs[i] + 0.5, Ly - 0.75, 'red', 2);
    // circles
    xs.forEach((x, i) => {
      ctx.beginPath(); ctx.arc(g.X(x), g.Y(Ly), R, 0, 7);
      ctx.fillStyle = g.css('card'); ctx.fill();
      ctx.lineWidth = 3; ctx.strokeStyle = g.css(cols[i]); ctx.setLineDash([]); ctx.stroke();
      g.text(x, Ly, names[i], 'ink', 'center', 0);
      if (s.stage >= 1 || i === 0) g.text(x, Ly, show(vals[i], i), 'blue', 'center', -36);
      if (s.stage === 2 && blame[i] !== null) g.text(x, Ly, fa(blame[i]), 'red', 'center', 50);
    });
    // the two knobs and their gradients
    [[0, 'w₁', s.w1, s.g1], [1, 'w₂', s.w2, s.g2]].forEach(([i, nm, w, gr]) => {
      const mx = (xs[i] + xs[i + 1]) / 2;
      g.text(mx, 1.05, `${nm} = ${fa(w)}`, 'orange', 'center', 0);
      if (s.stage === 2) g.text(mx, 0.4, `گرادیان: ${fa(gr)}`, 'red', 'center', 0);
    });
    g.text(9, 1.05, `y = ${fa(BP_Y)}`, 'muted', 'center', 0);
  },
  read: s => {
    const F = BP_t4, d = BP_d, eq = s.n ? String.raw`\approx` : '=';
    const hist = s.hist.length ? `<br>خطا تا این‌جا: ${s.hist.map(BP_fa4).join(' ← ')}${s.n ? ` (${fa(s.n)} قدم)` : ''}` : '';
    if (s.stage === 0) return `اول «رو به جلو» را بزنید. جوابِ درست ${E('y = 10')} است.`;
    const f = `<b style="color:var(--blue)">رو به جلو:</b> ${E(String.raw`h = \text{ReLU}(${F(s.w1)} \times 2) ${eq} ${F(s.h)}`)}، ${E(String.raw`\hat{y} = ${F(s.w2)} \times ${F(s.h)} ${eq} ${F(s.yh)}`)}، ${E(String.raw`E = (${F(s.yh)} - 10)^2 ${eq} ${F(s.E)}`)}`;
    if (s.stage === 1) return f + '<br>حدس با جوابِ درست فاصله دارد. حالا «رو به عقب» را بزنید تا تقصیر پخش شود.' + hist;
    return f + `<br><b style="color:var(--red)">رو به عقب:</b> ${E(String.raw`${d('E', String.raw`\hat{y}`)} = 2(\hat{y} - y) ${eq} ${F(s.gy)}`)}<br>` +
      `${E(String.raw`${d('E', 'w_2')} = ${F(s.gy)} \times h ${eq} ${F(s.g2)}`)}، ${E(String.raw`${d('E', 'h')} = ${F(s.gy)} \times w_2 ${eq} ${F(s.gh)}`)}<br>` +
      `${E(String.raw`${d('E', 'w_1')} = ${F(s.gh)} \times ${s.z > 0 ? 1 : 0} \times x ${eq} ${F(s.g1)}`)}` +
      '<br>گرادیانِ منفی یعنی: آن پیچ را بزرگ‌تر کنیم، خطا کم می‌شود. «یک قدم» همین کار را می‌کند.' + hist;
  },
});

// picture 2: n sigmoid layers in a row. Each one passes back at most 0.25 of the blame
// (sigmoid slope σ(z)(1 − σ(z)) is largest at z = 0: 0.5 × 0.5 = 0.25). Weights taken as 1.
// The layer k (1 = first, n = next to the error) gets 0.25^(n − k + 1); layer 1 gets 1 / 4^n.
// With ReLU (slope 1 while the neuron is on) every layer gets 1.
const BP_W_VANISH = h => plane(h, {
  x: [0, 11], y: [-0.22, 1.35], ratio: 0.7,
  state: { n: 5, relu: 0 },
  sliders: [{ key: 'n', label: 'تعداد لایه‌ها (n):', min: 1, max: 10, step: 1 }],
  buttons: [
    { label: 'سیگموید', on: s => { s.relu = 0; }, active: s => !s.relu },
    { label: 'ReLU', on: s => { s.relu = 1; }, active: s => !!s.relu },
  ],
  draw: (g, s) => {
    g.line(0.3, 0, 10.7, 0, 'line', 2);
    g.line(0.3, 1, 10.7, 1, 'muted', 1, [4, 4]);
    for (let k = 1; k <= s.n; k++) {
      const v = s.relu ? 1 : 0.25 ** (s.n - k + 1);
      g.rect(k - 0.33, 0, k + 0.33, v, 'green', 0.85);
      g.text(k, v, v >= 0.005 ? fa(v) : '≈۰', 'green', 'center', -9);
      g.text(k, 0, fa(k), 'muted', 'center', 12);
    }
    g.arrow(s.n + 0.4, 1.22, 0.6, 1.22, 'red', 2);
    g.text(Math.max(1.6, (s.n + 1) / 2), 1.22, 'جهتِ پس‌انتشار', 'red', 'center', -11);
  },
  read: s => {
    if (s.relu) return `ReLU: هر لایه تقصیر را در <b>۱</b> ضرب می‌کند (وقتی نورون روشن است، یعنی عددش مثبت).<br>${E(String.raw`1 \times 1 \times \dots \times 1 = 1`)}: لایه‌ی ۱ هم <b style="color:var(--green)">تمامِ</b> پیام را می‌گیرد.`;
    const p = 4 ** s.n;
    return `سیگموید: هر لایه تقصیر را حداکثر در <b>۰٫۲۵</b> ضرب می‌کند.<br>لایه‌ی ۱ (اولِ شبکه) فقط این سهم را می‌گیرد: ${E(String.raw`0.25^{${s.n}} = \frac{1}{${p}}`)}، یعنی یک ${BP_int(p)}‌اُم.` +
      (s.n >= 8 ? '<br>یعنی اولِ شبکه تقریباً هیچ پیامی نمی‌گیرد و یاد نمی‌گیرد.' : '');
  },
});

lesson({
  id: 'backpropagation', node: 'backpropagation', title: 'پس‌انتشار خطا', en: 'Backpropagation',
  parts: [
    { name: 'چرا و یعنی چه؟', cards: [
      { t: 'story', title: `پس‌انتشار خطا ${EN('Backpropagation')}`,
        body: `<p>یک شبکه‌ی عصبی میلیون‌ها پیچ دارد؛ همان وزن‌ها ${EN('Weight')}. برای گرادیان کاهشی، برای <b>هر</b> پیچ باید بدانیم: «اگر این پیچ را کمی بچرخانم، خطای آخر چقدر عوض می‌شود؟»</p>
               <p>راهِ ساده: پیچ‌ها را یکی‌یکی تکان بدهیم و هر بار کلِ شبکه را اجرا کنیم. یک میلیون پیچ یعنی یک میلیون اجرا، برای <b>یک</b> قدم!</p>
               <div class="key">مشکل: شیبِ خطا را برای همه‌ی پیچ‌ها، با هم و سریع، چطور حساب کنیم؟</div>`,
        who: 'لینایما (Linnainmaa) ۱۹۷۰ مشتق‌گیریِ معکوس را نوشت، وربوس (Werbos) ۱۹۷۴ برای شبکه‌ها پیشنهادش کرد، و روملهارت، هینتون و ویلیامز ۱۹۸۶ مشهورش کردند.' },
      { t: 'text', title: 'معنی ساده',
        body: `<p>کار در دو رفت انجام می‌شود:</p>
               <p><b style="color:var(--blue)">رفتِ رو به جلو</b> ${EN('Forward Pass')}: از ورودی تا آخر، عددها را حساب کن؛ حدسِ مدل و خطا. عددهای وسطِ راه را <b>نگه دار</b>.</p>
               <p><b style="color:var(--red)">رفتِ رو به عقب</b> ${EN('Backward Pass')}: از خطا شروع کن و «تقصیر» را عقب بفرست. در هر حلقه، تقصیرِ رسیده را در شیبِ همان حلقه ضرب کن (قاعده‌ی زنجیره‌ای).</p>
               <div class="key">تقصیرِ هر پیچ = گرادیانِ خطا نسبت به آن پیچ. یک رفت و یک برگشت، و همه‌ی تقصیرها معلوم است.</div>` },
      { t: 'play', w: BP_W_NET, title: 'یک شبکه‌ی خیلی کوچک',
        body: `${E('x = 2')} وارد می‌شود، در <b style="color:var(--orange)">${E('w_1')}</b> ضرب و از ReLU رد می‌شود: ${E('h')}. بعد در <b style="color:var(--orange)">${E('w_2')}</b> ضرب می‌شود: حدسِ ${E(String.raw`\hat{y}`)}. جوابِ درست ${E('y = 10')} و خطا ${E(String.raw`E = (\hat{y} - y)^2`)}. عددهای <b style="color:var(--blue)">آبی</b> = رفتِ جلو، <b style="color:var(--red)">قرمز</b> = تقصیر.`,
        look: [
          '«رو به جلو» را بزنید ← بالای دایره‌ها h = ۲، حدس = ۶ و خطا = ۱۶ می‌آید.',
          '«رو به عقب» را بزنید ← تقصیرها از راست به چپ: ۸− زیرِ حدس، ۲۴− زیرِ h؛ گرادیانِ w₂ می‌شود ۱۶− و گرادیانِ w₁ می‌شود ۴۸−.',
          '«یک قدم» را بزنید ← w₁ = ۱٫۴۸ و w₂ = ۳٫۱۶ می‌شود و خطا از ۱۶ به ۰٫۴۱۷۸ می‌افتد.',
          'یک بارِ دیگر «یک قدم» ← حدس ۹٫۹۹ و خطا حدودِ ۰٫۰۰۰۱.',
        ],
        see: 'یک رفت و یک برگشت گرادیانِ هر دو پیچ را داد، بی‌آن‌که پیچی را جدا تکان بدهیم. تقصیرِ ۲۴− که برای h حساب شد، دوباره برای w₁ به کار رفت. با همین چرخه (جلو، عقب، قدم) شبکه در دو قدم تقریباً بی‌خطا شد.' },
      { t: 'life', title: 'تقصیر را از آخر به اول پخش کن', items: [
        { h: 'شکایتِ رستوران', d: 'غذا سرد رسید. مدیر از آخر عقب می‌رود: گارسون چقدر دیر آورد؟ آشپز؟ تأمین‌کننده‌ی مواد؟ سهمِ هرکس را از روی سهمِ نفرِ بعدی‌اش پیدا می‌کند.' },
        { h: 'خط تولید کارخانه', d: 'قطعه‌ای معیوب درآمد. بازرس از ایستگاهِ آخر، ایستگاه‌به‌ایستگاه عقب می‌رود تا سهمِ هر ایستگاه را بفهمد؛ لازم نیست برای هر ایستگاه کلِ خط را از نو راه بیندازد.' },
        { h: 'دوی امدادی', d: 'تیم ۴ ثانیه از رکورد عقب ماند. مربی فیلم را از آخر نگاه می‌کند و این ۴ ثانیه را بین دونده‌ها و تحویلِ چوب تقسیم می‌کند. هر دونده می‌فهمد روی چه کار کند.' },
      ] },
      { t: 'sort', title: 'درست یا نادرست؟', yes: 'درست', no: 'نادرست', items: [
        { q: 'پس‌انتشار خودش وزن‌ها را عوض می‌کند.', a: false, why: `فقط گرادیان را حساب می‌کند. عوض کردن کارِ قدمِ گرادیان کاهشی است: ${E(String.raw`w_{\text{new}} = w - \eta \times \text{grad}`)}.` },
        { q: 'برای هر وزن، شبکه را یک بارِ جدا اجرا می‌کند.', a: false, why: 'نه؛ همه‌ی وزن‌ها در یک رفت و یک برگشت گرادیانشان را می‌گیرند. همین سریعش می‌کند.' },
        { q: 'رفتِ رو به عقب از عددهای نگه‌داشته‌ی رفتِ رو به جلو استفاده می‌کند.', a: true, why: `مثلاً ${E(String.raw`${BP_d('E', 'w_2')} = ${BP_d('E', String.raw`\hat{y}`)} \times h`)}؛ عددِ h را از رفتِ رو به جلو داریم.` },
        { q: 'اگر شیبِ یک حلقه صفر باشد، پیچ‌های قبل از آن (در همان مسیر) گرادیانِ صفر می‌گیرند.', a: true, why: 'تقصیر ضرب در صفر می‌شود و دیگر عقب‌تر نمی‌رسد؛ مثل ReLU وقتی عددش منفی است.' },
        { q: 'پس‌انتشار فقط وزن‌های لایه‌ی آخر را حساب می‌کند.', a: false, why: 'تقصیر تا اولِ شبکه عقب می‌رود؛ هر وزن، هر جا باشد، گرادیانش را می‌گیرد.' },
      ] },
      { t: 'quiz', q: `در تصویر، گرادیانِ ${E('w_2')} عددِ ۱۶− شد. علامتِ منفی یعنی چه؟`,
        options: [`باید ${E('w_2')} را کوچک‌تر کنیم`, `${E('w_2')} در خطا هیچ تقصیری ندارد`, `با بزرگ‌تر شدنِ ${E('w_2')} خطا کم می‌شود`], answer: 2,
        why: `گرادیانِ منفی یعنی با زیاد شدنِ ${E('w_2')}، خطا پایین می‌آید؛ پس قدم ${E('w_2')} را بزرگ می‌کند: ${E(String.raw`3 - 0.01 \times (-16) = 3.16`)}. «کوچک‌تر کنیم» علامت را برعکس خوانده. تقصیرِ صفر یعنی گرادیانِ صفر، نه منفی.` },
    ] },
    { name: 'فرمول', cards: [
      { t: 'formula', f: String.raw`\Cg{\frac{\partial E}{\partial w_1}} = \Cr{\frac{\partial E}{\partial \hat{y}}} \cdot \Co{\frac{\partial \hat{y}}{\partial h}} \cdot \Cb{\frac{\partial h}{\partial w_1}}`, title: `پس‌انتشار با قاعده‌ی زنجیره‌ای ${EN('Chain Rule')}`,
        intro: `<p>شبکه‌ی تصویر: ${E(String.raw`h = \text{ReLU}(w_1x)`)}، ${E(String.raw`\hat{y} = w_2h`)}، ${E(String.raw`E = (\hat{y} - y)^2`)}. E خطا، ${E(String.raw`\hat{y}`)} حدسِ مدل، h عددِ نورونِ وسط، ${E('w_1')} و ${E('w_2')} دو پیچ. ${E(String.raw`\partial`)} همان شیبِ جزئی از درسِ گرادیان است.</p>`,
        toks: [{ s: BP_d('E', 'w_1'), c: 'green', l: 'تقصیرِ w₁ (گرادیانش)' }, { s: '=' },
               { s: BP_d('E', String.raw`\hat{y}`), c: 'red', l: 'خطا نسبت به حدس: 2(ŷ − y)' }, { s: String.raw`\cdot` },
               { s: BP_d(String.raw`\hat{y}`, 'h'), c: 'orange', l: 'حدس نسبت به h: همان w₂' }, { s: String.raw`\cdot` },
               { s: BP_d('h', 'w_1'), c: 'blue', l: 'h نسبت به w₁: x (اگر ReLU روشن)' }],
        read: 'هر حلقه‌ی زنجیره یک ضرب. از راست به چپ بخوانید، همان‌طور که تقصیر عقب می‌رود.',
        note: `<p>برای ${E('w_2')} زنجیره کوتاه‌تر است: ${E(String.raw`${BP_d('E', 'w_2')} = ${BP_d('E', String.raw`\hat{y}`)} \cdot ${BP_d(String.raw`\hat{y}`, 'w_2')} = ${BP_d('E', String.raw`\hat{y}`)} \cdot h`)}.</p><div class="key">${E(BP_d('E', String.raw`\hat{y}`))} در هر دو هست: <b>یک بار</b> حساب، دو بار استفاده. راز سرعتِ پس‌انتشار همین است.</div>` },
      { t: 'example', title: 'با عدد: یک رفت و یک برگشت',
        intro: `<p>همان شبکه‌ی تصویر: ${E('x = 2')}، جوابِ درست ${E('y = 10')}، پیچ‌ها ${E('w_1 = 1')} و ${E('w_2 = 3')}.</p>`,
        steps: [
          `<b style="color:var(--blue)">جلو:</b> ${E(String.raw`h = \text{ReLU}(1 \times 2) = 2`)}، ${E(String.raw`\hat{y} = 3 \times 2 = 6`)}`,
          `<b style="color:var(--blue)">خطا:</b> ${E('E = (6 - 10)^2 = (-4)^2 = 16')}`,
          `<b style="color:var(--red)">عقب، حلقه‌ی آخر:</b> ${E(String.raw`${BP_d('E', String.raw`\hat{y}`)} = 2(6 - 10) = -8`)}`,
          `<b style="color:var(--red)">برای w₂:</b> ${E(String.raw`-8 \times h = -8 \times 2 = -16`)}`,
          `<b style="color:var(--red)">برای h:</b> ${E(String.raw`-8 \times w_2 = -8 \times 3 = -24`)}`,
          `<b style="color:var(--red)">برای w₁:</b> ${E(String.raw`-24 \times 1 \times x = -24 \times 2 = -48`)} (آن ۱ شیبِ ReLU است، چون h مثبت است)`,
        ],
        result: 'گرادیانِ w₁ = ۴۸− و گرادیانِ w₂ = ۱۶−. عددِ ۲۴− را یک بار حساب کردیم و برای w₁ دوباره به کار بردیم.' },
      { t: 'text', title: 'با یک تکانِ کوچک امتحان کنیم',
        body: `<p>${E('w_1')} را از ۱ به ۱٫۰۰۱ ببریم و همه را از نو حساب کنیم:</p>
               <p class="read">${E(String.raw`h = 2.002,\ \hat{y} = 6.006,\ E = (-3.994)^2 = 15.952036`)}<br>${E(String.raw`\frac{15.952036 - 16}{0.001} = -47.964 \approx -48`)}</p>
               <p>برای ${E('w_2')} (۳ به ۳٫۰۰۱): ${E('E = (-3.998)^2 = 15.984004')} ← ${E(String.raw`-15.996 \approx -16`)}.</p>
               <p>هر دو درست بود. ولی برای هر تکان، یک اجرای کامل لازم شد. پس‌انتشار هر دو را از <b>یک</b> برگشت داد.</p>
               <p>قدم با ${E(String.raw`\eta = 0.01`)}: ${E(String.raw`w_1 = 1 - 0.01 \times (-48) = 1.48`)}، ${E(String.raw`w_2 = 3 - 0.01 \times (-16) = 3.16`)}. خطا از ۱۶ به حدودِ ۰٫۴۲ رسید.</p>` },
      { t: 'play', w: BP_W_VANISH, title: 'تقصیر در راهِ برگشت آب می‌رود',
        body: `n لایه‌ی سیگموید پشتِ سرِ هم (وزن‌ها ۱). شیبِ سیگموید ${E(String.raw`\sigma(z)(1 - \sigma(z))`)} است و بیشترینش ${E(String.raw`0.5 \times 0.5 = 0.25`)}. میله‌ی <b style="color:var(--green)">سبز</b> = تقصیری که به هر لایه می‌رسد؛ لایه‌ی ۱ اولِ شبکه است. پیکانِ <b style="color:var(--red)">قرمز</b> = جهتِ برگشت.`,
        look: [
          'با n = ۵ شروع کنید ← لایه‌ی ۵ (کنارِ خطا) ۰٫۲۵ می‌گیرد، لایه‌ی ۴ حدودِ ۰٫۰۶، لایه‌ی ۳ حدودِ ۰٫۰۲ و دو لایه‌ی اول تقریباً صفر.',
          'n را روی ۱۰ بگذارید ← لایه‌ی ۱ فقط یک ۱٬۰۴۸٬۵۷۶‌اُم از تقصیر را می‌گیرد.',
          '«ReLU» را بزنید ← همه‌ی میله‌ها ۱ می‌شوند، با هر n.',
        ],
        see: 'چون تقصیرها در هر حلقه ضرب می‌شوند، شیب‌های کوچک پشتِ هم پیام را محو می‌کنند و لایه‌های اول تقریباً هیچ یاد نمی‌گیرند: «محو شدنِ گرادیان». ReLU با شیبِ ۱ این مشکل را ندارد؛ برای همین شبکه‌های عمیقِ امروز از آن استفاده می‌کنند.' },
      { t: 'rules', title: 'سه قانون مهم', items: [
        { r: 'رفتِ رو به عقب تقریباً <b>هم‌اندازه</b>‌ی رفتِ رو به جلو وقت می‌برد (معمولاً حدود دو برابر)، نه میلیون‌ها برابر.',
          why: 'چون چیزی را از نو حساب نمی‌کند: عددهای نگه‌داشته‌ی رفتِ جلو (مثل h) و تقصیرِ حلقه‌ی بعدی (مثل ۸−) را دوباره به کار می‌برد.' },
        { r: 'گرادیان‌ها در طولِ مسیر <b>ضرب</b> می‌شوند.',
          why: `برای همین، شیب‌های کمتر از ۱ پشت سر هم، تقصیر را محو می‌کنند (${E('0.25^{10}')} حدود یک‌میلیونیم) و بیشتر از ۱، منفجرش می‌کنند (${E(String.raw`1.5^{10} \approx 58`)}).` },
        { r: 'همه‌ی وزن‌ها در <b>یک</b> رفت و برگشت، گرادیانِ خودشان را می‌گیرند.',
          why: 'چون تقصیرِ هر نقطه یک بار حساب می‌شود و همه‌ی وزن‌های قبل از آن شریکش می‌شوند. تکان دادنِ یکی‌یکی، برای یک میلیون وزن یک میلیون اجرا می‌خواست.' },
      ] },
      { t: 'ai', title: 'پس‌انتشار در هوش مصنوعی',
        body: `<p>در PyTorch کسی این ضرب‌ها را دستی نمی‌نویسد. کتابخانه رفتِ جلو را ضبط می‌کند و با یک دستور (${N('loss.backward()')}) همه‌ی گرادیان‌ها را می‌دهد: <b>مشتق‌گیریِ خودکار</b> ${EN('Autograd')}.</p>
               <p>آموزشِ مدل‌های بزرگ مثل ChatGPT همین چرخه است: رو به جلو، رو به عقب، یک قدم؛ با شمارِ بسیار زیادی قدمِ کوچک، برای میلیاردها پیچ.</p>
               <p>سه چاره‌ی محو شدن: <b>ReLU</b> شیبِ ۱ دارد و تقصیر را کوچک نمی‌کند. <b>مقداردهیِ اولیه‌ی دقیق</b> ${EN('Initialization')} وزن‌های اولیه را نه خیلی کوچک می‌گیرد نه بزرگ. <b>اتصالِ میان‌بر</b> ${EN('Residual Connection')} برای تقصیر راهِ مستقیمی دورِ لایه‌ها باز می‌کند.</p>` },
      { t: 'quiz', q: `همان شبکه با ${E('x = 3')}، ${E('w_1 = 1')}، ${E('w_2 = 2')} و ${E('y = 4')} (ReLU روشن). ${E(BP_d('E', 'w_1'))} چقدر است؟`,
        options: ['۱۲', '۲۴', '۸'], answer: 1,
        why: `جلو: ${E('h = 3')}، ${E(String.raw`\hat{y} = 6`)}. عقب: ${E(String.raw`${BP_d('E', String.raw`\hat{y}`)} = 2 \times (6 - 4) = 4`)}، بعد ضرب در ${E('w_2 = 2')} و در ${E('x = 3')}: ${E(String.raw`4 \times 2 \times 3 = 24`)}. عدد ۱۲ یعنی حلقه‌ی وسط (${E('w_2')}) جا افتاده؛ این ${E(BP_d('E', 'w_2'))} است (${E(String.raw`4 \times h`)}). عدد ۸ یعنی حلقه‌ی آخر (x) جا افتاده.` },
      { t: 'text', title: 'یک سؤال برای بعد',
        body: `<p>در تصویرِ دوم، با ۱۰ لایه‌ی سیگموید، لایه‌ی اول فقط ${E(String.raw`\frac{1}{1048576}`)} از تقصیر را می‌گرفت.</p>
               <div class="key">چرا شبکه‌های عمیقِ قدیمی لایه‌های اولشان یاد نمی‌گرفت، و امروز چطور جلویش را می‌گیرند؟</div>
               <p>این سؤالِ معروفِ مصاحبه است: <b>محو شدن گرادیان</b> ${EN('Vanishing Gradient')}. در مأموریتِ مصاحبه با همین ابزارها جوابش را می‌سازیم.</p>` },
    ] },
  ],
  sheet: {
    one: 'پس‌انتشار خطا = رو به جلو خطا را حساب کن، بعد از خطا رو به عقب برو و در هر حلقه تقصیر را در شیبِ آن حلقه ضرب کن (قاعده‌ی زنجیره‌ای). ساخته شد چون تکان دادنِ میلیون‌ها پیچ یکی‌یکی خیلی کند است؛ این روش همه‌ی گرادیان‌ها را در یک برگشت می‌دهد.',
    f: String.raw`${BP_d('E', 'w_1')} = ${BP_d('E', String.raw`\hat{y}`)} \cdot ${BP_d(String.raw`\hat{y}`, 'h')} \cdot ${BP_d('h', 'w_1')} \qquad ${BP_d('E', 'w_2')} = ${BP_d('E', String.raw`\hat{y}`)} \cdot h`,
    rules: ['رفتِ جلو: عددها و خطا (و نگه داشتنِ عددهای وسط). رفتِ عقب: تقصیرها = گرادیان‌ها.', 'برگشت تقریباً هم‌اندازه‌ی رفت وقت می‌برد، چون عددها و تقصیرها دوباره به کار می‌روند.', 'گرادیان‌ها در مسیر ضرب می‌شوند: شیب‌های کوچک = محو شدن، بزرگ = انفجار.', 'پس‌انتشار فقط گرادیان می‌دهد؛ عوض کردنِ وزن کارِ قدمِ گرادیان کاهشی است.'],
    use: 'آموزشِ هر شبکه‌ی عصبی، تا ChatGPT: رو به جلو، رو به عقب، قدم. PyTorch و TensorFlow آن را خودکار انجام می‌دهند (Autograd). ReLU، مقداردهیِ اولیه‌ی دقیق و اتصالِ میان‌بر جلوی محو شدنِ گرادیان را می‌گیرند.',
    mistake: 'یک حلقه‌ی زنجیره را جا بیندازیم (مثلاً ضرب در w₂ یا x)، یا خیال کنیم پس‌انتشار خودش وزن‌ها را عوض می‌کند.',
  },
});
