// ---------- Interview mission: Imbalanced Data ----------
// (names start with MIMB_ because all lesson files share one global scope)

// 1000 transactions as small squares (40 × 25). Slider = fraud share in %, so frauds = 10 × share.
// Two "dumb" models that never look at the data:
//   m 0 "everything is normal": TP 0 → recall 0, accuracy = 1 − share (1% → 99%)
//   m 1 "everything is fraud":  recall 1, precision = share, accuracy = share
const MIMB_COLS = 40, MIMB_ROWS = 25, MIMB_N = 1000;
const MIMB_pct = p => fa(Math.round(p * 1000) / 10) + '٪';

const MIMB_W_DUMB = h => plane(h, {
  x: [0, MIMB_COLS], y: [0, MIMB_ROWS], equal: true,
  state: { share: 1, m: 0 },
  sliders: [{ key: 'share', label: 'سهمِ تقلب (٪):', min: 1, max: 50, step: 1 }],
  buttons: [
    { label: 'مدلِ تنبل: «همه سالم‌اند»', on: s => { s.m = 0; }, active: s => s.m === 0 },
    { label: 'مدلِ ترسو: «همه تقلب‌اند»', on: s => { s.m = 1; }, active: s => s.m === 1 },
  ],
  draw: (g, s) => {
    const fraud = MIMB_N * s.share / 100;
    for (let k = 0; k < MIMB_N; k++) {
      const col = k % MIMB_COLS, row = MIMB_ROWS - 1 - Math.floor(k / MIMB_COLS), isF = k < fraud;
      // lazy model: frauds are missed (red), normals are correct (soft). Scared model: frauds caught (green), normals false alarms (red).
      const color = s.m ? (isF ? 'green' : 'red') : (isF ? 'red' : 'soft');
      g.rect(col + 0.12, row + 0.12, col + 0.88, row + 0.88, color, s.m && !isF ? 0.35 : 1);
    }
  },
  read: s => {
    const fraud = MIMB_N * s.share / 100, normal = MIMB_N - fraud;
    const head = `از ${fa(MIMB_N)} تراکنش: <b>${fa(fraud)}</b> تقلب، <b>${fa(normal)}</b> سالم.<br>`;
    if (!s.m) return head + `مدلِ تنبل به هیچ تراکنشی نگاه نمی‌کند و می‌گوید «سالم». <b style="color:var(--red)">${fa(fraud)} تقلبِ جاافتاده</b>.<br>` +
      `صحت (Accuracy) = ${fa(normal)} از ${fa(MIMB_N)} = <b>${MIMB_pct(normal / MIMB_N)}</b> · بازیابی (Recall) = ۰ از ${fa(fraud)} = <b style="color:var(--red)">۰٪</b>`;
    return head + `مدلِ ترسو همه را «تقلب» اعلام می‌کند: <b style="color:var(--green)">${fa(fraud)} پیداشده</b>، <b style="color:var(--red)">${fa(normal)} هشدارِ اشتباه</b>.<br>` +
      `صحت = <b>${MIMB_pct(fraud / MIMB_N)}</b> · بازیابی = <b>۱۰۰٪</b> · دقت (Precision) = ${fa(fraud)} از ${fa(MIMB_N)} = <b style="color:var(--red)">${MIMB_pct(fraud / MIMB_N)}</b>`;
  },
});

lesson({
  id: 'm-imbalanced', node: 'imbalanced-data', title: 'با داده نامتوازن چه کنیم؟', en: 'Imbalanced Data',
  parts: [
    { name: 'سؤال و نردبان', cards: [
      { t: 'text', title: 'سؤالِ مصاحبه',
        body: `<p>مصاحبه‌گر می‌پرسد:</p>
               <div class="key" dir="ltr" style="text-align:left">"Your fraud dataset has 1% fraud. How do you handle it?"</div>
               <p>یعنی: «در داده‌ی شما فقط ۱٪ تراکنش‌ها تقلب ${EN('Fraud')} هستند. با آن چه می‌کنید؟» به چنین داده‌ای «نامتوازن» ${EN('Imbalanced')} می‌گویند: یک گروه خیلی کمتر از دیگری است.</p>
               <p>اگر الان جوابش را بلد نیستید، اشکالی ندارد. تکه‌هایش را در درس‌های قبل دیده‌اید.</p>` },
      { t: 'ladder' },
      { t: 'play', w: MIMB_W_DUMB, title: 'پله‌ی ۱: چرا صحت دروغ می‌گوید',
        body: 'از درسِ <b>معیارهای ارزیابی</b>: وقتی یک گروه نادر است، صحت (Accuracy) گول می‌زند. هر مربع یک تراکنش است؛ <b style="color:var(--red)">قرمز</b> = اشتباهِ مدل. با سهمِ ۱٪ شروع کنید: مدلِ تنبل بی‌آنکه چیزی یاد گرفته باشد صحتِ ۹۹٪ دارد و بازیابی‌اش صفر است. سهم را بالا ببرید. بعد مدلِ ترسو را امتحان کنید.' },
      { t: 'text', title: 'پله‌ی ۲: معیارِ درست را انتخاب کن',
        body: `<p>از درسِ معیارها: دقت (Precision) و بازیابی (Recall) اصلاً منفیِ درست (TN) را نمی‌شمارند؛ برای همین ۹۹۰ تراکنشِ سالم گولشان نمی‌زند.</p>
               <p>برای مقایسه‌ی مدل‌ها در همه‌ی آستانه‌ها: مساحتِ زیرِ منحنیِ دقت–بازیابی ${EN('PR-AUC')}.</p>
               <div class="key">مدلی که شانسی امتیاز بدهد، دقتش حدودِ همان سهمِ تقلب است؛ پس PR-AUC آن حدودِ ۰٫۰۱ است. ولی ROC-AUC چنین مدلی همیشه ۰٫۵ است، هر چقدر هم تقلب کم باشد. PR-AUC نشان می‌دهد کارِ واقعاً سخت چقدر خوب انجام شده.</div>` },
      { t: 'text', title: 'پله‌ی ۳: داده را متوازن کن، یا خطا را وزن بده',
        body: `<p><b>نمونه‌گیریِ دوباره</b> ${EN('Resampling')}: از گروهِ بزرگ کمتر برداریم ${EN('Undersampling')}، یا نمونه‌های گروهِ کوچک را تکرار کنیم ${EN('Oversampling')}.</p>
               <p>${EN('SMOTE')}: به جای تکرارِ عینی، بینِ دو تقلبِ نزدیک به هم، یک تقلبِ ساختگیِ تازه می‌سازد.</p>
               <p><b>وزنِ گروه‌ها</b> ${EN('Class Weights')}: از درسِ <b>تابع خطا</b> یادمان هست که مدل میانگینِ خطا را کم می‌کند. اگر خطا روی هر تقلب ۹۹ برابر حساب شود، ۱۰ تقلب × ۹۹ = ۹۹۰، هم‌وزنِ ۹۹۰ تراکنشِ سالم.</p>
               <div class="key">هر سه کار یک پیام دارند: «تقلب را نادیده نگیر».</div>` },
      { t: 'quiz', q: 'از ۱۰۰۰ تراکنش، ۱۰ تا تقلب است. مدل ۲۰ تراکنش را «تقلب» اعلام کرد و ۸ تای آن‌ها واقعاً تقلب بودند. بازیابی (Recall) چقدر است؟',
        options: ['۴۰٪', '۹۸٫۶٪', '۸۰٪'], answer: 2,
        why: 'بازیابی: از ۱۰ تقلبِ واقعی، ۸ تا پیدا شد: ۸۰٪. «۴۰٪» یعنی ۸ از ۲۰؛ این دقت (Precision) است. «۹۸٫۶٪» صحت است: (۸ + ۹۷۸) از ۱۰۰۰؛ بالاست چون ۹۷۸ منفیِ درست آن را بالا نگه داشته‌اند.' },
    ] },
    { name: 'جواب مصاحبه‌ای', cards: [
      { t: 'answer', lines: [
          'اول <b>Accuracy</b> را کنار می‌گذارم، چون مدلی که همیشه بگوید «no fraud» هم ۹۹٪ می‌گیرد؛ به جایش Precision، Recall و <b>PR-AUC</b> را گزارش می‌کنم.',
          'برای تقسیم از <b>stratified</b> split و stratified cross-validation استفاده می‌کنم تا هر بخش همان ۱٪ fraud را داشته باشد.',
          'در training یا <b>class weights</b> می‌دهم، یا resampling می‌کنم: undersampling، oversampling یا SMOTE؛ فقط روی training data.',
          'در آخر <b>threshold</b> را از روی هزینه‌ی fraudِ جاافتاده در برابرِ هزینه‌ی false alarm، روی validation data انتخاب می‌کنم.',
        ],
        tip: 'نکته: ترتیب را نگه دارید: معیار ← تقسیم ← آموزش ← آستانه. این نشان می‌دهد که کلِ مسیر را می‌بینید.' },
      { t: 'follow', items: [
          { q: 'Isn\'t oversampling cheating? (oversampling تقلب نیست؟)',
            a: 'نه، به شرطی که فقط روی training data باشد، و بعد از split. داده‌ی test باید همان ۱٪ دنیای واقعی را داشته باشد. اگر قبل از split oversample کنیم، کپیِ یک تقلب هم در train می‌افتد و هم در test؛ مدل جواب را از قبل دیده و نمره‌اش دروغ است. در cross-validation هم داخلِ هر fold جداگانه انجام می‌شود.' },
          { q: 'Which metric would you report? (کدام معیار را گزارش می‌کنید؟)',
            a: 'Precision و Recall در آستانه‌ی انتخاب‌شده، به‌اضافه‌ی confusion matrix؛ و PR-AUC برای مقایسه‌ی مدل‌ها در همه‌ی آستانه‌ها. اگر کسب‌وکار قید دارد: مثلاً «بیشترین Recall به شرطی که Precision حداقل ۹۰٪ باشد»، یا مستقیم پولی که صرفه‌جویی شد. Accuracy نه.' },
          { q: 'What if you can get more data? (اگر بشود داده‌ی بیشتر گرفت؟)',
            a: 'عالی است، به‌خصوص نمونه‌های بیشتر از گروهِ نادر، یعنی تقلب‌های بیشتر؛ ۱۰ نمونه‌ی تازه‌ی تقلب از ۱۰۰۰ تراکنشِ سالمِ تازه ارزشمندتر است. ولی در دنیای واقعی تقلب باز هم حدودِ ۱٪ می‌ماند؛ پس معیارها، تقسیمِ لایه‌ای و آستانه را هنوز لازم داریم.' },
        ] },
      { t: 'text', title: 'پله‌ی ۴: تقسیمِ لایه‌ای',
        body: `<p>از درسِ <b>اعتبارسنجی متقابل</b>: با ۱۰۰۰ تراکنش و ۱۰ تقلب، اگر داده را شانسی به ۵ دسته تقسیم کنیم، ممکن است یک دسته هیچ تقلبی نداشته باشد و بازیابی‌اش اصلاً حساب نشود.</p>
               <p>تقسیمِ لایه‌ای ${EN('Stratified')} در هر دسته همان ۱٪ را نگه می‌دارد: ۲ تقلب در هر دسته.</p>
               <div class="key">هم در train/test و هم در هر fold، نسبتِ گروه‌ها را نگه دارید.</div>` },
      { t: 'text', title: 'پله‌ی ۵: جابه‌جا کردنِ آستانه',
        body: `<p>از درسِ معیارها: <b>آستانه</b> را می‌شود جابه‌جا کرد. مدلی که روی داده‌ی نامتوازن یاد گرفته، به تقلب‌ها امتیازِ کم می‌دهد؛ آستانه‌ی ۵۰ از ۱۰۰ شاید تقریباً هیچ‌کس را نگیرد.</p>
               <div class="key">آستانه را پایین‌تر ببرید و از روی هزینه‌ی تقلبِ جاافتاده در برابرِ هزینه‌ی هشدارِ اشتباه، روی داده‌ی validation انتخاب کنید.</div>` },
      { t: 'quiz', q: 'مدلتان روی داده‌ی نامتوازن آموزش دیده و با آستانه‌ی پیش‌فرضِ ۰٫۵ تقریباً هیچ تقلبی را نمی‌گیرد (Recall خیلی پایین). اولین کارِ شما چیست؟',
        options: ['آستانه را روی داده‌ی test پایین بیاورم تا Recall بالا برود', 'Accuracy را نگاه کنم؛ چون ۹۹٪ است، مشکلی نیست', 'آستانه را روی داده‌ی validation و از روی هزینه‌ها پایین‌تر ببرم', 'تراکنش‌های سالمِ بیشتری جمع کنم'], answer: 2,
        why: 'مدل به تقلب‌ها امتیازِ کم می‌دهد؛ پایین آوردنِ آستانه Recall را بالا می‌برد، به قیمتِ هشدارِ اشتباهِ بیشتر، و این قیمت را هزینه‌ها تعیین می‌کنند. انتخاب روی test آن را آلوده می‌کند، پس validation. Accuracy همین‌جا گول می‌زند. تراکنشِ سالمِ بیشتر نامتوازنی را بدتر می‌کند.' },
    ] },
  ],
  sheet: {
    one: 'با داده‌ی نامتوازن، Accuracy دروغ می‌گوید (مدلِ «همیشه no fraud» هم ۹۹٪ است)؛ پس Precision، Recall و PR-AUC را بسنج، stratified تقسیم کن، با class weights یا resampling (فقط روی train) به گروهِ نادر وزن بده، و threshold را از روی هزینه‌ها جابه‌جا کن.',
    f: 'P = TP / (TP + FP)  ·  R = TP / (TP + FN)  ·  weight ≈ (normal count) / (fraud count) = 990 / 10 = 99',
    rules: ['مدلِ تنبل روی ۱٪ تقلب: Accuracy = ۹۹٪، Recall = ۰.', 'Resampling و SMOTE فقط روی training data و بعد از split؛ test همان ۱٪ واقعی بماند.', 'PR-AUC مدلِ شانسی ≈ سهمِ گروهِ نادر (۰٫۰۱)؛ ROC-AUC مدلِ شانسی همیشه ۰٫۵.'],
    use: 'کشفِ تقلب، تشخیصِ بیماری‌های نادر، خرابیِ دستگاه‌ها، پیدا کردنِ حمله در شبکه: هر جا که چیزِ مهم نادر است.',
    mistake: 'گزارش دادنِ Accuracy روی داده‌ی نامتوازن؛ و oversampling قبل از split که همان تقلب‌ها را به test هم می‌برد.',
  },
});
