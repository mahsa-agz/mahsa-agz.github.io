pattern({
  id: 'window', n: 3, name: 'پنجره‌ی لغزان (Sliding window)', sub: 'سمت راست را بزرگ کن، از چپ کوچک کن، هیچ‌وقت عقب نرو',
  story: `<p>اسمش از <b>شبکه</b> آمده. در دهه‌ی ۱۹۷۰، وقتی <b>وینت سرف و باب کان (Vint Cerf و Bob Kahn)</b> پروتکل TCP را طراحی می‌کردند، مشکل این بود: فرستنده نباید منتظرِ تأییدِ هر بسته بماند (خیلی کند)، ولی نباید هم بی‌حساب بفرستد (گیرنده غرق می‌شود). راه‌حل: یک <b>پنجره</b>. فرستنده می‌تواند حداکثر چند بسته‌ی تأییدنشده داشته باشد؛ با هر تأیید، لبه‌ی چپ جلو می‌رود و جا برای بسته‌ی بعدی در راست باز می‌شود. پنجره <b>می‌لغزد</b> و هیچ‌وقت عقب نمی‌رود.</p>
<p>در آمار هم ایده‌اش قدیمی‌تر است: <b>میانگین متحرک</b> (moving average). برای میانگینِ ۷ روزِ آخر، هر روز از اول جمع نمی‌زنی؛ روزِ جدید را اضافه و روزِ قدیمی را کم می‌کنی. <b>شهود اصلی:</b> دو پنجره‌ی پشت‌سرهم تقریباً یکی‌اند، پس فقط تفاوتشان را حساب کن.</p>`,
  uses: `<ul>
<li><b>شاخص‌های غلتان (rolling)</b>: کاربران فعالِ ۷ روز اخیر، میانگین متحرک. پانداس <code>rolling(7)</code> و SQL <code>ROWS BETWEEN 6 PRECEDING AND CURRENT ROW</code>.</li>
<li><b>محدودیت نرخ (rate limiting)</b>: «حداکثر ۱۰۰ درخواست در هر دقیقه».</li>
<li><b>طولانی‌ترین رکورد</b>: بلندترین دوره‌ی پشت‌سرهم با یک شرط (بدون تکرار، حداکثر k مورد بد).</li>
<li><b>جست‌وجو در متن با شرط</b>: کوتاه‌ترین بخشی که همه‌ی کلمه‌ها را دارد.</li>
<li><b>جاهایی که خوب نیست:</b> عضوهای <b>غیرپیوسته</b> (زیرمجموعه، نه زیرآرایه) یا جمع با <b>عدد منفی</b> ← جمع پیشوندی یا برنامه‌ریزی پویا.</li></ul>`,
  demo: {
    title: 'بلندترین زیررشته بدون حرف تکراری',
    fields: [['s', 'abcabcbb']],
    run(f) {
      const s = [...(f.s || '').slice(0, 16)], last = new Map(), out = [];
      let l = 0, best = 0;
      out.push({ cells: A(s), note: 'پنجره خالی است. r حرف‌ها را یکی‌یکی وارد می‌کند.' });
      s.forEach((c, r) => {
        let msg = '';
        if (last.has(c) && last.get(c) >= l) { msg = `«${c}» داخل پنجره تکراری است (اندیس ${last.get(c)}) ← <b>l</b> می‌پرد به ${last.get(c) + 1}. `; l = last.get(c) + 1; }
        last.set(c, r);
        const len = r - l + 1, nb = len > best; best = Math.max(best, len);
        out.push({ cells: A(s, { [l]: 'l', [r]: 'r' }, [l, r]), note: `${msg}«${c}» وارد شد. پنجره «${s.slice(l, r + 1).join('')}»، طول ${len}${nb ? ' ← بهترین تا الان' : ''}. بهترین: <b>${best}</b>` });
      });
      return out;
    }
  },
  why: `<p>یک زیررشته یا زیرآرایه (substring / subarray) یک <b>پنجره</b> است: <code>[l, r]</code>. بررسیِ همه‌ی پنجره‌ها <b>n²</b> (یا بدتر) است.</p>
<p>نکته‌ی کلیدی: در این سؤال‌ها <b>اگر پنجره‌ای خراب باشد، هر پنجره‌ی بزرگ‌تری که آن را در بر بگیرد هم خراب است</b> (تکرارِ زیاد، تعدادِ مقدارهای متفاوتِ زیاد، …). پس وقتی پنجره خراب شد، فقط <code>l</code> را جلو می‌بری و هیچ‌وقت لازم نیست برگردد.</p>
<p>هر اندیس یک بار وارد می‌شود (وقتی <code>r</code> به آن می‌رسد) و یک بار خارج (وقتی <code>l</code> از آن رد می‌شود): <b>O(n)</b>. یک <b>وضعیت</b> کوچک (یک جمع یا یک <code>Counter</code>) نگه دار و با ورود و خروج هر عضو به‌روزش کن، به‌جای این‌که از اول حساب کنی.</p>
<p class="note">این قانونِ «خراب خراب می‌ماند» لازم است. جمع با عددهای <b>منفی</b> آن را می‌شکند؛ آن سؤال‌ها مال <i>جمع پیشوندی</i> (الگوی ۴) هستند.</p>`,
  viz: `<div class="viz"><div class="vrow">${A(['a', 'b', 'c', 'a', 'b', 'b'], { 1: 'l', 3: 'r' }, [1, 3])}</div><div class="vnote">پنجره‌ی «bca» تکرار ندارد ← طول 3 · حرف بعدی «b» تکراری است ← <b>l</b> را از «b»ِ قبلی رد کن</div></div>`,
  spot: ['«<b>طولانی‌ترین / کوتاه‌ترین</b> زیررشته / زیرآرایه‌ای که …»', '«حداکثر k تا …»، «همه‌ی … را داشته باشد»', '<b>پیوسته</b> (contiguous؛ عضوها باید کنار هم باشند)', '«هر پنجره به اندازه‌ی k»'],
  template: String.raw`# longest window that stays valid
l = 0; best = 0
for r, x in enumerate(a):
    add(x)                          # x enters
    while not valid():
        remove(a[l]); l += 1        # shrink from the left
    best = max(best, r - l + 1)

# shortest window that is valid
for r, x in enumerate(a):
    add(x)
    while valid():
        best = min(best, r - l + 1)
        remove(a[l]); l += 1

# fixed size k
for r, x in enumerate(a):
    add(x)
    if r >= k: remove(a[r - k])`,
  tiktok: `<b>Longest Substring Without Repeating Characters</b> جزو ۶ سؤالِ پرتکرارِ تیک‌تاک است. نسخه‌ی پولی‌اش، <b>«حداکثر K حرفِ متفاوت»</b>، در ۳ ماه اخیر پرسیده شده. <b>Fruit Into Baskets</b> در پایین نسخه‌ی رایگانِ همان ایده است.`,
  problems: [
    {
      id: 'best-time-to-buy-and-sell-stock', t: 'Best Time to Buy and Sell Stock', d: 'E', f: 62.8, fn: 'maxProfit',
      plain: 'یک روز بخر و یک روزِ <b>بعدتر</b> بفروش. بیشترین سود، یا 0.',
      hint: 'اگر امروز بفروشی، بهترین روزِ خرید کدام است؟ می‌شود بدون نگاه به عقب آن را دانست؟',
      idea: 'ارزان‌ترین قیمتِ تا الان را نگه دار (لبه‌ی چپ). فروش امروز سودِ <code>قیمت − ارزان‌ترین</code> دارد. بیشینه را نگه دار.',
      traps: ['فروش قبل از خرید مجاز نیست؛ برای همین کمینه را در طول راه به‌روز می‌کنی، نه از اول.'],
      code: String.raw`class Solution:
    def maxProfit(self, prices):
        low, best = float('inf'), 0
        for p in prices:
            low = min(low, p)
            best = max(best, p - low)
        return best`,
      O: 'O(n) time · O(1) space',
      tests: [[[[7, 1, 5, 3, 6, 4]], 5], [[[7, 6, 4, 3, 1]], 0]]
    },
    {
      id: 'longest-substring-without-repeating-characters', t: 'Longest Substring Without Repeating Characters', d: 'M', f: 84.3, fn: 'lengthOfLongestSubstring',
      plain: 'طولِ بلندترین تکه از رشته که <b>هیچ حرفِ تکراری</b> ندارد.',
      hint: 'وقتی <code>s[r]</code> تکراری است، لبه‌ی چپِ جدید باید کجا باشد؟',
      idea: 'آخرین اندیسِ هر حرف را نگه دار. اگر <code>s[r]</code> داخل پنجره دیده شده، <code>l</code> را به یکی بعد از آن بپران.',
      traps: ['از <code>l = max(l, last[c] + 1)</code> استفاده کن؛ اندیسِ قدیمیِ سمت چپِ پنجره نباید <code>l</code> را عقب بکشد («abba»).'],
      code: String.raw`class Solution:
    def lengthOfLongestSubstring(self, s):
        last = {}
        l = best = 0
        for r, c in enumerate(s):
            if c in last:
                l = max(l, last[c] + 1)
            last[c] = r
            best = max(best, r - l + 1)
        return best`,
      O: 'O(n) time',
      tests: [[['abcabcbb'], 3], [['bbbbb'], 1], [['pwwkew'], 3], [['abba'], 2], [[''], 0]]
    },
    {
      id: 'minimum-size-subarray-sum', t: 'Minimum Size Subarray Sum', d: 'M', f: 52.9, fn: 'minSubArrayLen',
      plain: 'همه‌ی عددها مثبت‌اند. کوتاه‌ترین تکه با جمعِ <b>≥ target</b>. اگر نبود 0.',
      hint: 'این شکلِ «کوتاه‌ترینِ معتبر» است: تا وقتی معتبر است، سعی کن کوچکش کنی.',
      idea: '<code>a[r]</code> را اضافه کن. تا وقتی <code>total ≥ target</code>: طول را ثبت کن، بعد <code>a[l]</code> را کم کن و <code>l</code> را جلو ببر.',
      traps: ['وقتی هیچ تکه‌ای جواب نمی‌دهد 0 برگردان (best هنوز ∞ است).', 'فقط چون همه‌ی عددها مثبت‌اند کار می‌کند.'],
      code: String.raw`class Solution:
    def minSubArrayLen(self, target, nums):
        l = total = 0
        best = float('inf')
        for r, x in enumerate(nums):
            total += x
            while total >= target:
                best = min(best, r - l + 1)
                total -= nums[l]; l += 1
        return 0 if best == float('inf') else best`,
      O: 'O(n) time · O(1) space',
      tests: [[[7, [2, 3, 1, 2, 4, 3]], 2], [[4, [1, 4, 4]], 1], [[11, [1, 1, 1, 1]], 0]]
    },
    {
      id: 'fruit-into-baskets', t: 'Fruit Into Baskets', d: 'M', f: 34.5, fn: 'totalFruit',
      plain: 'بلندترین تکه از لیست که <b>حداکثر 2 مقدارِ متفاوت</b> دارد.',
      hint: 'وضعیت = یک <code>Counter</code> از پنجره. کِی نامعتبر است؟',
      idea: '<code>fruits[r]</code> را به شمارنده اضافه کن. تا وقتی بیش از 2 کلید دارد، <code>fruits[l]</code> را کم کن (وقتی شمارش به 0 رسید کلید را حذف کن).',
      traps: ['کلیدهایی را که به 0 رسیدند حذف کن، وگرنه <code>len(cnt)</code> بزرگ می‌ماند.', '2 را به k تغییر بده و سؤالِ پولیِ تیک‌تاک «حداکثر K متفاوت» را داری.'],
      code: String.raw`from collections import Counter

class Solution:
    def totalFruit(self, fruits):
        cnt = Counter()
        l = best = 0
        for r, f in enumerate(fruits):
            cnt[f] += 1
            while len(cnt) > 2:
                cnt[fruits[l]] -= 1
                if cnt[fruits[l]] == 0:
                    del cnt[fruits[l]]
                l += 1
            best = max(best, r - l + 1)
        return best`,
      O: 'O(n) time',
      tests: [[[[1, 2, 1]], 3], [[[0, 1, 2, 2]], 3], [[[1, 2, 3, 2, 2]], 4]]
    },
    {
      id: 'max-consecutive-ones-iii', t: 'Max Consecutive Ones III', d: 'M', f: 26.1, fn: 'longestOnes',
      plain: 'می‌توانی حداکثر <code>k</code> صفر را به یک تبدیل کنی. بلندترین رشته‌ی یک‌ها؟',
      hint: 'سؤال را این‌طور بگو: بلندترین پنجره با <b>حداکثر k صفر</b>.',
      idea: 'صفرهای پنجره را بشمار. تا وقتی <code>zeros &gt; k</code> است، <code>l</code> را جلو ببر (اگر <code>a[l]</code> صفر بود از شمارش کم کن).',
      traps: ['واقعاً چیزی را تبدیل نمی‌کنی؛ فقط صفرها را می‌شماری.'],
      code: String.raw`class Solution:
    def longestOnes(self, nums, k):
        l = zeros = best = 0
        for r, x in enumerate(nums):
            zeros += x == 0
            while zeros > k:
                zeros -= nums[l] == 0
                l += 1
            best = max(best, r - l + 1)
        return best`,
      O: 'O(n) time · O(1) space',
      tests: [[[[1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0], 2], 6], [[[0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1], 3], 10]]
    },
    {
      id: 'find-all-anagrams-in-a-string', t: 'Find All Anagrams in a String', d: 'M', f: 26.1, fn: 'findAnagrams',
      plain: 'جایگاه‌هایی در <code>s</code> که یک جابه‌جاشده از <code>p</code> از آن‌جا شروع می‌شود.',
      hint: 'اندازه‌ی پنجره ثابت است: <code>len(p)</code>. چه چیزی را مقایسه می‌کنی؟',
      idea: 'پنجره‌ی ثابت. تعداد حروفِ پنجره را نگه دار؛ <code>s[r]</code> را اضافه و <code>s[r − m]</code> را کم کن؛ وقتی با تعدادهای <code>p</code> برابر شد، <code>r − m + 1</code> را ثبت کن.',
      traps: ['مقایسه‌ی دو لیست ۲۶تایی O(26) یعنی ثابت است؛ مشکلی ندارد.', 'حالت <code>len(p) &gt; len(s)</code> خودش [] برمی‌گرداند.'],
      code: String.raw`class Solution:
    def findAnagrams(self, s, p):
        m, out = len(p), []
        need, win = [0] * 26, [0] * 26
        for c in p: need[ord(c) - 97] += 1
        for r, c in enumerate(s):
            win[ord(c) - 97] += 1
            if r >= m: win[ord(s[r - m]) - 97] -= 1
            if win == need: out.append(r - m + 1)
        return out`,
      O: 'O(n) time',
      tests: [[['cbaebabacd', 'abc'], [0, 6]], [['abab', 'ab'], [0, 1, 2]], [['a', 'ab'], []]]
    },
    {
      id: 'minimum-window-substring', t: 'Minimum Window Substring', d: 'H', f: 72.5, fn: 'minWindow',
      plain: 'کوتاه‌ترین تکه از <code>s</code> که <b>همه‌ی حروفِ <code>t</code></b> را (با تکرارها) داشته باشد. خودش را برگردان، یا "".',
      hint: 'شکلِ «کوتاه‌ترینِ معتبر». به‌جای مقایسه‌ی شمارنده‌ها در هر قدم، فقط یک عدد نگه دار: چند حرف هنوز <i>کم</i> است.',
      idea: '<code>need</code> = تعداد حروفِ t، <code>missing = len(t)</code>. <code>s[r]</code> را اضافه کن: اگر هنوز لازم بود، <code>missing −= 1</code>. تا وقتی <code>missing == 0</code>: ثبت کن، بعد <code>s[l]</code> را پس بده (اگر دوباره لازم شد، <code>missing += 1</code>).',
      traps: ['<code>need</code> برای حروفِ اضافه ممکن است منفی شود؛ اشکالی ندارد و درست است.', 'خودِ رشته را برگردان، نه طولش را.'],
      code: String.raw`from collections import Counter

class Solution:
    def minWindow(self, s, t):
        need = Counter(t)
        missing = len(t)
        l, best = 0, (0, float('inf'))
        for r, c in enumerate(s):
            if need[c] > 0: missing -= 1
            need[c] -= 1
            while missing == 0:
                if r - l < best[1] - best[0]:
                    best = (l, r)
                need[s[l]] += 1
                if need[s[l]] > 0: missing += 1
                l += 1
        return "" if best[1] == float('inf') else s[best[0]:best[1] + 1]`,
      O: 'O(|s| + |t|) time',
      tests: [[['ADOBECODEBANC', 'ABC'], 'BANC'], [['a', 'a'], 'a'], [['a', 'aa'], '']]
    }
  ]
});
