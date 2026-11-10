// ---------- Foundations: Gradient ----------
// Pictures: (1) a rectangle: the added strip IS the partial derivative,
// (2) a valley seen from above + two "slices" (walk only east / only north) with their tangent lines,
// (3) house price: two straight-line slices with slope triangles, (4) stepping downhill.
const GRAD_clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const GRAD_n = n => String(Math.round(n * 100) / 100);
const GRAD_p = n => (n < 0 ? `(${GRAD_n(n)})` : GRAD_n(n));
const GRAD_z = (x, y) => x * x + 2 * y * y;      // valley height
const GRAD_grad = (x, y) => [2 * x, 4 * y];       // [∂z/∂x, ∂z/∂y]
const GRAD_ARROW = 0.2; // arrows drawn 5× smaller so they fit
const GRAD_LR = 0.1;    // step size in the downhill picture

// valley from above: darker = higher (like a shaded map)
const GRAD_shade = (g, x0, x1, y0, y1) => {
  const c = g.ctx, d = 0.125, top = GRAD_z(x1, y1);
  c.save(); c.fillStyle = g.css('orange');
  for (let x = x0; x < x1; x += d) for (let y = y0; y < y1; y += d) {
    c.globalAlpha = 0.05 + 0.55 * Math.min(1, GRAD_z(x + d / 2, y + d / 2) / top);
    const L = Math.round(g.X(x)), T = Math.round(g.Y(y + d)); // whole pixels: no seams between cells
    c.fillRect(L, T, Math.round(g.X(x + d)) - L, Math.round(g.Y(y)) - T);
  }
  c.restore();
};

// (2) valley from above + two slices that share one state
const GRAD_W_HILL = host => {
  const s = { x: 2, y: 1 };
  const top = document.createElement('div'), east = document.createElement('div'), north = document.createElement('div');
  east.className = north.className = 'slice';
  host.append(top, east, north);
  const tan = (g, a, f, m, color, from, to) => { // the curve, its tangent at a, and the point
    g.fn(f, color, 3, from, to);
    g.line(a - 0.8, f(a) - 0.8 * m, a + 0.8, f(a) + 0.8 * m, 'green', 3);
    g.dot(a, f(a), 'red', 6);
  };
  const sE = plane(east, {
    x: [-3, 3], y: [0, 18], ratio: 0.42, step: [1, 3], state: s, names: ['شرق', 'ارتفاع'],
    draw: (g, s) => { g.grid(); tan(g, s.x, x => GRAD_z(x, s.y), 2 * s.x, 'blue', -3, 3); },
    read: s => `<b style="color:var(--blue)">فقط به شرق</b> (شمال ثابت روی ${fa(s.y)}): یک منحنیِ معمولی. شیبِ خط سبز = ${E('2x = ' + GRAD_n(2 * s.x))}`,
  });
  const sN = plane(north, {
    x: [-3, 3], y: [0, 18], ratio: 0.42, step: [1, 3], state: s, names: ['شمال', 'ارتفاع'],
    draw: (g, s) => { g.grid(); tan(g, s.y, y => GRAD_z(s.x, y), 4 * s.y, 'orange', -2, 2); },
    read: s => `<b style="color:var(--orange)">فقط به شمال</b> (شرق ثابت روی ${fa(s.x)}): شیبِ خط سبز = ${E('4y = ' + GRAD_n(4 * s.y))}`,
  });
  const map = plane(top, {
    x: [-3, 3], y: [-2, 2], equal: true, snap: 0.5, state: s,
    handles: [{ get: s => [s.x, s.y], set: (s, x, y) => { s.x = GRAD_clamp(x, -2.5, 2.5); s.y = GRAD_clamp(y, -1.5, 1.5); sE.draw(); sN.draw(); }, color: 'red' }],
    draw: (g, s) => {
      GRAD_shade(g, -3, 3, -2, 2);
      g.dot(0, 0, 'muted', 4);
      g.line(-3, s.y, 3, s.y, 'blue', 2, [6, 6]);   // the east-west walk
      g.line(s.x, -2, s.x, 2, 'orange', 2, [6, 6]); // the north-south walk
      const [gx, gy] = GRAD_grad(s.x, s.y);
      g.arrow(s.x, s.y, s.x + GRAD_ARROW * gx, s.y + GRAD_ARROW * gy, 'green', 6);
      g.text(2.9, -1.8, 'شرق', 'muted', 'right', 0);
      g.text(0, 1.8, 'شمال', 'muted', 'center', 0);
      g.text(-2.9, 1.8, 'پررنگ‌تر = بلندتر', 'muted', 'left', 0);
    },
    read: s => {
      const [gx, gy] = GRAD_grad(s.x, s.y);
      return `ارتفاع این‌جا: ${E(String.raw`${GRAD_p(s.x)}^2 + 2 \times ${GRAD_p(s.y)}^2 = ${GRAD_n(GRAD_z(s.x, s.y))}`)}<br>` +
        `<b style="color:var(--green)">گرادیان</b> = [شیب شرق، شیب شمال] = ${V(gx, gy)}` +
        (!gx && !gy ? '<br>هر دو شیب صفر: <b>کفِ دره</b>، پیکانی نمی‌ماند.' : '');
    },
  });
  return () => { map(); sE(); sN(); };
};

// (3) house price = 80 × area − 20 × age + 500 (million toman): two straight slices with slope triangles
const GRAD_price = (m, a) => 80 * m - 20 * a + 500;
const GRAD_W_HOUSE = h => plane(h, {
  x: [0, 1], y: [0, 1], ratio: 0.8, state: { m: 100, a: 10, turn: 35 },
  sliders: [{ key: 'm', label: 'متراژ', min: 80, max: 120, step: 5 }, { key: 'a', label: 'سن', min: 0, max: 40, step: 5 },
            { key: 'turn', label: 'چرخش', min: 0, max: 80, step: 5 }],
  draw: (g, s) => {
    // 3D: floor = (area, age), height = price. u, v, w are 0..1
    const W = g.X(1), H = g.Y(0), S = Math.min(W * 0.62, H * 0.95), th = s.turn * Math.PI / 180;
    const P = (m, a, p) => {
      const X = (m - 80) / 40 - 0.5, Y = a / 40 - 0.5, Z = (p - 6100) / 4000;
      const x1 = X * Math.cos(th) - Y * Math.sin(th), y1 = X * Math.sin(th) + Y * Math.cos(th);
      return [W / 2 + S * x1, H * 0.8 - S * 0.75 * Z + S * 0.3 * y1];
    };
    const c = g.ctx, pen = (col, w, dash) => { c.strokeStyle = g.css(col); c.lineWidth = w; c.setLineDash(dash || []); };
    const seg = (a, b) => { c.beginPath(); c.moveTo(...a); c.lineTo(...b); c.stroke(); };
    // floor grid
    pen('line', 1);
    for (let i = 0; i <= 4; i++) { seg(P(80 + 10 * i, 0, 6100), P(80 + 10 * i, 40, 6100)); seg(P(80, 10 * i, 6100), P(120, 10 * i, 6100)); }
    // price surface (a tilted flat sheet, because the formula is linear)
    c.beginPath(); [[80, 0], [120, 0], [120, 40], [80, 40]].forEach(([m, a], i) => { const q = P(m, a, GRAD_price(m, a)); i ? c.lineTo(...q) : c.moveTo(...q); });
    c.closePath(); c.globalAlpha = 0.18; c.fillStyle = g.css('accent'); c.fill(); c.globalAlpha = 1; pen('accent', 1.5); c.stroke();
    pen('muted', 1);
    for (let i = 1; i < 4; i++) { seg(P(80 + 10 * i, 0, GRAD_price(80 + 10 * i, 0)), P(80 + 10 * i, 40, GRAD_price(80 + 10 * i, 40))); seg(P(80, 10 * i, GRAD_price(80, 10 * i)), P(120, 10 * i, GRAD_price(120, 10 * i))); }
    // this house: a pole from the floor up to its price
    const here = P(s.m, s.a, GRAD_price(s.m, s.a));
    pen('muted', 2, [4, 4]); seg(P(s.m, s.a, 6100), here); c.setLineDash([]);
    // the two partial slopes as arrows on the sheet
    const arrow = (to, col) => { const [x0, y0] = here, [x1, y1] = to, an = Math.atan2(y1 - y0, x1 - x0);
      pen(col, 4); seg(here, to); c.fillStyle = g.css(col); c.beginPath(); c.moveTo(x1, y1);
      c.lineTo(x1 - 12 * Math.cos(an - 0.45), y1 - 12 * Math.sin(an - 0.45)); c.lineTo(x1 - 12 * Math.cos(an + 0.45), y1 - 12 * Math.sin(an + 0.45)); c.fill(); };
    const m2 = s.m <= 100 ? s.m + 20 : s.m - 20, a2 = s.a <= 20 ? s.a + 20 : s.a - 20;
    arrow(P(m2, s.a, GRAD_price(m2, s.a)), 'blue');
    arrow(P(s.m, a2, GRAD_price(s.m, a2)), 'orange');
    c.fillStyle = g.css('red'); c.beginPath(); c.arc(...here, 6, 0, 7); c.fill();
    // axis names
    c.font = '700 12px Vazirmatn, Tahoma, sans-serif'; c.fillStyle = g.css('muted'); c.textAlign = 'center';
    c.fillText('متراژ', ...P(124, -4, 6100)); c.fillText('سن', ...P(76, 44, 6100)); c.fillText('قیمت', ...P(80, 0, 10400));
    pen('muted', 1); seg(P(80, 0, 6100), P(80, 0, 10200));
  },
  read: s => `قیمت این خانه: ${E(String.raw`80 \times ${s.m} - 20 \times ${s.a} + 500 = ${GRAD_price(s.m, s.a)}`)}<br>` +
    `<b style="color:var(--blue)">پیکان آبی</b>: فقط متراژ عوض شود (۲۰ متر) ← قیمت <b>۱۶۰۰ بالا</b>، یعنی متری <b>+۸۰</b><br>` +
    `<b style="color:var(--orange)">پیکان نارنجی</b>: فقط سن عوض شود (۲۰ سال) ← قیمت <b>۴۰۰ پایین</b>، یعنی سالی <b>−۲۰</b><br>` +
    `گرادیان = ${V(80, -20)}. صفحه‌ی قیمت صاف است، پس این دو شیب همه‌جا یکی‌اند.`,
});

// (4) the same valley: each press moves the point by −0.1 × gradient and draws the path
const GRAD_W_DOWN = h => plane(h, {
  x: [-5, 5], y: [-3.75, 3.75], equal: true, snap: 0.5,
  state: { x: 4, y: 2.5, path: [[4, 2.5]] },
  handles: [{ get: s => [s.x, s.y], set: (s, x, y) => { s.x = GRAD_clamp(x, -4, 4); s.y = GRAD_clamp(y, -3, 3); s.path = [[s.x, s.y]]; }, color: 'red' }],
  buttons: [
    { label: 'یک قدم سرازیری', on: s => { const [gx, gy] = GRAD_grad(s.x, s.y); s.x -= GRAD_LR * gx; s.y -= GRAD_LR * gy; s.path.push([s.x, s.y]); } },
    { label: 'از نو', on: s => { s.x = 4; s.y = 2.5; s.path = [[4, 2.5]]; } },
  ],
  draw: (g, s) => {
    GRAD_shade(g, -5, 5, -3.75, 3.75);
    g.dot(0, 0, 'muted', 4);
    for (let i = 1; i < s.path.length; i++) g.line(s.path[i - 1][0], s.path[i - 1][1], s.path[i][0], s.path[i][1], 'green', 3);
    s.path.forEach(([x, y]) => g.dot(x, y, 'green', 4));
    const [gx, gy] = GRAD_grad(s.x, s.y);
    g.arrow(s.x, s.y, s.x - GRAD_ARROW * gx, s.y - GRAD_ARROW * gy, 'ink', 3);
  },
  read: s => {
    const [gx, gy] = GRAD_grad(s.x, s.y), n = s.path.length - 1;
    const end = Math.hypot(gx, gy) < 0.05 ? '<br>گرادیان تقریباً صفر شد: به <b>کفِ دره</b> رسیده‌ایم.' : '';
    return `قدم‌ها: <b>${fa(n)}</b> ← ارتفاع = <b>${fa(GRAD_z(s.x, s.y))}</b><br>` +
      `<b style="color:var(--green)">گرادیان</b> این‌جا = ${V(gx, gy)} (رو به سربالایی)<br>` +
      `قدم بعدی = ${E(String.raw`-0.1 \times \nabla f`)} = ${V(-GRAD_LR * gx, -GRAD_LR * gy)}؛ یعنی کمی خلاف گرادیان${end}`;
  },
});

lesson({
  id: 'gradient', node: 'gradient', title: 'گرادیان', en: 'Gradient',
  parts: [
    { name: 'چرا و یعنی چه؟', cards: [
      { t: 'story', title: `گرادیان ${EN('Gradient')}`,
        body: `<div class="key"><b>هدف گرادیان:</b> پیدا کردنِ <b>بهترین راهِ بالا رفتن یا پایین آمدن</b>. روی کوه ایستاده‌اید و مه است؛ فقط زیر پایتان را می‌بینید. از کدام طرف بروید تا <b>سریع‌تر از همه</b> پایین بیایید؟</div>
               <p>در درس مشتق فقط <b>یک جهت</b> داشتیم (جلو یا عقب) و شیب یک عدد بود. ولی روی کوه می‌شود به شرق، غرب، شمال، جنوب، یا هر طرفِ کج رفت. حالا «شیب» یک عدد نیست.</p>
               <p>راه‌حل: <b>جهت‌ها را یکی‌یکی امتحان کن</b>. یک قدم فقط رو به شرق: چقدر بالا رفتی؟ یک قدم فقط رو به شمال: چقدر؟ این دو شیب کنار هم = <b>گرادیان</b>، و پیکانش دقیقاً تندترین راهِ بالا را نشان می‌دهد. برعکسش، تندترین راه پایین است.</p>
               <p>مدل هوش مصنوعی هم همین کار را می‌کند: «کوه»ش خطای مدل است و می‌خواهد سریع‌تر از همه پایین بیاید.</p>`,
        who: `این ایده در قرن نوزدهم با کار ریاضی‌دان‌هایی مثل ویلیام همیلتون (William Hamilton) شکل گرفت. نماد ${E(String.raw`\nabla`)} را «نابلا» می‌خوانند.` },
      { t: 'text', title: 'معنی ساده',
        body: `<p><b>مشتق جزئی</b> ${EN('Partial Derivative')}: فقط <b>یک</b> ورودی را کمی عوض کن و بقیه را <b>ثابت نگه دار</b>. نتیجه چقدر عوض شد؟ این همان مشتقِ معمولیِ درس قبل است، فقط بقیه‌ی ورودی‌ها قفل‌اند.</p>
               <p><b>گرادیان</b> = همه‌ی این شیب‌های جزئی، کنار هم در یک فهرست: [شیبِ شرق، شیبِ شمال].</p>
               <div class="key">این فهرست را می‌شود یک <b>پیکان</b> کشید: به طرفی اشاره می‌کند که نتیجه <b>از همه سریع‌تر بالا</b> می‌رود، و طولش می‌گوید چقدر سریع.</div>
               <p>به فهرستی از عددها که پیکان می‌شود، <b>بردار</b> ${EN('Vector')} می‌گویند (فصل بردارها).</p>` },
      { t: 'play', w: GRAD_W_HILL, title: 'دره: دو قدم‌زدن جدا',
        body: `یک دره از بالا: هرچه رنگ <b style="color:var(--orange)">پررنگ‌تر</b>، زمین بلندتر؛ کفِ دره وسط است. نقطه‌ی <b style="color:var(--red)">قرمز</b> را بکشید. خط‌چینِ <b style="color:var(--blue)">آبی</b> یعنی «فقط شرق-غرب راه برو»؛ نمودار دوم همان راه را از کنار نشان می‌دهد. خط‌چینِ <b style="color:var(--orange)">نارنجی</b> یعنی «فقط شمال-جنوب»؛ نمودار سوم. شیبِ خط سبز در هر نمودار، یک مشتق معمولی است. پیکان <b style="color:var(--green)">سبز</b> روی نقشه = گرادیان (۵ بار کوچک‌تر کشیده شده).`,
        look: ['نقطه روی (۲، ۱) ← شیب شرق ۴، شیب شمال ۴. گرادیان [۴، ۴]: پیکان رو به شمال‌شرق، یعنی رو به سربالایی.',
               'نقطه را به (۲، ۰) ببرید ← در نمودار سوم نقطه درست ته منحنی است و خط سبز صاف: شیب شمال ۰. گرادیان [۴، ۰].',
               'نقطه را به (−۲، ۱) ببرید ← شیب شرق منفی شد (رو به شرق سرازیری است). گرادیان [−۴، ۴].',
               'نقطه را به (۰، ۰) ببرید ← هر دو خط سبز صاف‌اند. گرادیان [۰، ۰]: کفِ دره.'],
        see: 'گرادیان چیز جدیدی نیست: دو مشتقِ معمولی است، یکی برای هر جهت، که کنار هم گذاشته شده‌اند. پیکانشان همیشه رو به سربالاییِ تند است. آب باران برعکسِ همین پیکان جاری می‌شود، و مدل‌های هوش مصنوعی هم برعکسِ همین پیکان قدم برمی‌دارند تا خطایشان کم شود.' },
      { t: 'life', title: 'گرادیان همه‌جای زندگی هست', items: [
        { h: 'آشپزی', d: 'مزه به شکر و نمک بستگی دارد. «فقط یک قاشق شکر بیشتر» یک شیب است، «فقط یک ذره نمک بیشتر» شیبِ دیگر. گرادیان می‌گوید کدام بیشتر اثر دارد.' },
        { h: 'خانه', d: 'قیمت به متراژ و سن بستگی دارد: هر متر بیشتر چقدر گران‌تر، هر سال پیرتر چقدر ارزان‌تر.' },
        { h: 'کوه‌پیمایی', d: 'گرادیان تندترین راهِ بالا را نشان می‌دهد؛ آب باران درست برعکسِ آن پایین می‌رود.' },
        { h: 'هوش مصنوعی', d: 'خطای مدل به میلیون‌ها عدد بستگی دارد. گرادیان برای هر عدد می‌گوید کمی زیادش کنیم، خطا بالا می‌رود یا پایین.' },
      ] },
      { t: 'sort', title: 'این یک «شیب جزئی» است؟', yes: 'شیب جزئی است', no: 'شیب جزئی نیست', items: [
        { q: 'فقط یک قاشق شکر بیشتر، نمک همان بماند؛ مزه چقدر عوض شد؟', a: true, why: 'یک ورودی عوض شد، بقیه ثابت ماند.' },
        { q: 'شکر و نمک را با هم بیشتر کنیم؛ مزه چقدر عوض شد؟', a: false, why: 'دو ورودی با هم عوض شدند. شیب جزئی یعنی فقط یکی.' },
        { q: 'روی کوه فقط به شرق قدم بزنیم؛ با هر متر چقدر بالا رفتیم؟', a: true, why: 'فقط شرق-غرب عوض شد؛ شمال-جنوب ثابت ماند.' },
        { q: 'ارتفاع همین نقطه از کوه: ۱۲۰۰ متر', a: false, why: 'یک مقدار است، نه تغییر. «به‌ازای هر چه؟» ندارد.' },
        { q: 'قیمت ثابت، فقط تبلیغ بیشتر؛ فروش چقدر زیاد شد؟', a: true, why: 'فقط تبلیغ عوض شد؛ قیمت ثابت ماند.' },
      ] },
      { t: 'quiz', q: 'گرادیانِ یک کوه در جایی که ایستاده‌اید [۳، −۱] است (اول شرق، بعد شمال). اگر فقط به <b>شمال</b> بروید چه می‌شود؟',
        options: ['کمی پایین می‌روید', 'کمی بالا می‌روید', 'ارتفاع عوض نمی‌شود'], answer: 0,
        why: 'خانه‌ی دوم (شمال) منفی است: رفتن به شمال ارتفاع را کم می‌کند. خانه‌ی اول، ۳، می‌گوید رفتن به شرق بالا می‌برد، آن هم تند. اگر شیب صفر بود، ارتفاع عوض نمی‌شد.' },
    ] },
    { name: 'فرمول', cards: [
      { t: 'formula', f: String.raw`\Cg{\nabla f} = \left[\, \Cb{\frac{\partial f}{\partial x}},\ \Co{\frac{\partial f}{\partial y}} \,\right]`, title: `فرمول گرادیان ${EN('Gradient')}`,
        intro: `<p>${E('f(x, y)')} یعنی تابعی با دو ورودی، x و y. حرف ${E(String.raw`\partial`)} («پارشال»، یعنی جزئی) همان d مشتق است، با این فرق که <b>فقط یک ورودی</b> عوض می‌شود و بقیه ثابت‌اند.</p>`,
        toks: [{ s: String.raw`\nabla f`, c: 'green', l: 'گرادیانِ f (نابلا اف)' }, { s: '=' }, { s: '[' },
               { s: String.raw`\frac{\partial f}{\partial x}`, c: 'blue', l: 'شیب وقتی فقط x عوض شود (y قفل)' }, { s: ',' },
               { s: String.raw`\frac{\partial f}{\partial y}`, c: 'orange', l: 'شیب وقتی فقط y عوض شود (x قفل)' }, { s: ']' }],
        read: 'خوانده می‌شود: «نابلا اف برابر است با پارشال اف بر پارشال ایکس، و پارشال اف بر پارشال وای». کروشه [ ] یعنی یک فهرست (بردار).',
        note: `<p><b>روش حساب:</b> برای ${E(String.raw`\partial f / \partial x`)}، y را مثل یک عدد معمولی (مثلاً ۵) ببین و مشتق بگیر. برای ${E(String.raw`\partial f / \partial y`)}، برعکس. با ۱۰ ورودی، فهرست ۱۰ خانه دارد.</p>` },
      { t: 'example', w: GRAD_W_HOUSE, title: 'قیمت خانه با دو ورودی',
        intro: `<p>مدل ساده‌ی قیمت (میلیون تومان): ${E('f(x, y) = 80x - 20y + 500')}؛ ${E('x')} = متراژ، ${E('y')} = سن خانه. تصویر سه‌بعدی است: کف = متراژ و سن، ارتفاع = قیمت. با لغزنده‌ها خانه را عوض کنید و با «چرخش» از زاویه‌ی دیگر ببینید.</p>`,
        steps: [`<b style="color:var(--blue)">شیب رو به متراژ</b>: سن را قفل کن. ${E('-20y + 500')} حالا فقط یک عدد ثابت است و مشتقش ۰. پس ${E(String.raw`\frac{\partial f}{\partial x} = 80`)}. پیکان آبی: هر ۲۰ متر، ۱۶۰۰ بالا.`,
                `<b style="color:var(--orange)">شیب رو به سن</b>: متراژ را قفل کن. ${E(String.raw`\frac{\partial f}{\partial y} = -20`)}. پیکان نارنجی: هر ۲۰ سال، ۴۰۰ پایین.`,
                `گرادیان: ${E(String.raw`\nabla f = [80,\ -20]`)}`,
                `بررسی: خانه‌ی ۱۰۰ متریِ ۱۰ ساله: ${E(String.raw`80 \times 100 - 20 \times 10 + 500 = 8300`)}. یک متر بزرگ‌تر: ۸۳۸۰ (۸۰ بیشتر). یک سال پیرتر: ۸۲۸۰ (۲۰ کمتر).`,
                'لغزنده‌ها را جابه‌جا کنید: نقطه روی صفحه جابه‌جا می‌شود ولی پیکان‌ها همان شیب را دارند. صفحه‌ی قیمت صاف است، پس گرادیان همه‌جا یکی است.'],
        result: 'هر خانه‌ی گرادیان یک جمله است: «هر متر بیشتر، ۸۰ میلیون گران‌تر» و «هر سال پیرتر، ۲۰ میلیون ارزان‌تر». علامت منفی یعنی «این دکمه را بالا ببری، نتیجه پایین می‌آید».' },
      { t: 'example', title: `مثالِ دره: ${E('f(x, y) = x^2 + 2y^2')}`,
        steps: [`شیب رو به شرق: y را قفل کن؛ ${E('2y^2')} عدد ثابت است، مشتقش ۰. ${E(String.raw`x^2 \to 2x`)}. پس ${E(String.raw`\frac{\partial f}{\partial x} = 2x`)}`,
                `شیب رو به شمال: x را قفل کن. ${E(String.raw`2y^2 \to 4y`)}. پس ${E(String.raw`\frac{\partial f}{\partial y} = 4y`)}`,
                `در نقطه‌ی (۲، ۱): ${E(String.raw`\nabla f = [2 \cdot 2,\ 4 \cdot 1] = [4,\ 4]`)}؛ همان پیکانی که در تصویرِ دره دیدید.`,
                `بررسی با یک قدم کوچک (${E('h = 0.001')}): ${E('f(2, 1) = 6')} و ${E('f(2.001, 1) \\approx 6.004')} ← ${E(String.raw`\frac{0.004}{0.001} = 4`)} ✓`],
        result: 'هر شیب جزئی یک مشتق معمولی است که در آن بقیه‌ی ورودی‌ها فقط عدد ثابت‌اند.' },
      { t: 'play', w: GRAD_W_DOWN, title: 'خلاف گرادیان، رو به پایین',
        body: 'همان دره. پیکان سیاه = منفیِ گرادیان (رو به سرازیری). خط <b style="color:var(--green)">سبز</b> = مسیری که تا حالا رفته‌ایم. هر بار دکمه، نقطه را ۰٫۱ برابرِ منفیِ گرادیان جابه‌جا می‌کند. نقطه‌ی <b style="color:var(--red)">قرمز</b> را می‌شود کشید.',
        look: ['یک بار «یک قدم سرازیری» را بزنید ← گرادیان در (۴، ۲٫۵) برابر [۸، ۱۰] است، قدم [−۰٫۸، −۱]؛ ارتفاع از ۲۸٫۵ به ۱۴٫۷۴ می‌رسد.',
               'دو بار دیگر بزنید ← ارتفاع حدود ۴٫۷۸؛ قدم‌ها کوتاه‌تر شده‌اند.',
               'آن‌قدر بزنید تا قدم ۲۳ ← گرادیان تقریباً صفر: به کفِ دره رسیده‌ایم.',
               'نقطه را به (−۴، −۳) بکشید و دوباره بزنید ← از آن طرف هم به همان کف می‌رسد.'],
        see: 'گرادیان کاهشی یعنی همین: هر بار گرادیان را حساب کن و کمی خلاف آن برو. نزدیک کف، گرادیان کوچک است، پس قدم‌ها خودبه‌خود کوتاه می‌شوند. مسیر کج است چون دره رو به شمال تندتر است.' },
      { t: 'rules', title: 'سه قانون مهم', items: [
        { r: 'گرادیان رو به <b>سربالایی</b> است؛ <b>منفیِ</b> گرادیان رو به <b>سرازیری</b>.',
          why: 'هر خانه می‌گوید در جهت خودش کدام طرف بالا می‌رود. منفی کردن همه‌ی خانه‌ها، پیکان را درست برعکس می‌کند.' },
        { r: 'در <b>قله</b>، <b>کفِ دره</b>، یا وسطِ زین اسب، گرادیان <b>صفر</b> است.',
          why: 'آن‌جا در هر جهت لحظه‌ای صاف است، پس همه‌ی شیب‌ها صفرند. ولی زین (از یک طرف بالا، از طرف دیگر پایین) نشان می‌دهد گرادیانِ صفر همیشه یعنی کف نیست.' },
        { r: 'هر شیب جزئی مثل یک <b>مشتق معمولی</b> حساب می‌شود؛ ورودی‌های دیگر را <b>عدد ثابت</b> بگیرید.',
          why: `ورودیِ قفل‌شده تکان نمی‌خورد، پس فقط یک عدد است، و مشتقِ عدد ثابت صفر است. مثلاً در ${E('x^2 + 3y')} با y = ۲، تکه‌ی ${E('3y')} همان ۶ است.` },
      ] },
      { t: 'ai', title: 'گرادیان در هوش مصنوعی',
        body: `<p>یک مدل میلیون‌ها عددِ قابل تنظیم ${EN('Weight')} دارد و یک عدد «خطا» که باید کم شود.</p>
               <p>گرادیانِ خطا یک فهرستِ بزرگ است، با یک خانه برای هر عدد: «اگر همین عدد را کمی زیاد کنی، خطا چقدر و به کدام طرف عوض می‌شود».</p>
               <p><b>گرادیان کاهشی</b> ${EN('Gradient Descent')} قدم‌به‌قدم خلاف گرادیان (${E(String.raw`-\nabla f`)}) می‌رود، مثل تصویر قبل. این گرادیانِ بزرگ را <b>پس‌انتشار خطا</b> ${EN('Backpropagation')} با قاعده‌ی زنجیره‌ای حساب می‌کند.</p>` },
      { t: 'quiz', q: `قیمت خانه ${E('f = 80x - 20y + 500')} است (x متراژ، y سن). کدام کار قیمت را <b>بیشتر</b> بالا می‌برد؟`,
        options: ['خانه یک متر بزرگ‌تر باشد', 'خانه یک سال نوتر باشد', 'هر دو به یک اندازه'], answer: 0,
        why: 'گرادیان [۸۰، −۲۰] است. یک متر بیشتر: +۸۰. یک سال <b>نوتر</b> یعنی y یکی کمتر: −۲۰ × −۱ = +۲۰. پس متراژ ۴ برابر اثر دارد.' },
      { t: 'quiz', q: `گرادیانِ ${E('f(x, y) = 3x + y^2')} در نقطه‌ی (۲، ۱) چیست؟`,
        options: [V(3, 2), V(6, 1), V(2, 1)], answer: 0,
        why: `${E(String.raw`\frac{\partial f}{\partial x} = 3`)} (چون ${E('y^2')} قفل است و مشتقش ۰) و ${E(String.raw`\frac{\partial f}{\partial y} = 2y = 2`)}. پس ${V(3, 2)}. ${V(6, 1)} مقدارِ دو تکه‌ی تابع است (${E(String.raw`3 \cdot 2`)} و ${E('1^2')})، نه شیب‌شان. ${V(2, 1)} خودِ نقطه است.` },
      { t: 'quiz', q: 'می‌خواهید خطای یک مدل را <b>کم</b> کنید و گرادیانِ خطا [۴، −۲] است. هر عدد را به کدام طرف ببرید؟',
        options: ['اولی را کم کنید، دومی را زیاد', 'اولی را زیاد کنید، دومی را کم', 'هر دو را زیاد کنید'], answer: 0,
        why: 'برای پایین آمدن باید خلاف گرادیان رفت: منفیِ [۴، −۲] می‌شود [−۴، ۲]. یعنی عدد اول را کم و عدد دوم را زیاد کنید. گزینه‌ی دوم درست در جهت گرادیان است، یعنی خطا را <b>بیشتر</b> می‌کند.' },
      { t: 'text', title: 'جعبه‌ابزار پایه تمام شد',
        body: `<p>تابع، شیب، مشتق، قاعده‌ی زنجیره‌ای و حالا گرادیان: همه‌ی ابزارِ «تغییر» را دارید.</p>
               <div class="key">ولی قدمِ سرازیری چقدر بزرگ باشد؟ و از کجا بدانیم به کف رسیده‌ایم؟</div>
               <p>جوابش در فصل «مدل چطور یاد می‌گیرد؟» است: <b>گرادیان کاهشی</b>. فصل بعد، آمار: داده‌ها چه شکلی‌اند.</p>` },
    ] },
  ],
  sheet: {
    one: 'گرادیان = فهرستِ شیب‌های جزئی، یکی برای هر ورودی؛ هر بار فقط یک ورودی را تکان بده و بقیه را قفل کن. پیکانش رو به تندترین سربالایی است.',
    f: String.raw`\nabla f = \left[\frac{\partial f}{\partial x},\ \frac{\partial f}{\partial y}\right]`,
    rules: ['شیب جزئی: فقط یک ورودی عوض شود، بقیه را عدد ثابت بگیر.', 'گرادیان رو به سربالایی؛ منفیِ گرادیان رو به سرازیری.', 'در قله، کف و زین، گرادیان صفر است.', `دره: ${E(String.raw`x^2 + 2y^2 \to [2x,\ 4y]`)}؛ قیمت خانه: ${E(String.raw`80x - 20y + 500 \to [80,\ -20]`)}.`],
    use: 'گرادیانِ خطا برای هر عددِ قابل تنظیم (Weight) می‌گوید به کدام طرف و چقدر برود. گرادیان کاهشی (Gradient Descent) خلاف آن قدم برمی‌دارد؛ پس‌انتشار خطا (Backpropagation) آن را با قاعده‌ی زنجیره‌ای حساب می‌کند.',
    mistake: `برای پایین رفتن در جهت خودِ گرادیان برویم؛ گرادیان رو به بالاست، پس باید منفی‌اش را رفت. همچنین ورودی دیگر را ثابت نگیریم: در مشتق جزئیِ ${E('x^2 + 3y')} نسبت به x، تکه‌ی ${E('3y')} صفر می‌شود.`,
  },
});
