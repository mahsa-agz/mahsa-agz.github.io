// ---------- Interview mission: Why scale attention by √d? ----------
// (names start with MSQD_ because all lesson files share one global scope)

// fixed-seed random numbers (mulberry32) and normal samples (Box–Muller): mean 0, variance 1
const MSQD_rand = (a => () => { a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; })(20240517);
const MSQD_randn = () => Math.sqrt(-2 * Math.log(1 - MSQD_rand())) * Math.cos(2 * Math.PI * MSQD_rand());

// one query and 200 keys, 512 numbers each; a slider value d uses the first d numbers of each
const MSQD_DMAX = 512, MSQD_NK = 200, MSQD_NW = 6;
const MSQD_Q = Array.from({ length: MSQD_DMAX }, MSQD_randn);
const MSQD_K = Array.from({ length: MSQD_NK }, () => Array.from({ length: MSQD_DMAX }, MSQD_randn));
const MSQD_softmax = z => { const m = Math.max(...z), e = z.map(v => Math.exp(v - m)), s = e.reduce((a, b) => a + b, 0); return e.map(v => v / s); };
const MSQD_std = a => { const m = a.reduce((x, y) => x + y, 0) / a.length; return Math.sqrt(a.reduce((x, y) => x + (y - m) ** 2, 0) / a.length); };
const MSQD_pct = w => (w < 0.0005 ? 'کمتر از ۰٫۱٪' : fa(Math.round(w * 1000) / 10) + '٪');
const MSQD_cache = {};
const MSQD_scores = d => MSQD_cache[d] || (MSQD_cache[d] = MSQD_K.map(k => { let t = 0; for (let i = 0; i < d; i++) t += MSQD_Q[i] * k[i]; return t; }));
// checked in node (this seed): raw std ≈ √d for every d (e.g. d 64 → about 8, d 512 → about 22);
// without scaling the largest of the 6 weights is near 100% from d ≈ 64 on; with scaling it stays a soft mix

const MSQD_W_SPREAD = h => plane(h, {
  x: [-80, 80], y: [0, 12.4], ratio: 0.85,
  state: { d: 64 },
  sliders: [{ key: 'd', label: 'طولِ بردارها (d):', min: 1, max: MSQD_DMAX, step: 1 }],
  draw: (g, s) => {
    const raw = MSQD_scores(s.d), r = Math.sqrt(s.d), sc = raw.map(v => v / r);
    // two strips of dots: raw scores and scores ÷ √d, on the same number line
    [[raw, 11, 'امتیازِ خام'], [sc, 8.4, 'امتیاز ÷ √d']].forEach(([a, y, name]) => {
      const sd = MSQD_std(a);
      g.rect(-Math.min(sd, 78), y - 0.9, Math.min(sd, 78), y + 0.9, 'soft', 0.8);
      g.line(-78, y, 78, y, 'line', 1);
      a.forEach((v, j) => {
        const out = Math.abs(v) > 78, x = Math.max(-78, Math.min(78, v));
        g.dot(x, y + (((j * 37) % 11) / 10 - 0.5) * 1.4, out ? 'red' : 'blue', 2.5);
      });
      g.text(78, y + 0.9, name, 'ink', 'right', -8);
    });
    [-60, -30, 0, 30, 60].forEach(v => g.text(v, 7.4, fa(v), 'muted', 'center', 0));
    // softmax weights of the first 6 words, without and with scaling
    const groups = [[MSQD_softmax(raw.slice(0, MSQD_NW)), -76, 'بدونِ تقسیم', 'red'], [MSQD_softmax(sc.slice(0, MSQD_NW)), 6, 'با تقسیم بر √d', 'green']];
    g.line(-78, 0.6, 78, 0.6, 'line', 2);
    groups.forEach(([w, x0, name, col]) => {
      const top = w.indexOf(Math.max(...w));
      w.forEach((v, i) => {
        const x = x0 + i * 12;
        g.rect(x, 0.6, x + 8.5, 0.6 + 5 * v, col, 0.85);
        if (i === top) g.text(x + 4.25, 0.6 + 5 * v, MSQD_pct(v), 'ink', 'center', -9);
      });
      g.text(x0 + 35, 6.6, name, col, 'center', 0);
    });
  },
  read: s => {
    const raw = MSQD_scores(s.d), r = Math.sqrt(s.d), sc = raw.map(v => v / r);
    const m1 = Math.max(...MSQD_softmax(raw.slice(0, MSQD_NW))), m2 = Math.max(...MSQD_softmax(sc.slice(0, MSQD_NW)));
    return `d = ${fa(s.d)}، ${E(`√d ≈ ${fa(r)}`)}<br>` +
      `پراکندگیِ ${fa(MSQD_NK)} امتیازِ تصادفی: انحراف معیارِ خام ≈ <b style="color:var(--red)">${fa(MSQD_std(raw))}</b> (انتظار: √d)، بعد از تقسیم ≈ <b style="color:var(--green)">${fa(MSQD_std(sc))}</b> (انتظار: ۱)<br>` +
      `بزرگ‌ترین وزنِ سافت‌مکس: بدونِ تقسیم <b>${MSQD_pct(m1)}</b>، با تقسیم <b>${MSQD_pct(m2)}</b>` +
      (m1 > 0.95 ? '<br><span class="muted">بدونِ تقسیم تقریباً همه‌ی وزن روی یک کلمه است؛ بقیه تقریباً هیچ.</span>' : '');
  },
});

lesson({
  id: 'm-attention-sqrt-d', node: 'why-scale-attention-by-d', title: 'چرا تقسیم بر √d در توجه؟', en: 'Why scale attention by √d?',
  parts: [
    { name: 'سؤال و نردبان', cards: [
      { t: 'text', title: 'سؤالِ مصاحبه',
        body: `<p>مصاحبه‌گر می‌پرسد:</p>
               <div class="key" dir="ltr" style="text-align:left">"In scaled dot-product attention, why do we divide QKᵀ by √d<sub>k</sub>?"</div>
               <p>یعنی: «در فرمولِ توجه ${EN('Scaled Dot-Product Attention')}، چرا امتیازهای ${E('Q · Kᵀ')} را بر ${E('√d')} تقسیم می‌کنیم؟» (${E('d<sub>k</sub>')} همان d است: تعدادِ عددهای هر بردارِ برچسب.)</p>
               <p>اگر الان جوابش را بلد نیستید، اشکالی ندارد. همه‌ی تکه‌هایش را در درس‌های قبل دیده‌اید. قدم به قدم کنارِ هم می‌گذاریم.</p>` },
      { t: 'ladder' },
      { t: 'text', title: 'پله‌ی ۱: امتیاز، جمعِ d حاصل‌ضرب است',
        body: `<p>از درسِ <b>ضرب داخلی</b>: خانه‌های هم‌جا را ضرب و همه را جمع می‌کنیم.</p>
               <p class="read">${E('q · k = q₁k₁ + q₂k₂ + … + q<sub>d</sub>k<sub>d</sub>')}</p>
               <p>در درسِ <b>سازوکار توجه</b>، هر امتیاز همین بود: پرسشِ یک کلمه ضرب داخلی در برچسبِ کلمه‌ای دیگر.</p>
               <p>اولِ آموزش، عددهای q و k تقریباً <b>تصادفی</b>‌اند: میانگینِ ۰ و واریانسِ ۱. پس هر حاصل‌ضربِ ${E('qᵢkᵢ')} هم یک عددِ تصادفی دورِ ۰ است، با واریانسِ ۱.</p>
               <div class="key">امتیاز = جمعِ d عددِ تصادفی. هر چه d بزرگ‌تر، تعدادِ جمع‌شونده‌ها بیشتر.</div>` },
      { t: 'text', title: 'پله‌ی ۲: واریانس‌ها جمع می‌شوند',
        body: `<p>از درسِ <b>پراکندگی</b>: واریانس = میانگینِ انحراف‌ها به توان ۲، و انحراف معیار جذرِ آن.</p>
               <p>کوچک امتحان کنیم: هر حاصل‌ضرب ${E('+1')} یا ${E('−1')} با شانسِ برابر (واریانسِ ۱). جمعِ <b>دو</b> تا: ${E('2، 0، 0، −2')}. واریانس = ${E('(4 + 0 + 0 + 4) / 4 = 2')}.</p>
               <div class="key">وقتی عددهای تصادفیِ مستقل جمع می‌شوند، واریانس‌هایشان <b>جمع</b> می‌شوند: واریانسِ امتیاز = d، و اندازه‌ی معمولش (انحراف معیار) = ${E('√d')}.</div>
               <p>بخشی از حاصل‌ضرب‌ها همدیگر را خنثی می‌کنند؛ برای همین ${E('√d')}، نه d. با d = ۶۴، امتیازها معمولاً حدودِ ±۸ و گاهی ±۱۶ یا بیشترند.</p>` },
      { t: 'play', w: MSQD_W_SPREAD, title: 'پله‌ی ۳: d را بزرگ کنید',
        body: 'یک پرسش و ۲۰۰ برچسبِ تصادفی (همیشه همان‌ها). هر نقطه‌ی <b style="color:var(--blue)">آبی</b> یک امتیاز است؛ نوارِ کم‌رنگ = ± یک انحراف معیار. ردیفِ بالا خام، ردیفِ دوم تقسیم بر √d. پایین: وزن‌های سافت‌مکس برای ۶ کلمه‌ی اول، <b style="color:var(--red)">بدون</b> و <b style="color:var(--green)">با</b> تقسیم. d را از ۱ تا ۵۱۲ ببرید.' },
      { t: 'quiz', q: 'd = ۲۵۶ و عددهای q و k تصادفی با میانگینِ ۰ و واریانسِ ۱. امتیازِ خام (بدونِ تقسیم) معمولاً چه اندازه‌ای دارد؟',
        options: ['حدودِ ۲۵۶', 'حدودِ ۱۶', 'حدودِ ۱'], answer: 1,
        why: 'واریانسِ امتیاز d = ۲۵۶ است و اندازه‌ی معمول (انحراف معیار) جذرِ آن: √۲۵۶ = ۱۶. «۲۵۶» واریانس را با انحراف معیار قاطی کرده. «۱» اندازه‌ی امتیاز <b>بعد</b> از تقسیم بر √d است.' },
    ] },
    { name: 'جواب مصاحبه‌ای', cards: [
      { t: 'answer', lines: [
          'اگر اجزای q و k مستقل با <b>mean 0</b> و <b>variance 1</b> باشند، dot product ِ q·k جمعِ d<sub>k</sub> حاصل‌ضربِ مستقل است؛ پس variance آن d<sub>k</sub> و انحراف معیارش <b>√d<sub>k</sub></b> می‌شود.',
          'با d<sub>k</sub> بزرگ (مثلاً ۶۴ یا ۵۱۲)، scoreها بزرگ می‌شوند و <b>softmax</b> تقریباً <b>one-hot</b> می‌شود.',
          'آن‌جا softmax <b>saturate</b> است و gradientها تقریباً صفرند، مثلِ vanishing gradient؛ training کند و ناپایدار می‌شود.',
          'تقسیم بر √d<sub>k</sub>، variance ِ scoreها را دوباره <b>۱</b> می‌کند، مستقل از d<sub>k</sub>، تا softmax در ناحیه‌ی نرم بماند.',
        ],
        tip: 'نکته: زنجیره را کامل بگویید: variance = d ← scoreهای بزرگ ← softmax تیز ← gradient کوچک ← تقسیم بر √d. گفتنِ فقط «برای پایداری» نیمی از جواب است.' },
      { t: 'follow', items: [
          { q: 'Why √d and not d? (چرا √d و نه d؟)',
            a: 'تقسیم بر c واریانس را c² برابر کوچک می‌کند: d / c². برای اینکه ۱ شود، c = √d. اگر بر d تقسیم کنیم واریانس 1/d می‌شود؛ با d = ۶۴ امتیازها حدودِ ±۰٫۱۲۵‌اند و سافت‌مکس تقریباً مساوی پخش می‌کند: توجه اولِ کار نمی‌تواند روی چیزی تمرکز کند.' },
          { q: 'What would happen without it in training? (بدونِ آن در آموزش چه می‌شد؟)',
            a: 'از همان اول، هر کلمه تقریباً فقط به یک کلمه‌ی تصادفی نگاه می‌کرد و گرادیانِ ماتریس‌های W<sub>Q</sub> و W<sub>K</sub> نزدیکِ صفر بود؛ پس آموزش کُند، ناپایدار و حساس به learning rate می‌شد. مقاله‌ی «Attention Is All You Need» (۲۰۱۷) همین را دلیلش گفته: ضرب داخلی با d بزرگ، سافت‌مکس را به ناحیه‌ای با گرادیانِ بسیار کوچک می‌برد.' },
          { q: 'What is "temperature" in sampling? (دما در نمونه‌گیری چیست؟)',
            a: 'همان ایده، در خروجیِ مدلِ زبانی: امتیازِ کلمه‌های بعدی را قبل از سافت‌مکس بر T تقسیم می‌کنیم. T کمتر از ۱ ← سافت‌مکس تیزتر، جواب‌ها قابلِ پیش‌بینی‌تر؛ T بیشتر از ۱ ← نرم‌تر، جواب‌ها متنوع‌تر. در توجه، √d یک «دمای» ثابت است که d را خنثی می‌کند.' },
        ] },
      { t: 'quiz', q: 'همکارتان d<sub>k</sub> = ۱۰۲۴ گذاشته و تقسیم بر √d را جا انداخته. اولِ آموزش چه می‌بینید؟',
        options: ['فرقی نمی‌کند، چون سافت‌مکس جمعِ وزن‌ها را به هر حال ۱ می‌کند', 'وزن‌های توجه تقریباً مساوی می‌شوند', 'وزن‌ها تقریباً یک‌داغ‌اند و گرادیانِ Q و K نزدیکِ صفر'], answer: 2,
        why: 'امتیازها اندازه‌ای حدودِ √۱۰۲۴ = ۳۲ دارند؛ سافت‌مکس تیز و اشباع می‌شود و گرادیان محو. «جمعشان ۱ است» درست است ولی شکلِ پخش را عوض نمی‌کند. «تقریباً مساوی» نتیجه‌ی تقسیم بر d (یعنی بیش از حد) است، نه جا انداختنِ تقسیم.' },
      { t: 'text', title: 'پله‌ی ۴: سافت‌مکسِ تیز، گرادیانِ صفر',
        body: `<p>از درسِ <b>توان و لگاریتم</b>: ${E('eˣ')} با ضرب رشد می‌کند. اختلافِ ۱ در امتیاز ← وزنِ ${E('e ≈ 2.7')} برابر؛ اختلافِ ۸ ← ${E('e⁸ ≈ 2981')} برابر.</p>
               <p>در درسِ توجه دیدیم ${E('[16, 8, 0]')} ← ${E('[0.9997, 0.0003, 0.0000001]')}: تقریباً <b>یک‌داغ</b> ${EN('One-Hot')}، یعنی همه‌ی وزن روی یک کلمه.</p>
               <p>شیبِ وزنِ هر کلمه نسبت به امتیازِ خودش ${E('w(1 − w)')} است؛ همان شیبِ سیگموید! این‌جا ${E('0.9997 × 0.0003 ≈ 0.0003')}. با ${E('[2, 1, 0]')}: ${E('0.665 × 0.335 ≈ 0.22')}.</p>
               <div class="key">سافت‌مکسِ تیز مثلِ سیگموید اشباع می‌شود: گرادیان محو می‌شود (مأموریتِ محو شدن گرادیان).</div>` },
      { t: 'text', title: 'پله‌ی ۵: تقسیم بر √d، واریانس را ۱ می‌کند',
        body: `<p>اگر همه‌ی عددها را بر c تقسیم کنیم، فاصله‌ها از میانگین c برابر کوچک می‌شوند و توانِ ۲ ِ آن‌ها ${E('c²')} برابر. مثلاً ${E('−2، +2')} واریانسِ ۴ دارد؛ تقسیم بر ۲: ${E('−1، +1')}، واریانسِ ${E('4 / 2² = 1')}.</p>
               <p class="read">${E('Var(q · k / √d) = d / (√d)² = d / d = 1')}</p>
               <div class="key">هر d که باشد، امتیازها دوباره اندازه‌ی معمولِ ۱ دارند و سافت‌مکس نرم و یادگیرنده می‌ماند.</div>` },
    ] },
  ],
  sheet: {
    one: 'ضرب داخلیِ دو بردارِ تصادفی با d عدد، واریانسِ d و اندازه‌ی معمولِ √d دارد؛ امتیازهای بزرگ سافت‌مکس را تیز و گرادیان را محو می‌کنند. تقسیم بر √d واریانس را به ۱ برمی‌گرداند.',
    f: 'Var(q · k) = d   →   Var(q · k / √d) = d / d = 1   ·   Attention = softmax(Q · Kᵀ / √d) · V',
    rules: ['واریانسِ عددهای تصادفیِ مستقل جمع می‌شود؛ پس امتیاز مثل √d بزرگ می‌شود، نه d.', 'سافت‌مکسِ تیز (یک‌داغ) اشباع است: شیبِ w(1 − w) نزدیکِ صفر، مثلِ سیگموید.', 'تقسیم بر c واریانس را c² برابر کم می‌کند؛ c = √d دقیقاً ۱ می‌دهد. دما (Temperature) در خروجی همین ایده است.'],
    use: 'هر لایه‌ی توجه در ترنسفورمرها (ChatGPT، ترجمه، مدل‌های تصویر). همین ایده: دما در نمونه‌گیری و مقداردهیِ اولیه‌ی Xavier/He.',
    mistake: 'گفتنِ «برای کوچک کردنِ عددها و جلوگیری از سرریز» بدونِ واریانس و گرادیان؛ یا تقسیم بر d به‌جای √d.',
  },
});

// part 2: deeper cards first, quiz last
{ const c = LESSONS['m-attention-sqrt-d'].parts[1].cards; c.push(...c.splice(c.findIndex(x => x.t === 'quiz'), 1)); }
