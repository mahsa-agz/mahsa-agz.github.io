// ---------- How Models Learn: Accuracy, Precision, Recall ----------
// (names start with MET_ because all lesson files share one global scope)

// 100 people on a 10×10 grid (index = row * 10 + col). MET_SCORES = the model's fixed score (0–100) for each person:
// "how sure the model is that this person is sick". MET_SICK = the 10 people who are really sick.
const MET_SCORES = [13,10,7,4,88,17,14,24,11,8, 5,2,15,96,12,9,6,3,71,16, 13,10,63,7,4,17,14,91,11,8, 5,84,2,15,12,9,6,3,16,55,
  13,10,7,4,47,17,14,11,79,8, 5,2,43,15,12,9,73,6,3,16, 36,13,10,7,66,4,17,32,14,11, 8,5,59,2,15,12,9,29,6,3,
  16,27,13,10,7,52,4,17,14,11, 38,8,5,2,22,15,12,9,6,19];
const MET_SICK = new Set([7, 13, 27, 31, 48, 56, 64, 72, 85, 90]);
const MET_D = x => String(Math.round(x * 1000) / 1000).replace('.', '٫').replace(/\d/g, d => '۰۱۲۳۴۵۶۷۸۹'[d]);
const MET_pct = p => fa(Math.round(p * 1000) / 10) + '٪';

// flagged = score at or above the threshold. Checked in node: threshold 50 → TP 8, FP 4, FN 2, TN 86.
const MET_count = t => {
  let tp = 0, fp = 0, fn = 0, tn = 0;
  MET_SCORES.forEach((v, i) => { const f = v >= t, s = MET_SICK.has(i); if (s) f ? tp++ : fn++; else f ? fp++ : tn++; });
  const p = tp + fp ? tp / (tp + fp) : 0, r = tp / (tp + fn);
  return { tp, fp, fn, tn, acc: (tp + tn) / 100, p, r, f1: p + r ? 2 * p * r / (p + r) : 0 };
};

// ---- Picture 1: the grid of 100 people with a threshold slider ----
const MET_W_GRID = h => plane(h, {
  x: [0, 10], y: [0, 10], equal: true,
  state: { t: 50 },
  sliders: [{ key: 't', label: 'آستانه (Threshold):', min: 5, max: 95, step: 5 }],
  draw: (g, s) => {
    const { ctx, X, Y, css } = g, r = (X(1) - X(0)) * 0.42;
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.font = `700 ${Math.max(9, Math.round(r * 0.75))}px Vazirmatn, Tahoma, sans-serif`;
    MET_SCORES.forEach((v, i) => {
      const cx = X(i % 10 + 0.5), cy = Y(9.5 - Math.floor(i / 10)), sick = MET_SICK.has(i), f = v >= s.t;
      const fill = f ? (sick ? 'green' : 'red') : 'soft';
      ctx.beginPath(); ctx.arc(cx, cy, r, 0, 7); ctx.fillStyle = css(fill); ctx.fill();
      if (sick) { ctx.lineWidth = 3; ctx.strokeStyle = css(f ? 'ink' : 'red'); ctx.stroke(); }
      ctx.fillStyle = css(f ? 'card' : sick ? 'red' : 'muted');
      ctx.fillText(fa(v), cx, cy + 1);
    });
  },
  read: s => {
    const c = MET_count(s.t);
    return `هر کس امتیازش <b>${fa(s.t)}</b> یا بیشتر است، «بیمار» اعلام می‌شود.<br>` +
      `<b style="color:var(--green)">مثبتِ درست ${fa(c.tp)}</b>، <b style="color:var(--red)">هشدارِ اشتباه ${fa(c.fp)}</b>، ` +
      `<b style="color:var(--red)">جاافتاده ${fa(c.fn)}</b>، منفیِ درست ${fa(c.tn)}<br>` +
      `صحت (Accuracy) = <b>${MET_pct(c.acc)}</b> · دقت (Precision) = <b>${c.tp + c.fp ? MET_pct(c.p) : '—'}</b> · بازیابی (Recall) = <b>${MET_pct(c.r)}</b><br>` +
      `<span class="muted">مدلِ تنبلِ «همه سالم‌اند» هم صحتِ ۹۰٪ دارد.</span>`;
  },
});

// ---- Picture 2: precision–recall curve from the same 100 people; marker = current threshold ----
const MET_TS = Array.from({ length: 19 }, (_, k) => 5 + 5 * k);
const MET_PTS = MET_TS.map(t => { const c = MET_count(t); return [c.r, c.p, t]; });

const MET_W_PR = h => plane(h, {
  x: [-0.16, 1.08], y: [-0.14, 1.12], ratio: 0.85,
  state: { t: 50 },
  sliders: [{ key: 't', label: 'آستانه (Threshold):', min: 5, max: 95, step: 5 }],
  handles: [{
    get: s => { const c = MET_count(s.t); return [c.r, c.p]; },
    set: (s, x, y) => { let best = 1e9; MET_PTS.forEach(([r, p, t]) => { const d = (r - x) ** 2 + (p - y) ** 2; if (d < best) { best = d; s.t = t; } }); },
    color: 'orange',
  }],
  draw: (g, s) => {
    [0, 0.5, 1].forEach(v => {
      g.line(0, v, 1, v, v ? 'soft' : 'line', v ? 1 : 2); g.line(v, 0, v, 1, v ? 'soft' : 'line', v ? 1 : 2);
      g.text(-0.03, v, fa(v), 'muted', 'right', 0); g.text(v, 0, fa(v), 'muted', 'center', 14);
    });
    g.text(1, 0, 'Recall', 'blue', 'right', 30);
    g.text(0.02, 1.08, 'Precision', 'green', 'left', 0);
    for (let k = 1; k < MET_PTS.length; k++) g.line(MET_PTS[k - 1][0], MET_PTS[k - 1][1], MET_PTS[k][0], MET_PTS[k][1], 'orange', 3);
    MET_PTS.forEach(([r, p]) => g.dot(r, p, 'orange', 3.5));
    const c = MET_count(s.t);
    g.text(c.r, c.p, `آستانه ${fa(s.t)}`, 'ink', c.r > 0.6 ? 'right' : 'left', -20);
  },
  read: s => {
    const c = MET_count(s.t);
    return `آستانه <b>${fa(s.t)}</b>: مثبتِ درست ${fa(c.tp)}، هشدارِ اشتباه ${fa(c.fp)}، جاافتاده ${fa(c.fn)}<br>` +
      `<b style="color:var(--green)">P = ${MET_D(c.p)}</b> · <b style="color:var(--blue)">R = ${MET_D(c.r)}</b> · ` +
      `<b>F1 = ${MET_D(c.f1)}</b> <span class="muted">(میانگینِ ساده: ${MET_D((c.p + c.r) / 2)})</span>`;
  },
});

const MET_TABLE = `<table dir="rtl" style="border-collapse:collapse;margin:8px auto;text-align:center;font-size:.92em">
  <tr><td></td><td style="padding:4px 8px"><b>مدل: «بیمار»</b></td><td style="padding:4px 8px"><b>مدل: «سالم»</b></td></tr>
  <tr><td style="padding:4px 8px"><b>واقعاً بیمار</b></td><td style="padding:4px 8px;color:var(--green)">مثبتِ درست<br>TP</td><td style="padding:4px 8px;color:var(--red)">جاافتاده<br>FN</td></tr>
  <tr><td style="padding:4px 8px"><b>واقعاً سالم</b></td><td style="padding:4px 8px;color:var(--red)">هشدارِ اشتباه<br>FP</td><td style="padding:4px 8px">منفیِ درست<br>TN</td></tr></table>`;

lesson({
  id: 'metrics', node: 'accuracy-precision-recall', title: 'معیارهای ارزیابی', en: 'Accuracy, Precision, Recall',
  parts: [
    { name: 'چرا و یعنی چه؟', cards: [
      { t: 'story', title: `مدلِ «۹۹٪ درست» ${EN('Accuracy')}`,
        body: `<p>شرکتی می‌گوید: «مدلِ ما سرطان را تشخیص می‌دهد و ۹۹٪ وقت‌ها درست می‌گوید.» عالی به نظر می‌رسد.</p>
               <p>ولی از هر ۱۰۰ نفری که آزمایش می‌دهند، فقط ۱ نفر سرطان دارد. مدلی که <b>بدون نگاه کردن</b> به هر کس بگوید «سالمی»، ۹۹ نفر از ۱۰۰ را درست گفته: آن هم ۹۹٪ درست است! و حتی یک بیمار را هم پیدا نمی‌کند.</p>
               <div class="key">وقتی یک گروه <b>نادر</b> است، «درصدِ جواب‌های درست» دروغ می‌گوید. سؤال‌های تیزتری لازم داریم.</div>` },
      { t: 'text', title: `جدولِ درهم‌ریختگی ${EN('Confusion Matrix')}`,
        body: `<p>به چیزی که دنبالش هستیم (بیمار، اسپم، تقلب) «<b>مثبت</b>» ${EN('Positive')} می‌گوییم. هر جوابِ مدل در یکی از چهار خانه می‌افتد:</p>
               ${MET_TABLE}
               <p><b>TP</b> مثبتِ درست (True Positive) · <b>FP</b> هشدارِ اشتباه (False Positive) · <b>FN</b> جاافتاده (False Negative) · <b>TN</b> منفیِ درست (True Negative)</p>
               <div class="key">دو جور اشتباه داریم: آدمِ سالم را بترسانیم (FP)، یا بیمار را جا بیندازیم (FN).</div>` },
      { t: 'text', title: 'دو سؤالِ تیزتر',
        body: `<p><b>صحت</b> ${EN('Accuracy')}: از همه‌ی جواب‌ها، چند تا درست بود؟ همان «۹۹٪» که گولمان زد.</p>
               <div class="key"><b>دقت</b> ${EN('Precision')}: از کسانی که مدل «بیمار» اعلام کرد، چند نفر واقعاً بیمار بودند؟</div>
               <div class="key"><b>بازیابی</b> ${EN('Recall')}: از همه‌ی بیمارهای واقعی، مدل چند نفر را پیدا کرد؟</div>
               <p>مدلِ «همه سالم‌اند» بازیابیِ <b>صفر</b> دارد: هیچ بیماری را پیدا نکرد. دروغش لو رفت.</p>
               <p class="muted">توجه: در بعضی کتاب‌ها فارسیِ این اسم‌ها جابه‌جا شده (مثلاً Accuracy را «دقت» می‌نویسند). همیشه انگلیسی را نگاه کنید.</p>` },
      { t: 'play', w: MET_W_GRID, title: '۱۰۰ نفر و یک آستانه',
        body: 'هر دایره یک نفر؛ عددش امتیازی است که مدل داده: «چقدر مطمئنم که بیمار است». ۱۰ نفر با <b>حلقه</b> واقعاً بیمارند. هر کس امتیازش به <b>آستانه</b> (Threshold)، یعنی خطِ برشی که ما می‌گذاریم، برسد یا بالاتر باشد، «بیمار» اعلام می‌شود. <b style="color:var(--green)">سبز</b> = بیمارِ پیداشده، <b style="color:var(--red)">قرمز</b> = سالمِ ترسانده‌شده، <b style="color:var(--red)">حلقه‌ی قرمز</b> = بیمارِ جاافتاده. آستانه را پایین و بالا ببرید: دقت و بازیابی چه می‌کنند؟' },
      { t: 'sort', title: 'اینجا کدام مهم‌تر است؟', yes: 'بازیابی (Recall)', no: 'دقت (Precision)', items: [
        { q: 'آزمایشِ اولیه‌ی سرطان در یک شهر', a: true, why: 'جا انداختنِ یک بیمار ممکن است جانش را بگیرد. هشدارِ اشتباه فقط یک آزمایشِ دوم لازم دارد.' },
        { q: 'فیلترِ اسپمِ ایمیل', a: false, why: 'هر ایمیلی که اسپم اعلام می‌شود باید واقعاً اسپم باشد؛ گم شدنِ یک ایمیلِ واقعی گران است.' },
        { q: 'سیستمی که با شکِ تقلب، کارتِ بانکیِ مشتری را می‌بندد', a: false, why: 'هر بستنِ اشتباه، مشتریِ بی‌گناه را وسطِ خرید بی‌پول می‌گذارد و عصبانی می‌کند.' },
        { q: 'پیدا کردنِ همه‌ی افرادِ یک فهرستِ تحتِ تعقیب در دوربین‌ها', a: true, why: 'نباید کسی از فهرست جا بماند؛ هشدارهای اشتباه را یک مأمور بعداً با چشم بررسی می‌کند.' },
        { q: 'پیشنهادِ ۵ فیلم در صفحه‌ی اولِ یک برنامه', a: false, why: 'فقط ۵ جا داریم؛ هر کدام باید واقعاً به دلِ بیننده بنشیند. لازم نیست همه‌ی فیلم‌های خوب را نشان دهیم.' },
      ] },
      { t: 'quiz', q: 'در شهری ۳۰ بیمار هست. مدل ۲۰ نفر را «بیمار» اعلام کرد و ۱۵ نفرِ آن‌ها واقعاً بیمار بودند. دقتِ مدل (Precision) چقدر است؟',
        options: ['۵۰٪', '۷۵٪', '۶۷٪'], answer: 1,
        why: 'دقت: از اعلام‌شده‌ها چند تا درست؟ ۱۵ از ۲۰ = ۷۵٪. «۵۰٪» یعنی ۱۵ از ۳۰؛ این بازیابی (Recall) است. «۶۷٪» یعنی ۲۰ از ۳۰؛ اعلام‌شده‌ها را با بیمارها مقایسه کرده، نه درست‌ها را.' },
    ] },
    { name: 'فرمول', cards: [
      { t: 'formula', title: `دقت ${EN('Precision')}`,
        intro: `<p>اول صحت: درست‌ها تقسیم بر همه. ${E('Accuracy = (TP + TN) / (TP + FP + FN + TN)')}</p><p>حالا دقت: فقط ستونِ «مدل: بیمار» را نگاه می‌کنیم.</p>`,
        toks: [{ s: 'P', c: 'green', l: 'دقت' }, { s: '=' }, { s: 'TP', c: 'green', l: 'مثبتِ درست' },
               { s: '/' }, { s: '(TP + FP)', c: 'orange', l: 'همه‌ی اعلام‌شده‌ها' }],
        read: 'خوانده می‌شود: «دقت برابر است با مثبت‌های درست، تقسیم بر همه‌ی کسانی که مدل مثبت اعلام کرد».',
        note: '<p>هشدارِ اشتباه (FP) در مخرج است؛ هر هشدارِ اشتباه دقت را پایین می‌کشد.</p>' },
      { t: 'formula', title: `بازیابی ${EN('Recall')}`,
        intro: '<p>این بار فقط ردیفِ «واقعاً بیمار» را نگاه می‌کنیم.</p>',
        toks: [{ s: 'R', c: 'blue', l: 'بازیابی' }, { s: '=' }, { s: 'TP', c: 'green', l: 'مثبتِ درست' },
               { s: '/' }, { s: '(TP + FN)', c: 'blue', l: 'همه‌ی بیمارهای واقعی' }],
        read: 'خوانده می‌شود: «بازیابی برابر است با مثبت‌های درست، تقسیم بر همه‌ی مثبت‌های واقعی».',
        note: `<p>صورت همان TP است؛ فقط مخرج فرق دارد. اینجا جاافتاده (FN) بازیابی را پایین می‌کشد. اسمِ دیگرش «حساسیت» ${EN('Sensitivity')} است، همان که پزشک‌ها برای آزمایش می‌گویند.</p>` },
      { t: 'formula', title: `امتیازِ F1 ${EN('F1 Score')}`,
        intro: '<p>دو عدد داریم؛ گاهی یک عدد می‌خواهیم که هر دو را با هم بسنجد.</p>',
        toks: [{ s: 'F1', c: 'red', l: 'امتیازِ ترکیبی' }, { s: '=' }, { s: '2 · P · R', c: 'green', l: 'دو برابرِ ضربِ دقت و بازیابی' },
               { s: '/' }, { s: '(P + R)', c: 'blue', l: 'جمعِ دقت و بازیابی' }],
        read: `به این «میانگینِ هارمونیک» ${EN('Harmonic Mean')} می‌گویند.`,
        note: `<p><b>چرا میانگینِ ساده نه؟</b> مدلی که همه را «بیمار» بگوید: ${E('R = 1')} و مثلاً ${E('P = 0.1')}. میانگینِ ساده ۰٫۵۵ می‌شود؛ خوب به نظر می‌رسد! ولی ${E('F1 = 0.2 / 1.1 ≈ 0.18')}.</p><div class="key">F1 فقط وقتی بالاست که <b>هر دو</b> بالا باشند.</div>` },
      { t: 'text', title: 'با عدد امتحان کنیم',
        body: `<p>همان ۱۰۰ نفرِ تصویر با آستانه‌ی ۵۰: ${E('TP = 8, FP = 4, FN = 2, TN = 86')}</p>
               <p>${E('Accuracy = (8 + 86) / 100 = 0.94')}</p>
               <p>${E('P = 8 / (8 + 4) = 8 / 12 ≈ 0.667')}</p>
               <p>${E('R = 8 / (8 + 2) = 8 / 10 = 0.8')}</p>
               <p class="read">${E('F1 = 2 × 0.667 × 0.8 / (0.667 + 0.8) ≈ 1.067 / 1.467 ≈ 0.727')}</p>
               <div class="key">صحتِ ۹۴٪ خیلی خوب به نظر می‌رسد. ولی از هر ۳ هشدار، ۱ تا اشتباه است و ۲ بیمار از ۱۰ جا مانده‌اند.</div>` },
      { t: 'play', w: MET_W_PR, title: 'منحنیِ دقت–بازیابی',
        body: `همان ۱۰۰ نفر. هر نقطه‌ی <b style="color:var(--orange)">نارنجی</b> یک آستانه است: افقی = <b style="color:var(--blue)">بازیابی</b>، عمودی = <b style="color:var(--green)">دقت</b>. این منحنیِ دقت–بازیابی ${EN('Precision–Recall Curve')} است. دایره را روی منحنی بکشید یا لغزنده را ببرید. کدام آستانه بیشترین F1 را دارد؟ مدلِ کامل در گوشه‌ی بالا-راست (۱، ۱) بود.` },
      { t: 'rules', title: 'سه قانون مهم', items: [
        { r: 'آستانه را <b>بالا</b> ببرید: دقت معمولاً <b>بالا</b> می‌رود و بازیابی <b>پایین</b> می‌آید.',
          why: 'فقط آن‌هایی اعلام می‌شوند که مدل خیلی مطمئن است؛ هشدارِ اشتباه کم می‌شود، ولی بیمارهای با امتیازِ کمتر جا می‌مانند. «معمولاً»، چون گاهی یک سالمِ امتیازبالا همه را به هم می‌زند (در تصویر، آستانه‌ی ۵۵).' },
        { r: 'وقتی یک گروه <b>نادر</b> است، به دقت و بازیابی نگاه کنید، نه صحت.',
          why: 'منفی‌های درست (TN) آن‌قدر زیادند که صحت را بالا نگه می‌دارند، حتی برای مدلی که هیچ بیماری را پیدا نمی‌کند. TN در فرمولِ دقت و بازیابی اصلاً نیست.' },
        { r: 'معیار را از <b>هزینه‌ی هر اشتباه</b> انتخاب کنید.',
          why: 'ریاضی نمی‌گوید کدام اشتباه بدتر است؛ زندگی می‌گوید. جا انداختنِ سرطان ← بازیابی. بستنِ کارتِ بی‌گناه ← دقت.' },
      ] },
      { t: 'ai', title: 'معیارهای ارزیابی در هوش مصنوعی',
        body: `<p>هر مدلِ دسته‌بندی ${EN('Classifier')} همین‌طور سنجیده می‌شود: فیلترِ اسپم، تشخیصِ پزشکی از عکس، کشفِ تقلبِ بانکی، و فیلترهای ایمنیِ ChatGPT که درخواستِ خطرناک را می‌گیرند (بی‌آنکه سؤال‌های عادی را رد کنند).</p>
               <p>یک ابزارِ دیگر: منحنیِ ${EN('ROC')} همان آستانه‌ها را می‌گردد، ولی بازیابی را در برابرِ «سهمِ سالم‌های ترسانده‌شده» می‌کشد؛ مساحتِ زیرش ${EN('AUC')} است: ۱ یعنی کامل، ۰٫۵ یعنی مثلِ شیر یا خط.</p>
               <p>«Precision یا Recall؟» از محبوب‌ترین سؤال‌های مصاحبه است. به‌زودی در مأموریت‌ها جوابش را می‌سازیم.</p>` },
      { t: 'quiz', q: 'مدلی فقط وقتی کاملاً مطمئن است «بیمار» می‌گوید: دقت = ۱ و بازیابی = ۰٫۲. F1 تقریباً چقدر است؟',
        options: ['۰٫۶', '۱', '۰٫۳۳', '۰٫۲'], answer: 2,
        why: `${E('F1 = 2 × 1 × 0.2 / (1 + 0.2) = 0.4 / 1.2 ≈ 0.33')}. «۰٫۶» میانگینِ ساده است؛ ضعفِ بازیابی را پنهان می‌کند. «۱» فقط دقت را دیده. «۰٫۲» فقط عددِ کوچک‌تر است؛ F1 همیشه کمی بیشتر از آن است.` },
    ] },
  ],
  sheet: {
    one: 'صحت (Accuracy) وقتی یک گروه نادر است دروغ می‌گوید: مدلِ «همه سالم‌اند» هم ۹۹٪ درست است. برای همین دو سؤالِ تیزتر ساخته شد: دقت (Precision) = از اعلام‌شده‌ها چند تا درست؟ بازیابی (Recall) = از مثبت‌های واقعی چند تا پیدا شد؟',
    f: 'Accuracy = (TP + TN) / همه  ·  P = TP / (TP + FP)  ·  R = TP / (TP + FN)  ·  F1 = 2·P·R / (P + R)',
    rules: ['جدولِ درهم‌ریختگی (Confusion Matrix): مثبتِ درست TP، هشدارِ اشتباه FP، جاافتاده FN، منفیِ درست TN.', 'آستانه بالاتر ← معمولاً دقت بیشتر، بازیابی کمتر.', 'گروهِ نادر ← به دقت و بازیابی نگاه کن، نه صحت.', 'هزینه‌ی هر اشتباه، معیار را انتخاب می‌کند: سرطان ← بازیابی، اسپم ← دقت.', 'F1 میانگینِ هارمونیک است: فقط وقتی هر دو بالا باشند بالاست.'],
    use: 'سنجیدنِ هر مدلِ دسته‌بندی (Classifier): اسپم، پزشکی، تقلب، فیلترهای ایمنی. منحنیِ دقت–بازیابی و ROC/AUC برای انتخابِ آستانه. سؤالِ همیشگیِ مصاحبه: Precision یا Recall؟',
    mistake: 'به صحتِ بالا روی داده‌ی نامتوازن دل خوش کردن. و جابه‌جا کردنِ مخرج‌ها: دقت بر «اعلام‌شده‌ها» (TP + FP) تقسیم می‌شود، بازیابی بر «مثبت‌های واقعی» (TP + FN).',
  },
});
