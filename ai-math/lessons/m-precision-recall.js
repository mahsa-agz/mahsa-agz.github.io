// ---------- Interview mission: Precision vs Recall ----------
// (names start with MPR_ because all lesson files share one global scope)

// 20 people with a fixed model score (0–100): 6 really sick (top row), 14 healthy (bottom row).
// flagged = score at or above the threshold. Checked in node:
// t 40 → TP 6, FP 6 (P 0.5, R 1) · t 60 → TP 5, FP 3, FN 1 (P 0.625, R 0.833, best F1 0.714) · t 75 → TP 3, FP 1 (P 0.75, R 0.5)
// costs: miss 10 / false alarm 1 → best t 45 (cost 5); miss 1 / false alarm 10 → best t 90 and 95 (cost 5)
const MPR_SICK = [45, 60, 72, 80, 88, 95];
const MPR_WELL = [2, 7, 12, 17, 22, 27, 32, 38, 43, 50, 55, 65, 70, 85];
const MPR_pct = p => fa(Math.round(p * 1000) / 10) + '٪';
const MPR_count = t => {
  const tp = MPR_SICK.filter(v => v >= t).length, fp = MPR_WELL.filter(v => v >= t).length;
  return { tp, fp, fn: MPR_SICK.length - tp, tn: MPR_WELL.length - fp };
};
const MPR_TS = Array.from({ length: 19 }, (_, k) => 10 + 5 * k); // the slider's stops: 10 … 100

// draws the two rows of people and the threshold line
const MPR_draw = (g, s) => {
  const { ctx, X, Y, css } = g;
  g.rect(s.t, 0.35, 104, 2.75, 'soft', 0.5);
  [0, 25, 50, 75, 100].forEach(v => { g.line(v, 0.35, v, 0.45, 'muted', 1); g.text(v, 0.35, fa(v), 'muted', 'center', 10); });
  g.line(0, 0.4, 100, 0.4, 'line', 1);
  g.text(0, 2.6, 'واقعاً بیمار', 'ink', 'left', -2);
  g.text(0, 1.4, 'واقعاً سالم', 'ink', 'left', -2);
  const ball = (v, y, sick) => {
    const f = v >= s.t, r = Math.max(5, Math.min(8, (X(5) - X(0)) * 0.42));
    ctx.beginPath(); ctx.arc(X(v), Y(y), r, 0, 7);
    if (sick) {
      ctx.fillStyle = css(f ? 'green' : 'card'); ctx.fill();
      ctx.lineWidth = 3; ctx.strokeStyle = css(f ? 'green' : 'red'); ctx.stroke();
    } else { ctx.fillStyle = css(f ? 'red' : 'muted'); ctx.fill(); }
  };
  MPR_SICK.forEach(v => ball(v, 2.05, true));
  MPR_WELL.forEach(v => ball(v, 0.95, false));
  g.line(s.t, 0.35, s.t, 2.75, 'ink', 2, [6, 4]);
  g.text(s.t, 2.75, `آستانه ${fa(s.t)}`, 'ink', s.t > 80 ? 'right' : s.t < 20 ? 'left' : 'center', 2);
};

// ---- Picture 1: slide the threshold over fixed scores; live precision and recall ----
const MPR_W_THRESH = h => plane(h, {
  x: [-4, 104], y: [0, 3.1], ratio: 0.5,
  state: { t: 50 },
  sliders: [{ key: 't', label: 'آستانه (Threshold):', min: 10, max: 100, step: 5 }],
  draw: MPR_draw,
  read: s => {
    const c = MPR_count(s.t);
    return `<b style="color:var(--green)">مثبتِ درست ${fa(c.tp)}</b>، <b style="color:var(--red)">هشدارِ اشتباه ${fa(c.fp)}</b>، <b style="color:var(--red)">جاافتاده ${fa(c.fn)}</b><br>` +
      `دقت (Precision) = ${fa(c.tp)} از ${fa(c.tp + c.fp)} = <b>${c.tp + c.fp ? MPR_pct(c.tp / (c.tp + c.fp)) : '—'}</b> · ` +
      `بازیابی (Recall) = ${fa(c.tp)} از ${fa(MPR_SICK.length)} = <b>${MPR_pct(c.tp / MPR_SICK.length)}</b>` +
      (c.tp + c.fp ? '' : '<br><span class="muted">هیچ‌کس اعلام نشده؛ دقت تعریف نمی‌شود.</span>');
  },
});

// ---- Picture 2: the same people; pick which mistake is expensive and find the cheapest threshold ----
const MPR_cost = (t, m) => { const c = MPR_count(t); return m ? c.fn + 10 * c.fp : 10 * c.fn + c.fp; };
const MPR_W_COST = h => plane(h, {
  x: [-4, 104], y: [0, 3.1], ratio: 0.5,
  state: { t: 50, m: 0 },
  sliders: [{ key: 't', label: 'آستانه (Threshold):', min: 10, max: 100, step: 5 }],
  buttons: [
    { label: 'جاافتاده ۱۰ برابر گران‌تر', on: s => { s.m = 0; }, active: s => s.m === 0 },
    { label: 'هشدارِ اشتباه ۱۰ برابر گران‌تر', on: s => { s.m = 1; }, active: s => s.m === 1 },
  ],
  draw: MPR_draw,
  read: s => {
    const c = MPR_count(s.t), [a, b] = s.m ? [1, 10] : [10, 1];
    const best = Math.min(...MPR_TS.map(t => MPR_cost(t, s.m)));
    const where = MPR_TS.filter(t => MPR_cost(t, s.m) === best).map(fa).join(' و ');
    return `هزینه = ${fa(a)} × جاافتاده + ${fa(b)} × هشدارِ اشتباه = ${fa(a)} × ${fa(c.fn)} + ${fa(b)} × ${fa(c.fp)} = <b>${fa(MPR_cost(s.t, s.m))}</b><br>` +
      `<span class="muted">ارزان‌ترین آستانه برای این هزینه‌ها: ${where} (هزینه‌ی ${fa(best)})</span>`;
  },
});

const MPR_TABLE = `<table dir="rtl" style="border-collapse:collapse;margin:8px auto;text-align:center;font-size:.92em">
  <tr><td></td><td style="padding:4px 8px"><b>مدل: «مثبت»</b></td><td style="padding:4px 8px"><b>مدل: «منفی»</b></td></tr>
  <tr><td style="padding:4px 8px"><b>واقعاً مثبت</b></td><td style="padding:4px 8px;color:var(--green)">TP</td><td style="padding:4px 8px;color:var(--red)">FN جاافتاده</td></tr>
  <tr><td style="padding:4px 8px"><b>واقعاً منفی</b></td><td style="padding:4px 8px;color:var(--red)">FP هشدارِ اشتباه</td><td style="padding:4px 8px">TN</td></tr></table>`;

lesson({
  id: 'm-precision-recall', node: 'precision-vs-recall', title: 'Precision یا Recall؟', en: 'Precision vs Recall',
  parts: [
    { name: 'سؤال و نردبان', cards: [
      { t: 'text', title: 'سؤالِ مصاحبه',
        body: `<p>مصاحبه‌گر می‌پرسد:</p>
               <div class="key" dir="ltr" style="text-align:left">"When would you prefer precision over recall, and vice versa?"</div>
               <p>یعنی: «کِی دقت (Precision) برایتان مهم‌تر از بازیابی (Recall) است، و کِی برعکس؟»</p>
               <p>اگر الان جوابش را بلد نیستید، اشکالی ندارد. همه‌ی تکه‌هایش را در درس‌های قبل دیده‌اید. قدم به قدم کنارِ هم می‌گذاریم.</p>` },
      { t: 'ladder' },
      { t: 'text', title: 'پله‌ی ۱: دو جور اشتباه',
        body: `<p>از درسِ <b>معیارهای ارزیابی</b> یادمان هست: هر جوابِ مدل در یکی از چهار خانه‌ی جدولِ درهم‌ریختگی ${EN('Confusion Matrix')} می‌افتد.</p>
               ${MPR_TABLE}
               <p>${E(String.raw`P = \frac{TP}{TP + FP}`)}: از اعلام‌شده‌ها چند تا درست؟ هشدارِ اشتباه (FP) آن را پایین می‌کشد.</p>
               <p>${E(String.raw`R = \frac{TP}{TP + FN}`)}: از مثبت‌های واقعی چند تا پیدا شد؟ جاافتاده (FN) آن را پایین می‌کشد.</p>
               <div class="key">سؤالِ مصاحبه در اصل این است: کدام اشتباه گران‌تر است؟</div>` },
      { t: 'play', w: MPR_W_THRESH, title: 'پله‌ی ۲: آستانه هر دو را با هم جابه‌جا می‌کند',
        body: 'هر دایره یک نفر است، جایش امتیازی که مدل به او داده (۰ تا ۱۰۰). ردیفِ بالا ۶ بیمارِ واقعی، ردیفِ پایین ۱۴ سالم. هر کس به <b>آستانه</b> برسد «بیمار» اعلام می‌شود (ناحیه‌ی سایه‌دار). <b style="color:var(--green)">سبز</b> = بیمارِ پیداشده، <b style="color:var(--red)">قرمز</b> = سالمِ ترسانده‌شده، <b style="color:var(--red)">حلقه‌ی خالیِ قرمز</b> = بیمارِ جاافتاده.',
        look: [
          'آستانه را روی ۴۰ بگذارید ← هر ۶ بیمار سبز می‌شوند، ولی ۶ سالم هم قرمزند: دقت ۵۰٪، بازیابی ۱۰۰٪.',
          'آستانه را روی ۷۵ ببرید ← فقط ۱ سالم قرمز می‌ماند، ولی ۳ بیمار جا می‌افتند: دقت ۷۵٪، بازیابی ۵۰٪.',
          'آستانه را روی ۶۰ بگذارید ← ۵ بیمار پیدا، ۳ هشدارِ اشتباه: دقت ۶۲٫۵٪، بازیابی ۸۳٫۳٪.',
          'آستانه را روی ۱۰۰ ببرید ← هیچ‌کس اعلام نمی‌شود؛ بازیابی صفر و دقت اصلاً تعریف نمی‌شود.',
        ],
        see: 'یک دستگیره هر دو عدد را با هم جابه‌جا می‌کند: آستانه بالا ← دقت بیشتر، بازیابی کمتر. پس سؤالِ «کدام بهتر است؟» در واقع سؤالِ «آستانه را کجا بگذاریم؟» است، و جوابش را هزینه‌ی اشتباه‌ها می‌دهد.' },
      { t: 'text', title: 'پله‌ی ۳: نمی‌شود هر دو را مجانی بالا برد',
        body: `<p>در تصویر: آستانه‌ی ۴۰ ← دقت ۵۰٪، بازیابی ۱۰۰٪. آستانه‌ی ۷۵ ← دقت ۷۵٪، بازیابی ۵۰٪.</p>
               <p>از درسِ <b>احتمال شرطی و بیز</b>: دقت یعنی ${E(String.raw`P(\text{sick} \mid \text{flagged})`)} و بازیابی یعنی ${E(String.raw`P(\text{flagged} \mid \text{sick})`)}؛ دو جهتِ متفاوت، با دو مخرجِ متفاوت.</p>
               <div class="key">پس انتخاب را هزینه می‌کند: اگر <b>جاافتادن</b> گران است (سرطانِ جاافتاده)، بازیابی. اگر <b>هشدارِ اشتباه</b> گران است (ایمیلِ مهمی که به اسپم می‌رود)، دقت.</div>` },
      { t: 'quiz', q: 'در تصویر، آستانه‌ی ۶۰: مثبتِ درست ۵، هشدارِ اشتباه ۳، جاافتاده ۱. دقت (Precision) چقدر است؟',
        options: ['۸۳٪', '۶۲٫۵٪', '۳۷٫۵٪'], answer: 1,
        why: 'دقت: از ۸ اعلام‌شده (۵ + ۳)، ۵ تا درست: ۵ از ۸ = ۶۲٫۵٪. «۸۳٪» یعنی ۵ از ۶؛ این بازیابی است (مخرجش همه‌ی بیمارهاست). «۳۷٫۵٪» یعنی ۳ از ۸؛ سهمِ هشدارهای اشتباه را حساب کرده، نه درست‌ها را.' },
    ] },
    { name: 'جواب مصاحبه‌ای', cards: [
      { t: 'answer', lines: [
          'جواب به <b>هزینه‌ی هر اشتباه</b> بستگی دارد: Precision می‌گوید از مواردی که مثبت اعلام کردیم چند تا درست بود، Recall می‌گوید از مثبت‌های واقعی چند تا را پیدا کردیم.',
          'وقتی <b>False Positive</b> گران است، Precision را ترجیح می‌دهم؛ مثلاً spam filter، که نباید ایمیلِ مهم را به اسپم بفرستد.',
          'وقتی <b>False Negative</b> گران است، Recall را ترجیح می‌دهم؛ مثلاً cancer screening، که جا انداختنِ بیمار خطرناک است و هشدارِ اشتباه فقط یک آزمایشِ دوم لازم دارد.',
          'این دو با <b>threshold</b> با هم عوض می‌شوند؛ اگر هر دو مهم باشند، F1 را نگاه می‌کنم یا threshold را از روی PR curve و هزینه‌ها انتخاب می‌کنم.',
        ],
        tip: 'نکته: اول قاعده را بگویید (هزینه‌ی اشتباه)، بعد یک مثال برای هر طرف. مثال نشان می‌دهد که واقعاً فهمیده‌اید.' },
      { t: 'follow', items: [
          { q: 'How do you choose the threshold? (آستانه را چطور انتخاب می‌کنید؟)',
            a: 'سه راه: (۱) از هزینه‌ها: برای هر آستانه، هزینه‌ی کل = هزینه‌ی هر FN × تعدادِ FN + هزینه‌ی هر FP × تعدادِ FP؛ ارزان‌ترین را برمی‌داریم. (۲) از PR curve: مثلاً بیشترین Recall به شرطی که Precision حداقل ۹۰٪ بماند. (۳) از کسب‌وکار: مثلاً تیمِ بررسی فقط روزی ۱۰۰ مورد را می‌تواند ببیند. همیشه روی داده‌ی validation انتخاب می‌کنیم، نه test.' },
          { q: 'What is F1 and why harmonic mean? (F1 چیست و چرا میانگینِ هارمونیک؟)',
            a: `${E(String.raw`F_1 = \frac{2PR}{P + R}`)}. میانگینِ هارمونیک به عددِ کوچک‌تر نزدیک است؛ پس مدلی که همه را مثبت بگوید (${E(String.raw`R = 1,\ P = 0.1`)}) با میانگینِ ساده ۰٫۵۵ می‌گیرد، ولی F1 فقط ${E(String.raw`\frac{2 \times 0.1 \times 1}{1.1} \approx 0.18`)}. F1 فقط وقتی بالاست که هر دو بالا باشند.` },
          { q: 'What about ROC-AUC? (ROC-AUC چه؟)',
            a: 'ROC، Recall را در برابرِ سهمِ منفی‌هایی که اشتباه مثبت شدند (False Positive Rate) برای همه‌ی آستانه‌ها می‌کشد و AUC مساحتِ زیرِ آن است (۱ کامل، ۰٫۵ در حدِ حدسِ شانسی)؛ وقتی مثبت‌ها خیلی نادرند، PR-AUC گویاتر است.' },
        ] },
      { t: 'text', title: 'پله‌ی ۴: وقتی هر دو مهم‌اند (F1)',
        body: `<p>گاهی هیچ‌کدام از دو اشتباه خیلی گران‌تر نیست؛ مثلاً پیدا کردنِ نظرهای منفیِ مشتری‌ها. آن‌وقت یک عدد می‌خواهیم که هر دو را بسنجد.</p>
               <p>از درسِ معیارها: ${E(String.raw`F_1 = \frac{2 \cdot P \cdot R}{P + R}`)}، یعنی میانگینِ هارمونیک ${EN('Harmonic Mean')}.</p>
               <p>در تصویرِ آستانه، بیشترین F1 در آستانه‌ی ۶۰ است: ${E(String.raw`P = \tfrac{5}{8},\ R = \tfrac{5}{6},\ F_1 \approx 0.71`)}.</p>
               <div class="key">F1 فقط وقتی بالاست که <b>هر دو</b> بالا باشند؛ عددِ کوچک‌تر را نمی‌شود با عددِ بزرگ‌تر پنهان کرد.</div>` },
      { t: 'quiz', q: 'مصاحبه‌گر: «فیلتری داریم که ویدیوهای نامناسب را از برنامه‌ی کودکان پنهان می‌کند. پنهان شدنِ یک ویدیوی سالم ضررِ کمی دارد؛ نشان دادنِ یک ویدیوی بد به کودک خیلی بد است.» کدام را جلو می‌گذارید؟',
        options: ['Precision، چون هر ویدیویی که پنهان می‌شود باید واقعاً بد باشد', 'Accuracy، چون بیشترِ ویدیوها سالم‌اند', 'Recall، چون جاافتادنِ ویدیوی بد گران‌ترین اشتباه است', 'F1، چون هر دو را با هم می‌سنجد'], answer: 2,
        why: 'ویدیوی بدی که رد می‌شود یک False Negative است و گران‌ترین اشتباهِ این مسئله؛ پس Recall. Precision وقتی جلو می‌آید که پنهان کردنِ اشتباه گران باشد، که اینجا نیست. Accuracy وقتی ویدیوهای بد کم‌اند گول می‌زند. F1 برای وقتی است که دو اشتباه تقریباً هم‌وزن باشند.' },
      { t: 'play', w: MPR_W_COST, title: 'آستانه را از روی هزینه انتخاب کنید',
        body: 'همان ۲۰ نفر. دکمه‌ها می‌گویند کدام اشتباه ۱۰ برابر گران‌تر است. زیرِ تصویر هزینه‌ی کل حساب می‌شود.',
        look: [
          'دکمه‌ی «جاافتاده ۱۰ برابر گران‌تر»، آستانه ۵۰ ← ۱ جاافتاده و ۵ هشدارِ اشتباه: هزینه ۱۰ × ۱ + ۵ = ۱۵.',
          'آستانه را روی ۴۵ بیاورید ← هیچ بیماری جا نمی‌افتد: هزینه ۵، کمترینِ ممکن.',
          'حالا دکمه‌ی «هشدارِ اشتباه ۱۰ برابر گران‌تر» ← همان آستانه‌ی ۴۵ هزینه‌ی ۵۰ دارد.',
          'آستانه را روی ۹۰ ببرید ← هیچ هشدارِ اشتباهی نیست، ۵ جاافتاده: هزینه ۵.',
        ],
        see: 'وقتی جاافتادن گران است، بهترین آستانه پایین می‌آید (بازیابی بالا). وقتی هشدارِ اشتباه گران است، بالا می‌رود (دقت بالا). این همان جوابِ مصاحبه است، با عدد.' },
    ] },
  ],
  sheet: {
    one: 'به هزینه‌ی اشتباه نگاه کن: وقتی هشدارِ اشتباه (FP) گران است، Precision (مثلِ فیلترِ اسپم)؛ وقتی جاافتادن (FN) گران است، Recall (مثلِ غربالگریِ سرطان)؛ وقتی هر دو مهم‌اند، F1.',
    f: String.raw`P = \frac{TP}{TP + FP} \quad R = \frac{TP}{TP + FN} \quad F_1 = \frac{2PR}{P + R}`,
    rules: ['آستانه بالاتر ← معمولاً Precision بیشتر، Recall کمتر؛ هر دو را مجانی نمی‌شود بالا برد.', 'آستانه را از هزینه‌ها، از PR curve یا از محدودیتِ کسب‌وکار انتخاب کن، روی داده‌ی validation.', 'F1 میانگینِ هارمونیک است و به عددِ کوچک‌تر نزدیک می‌ماند.'],
    use: 'هر مدلِ دسته‌بندی: اسپم، پزشکی، تقلب، فیلترهای ایمنی. یکی از رایج‌ترین سؤال‌های مصاحبه.',
    mistake: 'گفتنِ «همیشه Recall» یا «همیشه Precision» بدونِ حرف زدن از هزینه‌ی هر اشتباه؛ یا جواب دادن با Accuracy.',
  },
});
