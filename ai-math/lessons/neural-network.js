// ---------- Deep Learning: Neural Network ----------
// (names start with NN_ because all lesson files share one global scope)

const NN_sig = z => 1 / (1 + Math.exp(-z));
const NN_relu = z => Math.max(0, z);
const NN_clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const NN_SPAN = (c, t) => `<span style="color:var(--${c})">${t}</span>`;
// a signed term for a formula: "+ 2" / "− 1.5"
const NN_sg = n => (n < 0 ? '− ' : '+ ') + fa(Math.abs(n));

// the four corners (x₁, x₂) and the answer each pattern wants there
const NN_CORNERS = [[0, 0], [1, 0], [0, 1], [1, 1]];
const NN_DATA = { and: [0, 0, 0, 1], or: [0, 1, 1, 1], xor: [0, 1, 1, 0] };
const NN_NAMES = { and: 'AND', or: 'OR', xor: 'XOR' };

// color the plane: orange, stronger where the output f(x₁, x₂) is closer to 1
const NN_shade = (g, f) => {
  const c = g.ctx, st = 0.1;
  c.fillStyle = g.css('orange');
  for (let i = 0; i < 22; i++) for (let j = 0; j < 22; j++) {
    const x = -0.6 + i * st, y = -0.6 + j * st;
    c.globalAlpha = NN_clamp(f(x + st / 2, y + st / 2), 0, 1) * 0.55;
    c.fillRect(g.X(x), g.Y(y + st), g.X(x + st) - g.X(x) + 0.6, g.Y(y) - g.Y(y + st) + 0.6);
  }
  c.globalAlpha = 1;
};
// the straight line w₁x₁ + w₂x₂ + b = 0
const NN_zline = (g, w1, w2, b, color, w, dash) => {
  if (Math.abs(w2) > 1e-9) g.line(-1, -(b - w1) / w2, 2, -(b + 2 * w1) / w2, color, w, dash);
  else if (Math.abs(w1) > 1e-9) g.line(-b / w1, -1, -b / w1, 2, color, w, dash);
};
// the four points: answer 1 = filled, answer 0 = hollow; a red ring = the model got it wrong
const NN_pts = (g, lab, pred) => NN_CORNERS.forEach(([x, y], i) => {
  if (pred[i] !== lab[i]) { const c = g.ctx; c.strokeStyle = g.css('red'); c.lineWidth = 3; c.setLineDash([]); c.beginPath(); c.arc(g.X(x), g.Y(y), 18, 0, 7); c.stroke(); }
  lab[i] ? g.dot(x, y, 'ink', 9) : g.knob(x, y, 'ink');
});
const NN_right = (lab, pred) => lab.filter((v, i) => v === pred[i]).length;

// ---- Picture 1: one neuron, σ(w₁x₁ + w₂x₂ + b); its border is always a straight line ----
const NN_W_ONE = h => plane(h, {
  x: [-0.6, 1.6], y: [-0.6, 1.6], equal: true, labels: true, names: ['x₁', 'x₂'],
  state: { w1: 1, w2: 1, b: -1.5, d: 'and' },
  sliders: [{ key: 'w1', label: 'w₁ (وزنِ ۱):', min: -3, max: 3, step: 0.5 }, { key: 'w2', label: 'w₂ (وزنِ ۲):', min: -3, max: 3, step: 0.5 },
            { key: 'b', label: 'b (عدد ثابت):', min: -4, max: 4, step: 0.5 }],
  buttons: ['and', 'or', 'xor'].map(k => ({ label: `داده‌ی ${NN_NAMES[k]}`, on: s => { s.d = k; }, active: s => s.d === k })),
  draw: (g, s) => {
    g.grid();
    NN_shade(g, (x, y) => NN_sig(s.w1 * x + s.w2 * y + s.b));
    NN_zline(g, s.w1, s.w2, s.b, 'orange', 3);
    NN_pts(g, NN_DATA[s.d], NN_CORNERS.map(([x, y]) => (s.w1 * x + s.w2 * y + s.b >= 0 ? 1 : 0)));
  },
  read: s => {
    const lab = NN_DATA[s.d], ps = NN_CORNERS.map(([x, y]) => NN_sig(s.w1 * x + s.w2 * y + s.b));
    const n = NN_right(lab, ps.map(p => (p >= 0.5 ? 1 : 0)));
    const list = NN_CORNERS.map(([x, y], i) => `(${fa(x)}، ${fa(y)}) ← ${fa(ps[i])}`).join(' &nbsp; ');
    return `${E(`a = σ(${fa(s.w1)}·x₁ ${NN_sg(s.w2)}·x₂ ${NN_sg(s.b)})`)}<br>${list}<br>` +
      `داده‌ی ${NN_NAMES[s.d]}: درست = <b style="color:var(--green)">${fa(n)} از ۴</b> (خروجیِ ۰٫۵ یا بیشتر یعنی «۱»)` +
      (s.d === 'xor' && n < 4 ? '<br>هر خطی را امتحان کنید: برای XOR بیشتر از <b>۳ از ۴</b> نمی‌شود. یک خطِ صاف این دو جفت را از هم جدا نمی‌کند.' : '') +
      (!s.w1 && !s.w2 ? '<br>هر دو وزن صفر است: ورودی‌ها هیچ اثری ندارند و همه‌جا یک رنگ است.' : '');
  },
});

// ---- Picture 2: a 2–2–1 network with ReLU in the hidden layer ----
const NN_GOOD = { W: [1, 1, 1, 1], b: [0, -1], v: [1, -2], c: 0 };
const NN_net = (s, x1, x2) => {
  const f = s.relu ? NN_relu : z => z;
  const h1 = f(s.W[0] * x1 + s.W[1] * x2 + s.b[0]), h2 = f(s.W[2] * x1 + s.W[3] * x2 + s.b[1]);
  return s.v[0] * h1 + s.v[1] * h2 + s.c;
};
const NN_isGood = s => JSON.stringify([s.W, s.b, s.v, s.c]) === JSON.stringify([NN_GOOD.W, NN_GOOD.b, NN_GOOD.v, NN_GOOD.c]);
const NN_rnd = () => Math.round((Math.random() * 4 - 2) * 2) / 2 + 0;

const NN_W_NET = h => plane(h, {
  x: [-0.6, 1.6], y: [-0.6, 1.6], equal: true, labels: true, names: ['x₁', 'x₂'],
  state: { W: [1, 1, 1, 1], b: [0, -1], v: [1, -2], c: 0, relu: true },
  buttons: [
    { label: 'وزن‌های حل‌کننده', on: s => { s.W = [...NN_GOOD.W]; s.b = [...NN_GOOD.b]; s.v = [...NN_GOOD.v]; s.c = 0; }, active: s => NN_isGood(s) },
    { label: 'وزن‌های تصادفی', on: s => { s.W = [0, 0, 0, 0].map(NN_rnd); s.b = [0, 0].map(NN_rnd); s.v = [0, 0].map(NN_rnd); s.c = NN_rnd(); } },
    { label: 'خمیدگی (ReLU)', on: s => { s.relu = !s.relu; }, active: s => s.relu },
  ],
  draw: (g, s) => {
    g.grid();
    NN_shade(g, (x, y) => NN_net(s, x, y));
    NN_zline(g, s.W[0], s.W[1], s.b[0], 'muted', 2, [6, 5]);
    NN_zline(g, s.W[2], s.W[3], s.b[1], 'muted', 2, [6, 5]);
    NN_pts(g, NN_DATA.xor, NN_CORNERS.map(([x, y]) => (NN_net(s, x, y) >= 0.5 ? 1 : 0)));
  },
  read: s => {
    const ys = NN_CORNERS.map(([x, y]) => NN_net(s, x, y)), n = NN_right(NN_DATA.xor, ys.map(y => (y >= 0.5 ? 1 : 0)));
    const list = NN_CORNERS.map(([x, y], i) => `(${fa(x)}، ${fa(y)}) ← ${fa(ys[i])}`).join(' &nbsp; ');
    const note = !s.relu ? 'بدونِ خمیدگی، کلِ شبکه فقط یک <b>خطِ صاف</b> است؛ دو لایه هم کمکی نکرد.'
      : n === 4 ? (NN_isGood(s) ? 'هر ۴ درست! دو نورونِ پنهان صفحه را دو جا تا کرده‌اند و یک نوار ساخته‌اند.' : 'این بار شانسی هر ۴ درست شد!')
      : 'وزن‌های بد. پیدا کردنِ وزن‌های خوب کارِ <b>آموزش</b> است: درسِ بعد.';
    return `لایه‌ی پنهان: ${E(`W = [[${fa(s.W[0])}, ${fa(s.W[1])}], [${fa(s.W[2])}, ${fa(s.W[3])}]], b = [${fa(s.b[0])}, ${fa(s.b[1])}]`)}<br>` +
      `خروجی: ${E(`y = ${fa(s.v[0])}·h₁ ${NN_sg(s.v[1])}·h₂ ${NN_sg(s.c)}`)}<br>${list}<br>` +
      `داده‌ی XOR: درست = <b style="color:var(--green)">${fa(n)} از ۴</b><br>${note}`;
  },
});

const NN_TD = 'style="padding:2px 9px"';
const NN_TABLE = `<table dir="ltr" style="border-collapse:collapse;margin:6px auto;text-align:center">
  <tr><td ${NN_TD}><b>x₁, x₂</b></td><td ${NN_TD}><b>h₁</b></td><td ${NN_TD}><b>h₂</b></td><td ${NN_TD}><b>y = h₁ − 2h₂</b></td></tr>
  <tr><td ${NN_TD} class="eq">0, 0</td><td ${NN_TD}>0</td><td ${NN_TD}>ReLU(−1) = 0</td><td ${NN_TD} style="color:var(--green)">0</td></tr>
  <tr><td ${NN_TD} class="eq">1, 0</td><td ${NN_TD}>1</td><td ${NN_TD}>ReLU(0) = 0</td><td ${NN_TD} style="color:var(--green)">1</td></tr>
  <tr><td ${NN_TD} class="eq">0, 1</td><td ${NN_TD}>1</td><td ${NN_TD}>ReLU(0) = 0</td><td ${NN_TD} style="color:var(--green)">1</td></tr>
  <tr><td ${NN_TD} class="eq">1, 1</td><td ${NN_TD}>2</td><td ${NN_TD}>ReLU(1) = 1</td><td ${NN_TD} style="color:var(--green)">2 − 2 = 0</td></tr></table>`;

lesson({
  id: 'neural-network', node: 'neural-network', title: 'شبکه عصبی', en: 'Neural Network',
  parts: [
    { name: 'چرا و یعنی چه؟', cards: [
      { t: 'story', title: `وقتی یک خط کافی نیست ${EN('Neural Network')}`,
        body: `
        <p>رگرسیون لجستیک دو دسته را با یک <b>خطِ صاف</b> جدا می‌کند. ولی بعضی الگوها با هیچ خطی جدا نمی‌شوند.</p>
               <p>چراغِ راه‌پله با دو کلید: هر دو خاموش ← خاموش. یکی را بزنید ← روشن. هر دو ← دوباره خاموش. این الگو <b>یای انحصاری</b> ${EN('XOR')} است: «یکی، نه هر دو».</p>
               <div class="key">مشکل: برای الگوهای خمیده، یک خط کم است. باید چند تکه‌ی ساده را روی هم بچینیم.</div>`,
        who: 'روزنبلات (Rosenblatt) در ۱۹۵۸ «پرسپترون» (Perceptron)، یک نورونِ مصنوعی، را ساخت. مینسکی و پاپرت (Minsky، Papert) در ۱۹۶۹ نشان دادند یک لایه XOR را حل نمی‌کند و این به کم‌شدنِ علاقه به شبکه‌ها کمک کرد. در ۱۹۸۶ روملهارت، هینتون و ویلیامز با پس‌انتشار خطا (Backpropagation) آموزشِ شبکه‌های چندلایه را شناساندند.' },
      { t: 'text', title: 'معنی ساده: یک نورون',
        body: `<p><b>نورون</b> ${EN('Neuron')} کوچک‌ترین تکه‌ی شبکه است و دو کار می‌کند:</p>
               <p><b>۱. جمعِ وزن‌دار:</b> هر ورودی را در <b>وزنش</b> ضرب می‌کند، همه را جمع می‌کند و یک <b>عدد ثابت</b> ${EN('Bias')} هم اضافه می‌کند. مثلِ امتیازِ رگرسیون لجستیک.</p>
               <p><b>۲. خم کردن:</b> امتیاز را از یک <b>تابعِ فعال‌سازی</b> ${EN('Activation Function')} رد می‌کند. مثلاً سیگموید (درسِ قبل)، یا ساده‌ترین: <b>ReLU</b>، یعنی «مثبت را نگه دار، منفی را صفر کن».</p>
               <div class="key">نورون = جمعِ وزن‌دارِ ورودی‌ها + عدد ثابت، بعد یک خم.</div>` },
      { t: 'play', w: NN_W_ONE, title: 'یک نورون، یک خط',
        body: 'صفحه با خروجیِ نورون رنگ شده: <b style="color:var(--orange)">نارنجی‌تر</b> = نزدیک‌تر به ۱. نقطه‌ی پُر یعنی جوابِ درست «۱» است، توخالی یعنی «۰»؛ حلقه‌ی <b style="color:var(--red)">قرمز</b> = اشتباه. با لغزنده‌ها AND و OR را حل کنید. بعد «داده‌ی XOR» را بزنید.' },
      { t: 'life', title: 'شبکه‌ی عصبی در زندگی', items: [
        { h: 'شورای کارشناس‌ها', d: 'سه پزشک نظر می‌دهند؛ به نظرِ باتجربه‌تر <b>وزنِ</b> بیشتری می‌دهیم، جمع می‌زنیم و اگر از حدی گذشت، تصمیم می‌گیریم. این یک نورون است.' },
        { h: 'بروم مهمانی؟', d: 'امتیاز = ۲ × (هوا خوب است) + ۳ × (دوستانم می‌آیند) − ۴ × (راه دور است) − ۱. هوا خوب، دوستان می‌آیند، راه نزدیک: ۲ + ۳ − ۰ − ۱ = ۴، مثبت ← می‌روم.' },
        { h: 'شناختنِ یک چهره', d: 'لایه‌ی اول لبه‌ها را می‌بیند، لایه‌ی بعد از لبه‌ها چشم و بینی می‌سازد، لایه‌ی آخر از آن‌ها چهره را. هر لایه روی کارِ قبلی می‌سازد.' },
      ] },
      { t: 'sort', title: 'یک نورونِ تنها از پسش برمی‌آید؟', yes: 'بله', no: 'نه', items: [
        { q: 'AND: «۱» فقط وقتی هر دو ورودی ۱ باشند', a: true, why: 'یک خط، گوشه‌ی (۱، ۱) را از سه گوشه‌ی دیگر جدا می‌کند؛ مثلاً w₁ = w₂ = ۱ و b = −۱٫۵.' },
        { q: 'OR: «۱» وقتی دست‌کم یکی ۱ باشد', a: true, why: 'یک خط، گوشه‌ی (۰، ۰) را جدا می‌کند؛ مثلاً w₁ = w₂ = ۱ و b = −۰٫۵.' },
        { q: 'XOR: «۱» وقتی دقیقاً یکی ۱ باشد', a: false, why: 'جوابِ «۱»ها روی یک قطرِ مربع‌اند و «۰»ها روی قطرِ دیگر. هیچ خطِ صافی این دو قطر را جدا نمی‌کند.' },
        { q: '«۱» برای نقطه‌های داخلِ یک دایره', a: false, why: 'مرزِ یک نورون همیشه یک خطِ صاف است و دایره خمیده است. با چند نورون، چند خط دورِ دایره می‌شود کشید.' },
        { q: '«۱» وقتی x₁ از x₂ بزرگ‌تر باشد', a: true, why: 'مرز همان خطِ x₁ = x₂ است: w₁ = ۱، w₂ = −۱، b = ۰.' },
      ] },
      { t: 'quiz', q: 'نورونی با ReLU: w₁ = ۲، w₂ = −۱، b = ۱. ورودی x₁ = ۱ و x₂ = ۴. خروجی چند است؟',
        options: ['۰', '−۱', '۷'], answer: 0,
        why: 'امتیاز: ۲ × ۱ + (−۱) × ۴ + ۱ = −۱. ReLU منفی را صفر می‌کند، پس خروجی ۰ است. «−۱» یعنی خم فراموش شده. «۷» یعنی منفیِ وزنِ دوم جا افتاده (۲ + ۴ + ۱).' },
    ] },
    { name: 'فرمول', cards: [
      { t: 'formula', title: `فرمولِ یک نورون ${EN('Neuron')}`,
        intro: `<p>ورودی‌ها یک بردارند: ${E('x = [x₁, x₂, …]')}. وزن‌ها هم یک بردار: ${E('w = [w₁, w₂, …]')}. ${E('w · x')} همان <b>ضرب داخلی</b> است: ${E('w₁x₁ + w₂x₂ + …')}</p>`,
        toks: [{ s: 'a', c: 'green', l: 'خروجیِ نورون' }, { s: '=' }, { s: 'f', c: 'ink', l: 'تابعِ فعال‌سازی (خم)' }, { s: '(' },
               { s: 'w', c: 'orange', l: 'وزن‌ها' }, { s: '·' }, { s: 'x', c: 'blue', l: 'ورودی‌ها' }, { s: '+' }, { s: 'b', c: 'orange', l: 'عدد ثابت' }, { s: ')' }],
        read: 'خوانده می‌شود: «a برابر است با f ِ w ضرب داخلی x به‌علاوه‌ی b».',
        note: `<p>دو خمِ معروف:<br>${E('ReLU(z) = max(0, z)')}: ${E('ReLU(3) = 3')}، ${E('ReLU(−2) = 0')}<br>${E('σ(z) = 1 / (1 + e⁻ᶻ)')}: خروجی بینِ ۰ و ۱ (درسِ رگرسیون لجستیک)</p>
               <p>w و b همان <b>پیچ‌ها</b>ی درسِ گرادیان کاهشی‌اند: عددهایی که مدل یاد می‌گیرد.</p>` },
      { t: 'formula', title: `فرمولِ یک لایه ${EN('Layer')}`,
        intro: `<p><b>لایه</b> ${EN('Layer')} = چند نورون کنارِ هم با همان ورودی‌ها. <b>شبکه</b> = چند لایه پشتِ هم؛ لایه‌های وسط را <b>لایه‌ی پنهان</b> ${EN('Hidden Layer')} می‌گویند. هر سطرِ ماتریسِ W (درسِ ماتریس)، وزن‌های یک نورون است و همه را یک‌جا حساب می‌کنیم.</p>`,
        toks: [{ s: 'a', c: 'green', l: 'خروجیِ همه‌ی نورون‌ها' }, { s: '=' }, { s: 'f', c: 'ink', l: 'خم، روی هر خانه' }, { s: '(' },
               { s: 'W', c: 'orange', l: 'ماتریسِ وزن‌ها' }, { s: 'x', c: 'blue', l: 'بردارِ ورودی' }, { s: '+' }, { s: 'b', c: 'orange', l: 'بردارِ عددهای ثابت' }, { s: ')' }],
        read: 'هر خانه‌ی Wx = ضرب داخلیِ یک سطر با x = امتیازِ یک نورون.',
        note: `<p>۲ ورودی و ۳ نورون: W ماتریسی ۳ × ۲ است، b سه عدد دارد و a سه عدد: یک بردارِ تازه برای لایه‌ی بعد.</p>
               <p>شبکه‌ی دو لایه: ${E('y = f₂(W₂ · f₁(W₁x + b₁) + b₂)')}</p>` },
      { t: 'text', title: 'شبکه‌ای که XOR را حل می‌کند',
        body: `<p>۲ ورودی، ۲ نورونِ پنهان با ReLU، ۱ خروجی (بدونِ خم): ${E('h₁ = ReLU(x₁ + x₂)')}، ${E('h₂ = ReLU(x₁ + x₂ − 1)')}، ${E('y = h₁ − 2·h₂')}</p>
               <p>${NN_SPAN('blue', 'h₁')} می‌شمارد چند کلید روشن است؛ ${NN_SPAN('blue', 'h₂')} فقط وقتی هر دو روشن‌اند. چهار حالت:</p>
               ${NN_TABLE}
               <p>جواب‌ها ۰، ۱، ۱، ۰: دقیقاً XOR! در ردیفِ آخر h₂ روشن می‌شود و ۲ را از ۲ کم می‌کند.</p>` },
      { t: 'play', w: NN_W_NET, title: 'شبکه‌ی ۲–۲–۱ روی XOR',
        body: 'رنگِ <b style="color:var(--orange)">نارنجی</b> = خروجیِ شبکه. دو خط‌چین = جایی که هر نورونِ پنهان از صفر بیرون می‌آید و خم می‌شود. «وزن‌های تصادفی» را چند بار بزنید. بعد با وزن‌های حل‌کننده، «خمیدگی (ReLU)» را خاموش کنید.' },
      { t: 'rules', title: 'سه قانون مهم', items: [
        { r: 'بدونِ تابعِ فعال‌سازی، <b>هر تعداد لایه = یک لایه</b>.',
          why: `چون ${E('W₂(W₁x) = (W₂W₁)x')} و ضربِ دو ماتریس باز یک ماتریس است (درسِ ضرب ماتریس؛ عدد ثابت‌ها هم همین‌طور جمع می‌شوند). در مثالِ XOR بدونِ ReLU: ${E('y = (x₁ + x₂) − 2(x₁ + x₂ − 1) = 2 − x₁ − x₂')}، یک خطِ صاف.` },
        { r: 'نورون و لایه‌ی بیشتر = شبکه‌ی <b>انعطاف‌پذیرتر</b>، ولی <b>داده‌ی بیشتر</b> لازم دارد.',
          why: 'هر نورون پیچ‌های تازه می‌آورد. پیچِ زیاد با داده‌ی کم یعنی شبکه داده‌ها را حفظ می‌کند: همان بیش‌برازش (Overfitting).' },
        { r: 'شبکه‌ی عصبی فقط یک <b>تابعِ بزرگ</b> است با پیچ‌های زیاد.',
          why: 'ورودی می‌گیرد و خروجی می‌دهد (درسِ تابع). هر لایه یک تابع است و شبکه تابع‌هایی تو در تو؛ برای همین قاعده‌ی زنجیره‌ای در آموزشش به کار می‌آید.' },
      ] },
      { t: 'ai', title: 'شبکه‌ی عصبی در هوش مصنوعی',
        body: `<p>ChatGPT، تشخیصِ چهره در گوشی، دستیارِ صوتی و ترجمه‌ی ماشینی، همه شبکه‌های عصبیِ غول‌پیکرند. مثلاً GPT-3 (سالِ ۲۰۲۰) حدودِ ۱۷۵ میلیارد پیچ داشت.</p>
               <p><b>یادگیریِ عمیق</b> ${EN('Deep Learning')} یعنی شبکه با <b>لایه‌های زیاد</b>؛ «عمیق» یعنی همین.</p>
               <p>پیچ‌ها را دستی نمی‌گذارند. با <b>گرادیان کاهشی</b> یاد گرفته می‌شوند، و گرادیانِ میلیاردها پیچ را <b>پس‌انتشار خطا</b> ${EN('Backpropagation')} حساب می‌کند.</p>` },
      { t: 'quiz', q: 'در همان شبکه‌ی XOR (h₁ = ReLU(x₁ + x₂)، h₂ = ReLU(x₁ + x₂ − 1)، y = h₁ − 2h₂)، ورودی x₁ = ۲ و x₂ = ۰ را بدهیم. y چند است؟',
        options: ['۲', '۱', '۰'], answer: 2,
        why: 'h₁ = ReLU(۲) = ۲، h₂ = ReLU(۱) = ۱، پس y = ۲ − ۲ × ۱ = ۰. «۲» یعنی h₂ فراموش شده. «۱» یعنی ضریبِ ۲ جا افتاده (۲ − ۱).' },
      { t: 'text', title: 'یک سؤال برای درس بعد',
        body: `<p>وزن‌های XOR را ما دستی پیدا کردیم. وزن‌های تصادفی اغلب بد بودند. شبکه‌ی واقعی میلیون‌ها پیچ دارد.</p>
               <div class="key">گرادیان کاهشی برای هر پیچ شیبِ خطا را می‌خواهد. شیبِ پیچی را که سه لایه عقب‌تر است، چطور حساب کنیم؟</div>
               <p>جواب: <b>پس‌انتشار خطا</b> ${EN('Backpropagation')}. درس بعد!</p>` },
    ] },
  ],
  sheet: {
    one: 'شبکه‌ی عصبی = لایه‌هایی از نورون؛ هر نورون جمعِ وزن‌دارِ ورودی‌ها + عدد ثابت را حساب می‌کند و از یک خم (تابعِ فعال‌سازی) رد می‌کند. ساخته شد چون یک خطِ صاف (یک نورون) الگوهای خمیده مثل XOR را جدا نمی‌کند.',
    f: 'نورون: a = f(w · x + b)  ·  لایه: a = f(Wx + b)  ·  ReLU(z) = max(0, z)',
    rules: ['یک نورون = یک مرزِ صاف؛ AND و OR را حل می‌کند، XOR را نه.',
      'بدونِ خم، چند لایه = یک لایه (W₂W₁ باز یک ماتریس است).',
      'هر لایه از خروجیِ لایه‌ی قبل ویژگیِ تازه می‌سازد.',
      'XOR: h₁ = ReLU(x₁ + x₂)، h₂ = ReLU(x₁ + x₂ − 1)، y = h₁ − 2h₂.',
      'پیچِ بیشتر = انعطافِ بیشتر، ولی داده‌ی بیشتر لازم (وگرنه بیش‌برازش).'],
    use: 'ChatGPT، تشخیصِ تصویر و صدا: شبکه‌های عمیق با میلیاردها پیچ که با گرادیان کاهشی و پس‌انتشار خطا آموزش می‌بینند.',
    mistake: 'فکر کنیم لایه‌ی بیشتر بدونِ تابعِ فعال‌سازی کمک می‌کند؛ بدونِ خم، کلِ شبکه باز یک خطِ صاف است.',
  },
});
